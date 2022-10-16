from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.logger import logger
from .models.request import Request
from .schemas.order import Base, OrderSchema
import aiohttp
from .pika_client import PikaClient
from datetime import datetime
import os
from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from starlette_prometheus import metrics, PrometheusMiddleware
import asyncio
import logging

app = FastAPI()
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

pika_client = PikaClient()
Base.metadata.create_all(bind=engine)

gunicorn_logger = logging.getLogger("gunicorn.error")
logger.handlers = gunicorn_logger.handlers
logger.setLevel(logging.DEBUG)


# Dependency. Why?
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/orders")
async def orders(request: Request, db: Session = Depends(get_db)):
    product_code = request.product_code
    user_id = request.user_id
    product_resp, user_resp = await fetch_all(product_code, user_id)

    if product_resp.status >= 400 and product_resp.status < 500:
        raise HTTPException(status_code=400, detail="Product not found")
    if user_resp.status >= 400 and user_resp.status < 500:
        raise HTTPException(status_code=400, detail="User not found")
    if user_resp.status >= 500 or product_resp.status >= 500:
        logger.error(
            f"error contacting product and/or user informatiom. User API returned \
            with code {user_resp.status} and product API with code {product_resp.status}"
        )
        raise HTTPException(status_code=500, detail="Unexpected error")

    product = await product_resp.json()
    user = await user_resp.json()
    customer_fullname = f'{user["firstName"]} {user["lastName"]}'

    order = OrderSchema()
    order.user_id = user_id
    order.product_code = product_code
    order.customer_fullname = customer_fullname
    order.product_name = product["name"]
    order.total_amount = product["price"]

    try:
        db.add(order)
        db.flush()
        db.refresh(order)
        # todo: if necessary, we can add a circuit breaker to better handle rabbitmq down time.
        # Or just return 503.
        pika_client.send_message(
            {
                "producer": "order-management",  # todo: check if this is really what they want
                "sent_at": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),  # this might be problematic if the clocks are not sync
                "payload": {
                    "order": {
                        "order_id": order.id,
                        "customer_fullname": customer_fullname,
                        "product_name": product["name"],
                        "total_amount": product["price"],
                        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    },
                },
            }
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(str(e))
        raise HTTPException(status_code=503, detail="server is unavaible")

    return JSONResponse(content={"detail": "order created successfully"})


def fetch_url(session, url):
    response = session.get(url)
    return response


async def fetch_all(product_code, user_id):
    loop = asyncio.get_event_loop()

    session = aiohttp.ClientSession(loop=loop)
    urls = [
        f"http://{os.environ['PRODUCT_SERVICE_URL']}:{os.environ['PRODUCT_SERVICE_PORT']}/products/{product_code}",
        f"http://{os.environ['USER_SERVICE_URL']}:{os.environ['USER_SERVICE_PORT']}/users/{user_id}",
    ]
    results = await asyncio.gather(*[fetch_url(session, url) for url in urls])
    return results[0], results[1]

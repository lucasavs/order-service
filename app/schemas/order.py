from sqlalchemy import Column, Integer, Float, DateTime, String
from sqlalchemy.sql import func

from ..database import Base


class OrderSchema(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    product_code = Column(String)
    customer_fullname = Column(String)
    product_name = Column(String)
    total_amount = Column(Float)
    created_at = Column(DateTime, default=func.now())

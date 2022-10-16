from pydantic import BaseModel


class Request(BaseModel):
    user_id: str
    product_code: str

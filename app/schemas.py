from pydantic import BaseModel, Field
from typing import List, Optional

class OrderItem(BaseModel):
    item_id: str
    name: str
    size: str
    color: str
    price: float = Field(gt=0)
    quantity: int = Field(gt=0)

class CreateOrderRequest(BaseModel):
    customer_name: str
    items: List[OrderItem]

class OrderResponse(BaseModel):
    order_id: int
    customer_name: str
    items: List[OrderItem]
    total_price: float
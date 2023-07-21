from typing import List, Dict, Union
from pydantic import BaseModel

from .types import OrderStatus


class Item(BaseModel):
    """Represents an item in an order"""

    item: str
    quantity: int

    def as_dict(self):
        return {"item": self.item, "quantity": self.quantity}


class OrderBase(BaseModel):
    """Base model for an order"""

    address: str
    recipient_name: str
    active: bool
    status: OrderStatus
    items: List[Dict[str, Union[str, int]]]


class OrderCreate(OrderBase):
    items: List[Item]


class Order(OrderBase):
    """Represents an order within the API"""

    id: int

    class Config:
        from_attributes = True

from typing import List, Dict, Union
from pydantic import BaseModel

import strawberry

from .types import OrderStatus
from strawberry.scalars import JSON
from .database import db
from . import models


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

# GraphQL Stuff

@strawberry.type
class OrderSchema:
    """Represents an order in GraphQL"""
    id: int
    address: str
    recipient_name: str
    active: bool
    status: OrderStatus
    items: List[JSON]

def get_orders():
    return db.query(models.Order).all()

@strawberry.type
class Query:
    orders: List[OrderSchema] = strawberry.field(resolver=get_orders)
    @strawberry.field
    def order(self, id: int) -> OrderSchema:
        return db.query(models.Order).filter(models.Order.id == id).first()
@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_order(self, address:str, 
                  recipient_name: str, 
                  items:List[JSON], 
                  active: bool=True, 
                  status: OrderStatus = OrderStatus.ORDER_PROCESSING) -> OrderSchema:
        """Adds an order to the database via GraphQL"""
        order = models.Order(
            address=address,
            recipient_name=recipient_name,
            items=items,
            status=status,
            active=active,
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        return order
    
    @strawberry.mutation
    def update_order(self, 
                     info, 
                     id:int, 
                     address:str=None, 
                     recipient_name: str=None, 
                     items:List[JSON]=None, 
                     active: bool=None, 
                     status: OrderStatus=None) -> OrderSchema:
        """Updates an order in the database via GraphQL"""
        order = models.Order(
            id=id,
            address=address,
            recipient_name=recipient_name,
            items=items,
            status=status,
            active=active,
        )

        db.merge(order)
        db.commit()
        return order
    
    @strawberry.mutation
    def delete_order(self, id:int) -> OrderSchema:
        """Deletes an order from the database and returns it via GraphQL"""
        db_order = db.query(models.Order).filter_by(id=id).first()
        db.delete(db_order)
        db.commit()
        return db_order
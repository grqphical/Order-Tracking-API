from sqlalchemy import Column, Integer, String, Boolean, Enum, JSON
from sqlalchemy.ext.mutable import MutableList

from .database import Base
from .types import OrderStatus


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    recipient_name = Column(String, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    status = Column(
        Enum(OrderStatus), nullable=False, default=OrderStatus.ORDER_RECEIVED
    )

    items = Column(MutableList.as_mutable(JSON), nullable=False)

    def __repr__(self):
        return f"Order(id={self.id}, address={self.address}, \
                recipient_name={self.recipient_name}, \
                items={self.items}, \
                status={self.status}, \
                active={self.active})"

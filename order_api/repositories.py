from sqlalchemy.orm import Session

from . import models, schemas
from .types import OrderStatus


class OrderRepo:
    """Used to interact with the orders database"""

    async def create(db: Session, order: schemas.OrderCreate):
        # convert the item schema to JSON first
        json_items = []
        for item in order.items:
            json_items.append(item.as_dict())

        db_order = models.Order(
            address=order.address,
            recipient_name=order.recipient_name,
            items=json_items,
            status=order.status,
            active=order.active,
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order

    def fetch_by_id(db: Session, id: int):
        return db.query(models.Order).filter(models.Order.id == id).first()

    def fetch_all(db: Session, skip: int = 0, limit: int = 1000):
        return db.query(models.Order).offset(skip).limit(limit).all()

    def fetch_active(db: Session, limit: int = 1000):
        return (
            db.query(models.Order)
            .filter(models.Order.active)
            .limit(limit)
            .all()
        )

    def fetch_by_status(db: Session, status: OrderStatus, limit: int = 1000):
        return (
            db.query(models.Order)
            .filter(models.Order.status == status)
            .limit(limit)
            .all()
        )

    async def delete(db: Session, id: int):
        db_order = db.query(models.Order).filter_by(id=id).first()
        db.delete(db_order)
        db.commit()

    async def update(db: Session, order_data):
        updated_order = db.merge(order_data)
        db.commit()
        return updated_order

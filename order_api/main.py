from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

from . import models, schemas
from .database import get_db, engine
from .repositories import OrderRepo
from .types import OrderStatus
from sqlalchemy.orm import Session
from typing import List
from fastapi.encoders import jsonable_encoder
from strawberry.fastapi import GraphQLRouter

import http
import strawberry

app = FastAPI(title="Order Tracking API", version="1.0.0")

# Load our GraphQL schemas and create the router
graphql_schema = strawberry.Schema(query=schemas.Query, mutation=schemas.Mutation)
graphql_app = GraphQLRouter(graphql_schema)

app.include_router(graphql_app, prefix="/graphql", tags=["GraphQL"])

models.Base.metadata.create_all(bind=engine)


@app.exception_handler(Exception)
def validation_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    return JSONResponse(
        status_code=http.HTTPStatus.BAD_REQUEST,
        content={"message": f"{base_error_message}. Detail: {err}"},
    )


@app.get("/", include_in_schema=False)
async def index():
    """If they naviagte to the api route, redirect them to the docs"""
    return RedirectResponse("/docs")


@app.get("/orders", tags=["Order"], response_model=List[schemas.Order])
async def get_all_orders(db: Session = Depends(get_db)):
    """Returns every order"""
    return OrderRepo.fetch_all(db)


@app.get("/orders/active", tags=["Order"], response_model=List[schemas.Order])
async def get_active_orders(db: Session = Depends(get_db)):
    """Returns every active order"""
    return OrderRepo.fetch_active(db)


@app.get(
    "/orders/status/{order_status}", tags=["Order"],
    response_model=List[schemas.Order]
)
async def get_orders_by_status(
    order_status: OrderStatus, db: Session = Depends(get_db)
):
    """Returns every order with the given status.
    Example if you give a status of ORDER_PROCESSING,
    it will get every order with that status
    """
    return OrderRepo.fetch_by_status(db, order_status)


@app.post(
    "/orders",
    tags=["Order"],
    response_model=schemas.Order,
    status_code=http.HTTPStatus.CREATED,
)
async def create_order(
    order_request: schemas.OrderCreate, db: Session = Depends(get_db)
):
    """Creates an order in the database"""
    return await OrderRepo.create(db=db, order=order_request)


@app.get("/orders/{order_id}", tags=["Order"], response_model=schemas.Order)
async def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    db_order = OrderRepo.fetch_by_id(db, order_id)

    if not db_order:
        raise HTTPException(
            status_code=http.HTTPStatus.NOT_FOUND,
            detail=f"Order not found with ID {order_id}",
        )

    return db_order


@app.delete("/orders/{order_id}", tags=["Order"])
async def deactivate_order(order_id: int, db: Session = Depends(get_db)):
    """Makes an order inactive"""
    db_order = OrderRepo.fetch_by_id(db, order_id)

    if not db_order:
        raise HTTPException(
            status_code=http.HTTPStatus.NOT_FOUND,
            detail=f"Order not found with ID {order_id}",
        )

    db_order.active = False
    return await OrderRepo.update(db=db, order_data=db_order)


@app.patch("/orders/{order_id}", tags=["Order"],
           response_model=schemas.Order)
async def update_order(
    order_id: int, order_request: schemas.OrderCreate,
    db: Session = Depends(get_db)
):
    """Updates an order's information"""
    db_order = OrderRepo.fetch_by_id(db, order_id)

    if db_order:
        update_order_encoded = jsonable_encoder(order_request)
        db_order.address = update_order_encoded["address"]
        db_order.items = update_order_encoded["items"]
        db_order.status = update_order_encoded["status"]
        db_order.active = update_order_encoded["active"]
        db_order.recipient_name = update_order_encoded["recipient_name"]
        return await OrderRepo.update(db=db, order_data=db_order)
    else:
        raise HTTPException(
            status_code=http.HTTPStatus.NOT_FOUND,
            detail=f"Order not found with ID {order_id}",
        )

import enum
import strawberry

@strawberry.enum
class OrderStatus(str, enum.Enum):
    """Used to track an order's status"""

    ORDER_RECEIVED = "ORDER_RECEIVED"
    ORDER_PROCESSING = "ORDER_PROCESSING"
    ORDER_OUT_FOR_DELIVERY = "ORDER_OUT_FOR_DELIVERY"
    ORDER_SHIPPED = "ORDER_SHIPPED"

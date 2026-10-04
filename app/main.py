import logging
import sys
from datetime import datetime
import uuid
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, Field

# -------------------------------------------------------------------
# 1. Configure Python Logging (Outputs to stdout so OpenShift & Docker capture it)
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("orders_service")

app = FastAPI(
    title="Order Microservice",
    version="1.0.0",
    description="Microservice for handling order creation and details",
)

# -------------------------------------------------------------------
# 2. Add Request/Response Logging Middleware
# -------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Completed Request: {request.method} {request.url.path} - Status: {response.status_code}")
    return response


# --- In-Memory Database ---
orders_db = {}


# --- Pydantic Schemas ---
class OrderItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, description="Quantity must be greater than zero")
    unit_price: float = Field(gt=0, description="Unit price must be greater than zero")


class CreateOrderRequest(BaseModel):
    customer_id: str
    items: List[OrderItem]


class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    items: List[OrderItem]
    total_amount: float
    status: str
    created_at: datetime


# --- Health Check Endpoint ---
@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}


# --- Order Endpoints ---

@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_data: CreateOrderRequest):
    """
    Create a new order and calculate total amount.
    """
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    total_amount = sum(item.quantity * item.unit_price for item in order_data.items)

    new_order = {
        "order_id": order_id,
        "customer_id": order_data.customer_id,
        "items": [item.dict() for item in order_data.items],
        "total_amount": round(total_amount, 2),
        "status": "PENDING",
        "created_at": datetime.utcnow(),
    }

    orders_db[order_id] = new_order

    # Log specific business details
    logger.info(f"ORDER CREATED successfully: order_id={order_id}, customer_id={order_data.customer_id}, total_amount={total_amount:.2f}")
    logger.info(f"ORDER PAYLOAD DETAILS: {new_order}")

    return new_order


@app.get("/orders", response_model=List[OrderResponse], status_code=status.HTTP_200_OK)
def list_orders():
    """
    Retrieve all created orders.
    """
    logger.info(f"FETCH ALL ORDERS: Returning {len(orders_db)} record(s)")
    return list(orders_db.values())


@app.get("/orders/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
def get_order(order_id: str):
    """
    Retrieve order details by Order ID.
    """
    order = orders_db.get(order_id)
    if not order:
        logger.warning(f"ORDER NOT FOUND: Requested order_id={order_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID '{order_id}' not found",
        )
    logger.info(f"ORDER RETRIEVED: order_id={order_id}")
    return order
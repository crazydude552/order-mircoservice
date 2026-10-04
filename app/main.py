from fastapi import FastAPI, HTTPException, status
from typing import List
from app.schemas import CreateOrderRequest, OrderResponse
from app.database import repo

app = FastAPI(
    title="Order Microservice",
    version="1.0.0",
    description="Microservice managing orders in local memory"
)

@app.get("/healthz", tags=["Health"])
def health_check():
    """Liveness probe endpoint for Kubernetes/OpenShift."""
    return {"status": "ok"}

@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
def create_order(order_data: CreateOrderRequest):
    return repo.create_order(order_data)

@app.get("/orders", response_model=List[OrderResponse], tags=["Orders"])
def get_all_orders():
    return repo.get_all_orders()

@app.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def get_order_by_id(order_id: int):
    order = repo.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order

@app.delete("/orders/{order_id}", status_code=status.HTTP_200_OK, tags=["Orders"])
def delete_order(order_id: int):
    success = repo.delete_order(order_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return {"status": "success", "message": f"Order {order_id} deleted"}
from typing import Dict, List, Optional
from app.schemas import OrderResponse, CreateOrderRequest

class OrderRepository:
    def __init__(self):
        self._db: Dict[int, OrderResponse] = {}
        self._counter: int = 1

    def create_order(self, order_data: CreateOrderRequest) -> OrderResponse:
        total = sum(item.price * item.quantity for item in order_data.items)
        new_order = OrderResponse(
            order_id=self._counter,
            customer_name=order_data.customer_name,
            items=order_data.items,
            total_price=round(total, 2)
        )
        self._db[self._counter] = new_order
        self._counter += 1
        return new_order

    def get_order(self, order_id: int) -> Optional[OrderResponse]:
        return self._db.get(order_id)

    def get_all_orders(self) -> List[OrderResponse]:
        return list(self._db.values())

    def delete_order(self, order_id: int) -> bool:
        if order_id in self._db:
            del self._db[order_id]
            return True
        return False

# Single global instance for in-memory storage
repo = OrderRepository()
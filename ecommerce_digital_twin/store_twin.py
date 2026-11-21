"""Core digital twin logic for simulating an online store."""

import copy

from models import Order, OrderResult, Product

MAX_DISCOUNT_RATE = 0.50


class StoreDigitalTwin:
    """A lightweight digital twin of an e-commerce store."""

    def __init__(self, store_name: str) -> None:
        """Initialize the store twin with empty inventory and history."""
        self.store_name = store_name
        self.inventory: dict[str, Product] = {}
        self.order_history: list[OrderResult] = []

    def add_product(self, product: Product) -> None:
        """Register or update a product in the store inventory."""
        self.inventory[product.sku] = product

    def process_order(self, order: Order) -> OrderResult:
        """Validate and process one order, updating inventory if fulfilled."""
        product = self.inventory.get(order.sku)

        if product is None:
            result = OrderResult(
                order_id=order.order_id,
                fulfilled=False,
                revenue=0.0,
                cost=0.0,
                message=f"Product '{order.sku}' not found.",
            )
            self.order_history.append(result)
            return result

        if order.quantity <= 0:
            result = OrderResult(
                order_id=order.order_id,
                fulfilled=False,
                revenue=0.0,
                cost=0.0,
                message="Order quantity must be positive.",
            )
            self.order_history.append(result)
            return result

        if not 0.0 <= order.discount_rate <= MAX_DISCOUNT_RATE:
            result = OrderResult(
                order_id=order.order_id,
                fulfilled=False,
                revenue=0.0,
                cost=0.0,
                message="Discount rate is out of allowed range.",
            )
            self.order_history.append(result)
            return result

        if product.stock < order.quantity:
            result = OrderResult(
                order_id=order.order_id,
                fulfilled=False,
                revenue=0.0,
                cost=0.0,
                message=(
                    f"Insufficient stock for {product.name} "
                    f"(requested {order.quantity}, available {product.stock})."
                ),
            )
            self.order_history.append(result)
            return result

        product.stock -= order.quantity
        gross_revenue = product.unit_price * order.quantity
        net_revenue = gross_revenue * (1.0 - order.discount_rate)
        total_cost = product.unit_cost * order.quantity

        result = OrderResult(
            order_id=order.order_id,
            fulfilled=True,
            revenue=round(net_revenue, 2),
            cost=round(total_cost, 2),
            message=f"Fulfilled {order.quantity}x {product.name}.",
        )
        self.order_history.append(result)
        return result

    def run_simulation(self, orders: list[Order]) -> list[OrderResult]:
        """Process a batch of orders sequentially."""
        return [self.process_order(order) for order in orders]

    def get_low_stock_products(self) -> list[Product]:
        """Return all products that need restocking."""
        return [
            product
            for product in self.inventory.values()
            if product.needs_restock()
        ]

    def get_summary(self) -> dict[str, float | int]:
        """Compute key financial and operational KPIs for the store."""
        total_orders = len(self.order_history)
        fulfilled_orders = sum(
            1 for result in self.order_history if result.fulfilled
        )
        failed_orders = total_orders - fulfilled_orders
        total_revenue = sum(result.revenue for result in self.order_history)
        total_cost = sum(result.cost for result in self.order_history)
        net_profit = total_revenue - total_cost

        return {
            "total_orders": total_orders,
            "fulfilled_orders": fulfilled_orders,
            "failed_orders": failed_orders,
            "total_revenue": round(total_revenue, 2),
            "total_cost": round(total_cost, 2),
            "net_profit": round(net_profit, 2),
        }

    def clone(self) -> "StoreDigitalTwin":
        """Create an independent copy of the twin for what-if testing."""
        return copy.deepcopy(self)

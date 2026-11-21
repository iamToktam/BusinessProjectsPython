"""Data models for the e-commerce digital twin simulation."""

from dataclasses import dataclass


@dataclass
class Product:
    """Represents a product tracked in the store inventory."""

    sku: str
    name: str
    unit_price: float
    unit_cost: float
    stock: int
    reorder_level: int = 5

    def needs_restock(self) -> bool:
        """Return True if current stock is at or below reorder level."""
        return self.stock <= self.reorder_level

    def unit_profit(self) -> float:
        """Return the base profit earned on a single unit."""
        return self.unit_price - self.unit_cost


@dataclass
class Order:
    """Represents a single customer order."""

    order_id: str
    sku: str
    quantity: int
    discount_rate: float = 0.0


@dataclass
class OrderResult:
    """Represents the outcome of processing a customer order."""

    order_id: str
    fulfilled: bool
    revenue: float
    cost: float
    message: str

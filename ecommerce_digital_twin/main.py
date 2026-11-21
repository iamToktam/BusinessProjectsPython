"""Entry point for running the e-commerce digital twin simulation."""

from pathlib import Path

from models import Order, Product
from reporting import generate_charts, generate_pdf_report
from store_twin import StoreDigitalTwin

PROMO_DISCOUNT_RATE = 0.10
REPORT_WIDTH = 56
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def create_sample_store() -> StoreDigitalTwin:
    """Create a sample online store with initial product inventory."""
    twin = StoreDigitalTwin(store_name="TechGear Online Store")
    sample_products = [
        Product(
            sku="MOUSE-01",
            name="Wireless Mouse",
            unit_price=35.0,
            unit_cost=18.0,
            stock=12,
            reorder_level=4,
        ),
        Product(
            sku="KEYB-02",
            name="Mechanical Keyboard",
            unit_price=95.0,
            unit_cost=55.0,
            stock=8,
            reorder_level=3,
        ),
        Product(
            sku="HUB-03",
            name="USB-C Hub",
            unit_price=45.0,
            unit_cost=22.0,
            stock=10,
            reorder_level=3,
        ),
        Product(
            sku="STND-04",
            name="Laptop Stand",
            unit_price=50.0,
            unit_cost=25.0,
            stock=6,
            reorder_level=2,
        ),
    ]

    for product in sample_products:
        twin.add_product(product)

    return twin


def create_baseline_orders() -> list[Order]:
    """Return a sample list of daily orders at regular prices."""
    return [
        Order(order_id="ORD-101", sku="MOUSE-01", quantity=4),
        Order(order_id="ORD-102", sku="KEYB-02", quantity=3),
        Order(order_id="ORD-103", sku="HUB-03", quantity=5),
        Order(order_id="ORD-104", sku="STND-04", quantity=5),
        Order(order_id="ORD-105", sku="STND-04", quantity=3),
    ]


def create_promo_orders(discount_rate: float) -> list[Order]:
    """Return higher-volume orders expected during a discount campaign."""
    return [
        Order(
            order_id="ORD-201",
            sku="MOUSE-01",
            quantity=7,
            discount_rate=discount_rate,
        ),
        Order(
            order_id="ORD-202",
            sku="KEYB-02",
            quantity=5,
            discount_rate=discount_rate,
        ),
        Order(
            order_id="ORD-203",
            sku="HUB-03",
            quantity=7,
            discount_rate=discount_rate,
        ),
        Order(
            order_id="ORD-204",
            sku="STND-04",
            quantity=5,
            discount_rate=discount_rate,
        ),
        Order(
            order_id="ORD-205",
            sku="MOUSE-01",
            quantity=4,
            discount_rate=discount_rate,
        ),
    ]


def print_report(title: str, twin: StoreDigitalTwin) -> None:
    """Display a formatted operational and financial report."""
    summary = twin.get_summary()
    low_stock_items = twin.get_low_stock_products()

    print("=" * REPORT_WIDTH)
    print(f"{twin.store_name} - {title}")
    print("=" * REPORT_WIDTH)

    print("Order Log:")
    for result in twin.order_history:
        status = "OK" if result.fulfilled else "FAILED"
        print(f"  [{status}] {result.order_id}: {result.message}")

    print("\nFinancial Summary:")
    print(f"  Total Orders:     {summary['total_orders']}")
    print(f"  Fulfilled Orders: {summary['fulfilled_orders']}")
    print(f"  Failed Orders:    {summary['failed_orders']}")
    print(f"  Total Revenue:    ${summary['total_revenue']:.2f}")
    print(f"  Total Cost:       ${summary['total_cost']:.2f}")
    print(f"  Net Profit:       ${summary['net_profit']:.2f}")

    print("\nRestock Alerts:")
    if not low_stock_items:
        print("  All products are sufficiently stocked.")
    else:
        for item in low_stock_items:
            print(
                f"  - {item.name} ({item.sku}): "
                f"{item.stock} left (reorder at {item.reorder_level})"
            )
    print()


def main() -> None:
    """Run baseline and what-if scenarios, then export charts and PDF."""
    base_twin = create_sample_store()

    # Clone the twin so both scenarios start from the exact same state.
    baseline_twin = base_twin.clone()
    promo_twin = base_twin.clone()

    baseline_twin.run_simulation(create_baseline_orders())
    promo_twin.run_simulation(create_promo_orders(PROMO_DISCOUNT_RATE))

    print_report("Baseline Scenario (0% Discount)", baseline_twin)
    print_report("What-If Scenario (10% Discount)", promo_twin)

    baseline_profit = baseline_twin.get_summary()["net_profit"]
    promo_profit = promo_twin.get_summary()["net_profit"]
    profit_diff = round(promo_profit - baseline_profit, 2)
    sign = "+" if profit_diff >= 0 else "-"

    print("-" * REPORT_WIDTH)
    print(
        f"Profit Difference (Promo vs Baseline): "
        f"{sign}${abs(profit_diff):.2f}"
    )
    print("-" * REPORT_WIDTH)

    chart_path = generate_charts(
        baseline_twin,
        promo_twin,
        OUTPUT_DIR / "simulation_charts.png",
    )
    pdf_path = generate_pdf_report(
        baseline_twin,
        promo_twin,
        chart_path,
        OUTPUT_DIR / "digital_twin_report.pdf",
    )

    print(f"\nSaved charts to: {chart_path}")
    print(f"Saved PDF report to: {pdf_path}")


if __name__ == "__main__":
    main()

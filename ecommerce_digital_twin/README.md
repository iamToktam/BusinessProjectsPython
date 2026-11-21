# E-Commerce Digital Twin

A simple, readable Python simulation of an online store digital twin.
This project focuses on clean code structure and adherence to the **PEP 8**
style guide so other students can easily read, understand, and extend it.

## Overview

A business digital twin is a virtual model of a real operation that lets you
monitor performance and test "what-if" scenarios safely before applying
changes in the real world.

This project simulates:

- Inventory tracking for e-commerce products
- Order validation and fulfillment (stock and discount checks)
- Financial KPI calculation (revenue, cost, and net profit)
- Low-stock restock alerts
- Side-by-side comparison of a **Baseline Scenario** vs. a
  **10% Promotional Discount What-If Scenario**

## Project Structure

```text
ecommerce_digital_twin/
├── models.py       # Product, Order, and OrderResult dataclasses
├── store_twin.py   # StoreDigitalTwin class and business logic
├── main.py         # Sample scenarios and formatted report output
└── README.md       # Project documentation
```

## Requirements

- Python 3.10+ (uses only the Python standard library; no external packages)

## How to Run

From the repository root:

```bash
python3 ecommerce_digital_twin/main.py
```

Or from inside the project directory:

```bash
cd ecommerce_digital_twin
python3 main.py
```

## PEP 8 Practices Applied

- Standard naming conventions (`PascalCase` for classes, `snake_case` for
  functions and variables, `UPPER_CASE` for constants)
- Maximum line length of 79 characters
- Clean import organization (standard library imports separated from local
  imports)
- Clear docstrings and type hints on all classes, methods, and functions
- Modular separation between data models, core logic, and script execution

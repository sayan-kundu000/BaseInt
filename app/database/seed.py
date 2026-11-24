"""Database seeding script with realistic business and analytics data."""

from datetime import datetime, timedelta
import random
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    select,
)
from app.database.connection import get_engine

metadata = MetaData()

# Define Customers Table
customers_table = Table(
    "customers",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("email", String(150), unique=True, nullable=False),
    Column("region", String(50), nullable=False),
    Column("signup_date", DateTime, default=datetime.utcnow),
)

# Define Products Table
products_table = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(150), nullable=False),
    Column("category", String(100), nullable=False),
    Column("price", Float, nullable=False),
    Column("stock_quantity", Integer, default=0),
)

# Define Orders Table (Specifically verified by Test Case 1: id, order_date)
orders_table = Table(
    "orders",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("order_date", DateTime, nullable=False),
    Column("customer_id", Integer, ForeignKey("customers.id"), nullable=False),
    Column("amount", Float, nullable=False),
    Column("status", String(50), default="COMPLETED"),
)

# Define Order Items Table
order_items_table = Table(
    "order_items",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("order_id", Integer, ForeignKey("orders.id"), nullable=False),
    Column("product_id", Integer, ForeignKey("products.id"), nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("unit_price", Float, nullable=False),
)


def seed_database(engine=None):
    """Create schemas and populate sample data."""
    if engine is None:
        engine = get_engine()

    # Create tables
    metadata.create_all(engine)

    with engine.begin() as conn:
        # Check if already seeded
        result = conn.execute(select(customers_table).limit(1)).fetchall()
        if result:
            return "Database already seeded with tables and records."

        # Sample Customers
        customers_data = [
            {"name": "Sayan Kundu", "email": "sayan@example.com", "region": "North America", "signup_date": datetime(2025, 1, 15, 10, 0)},
            {"name": "Alice Vance", "email": "alice.v@enterprise.io", "region": "Europe", "signup_date": datetime(2025, 2, 20, 11, 30)},
            {"name": "Carlos Gomez", "email": "carlos.g@techcorp.com", "region": "Latin America", "signup_date": datetime(2025, 3, 5, 9, 15)},
            {"name": "Mei Lin", "email": "mei.lin@asiapacific.org", "region": "Asia-Pacific", "signup_date": datetime(2025, 3, 22, 14, 45)},
            {"name": "Devin Brooks", "email": "devin.b@cloudscale.net", "region": "North America", "signup_date": datetime(2025, 4, 10, 16, 20)},
            {"name": "Zara Ahmed", "email": "zara.a@middleeast.ae", "region": "Middle East", "signup_date": datetime(2025, 5, 1, 12, 10)},
            {"name": "Liam O'Connor", "email": "liam@celtictech.ie", "region": "Europe", "signup_date": datetime(2025, 5, 18, 8, 50)},
            {"name": "Elena Rostova", "email": "elena.r@nordicdata.fi", "region": "Europe", "signup_date": datetime(2025, 6, 2, 17, 35)},
        ]
        conn.execute(customers_table.insert(), customers_data)

        # Sample Products
        products_data = [
            {"name": "Enterprise Analytics Suite", "category": "Software", "price": 4999.00, "stock_quantity": 999},
            {"name": "Cloud Data Pipeline Node", "category": "Infrastructure", "price": 1250.00, "stock_quantity": 450},
            {"name": "Neural Reranker Microservice", "category": "AI Models", "price": 850.00, "stock_quantity": 300},
            {"name": "AST Security Firewall Box", "category": "Hardware", "price": 2800.00, "stock_quantity": 85},
            {"name": "High-Throughput Vector DB Appliance", "category": "Hardware", "price": 6200.00, "stock_quantity": 40},
            {"name": "Self-Correction Telemetry Agent", "category": "Software", "price": 450.00, "stock_quantity": 1200},
            {"name": "NeMo Guardrail Policy Bundle", "category": "Security", "price": 950.00, "stock_quantity": 600},
            {"name": "Realtime BI Dashboard License", "category": "Software", "price": 1500.00, "stock_quantity": 250},
        ]
        conn.execute(products_table.insert(), products_data)

        # Sample Orders & Order Items
        base_date = datetime(2026, 1, 1)
        statuses = ["COMPLETED", "COMPLETED", "COMPLETED", "PENDING", "PROCESSING"]
        
        orders_data = []
        for i in range(1, 31):
            order_day = base_date + timedelta(days=i * 3, hours=random.randint(1, 12))
            cust_id = random.randint(1, len(customers_data))
            # Calculate mock amount
            amt = round(random.uniform(750.0, 14500.0), 2)
            orders_data.append({
                "id": i,
                "order_date": order_day,
                "customer_id": cust_id,
                "amount": amt,
                "status": random.choice(statuses)
            })
        conn.execute(orders_table.insert(), orders_data)

        order_items_data = []
        item_id = 1
        for ord_dict in orders_data:
            num_items = random.randint(1, 3)
            for _ in range(num_items):
                prod_id = random.randint(1, len(products_data))
                qty = random.randint(1, 4)
                price = products_data[prod_id - 1]["price"]
                order_items_data.append({
                    "id": item_id,
                    "order_id": ord_dict["id"],
                    "product_id": prod_id,
                    "quantity": qty,
                    "unit_price": price
                })
                item_id += 1
        conn.execute(order_items_table.insert(), order_items_data)

    return f"Seeded successfully: {len(customers_data)} customers, {len(products_data)} products, {len(orders_data)} orders, {len(order_items_data)} items."


if __name__ == "__main__":
    eng = get_engine()
    res = seed_database(eng)
    print(res)

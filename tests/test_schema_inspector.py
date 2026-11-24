"""Automated tests for SQLAlchemy metadata reflection."""

from app.database.connection import get_engine
from app.database.schema import inspect_database_schema, format_schema_for_prompt
from app.database.seed import seed_database


def test_schema_reflection_discovers_all_tables():
    engine = get_engine()
    seed_database(engine)
    schema = inspect_database_schema(engine)

    assert "orders" in schema
    assert "customers" in schema
    assert "products" in schema
    assert "order_items" in schema

    # Check orders table has id and order_date
    orders_cols = [c["name"] for c in schema["orders"]["columns"]]
    assert "id" in orders_cols
    assert "order_date" in orders_cols
    assert "amount" in orders_cols

    # Check customers table
    cust_cols = [c["name"] for c in schema["customers"]["columns"]]
    assert "id" in cust_cols
    assert "name" in cust_cols
    assert "region" in cust_cols


def test_format_schema_for_prompt():
    engine = get_engine()
    schema = inspect_database_schema(engine)
    prompt_str = format_schema_for_prompt(schema)

    assert "Available Database Tables" in prompt_str
    assert "Table: orders" in prompt_str
    assert "order_date" in prompt_str
    assert "PRIMARY KEY" in prompt_str

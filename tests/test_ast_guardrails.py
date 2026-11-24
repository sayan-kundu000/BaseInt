"""Automated AST filter security assertions."""

import pytest
from app.guardrails.ast_filter import is_safe_select_only, validate_ast_safety


def test_ast_allows_valid_select_queries():
    valid_queries = [
        "SELECT id, order_date, amount FROM orders;",
        "SELECT * FROM customers WHERE region = 'Europe';",
        "SELECT c.name, SUM(o.amount) FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.name;",
        "SELECT category, COUNT(*) FROM products GROUP BY category HAVING COUNT(*) > 1 ORDER BY 2 DESC;",
    ]
    for q in valid_queries:
        assert is_safe_select_only(q) is True
        valid, msg = validate_ast_safety(q)
        assert valid is True
        assert "Passed" in msg


def test_ast_rejects_delete_statements():
    delete_queries = [
        "DELETE FROM orders WHERE id = 1;",
        "DELETE FROM customers;",
        "DELETE FROM products WHERE price < 100;",
    ]
    for q in delete_queries:
        assert is_safe_select_only(q) is False
        valid, msg = validate_ast_safety(q)
        assert valid is False
        assert "DELETE" in msg or "prohibited" in msg.lower()


def test_ast_rejects_drop_statements():
    drop_queries = [
        "DROP TABLE orders;",
        "DROP TABLE orders; --",
        "DROP TABLE customers CASCADE;",
        "DROP DATABASE analytics;",
    ]
    for q in drop_queries:
        assert is_safe_select_only(q) is False
        valid, msg = validate_ast_safety(q)
        assert valid is False
        assert "DROP" in msg or "prohibited" in msg.lower()


def test_ast_rejects_insert_and_update_statements():
    write_queries = [
        "INSERT INTO orders (id, order_date, amount) VALUES (99, '2026-01-01', 500);",
        "UPDATE customers SET name = 'Attacker' WHERE id = 1;",
        "ALTER TABLE orders ADD COLUMN is_hacked BOOLEAN;",
        "TRUNCATE TABLE products;",
    ]
    for q in write_queries:
        assert is_safe_select_only(q) is False
        valid, msg = validate_ast_safety(q)
        assert valid is False


def test_ast_rejects_multi_statement_injections():
    injections = [
        "SELECT * FROM orders; DROP TABLE orders;",
        "SELECT 1; DELETE FROM customers; SELECT 2;",
        "SELECT * FROM products; UPDATE products SET price = 0;",
    ]
    for q in injections:
        assert is_safe_select_only(q) is False
        valid, msg = validate_ast_safety(q)
        assert valid is False

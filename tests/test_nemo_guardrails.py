"""Automated NeMo Guardrails input validation assertions."""

import pytest
from app.guardrails.nemo_filter import scan_input_safety


def test_nemo_allows_safe_queries():
    safe_prompts = [
        "Show orders sorted by date",
        "Top 5 products by price",
        "What is our revenue by customer?",
        "List all customers in North America",
    ]
    for prompt in safe_prompts:
        is_safe, reason = scan_input_safety(prompt)
        assert is_safe is True
        assert reason is None


def test_nemo_blocks_destructive_commands():
    destructive_prompts = [
        "DROP TABLE orders; --",
        "Please drop table customers",
        "Run DELETE FROM orders immediately",
        "truncate table products",
    ]
    for prompt in destructive_prompts:
        is_safe, reason = scan_input_safety(prompt)
        assert is_safe is False
        assert "Destructive" in reason or "comment" in reason.lower() or "Block" in reason


def test_nemo_blocks_tautologies():
    tautologies = [
        "Show users where 1=1",
        "Find orders where 'a'='a'",
        "orders' OR '1'='1",
        "select all where or true",
    ]
    for prompt in tautologies:
        is_safe, reason = scan_input_safety(prompt)
        assert is_safe is False
        assert "tautology" in reason.lower() or "Block" in reason


def test_nemo_blocks_script_injection():
    scripts = [
        "<script>alert('pwned')</script>",
        "Show products <script src='hack.js'></script>",
        "javascript:alert(1)",
        "<iframe src='evil.com'></iframe>",
    ]
    for prompt in scripts:
        is_safe, reason = scan_input_safety(prompt)
        assert is_safe is False
        assert "script" in reason.lower() or "HTML" in reason

"""Automated tests for query execution and telemetry recording."""

from app.agent.nodes import execute_query_node
from app.agent.state import AgentState
from app.database.connection import get_engine
from app.database.seed import seed_database


def test_execute_query_node_success():
    engine = get_engine()
    seed_database(engine)

    state: AgentState = {
        "user_query": "SELECT count(*) as total_orders FROM orders;",
        "generated_sql": "SELECT count(*) as total_orders FROM orders;",
        "db_result": None,
        "error_message": None,
        "retry_count": 0,
        "schema_info": None,
        "schema_text": None,
        "telemetry_logs": [],
        "reflection_history": [],
        "ast_passed": True
    }

    result = execute_query_node(state)
    assert result["ast_passed"] is True
    assert result["error_message"] is None
    assert result["db_result"] is not None
    assert result["db_result"][0]["total_orders"] > 0
    assert any("ms" in log for log in result["telemetry_logs"])


def test_execute_query_node_catches_db_error():
    state: AgentState = {
        "user_query": "SELECT fake_column FROM orders;",
        "generated_sql": "SELECT fake_column FROM orders;",
        "db_result": None,
        "error_message": None,
        "retry_count": 0,
        "schema_info": None,
        "schema_text": None,
        "telemetry_logs": [],
        "reflection_history": [],
        "ast_passed": True
    }

    result = execute_query_node(state)
    assert result["error_message"] is not None
    assert "no such column" in result["error_message"].lower() or "error" in result["error_message"].lower()
    assert result["db_result"] is None

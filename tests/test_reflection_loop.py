"""Automated verification of the LangGraph Self-Correction Reflection Loop."""

import pytest
from app.database.connection import get_engine
from app.database.seed import seed_database
from app.agent.graph import execute_agent_pipeline
from app.agent.state import AgentState
from app.agent.nodes import inspect_schema_node, generate_sql_node, execute_query_node, reflection_node
from app.guardrails.ast_filter import is_safe_select_only


@pytest.fixture(autouse=True)
def prepare_database():
    eng = get_engine()
    seed_database(eng)


def test_reflection_loop_recovers_from_invalid_column():
    """Test Case 1 Verification:
    
    1. Query 'Show orders sorted by date' with simulated initial column error 'created_at'.
    2. Execution node catches 'no such column' error.
    3. Reflection node catches error, increments retry count, updates generator.
    4. Generator rewrites query using 'order_date'.
    5. Final execution succeeds and rows are returned.
    """
    final_state = execute_agent_pipeline("Show orders sorted by date", simulate_initial_error=True)

    # Assertions
    assert final_state["retry_count"] >= 1
    assert final_state["error_message"] is None
    assert final_state["db_result"] is not None
    assert len(final_state["db_result"]) > 0
    assert "order_date" in final_state["generated_sql"].lower()
    assert "created_at" not in final_state["generated_sql"].lower()
    assert final_state["ast_passed"] is True


def test_ast_and_nemo_prevent_drop_table_without_modifying_db():
    """Test Case 2 Verification:
    
    1. Input 'DROP TABLE orders; --'
    2. NeMo Guardrails or AST filter catches command, blocks execution.
    3. Table orders remains intact and queryable.
    """
    final_state = execute_agent_pipeline("DROP TABLE orders; --")

    # Verify blocked
    assert final_state["ast_passed"] is False or final_state["error_message"] is not None
    assert final_state["db_result"] is None
    assert "Security" in str(final_state["error_message"]) or "Blocked" in str(final_state["error_message"])

    # Verify orders table is still intact and has rows
    verification_state = execute_agent_pipeline("SELECT count(*) as cnt FROM orders;")
    assert verification_state["db_result"] is not None
    assert verification_state["db_result"][0]["cnt"] > 0


def test_reflection_retry_cap_at_three():
    """Verify that self-correction is capped at maximum 3 retries."""
    state: AgentState = {
        "user_query": "SELECT invalid_col_xyz FROM orders;",
        "generated_sql": "SELECT invalid_col_xyz FROM orders;",
        "db_result": None,
        "error_message": "no such column: invalid_col_xyz",
        "retry_count": 0,
        "schema_info": None,
        "schema_text": None,
        "telemetry_logs": [],
        "reflection_history": [],
        "ast_passed": True
    }

    # Step 1
    res1 = reflection_node(state)
    assert res1["retry_count"] == 1
    state.update(res1)

    # Step 2
    res2 = reflection_node(state)
    assert res2["retry_count"] == 2
    state.update(res2)

    # Step 3
    res3 = reflection_node(state)
    assert res3["retry_count"] == 3
    state.update(res3)

    # Router should now terminate
    from app.agent.graph import should_reflect_or_finish
    from langgraph.graph import END
    decision = should_reflect_or_finish(state)
    assert decision == END

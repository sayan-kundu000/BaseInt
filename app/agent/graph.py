"""LangGraph StateGraph coordination and compilation for BaseInt."""

from typing import Literal, Dict, Any
from langgraph.graph import StateGraph, END
from app.config import settings
from app.agent.state import AgentState
from app.agent.nodes import (
    inspect_schema_node,
    generate_sql_node,
    execute_query_node,
    reflection_node,
)
from app.guardrails.nemo_filter import scan_input_safety


def should_reflect_or_finish(state: AgentState) -> Literal["reflection_node", "__end__"]:
    """Conditional router: evaluates whether to enter the reflection loop or finalize."""
    error_message = state.get("error_message")
    retry_count = state.get("retry_count", 0)
    ast_passed = state.get("ast_passed", True)

    # If execution succeeded with no error, finish
    if not error_message:
        return END

    # If blocked by AST security filter, do not self-correct to bypass security; finish immediately
    if not ast_passed or "AST Safety Filter Blocked" in error_message:
        return END

    # If maximum retries exceeded (capped at max 3 retries as per specification), finish
    if retry_count >= settings.max_retries:
        return END

    # Otherwise, enter reflection node to formulate self-correction
    return "reflection_node"


def build_sql_agent_graph():
    """Construct and compile the LangGraph StateMachine."""
    workflow = StateGraph(AgentState)

    # Register the 4 mandatory nodes
    workflow.add_node("inspect_schema_node", inspect_schema_node)
    workflow.add_node("generate_sql_node", generate_sql_node)
    workflow.add_node("execute_query_node", execute_query_node)
    workflow.add_node("reflection_node", reflection_node)

    # Establish linear transitions
    workflow.set_entry_point("inspect_schema_node")
    workflow.add_edge("inspect_schema_node", "generate_sql_node")
    workflow.add_edge("generate_sql_node", "execute_query_node")

    # Conditional reflection edge
    workflow.add_conditional_edges(
        "execute_query_node",
        should_reflect_or_finish,
        {
            "reflection_node": "reflection_node",
            END: END
        }
    )

    # Loop back from reflection to generator
    workflow.add_edge("reflection_node", "generate_sql_node")

    return workflow.compile()


# Global compiled graph instance
app_graph = build_sql_agent_graph()


def execute_agent_pipeline(user_query: str, simulate_initial_error: bool = False) -> AgentState:
    """Execute the full agent pipeline including NeMo Guardrails, Schema Reflection, and SQL Generation."""
    # Step 0: NeMo Guardrails Input Validation
    is_safe, violation = scan_input_safety(user_query)
    if not is_safe:
        return {
            "user_query": user_query,
            "generated_sql": "",
            "db_result": None,
            "error_message": f"Security Alert: {violation}",
            "retry_count": 0,
            "schema_info": None,
            "schema_text": None,
            "telemetry_logs": [
                f"[NeMo Guardrails] Input query failed safety checks.",
                f"[Security Reason] {violation}"
            ],
            "reflection_history": [],
            "ast_passed": False
        }

    # Initial State
    initial_history = []
    if simulate_initial_error:
        initial_history.append({"flags": ["simulate_initial_error"]})

    initial_state: AgentState = {
        "user_query": user_query,
        "generated_sql": "",
        "db_result": None,
        "error_message": None,
        "retry_count": 0,
        "schema_info": None,
        "schema_text": None,
        "telemetry_logs": [],
        "reflection_history": initial_history,
        "ast_passed": True
    }

    # Run StateGraph
    final_state = app_graph.invoke(initial_state)
    return final_state

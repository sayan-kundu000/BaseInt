"""State definition for the BaseInt LangGraph StateGraph."""

from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    """LangGraph state dictionary tracking query progression and self-correction."""
    user_query: str
    generated_sql: str
    db_result: Optional[List[Dict[str, Any]]]
    error_message: Optional[str]
    retry_count: int
    schema_info: Optional[Dict[str, Any]]
    schema_text: Optional[str]
    telemetry_logs: List[str]
    reflection_history: List[Dict[str, Any]]
    ast_passed: bool

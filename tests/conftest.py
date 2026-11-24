"""Pytest fixtures and test environment setup."""

import pytest
from sqlalchemy import create_engine
from app.database.connection import get_engine
from app.database.seed import seed_database
from app.agent.graph import build_sql_agent_graph


@pytest.fixture(scope="session")
def test_db_engine():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    seed_database(engine)
    return engine


@pytest.fixture(scope="session")
def agent_graph():
    """Compiled LangGraph workflow."""
    return build_sql_agent_graph()

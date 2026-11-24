"""SQLAlchemy database connection and engine manager."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

_engine = None
_session_factory = None


def get_engine(database_url: str = None):
    """Retrieve or initialize the SQLAlchemy engine."""
    global _engine
    url = database_url or settings.database_url
    if _engine is None or str(_engine.url) != url:
        connect_args = {}
        if url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        _engine = create_engine(url, connect_args=connect_args)
    return _engine


def get_session(database_url: str = None):
    """Obtain a new database session."""
    global _session_factory
    engine = get_engine(database_url)
    if _session_factory is None:
        _session_factory = sessionmaker(bind=engine)
    return _session_factory()

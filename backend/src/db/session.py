"""SQLAlchemy engine and session factory.

Sessions are short-lived and scoped: one per HTTP request (FastAPI dependency),
or one per job run (context manager). Never hold a session as a module-level global.
"""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import get_settings

_engine = create_engine(get_settings().database_url, future=True)
_SessionLocal = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Yield a transactional session that commits on success and rolls back on error.

    Use from scheduled jobs and scripts. FastAPI handlers should use `get_session`
    instead so the framework manages the lifecycle.
    """
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Iterator[Session]:
    """FastAPI dependency that yields a session and closes it after the request."""
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()

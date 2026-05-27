"""Declarative base for all SQLAlchemy models.

Every model imports `Base` from here. There is exactly one Base per project so
`Base.metadata` is the single source of truth for what tables exist.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base class for all ORM models in the project."""

"""Structured JSON logging via structlog.

Call `configure_logging()` exactly once at process start (FastAPI lifespan,
job entrypoint, alembic env). Then `get_logger(__name__)` anywhere to log.
"""

import logging
import sys

import structlog


def configure_logging(level: str = "INFO") -> None:
    """Wire stdlib logging and structlog for JSON output to stdout.

    Args:
        level: Minimum level. One of DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """
    numeric_level = getattr(logging, level.upper())

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a bound logger. Pass `__name__` so log lines carry their source module."""
    return structlog.get_logger(name)

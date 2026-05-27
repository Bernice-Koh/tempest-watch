"""Typed exception hierarchy. All custom errors subclass TempestWatchError.

Internal code raises these; handlers and job entrypoints catch them and map to
HTTP responses or log lines. Never raise bare `Exception`.
"""


class TempestWatchError(Exception):
    """Base exception for all tempest-watch errors."""


class ConfigurationError(TempestWatchError):
    """Required configuration is missing or invalid."""


class ExternalServiceError(TempestWatchError):
    """An external source (API, scrape target, LLM) failed in an unrecoverable way."""


class NotFoundError(TempestWatchError):
    """A requested entity does not exist."""


class MatcherError(TempestWatchError):
    """The matcher pipeline produced an unusable result for a listing."""

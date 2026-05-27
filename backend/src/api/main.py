"""FastAPI application entrypoint. Wires routes, exception handlers, and lifespan."""

from fastapi import FastAPI

app = FastAPI(title="tempest-watch", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Return process liveness. Used by uptime checks and by humans poking the box."""
    return {"status": "ok"}

"""FastAPI app entry point. Module routers are mounted here as they are written."""

from fastapi import FastAPI

app = FastAPI(title="RehabGraph-RAG API", version="0.1.0")


@app.get("/api/v1/health", tags=["system"])
async def health() -> dict[str, str]:
    """Liveness check for Docker and the load balancer. Public, returns no data."""
    return {"status": "ok"}

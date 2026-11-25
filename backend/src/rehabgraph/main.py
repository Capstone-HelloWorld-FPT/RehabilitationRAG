"""FastAPI app entry point. Module routers are mounted here as they are written."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rehabgraph.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title="RehabGraph-RAG API", version="0.1.0")
    # The frontend (Vercel) and the API (Railway) are on different domains.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,  # refresh token cookie (BACKEND-ARCHITECTURE section 6.1)
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/v1/health", tags=["system"])
    async def health() -> dict[str, str]:
        """Liveness check for Docker and Railway. Public, returns no data."""
        return {"status": "ok"}

    return app


app = create_app()

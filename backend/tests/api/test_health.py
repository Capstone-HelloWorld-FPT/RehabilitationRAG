import httpx

from rehabgraph.config import Settings
from rehabgraph.main import create_app

FRONTEND = "https://rehabgraph-test.vercel.app"


def client(origins: list[str]) -> httpx.AsyncClient:
    app = create_app(Settings(cors_origins=origins))
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def test_health_returns_ok_without_login() -> None:
    async with client([FRONTEND]) as c:
        response = await c.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_cors_allows_the_configured_frontend() -> None:
    async with client([FRONTEND]) as c:
        response = await c.options(
            "/api/v1/health",
            headers={"Origin": FRONTEND, "Access-Control-Request-Method": "GET"},
        )
    assert response.headers["access-control-allow-origin"] == FRONTEND


async def test_cors_blocks_other_origins() -> None:
    async with client([FRONTEND]) as c:
        response = await c.get("/api/v1/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in response.headers

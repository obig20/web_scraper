"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import text
from starlette.responses import Response

from app.api.v1.router import api_router
from app.config import get_settings
from app.core.database import engine, Base
from app.core.elasticsearch import close_es_client
from app.core.logging import setup_logging
from app.search.service import SearchService

settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

REQUEST_COUNT = Counter("chre_http_requests_total", "Total HTTP requests", ["method", "endpoint"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        search = SearchService()
        await search.ensure_index()
    except Exception:
        pass  # ES may not be ready at startup
    yield
    await close_es_client()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="AI-powered research platform for crime, mystery, paranormal, and horror content",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    response = await call_next(request)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    return response


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.app_name}


@app.get("/health/ready")
async def readiness():
    checks = {}
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"
    return JSONResponse(
        content={"status": "ready" if all(v == "ok" for v in checks.values()) else "degraded", "checks": checks}
    )


if settings.prometheus_enabled:

    @app.get("/metrics")
    async def metrics():
        return Response(content=generate_latest(), media_type="text/plain")


app.include_router(api_router, prefix=settings.api_v1_prefix)

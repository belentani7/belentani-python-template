from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from structlog import get_logger

from {{cookiecutter.project_slug}}.config.settings import get_settings
from {{cookiecutter.project_slug}}.interfaces.api.v1 import router as api_v1_router

logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión de ciclo de vida — startup/shutdown."""
    logger.info("starting_application", app_name=settings.app_name, environment=settings.environment)
    # TODO: Inicializar conexiones DB, Redis, Sentry, OTEL
    yield
    logger.info("shutting_down_application")
    # TODO: Cerrar conexiones


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("unhandled_exception", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error" if not settings.debug else str(exc)},
        )

    # Health check
    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok", "service": settings.app_name, "environment": settings.environment}

    # API routes
    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app();

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "{{cookiecutter.project_slug}}.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    );

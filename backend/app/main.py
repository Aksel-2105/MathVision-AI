from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.analysis import router as analysis_router
from app.api.routes.experiments import comparison_router
from app.api.routes.experiments import router as experiments_router
from app.api.routes.health import router as health_router
from app.api.routes.images import router as images_router
from app.api.routes.mathematical_analysis import router as mathematical_analysis_router
from app.api.routes.processing import router as processing_router
from app.api.routes.recommendations import router as recommendations_router
from app.core.config import settings
from app.core.exceptions import AppError, app_error_handler
from app.core.logging import configure_logging

FRONTEND_DIST = Path("/app/frontend-dist")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging(settings.log_level)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Image upload and statistical analysis API for MathVision AI.",
    lifespan=lifespan,
)
app.add_exception_handler(AppError, app_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
    max_age=600,
)


@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(health_router, prefix="/api/v1")
app.include_router(images_router, prefix="/api/v1")
app.include_router(mathematical_analysis_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(processing_router, prefix="/api/v1")
app.include_router(experiments_router, prefix="/api/v1")
app.include_router(comparison_router, prefix="/api/v1")
app.include_router(recommendations_router, prefix="/api/v1")

if (FRONTEND_DIST / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="frontend-assets",
    )


@app.get("/{path:path}", include_in_schema=False)
async def serve_frontend(path: str) -> FileResponse:
    """Serve the compiled SPA when running the single-service production image."""
    if not FRONTEND_DIST.is_dir() or not (FRONTEND_DIST / "index.html").is_file():
        raise HTTPException(status_code=404, detail="Frontend build is not installed")

    frontend_root = FRONTEND_DIST.resolve()
    requested_path = (FRONTEND_DIST / path).resolve()
    try:
        requested_path.relative_to(frontend_root)
    except ValueError as error:
        raise HTTPException(
            status_code=404, detail="Frontend asset not found"
        ) from error

    if requested_path.is_file():
        return FileResponse(requested_path)
    return FileResponse(FRONTEND_DIST / "index.html")

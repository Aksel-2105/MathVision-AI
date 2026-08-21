from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from app.core.config import settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str
    service: str
    version: str
    phase: str
    timestamp: datetime


@router.get(
    "/health", response_model=HealthResponse, summary="Check API process health"
)
def health_check() -> HealthResponse:
    """Return an honest process-level health response without requiring image work."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        phase="foundation",
        timestamp=datetime.now(UTC),
    )

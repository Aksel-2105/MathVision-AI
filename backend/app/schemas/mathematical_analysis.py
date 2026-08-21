from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MathematicalAnalysisResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    image_id: str
    analysis_version: str
    status: str
    computed_at: datetime
    duration_ms: float = Field(ge=0)
    progress: list[dict[str, Any]]
    source: dict[str, Any]
    overview: dict[str, Any]
    matrix: dict[str, Any]
    statistics: dict[str, Any]
    probability: dict[str, Any]
    histograms: dict[str, Any]
    gradients: dict[str, Any]
    frequency: dict[str, Any]
    dct: dict[str, Any]
    wavelets: dict[str, Any]
    svd: dict[str, Any]
    color: dict[str, Any]
    texture: dict[str, Any]
    noise: dict[str, Any]
    local_maps: dict[str, Any]
    geometry: dict[str, Any]
    compression: dict[str, Any]
    report: dict[str, Any]

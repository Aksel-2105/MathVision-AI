from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.processing import AlgorithmName, ParameterValue, QualityMetrics


class ExperimentCreateRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    image_id: str
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)


class ExperimentRunRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    processing_id: str


class ExperimentRunResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    processing_id: str
    algorithm: AlgorithmName
    parameters: dict[str, ParameterValue]
    metrics: QualityMetrics
    output_url: str
    created_at: str


class ExperimentSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    description: str | None
    source_image_id: str
    source_image_name: str
    created_at: str
    updated_at: str
    run_count: int = Field(ge=0)


class ExperimentDetail(ExperimentSummary):
    runs: list[ExperimentRunResponse]


class ExperimentListResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    experiments: list[ExperimentSummary]


class ComparisonRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    processing_ids: list[str] = Field(min_length=2, max_length=20)


class ComparisonRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    processing_id: str
    algorithm: AlgorithmName
    parameters: dict[str, ParameterValue]
    metrics: QualityMetrics
    output_url: str
    rank: int = Field(gt=0)
    ranking_score: float = Field(ge=0, le=1)


class ComparisonResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_image_id: str
    rows: list[ComparisonRow]
    ranking_policy: str


ExportFormat = Literal["json", "csv"]

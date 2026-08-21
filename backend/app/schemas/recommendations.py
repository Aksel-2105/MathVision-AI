from pydantic import BaseModel, ConfigDict, Field

from app.schemas.processing import AlgorithmName


class TrainingResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    model_version: str
    trained_at: str
    sample_count: int = Field(gt=0)
    class_count: int = Field(gt=0)
    classes: list[AlgorithmName]
    validation_accuracy: float | None = Field(default=None, ge=0, le=1)
    validation_method: str
    feature_names: list[str]
    limitations: list[str]


class ModelStatusResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    trained: bool
    model_version: str | None = None
    trained_at: str | None = None
    sample_count: int = Field(default=0, ge=0)
    class_count: int = Field(default=0, ge=0)
    classes: list[AlgorithmName] = Field(default_factory=list)
    validation_accuracy: float | None = Field(default=None, ge=0, le=1)
    validation_method: str | None = None
    feature_names: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class RecommendationRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    image_id: str


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    image_id: str
    model_version: str
    recommended_algorithm: AlgorithmName
    confidence: float = Field(ge=0, le=1)
    probabilities: dict[AlgorithmName, float]
    features: dict[str, float]
    feature_importance: dict[str, float]
    explanation: str
    limitations: list[str]
    generated_at: str

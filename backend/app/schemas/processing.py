from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AlgorithmName = Literal[
    "median",
    "gaussian",
    "bilateral",
    "nlm",
    "wavelet",
    "wiener",
    "contrast_stretch",
    "histogram_equalization",
    "clahe",
    "dct_compression",
    "wavelet_compression",
    "svd_compression",
]
ParameterValue = str | int | float | bool


class ProcessingRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    image_id: str
    algorithm: AlgorithmName
    parameters: dict[str, ParameterValue] = Field(default_factory=dict)


class AlgorithmInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: AlgorithmName
    label: str
    category: Literal["denoising", "enhancement", "compression"]
    description: str
    defaults: dict[str, ParameterValue] = Field(default_factory=dict)


class AlgorithmListResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    algorithms: list[AlgorithmInfo]


class QualityMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)

    mse: float = Field(ge=0)
    rmse: float = Field(ge=0)
    psnr: float | None = Field(default=None, ge=0)
    psnr_note: str | None = None
    ssim: float | None = Field(default=None, ge=-1, le=1)
    ssim_note: str | None = None
    original_size_bytes: int = Field(gt=0)
    output_size_bytes: int = Field(gt=0)
    compression_ratio: float = Field(gt=0)
    size_reduction_percent: float
    execution_time_ms: float = Field(ge=0)
    retained_coefficient_ratio: float | None = Field(default=None, ge=0, le=1)
    representation_type: Literal["encoded_output", "mathematical_simulation"]


class ProcessingResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    image_id: str
    algorithm: AlgorithmName
    parameters: dict[str, ParameterValue]
    output_url: str
    output_format: str
    output_size_bytes: int = Field(gt=0)
    created_at: str
    metrics: QualityMetrics

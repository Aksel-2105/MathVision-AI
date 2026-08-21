from pydantic import BaseModel, ConfigDict, Field


class HistogramSeries(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    values: list[int]


class HistogramData(BaseModel):
    model_config = ConfigDict(frozen=True)

    bins: list[int]
    series: list[HistogramSeries]
    unit: str = "pixel_count"


class NoiseEstimate(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: str
    level: float = Field(ge=0, le=1)
    method: str
    limitations: str


class ImageFeatures(BaseModel):
    model_config = ConfigDict(frozen=True)

    width: int = Field(gt=0)
    height: int = Field(gt=0)
    channels: int = Field(gt=0)
    color_mode: str
    file_size_bytes: int = Field(gt=0)
    aspect_ratio: float = Field(gt=0)
    min_intensity: float
    max_intensity: float
    mean_intensity: float
    median_intensity: float
    variance: float = Field(ge=0)
    standard_deviation: float = Field(ge=0)
    dynamic_range: float = Field(ge=0)
    rms_contrast: float = Field(ge=0)
    entropy: float = Field(ge=0)
    edge_density: float = Field(ge=0, le=1)
    laplacian_variance: float = Field(ge=0)
    sharpness_estimate: float = Field(ge=0)
    brightness: float = Field(ge=0, le=1)
    saturation: float = Field(ge=0, le=1)
    gradient_mean: float = Field(ge=0)
    gradient_standard_deviation: float = Field(ge=0)
    high_frequency_energy: float = Field(ge=0)


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    image_id: str
    analysis_version: str
    features: ImageFeatures
    histogram: HistogramData
    noise_estimate: NoiseEstimate

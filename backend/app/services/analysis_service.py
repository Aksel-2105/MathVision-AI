from uuid import uuid4

from app.core.exceptions import AppError
from app.imaging.features import extract_features
from app.imaging.io import load_image_array
from app.schemas.analysis import AnalysisResponse
from app.services.image_service import StoredImage


class AnalysisStore:
    def __init__(self) -> None:
        self._records: dict[str, AnalysisResponse] = {}

    def create(self, image: StoredImage) -> AnalysisResponse:
        array = load_image_array(image.path)
        features, histogram, noise_estimate = extract_features(
            array,
            width=image.width,
            height=image.height,
            channels=image.channels,
            color_mode=image.color_mode,
            file_size_bytes=image.size_bytes,
        )
        response = AnalysisResponse(
            id=str(uuid4()),
            image_id=image.id,
            analysis_version="2.0.0",
            features=features,
            histogram=histogram,
            noise_estimate=noise_estimate,
        )
        self._records[response.id] = response
        return response

    def get(self, analysis_id: str) -> AnalysisResponse:
        response = self._records.get(analysis_id)
        if response is None:
            raise AppError(
                "analysis_not_found",
                "The requested analysis was not found.",
                404,
            )
        return response

    def clear(self) -> None:
        self._records.clear()


analysis_store = AnalysisStore()


def analyze_image(image: StoredImage) -> AnalysisResponse:
    return analysis_store.create(image)

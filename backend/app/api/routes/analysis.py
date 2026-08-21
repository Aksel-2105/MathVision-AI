from fastapi import APIRouter, status

from app.schemas.analysis import AnalysisResponse
from app.services.analysis_service import analysis_store, analyze_image
from app.services.image_service import get_validated_image

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post(
    "/{image_id}",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Extract mathematical and statistical image features",
)
def create_analysis(image_id: str) -> AnalysisResponse:
    return analyze_image(get_validated_image(image_id))


@router.get(
    "/{analysis_id}",
    response_model=AnalysisResponse,
    summary="Read a completed image analysis",
)
def get_analysis(analysis_id: str) -> AnalysisResponse:
    return analysis_store.get(analysis_id)

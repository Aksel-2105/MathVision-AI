from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.recommendations import (
    ModelStatusResponse,
    RecommendationRequest,
    RecommendationResponse,
    TrainingResponse,
)
from app.services.recommendation_service import recommendation_model_store

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/model", response_model=ModelStatusResponse)
def get_model_status() -> ModelStatusResponse:
    return recommendation_model_store.status()


@router.post(
    "/train", response_model=TrainingResponse, status_code=status.HTTP_201_CREATED
)
def train_model(db: Session = Depends(get_db)) -> TrainingResponse:  # noqa: B008
    return recommendation_model_store.train(db)


@router.post("", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest) -> RecommendationResponse:
    return recommendation_model_store.recommend(request.image_id)

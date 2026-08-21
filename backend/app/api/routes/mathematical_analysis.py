import csv
import io
import json

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse, StreamingResponse

from app.core.exceptions import AppError
from app.schemas.mathematical_analysis import MathematicalAnalysisResponse
from app.services.image_service import get_validated_image
from app.services.mathematical_analysis_service import mathematical_analysis_service

router = APIRouter(prefix="/mathematical-analysis", tags=["mathematical-analysis"])


@router.post(
    "/{image_id}",
    response_model=MathematicalAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run advanced mathematical image analysis",
)
def run_mathematical_analysis(
    image_id: str,
    grid_size: int = Query(default=4, ge=4, le=16),
) -> MathematicalAnalysisResponse:
    if grid_size not in {4, 8, 16}:
        raise AppError(
            "invalid_mathematical_grid",
            "grid_size must be one of 4, 8, or 16.",
            422,
        )
    image = get_validated_image(image_id)
    return mathematical_analysis_service.analyze(image_id, image.path, grid_size)


@router.get(
    "/{analysis_id}",
    response_model=MathematicalAnalysisResponse,
    summary="Read a cached mathematical analysis",
)
def get_mathematical_analysis(analysis_id: str) -> MathematicalAnalysisResponse:
    result = mathematical_analysis_service.get(analysis_id)
    if result is None:
        raise AppError(
            "mathematical_analysis_not_found",
            "The requested mathematical analysis was not found.",
            404,
        )
    return result


@router.get(
    "/{analysis_id}/export",
    response_model=None,
    summary="Export a mathematical analysis report",
)
def export_mathematical_analysis(
    analysis_id: str,
    format: str = Query(default="json", pattern="^(json|csv)$"),
) -> JSONResponse | StreamingResponse:
    result = mathematical_analysis_service.get(analysis_id)
    if result is None:
        raise AppError(
            "mathematical_analysis_not_found",
            "The requested mathematical analysis was not found.",
            404,
        )
    payload = result.model_dump(mode="json")
    if format == "json":
        return JSONResponse(
            payload,
            headers={
                "Content-Disposition": f'attachment; filename="mathvision-{analysis_id}.json"'
            },
        )
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["section", "metric", "value"])
    for section, values in payload.items():
        if isinstance(values, dict):
            for metric, value in values.items():
                writer.writerow([section, metric, json.dumps(value, ensure_ascii=True)])
        else:
            writer.writerow(
                ["metadata", section, json.dumps(values, ensure_ascii=True)]
            )
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="mathvision-{analysis_id}.csv"'
        },
    )

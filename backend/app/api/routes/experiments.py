from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.experiments import (
    ComparisonRequest,
    ComparisonResponse,
    ExperimentCreateRequest,
    ExperimentDetail,
    ExperimentListResponse,
    ExperimentRunRequest,
    ExperimentRunResponse,
    ExperimentSummary,
)
from app.services.experiment_service import (
    add_run,
    compare_experiment,
    compare_processing,
    create_experiment,
    delete_experiment,
    export_experiment,
    get_experiment,
    list_experiments,
)

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.post("", response_model=ExperimentSummary, status_code=status.HTTP_201_CREATED)
def create_experiment_route(
    request: ExperimentCreateRequest, db: Session = Depends(get_db)
) -> ExperimentSummary:
    return create_experiment(db, request.image_id, request.name, request.description)


@router.get("", response_model=ExperimentListResponse)
def list_experiments_route(
    image_id: str | None = Query(default=None), db: Session = Depends(get_db)
) -> ExperimentListResponse:
    return ExperimentListResponse(experiments=list_experiments(db, image_id))


@router.get("/{experiment_id}", response_model=ExperimentDetail)
def get_experiment_route(
    experiment_id: str, db: Session = Depends(get_db)
) -> ExperimentDetail:
    return get_experiment(db, experiment_id)


@router.post(
    "/{experiment_id}/runs", response_model=ExperimentRunResponse, status_code=201
)
def add_run_route(
    experiment_id: str, request: ExperimentRunRequest, db: Session = Depends(get_db)
) -> ExperimentRunResponse:
    return add_run(db, experiment_id, request.processing_id)


@router.get("/{experiment_id}/comparison", response_model=ComparisonResponse)
def compare_experiment_route(
    experiment_id: str, db: Session = Depends(get_db)
) -> ComparisonResponse:
    return compare_experiment(db, experiment_id)


@router.get("/{experiment_id}/export")
def export_experiment_route(
    experiment_id: str,
    file_format: str = Query(default="json", alias="format"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    content, media_type = export_experiment(db, experiment_id, file_format)
    extension = "csv" if file_format == "csv" else "json"
    content_disposition = f'attachment; filename="mathvision-experiment.{extension}"'
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={"Content-Disposition": content_disposition},
    )


@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experiment_route(
    experiment_id: str, db: Session = Depends(get_db)
) -> Response:
    delete_experiment(db, experiment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


comparison_router = APIRouter(prefix="/comparisons", tags=["comparisons"])


@comparison_router.post("", response_model=ComparisonResponse)
def compare_processing_route(request: ComparisonRequest) -> ComparisonResponse:
    return compare_processing(request.processing_ids)

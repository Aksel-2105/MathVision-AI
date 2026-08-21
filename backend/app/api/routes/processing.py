from fastapi import APIRouter, status
from fastapi.responses import FileResponse

from app.imaging.algorithms import list_algorithms
from app.schemas.processing import (
    AlgorithmListResponse,
    ProcessingRequest,
    ProcessingResponse,
)
from app.services.image_service import get_validated_image
from app.services.processing_service import process_uploaded_image, processing_store

router = APIRouter(prefix="/processing", tags=["processing"])


@router.get(
    "/algorithms",
    response_model=AlgorithmListResponse,
    summary="List supported image-processing algorithms",
)
def get_algorithms() -> AlgorithmListResponse:
    return AlgorithmListResponse(algorithms=list_algorithms())


@router.post(
    "",
    response_model=ProcessingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Process an uploaded image and calculate quality metrics",
)
def create_processing(request: ProcessingRequest) -> ProcessingResponse:
    return process_uploaded_image(
        get_validated_image(request.image_id), request.algorithm, request.parameters
    )


@router.get(
    "/{processing_id}",
    response_model=ProcessingResponse,
    summary="Read a completed processing result",
)
def get_processing(processing_id: str) -> ProcessingResponse:
    return processing_store.get(processing_id).response


@router.get(
    "/{processing_id}/content",
    response_class=FileResponse,
    summary="Download a processed PNG image",
)
def get_processing_content(processing_id: str) -> FileResponse:
    record = processing_store.get(processing_id)
    return FileResponse(
        record.path, media_type="image/png", filename=f"{processing_id}.png"
    )

from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.images import ImageUploadResponse
from app.services.image_service import image_store

router = APIRouter(prefix="/images", tags=["images"])


@router.post(
    "/upload",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Validate and store an image upload",
)
async def upload_image(file: UploadFile = File(...)) -> ImageUploadResponse:  # noqa: B008
    data = await file.read(settings.max_upload_size_bytes + 1)
    try:
        stored = image_store.save(file.filename or "", file.content_type, data)
    finally:
        await file.close()
    return stored.to_response()


@router.get(
    "/{image_id}",
    response_model=ImageUploadResponse,
    summary="Read stored image metadata",
)
def get_image(image_id: str) -> ImageUploadResponse:
    return image_store.get(image_id).to_response()


@router.get("/{image_id}/content", summary="Read stored image content")
def get_image_content(image_id: str) -> FileResponse:
    image = image_store.get(image_id)
    return FileResponse(
        image.path,
        media_type=image.mime_type,
        filename=image.safe_name,
    )


@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a stored image",
)
def delete_image(image_id: str) -> None:
    image_store.delete(image_id)

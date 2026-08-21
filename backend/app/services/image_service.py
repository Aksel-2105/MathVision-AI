from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.core.exceptions import AppError
from app.imaging.io import validate_image_bytes
from app.schemas.images import ImageUploadResponse


@dataclass(frozen=True)
class StoredImage:
    id: str
    original_name: str
    safe_name: str
    path: Path
    content_hash: str
    mime_type: str
    format: str
    width: int
    height: int
    channels: int
    color_mode: str
    size_bytes: int
    created_at: datetime
    expires_at: datetime

    def to_response(self) -> ImageUploadResponse:
        return ImageUploadResponse(
            id=self.id,
            original_name=self.original_name,
            content_hash=self.content_hash,
            mime_type=self.mime_type,
            format=self.format,
            width=self.width,
            height=self.height,
            channels=self.channels,
            color_mode=self.color_mode,
            size_bytes=self.size_bytes,
            created_at=self.created_at,
            expires_at=self.expires_at,
            content_url=f"/api/v1/images/{self.id}/content",
        )


class ImageStore:
    """Phase 2 filesystem store with process metadata and expiry cleanup."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)
        self._records: dict[str, StoredImage] = {}

    def _purge_expired(self) -> None:
        now = datetime.now(UTC)
        expired = [
            image_id
            for image_id, image in self._records.items()
            if image.expires_at <= now
        ]
        for image_id in expired:
            image = self._records.pop(image_id)
            image.path.unlink(missing_ok=True)

    def save(self, filename: str, content_type: str | None, data: bytes) -> StoredImage:
        self._purge_expired()
        validated = validate_image_bytes(filename, content_type, data)
        image_id = str(uuid4())
        safe_name = f"{image_id}{validated.extension}"
        path = self.directory / safe_name
        path.write_bytes(data)
        now = datetime.now(UTC)
        record = StoredImage(
            id=image_id,
            original_name=filename,
            safe_name=safe_name,
            path=path,
            content_hash=sha256(data).hexdigest(),
            mime_type=validated.mime_type,
            format=validated.format,
            width=validated.width,
            height=validated.height,
            channels=validated.channels,
            color_mode=validated.color_mode,
            size_bytes=len(data),
            created_at=now,
            expires_at=now + timedelta(hours=settings.retention_hours),
        )
        self._records[image_id] = record
        return record

    def get(self, image_id: str) -> StoredImage:
        self._purge_expired()
        image = self._records.get(image_id)
        if image is None:
            raise AppError("image_not_found", "The requested image was not found.", 404)
        if not image.path.is_file():
            self._records.pop(image_id, None)
            raise AppError("image_not_found", "The requested image was not found.", 404)
        return image

    def delete(self, image_id: str) -> None:
        image = self.get(image_id)
        image.path.unlink(missing_ok=True)
        self._records.pop(image_id, None)

    def clear(self) -> None:
        for image in self._records.values():
            image.path.unlink(missing_ok=True)
        self._records.clear()


image_store = ImageStore(settings.upload_dir)


def get_validated_image(image_id: str) -> StoredImage:
    return image_store.get(image_id)

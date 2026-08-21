from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageFile, UnidentifiedImageError

from app.core.config import settings
from app.core.exceptions import AppError

ImageFile.LOAD_TRUNCATED_IMAGES = False
Image.MAX_IMAGE_PIXELS = settings.max_image_pixels

ALLOWED_FORMATS: dict[str, tuple[str, ...]] = {
    ".png": ("PNG", "image/png"),
    ".jpg": ("JPEG", "image/jpeg"),
    ".jpeg": ("JPEG", "image/jpeg"),
    ".bmp": ("BMP", "image/bmp"),
    ".tif": ("TIFF", "image/tiff"),
    ".tiff": ("TIFF", "image/tiff"),
    ".webp": ("WEBP", "image/webp"),
}


@dataclass(frozen=True)
class ValidatedImage:
    format: str
    mime_type: str
    extension: str
    width: int
    height: int
    channels: int
    color_mode: str


def _channel_count(image: Image.Image) -> int:
    return len(image.getbands())


def validate_image_bytes(
    filename: str,
    content_type: str | None,
    data: bytes,
) -> ValidatedImage:
    if not filename or Path(filename).name != filename:
        raise AppError(
            "invalid_filename",
            "The uploaded filename is invalid.",
            400,
        )
    if len(data) == 0:
        raise AppError("empty_file", "The uploaded file is empty.", 400)
    if len(data) > settings.max_upload_size_bytes:
        raise AppError(
            "file_too_large",
            "The image exceeds the maximum upload size.",
            413,
            {"max_bytes": settings.max_upload_size_bytes},
        )

    extension = Path(filename).suffix.lower()
    allowed = ALLOWED_FORMATS.get(extension)
    if allowed is None:
        raise AppError(
            "unsupported_file_type",
            "This file type is not supported. Use PNG, JPEG, BMP, TIFF, or WEBP.",
            415,
        )

    expected_format, expected_mime = allowed
    try:
        with Image.open(BytesIO(data)) as image:
            image.verify()
        with Image.open(BytesIO(data)) as image:
            image.load()
            actual_format = (image.format or "").upper()
            width, height = image.size
            channels = _channel_count(image)
            color_mode = image.mode
    except Image.DecompressionBombError as error:
        raise AppError(
            "image_dimensions_too_large",
            "The image dimensions exceed the configured safety limit.",
            413,
            {"max_pixels": settings.max_image_pixels},
        ) from error
    except (UnidentifiedImageError, OSError, ValueError) as error:
        raise AppError(
            "corrupted_image",
            "The uploaded file could not be decoded as a valid image.",
            400,
        ) from error

    if width * height > settings.max_image_pixels:
        raise AppError(
            "image_dimensions_too_large",
            "The image dimensions exceed the configured safety limit.",
            413,
            {"max_pixels": settings.max_image_pixels},
        )
    if actual_format != expected_format:
        raise AppError(
            "format_mismatch",
            "The file extension does not match the decoded image format.",
            400,
        )
    if content_type and content_type not in {expected_mime, "application/octet-stream"}:
        raise AppError(
            "mime_type_mismatch",
            "The declared MIME type does not match the decoded image.",
            415,
            {"expected": expected_mime},
        )

    return ValidatedImage(
        format=actual_format,
        mime_type=expected_mime,
        extension=extension,
        width=width,
        height=height,
        channels=channels,
        color_mode=color_mode,
    )


def load_image_array(path: Path) -> np.ndarray:
    try:
        with Image.open(path) as image:
            if image.mode in {"1", "L", "I", "F", "I;16"}:
                image = image.convert("L")
            else:
                image = image.convert("RGB")
            image.load()
            return np.asarray(image).copy()
    except (UnidentifiedImageError, OSError, ValueError) as error:
        raise AppError(
            "stored_image_unreadable",
            "The stored image is no longer readable.",
            500,
        ) from error

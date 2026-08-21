from dataclasses import dataclass
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from time import perf_counter
from uuid import uuid4

import numpy as np
from PIL import Image

from app.core.config import settings
from app.core.exceptions import AppError
from app.imaging.algorithms import process_image
from app.imaging.io import load_image_array
from app.mathematics.metrics import calculate_quality_metrics
from app.schemas.processing import (
    AlgorithmName,
    ParameterValue,
    ProcessingResponse,
    QualityMetrics,
)
from app.services.image_service import StoredImage


@dataclass(frozen=True)
class StoredProcessing:
    response: ProcessingResponse
    path: Path


class ProcessingStore:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)
        self._records: dict[str, StoredProcessing] = {}

    def create(
        self,
        image: StoredImage,
        algorithm: AlgorithmName,
        parameters: dict[str, ParameterValue],
    ) -> ProcessingResponse:
        original = load_image_array(image.path)
        started = perf_counter()
        processed = process_image(original, algorithm, parameters)
        quality = calculate_quality_metrics(original, processed.array)
        output_id = str(uuid4())
        output_path = self.directory / f"{output_id}.png"
        self._write_png(processed.array, output_path)
        output_size = output_path.stat().st_size
        execution_time_ms = (perf_counter() - started) * 1000
        response = ProcessingResponse(
            id=output_id,
            image_id=image.id,
            algorithm=algorithm,
            parameters=parameters,
            output_url=f"/api/v1/processing/{output_id}/content",
            output_format="PNG",
            output_size_bytes=output_size,
            created_at=datetime.now(UTC).isoformat(),
            metrics=QualityMetrics(
                mse=quality.mse,
                rmse=quality.rmse,
                psnr=quality.psnr,
                psnr_note=quality.psnr_note,
                ssim=quality.ssim,
                ssim_note=quality.ssim_note,
                original_size_bytes=image.size_bytes,
                output_size_bytes=output_size,
                compression_ratio=image.size_bytes / output_size,
                size_reduction_percent=(1 - output_size / image.size_bytes) * 100,
                execution_time_ms=execution_time_ms,
                retained_coefficient_ratio=processed.retained_coefficient_ratio,
                representation_type=processed.representation_type,
            ),
        )
        self._records[output_id] = StoredProcessing(response, output_path)
        return response

    @staticmethod
    def _write_png(array: np.ndarray, path: Path) -> None:
        try:
            image = Image.fromarray(array)
            buffer = BytesIO()
            image.save(buffer, format="PNG", optimize=True)
            path.write_bytes(buffer.getvalue())
        except (OSError, ValueError, TypeError) as error:
            raise AppError(
                "processing_output_failed",
                "The processed image could not be encoded.",
                500,
            ) from error

    def get(self, processing_id: str) -> StoredProcessing:
        record = self._records.get(processing_id)
        if record is None or not record.path.is_file():
            raise AppError(
                "processing_not_found",
                "The requested processing result was not found.",
                404,
            )
        return record

    def clear(self) -> None:
        for record in self._records.values():
            record.path.unlink(missing_ok=True)
        self._records.clear()


processing_store = ProcessingStore(settings.processed_dir)


def process_uploaded_image(
    image: StoredImage,
    algorithm: AlgorithmName,
    parameters: dict[str, ParameterValue],
) -> ProcessingResponse:
    return processing_store.create(image, algorithm, parameters)

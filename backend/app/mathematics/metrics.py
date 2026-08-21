from dataclasses import dataclass

import cv2
import numpy as np

from app.core.exceptions import AppError


@dataclass(frozen=True)
class ImageQualityMetrics:
    mse: float
    rmse: float
    psnr: float | None
    psnr_note: str | None
    ssim: float | None
    ssim_note: str | None


def _validate_pair(original: np.ndarray, processed: np.ndarray) -> None:
    if original.shape != processed.shape:
        raise AppError(
            "metric_shape_mismatch",
            "The original and processed images must have the same shape.",
            422,
        )
    if original.ndim not in {2, 3}:
        raise AppError(
            "metric_invalid_image",
            "Quality metrics require a grayscale or RGB image.",
            422,
        )


def _ssim_window(original: np.ndarray) -> int | None:
    height, width = original.shape[:2]
    window = min(7, height, width)
    if window % 2 == 0:
        window -= 1
    return window if window >= 3 else None


def calculate_quality_metrics(
    original: np.ndarray,
    processed: np.ndarray,
) -> ImageQualityMetrics:
    _validate_pair(original, processed)
    original_float: np.ndarray = original.astype(np.float64)
    processed_float: np.ndarray = processed.astype(np.float64)
    mse = float(np.mean(np.square(original_float - processed_float)))
    rmse = float(np.sqrt(mse))
    if mse == 0:
        psnr = None
        psnr_note = "identical_images"
    else:
        psnr = float(10 * np.log10((255.0**2) / mse))
        psnr_note = None

    window = _ssim_window(original)
    if window is None:
        ssim = None
        ssim_note = "image_too_small_for_ssim"
    else:
        if original.ndim == 3:
            original_float = np.mean(original_float, axis=2)
            processed_float = np.mean(processed_float, axis=2)
        kernel = (window, window)
        mu_original = cv2.GaussianBlur(original_float, kernel, 1.5)
        mu_processed = cv2.GaussianBlur(processed_float, kernel, 1.5)
        sigma_original = (
            cv2.GaussianBlur(original_float**2, kernel, 1.5) - mu_original**2
        )
        sigma_processed = (
            cv2.GaussianBlur(processed_float**2, kernel, 1.5) - mu_processed**2
        )
        sigma_cross = (
            cv2.GaussianBlur(original_float * processed_float, kernel, 1.5)
            - mu_original * mu_processed
        )
        c1 = 6.5025
        c2 = 58.5225
        score = ((2 * mu_original * mu_processed + c1) * (2 * sigma_cross + c2)) / (
            (mu_original**2 + mu_processed**2 + c1)
            * (sigma_original + sigma_processed + c2)
        )
        ssim = float(np.mean(score))
        ssim_note = None
    return ImageQualityMetrics(mse, rmse, psnr, psnr_note, ssim, ssim_note)

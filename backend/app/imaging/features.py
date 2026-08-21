from typing import Literal

import cv2
import numpy as np

from app.schemas.analysis import (
    HistogramData,
    HistogramSeries,
    ImageFeatures,
    NoiseEstimate,
)

HistogramLabel = Literal["Grayscale", "Red", "Green", "Blue"]


def _grayscale(array: np.ndarray) -> np.ndarray:
    if array.ndim == 2:
        return array.astype(np.uint8, copy=False)
    return cv2.cvtColor(array.astype(np.uint8), cv2.COLOR_RGB2GRAY)


def _histogram(array: np.ndarray) -> HistogramData:
    bins = list(range(256))
    if array.ndim == 2:
        values, _ = np.histogram(array, bins=256, range=(0, 256))
        series = [
            HistogramSeries(label="Grayscale", values=values.astype(int).tolist())
        ]
    else:
        labels: tuple[HistogramLabel, ...] = ("Red", "Green", "Blue")
        series = []
        for index, label in enumerate(labels):
            values, _ = np.histogram(array[:, :, index], bins=256, range=(0, 256))
            series.append(
                HistogramSeries(label=label, values=values.astype(int).tolist())
            )
    return HistogramData(bins=bins, series=series)


def _entropy(gray: np.ndarray) -> float:
    values, _ = np.histogram(gray, bins=256, range=(0, 256))
    probabilities = values.astype(np.float64) / gray.size
    nonzero = probabilities[probabilities > 0]
    return float(max(0.0, -np.sum(nonzero * np.log2(nonzero))))


def _saturation(array: np.ndarray) -> float:
    if array.ndim == 2:
        return 0.0
    hsv = cv2.cvtColor(array.astype(np.uint8), cv2.COLOR_RGB2HSV)
    return float(np.mean(hsv[:, :, 1]) / 255.0)


def extract_features(
    array: np.ndarray,
    *,
    width: int,
    height: int,
    channels: int,
    color_mode: str,
    file_size_bytes: int,
) -> tuple[ImageFeatures, HistogramData, NoiseEstimate]:
    gray = _grayscale(array)
    gray_float = gray.astype(np.float64)
    mean = float(np.mean(gray_float))
    standard_deviation = float(np.std(gray_float))
    minimum = float(np.min(gray_float))
    maximum = float(np.max(gray_float))
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    edges = cv2.Canny(gray, 100, 200)
    gradient_x = cv2.Sobel(gray_float, cv2.CV_64F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(gray_float, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    residual = gray_float - blurred.astype(np.float64)
    noise_level = float(np.clip(np.std(residual) / 255.0, 0.0, 1.0))
    impulse_ratio = float(np.mean((gray <= 2) | (gray >= 253)))
    if impulse_ratio >= 0.02:
        noise_type = "possible_impulse"
    elif noise_level >= 0.08:
        noise_type = "possible_high_frequency"
    else:
        noise_type = "none_detected"

    features = ImageFeatures(
        width=width,
        height=height,
        channels=channels,
        color_mode=color_mode,
        file_size_bytes=file_size_bytes,
        aspect_ratio=float(width / height),
        min_intensity=minimum,
        max_intensity=maximum,
        mean_intensity=mean,
        median_intensity=float(np.median(gray_float)),
        variance=float(np.var(gray_float)),
        standard_deviation=standard_deviation,
        dynamic_range=maximum - minimum,
        rms_contrast=standard_deviation,
        entropy=_entropy(gray),
        edge_density=float(np.count_nonzero(edges) / edges.size),
        laplacian_variance=float(np.var(laplacian)),
        sharpness_estimate=float(np.var(laplacian)),
        brightness=float(mean / 255.0),
        saturation=_saturation(array),
        gradient_mean=float(np.mean(gradient_magnitude)),
        gradient_standard_deviation=float(np.std(gradient_magnitude)),
        high_frequency_energy=float(np.mean(np.square(laplacian / 255.0))),
    )
    noise = NoiseEstimate(
        type=noise_type,
        level=noise_level,
        method="3x3 Gaussian residual and impulse-pixel ratio heuristic",
        limitations=(
            "This is a no-reference estimate; it is not a trained classifier "
            "and has no clean-image ground truth."
        ),
    )
    return features, _histogram(array), noise

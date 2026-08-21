# mypy: ignore-errors
from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

import cv2
import numpy as np

from app.imaging.io import load_image_array
from app.mathematics.compression_potential import compute_compression_potential
from app.mathematics.dct_analysis import compute_dct
from app.mathematics.descriptive_statistics import compute_descriptive_statistics
from app.mathematics.frequency_analysis import compute_fft
from app.mathematics.gradients import compute_gradients
from app.mathematics.information_theory import compute_information
from app.mathematics.linear_algebra import compute_svd
from app.mathematics.local_analysis import compute_local_maps
from app.mathematics.noise_analysis import compute_noise
from app.mathematics.probability import compute_probability
from app.mathematics.texture_analysis import compute_texture
from app.mathematics.wavelet_analysis import compute_wavelets
from app.schemas.mathematical_analysis import MathematicalAnalysisResponse


def _gray(array: np.ndarray) -> np.ndarray:
    if array.ndim == 2:
        return array
    return cv2.cvtColor(array.astype(np.uint8), cv2.COLOR_RGB2GRAY)


def _channels(array: np.ndarray, gray: np.ndarray) -> dict[str, np.ndarray]:
    if array.ndim == 2:
        return {"Grayscale": gray}
    return {
        name: array[:, :, index] for index, name in enumerate(("Red", "Green", "Blue"))
    }


def _small_matrix(array: np.ndarray, sample_size: int = 10) -> dict[str, object]:
    h, w = array.shape[:2]
    y1, x1 = min(sample_size, h), min(sample_size, w)
    if array.ndim == 2:
        sample = array[:y1, :x1].tolist()
        representation = "I ∈ R^(m×n)"
    else:
        sample = array[:y1, :x1, :3].tolist()
        representation = "I ∈ R^(m×n×3)"
    return {
        "representation": representation,
        "rows": h,
        "columns": w,
        "channels": 1 if array.ndim == 2 else 3,
        "sample_size": [y1, x1],
        "origin": {"row": 0, "column": 0},
        "values": sample,
        "coordinate_convention": "zero-based [row, column, channel]",
        "data_type": str(array.dtype),
        "bit_depth": int(array.dtype.itemsize * 8),
        "value_domain": [0, 255],
        "scalar_value_count": int(array.size),
        "memory_bytes": int(array.nbytes),
    }


def _histograms(channel_data: dict[str, np.ndarray]) -> dict[str, object]:
    output: dict[str, object] = {}
    for name, values in channel_data.items():
        counts, _ = np.histogram(values, bins=256, range=(0, 256))
        total = max(1, values.size)
        output[name] = {
            "bins": list(range(256)),
            "counts": counts.astype(int).tolist(),
            "normalized": (counts / total).tolist(),
            "cumulative": (np.cumsum(counts) / total).tolist(),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "black_clipping_ratio": float(np.mean(values == 0)),
            "white_clipping_ratio": float(np.mean(values == 255)),
        }
    return {
        "channels": output,
        "regions": {
            "shadows": [0, 64],
            "midtones": [64, 192],
            "highlights": [192, 256],
        },
        "interpretation": "Histogram shape is summarized from empirical moments; skew and multimodality are signals, not definitive scene labels.",
        "limitations": "Histogram discards spatial arrangement, so different images can share the same histogram.",
    }


def _color_analysis(
    array: np.ndarray, channels: dict[str, np.ndarray]
) -> dict[str, object]:
    if array.ndim == 2:
        return {
            "available": False,
            "reason": "The uploaded image is grayscale; RGB covariance, hue, and saturation are not defined.",
        }
    rgb = array[:, :, :3].astype(np.float64)
    covariance = np.cov(rgb.reshape(-1, 3), rowvar=False)
    correlation = np.corrcoef(rgb.reshape(-1, 3), rowvar=False)
    hsv = cv2.cvtColor(array.astype(np.uint8), cv2.COLOR_RGB2HSV)
    luminance = cv2.cvtColor(array.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    means = np.array([np.mean(values) for values in channels.values()])
    return {
        "available": True,
        "channel_means": {
            name: float(np.mean(values)) for name, values in channels.items()
        },
        "channel_entropy": {
            name: float(compute_information(values, {name: values})["entropy"])
            for name, values in channels.items()
        },
        "covariance_matrix": np.round(covariance, 5).tolist(),
        "correlation_matrix": np.round(correlation, 5).tolist(),
        "channel_dominance": list(channels.keys())[int(np.argmax(means))],
        "color_balance": {
            "red_green_difference": float(means[0] - means[1]),
            "green_blue_difference": float(means[1] - means[2]),
        },
        "mean_saturation": float(np.mean(hsv[:, :, 1]) / 255),
        "mean_hue_degrees": float(np.mean(hsv[:, :, 0]) * 2),
        "luminance_mean": float(np.mean(luminance)),
        "formula": "ρᵢⱼ = cov(Xᵢ,Xⱼ)/(σᵢσⱼ)",
        "interpretation": "Correlation near +1 indicates channels vary together; covariance retains intensity units while correlation is normalized.",
        "limitations": "Hue is unstable for low-saturation pixels and RGB correlation does not imply semantic causation.",
    }


def _geometry(gray: np.ndarray, gradients: dict[str, object]) -> dict[str, object]:
    h, w = gray.shape
    values = gray.astype(np.float64)
    total = float(np.sum(values)) or 1.0
    yy, xx = np.indices(gray.shape)
    dx = float(np.sum(xx * values) / total / max(1, w - 1))
    dy = float(np.sum(yy * values) / total / max(1, h - 1))
    flipped_h = np.fliplr(values)
    flipped_v = np.flipud(values)
    denom = max(np.linalg.norm(values), 1e-12)
    horizontal = float(1 - np.linalg.norm(values - flipped_h) / denom)
    vertical = float(1 - np.linalg.norm(values - flipped_v) / denom)
    orientation = gradients["orientation_distribution_degrees"]
    dominant = (
        max(orientation, key=lambda key: float(orientation[key]))
        if orientation
        else "0"
    )
    return {
        "aspect_ratio": float(w / h),
        "luminance_center_of_mass": {"normalized_x": dx, "normalized_y": dy},
        "horizontal_symmetry_score": max(0.0, horizontal),
        "vertical_symmetry_score": max(0.0, vertical),
        "dominant_edge_orientation_degrees": float(dominant),
        "rotation_estimate": {
            "value": None,
            "wording": "Not estimated from raster statistics alone.",
        },
        "crop_imbalance": {
            "left_right": float(abs(dx - 0.5) * 2),
            "top_bottom": float(abs(dy - 0.5) * 2),
        },
        "limitations": "Symmetry and center of mass are intensity-weighted descriptors and do not identify objects or perspective reliably.",
    }


def _overview(
    array: np.ndarray,
    gray: np.ndarray,
    stats: dict[str, object],
    info: dict[str, object],
    gradients: dict[str, object],
    noise: dict[str, object],
    compression: dict[str, object],
) -> dict[str, object]:
    global_stats = stats["global"]
    mean = float(global_stats["mean"])
    std = float(global_stats["standard_deviation"])
    exposure = (
        "underexposed"
        if mean < 85
        else "overexposed"
        if mean > 190
        else "normally exposed"
    )
    sharpness = float(gradients["variance_of_laplacian"])
    return {
        "brightness": "Low" if mean < 85 else "High" if mean > 190 else "Moderate",
        "contrast": "Low" if std < 32 else "High" if std > 70 else "Moderate",
        "entropy": "High"
        if float(info["normalized_entropy"]) > 0.75
        else "Moderate"
        if float(info["normalized_entropy"]) > 0.45
        else "Low",
        "sharpness": "Relative derivative indicator: high"
        if sharpness > 500
        else "Relative derivative indicator: low",
        "noise_estimate": "Elevated"
        if float(noise["estimated_noise_standard_deviation"]) > 12
        else "Low-to-moderate",
        "compression_potential": compression["classification"],
        "exposure_interpretation": f"The global luminance is {exposure}; this does not prove recoverable detail in clipped regions.",
        "image_shape": list(array.shape),
        "interpretation": "This overview is a compact interpretation of the detailed measurements below; every label remains dependent on image content and scale.",
    }


class MathematicalAnalysisService:
    def __init__(self) -> None:
        self._cache_by_image: dict[tuple[str, int], MathematicalAnalysisResponse] = {}
        self._cache_by_id: dict[str, MathematicalAnalysisResponse] = {}

    def analyze(
        self, image_id: str, path: object, grid_size: int = 4
    ) -> MathematicalAnalysisResponse:
        cached = self._cache_by_image.get((image_id, grid_size))
        if cached is not None:
            return cached
        started = perf_counter()
        array = load_image_array(path)  # type: ignore[arg-type]
        gray = _gray(array)
        channels = _channels(array, gray)
        progress = [
            {"stage": "matrix", "status": "complete", "progress": 0.08},
            {"stage": "statistics", "status": "complete", "progress": 0.2},
            {"stage": "frequency", "status": "complete", "progress": 0.48},
            {"stage": "multiscale", "status": "complete", "progress": 0.7},
            {"stage": "report", "status": "complete", "progress": 1.0},
        ]
        statistics = compute_descriptive_statistics(array)
        probability = compute_probability(gray, channels)
        information = compute_information(gray, channels)
        gradients = compute_gradients(gray)
        frequency = compute_fft(gray)
        dct = compute_dct(gray)
        wavelets = compute_wavelets(gray)
        svd = compute_svd(gray)
        texture = compute_texture(gray)
        noise = compute_noise(gray, float(wavelets["estimated_noise_sigma"]))
        local_maps = compute_local_maps(gray, grid_size)
        compression = compute_compression_potential(
            float(information["entropy"]),
            float(information["estimated_redundancy"]),
            dct,
            wavelets,
            svd,
            float(frequency["high_frequency_energy_ratio"]),
        )
        histograms = _histograms(channels)
        geometry = _geometry(gray, gradients)
        overview = _overview(
            array, gray, statistics, information, gradients, noise, compression
        )
        mean = float(statistics["global"]["mean"])
        report = {
            "title": "Mathematical Image Analysis Report",
            "sections": [
                "Image matrix profile",
                "Statistics and probability",
                "Brightness and contrast",
                "Entropy and redundancy",
                "Gradients, sharpness, and frequency",
                "Wavelets and singular values",
                "Texture and noise",
                "Compression potential",
            ],
            "main_findings": [
                f"The luminance mean is {mean:.2f} over an 8-bit domain.",
                f"Entropy is {float(information['entropy']):.3f} bits/pixel with normalized redundancy {float(information['estimated_redundancy']):.3f}.",
                f"Compression potential is classified as {compression['classification']} from normalized transform indicators.",
            ],
            "careful_diagnosis": "The measurements describe observable raster statistics. Noise and blur wording is heuristic because no clean reference or validated classifier is available.",
            "recommended_next_operation": "Use the existing processing workspace to compare denoising or compression algorithms while monitoring SSIM/PSNR when a reference is available.",
            "recommended_initial_parameters": {
                "wavelet": wavelets["wavelet"],
                "wavelet_threshold": wavelets["threshold"],
                "grid": local_maps["grid_size"],
            },
            "limitations": [
                statistics["limitations"],
                information["limitations"],
                gradients["limitations"],
                noise["limitations"],
                compression["limitations"],
            ],
            "download_formats": ["json", "csv"],
            "pdf_ready": True,
        }
        result = MathematicalAnalysisResponse(
            id=str(uuid4()),
            image_id=image_id,
            analysis_version="1.0.0",
            status="complete",
            computed_at=datetime.now(UTC),
            duration_ms=(perf_counter() - started) * 1000,
            progress=progress,
            source={
                "shape": list(array.shape),
                "dtype": str(array.dtype),
                "channels": int(array.shape[2]) if array.ndim == 3 else 1,
            },
            overview=overview,
            matrix=_small_matrix(array),
            statistics=statistics,
            probability=probability,
            histograms=histograms,
            gradients=gradients,
            frequency=frequency,
            dct=dct,
            wavelets=wavelets,
            svd=svd,
            color=_color_analysis(array, channels),
            texture=texture,
            noise=noise,
            local_maps=local_maps,
            geometry=geometry,
            compression=compression,
            report=report,
        )
        self._cache_by_image[(image_id, grid_size)] = result
        self._cache_by_id[result.id] = result
        return result

    def get(self, analysis_id: str) -> MathematicalAnalysisResponse | None:
        return self._cache_by_id.get(analysis_id)


mathematical_analysis_service = MathematicalAnalysisService()

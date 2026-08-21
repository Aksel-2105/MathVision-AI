from collections.abc import Callable
from dataclasses import dataclass
from math import ceil
from typing import Literal

import cv2
import numpy as np
import pywt  # type: ignore[import-untyped]
from scipy.signal import wiener as scipy_wiener  # type: ignore[import-untyped]

from app.core.exceptions import AppError
from app.schemas.processing import AlgorithmInfo, AlgorithmName, ParameterValue


@dataclass(frozen=True)
class ProcessedImage:
    array: np.ndarray
    retained_coefficient_ratio: float | None = None
    representation_type: Literal["encoded_output", "mathematical_simulation"] = (
        "encoded_output"
    )


@dataclass(frozen=True)
class AlgorithmDefinition:
    info: AlgorithmInfo
    process: Callable[[np.ndarray, dict[str, ParameterValue]], ProcessedImage]


def _invalid_parameters(message: str) -> AppError:
    return AppError("invalid_parameters", message, 422)


def _int_param(
    parameters: dict[str, ParameterValue],
    name: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    value = parameters.get(name, default)
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not minimum <= value <= maximum
    ):
        raise _invalid_parameters(
            f"{name} must be an integer between {minimum} and {maximum}."
        )
    return value


def _odd_param(
    parameters: dict[str, ParameterValue],
    name: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    value = _int_param(parameters, name, default, minimum, maximum)
    if value % 2 == 0:
        raise _invalid_parameters(f"{name} must be odd.")
    return value


def _float_param(
    parameters: dict[str, ParameterValue],
    name: str,
    default: float,
    minimum: float,
    maximum: float,
) -> float:
    value = parameters.get(name, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _invalid_parameters(
            f"{name} must be a number between {minimum} and {maximum}."
        )
    numeric = float(value)
    if not minimum <= numeric <= maximum:
        raise _invalid_parameters(
            f"{name} must be a number between {minimum} and {maximum}."
        )
    return numeric


def _choice_param(
    parameters: dict[str, ParameterValue], name: str, default: str, choices: set[str]
) -> str:
    value = parameters.get(name, default)
    if not isinstance(value, str) or value not in choices:
        options = ", ".join(sorted(choices))
        raise _invalid_parameters(f"{name} must be one of: {options}.")
    return value


def _apply_per_channel(
    array: np.ndarray, function: Callable[[np.ndarray], np.ndarray]
) -> np.ndarray:
    if array.ndim == 2:
        return np.asarray(function(array))
    return np.asarray(
        np.stack(
            [function(array[:, :, index]) for index in range(array.shape[2])], axis=2
        )
    )


def _as_uint8(array: np.ndarray) -> np.ndarray:
    return np.asarray(
        np.clip(np.nan_to_num(array, nan=0.0, posinf=255.0, neginf=0.0), 0, 255).astype(
            np.uint8
        )
    )


def _validate_common(parameters: dict[str, ParameterValue]) -> None:
    if parameters:
        raise _invalid_parameters("This algorithm does not accept parameters.")


def _median(array: np.ndarray, parameters: dict[str, ParameterValue]) -> ProcessedImage:
    kernel = _odd_param(parameters, "kernel_size", 3, 3, 15)
    return ProcessedImage(np.asarray(cv2.medianBlur(array, kernel)))


def _gaussian(
    array: np.ndarray, parameters: dict[str, ParameterValue]
) -> ProcessedImage:
    kernel = _odd_param(parameters, "kernel_size", 5, 3, 15)
    sigma = _float_param(parameters, "sigma", 0.0, 0.0, 100.0)
    return ProcessedImage(cv2.GaussianBlur(array, (kernel, kernel), sigma))


def _bilateral(
    array: np.ndarray, parameters: dict[str, ParameterValue]
) -> ProcessedImage:
    diameter = _odd_param(parameters, "diameter", 5, 3, 15)
    sigma_color = _float_param(parameters, "sigma_color", 50.0, 1.0, 255.0)
    sigma_space = _float_param(parameters, "sigma_space", 50.0, 1.0, 255.0)
    return ProcessedImage(
        cv2.bilateralFilter(array, diameter, sigma_color, sigma_space)
    )


def _nlm(array: np.ndarray, parameters: dict[str, ParameterValue]) -> ProcessedImage:
    h = _float_param(parameters, "h", 10.0, 1.0, 100.0)
    template_size = _odd_param(parameters, "template_size", 7, 3, 15)
    search_size = _odd_param(parameters, "search_size", 21, 7, 31)
    if array.ndim == 2:
        result = cv2.fastNlMeansDenoising(array, None, h, template_size, search_size)
    else:
        result = cv2.fastNlMeansDenoisingColored(
            array, None, h, h, template_size, search_size
        )
    return ProcessedImage(result)


def _wavelet_denoise(
    array: np.ndarray, parameters: dict[str, ParameterValue]
) -> ProcessedImage:
    wavelet = _choice_param(parameters, "wavelet", "db2", {"haar", "db2", "sym2"})
    level = _int_param(parameters, "level", 2, 1, 4)
    mode = _choice_param(parameters, "mode", "soft", {"soft", "hard"})

    def denoise_channel(channel: np.ndarray) -> np.ndarray:
        max_level = pywt.dwt_max_level(
            min(channel.shape), pywt.Wavelet(wavelet).dec_len
        )
        actual_level = min(level, max_level)
        if actual_level < 1:
            return channel
        coefficients = pywt.wavedec2(
            channel.astype(np.float64), wavelet, level=actual_level
        )
        detail_values = np.concatenate(
            [np.ravel(detail) for band in coefficients[1:] for detail in band]
        )
        sigma = float(np.median(np.abs(detail_values)) / 0.6745)
        threshold = sigma * np.sqrt(2 * np.log(channel.size))
        filtered = [coefficients[0]]
        filtered.extend(
            tuple(pywt.threshold(detail, threshold, mode=mode) for detail in band)
            for band in coefficients[1:]
        )
        return np.asarray(
            pywt.waverec2(filtered, wavelet)[: channel.shape[0], : channel.shape[1]]
        )

    return ProcessedImage(_as_uint8(_apply_per_channel(array, denoise_channel)))


def _wiener(array: np.ndarray, parameters: dict[str, ParameterValue]) -> ProcessedImage:
    kernel = _odd_param(parameters, "kernel_size", 5, 3, 15)

    def filter_channel(channel: np.ndarray) -> np.ndarray:
        return np.asarray(scipy_wiener(channel.astype(np.float64), (kernel, kernel)))

    return ProcessedImage(_as_uint8(_apply_per_channel(array, filter_channel)))


def _contrast_stretch(
    array: np.ndarray, parameters: dict[str, ParameterValue]
) -> ProcessedImage:
    _validate_common(parameters)

    def stretch(channel: np.ndarray) -> np.ndarray:
        percentiles: np.ndarray = np.percentile(channel, (2, 98))
        low = float(percentiles[0])
        high = float(percentiles[1])
        if high <= low:
            return channel
        return np.asarray((channel.astype(np.float64) - low) * 255.0 / (high - low))

    return ProcessedImage(_as_uint8(_apply_per_channel(array, stretch)))


def _luminance_transform(
    array: np.ndarray, transform: Callable[[np.ndarray], np.ndarray]
) -> np.ndarray:
    if array.ndim == 2:
        return np.asarray(transform(array))
    ycrcb = cv2.cvtColor(array, cv2.COLOR_RGB2YCrCb)
    ycrcb[:, :, 0] = transform(ycrcb[:, :, 0])
    return np.asarray(cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB))


def _histogram_equalization(
    array: np.ndarray, parameters: dict[str, ParameterValue]
) -> ProcessedImage:
    _validate_common(parameters)
    return ProcessedImage(_as_uint8(_luminance_transform(array, cv2.equalizeHist)))


def _clahe(array: np.ndarray, parameters: dict[str, ParameterValue]) -> ProcessedImage:
    clip_limit = _float_param(parameters, "clip_limit", 2.0, 0.1, 40.0)
    tile_grid_size = _int_param(parameters, "tile_grid_size", 8, 2, 32)
    clahe = cv2.createCLAHE(
        clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size)
    )
    return ProcessedImage(_as_uint8(_luminance_transform(array, clahe.apply)))


def _retention_ratio(parameters: dict[str, ParameterValue]) -> float:
    return _float_param(parameters, "retain_ratio", 0.5, 0.01, 1.0)


def _dct_compression(
    array: np.ndarray, parameters: dict[str, ParameterValue]
) -> ProcessedImage:
    retain_ratio = _retention_ratio(parameters)

    def compress(channel: np.ndarray) -> np.ndarray:
        height, width = channel.shape
        padded = np.pad(
            channel.astype(np.float32), ((0, height % 2), (0, width % 2)), mode="edge"
        )
        coefficients = cv2.dct(padded)
        rows = max(1, ceil(coefficients.shape[0] * retain_ratio))
        columns = max(1, ceil(coefficients.shape[1] * retain_ratio))
        mask = np.zeros_like(coefficients)
        mask[:rows, :columns] = 1
        restored = cv2.idct(coefficients * mask)
        return restored[:height, :width]

    return ProcessedImage(
        _as_uint8(_apply_per_channel(array, compress)),
        retain_ratio,
        "mathematical_simulation",
    )


def _wavelet_compression(
    array: np.ndarray, parameters: dict[str, ParameterValue]
) -> ProcessedImage:
    wavelet = _choice_param(parameters, "wavelet", "haar", {"haar", "db2", "sym2"})
    level = _int_param(parameters, "level", 2, 1, 4)
    retain_ratio = _retention_ratio(parameters)

    def compress(channel: np.ndarray) -> tuple[np.ndarray, float]:
        max_level = pywt.dwt_max_level(
            min(channel.shape), pywt.Wavelet(wavelet).dec_len
        )
        actual_level = min(level, max_level)
        if actual_level < 1:
            return channel, 1.0
        coefficients = pywt.wavedec2(
            channel.astype(np.float64), wavelet, level=actual_level
        )
        flat = np.concatenate(
            [np.ravel(item) for item in pywt.coeffs_to_array(coefficients)[0]]
        )
        threshold = np.quantile(np.abs(flat), 1.0 - retain_ratio)
        filtered = [coefficients[0]]
        filtered.extend(
            tuple(np.where(np.abs(detail) >= threshold, detail, 0) for detail in band)
            for band in coefficients[1:]
        )
        reconstructed = pywt.waverec2(filtered, wavelet)[
            : channel.shape[0], : channel.shape[1]
        ]
        retained = float(
            np.count_nonzero(pywt.coeffs_to_array(filtered)[0]) / flat.size
        )
        return reconstructed, retained

    outputs: list[np.ndarray] = []
    ratios: list[float] = []
    for index in range(array.shape[2] if array.ndim == 3 else 1):
        channel = array if array.ndim == 2 else array[:, :, index]
        output, ratio = compress(channel)
        outputs.append(output)
        ratios.append(ratio)
    result = outputs[0] if array.ndim == 2 else np.stack(outputs, axis=2)
    return ProcessedImage(
        _as_uint8(result), float(np.mean(ratios)), "mathematical_simulation"
    )


def _svd_compression(
    array: np.ndarray, parameters: dict[str, ParameterValue]
) -> ProcessedImage:
    retain_ratio = _retention_ratio(parameters)

    def compress(channel: np.ndarray) -> np.ndarray:
        u, singular_values, vt = np.linalg.svd(
            channel.astype(np.float64), full_matrices=False
        )
        rank = max(1, ceil(len(singular_values) * retain_ratio))
        return np.asarray((u[:, :rank] * singular_values[:rank]) @ vt[:rank, :])

    return ProcessedImage(
        _as_uint8(_apply_per_channel(array, compress)),
        retain_ratio,
        "mathematical_simulation",
    )


_DEFINITIONS: tuple[AlgorithmDefinition, ...] = (
    AlgorithmDefinition(
        AlgorithmInfo(
            name="median",
            label="Median Filter",
            category="denoising",
            description="Removes impulse noise while preserving sharp edges.",
            defaults={"kernel_size": 3},
        ),
        _median,
    ),
    AlgorithmDefinition(
        AlgorithmInfo(
            name="gaussian",
            label="Gaussian Filter",
            category="denoising",
            description="Smooths high-frequency noise with a Gaussian kernel.",
            defaults={"kernel_size": 5, "sigma": 0.0},
        ),
        _gaussian,
    ),
    AlgorithmDefinition(
        AlgorithmInfo(
            name="bilateral",
            label="Bilateral Filter",
            category="denoising",
            description="Smooths noise while respecting intensity boundaries.",
            defaults={"diameter": 5, "sigma_color": 50.0, "sigma_space": 50.0},
        ),
        _bilateral,
    ),
    AlgorithmDefinition(
        AlgorithmInfo(
            name="nlm",
            label="Non-Local Means",
            category="denoising",
            description="Denoises using repeated patches from the image.",
            defaults={"h": 10.0, "template_size": 7, "search_size": 21},
        ),
        _nlm,
    ),
    AlgorithmDefinition(
        AlgorithmInfo(
            name="wavelet",
            label="Wavelet Denoising",
            category="denoising",
            description="Thresholds wavelet detail coefficients to suppress noise.",
            defaults={"wavelet": "db2", "level": 2, "mode": "soft"},
        ),
        _wavelet_denoise,
    ),
    AlgorithmDefinition(
        AlgorithmInfo(
            name="wiener",
            label="Wiener Filter",
            category="denoising",
            description="Applies local statistical Wiener filtering.",
            defaults={"kernel_size": 5},
        ),
        _wiener,
    ),
    AlgorithmDefinition(
        AlgorithmInfo(
            name="contrast_stretch",
            label="Contrast Stretch",
            category="enhancement",
            description="Expands the useful intensity range using robust percentiles.",
            defaults={},
        ),
        _contrast_stretch,
    ),
    AlgorithmDefinition(
        AlgorithmInfo(
            name="histogram_equalization",
            label="Histogram Equalization",
            category="enhancement",
            description="Redistributes luminance values to improve global contrast.",
            defaults={},
        ),
        _histogram_equalization,
    ),
    AlgorithmDefinition(
        AlgorithmInfo(
            name="clahe",
            label="CLAHE",
            category="enhancement",
            description="Improves local contrast with clipped adaptive histograms.",
            defaults={"clip_limit": 2.0, "tile_grid_size": 8},
        ),
        _clahe,
    ),
    AlgorithmDefinition(
        AlgorithmInfo(
            name="dct_compression",
            label="DCT Compression",
            category="compression",
            description="Keeps a low-frequency DCT region as a mathematical compression simulation.",
            defaults={"retain_ratio": 0.5},
        ),
        _dct_compression,
    ),
    AlgorithmDefinition(
        AlgorithmInfo(
            name="wavelet_compression",
            label="Wavelet Compression",
            category="compression",
            description="Zeros small wavelet coefficients as a mathematical compression simulation.",
            defaults={"wavelet": "haar", "level": 2, "retain_ratio": 0.5},
        ),
        _wavelet_compression,
    ),
    AlgorithmDefinition(
        AlgorithmInfo(
            name="svd_compression",
            label="SVD Compression",
            category="compression",
            description="Reconstructs the image from a truncated singular-value basis.",
            defaults={"retain_ratio": 0.5},
        ),
        _svd_compression,
    ),
)

ALGORITHMS: dict[AlgorithmName, AlgorithmDefinition] = {
    definition.info.name: definition for definition in _DEFINITIONS
}


def list_algorithms() -> list[AlgorithmInfo]:
    return [definition.info for definition in _DEFINITIONS]


def process_image(
    array: np.ndarray, algorithm: AlgorithmName, parameters: dict[str, ParameterValue]
) -> ProcessedImage:
    definition = ALGORITHMS.get(algorithm)
    if definition is None:
        raise _invalid_parameters("The requested algorithm is not supported.")
    return definition.process(array, parameters)

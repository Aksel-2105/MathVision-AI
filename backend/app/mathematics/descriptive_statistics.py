# mypy: ignore-errors
from collections import Counter

import numpy as np
from scipy.stats import kurtosis, skew


def _stats(values: np.ndarray) -> dict[str, object]:
    data = values.astype(np.float64).ravel()
    counts = Counter(data.tolist())
    mode_value, mode_count = counts.most_common(1)[0]
    mean = float(np.mean(data))
    std = float(np.std(data))
    minimum = float(np.min(data))
    maximum = float(np.max(data))
    percentiles = {
        str(p): float(np.percentile(data, p))
        for p in (1, 5, 10, 25, 50, 75, 90, 95, 99)
    }
    return {
        "minimum": minimum,
        "maximum": maximum,
        "range": maximum - minimum,
        "mean": mean,
        "median": float(np.median(data)),
        "mode": {
            "value": float(mode_value),
            "frequency": int(mode_count),
            "meaningful": mode_count > 1,
        },
        "variance": float(np.var(data)),
        "standard_deviation": std,
        "q1": percentiles["25"],
        "q3": percentiles["75"],
        "interquartile_range": percentiles["75"] - percentiles["25"],
        "percentiles": percentiles,
        "skewness": float(skew(data, bias=False)) if data.size > 2 and std > 0 else 0.0,
        "kurtosis_excess": float(kurtosis(data, bias=False))
        if data.size > 3 and std > 0
        else 0.0,
        "rms": float(np.sqrt(np.mean(np.square(data)))),
        "coefficient_of_variation": float(std / mean) if mean != 0 else None,
        "dynamic_range": maximum - minimum,
        "sample_count": int(data.size),
    }


def compute_descriptive_statistics(array: np.ndarray) -> dict[str, object]:
    channels: dict[str, dict[str, object]] = {}
    if array.ndim == 2:
        channels["Grayscale"] = _stats(array)
        global_stats = channels["Grayscale"]
    else:
        for index, name in enumerate(("Red", "Green", "Blue")):
            channels[name] = _stats(array[:, :, index])
        global_stats = _stats(np.mean(array[:, :, :3], axis=2))
    return {
        "global": global_stats,
        "channels": channels,
        "formulae": {
            "mean": "μ = (1/N) Σᵢ xᵢ",
            "variance": "σ² = (1/N) Σᵢ (xᵢ − μ)²",
            "standard_deviation": "σ = √σ²",
            "rms": "RMS = √((1/N) Σᵢ xᵢ²)",
            "coefficient_of_variation": "CV = σ/μ when μ ≠ 0",
        },
        "symbols": {
            "N": "number of scalar intensity samples",
            "xᵢ": "pixel intensity",
            "μ": "sample mean",
            "σ": "standard deviation",
        },
        "method": "Population moments are used for image pixels; scipy skewness and excess kurtosis use unbiased finite-sample corrections.",
        "limitations": "Mode, skewness, kurtosis, and coefficient of variation can be unstable for constant or nearly constant images.",
    }

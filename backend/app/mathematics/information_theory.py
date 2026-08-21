# mypy: ignore-errors
import numpy as np


def entropy(values: np.ndarray) -> float:
    histogram, _ = np.histogram(values, bins=256, range=(0, 256))
    probabilities = histogram.astype(np.float64) / max(1, values.size)
    nonzero = probabilities[probabilities > 0]
    return float(-np.sum(nonzero * np.log2(nonzero)))


def compute_information(
    gray: np.ndarray, channels: dict[str, np.ndarray]
) -> dict[str, object]:
    max_entropy = 8.0
    channel_entropy = {name: entropy(values) for name, values in channels.items()}
    total = entropy(gray)
    normalized = total / max_entropy
    return {
        "entropy": total,
        "channel_entropy": channel_entropy,
        "maximum_theoretical_entropy": max_entropy,
        "normalized_entropy": normalized,
        "estimated_redundancy": 1.0 - normalized,
        "formulae": {
            "shannon": "H(X) = −Σₖ pₖ log₂(pₖ)",
            "normalized": "H_norm = H/ log₂(256)",
            "redundancy": "R = 1 − H_norm",
        },
        "interpretation": "High entropy can reflect meaningful detail, texture, or noise; it is not by itself a quality score.",
        "limitations": "The redundancy estimate is an entropy-based upper-level indicator, not a codec bitrate prediction.",
    }

# mypy: ignore-errors
import cv2
import numpy as np


def compute_dct(gray: np.ndarray) -> dict[str, object]:
    coefficients = cv2.dct(gray.astype(np.float32))
    energy = np.square(coefficients)
    total = float(np.sum(energy)) or 1.0
    flattened = np.sort(energy.ravel())[::-1]
    cumulative = np.cumsum(flattened) / total
    retention = {
        str(level): int(np.searchsorted(cumulative, level / 100) + 1)
        for level in (90, 95, 99)
    }
    low_rows = max(1, gray.shape[0] // 8)
    low_cols = max(1, gray.shape[1] // 8)
    low_energy = float(np.sum(energy[:low_rows, :low_cols]) / total)
    return {
        "low_frequency_energy_ratio": low_energy,
        "high_frequency_energy_ratio": 1.0 - low_energy,
        "coefficients_needed_for_energy_percent": retention,
        "near_zero_coefficient_ratio": float(
            np.mean(
                np.abs(coefficients)
                < max(1e-6, np.percentile(np.abs(coefficients), 20))
            )
        ),
        "coefficient_sparsity": float(np.mean(np.abs(coefficients) < 1e-3)),
        "energy_concentration": float(np.mean(cumulative >= 0.95) ** -1)
        if cumulative.size
        else 0.0,
        "map": np.round(np.log1p(np.abs(coefficients[:96, :96])), 5).tolist(),
        "formula": "C(u,v) = αᵤαᵥ ΣₓΣᵧ I(x,y) cos(π(2x+1)u/2m) cos(π(2y+1)v/2n)",
        "interpretation": "Coefficient retention is a mathematical transform-domain indicator; it is not an encoded JPEG file-size guarantee.",
        "limitations": "DCT analysis is calculated on the luminance/grayscale representation and ignores codec headers and entropy coding.",
    }

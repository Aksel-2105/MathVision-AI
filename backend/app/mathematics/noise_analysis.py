# mypy: ignore-errors
import cv2
import numpy as np
from scipy.stats import normaltest


def compute_noise(gray: np.ndarray, wavelet_sigma: float) -> dict[str, object]:
    values = gray.astype(np.float64)
    residual = values - cv2.GaussianBlur(values, (3, 3), 0).astype(np.float64)
    sigma = float(np.std(residual))
    residual_flat = residual.ravel()
    gaussian_p = (
        float(normaltest(residual_flat[: min(10000, residual_flat.size)]).pvalue)
        if residual_flat.size >= 20
        else None
    )
    impulse = float(np.mean((gray <= 2) | (gray >= 253)))
    signal = float(np.std(values))
    snr = (
        float(20 * np.log10(max(signal, 1e-12) / max(sigma, 1e-12)))
        if sigma > 0
        else None
    )
    h, w = gray.shape
    resized = cv2.resize(residual, (min(64, w), min(64, h)))
    return {
        "estimated_noise_standard_deviation": sigma,
        "wavelet_noise_sigma": wavelet_sigma,
        "impulse_noise_ratio": impulse,
        "gaussian_likeness": {
            "normaltest_p_value": gaussian_p,
            "wording": "consistent with Gaussian-like residual"
            if gaussian_p is not None and gaussian_p > 0.05
            else "not confirmed as Gaussian-like",
        },
        "periodic_noise_score": float(
            max(
                0.0,
                min(
                    1.0,
                    (
                        np.std(np.mean(residual, axis=0))
                        + np.std(np.mean(residual, axis=1)) / 2
                    )
                    / 32,
                ),
            )
        ),
        "speckle_indicator": float(np.std(residual / np.maximum(values, 1.0))),
        "signal_to_noise_db": snr,
        "residual_histogram": np.histogram(residual, bins=64)[0].astype(int).tolist(),
        "residual_preview": np.round(resized, 3).tolist(),
        "confidence": float(max(0.0, min(1.0, sigma / 32))),
        "method": "3×3 Gaussian residual, robust wavelet HH estimate, impulse-pixel ratio, residual normality heuristic, and local residual variation.",
        "limitations": "No clean reference is available. Blur, texture, compression artifacts, and edges can all appear in the residual; the wording is heuristic, not a validated classifier.",
    }

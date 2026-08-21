# mypy: ignore-errors
import cv2
import numpy as np


def _map(values: np.ndarray, size: int = 96) -> list[list[float]]:
    h, w = values.shape
    scale = min(1.0, size / max(h, w))
    resized = cv2.resize(
        values.astype(np.float32), (max(1, int(w * scale)), max(1, int(h * scale)))
    )
    return np.round(resized, 5).tolist()


def compute_fft(gray: np.ndarray) -> dict[str, object]:
    values = gray.astype(np.float64)
    spectrum = np.fft.fftshift(np.fft.fft2(values))
    magnitude = np.abs(spectrum)
    log_magnitude = np.log1p(magnitude)
    phase = np.angle(spectrum)
    h, w = values.shape
    yy, xx = np.ogrid[:h, :w]
    radius = np.sqrt((yy - h / 2) ** 2 + (xx - w / 2) ** 2)
    max_radius = min(h, w) / 2
    low = radius <= max_radius * 0.15
    high = radius >= max_radius * 0.55
    energy = np.square(magnitude)
    total = float(np.sum(energy)) or 1.0
    radial: list[float] = []
    for index in range(16):
        band = (radius >= index * max_radius / 16) & (
            radius < (index + 1) * max_radius / 16
        )
        radial.append(float(np.mean(magnitude[band])) if np.any(band) else 0.0)
    horizontal = float(np.mean(magnitude[h // 2, :]) / max(1e-12, np.mean(magnitude)))
    vertical = float(np.mean(magnitude[:, w // 2]) / max(1e-12, np.mean(magnitude)))
    return {
        "low_frequency_energy_ratio": float(np.sum(energy[low]) / total),
        "mid_frequency_energy_ratio": float(np.sum(energy[~low & ~high]) / total),
        "high_frequency_energy_ratio": float(np.sum(energy[high]) / total),
        "radial_frequency_profile": radial,
        "horizontal_periodicity_score": horizontal,
        "vertical_periodicity_score": vertical,
        "dominant_frequency": {
            "row": int(np.unravel_index(np.argmax(magnitude), magnitude.shape)[0]),
            "column": int(np.unravel_index(np.argmax(magnitude), magnitude.shape)[1]),
        },
        "maps": {
            "magnitude": _map(magnitude),
            "log_magnitude": _map(log_magnitude),
            "phase": _map(phase),
        },
        "formula": "F(u,v) = ΣₓΣᵧ I(x,y)e^(−2πi(ux/m + vy/n))",
        "method": "Centered two-dimensional FFT with safe log1p magnitude scaling and radial energy bands.",
        "limitations": "Periodic-noise scores are heuristic spectral indicators and require visual/contextual confirmation.",
    }

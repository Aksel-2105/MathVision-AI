# mypy: ignore-errors
import cv2
import numpy as np


def _small_map(values: np.ndarray, size: int = 64) -> list[list[float]]:
    h, w = values.shape
    scale = min(1.0, size / max(h, w))
    resized = cv2.resize(
        values.astype(np.float32), (max(1, int(w * scale)), max(1, int(h * scale)))
    )
    return np.round(resized, 4).tolist()


def compute_gradients(gray: np.ndarray) -> dict[str, object]:
    if min(gray.shape) < 3:
        gray = np.pad(
            gray,
            ((0, max(0, 3 - gray.shape[0])), (0, max(0, 3 - gray.shape[1]))),
            mode="edge",
        )
    values = gray.astype(np.float64)
    dx = cv2.Sobel(values, cv2.CV_64F, 1, 0, ksize=3)
    dy = cv2.Sobel(values, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.hypot(dx, dy)
    orientation = np.arctan2(dy, dx)
    laplacian = cv2.Laplacian(values, cv2.CV_64F)
    sobel_edges = magnitude > np.percentile(magnitude, 75)
    canny = cv2.Canny(gray, 100, 200)
    angles, counts = np.unique(
        np.round(np.degrees(orientation[sobel_edges]) / 15) * 15, return_counts=True
    )
    distribution = {
        str(float(angle)): float(count / max(1, np.sum(counts)))
        for angle, count in zip(angles, counts, strict=True)
    }
    return {
        "mean_gradient_strength": float(np.mean(magnitude)),
        "maximum_gradient_strength": float(np.max(magnitude)),
        "edge_density": float(np.mean(sobel_edges)),
        "canny_edge_density": float(np.mean(canny > 0)),
        "variance_of_laplacian": float(np.var(laplacian)),
        "tenengrad": float(np.mean(np.square(magnitude))),
        "orientation_distribution_degrees": distribution,
        "maps": {
            "horizontal_derivative": _small_map(dx),
            "vertical_derivative": _small_map(dy),
            "gradient_magnitude": _small_map(magnitude),
            "gradient_orientation": _small_map(orientation),
            "sobel_edges": _small_map(sobel_edges.astype(float)),
            "canny_edges": _small_map((canny > 0).astype(float)),
            "laplacian": _small_map(laplacian),
        },
        "formulae": {
            "gradient": "∇I = (∂ₓI, ∂ᵧI)",
            "magnitude": "‖∇I‖ = √((∂ₓI)² + (∂ᵧI)²)",
            "laplacian": "∇²I = ∂²ₓI + ∂²ᵧI",
        },
        "method": "3×3 Sobel derivatives, percentile-based Sobel edge mask, Canny thresholds 100/200, and OpenCV Laplacian.",
        "limitations": "Derivative measures respond to both genuine edges and noise; use the Noise and Sharpness sections together.",
    }

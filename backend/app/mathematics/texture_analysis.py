# mypy: ignore-errors
import numpy as np
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern


def compute_texture(gray: np.ndarray) -> dict[str, object]:
    quantized = np.floor(gray.astype(np.float64) / 32).astype(np.uint8)
    angles = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]
    matrix = graycomatrix(
        quantized, distances=[1], angles=angles, levels=8, symmetric=True, normed=True
    )
    properties = (
        "contrast",
        "dissimilarity",
        "homogeneity",
        "energy",
        "correlation",
        "ASM",
    )
    direction_values = {
        name: [float(value) for value in graycoprops(matrix, name)[0]]
        for name in properties
    }
    lbp = local_binary_pattern(gray, 8, 1, method="uniform")
    histogram, _ = np.histogram(lbp, bins=10, range=(0, 10))
    probabilities = histogram.astype(np.float64) / max(1, lbp.size)
    probabilities = probabilities[probabilities > 0]
    return {
        "distance": 1,
        "angles_degrees": [0, 45, 90, 135],
        "directional_features": direction_values,
        "average_features": {
            name: float(np.mean(values)) for name, values in direction_values.items()
        },
        "lbp_histogram": histogram.tolist(),
        "texture_entropy": float(-np.sum(probabilities * np.log2(probabilities)))
        if probabilities.size
        else 0.0,
        "texture_uniformity": float(np.sum(np.square(probabilities))),
        "formula": "P(i,j | d,θ) is the normalized frequency of gray-level pairs separated by distance d at angle θ.",
        "method": "8-level quantization, distance 1, four directions, symmetric normalized GLCM; LBP uses P=8 and radius R=1.",
        "limitations": "GLCM features depend on quantization, distance, angle, and image scale; they describe texture, not semantic content.",
    }

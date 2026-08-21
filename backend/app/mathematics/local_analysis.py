# mypy: ignore-errors
import cv2
import numpy as np

from app.mathematics.information_theory import entropy


def compute_local_maps(gray: np.ndarray, grid_size: int = 4) -> dict[str, object]:
    values = gray.astype(np.float64)
    h, w = values.shape
    maps = {
        name: np.zeros((grid_size, grid_size), dtype=float)
        for name in (
            "brightness",
            "contrast",
            "entropy",
            "sharpness",
            "edge_density",
            "noise",
        )
    }
    cells: list[dict[str, object]] = []
    for row in range(grid_size):
        for column in range(grid_size):
            y0, y1 = row * h // grid_size, (row + 1) * h // grid_size
            x0, x1 = column * w // grid_size, (column + 1) * w // grid_size
            cell = values[y0:y1, x0:x1]
            lap = cv2.Laplacian(cell, cv2.CV_64F)
            residual = cell - cv2.GaussianBlur(cell, (3, 3), 0)
            record = {
                "row": row,
                "column": column,
                "coordinates": {"x0": x0, "y0": y0, "x1": x1, "y1": y1},
                "mean_luminance": float(np.mean(cell)),
                "variance": float(np.var(cell)),
                "entropy": entropy(cell),
                "local_contrast": float(np.std(cell)),
                "sharpness": float(np.var(lap)),
                "edge_density": float(
                    np.mean(
                        np.abs(cv2.Sobel(cell, cv2.CV_64F, 1, 0, ksize=3))
                        > np.percentile(np.abs(cell - np.mean(cell)), 75)
                    )
                ),
                "noise": float(np.std(residual)),
            }
            cells.append(record)
            maps["brightness"][row, column] = float(record["mean_luminance"])
            maps["contrast"][row, column] = float(record["local_contrast"])
            maps["entropy"][row, column] = float(record["entropy"])
            maps["sharpness"][row, column] = float(record["sharpness"])
            maps["edge_density"][row, column] = float(record["edge_density"])
            maps["noise"][row, column] = float(record["noise"])
    return {
        "grid_size": grid_size,
        "cells": cells,
        "maps": {name: np.round(data, 4).tolist() for name, data in maps.items()},
        "method": "Non-overlapping grid cells; all values are computed from the corresponding uploaded-image pixels.",
        "limitations": "Small cells have fewer samples and produce noisier estimates; grid metrics are descriptive, not object segmentation.",
    }

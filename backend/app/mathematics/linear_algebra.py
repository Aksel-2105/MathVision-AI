# mypy: ignore-errors
import numpy as np


def compute_svd(gray: np.ndarray) -> dict[str, object]:
    values = gray.astype(np.float64)
    u, singular_values, vt = np.linalg.svd(values, full_matrices=False)
    energy = np.square(singular_values)
    total = float(np.sum(energy)) or 1.0
    cumulative = np.cumsum(energy) / total
    ranks = {
        str(level): int(np.searchsorted(cumulative, level / 100) + 1)
        for level in (90, 95, 99)
    }
    effective = float(
        np.exp(-np.sum((energy / total) * np.log(np.maximum(energy / total, 1e-15))))
    )
    rank = (
        int(
            np.sum(
                singular_values
                > max(values.shape) * np.finfo(float).eps * singular_values[0]
            )
        )
        if singular_values.size
        else 0
    )
    reconstructions: dict[str, object] = {}
    for k in sorted(set((1, min(5, len(singular_values)), ranks["95"]))):
        if k > 0:
            reconstruction = (u[:, :k] * singular_values[:k]) @ vt[:k, :]
            reconstructions[str(k)] = {
                "k": k,
                "relative_frobenius_error": float(
                    np.linalg.norm(values - reconstruction)
                    / max(np.linalg.norm(values), 1e-12)
                ),
                "preview": np.clip(
                    np.round(reconstruction[:64, :64], 2), 0, 255
                ).tolist(),
            }
    return {
        "singular_values": np.round(singular_values[:128], 5).tolist(),
        "normalized_singular_values": np.round(
            (singular_values[:128] / max(singular_values[0], 1e-12)), 5
        ).tolist()
        if singular_values.size
        else [],
        "cumulative_energy": np.round(cumulative[:128], 5).tolist(),
        "numerical_rank": rank,
        "effective_rank": effective,
        "ranks_for_energy_percent": ranks,
        "condition_number": float(singular_values[0] / singular_values[-1])
        if singular_values.size and singular_values[-1] > 0
        else None,
        "reconstructions": reconstructions,
        "formula": "I = UΣVᵀ; Iₖ = Σᵣ₌₁ᵏ σᵣuᵣvᵣᵀ",
        "interpretation": "A small energy rank indicates that a low-rank approximation may represent the luminance structure efficiently.",
        "limitations": "SVD is computed on luminance/grayscale data; rank is numerical and depends on floating-point tolerance.",
    }

# mypy: ignore-errors
import numpy as np
import pywt


def _subband(name: str, values: np.ndarray) -> dict[str, object]:
    data = values.astype(np.float64)
    magnitude = np.abs(data)
    return {
        "name": name,
        "shape": list(data.shape),
        "energy": float(np.sum(np.square(data))),
        "entropy": float(_entropy(data)),
        "near_zero_ratio": float(
            np.mean(magnitude < max(1e-8, np.percentile(magnitude, 20)))
        ),
        "preview": np.round(data[:64, :64], 4).tolist(),
    }


def _entropy(values: np.ndarray) -> float:
    histogram, _ = np.histogram(values, bins=64)
    probabilities = histogram.astype(np.float64) / max(1, values.size)
    probabilities = probabilities[probabilities > 0]
    return (
        float(-np.sum(probabilities * np.log2(probabilities)))
        if probabilities.size
        else 0.0
    )


def compute_wavelets(gray: np.ndarray, wavelet_name: str = "haar") -> dict[str, object]:
    if min(gray.shape) < 2:
        gray = np.pad(
            gray,
            ((0, max(0, 2 - gray.shape[0])), (0, max(0, 2 - gray.shape[1]))),
            mode="edge",
        )
    wavelet = pywt.Wavelet(wavelet_name)
    level = int(pywt.dwt_max_level(min(gray.shape), wavelet.dec_len))
    level = max(1, min(level, 4))
    coefficients = pywt.wavedec2(gray.astype(np.float64), wavelet, level=level)
    bands: list[dict[str, object]] = [_subband(f"LL{level}", coefficients[0])]
    for depth, detail in enumerate(coefficients[1:], start=level):
        bands.extend(
            [
                _subband(f"LH{depth}", detail[0]),
                _subband(f"HL{depth}", detail[1]),
                _subband(f"HH{depth}", detail[2]),
            ]
        )
    hh = coefficients[-1][2]
    sigma = float(np.median(np.abs(hh - np.median(hh))) / 0.6745)
    all_detail = np.concatenate(
        [part.ravel() for detail in coefficients[1:] for part in detail]
    )
    threshold = float(sigma * np.sqrt(2 * np.log(max(2, gray.size))))
    hard = pywt.waverec2(
        [
            coefficients[0],
            *[
                (
                    pywt.threshold(a, threshold, "hard"),
                    pywt.threshold(b, threshold, "hard"),
                    pywt.threshold(c, threshold, "hard"),
                )
                for a, b, c in coefficients[1:]
            ],
        ],
        wavelet,
    )
    return {
        "wavelet": wavelet_name,
        "supported_families": ["haar", "db2", "sym2", "coif1"],
        "maximum_decomposition_level": int(level),
        "used_level": int(level),
        "subbands": bands,
        "estimated_noise_sigma": sigma,
        "threshold": threshold,
        "detail_near_zero_ratio": float(
            np.mean(
                np.abs(all_detail) < max(1e-8, np.percentile(np.abs(all_detail), 20))
            )
        )
        if all_detail.size
        else 0.0,
        "hard_threshold_preview": np.clip(np.round(hard[:64, :64], 3), 0, 255).tolist(),
        "formula": "I → {LL₁,LH₁,HL₁,HH₁}; LL₁ → {LL₂,LH₂,HL₂,HH₂}",
        "interpretation": "HH detail median absolute deviation gives a robust noise-scale estimate; threshold previews are not a committed restoration.",
        "limitations": "Boundary handling and wavelet family affect energy and sparsity; images are normalized to the loaded 8-bit representation.",
    }

# mypy: ignore-errors
import numpy as np


def compute_probability(
    gray: np.ndarray, channels: dict[str, np.ndarray]
) -> dict[str, object]:
    def distribution(values: np.ndarray) -> dict[str, object]:
        histogram, _ = np.histogram(values, bins=256, range=(0, 256))
        pmf = histogram.astype(np.float64) / max(1, values.size)
        cdf = np.cumsum(pmf)
        return {
            "pmf": pmf.tolist(),
            "cdf": cdf.tolist(),
            "dark_probability": float(np.mean(values < 64)),
            "midtone_probability": float(np.mean((values >= 64) & (values < 192))),
            "bright_probability": float(np.mean(values >= 192)),
            "black_clipping_probability": float(np.mean(values == 0)),
            "white_clipping_probability": float(np.mean(values == 255)),
        }

    return {
        "thresholds": {
            "dark": "[0, 64)",
            "midtone": "[64, 192)",
            "bright": "[192, 256]",
            "black_clipping": "0",
            "white_clipping": "255",
        },
        "grayscale": distribution(gray),
        "channels": {name: distribution(values) for name, values in channels.items()},
        "formulae": {
            "pmf": "pₖ = P(X = k) = count(X=k)/N",
            "cdf": "F(k) = P(X ≤ k) = Σⱼ≤k pⱼ",
        },
        "symbols": {
            "X": "discrete pixel-intensity random variable",
            "k": "intensity level 0…255",
            "N": "number of pixels",
        },
        "interpretation": "Probabilities describe the empirical distribution of the uploaded pixels; they are not a population model.",
        "limitations": "Thresholds are conventional 8-bit luminance bands and should be interpreted differently for non-8-bit sources after normalization.",
    }

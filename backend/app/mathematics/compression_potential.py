# mypy: ignore-errors


def compute_compression_potential(
    entropy: float,
    redundancy: float,
    dct: dict[str, object],
    wavelet: dict[str, object],
    svd: dict[str, object],
    high_frequency: float,
) -> dict[str, object]:
    dct_low = float(dct["low_frequency_energy_ratio"])
    wavelet_sparse = float(wavelet["detail_near_zero_ratio"])
    svd_ranks = svd["ranks_for_energy_percent"]
    rank95 = float(svd_ranks["95"]) / max(1.0, float(len(svd["singular_values"])))
    components = {
        "entropy_redundancy": max(0.0, min(1.0, redundancy)),
        "dct_concentration": max(0.0, min(1.0, dct_low)),
        "wavelet_sparsity": max(0.0, min(1.0, wavelet_sparse)),
        "svd_low_rank": max(0.0, min(1.0, 1.0 - rank95)),
        "low_high_frequency_balance": max(0.0, min(1.0, 1.0 - high_frequency)),
    }
    score = sum(components.values()) / len(components)
    level = "High" if score >= 0.67 else "Moderate" if score >= 0.4 else "Low"
    return {
        "score": score,
        "classification": level,
        "normalized_components": components,
        "dct_suitability": dct_low,
        "wavelet_suitability": wavelet_sparse,
        "svd_suitability": 1.0 - rank95,
        "reasons": [
            f"DCT low-frequency energy ratio is {dct_low:.3f}.",
            f"Wavelet detail near-zero ratio is {wavelet_sparse:.3f}.",
            f"Entropy is {entropy:.3f} bits with estimated redundancy {redundancy:.3f}.",
        ],
        "formula": "S = mean(normalized redundancy, DCT concentration, wavelet sparsity, SVD low-rank potential, low-frequency balance)",
        "limitations": "This is a normalized transform-domain indicator. It is not a file-size forecast and weights the listed components equally.",
    }

import numpy as np

from app.mathematics.compression_potential import compute_compression_potential
from app.mathematics.dct_analysis import compute_dct
from app.mathematics.descriptive_statistics import compute_descriptive_statistics
from app.mathematics.frequency_analysis import compute_fft
from app.mathematics.gradients import compute_gradients
from app.mathematics.information_theory import entropy
from app.mathematics.linear_algebra import compute_svd
from app.mathematics.local_analysis import compute_local_maps
from app.mathematics.noise_analysis import compute_noise
from app.mathematics.probability import compute_probability
from app.mathematics.texture_analysis import compute_texture
from app.mathematics.wavelet_analysis import compute_wavelets


def test_descriptive_statistics_include_quantiles_and_constant_edge_case() -> None:
    image = np.array([[0, 1], [2, 3]], dtype=np.uint8)
    result = compute_descriptive_statistics(image)
    stats = result["global"]
    assert stats["mean"] == 1.5
    assert stats["q1"] == 0.75
    assert stats["q3"] == 2.25
    constant = compute_descriptive_statistics(np.full((2, 2), 7, dtype=np.uint8))[
        "global"
    ]
    assert constant["variance"] == 0.0
    assert constant["coefficient_of_variation"] == 0.0


def test_probability_and_entropy_are_normalized() -> None:
    image = np.arange(16, dtype=np.uint8).reshape(4, 4)
    result = compute_probability(image, {"Grayscale": image})["grayscale"]
    assert np.isclose(sum(result["pmf"]), 1.0)
    assert np.isclose(result["cdf"][-1], 1.0)
    assert entropy(np.zeros((4, 4), dtype=np.uint8)) == 0.0


def test_gradients_fft_dct_and_svd_handle_small_constant_and_signal_images() -> None:
    image = np.tile(np.arange(8, dtype=np.uint8), (8, 1))
    gradients = compute_gradients(image)
    assert gradients["edge_density"] >= 0.0
    fft = compute_fft(image)
    total_frequency = (
        fft["low_frequency_energy_ratio"]
        + fft["mid_frequency_energy_ratio"]
        + fft["high_frequency_energy_ratio"]
    )
    assert np.isclose(total_frequency, 1.0)
    dct = compute_dct(image)
    assert dct["coefficients_needed_for_energy_percent"]["95"] >= 1
    svd = compute_svd(image)
    assert svd["ranks_for_energy_percent"]["90"] >= 1


def test_wavelet_texture_noise_local_and_compression_sections_return_real_metrics() -> (
    None
):
    image = np.full((1, 1), 128, dtype=np.uint8)
    wavelet = compute_wavelets(image)
    assert wavelet["used_level"] >= 1
    texture = compute_texture(np.full((4, 4), 128, dtype=np.uint8))
    assert texture["distance"] == 1
    noise = compute_noise(image, float(wavelet["estimated_noise_sigma"]))
    assert noise["estimated_noise_standard_deviation"] >= 0.0
    local = compute_local_maps(np.full((4, 4), 128, dtype=np.uint8), 4)
    assert len(local["cells"]) == 16
    potential = compute_compression_potential(
        0.0,
        1.0,
        {"low_frequency_energy_ratio": 1.0},
        wavelet,
        {"ranks_for_energy_percent": {"95": 1}, "singular_values": [1.0]},
        0.0,
    )
    assert 0.0 <= potential["score"] <= 1.0

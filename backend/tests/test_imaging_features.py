from math import isfinite

import numpy as np

from app.imaging.features import extract_features


def test_constant_grayscale_features_have_zero_entropy_and_edges() -> None:
    array = np.full((8, 10), 128, dtype=np.uint8)

    features, histogram, noise = extract_features(
        array,
        width=10,
        height=8,
        channels=1,
        color_mode="L",
        file_size_bytes=100,
    )

    assert features.mean_intensity == 128
    assert features.entropy == 0
    assert features.edge_density == 0
    assert sum(histogram.series[0].values) == 80
    assert histogram.series[0].values[128] == 80
    assert noise.type == "none_detected"


def test_rgb_histogram_has_three_channels_and_preserves_counts() -> None:
    array = np.zeros((4, 5, 3), dtype=np.uint8)
    array[:, :, 0] = 255
    array[:, :, 1] = 50

    features, histogram, _ = extract_features(
        array,
        width=5,
        height=4,
        channels=3,
        color_mode="RGB",
        file_size_bytes=200,
    )

    assert features.channels == 3
    assert features.saturation > 0
    assert [series.label for series in histogram.series] == ["Red", "Green", "Blue"]
    assert histogram.series[0].values[255] == 20
    assert histogram.series[1].values[50] == 20
    assert histogram.series[2].values[0] == 20


def test_one_pixel_image_returns_finite_features() -> None:
    features, _, _ = extract_features(
        np.zeros((1, 1), dtype=np.uint8),
        width=1,
        height=1,
        channels=1,
        color_mode="L",
        file_size_bytes=1,
    )

    assert features.entropy == 0
    assert isfinite(features.high_frequency_energy)

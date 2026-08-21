import numpy as np

from app.mathematics.metrics import calculate_quality_metrics


def test_quality_metrics_identical_images_report_perfect_match() -> None:
    image = np.full((8, 8), 120, dtype=np.uint8)

    metrics = calculate_quality_metrics(image, image.copy())

    assert metrics.mse == 0
    assert metrics.rmse == 0
    assert metrics.psnr is None
    assert metrics.psnr_note == "identical_images"
    assert metrics.ssim == 1


def test_quality_metrics_calculate_known_error() -> None:
    original = np.zeros((2, 2), dtype=np.uint8)
    processed = np.array([[0, 0], [0, 255]], dtype=np.uint8)

    metrics = calculate_quality_metrics(original, processed)

    assert metrics.mse == 255**2 / 4
    assert metrics.rmse == 127.5
    assert metrics.psnr is not None
    assert round(metrics.psnr, 3) == 6.021
    assert metrics.ssim is None
    assert metrics.ssim_note == "image_too_small_for_ssim"

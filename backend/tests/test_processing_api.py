from io import BytesIO

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image


def gradient_png_bytes() -> bytes:
    values = np.tile(np.arange(64, dtype=np.uint8), (48, 1))
    image = Image.fromarray(np.dstack([values, np.flip(values, axis=1), values]))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def upload_gradient(client: TestClient) -> str:
    response = client.post(
        "/api/v1/images/upload",
        files={"file": ("gradient.png", gradient_png_bytes(), "image/png")},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_algorithms_and_processing_result_flow(client: TestClient) -> None:
    algorithms = client.get("/api/v1/processing/algorithms")
    assert algorithms.status_code == 200
    assert len(algorithms.json()["algorithms"]) == 12

    image_id = upload_gradient(client)
    processed = client.post(
        "/api/v1/processing",
        json={
            "image_id": image_id,
            "algorithm": "median",
            "parameters": {"kernel_size": 3},
        },
    )

    assert processed.status_code == 201
    result = processed.json()
    assert result["algorithm"] == "median"
    assert result["output_format"] == "PNG"
    assert result["metrics"]["mse"] >= 0
    assert result["metrics"]["rmse"] >= 0
    assert result["metrics"]["ssim"] is not None
    assert result["metrics"]["representation_type"] == "encoded_output"

    content = client.get(result["output_url"])
    assert content.status_code == 200
    assert content.headers["content-type"] == "image/png"
    with Image.open(BytesIO(content.content)) as image:
        assert image.size == (64, 48)

    stored = client.get(f"/api/v1/processing/{result['id']}")
    assert stored.status_code == 200
    assert stored.json()["id"] == result["id"]


def test_processing_rejects_invalid_parameters(client: TestClient) -> None:
    image_id = upload_gradient(client)
    response = client.post(
        "/api/v1/processing",
        json={
            "image_id": image_id,
            "algorithm": "median",
            "parameters": {"kernel_size": 4},
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_parameters"


def test_compression_reports_mathematical_simulation(client: TestClient) -> None:
    image_id = upload_gradient(client)
    response = client.post(
        "/api/v1/processing",
        json={
            "image_id": image_id,
            "algorithm": "dct_compression",
            "parameters": {"retain_ratio": 0.25},
        },
    )

    assert response.status_code == 201
    assert (
        response.json()["metrics"]["representation_type"] == "mathematical_simulation"
    )
    assert response.json()["metrics"]["retained_coefficient_ratio"] == 0.25

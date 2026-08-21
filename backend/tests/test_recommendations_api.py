from io import BytesIO

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image


def source_png_bytes(seed: int) -> bytes:
    values = np.tile(np.arange(64, dtype=np.uint8), (48, 1))
    if seed:
        values = np.roll(values, seed, axis=1)
    image = Image.fromarray(np.dstack([values, np.flip(values, axis=1), values]))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def create_saved_experiment(
    client: TestClient, seed: int, algorithm: str
) -> tuple[str, str]:
    upload = client.post(
        "/api/v1/images/upload",
        files={"file": (f"source-{seed}.png", source_png_bytes(seed), "image/png")},
    )
    assert upload.status_code == 201
    image_id = upload.json()["id"]
    experiment = client.post(
        "/api/v1/experiments",
        json={"image_id": image_id, "name": f"Training sample {seed}"},
    )
    assert experiment.status_code == 201
    experiment_id = experiment.json()["id"]
    processing = client.post(
        "/api/v1/processing",
        json={"image_id": image_id, "algorithm": algorithm, "parameters": {}},
    )
    assert processing.status_code == 201
    run = client.post(
        f"/api/v1/experiments/{experiment_id}/runs",
        json={"processing_id": processing.json()["id"]},
    )
    assert run.status_code == 201
    return image_id, experiment_id


def test_training_persists_status_and_recommendation(client: TestClient) -> None:
    first_image, _ = create_saved_experiment(client, 0, "median")
    create_saved_experiment(client, 1, "gaussian")

    training = client.post("/api/v1/recommendations/train")

    assert training.status_code == 201
    payload = training.json()
    assert payload["model_version"] == "random-forest-v1"
    assert payload["sample_count"] == 2
    assert payload["class_count"] == 2
    assert payload["validation_accuracy"] is None
    assert "holdout" in " ".join(payload["limitations"])

    status = client.get("/api/v1/recommendations/model")
    assert status.status_code == 200
    assert status.json()["trained"] is True
    assert status.json()["sample_count"] == 2

    recommendation = client.post(
        "/api/v1/recommendations", json={"image_id": first_image}
    )
    assert recommendation.status_code == 200
    result = recommendation.json()
    assert result["recommended_algorithm"] in {"median", "gaussian"}
    assert 0 <= result["confidence"] <= 1
    assert "entropy" in result["feature_importance"]
    assert "most influential image features" in result["explanation"]


def test_training_requires_saved_experiment_outcomes(client: TestClient) -> None:
    response = client.post("/api/v1/recommendations/train")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "training_insufficient_data"


def test_recommendation_requires_a_trained_model(client: TestClient) -> None:
    upload = client.post(
        "/api/v1/images/upload",
        files={"file": ("source.png", source_png_bytes(0), "image/png")},
    )

    response = client.post(
        "/api/v1/recommendations", json={"image_id": upload.json()["id"]}
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "recommendation_model_not_trained"

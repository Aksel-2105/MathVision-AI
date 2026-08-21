from io import BytesIO

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image


def source_png_bytes() -> bytes:
    values = np.tile(np.arange(64, dtype=np.uint8), (48, 1))
    image = Image.fromarray(np.dstack([values, np.flip(values, axis=1), values]))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def upload_source(client: TestClient) -> str:
    response = client.post(
        "/api/v1/images/upload",
        files={"file": ("experiment.png", source_png_bytes(), "image/png")},
    )
    assert response.status_code == 201
    return response.json()["id"]


def process(client: TestClient, image_id: str, algorithm: str) -> str:
    response = client.post(
        "/api/v1/processing",
        json={"image_id": image_id, "algorithm": algorithm, "parameters": {}},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_experiment_persists_runs_comparison_and_exports(client: TestClient) -> None:
    image_id = upload_source(client)
    experiment_response = client.post(
        "/api/v1/experiments",
        json={
            "image_id": image_id,
            "name": "Denoising sweep",
            "description": "Phase 4",
        },
    )
    assert experiment_response.status_code == 201
    experiment_id = experiment_response.json()["id"]

    median_id = process(client, image_id, "median")
    gaussian_id = process(client, image_id, "gaussian")
    for processing_id in (median_id, gaussian_id):
        added = client.post(
            f"/api/v1/experiments/{experiment_id}/runs",
            json={"processing_id": processing_id},
        )
        assert added.status_code == 201

    detail = client.get(f"/api/v1/experiments/{experiment_id}")
    assert detail.status_code == 200
    assert detail.json()["run_count"] == 2
    assert len(detail.json()["runs"]) == 2

    comparison = client.get(f"/api/v1/experiments/{experiment_id}/comparison")
    assert comparison.status_code == 200
    rows = comparison.json()["rows"]
    assert [row["rank"] for row in rows] == [1, 2]
    assert rows[0]["ranking_score"] >= rows[1]["ranking_score"]

    json_export = client.get(f"/api/v1/experiments/{experiment_id}/export?format=json")
    assert json_export.status_code == 200
    assert json_export.headers["content-type"].startswith("application/json")
    assert json_export.json()["experiment"]["id"] == experiment_id

    csv_export = client.get(f"/api/v1/experiments/{experiment_id}/export?format=csv")
    assert csv_export.status_code == 200
    assert csv_export.headers["content-type"].startswith("text/csv")
    assert "rank,processing_id,algorithm" in csv_export.text


def test_experiment_rejects_duplicate_runs_and_can_be_deleted(
    client: TestClient,
) -> None:
    image_id = upload_source(client)
    experiment_id = client.post(
        "/api/v1/experiments", json={"image_id": image_id, "name": "One run"}
    ).json()["id"]
    processing_id = process(client, image_id, "median")
    assert (
        client.post(
            f"/api/v1/experiments/{experiment_id}/runs",
            json={"processing_id": processing_id},
        ).status_code
        == 201
    )
    duplicate = client.post(
        f"/api/v1/experiments/{experiment_id}/runs",
        json={"processing_id": processing_id},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "duplicate_experiment_run"

    deleted = client.delete(f"/api/v1/experiments/{experiment_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/experiments/{experiment_id}").status_code == 404


def test_comparison_rejects_results_from_different_images(client: TestClient) -> None:
    first_image = upload_source(client)
    first_processing = process(client, first_image, "median")
    second_image_response = client.post(
        "/api/v1/images/upload",
        files={"file": ("second.png", source_png_bytes(), "image/png")},
    )
    second_processing = process(client, second_image_response.json()["id"], "median")

    response = client.post(
        "/api/v1/comparisons",
        json={"processing_ids": [first_processing, second_processing]},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "comparison_image_mismatch"

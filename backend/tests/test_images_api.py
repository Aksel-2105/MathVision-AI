from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image


def png_bytes() -> bytes:
    image = Image.new("RGB", (16, 12), color=(80, 120, 160))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def test_upload_metadata_content_and_analysis_flow(client: TestClient) -> None:
    response = client.post(
        "/api/v1/images/upload",
        files={"file": ("sample.png", png_bytes(), "image/png")},
    )

    assert response.status_code == 201
    image = response.json()
    assert image["width"] == 16
    assert image["height"] == 12
    assert image["format"] == "PNG"
    assert len(image["content_hash"]) == 64

    content_response = client.get(f"/api/v1/images/{image['id']}/content")
    assert content_response.status_code == 200
    assert content_response.content == png_bytes()

    analysis_response = client.post(f"/api/v1/analysis/{image['id']}")
    assert analysis_response.status_code == 201
    analysis = analysis_response.json()
    assert analysis["image_id"] == image["id"]
    assert analysis["features"]["entropy"] == 0
    grayscale_values = analysis["histogram"]["series"][0]["values"]
    assert sum(grayscale_values) == 192
    assert max(grayscale_values) == 192

    stored_analysis = client.get(f"/api/v1/analysis/{analysis['id']}")
    assert stored_analysis.status_code == 200
    assert stored_analysis.json()["id"] == analysis["id"]


def test_invalid_and_mismatched_uploads_return_structured_errors(
    client: TestClient,
) -> None:
    unsupported = client.post(
        "/api/v1/images/upload",
        files={"file": ("sample.txt", b"not an image", "text/plain")},
    )
    assert unsupported.status_code == 415
    assert unsupported.json()["error"]["code"] == "unsupported_file_type"

    corrupted = client.post(
        "/api/v1/images/upload",
        files={"file": ("sample.png", b"not an image", "image/png")},
    )
    assert corrupted.status_code == 400
    assert corrupted.json()["error"]["code"] == "corrupted_image"

    mismatch = client.post(
        "/api/v1/images/upload",
        files={"file": ("sample.png", png_bytes(), "image/jpeg")},
    )
    assert mismatch.status_code == 415
    assert mismatch.json()["error"]["code"] == "mime_type_mismatch"


def test_delete_removes_image(client: TestClient) -> None:
    response = client.post(
        "/api/v1/images/upload",
        files={"file": ("sample.png", png_bytes(), "image/png")},
    )
    image_id = response.json()["id"]

    deleted = client.delete(f"/api/v1/images/{image_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/images/{image_id}").status_code == 404

from fastapi.testclient import TestClient
from app.config import settings


class TestUpload:
    def test_upload_success(self, client: TestClient, test_image_bytes):
        files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
        data = {"uid": "user_001", "type": "avatar"}
        headers = {"X-API-Secret": settings.API_SECRET}

        res = client.post("/api/upload", files=files, data=data, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "id" in data
        assert "url" in data
        assert data["status"] == "active"

    def test_upload_fishing_spot(self, client: TestClient, test_image_bytes):
        files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
        data = {"uid": "user_001", "type": "fishing_spot", "spot_id": "spot_888"}
        headers = {"X-API-Secret": settings.API_SECRET}

        res = client.post("/api/upload", files=files, data=data, headers=headers)
        assert res.status_code == 200

    def test_upload_catch(self, client: TestClient, test_image_bytes):
        files = {"file": ("test.png", test_image_bytes, "image/png")}
        data = {"uid": "user_002", "type": "catch"}
        headers = {"X-API-Secret": settings.API_SECRET}

        res = client.post("/api/upload", files=files, data=data, headers=headers)
        assert res.status_code == 200

    def test_upload_invalid_secret(self, client: TestClient, test_image_bytes):
        files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
        data = {"uid": "user_001", "type": "avatar"}
        headers = {"X-API-Secret": "wrong_secret"}

        res = client.post("/api/upload", files=files, data=data, headers=headers)
        assert res.status_code == 401

    def test_upload_invalid_type(self, client: TestClient, test_image_bytes):
        files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
        data = {"uid": "user_001", "type": "invalid_type"}
        headers = {"X-API-Secret": settings.API_SECRET}

        res = client.post("/api/upload", files=files, data=data, headers=headers)
        assert res.status_code == 400

    def test_upload_missing_spot_id(self, client: TestClient, test_image_bytes):
        files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
        data = {"uid": "user_001", "type": "fishing_spot"}
        headers = {"X-API-Secret": settings.API_SECRET}

        res = client.post("/api/upload", files=files, data=data, headers=headers)
        assert res.status_code == 400

    def test_upload_empty_file(self, client: TestClient):
        files = {"file": ("test.jpg", b"", "image/jpeg")}
        data = {"uid": "user_001", "type": "avatar"}
        headers = {"X-API-Secret": settings.API_SECRET}

        res = client.post("/api/upload", files=files, data=data, headers=headers)
        assert res.status_code == 400

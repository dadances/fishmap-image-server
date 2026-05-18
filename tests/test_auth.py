from fastapi.testclient import TestClient
from app.config import settings


class TestAuth:
    def test_upload_without_secret(self, client: TestClient, test_image_bytes):
        files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
        data = {"uid": "user_001", "type": "avatar"}

        res = client.post("/api/upload", files=files, data=data)
        assert res.status_code == 401

    def test_upload_with_wrong_secret(self, client: TestClient, test_image_bytes):
        files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
        data = {"uid": "user_001", "type": "avatar"}
        headers = {"X-API-Secret": "wrong"}

        res = client.post("/api/upload", files=files, data=data, headers=headers)
        assert res.status_code == 401

    def test_upload_with_correct_secret(self, client: TestClient, test_image_bytes):
        files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
        data = {"uid": "user_001", "type": "avatar"}
        headers = {"X-API-Secret": settings.API_SECRET}

        res = client.post("/api/upload", files=files, data=data, headers=headers)
        assert res.status_code == 200

    def test_admin_without_token(self, client: TestClient):
        res = client.get("/admin/api/images")
        assert res.status_code == 401

    def test_admin_with_wrong_token(self, client: TestClient):
        res = client.get("/admin/api/images", headers={"X-Admin-Token": "wrong"})
        assert res.status_code == 401

from fastapi.testclient import TestClient
from app.config import settings


class TestAdmin:
    def test_login_success(self, client: TestClient):
        res = client.post("/admin/api/login", json={"username": "admin", "password": "fishmap2024"})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "token" in data

    def test_login_failure(self, client: TestClient):
        res = client.post("/admin/api/login", json={"username": "admin", "password": "wrong"})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is False

    def test_list_images(self, client: TestClient, admin_token, test_image_bytes):
        files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
        data = {"uid": "user_001", "type": "avatar"}
        headers = {"X-API-Secret": settings.API_SECRET}
        client.post("/api/upload", files=files, data=data, headers=headers)

        res = client.get("/admin/api/images", headers={"X-Admin-Token": admin_token})
        assert res.status_code == 200
        data = res.json()
        assert "images" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_list_images_filter(self, client: TestClient, admin_token, test_image_bytes):
        files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
        data = {"uid": "user_test_filter", "type": "catch"}
        headers = {"X-API-Secret": settings.API_SECRET}
        client.post("/api/upload", files=files, data=data, headers=headers)

        res = client.get("/admin/api/images?uid=user_test_filter", headers={"X-Admin-Token": admin_token})
        assert res.status_code == 200
        data = res.json()
        assert all(img["uid"] == "user_test_filter" for img in data["images"])

    def test_stats(self, client: TestClient, admin_token, test_image_bytes):
        files = {"file": ("test.jpg", test_image_bytes, "image/jpeg")}
        data = {"uid": "user_001", "type": "avatar"}
        headers = {"X-API-Secret": settings.API_SECRET}
        client.post("/api/upload", files=files, data=data, headers=headers)

        res = client.get("/admin/api/stats", headers={"X-Admin-Token": admin_token})
        assert res.status_code == 200
        data = res.json()
        assert "total" in data
        assert "active" in data

    def test_server_info(self, client: TestClient, admin_token):
        res = client.get("/admin/api/info", headers={"X-Admin-Token": admin_token})
        assert res.status_code == 200
        data = res.json()
        assert "local_ip" in data
        assert "port" in data
        assert "test_url" in data

    def test_unauthorized_access(self, client: TestClient):
        res = client.get("/admin/api/images")
        assert res.status_code == 401

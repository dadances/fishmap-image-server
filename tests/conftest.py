import pytest
import os
import sys
import tempfile

# Set test paths before importing app
test_dir = tempfile.mkdtemp()
os.environ["IMAGE_DIR"] = os.path.join(test_dir, "images")
os.environ["BACKUP_DIR"] = os.path.join(test_dir, "images", "backup")
os.environ["DB_PATH"] = os.path.join(test_dir, "db", "images.db")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.database import init_db


@pytest.fixture(autouse=True)
def setup_test_db():
    settings.DB_PATH = tempfile.mktemp(suffix=".db")
    settings.IMAGE_DIR = tempfile.mkdtemp()
    settings.BACKUP_DIR = os.path.join(settings.IMAGE_DIR, "backup")
    init_db()
    yield
    if os.path.exists(settings.DB_PATH):
        os.remove(settings.DB_PATH)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_image_bytes():
    from PIL import Image
    import io
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def admin_token(client):
    res = client.post("/admin/api/login", json={"username": "admin", "password": "fishmap2024"})
    return res.json()["token"]

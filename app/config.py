import os
import socket
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_SECRET: str = "fishmap"
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20MB
    ALLOWED_TYPES: set = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

    IMAGE_DIR: str = os.environ.get("IMAGE_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "images"))
    BACKUP_DIR: str = os.environ.get("BACKUP_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "images", "backup"))
    DB_PATH: str = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "db", "images.db"))

    ADMIN_USER: str = os.environ.get("ADMIN_USER", "admin")
    ADMIN_PASSWORD: str = os.environ.get("ADMIN_PASSWORD", "fishmap2024")

    PORT: int = 8000

    def get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
        finally:
            s.close()

    class Config:
        env_file = ".env"


settings = Settings()

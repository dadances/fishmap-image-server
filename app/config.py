import os
import socket
import json
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_SECRET: str = "fishmap"
    DOMAIN: str = os.environ.get("DOMAIN", "fishmap.top")
    SCHEME: str = os.environ.get("SCHEME", "https")
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20MB
    ALLOWED_TYPES: set = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

    IMAGE_DIR: str = os.environ.get("IMAGE_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "images"))
    BACKUP_DIR: str = os.environ.get("BACKUP_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "images", "backup"))
    DB_PATH: str = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "db", "images.db"))

    ADMIN_USER: str = os.environ.get("ADMIN_USER", "admin")
    ADMIN_PASSWORD: str = os.environ.get("ADMIN_PASSWORD", "fishmap2024")

    PORT: int = 2000

    CONFIG_FILE: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "config.json")

    def get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
        finally:
            s.close()

    def save_config(self, **kwargs):
        config = {}
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as f:
                config = json.load(f)
        config.update(kwargs)
        os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as f:
                config = json.load(f)
            if "ADMIN_USER" in config:
                self.ADMIN_USER = config["ADMIN_USER"]
            if "ADMIN_PASSWORD" in config:
                self.ADMIN_PASSWORD = config["ADMIN_PASSWORD"]
            if "IMAGE_DIR" in config:
                self.IMAGE_DIR = config["IMAGE_DIR"]
                self.BACKUP_DIR = os.path.join(config["IMAGE_DIR"], "backup")
            if "DB_PATH" in config:
                self.DB_PATH = config["DB_PATH"]

    class Config:
        env_file = ".env"


settings = Settings()
settings.load_config()

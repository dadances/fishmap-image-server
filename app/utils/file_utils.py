import magic
from app.config import settings
from fastapi import HTTPException


def validate_file(content: bytes, filename: str, content_type: str):
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large, max {settings.MAX_FILE_SIZE // (1024*1024)}MB")

    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed")

    detected_type = magic.from_buffer(content, mime=True)
    if detected_type not in settings.ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail=f"Invalid file type: {detected_type}")

    return detected_type

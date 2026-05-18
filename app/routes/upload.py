from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from app.config import settings
from app.services import image_service
from app.utils.file_utils import validate_file
from app.schemas import UploadResponse

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    uid: str = Form(...),
    type: str = Form(...),
    spot_id: Optional[str] = Form(None),
):
    secret = request.headers.get("X-API-Secret")
    if secret != settings.API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API secret")

    if type not in ("avatar", "fishing_spot", "catch"):
        raise HTTPException(status_code=400, detail="Invalid image type")

    if type == "fishing_spot" and not spot_id:
        raise HTTPException(status_code=400, detail="spot_id is required for fishing_spot type")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    filename = file.filename or "unknown.jpg"
    mime_type = validate_file(content, filename, file.content_type or "")

    file_id = image_service.generate_id()
    ext = image_service.get_file_extension(mime_type)

    image_service.save_image(content, file_id, ext)

    client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()

    image_service.create_image_record(
        file_id=file_id,
        uid=uid,
        spot_id=spot_id,
        image_type=type,
        original_filename=filename,
        file_size=len(content),
        mime_type=mime_type,
        client_ip=client_ip,
    )

    return UploadResponse(
        id=file_id,
        url=f"/images/{file_id}{ext}",
        status="active",
    )

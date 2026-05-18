import uuid
import os
import json
from typing import Optional, Dict
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from app.config import settings
from app.services import image_service
from app.utils.file_utils import validate_file
from app.schemas import ImageListResponse, ImageInfo, StatsResponse, ServerInfoResponse, LoginRequest, LoginResponse

router = APIRouter()

ADMIN_TOKENS: Dict[str, str] = {}


def verify_admin(request: Request):
    token = request.headers.get("X-Admin-Token")
    if not token or token not in ADMIN_TOKENS:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest):
    if body.username == settings.ADMIN_USER and body.password == settings.ADMIN_PASSWORD:
        token = uuid.uuid4().hex
        ADMIN_TOKENS[token] = body.username
        return LoginResponse(success=True, token=token)
    return LoginResponse(success=False, message="Invalid credentials")


@router.get("/images", response_model=ImageListResponse)
async def list_images(
    request: Request,
    page: int = 1,
    size: int = 20,
    uid: Optional[str] = None,
    spot_id: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    _: None = Depends(verify_admin),
):
    images, total = image_service.list_images(page=page, size=size, uid=uid, spot_id=spot_id, image_type=type, status=status)
    return ImageListResponse(images=[ImageInfo(**img) for img in images], total=total, page=page, size=size)


@router.get("/recycle")
async def get_recycle_bin(
    request: Request,
    page: int = 1,
    size: int = 20,
    _: None = Depends(verify_admin),
):
    images, total = image_service.get_recycle_bin(page=page, size=size)
    return {"images": images, "total": total, "page": page, "size": size}


@router.post("/recycle/{image_id}/restore")
async def restore_image(
    image_id: str,
    request: Request,
    _: None = Depends(verify_admin),
):
    record = image_service.get_image_by_id(image_id)
    if not record or record["status"] != "recycled":
        raise HTTPException(status_code=404, detail="Image not in recycle bin")

    ext = image_service.get_file_extension(record["mime_type"])
    image_service.restore_image(image_id, ext)
    image_service.update_image_status(image_id, "active")

    return {"success": True, "message": "Image restored"}


@router.delete("/recycle/{image_id}/permanent")
async def permanent_delete(
    image_id: str,
    request: Request,
    _: None = Depends(verify_admin),
):
    record = image_service.get_image_by_id(image_id)
    if not record or record["status"] != "recycled":
        raise HTTPException(status_code=404, detail="Image not in recycle bin")

    ext = image_service.get_file_extension(record["mime_type"])
    image_service.permanent_delete(image_id, ext)

    conn = image_service.get_connection()
    conn.execute("DELETE FROM images WHERE id = ?", (image_id,))
    conn.commit()
    conn.close()

    return {"success": True, "message": "Image permanently deleted"}


@router.post("/recycle/cleanup")
async def cleanup_expired(
    request: Request,
    _: None = Depends(verify_admin),
):
    count = image_service.cleanup_expired_recycle()
    return {"success": True, "cleaned": count}


@router.post("/images/{image_id}/replace")
async def replace_image(
    image_id: str,
    request: Request,
    file: UploadFile = File(...),
    reason: str = File("不符合平台规范"),
    _: None = Depends(verify_admin),
):
    record = image_service.get_image_by_id(image_id)
    if not record:
        raise HTTPException(status_code=404, detail="Image not found")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    filename = file.filename or "placeholder.jpg"
    mime_type = validate_file(content, filename, file.content_type or "")
    ext = image_service.get_file_extension(mime_type)

    image_service.replace_image(image_id, ext, content)
    image_service.update_image_status(image_id, "replaced", reason)

    return {"success": True, "message": "Image replaced"}


@router.post("/images/{image_id}/replace-placeholder")
async def replace_with_placeholder(
    image_id: str,
    request: Request,
    reason: str = "不符合平台规范",
    _: None = Depends(verify_admin),
):
    record = image_service.get_image_by_id(image_id)
    if not record:
        raise HTTPException(status_code=404, detail="Image not found")

    ext = image_service.get_file_extension(record["mime_type"])
    placeholder = generate_placeholder(reason)
    image_service.replace_image(image_id, ext, placeholder)
    image_service.update_image_status(image_id, "replaced", reason)

    return {"success": True, "message": "Image replaced with placeholder"}


def generate_placeholder(reason: str) -> bytes:
    from PIL import Image, ImageDraw, ImageFont
    import io

    img = Image.new("RGB", (800, 600), color=(220, 220, 220))
    draw = ImageDraw.Draw(img)

    text = f"不符合平台规范\n{reason}"
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (800 - text_w) / 2
    y = (600 - text_h) / 2

    draw.text((x, y), text, fill=(128, 128, 128), font=font)

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@router.post("/images/{image_id}/recycle")
async def recycle_image(
    image_id: str,
    request: Request,
    reason: str = "不符合平台规范",
    _: None = Depends(verify_admin),
):
    record = image_service.get_image_by_id(image_id)
    if not record:
        raise HTTPException(status_code=404, detail="Image not found")

    ext = image_service.get_file_extension(record["mime_type"])
    image_service.recycle_image(image_id, ext)
    image_service.update_image_status(image_id, "recycled", reason)

    return {"success": True, "message": "Image moved to recycle bin"}


@router.delete("/images/{image_id}")
async def delete_image(
    image_id: str,
    request: Request,
    reason: str = "不符合平台规范",
    _: None = Depends(verify_admin),
):
    record = image_service.get_image_by_id(image_id)
    if not record:
        raise HTTPException(status_code=404, detail="Image not found")

    ext = image_service.get_file_extension(record["mime_type"])
    image_service.recycle_image(image_id, ext)
    image_service.update_image_status(image_id, "recycled", reason)

    return {"success": True, "message": "Image moved to recycle bin"}


@router.get("/stats", response_model=StatsResponse)
async def get_stats(_: None = Depends(verify_admin)):
    return StatsResponse(**image_service.get_stats())


@router.get("/info", response_model=ServerInfoResponse)
async def get_server_info(_: None = Depends(verify_admin)):
    local_ip = settings.get_local_ip()
    return ServerInfoResponse(
        local_ip=local_ip,
        port=settings.PORT,
        test_url=f"http://{local_ip}:{settings.PORT}",
    )


@router.get("/settings")
async def get_settings(_: None = Depends(verify_admin)):
    return {
        "image_dir": settings.IMAGE_DIR,
        "db_path": settings.DB_PATH,
        "admin_user": settings.ADMIN_USER,
        "max_file_size_mb": settings.MAX_FILE_SIZE // (1024 * 1024),
    }


@router.post("/settings")
async def update_settings(
    request: Request,
    image_dir: Optional[str] = None,
    db_path: Optional[str] = None,
    admin_user: Optional[str] = None,
    admin_password: Optional[str] = None,
    max_file_size_mb: Optional[int] = None,
    _: None = Depends(verify_admin),
):
    updates = {}
    if image_dir is not None:
        updates["IMAGE_DIR"] = image_dir
        settings.IMAGE_DIR = image_dir
        settings.BACKUP_DIR = os.path.join(image_dir, "backup")
        os.makedirs(image_dir, exist_ok=True)
        os.makedirs(settings.BACKUP_DIR, exist_ok=True)
    if db_path is not None:
        updates["DB_PATH"] = db_path
        settings.DB_PATH = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if admin_user is not None:
        updates["ADMIN_USER"] = admin_user
        settings.ADMIN_USER = admin_user
    if admin_password is not None:
        updates["ADMIN_PASSWORD"] = admin_password
        settings.ADMIN_PASSWORD = admin_password
    if max_file_size_mb is not None:
        updates["MAX_FILE_SIZE"] = max_file_size_mb * 1024 * 1024
        settings.MAX_FILE_SIZE = max_file_size_mb * 1024 * 1024

    settings.save_config(**updates)

    return {"success": True, "message": "Settings updated"}

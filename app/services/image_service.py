import os
import uuid
import shutil
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from app.config import settings
from app.database import get_connection


def ensure_dirs():
    os.makedirs(settings.IMAGE_DIR, exist_ok=True)
    os.makedirs(settings.BACKUP_DIR, exist_ok=True)


def generate_id() -> str:
    return uuid.uuid4().hex[:8]


def get_file_extension(mime_type: str) -> str:
    ext_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    return ext_map.get(mime_type, ".jpg")


def save_image(file_bytes: bytes, file_id: str, ext: str) -> str:
    ensure_dirs()
    file_path = os.path.join(settings.IMAGE_DIR, f"{file_id}{ext}")
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return file_path


def backup_image(file_id: str, ext: str):
    ensure_dirs()
    src = os.path.join(settings.IMAGE_DIR, f"{file_id}{ext}")
    if os.path.exists(src):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        dst = os.path.join(settings.BACKUP_DIR, f"{file_id}{ext}.bak.{timestamp}")
        shutil.copy2(src, dst)


def replace_image(file_id: str, ext: str, new_bytes: bytes):
    ensure_dirs()
    backup_image(file_id, ext)
    file_path = os.path.join(settings.IMAGE_DIR, f"{file_id}{ext}")
    with open(file_path, "wb") as f:
        f.write(new_bytes)


def delete_image(file_id: str, ext: str):
    ensure_dirs()
    backup_image(file_id, ext)
    file_path = os.path.join(settings.IMAGE_DIR, f"{file_id}{ext}")
    if os.path.exists(file_path):
        os.remove(file_path)


def create_image_record(
    file_id: str,
    uid: str,
    spot_id: Optional[str],
    image_type: str,
    original_filename: str,
    file_size: int,
    mime_type: str,
    client_ip: str,
) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO images (id, uid, spot_id, type, original_filename, file_size, mime_type, client_ip)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (file_id, uid, spot_id, image_type, original_filename, file_size, mime_type, client_ip),
    )
    conn.commit()
    row = cursor.execute("SELECT * FROM images WHERE id = ?", (file_id,)).fetchone()
    conn.close()
    return dict(row)


def get_image_by_id(file_id: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM images WHERE id = ?", (file_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_images(
    page: int = 1,
    size: int = 20,
    uid: Optional[str] = None,
    spot_id: Optional[str] = None,
    image_type: Optional[str] = None,
    status: Optional[str] = None,
) -> Tuple[List[dict], int]:
    conn = get_connection()
    conditions = []
    params = []

    if uid:
        conditions.append("uid = ?")
        params.append(uid)
    if spot_id:
        conditions.append("spot_id = ?")
        params.append(spot_id)
    if image_type:
        conditions.append("type = ?")
        params.append(image_type)
    if status:
        conditions.append("status = ?")
        params.append(status)

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    count_row = conn.execute(f"SELECT COUNT(*) as cnt FROM images {where}", params).fetchone()
    total = count_row["cnt"]

    offset = (page - 1) * size
    rows = conn.execute(
        f"SELECT * FROM images {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [size, offset],
    ).fetchall()

    conn.close()
    return [dict(r) for r in rows], total


def update_image_status(
    file_id: str, status: str, replace_reason: Optional[str] = None
) -> Optional[dict]:
    conn = get_connection()
    conn.execute(
        "UPDATE images SET status = ?, replace_reason = ?, updated_at = datetime('now') WHERE id = ?",
        (status, replace_reason, file_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM images WHERE id = ?", (file_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_stats() -> dict:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) as cnt FROM images").fetchone()["cnt"]
    active = conn.execute("SELECT COUNT(*) as cnt FROM images WHERE status = 'active'").fetchone()["cnt"]
    replaced = conn.execute("SELECT COUNT(*) as cnt FROM images WHERE status = 'replaced'").fetchone()["cnt"]
    deleted = conn.execute("SELECT COUNT(*) as cnt FROM images WHERE status = 'deleted'").fetchone()["cnt"]

    by_type = {}
    for row in conn.execute("SELECT type, COUNT(*) as cnt FROM images GROUP BY type").fetchall():
        by_type[row["type"]] = row["cnt"]

    conn.close()
    return {
        "total": total,
        "active": active,
        "replaced": replaced,
        "deleted": deleted,
        "by_type": by_type,
    }

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class UploadResponse(BaseModel):
    id: str
    url: str
    status: str


class ImageInfo(BaseModel):
    id: str
    uid: str
    spot_id: Optional[str] = None
    type: str
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    status: str
    replace_reason: Optional[str] = None
    client_ip: Optional[str] = None
    deleted_at: Optional[str] = None
    image_url: Optional[str] = None
    created_at: str
    updated_at: str


class ImageListResponse(BaseModel):
    images: List[ImageInfo]
    total: int
    page: int
    size: int


class StatsResponse(BaseModel):
    total: int
    active: int
    replaced: int
    recycled: int
    by_type: Dict[str, int]


class ServerInfoResponse(BaseModel):
    local_ip: str
    port: int
    test_url: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    message: Optional[str] = None

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from contextlib import asynccontextmanager
from app.database import init_db
from app.routes import upload, admin
from app.config import settings
import os


class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        if request.url.path.startswith("/images/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.IMAGE_DIR, exist_ok=True)
    os.makedirs(settings.BACKUP_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.IMAGE_DIR, "recycle"), exist_ok=True)
    init_db()
    from app.services.image_service import cleanup_orphan_files, cleanup_expired_recycle
    orph = cleanup_orphan_files()
    exp = cleanup_expired_recycle()
    if orph or exp:
        print(f"Startup cleanup: {orph} orphan files, {exp} expired recycle")

    app.mount("/images", StaticFiles(directory=settings.IMAGE_DIR), name="images")
    app.mount("/admin", StaticFiles(directory="admin", html=True), name="admin")

    yield


app = FastAPI(title="FishMap Image Server", version="1.0.0", lifespan=lifespan)

app.add_middleware(NoCacheMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(admin.router, prefix="/admin/api")


@app.get("/health")
async def health():
    return {"status": "ok"}

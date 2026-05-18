from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.routes import upload, admin
from app.config import settings
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.IMAGE_DIR, exist_ok=True)
    os.makedirs(settings.BACKUP_DIR, exist_ok=True)
    init_db()
    app.mount("/images", StaticFiles(directory=settings.IMAGE_DIR), name="images")
    app.mount("/admin", StaticFiles(directory="admin", html=True), name="admin")
    yield


app = FastAPI(title="FishMap Image Server", version="1.0.0", lifespan=lifespan)

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

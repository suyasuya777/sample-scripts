import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import get_settings
from routers import auth, item
from storage import UPLOAD_ROOT, ensure_dirs

ensure_dirs()

app = FastAPI()

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


app.mount("/images", StaticFiles(directory=str(UPLOAD_ROOT)), name="images")

app.include_router(item.router)
app.include_router(auth.router)

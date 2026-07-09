from __future__ import annotations

import io
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image

UPLOAD_ROOT = Path("uploads")
ITEMS_DIR = UPLOAD_ROOT / "items"

PUBLIC_PREFIX = "/images"

ALLOWED_FORMATS: dict[str, str] = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
    "GIF": ".gif",
}

MAX_BYTES = 5 * 1024 * 1024


def ensure_dirs() -> None:
    ITEMS_DIR.mkdir(parents=True, exist_ok=True)


async def save_item_image(file: UploadFile, item_id: int) -> str:

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="空のファイルです",
        )
    if len(content) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="画像サイズが大きすぎます（最大5MB）",
        )

    try:
        img = Image.open(io.BytesIO(content))
        detected = img.format
        img.verify()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="画像として認識できないファイルです",
        )

    ext = ALLOWED_FORMATS.get(detected)
    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="対応していない画像形式です（jpeg / png / webp / gif のみ）"
        )

    ensure_dirs()
    filename = f"{item_id}_{uuid.uuid4().hex}{ext}"
    (ITEMS_DIR / filename).write_bytes(content)

    return f"{PUBLIC_PREFIX}/items/{filename}"


def delete_item_image(image_url: str | None) -> None:
    if not image_url:
        return
    # /images/items/<name> → uploads/items/<name>
    path = ITEMS_DIR / Path(image_url).name
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass

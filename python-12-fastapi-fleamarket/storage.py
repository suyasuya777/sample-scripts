from __future__ import annotations

import io
import logging
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

logger = logging.getLogger(__name__)


def ensure_dirs() -> None:
    ITEMS_DIR.mkdir(parents=True, exist_ok=True)


async def save_item_image(file: UploadFile, item_id: int) -> str:

    if file.size is not None and file.size > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="画像サイズが大きすぎます（最大5MB）",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="空のファイルです",
        )
    if len(content) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="画像サイズが大きすぎます（最大5MB）",
        )

    try:
        with Image.open(io.BytesIO(content)) as probe:
            detected = probe.format
            probe.verify()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="画像として認識できないファイルです",
        ) from None

    ext = ALLOWED_FORMATS.get(detected)
    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="対応していない画像形式です（jpeg / png / webp / gif のみ）",
        )

    filename = f"{item_id}_{uuid.uuid4().hex}{ext}"
    path = ITEMS_DIR / filename

    try:
        with Image.open(io.BytesIO(content)) as img:
            img.save(path, format=detected)
    except Exception:
        path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="画像を保存できませんでした",
        ) from None

    return f"{PUBLIC_PREFIX}/items/{filename}"


def delete_item_image(image_url: str | None) -> None:
    if not image_url:
        return
    # /images/items/<name> → uploads/items/<name>
    path = ITEMS_DIR / Path(image_url).name
    try:
        path.unlink(missing_ok=True)
    except OSError:
        logger.warning("画像の削除に失敗しました: %s", path, exc_info=True)

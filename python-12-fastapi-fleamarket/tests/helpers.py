"""テスト用の画像バイト列を生成するヘルパー"""

import io

from PIL import Image

# 手組みの Exif ブロック（Make タグに "MyPhone" を格納）
_EXIF_TIFF = (
    b"MM\x00\x2a\x00\x00\x00\x08"
    b"\x00\x01"
    b"\x01\x0f\x00\x02\x00\x00\x00\x08\x00\x00\x00\x1a"
    b"\x00\x00\x00\x00"
    b"MyPhone\x00"
)


def _encode(fmt: str, size=(8, 8), **kwargs) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, (0, 180, 90)).save(buf, format=fmt, **kwargs)
    return buf.getvalue()


def png_bytes(size=(8, 8)) -> bytes:
    return _encode("PNG", size)


def bmp_bytes() -> bytes:
    """許可されていない画像形式（415 の検証用）"""
    return _encode("BMP")


def jpeg_with_exif_bytes() -> bytes:
    """Exif（撮影端末情報）を含む JPEG"""
    return _encode("JPEG", exif=b"Exif\x00\x00" + _EXIF_TIFF)


def polyglot_png_bytes() -> bytes:
    """画像として正常だが、末尾にスクリプトを埋め込んだファイル"""
    return png_bytes() + b"<script>alert(document.cookie)</script>"

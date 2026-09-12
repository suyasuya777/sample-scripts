"""画像アップロードの検証（形式判定・サイズ制限・再エンコード・後始末）

`image_dir` フィクスチャで保存先を一時ディレクトリに差し替えているため、
実際の uploads/ には書き込まれない。
"""

import pytest
from httpx import AsyncClient

from tests.helpers import (
    bmp_bytes,
    jpeg_with_exif_bytes,
    polyglot_png_bytes,
    png_bytes,
)

MAX_BYTES = 5 * 1024 * 1024


def saved_file(image_dir):
    """保存されたファイルを1件だけ取り出す"""
    files = sorted(image_dir.glob("*"))
    assert len(files) == 1, f"想定と異なるファイル数: {files}"
    return files[0]


# --- 正常系 ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_png_をアップロードできる(client_fixture: AsyncClient, image_dir):
    response = await client_fixture.post(
        "/items/1/image", files={"file": ("a.png", png_bytes(), "image/png")}
    )
    assert response.status_code == 200

    image_url = response.json()["image_url"]
    assert image_url.startswith("/images/items/")
    assert image_url.endswith(".png")
    assert saved_file(image_dir).name == image_url.rsplit("/", 1)[-1]


@pytest.mark.asyncio
async def test_ファイル名は元の名前を含まない(
    client_fixture: AsyncClient, image_dir
):
    response = await client_fixture.post(
        "/items/1/image", files={"file": ("secret.png", png_bytes(), "image/png")}
    )
    assert response.status_code == 200
    assert "secret" not in saved_file(image_dir).name
    assert saved_file(image_dir).name.startswith("1_")


@pytest.mark.asyncio
async def test_出品と同時に画像を送れる(client_fixture: AsyncClient, image_dir):
    response = await client_fixture.post(
        "/items",
        data={"name": "カメラ", "price": 5000},
        files={"file": ("a.png", png_bytes(), "image/png")},
    )
    assert response.status_code == 201
    assert response.json()["image_url"].endswith(".png")
    assert len(list(image_dir.glob("*"))) == 1


# --- 形式判定（拡張子・Content-Type を信用しない） ---------------------------

@pytest.mark.asyncio
async def test_拡張子偽装は実データの形式で保存される(
    client_fixture: AsyncClient, image_dir
):
    """evil.php という名前の PNG を送っても .png として保存される"""
    response = await client_fixture.post(
        "/items/1/image",
        files={"file": ("evil.php", png_bytes(), "application/x-php")},
    )
    assert response.status_code == 200
    assert saved_file(image_dir).suffix == ".png"


@pytest.mark.asyncio
async def test_対応外の画像形式は415(client_fixture: AsyncClient, image_dir):
    response = await client_fixture.post(
        "/items/1/image", files={"file": ("a.bmp", bmp_bytes(), "image/bmp")}
    )
    assert response.status_code == 415
    assert list(image_dir.glob("*")) == []


@pytest.mark.asyncio
async def test_画像でないファイルは415(client_fixture: AsyncClient, image_dir):
    response = await client_fixture.post(
        "/items/1/image",
        files={"file": ("a.png", b"hello world" * 50, "image/png")},
    )
    assert response.status_code == 415
    assert list(image_dir.glob("*")) == []


# --- サイズ制限 --------------------------------------------------------------

@pytest.mark.asyncio
async def test_空ファイルは400(client_fixture: AsyncClient, image_dir):
    response = await client_fixture.post(
        "/items/1/image", files={"file": ("a.png", b"", "image/png")}
    )
    assert response.status_code == 400
    assert list(image_dir.glob("*")) == []


@pytest.mark.asyncio
async def test_5MB超は413(client_fixture: AsyncClient, image_dir):
    oversized = b"x" * (MAX_BYTES + 1)
    response = await client_fixture.post(
        "/items/1/image", files={"file": ("big.png", oversized, "image/png")}
    )
    assert response.status_code == 413
    assert list(image_dir.glob("*")) == []


# --- 再エンコード ------------------------------------------------------------

@pytest.mark.asyncio
async def test_末尾に埋め込まれたスクリプトが除去される(
    client_fixture: AsyncClient, image_dir
):
    payload = polyglot_png_bytes()
    assert b"<script>" in payload  # 送信前は含まれている

    response = await client_fixture.post(
        "/items/1/image", files={"file": ("a.png", payload, "image/png")}
    )
    assert response.status_code == 200
    assert b"<script>" not in saved_file(image_dir).read_bytes()


@pytest.mark.asyncio
async def test_exifが除去される(client_fixture: AsyncClient, image_dir):
    payload = jpeg_with_exif_bytes()
    assert b"MyPhone" in payload  # 送信前は含まれている

    response = await client_fixture.post(
        "/items/1/image", files={"file": ("a.jpg", payload, "image/jpeg")}
    )
    assert response.status_code == 200
    assert saved_file(image_dir).suffix == ".jpg"
    assert b"MyPhone" not in saved_file(image_dir).read_bytes()


# --- ファイルの後始末 --------------------------------------------------------

@pytest.mark.asyncio
async def test_差し替え時に旧ファイルが削除される(
    client_fixture: AsyncClient, image_dir
):
    first = await client_fixture.post(
        "/items/1/image", files={"file": ("a.png", png_bytes(), "image/png")}
    )
    old_name = first.json()["image_url"].rsplit("/", 1)[-1]

    second = await client_fixture.post(
        "/items/1/image", files={"file": ("b.png", png_bytes((16, 16)), "image/png")}
    )
    new_name = second.json()["image_url"].rsplit("/", 1)[-1]

    assert old_name != new_name
    assert not (image_dir / old_name).exists()
    assert (image_dir / new_name).exists()


@pytest.mark.asyncio
async def test_アイテム削除で画像ファイルも削除される(
    client_fixture: AsyncClient, image_dir
):
    await client_fixture.post(
        "/items/1/image", files={"file": ("a.png", png_bytes(), "image/png")}
    )
    assert len(list(image_dir.glob("*"))) == 1

    response = await client_fixture.delete("/items/1")
    assert response.status_code == 204
    assert list(image_dir.glob("*")) == []


@pytest.mark.asyncio
async def test_画像なしのアイテム削除でも例外にならない(
    client_fixture: AsyncClient, image_dir
):
    response = await client_fixture.delete("/items/1")
    assert response.status_code == 204

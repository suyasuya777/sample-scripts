"""
学習ポイント: ファイルアップロード
- UploadFile : アップロードされたファイルオブジェクト
- File       : ファイルフィールドの宣言
- Form       : フォームデータの受け取り
- 複数ファイル: List[UploadFile]
"""
import os
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(""),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="許可されていないファイル形式です")
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="ファイルサイズが上限を超えています")
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        f.write(content)
    return {"filename": file.filename, "size": len(content), "description": description}

@app.post("/upload/multiple")
async def upload_multiple(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        content = await file.read()
        results.append({"filename": file.filename, "size": len(content)})
    return results

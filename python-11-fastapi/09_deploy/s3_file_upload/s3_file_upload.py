"""
学習ポイント: AWS S3へのファイルアップロード（α）
- boto3         : AWS SDK for Python
- presigned URL : 一時的な署名付きURLを生成してクライアントから直接アップロード
- put_object    : サーバー経由でS3にアップロード

実行前に AWS 認証情報を設定:
  export AWS_ACCESS_KEY_ID=xxx
  export AWS_SECRET_ACCESS_KEY=xxx
  export AWS_DEFAULT_REGION=ap-northeast-1
"""
import os
import boto3
from fastapi import FastAPI, UploadFile, File, HTTPException
from botocore.exceptions import ClientError

app = FastAPI()
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "your-bucket-name")
s3_client = boto3.client("s3", region_name=os.getenv("AWS_DEFAULT_REGION", "ap-northeast-1"))

@app.post("/upload/s3")
async def upload_to_s3(file: UploadFile = File(...)):
    """サーバー経由でS3にアップロード"""
    try:
        content = await file.read()
        s3_key = f"uploads/{file.filename}"
        s3_client.put_object(
            Bucket=S3_BUCKET, Key=s3_key,
            Body=content, ContentType=file.content_type,
        )
        url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"
        return {"s3_key": s3_key, "url": url}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3アップロード失敗: {e}")

@app.get("/upload/presigned-url")
async def get_presigned_url(filename: str, content_type: str = "image/jpeg"):
    """クライアントが直接S3にアップロードするための署名付きURL生成"""
    try:
        s3_key = f"uploads/{filename}"
        presigned = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": S3_BUCKET, "Key": s3_key, "ContentType": content_type},
            ExpiresIn=300,  # 5分間有効
        )
        return {"upload_url": presigned, "s3_key": s3_key, "expires_in": 300}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

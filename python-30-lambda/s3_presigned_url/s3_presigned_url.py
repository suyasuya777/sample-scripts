import json
import logging
import boto3
from botocore.config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client(
    "s3",
    config=Config(signature_version="s3v4"),  # Presigned URL は SigV4 を使用
)

BUCKET_NAME = "your-bucket-name"
EXPIRES_IN = 3600  # 有効期限（秒）


# ── アップロード用 URL 生成 ────────────────────────────────────
def generate_upload_url(key: str, content_type: str = "application/octet-stream") -> str:
    """
    put_object 用の署名付き URL を生成する。
    クライアントはこの URL に対して PUT リクエストでファイルをアップロードする。
    Content-Type を指定することでファイル種別を制限できる。
    """
    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=EXPIRES_IN,
    )
    logger.info("upload url generated: key=%s", key)
    return url


# ── ダウンロード用 URL 生成 ────────────────────────────────────
def generate_download_url(key: str) -> str:
    """
    get_object 用の署名付き URL を生成する。
    クライアントはこの URL に GET リクエストするだけでファイルを取得できる。
    """
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": key,
        },
        ExpiresIn=EXPIRES_IN,
    )
    logger.info("download url generated: key=%s", key)
    return url


# ── Lambda ハンドラー ─────────────────────────────────────────
def lambda_handler(event: dict, context) -> dict:
    params = event.get("queryStringParameters") or {}
    action = params.get("action", "download")
    key = params.get("key")

    if not key:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "key パラメータが必要です"}),
        }

    if action == "upload":
        content_type = params.get("content_type", "application/octet-stream")
        url = generate_upload_url(key, content_type)
    else:
        url = generate_download_url(key)

    return {
        "statusCode": 200,
        "body": json.dumps({"url": url, "expires_in": EXPIRES_IN}),
    }

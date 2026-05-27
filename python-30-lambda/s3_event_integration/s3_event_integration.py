import json
import logging
import urllib.parse
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")


# ── ファイル種別ごとの処理 ─────────────────────────────────────
def process_image(bucket: str, key: str) -> None:
    """画像リサイズ処理の雛形"""
    logger.info("画像リサイズ: bucket=%s key=%s", bucket, key)
    # 例: Pillow / Lambda Layer で実装
    # obj = s3.get_object(Bucket=bucket, Key=key)
    # image = Image.open(obj["Body"])
    # resized = image.resize((800, 600))
    # ...


def process_csv(bucket: str, key: str) -> None:
    """CSV パース処理の雛形"""
    logger.info("CSV パース: bucket=%s key=%s", bucket, key)
    obj = s3.get_object(Bucket=bucket, Key=key)
    lines = obj["Body"].read().decode("utf-8").splitlines()
    logger.info("行数: %d", len(lines))
    # 各行を処理する実装をここに追加


def process_default(bucket: str, key: str) -> None:
    """その他ファイルの処理"""
    logger.info("未対応ファイル: bucket=%s key=%s", bucket, key)


# ── ファイル種別の判定 ─────────────────────────────────────────
def dispatch(bucket: str, key: str) -> None:
    ext = key.rsplit(".", 1)[-1].lower() if "." in key else ""
    if ext in ("jpg", "jpeg", "png", "gif", "webp"):
        process_image(bucket, key)
    elif ext == "csv":
        process_csv(bucket, key)
    else:
        process_default(bucket, key)


# ── Lambda ハンドラー ─────────────────────────────────────────
def lambda_handler(event: dict, context) -> dict:
    logger.info("event: %s", json.dumps(event))

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        # キー名は URL エンコードされているためデコードが必要
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        size = record["s3"]["object"].get("size", 0)
        logger.info("bucket=%s key=%s size=%d", bucket, key, size)
        dispatch(bucket, key)

    return {"statusCode": 200, "body": "OK"}

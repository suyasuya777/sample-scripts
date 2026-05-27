import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ── グローバルキャッシュ（Lambda 実行環境の再利用を活用）────────
# 同一コンテナが再利用される間はキャッシュが有効。コールドスタート時のみ取得する。
_secrets_cache: dict = {}
_params_cache: dict = {}

secrets_client = boto3.client("secretsmanager")
ssm_client = boto3.client("ssm")


# ── Secrets Manager ───────────────────────────────────────────
def get_secret(secret_name: str) -> dict:
    """
    Secrets Manager からシークレットを取得してキャッシュする。
    DB 認証情報など JSON 形式のシークレットを想定。
    """
    if secret_name in _secrets_cache:
        logger.info("secrets cache hit: %s", secret_name)
        return _secrets_cache[secret_name]

    try:
        result = secrets_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(result["SecretString"])
        _secrets_cache[secret_name] = secret
        logger.info("secrets fetched: %s", secret_name)
        return secret
    except ClientError as e:
        logger.error("get_secret error: %s", e)
        raise


# ── SSM Parameter Store ───────────────────────────────────────
def get_parameter(param_name: str, with_decryption: bool = True) -> str:
    """
    SSM Parameter Store からパラメータを取得してキャッシュする。
    with_decryption=True で SecureString も復号して取得できる。
    """
    if param_name in _params_cache:
        logger.info("ssm cache hit: %s", param_name)
        return _params_cache[param_name]

    try:
        result = ssm_client.get_parameter(
            Name=param_name,
            WithDecryption=with_decryption,
        )
        value = result["Parameter"]["Value"]
        _params_cache[param_name] = value
        logger.info("ssm fetched: %s", param_name)
        return value
    except ClientError as e:
        logger.error("get_parameter error: %s", e)
        raise


# ── Lambda ハンドラー ─────────────────────────────────────────
def lambda_handler(event: dict, context) -> dict:
    # DB 認証情報を Secrets Manager から取得
    db_secret = get_secret("/myapp/prod/db")
    db_host = db_secret.get("host")
    db_user = db_secret.get("username")

    # 設定値を SSM から取得
    api_endpoint = get_parameter("/myapp/prod/api_endpoint")

    logger.info("db_host=%s api_endpoint=%s", db_host, api_endpoint)

    return {
        "statusCode": 200,
        "body": json.dumps({"db_host": db_host, "api_endpoint": api_endpoint}),
    }

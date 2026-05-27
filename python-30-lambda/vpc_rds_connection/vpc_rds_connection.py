import json
import logging
import boto3
import pymysql        # pip install pymysql
# import psycopg2     # PostgreSQL の場合はこちら

logger = logging.getLogger()
logger.setLevel(logging.INFO)

secrets_client = boto3.client("secretsmanager")

SECRET_NAME = "/myapp/prod/db"

# ── グローバルコネクション（Lambda 実行環境の再利用で接続を維持）──
_connection = None


def get_db_secret() -> dict:
    """Secrets Manager から DB 認証情報を取得"""
    result = secrets_client.get_secret_value(SecretId=SECRET_NAME)
    return json.loads(result["SecretString"])


def get_connection():
    """
    コネクションを再利用する。
    接続が切れていた場合は再接続する（RDS Proxy 使用時はプーリングを任せられる）。
    """
    global _connection
    try:
        if _connection and _connection.open:
            _connection.ping(reconnect=True)
            return _connection
    except Exception:
        _connection = None

    secret = get_db_secret()
    _connection = pymysql.connect(
        host=secret["host"],
        user=secret["username"],
        password=secret["password"],
        database=secret.get("dbname", "mydb"),
        port=int(secret.get("port", 3306)),
        connect_timeout=5,
        cursorclass=pymysql.cursors.DictCursor,
    )
    logger.info("DB 接続確立: host=%s", secret["host"])
    return _connection


# ── クエリ実行 ────────────────────────────────────────────────
def fetch_users(limit: int = 10) -> list:
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name, email FROM users LIMIT %s", (limit,))
        return cursor.fetchall()


# ── Lambda ハンドラー ─────────────────────────────────────────
def lambda_handler(event: dict, context) -> dict:
    try:
        users = fetch_users(limit=event.get("limit", 10))
        logger.info("取得件数: %d", len(users))
        return {
            "statusCode": 200,
            "body": json.dumps(users, ensure_ascii=False, default=str),
        }
    except Exception as e:
        logger.error("DB エラー: %s", e)
        return {"statusCode": 500, "body": json.dumps({"message": "DB エラー"})}

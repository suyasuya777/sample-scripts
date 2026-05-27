import logging
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ── バリデーション設定 ────────────────────────────────────────
ALLOWED_DOMAINS = {"example.com", "company.co.jp"}
FORBIDDEN_WORDS = {"spam", "test123", "admin"}


def validate_email_domain(email: str) -> str | None:
    """メールドメインを許可リストで制限する"""
    domain = email.split("@")[-1].lower() if "@" in email else ""
    if domain not in ALLOWED_DOMAINS:
        return f"メールドメイン {domain} は許可されていません"
    return None


def validate_username(username: str) -> str | None:
    """禁止ワードチェック"""
    lower = username.lower()
    for word in FORBIDDEN_WORDS:
        if word in lower:
            return f"ユーザー名に禁止ワード '{word}' が含まれています"
    return None


def validate_password_strength(password: str) -> str | None:
    """パスワード強度チェック（8文字以上・英数字混在）"""
    if len(password) < 8:
        return "パスワードは8文字以上にしてください"
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "パスワードは英字と数字を組み合わせてください"
    return None


# ── Lambda ハンドラー ─────────────────────────────────────────
def lambda_handler(event: dict, context) -> dict:
    """
    Cognito Pre Sign-up トリガー。
    event を変更して返すことで Cognito の動作を制御する。
    例外を raise すると Cognito がサインアップを拒否する。
    """
    user_attributes = event["request"]["userAttributes"]
    email = user_attributes.get("email", "")
    username = event.get("userName", "")
    password = event["request"].get("password", "")

    logger.info("Pre Sign-up: username=%s email=%s", username, email)

    # バリデーション実行
    for error in [
        validate_email_domain(email),
        validate_username(username),
        validate_password_strength(password),
    ]:
        if error:
            logger.warning("サインアップ拒否: %s", error)
            raise Exception(error)

    # 自動確認・自動検証フラグ（開発環境などで使用）
    event["response"]["autoConfirmUser"] = False   # True にすると確認メール不要
    event["response"]["autoVerifyEmail"] = False   # True にするとメール自動検証

    logger.info("サインアップ許可: %s", username)
    return event

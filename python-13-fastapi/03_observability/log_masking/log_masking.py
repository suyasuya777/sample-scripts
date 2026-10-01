"""
学習ポイント: ログに載せてはいけないもの
- 認証系   : Authorization / Cookie / X-API-Key / セッションID
- 資格情報 : パスワード、トークン、秘密鍵、カード番号
- 個人情報 : メールアドレス、電話番号、住所（用途によっては可）
- 経路     : ヘッダ、クエリ文字列、リクエストボディ、例外メッセージ

SRE 的な論点:
  リクエストボディを丸ごとログに出す実装は、便利だが事故の温床。
  一度出力されたログは保持期間中ずっと残り、ログ閲覧権限を持つ全員が見られる。
  「調査のために一時的に」入れた全文ログが消し忘れられるのが典型的な経路。

  ログに出さないことより、「出しても問題ない形に落としてから出す」ほうが
  運用として続く。マスク関数を1つ作り、ログ出力を必ず経由させる。
"""
import re

SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key", "proxy-authorization"}
SENSITIVE_KEYS = {"password", "passwd", "secret", "token", "access_token",
                  "refresh_token", "api_key", "card_number", "cvv"}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def mask_value(v: str) -> str:
    if len(v) <= 4:
        return "***"
    return f"{v[:2]}***{v[-2:]}"


def mask_headers(headers: dict) -> dict:
    return {
        k: ("***" if k.lower() in SENSITIVE_HEADERS else v)
        for k, v in headers.items()
    }


def mask_body(obj):
    """辞書・リストを再帰的にたどってマスクする"""
    if isinstance(obj, dict):
        return {
            k: ("***" if k.lower() in SENSITIVE_KEYS else mask_body(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [mask_body(v) for v in obj]
    if isinstance(obj, str):
        return EMAIL_RE.sub(lambda m: mask_value(m.group()), obj)
    return obj


if __name__ == "__main__":
    h = {"Authorization": "Bearer eyJhbGciOi...", "User-Agent": "curl/8.0"}
    b = {"email": "taro@example.com", "password": "p@ssw0rd",
         "items": [{"token": "abcdef123456", "qty": 1}]}
    print(mask_headers(h))
    print(mask_body(b))

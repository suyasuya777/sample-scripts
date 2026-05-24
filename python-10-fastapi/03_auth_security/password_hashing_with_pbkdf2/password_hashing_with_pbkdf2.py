"""
学習ポイント: PBKDF2-HMAC-SHA256 によるパスワードハッシュ化
- os.urandom(32)     : 暗号論的に安全な32バイトのランダムバイト列（ソルト生成）
- base64.b64encode() : バイト列をBase64文字列に変換（DB保存用）
- hashlib.pbkdf2_hmac: PBKDF2-HMAC-SHA256でパスワードをハッシュ化
  - 反復回数(iterations)が多いほど総当たり攻撃に強い
- ソルトの役割       : 同じパスワードでも異なるハッシュ値になる（レインボーテーブル対策）
"""
import hashlib
import base64
import os

ITERATIONS = 1000  # 本番では100000以上を推奨

def generate_salt() -> tuple[bytes, str]:
    """32バイトのランダムソルトを生成してBase64エンコード"""
    raw_salt = os.urandom(32)
    encoded_salt = base64.b64encode(raw_salt)
    return encoded_salt, encoded_salt.decode()

def hash_password(plain_password: str, salt: bytes) -> str:
    """PBKDF2-HMAC-SHA256でパスワードをハッシュ化"""
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        ITERATIONS,
    )
    return hashed.hex()

def verify_password(plain_password: str, stored_salt: str, stored_hash: str) -> bool:
    """入力パスワードを同じソルトで再ハッシュして比較"""
    recalculated = hash_password(plain_password, stored_salt.encode())
    return recalculated == stored_hash

# ── 使用例 ─────────────────────────────────────────────
if __name__ == "__main__":
    password = "mySecurePassword123"
    salt_bytes, salt_str = generate_salt()
    hashed = hash_password(password, salt_bytes)

    print(f"Salt (stored in DB): {salt_str}")
    print(f"Hash (stored in DB): {hashed}")
    print(f"Verify correct password: {verify_password(password, salt_str, hashed)}")
    print(f"Verify wrong password:   {verify_password('wrong', salt_str, hashed)}")

"""
学習ポイント: Pydanticによるバリデーション
- Field制約    : min_length / max_length / gt / ge / lt / le / regex
- @field_validator: カスタムバリデーター
- @model_validator : 複数フィールドをまたぐバリデーション
- ValidationError  : バリデーション失敗時の例外
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8)
    confirm_password: str
    age: Optional[int] = Field(None, ge=0, le=120)
    email: str = Field(examples=["user@example.com"])

    @field_validator("username")
    @classmethod
    def username_not_reserved(cls, v: str) -> str:
        """予約語チェック"""
        reserved = ["admin", "root", "system"]
        if v.lower() in reserved:
            raise ValueError(f"'{v}' は使用できないユーザー名です")
        return v

    @field_validator("email")
    @classmethod
    def email_format(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("メールアドレスの形式が正しくありません")
        return v.lower()

    @model_validator(mode="after")
    def passwords_match(self):
        """パスワードと確認用パスワードの一致チェック"""
        if self.password != self.confirm_password:
            raise ValueError("パスワードが一致しません")
        return self


if __name__ == "__main__":
    try:
        u = UserCreate(username="admin", password="pass1234", confirm_password="pass1234", email="a@b.com")
    except Exception as e:
        print(f"Error: {e}")
    u = UserCreate(username="user1", password="pass1234", confirm_password="pass1234", email="User@Example.com")
    print(u.model_dump())

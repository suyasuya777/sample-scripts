from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="ユーザー名（1〜50文字）")
    email: EmailStr = Field(..., description="メールアドレス（形式バリデーションあり）")


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    items: list["ItemResponse"] = Field(default=[], description="所有アイテム一覧")

    model_config = {"from_attributes": True}


# 循環参照を解決するため末尾でインポート＆rebuild
from schemas.item import ItemResponse  # noqa: E402
UserResponse.model_rebuild()

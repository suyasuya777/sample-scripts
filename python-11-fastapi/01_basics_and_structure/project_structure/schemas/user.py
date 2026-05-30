from __future__ import annotations
from typing import Annotated
from pydantic import BaseModel, Field, EmailStr

NameStr = Annotated[
    str, Field(min_length=1, max_length=50, description="ユーザー名（1〜50文字）")
]
EmailStr_ = Annotated[
    EmailStr, Field(description="メールアドレス（形式バリデーションあり）")
]


class UserBase(BaseModel):
    name: NameStr
    email: EmailStr_


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Annotated[
        str | None, Field(None, min_length=1, max_length=50, description="ユーザー名（1〜50文字）")
    ] = None
    email: Annotated[
        EmailStr | None, Field(None, description="メールアドレス（形式バリデーションあり）")
    ] = None


class UserResponse(UserBase):
    id: int
    items: Annotated[
        list[ItemResponse], Field(default=[], description="所有アイテム一覧")
    ] = []

    model_config = {"from_attributes": True}


# 循環参照を解決するため末尾でインポート＆rebuild
from schemas.item import ItemResponse  # noqa: E402

UserResponse.model_rebuild()

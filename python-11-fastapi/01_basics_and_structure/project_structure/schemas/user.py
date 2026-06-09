from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from schemas import item as item_schema

UserName = Annotated[
    str,
    Field(
        min_length=1,
        max_length=50,
        description="ユーザー名"
    )
]

UserEmail = Annotated[
    EmailStr,
    Field(
        max_length=50,
        description="メールアドレス"
    )
]

UserOptionalName = Annotated[
    str | None,
    Field(
        min_length=1,
        max_length=50,
        description="ユーザー名（省略可）"
    )
]

UserOptionalEmail = Annotated[
    EmailStr | None,
    Field(
        max_length=50,
        description="メールアドレス（省略可）"
    )
]

UserItems = Annotated[
    list[item_schema.ItemResponse],
    Field(
        description="所有アイテム一覧"
    )
]


class UserBase(BaseModel):
    name: UserName
    email: UserEmail


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: UserOptionalName = None
    email: UserOptionalEmail = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    items: UserItems = Field(default_factory=list)

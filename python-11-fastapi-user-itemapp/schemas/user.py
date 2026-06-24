from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from schemas.item import ItemResponse

UserName = Annotated[
    str,
    Field(
        min_length=1,
        max_length=50,
        description="ユーザ名"
    )
]

UserEmail = Annotated[
    EmailStr,
    Field(
        max_length=254,
        description="メールアドレス"
    )
]

UserOptionalName = Annotated[
    str | None,
    Field(
        min_length=1,
        max_length=50,
        description="ユーザ名（省略可）"
    )
]

UserOptionalEmail = Annotated[
    EmailStr | None,
    Field(
        max_length=254,
        description="メールアドレス（省略可）"
    )
]

UserItems = Annotated[
    list[ItemResponse],
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

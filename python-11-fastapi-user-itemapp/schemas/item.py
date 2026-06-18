from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


ItemTitle = Annotated[
    str,
    Field(
        min_length=1,
        max_length=50,
        description="タイトル"
    )
]

ItemDescription = Annotated[
    str | None,
    Field(
        max_length=255,
        description="説明"
    )
]

ItemUserId = Annotated[
    int,
    Field(
        gt=0,
        description="所有ユーザＩＤ"
    )
]

ItemOptionalTitle = Annotated[
    str | None,
    Field(
        min_length=1,
        max_length=50,
        description="タイトル（省略可）"
    )
]

ItemOptionalDescription = Annotated[
    str | None,
    Field(
        max_length=255,
        description="説明（省略可）"
    )
]

ItemOptionalUserId = Annotated[
    int | None,
    Field(
        gt=0,
        description="所有ユーザＩＤ（省略可）"
    )
]


class ItemBase(BaseModel):
    title: ItemTitle
    description: ItemDescription
    user_id: ItemUserId


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: ItemOptionalTitle
    description: ItemOptionalDescription
    user_id: ItemOptionalUserId


class ItemResponse(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
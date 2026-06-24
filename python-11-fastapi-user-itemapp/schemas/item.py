from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict


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
        min_length=1,
        max_length=255,
        description="説明（省略可）"
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

ItemOptionalDescription = ItemDescription

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
    title: ItemOptionalTitle = None
    description: ItemOptionalDescription = None
    user_id: ItemOptionalUserId = None


class ItemResponse(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

from typing import Annotated

from pydantic import BaseModel, Field

TitleStr = Annotated[
    str, Field(..., min_length=1, max_length=100, description="タイトル（1〜100文字）")
]
DescriptionStr = Annotated[
    str | None, Field(None, max_length=500, description="説明（500文字以内）")
]
UserIdInt = Annotated[
    int, Field(..., gt=0, description="所有ユーザーID（1以上の整数）")
]


class ItemBase(BaseModel):
    title: TitleStr
    description: DescriptionStr
    user_id: UserIdInt


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Annotated[
        str | None, Field(None, min_length=1, max_length=100, description="タイトル")
    ] = None
    description: DescriptionStr = None
    user_id: Annotated[
        int | None, Field(None, gt=0, description="所有ユーザーID（1以上の整数）")
    ] = None


class ItemResponse(ItemBase):
    id: int

    model_config = {"from_attributes": True}

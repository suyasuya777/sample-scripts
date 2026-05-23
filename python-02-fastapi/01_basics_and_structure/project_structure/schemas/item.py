from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="タイトル（1〜100文字）")
    description: str | None = Field(None, max_length=500, description="説明（500文字以内）")
    user_id: int = Field(..., gt=0, description="所有ユーザーID（1以上の整数）")


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int

    model_config = {"from_attributes": True}

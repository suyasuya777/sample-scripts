from datetime import datetime
from enum import Enum
from typing import Annotated, Optional
from pydantic import BaseModel, Field, ConfigDict


class ItemStatus(Enum):
    ON_SALE = "ON_SALE"
    SOLD_OUT = "SOLD_OUT"


# ── 型エイリアス ──────────────────────────────────────────
ItemId = Annotated[int, Field(gt=0, examples=[1])]
ItemName = Annotated[str, Field(min_length=2, max_length=20, examples=["PC"])]
ItemPrice = Annotated[int, Field(gt=0, examples=[10000])]
ItemDesc = Annotated[Optional[str], Field(None, examples=["美品です"])]
ItemNameOpt = Annotated[
    Optional[str], Field(None, min_length=2, max_length=20, examples=["PC"])
]
ItemPriceOpt = Annotated[Optional[int], Field(None, gt=0, examples=[10000])]
ItemStatusOpt = Annotated[
    Optional[ItemStatus], Field(None, examples=[ItemStatus.SOLD_OUT])
]

UserId = Annotated[int, Field(gt=0, examples=[1])]
Username = Annotated[str, Field(min_length=2, examples=["user1"])]
Password = Annotated[str, Field(min_length=8, examples=["test1234"])]


# ── モデル ────────────────────────────────────────────────
class ItemCreate(BaseModel):
    name: ItemName
    price: ItemPrice
    description: ItemDesc = None


class ItemUpdate(BaseModel):
    name: ItemNameOpt = None
    price: ItemPriceOpt = None
    description: ItemDesc = None
    status: ItemStatusOpt = None


class ItemResponse(BaseModel):
    id: ItemId
    name: ItemName
    price: ItemPrice
    description: ItemDesc = None
    status: Annotated[ItemStatus, Field(examples=[ItemStatus.ON_SALE])]
    created_at: datetime
    updated_at: datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: Username
    password: Password


class UserResponse(BaseModel):
    id: UserId
    username: Username
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class DecodedToken(BaseModel):
    username: str
    user_id: int

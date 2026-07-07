from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ItemStatus(Enum):
    ON_SALE = "ON_SALE"
    SOLD_OUT = "SOLD_OUT"


ItemId = Annotated[
    int,
    Field(
        gt=0,
        examples=[1]
    )
]

ItemName = Annotated[
    str,
    Field(
        min_length=2,
        max_length=50,
        examples=["PC"]
    )
]

ItemPrice = Annotated[
    int,
    Field(
        gt=0,
        examples=[10000]
    )
]

ItemOptionalDescription = Annotated[
    str | None,
    Field(
        max_length=255,
        examples=["美品です"]
    )
]

ItemOptionalName = Annotated[
    str | None,
    Field(
        min_length=2,
        max_length=50,
        examples=["PC"]
    )
]

ItemOptionalPrice = Annotated[
    int | None,
    Field(
        gt=0,
        examples=[10000]
    )
]

ItemOptionalStatus = Annotated[
    ItemStatus | None,
    Field(
        examples=[ItemStatus.SOLD_OUT]
    )
]


UserId = Annotated[
    int,
    Field(
        gt=0,
        examples=[1]
    )
]

Username = Annotated[
    str,
    Field(
        min_length=2,
        max_length=50,
        examples=["user1"]
    )
]

Password = Annotated[
    str,
    Field(
        min_length=8,
        max_length=255,
        examples=["test1234"]
    )
]


class ItemBase(BaseModel):
    name: ItemName
    price: ItemPrice
    description: ItemOptionalDescription = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: ItemOptionalName = None
    price: ItemOptionalPrice = None
    description: ItemOptionalDescription = None
    status: ItemOptionalStatus = None


class ItemResponse(ItemBase):
    id: ItemId
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

from datetime import datetime
from typing import Annotated

from fastapi import Form, HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from enums import ItemStatusEnum

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
    ItemStatusEnum | None,
    Field(
        examples=[ItemStatusEnum.ON_SALE]
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


class StrippedBaseModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class ItemBase(StrippedBaseModel):
    name: ItemName
    price: ItemPrice
    description: ItemOptionalDescription = None


class ItemCreate(ItemBase):
    pass


def item_create_form(
    name: Annotated[str, Form()],
    price: Annotated[int, Form()],
    description: Annotated[str | None, Form()] = None,
) -> ItemCreate:
    try:
        return ItemCreate(name=name, price=price, description=description)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors(include_url=False))


class ItemUpdate(StrippedBaseModel):
    name: ItemOptionalName = None
    price: ItemOptionalPrice = None
    description: ItemOptionalDescription = None
    status: ItemOptionalStatus = None


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: int
    description: str | None
    status: ItemStatusEnum
    image_url: str | None
    created_at: datetime
    updated_at: datetime
    user_id: int


class UserCreate(StrippedBaseModel):
    username: Username
    password: Password


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime
    updated_at: datetime


class Token(StrippedBaseModel):
    access_token: str
    token_type: str


class DecodedToken(StrippedBaseModel):
    username: str
    user_id: int

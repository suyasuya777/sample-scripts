from typing import Annotated

from fastapi import (APIRouter, Depends, File, HTTPException, Path, Query,
                     UploadFile, status)
from sqlalchemy.ext.asyncio import AsyncSession

from cruds import auth as auth_cruds
from cruds import item as item_cruds
from database import get_db
from schemas import (DecodedToken, ItemCreate, ItemResponse, ItemUpdate,
                     item_create_form)
from storage import delete_item_image, save_item_image

DbDependency = Annotated[
    AsyncSession,
    Depends(get_db)
]

UserDependency = Annotated[
    DecodedToken,
    Depends(auth_cruds.get_current_user)
]


ItemId = Annotated[int, Path(gt=0)]
NameQuery = Annotated[str | None, Query(min_length=1, max_length=20)]

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("", response_model=list[ItemResponse])
async def get_items(
    db: DbDependency,
    name: NameQuery = None
):
    if name is None:
        return await item_cruds.get_items(db)
    return await item_cruds.get_items_by_name(db, name)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    db: DbDependency,
    user: UserDependency,
    item_id: ItemId
):
    item = await item_cruds.get_item(db, item_id, user.user_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    db: DbDependency,
    user: UserDependency,
    item_in: Annotated[ItemCreate, Depends(item_create_form)],
    file: Annotated[UploadFile | None, File()] = None,
):
    item = await item_cruds.create_item(db, item_in, user.user_id)

    image_url = None
    if file is not None:
        image_url = await save_item_image(file, item.id)
        item = await item_cruds.set_item_image(db, item, image_url)

    try:
        await db.commit()
    except Exception:
        if image_url:
            delete_item_image(image_url)
        raise
    return item


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    db: DbDependency,
    user: UserDependency,
    item_in: ItemUpdate,
    item_id: ItemId
):
    item = await item_cruds.update_item(db, item_id, item_in, user.user_id)

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not updated")

    await db.commit()
    return item


@router.post("/{item_id}/image", response_model=ItemResponse)
async def upload_item_image(
    db: DbDependency,
    user: UserDependency,
    item_id: ItemId,
    file: Annotated[UploadFile, File()],
):
    item = await item_cruds.get_item(db, item_id, user.user_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    old_url = item.image_url
    new_url = await save_item_image(file, item_id)
    item = await item_cruds.set_item_image(db, item, new_url)

    await db.commit()

    if old_url and old_url != new_url:
        delete_item_image(old_url)

    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    db: DbDependency,
    user: UserDependency,
    item_id: ItemId
):
    item = await item_cruds.delete_item(db, item_id, user.user_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not deleted")

    await db.commit()

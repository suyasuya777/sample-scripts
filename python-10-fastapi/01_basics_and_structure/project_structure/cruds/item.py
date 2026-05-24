from sqlalchemy.orm import Session
from models.item import Item
from schemas.item import ItemCreate


def get_items(db: Session) -> list[Item]:
    return db.query(Item).all()


def get_items_by_user(db: Session, user_id: int) -> list[Item]:
    return db.query(Item).filter(Item.user_id == user_id).all()


def create_item(db: Session, item_in: ItemCreate) -> Item:
    item = Item(**item_in.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

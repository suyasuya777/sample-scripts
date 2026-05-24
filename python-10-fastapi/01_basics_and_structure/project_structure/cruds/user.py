from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate


def get_users(db: Session) -> list[User]:
    return db.query(User).all()


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(**user_in.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

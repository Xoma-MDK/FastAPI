import models
from sqlalchemy.orm import Session
from schemas import UserCreate, UserOut, UserBase
from datetime import datetime
from services.AuthService import Auth
from fastapi import HTTPException

auth_handler = Auth()


def get_users(db: Session):
    users_db = db.query(models.User).all()
    users_out = []
    for user in users_db:
        user_out = UserOut(id=user.id, email=user.email,
                           name=user.name, surname=user.surname)
        users_out.append(user_out)
    return users_out


def get_user(db: Session, email: str):
    user_db = db.query(models.User).filter(
        models.User.email == email).first()
    if user_db != None:
        user_db.last_active_at = datetime.now()
        db.add(user_db)
        db.commit()
    return user_db


def get_user_by_id(db: Session, id: int):
    user_db = db.query(models.User).filter(models.User.id == id).first()
    if user_db != None:
        user_db.last_active_at = datetime.now()
        db.add(user_db)
        db.commit()
    return user_db


def post_user(db: Session, User: UserCreate):
    db_user = models.User(
        name=User.name,
        surname=User.surname,
        email=User.email,
        password_hash=auth_handler.encode_password(User.password)
    )
    db.add(db_user)
    db.commit()
    return db_user


def update_user(db: Session, user: models.User, new_user: UserBase):
    user_db: models.User | None = db.query(models.User).filter(
        models.User.email == new_user.email).first()
    if (user_db != None) and (user_db.id != user.id):
        raise HTTPException(status_code=409, detail='Username busy')
    user_db = db.query(models.User).get(user.id)
    user_db.email = new_user.email
    user_db.name = new_user.name
    user_db.surname = new_user.surname
    user_db.last_active_at = datetime.now()
    db.add(user_db)
    db.commit()
    return user_db

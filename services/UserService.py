import models
from sqlalchemy.orm import Session
from schemas import UserCreate, UserOut
from datetime import datetime
from services.AuthService import Auth
from fastapi import HTTPException

auth_handler = Auth()


def get_users(db: Session):
    users_db = db.query(models.User).all()
    users_out = []
    for user in users_db:
        user_out = UserOut(id=user.id, username=user.username)
        users_out.append(user_out)
    return users_out


def get_user(db: Session, username: str):
    user_db = db.query(models.User).filter(
        models.User.username == username).first()
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
        username=User.username,
        password_hash=auth_handler.encode_password(User.password)
    )
    db.add(db_user)
    db.commit()
    return db_user


def update_user_name(db: Session, user: models.User, username):
    user_db = db.query(models.User).get(user.id)
    if db.query(models.User).filter(models.User.username == username).first() != None:
        raise HTTPException(status_code=409, detail='Username busy')
    user_db.username = username
    user_db.last_active_at = datetime.now()
    db.add(user_db)
    db.commit()
    return user_db

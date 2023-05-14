import models
from sqlalchemy.orm import Session
from typing import List
from schemas import UserCreate, UserOut
from fastapi import HTTPException
import os
from datetime import datetime
from auth import Auth



auth_handler = Auth()


def getUsers(db: Session):
    users_db = db.query(models.User).all()
    users_out = []
    for user in users_db:
        user_out = UserOut(id = user.id, username = user.username)
        users_out.append(user_out)
    return users_out


def getUser(db: Session, username: str):
    user_db = db.query(models.User).filter(models.User.username == username).first()
    if user_db != None:
        user_db.last_active_at = datetime.now()
        db.add(user_db)
        db.commit()
    return user_db



def postUser(db: Session, User: UserCreate):
    db_user = models.User(
        username = User.username,
        password_hash = auth_handler.encode_password(User.password) 
    )
    db.add(db_user)
    db.commit()
    return db_user


def updateUserRefreshToken(db: Session, user: models.User, refresh_token_hash):
    user_tokens = db.query(models.User).get(user.id)
    user_tokens.token = refresh_token_hash
    user_tokens.last_active_at = datetime.now()
    db.add(user_tokens)
    db.commit()



def updateUserName(db: Session, user: models.User, username):
    user_db = db.query(models.User).get(user.id)
    if db.query(models.User).filter(models.User.username == username).first() != None:
        raise HTTPException(status_code=409, detail='Username busy') 
    user_db.username = username
    user_db.last_active_at = datetime.now()
    db.add(user_db)
    db.commit()
    return user_db


def newMessage(db: Session, data: dict):
    new_message = models.Message(
        sender_id = data['sender_id'],
        recipient_id = data['recipient_id'],
        group_id = data['group_id'],
        message_text = data['message_text']
    )
    db.add(new_message)
    db.commit()
    return(new_message)
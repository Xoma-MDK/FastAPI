import models
from sqlalchemy.orm import Session
from typing import List
from schemas import UserCreate, UserOut, Message
from fastapi import HTTPException
import os
from datetime import datetime
from auth import Auth

UPLOADED_FILES_PATH = "./uploaded_files/"

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



def getUserById(db: Session, id: int):
    user_db = db.query(models.User).filter(models.User.id == id).first()
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

def get_file_from_db(db: Session, user_id):
    return db.query(models.Avatars).filter(models.Avatars.user_id == user_id).first()


# Get file size
def get_file_size(filename, path : str = None):
    file_path = f'{UPLOADED_FILES_PATH}{filename}'
    if path:
        file_path = f'{path}{filename}'
    return os.path.getsize(file_path)


# Save file to uploads folder
async def save_file_to_uploads(file, filename):
    with open(f'{UPLOADED_FILES_PATH}{filename}', "wb") as uploaded_file:
        file_content = await file.read()
        uploaded_file.write(file_content)
        uploaded_file.close()

def delete_file_from_uploads(file_name):
    try:
        os.remove(UPLOADED_FILES_PATH + file_name)
    except Exception as e:
        print(e)


def add_file_to_db(db: Session, **kwargs):
    new_file = models.Avatars(
                                name=kwargs['name'],
                                user_id=kwargs['user_id'],
                                size=kwargs['file_size'],
                                mime_type=kwargs['file'].content_type,
                                edited_at=datetime.now()
                            )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

def update_file_in_db(db: Session, **kwargs):
    update_file = db.query(models.Avatars).filter(models.Avatars.user_id == kwargs['user_id']).first()
    update_file.name = kwargs['name']
    update_file.user_id = kwargs['user_id']
    update_file.size = kwargs['file_size']
    update_file.mime_type = kwargs['file'].content_type
    update_file.edited_at = datetime.now()

    db.commit()
    db.refresh(update_file)
    return update_file


def delete_file_from_db(db: Session, file_info_from_db):
    db.delete(file_info_from_db)
    db.commit()
    
    
def format_filename(file):
    filename, ext = os.path.splitext(file.filename)
    return filename + ext


async def get_messages(
    db: Session, 
    sender_user: models.User, 
    recipient_user: models.User = None,
    group_id: int = None,
    limit: int = 50
    ):
     messages = []
     if recipient_user != None:
        messages_id_db = db.query(models.Message).filter(
            models.Message.sender == sender_user,
            models.Message.recipient == recipient_user
         ).order_by(models.Message.created_at.asc()).limit(limit).all()
        if messages_id_db != []:
            for message_in_db in messages_id_db:
                message = Message(
                    id = message_in_db.id,
                    sender_id = message_in_db.sender_id,
                    recipient_id = message_in_db.recipient_id,
                    message_text = message_in_db.message_text,
                    created_at = message_in_db.created_at
                )
                messages.append(message)
        messages_id_db = db.query(models.Message).filter(
            models.Message.sender == recipient_user,
            models.Message.recipient == sender_user
         ).order_by(models.Message.created_at.asc()).limit(limit).all()
        if messages_id_db != []:
            for message_in_db in messages_id_db:
                message = Message(
                    id = message_in_db.id,
                    sender_id = message_in_db.sender_id,
                    recipient_id = message_in_db.recipient_id,
                    message_text = message_in_db.message_text,
                    created_at = message_in_db.created_at
                )
                messages.append(message)
     if group_id != None:
        messages_id_db = db.query(models.Message).filter(
            models.Message.group_id == group_id
         ).order_by(models.Message.created_at.asc()).limit(limit).all()
        if messages_id_db != []:
            for message_in_db in messages_id_db:
                message = Message(
                    id = message_in_db.id,
                    sender_id = message_in_db.sender_id,
                    recipient_id = message_in_db.recipient_id,
                    message_text = message_in_db.message_text,
                    created_at = message_in_db.created_at
                )
                messages.append(message)
     return messages
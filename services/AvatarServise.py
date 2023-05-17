import models
from sqlalchemy.orm import Session
from sqlalchemy import or_
from settings import UPLOADED_FILES_PATH
import os
from datetime import datetime
from uuid import uuid4


def get_file_from_db(db: Session, user_id):
    return db.query(models.Avatars).filter(models.Avatars.user_id == user_id).first()


def get_file_size(filename, path: str = None):
    file_path = f'{UPLOADED_FILES_PATH}{filename}'
    if path:
        file_path = f'{path}{filename}'
    return os.path.getsize(file_path)


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
    update_file = db.query(models.Avatars).filter(
        models.Avatars.user_id == kwargs['user_id']).first()
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
    filename = uuid4()
    return filename + ext

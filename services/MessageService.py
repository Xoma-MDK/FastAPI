import models
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from schemas import MessageOut, MessageEncoder, Message, Dialog
import json


def new_message(db: Session, data: dict) -> models.Message:
    new_message_in_db = models.Message(
        sender_id=data['sender_id'],
        recipient_id=data['recipient_id'],
        group_id=data['group_id'],
        message_text=data['message_text']
    )
    db.add(new_message_in_db)
    db.commit()
    return new_message_in_db


def message_to_out_json(message: models.Message) -> str:
    message_out = MessageOut(
        id=message.id,
        sender_id=message.sender_id,
        recipient_id=message.recipient_id,
        group_id=message.group_id,
        message_text=message.message_text,
        created_at=message.created_at.isoformat(),
        readed=message.readed
    )
    return json.dumps(message_out, cls=MessageEncoder)


async def get_messages(
    db: Session,
    sender_user: models.User,
    recipient_user: models.User = None,
    group_id: int = None,
    limit: int = 50,
    offset: int = 0,
) -> List[models.Message]:
    messages = []
    if recipient_user != None:
        messages_id_db = db.query(models.Message).filter(
            or_(
                and_(models.Message.sender == sender_user,
                     models.Message.recipient == recipient_user),
                and_(models.Message.sender == recipient_user,
                     models.Message.recipient == sender_user)
            )
        ).order_by(models.Message.created_at.desc()).limit(limit).offset(offset).all()
        if messages_id_db != []:
            for message_in_db in messages_id_db:
                if message_in_db.recipient == sender_user:
                    message_in_db.readed = 1
                message = Message(
                    id=message_in_db.id,
                    sender_id=message_in_db.sender_id,
                    recipient_id=message_in_db.recipient_id,
                    message_text=message_in_db.message_text,
                    created_at=message_in_db.created_at
                )
                messages.append(message)
            db.add_all(messages_id_db)
            db.commit()
    if group_id != None:
        messages_id_db = db.query(models.Message).filter(
            models.Message.group_id == group_id
        ).order_by(models.Message.created_at.desc()).limit(limit).offset(offset).all()
        if messages_id_db != []:
            for message_in_db in messages_id_db:
                message = Message(
                    id=message_in_db.id,
                    sender_id=message_in_db.sender_id,
                    recipient_id=message_in_db.recipient_id,
                    message_text=message_in_db.message_text,
                    created_at=message_in_db.created_at
                )
                messages.append(message)
    return messages


def get_dialog(db: Session, sender: models.User, recipient: models.User) -> Dialog | None:
    message = db.query(models.Message).filter(
        or_(
            and_(models.Message.sender == sender,
                 models.Message.recipient == recipient),
            and_(models.Message.sender == recipient,
                 models.Message.recipient == sender)
        )
    ).order_by(
        models.Message.id.desc()
    ).first()
    if message == None:
        return None
    count_unread_messages = db.query(models.Message).filter(
        models.Message.sender == recipient,
        models.Message.recipient == sender,
        models.Message.readed == False
    ).count()
    return Dialog(
        recipient_id=recipient.id,
        last_message=message_to_out_json(message),
        count_unread_messages=count_unread_messages)


def get_dialogs(db: Session, sender: models.User) -> List[Dialog] | None:
    users = db.query(models.User).filter(models.User != sender).all()
    dialogs = []
    for user in users:
        dialog = get_dialog(db, sender, user)
        if dialog != None:
            dialogs.append(dialog)
    return dialogs

import models
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from schemas import MessageOut, MessageEncoder, Message
import json


def new_message(db: Session, data: dict):
    new_message_in_db = models.Message(
        sender_id=data['sender_id'],
        recipient_id=data['recipient_id'],
        group_id=data['group_id'],
        message_text=data['message_text']
    )
    db.add(new_message_in_db)
    db.commit()
    return (new_message_in_db)


def message_to_out_json(message: models.Message):
    message_out = MessageOut(
        id=message.id,
        sender_id=message.sender_id,
        recipient_id=message.recipient_id,
        group_id=message.group_id,
        message_text=message.message_text,
        created_at=message.created_at.isoformat()
    )
    return json.dumps(message_out, cls=MessageEncoder)


async def get_messages(
    db: Session,
    sender_user: models.User,
    recipient_user: models.User = None,
    group_id: int = None,
    limit: int = 50,
    offset: int = 0,
):
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
                message = Message(
                    id=message_in_db.id,
                    sender_id=message_in_db.sender_id,
                    recipient_id=message_in_db.recipient_id,
                    message_text=message_in_db.message_text,
                    created_at=message_in_db.created_at
                )
                messages.append(message)
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

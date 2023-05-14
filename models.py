from sqlalchemy import Column, ForeignKey, String, TIMESTAMP, Text, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from database import Base, engine


class User(Base):
    __tablename__ = 'users'

    id = Column(INTEGER(11), primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    token = Column(String(255), nullable=True)
    last_active_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class ChatGroup(Base):
    __tablename__ = 'chat_groups'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(255), nullable=False)
    creator_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    creator = relationship('User')



class ChatGroupMember(Base):
    __tablename__ = 'chat_group_members'

    id = Column(INTEGER(11), primary_key=True)
    group_id = Column(ForeignKey('chat_groups.id'), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)

    group = relationship('ChatGroup')
    user = relationship('User')


class Message(Base):
    __tablename__ = 'messages'

    id = Column(INTEGER(11), primary_key=True)
    sender_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    recipient_id = Column(ForeignKey('users.id'), index=True)
    group_id = Column(ForeignKey('chat_groups.id'), index=True)
    message_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    group = relationship('ChatGroup')
    recipient = relationship('User', primaryjoin='Message.recipient_id == User.id')
    sender = relationship('User', primaryjoin='Message.sender_id == User.id')


class Attachment(Base):
    __tablename__ = 'attachments'

    id = Column(INTEGER(11), primary_key=True)
    message_id = Column(ForeignKey('messages.id'), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(255), nullable=False)

    message = relationship('Message')


class Avatars(Base):
    __tablename__ = 'avatars'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(length=150))
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    size = Column(INTEGER)
    mime_type = Column(String(length=150))
    edited_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class UnreadMessage(Base):
    __tablename__ = 'unread_messages'

    id = Column(INTEGER(11), primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    message_id = Column(ForeignKey('messages.id'), nullable=False, index=True)

    message = relationship('Message')
    user = relationship('User')

Base.metadata.create_all(engine)
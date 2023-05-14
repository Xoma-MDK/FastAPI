import json
from pydantic import BaseModel
from typing import Union
from datetime import datetime


class UserBase(BaseModel):
    username: str

    class Config:
        orm_mode = True


class UserLogin(UserBase):
    password: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str

    class Config:
        orm_mode = True


class Tokens(BaseModel):
    access_token: str
    refresh_token: str

    class Config:
        orm_mode = True


class UserOut(UserBase):
    id: int


class Message(BaseModel):
    id: int
    sender_id: int
    recipient_id: Union[int, None]
    group_id: Union[int, None]
    message_text: str
    created_at: datetime


class MessageOut(BaseModel):
    id: int
    sender_id: int
    recipient_id: Union[int, None]
    group_id: Union[int, None]
    message_text: str
    created_at: str


class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MessageOut):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

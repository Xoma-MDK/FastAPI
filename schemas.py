from pydantic import BaseModel
from typing import Union

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
    
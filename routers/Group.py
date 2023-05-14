from typing import Optional
from fastapi import APIRouter, Depends, Query, Security, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database import SessionLocal
import schemas
from service import *
from auth import Auth
import json
group_route = APIRouter()
security = HTTPBearer()


def get_db():  # Получает сессию для отправки запросов
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

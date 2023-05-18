from typing import Optional
from fastapi import APIRouter, Depends, Query, Security, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database import SessionLocal
from sqlalchemy.orm import Session
import schemas
from services.AuthService import Auth
from services.MessageService import get_messages, new_message, message_to_out_json
from services.UserService import get_user, get_user_by_id
import json

messages_route = APIRouter()
security = HTTPBearer()
auth_handler = Auth()


def get_db():  # Получает сессию для отправки запросов
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@messages_route.get('/get', tags=["Message"], response_model=list[schemas.Message])
async def message_get(
        recipient_id: Optional[int] = Query(None),
        group_id: Optional[int] = Query(None),
        limit: Optional[int] = Query(50),
        offset: Optional[int] = Query(0),
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: Session = Depends(get_db)):

    if (auth_handler.decode_token(credentials.credentials)):
        token = credentials.credentials
        sender = get_user(db, auth_handler.decode_token(token))
        recipient = get_user_by_id(db, recipient_id)

        if (recipient_id != None and group_id != None) or (recipient_id == None and group_id == None):
            raise HTTPException(400)

        if recipient_id != None:
            messages = await get_messages(db, sender, recipient, None, limit, offset)
            return messages

        if group_id != None:
            messages = await get_messages(db, sender, None, group_id, limit, offset)
            return messages

    else:
        auth_handler.decode_token(credentials.credentials)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int:WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id):
        if user_id in list(self.active_connections.keys()):
            await websocket.accept()
            await websocket.close(code=4000)
            return False

        await websocket.accept()
        self.active_connections[user_id] = websocket

        return True

    def disconnect(self, websocket: WebSocket):
        del self.active_connections[list(filter(
            lambda x: self.active_connections[x] == websocket, self.active_connections))[0]]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_user_message(self, message: str, user_id: int):
        websocket = self.active_connections[user_id]
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for user_id, connection in self.active_connections.items():
            await connection.send_text(message)


manager = ConnectionManager()

keys = [
    "sender_id",
    "recipient_id",
    "group_id",
    "message_text"
]


@messages_route.websocket("/ws/{user_id}")
async def websocket(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    if await manager.connect(websocket, int(user_id)) == False:
        return

    try:
        while True:
            data: dict = json.loads(await websocket.receive_text())

            if keys == list(data.keys()):
                message = new_message(db, data)

            await manager.broadcast(f"{message_to_out_json(message)}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)

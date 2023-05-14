from typing import Optional
from fastapi import APIRouter, Depends, Query, Security, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database import SessionLocal
import schemas
from service import *
from auth import Auth
import json
messages_route = APIRouter()
security = HTTPBearer()


def get_db(): #Получает сессию для отправки запросов
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@messages_route.get('/get', tags=["Message"])
async def message_get(recipient_id: Optional[int] = Query(None), group_id: Optional[int] = Query(None), limit: Optional[int] = Query(50), credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    if(auth_handler.decode_token(credentials.credentials)):
        token = credentials.credentials
        sender = getUser(db, auth_handler.decode_token(token))
        recipient = getUserById(db, recipient_id)
        if (recipient_id != None and group_id != None) or (recipient_id == None and group_id == None):
            raise HTTPException(400)
        if recipient_id != None:
            messages = await get_messages(db, sender, recipient, None, limit)
            return messages
        if group_id != None:
            messages = await get_messages(db, sender, None, group_id, limit)
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
        del self.active_connections[list(filter(lambda x: self.active_connections[x] == websocket, self.active_connections))[0]]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        
        
        
    async def send_user_message(self, message: str, user_id: int):
        websocket = self.active_connections[user_id]
        await websocket.send_text(message)
        
        
        
    async def broadcast(self, message: str):
        for user_id, connection  in self.active_connections.items():
            await connection.send_text(message)



manager = ConnectionManager()

keys = [
    "sender_id",
    "recipient_id",
    "group_id",
    "message_text"
]

@messages_route.websocket("/ws/{user_id}")
async def websocket(websocket: WebSocket, user_id, db: Session = Depends(get_db)):
    if await manager.connect(websocket, int(user_id)) == False:
        return
    try:
        while True:
            data: dict = json.loads(await websocket.receive_text())
            if keys == list(data.keys()):
                newMessage(db, data)
            await manager.send_personal_message(f"{data}", websocket)
            await manager.broadcast(f"{data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
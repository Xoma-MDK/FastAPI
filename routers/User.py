from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database import SessionLocal
import schemas
from service import *
from auth import Auth
user_route = APIRouter()
security = HTTPBearer()



def get_db(): #Получает сессию для отправки запросов
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@user_route.get('/', tags=["User"], response_model = list[schemas.UserOut])
def users(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    if(auth_handler.decode_token(credentials.credentials)):
        return getUsers(db)
    else:
        auth_handler.decode_token(credentials.credentials)


@user_route.get('/me', tags=["User"], response_model = schemas.UserOut)
def me(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    if(auth_handler.decode_token(credentials.credentials)):
        user = getUser(db, auth_handler.decode_token(credentials.credentials))
        return schemas.UserOut(id = user.id, username = user.username)
    else:
        auth_handler.decode_token(credentials.credentials)
        


@user_route.post('/edit', tags=["User"], response_model = schemas.UserOut)
def me_edit(new_user: schemas.UserBase, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    if(auth_handler.decode_token(credentials.credentials)):
        token = credentials.credentials
        user = getUser(db, auth_handler.decode_token(token))
        if user != None:
            user = updateUserName(db, user, new_user.username)
            return schemas.UserOut(id = user.id, username = user.username)
        else: 
            raise HTTPException(404, "User not found")
    else:
        auth_handler.decode_token(credentials.credentials)
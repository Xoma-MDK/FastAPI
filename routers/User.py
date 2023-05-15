from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database import SessionLocal
from sqlalchemy.orm import Session
import schemas
from services.AuthService import Auth, update_user_refresh_token
from services.UserService import get_user, get_user_by_id, get_users, update_user_name
auth_handler = Auth()
user_route = APIRouter()
security = HTTPBearer()


def get_db():  # Получает сессию для отправки запросов
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@user_route.get('/all', tags=["User"], response_model=list[schemas.UserOut])
def users(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    if (auth_handler.decode_token(credentials.credentials)):
        return get_users(db)
    else:
        auth_handler.decode_token(credentials.credentials)


@user_route.get('/get', tags=["User"], response_model=schemas.UserOut)
def user(user_id: int, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    if (auth_handler.decode_token(credentials.credentials)):
        user = get_user_by_id(db, user_id)
        return schemas.UserOut(id=user.id, username=user.username)
    else:
        auth_handler.decode_token(credentials.credentials)


@user_route.get('/me', tags=["User"], response_model=schemas.UserOut)
def me(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    if (auth_handler.decode_token(credentials.credentials)):
        user = get_user(db, auth_handler.decode_token(credentials.credentials))
        return schemas.UserOut(id=user.id, username=user.username)
    else:
        auth_handler.decode_token(credentials.credentials)


@user_route.post('/edit', tags=["User"], response_model=schemas.UserOut)
def me_edit(new_user: schemas.UserBase, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    if (auth_handler.decode_token(credentials.credentials)):
        token = credentials.credentials
        user = get_user(db, auth_handler.decode_token(token))
        if user != None:
            user = update_user_name(db, user, new_user.username)
            new_token = auth_handler.encode_token(user.username)
            refresh_token = auth_handler.encode_refresh_token(user.username)
            update_user_refresh_token(
                db, user, auth_handler.get_token_hash(refresh_token))
            return schemas.Tokens(access_token=new_token, refresh_token=refresh_token)
        else:
            raise HTTPException(404, "User not found")
    else:
        auth_handler.decode_token(credentials.credentials)

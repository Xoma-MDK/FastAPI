from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database import SessionLocal
import schemas
from service import *
from auth import Auth
auth_route = APIRouter()
security = HTTPBearer()



def get_db(): #Получает сессию для отправки запросов
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@auth_route.post('/signup', tags=["Auth"])
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if getUser(db, user.username) != None:
         raise HTTPException(status_code=409, detail='Account already exists') 
    
    user = postUser(db, user)
    access_token = auth_handler.encode_token(user.username)
    refresh_token = auth_handler.encode_refresh_token(user.username)
    updateUserRefreshToken(db, user, auth_handler.get_token_hash(refresh_token))
    
    return schemas.Tokens(access_token = access_token, refresh_token = refresh_token)



@auth_route.post('/login', tags=["Auth"], response_model = schemas.Tokens)
def login(user_details: schemas.UserLogin, db: Session = Depends(get_db)):
    user = getUser(db, user_details.username)
    
    if (user is None):
        raise HTTPException(status_code=401, detail='Invalid username')
    
    if (not auth_handler.verify_password(user_details.password, user.password_hash)):
        raise HTTPException(status_code=401, detail='Invalid password')
    
    access_token = auth_handler.encode_token(user.username)
    refresh_token = auth_handler.encode_refresh_token(user.username)
    updateUserRefreshToken(db, user, auth_handler.get_token_hash(refresh_token))
    
    return schemas.Tokens(access_token = access_token, refresh_token = refresh_token)



@auth_route.post('/refresh', tags=["Auth"])
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    refresh_token = credentials.credentials
    user = getUser(db, auth_handler.decode_refresh_token(refresh_token))
    
    if(not auth_handler.verify_Tokens(refresh_token, user.token)):
        updateUserRefreshToken(db, user, None)
        raise HTTPException(status_code=401, detail = 'Invalid refresh token')
    
    new_token = auth_handler.refresh_token(refresh_token)
    refresh_token = auth_handler.encode_refresh_token(user.Login)
    updateUserRefreshToken(db, user, auth_handler.get_token_hash(refresh_token))
    
    return schemas.Tokens(access_token = new_token, refresh_token = refresh_token)



@auth_route.post('/logout', tags=["Auth"])
def logout(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    
    if(auth_handler.decode_token(token)):
        user = getUser(db, auth_handler.decode_token(token))
        updateUserRefreshToken(db, user, None)
    else:
        auth_handler.decode_token(token)



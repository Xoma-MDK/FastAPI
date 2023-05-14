from fastapi import APIRouter, Depends, Security, Response, status, Query, File, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database import SessionLocal
from fastapi.responses import FileResponse
import schemas
from service import *
from auth import Auth
from typing import Optional, List
user_route = APIRouter()
security = HTTPBearer()


def get_db():  # Получает сессию для отправки запросов
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@user_route.get("/avatar/download", tags=["User"], status_code=status.HTTP_200_OK)
async def download_file(response: Response, user_id: int, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Security(security)):
    if (auth_handler.decode_token(credentials.credentials)):
        file_info_from_db = get_file_from_db(db, user_id)
        if file_info_from_db:
            try:
                if os.path.exists(UPLOADED_FILES_PATH + file_info_from_db.name):
                    file_resp = FileResponse(UPLOADED_FILES_PATH + file_info_from_db.name,
                                             media_type=file_info_from_db.mime_type,
                                             filename=file_info_from_db.name)
                    response.status_code = status.HTTP_200_OK
                    return file_resp
            except FileNotFoundError:
                raise HTTPException(404)
            except RuntimeError:
                raise HTTPException(404)
            except:
                raise HTTPException(404)
        else:
            raise HTTPException(404)
    else:
        auth_handler.decode_token(credentials.credentials)


@user_route.post("/avatar/upload", tags=["User"], status_code=status.HTTP_200_OK)
async def upload_file(response: Response, file: UploadFile = File(...), db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Security(security)):
    if (auth_handler.decode_token(credentials.credentials)):
        user = get_user(db, auth_handler.decode_token(credentials.credentials))
        name = format_filename(file)
        if not file.content_type.startswith("image"):
            raise HTTPException(406, "File is not as image")
        print(454)
        await save_file_to_uploads(file, name)
        print(564)
        file_size = get_file_size(name)
        file_info_from_db = get_file_from_db(db, user.id)
        if not file_info_from_db:
            response.status_code = status.HTTP_201_CREATED
            return add_file_to_db(db, name=name, user_id=user.id, file_size=file_size, file=file)
        if file_info_from_db:
            delete_file_from_uploads(file_info_from_db.name)
            response.status_code = status.HTTP_201_CREATED
            return update_file_in_db(db, name=name, user_id=user.id, file_size=file_size, file=file)
    else:
        auth_handler.decode_token(credentials.credentials)


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
            return schemas.UserOut(id=user.id, username=user.username)
        else:
            raise HTTPException(404, "User not found")
    else:
        auth_handler.decode_token(credentials.credentials)

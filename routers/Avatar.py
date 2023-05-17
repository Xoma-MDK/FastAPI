from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Security, Response, status, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database import SessionLocal
from services.AuthService import Auth
from services.AvatarServise import get_file_from_db, get_file_size, format_filename, add_file_to_db, save_file_to_uploads, delete_file_from_uploads, update_file_in_db
from services.UserService import get_user
import os
from settings import UPLOADED_FILES_PATH


avatar_route = APIRouter()
security = HTTPBearer()
auth_handler = Auth()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@avatar_route.get("/download", tags=["Avatar"], status_code=status.HTTP_200_OK)
async def download_file(
        response: Response,
        user_id: int,
        db: Session = Depends(get_db),
        credentials: HTTPAuthorizationCredentials = Security(security)):

    if (auth_handler.decode_token(credentials.credentials)):
        file_info_from_db = get_file_from_db(db, user_id)

        if file_info_from_db:

            if os.path.exists(UPLOADED_FILES_PATH + file_info_from_db.name):
                file_resp = FileResponse(UPLOADED_FILES_PATH + file_info_from_db.name,
                                         media_type=file_info_from_db.mime_type,
                                         filename=file_info_from_db.name)
                return file_resp
        else:
            raise HTTPException(404)
    else:
        auth_handler.decode_token(credentials.credentials)


@avatar_route.post("/upload", tags=["Avatar"], status_code=status.HTTP_200_OK)
async def upload_file(
        response: Response,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        credentials: HTTPAuthorizationCredentials = Security(security)):

    if (auth_handler.decode_token(credentials.credentials)):
        user = get_user(db, auth_handler.decode_token(credentials.credentials))
        name = format_filename(file)

        if not file.content_type.startswith("image"):
            raise HTTPException(406, "File is not as image")

        await save_file_to_uploads(file, name)
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

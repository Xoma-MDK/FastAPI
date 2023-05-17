import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta
import models
from sqlalchemy.orm import Session
from settings import secret


class Auth():
    hasher_bcrypt = CryptContext(schemes=['bcrypt'])
    hasher_sha256 = CryptContext(schemes=["sha256_crypt"])
    secret = secret

    def encode_password(self, password):
        return self.hasher_sha256.hash(password)

    def get_token_hash(self, token):
        return self.hasher_bcrypt.hash(token)

    def verify_Tokens(self, token, encoded_token):
        return self.hasher_bcrypt.verify(token, encoded_token)

    def verify_password(self, password, encoded_password):
        return self.hasher_sha256.verify(password, encoded_password)

    def encode_token(self, username):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=1),
            'iat': datetime.utcnow(),
            'scope': 'access_token',
            'sub': username
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])

            if (payload['scope'] == 'access_token'):
                return payload['sub']
            raise HTTPException(
                status_code=401, detail='Scope for the token is invalid')

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')

        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    def decode_refresh_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])

            if (payload['scope'] == 'refresh_token'):
                return payload['sub']
            raise HTTPException(
                status_code=401, detail='Scope for the token is invalid')

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')

        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    def encode_refresh_token(self, username):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=14, hours=0),
            'iat': datetime.utcnow(),
            'scope': 'refresh_token',
            'sub': username
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(
                refresh_token, self.secret, algorithms=['HS256'])

            if (payload['scope'] == 'refresh_token'):
                username = payload['sub']
                new_token = self.encode_token(username)
                return new_token
            raise HTTPException(
                status_code=401, detail='Invalid scope for token')

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401, detail='Refresh token expired')

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401, detail='Invalid refresh token')


def update_user_refresh_token(db: Session, user: models.User, refresh_token_hash):
    user_tokens = db.query(models.User).get(user.id)
    user_tokens.token = refresh_token_hash
    user_tokens.last_active_at = datetime.now()

    db.add(user_tokens)
    db.commit()

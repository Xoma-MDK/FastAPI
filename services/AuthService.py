import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta
import models
from sqlalchemy.orm import Session


class Auth():
    hasher_bcrypt = CryptContext(schemes=['bcrypt'])
    hasher_sha256 = CryptContext(schemes=["sha256_crypt"])
    secret = "sKsu68ZWu1Sb1-aPCM-SHYHQ=rm!De3lGZNbd6SJaoe6g3mGVipWXw6PeKUKbIoXRyMr4TfsA7qLkp4kBEU42Tq?9Kponxl-N7Z?KVc!09s!e5DDnxHDpWsL8d=y-0Qdz7cBuzdbLXTDwpWw7/6!yhzL3vp5JaRiuzfl9k7QaOWey?qpD2TvuCK-nuMxWEY-KiT9uNKpVBkG/pztQjjCqbkWE8BSJMXC4sowQJ6BQnyz-vxLjJtTigTU1lNwA2kUjpfPkL144D?7kFd9nzmo0IWcR2T7soiWCAixQGU05WbwX8?VQ6Owj20f5orb2vyuj9OZEH5t3RO!sa?IkihkxY3ewYykleC/NKhVowXTNCFQ0IKV=rQbBqcGctNpQHrbKux9?cr9MtmJDV41Cj9mpZfRhjuU!okuyY5nk?/lApuU1M9Jym6SeTDB0ycvnUmx?Q=7?Xm!ZiBpGSTJA-AK!snjcvAQd0=/VoPxswU!-ymHcALXy1e3kcECOzPPHISUAWpUptTGB!?vKbnQeJDVfIsnE!zjNRvHxGidYtttgHKHKVv3n8zOYIdAACXwEuYFnv?985klS1rD-st1j=XwlBL72QgrPzHOM6cUTSHcklLUCc4NJsEe4JQkJMfQ0N/K7=gypj2gKp0qs6nV5dwgIGcLesfqtANUZ20SA/AjDa88RLWBIIisW9tWefvGm5bAyDI8?=KhLBZTzV0pEepLdzesgfZKnjC4mvkC7WGgK2O8iMsZcY?6aKQbPOJxvM1Ys3do8!nQqg8s3KCA?nr7/CM?hRPeXw76k52nrF0kCx6KwuDHTgj!uzOqL8h8m!tZatIM9FGsqNdL9=q9PCLPuUv7ry-HgoLE9bN5!sFrOkmceJ5G1sXe9=-4GpIThWkN=cvk2oV3V0EOxp1MUrshUm8IuEzjj00hTcEsLAO!9oPk2oDdU!Uda4GR25wP--HPMo6bL!6N7UAg5ZO?X!YhjRJi4ITsegOOMArjKtvYcDMSGeSuLhYYp!1AGDpI72TnudV9dT3nFZdQw/SFQp?-JpaxlDjVB7DpN3VCKwyt!mDCkHpHIBPz3iArsXPG4ZE45ndLwZXVu0pSmILCZ3a/fbIv3vZcmxxN!Tft4?-zD4DuM4IjZCtaERNDhkOhN-7Y8x6G5u96MXlic?c/SdCET6mQx8rL5Zm54hwQ51Ee/DZ37cWCz9IVVZS2y6NgetZyoFIOB5HTPgHL!66=hPIseJdJMUzBLFw02nCZLqvJGEgRLdoZl994GQfr6!QcIaGTH/Sf/0YNurxuvQc??uwMyf?0nBT62IIB8jjIQLGj/0N0BkeOKOiCJK!J4QKi-RTe36c1=-P?oU3USMxcAXARGUlOQ-Ae3XDpz284VeFj-xA23zj5SQ9hauJZFBkR-MfgcnRQUy=xZ/JdenpMDGnJyWosF46dZ1hhCAJYdb/LsZPn0K3-fCj5nrY/21NsLaqDuyFP4ai?KjyaLp5BMNxfXL?YHxyxhz3iVXgWQK=EWy5Q0fun36oWXDe4eZKVoJWDw7=y-RspqljFhqDolOfyMk2PfreTd7fHJA8q4jHRq/04GhIckz/fJt!pZZiPsLfMfhzKAo9xO3qK5Nk?-gQYTRmGgiFXG-BVsHg4o9Lb!-L8B7rY=T24E-T7=J9OCanSU5?uRCl2Ooyb2tTVZJnwZY4A?C7wNCqsQt=V/tn9D0ke1TfS5Uwk3t7Br2=dHfQE1-8/!MxA7?JXprDuIJ!uUPV36PfNrMMdBuj/3trOWNbFC!tTEHH7Ax-nazzlkBt5AGQOPJP=Y4tNP/1HusqEZqcqptIc7mxZ5g5TBLs4NtMbpYSlbNN5GJlN/I6tl9OtZ=SbeU43hK0VcbB4OWGpq8zgNmeYdWPvz6qA?UWFIBHPXo/Qe2dhXhwojKA=cUF!/6UTNOBxo28cGPDOc33J93dy94kJCRC=hQb9SJn2snzY!p9Twtklh?8Q=YQ2F!pHpOg-aR625F-w1gPOXwTwjMBWOkPKjB7pEDi05NqtmCmB-NnZqS?mTN1fgYnG0IBX"

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
            'exp': datetime.utcnow() + timedelta(days=0, minutes=15),
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

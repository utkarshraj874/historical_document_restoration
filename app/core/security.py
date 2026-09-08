from passlib.context import CryptContext
# importing a class from passlib libray 
# cryptcontext knows  how to hash password , how to verify passwords
from jose import jwt
from datetime import datetime
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import ExpiredSignatureError
from fastapi import HTTPException
from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)
pwd_context = CryptContext(
    schemes = ["argon2"],
    deprecated = "auto"
)
def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(
      plain_password:str,
      hashed_password:str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

def create_access_token(data:dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update(
        {"exp":expire}
    )

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

def verify_access_token(token:str):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload
    except ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="token has expired"
        )

    except  JWTError:

        raise HTTPException(
            status_code=401,
            detail = "invalid token"
        )
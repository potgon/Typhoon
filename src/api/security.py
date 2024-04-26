import os
from datetime import datetime, timedelta, timezone
from typing import Union, Any

from jose import jwt
from passlib.context import CryptContext

from utils.logger import make_log

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    make_log("OAUTH", 20, "api_workflow.log", "Creating access token")
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRES_MINUTES
        )
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)
    make_log("OAUTH", 20, "api_workflow.log", f"Encoded JWT: {encoded_jwt}")
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

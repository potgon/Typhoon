import os
from typing import Optional, Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from tortoise.exceptions import MultipleObjectsReturned, DoesNotExist

from database.models import User
from api.security import ALGORITHM, verify_password
from api.schemas import TokenData
from utils.logger import make_log

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="access_token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    make_log("OAUTH", 20, "api_workflow.log", "Getting current user")
    credential_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        make_log("OAUTH", 20, "api_workflow.log", f"Payload username: {username}")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    try:
        user = await User.get(username=token_data.username)
    except (MultipleObjectsReturned, DoesNotExist):
        raise HTTPException(
            status=401, detail="Unauthorized: User not found in the database"
        )
    if user is None:
        raise credential_exception

    make_log(
        "OAUTH", 20, "api_workflow.log", f"User id retrieved from token: {user.id}"
    )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    make_log("OAUTH", 20, "api_workflow.log", "Getting current active user")
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def authenticate_user(username: str, password: str) -> Optional[User]:
    db_user = await User.filter(username=username).first()
    if not db_user:
        return None
    if not verify_password(password, db_user.password):
        return None
    return db_user


CurrentUser = Annotated[User, Depends(get_current_user)]

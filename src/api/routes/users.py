from fastapi import APIRouter, HTTPException
from tortoise.exceptions import IntegrityError
from typing import Optional

from api.security import get_password_hash
from api.schemas import UserCreate
from database.models import User
from utils.logger import make_log

router = APIRouter()


@router.post("/")
async def create_user(user_data: UserCreate) -> Optional[UserCreate]:
    hashed_password = get_password_hash(user_data.password)
    try:
        user = await User(email=user_data.email, password=hashed_password).save()
        make_log(
            "USERS",
            20,
            "api_error.log",
            f"User: {user_data.email} successfully created",
        )
        return user
    except IntegrityError as e:
        make_log(
            "USERS", 40, "api_error.log", f"Integrity error creating user: {str(e)}"
        )
        raise HTTPException(status_code=400, detail="Email already registered")

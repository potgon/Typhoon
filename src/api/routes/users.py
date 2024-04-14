from fastapi import APIRouter, HTTPException
from tortoise.exceptions import IntegrityError
from typing import Optional

from api.security import get_password_hash
from api.schemas import UserCreate
from database.models import User

router = APIRouter()

@router.post("/users")
async def create_user(user_data: UserCreate) -> Optional[User]:
    hashed_password = get_password_hash(user_data.password)
    try:
        user = await User(email=user_data.email, password=hashed_password).save()
        return user
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
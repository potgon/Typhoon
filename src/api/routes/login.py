from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from database.models import User
from api.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRES_MINUTES
from api.schemas import Token

router = APIRouter()

@router.post("/login/access-token/", response_model=Token)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = await User.filter(email=form_data.username).first()
    if not user or verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect credentials")    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is not active")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    access_token = create_access_token(
        data = {"user_id": user.id}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from database.models import User
from api.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRES_MINUTES
from api.schemas import Token

router = APIRouter()

async def get_email_and_password(form_data: OAuth2PasswordRequestForm = Depends()) -> tuple:
    return form_data.email, form_data.password

@router.post("/login/access-token/", response_model=Token)
async def login_access_token(email: str = Form(...), password: str = Form(...)) -> Token:
    user = await User.filter(email=email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect credentials")    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is not active")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    
    access_token = create_access_token(
        subject = user.id, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
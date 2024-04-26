from typing import Annotated, Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from api.security import (
    create_access_token,
    ACCESS_TOKEN_EXPIRES_MINUTES,
    verify_password,
)
from api.schemas import Token
from api.deps import authenticate_user, get_current_active_user, CurrentUser
from utils.logger import make_log
from database.models import User

router = APIRouter()


@router.post("/login/access-token/", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    make_log("OAUTH", 20, "api_workflow.log", "Atempting log-in")
    user = await authenticate_user(
        username=form_data.username, password=form_data.password
    )
    make_log(
        "OAUTH",
        20,
        "api_workflow.log",
        f"Form data retrieved: {form_data.username} , {form_data.password}",
    )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/login/test-token")
async def test_token(current_user: CurrentUser) -> Any:
    return current_user


@router.post("/login", response_model=Dict)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = User.filter(email=form_data.username).first()
    except:
        raise HTTPException(status_code=401, detail="Invalid user credentials")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid user credentials")

    return {"access_token": create_access_token(user.email)}

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.testing.config import db_url

from app.auth.schema import (Token, LoginInfoSchema, LoginInfoRead, UserRead, LoginInfoListResponse, ActionLogRead,
                             ActionLogListResponse)
from app.auth.util import (authenticate_user, create_access_token, oauth2_scheme, blacklist_token, log_login_info,
                           get_login_info, read_me, UserDep, AdminDep, get_logging)
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.get_db import SessionDep

router = APIRouter()


@router.post("/login")
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: SessionDep,
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    login_info = LoginInfoSchema(user_id=user.id, email=user.email, phone=user.phone, username=user.username)
    await log_login_info(db, login_info)
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value,
            "phone": user.phone,
            "email": user.email,
        },
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout")
async def logout(current_user: UserDep, token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    await blacklist_token(token, db)
    return {"msg": "Successfully logged out"}


@router.get("/me/", response_model=UserRead)
async def read_user_me(current_user: UserDep, db: SessionDep):
    user = await read_me(db, current_user)
    return UserRead.model_validate(user)


@router.get("/login_info/", response_model=LoginInfoListResponse)
async def get_login_info_endpoint(current_user: AdminDep, db: SessionDep, limit: int = 10, page: int = 1):
    db_login_info, total_count = await get_login_info(db, limit, page)
    items = [LoginInfoRead.model_validate(login_info) for login_info in db_login_info]
    return LoginInfoListResponse(items=items, total_count=total_count)


@router.get('/logging', response_model=ActionLogListResponse)
async def logging_endpoint(current_user: AdminDep, db: SessionDep, limit: int = 10, page: int = 1):
    db_logging, total_count = await get_logging(db, limit, page)
    items = [ActionLogRead.model_validate(log) for log in db_logging]
    return ActionLogListResponse(items=items, total_count=total_count)


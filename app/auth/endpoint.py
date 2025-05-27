from fastapi import APIRouter

from app.auth.model import UserRole
from app.db.get_db import SessionDep
from app.auth.schema import UserCreate, UserRead, UserUpdateUnique, UserUpdatePassword, UserUpdateName
from app.auth.util import (create_user, update_user_name, update_user_unique, update_user_password, get_user_by_id,
                           get_users, delete_user, UserDep, get_user_by_username, get_user_by_email, get_user_by_phone,
                           AdminDep)


router = APIRouter()


@router.post("/", response_model=UserRead)
async def register_user(user: UserCreate, current_user: AdminDep, db: SessionDep):
    return await create_user(db, user)


@router.get("/", response_model=list[UserRead])
async def get_users_endpoint(current_user: AdminDep, db: SessionDep, limit: int = 10, page: int = 1, role: UserRole = None):
    return await get_users(db, limit=limit, page=page, role=role if role else None)


@router.get('/id/{user_id}', response_model=UserRead)
async def get_user_by_id_endpoint(user_id: int, current_user: UserDep, db: SessionDep):
    return await get_user_by_id(db, user_id)


@router.get('/username/{username}', response_model=UserRead)
async def get_user_by_username_endpoint(username: str, current_user: AdminDep, db: SessionDep):
    return await get_user_by_username(db, username)


@router.get('/email/{user_email}', response_model=UserRead)
async def get_user_by_email_endpoint(email: str, current_user: AdminDep, db: SessionDep):
    return await get_user_by_email(db, email)


@router.get('/phone/{user_phone}', response_model=UserRead)
async def get_user_by_phone_endpoint(phone: str, current_user: AdminDep, db: SessionDep):
    return await get_user_by_phone(db, phone)


@router.put('/update_password/')
async def update_user_password_endpoint(user: UserUpdatePassword, current_user: UserDep, db: SessionDep):
    return await update_user_password(db, current_user['id'], user)


@router.put('/update_name/')
async def update_user_name_endpoint(user: UserUpdateName, current_user: UserDep, db: SessionDep):
    return await update_user_name(db, current_user['id'], user)


@router.put('/update_unique/', response_model=UserRead)
async def update_user_unique_endpoint(user: UserUpdateUnique, current_user: UserDep, db: SessionDep):
    return await update_user_unique(db, current_user['id'], user)


@router.delete('/{user_id}')
async def delete_user_endpoint(user_id: int, current_user: UserDep, db: SessionDep):
    return await delete_user(db, user_id)



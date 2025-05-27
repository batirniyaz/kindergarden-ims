from datetime import timedelta
from typing import Annotated
from sqlalchemy import func

from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.model import User, LoginInfo, TokenBlacklist
from app.auth.schema import TokenData, UserRead, UserCreate, UserUpdateUnique, UserUpdatePassword, UserUpdateName, \
    LoginInfoSchema
from app.config import SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.get_db import SessionDep
from app.config import now_tashkent
from app.models.action_log import ActionLog

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



async def blacklist_token(token: str, db: AsyncSession):
    try:
        token_blacklist = TokenBlacklist(jti=token)
        db.add(token_blacklist)
        await db.commit()
        await db.refresh(token_blacklist)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def is_token_blacklisted(token: str, db: AsyncSession) -> bool:
    try:
        res = await db.execute(select(TokenBlacklist).filter_by(jti=token))
        token_blacklist = res.scalars().first()
        if token_blacklist:
            return True
        return False
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


async def get_user_by_phone(db: AsyncSession, phone: str) -> UserRead:
    res = await db.execute(select(User).filter_by(phone=phone))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this phone number not found")
    return UserRead.model_validate(user)


async def get_user_by_username(db: AsyncSession, username: str) -> UserRead:
    res = await db.execute(select(User).filter_by(username=username))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this username not found")
    return UserRead.model_validate(user)


async def get_user_by_username_with_pass(db: AsyncSession, username: str) -> User:
    res = await db.execute(select(User).filter_by(username=username))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this username not found")
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> UserRead:
    res = await db.execute(select(User).filter_by(email=email))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email not found")
    return UserRead.model_validate(user)


async def get_user_by_id(db: AsyncSession, user_id: int) -> UserRead:
    res = await db.execute(select(User).filter_by(id=user_id))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserRead.model_validate(user)


async def get_user_by_id_with_pass(db: AsyncSession, user_id: int) -> User:
    res = await db.execute(select(User).filter_by(id=user_id))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username_with_pass(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = now_tashkent() + expires_delta
    else:
        expire = now_tashkent() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: SessionDep,
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    is_t_black = await is_token_blacklisted(token, db)
    if is_t_black:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        phone: str = payload.get("phone")
        email: str = payload.get("email")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user_by_username_with_pass(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return {"id": user_id, "username": username, "role": role, "phone": phone, "email": email}


UserDep = Annotated[dict, Depends(get_current_user)]


async def create_user(db: AsyncSession, user: UserCreate) -> UserRead:

    try:
        hashed_password = get_password_hash(user.password)

        user = User(
            hashed_password=hashed_password,
            phone=user.phone,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            role=user.role,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UserRead.model_validate(user)
    except IntegrityError as e:
        await db.rollback()
        if "unique constraint" in str(e.orig):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username, phone or email already exists")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_users(db: AsyncSession, limit: int = 10, page: int = 1, role: str = None) -> list[UserRead]:
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    stmt = stmt.limit(limit).offset((page - 1) * limit)
    res = await db.execute(stmt)
    users = res.scalars().all()
    return [UserRead.model_validate(user) for user in users] or []


async def update_user_password(db: AsyncSession, user_id: int, user: UserUpdatePassword):
    user_db = await get_user_by_id_with_pass(db, user_id)
    if verify_password(user.password, user_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='New password cannot be the same as the old password')

    try:
        hashed_pass = get_password_hash(user.password)
        user_db.hashed_password = hashed_pass
        db.add(user_db)
        await db.commit()
        return {"detail": "Password updated successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def update_user_name(db: AsyncSession, user_id: int, user: UserUpdateName):
    user_db = await get_user_by_id_with_pass(db, user_id)
    try:
        for key, value in user.model_dump(exclude_unset=True).items():
            setattr(user_db, key, value)

        db.add(user_db)
        await db.commit()
        return {"detail": "User name updated successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def update_user_unique(db: AsyncSession, user_id: int, user: UserUpdateUnique) -> UserRead:
    for field, value in [("phone", user.phone), ("email", user.email), ("username", user.username)]:
        result = await db.execute(select(User).where(getattr(User, field) == value))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail=f"User with this {field} already exists")

    user_db = await get_user_by_id_with_pass(db, user_id)
    try:
        for key, value in user.model_dump(exclude_unset=True).items():
            setattr(user_db, key, value)

        db.add(user_db)
        await db.commit()
        return UserRead.model_validate(user_db)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user_by_id_with_pass(db, user_id)
    try:
        await db.delete(user)
        await db.commit()
        return {"detail": "User deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def read_me(db: AsyncSession, current_user) -> User:
    user = await get_user_by_id(db, current_user['id'])
    return user


async def log_login_info(db: AsyncSession, login: LoginInfoSchema):
    try:
        login_info = LoginInfo(**login.model_dump())
        db.add(login_info)
        await db.commit()
        await db.refresh(login_info)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_login_info(db: AsyncSession, limit: int = 10, page: int = 1) -> tuple[list[LoginInfo], int]:
    try:
        res = await db.execute(select(LoginInfo).limit(limit).offset((page - 1) * limit).order_by(LoginInfo.id.desc()))
        login_infos = res.scalars().all()

        total_count = await db.scalar(select(func.count(LoginInfo.id)))
        return login_infos or [], total_count
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_logging(db: AsyncSession, limit: int = 10, page: int = 1):
    try:
        res = await db.execute(select(ActionLog).limit(limit).offset((page - 1) * limit).order_by(ActionLog.id.desc()))
        login_infos = res.scalars().all()

        total_count = await db.scalar(select(func.count(ActionLog.id)))
        return login_infos or [], total_count
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def role_required(*allowed_roles: str):
    async def _role_checker(current_user: UserDep):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Requires role: {allowed_roles}"
            )
        return current_user
    return Depends(_role_checker)

AdminDep = Annotated[dict, role_required("admin")]
ManagerDep = Annotated[dict, role_required("manager", "admin")]
CookDep = Annotated[dict, role_required("cook", "admin")]

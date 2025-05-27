from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
import datetime

from app.auth.model import UserRole
from app.schemas.util import TashkentBaseModel


class Token(BaseModel):
    access_token: str = Field(..., description="The access token")
    token_type: str = Field(..., description="The token type")


class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="The username of the user")


class UserCreate(TashkentBaseModel):
    username: str = Field(..., max_length=25, min_length=3, description="The username of the user")
    phone: str = Field(..., max_length=13, min_length=13, description="The phone number of the user")
    email: EmailStr = Field(..., max_length=50, description="The email of the user")
    first_name: str = Field(..., max_length=25, description="The first name of the user")
    last_name: str = Field(..., max_length=25, description="The last name of the user")
    role: UserRole = Field(..., description="The role of the user")
    password: str = Field(..., max_length=255, description="The hashed password of the user")

    model_config = ConfigDict(extra='forbid')


class UserUpdateName(TashkentBaseModel):
    first_name: Optional[str] = Field(None, max_length=25, description="The first name of the user")
    last_name: Optional[str] = Field(None, max_length=25, description="The last name of the user")

    model_config = ConfigDict(extra='forbid')


class UserUpdateUnique(TashkentBaseModel):
    phone: Optional[str] = Field(None, max_length=13, min_length=13, description="The phone number of the user")
    email: Optional[EmailStr] = Field(None, max_length=50, description="The email of the user")
    username: Optional[str] = Field(None, max_length=25, description="The username of the user")

    model_config = ConfigDict(extra='forbid')


class UserUpdatePassword(TashkentBaseModel):
    password: str = Field(..., max_length=255, description="The password of the user")

    model_config = ConfigDict(extra='forbid')


class UserRead(TashkentBaseModel):
    id: int = Field(..., description="The ID of the user")
    username: str = Field(..., description="The username of the user")
    phone: str = Field(..., description="The phone number of the user")
    email: EmailStr = Field(..., description="The email of the user")
    first_name: str = Field(..., description="The first name of the user")
    last_name: str = Field(..., description="The last name of the user")
    role: UserRole = Field(..., description="The role of the user")
    created_at: datetime.datetime = Field(..., description="The time the user was created")
    updated_at: datetime.datetime = Field(..., description="The time the user was updated")

    model_config = ConfigDict(from_attributes=True)


class LoginInfoSchema(TashkentBaseModel):
    user_id: int = Field(..., description="The ID of the user")
    email: EmailStr = Field(..., max_length=50, description="The email of the user")
    phone: str = Field(..., max_length=13, description="The phone number of the user")
    username: str = Field(..., max_length=25, description="The username of the user")


class LoginInfoRead(LoginInfoSchema):
    id: int = Field(..., description="The ID of the login info")
    login_at: datetime.datetime = Field(..., description="The time the user logged in")

    model_config = ConfigDict(from_attributes=True)


class LoginInfoListResponse(BaseModel):
    total_count: int = Field(..., description="Total number of login info")
    items: list[LoginInfoRead] = Field(..., description="List of login info")

    model_config = ConfigDict(from_attributes=True)


class ActionLogRead(TashkentBaseModel):
    id: int = Field(..., description="The ID of the action log")
    user_id: int = Field(..., description="The ID of the user who performed the action")
    phone: str = Field(..., max_length=13, description="The phone number of the user")
    email: EmailStr = Field(..., max_length=50, description="The email of the user")
    username: str = Field(..., max_length=25, description="The username of the user")
    role: UserRole = Field(..., description="The role of the user")
    query: str = Field(..., description="The query string of the request")
    method: str = Field(..., description="The method of the request")
    path: str = Field(..., description="The path of the request")
    status_code: int = Field(..., description="The status code of the response")
    process_time: float = Field(..., description="The time taken to process the request in seconds")
    client_host: str = Field(..., description="The host of the client making the request")

    created_at: datetime.datetime = Field(..., description="The time the action log was created")
    updated_at: datetime.datetime = Field(..., description="The time the action log was updated")

    model_config = ConfigDict(from_attributes=True)


class ActionLogListResponse(BaseModel):
    total_count: int = Field(..., description="Total number of action logs")
    items: list[ActionLogRead] = Field(..., description="List of action logs")

    model_config = ConfigDict(from_attributes=True)

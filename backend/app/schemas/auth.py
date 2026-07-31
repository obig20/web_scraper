"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMBase


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=128)
    password: str = Field(min_length=8)
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(ORMBase):
    id: str
    email: str
    username: str
    full_name: str | None
    role: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

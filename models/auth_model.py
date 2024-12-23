from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str
    password: str


class UserCreate(UserBase):
    password: str
    email: str
    first_name: str
    last_name: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schema import PsychologistSchema, PsychologistInsertSchema


class UserSchema(BaseModel):
    id: int
    active: bool
    username: str
    email: str
    psychologist: Optional[PsychologistSchema] = None
    model_config = ConfigDict(from_attributes=True)


class UserInsertSchema(BaseModel):
    username: str
    password: str
    email: EmailStr
    psychologist: Optional[PsychologistInsertSchema] = None
    model_config = ConfigDict(from_attributes=True)


class ResendVerificationSchema(BaseModel):
    email: EmailStr


class VerifyEmailSchema(BaseModel):
    token: str


class UserUpdateSchema(BaseModel):
    active: Optional[bool] = None
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

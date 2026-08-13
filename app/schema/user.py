from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schema import PatientSchema


class UserSchema(BaseModel):
    id: int
    active: bool
    username: str
    password: str
    email: str
    psychologist: Optional[PatientSchema] = None
    model_config = ConfigDict(from_attributes=True)


class UserInsertSchema(BaseModel):
    active: bool
    username: str
    password: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    active: Optional[bool] = None
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

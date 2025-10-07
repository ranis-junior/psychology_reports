from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProgramsUploadSchema(BaseModel):
    id: int
    name: str
    filename: str
    path: str
    sequence: int
    generated: bool
    id_psychologist: int
    created_at: datetime
    updated_at: datetime
    cover: Optional[str] = None
    pdf: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProgramsUploadInsertSchema(BaseModel):
    name: str
    filename: str
    path: str
    sequence: int
    generated: bool
    id_psychologist: int

    model_config = ConfigDict(from_attributes=True)


class ProgramsUploadUpdateSchema(BaseModel):
    id: int
    name: Optional[str] = None
    filename: Optional[str] = None
    path: Optional[str] = None
    sequence: Optional[int] = None
    generated: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class ProgramsUploadGenerateSchema(BaseModel):
    id: int
    name: str
    sequence: int

    model_config = ConfigDict(from_attributes=True)

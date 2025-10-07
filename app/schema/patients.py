from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schema.pti import PtiSchema


class PatientSchema(BaseModel):
    id: int
    name: str
    birth_date: date
    gender: str
    id_psychologist: int
    father: Optional[str] = None
    father_profession: Optional[str] = None
    mother: Optional[str] = None
    mother_profession: Optional[str] = None
    photo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PatientListSchema(BaseModel):
    id: int
    name: str
    birth_date: date
    gender: str
    id_psychologist: int
    photo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PatientInsertSchema(BaseModel):
    name: str
    birth_date: date
    gender: str
    id_psychologist: int
    father: Optional[str] = None
    father_profession: Optional[str] = None
    mother: Optional[str] = None
    mother_profession: Optional[str] = None

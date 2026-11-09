from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PsychologistSchema(BaseModel):
    id: int
    name: str
    crp: str
    birth_date: date
    id_user: int
    model_config = ConfigDict(from_attributes=True)


class PsychologistInsertSchema(BaseModel):
    name: str
    crp: str
    birth_date: date
    id_user: Optional[int] = None

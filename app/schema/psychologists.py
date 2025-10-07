from datetime import date

from pydantic import BaseModel


class PsychologistSchema(BaseModel):
    id: int
    name: str
    crp: str
    birth_date: date


class PsychologistInsertSchema(BaseModel):
    name: str
    crp: str
    birth_date: date

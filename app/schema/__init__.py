from pydantic import BaseModel, ConfigDict


class Message(BaseModel):
    message: str

from .psychologists import PsychologistSchema, PsychologistInsertSchema
from .patients import PatientSchema
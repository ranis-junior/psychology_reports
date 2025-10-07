from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schema.pti_stimulus_areas import PtiStimulusAreasSchema, PtiStimulusAreasFullInsertSchema


class PtiSchema(BaseModel):
    id: int
    id_patient: int
    evaluation_date: datetime
    created_at: datetime
    updated_at: datetime
    pti_stimulus_areas: Optional[list[PtiStimulusAreasSchema]] = None

    model_config = ConfigDict(from_attributes=True)


class PtiInsertSchema(BaseModel):
    id_patient: int
    evaluation_date: datetime


class PtiFullInsertSchema(BaseModel):
    id_patient: int
    evaluation_date: datetime
    pti_stimulus_areas: list[PtiStimulusAreasFullInsertSchema]

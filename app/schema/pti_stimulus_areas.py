from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schema.pti_specific_objectives_topics import PtiSpecificObjectivesTopicsSchema, \
    PtiSpecificObjectivesTopicsFullInsertSchema


class PtiStimulusAreasSchema(BaseModel):
    id: int
    name: str
    id_pti: int
    created_at: datetime
    updated_at: datetime

    pti_specific_objectives_topics: Optional[list[PtiSpecificObjectivesTopicsSchema]] = None

    model_config = ConfigDict(from_attributes=True)


class PtiStimulusAreasInsertSchema(BaseModel):
    name: str
    id_pti: Optional[int] = None


class PtiStimulusAreasFullInsertSchema(BaseModel):
    name: str
    pti_specific_objectives_topics: list[PtiSpecificObjectivesTopicsFullInsertSchema]

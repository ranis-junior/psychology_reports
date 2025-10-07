from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schema.pti_specific_objectives_subtopics import PtiSpecificObjectivesSubTopicsSchema, \
    PtiSpecificObjectivesSubTopicsFullInsertSchema


class PtiSpecificObjectivesTopicsSchema(BaseModel):
    id: int
    name: Optional[str]
    id_pti_stimulus_area: int
    created_at: datetime
    updated_at: datetime

    pti_specific_objective_subtopic: Optional[list[PtiSpecificObjectivesSubTopicsSchema]] = None

    model_config = ConfigDict(from_attributes=True)


class PtiSpecificObjectivesTopicsInsertSchema(BaseModel):
    name: Optional[str]
    id_pti_stimulus_area: Optional[int] = None


class PtiSpecificObjectivesTopicsFullInsertSchema(BaseModel):
    name: Optional[str]
    pti_specific_objective_subtopic: list[PtiSpecificObjectivesSubTopicsFullInsertSchema]

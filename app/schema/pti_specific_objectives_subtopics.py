from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PtiSpecificObjectivesSubTopicsSchema(BaseModel):
    id: int
    name: Optional[str]
    id_pti_specific_objectives_topics: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PtiSpecificObjectivesSubTopicsInsertSchema(BaseModel):
    name: str
    id_pti_specific_objectives_topics: Optional[int] = None


class PtiSpecificObjectivesSubTopicsFullInsertSchema(BaseModel):
    name: str

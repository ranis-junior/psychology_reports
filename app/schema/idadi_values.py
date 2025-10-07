from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schema.idadi_domains import IdadiDomainsSchema


class IdadiValuesSchema(BaseModel):
    id: int
    raw_score: int
    standard_score: int
    created_at: datetime
    updated_at: datetime
    domain: IdadiDomainsSchema

    model_config = ConfigDict(from_attributes=True)


class IdadiValuesInsertSchema(BaseModel):
    raw_score: int
    standard_score: Optional[int] = None
    id_domain: int

    model_config = ConfigDict(from_attributes=True)


class IdadiValuesUpdateSchema(BaseModel):
    id: int
    raw_score: int
    standard_score: Optional[int] = None
    id_domain: int

    model_config = ConfigDict(from_attributes=True)

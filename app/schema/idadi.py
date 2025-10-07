from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schema.idadi_values import IdadiValuesSchema, IdadiValuesInsertSchema, IdadiValuesUpdateSchema


class IdadiSchema(BaseModel):
    id: int
    id_patient: int
    protocol_age: int
    application_date: datetime
    created_at: datetime
    updated_at: datetime

    values: list[IdadiValuesSchema]

    model_config = ConfigDict(from_attributes=True)


class IdadiInsertSchema(BaseModel):
    id_patient: int
    protocol_age: Optional[int] = None
    application_date: Optional[datetime] = None

    values: list[IdadiValuesInsertSchema]

    model_config = ConfigDict(from_attributes=True)


class IdadiUpdateSchema(BaseModel):
    id: int
    id_patient: int
    protocol_age: Optional[int] = None
    application_date: Optional[datetime] = None

    values: list[IdadiValuesUpdateSchema]

    model_config = ConfigDict(from_attributes=True)

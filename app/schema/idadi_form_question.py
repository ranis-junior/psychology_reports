from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schema.idadi_domains import IdadiDomainsSchema
from app.schema.idadi_form_question_patient import IdadiFormQuestionPatientSchema


class IdadiFormQuestionSchema(BaseModel):
    id: int
    code: str
    description: str
    initial_start_age_range: int
    final_start_age_range: int
    initial_end_age_range: int
    final_end_age_range: int
    domain: Optional[IdadiDomainsSchema] = None
    answer: Optional[IdadiFormQuestionPatientSchema] = None

    model_config = ConfigDict(from_attributes=True)

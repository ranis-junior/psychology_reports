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

    @classmethod
    def from_catalog(cls, question) -> 'IdadiFormQuestionSchema':
        return cls(
            id=question.id,
            code=question.code,
            description=question.description,
            initial_start_age_range=question.initial_start_age_range,
            final_start_age_range=question.final_start_age_range,
            initial_end_age_range=question.initial_end_age_range,
            final_end_age_range=question.final_end_age_range,
            domain=IdadiDomainsSchema.model_validate(question.domain) if question.domain else None,
        )

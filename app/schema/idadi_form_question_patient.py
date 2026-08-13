from pydantic import BaseModel, ConfigDict


class IdadiFormQuestionPatientSchema(BaseModel):
    id: int
    yes: bool
    no: bool
    maybe: bool
    id_idadi_form_question: int
    id_patient: int

    model_config = ConfigDict(from_attributes=True)


class IdadiFormQuestionPatientInsertSchema(BaseModel):
    yes: bool
    no: bool
    maybe: bool
    id_idadi_form_question: int
    id_patient: int

    model_config = ConfigDict(from_attributes=True)


class IdadiFormQuestionPatientUpdateSchema(BaseModel):
    yes: bool
    no: bool
    maybe: bool

    model_config = ConfigDict(from_attributes=True)

class IdadiFormQuestionPatientUpdateBatchSchema(BaseModel):
    id: int
    yes: bool
    no: bool
    maybe: bool

    model_config = ConfigDict(from_attributes=True)

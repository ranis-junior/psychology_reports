from pydantic import BaseModel, ConfigDict


class PatientRecordSchema(BaseModel):
    id: int
    demand_description: str
    instruments_used: str
    idadi_analysis: str
    anamnese_analysis: str
    anamnese_result: str
    conclusion: str

    id_patient: int

    model_config = ConfigDict(from_attributes=True)


class PatientRecordInsertSchema(BaseModel):
    demand_description: str
    instruments_used: str
    idadi_analysis: str
    anamnese_analysis: str
    anamnese_result: str
    conclusion: str

    id_patient: int

    model_config = ConfigDict(from_attributes=True)

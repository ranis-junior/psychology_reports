from http import HTTPStatus

from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import select, and_

from app.models import Patient
from app.models.patient_record import PatientRecord
from app.routers import Session
from app.schema import PatientSchema
from app.schema.patient_record import PatientRecordSchema, PatientRecordInsertSchema
from app.schema.patients import PatientInsertSchema, PatientListSchema
from app.service.minio import upload_image_to_minio, get_file_url_from_minio

router = APIRouter(prefix="/patient_records", tags=["record"], redirect_slashes=True)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=PatientRecordSchema)
async def create_patient_record(patient_record: PatientRecordInsertSchema, session: Session):
    db_patient = await session.scalar(
        select(Patient).where(Patient.id == patient_record.id_patient)
    )
    if not db_patient:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Patient not exists.'
        )

    db_patient_record = await session.scalar(
        select(PatientRecord).where(
            PatientRecord.id_patient == patient_record.id_patient
        )
    )

    if db_patient_record:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Resource already exists.'
        )

    db_patient_record = PatientRecord(
        demand_description=patient_record.demand_description,
        instruments_used=patient_record.instruments_used,
        idadi_analysis=patient_record.idadi_analysis,
        anamnese_analysis=patient_record.anamnese_analysis,
        anamnese_result=patient_record.anamnese_result,
        conclusion=patient_record.conclusion,
        id_patient=patient_record.id_patient,
    )

    session.add(db_patient_record)
    await session.commit()
    await session.refresh(db_patient_record)

    return db_patient_record


@router.get("/{id_patient_record}", response_model=PatientRecordSchema)
async def find_by_id(id_patient_record: int, session: Session):
    db_patient_record = await session.scalar(
        select(PatientRecord).where(PatientRecord.id_patient == id_patient_record)
    )
    if not db_patient_record:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not exists.")

    return db_patient_record


@router.put('/{patient_record_id}', response_model=PatientRecordSchema)
async def update_patient_record(
        patient_record_id: int,
        patient: PatientRecordInsertSchema,
        session: Session
):
    db_patient_record = await session.scalar(
        select(PatientRecord).where(PatientRecord.id == patient_record_id)
    )

    if not db_patient_record:   
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not exists.")

    db_patient_record.demand_description = patient.demand_description
    db_patient_record.instruments_used = patient.instruments_used
    db_patient_record.idadi_analysis = patient.idadi_analysis
    db_patient_record.anamnese_analysis = patient.anamnese_analysis
    db_patient_record.anamnese_result = patient.anamnese_result
    db_patient_record.conclusion = patient.conclusion
    db_patient_record.id_patient = patient.id_patient

    session.add(db_patient_record)
    await session.commit()
    return db_patient_record


@router.delete('/{patient_record_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_patient_record(
        patient_record_id: int,
        session: Session
):
    db_patient = await session.scalar(
        select(PatientRecord).where(PatientRecord.id == patient_record_id)
    )

    if not db_patient:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not exists.")

    await session.delete(db_patient)
    await session.commit()

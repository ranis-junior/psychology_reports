from http import HTTPStatus

from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import select, and_

from app.models import Patient
from app.routers import Session
from app.schema import PatientSchema
from app.schema.patients import PatientInsertSchema, PatientListSchema
from app.service.minio import upload_image_to_minio, get_file_url_from_minio

router = APIRouter(prefix="/patients", tags=["patients"], redirect_slashes=True)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=PatientSchema)
async def create_patient(patient: PatientInsertSchema, session: Session):
    db_patient = await session.scalar(
        select(Patient).where(
            and_(Patient.name == patient.name, Patient.birth_date == patient.birth_date)
        )
    )

    if db_patient:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Resource already exists.'
        )

    db_patient = Patient(
        name=patient.name,
        birth_date=patient.birth_date,
        id_psychologist=patient.id_psychologist,
        gender=patient.gender,
        father=patient.father,
        mother=patient.mother,
        father_profession=patient.father_profession,
        mother_profession=patient.mother_profession,
    )

    session.add(db_patient)
    await session.commit()
    await session.refresh(db_patient, attribute_names=['pti'])

    return db_patient


@router.get("/{id_patient}", response_model=PatientSchema)
async def find_by_id(id_patient: int, session: Session):
    db_patient = await session.scalar(
        select(Patient).where(Patient.id == id_patient)
    )
    if not db_patient:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Patient not found")

    schema = PatientSchema.model_validate(db_patient)
    if schema.photo:
        schema.photo = get_file_url_from_minio(schema.photo, schema.id)

    return schema


@router.get("/from_psychologist/{id_psychologist}", response_model=list[PatientListSchema])
async def read_patients(id_psychologist: int, session: Session, skip: int = 0, limit: int = 100):
    patients = (await session.scalars(
        select(Patient).where(Patient.id_psychologist == id_psychologist).offset(skip).limit(limit).order_by(
            Patient.name.asc())
    )).all()

    patients_schema = []
    for patient in patients:
        schema = PatientListSchema.model_validate(patient)
        if schema.photo:
            schema.photo = get_file_url_from_minio(schema.photo, schema.id)
        patients_schema.append(schema)

    return patients_schema


@router.put('/{patient_id}', response_model=PatientSchema)
async def update_patient(
        patient_id: int,
        patient: PatientInsertSchema,
        session: Session
):
    db_patient = await session.scalar(
        select(Patient).where(Patient.id == patient_id)
    )

    if not db_patient:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Patient not found")

    db_patient.name = patient.name
    db_patient.birth_date = patient.birth_date
    db_patient.gender = patient.gender
    db_patient.id_psychologist = patient.id_psychologist
    db_patient.father = patient.father
    db_patient.father_profession = patient.father_profession
    db_patient.mother = patient.mother
    db_patient.mother_profession = patient.mother_profession

    session.add(db_patient)
    await session.commit()
    await session.refresh(db_patient, attribute_names=['pti'])
    return db_patient


@router.post("/upload/{id_patient}", status_code=HTTPStatus.CREATED)
async def create_upload_file(id_patient: int, session: Session, file: UploadFile):
    db_patient = await session.scalar(
        select(Patient).where(Patient.id == id_patient)
    )

    if not db_patient:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Resource not exists.'
        )

    extension = file.filename.split('.')[1]
    image_name = f'cover.{extension}'
    db_patient.photo = image_name
    await session.commit()

    image_bytes = await file.read()
    upload_image_to_minio(image_bytes, file.content_type, image_name, db_patient.id)


@router.delete('/{patient_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_patient(
        patient_id: int,
        session: Session
):
    db_patient = await session.scalar(
        select(Patient).where(Patient.id == patient_id)
    )

    if not db_patient:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Patient not found")

    await session.delete(db_patient)
    await session.commit()

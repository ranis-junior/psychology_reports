import datetime
from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from starlette.responses import JSONResponse
from taskiq import SendTaskError
from taskiq.depends.progress_tracker import TaskProgress, TaskState

from app.models import Patient, IdadiNormativeTables
from app.models.idadi import Idadi
from app.models.idadi_values import IdadiValues
from app.routers import Session
from app.schema.idadi import IdadiUpdateSchema, IdadiInsertSchema, IdadiSchema
from app.tasks.report import generate_jasper_report
from app.worker import broker

router = APIRouter(prefix="/idadi", tags=["idadi"], redirect_slashes=True)
MAIN_REPORT_NAME = 'final_report'


@router.get('/report/generate/{id_patient}', status_code=HTTPStatus.CREATED)
async def generate_report(id_patient: int, session: Session):
    db_patient = await session.scalar(
        select(Patient).where(Patient.id == id_patient)
    )

    if not db_patient:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Patient not exists.'
        )

    try:
        task_result = await generate_jasper_report.kiq(MAIN_REPORT_NAME, {'id_patient': id_patient})
    except SendTaskError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=e.as_str())
    return {
        'task_id': task_result.task_id,
        'status': 'processing'
    }


@router.get('/report/status/{task_id}')
async def status_report(task_id: str):
    progress = await broker.result_backend.get_progress(task_id=task_id)
    if not progress:
        return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={
            'status': 'not exists'
        })

    if await broker.result_backend.is_result_ready(task_id):
        result = await broker.result_backend.get_result(task_id)
        return JSONResponse(status_code=HTTPStatus.OK, content={
            'task_id': task_id,
            'status': 'done',
            'result': result.return_value
        })
    elif progress.state == TaskState.SUCCESS:
        return JSONResponse(status_code=HTTPStatus.GONE, content={
            'task_id': task_id,
            'status': 'consumed'
        })
    else:
        return JSONResponse(status_code=HTTPStatus.ACCEPTED, content={
            'task_id': task_id,
            'status': 'processing'
        })


@router.post('/', status_code=HTTPStatus.CREATED, response_model=IdadiSchema)
async def create_idadi_value(idadi: IdadiInsertSchema, session: Session):
    db_idadi: Idadi = await session.scalar(
        select(Idadi).where(Idadi.id_patient == idadi.id_patient)
    )

    if db_idadi:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Resource already exists.'
        )

    db_patient: Patient = await session.scalar(
        select(Patient).where(Patient.id == idadi.id_patient)
    )

    diff_dates = lambda d1, d2: (d1.year - d2.year) * 12 + d1.month - d2.month
    age_in_months = idadi.protocol_age if idadi.protocol_age else diff_dates(datetime.today(), db_patient.birth_date)
    application_date = idadi.application_date if idadi.application_date else datetime.today()
    db_idadi = Idadi(
        protocol_age=age_in_months,
        application_date=application_date,
        id_patient=idadi.id_patient
    )

    session.add(db_idadi)
    await session.flush()

    for value in idadi.values:
        if not value.standard_score:
            idadi_normative_value: IdadiNormativeTables = await session.scalar(
                select(IdadiNormativeTables).where(and_(IdadiNormativeTables.initial_age_range <= age_in_months,
                                                        IdadiNormativeTables.final_age_range >= age_in_months,
                                                        IdadiNormativeTables.id_domain == value.id_domain,
                                                        IdadiNormativeTables.raw_score == value.raw_score)
                                                   )
            )
            value.standard_score = idadi_normative_value.standardized if idadi_normative_value else 0

        db_idadi_value = IdadiValues(
            raw_score=value.raw_score,
            standard_score=value.standard_score,
            id_domain=value.id_domain,
            id_idadi=db_idadi.id
        )

        session.add(db_idadi_value)
    await session.commit()
    await session.refresh(db_idadi, attribute_names=['values'])

    return db_idadi


@router.get("/{id_patient}", response_model=IdadiSchema)
async def find_idadi_for_patient(id_patient: int, session: Session):
    db_idadi = await session.scalar(
        select(Idadi).where(Idadi.id_patient == id_patient).options(joinedload(Idadi.values))
    )
    if not db_idadi:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not exists.")
    return db_idadi


@router.put('/', response_model=IdadiSchema)
async def update_idadi(
        idadi: IdadiUpdateSchema,
        session: Session
):
    db_idadi: Idadi = await session.scalar(
        select(Idadi).where(Idadi.id_patient == idadi.id_patient)
    )

    if not db_idadi:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Resource not exists.'
        )

    db_patient: Patient = await session.scalar(
        select(Patient).where(Patient.id == idadi.id_patient)
    )

    diff_dates = lambda d1, d2: (d1.year - d2.year) * 12 + d1.month - d2.month
    age_in_months = idadi.protocol_age if idadi.protocol_age else diff_dates(datetime.today(), db_patient.birth_date)
    application_date = idadi.application_date if idadi.application_date else datetime.today()

    db_idadi.protocol_age = age_in_months
    db_idadi.application_date = application_date

    session.add(db_idadi)

    for value in idadi.values:
        db_idadi_value: IdadiValues = (await session.scalar(
            select(IdadiValues).where(IdadiValues.id == value.id)
        ))

        if not db_idadi_value:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Idadi value not found")

        if not value.standard_score:
            idadi_normative_value: IdadiNormativeTables = await session.scalar(
                select(IdadiNormativeTables).where(and_(IdadiNormativeTables.initial_age_range <= age_in_months,
                                                        IdadiNormativeTables.final_age_range >= age_in_months,
                                                        IdadiNormativeTables.id_domain == value.id_domain,
                                                        IdadiNormativeTables.raw_score == value.raw_score)
                                                   )
            )
            value.standard_score = idadi_normative_value.standardized if idadi_normative_value else 0

        db_idadi_value.raw_score = value.raw_score
        db_idadi_value.standard_score = value.standard_score
        db_idadi_value.id_domain = value.id_domain

        session.add(db_idadi_value)
    await session.commit()
    await session.refresh(db_idadi, attribute_names=['values'])

    return db_idadi


@router.delete('/{id_idadi}', status_code=HTTPStatus.NO_CONTENT)
async def delete_idadi(
        id_idadi: int,
        session: Session
):
    db_idadi = await session.scalar(
        select(Idadi).where(Idadi.id == id_idadi)
    )

    if not db_idadi:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Idadi not found")

    db_idadi_values = await session.scalars(
        select(IdadiValues).where(IdadiValues.id_idadi == id_idadi)
    )
    for value in db_idadi_values.all():
        await session.delete(value)
    await session.delete(db_idadi)
    await session.commit()

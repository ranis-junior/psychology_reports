from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy.orm import contains_eager

from app.auth.security import get_current_user
from app.models import IdadiFormQuestion, IdadiFormQuestionPatient, Patient
from app.routers import Session
from app.schema.idadi_form_question import IdadiFormQuestionSchema

router = APIRouter(prefix="/idadi-form-question", tags=["idadi-form-question"], redirect_slashes=True,
                   dependencies=[Depends(get_current_user)])


@router.get("/", response_model=List[IdadiFormQuestionSchema])
async def list_idadi_form_questions(session: Session, skip: int = 0, limit: int = 100,
                                    id_patient: Optional[int] = None):
    if id_patient is not None:
        db_patient = await session.scalar(
            select(Patient).where(Patient.id == id_patient)
        )
        if not db_patient:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Patient not found")

        idadi_questions = (await session.scalars(
            select(IdadiFormQuestion).outerjoin(
                IdadiFormQuestionPatient,
                (IdadiFormQuestionPatient.id_idadi_form_question == IdadiFormQuestion.id) & (
                        IdadiFormQuestionPatient.id_patient == id_patient))
            .offset(skip).limit(limit)
            .options(contains_eager(IdadiFormQuestion.answer))
        )).unique().all()

        return idadi_questions

    idadi_questions = (await session.scalars(
        select(IdadiFormQuestion).offset(skip).limit(limit)
    )).all()

    return [IdadiFormQuestionSchema.from_catalog(question) for question in idadi_questions]


@router.get("/between-age/", response_model=List[IdadiFormQuestionSchema])
async def read_idadi_form_questions_from_age_range(id_patient: int, initial_age_range: int, final_age_range: int,
                                                   session: Session):
    db_patient = (await session.scalar(
        select(Patient).where(Patient.id == id_patient)
    ))
    if not db_patient:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Patient not found")

    idadi_questions = (await session.scalars(
        select(IdadiFormQuestion).where(
            and_(and_(IdadiFormQuestion.initial_start_age_range >= initial_age_range,
                      IdadiFormQuestion.final_start_age_range <= final_age_range),
                 and_(IdadiFormQuestion.initial_end_age_range >= initial_age_range,
                      IdadiFormQuestion.final_end_age_range <= final_age_range)
                 )).outerjoin(IdadiFormQuestionPatient,
                              (IdadiFormQuestionPatient.id_idadi_form_question == IdadiFormQuestion.id) & (
                                      IdadiFormQuestionPatient.id_patient == id_patient))
        .options(contains_eager(IdadiFormQuestion.answer))
    )).unique().all()

    return idadi_questions

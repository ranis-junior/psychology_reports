from http import HTTPStatus
from typing import List

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, and_, delete

from app.models import IdadiFormQuestion, IdadiFormQuestionPatient, Patient
from app.routers import Session
from app.schema.idadi_form_question_patient import IdadiFormQuestionPatientSchema, IdadiFormQuestionPatientInsertSchema, \
    IdadiFormQuestionPatientUpdateSchema, IdadiFormQuestionPatientUpdateBatchSchema

router = APIRouter(prefix="/idadi-form-question-patient", tags=["idadi-form-question-patient"], redirect_slashes=True)


@router.get("/{id_patient}/", response_model=List[IdadiFormQuestionPatientSchema])
async def read_idadi_form_questions_patient_by_id_patient(id_patient: int, session: Session):
    idadi_answers = (await session.scalars(
        select(
            IdadiFormQuestionPatient
        ).where(
            IdadiFormQuestionPatient.id_patient == id_patient
        )
    )).all()

    return idadi_answers


@router.post('/', status_code=HTTPStatus.CREATED, response_model=IdadiFormQuestionPatientSchema)
async def create_idadi_form_questions_patient(patient_answer: IdadiFormQuestionPatientInsertSchema, session: Session):
    db_patient = await session.scalar(
        select(Patient).where(Patient.id == patient_answer.id_patient)
    )

    if not db_patient:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Patient not exists.'
        )

    db_answer = await session.scalar(
        select(IdadiFormQuestionPatient).where(
            and_(IdadiFormQuestionPatient.id_patient == patient_answer.id_patient,
                 IdadiFormQuestionPatient.id_idadi_form_question == patient_answer.id_idadi_form_question)
        )
    )

    if db_answer:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Resource already exists.'
        )

    db_answer = IdadiFormQuestionPatient(
        id_patient=patient_answer.id_patient,
        id_idadi_form_question=patient_answer.id_idadi_form_question,
        yes=patient_answer.yes,
        no=patient_answer.no,
        maybe=patient_answer.maybe,
    )

    session.add(db_answer)
    await session.commit()

    return db_answer


@router.post('/batch/', status_code=HTTPStatus.CREATED, response_model=List[IdadiFormQuestionPatientSchema])
async def create_idadi_form_questions_patient_batch(patient_answers: List[IdadiFormQuestionPatientInsertSchema],
                                                    session: Session):
    id_patient = patient_answers[0].id_patient

    db_patient = await session.scalar(
        select(Patient).where(Patient.id == id_patient)
    )
    if not db_patient:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Patient not exists.'
        )

    questions_ids = set(map(lambda x: x.id_idadi_form_question, patient_answers))
    db_questions = (await session.scalars(
        select(IdadiFormQuestion).where(IdadiFormQuestion.id.in_(questions_ids))
    )).all()
    found_ids = set(question.id for question in db_questions)
    missing_question_ids = questions_ids - found_ids
    if missing_question_ids:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={
                'msg': 'Question not exists.',
                'ids': list(missing_question_ids),
            }
        )

    db_answers = []
    for patient_answer in patient_answers:
        db_answer = await session.scalar(
            select(IdadiFormQuestionPatient).where(
                and_(IdadiFormQuestionPatient.id_patient == patient_answer.id_patient,
                     IdadiFormQuestionPatient.id_idadi_form_question == patient_answer.id_idadi_form_question)
            )
        )
        if db_answer:
            db_answers.append(db_answer)

    if db_answers:
        ids = {answer.id for answer in db_answers}
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail={
                'msg': 'Answer already exists.',
                'ids': list(ids),
            }
        )

    db_answers = []
    for patient_answer in patient_answers:
        db_answer = IdadiFormQuestionPatient(
            id_patient=patient_answer.id_patient,
            id_idadi_form_question=patient_answer.id_idadi_form_question,
            yes=patient_answer.yes,
            no=patient_answer.no,
            maybe=patient_answer.maybe,
        )

        session.add(db_answer)
        db_answers.append(db_answer)
    await session.commit()

    return db_answers


@router.delete('/{id_patient_answer}/', status_code=HTTPStatus.NO_CONTENT)
async def delete_idadi_form_questions_patient(id_patient_answer: int, session: Session):
    db_answer = await session.scalar(
        select(IdadiFormQuestionPatient).where(
            IdadiFormQuestionPatient.id == id_patient_answer
        )
    )

    if not db_answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not exists.")

    await session.delete(db_answer)
    await session.commit()


@router.delete('/by-patient/{id_patient:int}/', status_code=HTTPStatus.NO_CONTENT)
async def delete_idadi_form_questions_patient_by_patient(id_patient: int, session: Session):
    await session.execute(
        delete(IdadiFormQuestionPatient).where(
            IdadiFormQuestionPatient.id_patient == id_patient
        ))
    await session.commit()


@router.put('/{idadi_answer_id:int}/', response_model=IdadiFormQuestionPatientSchema)
async def update_idadi_form_questions_patient(idadi_answer_id: int,
                                              idadi_answer: IdadiFormQuestionPatientUpdateSchema,
                                              session: Session):
    db_answer = await session.scalar(
        select(IdadiFormQuestionPatient).where(IdadiFormQuestionPatient.id == idadi_answer_id)
    )

    if not db_answer:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not exists.")

    db_answer.yes = idadi_answer.yes
    db_answer.no = idadi_answer.no
    db_answer.maybe = idadi_answer.maybe

    session.add(db_answer)
    await session.commit()
    return db_answer


@router.put('/batch/', response_model=List[IdadiFormQuestionPatientSchema])
async def update_idadi_form_questions_patient(idadi_answers: List[IdadiFormQuestionPatientUpdateBatchSchema],
                                              session: Session):
    answer_ids = {answer.id for answer in idadi_answers}
    db_answers = (await session.scalars(
        select(IdadiFormQuestionPatient).where(IdadiFormQuestionPatient.id.in_(answer_ids))
    )).all()

    found_ids = {answer.id for answer in db_answers}
    missing_answer_ids = answer_ids - found_ids
    if missing_answer_ids:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={
            'msg': 'Answer not found.',
            'ids': list(missing_answer_ids),
        })
    for answer in db_answers:
        idadi_answer = next(filter(lambda x: x.id == answer.id, idadi_answers))
        answer.yes = idadi_answer.yes
        answer.no = idadi_answer.no
        answer.maybe = idadi_answer.maybe
        session.add(answer)
    await session.commit()
    return db_answers

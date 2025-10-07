import asyncio
from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.models import Pti, Patient, PtiStimulusAreas, PtiSpecificObjectivesTopics, PtiSpecificObjectivesSubTopics
from app.routers import Session
from app.schema.pti import PtiSchema, PtiInsertSchema, PtiFullInsertSchema

router = APIRouter(prefix="/pti", tags=["pti"], redirect_slashes=True)


@router.post('/', summary="Cria um PTI simples, para ser preenchido posteriormente",
             response_description="O PTI criado com ID", status_code=HTTPStatus.CREATED,
             response_model=PtiSchema)
async def create_pti(pti: PtiInsertSchema, session: Session):
    db_id_patient = (await session.scalar(
        select(Patient.id).where(Patient.id == pti.id_patient)
    ))

    if not db_id_patient:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Patient not exists.'
        )

    db_pti = await session.scalar(
        select(Pti).where(
            Pti.id_patient == pti.id_patient
        )
    )

    if db_pti:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Resource already exists.'
        )

    db_pti = Pti(
        id_patient=pti.id_patient,
        evaluation_date=pti.evaluation_date,
    )

    session.add(db_pti)
    print(db_pti.pti_stimulus_areas)
    await session.commit()
    await session.refresh(db_pti, attribute_names=['pti_stimulus_areas'])

    return db_pti


@router.get("/", response_model=list[PtiSchema])
async def list_pti(session: Session):
    db_pti_list: list[Pti] = (await session.scalars(
        select(Pti)
    )).unique().all()

    return db_pti_list


@router.get("/from_patient/{id_patient}", response_model=PtiSchema)
async def read_pti_from_patient(id_patient: int, session: Session):
    db_pti: Pti = await session.scalar(
        select(Pti).where(Pti.id_patient == id_patient)
    )

    if not db_pti:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Resource not exists.'
        )

    return db_pti


@router.delete('/{id_pti}', status_code=HTTPStatus.NO_CONTENT)
async def delete_pti(
        id_pti: int,
        session: Session
):
    db_pti = await session.scalar(
        select(Pti).where(Pti.id == id_pti)
    )

    if not db_pti:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pti not found")

    await session.delete(db_pti)
    await session.commit()


@router.post("/full_insert", response_model=PtiSchema)
async def create_full_pti(
        pti_data: PtiFullInsertSchema,
        session: Session
):
    db_patient = await session.scalar(
        select(Patient).where(Patient.id == pti_data.id_patient)
    )
    if not db_patient:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Patient not found")

    db_pti = Pti(**pti_data.model_dump(exclude={'pti_stimulus_areas'}))
    session.add(db_pti)
    await session.flush()

    for stimulus_area in pti_data.pti_stimulus_areas:
        db_stimulus_area = PtiStimulusAreas(**stimulus_area.model_dump(exclude={"pti_specific_objectives_topics"}),
                                            id_pti=db_pti.id)
        session.add(db_stimulus_area)
        await session.flush()

        for specific_objective_topic in stimulus_area.pti_specific_objectives_topics:
            db_specific_objective_topic = PtiSpecificObjectivesTopics(
                **specific_objective_topic.model_dump(exclude={"pti_specific_objective_subtopic"}),
                id_pti_stimulus_area=db_stimulus_area.id)
            session.add(db_specific_objective_topic)
            await session.flush()

            for specific_objective_subtopic in specific_objective_topic.pti_specific_objective_subtopic:
                db_specific_objective_subtopic = PtiSpecificObjectivesSubTopics(
                    **specific_objective_subtopic.model_dump(),
                    id_pti_specific_objectives_topics=db_specific_objective_topic.id)
                session.add(db_specific_objective_subtopic)

    await session.commit()
    await session.refresh(db_pti)

    return db_pti

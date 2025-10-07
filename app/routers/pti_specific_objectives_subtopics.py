from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func

from app.models import PtiSpecificObjectivesTopics, PtiSpecificObjectivesSubTopics
from app.routers import Session
from app.schema.pti_specific_objectives_subtopics import PtiSpecificObjectivesSubTopicsSchema, \
    PtiSpecificObjectivesSubTopicsInsertSchema

router = APIRouter(prefix="/specific_objectives_subtopics", tags=["specific_objectives_subtopics"],
                   redirect_slashes=True)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=PtiSpecificObjectivesSubTopicsSchema)
async def create_pti_specific_objectives_subtopics(
        pti_specific_objectives_subtopics: PtiSpecificObjectivesSubTopicsInsertSchema,
        session: Session):
    db_pti_specific_objectives_subtopics = await session.scalar(
        select(PtiSpecificObjectivesTopics).where(
            func.lower(PtiSpecificObjectivesSubTopics.name) == pti_specific_objectives_subtopics.name.lower()
        )
    )

    if db_pti_specific_objectives_subtopics:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Resource already exists.',
        )

    db_pti_specific_objectives_subtopics = PtiSpecificObjectivesSubTopics(
        name=pti_specific_objectives_subtopics.name,
        id_pti_specific_objectives_topics=pti_specific_objectives_subtopics.id_pti_specific_objectives_topics,
    )

    session.add(db_pti_specific_objectives_subtopics)
    await session.commit()

    return db_pti_specific_objectives_subtopics


@router.get("/", response_model=list[PtiSpecificObjectivesSubTopicsSchema])
async def list_specific_objectives_subtopics(session: Session):
    db_pti_specific_objectives_subtopics = (await session.scalars(
        select(PtiSpecificObjectivesSubTopics)
    )).all()

    return db_pti_specific_objectives_subtopics


@router.get("/from_topic/{id_pti_specific_objective_topic}", response_model=list[PtiSpecificObjectivesSubTopicsSchema])
async def read_specific_objectives_subtopics_from_objective_topics(id_pti_specific_objective_topic: int,
                                                                   session: Session):
    db_pti_specific_objectives_subtopics = (await session.scalars(
        select(PtiSpecificObjectivesSubTopics).where(
            PtiSpecificObjectivesSubTopics.id_pti_specific_objectives_topics == id_pti_specific_objective_topic)
    )).all()

    return db_pti_specific_objectives_subtopics


@router.put('/{id_pti_specific_objectives_subtopics}', response_model=PtiSpecificObjectivesSubTopicsSchema)
async def update_pti_specific_objectives_subtopics(
        id_pti_specific_objectives_subtopics: int,
        pti_specific_objectives_subtopics: PtiSpecificObjectivesSubTopicsInsertSchema,
        session: Session
):
    db_pti_specific_objectives_subtopics = await session.scalar(
        select(PtiSpecificObjectivesSubTopics).where(
            PtiSpecificObjectivesSubTopics.id == id_pti_specific_objectives_subtopics)
    )

    if not db_pti_specific_objectives_subtopics:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Specific Objective subtopic not found")

    db_pti_specific_objectives_subtopics.name = pti_specific_objectives_subtopics.name

    session.add(db_pti_specific_objectives_subtopics)

    await session.commit()
    await session.refresh(db_pti_specific_objectives_subtopics)

    return db_pti_specific_objectives_subtopics


@router.delete('/{id_pti_specific_objectives_subtopics}', status_code=HTTPStatus.NO_CONTENT)
async def delete_pti_specific_objectives_subtopics(
        id_pti_specific_objectives_subtopics: int,
        session: Session
):
    db_pti_specific_objectives_subtopics = await session.scalar(
        select(PtiSpecificObjectivesSubTopics).where(
            PtiSpecificObjectivesSubTopics.id == id_pti_specific_objectives_subtopics)
    )

    if not db_pti_specific_objectives_subtopics:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Specific Objective Subtopic not found.")

    await session.delete(db_pti_specific_objectives_subtopics)
    await session.commit()

#

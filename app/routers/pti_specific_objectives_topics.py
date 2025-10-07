from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func

from app.models import PtiSpecificObjectivesTopics
from app.routers import Session
from app.schema.pti_specific_objectives_topics import PtiSpecificObjectivesTopicsSchema, \
    PtiSpecificObjectivesTopicsInsertSchema

router = APIRouter(prefix="/specific_objectives_topics", tags=["specific_objectives_topics"], redirect_slashes=True)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=PtiSpecificObjectivesTopicsSchema)
async def create_pti_specific_objectives_topics(pti_specific_objectives_topics: PtiSpecificObjectivesTopicsInsertSchema,
                                                session: Session):
    db_pti_specific_objectives_topics = await session.scalar(
        select(PtiSpecificObjectivesTopics).where(
            func.lower(PtiSpecificObjectivesTopics.name) == pti_specific_objectives_topics.name.lower()
        )
    )

    if db_pti_specific_objectives_topics:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Resource already exists.',
        )

    db_pti_specific_objectives_topics = PtiSpecificObjectivesTopics(
        name=pti_specific_objectives_topics.name,
        id_pti_stimulus_area=pti_specific_objectives_topics.id_pti_stimulus_area
    )

    session.add(db_pti_specific_objectives_topics)
    await session.commit()
    await session.refresh(db_pti_specific_objectives_topics, attribute_names=['pti_specific_objective_subtopic'])

    return db_pti_specific_objectives_topics


@router.get("/", response_model=list[PtiSpecificObjectivesTopicsSchema])
async def list_specific_objectives(session: Session):
    db_pti_specific_objectives_topics = (await session.scalars(
        select(PtiSpecificObjectivesTopics)
    )).unique().all()

    return db_pti_specific_objectives_topics


@router.get("/from_stimulus_area/{id_pti_stimulus_area}", response_model=list[PtiSpecificObjectivesTopicsSchema])
async def read_specific_objectives_from_stimulus_area(id_pti_stimulus_area: int, session: Session):
    db_pti_specific_objectives_topics = (await session.scalars(
        select(PtiSpecificObjectivesTopics).where(
            PtiSpecificObjectivesTopics.id_pti_stimulus_area == id_pti_stimulus_area)
    )).unique().all()

    return db_pti_specific_objectives_topics


@router.put('/{id_pti_specific_objectives_topics}', response_model=PtiSpecificObjectivesTopicsSchema)
async def update_pti_specific_objectives_topics(
        id_pti_specific_objectives_topics: int,
        pti_specific_objectives_topics: PtiSpecificObjectivesTopicsInsertSchema,
        session: Session
):
    db_pti_specific_objectives_topics = await session.scalar(
        select(PtiSpecificObjectivesTopics).where(PtiSpecificObjectivesTopics.id == id_pti_specific_objectives_topics)
    )

    if not db_pti_specific_objectives_topics:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Specific Objective topic not found")

    db_pti_specific_objectives_topics.name = pti_specific_objectives_topics.name

    session.add(db_pti_specific_objectives_topics)

    await session.commit()
    await session.refresh(db_pti_specific_objectives_topics)

    return db_pti_specific_objectives_topics


@router.delete('/{id_pti_specific_objectives_topics}', status_code=HTTPStatus.NO_CONTENT)
async def delete_pti_specific_objectives_topics(
        id_pti_specific_objectives_topics: int,
        session: Session
):
    db_pti_specific_objectives_topics = await session.scalar(
        select(PtiSpecificObjectivesTopics).where(PtiSpecificObjectivesTopics.id == id_pti_specific_objectives_topics)
    )

    if not db_pti_specific_objectives_topics:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Specific Objective Topic not found.")

    await session.delete(db_pti_specific_objectives_topics)
    await session.commit()

from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func

from app.models import PtiStimulusAreas
from app.routers import Session
from app.schema.pti_stimulus_areas import PtiStimulusAreasSchema, PtiStimulusAreasInsertSchema

router = APIRouter(prefix="/stimulus_area", tags=["pti_stimulus_area"], redirect_slashes=True)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=PtiStimulusAreasSchema)
async def create_pti_stimulus_area(pti_stimulus_area: PtiStimulusAreasInsertSchema, session: Session):
    db_pti_stimulus_area = await session.scalar(
        select(PtiStimulusAreas).where(
            func.lower(PtiStimulusAreas.name) == pti_stimulus_area.name.lower()
        )
    )

    if db_pti_stimulus_area:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Resource already exists.',
        )

    db_pti_stimulus_area = PtiStimulusAreas(
        name=pti_stimulus_area.name,
        id_pti=pti_stimulus_area.id_pti
    )

    session.add(db_pti_stimulus_area)
    await session.commit()
    await session.refresh(db_pti_stimulus_area, attribute_names=['pti'])

    return db_pti_stimulus_area


@router.get("/", response_model=list[PtiStimulusAreasSchema])
async def list_stimulus_area(session: Session):
    db_pti_stimulus_area = (await session.scalars(
        select(PtiStimulusAreas)
    )).unique().all()

    return db_pti_stimulus_area


@router.get("/from_pti/{id_pti}", response_model=list[PtiStimulusAreasSchema])
async def read_stimulus_area_from_pti(id_pti: int, session: Session):
    db_pti_stimulus_area = (await session.scalars(
        select(PtiStimulusAreas).where(PtiStimulusAreas.id_pti == id_pti)
    )).unique().all()

    return db_pti_stimulus_area


@router.put('/{id_pti_stimulus_area}', response_model=PtiStimulusAreasSchema)
async def update_pti_stimulus_area(
        id_pti_stimulus_area: int,
        pti_stimulus_area: PtiStimulusAreasInsertSchema,
        session: Session
):
    db_pti_stimulus_area = await session.scalar(
        select(PtiStimulusAreas).where(PtiStimulusAreas.id == id_pti_stimulus_area)
    )

    if not db_pti_stimulus_area:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Stimulus Area not found")

    db_pti_stimulus_area.name = pti_stimulus_area.name

    session.add(db_pti_stimulus_area)

    await session.commit()
    await session.refresh(db_pti_stimulus_area)

    return db_pti_stimulus_area


@router.delete('/{id_pti_stimulus_area}', status_code=HTTPStatus.NO_CONTENT)
async def delete_pti_stimulu_area(
        id_pti_stimulus_area: int,
        session: Session
):
    db_pti_stimulu_area = await session.scalar(
        select(PtiStimulusAreas).where(PtiStimulusAreas.id == id_pti_stimulus_area)
    )

    if not db_pti_stimulu_area:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Stimulus Area not found.")

    await session.delete(db_pti_stimulu_area)
    await session.commit()

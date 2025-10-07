from http import HTTPStatus
from typing import List

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.models import Psychologist
from app.routers import Session
from app.schema import PsychologistSchema, PsychologistInsertSchema

router = APIRouter(prefix="/psychologists", tags=["psychologists"], redirect_slashes=True)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=PsychologistSchema)
async def create_psychologist(psy: PsychologistInsertSchema, session: Session):
    db_psy = await session.scalar(
        select(Psychologist).where(
            or_(Psychologist.name == psy.name, Psychologist.crp == psy.crp)
        )
    )

    if db_psy:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Resource already exists.'
        )

    db_psy = Psychologist(
        name=psy.name,
        birth_date=psy.birth_date,
        crp=psy.crp,
    )

    session.add(db_psy)
    await session.commit()
    await session.refresh(db_psy)

    return db_psy


@router.get("/", response_model=List[PsychologistSchema])
async def list_psychologists(session: Session, skip: int = 0, limit: int = 100):
    psychologists = (await session.scalars(
        select(Psychologist).offset(skip).limit(limit)
    )).all()

    return psychologists


@router.put('/{psychologist_id}', response_model=PsychologistSchema)
async def update_psychologist(
        psychologist_id: int,
        psy: PsychologistInsertSchema,
        session: Session
):
    db_psy = (await session.scalar(
        select(Psychologist).where(Psychologist.id == psychologist_id)
    ))

    if not db_psy:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Psychologist not found")

    db_psy.name = psy.name
    db_psy.birth_date = psy.birth_date
    db_psy.crp = psy.crp

    session.add(db_psy)
    await session.commit()
    await session.refresh(db_psy)

    return db_psy


@router.delete('/{psychologist_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_psychologist(
        psychologist_id: int,
        session: Session
):
    db_psy = await session.scalar(
        select(Psychologist).where(Psychologist.id == psychologist_id)
    )

    if not db_psy:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Psychologist not found")

    await session.delete(db_psy)
    await session.commit()

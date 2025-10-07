from typing import List

from fastapi import APIRouter
from sqlalchemy import select

from app.models import IdadiDomains
from app.routers import Session
from app.schema.idadi_domains import IdadiDomainsSchema

router = APIRouter(prefix="/idadi-domains", tags=["idadi-domains"], redirect_slashes=True)


@router.get("/", response_model=List[IdadiDomainsSchema])
async def list_idadi_domains(session: Session):
    db_idadi_domains = (await session.scalars(
        select(IdadiDomains)
    )).all()

    return db_idadi_domains

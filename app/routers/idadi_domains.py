from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.auth.security import get_current_user
from app.models import IdadiDomains
from app.routers import Session
from app.schema.idadi_domains import IdadiDomainsSchema

router = APIRouter(prefix="/idadi-domains", tags=["idadi-domains"], redirect_slashes=True,
                   dependencies=[Depends(get_current_user)])


@router.get("/", response_model=List[IdadiDomainsSchema])
async def list_idadi_domains(session: Session):
    db_idadi_domains = (await session.scalars(
        select(IdadiDomains)
    )).all()

    return db_idadi_domains

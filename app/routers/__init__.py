from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session_generator

Session = Annotated[AsyncSession, Depends(get_session_generator)]

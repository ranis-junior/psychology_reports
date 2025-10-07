from datetime import date
from typing import List

from sqlalchemy import Text, Date, Integer
from sqlalchemy.orm import Mapped, relationship, mapped_column
from app.models import Base, TimestampMixin


class Psychologist(Base, TimestampMixin):
    __tablename__ = 'psychologists'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    crp: Mapped[str] = mapped_column(Text, nullable=False)
    patients: Mapped[List['Patient']] = relationship(back_populates='psychologists', init=False)

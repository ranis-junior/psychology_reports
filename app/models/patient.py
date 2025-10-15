from datetime import date
from typing import Optional

from sqlalchemy import Text, Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models import Base, TimestampMixin


class Patient(Base, TimestampMixin):
    __tablename__ = 'patients'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(Text, nullable=False)

    id_psychologist: Mapped[int] = mapped_column(ForeignKey("psychologists.id"), nullable=False)

    psychologists: Mapped['Psychologist'] = relationship(back_populates="patients", init=False)
    pti: Mapped['Pti'] = relationship(back_populates="patient", init=False)

    father: Mapped[Optional[str]]
    father_profession: Mapped[Optional[str]]
    mother: Mapped[Optional[str]]
    mother_profession: Mapped[Optional[str]]
    photo: Mapped[Optional[str]] = mapped_column(Text, init=False)

from datetime import datetime
from typing import List

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, TimestampMixin


class Idadi(Base, TimestampMixin):
    __tablename__ = 'idadi'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    protocol_age: Mapped[int]
    application_date: Mapped[datetime]
    id_patient: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)


    values: Mapped[List['IdadiValues']] = relationship(back_populates='idadi', init=False)

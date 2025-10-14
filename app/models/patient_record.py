from datetime import date
from typing import Optional

from sqlalchemy import Text, Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models import Base, TimestampMixin


class PatientRecord(Base, TimestampMixin):
    __tablename__ = 'patient_records'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    demand_description: Mapped[Optional[str]]
    instruments_used: Mapped[Optional[str]]
    idadi_analysis: Mapped[Optional[str]]
    anamnese_analysis: Mapped[Optional[str]]
    anamnese_result: Mapped[Optional[str]]
    conclusion: Mapped[Optional[str]]

    id_patient: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)


from datetime import date

from sqlalchemy import Text, Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models import Base, TimestampMixin


class PatientRecord(Base, TimestampMixin):
    __tablename__ = 'patient_records'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    demand_description: Mapped[str]
    instruments_used: Mapped[str]
    idadi_analysis: Mapped[str]
    anamnese_analysis: Mapped[str]
    anamnese_result: Mapped[str]
    conclusion: Mapped[str]

    id_patient: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)


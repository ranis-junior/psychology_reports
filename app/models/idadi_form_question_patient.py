from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base, TimestampMixin


class IdadiFormQuestionPatient(Base, TimestampMixin):
    __tablename__ = 'idadi_form_question_patient'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    yes: Mapped[bool]
    no: Mapped[bool]
    maybe: Mapped[bool]
    id_idadi_form_question: Mapped[int] = mapped_column(ForeignKey("idadi_form_questions.id"), nullable=False)
    id_patient: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)

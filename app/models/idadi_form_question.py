from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, TimestampMixin


class IdadiFormQuestion(Base, TimestampMixin):
    __tablename__ = 'idadi_form_questions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    code: Mapped[str]
    description: Mapped[str]
    initial_start_age_range: Mapped[int]
    final_start_age_range: Mapped[int]
    initial_end_age_range: Mapped[int]
    final_end_age_range: Mapped[int]
    answer: Mapped['IdadiFormQuestionPatient'] = relationship(init=False, lazy='joined')

    id_domain: Mapped[int] = mapped_column(ForeignKey("idadi_domains.id"), nullable=False)

    domain: Mapped['IdadiDomains'] = relationship(init=False, lazy='joined')

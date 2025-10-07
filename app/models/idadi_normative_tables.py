from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models import Base, TimestampMixin


class IdadiNormativeTables(Base, TimestampMixin):
    __tablename__ = 'idadi_normative_tables'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    initial_age_range: Mapped[int]
    final_age_range: Mapped[int]
    raw_score: Mapped[int]
    developmental_score: Mapped[float]
    lower_confidence_interval: Mapped[float]
    upper_confidence_interval: Mapped[float]
    z: Mapped[float]
    standardized: Mapped[int]
    see: Mapped[float]
    information: Mapped[float]

    id_domain: Mapped[int] = mapped_column(ForeignKey("idadi_domains.id"), nullable=False)

    domain: Mapped['IdadiDomains'] = relationship(init=False, lazy='joined')

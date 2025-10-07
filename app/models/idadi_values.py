from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models import Base, TimestampMixin


class IdadiValues(Base, TimestampMixin):
    __tablename__ = 'idadi_values'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    raw_score: Mapped[int]
    standard_score: Mapped[int]

    id_domain: Mapped[int] = mapped_column(ForeignKey("idadi_domains.id"), nullable=False)
    domain: Mapped['IdadiDomains'] = relationship(init=False, lazy='joined')

    id_idadi: Mapped[int] = mapped_column(ForeignKey("idadi.id"), nullable=False)
    idadi: Mapped['Idadi'] = relationship(back_populates='values', init=False, lazy='joined')

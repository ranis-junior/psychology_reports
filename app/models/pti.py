from datetime import datetime
from typing import List

from sqlalchemy import Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models import Base, TimestampMixin


class Pti(Base, TimestampMixin):
    __tablename__ = 'pti'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)

    id_patient: Mapped[int] = mapped_column(ForeignKey('patients.id'), nullable=False)
    evaluation_date: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    patient: Mapped['Patient'] = relationship(back_populates='pti', init=False)

    pti_stimulus_areas: Mapped[List['PtiStimulusAreas']] = relationship(back_populates='pti', init=False, lazy='joined',
                                                                        cascade='delete')

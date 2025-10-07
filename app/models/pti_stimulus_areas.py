from typing import List

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from . import Base, TimestampMixin


class PtiStimulusAreas(Base, TimestampMixin):
    __tablename__ = 'pti_stimulus_areas'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

    id_pti: Mapped[int] = mapped_column(ForeignKey('pti.id'), nullable=False)
    pti: Mapped['Pti'] = relationship(back_populates='pti_stimulus_areas', init=False)

    pti_specific_objectives_topics: Mapped[List['PtiSpecificObjectivesTopics']] = relationship(
        back_populates='pti_stimulus_areas', init=False, lazy='joined', cascade='delete')

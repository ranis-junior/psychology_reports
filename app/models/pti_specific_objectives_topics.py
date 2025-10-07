from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, TimestampMixin


class PtiSpecificObjectivesTopics(Base, TimestampMixin):
    __tablename__ = 'pti_specific_objectives_topics'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(nullable=False)

    id_pti_stimulus_area: Mapped[int] = mapped_column(ForeignKey('pti_stimulus_areas.id'), nullable=False)
    pti_stimulus_areas: Mapped['PtiStimulusAreas'] = relationship(back_populates='pti_specific_objectives_topics',
                                                                  init=False)

    pti_specific_objective_subtopic: Mapped[list['PtiSpecificObjectivesSubTopics']] = relationship(
        back_populates='pti_specific_objectives_topics', init=False, lazy='joined', cascade='delete')

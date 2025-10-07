from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, TimestampMixin


class PtiSpecificObjectivesSubTopics(Base, TimestampMixin):
    __tablename__ = 'pti_specific_objectives_subtopics'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(nullable=False)

    id_pti_specific_objectives_topics: Mapped[int] = mapped_column(ForeignKey('pti_specific_objectives_topics.id'),
                                                                   nullable=False)
    pti_specific_objectives_topics: Mapped['PtiSpecificObjectivesTopics'] = relationship(
        back_populates='pti_specific_objective_subtopic',
        init=False)

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedAsDataclass
from sqlalchemy.sql import func


class Base(DeclarativeBase, MappedAsDataclass, AsyncAttrs):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
        init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


from app.models.patient import Patient
from app.models.patient_record import PatientRecord
from app.models.psychologist import Psychologist
from app.models.pti import Pti
from app.models.pti_stimulus_areas import PtiStimulusAreas
from app.models.pti_specific_objectives_topics import PtiSpecificObjectivesTopics
from app.models.pti_specific_objectives_subtopics import PtiSpecificObjectivesSubTopics
from app.models.idadi import Idadi
from app.models.idadi_domains import IdadiDomains
from app.models.idadi_normative_tables import IdadiNormativeTables
from app.models.idadi_values import IdadiValues
from app.models.programs_upload import ProgramsUpload

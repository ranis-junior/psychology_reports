from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base, TimestampMixin


class ProgramsUpload(Base, TimestampMixin):
    __tablename__ = 'programs_upload'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    name: Mapped[str]
    filename: Mapped[str]
    path: Mapped[str]
    generated: Mapped[bool]
    sequence: Mapped[int]
    id_psychologist: Mapped[int] = mapped_column(ForeignKey("psychologists.id"), nullable=False)

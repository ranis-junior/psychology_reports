from sqlalchemy import Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base, TimestampMixin


class IdadiDomains(Base, TimestampMixin):
    __tablename__ = 'idadi_domains'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str]

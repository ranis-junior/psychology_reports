from sqlalchemy import Integer, Boolean, Text
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    username: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    psychologist: Mapped['Psychologist'] = relationship(init=False)

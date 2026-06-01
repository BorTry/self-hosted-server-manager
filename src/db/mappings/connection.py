from sqlalchemy import ForeignKey, func, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from sqlalchemy.dialects.postgresql import INET
from datetime import datetime

class Base(DeclarativeBase):
    metadata = MetaData(schema="admin")

class connections(Base):
    __tablename__ = "connections"

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    ip: Mapped[str] =                                   mapped_column(INET, nullable=False, unique=True)
    blacklisted: Mapped[bool] =                         mapped_column(default=False)
    attempts: Mapped[list["login_attempts"]] =          relationship("login_attempts")

    def __repr__(self) -> str:
        return f'connection(id={self.id!r}, ip={self.ip!r})'

class login_attempts(Base):
    __tablename__ = "login_attempts"

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    connection_id: Mapped["connections"] =              mapped_column(ForeignKey("admin.connections.id"))
    failed_login: Mapped[bool] =                        mapped_column(nullable=False, default=True)
    time: Mapped[datetime] =                            mapped_column(default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f'login_attempts(id={self.id!r}, connection_id={self.connection_id!r}, failed={self.failed_login!r}, time={self.time!r})'
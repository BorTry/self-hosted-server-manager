from sqlalchemy import Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from datetime import datetime

class Base(DeclarativeBase):
    pass

class metrics_view(Base):
    __tablename__ = "metrics"

    name: Mapped[str] =                                 mapped_column(primary_key=True)
    time: Mapped[datetime] =                            mapped_column(DateTime(timezone=True), primary_key=True)
    cpu: Mapped[Float] =                                mapped_column(Float(precision=4), nullable=False)
    ram: Mapped[Float] =                                mapped_column(Float(precision=4), nullable=False)
    up: Mapped[int] =                                   mapped_column(nullable=False)
    down: Mapped[int] =                                 mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f'metric_view(name={self.name!r}, time={self.time!r} cpu={self.cpu!r} ram={self.ram!r} up={self.up!r} down={self.down!r})'
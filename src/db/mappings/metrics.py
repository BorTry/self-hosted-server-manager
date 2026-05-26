from sqlalchemy import ForeignKey, func, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from datetime import datetime

class Base(DeclarativeBase):
    pass

class container(Base):
    __tablename__ = "container"

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    name: Mapped[str] =                                 mapped_column(nullable=False)

class metric_timestamp(Base):
    __tablename__ = "metric_timestamp"

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    time: Mapped[datetime] =                            mapped_column(default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f'metric_timestamp(id={self.id!r}, time={self.time!r})'

class performance_metric(Base):
    __tablename__ = "performance_metric"

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    container_id: Mapped[int] =                         mapped_column(ForeignKey("container.id"), nullable=False)
    time_id: Mapped["metric_timestamp"] =               mapped_column(ForeignKey("metric_timestamp.id"), nullable=False)
    cpu: Mapped[Float] =                                mapped_column(Float(precision=4), nullable=False)
    ram: Mapped[Float] =                                mapped_column(Float(precision=4), nullable=False)
    time: Mapped["metric_timestamp"] =                  relationship()

    def __repr__(self) -> str:
        return f'performance_metric(id={self.id!r}, time_id={self.time_id!r}, cpu={self.cpu!r}, ram={self.ram!r})'

class traffic_metric(Base):
    __tablename__ = "traffic_metric"

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    container_id: Mapped[int] =                         mapped_column(ForeignKey("container.id"), nullable=False)
    time_id: Mapped["metric_timestamp"] =               mapped_column(ForeignKey("metric_timestamp.id"), nullable=False)
    up: Mapped[Float] =                                 mapped_column(Float(precision=4), nullable=False)
    down: Mapped[Float] =                               mapped_column(Float(precision=4), nullable=False)
    time: Mapped["metric_timestamp"] =                  relationship()

    def __repr__(self) -> str:
        return f'traffic_metric(id={self.id!r}, time_id={self.time_id!r}, up={self.up!r}, down={self.down!r})'
from sqlalchemy import ForeignKey, Float, DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from datetime import datetime, timezone

from .servers import container as Container
from .metadata import server_metric_meta_data

class Base(DeclarativeBase):
    metadata = server_metric_meta_data

class metric_timestamp(Base):
    __tablename__ = "timestamp"
    __table_args__ = {"schema":"metrics"}

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    time: Mapped[datetime] =                            mapped_column(DateTime(timezone=True), default=lambda _: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f'metric_timestamp(id={self.id!r}, time={self.time!r})'

class performance_metric(Base):
    __tablename__ = "performance"
    __table_args__ = {"schema":"metrics"}

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    container_id: Mapped[int] =                         mapped_column(ForeignKey("servers.container.id"), nullable=False)
    time_id: Mapped[int] =                              mapped_column(ForeignKey("metrics.timestamp.id"), nullable=False)
    cpu: Mapped[Float] =                                mapped_column(Float(precision=4), nullable=False)
    ram: Mapped[Float] =                                mapped_column(Float(precision=4), nullable=False)

    time =                                              relationship("metric_timestamp", foreign_keys=[time_id])
    container =                                         relationship(Container, foreign_keys=[container_id])

    def __repr__(self) -> str:
        return f'performance_metric(id={self.id!r}, time_id={self.time_id!r}, cpu={self.cpu!r}, ram={self.ram!r})'

class traffic_metric(Base):
    __tablename__ = "traffic"
    __table_args__ = {"schema":"metrics"}

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    container_id: Mapped[int] =                         mapped_column(ForeignKey("servers.container.id"), nullable=False)
    time_id: Mapped[int] =                              mapped_column(ForeignKey("metrics.timestamp.id"), nullable=False)
    up: Mapped[Float] =                                 mapped_column(Float(precision=4), nullable=False)
    down: Mapped[Float] =                               mapped_column(Float(precision=4), nullable=False)

    time =                                              relationship("metric_timestamp", foreign_keys=[time_id])
    container =                                         relationship(Container, foreign_keys=[container_id])

    def __repr__(self) -> str:
        return f'traffic_metric(id={self.id!r}, time_id={self.time_id!r}, up={self.up!r}, down={self.down!r})'
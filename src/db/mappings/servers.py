from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .metadata import server_metric_meta_data

class Base(DeclarativeBase):
    metadata = server_metric_meta_data

class container(Base):
    __tablename__ = "container"
    __table_args__ = {"schema":"servers"}

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    name: Mapped[str] =                                 mapped_column(nullable=False)
    ram_limit: Mapped[Numeric] =                        mapped_column(Numeric(5, 2))
    cpu_limit: Mapped[int] =                            mapped_column()

class ports_mapping(Base):
    __tablename__ = "ports_mapping"
    __table_args__ = {"schema":"servers"}

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    server_id: Mapped["container"] =                    mapped_column(ForeignKey("servers.container.id"), nullable=False)
    ports_open: Mapped[bool] =                          mapped_column(nullable=False, default=False)
    strict_ports: Mapped[bool] =                        mapped_column(nullable=False, default=False)
    do_port_forward: Mapped[bool] =                     mapped_column(nullable=False, default=False)    
    success_port: Mapped[bool] =                        mapped_column()

class ports(Base):
    __tablename__ = "ports"
    __table_args__ = {"schema":"servers"}

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    mapping_id: Mapped["ports_mapping"] =               mapped_column(ForeignKey("servers.ports_mapping.id"), nullable=False)
    container_port: Mapped[int] =                       mapped_column(nullable=False)
    host_port: Mapped[int] =                            mapped_column(nullable=False, unique=True)
    type_id: Mapped[int] =                              mapped_column(ForeignKey("servers.port_types.id"), nullable=False)
    
    def __repr__(self) -> str:
        return f'performance_metric(id={self.id!r}, time_id={self.time_id!r}, cpu={self.cpu!r}, ram={self.ram!r})'

class port_type(Base):
    __tablename__ = "port_types"
    __table_args__ = {"schema":"servers"}

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    type: Mapped[str] =                                 mapped_column(nullable=False)
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .metadata import server_metric_meta_data

class Base(DeclarativeBase):
    metadata = server_metric_meta_data

class launch_opts_mapping(Base):
    __tablename__ = "launch_opts_mapping"
    __table_args__ = {"schema":"servers"}

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    name: Mapped[str] =                                 mapped_column(nullable=False)
    var_flag: Mapped[str] =                             mapped_column(nullable=False)
    path: Mapped[str] =                                 mapped_column(nullable=False, default="")
    change_var: Mapped[str] =                           mapped_column(nullable=False, default="")
    container_id: Mapped[int] =                         mapped_column(ForeignKey("servers.container.id"), nullable=False)
    handling: Mapped[int] =                             mapped_column(nullable=False)
    source: Mapped[int] =                               mapped_column(nullable=False)

    def __repr__(self):
        return f"launch_opts_mapping(id={self.id}, name={self.name}, path={self.path}, change_var={self.change_var}, container_id={self.container_id}, handling={self.handling}, source={self.source})"

class launch_opts(Base):
    __tablename__ = "launch_opts"
    __table_args__ = {"schema":"servers"}

    id: Mapped[int] =                                   mapped_column(primary_key=True)
    mapping_id: Mapped[int] =                           mapped_column(ForeignKey("servers.launch_opts_mapping.id"), nullable=False)
    name: Mapped[str] =                                 mapped_column(nullable=False, default="")
    value: Mapped[str] =                                mapped_column(nullable=False, default="")
    path: Mapped[str] =                                 mapped_column(nullable=False, default="")

    def __repr__(self):
        return f"launch_opt(id={self.id}, mapping_id={self.mapping_id}, name={self.name}, value={self.value}, path={self.path})"
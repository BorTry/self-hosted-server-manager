from sqlalchemy import Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class servers_view(Base):
    __tablename__ = "servers"

    name: Mapped[str] =                                 mapped_column(primary_key=True)
    steam_server_id: Mapped[int] =                      mapped_column(nullable=True)
    cpu_limit: Mapped[Float] =                          mapped_column(Float(precision=4), nullable=False)
    ram_limit: Mapped[Float] =                          mapped_column(Float(precision=4), nullable=False)
    host_port: Mapped[int] =                            mapped_column(nullable=True)
    container_port: Mapped[int] =                       mapped_column(nullable=True)
    type: Mapped[str] =                                 mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f'servers_view(name={self.name!r}, steam_server_id={self.steam_server_id!r} cpu_limit={self.cpu_limit!r} ram_limit={self.ram_limit!r} host_port={self.host_port!r} container_port={self.container_port!r} type={self.type!r}'
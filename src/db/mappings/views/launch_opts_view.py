from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class launch_opts_view(Base):
    __tablename__ = "launch_opts"

    lo_name: Mapped[str] =                              mapped_column(primary_key=True)
    s_name: Mapped[str] =                               mapped_column(nullable=False)
    lom_name: Mapped[str] =                             mapped_column(nullable=False)
    handling: Mapped[int] =                             mapped_column(nullable=False)
    value: Mapped[str] =                                mapped_column(nullable=True)
    source: Mapped[int] =                               mapped_column(nullable=True)
    path: Mapped[str] =                                 mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f'launch_opts_view(lo_name={self.lo_name!r}, s_name={self.s_name!r} lom_name={self.lom_name!r} handling={self.handling!r} value={self.value!r} source={self.source!r} path={self.path!r})'
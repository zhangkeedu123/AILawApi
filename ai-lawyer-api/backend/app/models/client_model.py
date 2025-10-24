from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    type: Mapped[str | None] = mapped_column(String(50), default="个人")
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(200))
    cases: Mapped[int] = mapped_column(Integer, default=0)
    contracts: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str | None] = mapped_column(String(50), default="active")

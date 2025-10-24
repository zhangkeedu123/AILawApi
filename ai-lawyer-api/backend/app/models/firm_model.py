from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class Firm(Base):
    __tablename__ = "firms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    contact: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(300))
    city: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str | None] = mapped_column(String(50), default="active")
    employees: Mapped[int] = mapped_column(Integer, default=0)
    package: Mapped[str | None] = mapped_column(String(100))

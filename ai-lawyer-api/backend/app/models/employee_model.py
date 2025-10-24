from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    title: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(200))
    firm_name: Mapped[str | None] = mapped_column(String(200))  # 简化：用名称关联
    status: Mapped[str | None] = mapped_column(String(50), default="active")

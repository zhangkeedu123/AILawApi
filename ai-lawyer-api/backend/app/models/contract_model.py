from sqlalchemy import String, Integer, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer: Mapped[str] = mapped_column(String(200), index=True)
    contractName: Mapped[str] = mapped_column(String(200))
    uploadDate: Mapped[str | None] = mapped_column(String(50))  # 用字符串保存日期字符串，如需严格可改 Date
    amount: Mapped[int | None] = mapped_column(Integer)
    type: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str | None] = mapped_column(String(100))

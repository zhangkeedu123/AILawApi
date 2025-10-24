from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    caseName: Mapped[str | None] = mapped_column(String(200))
    docName: Mapped[str] = mapped_column(String(200))
    docType: Mapped[str | None] = mapped_column(String(100))
    createDate: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str | None] = mapped_column(String(50), default="草稿")

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.infrastructure.database import Base


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_path = Column(String, nullable=False, unique=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())


class DocumentTextModel(Base):
    __tablename__ = "document_text"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    extracted_text = Column(Text, nullable=False)
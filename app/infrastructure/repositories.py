from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, delete
import os

from app.domain.entities import Document, DocumentText, HealthStatus
from app.application.interfaces import IDocumentRepository, IHealthCheckRepository
from app.infrastructure.models import DocumentModel, DocumentTextModel


class PostgresDocumentRepository(IDocumentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_document(self, file_path: str) -> Document:
        document = DocumentModel(file_path=file_path)
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return Document(
            id=document.id,
            file_path=document.file_path,
            upload_date=document.upload_date
        )

    async def get_document(self, document_id: int) -> Document | None:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == document_id)
        )
        document = result.scalar_one_or_none()
        if document:
            return Document(
                id=document.id,
                file_path=document.file_path,
                upload_date=document.upload_date
            )
        return None

    async def save_extracted_text(self, document_id: int, text: str) -> DocumentText:
        doc_text = DocumentTextModel(document_id=document_id, extracted_text=text)
        self.session.add(doc_text)
        await self.session.commit()
        await self.session.refresh(doc_text)
        return DocumentText(
            id=doc_text.id,
            document_id=doc_text.document_id,
            extracted_text=doc_text.extracted_text
        )

    async def get_text_by_document(self, document_id: int) -> DocumentText | None:
        result = await self.session.execute(
            select(DocumentTextModel).where(DocumentTextModel.document_id == document_id)
        )
        doc_text = result.scalar_one_or_none()
        if doc_text:
            return DocumentText(
                id=doc_text.id,
                document_id=doc_text.document_id,
                extracted_text=doc_text.extracted_text
            )
        return None

    async def delete_document(self, document_id: int) -> bool:
        document = await self.get_document(document_id)
        if not document:
            return False

        await self.session.execute(
            delete(DocumentTextModel).where(DocumentTextModel.document_id == document_id)
        )

        await self.session.execute(
            delete(DocumentModel).where(DocumentModel.id == document_id)
        )
        await self.session.commit()

        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            return True
        except OSError:
            return False


class PostgresHealthCheckRepository(IHealthCheckRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_status(self) -> list[HealthStatus]:
        try:
            await self.session.execute(text("SELECT 1"))
            await self.session.commit()

        except Exception as e:
            await self.session.rollback()
            return [
                HealthStatus(
                    service="Database",
                    status="Error",
                    details=str(e))
            ]
        else:
            return [
                HealthStatus(
                    service="Database",
                    status="OK",
                    details="PostgreSQL connection is active"
                )
            ]
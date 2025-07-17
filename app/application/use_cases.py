from fastapi import UploadFile
from datetime import datetime
from pathlib import Path
import base64
import os
import shutil

from app.domain.entities import HealthStatus, Document, DocumentText
from app.application.interfaces import IHealthCheckRepository, IDocumentRepository, IAsyncWorker
from app.infrastructure.services import RabbitMQHealthCheck, TesseractHealthCheck

BASE_DIR = Path(__file__).resolve().parent.parent

class HealthCheckUseCase:
    def __init__(self, health_repo: IHealthCheckRepository):
        self.health_repo = health_repo

    async def execute(self) -> list[HealthStatus]:
        base_statuses = [
            HealthStatus(
                service="API",
                status="OK",
                details="Service is running"
            ),
            RabbitMQHealthCheck.check(),
            TesseractHealthCheck.check(),
        ]

        db_statuses = await self.health_repo.get_status()
        return base_statuses + db_statuses


class GetDocumentTextUseCase:
    def __init__(self, document_repo: IDocumentRepository):
        self.document_repo = document_repo

    async def execute(self, document_id: int) -> DocumentText:
        doc_text = await self.document_repo.get_text_by_document(document_id)

        if not doc_text:
            raise ValueError(f"Text not found for document {document_id}")

        return doc_text


class DocumentUploadUseCase:
    def __init__(self, document_repo: IDocumentRepository):
        self.document_repo = document_repo
        self.upload_dir = BASE_DIR / "documents"
        self.upload_dir.mkdir(exist_ok=True)

    async def execute(self, file_name: str, file_content: str) -> Document:
        file_data = base64.b64decode(file_content)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_name = f"{timestamp}_{file_name}"
        file_path = self.upload_dir / unique_name

        with open(file_path, "wb") as f:
            f.write(file_data)

        return await self.document_repo.save_document(str(file_path))


class DocumentUploadSwaggerUseCase:
    def __init__(self, document_repo: IDocumentRepository):
        self.document_repo = document_repo
        self.upload_dir = BASE_DIR / "documents"
        self.upload_dir.mkdir(exist_ok=True)

    async def execute(self, file: UploadFile) -> Document:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_name = f"{timestamp}_{file.filename}"
        file_path = self.upload_dir / unique_name

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return await self.document_repo.save_document(str(file_path))


class DocumentDeleteUseCase:
    def __init__(self, document_repo: IDocumentRepository):
        self.document_repo = document_repo

    async def execute(self, document_id: int) -> bool:
        return await self.document_repo.delete_document(document_id)


class DocumentAnalyzeUseCase:
    def __init__(self, async_worker: IAsyncWorker, document_repo: IDocumentRepository):
        self.async_worker = async_worker
        self.document_repo = document_repo

    async def execute(self, document_id: int) -> str:
        document = await self.document_repo.get_document(document_id)
        if not document:
            raise ValueError("Document not found")

        task_id = await self.async_worker.analyze_document(document_id)
        return task_id
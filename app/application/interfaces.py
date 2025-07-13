from abc import ABC, abstractmethod
from typing import Optional, List

from app.domain.entities import HealthStatus, Document, DocumentText


class IHealthCheckRepository(ABC):
    @abstractmethod
    async def get_status(self) -> list[HealthStatus]:
        pass


class IDocumentRepository(ABC):
    @abstractmethod
    async def save_document(self, file_path: str) -> Document:
        pass

    @abstractmethod
    async def get_document(self, document_id: int) -> Optional[Document]:
        pass

    @abstractmethod
    async def save_extracted_text(self, document_id: int, text: str) -> DocumentText:
        pass

    @abstractmethod
    async def get_text_by_document(self, document_id: int) -> Optional[DocumentText]:
        pass

    @abstractmethod
    async def delete_document(self, document_id: int) -> bool:
        pass

class IAsyncWorker(ABC):
    @abstractmethod
    async def analyze_document(self, document_id: int) -> str:
        pass
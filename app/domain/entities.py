from datetime import datetime
from dataclasses import dataclass

@dataclass
class HealthStatus:
    service: str
    status: str
    details: str = ""

@dataclass
class Document:
    id: int
    file_path: str
    upload_date: datetime

@dataclass
class DocumentText:
    id: int
    document_id: int
    extracted_text: str
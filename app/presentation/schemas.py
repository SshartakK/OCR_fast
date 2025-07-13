from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class HealthStatusResponse(BaseModel):
    service: str
    status: str
    details: str

class HealthCheckResponse(BaseModel):
    status: str
    services: list[HealthStatusResponse]

class DocumentUploadRequest(BaseModel):
    file_name: str
    file_content: str

class DocumentResponse(BaseModel):
    id: int
    file_path: str
    upload_date: datetime

class DocumentTextResponse(BaseModel):
    id: int
    document_id: int
    extracted_text: str

class DocumentUploadSwaggerResponse(BaseModel):
    message: str
    document_id: int
    file_path: str
    upload_date: datetime

class DocumentDeleteResponse(BaseModel):
    success: bool
    message: str
    document_id: int

class DocumentAnalyzeResponse(BaseModel):
    status: str
    task_id: str
    document_id: int
    message: str

class DocumentTextResponse(BaseModel):
    document_id: int
    extracted_text: str
    status: str = "success"

class DocumentTextNotFoundResponse(BaseModel):
    document_id: int
    status: str = "error"
    message: str = "Text not found for this document"
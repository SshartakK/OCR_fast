from typing import Union
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import base64
from starlette.responses import JSONResponse

from app.application.use_cases import HealthCheckUseCase, DocumentUploadUseCase, DocumentUploadSwaggerUseCase, \
    DocumentDeleteUseCase, DocumentAnalyzeUseCase, GetDocumentTextUseCase
from app.infrastructure.repositories import PostgresHealthCheckRepository, PostgresDocumentRepository
from app.infrastructure.database import get_db
from app.infrastructure.services import CeleryWorkerService
from app.presentation.schemas import HealthCheckResponse, HealthStatusResponse, DocumentResponse, \
    DocumentUploadSwaggerResponse, DocumentDeleteResponse, DocumentAnalyzeResponse, DocumentTextResponse, \
    DocumentTextNotFoundResponse

router = APIRouter(prefix="/api/v1", tags=["Health Check"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        repo = PostgresHealthCheckRepository(db)
        use_case = HealthCheckUseCase(repo)
        statuses = await use_case.execute()

    except Exception as e:
        return {
            "status": "Error",
            "services": [
                {
                    "service": "Database",
                    "status": "Error",
                    "details": str(e)
                }
            ]
        }

    else:
        overall_status = "OK"
        for status in statuses:
            if status.status != "OK":
                overall_status = "Degraded"
                break
        return {
            "status": overall_status,
            "services": [
                {
                    "service": status.service,
                    "status": status.status,
                    "details": status.details
                }
                for status in statuses
            ]
        }


@router.post("/upload_doc", response_model=DocumentResponse)
async def upload_document(file_name: str = Form(...), file_content: str = Form(...), db: AsyncSession = Depends(get_db)):
    try:
        repo = PostgresDocumentRepository(db)
        use_case = DocumentUploadUseCase(repo)
        document = await use_case.execute(file_name, file_content)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading document: {str(e)}"
        )

    else:
        return {
            "id": document.id,
            "file_path": document.file_path,
            "upload_date": document.upload_date
        }


@router.post("/upload_doc_swagger", response_model=DocumentUploadSwaggerResponse, status_code=status.HTTP_201_CREATED,
             summary="Upload document via Swagger UI", description="Uploads a document file through Swagger UI interface and saves to database")
async def upload_document_swagger(file: UploadFile = File(..., description="Document file to upload"), db: AsyncSession = Depends(get_db)):
    try:
        allowed_types = ["image/jpeg", "image/png", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
            )

        repo = PostgresDocumentRepository(db)
        use_case = DocumentUploadSwaggerUseCase(repo)
        document = await use_case.execute(file)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )
    else:
        return {
            "message": "File uploaded successfully",
            "document_id": document.id,
            "file_path": document.file_path,
            "upload_date": document.upload_date
        }
    finally:
        await file.close()


@router.delete("/doc_delete/{document_id}", response_model=DocumentDeleteResponse, summary="Delete document", description="Deletes document from database and filesystem")
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    repo = PostgresDocumentRepository(db)
    use_case = DocumentDeleteUseCase(repo)
    success = await use_case.execute(document_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found or could not be deleted"
        )

    return {
        "success": True,
        "message": "Document deleted successfully",
        "document_id": document_id
    }


@router.post("/doc_analyse/{document_id}", response_model=DocumentAnalyzeResponse, summary="Analyze document", description="Starts background text recognition for document")
async def analyze_document(document_id: int, db: AsyncSession = Depends(get_db), worker: CeleryWorkerService = Depends()):
    try:
        repo = PostgresDocumentRepository(db)
        use_case = DocumentAnalyzeUseCase(worker, repo)
        task_id = await use_case.execute(document_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting analysis: {str(e)}"
        )

    else:
        return {
            "status": "started",
            "task_id": task_id,
            "document_id": document_id,
            "message": "Document analysis started in background"
        }


@router.get("/get_text/{document_id}", response_model=Union[DocumentTextResponse, DocumentTextNotFoundResponse], summary="Get extracted text", description="Returns OCR extracted text for specified document")
async def get_document_text(document_id: int, db: AsyncSession = Depends(get_db)):
    try:
        repo = PostgresDocumentRepository(db)
        use_case = GetDocumentTextUseCase(repo)
        doc_text = await use_case.execute(document_id)

    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "document_id": document_id,
                "status": "error",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document text: {str(e)}"
        )
    else:
        return {
            "document_id": doc_text.document_id,
            "extracted_text": doc_text.extracted_text
        }
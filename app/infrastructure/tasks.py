import pytesseract
from PIL import Image
import os

from app.infrastructure.celery import celery_app
from app.infrastructure.database import SyncSession
from app.infrastructure.models import DocumentTextModel, DocumentModel
from app.core.config import settings

pytesseract.pytesseract.tesseract_cmd = settings.tesseract_path


@celery_app.task(bind=True, name="process_document")
def process_document_task(self, document_id: int):
    with SyncSession() as session:
        document = session.query(DocumentModel).filter_by(id=document_id).first()
        if not document:
            raise ValueError(f"Document with id {document_id} not found")

        if not os.path.exists(document.file_path):
            raise FileNotFoundError(f"File not found at {document.file_path}")

        try:
            text = extract_text_from_image(document.file_path)

            doc_text = DocumentTextModel(
                document_id=document.id,
                extracted_text=text)
        except Exception as e:
            session.rollback()
            raise

        else:
            session.add(doc_text)
            session.commit()

            return {
                "status": "success",
                "document_id": document_id,
                "text_length": len(text)
            }

def extract_text_from_image(file_path: str) -> str:
    try:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img)
    except Exception as e:
        raise RuntimeError(f"OCR processing failed: {str(e)}")
import pika
from celery.result import AsyncResult
import pytesseract
from pika import ConnectionParameters, BlockingConnection

from app.application.interfaces import IAsyncWorker
from app.infrastructure.celery import celery_app
from app.infrastructure.tasks import process_document_task
from app.core.config import settings
from app.domain.entities import HealthStatus


class CeleryWorkerService(IAsyncWorker):
    async def analyze_document(self, document_id: int) -> str:
        task = process_document_task.apply_async(args=[document_id])
        return task.id

    async def get_task_status(self, task_id: str) -> dict:
        task_result = AsyncResult(task_id, app=celery_app)
        return {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result
        }


class RabbitMQHealthCheck:
    @staticmethod
    def check() -> HealthStatus:
        try:
            connection = BlockingConnection(
                ConnectionParameters(
                    host='rabbitmq',
                    port=5672,
                    virtual_host='/',
                    credentials=pika.PlainCredentials('user', 'password'))
            )
            connection.close()
        except Exception as e:
            return HealthStatus(
                service="Message Broker",
                status="Error",
                details=f"RabbitMQ connection failed: {str(e)}"
            )
        else:
            return HealthStatus(
                service="Message Broker",
                status="OK",
                details="RabbitMQ connection is active"
            )


class TesseractHealthCheck:
    @staticmethod
    def check() -> HealthStatus:
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            return HealthStatus(
                service="OCR Engine",
                status="Error",
                details=f"Tesseract check failed: {str(e)}"
            )
        else:
            return HealthStatus(
                service="OCR Engine",
                status="OK",
                details=f"Tesseract {pytesseract.get_tesseract_version()} is available"
            )
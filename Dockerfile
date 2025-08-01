FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/* \

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY alembic.ini ./
COPY ./alembic ./alembic
COPY .env ./

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

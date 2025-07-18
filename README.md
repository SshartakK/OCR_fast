# OCR_fast

## Описание

OCR_fast — это сервис для загрузки, хранения и анализа документов с помощью OCR (распознавания текста на изображениях). Проект поддерживает асинхронную обработку файлов через Celery и RabbitMQ, хранение результатов в PostgreSQL, а также автоматические миграции базы данных при запуске.

### Основной функционал
- Загрузка изображений и документов через API
- Асинхронное распознавание текста (OCR) с помощью Celery worker
- Хранение документов и результатов анализа в базе данных PostgreSQL
- Мониторинг состояния сервисов (БД, RabbitMQ, OCR)
- Панель управления RabbitMQ по адресу http://localhost:15673

---

## Быстрый старт через Docker

### 1. Клонируйте репозиторий и перейдите в папку проекта
```bash
cd OCR_fast
```

### 2. Постройте и запустите контейнеры
```bash
docker-compose up --build
```

### 3. Сервисы
- **API:** http://localhost:8000 (Swagger UI: http://localhost:8000/docs)
- **PostgreSQL:** localhost:5433 (user: artem, password: root, db: artemfastdb)
- **RabbitMQ:** amqp://user:password@localhost:5673/ (web-панель: http://localhost:15673)

### 4. Остановка
```bash
docker-compose down
```

---

## Структура docker-compose
- **web** — FastAPI-приложение, автоматически применяет миграции Alembic при запуске
- **worker** — Celery worker для асинхронной обработки документов
- **db** — PostgreSQL
- **rabbitmq** — брокер сообщений

> Папка `app/documents` шарится между web и worker, чтобы оба сервиса имели доступ к загруженным файлам

---

## Пример .env (настройки по умолчанию)
```
POSTGRES_USER=artem
POSTGRES_PASSWORD=root
POSTGRES_DB=artemfastdb
POSTGRES_HOST=db
POSTGRES_PORT=5432
CELERY_BROKER_URL=amqp://user:password@rabbitmq:5672//
```

---

## Миграции
Миграции применяются автоматически при запуске web-сервиса. Для ручного запуска:
```bash
docker-compose exec web alembic upgrade head
```

---

## Дополнительно
- Для работы OCR требуется установленный пакет tesseract (он уже добавлен в Dockerfile)
- Для доступа к RabbitMQ web-панели используйте user/password
- Для доступа к БД используйте параметры из .env или docker-compose

---

## Лицензия
MIT
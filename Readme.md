# Запуск проекта

**Сервис для загрузки, сканирования и управления файлами** с асинхронной обработкой через Celery, валидацией по байтовым сигнатурам и структурированным логированием в JSON.

Ключевые возможности:
- Загрузка файлов с проверкой MIME-типа и расширения (Magic Bytes)
- Асинхронное сканирование на угрозы (с расширениями и размером)
- Извлечение метаданных (количество строк, символов, страниц)
- Генерация алертов по результатам обработки
- REST API с полной OpenAPI-документацией

## Требования
- Python 3.12+
- Docker и Docker Compose (опционально)
- PostgreSQL и Redis (можно запустить через Docker)
- Пакеты: `fastapi`, `celery`, `sqlalchemy`, `structlog`, `filetype`, `psycopg2-binary`

## Установка зависимостей

```bash
cd backend
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
```

## Настройка окружения

Конфигурация проекта содержится в файле `.env.dev` (используется по умолчанию в `docker-compose.dev.yml`).

Если запускаете сервис локально без Docker, создайте его копию под именем `.env`:

```bash
cp .env.dev .env
```
Пример содержимого .env.dev

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=test
POSTGRES_HOST=localhost  # или backend-db при использовании Docker
PGPORT=5433
REDIS_URL=redis://localhost:6379/0
```

## Запуск с Docker (рекомендуется)

```bash
docker-compose -f docker-compose.dev.yml up -d
```

После запуска cервисы доступны по адресам:
- Бэкенд: http://localhost:8000
- Документация API: http://localhost:8000/docs
- Фронтенд: http://localhost:3000

## Локальный запуск (без Docker)

1. Запустите PostgreSQL и Redis вручную.
2. Примените миграции (если есть):
   ```bash
   alembic upgrade head
   ```
3. Запустите Uvicorn:
   ```bash
   uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
   ```
4. В отдельном терминале запустите Celery worker:
   ```bash
   celery -A src.tasks.celery_app worker -l info
   ```

## Запуск тестов

```bash
pytest --cov=src -v
```

Для запуска с покрытием и генерацией отчёта в XML:
```bash
pytest --cov=src --cov-report=xml
```

## Проверка качества кода

```bash
bandit -r src -ll
skylos src
```

## CI/CD (GitHub Actions)

При каждом push и pull-request автоматически запускаются:
- `bandit` (безопасность)
- `skylos` (чистота кода)
- `pytest --cov=src` (тесты с покрытием)

Файл конфигурации: `.github/workflows/ci.yml`

## Переменные окружения для тестов

Тесты используют тестовую БД, задаваемую через переменные:
```bash
export POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres POSTGRES_DB=test POSTGRES_HOST=localhost PGPORT=5433
```
Если БД запущена в Docker, укажите `POSTGRES_HOST=localhost` (или `127.0.0.1`).
Для Redis в тестах используется `REDIS_URL=redis://localhost:6379/0`.
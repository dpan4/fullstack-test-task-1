# Запуск проекта

## Требования
- Python 3.12+
- Docker и Docker Compose (опционально)
- PostgreSQL и Redis (можно запустить через Docker)

## Установка зависимостей

```bash
cd backend
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
```

## Настройка окружения

Создайте файл `.env` в корне проекта со следующими переменными:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=test
POSTGRES_HOST=localhost  # или backend-db при использовании Docker
PGPORT=5432
REDIS_URL=redis://localhost:6379/0
```

## Запуск с Docker (рекомендуется)

```bash
docker-compose -f docker-compose.dev.yml up -d
```

После запуска:
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

## Переменные окружения для тестов

Тесты используют тестовую БД, задаваемую через переменные:
```bash
export POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres POSTGRES_DB=test POSTGRES_HOST=localhost PGPORT=5432
```
Если БД запущена в Docker, укажите `POSTGRES_HOST=localhost` (или `127.0.0.1`).
Для Redis в тестах используется `REDIS_URL=redis://localhost:6379/0`.
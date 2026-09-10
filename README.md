# Запуск проекта

**Сервис для загрузки, сканирования и управления файлами** с асинхронной обработкой через Celery, валидацией по байтовым сигнатурам и структурированным логированием в JSON.

Ключевые возможности:
- Загрузка файлов с проверкой MIME-типа и расширения (Magic Bytes)
- Асинхронное сканирование на угрозы (с расширениями и размером)
- Извлечение метаданных (количество строк, символов, страниц)
- Генерация алертов по результатам обработки
- REST API с полной OpenAPI-документацией

## 1. Клонирование репозитория

```bash
git clone https://github.com/dpan4/fullstack-test-task-1/
cd fullstack-test-task
```

## 2. Настройка окружения

Конфигурация проекта содержится в файле `.env.dev` (используется по умолчанию в `docker-compose.dev.yml`).

Для локального запуска без Docker создайте копию `.env.dev` как `.env`:

```bash
cp .env.dev .env
```

Пример содержимого `.env.dev` (или `.env`):

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=test
POSTGRES_HOST=localhost      # или backend-db при использовании Docker
PGPORT=5433
REDIS_URL=redis://localhost:6379/0
```

## 3. Запуск

### Вариант А: Docker Compose (рекомендуется)

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

После запуска сервисы доступны по адресам:
- Бэкенд: http://localhost:8000
- Документация API: http://localhost:8000/docs
- Фронтенд: http://localhost:3000

### Вариант Б: Локальный запуск (без Docker)

**Бэкенд:**

```bash
cd backend
python -m venv venv
source venv/bin/activate          # или venv\Scripts\activate на Windows
pip install -r requirements.txt
```

Примените миграции (если есть):

```bash
alembic upgrade head
```

Запустите Uvicorn:

```bash
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

В отдельном терминале запустите Celery worker:

```bash
celery -A src.tasks.celery_app worker -l info
```

**Фронтенд:**

```bash
cd frontend
npm install
npm run dev
```

Фронтенд будет доступен по адресу http://localhost:3000.

## 4. Тестирование и статический анализ

### Автозапуск через `run_tests.sh`

В репозитории есть скрипт `run_tests.sh`, который сам подтягивает переменные окружения из `.env.dev`/`.env`, активирует `venv` (ищет `venv_new` или `venv`), выставляет дефолтные значения для подключения к БД и запускает `pytest --cov=src -v`.

Перед первым запуском выдайте скрипту право на исполнение:

```bash
chmod +x backend/run_tests.sh
```

Запуск из корня проекта:

```bash
./backend/run_tests.sh
```

Запуск из директории `backend`:

```bash
./run_tests.sh
```

Любые дополнительные флаги `pytest` пробрасываются в скрипт как аргументы, например:

```bash
./run_tests.sh -x -k test_upload
./run_tests.sh --cov-report=xml
```

Скрипт сам подтягивает окружение (переменные `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `PGPORT`, `PGSSLMODE`, `REDIS_URL`) и активирует виртуальное окружение — вручную ничего экспортировать не нужно.

### Ручной запуск

Прогон тестов с покрытием:

```bash
pytest --cov=src -v
```

Для генерации отчёта в XML:

```bash
pytest --cov=src --cov-report=xml
```

Проверка безопасности:

```bash
bandit -r src -ll
```

Проверка качества кода:

```bash
skylos src
```

## 5. CI/CD

В репозитории настроен GitHub Actions (`.github/workflows/ci.yml`). При каждом push и pull-request автоматически запускаются:
- `bandit` (безопасность)
- `skylos` (чистота кода)
- `pytest --cov=src` (тесты с покрытием)

## Переменные окружения для тестов

Тесты используют тестовую БД, задаваемую через переменные:

```bash
export POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres POSTGRES_DB=test POSTGRES_HOST=localhost PGPORT=5433
```

Если БД запущена в Docker, укажите `POSTGRES_HOST=localhost` (или `127.0.0.1`).
Для Redis в тестах используется `REDIS_URL=redis://localhost:6379/0`.

#!/bin/bash
set -e

# Переходим в директорию backend, если скрипт запущен из корня проекта
if [ -d "backend" ]; then
    cd backend
fi

# Подтягиваем переменные из .env.dev или .env
if [ -f ".env.dev" ]; then
    set -a
    source .env.dev
    set +a
elif [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Дефолтные переменные для подключения к БД (если их нет в .env)
export POSTGRES_USER="${POSTGRES_USER:-postgres}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
export POSTGRES_DB="${POSTGRES_DB:-test}"
export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
export PGPORT="${PGPORT:-5433}"
export PGSSLMODE="${PGSSLMODE:-disable}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export PYTHONPATH=".:$PYTHONPATH"

# Поиск и активация venv
if [ -d "venv_new" ]; then
    source venv_new/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv_new" ]; then
    source ../venv_new/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
else
    echo "Ошибка: виртуальное окружение не найдено!"
    exit 1
fi

echo "🚀 Запуск pytest (БД: $POSTGRES_HOST:$PGPORT/$POSTGRES_DB, Юзер: $POSTGRES_USER)"
pytest --cov=src -v "$@"
#!/bin/bash
set -e

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

if [ -d "venv_new" ]; then
    source venv_new/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Виртуальное окружение не найдено!"
    exit 1
fi

pytest --cov=src -v "$@"

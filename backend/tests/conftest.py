import os
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("PGPORT", "5433")

import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from src.models import Base
from src.service import DB_URL, engine

# Celery eager mode for tests
@pytest.fixture(autouse=True)
def setup_celery_eager():
    from src.tasks import celery_app
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True
    )
    yield

# Создание таблиц один раз для всей сессии тестов
@pytest.fixture(scope="session", autouse=True)
async def create_tables():
    # Используем временный движок для создания таблиц
    temp_engine = create_async_engine(DB_URL, poolclass=NullPool, connect_args={"ssl": False})
    async with temp_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await temp_engine.dispose()
    yield
    # После всех тестов можно у��алить таблицы (опционально)
    # Но для простоты оставим

# Сброс движка после каждого теста
@pytest.fixture(autouse=True)
async def cleanup_db_engine():
    yield
    await engine.dispose()
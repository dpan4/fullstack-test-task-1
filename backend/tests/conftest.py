import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.models import Base
from src.service import DB_URL
from unittest.mock import patch

@pytest.fixture(scope="function")
async def engine():
    engine = create_async_engine(DB_URL, pool_size=5, max_overflow=10, pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()
        await session.close()

# Мок для Celery задач — все задачи выполняются синхронно
@pytest.fixture(autouse=True)
def mock_celery():
    from src.tasks import scan_file_for_threats, extract_file_metadata, send_file_alert
    with patch("src.tasks.scan_file_for_threats.delay", side_effect=lambda file_id: scan_file_for_threats(file_id)), \
         patch("src.tasks.extract_file_metadata.delay", side_effect=lambda file_id: extract_file_metadata(file_id)), \
         patch("src.tasks.send_file_alert.delay", side_effect=lambda file_id: send_file_alert(file_id)):
        yield
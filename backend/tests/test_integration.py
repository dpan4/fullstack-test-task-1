import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, delete
from src.app import app
from src.service import STORAGE_DIR
from src.models import StoredFile, Alert
from src.service import async_session_maker
from sqlalchemy import select
from pathlib import Path


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
async def cleanup_db():
    yield
    async with async_session_maker() as session:
        await session.execute(delete(Alert))
        await session.execute(delete(StoredFile))
        await session.commit()
    for file in STORAGE_DIR.glob("*"):
        if file.is_file():
            file.unlink()


async def wait_for_processing(async_client: AsyncClient, file_id: str, timeout: int = 10):
    for _ in range(timeout):
        response = await async_client.get(f"/files/{file_id}")
        if response.status_code == 200:
            data = response.json()
            if data.get("processing_status") == "processed":
                return data
        await asyncio.sleep(1)
    response = await async_client.get(f"/files/{file_id}")
    return response.json()


class TestFileUpload:
    @pytest.mark.asyncio
    async def test_upload_file_returns_201_and_uploaded_status(self, async_client: AsyncClient):
        content = b"Test file content for upload"
        files = {"file": ("test.txt", content, "text/plain")}
        data = {"title": "Test Upload"}

        response = await async_client.post("/files", files=files, data=data)

        assert response.status_code == 201
        result = response.json()
        assert result["title"] == "Test Upload"
        assert result["original_name"] == "test.txt"
        assert result["processing_status"] == "uploaded"
        assert "id" in result
        assert result["size"] == len(content)


class TestThreatScanning:
    @pytest.mark.asyncio
    async def test_safe_file_txt_gets_clean_scan(self, async_client: AsyncClient):
        content = b"Safe text file content"
        files = {"file": ("document.txt", content, "text/plain")}
        data = {"title": "Safe Document"}

        response = await async_client.post("/files", files=files, data=data)
        assert response.status_code == 201
        file_id = response.json()["id"]

        file_data = await wait_for_processing(async_client, file_id)

        assert file_data["scan_status"] == "clean"
        assert file_data["requires_attention"] is False
        assert "no threats found" in file_data["scan_details"].lower()

    @pytest.mark.asyncio
    async def test_suspicious_file_exe_gets_suspicious_scan(self, async_client: AsyncClient):
        content = b"MZ fake exe content"
        files = {"file": ("malware.exe", content, "application/x-msdownload")}
        data = {"title": "Suspicious Executable"}

        response = await async_client.post("/files", files=files, data=data)
        assert response.status_code == 201
        file_id = response.json()["id"]

        file_data = await wait_for_processing(async_client, file_id)

        assert file_data["scan_status"] == "suspicious"
        assert file_data["requires_attention"] is True
        assert "suspicious extension" in file_data["scan_details"].lower()


class TestMetadataExtraction:
    @pytest.mark.asyncio
    async def test_text_file_metadata_contains_line_and_char_count(self, async_client: AsyncClient):
        content = b"Line 1\nLine 2\nLine 3\n"
        files = {"file": ("data.txt", content, "text/plain")}
        data = {"title": "Text File"}

        response = await async_client.post("/files", files=files, data=data)
        assert response.status_code == 201
        file_id = response.json()["id"]

        file_data = await wait_for_processing(async_client, file_id)

        metadata = file_data["metadata_json"]
        assert metadata is not None
        assert metadata["extension"] == ".txt"
        assert metadata["size_bytes"] == len(content)
        assert metadata["mime_type"] == "text/plain"
        assert metadata["line_count"] == 3
        assert metadata["char_count"] == len(content.decode("utf-8"))


class TestAlertGeneration:
    @pytest.mark.asyncio
    async def test_alert_created_after_file_processing(self, async_client: AsyncClient):
        content = b"Alert test content"
        files = {"file": ("alert.txt", content, "text/plain")}
        data = {"title": "Alert Test"}

        response = await async_client.post("/files", files=files, data=data)
        assert response.status_code == 201
        file_id = response.json()["id"]

        await wait_for_processing(async_client, file_id)

        alerts_response = await async_client.get("/alerts")
        assert alerts_response.status_code == 200
        alerts = alerts_response.json()

        file_alerts = [a for a in alerts if a["file_id"] == file_id]
        assert len(file_alerts) >= 1
        alert = file_alerts[0]
        assert alert["level"] in ("info", "warning", "critical")
        assert alert["message"]


class TestDownloadIntegrity:
    @pytest.mark.asyncio
    async def test_download_returns_identical_bytes(self, async_client: AsyncClient):
        original_content = b"Binary content for integrity check \x00\x01\x02\xff"
        files = {"file": ("binary.bin", original_content, "application/octet-stream")}
        data = {"title": "Binary File"}

        response = await async_client.post("/files", files=files, data=data)
        assert response.status_code == 201
        file_id = response.json()["id"]

        await wait_for_processing(async_client, file_id)

        download_response = await async_client.get(f"/files/{file_id}/download")
        assert download_response.status_code == 200
        assert download_response.content == original_content


class TestDeleteRegression:
    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="Known bug: DELETE returns 500 due to cascade delete issue")
    async def test_delete_file_returns_204(self, async_client: AsyncClient):
        content = b"File to delete"
        files = {"file": ("delete.txt", content, "text/plain")}
        data = {"title": "Delete Test"}

        response = await async_client.post("/files", files=files, data=data)
        assert response.status_code == 201
        file_id = response.json()["id"]

        delete_response = await async_client.delete(f"/files/{file_id}")
        assert delete_response.status_code == 204

        get_response = await async_client.get(f"/files/{file_id}")
        assert get_response.status_code == 404
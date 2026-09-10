from fastapi import FastAPI, HTTPException, Request
from fastapi import File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette import status
from src.schemas import AlertItem, FileItem, FileUpdate
from src.service import create_file, delete_file, get_file, list_alerts, list_files, update_file, STORAGE_DIR
from src.tasks import scan_file_for_threats
from src.logging import configure_structlog, set_request_id, get_logger
import uuid

configure_structlog()
logger = get_logger()

app = FastAPI()


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    set_request_id(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


@app.get("/files", response_model=list[FileItem])
async def list_files_view():
    return await list_files()


@app.get("/alerts", response_model=list[AlertItem])
async def list_alerts_view():
    return await list_alerts()


@app.post("/files", response_model=FileItem, status_code=201, openapi_extra={
    "requestBody": {
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "example": "My Document"},
                        "file": {"type": "string", "format": "binary"}
                    },
                    "required": ["title", "file"]
                },
                "examples": {
                    "text_file": {
                        "summary": "Upload a text file",
                        "value": {
                            "title": "Sample Text",
                            "file": "(binary data)"
                        }
                    },
                    "pdf_file": {
                        "summary": "Upload a PDF",
                        "value": {
                            "title": "Sample PDF",
                            "file": "(binary data)"
                        }
                    }
                }
            }
        }
    },
    "responses": {
        "201": {
            "description": "File created",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "My Document",
                        "original_name": "document.txt",
                        "mime_type": "text/plain",
                        "size": 1024,
                        "processing_status": "uploaded",
                        "scan_status": None,
                        "scan_details": None,
                        "metadata_json": None,
                        "requires_attention": False,
                        "created_at": "2026-09-10T12:00:00Z",
                        "updated_at": "2026-09-10T12:00:00Z"
                    }
                }
            }
        }
    }
})
async def create_file_view(
    title: str = Form(...),
    file: UploadFile = File(...),
):
    file_item = await create_file(title=title, upload_file=file)
    scan_file_for_threats.delay(file_item.id)
    return file_item


@app.get("/files/{file_id}", response_model=FileItem, openapi_extra={
    "parameters": [
        {
            "name": "file_id",
            "in": "path",
            "required": True,
            "schema": {"type": "string", "format": "uuid"},
            "example": "550e8400-e29b-41d4-a716-446655440000"
        }
    ],
    "responses": {
        "200": {
            "description": "File details",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "My Document",
                        "original_name": "document.txt",
                        "mime_type": "text/plain",
                        "size": 1024,
                        "processing_status": "processed",
                        "scan_status": "clean",
                        "scan_details": "no threats found",
                        "metadata_json": {"line_count": 10, "char_count": 100},
                        "requires_attention": False,
                        "created_at": "2026-09-10T12:00:00Z",
                        "updated_at": "2026-09-10T12:05:00Z"
                    }
                }
            }
        },
        "404": {
            "description": "File not found",
            "content": {
                "application/json": {
                    "example": {"detail": "File not found"}
                }
            }
        }
    }
})
async def get_file_view(file_id: str):
    return await get_file(file_id)


@app.patch("/files/{file_id}", response_model=FileItem)
async def update_file_view(
    file_id: str,
    payload: FileUpdate,
):
    return await update_file(file_id=file_id, title=payload.title)


@app.get("/files/{file_id}/download")
async def download_file(file_id: str):
    file_item = await get_file(file_id)
    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@app.delete("/files/{file_id}", status_code=204)
async def delete_file_view(file_id: str):
    await delete_file(file_id)

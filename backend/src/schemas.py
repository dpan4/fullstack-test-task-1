from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, ConfigDict, Field


class FileItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="UUID of the file", example="550e8400-e29b-41d4-a716-446655440000")
    title: str = Field(description="User-provided title", example="My Document")
    original_name: str = Field(description="Original filename", example="document.pdf")
    mime_type: str = Field(description="MIME type", example="application/pdf")
    size: int = Field(description="File size in bytes", example=1024)
    processing_status: str = Field(description="Processing status: uploaded, processing, processed, failed", example="processed")
    scan_status: Optional[str] = Field(None, description="Threat scan result: clean, suspicious, failed", example="clean")
    scan_details: Optional[str] = Field(None, description="Details about scan", example="no threats found")
    metadata_json: Optional[Dict[str, Any]] = Field(None, description="Extracted metadata (line count, page count, etc.)", example={"line_count": 10, "char_count": 100})
    requires_attention: bool = Field(description="Whether the file requires manual review", example=False)
    created_at: datetime = Field(description="Creation timestamp", example="2026-09-10T12:00:00Z")
    updated_at: datetime = Field(description="Last update timestamp", example="2026-09-10T12:05:00Z")


class FileUpdate(BaseModel):
    title: str = Field(description="New title for the file", example="Updated Document")


class AlertItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Alert ID", example=1)
    file_id: str = Field(description="Associated file UUID", example="550e8400-e29b-41d4-a716-446655440000")
    level: str = Field(description="Alert severity: info, warning, critical", example="warning")
    message: str = Field(description="Alert message", example="File requires attention: suspicious extension .exe")
    created_at: datetime = Field(description="Alert creation timestamp", example="2026-09-10T12:05:00Z")

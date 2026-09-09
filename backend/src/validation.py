import filetype
from fastapi import HTTPException, status
from pathlib import Path

ALLOWED_TYPES = {
    "image/jpeg": ["jpg", "jpeg"],
    "image/png": ["png"],
    "image/gif": ["gif"],
    "application/pdf": ["pdf"],
    "text/plain": ["txt"],
    "application/octet-stream": [],  # binary, allow any extension
    "application/x-msdownload": ["exe"],  # executable files
}

def validate_file_magic(content: bytes, filename: str, mime_type: str) -> None:
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    if mime_type == "application/octet-stream":
        return  # skip validation for binary
    kind = filetype.guess(content)
    if kind is None:
        # Unknown file type: allow if mime_type is text/* and decodes, otherwise accept (no magic known)
        if mime_type.startswith("text/"):
            try:
                content.decode("utf-8")
                return
            except UnicodeDecodeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File content does not match text mime type")
        # For non-text unknown types, accept (e.g. .exe, .bin)
        return
    if kind.mime != mime_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"MIME type mismatch: expected {mime_type}, got {kind.mime}")
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext and ext not in ALLOWED_TYPES.get(mime_type, []):
        # allow any extension for octet-stream
        if mime_type != "application/octet-stream":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Extension .{ext} not allowed for {mime_type}")
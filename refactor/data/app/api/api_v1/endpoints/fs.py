from typing import Any, Optional
from app.schemas.common import HTTPExceptionSchema
from app.schemas.fs import UploadResponse
from fastapi.responses import FileResponse
from fastapi import APIRouter, File, HTTPException


router = APIRouter()


@router.post("/upload", status_code=200, response_model=UploadResponse)
def upload_file(
    *,
    file: bytes = File(...)
) -> Any:
    """
    Upload a file
    """
    return {
        "filename": "result.plk",
        "path": "/Users/aq/Documents/agnostiq/uploads/result.plk"
    }


@router.get("/download", status_code=200, response_class=FileResponse, responses={
    404: {"model": HTTPExceptionSchema, "description": "File was not found"},
    200: {
        "content": {"application/octet-stream": {}},
        "description": "Return binary content of file.",
    }
})
def download_file(
     *,
    file_location: str
) -> Any:
    """
    Donwload a file
    """
    if not file_location:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_location, media_type='application/octet-stream',filename=file_location)
 

from __future__ import annotations
import re
import shutil
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.requests import GenerateRequest, GenerateResponse
from app.services import ai_processor, document_parser, h5p_packager

router = APIRouter(prefix="/activities", tags=["activities"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_activity(
    file: UploadFile = File(..., description="Word document (.docx)"),
    activity_type: str = Form(default="auto"),
    pass_percentage: int = Form(default=50),
) -> GenerateResponse:
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")

    upload_dir = Path(settings.upload_dir)
    output_dir = Path(settings.output_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save upload
    safe_name = re.sub(r"[^\w\-.]", "_", file.filename)
    upload_path = upload_dir / safe_name
    with upload_path.open("wb") as fh:
        shutil.copyfileobj(file.file, fh)

    try:
        doc = document_parser.parse_docx(upload_path)
        result = ai_processor.process_document(
            doc,
            activity_type=activity_type,
            pass_percentage=pass_percentage,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        upload_path.unlink(missing_ok=True)

    h5p_bytes = h5p_packager.pack(result.h5p)
    output_filename = re.sub(r"\.docx$", ".h5p", safe_name, flags=re.IGNORECASE)
    output_path = output_dir / output_filename
    output_path.write_bytes(h5p_bytes)

    return GenerateResponse(
        filename=output_filename,
        content_type=result.h5p.content_type,
        title=result.h5p.title,
        download_path=f"/activities/download/{output_filename}",
        cache_read_tokens=result.cache_read_tokens,
        cache_write_tokens=result.cache_write_tokens,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )


@router.get("/download/{filename}")
async def download_activity(filename: str) -> FileResponse:
    output_path = Path(settings.output_dir) / filename
    if not output_path.exists() or output_path.suffix != ".h5p":
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(output_path),
        media_type="application/zip",
        filename=filename,
    )

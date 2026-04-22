from __future__ import annotations
import base64
import re
import shutil
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.requests import AnalyzeResponse, BreakdownPlanResponse, GenerateRequest, GenerateResponse, PreviewSection
from app.services import ai_processor, document_analyzer, document_parser, h5p_packager

router = APIRouter(prefix="/activities", tags=["activities"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_activity(file: UploadFile = File(..., description="Word document (.docx)")) -> AnalyzeResponse:
    upload_path, safe_name = _save_upload(file)
    try:
        doc = document_parser.parse_docx(upload_path)
        analysis = document_analyzer.analyze_document(doc)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        upload_path.unlink(missing_ok=True)

    return AnalyzeResponse(
        title=doc.title or safe_name,
        suggested_activity_type=analysis.suggested_activity_type,
        is_large_document=analysis.is_large_document,
        breakdown_strategy=analysis.breakdown_strategy,
        section_count=analysis.section_count,
        paragraph_count=analysis.paragraph_count,
        list_count=analysis.list_count,
        question_like_section_count=analysis.question_like_section_count,
        estimated_slide_count=analysis.estimated_slide_count,
        estimated_question_count=analysis.estimated_question_count,
        suggestions=analysis.suggestions,
        breakdown_plans=[
            BreakdownPlanResponse(
                title=plan.title,
                summary=plan.summary,
                rationale=plan.rationale,
                suggested_activity_type=plan.suggested_activity_type,
                section_start=plan.section_start,
                section_end=plan.section_end,
                section_count=plan.section_count,
                estimated_question_count=plan.estimated_question_count,
                estimated_slide_count=plan.estimated_slide_count,
                headings=plan.headings,
            )
            for plan in analysis.breakdown_plans
        ],
        sections=[
            PreviewSection(
                heading=section.heading,
                level=section.level,
                category=section.category,
                paragraph_count=section.paragraph_count,
                list_count=section.list_count,
                question_count=section.question_count,
                sample_paragraphs=section.sample_paragraphs,
                sample_list_items=section.sample_list_items,
            )
            for section in analysis.sections
        ],
    )


@router.post("/generate", response_model=GenerateResponse)
async def generate_activity(
    file: UploadFile = File(..., description="Word document (.docx)"),
    ai_provider: str = Form(default=settings.default_ai_provider),
    model: str = Form(default=""),
    activity_type: str = Form(default="auto"),
    pass_percentage: int = Form(default=50),
) -> GenerateResponse:
    if ai_provider not in {"openai", "anthropic"}:
        raise HTTPException(status_code=400, detail="Unsupported AI provider")
    if activity_type not in {"auto", "H5P.QuestionSet", "H5P.CoursePresentation"}:
        raise HTTPException(status_code=400, detail="Unsupported activity type")
    if not 0 < pass_percentage <= 100:
        raise HTTPException(status_code=400, detail="Pass percentage must be between 1 and 100")

    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    upload_path, safe_name = _save_upload(file)

    try:
        doc = document_parser.parse_docx(upload_path)
        result = ai_processor.process_document(
            doc,
            ai_provider=ai_provider,
            activity_type=activity_type,
            pass_percentage=pass_percentage,
            model_override=model.strip() or None,
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
        ai_provider=result.ai_provider,
        ai_model=result.model_used,
        download_base64=base64.b64encode(h5p_bytes).decode("ascii"),
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


def _save_upload(file: UploadFile) -> tuple[Path, str]:
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^\w\-.]", "_", file.filename)
    upload_path = upload_dir / safe_name
    with upload_path.open("wb") as fh:
        shutil.copyfileobj(file.file, fh)
    return upload_path, safe_name

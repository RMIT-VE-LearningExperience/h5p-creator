from __future__ import annotations
import asyncio
import base64
import json
import re
import shutil
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.requests import (
    AnalyzeResponse,
    BatchGenerateResponse,
    BatchResultItem,
    BreakdownPlanResponse,
    ExportRequest,
    ExportResponse,
    GenerateRequest,
    GenerateResponse,
    PreviewSection,
)
from app.services import ai_processor, document_analyzer, document_parser, h5p_packager

router = APIRouter(prefix="/activities", tags=["activities"])

_ALLOWED_ACTIVITY_TYPES = {
    "auto", "H5P.QuestionSet", "H5P.CoursePresentation", "H5P.SortParagraphs",
    "H5P.MultiChoice", "H5P.TrueFalse", "H5P.DragText",
    "H5P.Blanks", "H5P.GuessTheAnswer", "H5P.Summary",
}


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
    file: UploadFile = File(...),
    ai_provider: str = Form(default=settings.default_ai_provider),
    model: str = Form(default=""),
    activity_type: str = Form(default="auto"),
    pass_percentage: int = Form(default=100),
    paragraph_count: int = Form(default=4),
) -> GenerateResponse:
    if ai_provider not in {"openai", "anthropic", "val"}:
        raise HTTPException(status_code=400, detail="Unsupported AI provider")
    if activity_type not in _ALLOWED_ACTIVITY_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported activity type")
    if not 0 < pass_percentage <= 100:
        raise HTTPException(status_code=400, detail="Pass percentage must be between 1 and 100")

    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    upload_path, safe_name = _save_upload(file)

    try:
        doc = document_parser.parse_any(upload_path)
        result = ai_processor.process_document(
            doc,
            ai_provider=ai_provider,
            activity_type=activity_type,
            pass_percentage=pass_percentage,
            paragraph_count=max(3, min(paragraph_count, 20)),
            model_override=model.strip() or None,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        upload_path.unlink(missing_ok=True)

    h5p_bytes = h5p_packager.pack(result.h5p)
    output_filename = re.sub(r"\.(docx|pdf|pptx)$", ".h5p", safe_name, flags=re.IGNORECASE)
    if not output_filename.endswith(".h5p"):
        output_filename += ".h5p"
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
        questions=h5p_packager.extract_questions(result.h5p),
        paragraphs=h5p_packager.extract_paragraphs(result.h5p),
        preview_fields=h5p_packager.extract_preview_fields(result.h5p),
        cache_read_tokens=result.cache_read_tokens,
        cache_write_tokens=result.cache_write_tokens,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
    )


@router.post("/generate_batch", response_model=BatchGenerateResponse)
async def generate_batch(
    files: list[UploadFile] = File(default=[]),
    text_content: str = Form(default=""),
    subject_area: str = Form(default=""),
    learner_context: str = Form(default=""),
    activity_types: str = Form(...),
    content_mode: str = Form(default="shared"),
    count_per_type: int = Form(default=1),
    pass_percentage: int = Form(default=100),
    paragraph_count: int = Form(default=4),
    ai_provider: str = Form(default=settings.default_ai_provider),
    model: str = Form(default=""),
) -> BatchGenerateResponse:
    # Validate activity_types JSON
    try:
        types: list[str] = json.loads(activity_types)
    except Exception:
        raise HTTPException(status_code=400, detail="activity_types must be a JSON array")
    if not types or not isinstance(types, list):
        raise HTTPException(status_code=400, detail="Select at least one activity type")
    invalid = [t for t in types if t not in _ALLOWED_ACTIVITY_TYPES or t == "auto"]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Unsupported activity types: {invalid}")
    if not files and not text_content.strip():
        raise HTTPException(status_code=400, detail="Provide at least one file or paste some content")
    if ai_provider not in {"openai", "anthropic", "val"}:
        raise HTTPException(status_code=400, detail="Unsupported AI provider")
    if not 0 < pass_percentage <= 100:
        raise HTTPException(status_code=400, detail="Pass percentage must be between 1 and 100")
    count_per_type = max(1, min(count_per_type, 10))
    paragraph_count = max(3, min(paragraph_count, 20))
    subject_area = subject_area.strip()
    learner_context = learner_context.strip()

    # Save and parse uploaded files; also accept pasted plain text
    upload_paths: list[Path] = []
    docs: list[document_parser.ParsedDocument] = []
    try:
        for f in files:
            path, _ = _save_upload(f)
            upload_paths.append(path)
        for path in upload_paths:
            try:
                docs.append(document_parser.parse_any(path))
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"Failed to parse {path.name}: {exc}") from exc
        if text_content.strip():
            docs.append(document_parser.text_to_parsed_document(text_content.strip()))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        for path in upload_paths:
            path.unlink(missing_ok=True)

    # Build job list: (activity_type, doc)
    total = len(types) * count_per_type
    jobs: list[tuple[str, document_parser.ParsedDocument]] = []

    if content_mode == "shared":
        merged = document_parser.merge_documents(docs)
        for t in types:
            for _ in range(count_per_type):
                jobs.append((t, merged))
    else:  # unique
        if len(docs) == 1:
            chunks = document_parser.split_document(docs[0], total)
            job_idx = 0
            for t in types:
                for _ in range(count_per_type):
                    jobs.append((t, chunks[job_idx % len(chunks)]))
                    job_idx += 1
        else:
            job_idx = 0
            for t in types:
                for _ in range(count_per_type):
                    jobs.append((t, docs[job_idx % len(docs)]))
                    job_idx += 1

    # Run AI calls in parallel, capped at 3 concurrent to avoid rate limits
    model_override = model.strip() or None
    sem = asyncio.Semaphore(3)

    async def _run_one(activity_type: str, doc: document_parser.ParsedDocument) -> ai_processor.ProcessorResult:
        async with sem:
            return await asyncio.to_thread(
                ai_processor.process_document,
                doc,
                ai_provider=ai_provider,
                activity_type=activity_type,
                pass_percentage=pass_percentage,
                paragraph_count=paragraph_count,
                model_override=model_override,
                subject_area=subject_area,
                learner_context=learner_context,
            )

    try:
        processor_results: list[ai_processor.ProcessorResult] = await asyncio.gather(
            *[_run_one(t, d) for t, d in jobs]
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Pack and assemble results
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[BatchResultItem] = []
    total_input = 0
    total_output = 0

    for (activity_type, _), result in zip(jobs, processor_results):
        h5p_bytes = h5p_packager.pack(result.h5p)
        safe_title = re.sub(r"[^\w\-]", "_", result.h5p.title)[:40] or "activity"
        output_filename = f"{safe_title}.h5p"
        (output_dir / output_filename).write_bytes(h5p_bytes)

        total_input  += result.input_tokens
        total_output += result.output_tokens

        results.append(BatchResultItem(
            activity_type=result.h5p.content_type,
            title=result.h5p.title,
            filename=output_filename,
            download_base64=base64.b64encode(h5p_bytes).decode("ascii"),
            ai_provider=result.ai_provider,
            ai_model=result.model_used,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            preview_fields=h5p_packager.extract_preview_fields(result.h5p),
            questions=h5p_packager.extract_questions(result.h5p),
            paragraphs=h5p_packager.extract_paragraphs(result.h5p),
        ))

    return BatchGenerateResponse(
        results=results,
        total_input_tokens=total_input,
        total_output_tokens=total_output,
    )


@router.post("/export", response_model=ExportResponse)
async def export_activity(body: ExportRequest) -> ExportResponse:
    try:
        if body.content_type == "H5P.SortParagraphs":
            if len(body.paragraphs) < 3:
                raise HTTPException(status_code=400, detail="Sort Paragraphs requires at least 3 paragraphs")
            h5p_bytes = h5p_packager.pack_paragraphs(
                title=body.title,
                paragraphs=body.paragraphs,
            )
        elif body.content_type in {"H5P.QuestionSet"}:
            if not body.questions:
                raise HTTPException(status_code=400, detail="No questions provided")
            h5p_bytes = h5p_packager.pack_questions(
                title=body.title,
                content_type=body.content_type,
                questions=body.questions,
                pass_percentage=body.pass_percentage,
            )
        elif body.raw_content is not None:
            h5p_bytes = h5p_packager.pack_raw(
                title=body.title,
                content_type=body.content_type,
                raw_content=body.raw_content,
            )
        else:
            raise HTTPException(status_code=400, detail=f"Cannot export {body.content_type} without content")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    safe_title = re.sub(r"[^\w\-]", "_", body.title)[:50] or "activity"
    return ExportResponse(
        filename=f"{safe_title}.h5p",
        content_type=body.content_type,
        download_base64=base64.b64encode(h5p_bytes).decode("ascii"),
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
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in {".docx", ".pdf", ".pptx"}:
        raise HTTPException(status_code=400, detail="Only .docx, .pdf, and .pptx files are supported")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^\w\-.]", "_", file.filename)
    upload_path = upload_dir / safe_name
    with upload_path.open("wb") as fh:
        shutil.copyfileobj(file.file, fh)
    return upload_path, safe_name

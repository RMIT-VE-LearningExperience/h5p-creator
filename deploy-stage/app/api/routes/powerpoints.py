from __future__ import annotations

import base64
import re
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services import canvas_lms, powerpoint_generator

router = APIRouter(prefix="/powerpoints", tags=["powerpoints"])


class CoursePowerPointRequest(BaseModel):
    course_url: str = Field(..., min_length=1, max_length=600)
    slide_count: int = Field(default=12, ge=4, le=40)
    audience: str = Field(default="", max_length=300)
    include_images: bool = True
    selected_module_ids: list[int] = Field(default_factory=list, max_length=30)


class CoursePowerPointResponse(BaseModel):
    filename: str
    title: str
    slide_count: int
    download_path: str
    download_base64: str
    ai_provider: str
    ai_model: str
    input_tokens: int
    output_tokens: int


@router.get("/course/modules")
async def list_course_modules(course_url: str) -> dict:
    course_id = _extract_course_id(course_url)
    if not course_id:
        raise HTTPException(status_code=400, detail="Enter a Canvas course URL or numeric course ID.")
    try:
        source = await canvas_lms.read_course(course_id)
    except canvas_lms.CanvasConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "course": source.get("course") or {},
        "modules": [
            {
                "id": module.get("id"),
                "name": module.get("name") or "",
                "published": bool(module.get("published")),
                "items_count": module.get("items_count") or len(module.get("items") or []),
                "items": module.get("items") or [],
            }
            for module in source.get("modules") or []
        ],
    }


@router.post("/course", response_model=CoursePowerPointResponse)
async def generate_course_powerpoint(body: CoursePowerPointRequest) -> CoursePowerPointResponse:
    course_id = _extract_course_id(body.course_url)
    if not course_id:
        raise HTTPException(status_code=400, detail="Enter a Canvas course URL or numeric course ID.")

    try:
        source = await powerpoint_generator.build_course_source(
            course_id,
            include_images=body.include_images,
            selected_module_ids=body.selected_module_ids,
        )
        if not source.pages and not source.files and not source.modules:
            raise HTTPException(status_code=400, detail="No readable course content was found.")
        spec, model_name, input_tokens, output_tokens = powerpoint_generator.generate_deck_spec(
            source,
            slide_count=body.slide_count,
            audience=body.audience.strip(),
            include_images=body.include_images,
        )
        pptx_bytes = await powerpoint_generator.render_deck(
            spec,
            source,
            include_images=body.include_images,
        )
    except HTTPException:
        raise
    except canvas_lms.CanvasConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except powerpoint_generator.CourseDeckError as exc:
        status = 503 if str(exc) == "VAL_NETWORK_ERROR" else 502
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_title = re.sub(r"[^\w\-]", "_", spec.title)[:50] or f"course_{course_id}_powerpoint"
    filename = f"{safe_title}.pptx"
    (output_dir / filename).write_bytes(pptx_bytes)

    return CoursePowerPointResponse(
        filename=filename,
        title=spec.title,
        slide_count=len(spec.slides) + 2,
        download_path=f"/powerpoints/download/{filename}",
        download_base64=base64.b64encode(pptx_bytes).decode("ascii"),
        ai_provider="val",
        ai_model=model_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


@router.get("/download/{filename}")
async def download_powerpoint(filename: str) -> FileResponse:
    output_path = Path(settings.output_dir) / filename
    if not output_path.exists() or output_path.suffix != ".pptx":
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(output_path),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=filename,
    )


def _extract_course_id(value: str) -> int | None:
    text = value.strip()
    if text.isdigit():
        return int(text)
    match = re.search(r"/courses/(\d+)", text)
    if match:
        return int(match.group(1))
    return None

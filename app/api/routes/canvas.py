from __future__ import annotations

import asyncio
import base64
import re
from html.parser import HTMLParser
from typing import AsyncIterator

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.config import settings
from app.schemas.requests import BatchGenerateResponse, BatchResultItem
from app.services import ai_processor, canvas_chat, canvas_files, canvas_lms, document_parser, h5p_packager, training_gov, video_slots, youtube_search

async def _bind_canvas_credentials(
    canvas_base_url: str | None = Header(default=None, alias="X-Canvas-Base-URL"),
    canvas_api_token: str | None = Header(default=None, alias="X-Canvas-API-Token"),
) -> AsyncIterator[None]:
    if bool(canvas_base_url) != bool(canvas_api_token):
        raise HTTPException(status_code=400, detail="Canvas URL and API token are both required.")
    try:
        credentials = (
            canvas_lms.credentials_from_user(canvas_base_url or "", canvas_api_token or "")
            if canvas_base_url and canvas_api_token
            else canvas_lms.default_credentials()
        )
    except canvas_lms.CanvasConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    context_token = canvas_lms.bind_request_credentials(credentials)
    try:
        yield
    finally:
        canvas_lms.reset_request_credentials(context_token)


router = APIRouter(
    prefix="/canvas",
    tags=["canvas"],
    dependencies=[Depends(_bind_canvas_credentials)],
)

_ALLOWED_ACTIVITY_TYPES = {
    "H5P.QuestionSet", "H5P.CoursePresentation", "H5P.SortParagraphs",
    "H5P.MultiChoice", "H5P.TrueFalse", "H5P.DragText",
    "H5P.Blanks", "H5P.GuessTheAnswer", "H5P.Summary",
}


class CanvasChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1200)
    courses: list[dict] = Field(default_factory=list)


class CanvasChatResponse(BaseModel):
    answer: str
    ai_provider: str
    ai_model: str


class CanvasFileSelectionRequest(BaseModel):
    file_ids: list[int] = Field(..., min_length=1, max_length=10)


class CanvasFileChatRequest(CanvasFileSelectionRequest):
    question: str = Field(..., min_length=2, max_length=1200)


class CanvasFileGenerateRequest(CanvasFileSelectionRequest):
    activity_type: str = "H5P.QuestionSet"
    content_mode: str = "shared"
    pass_percentage: int = 100
    paragraph_count: int = 4


class CanvasPageSelectionRequest(BaseModel):
    course_id: int
    course_name: str = ""
    page_urls: list[str] = Field(..., min_length=1)


class CanvasVideoSuggestionRequest(BaseModel):
    course_id: int
    course_name: str = ""
    page_urls: list[str] = Field(default_factory=list)
    module_ids: list[int] = Field(default_factory=list)


class CanvasPageChatRequest(CanvasPageSelectionRequest):
    question: str = Field(..., min_length=2, max_length=1200)


class VideoSlotSuggestionRequest(BaseModel):
    course_id: int
    course_name: str = ""
    page_urls: list[str] = Field(..., min_length=1)
    aqf_level: int | None = Field(default=None, ge=1, le=10)
    training_product_code: str = Field(default="", max_length=20)
    training_product_title: str = Field(default="", max_length=300)


class AQFLevelSuggestionRequest(BaseModel):
    course_id: int
    course_name: str = ""


class VideoSlotPreviewRequest(BaseModel):
    course_id: int
    page_url: str
    slot_index: int = Field(..., ge=0)
    slot_id: str = Field(default="", max_length=100)
    videos: list[dict] = Field(..., min_length=1, max_length=5)
    aqf_level: int | None = Field(default=None, ge=1, le=10)


class VideoSlotApplyRequest(BaseModel):
    course_id: int
    page_url: str
    updated_body: str
    expected_updated_at: str = ""


class VideoSlotRevertRequest(BaseModel):
    course_id: int
    page_url: str
    revision_id: int


class VideoSlotRefineRequest(BaseModel):
    course_id: int
    course_name: str = ""
    page_url: str
    slot_index: int = Field(..., ge=0)
    slot_id: str = Field(default="", max_length=100)
    additional_context: str = Field(default="", max_length=1000)
    aqf_level: int | None = Field(default=None, ge=1, le=10)
    training_product_code: str = Field(default="", max_length=20)
    training_product_title: str = Field(default="", max_length=300)


@router.get("/status")
async def canvas_status() -> dict:
    if not canvas_lms.is_configured():
        return {
            "configured": False,
            "connected": False,
            "read_only": False,
            "accepts_user_credentials": True,
        }
    try:
        user = await canvas_lms.get_current_user()
    except canvas_lms.CanvasAPIError as exc:
        status_code = 401 if "rejected" in str(exc).lower() else 502
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    credentials = canvas_lms.current_credentials()
    return {
        "configured": True,
        "connected": True,
        "read_only": False,
        "accepts_user_credentials": True,
        "account_scope": bool(credentials.account_id),
        "credential_source": credentials.source,
        "canvas_host": credentials.base_url,
        "user": user,
    }


@router.get("/courses/search")
async def search_canvas_courses(
    q: str = Query(..., min_length=2, max_length=120),
    limit: int = Query(20, ge=1, le=50),
) -> dict:
    try:
        courses = await canvas_lms.search_courses(q, limit=limit)
    except canvas_lms.CanvasConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"results": courses}


@router.get("/courses/{course_id}")
async def read_canvas_course(course_id: int) -> dict:
    try:
        return await canvas_lms.read_course(course_id)
    except canvas_lms.CanvasConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/courses/{course_id}/files")
async def list_canvas_course_files(
    course_id: int,
    limit: int = Query(100, ge=1, le=200),
) -> dict:
    try:
        files = await canvas_lms.list_course_files(course_id, limit=limit)
    except canvas_lms.CanvasConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"results": files}


@router.post("/files/preview")
async def preview_canvas_files(body: CanvasFileSelectionRequest) -> dict:
    try:
        parsed = await canvas_files.parse_canvas_files(body.file_ids)
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "files": [
            {
                "id": item.id,
                "filename": item.filename,
                "extension": item.extension,
                "title": item.title,
                "character_count": len(item.text or ""),
                "text": _truncate(item.text, 12000),
            }
            for item in parsed
        ],
    }


@router.post("/pages/preview")
async def preview_canvas_pages(body: CanvasPageSelectionRequest) -> dict:
    try:
        pages = [await canvas_lms.read_page(body.course_id, url) for url in body.page_urls]
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "pages": [
            {
                "title": page["title"],
                "url": page["url"],
                "published": page["published"],
                "updated_at": page["updated_at"],
                "text": _truncate(_html_to_text(page["body"]), 12000),
                "character_count": len(_html_to_text(page["body"])),
            }
            for page in pages
        ],
    }


@router.post("/pages/youtube")
async def suggest_youtube_for_canvas_pages(body: CanvasPageSelectionRequest) -> dict:
    return await _suggest_videos_for_canvas_content(
        CanvasVideoSuggestionRequest(
            course_id=body.course_id,
            course_name=body.course_name,
            page_urls=body.page_urls,
        )
    )


@router.post("/videos/suggest")
async def suggest_youtube_for_canvas_content(body: CanvasVideoSuggestionRequest) -> dict:
    return await _suggest_videos_for_canvas_content(body)


async def _suggest_videos_for_canvas_content(body: CanvasVideoSuggestionRequest) -> dict:
    try:
        course = await canvas_lms.read_course(body.course_id)
        selected_urls = list(dict.fromkeys(url for url in body.page_urls if url))
        selected_modules = {str(module_id) for module_id in body.module_ids}

        if selected_modules:
            for module in course.get("modules") or []:
                if str(module.get("id")) not in selected_modules:
                    continue
                for item in module.get("items") or []:
                    if item.get("type") == "Page" and item.get("page_url"):
                        selected_urls.append(item["page_url"])

        if not selected_urls and not selected_modules:
            selected_urls.extend(page.get("url") for page in course.get("pages") or [] if page.get("url"))

        selected_urls = list(dict.fromkeys(selected_urls))
        if not selected_urls:
            raise HTTPException(status_code=400, detail="The selected course content has no readable Canvas pages.")

        pages = [await canvas_lms.read_page(body.course_id, url) for url in selected_urls]
        results = []
        for page in pages:
            page_text = _html_to_text(page["body"])
            page_context = {
                "course": {"id": body.course_id, "name": body.course_name},
                "selected_page_bodies": [{
                    "title": page["title"],
                    "url": page["url"],
                    "published": page["published"],
                    "text": _truncate(page_text, 10000),
                    "embedded_youtube_links": _extract_youtube_links(page["body"]),
                }],
            }
            suggestions = await _youtube_results_for_item(page_context)
            results.append({
                "title": page["title"],
                "url": page["url"],
                "published": page["published"],
                "embedded_youtube_links": page_context["selected_page_bodies"][0]["embedded_youtube_links"],
                "search_queries": _build_youtube_queries("", page_context),
                "videos": suggestions,
            })
    except canvas_lms.CanvasConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "course": course.get("course") or {"id": body.course_id, "name": body.course_name},
        "pages": results,
    }


_BEFORE_CLASS_TITLE_RE = re.compile(r"before[\s-]*class|pre[\s-]*class|\bprep\b", re.IGNORECASE)


async def _before_class_context(course: dict, course_id: int, page_url: str) -> dict | None:
    for module in course.get("modules") or []:
        items = module.get("items") or []
        if not any(item.get("type") == "Page" and item.get("page_url") == page_url for item in items):
            continue
        for item in items:
            sibling_url = item.get("page_url") or ""
            if item.get("type") != "Page" or not sibling_url or sibling_url == page_url:
                continue
            if not _BEFORE_CLASS_TITLE_RE.search(item.get("title") or ""):
                continue
            sibling_page = await canvas_lms.read_page(course_id, sibling_url)
            return {
                "module_name": module.get("name") or "",
                "title": sibling_page["title"],
                "url": sibling_page["url"],
                "text": _truncate(_html_to_text(sibling_page["body"]), 4000),
            }
    return None


def _module_name_for_page(course: dict, page_url: str) -> str:
    for module in course.get("modules") or []:
        items = module.get("items") or []
        if any(item.get("type") == "Page" and item.get("page_url") == page_url for item in items):
            return module.get("name") or ""
    return ""


def _aqf_search_modifier(aqf_level: int | None) -> str:
    if not aqf_level:
        return ""
    if aqf_level <= 2:
        return "introductory basics"
    if aqf_level <= 4:
        return "beginner practical"
    if aqf_level <= 6:
        return "applied professional"
    if aqf_level <= 8:
        return "advanced professional"
    return "expert research"


def _search_query_for_aqf(query: str, aqf_level: int | None) -> str:
    query = (query or "").strip()
    modifier = _aqf_search_modifier(aqf_level)
    if not query or not modifier:
        return query
    lowered = query.lower()
    if any(term in lowered for term in ("introductory", "beginner", "basics", "applied", "professional", "advanced", "expert", "research")):
        return query
    return f"{query} {modifier}"


def _training_product_search_context(code: str, title: str) -> str:
    return " ".join(part.strip() for part in (code, title) if part and part.strip())


async def _training_gov_aqf_suggestion(course: dict) -> dict | None:
    compact = canvas_chat.compact_aqf_context(course)
    values = [
        compact["course"]["course_code"],
        compact["course"]["name"],
        *[item["name"] for item in compact["modules"]],
        *[item["title"] for item in compact["pages"]],
    ]
    codes = training_gov.extract_training_product_codes(*values, limit=4)
    if not codes:
        return None

    async def lookup(code: str):
        try:
            return await asyncio.wait_for(
                training_gov.lookup_training_product(code),
                timeout=18,
            )
        except (TimeoutError, ValueError, RuntimeError):
            return None

    products = await asyncio.gather(*(lookup(code) for code in codes))
    for product in products:
        if not product:
            continue
        suggestion = training_gov.aqf_suggestion(product)
        if suggestion:
            suggestion["aqf_label"] = canvas_chat.aqf_label(suggestion["aqf_level"])
            return suggestion
    return None


@router.post("/courses/aqf-suggestion")
async def suggest_course_aqf_level(body: AQFLevelSuggestionRequest) -> dict:
    try:
        course = await canvas_lms.read_course(body.course_id)
        if body.course_name and course.get("course"):
            course["course"]["name"] = body.course_name
        suggestion = await _training_gov_aqf_suggestion(course)
        if not suggestion:
            suggestion = await asyncio.to_thread(lambda: canvas_chat.suggest_aqf_level(course))
    except canvas_lms.CanvasConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except canvas_chat.CanvasChatConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_chat.CanvasChatError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return suggestion


@router.post("/pages/video-slots")
async def suggest_video_slots(body: VideoSlotSuggestionRequest) -> dict:
    try:
        course = await canvas_lms.read_course(body.course_id)
        page_urls = list(dict.fromkeys(url for url in body.page_urls if url))
        if not page_urls:
            raise HTTPException(status_code=400, detail="Select at least one Canvas page.")

        async def process_page(page_url: str) -> dict:
            page = await canvas_lms.read_page(body.course_id, page_url)
            slots = video_slots.find_video_slots(page["body"])
            before_class = await _before_class_context(course, body.course_id, page_url)
            page_text = _html_to_text(page["body"])
            page_summary = _page_context_summary(page["title"], page_text)
            course_name = body.course_name or (course.get("course") or {}).get("name") or ""
            training_context = _training_product_search_context(
                body.training_product_code,
                body.training_product_title,
            )
            search_course_name = " · ".join(
                part for part in (course_name, training_context) if part
            )
            module_name = _module_name_for_page(course, page_url)

            selected_page_bodies = [{
                "title": page["title"],
                "url": page["url"],
                "published": page["published"],
                "text": _truncate(page_text, 10000),
                "embedded_youtube_links": _extract_youtube_links(page["body"]),
            }]
            if before_class:
                selected_page_bodies.append({
                    "title": before_class["title"],
                    "url": before_class["url"],
                    "published": True,
                    "text": before_class["text"],
                    "embedded_youtube_links": [],
                })
            page_context = {
                "course": {"id": body.course_id, "name": search_course_name},
                "selected_page_bodies": selected_page_bodies,
            }

            async def resolve_query(existing_search: str) -> str:
                if existing_search:
                    return _search_query_for_aqf(existing_search, body.aqf_level)
                try:
                    query = await asyncio.to_thread(
                        lambda: canvas_chat.generate_search_query(
                            page_title=page["title"],
                            page_text=page_text,
                            course_name=search_course_name,
                            module_name=module_name,
                            before_class_text=before_class["text"] if before_class else "",
                            aqf_level=body.aqf_level,
                        )
                    )
                    return _search_query_for_aqf(query, body.aqf_level)
                except (canvas_chat.CanvasChatConfigError, canvas_chat.CanvasChatError):
                    fallback_queries = _build_youtube_queries("", page_context)
                    fallback_query = fallback_queries[0] if fallback_queries else ""
                    return _search_query_for_aqf(fallback_query, body.aqf_level)

            slot_results = []
            editable_slots = slots or [video_slots.make_append_slot(page["body"])]
            for slot in editable_slots:
                query = await resolve_query(slot.suggested_search)
                videos = await youtube_search.search_videos(query, limit=6) if query else []
                slot_results.append({
                    "index": slot.index,
                    "slot_id": slot.slot_id,
                    "suggested_search": slot.suggested_search,
                    "original_description_text": slot.original_description_text,
                    "search_query": query,
                    "already_filled": slot.already_filled,
                    "insertion_mode": slot.insertion_mode,
                    "videos": videos,
                })
            return {
                "title": page["title"],
                "url": page["url"],
                "published": page["published"],
                "module_name": module_name,
                "before_class_context": before_class,
                "page_summary": page_summary,
                "slots": slot_results,
            }

        semaphore = asyncio.Semaphore(5)

        async def process_page_bounded(page_url: str) -> dict:
            async with semaphore:
                return await process_page(page_url)

        results = await asyncio.gather(
            *(process_page_bounded(page_url) for page_url in page_urls)
        )
    except canvas_lms.CanvasConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "course": course.get("course") or {"id": body.course_id, "name": body.course_name},
        "pages": results,
    }


@router.post("/pages/video-slots/refine")
async def refine_video_slot_search(body: VideoSlotRefineRequest) -> dict:
    try:
        course = await canvas_lms.read_course(body.course_id)
        page = await canvas_lms.read_page(body.course_id, body.page_url)
        slot = video_slots.find_video_slot(
            page["body"], slot_id=body.slot_id, slot_index=body.slot_index
        )
        if slot is None:
            raise HTTPException(status_code=400, detail="That video slot no longer exists on this page.")

        before_class = await _before_class_context(course, body.course_id, body.page_url)
        course_name = body.course_name or (course.get("course") or {}).get("name") or ""
        training_context = _training_product_search_context(
            body.training_product_code,
            body.training_product_title,
        )
        search_course_name = " · ".join(
            part for part in (course_name, training_context) if part
        )
        module_name = _module_name_for_page(course, body.page_url)
        page_text = _html_to_text(page["body"])

        query = await asyncio.to_thread(
            lambda: canvas_chat.generate_search_query(
                page_title=page["title"],
                page_text=page_text,
                course_name=search_course_name,
                module_name=module_name,
                before_class_text=before_class["text"] if before_class else "",
                additional_context=body.additional_context,
                aqf_level=body.aqf_level,
            )
        )
        query = _search_query_for_aqf(query, body.aqf_level)
        videos = await youtube_search.search_videos(query, limit=6) if query else []
    except canvas_lms.CanvasConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except canvas_chat.CanvasChatConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_chat.CanvasChatError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "search_query": query,
        "original_description_text": slot.original_description_text,
        "videos": videos,
    }


@router.post("/pages/video-slots/preview")
async def preview_video_slot(body: VideoSlotPreviewRequest) -> dict:
    try:
        page = await canvas_lms.read_page(body.course_id, body.page_url)
        slot = video_slots.find_video_slot(
            page["body"], slot_id=body.slot_id, slot_index=body.slot_index
        )
        if slot is None:
            raise HTTPException(status_code=400, detail="That video slot no longer exists on this page.")

        descriptions = []
        used_description_fallback = False
        for video in body.videos:
            duration_label = video_slots.format_duration(video.get("duration") or "")
            try:
                description = await asyncio.to_thread(
                    canvas_chat.generate_slot_description,
                    video,
                    duration_label,
                    slot.original_description_text,
                    {"title": page["title"]},
                    body.aqf_level,
                )
            except (canvas_chat.CanvasChatConfigError, canvas_chat.CanvasChatError):
                description = canvas_chat.fallback_slot_description(video, duration_label)
                used_description_fallback = True
            descriptions.append(description)

        rendered = video_slots.render_slot_html(slot, body.videos, descriptions)
        replacement_html = "\n".join(
            f"{description_html}\n{embed_html}"
            for description_html, embed_html in rendered
        )
        before_preview_standalone_html = video_slots.wrap_for_preview(
            video_slots.render_current_slot_html(slot)
        )
        preview_standalone_html = video_slots.wrap_for_preview(rendered)
        updated_body = video_slots.apply_slot(
            page["body"], body.slot_index, rendered, slot_id=body.slot_id
        )
    except canvas_lms.CanvasConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except canvas_chat.CanvasChatConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_chat.CanvasChatError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "preview_html": replacement_html,
        "before_preview_standalone_html": before_preview_standalone_html,
        "preview_standalone_html": preview_standalone_html,
        "updated_body": updated_body,
        "expected_updated_at": page["updated_at"],
        "description_fallback": used_description_fallback,
    }


@router.post("/pages/video-slots/apply")
async def apply_video_slot(body: VideoSlotApplyRequest) -> dict:
    try:
        current = await canvas_lms.read_page(body.course_id, body.page_url)
        if body.expected_updated_at and current["updated_at"] != body.expected_updated_at:
            raise HTTPException(
                status_code=409,
                detail="This Canvas page changed since you previewed the update. Preview again before pushing.",
            )
        updated = await canvas_lms.update_page(body.course_id, body.page_url, body.updated_body)

        revert_revision_id = None
        try:
            revisions = await canvas_lms.list_page_revisions(body.course_id, body.page_url)
            revisions.sort(key=lambda rev: rev["revision_id"] or 0, reverse=True)
            previous = next((rev for rev in revisions if not rev["latest"]), None)
            if previous:
                revert_revision_id = previous["revision_id"]
        except canvas_lms.CanvasAPIError:
            pass  # Push already succeeded; revision history just isn't available to revert from.
    except canvas_lms.CanvasConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "title": updated["title"],
        "url": updated["url"],
        "published": updated["published"],
        "updated_at": updated["updated_at"],
        "revert_revision_id": revert_revision_id,
    }


@router.post("/pages/video-slots/revert")
async def revert_video_slot(body: VideoSlotRevertRequest) -> dict:
    try:
        reverted = await canvas_lms.revert_page_to_revision(body.course_id, body.page_url, body.revision_id)
    except canvas_lms.CanvasConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "title": reverted["title"],
        "url": reverted["url"],
        "published": reverted["published"],
        "updated_at": reverted["updated_at"],
    }


@router.post("/pages/chat", response_model=CanvasChatResponse)
async def chat_about_canvas_pages(body: CanvasPageChatRequest) -> CanvasChatResponse:
    try:
        pages = [await canvas_lms.read_page(body.course_id, url) for url in body.page_urls]
        page_context = [
            {
                "title": page["title"],
                "url": page["url"],
                "published": page["published"],
                "text": _truncate(_html_to_text(page["body"]), 10000),
                "embedded_youtube_links": _extract_youtube_links(page["body"]),
            }
            for page in pages
        ]
        youtube_results = await _youtube_results_for_question(
            body.question,
            {"course": {"name": "Selected Canvas pages", "id": body.course_id}, "selected_page_bodies": page_context},
        )
        result = canvas_chat.answer_course_question(
            question=body.question,
            courses=[{
                "course": {"name": "Selected Canvas pages", "id": body.course_id},
                "pages": page_context,
                "youtube_search_results": youtube_results,
            }],
        )
    except canvas_chat.CanvasChatConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_chat.CanvasChatError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return CanvasChatResponse(**result)


@router.post("/files/chat", response_model=CanvasChatResponse)
async def chat_about_canvas_files(body: CanvasFileChatRequest) -> CanvasChatResponse:
    try:
        parsed = await canvas_files.parse_canvas_files(body.file_ids)
        context = canvas_files.build_text_context(parsed)
        result = canvas_chat.answer_course_question(
            question=body.question,
            courses=[{
                "course": {"name": "Selected Canvas files"},
                "files": [
                    {
                        "id": item.id,
                        "filename": item.filename,
                        "title": item.title,
                        "text": _truncate(item.text, 8000),
                    }
                    for item in parsed
                ],
                "file_context": context,
            }],
        )
    except canvas_chat.CanvasChatConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_chat.CanvasChatError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return CanvasChatResponse(**result)


@router.post("/files/generate", response_model=BatchGenerateResponse)
async def generate_from_canvas_files(body: CanvasFileGenerateRequest) -> BatchGenerateResponse:
    if body.activity_type not in _ALLOWED_ACTIVITY_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported activity type")
    if body.content_mode not in {"shared", "unique"}:
        raise HTTPException(status_code=400, detail="Unsupported content mode")
    if not 0 < body.pass_percentage <= 100:
        raise HTTPException(status_code=400, detail="Pass percentage must be between 1 and 100")

    try:
        parsed = await canvas_files.parse_canvas_files(body.file_ids)
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    docs = [item.document for item in parsed]
    if not docs or not any((doc.raw_text or "").strip() for doc in docs):
        raise HTTPException(status_code=400, detail="Selected files did not contain readable text")

    if body.content_mode == "shared":
        jobs = [document_parser.merge_documents(docs)]
    else:
        jobs = docs

    sem = asyncio.Semaphore(3)

    async def _run_one(doc: document_parser.ParsedDocument) -> ai_processor.ProcessorResult:
        async with sem:
            return await asyncio.to_thread(
                ai_processor.process_document,
                doc,
                ai_provider="val",
                activity_type=body.activity_type,
                pass_percentage=body.pass_percentage,
                paragraph_count=max(3, min(body.paragraph_count, 20)),
                model_override=None,
            )

    try:
        processor_results = await asyncio.gather(*[_run_one(doc) for doc in jobs])
    except Exception as exc:
        if "VAL_NETWORK_ERROR" in str(exc):
            raise HTTPException(status_code=503, detail="VAL_NETWORK_ERROR") from exc
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    results = []
    total_input = 0
    total_output = 0
    output_dir = canvas_lms.settings.output_dir or settings.output_dir

    from pathlib import Path
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for result in processor_results:
        h5p_bytes = h5p_packager.pack(result.h5p)
        safe_title = re.sub(r"[^\w\-]", "_", result.h5p.title)[:40] or "canvas_activity"
        output_filename = f"{safe_title}.h5p"
        (out / output_filename).write_bytes(h5p_bytes)
        total_input += result.input_tokens
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


@router.post("/chat", response_model=CanvasChatResponse)
async def chat_about_canvas_courses(body: CanvasChatRequest) -> CanvasChatResponse:
    try:
        courses = await _augment_courses_with_page_bodies(body.courses, body.question)
        courses = await _augment_courses_with_youtube_results(courses, body.question)
        result = canvas_chat.answer_course_question(
            question=body.question,
            courses=courses,
        )
    except canvas_chat.CanvasChatConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except canvas_chat.CanvasChatError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except canvas_lms.CanvasAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return CanvasChatResponse(**result)


def _truncate(value: str, max_chars: int) -> str:
    text = (value or "").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n[truncated]"


async def _augment_courses_with_page_bodies(courses: list[dict], question: str) -> list[dict]:
    question_lc = question.lower()
    question_norm = _match_text(question)
    augmented = []
    for item in courses:
        course = item.get("course") or {}
        course_id = course.get("id")
        pages = item.get("pages") or []
        selected_urls = item.get("selected_page_urls") or []
        urls: list[str] = []

        for url in selected_urls:
            if url and url not in urls:
                urls.append(url)

        if course_id and not urls:
            for page in pages:
                title = str(page.get("title") or "").lower()
                url = str(page.get("url") or "").lower()
                title_norm = _match_text(title)
                url_norm = _match_text(url)
                if (
                    (title and title in question_lc)
                    or (url and url in question_lc)
                    or (title_norm and title_norm in question_norm)
                    or (url_norm and url_norm in question_norm)
                ):
                    page_url = page.get("url")
                    if page_url and page_url not in urls:
                        urls.append(page_url)

        page_bodies = []
        if course_id:
            for page_url in urls[:5]:
                page = await canvas_lms.read_page(int(course_id), page_url)
                page_bodies.append({
                    "title": page["title"],
                    "url": page["url"],
                    "published": page["published"],
                    "text": _truncate(_html_to_text(page["body"]), 10000),
                    "embedded_youtube_links": _extract_youtube_links(page["body"]),
                })

        if page_bodies:
            item = {**item, "selected_page_bodies": page_bodies}
        augmented.append(item)
    return augmented


async def _augment_courses_with_youtube_results(courses: list[dict], question: str) -> list[dict]:
    if not _looks_like_video_question(question) or not youtube_search.is_configured():
        return courses

    augmented = []
    for item in courses:
        results = await _youtube_results_for_question(question, item)
        if results:
            item = {**item, "youtube_search_results": results}
        augmented.append(item)
    return augmented


async def _youtube_results_for_question(question: str, item: dict) -> list[dict]:
    if not _looks_like_video_question(question) or not youtube_search.is_configured():
        return []
    return await _youtube_results_for_item(item, question)


async def _youtube_results_for_item(item: dict, question: str = "") -> list[dict]:
    if not youtube_search.is_configured():
        return []
    results: list[dict] = []
    seen: set[str] = set()
    for query in _build_youtube_queries(question, item):
        try:
            videos = await youtube_search.search_videos(query, limit=5)
        except (youtube_search.YouTubeConfigError, youtube_search.YouTubeAPIError):
            continue
        for video in videos:
            video_id = str(video.get("id") or "")
            if not video_id or video_id in seen:
                continue
            seen.add(video_id)
            results.append({**video, "search_query": query})
            if len(results) >= 5:
                return results
    return results


def _looks_like_video_question(question: str) -> bool:
    q = question.lower()
    return any(term in q for term in ("youtube", "video", "watch", "embed", "link", "url"))


def _build_youtube_queries(question: str, item: dict) -> list[str]:
    course = item.get("course") or {}
    bodies = item.get("selected_page_bodies") or []
    pages = item.get("pages") or []
    queries: list[str] = []

    for body in bodies[:2]:
        page_terms: list[str] = []
        if body.get("title"):
            page_terms.append(str(body["title"]))
        text = str(body.get("text") or "")
        keywords = ""
        if text:
            keywords = _keywords_from_text(text, 8)
            page_terms.append(keywords)
        if page_terms:
            queries.append(" ".join(page_terms))
        if keywords:
            queries.append(keywords)

    if not queries:
        for page in pages[:5]:
            title = str(page.get("title") or "")
            if title and _match_text(title) in _match_text(question):
                queries.append(title)

    if course.get("name"):
        course_name = str(course["name"])
        if course_name.lower() != "selected canvas course":
            course_keywords = _keywords_from_text(course_name, 4)
            if course_keywords:
                queries = [f"{course_keywords} {query}" for query in queries[:2]] + queries
    if question:
        queries.append(_clean_youtube_question(question))

    cleaned: list[str] = []
    for query in queries:
        query = re.sub(r"\s+", " ", query).strip()
        if len(query) >= 2 and query not in cleaned:
            cleaned.append(query[:160])
    return cleaned[:5]


def _keywords_from_text(text: str, max_words: int) -> str:
    words = re.findall(r"[A-Za-z][A-Za-z0-9'-]{2,}", text.lower())
    stop = {
        "the", "and", "for", "with", "that", "this", "from", "you", "your",
        "are", "will", "can", "have", "has", "not", "was", "were", "into",
        "canvas", "page", "module", "course", "video", "youtube", "watch",
        "completion", "complete", "job", "should", "allow", "time", "includes",
        "also", "before", "after", "such", "therefore", "there", "while",
        "future", "first", "class", "good",
    }
    counts: dict[str, int] = {}
    first_pos: dict[str, int] = {}
    for index, word in enumerate(words):
        if word in stop or any(ch.isdigit() for ch in word):
            continue
        counts[word] = counts.get(word, 0) + 1
        first_pos.setdefault(word, index)
    ranked = sorted(counts, key=lambda word: (-counts[word], first_pos[word]))
    selected: list[str] = []
    for word in ranked:
        selected.append(word)
        if len(selected) >= max_words:
            break
    return " ".join(selected)


def _clean_youtube_question(question: str) -> str:
    text = re.sub(r"\b(find|youtube|video|link|url|canvas|page|for|the|this|that)\b", " ", question, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()


def _extract_youtube_links(html: str) -> list[dict]:
    links: list[dict] = []
    seen: set[str] = set()
    for match in re.finditer(r'https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^"\'<>\s)]+', html or "", flags=re.I):
        raw_url = match.group(0).replace("&amp;", "&")
        video_id = _youtube_video_id(raw_url)
        key = video_id or raw_url
        if key in seen:
            continue
        seen.add(key)
        links.append({
            "url": raw_url,
            "video_id": video_id,
            "watch_url": f"https://www.youtube.com/watch?v={video_id}" if video_id else raw_url,
        })
    return links


def _youtube_video_id(url: str) -> str:
    patterns = [
        r"[?&]v=([A-Za-z0-9_-]{6,})",
        r"/embed/([A-Za-z0-9_-]{6,})",
        r"youtu\.be/([A-Za-z0-9_-]{6,})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)


def _html_to_text(html: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(html or "")
    text = " ".join(parser.parts)
    text = re.sub(r"\s*\n\s*", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _page_context_summary(page_title: str, page_text: str, limit: int = 280) -> str:
    """Return a short, useful excerpt without video-template instructions."""
    title_key = _match_text(page_title)
    useful_lines = []
    for line in (page_text or "").splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        line_key = _match_text(line)
        if (
            not line
            or line_key == title_key
            or re.search(r"watch this\s*\(", line, re.IGNORECASE)
            or re.search(r"embed your youtube video here", line, re.IGNORECASE)
        ):
            continue
        useful_lines.append(line)

    summary = " ".join(useful_lines)
    if not summary:
        return f"This page covers {page_title}." if page_title else "No page description is available."
    if len(summary) <= limit:
        return summary
    shortened = summary[: limit + 1].rsplit(" ", 1)[0].rstrip(" ,;:")
    return f"{shortened}..."


def _match_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (value or "").lower())).strip()

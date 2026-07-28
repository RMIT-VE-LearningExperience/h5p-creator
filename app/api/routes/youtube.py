from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services import youtube_search

router = APIRouter(prefix="/youtube", tags=["youtube"])


class YouTubeChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1200)
    videos: list[dict[str, Any]] = Field(..., min_length=1, max_length=10)


class YouTubeChatResponse(BaseModel):
    answer: str
    ai_provider: str
    ai_model: str
    refined_query: str | None = None


@router.get("/status")
async def youtube_status() -> dict:
    return {"configured": youtube_search.is_configured()}


@router.get("/search")
async def search_youtube_videos(
    q: str = Query(..., min_length=2, max_length=160),
    limit: int = Query(8, ge=1, le=12),
) -> dict:
    try:
        videos = await youtube_search.search_videos(q, limit=limit)
    except youtube_search.YouTubeConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except youtube_search.YouTubeAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"results": videos}


@router.get("/videos/{video_id}/transcript")
async def youtube_video_transcript(video_id: str) -> dict:
    try:
        return await youtube_search.get_transcript(video_id)
    except youtube_search.YouTubeAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/chat", response_model=YouTubeChatResponse)
async def chat_about_youtube_videos(body: YouTubeChatRequest) -> YouTubeChatResponse:
    try:
        result = _ask_val_about_videos(body.question, body.videos)
    except RuntimeError as exc:
        detail = str(exc)
        status = 503 if "VAL_API_KEY" in detail or "OpenAI SDK" in detail else 502
        raise HTTPException(status_code=status, detail=detail) from exc
    return YouTubeChatResponse(**result)


def _ask_val_about_videos(question: str, videos: list[dict[str, Any]]) -> dict[str, str]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("OpenAI SDK is not installed.") from exc

    if not settings.val_api_key:
        raise RuntimeError("VAL_API_KEY is not configured.")

    compact_videos = [_compact_video(video) for video in videos[:10]]
    client = OpenAI(api_key=settings.val_api_key, base_url=settings.val_base_url)
    model_name = settings.val_model
    user_content = "\n\n".join([
        "## Selected YouTube video metadata",
        json.dumps(compact_videos, ensure_ascii=False, indent=2),
        "## Question",
        question.strip(),
    ])
    system_prompt = (
        "Answer questions using only the supplied YouTube video metadata. "
        "Be clear when the metadata is not enough. Do not claim to have watched "
        "the videos or read transcripts unless transcript text is explicitly supplied. "
        "If the question is asking to narrow, refine, or replace the search results "
        "(e.g. \"find something shorter\", \"more about PPE\", \"something more advanced\"), "
        "also propose a short YouTube search query string that would find better matches. "
        "Respond with JSON: {\"answer\": \"<your answer>\", \"refined_query\": \"<query>\" or null}."
    )

    try:
        response = client.chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
    except Exception as exc:
        msg = str(exc)
        if any(x in msg for x in ("403", "Forbidden", "forbidden", "blocked", "unavailable")):
            raise RuntimeError("VAL_NETWORK_ERROR") from exc
        raise RuntimeError(f"VAL chat failed: {msg}") from exc

    raw = (response.choices[0].message.content or "").strip()
    try:
        parsed = json.loads(raw)
        answer = str(parsed.get("answer") or "").strip()
        refined_query = parsed.get("refined_query")
        refined_query = str(refined_query).strip() if refined_query else None
    except (ValueError, AttributeError):
        answer = raw
        refined_query = None
    if not answer:
        raise RuntimeError("VAL returned no answer.")
    return {"answer": answer, "ai_provider": "val", "ai_model": model_name, "refined_query": refined_query}


def _compact_video(video: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": video.get("id"),
        "title": video.get("title") or "",
        "description": _truncate(video.get("description") or "", 3000),
        "channel_title": video.get("channel_title") or "",
        "published_at": video.get("published_at") or "",
        "duration": video.get("duration") or "",
        "view_count": video.get("view_count"),
        "url": video.get("url") or "",
    }


def _truncate(value: str, max_chars: int) -> str:
    text = (value or "").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n[truncated]"

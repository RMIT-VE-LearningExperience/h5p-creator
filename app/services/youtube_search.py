from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings


class YouTubeConfigError(RuntimeError):
    pass


class YouTubeAPIError(RuntimeError):
    pass


_YOUTUBE_API = "https://www.googleapis.com/youtube/v3"


def is_configured() -> bool:
    return bool(settings.youtube_api_key)


def _api_key() -> str:
    if not settings.youtube_api_key:
        raise YouTubeConfigError("YouTube is not configured. Set YOUTUBE_API_KEY on the server.")
    return settings.youtube_api_key


async def search_videos(query: str, limit: int = 8) -> list[dict[str, Any]]:
    query = query.strip()
    if len(query) < 2:
        return []

    max_results = max(1, min(limit, 12))
    search_payload = await _get_json(
        "search",
        {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "safeSearch": "moderate",
        },
    )
    items = search_payload.get("items") or []
    video_ids = [
        item.get("id", {}).get("videoId")
        for item in items
        if item.get("id", {}).get("videoId")
    ]
    details_by_id = await _video_details(video_ids)

    results = []
    for item in items:
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            continue
        snippet = item.get("snippet") or {}
        details = details_by_id.get(video_id, {})
        detail_snippet = details.get("snippet") or snippet
        thumbnails = detail_snippet.get("thumbnails") or snippet.get("thumbnails") or {}
        thumb = thumbnails.get("medium") or thumbnails.get("default") or thumbnails.get("high") or {}
        stats = details.get("statistics") or {}
        content = details.get("contentDetails") or {}
        results.append({
            "id": video_id,
            "title": detail_snippet.get("title") or "",
            "description": detail_snippet.get("description") or "",
            "channel_title": detail_snippet.get("channelTitle") or "",
            "published_at": detail_snippet.get("publishedAt") or "",
            "thumbnail_url": thumb.get("url") or "",
            "duration": content.get("duration") or "",
            "view_count": _to_int(stats.get("viewCount")),
            "url": f"https://www.youtube.com/watch?v={video_id}",
        })
    return results


async def _video_details(video_ids: list[str]) -> dict[str, dict[str, Any]]:
    if not video_ids:
        return {}
    payload = await _get_json(
        "videos",
        {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(video_ids[:50]),
        },
    )
    return {
        item.get("id"): item
        for item in payload.get("items") or []
        if item.get("id")
    }


async def _get_json(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    request_params = {**params, "key": _api_key()}
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(f"{_YOUTUBE_API}/{endpoint}", params=request_params)

    if response.status_code in {400, 401}:
        raise YouTubeAPIError("YouTube rejected the API key or request.")
    if response.status_code == 403:
        detail = _error_message(response)
        if "quota" in detail.lower():
            raise YouTubeAPIError("YouTube API quota is exhausted for this key.")
        raise YouTubeAPIError("YouTube API access is forbidden. Check that YouTube Data API v3 is enabled for this key.")
    if response.status_code >= 400:
        raise YouTubeAPIError(f"YouTube API returned HTTP {response.status_code}.")
    return response.json()


def _error_message(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text
    error = data.get("error") or {}
    return error.get("message") or str(error)


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

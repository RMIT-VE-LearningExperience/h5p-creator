from __future__ import annotations

import asyncio
import json
import re
from typing import Any
from xml.etree import ElementTree

import httpx

from app.core.config import settings


class YouTubeConfigError(RuntimeError):
    pass


class YouTubeAPIError(RuntimeError):
    pass


_YOUTUBE_API = "https://www.googleapis.com/youtube/v3"
_YOUTUBE_WATCH = "https://www.youtube.com/watch"


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


async def get_transcript(video_id: str) -> dict[str, Any]:
    video_id = (video_id or "").strip()
    if not re.fullmatch(r"[\w-]{6,20}", video_id):
        raise YouTubeAPIError("Invalid YouTube video ID.")

    packaged = await _get_transcript_with_package(video_id)
    if packaged is not None:
        return packaged

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        watch_response = await client.get(
            _YOUTUBE_WATCH,
            params={"v": video_id},
            headers={"Accept-Language": "en"},
        )
        if watch_response.status_code >= 400:
            raise YouTubeAPIError("Could not load YouTube video metadata.")

        track = _select_caption_track(watch_response.text)
        if not track:
            return {
                "video_id": video_id,
                "available": False,
                "language": None,
                "is_generated": None,
                "segments": [],
                "text": "",
                "message": "No transcript or captions were found for this video.",
            }

        transcript_url = _transcript_url(track.get("baseUrl") or "")
        transcript_response = await client.get(transcript_url)
        if transcript_response.status_code >= 400:
            raise YouTubeAPIError("Could not load the YouTube transcript.")

    segments = _parse_transcript(transcript_response.text)
    text = "\n".join(segment["text"] for segment in segments if segment.get("text"))
    return {
        "video_id": video_id,
        "available": bool(segments),
        "language": ((track.get("name") or {}).get("simpleText") or track.get("languageCode") or ""),
        "is_generated": track.get("kind") == "asr",
        "segments": segments,
        "text": text,
        "message": "" if segments else "No transcript text was available for this video.",
    }


async def _get_transcript_with_package(video_id: str) -> dict[str, Any] | None:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return None

    try:
        transcript = await asyncio.to_thread(
            lambda: YouTubeTranscriptApi().fetch(video_id, languages=["en"])
        )
    except Exception:
        return None

    segments = []
    for snippet in transcript:
        text = str(getattr(snippet, "text", "") or "").strip()
        if not text:
            continue
        start = float(getattr(snippet, "start", 0) or 0)
        duration = float(getattr(snippet, "duration", 0) or 0)
        segments.append({
            "start": round(start, 2),
            "duration": round(duration, 2),
            "time": _format_seconds(start),
            "text": re.sub(r"\s+", " ", text),
        })
    return {
        "video_id": video_id,
        "available": bool(segments),
        "language": getattr(transcript, "language", "English") or "English",
        "is_generated": bool(getattr(transcript, "is_generated", False)),
        "segments": segments,
        "text": "\n".join(segment["text"] for segment in segments),
        "message": "" if segments else "No transcript text was available for this video.",
    }


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


def _select_caption_track(page_html: str) -> dict[str, Any] | None:
    player_response = _extract_player_response(page_html)
    tracks = (
        player_response.get("captions", {})
        .get("playerCaptionsTracklistRenderer", {})
        .get("captionTracks", [])
    )
    if not tracks:
        return None
    english = [
        track for track in tracks
        if str(track.get("languageCode") or "").lower().startswith("en")
    ]
    candidates = english or tracks
    return next((track for track in candidates if track.get("kind") != "asr"), candidates[0])


def _extract_player_response(page_html: str) -> dict[str, Any]:
    patterns = [
        r"ytInitialPlayerResponse\s*=\s*({.+?});\s*</script>",
        r"ytInitialPlayerResponse\s*=\s*({.+?});",
    ]
    for pattern in patterns:
        match = re.search(pattern, page_html or "", re.DOTALL)
        if not match:
            continue
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
    return {}


def _transcript_url(base_url: str) -> str:
    if not base_url:
        raise YouTubeAPIError("Transcript track did not include a URL.")
    if "fmt=" in base_url:
        return base_url
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}fmt=json3"


def _parse_transcript(raw: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return _parse_xml_transcript(raw)

    segments = []
    for event in payload.get("events") or []:
        parts = event.get("segs") or []
        text = "".join(part.get("utf8") or "" for part in parts).strip()
        if not text:
            continue
        start_ms = int(event.get("tStartMs") or 0)
        duration_ms = int(event.get("dDurationMs") or 0)
        segments.append({
            "start": round(start_ms / 1000, 2),
            "duration": round(duration_ms / 1000, 2),
            "time": _format_seconds(start_ms / 1000),
            "text": re.sub(r"\s+", " ", text),
        })
    return segments


def _parse_xml_transcript(raw: str) -> list[dict[str, Any]]:
    try:
        root = ElementTree.fromstring(raw)
    except ElementTree.ParseError:
        return []
    segments = []
    for node in root.findall(".//text"):
        text = "".join(node.itertext()).strip()
        if not text:
            continue
        start = float(node.attrib.get("start") or 0)
        duration = float(node.attrib.get("dur") or 0)
        segments.append({
            "start": round(start, 2),
            "duration": round(duration, 2),
            "time": _format_seconds(start),
            "text": re.sub(r"\s+", " ", text),
        })
    return segments


def _format_seconds(value: float) -> str:
    total = max(0, int(value))
    hours, remainder = divmod(total, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


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

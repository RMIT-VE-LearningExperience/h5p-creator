from __future__ import annotations

import json
import re
from typing import Any

from app.core.config import settings


class CanvasChatConfigError(RuntimeError):
    pass


class CanvasChatError(RuntimeError):
    pass


_SYSTEM_PROMPT = """\
You answer questions about Canvas courses using only the supplied Canvas course
context. Be concise and practical. If the answer is not present in the context,
say what is missing and suggest what Canvas data would be needed. Do not invent
student names, private data, grades, or unpublished details that are not in the
context. Treat the data as read-only. If YouTube search results are supplied,
use them as app-provided candidates and explain why a candidate does or does not
match the Canvas page. Do not say the user must search YouTube manually when
YouTube results are present in the context. If embedded YouTube links are
supplied in the Canvas page context, prefer those exact links over search
results.
"""


def answer_course_question(question: str, courses: list[dict[str, Any]]) -> dict[str, str]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise CanvasChatConfigError("OpenAI SDK is not installed.") from exc

    if not courses:
        raise CanvasChatError("Search for or read at least one Canvas course before asking a question.")
    if not settings.val_api_key:
        raise CanvasChatConfigError("VAL_API_KEY is not configured.")

    model_name = settings.val_model
    client = OpenAI(api_key=settings.val_api_key, base_url=settings.val_base_url)
    context = _compact_courses(courses)
    user_content = "\n\n".join([
        "## Canvas course context",
        json.dumps(context, ensure_ascii=False, indent=2),
        "## Question",
        question.strip(),
    ])

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
    except Exception as exc:
        msg = str(exc)
        if any(x in msg for x in ("403", "Forbidden", "forbidden", "blocked", "unavailable")):
            raise CanvasChatError("VAL_NETWORK_ERROR") from exc
        raise CanvasChatError(f"VAL chat failed: {msg}") from exc

    answer = (response.choices[0].message.content or "").strip()
    if not answer:
        raise CanvasChatError("VAL returned no answer.")
    return {
        "answer": answer,
        "ai_provider": "val",
        "ai_model": model_name,
    }


_AQF_LABELS = {
    1: "AQF 1 (Certificate I)",
    2: "AQF 2 (Certificate II)",
    3: "AQF 3 (Certificate III)",
    4: "AQF 4 (Certificate IV)",
    5: "AQF 5 (Diploma)",
    6: "AQF 6 (Advanced Diploma / Associate Degree)",
    7: "AQF 7 (Bachelor Degree)",
    8: "AQF 8 (Bachelor Honours / Graduate Certificate/Diploma)",
    9: "AQF 9 (Masters Degree)",
    10: "AQF 10 (Doctoral Degree)",
}


def aqf_label(aqf_level: int | None) -> str | None:
    return _AQF_LABELS.get(aqf_level) if aqf_level else None


_AQF_SUGGESTION_SYSTEM_PROMPT = """\
Suggest the most likely Australian Qualifications Framework (AQF) level for the
given Canvas course. Use only the supplied course, module, and page metadata. Prefer
explicit qualification signals in the title first (Certificate I-IV, Diploma,
Advanced Diploma, Bachelor, Honours, Graduate Certificate/Diploma, Masters,
Doctoral), then infer from course/module/page language if needed. Return JSON:
{"aqf_level": <integer 1-10>, "reason": "<brief reason>"}.
"""


def suggest_aqf_level(course_context: dict[str, Any]) -> dict[str, Any]:
    heuristic = _heuristic_aqf_level(course_context)
    try:
        from openai import OpenAI
    except ImportError as exc:
        if heuristic:
            return heuristic
        raise CanvasChatConfigError("OpenAI SDK is not installed.") from exc
    if not settings.val_api_key:
        if heuristic:
            return heuristic
        raise CanvasChatConfigError("VAL_API_KEY is not configured.")

    model_name = settings.val_model
    client = OpenAI(api_key=settings.val_api_key, base_url=settings.val_base_url)
    user_content = json.dumps(compact_aqf_context(course_context), ensure_ascii=False, indent=2)

    try:
        response = client.chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _AQF_SUGGESTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
    except Exception as exc:
        if heuristic:
            return heuristic
        msg = str(exc)
        if any(x in msg for x in ("403", "Forbidden", "forbidden", "blocked", "unavailable")):
            raise CanvasChatError("VAL_NETWORK_ERROR") from exc
        raise CanvasChatError(f"VAL AQF suggestion failed: {msg}") from exc

    raw = (response.choices[0].message.content or "").strip()
    try:
        parsed = json.loads(raw)
        aqf_level = int(parsed.get("aqf_level"))
        reason = str(parsed.get("reason") or "").strip()
    except (TypeError, ValueError, AttributeError):
        if heuristic:
            return heuristic
        raise CanvasChatError("VAL returned no AQF suggestion.")
    if aqf_level < 1 or aqf_level > 10:
        if heuristic:
            return heuristic
        raise CanvasChatError("VAL returned an invalid AQF level.")
    return {
        "aqf_level": aqf_level,
        "aqf_label": _AQF_LABELS[aqf_level],
        "reason": reason or "Suggested from the Canvas course metadata.",
    }


def compact_aqf_context(course_context: dict[str, Any]) -> dict[str, Any]:
    course = course_context.get("course") or {}
    return {
        "course": {
            "name": course.get("name") or "",
            "course_code": course.get("course_code") or "",
        },
        "modules": [
            {"name": module.get("name") or ""}
            for module in (course_context.get("modules") or [])[:30]
        ],
        "pages": [
            {"title": page.get("title") or ""}
            for page in (course_context.get("pages") or [])[:50]
        ],
    }


def _heuristic_aqf_level(course_context: dict[str, Any]) -> dict[str, Any] | None:
    compact = compact_aqf_context(course_context)
    text = " ".join([
        compact["course"]["name"],
        compact["course"]["course_code"],
        *[item["name"] for item in compact["modules"]],
        *[item["title"] for item in compact["pages"]],
    ]).lower()
    patterns = [
        (10, r"\b(?:doctorate|doctoral|phd|ph\.d)\b", "doctoral course language"),
        (9, r"\b(?:master|masters|master's|postgraduate)\b", "masters or postgraduate course language"),
        (8, r"\b(?:honours|honors|graduate certificate|graduate diploma|grad cert|grad dip)\b", "honours or graduate certificate/diploma language"),
        (7, r"\b(?:bachelor|undergraduate|degree)\b", "bachelor degree language"),
        (6, r"\b(?:advanced diploma|associate degree)\b", "advanced diploma or associate degree language"),
        (5, r"\b(?:diploma)\b", "diploma language"),
        (4, r"\b(?:certificate iv|cert iv|certificate 4|cert 4)\b", "Certificate IV language"),
        (3, r"\b(?:certificate iii|cert iii|certificate 3|cert 3)\b", "Certificate III language"),
        (2, r"\b(?:certificate ii|cert ii|certificate 2|cert 2)\b", "Certificate II language"),
        (1, r"\b(?:certificate i|cert i|certificate 1|cert 1)\b", "Certificate I language"),
    ]
    for level, pattern, reason in patterns:
        if re.search(pattern, text):
            return {
                "aqf_level": level,
                "aqf_label": _AQF_LABELS[level],
                "reason": f"Suggested from {reason}.",
            }
    return None


_SLOT_DESCRIPTION_SYSTEM_PROMPT = """\
You write short Canvas course-page copy that introduces an embedded YouTube video.
Given a real video's title/description and its exact runtime, write ONE paragraph in
this exact style, replacing the bracketed parts with real content:
"Watch this (MM:SS mins) video to learn about ... <what the video actually covers>."
Use the runtime you are given verbatim - do not invent or alter it. Base what the video
covers only on the supplied title/description, do not invent details not evidenced
there. Match the tone of the original placeholder text if one is supplied. Return JSON:
{"description": "<the paragraph>"}.
"""


def generate_slot_description(
    video: dict[str, Any],
    duration_label: str,
    original_description: str,
    page_context: dict[str, Any],
    aqf_level: int | None = None,
) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise CanvasChatConfigError("OpenAI SDK is not installed.") from exc
    if not settings.val_api_key:
        raise CanvasChatConfigError("VAL_API_KEY is not configured.")

    model_name = settings.val_model
    client = OpenAI(api_key=settings.val_api_key, base_url=settings.val_base_url)
    user_content = json.dumps({
        "video": {
            "title": video.get("title") or "",
            "description": (video.get("description") or "")[:1500],
            "duration_label": duration_label,
        },
        "original_placeholder_description": original_description or "",
        "page_title": page_context.get("title") or "",
        "aqf_level": _AQF_LABELS.get(aqf_level) if aqf_level else None,
    }, ensure_ascii=False, indent=2)

    try:
        response = client.chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SLOT_DESCRIPTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
    except Exception as exc:
        msg = str(exc)
        if any(x in msg for x in ("401", "session has expired", "token is invalid")):
            raise CanvasChatError(
                "VAL authentication expired. The server credential needs to be refreshed."
            ) from exc
        if any(x in msg for x in ("403", "Forbidden", "forbidden", "blocked", "unavailable")):
            raise CanvasChatError("VAL_NETWORK_ERROR") from exc
        raise CanvasChatError(f"VAL description generation failed: {msg}") from exc

    raw = (response.choices[0].message.content or "").strip()
    try:
        parsed = json.loads(raw)
        description = str(parsed.get("description") or "").strip()
    except (ValueError, AttributeError):
        description = raw
    if not description:
        raise CanvasChatError("VAL returned no description.")
    return description


def fallback_slot_description(video: dict[str, Any], duration_label: str) -> str:
    title = re.sub(r"\s+", " ", str(video.get("title") or "")).strip().rstrip(".")
    topic = title or "the topic demonstrated"
    runtime = f" ({duration_label} mins)" if duration_label else ""
    return f"Watch this{runtime} video to learn about {topic}."


_SEARCH_QUERY_SYSTEM_PROMPT = """\
You write a single short, focused YouTube search query (5-10 words, no quotes, no
boolean operators) that would find a video matching what a Canvas course page is
actually about. You are given context at three levels - course and module give broad
subject framing, the page is what refines the query to the exact topic. Weight the
page content most heavily; use course/module only to disambiguate generic page text
(e.g. a page titled "Introduction" means little without knowing the course/module).
Ignore generic words like "watch", "video", "class", "week", or course administrivia.
If "additional_context" is supplied, treat it as an explicit instruction from the person
refining the search (e.g. "focus on a specific brand", "shorter video", "more about
X") and prioritise it over your own judgement of the page content. If an AQF level is
supplied, bias the query toward that complexity (e.g. lower AQF levels -> introductory/
basics framing, higher AQF levels -> advanced/professional framing) without making the
query longer or less searchable. Return JSON: {"query": "<the search query>"}.
"""


def generate_search_query(
    page_title: str,
    page_text: str,
    course_name: str = "",
    module_name: str = "",
    before_class_text: str = "",
    additional_context: str = "",
    aqf_level: int | None = None,
) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise CanvasChatConfigError("OpenAI SDK is not installed.") from exc
    if not settings.val_api_key:
        raise CanvasChatConfigError("VAL_API_KEY is not configured.")

    model_name = settings.val_model
    client = OpenAI(api_key=settings.val_api_key, base_url=settings.val_base_url)
    user_content = json.dumps({
        "course_name": course_name or "",
        "module_name": module_name or "",
        "page_title": page_title or "",
        "page_text": (page_text or "")[:6000],
        "before_class_text": (before_class_text or "")[:3000],
        "additional_context": (additional_context or "")[:1000],
        "aqf_level": _AQF_LABELS.get(aqf_level) if aqf_level else None,
    }, ensure_ascii=False, indent=2)

    try:
        response = client.chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SEARCH_QUERY_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
    except Exception as exc:
        msg = str(exc)
        if any(x in msg for x in ("403", "Forbidden", "forbidden", "blocked", "unavailable")):
            raise CanvasChatError("VAL_NETWORK_ERROR") from exc
        raise CanvasChatError(f"VAL search query generation failed: {msg}") from exc

    raw = (response.choices[0].message.content or "").strip()
    try:
        parsed = json.loads(raw)
        query = str(parsed.get("query") or "").strip()
    except (ValueError, AttributeError):
        query = raw
    if not query:
        raise CanvasChatError("VAL returned no search query.")
    return query


def _compact_courses(courses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compacted = []
    for item in courses[:10]:
        if "course" in item:
            course = item.get("course") or {}
            compacted.append({
                "course": course,
                "summary": item.get("summary") or {},
                "teachers": item.get("teachers") or [],
                "sections": item.get("sections") or [],
                "modules": (item.get("modules") or [])[:80],
                "assignments": (item.get("assignments") or [])[:80],
                "pages": (item.get("pages") or [])[:80],
                "discussions": (item.get("discussions") or [])[:50],
                "quizzes": (item.get("quizzes") or [])[:50],
                "files": (item.get("files") or [])[:10],
                "file_context": item.get("file_context") or "",
                "selected_page_bodies": (item.get("selected_page_bodies") or [])[:5],
                "youtube_search_results": (item.get("youtube_search_results") or [])[:8],
            })
        else:
            compacted.append({
                "course": {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "course_code": item.get("course_code"),
                    "workflow_state": item.get("workflow_state"),
                    "term": item.get("term"),
                    "total_students": item.get("total_students"),
                }
            })
    return compacted

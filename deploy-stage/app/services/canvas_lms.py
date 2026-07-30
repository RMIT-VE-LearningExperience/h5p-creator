from __future__ import annotations

import re
from contextvars import ContextVar, Token
from dataclasses import dataclass
from ipaddress import ip_address
from typing import Any
from urllib.parse import quote, urljoin, urlsplit

import httpx

from app.core.config import settings


class CanvasConfigError(RuntimeError):
    pass


class CanvasAPIError(RuntimeError):
    pass


@dataclass(frozen=True)
class CanvasCredentials:
    base_url: str
    api_token: str
    account_id: str | None = None
    source: str = "server"


_request_credentials: ContextVar[CanvasCredentials | None] = ContextVar(
    "canvas_request_credentials",
    default=None,
)


def credentials_from_user(base_url: str, api_token: str) -> CanvasCredentials:
    clean_url = _validate_canvas_base_url(base_url)
    clean_token = (api_token or "").strip()
    if not clean_token or "\n" in clean_token or "\r" in clean_token:
        raise CanvasConfigError("Enter a valid Canvas API token.")
    return CanvasCredentials(base_url=clean_url, api_token=clean_token, source="user")


def default_credentials() -> CanvasCredentials | None:
    if not settings.canvas_base_url or not settings.canvas_api_token:
        return None
    return CanvasCredentials(
        base_url=_validate_canvas_base_url(settings.canvas_base_url),
        api_token=settings.canvas_api_token,
        account_id=settings.canvas_account_id,
        source="server",
    )


def bind_request_credentials(credentials: CanvasCredentials | None) -> Token:
    return _request_credentials.set(credentials)


def reset_request_credentials(token: Token) -> None:
    _request_credentials.reset(token)


def current_credentials() -> CanvasCredentials:
    credentials = _request_credentials.get() or default_credentials()
    if credentials is None:
        raise CanvasConfigError("Connect your Canvas account to continue.")
    return credentials


def is_configured() -> bool:
    try:
        current_credentials()
        return True
    except CanvasConfigError:
        return False


_DEFAULT_COURSE_SEARCH_IDS = {86343, 95383, 118740}


def _client_headers() -> dict[str, str]:
    credentials = current_credentials()
    return {
        "Authorization": f"Bearer {credentials.api_token}",
        "Accept": "application/json",
    }


def _base_api_url() -> str:
    return urljoin(current_credentials().base_url.rstrip("/") + "/", "api/v1/")


def _validate_canvas_base_url(value: str) -> str:
    raw = (value or "").strip().rstrip("/")
    parsed = urlsplit(raw)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme != "https" or not hostname or parsed.username or parsed.password:
        raise CanvasConfigError("Canvas URL must be a valid HTTPS institution URL.")
    if parsed.query or parsed.fragment:
        raise CanvasConfigError("Canvas URL must not include a query string or fragment.")
    path = parsed.path.rstrip("/")
    if path not in {"", "/api/v1"}:
        raise CanvasConfigError("Enter the Canvas institution URL only, without a course or page path.")
    try:
        address = ip_address(hostname)
    except ValueError:
        address = None
    if address and (address.is_private or address.is_loopback or address.is_link_local or address.is_reserved):
        raise CanvasConfigError("Private or local Canvas hosts are not allowed.")

    allowed_hosts = {"instructure.com"}
    allowed_hosts.update(
        host.strip().lower().rstrip(".")
        for host in re.split(r"[\s,]+", settings.canvas_allowed_hosts or "")
        if host.strip()
    )
    if settings.canvas_base_url:
        configured_host = (urlsplit(settings.canvas_base_url).hostname or "").lower().rstrip(".")
        if configured_host:
            allowed_hosts.add(configured_host)
    if not any(hostname == host or hostname.endswith(f".{host}") for host in allowed_hosts):
        raise CanvasConfigError(
            "Canvas host is not approved. Use an *.instructure.com URL or ask the administrator to allow your institution host."
        )
    return f"https://{parsed.netloc}"


def _next_link(link_header: str | None) -> str | None:
    if not link_header:
        return None
    for part in link_header.split(","):
        match = re.match(r'\s*<([^>]+)>;\s*rel="([^"]+)"', part)
        if match and match.group(2) == "next":
            return match.group(1)
    return None


async def _get_json(path_or_url: str, params: dict[str, Any] | None = None) -> Any:
    url = path_or_url if path_or_url.startswith("http") else urljoin(_base_api_url(), path_or_url.lstrip("/"))
    async with httpx.AsyncClient(headers=_client_headers(), timeout=30.0) as client:
        response = await client.get(url, params=params)
    if response.status_code == 401:
        raise CanvasAPIError("Canvas rejected the API token.")
    if response.status_code == 403:
        raise CanvasAPIError("Canvas token does not have access to this course or account.")
    if response.status_code == 404:
        raise CanvasAPIError("Canvas resource was not found.")
    if response.status_code >= 400:
        raise CanvasAPIError(f"Canvas API returned HTTP {response.status_code}.")
    return response.json()


async def _put_json(path: str, json_body: dict[str, Any]) -> Any:
    url = urljoin(_base_api_url(), path.lstrip("/"))
    headers = {**_client_headers(), "Accept": "application/json"}
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        response = await client.put(url, json=json_body)
    if response.status_code == 401:
        raise CanvasAPIError("Canvas rejected the API token.")
    if response.status_code == 403:
        raise CanvasAPIError("Canvas token does not have permission to update this page.")
    if response.status_code == 404:
        raise CanvasAPIError("Canvas page was not found.")
    if response.status_code >= 400:
        raise CanvasAPIError(f"Canvas API returned HTTP {response.status_code}.")
    return response.json()


async def _post_json(path: str, json_body: dict[str, Any] | None = None) -> Any:
    url = urljoin(_base_api_url(), path.lstrip("/"))
    headers = {**_client_headers(), "Accept": "application/json"}
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        response = await client.post(url, json=json_body or {})
    if response.status_code == 401:
        raise CanvasAPIError("Canvas rejected the API token.")
    if response.status_code == 403:
        raise CanvasAPIError("Canvas token does not have permission for this action.")
    if response.status_code == 404:
        raise CanvasAPIError("Canvas resource was not found.")
    if response.status_code >= 400:
        raise CanvasAPIError(f"Canvas API returned HTTP {response.status_code}.")
    return response.json()


async def _get_bytes(path_or_url: str, params: dict[str, Any] | None = None) -> bytes:
    url = path_or_url if path_or_url.startswith("http") else urljoin(_base_api_url(), path_or_url.lstrip("/"))
    canvas_host = urlsplit(current_credentials().base_url).hostname
    download_host = urlsplit(url).hostname
    headers = _client_headers() if download_host == canvas_host else {"Accept": "application/octet-stream"}
    async with httpx.AsyncClient(headers=headers, timeout=60.0, follow_redirects=True) as client:
        response = await client.get(url, params=params)
    if response.status_code == 401:
        raise CanvasAPIError("Canvas rejected the API token.")
    if response.status_code == 403:
        raise CanvasAPIError("Canvas token does not have access to this file.")
    if response.status_code == 404:
        raise CanvasAPIError("Canvas file was not found.")
    if response.status_code >= 400:
        raise CanvasAPIError(f"Canvas file download returned HTTP {response.status_code}.")
    return response.content


async def _get_paginated(
    path: str,
    params: dict[str, Any] | None = None,
    limit: int | None = 100,
) -> list[dict[str, Any]]:
    url = urljoin(_base_api_url(), path.lstrip("/"))
    items: list[dict[str, Any]] = []
    request_params = dict(params or {})
    request_params.setdefault("per_page", min(limit, 100) if limit is not None else 100)
    async with httpx.AsyncClient(headers=_client_headers(), timeout=30.0) as client:
        while url and (limit is None or len(items) < limit):
            response = await client.get(url, params=request_params)
            request_params = None
            if response.status_code == 401:
                raise CanvasAPIError("Canvas rejected the API token.")
            if response.status_code == 403:
                raise CanvasAPIError("Canvas token does not have access to this course or account.")
            if response.status_code >= 400:
                raise CanvasAPIError(f"Canvas API returned HTTP {response.status_code}.")
            payload = response.json()
            if isinstance(payload, list):
                items.extend(item for item in payload if isinstance(item, dict))
            else:
                break
            url = _next_link(response.headers.get("link"))
    return items[:limit] if limit is not None else items


def _course_summary(course: dict[str, Any]) -> dict[str, Any]:
    term = course.get("term") or {}
    return {
        "id": course.get("id"),
        "name": course.get("name") or course.get("course_code") or f"Course {course.get('id')}",
        "course_code": course.get("course_code") or "",
        "workflow_state": course.get("workflow_state") or "",
        "start_at": course.get("start_at") or "",
        "end_at": course.get("end_at") or "",
        "term": {
            "id": term.get("id"),
            "name": term.get("name") or "",
        },
        "total_students": course.get("total_students"),
    }


async def search_courses(query: str, limit: int = 20) -> list[dict[str, Any]]:
    query = query.strip()
    if not query:
        return []

    params: dict[str, Any] = {
        "search_term": query,
        "include[]": ["term", "total_students"],
        "state[]": ["available", "completed", "unpublished"],
    }
    credentials = current_credentials()
    if credentials.account_id:
        path = f"accounts/{credentials.account_id}/courses"
        fetch_limit = max(1, min(limit * 3, 100))
    else:
        path = "courses"
        params.pop("state[]", None)
        fetch_limit = 500

    courses = await _get_paginated(path, params=params, limit=fetch_limit)
    summaries = [_course_summary(course) for course in courses]
    filtered = [course for course in summaries if _course_matches_query(course, query)]
    filtered.extend(await _search_known_course_ids(query, {course["id"] for course in filtered if course.get("id")}))
    filtered.sort(key=lambda course: _course_match_score(course, query), reverse=True)
    return filtered[:max(1, min(limit, 50))]


async def _search_known_course_ids(query: str, existing_ids: set[int]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for course_id in _known_course_search_ids():
        if course_id in existing_ids:
            continue
        try:
            course = await _get_json(
                f"courses/{course_id}",
                params={"include[]": ["term", "total_students"]},
            )
        except CanvasAPIError:
            continue
        summary = _course_summary(course)
        if _course_matches_query(summary, query):
            matches.append(summary)
    return matches


def _known_course_search_ids() -> list[int]:
    if current_credentials().source == "user":
        return []
    ids = set(_DEFAULT_COURSE_SEARCH_IDS)
    for value in re.split(r"[\s,]+", settings.canvas_course_search_ids or ""):
        if value.isdigit():
            ids.add(int(value))
    return sorted(ids)


async def get_current_user() -> dict[str, Any]:
    user = await _get_json("users/self")
    return {
        "id": user.get("id"),
        "name": user.get("name") or user.get("short_name") or "Canvas user",
        "login_id": user.get("login_id") or "",
    }


def _normalise_search_text(value: Any) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", str(value or "").lower())).strip()


def _course_search_text(course: dict[str, Any]) -> str:
    term = course.get("term") or {}
    return _normalise_search_text(" ".join([
        str(course.get("id") or ""),
        course.get("name") or "",
        course.get("course_code") or "",
        term.get("name") or "",
        course.get("workflow_state") or "",
    ]))


def _course_matches_query(course: dict[str, Any], query: str) -> bool:
    query_norm = _normalise_search_text(query)
    if not query_norm:
        return False
    haystack = _course_search_text(course)
    if query_norm in haystack:
        return True
    terms = query_norm.split()
    return all(term in haystack for term in terms)


def _course_match_score(course: dict[str, Any], query: str) -> int:
    query_norm = _normalise_search_text(query)
    name = _normalise_search_text(course.get("name"))
    code = _normalise_search_text(course.get("course_code"))
    haystack = _course_search_text(course)
    terms = query_norm.split()
    score = 0
    if str(course.get("id") or "") == query_norm:
        score += 1000
    if name == query_norm or code == query_norm:
        score += 500
    if name.startswith(query_norm) or code.startswith(query_norm):
        score += 250
    if query_norm in name or query_norm in code:
        score += 150
    score += sum(10 for term in terms if term in haystack)
    return score


async def read_course(course_id: int) -> dict[str, Any]:
    course = await _get_json(
        f"courses/{course_id}",
        params={
            "include[]": ["term", "sections", "teachers", "total_students", "course_image"],
        },
    )

    assignments = await _get_optional_list(
        f"courses/{course_id}/assignments",
        {"include[]": ["submission", "score_statistics"], "order_by": "position"},
        100,
    )
    modules = await _get_optional_list(
        f"courses/{course_id}/modules",
        {"include[]": ["items"]},
        None,
    )
    sections = await _get_optional_list(
        f"courses/{course_id}/sections",
        {"include[]": ["total_students"]},
        100,
    )
    discussions = await _get_optional_list(f"courses/{course_id}/discussion_topics", {"only_announcements": "false"}, 50)
    quizzes = await _get_optional_list(f"courses/{course_id}/quizzes", None, 50)
    pages = await _get_optional_list(
        f"courses/{course_id}/pages",
        {"sort": "title", "order": "asc"},
        None,
    )
    activity = await _get_optional_value(f"courses/{course_id}/analytics/activity", None)

    published_assignments = [item for item in assignments if item.get("published")]
    published_modules = [item for item in modules if item.get("published")]
    module_items = sum(len(item.get("items") or []) for item in modules)

    return {
        "course": _course_summary(course),
        "teachers": [
            {
                "id": teacher.get("id"),
                "display_name": teacher.get("display_name") or teacher.get("name") or "",
            }
            for teacher in course.get("teachers") or []
        ],
        "sections": [
            {
                "id": section.get("id"),
                "name": section.get("name") or "",
                "total_students": section.get("total_students"),
            }
            for section in sections
        ],
        "modules": [
            {
                "id": module.get("id"),
                "name": module.get("name") or "",
                "published": bool(module.get("published")),
                "items_count": len(module.get("items") or []),
                "items": [
                    {
                        "id": item.get("id"),
                        "title": item.get("title") or "",
                        "type": item.get("type") or "",
                        "content_id": item.get("content_id"),
                        "page_url": item.get("page_url") or "",
                        "html_url": item.get("html_url") or "",
                    }
                    for item in module.get("items") or []
                    if isinstance(item, dict)
                ],
            }
            for module in modules
        ],
        "assignments": [
            {
                "id": assignment.get("id"),
                "name": assignment.get("name") or "",
                "points_possible": assignment.get("points_possible"),
                "due_at": assignment.get("due_at") or "",
                "published": bool(assignment.get("published")),
                "has_submitted_submissions": bool(assignment.get("has_submitted_submissions")),
                "score_statistics": assignment.get("score_statistics") or {},
            }
            for assignment in assignments
        ],
        "pages": [
            {
                "title": page.get("title") or "",
                "url": page.get("url") or "",
                "published": bool(page.get("published")),
            }
            for page in pages
        ],
        "discussions": [
            {
                "id": discussion.get("id"),
                "title": discussion.get("title") or "",
                "posted_at": discussion.get("posted_at") or "",
                "published": not bool(discussion.get("unpublished")),
            }
            for discussion in discussions
        ],
        "quizzes": [
            {
                "id": quiz.get("id"),
                "title": quiz.get("title") or "",
                "due_at": quiz.get("due_at") or "",
                "published": bool(quiz.get("published")),
            }
            for quiz in quizzes
        ],
        "activity": activity if isinstance(activity, list) else [],
        "summary": {
            "assignments": len(assignments),
            "published_assignments": len(published_assignments),
            "modules": len(modules),
            "published_modules": len(published_modules),
            "module_items": module_items,
            "sections": len(sections),
            "pages": len(pages),
            "discussions": len(discussions),
            "quizzes": len(quizzes),
        },
    }


_READABLE_EXTENSIONS = {".pdf", ".pptx", ".docx"}


async def list_course_files(course_id: int, limit: int = 100) -> list[dict[str, Any]]:
    files = await _get_paginated(
        f"courses/{course_id}/files",
        params={"sort": "name", "order": "asc"},
        limit=max(1, min(limit, 200)),
    )
    readable = []
    for item in files:
        filename = item.get("filename") or item.get("display_name") or ""
        ext = _file_extension(filename)
        if ext not in _READABLE_EXTENSIONS:
            continue
        readable.append({
            "id": item.get("id"),
            "filename": filename,
            "display_name": item.get("display_name") or filename,
            "content_type": item.get("content-type") or item.get("content_type") or "",
            "size": item.get("size"),
            "updated_at": item.get("updated_at") or "",
            "extension": ext.lstrip("."),
        })
    return readable


async def download_file(file_id: int) -> tuple[dict[str, Any], bytes]:
    file_info = await _get_json(f"files/{file_id}")
    download_url = file_info.get("url")
    if not download_url:
        raise CanvasAPIError("Canvas did not return a download URL for this file.")
    return file_info, await _get_bytes(download_url)


async def read_page(course_id: int, page_url: str) -> dict[str, Any]:
    if not page_url:
        raise CanvasAPIError("Canvas page URL is missing.")
    encoded = quote(page_url, safe="")
    page = await _get_json(f"courses/{course_id}/pages/{encoded}")
    return {
        "title": page.get("title") or "",
        "url": page.get("url") or page_url,
        "published": bool(page.get("published")),
        "body": page.get("body") or "",
        "updated_at": page.get("updated_at") or "",
    }


async def update_page(course_id: int, page_url: str, body_html: str) -> dict[str, Any]:
    if not page_url:
        raise CanvasAPIError("Canvas page URL is missing.")
    encoded = quote(page_url, safe="")
    page = await _put_json(
        f"courses/{course_id}/pages/{encoded}",
        {"wiki_page": {"body": body_html}},
    )
    return {
        "title": page.get("title") or "",
        "url": page.get("url") or page_url,
        "published": bool(page.get("published")),
        "body": page.get("body") or "",
        "updated_at": page.get("updated_at") or "",
    }


async def list_page_revisions(course_id: int, page_url: str) -> list[dict[str, Any]]:
    if not page_url:
        raise CanvasAPIError("Canvas page URL is missing.")
    encoded = quote(page_url, safe="")
    revisions = await _get_json(f"courses/{course_id}/pages/{encoded}/revisions")
    if not isinstance(revisions, list):
        return []
    return [
        {
            "revision_id": revision.get("revision_id"),
            "updated_at": revision.get("updated_at") or "",
            "latest": bool(revision.get("latest")),
            "edited_by": (revision.get("edited_by") or {}).get("display_name") or "",
        }
        for revision in revisions
        if isinstance(revision, dict)
    ]


async def revert_page_to_revision(course_id: int, page_url: str, revision_id: int) -> dict[str, Any]:
    if not page_url:
        raise CanvasAPIError("Canvas page URL is missing.")
    encoded = quote(page_url, safe="")
    page = await _post_json(f"courses/{course_id}/pages/{encoded}/revisions/{revision_id}")
    return {
        "title": page.get("title") or "",
        "url": page.get("url") or page_url,
        "published": bool(page.get("published")),
        "body": page.get("body") or "",
        "updated_at": page.get("updated_at") or "",
    }


def _file_extension(filename: str) -> str:
    match = re.search(r"(\.[A-Za-z0-9]+)$", filename or "")
    return match.group(1).lower() if match else ""


async def _get_optional_list(
    path: str,
    params: dict[str, Any] | None,
    limit: int | None,
) -> list[dict[str, Any]]:
    try:
        return await _get_paginated(path, params=params, limit=limit)
    except CanvasAPIError:
        return []


async def _get_optional_value(path: str, params: dict[str, Any] | None) -> Any:
    try:
        return await _get_json(path, params=params)
    except CanvasAPIError:
        return None

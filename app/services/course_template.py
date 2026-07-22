from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services import canvas_lms


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value or "course").strip("-").lower()
    return slug or "course"


def _safe_filename(page_url: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", page_url or "page")
    return f"{slug}.html"


async def export_course_template(course_id: int) -> dict[str, Any]:
    """Read a Canvas course's full module/page structure, including raw page HTML."""
    course = await canvas_lms.read_course(course_id)

    pages: list[dict[str, Any]] = []
    for page_meta in course.get("pages") or []:
        page_url = page_meta.get("url") or ""
        if not page_url:
            continue
        page = await canvas_lms.read_page(course_id, page_url)
        pages.append({
            "title": page["title"],
            "url": page["url"],
            "published": page["published"],
            "body": page["body"],
        })

    modules = [
        {
            "id": module.get("id"),
            "name": module.get("name") or "",
            "published": bool(module.get("published")),
            "position": index,
            "items": module.get("items") or [],
        }
        for index, module in enumerate(course.get("modules") or [])
    ]

    return {
        "course_id": course_id,
        "course": course.get("course") or {},
        "modules": modules,
        "pages": pages,
    }


def save_course_template(
    snapshot: dict[str, Any],
    output_dir: Path,
    template_name: str = "",
    developed_by: str = "",
) -> Path:
    """Write a snapshot from export_course_template to disk: manifest.json + one .html file per page."""
    output_dir.mkdir(parents=True, exist_ok=True)
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    page_entries = []
    seen_filenames: set[str] = set()
    for page in snapshot["pages"]:
        filename = _safe_filename(page["url"])
        if filename in seen_filenames:
            filename = f"{page['url']}-{len(seen_filenames)}.html"
        seen_filenames.add(filename)
        (pages_dir / filename).write_text(page["body"] or "", encoding="utf-8")
        page_entries.append({
            "title": page["title"],
            "url": page["url"],
            "published": page["published"],
            "html_file": f"pages/{filename}",
            "character_count": len(page["body"] or ""),
        })

    manifest = {
        "course_id": snapshot["course_id"],
        "course_name": (snapshot.get("course") or {}).get("name") or "",
        "template_name": template_name,
        "developed_by": developed_by,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "modules": [
            {
                "id": module["id"],
                "name": module["name"],
                "published": module["published"],
                "position": module["position"],
                "items": [
                    {
                        "title": item.get("title") or "",
                        "type": item.get("type") or "",
                        "page_url": item.get("page_url") or "",
                    }
                    for item in module["items"]
                ],
            }
            for module in snapshot["modules"]
        ],
        "pages": page_entries,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path

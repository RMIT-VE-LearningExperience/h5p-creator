#!/usr/bin/env python3
"""Export a Canvas course's module/page structure as a reusable template snapshot.

Reads modules and every page's raw HTML from a Canvas course and saves them to
course_templates/<course-slug>/ as manifest.json + one .html file per page, so the
structure (e.g. a blended-learning template) can be tracked and referenced later
without touching the live Canvas course.

Usage:
    python3 scripts/export_course_template.py 170296 \
        --name "Blended Learning Template" --by "Kirsty Tod"
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services import course_template  # noqa: E402


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course_id", type=int)
    parser.add_argument("--name", default="", help="Template name, e.g. 'Blended Learning Template'")
    parser.add_argument("--by", default="", help="Who developed the template")
    parser.add_argument("--out", default=None, help="Output directory (default: course_templates/<slug>)")
    args = parser.parse_args()

    snapshot = await course_template.export_course_template(args.course_id)
    course_name = (snapshot.get("course") or {}).get("name") or f"course_{args.course_id}"
    slug = course_template.slugify(course_name)
    output_dir = Path(args.out) if args.out else Path("course_templates") / slug

    manifest_path = course_template.save_course_template(
        snapshot, output_dir, template_name=args.name, developed_by=args.by
    )
    print(f"Saved template to {manifest_path}")
    print(f"  {len(snapshot['modules'])} modules, {len(snapshot['pages'])} pages")


if __name__ == "__main__":
    asyncio.run(main())

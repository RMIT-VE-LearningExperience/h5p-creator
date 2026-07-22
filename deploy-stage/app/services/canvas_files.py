from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from app.services import canvas_lms, document_parser


@dataclass
class CanvasParsedFile:
    id: int
    filename: str
    extension: str
    title: str
    text: str
    document: document_parser.ParsedDocument


async def parse_canvas_file(file_id: int) -> CanvasParsedFile:
    file_info, data = await canvas_lms.download_file(file_id)
    filename = file_info.get("filename") or file_info.get("display_name") or f"canvas-file-{file_id}"
    ext = _extension(filename)
    if ext not in {".pdf", ".pptx", ".docx"}:
        raise ValueError("Only PDF, PowerPoint, and Word files can be parsed.")

    safe_name = re.sub(r"[^\w.\-]", "_", filename)
    with tempfile.NamedTemporaryFile(prefix="canvas-", suffix=ext, delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    try:
        doc = document_parser.parse_any(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    return CanvasParsedFile(
        id=file_id,
        filename=filename,
        extension=ext.lstrip("."),
        title=doc.title or safe_name,
        text=doc.raw_text,
        document=doc,
    )


async def parse_canvas_files(file_ids: list[int]) -> list[CanvasParsedFile]:
    parsed = []
    for file_id in file_ids[:10]:
        parsed.append(await parse_canvas_file(file_id))
    return parsed


def build_text_context(files: list[CanvasParsedFile], max_chars_per_file: int = 8000) -> str:
    blocks = []
    for item in files:
        text = (item.text or "").strip()
        if len(text) > max_chars_per_file:
            text = text[:max_chars_per_file].rstrip() + "\n[truncated]"
        blocks.append(f"## {item.filename}\n{text}")
    return "\n\n".join(blocks).strip()


def _extension(filename: str) -> str:
    return Path(filename).suffix.lower()

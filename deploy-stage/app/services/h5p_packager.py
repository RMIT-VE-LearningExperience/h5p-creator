"""Package H5P content JSON into a valid .h5p file (ZIP archive)."""
from __future__ import annotations
import io
import json
import zipfile
from typing import Any

from app.schemas.h5p_types import H5PResult

# Library dependency manifests keyed by mainLibrary
_DEPENDENCIES: dict[str, list[dict[str, Any]]] = {
    "H5P.MultiChoice": [
        {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16},
        {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
        {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
        {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
    ],
    "H5P.QuestionSet": [
        {"machineName": "H5P.QuestionSet", "majorVersion": 1, "minorVersion": 21},
        {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16},
        {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
        {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
        {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Video", "majorVersion": 1, "minorVersion": 6},
        {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
    ],
    "H5P.CoursePresentation": [
        {"machineName": "H5P.CoursePresentation", "majorVersion": 1, "minorVersion": 27},
        {"machineName": "H5P.AdvancedText", "majorVersion": 1, "minorVersion": 1},
        {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
        {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
    ],
}


def pack(result: H5PResult) -> bytes:
    """Return the raw bytes of a .h5p ZIP archive."""
    h5p_meta = {
        "title": result.title,
        "language": "en",
        "mainLibrary": result.content_type,
        "license": "U",
        "embedTypes": ["iframe"],
        "preloadedDependencies": _DEPENDENCIES.get(result.content_type, []),
    }

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("h5p.json", json.dumps(h5p_meta, ensure_ascii=False, indent=2))
        zf.writestr(
            "content/content.json",
            json.dumps(result.content, ensure_ascii=False, indent=2),
        )
    return buf.getvalue()

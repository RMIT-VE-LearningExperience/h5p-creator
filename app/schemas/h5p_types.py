from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel


class H5PResult(BaseModel):
    """Top-level output from the AI processor."""
    content_type: Literal["H5P.QuestionSet", "H5P.CoursePresentation"]
    title: str
    content: dict[str, Any]

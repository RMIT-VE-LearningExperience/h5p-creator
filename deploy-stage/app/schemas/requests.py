from pydantic import BaseModel
from typing import Literal


class GenerateRequest(BaseModel):
    activity_type: Literal["auto", "H5P.QuestionSet", "H5P.CoursePresentation", "H5P.MultiChoice"] = "auto"
    pass_percentage: int = 50


class GenerateResponse(BaseModel):
    filename: str
    content_type: str
    title: str
    download_path: str
    ai_provider: Literal["openai", "anthropic"]
    ai_model: str
    download_base64: str | None = None
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0


class PreviewSection(BaseModel):
    heading: str
    level: int
    category: Literal["question-bank", "mixed", "content", "reference"]
    paragraph_count: int
    list_count: int
    question_count: int
    sample_paragraphs: list[str]
    sample_list_items: list[str]


class BreakdownPlanResponse(BaseModel):
    title: str
    summary: str
    rationale: str
    suggested_activity_type: Literal["H5P.QuestionSet", "H5P.CoursePresentation"]
    section_start: int
    section_end: int
    section_count: int
    estimated_question_count: int
    estimated_slide_count: int
    headings: list[str]


class AnalyzeResponse(BaseModel):
    title: str
    suggested_activity_type: Literal["H5P.QuestionSet", "H5P.CoursePresentation"]
    is_large_document: bool
    breakdown_strategy: Literal["generate-directly", "split-by-question-groups", "split-by-major-heading"]
    section_count: int
    paragraph_count: int
    list_count: int
    question_like_section_count: int
    estimated_slide_count: int
    estimated_question_count: int
    suggestions: list[str]
    breakdown_plans: list[BreakdownPlanResponse]
    sections: list[PreviewSection]

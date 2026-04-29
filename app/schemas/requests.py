from pydantic import BaseModel
from typing import Any, Literal


class GenerateRequest(BaseModel):
    activity_type: Literal[
        "auto",
        "H5P.QuestionSet",
        "H5P.CoursePresentation",
        "H5P.SortParagraphs",
        "H5P.MultiChoice",
        "H5P.TrueFalse",
        "H5P.DragText",
        "H5P.Blanks",
        "H5P.GuessTheAnswer",
        "H5P.Summary",
    ] = "auto"
    pass_percentage: int = 100


class AnswerItem(BaseModel):
    text: str
    correct: bool


class ParagraphItem(BaseModel):
    id: str
    text_html: str


class QuestionItem(BaseModel):
    id: str
    title: str
    question_html: str
    answers: list[AnswerItem]
    library: str = "H5P.MultiChoice 1.16"


class GenerateResponse(BaseModel):
    filename: str
    content_type: str
    title: str
    download_path: str
    ai_provider: Literal["openai", "anthropic"]
    ai_model: str
    download_base64: str | None = None
    questions: list[QuestionItem] = []
    paragraphs: list[ParagraphItem] = []
    preview_fields: list[dict[str, str]] = []
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0


class ExportRequest(BaseModel):
    title: str
    content_type: str = "H5P.QuestionSet"
    pass_percentage: int = 100
    questions: list[QuestionItem] = []
    paragraphs: list[ParagraphItem] = []
    raw_content: dict[str, Any] | None = None


class ExportResponse(BaseModel):
    filename: str
    content_type: str
    download_base64: str


class BatchResultItem(BaseModel):
    activity_type: str
    title: str
    filename: str
    download_base64: str
    ai_provider: str
    ai_model: str
    input_tokens: int = 0
    output_tokens: int = 0
    preview_fields: list[dict[str, str]] = []
    questions: list[QuestionItem] = []
    paragraphs: list[ParagraphItem] = []


class BatchGenerateResponse(BaseModel):
    results: list[BatchResultItem]
    total_input_tokens: int = 0
    total_output_tokens: int = 0


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

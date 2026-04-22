from __future__ import annotations

from dataclasses import dataclass, field

from app.services.document_parser import ParsedDocument, Section


@dataclass
class SectionAnalysis:
    heading: str
    level: int
    category: str
    paragraph_count: int
    list_count: int
    question_count: int
    sample_paragraphs: list[str] = field(default_factory=list)
    sample_list_items: list[str] = field(default_factory=list)


@dataclass
class DocumentAnalysis:
    suggested_activity_type: str
    is_large_document: bool
    breakdown_strategy: str
    section_count: int
    paragraph_count: int
    list_count: int
    question_like_section_count: int
    estimated_slide_count: int
    estimated_question_count: int
    suggestions: list[str]
    breakdown_plans: list["BreakdownPlan"]
    sections: list[SectionAnalysis]


@dataclass
class BreakdownPlan:
    title: str
    summary: str
    rationale: str
    suggested_activity_type: str
    section_start: int
    section_end: int
    section_count: int
    estimated_question_count: int
    estimated_slide_count: int
    headings: list[str] = field(default_factory=list)


def analyze_document(doc: ParsedDocument) -> DocumentAnalysis:
    section_analyses = [_analyze_section(section) for section in doc.sections]
    section_count = len(doc.sections)
    paragraph_count = sum(len(section.paragraphs) for section in doc.sections)
    list_count = sum(len(section.lists) for section in doc.sections)
    question_like_section_count = sum(
        1 for section in section_analyses if section.category == "question-bank"
    )
    estimated_question_count = sum(section.question_count for section in section_analyses)
    estimated_slide_count = max(
        1,
        sum(
            1
            for section in doc.sections
            if section.heading or section.paragraphs or section.lists
        ),
    )

    suggested_activity_type = _suggest_activity_type(
        section_count=section_count,
        question_like_section_count=question_like_section_count,
        estimated_question_count=estimated_question_count,
    )
    is_large_document = (
        section_count >= 10
        or paragraph_count >= 25
        or estimated_question_count >= 15
        or len(doc.raw_text) >= 8000
    )

    suggestions: list[str] = []
    if not any(section.heading for section in doc.sections):
        suggestions.append(
            "Add Word heading styles to improve slide grouping and activity structure."
        )
    if is_large_document:
        suggestions.append(
            "This looks large. Consider splitting it into multiple activities by major heading."
        )
    if question_like_section_count and question_like_section_count < section_count:
        suggestions.append(
            "The document mixes instructional content and assessment items. A Course Presentation with separate quiz activities may be clearer."
        )
    if estimated_question_count >= 10:
        suggestions.append(
            "Large question sets are easier to review if questions are grouped by topic before generation."
        )
    if not suggestions:
        suggestions.append(
            "The document structure is clean enough to generate directly."
        )

    breakdown_strategy = _breakdown_strategy(
        is_large_document=is_large_document,
        question_like_section_count=question_like_section_count,
        section_count=section_count,
    )
    breakdown_plans = _build_breakdown_plans(
        doc=doc,
        section_analyses=section_analyses,
        is_large_document=is_large_document,
    )

    return DocumentAnalysis(
        suggested_activity_type=suggested_activity_type,
        is_large_document=is_large_document,
        breakdown_strategy=breakdown_strategy,
        section_count=section_count,
        paragraph_count=paragraph_count,
        list_count=list_count,
        question_like_section_count=question_like_section_count,
        estimated_slide_count=estimated_slide_count,
        estimated_question_count=estimated_question_count,
        suggestions=suggestions,
        breakdown_plans=breakdown_plans,
        sections=section_analyses,
    )


def _analyze_section(section: Section) -> SectionAnalysis:
    question_count = sum(1 for block in section.lists if len(block) >= 2)
    paragraph_count = len(section.paragraphs)
    list_count = len(section.lists)

    if question_count > 0 and paragraph_count == 0:
        category = "question-bank"
    elif question_count > 0 and paragraph_count > 0:
        category = "mixed"
    elif paragraph_count > 0:
        category = "content"
    else:
        category = "reference"

    sample_paragraphs = section.paragraphs[:2]
    sample_list_items = [item.text for block in section.lists[:2] for item in block[:3]]

    return SectionAnalysis(
        heading=section.heading or "Untitled section",
        level=max(section.level, 1),
        category=category,
        paragraph_count=paragraph_count,
        list_count=list_count,
        question_count=question_count,
        sample_paragraphs=sample_paragraphs,
        sample_list_items=sample_list_items,
    )


def _suggest_activity_type(
    *,
    section_count: int,
    question_like_section_count: int,
    estimated_question_count: int,
) -> str:
    if section_count == 0:
        return "H5P.QuestionSet"
    if question_like_section_count / section_count >= 0.5 or estimated_question_count >= 5:
        return "H5P.QuestionSet"
    return "H5P.CoursePresentation"


def _breakdown_strategy(
    *,
    is_large_document: bool,
    question_like_section_count: int,
    section_count: int,
) -> str:
    if not is_large_document:
        return "generate-directly"
    if question_like_section_count >= max(2, section_count // 2):
        return "split-by-question-groups"
    return "split-by-major-heading"


def _build_breakdown_plans(
    *,
    doc: ParsedDocument,
    section_analyses: list[SectionAnalysis],
    is_large_document: bool,
) -> list[BreakdownPlan]:
    if not section_analyses:
        return []

    groups = _group_sections(doc.sections, section_analyses, is_large_document)
    plans: list[BreakdownPlan] = []

    for start_index, end_index, grouped_sections in groups:
        headings = [
            section.heading or f"Section {index + 1}"
            for index, section in enumerate(doc.sections[start_index:end_index], start=start_index)
        ]
        grouped_analyses = section_analyses[start_index:end_index]
        estimated_question_count = sum(section.question_count for section in grouped_analyses)
        estimated_slide_count = max(1, len(grouped_sections))
        suggested_activity_type = _suggest_activity_type(
            section_count=len(grouped_analyses),
            question_like_section_count=sum(
                1 for section in grouped_analyses if section.category == "question-bank"
            ),
            estimated_question_count=estimated_question_count,
        )
        summary = _plan_summary(
            grouped_analyses=grouped_analyses,
            suggested_activity_type=suggested_activity_type,
        )

        plans.append(
            BreakdownPlan(
                title=_plan_title(grouped_sections, len(plans) + 1),
                summary=summary,
                rationale=_plan_rationale(grouped_analyses),
                suggested_activity_type=suggested_activity_type,
                section_start=start_index + 1,
                section_end=end_index,
                section_count=len(grouped_sections),
                estimated_question_count=estimated_question_count,
                estimated_slide_count=estimated_slide_count,
                headings=headings[:6],
            )
        )

    return plans


def _group_sections(
    sections: list[Section],
    section_analyses: list[SectionAnalysis],
    is_large_document: bool,
) -> list[tuple[int, int, list[Section]]]:
    if not is_large_document:
        return [(0, len(sections), sections)]

    major_heading_indexes = [
        index for index, section in enumerate(sections)
        if section.heading and section.level <= 2
    ]
    if len(major_heading_indexes) >= 3:
        boundaries = major_heading_indexes + [len(sections)]
        groups: list[tuple[int, int, list[Section]]] = []
        for boundary_index, start_index in enumerate(major_heading_indexes):
            end_index = boundaries[boundary_index + 1]
            groups.append((start_index, end_index, sections[start_index:end_index]))
        return groups

    target_size = 6
    groups = []
    for start_index in range(0, len(sections), target_size):
        end_index = min(len(sections), start_index + target_size)
        groups.append((start_index, end_index, sections[start_index:end_index]))
    return groups


def _plan_title(grouped_sections: list[Section], plan_number: int) -> str:
    first_heading = next((section.heading for section in grouped_sections if section.heading), "")
    if first_heading:
        return first_heading
    return f"Activity Part {plan_number}"


def _plan_summary(
    *,
    grouped_analyses: list[SectionAnalysis],
    suggested_activity_type: str,
) -> str:
    question_count = sum(section.question_count for section in grouped_analyses)
    paragraph_count = sum(section.paragraph_count for section in grouped_analyses)
    if suggested_activity_type == "H5P.QuestionSet":
        return f"Use this as a quiz-focused activity with about {question_count} question blocks."
    return f"Use this as a content-focused activity with about {paragraph_count} paragraph blocks."


def _plan_rationale(grouped_analyses: list[SectionAnalysis]) -> str:
    categories = {section.category for section in grouped_analyses}
    if categories == {"question-bank"}:
        return "This segment is assessment-heavy and should stay separate for easier review."
    if "mixed" in categories:
        return "This segment mixes explanation and questions, so it should be reviewed as a self-contained module."
    return "This segment is primarily content and will be easier to navigate as its own activity."

"""Package H5P content JSON into a valid .h5p file (ZIP archive)."""
from __future__ import annotations
import io
import json
import re
import uuid
import zipfile
from typing import Any

from app.schemas.h5p_types import H5PResult
from app.schemas.requests import AnswerItem, ParagraphItem, QuestionItem

# Library dependency manifests keyed by mainLibrary (order matches RMIT sample files)
_DEPENDENCIES: dict[str, list[dict[str, Any]]] = {
    # Verified against RMIT multiplechoice.h5p sample
    "H5P.MultiChoice": [
        {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
        {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
        {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10},
        {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
        {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16},
    ],
    # Verified against RMIT questionset.h5p sample
    "H5P.QuestionSet": [
        {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
        {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
        {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10},
        {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
        {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16},
        {"machineName": "H5P.TrueFalse", "majorVersion": 1, "minorVersion": 8},
        {"machineName": "H5P.Video", "majorVersion": 1, "minorVersion": 6},
        {"machineName": "H5P.QuestionSet", "majorVersion": 1, "minorVersion": 21},
    ],
    # No RMIT CoursePresentation sample — added Transition + jQuery.ui to match pattern
    "H5P.CoursePresentation": [
        {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
        {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
        {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10},
        {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.AdvancedText", "majorVersion": 1, "minorVersion": 1},
        {"machineName": "H5P.CoursePresentation", "majorVersion": 1, "minorVersion": 27},
    ],
    # Verified against RMIT sorttheparagraph.h5p sample
    "H5P.SortParagraphs": [
        {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
        {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
        {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10},
        {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
        {"machineName": "H5P.SortParagraphs", "majorVersion": 0, "minorVersion": 11},
    ],
    "H5P.TrueFalse": [
        {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
        {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
        {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10},
        {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
        {"machineName": "H5P.TrueFalse", "majorVersion": 1, "minorVersion": 8},
    ],
    "H5P.DragText": [
        {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
        {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
        {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10},
        {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
        {"machineName": "H5P.DragText", "majorVersion": 1, "minorVersion": 10},
    ],
    "H5P.Blanks": [
        {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
        {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
        {"machineName": "H5P.TextUtilities", "majorVersion": 1, "minorVersion": 3},
        {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10},
        {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
        {"machineName": "H5P.Blanks", "majorVersion": 1, "minorVersion": 14},
    ],
    "H5P.GuessTheAnswer": [
        {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10},
        {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Image", "majorVersion": 1, "minorVersion": 1},
        {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
        {"machineName": "H5P.GuessTheAnswer", "majorVersion": 1, "minorVersion": 5},
    ],
    "H5P.Summary": [
        {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
        {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
        {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10},
        {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
        {"machineName": "H5P.Summary", "majorVersion": 1, "minorVersion": 10},
    ],
}

# All RMIT sample files use embedTypes ["div"] — apply universally
_EMBED_TYPE = ["div"]

_SINGLE_ITEM_TYPES = frozenset({
    "H5P.TrueFalse", "H5P.DragText", "H5P.Blanks",
    "H5P.GuessTheAnswer", "H5P.Summary", "H5P.MultiChoice",
})


def extract_questions(result: H5PResult) -> list[QuestionItem]:
    """Parse a generated QuestionSet H5P result into a flat list of QuestionItems."""
    if result.content_type not in {"H5P.QuestionSet"}:
        return []
    items: list[QuestionItem] = []
    for q in result.content.get("questions", []):
        library: str = q.get("library", "H5P.MultiChoice 1.16")
        params = q.get("params", {})
        question_html: str = params.get("question", "")
        raw_title: str = (q.get("metadata") or {}).get("title", "")
        if not raw_title or raw_title.lower().startswith("untitled"):
            raw_title = _strip_html(question_html)
        title = raw_title[:80].rsplit(" ", 1)[0] if len(raw_title) > 80 else raw_title

        if library.startswith("H5P.TrueFalse"):
            correct_val = str(params.get("correct", "true")).lower()
            answers = [
                AnswerItem(text="True", correct=correct_val == "true"),
                AnswerItem(text="False", correct=correct_val == "false"),
            ]
        else:
            answers = [
                AnswerItem(text=_strip_html(a.get("text", "")), correct=bool(a.get("correct")))
                for a in params.get("answers", [])
            ]

        items.append(QuestionItem(
            id=q.get("subContentId") or str(uuid.uuid4()),
            title=title,
            question_html=question_html,
            answers=answers,
            library=library,
        ))
    return items


def extract_paragraphs(result: H5PResult) -> list[ParagraphItem]:
    """Parse a generated SortParagraphs H5P result into a flat list of ParagraphItems."""
    if result.content_type != "H5P.SortParagraphs":
        return []
    return [
        ParagraphItem(id=str(uuid.uuid4()), text_html=p if isinstance(p, str) else p.get("text", ""))
        for p in result.content.get("paragraphs", [])
    ]


def extract_preview_fields(result: H5PResult) -> list[dict[str, str]]:
    """Return display-ready label/value pairs for single-item content types."""
    ct = result.content_type
    c = result.content
    if ct == "H5P.TrueFalse":
        correct_val = str(c.get("correct", "true")).lower()
        return [
            {"label": "Question", "value": _strip_html(c.get("question", ""))},
            {"label": "Correct answer", "value": "True" if correct_val == "true" else "False"},
        ]
    if ct == "H5P.DragText":
        return [
            {"label": "Instructions", "value": _strip_html(c.get("taskDescription", ""))},
            {"label": "Text (draggable words in *asterisks*)", "value": c.get("textField", "")},
        ]
    if ct == "H5P.Blanks":
        return [
            {"label": "Instructions", "value": _strip_html(c.get("taskDescription", ""))},
            {"label": "Text (blanks in *asterisks*)", "value": _strip_html(c.get("text", ""))},
        ]
    if ct == "H5P.GuessTheAnswer":
        return [
            {"label": "Question", "value": _strip_html(c.get("taskDescription", ""))},
            {"label": "Answer (revealed on click)", "value": c.get("solutionText", "")},
        ]
    if ct == "H5P.Summary":
        fields: list[dict[str, str]] = [
            {"label": "Introduction", "value": _strip_html(c.get("intro", ""))},
        ]
        for i, group in enumerate(c.get("summaries", []), 1):
            statements = group.get("summary", [])
            if statements:
                fields.append({"label": f"Statement {i} (correct)", "value": _strip_html(statements[0])})
                for j, distractor in enumerate(statements[1:], 1):
                    fields.append({"label": f"Statement {i} distractor {j}", "value": _strip_html(distractor)})
        return fields
    if ct == "H5P.MultiChoice":
        fields = [{"label": "Question", "value": _strip_html(c.get("question", ""))}]
        for a in c.get("answers", []):
            tick = "✓" if a.get("correct") else "✗"
            fields.append({"label": f"Answer {tick}", "value": _strip_html(a.get("text", ""))})
        return fields
    return []


def pack_paragraphs(title: str, paragraphs: list[ParagraphItem]) -> bytes:
    """Build a .h5p archive from a list of ParagraphItems."""
    content = {
        "taskDescription": "<p>Sort the paragraphs into the correct order.</p>",
        "paragraphs": [p.text_html for p in paragraphs],
        "overallFeedback": {
            "overallFeedback": [{"from": 0, "to": 100, "feedback": ""}],
        },
        "behaviour": {
            "scoringMode": "positions",
            "applyPenalties": True,
            "duplicatesInterchangeable": True,
            "addButtonsForMovement": True,
            "enableRetry": True,
            "enableSolutionsButton": True,
        },
        "l10n": {
            "checkAnswer": "Check",
            "submitAnswer": "Submit",
            "tryAgain": "Retry",
            "showSolution": "Show solution",
            "up": "Up",
            "down": "Down",
            "disabled": "Disabled",
        },
    }
    return pack(H5PResult(content_type="H5P.SortParagraphs", title=title, content=content))


def pack_questions(title: str, content_type: str, questions: list[QuestionItem], pass_percentage: int) -> bytes:
    """Build a .h5p archive from a filtered list of QuestionItems."""
    if content_type == "H5P.QuestionSet":
        content = _build_question_set_content(questions, pass_percentage)
    else:
        raise ValueError(f"pack_questions does not support {content_type}")
    return pack(H5PResult(content_type=content_type, title=title, content=content))


def pack_raw(title: str, content_type: str, raw_content: dict[str, Any]) -> bytes:
    """Build a .h5p archive from a raw content dict (for single-item types)."""
    return pack(H5PResult(content_type=content_type, title=title, content=raw_content))  # type: ignore[arg-type]


def _build_question_set_content(questions: list[QuestionItem], pass_percentage: int) -> dict[str, Any]:
    entries = []
    for q in questions:
        if q.library.startswith("H5P.TrueFalse"):
            true_answer = next((a for a in q.answers if a.text == "True"), None)
            correct_val = "true" if (true_answer and true_answer.correct) else "false"
            entries.append({
                "library": "H5P.TrueFalse 1.8",
                "params": {
                    "question": q.question_html,
                    "correct": correct_val,
                    "behaviour": {
                        "enableRetry": True,
                        "enableSolutionsButton": True,
                        "enableCheckButton": True,
                        "confirmCheckDialog": False,
                        "confirmRetryDialog": False,
                        "autoCheck": False,
                    },
                    "l10n": {
                        "trueText": "True",
                        "falseText": "False",
                        "score": "You got @score of @total points",
                        "checkAnswer": "Check",
                        "submitAnswer": "Submit",
                        "showSolutionButton": "Show solution",
                        "tryAgain": "Retry",
                        "wrongAnswerMessage": "Wrong answer",
                        "correctAnswerMessage": "Correct answer",
                        "scoreBarLabel": "You got :num out of :total points",
                    },
                },
                "subContentId": q.id,
                "metadata": {"contentType": "True/False Question", "license": "U", "title": q.title or "Question"},
            })
        else:
            entries.append({
                "library": "H5P.MultiChoice 1.16",
                "params": {
                    "question": q.question_html,
                    "answers": [
                        {
                            "correct": a.correct,
                            "tipsAndFeedback": {
                                "tip": "",
                                "chosenFeedback": "<div>Correct!</div>" if a.correct else "<div>Incorrect.</div>",
                                "notChosenFeedback": "",
                            },
                            "text": f"<p>{a.text}</p>",
                        }
                        for a in q.answers
                    ],
                    "behaviour": {
                        "enableRetry": True, "enableSolutionsButton": True,
                        "enableCheckButton": True, "type": "auto", "singlePoint": False,
                        "randomAnswers": True, "showSolutionsRequiresInput": True,
                        "confirmCheckDialog": False, "confirmRetryDialog": False,
                        "autoCheck": False, "passPercentage": 100, "showScorePoints": True,
                    },
                    "UI": {"checkAnswerButton": "Check", "showSolutionButton": "Show solution", "tryAgainButton": "Retry"},
                    "media": {"disableImageZooming": False},
                },
                "subContentId": q.id,
                "metadata": {"contentType": "Multiple Choice", "license": "U", "title": q.title or "Question"},
            })
    return {
        "introPage": {"showIntroPage": False, "startButtonText": "Start Quiz", "title": "", "introduction": ""},
        "progressType": "dots",
        "passPercentage": pass_percentage,
        "questions": entries,
        "endGame": {
            "showResultPage": True, "showSolutionButton": True, "showRetryButton": True,
            "noResultMessage": "Finished", "message": "Your result:",
            "overallFeedback": [{"from": 0, "to": 100, "feedback": ""}],
            "solutionButtonText": "Show solution", "retryButtonText": "Retry",
            "finishButtonText": "Finish", "submitButtonText": "Submit",
            "showAnimations": False, "skippable": False, "skipButtonText": "Skip video",
        },
        "override": {"checkButton": True},
        "texts": {
            "prevButton": "Previous question", "nextButton": "Next question",
            "finishButton": "Finish", "textualProgress": "Question: @current of @total questions",
            "jumpToQuestion": "Question %d of %total", "questionLabel": "Question",
            "readSpeakerProgress": "Question @current of @total",
            "unansweredText": "Unanswered", "answeredText": "Answered",
            "currentQuestionText": "Current question",
        },
    }


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html).strip()


def pack(result: H5PResult) -> bytes:
    """Return the raw bytes of a .h5p ZIP archive."""
    h5p_meta = {
        "title": result.title,
        "language": "en",
        "mainLibrary": result.content_type,
        "license": "U",
        "embedTypes": _EMBED_TYPE,
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

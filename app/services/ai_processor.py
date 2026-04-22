"""Convert parsed Word document content into H5P JSON using Claude."""
from __future__ import annotations
import json
from dataclasses import dataclass

import anthropic

from app.core.config import settings
from app.schemas.h5p_types import H5PResult
from app.services.document_parser import ParsedDocument

# ---------------------------------------------------------------------------
# Cached system prompt — stable across all requests, caches after first use.
# Minimum 4 096 tokens required for Opus 4.7 prompt caching to activate.
# ---------------------------------------------------------------------------
_H5P_SYSTEM_PROMPT = """\
You are an expert H5P content creator who converts educational Word documents
into valid H5P JSON activities ready for import into rmit.h5p.com and use in
Canvas LMS.

H5P (HTML5 Package) is a framework for interactive learning content. You will
analyse a structured document representation and return a single JSON object.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTENT TYPE 1 — H5P.QuestionSet  (use for quizzes / assessments)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Choose this type when the document contains explicit questions followed by
answer options (e.g. numbered or bulleted lists under a question sentence).
Bold list items indicate correct answers.

Full JSON skeleton:
{
  "introPage": {
    "showIntroPage": false,
    "startButtonText": "Start Quiz",
    "title": "",
    "introduction": ""
  },
  "progressType": "dots",
  "passPercentage": 50,
  "questions": [
    {
      "library": "H5P.MultiChoice 1.16",
      "params": {
        "question": "<p>Question text</p>",
        "answers": [
          {
            "correct": true,
            "tipsAndFeedback": {
              "tip": "",
              "chosenFeedback": "<div>Correct!</div>",
              "notChosenFeedback": ""
            },
            "text": "<p>Correct answer</p>"
          },
          {
            "correct": false,
            "tipsAndFeedback": {
              "tip": "",
              "chosenFeedback": "<div>Incorrect.</div>",
              "notChosenFeedback": ""
            },
            "text": "<p>Wrong answer</p>"
          }
        ],
        "behaviour": {
          "enableRetry": true,
          "enableSolutionsButton": true,
          "enableCheckButton": true,
          "type": "auto",
          "singlePoint": false,
          "randomAnswers": true,
          "showSolutionsRequiresInput": true,
          "confirmCheckDialog": false,
          "confirmRetryDialog": false,
          "autoCheck": false,
          "passPercentage": 100,
          "showScorePoints": true
        },
        "UI": {
          "checkAnswerButton": "Check",
          "showSolutionButton": "Show solution",
          "tryAgainButton": "Retry"
        },
        "media": {"disableImageZooming": false}
      },
      "subContentId": "<uuid-v4>",
      "metadata": {
        "contentType": "Multiple Choice",
        "license": "U",
        "title": "Untitled Multiple Choice"
      }
    }
  ],
  "endGame": {
    "showResultPage": true,
    "showSolutionButton": true,
    "showRetryButton": true,
    "noResultMessage": "Finished",
    "message": "Your result:",
    "overallFeedback": [{"from": 0, "to": 100, "feedback": ""}],
    "solutionButtonText": "Show solution",
    "retryButtonText": "Retry",
    "finishButtonText": "Finish",
    "submitButtonText": "Submit",
    "showAnimations": false,
    "skippable": false,
    "skipButtonText": "Skip video"
  },
  "override": {"checkButton": true},
  "texts": {
    "prevButton": "Previous question",
    "nextButton": "Next question",
    "finishButton": "Finish",
    "textualProgress": "Question: @current of @total questions",
    "jumpToQuestion": "Question %d of %total",
    "questionLabel": "Question",
    "readSpeakerProgress": "Question @current of @total",
    "unansweredText": "Unanswered",
    "answeredText": "Answered",
    "currentQuestionText": "Current question"
  }
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTENT TYPE 2 — H5P.CoursePresentation  (use for slide-based content)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Choose this type when the document is structured as sections / topics / slides
containing explanatory text, definitions, or instructional content.

Each H1/H2 heading maps to one slide. Paragraphs under a heading become the
slide body text.

Full JSON skeleton:
{
  "presentation": {
    "slides": [
      {
        "elements": [
          {
            "x": 1.5,
            "y": 2,
            "width": 97,
            "height": 15,
            "action": {
              "library": "H5P.AdvancedText 1.1",
              "params": {"text": "<h2>Slide Title</h2>"},
              "subContentId": "<uuid-v4>",
              "metadata": {
                "contentType": "Text",
                "license": "U",
                "title": "Untitled Text"
              }
            },
            "alwaysDisplayComments": false,
            "backgroundOpacity": 0,
            "displayAsButton": false,
            "buttonSize": "big",
            "goToSlideType": "specified",
            "invisible": false,
            "solution": ""
          },
          {
            "x": 1.5,
            "y": 20,
            "width": 97,
            "height": 70,
            "action": {
              "library": "H5P.AdvancedText 1.1",
              "params": {"text": "<p>Slide body content here.</p>"},
              "subContentId": "<uuid-v4>",
              "metadata": {
                "contentType": "Text",
                "license": "U",
                "title": "Untitled Text"
              }
            },
            "alwaysDisplayComments": false,
            "backgroundOpacity": 0,
            "displayAsButton": false,
            "buttonSize": "big",
            "goToSlideType": "specified",
            "invisible": false,
            "solution": ""
          }
        ],
        "slideBackgroundSelector": {}
      }
    ],
    "globalBackgroundSelector": {},
    "keywordListEnabled": true,
    "keywordListAlwaysShow": false,
    "keywordListAutoHide": false,
    "keywordListOpacity": 90
  }
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONVERSION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. H1 heading → document title and first slide title (or quiz title)
2. H2/H3 headings → section breaks / question categories / slide titles
3. Paragraphs under a heading → slide body or question context
4. Bulleted or numbered list items → MultiChoice answer options
5. Bold list items → correct answers (set "correct": true)
6. If there are NO bold items in a list, mark only the first item correct
7. All text must be wrapped in HTML tags: <p>, <h2>, <ul><li>, etc.
8. Replace every <uuid-v4> placeholder with a real UUID v4 string
9. passPercentage should use the value provided by the caller
10. When activity_type is "auto":
    - Prefer QuestionSet if >50% of sections contain question-style lists
    - Prefer CoursePresentation otherwise

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT  (CRITICAL — follow exactly)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Return ONLY a single JSON object — no markdown fences, no explanation, no
extra keys. The object must have exactly these three top-level keys:

{
  "content_type": "H5P.QuestionSet",      ← or "H5P.CoursePresentation"
  "title": "Human-readable activity title",
  "content": { ... complete H5P content JSON as shown above ... }
}

If the document is empty or unrecognisable, return:
{"content_type": "H5P.QuestionSet", "title": "Empty Activity", "content": {}}
"""


@dataclass
class ProcessorResult:
    h5p: H5PResult
    cache_read_tokens: int
    cache_write_tokens: int
    input_tokens: int
    output_tokens: int


def process_document(
    doc: ParsedDocument,
    activity_type: str = "auto",
    pass_percentage: int = 50,
) -> ProcessorResult:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    user_content = _build_user_message(doc, activity_type, pass_percentage)

    with client.messages.stream(
        model=settings.anthropic_model,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=[
            {
                "type": "text",
                "text": _H5P_SYSTEM_PROMPT,
                # Cache this large stable schema definition
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_content}],
    ) as stream:
        final = stream.get_final_message()

    text_block = next(
        (b for b in final.content if b.type == "text"), None
    )
    if text_block is None:
        raise ValueError("Claude returned no text content")

    raw_json = text_block.text.strip()
    # Strip accidental markdown fences if present
    if raw_json.startswith("```"):
        raw_json = raw_json.split("```")[1]
        if raw_json.startswith("json"):
            raw_json = raw_json[4:]
        raw_json = raw_json.strip()

    data = json.loads(raw_json)
    h5p_result = H5PResult(**data)

    usage = final.usage
    return ProcessorResult(
        h5p=h5p_result,
        cache_read_tokens=getattr(usage, "cache_read_input_tokens", 0) or 0,
        cache_write_tokens=getattr(usage, "cache_creation_input_tokens", 0) or 0,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
    )


def _build_user_message(
    doc: ParsedDocument,
    activity_type: str,
    pass_percentage: int,
) -> str:
    lines: list[str] = [
        f"activity_type: {activity_type}",
        f"pass_percentage: {pass_percentage}",
        "",
        "## Document structure",
        f"Title: {doc.title}",
        "",
    ]

    for section in doc.sections:
        if section.heading:
            lines.append(f"{'#' * max(section.level, 1)} {section.heading}")
        for para in section.paragraphs:
            lines.append(para)
        for lst in section.lists:
            for item in lst:
                prefix = "**" if item.is_bold else "-"
                suffix = "**" if item.is_bold else ""
                lines.append(f"{prefix} {item.text}{suffix}")
        lines.append("")

    return "\n".join(lines)

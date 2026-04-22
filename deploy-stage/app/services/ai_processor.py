"""Convert parsed Word document content into H5P JSON using OpenAI or Anthropic."""
from __future__ import annotations
from dataclasses import dataclass

from app.core.config import settings
from app.schemas.h5p_types import H5PResult
from app.services.document_parser import ParsedDocument

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
CONTENT TYPE 2 — H5P.MultiChoice  (use for a single standalone question)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Choose this type when the caller explicitly requests a single multiple choice
activity or when the document contains one primary question with answer options.

Full JSON skeleton:
{
  "question": "<p>Question text</p>",
  "answers": [
    {
      "text": "<p>Correct answer</p>",
      "correct": true,
      "tipsAndFeedback": {
        "tip": "",
        "chosenFeedback": "<div>Correct!</div>",
        "notChosenFeedback": ""
      }
    },
    {
      "text": "<p>Wrong answer</p>",
      "correct": false,
      "tipsAndFeedback": {
        "tip": "",
        "chosenFeedback": "<div>Incorrect.</div>",
        "notChosenFeedback": ""
      }
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
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTENT TYPE 3 — H5P.CoursePresentation  (use for slide-based content)
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
DOCUMENT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The user message marks question blocks explicitly:

  QUESTION: <question text>
    [CORRECT] <correct answer>
    [ ] <wrong answer>
    [ ] <wrong answer>

Each QUESTION: block is one question. You MUST create one entry in the
questions array for EVERY QUESTION: block — do not skip or merge any.
Unmarked paragraphs are explanatory context, not questions.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONVERSION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. H1 heading → document title
2. H2/H3 headings → section breaks / question categories / slide titles
3. Each QUESTION: block → one question entry in the questions array (QuestionSet)
   or one slide (CoursePresentation)
4. [CORRECT] items → "correct": true in the answer object
5. [ ] items → "correct": false in the answer object
6. If no [CORRECT] items exist in a block, mark only the first option correct
7. All text must be wrapped in HTML tags: <p>, <h2>, <ul><li>, etc.
8. Replace every <uuid-v4> placeholder with a real UUID v4 string
9. passPercentage should use the value provided by the caller
10. When activity_type is "auto":
    - Prefer QuestionSet if any QUESTION: blocks are present
    - Prefer CoursePresentation for purely explanatory documents
11. When activity_type is "H5P.QuestionSet", return H5P.QuestionSet exactly
12. When activity_type is "H5P.CoursePresentation", return H5P.CoursePresentation exactly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT  (CRITICAL — follow exactly)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Return ONLY a single JSON object — no markdown fences, no explanation, no
extra keys. The object must have exactly these three top-level keys:

{
  "content_type": "H5P.QuestionSet",      ← or "H5P.MultiChoice" or "H5P.CoursePresentation"
  "title": "Human-readable activity title",
  "content": { ... complete H5P content JSON as shown above ... }
}

If the document is empty or unrecognisable, return:
{"content_type": "H5P.QuestionSet", "title": "Empty Activity", "content": {}}
"""


@dataclass
class ProcessorResult:
    h5p: H5PResult
    ai_provider: str
    model_used: str
    cache_read_tokens: int
    cache_write_tokens: int
    input_tokens: int
    output_tokens: int


def process_document(
    doc: ParsedDocument,
    ai_provider: str,
    activity_type: str = "auto",
    pass_percentage: int = 50,
    model_override: str | None = None,
) -> ProcessorResult:
    provider = ai_provider.lower().strip()
    user_content = _build_user_message(
        doc,
        activity_type,
        pass_percentage,
        force_requested_type=activity_type != "auto",
    )

    if provider == "openai":
        result = _process_with_openai(user_content, model_override)
        return _validate_or_retry(
            result=result,
            provider=provider,
            doc=doc,
            activity_type=activity_type,
            pass_percentage=pass_percentage,
            model_override=model_override,
        )
    if provider == "anthropic":
        result = _process_with_anthropic(user_content, model_override)
        return _validate_or_retry(
            result=result,
            provider=provider,
            doc=doc,
            activity_type=activity_type,
            pass_percentage=pass_percentage,
            model_override=model_override,
        )
    raise ValueError("Unsupported AI provider")


def _process_with_openai(user_content: str, model_override: str | None) -> ProcessorResult:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ValueError("OpenAI SDK is not installed. Install dependencies again.") from exc

    model_name = model_override or settings.openai_model
    client = OpenAI(api_key=settings.openai_api_key)

    response = client.chat.completions.create(
        model=model_name,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _H5P_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )

    raw_json = _strip_markdown_fences((response.choices[0].message.content or "").strip())
    if not raw_json:
        raise ValueError("OpenAI returned no text output")
    h5p_result = H5PResult.model_validate_json(raw_json)

    usage = getattr(response, "usage", None)
    return ProcessorResult(
        h5p=h5p_result,
        ai_provider="openai",
        model_used=model_name,
        cache_read_tokens=0,
        cache_write_tokens=0,
        input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
        output_tokens=getattr(usage, "completion_tokens", 0) or 0,
    )


def _process_with_anthropic(user_content: str, model_override: str | None) -> ProcessorResult:
    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY is not configured")

    try:
        import anthropic
    except ImportError as exc:
        raise ValueError("Anthropic SDK is not installed. Install dependencies again.") from exc

    model_name = model_override or settings.anthropic_model
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    with client.messages.stream(
        model=model_name,
        max_tokens=16000,
        system=[
            {
                "type": "text",
                "text": _H5P_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_content}],
    ) as stream:
        final = stream.get_final_message()

    text_block = next((block for block in final.content if block.type == "text"), None)
    if text_block is None:
        raise ValueError("Anthropic returned no text content")

    raw_json = _strip_markdown_fences(text_block.text.strip())
    h5p_result = H5PResult.model_validate_json(raw_json)
    usage = final.usage

    return ProcessorResult(
        h5p=h5p_result,
        ai_provider="anthropic",
        model_used=model_name,
        cache_read_tokens=getattr(usage, "cache_read_input_tokens", 0) or 0,
        cache_write_tokens=getattr(usage, "cache_creation_input_tokens", 0) or 0,
        input_tokens=getattr(usage, "input_tokens", 0) or 0,
        output_tokens=getattr(usage, "output_tokens", 0) or 0,
    )


def _build_user_message(
    doc: ParsedDocument,
    activity_type: str,
    pass_percentage: int,
    force_requested_type: bool = False,
) -> str:
    lines: list[str] = [
        f"activity_type: {activity_type}",
        f"pass_percentage: {pass_percentage}",
        "",
        "## Document structure",
        f"Title: {doc.title}",
        "",
    ]

    if force_requested_type:
        lines.extend(
            [
                "## Required output type",
                f"You MUST return content_type exactly {activity_type}.",
                "Do not auto-select a different H5P type.",
                "",
            ]
        )

    for section in doc.sections:
        if section.heading:
            lines.append(f"{'#' * max(section.level, 1)} {section.heading}")

        # Pair each paragraph with the list that follows it when counts match —
        # this is the question-text + answer-options pattern.
        paired = (
            len(section.paragraphs) == len(section.lists) and section.paragraphs
        )
        if paired:
            for para, lst in zip(section.paragraphs, section.lists):
                lines.append(f"QUESTION: {para}")
                for item in lst:
                    marker = "[CORRECT]" if item.is_bold else "[ ]"
                    lines.append(f"  {marker} {item.text}")
                lines.append("")
        else:
            # Heading-as-question: one heading with a single answer list
            if not section.paragraphs and len(section.lists) == 1 and section.heading:
                lines.append(f"QUESTION: {section.heading}")
                for item in section.lists[0]:
                    marker = "[CORRECT]" if item.is_bold else "[ ]"
                    lines.append(f"  {marker} {item.text}")
                lines.append("")
            else:
                for para in section.paragraphs:
                    lines.append(para)
                for lst in section.lists:
                    for item in lst:
                        marker = "[CORRECT]" if item.is_bold else "[ ]"
                        lines.append(f"  {marker} {item.text}")
                lines.append("")

    return "\n".join(lines)


def _strip_markdown_fences(raw_json: str) -> str:
    if raw_json.startswith("```"):
        raw_json = raw_json.split("```")[1]
        if raw_json.startswith("json"):
            raw_json = raw_json[4:]
        raw_json = raw_json.strip()
    return raw_json


def _validate_requested_type(result: ProcessorResult, activity_type: str) -> ProcessorResult:
    if activity_type != "auto" and result.h5p.content_type != activity_type:
        raise ValueError(
            f"Requested {activity_type} but model returned {result.h5p.content_type}"
        )
    return result


def _validate_or_retry(
    *,
    result: ProcessorResult,
    provider: str,
    doc: ParsedDocument,
    activity_type: str,
    pass_percentage: int,
    model_override: str | None,
) -> ProcessorResult:
    if activity_type == "auto" or result.h5p.content_type == activity_type:
        return result

    retry_user_content = _build_user_message(
        doc,
        activity_type,
        pass_percentage,
        force_requested_type=True,
    )

    if provider == "openai":
        retry_result = _process_with_openai(retry_user_content, model_override)
    elif provider == "anthropic":
        retry_result = _process_with_anthropic(retry_user_content, model_override)
    else:
        raise ValueError("Unsupported AI provider")

    return _validate_requested_type(retry_result, activity_type)

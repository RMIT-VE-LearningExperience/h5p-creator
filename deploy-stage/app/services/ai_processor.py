"""Convert parsed Word document content into H5P JSON using OpenAI or Anthropic."""
from __future__ import annotations
import re
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
QuestionSet may contain a MIX of H5P.MultiChoice 1.16 and H5P.TrueFalse 1.8
questions — use TrueFalse when a statement has a clear true/false answer.

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
        "title": "First 60 chars of question text (HTML stripped)"
      }
    },
    {
      "library": "H5P.TrueFalse 1.8",
      "params": {
        "question": "<p>Statement to judge as true or false</p>",
        "correct": "true",
        "behaviour": {
          "enableRetry": true,
          "enableSolutionsButton": true,
          "enableCheckButton": true,
          "confirmCheckDialog": false,
          "confirmRetryDialog": false,
          "autoCheck": false
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
          "scoreBarLabel": "You got :num out of :total points"
        }
      },
      "subContentId": "<uuid-v4>",
      "metadata": {
        "contentType": "True/False Question",
        "license": "U",
        "title": "First 60 chars of statement text (HTML stripped)"
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
CONTENT TYPE 4 — H5P.SortParagraphs  (use for sequencing / ordering tasks)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Choose this type ONLY when activity_type is "H5P.SortParagraphs".
Never auto-select it. Best for procedural steps, chronological events, or
logically ordered arguments where sequence matters.

Each body paragraph in the document becomes one paragraph entry. The order
in the array IS the correct answer order. Include 3–12 paragraphs.

STRICT RULES for paragraph text:
- NEVER begin a paragraph with a number, letter, or named label such as
  "Rule 1:", "Step 2:", "Phase 3.", "1.", "a)". Remove them entirely.
  The learner must not be able to sort by scanning for numbers — the
  meaning of the text alone must reveal the correct order.
- Keep each paragraph to 1–3 sentences maximum. If a source paragraph
  is longer, condense it to its single key point. Long paragraphs make
  the activity unreadable on screen.
- Write in plain prose — no sub-lists or bullet points inside a paragraph.

Full JSON skeleton:
{
  "taskDescription": "<p>Sort the paragraphs into the correct order.</p>",
  "paragraphs": [
    "<p>First step or event in correct order</p>",
    "<p>Second step or event</p>",
    "<p>Third step or event</p>"
  ],
  "overallFeedback": {
    "overallFeedback": [{"from": 0, "to": 100, "feedback": ""}]
  },
  "behaviour": {
    "scoringMode": "positions",
    "applyPenalties": true,
    "duplicatesInterchangeable": true,
    "addButtonsForMovement": true,
    "enableRetry": true,
    "enableSolutionsButton": true
  },
  "l10n": {
    "checkAnswer": "Check",
    "submitAnswer": "Submit",
    "tryAgain": "Retry",
    "showSolution": "Show solution",
    "up": "Up",
    "down": "Down",
    "disabled": "Disabled"
  }
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTENT TYPE 5 — H5P.TrueFalse  (use for a single true/false statement)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Choose this type ONLY when activity_type is "H5P.TrueFalse".
Pick one clear factual statement from the document. The learner must judge
whether it is true or false. IMPORTANT: "correct" must be the lowercase
string "true" or "false" — never a boolean.

Full JSON skeleton:
{
  "question": "<p>A clear factual statement from the document.</p>",
  "correct": "true",
  "behaviour": {
    "enableRetry": true,
    "enableSolutionsButton": true,
    "enableCheckButton": true,
    "confirmCheckDialog": false,
    "confirmRetryDialog": false,
    "autoCheck": false
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
    "a11yCheck": "Check the answers. The responses will be marked as correct, incorrect, or unanswered.",
    "a11yShowSolution": "Show the solution. The task will be marked with its correct solution.",
    "a11yRetry": "Retry the task. Reset all responses and start the task over again."
  },
  "confirmCheck": {
    "header": "Finish ?",
    "body": "Are you sure you wish to finish ?",
    "cancelLabel": "Cancel",
    "confirmLabel": "Finish"
  },
  "confirmRetry": {
    "header": "Retry ?",
    "body": "Are you sure you wish to retry ?",
    "cancelLabel": "Cancel",
    "confirmLabel": "Confirm"
  }
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTENT TYPE 6 — H5P.DragText  (use for drag the words)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Choose this type ONLY when activity_type is "H5P.DragText".
Extract 1–3 key sentences from the document. Mark 3–6 significant words
with asterisks: *word*. These become the draggable tokens that learners
drag into the correct blanks.
Syntax: *word* for a draggable word. *word:hint* to add a hint tooltip.
Do NOT mark trivial words (the, a, is) — mark key terms, names, numbers.

Full JSON skeleton:
{
  "taskDescription": "<p>Drag the correct words into the blanks.</p>",
  "textField": "The key sentence with *draggable* words *marked* with asterisks.",
  "overallFeedback": [{"from": 0, "to": 100, "feedback": ""}],
  "behaviour": {
    "enableRetry": true,
    "enableSolutionsButton": true,
    "instantFeedback": false,
    "enableCheckButton": true
  },
  "media": {"disableImageZooming": false},
  "checkAnswer": "Check",
  "submitAnswer": "Submit",
  "tryAgain": "Retry",
  "showSolution": "Show solution",
  "dropZoneIndex": "Drop Zone @index.",
  "empty": "Drop Zone @index is empty.",
  "contains": "Drop Zone @index contains draggable @draggable.",
  "ariaDraggableIndex": "@index of @count draggables.",
  "tipLabel": "Show tip",
  "correctText": "Correct!",
  "incorrectText": "Incorrect!",
  "resetDropTitle": "Reset drop",
  "resetDropDescription": "Are you sure you want to reset this drop zone?",
  "grabbed": "Draggable is grabbed.",
  "cancelledDragging": "Cancelled dragging.",
  "correctAnswer": "Correct answer:",
  "feedbackHeader": "Feedback",
  "scoreBarLabel": "You got :num out of :total points",
  "a11yCheck": "Check the answers. The responses will be marked as correct, incorrect, or unanswered.",
  "a11yShowSolution": "Show the solution. The task will be marked with its correct solution.",
  "a11yRetry": "Retry the task. Reset all responses and start the task over again."
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTENT TYPE 7 — H5P.Blanks  (use for fill in the blanks)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Choose this type ONLY when activity_type is "H5P.Blanks".
Write a passage of 3–8 sentences drawn from the document content. Remove
5–10 key terms and replace them with *answer* markers.
Syntax: *answer* for a single correct answer.
        *answer1/answer2* for alternative acceptable answers.
        *answer:hint text* to add a hint for that blank.
IMPORTANT: The "text" field is a SINGLE HTML string — not an array.

Full JSON skeleton:
{
  "taskDescription": "<p>Fill in the missing words.</p>",
  "text": "<p>The first stage is *denial*, which acts as a protective mechanism. As that fades, *anger* often surfaces. The stage of *bargaining* is accompanied by guilt.</p>",
  "overallFeedback": [{"from": 0, "to": 100, "feedback": ""}],
  "behaviour": {
    "enableRetry": true,
    "enableSolutionsButton": true,
    "autoCheck": false,
    "caseSensitive": false,
    "showSolutionsRequiresInput": true,
    "separateLines": false,
    "confirmCheckDialog": false,
    "confirmRetryDialog": false,
    "acceptSpellingErrors": false,
    "allowRetryIfCorrect": false,
    "enableCheckButton": true
  },
  "media": {"disableImageZooming": false},
  "showSolutions": "Show solution",
  "tryAgain": "Retry",
  "checkAnswer": "Check",
  "submitAnswer": "Submit",
  "notFilledOut": "Please fill in all blanks to view solution",
  "answerIsCorrect": "':ans' is correct",
  "answerIsWrong": "':ans' is wrong",
  "answeredCorrectly": "Answered correctly",
  "answeredIncorrectly": "Answered incorrectly",
  "solutionLabel": "Correct answer:",
  "inputLabel": "Blank input @num of @total",
  "inputHasTipLabel": "Tip available",
  "tipLabel": "Tip",
  "scoreBarLabel": "You got :num out of :total points",
  "a11yCheck": "Check the answers. The responses will be marked as correct, incorrect, or unanswered.",
  "a11yShowSolution": "Show the solution. The task will be marked with its correct solution.",
  "a11yRetry": "Retry the task. Reset all responses and start the task over again.",
  "confirmCheck": {
    "header": "Finish ?",
    "body": "Are you sure you wish to finish ?",
    "cancelLabel": "Cancel",
    "confirmLabel": "Finish"
  },
  "confirmRetry": {
    "header": "Retry ?",
    "body": "Are you sure you wish to retry ?",
    "cancelLabel": "Cancel",
    "confirmLabel": "Confirm"
  }
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTENT TYPE 8 — H5P.GuessTheAnswer  (use for guess the answer / reveal)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Choose this type ONLY when activity_type is "H5P.GuessTheAnswer".
Extract one concept, term, or question from the document. The learner reads
the question, thinks about it, then clicks to reveal the answer.
No scoring — this is purely a reveal/discussion activity.
IMPORTANT: "solutionLabel" is the button/prompt text shown BEFORE the answer
is revealed. "solutionText" is the actual answer text shown after clicking.

Full JSON skeleton:
{
  "taskDescription": "<p>What is the key concept described in this section?</p>",
  "solutionLabel": "Click to reveal the answer",
  "solutionText": "The full answer text drawn from the document."
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTENT TYPE 9 — H5P.Summary  (use for key statement identification)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Choose this type ONLY when activity_type is "H5P.Summary".
Extract 3–6 key statements from the document. For each statement, write
1–2 plausible but incorrect distractors. The learner eliminates distractors
until only correct statements remain.
IMPORTANT: In each "summary" array, the FIRST item is ALWAYS the correct
statement. Additional items are distractors. Each group needs a unique
subContentId (UUID v4).

Full JSON skeleton:
{
  "intro": "Choose the correct statement.",
  "summaries": [
    {
      "subContentId": "<uuid-v4>",
      "summary": [
        "<p>Correct statement drawn directly from the document.</p>",
        "<p>Plausible but incorrect distractor statement.</p>"
      ],
      "tip": ""
    },
    {
      "subContentId": "<uuid-v4>",
      "summary": [
        "<p>Second correct statement from the document.</p>",
        "<p>Another incorrect distractor.</p>"
      ],
      "tip": ""
    }
  ],
  "overallFeedback": [{"from": 0, "to": 100, "feedback": ""}],
  "solvedLabel": "Progress:",
  "scoreLabel": "Wrong answers:",
  "resultLabel": "Your result",
  "labelCorrect": "Correct.",
  "labelIncorrect": "Incorrect! Please try again.",
  "alternativeIncorrectLabel": "Incorrect",
  "labelCorrectAnswers": "Correct answers.",
  "tipButtonLabel": "Show tip",
  "scoreBarLabel": "You got :num out of :total points",
  "progressText": "Progress :num of :total"
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
CRITICAL: Use ONLY the content from the provided document. NEVER invent
placeholder text, generic filler, or example sentences such as "This is a
sample activity", "Since no content was provided", "placeholder", or any
fabricated educational content. If the document content is insufficient to
produce a meaningful activity, return whatever the document does contain —
do not substitute invented text.

1. H1 heading → document title
2. H2/H3 headings → section breaks / question categories / slide titles
3. Each QUESTION: block → one question entry in the questions array (QuestionSet)
   or one slide (CoursePresentation)
4. [CORRECT] items → "correct": true in the answer object
5. [ ] items → "correct": false in the answer object
6. If no [CORRECT] items exist in a block, mark only the first option correct
7. Maximum 4 answer options per question. If more exist, keep all [CORRECT]
   answers and select the best distractors to reach a total of 4.
7b. Every MultiChoice question MUST contain at least one answer with
   "correct": false. If the source material only provides correct
   statements, invent 1–2 plausible but clearly wrong distractors so
   the learner must discriminate. NEVER produce a question where every
   option is correct.
8. Each question's metadata.title must be the question text with HTML tags
   removed, truncated to 60 characters at a word boundary. Never use
   "Untitled Multiple Choice" or any generic placeholder.
8b. Strip section number prefixes from question text and titles. Do not
   begin a question with patterns like "3.1", "4.2 General Storage Rules:",
   "Section 2:" or similar numbering. The question should start directly
   with the interrogative ("Which...", "What...", "How...", etc.).
9. All text must be wrapped in HTML tags: <p>, <h2>, <ul><li>, etc.
10. Replace every <uuid-v4> placeholder with a real UUID v4 string
11. passPercentage should use the value provided by the caller
12. When activity_type is "auto":
    - Prefer QuestionSet if any QUESTION: blocks are present
    - Prefer CoursePresentation for purely explanatory documents
    - Never auto-select H5P.SortParagraphs
13. When activity_type is "H5P.QuestionSet", return H5P.QuestionSet exactly
14. When activity_type is "H5P.CoursePresentation", return H5P.CoursePresentation exactly
15. When activity_type is "H5P.SortParagraphs", return H5P.SortParagraphs exactly
    using the paragraphs skeleton — ignore QUESTION: blocks
16. When activity_type is "H5P.TrueFalse", return H5P.TrueFalse exactly
    Pick the most interesting factual claim. "correct" must be lowercase "true"/"false".
17. When activity_type is "H5P.DragText", return H5P.DragText exactly
    Choose key sentences; mark 3–6 important words with *asterisks*.
18. When activity_type is "H5P.Blanks", return H5P.Blanks exactly
    Write a flowing passage; mark key terms as *answer*. Use a single "text" field.
19. When activity_type is "H5P.GuessTheAnswer", return H5P.GuessTheAnswer exactly
    taskDescription is the question; solutionText is the answer revealed on click.
20. When activity_type is "H5P.Summary", return H5P.Summary exactly
    3–6 groups, each with one correct statement first, then 1–2 distractors.
21. When activity_type is "H5P.MultiChoice", return H5P.MultiChoice exactly
    Single standalone question with 3–4 answer options.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT  (CRITICAL — follow exactly)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Return ONLY a single JSON object — no markdown fences, no explanation, no
extra keys. The object must have exactly these three top-level keys:

{
  "content_type": "H5P.QuestionSet",
  "title": "Descriptive activity title — never use the word 'Assessment', never start with a number or section prefix like '1.' or '3.2', and never use generic words like 'Introduction' or 'Overview' alone. Derive a specific, content-driven title from the subject matter (e.g. 'Chemical Spill Response Procedures' not '5. Spills').",
  "content": { ... complete H5P content JSON as shown above ... }
}

Valid content_type values: "H5P.QuestionSet", "H5P.MultiChoice",
"H5P.CoursePresentation", "H5P.SortParagraphs", "H5P.TrueFalse",
"H5P.DragText", "H5P.Blanks", "H5P.GuessTheAnswer", "H5P.Summary"

If the document is empty or unrecognisable, return:
{"content_type": "H5P.QuestionSet", "title": "Empty Activity", "content": {}}
"""

_SINGLE_ITEM_TYPES = frozenset({
    "H5P.TrueFalse", "H5P.DragText", "H5P.Blanks",
    "H5P.GuessTheAnswer", "H5P.Summary", "H5P.MultiChoice",
})


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
    paragraph_count: int = 4,
    model_override: str | None = None,
    subject_area: str = "",
    learner_context: str = "",
) -> ProcessorResult:
    provider = ai_provider.lower().strip()
    user_content = _build_user_message(
        doc,
        activity_type,
        pass_percentage,
        paragraph_count=paragraph_count,
        force_requested_type=activity_type != "auto",
        subject_area=subject_area,
        learner_context=learner_context,
    )

    if provider in ("openai", "val"):
        result = _process_with_openai(user_content, model_override, use_val=provider == "val")
        return _validate_or_retry(
            result=result,
            provider=provider,
            doc=doc,
            activity_type=activity_type,
            pass_percentage=pass_percentage,
            paragraph_count=paragraph_count,
            model_override=model_override,
            subject_area=subject_area,
            learner_context=learner_context,
        )
    if provider == "anthropic":
        result = _process_with_anthropic(user_content, model_override)
        return _validate_or_retry(
            result=result,
            provider=provider,
            doc=doc,
            activity_type=activity_type,
            pass_percentage=pass_percentage,
            paragraph_count=paragraph_count,
            model_override=model_override,
            subject_area=subject_area,
            learner_context=learner_context,
        )
    raise ValueError("Unsupported AI provider")


def _process_with_openai(user_content: str, model_override: str | None, use_val: bool = False) -> ProcessorResult:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ValueError("OpenAI SDK is not installed. Install dependencies again.") from exc

    if use_val:
        if not settings.val_api_key:
            raise ValueError("VAL_API_KEY is not configured")
        model_name = model_override or settings.val_model
        client = OpenAI(api_key=settings.val_api_key, base_url=settings.val_base_url)
    else:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        model_name = model_override or settings.openai_model
        client = OpenAI(api_key=settings.openai_api_key)

    try:
        response = client.chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _H5P_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
    except Exception as exc:
        msg = str(exc)
        if use_val and any(x in msg for x in ("403", "Forbidden", "forbidden", "blocked", "unavailable")):
            raise ValueError("VAL_NETWORK_ERROR") from exc
        if use_val and ("401" in msg or "session has expired" in msg or "token is invalid" in msg):
            # VAL key rejected — fall back to OpenAI if available
            print(f"[VAL] Auth failed ({msg[:120]}), falling back to OpenAI", flush=True)
            return _process_with_openai(user_content, model_override, use_val=False)
        raise

    raw_json = _strip_markdown_fences((response.choices[0].message.content or "").strip())
    if not raw_json:
        raise ValueError("OpenAI returned no text output")
    h5p_result = _clean_sort_paragraphs(H5PResult.model_validate_json(raw_json))

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
    h5p_result = _clean_sort_paragraphs(H5PResult.model_validate_json(raw_json))
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
    paragraph_count: int = 4,
    force_requested_type: bool = False,
    subject_area: str = "",
    learner_context: str = "",
) -> str:
    lines: list[str] = [
        f"activity_type: {activity_type}",
        f"pass_percentage: {pass_percentage}",
        "",
    ]

    if subject_area or learner_context:
        lines.append("## Activity context")
        if subject_area:
            lines.append(f"- Subject area / unit code: {subject_area}")
            lines.append(f"  The activity title MUST begin with '{subject_area} —'")
        if learner_context:
            lines.append(f"- Learner context: {learner_context}")
        lines.append("")

    lines.extend([
        "## Document structure",
        f"Title: {doc.title}",
        "",
    ])

    if force_requested_type:
        lines.extend(
            [
                "## Required output type",
                f"You MUST return content_type exactly {activity_type}.",
                "Do not auto-select a different H5P type.",
                "",
            ]
        )

    # Single-item types and SortParagraphs use the full raw document text
    if activity_type in _SINGLE_ITEM_TYPES or activity_type == "H5P.SortParagraphs":
        if activity_type == "H5P.SortParagraphs":
            lines.extend(
                [
                    "## Sort the Paragraphs — instructions",
                    f"You MUST include EXACTLY {paragraph_count} paragraphs in the paragraphs array.",
                    "Read the full document below and identify the content that has a natural",
                    "sequential order (e.g. procedural steps, chronological events, logical argument).",
                    "Select the most meaningful sentences or steps and return them in their correct order.",
                    "",
                ]
            )
        lines.extend(["## Full document text", doc.raw_text])
        return "\n".join(lines)

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


_PARA_LABEL_RE = re.compile(
    r"(?:"
    r"(?:Rule|Step|Phase|Stage|Part|Point|Item|Section|Task|Action)"
    r"\s*\d+\s*[:.)\-–]\s*"
    r"|\d+\s*[:.)\-–]\s*"
    r")+",
    re.IGNORECASE,
)


def _clean_sort_paragraphs(h5p: H5PResult) -> H5PResult:
    """Strip leading numbering / labels from SortParagraphs entries."""
    if h5p.content_type != "H5P.SortParagraphs":
        return h5p
    paragraphs = h5p.content.get("paragraphs", [])
    if not paragraphs:
        return h5p
    cleaned = [
        re.sub(
            r"^(<p[^>]*>)" + _PARA_LABEL_RE.pattern,
            r"\1",
            p,
            flags=re.IGNORECASE,
        )
        for p in paragraphs
    ]
    return H5PResult(
        content_type=h5p.content_type,
        title=h5p.title,
        content={**h5p.content, "paragraphs": cleaned},
    )


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
    paragraph_count: int,
    model_override: str | None,
    subject_area: str = "",
    learner_context: str = "",
) -> ProcessorResult:
    if activity_type == "auto" or result.h5p.content_type == activity_type:
        return result

    retry_user_content = _build_user_message(
        doc,
        activity_type,
        pass_percentage,
        paragraph_count=paragraph_count,
        force_requested_type=True,
        subject_area=subject_area,
        learner_context=learner_context,
    )

    if provider in ("openai", "val"):
        retry_result = _process_with_openai(retry_user_content, model_override, use_val=provider == "val")
    elif provider == "anthropic":
        retry_result = _process_with_anthropic(retry_user_content, model_override)
    else:
        raise ValueError("Unsupported AI provider")

    return _validate_requested_type(retry_result, activity_type)

# H5P Creator

FastAPI + Codex/OpenAI service that converts Word documents, PDFs, and PowerPoints into H5P activity packages ready for RMIT's H5P platform (h5p.rmit.edu.au).

## Running locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Requires a `.env` file (see `.env.example` or copy from existing `.env`):

```
ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=Codex-opus-4-7
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-2024-08-06
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
```

## Architecture

```
app/
  api/routes/activities.py   — FastAPI endpoints (/generate_batch, /export, /download)
  core/config.py             — Pydantic settings (reads .env)
  schemas/
    h5p_types.py             — H5PResult model (content_type + content dict)
    requests.py              — All request/response Pydantic models
  services/
    document_parser.py       — Parse .docx / .pdf / .pptx → ParsedDocument
    document_analyzer.py     — Analyze document structure (section counts, suggestions)
    ai_processor.py          — Build prompts, call Codex/OpenAI, return ProcessorResult
    h5p_packager.py          — Build content.json + h5p.json, zip into .h5p bytes
  static/
    index.html               — Single-page app (2-step flow)
    app.js                   — All frontend logic
    styles.css               — Styling
```

## Supported H5P content types

All dependency versions verified against RMIT sample files.

| Type | Library | Notes |
|------|---------|-------|
| Quiz | H5P.QuestionSet 1.21 | Supports mixed MultiChoice + TrueFalse questions |
| Multiple Choice | H5P.MultiChoice 1.16 | Standalone single question |
| True / False | H5P.TrueFalse 1.8 | `correct` field is lowercase string "true"/"false" |
| Drag the Words | H5P.DragText 1.10 | `textField` uses `*word*` asterisk syntax |
| Fill in the Blanks | H5P.Blanks 1.14 | `text` field (single string) with `*answer*` syntax |
| Guess the Answer | H5P.GuessTheAnswer 1.5 | `solutionText` = revealed answer; no scoring |
| Sort the Paragraphs | H5P.SortParagraphs 0.11 | Array order = correct answer order |
| Summary | H5P.Summary 1.10 | First item in each `summary[]` is always the correct statement |
| Presentation | H5P.CoursePresentation 1.27 | Slide-based; not in MVP activity list |

All types use `embedTypes: ["div"]` matching RMIT samples.

## Batch generation flow

`POST /activities/generate_batch` accepts:
- `files[]` — one or more .docx / .pdf / .pptx files
- `activity_types` — JSON array of H5P type strings
- `content_mode` — `"shared"` (all types see all content) or `"unique"` (content split between activities)
- `count_per_type` — how many activities to generate per type (default 1)
- `pass_percentage` — quiz pass threshold (default 100)
- `paragraph_count` — for SortParagraphs only (default 4)

Returns a list of packed `.h5p` files as base64, one per (type × count) combination.

## Adding a new H5P content type

1. Add the `content_type` literal to `H5PResult` in `app/schemas/h5p_types.py`
2. Add the dependency list to `_DEPENDENCIES` in `app/services/h5p_packager.py` (verify versions against a real RMIT .h5p sample)
3. Add the content type section to `_H5P_SYSTEM_PROMPT` in `app/services/ai_processor.py` with the exact `content.json` skeleton
4. Add a conversion rule to the CONVERSION RULES section of the system prompt
5. Add `extract_preview_fields` handling for the new type in `app/services/h5p_packager.py`
6. Add the type to `_ALLOWED_ACTIVITY_TYPES` in `app/api/routes/activities.py`
7. Add a checkbox option in `app/static/index.html`
8. Add a `friendlyActivityType` mapping in `app/static/app.js`
9. Mirror all changes to `deploy-stage/`

## deploy-stage

`deploy-stage/` is a mirror of `app/` for staging deployment. After any change to `app/`, run:

```bash
for f in schemas/h5p_types.py schemas/requests.py services/ai_processor.py \
          services/h5p_packager.py api/routes/activities.py \
          static/app.js static/index.html static/styles.css; do
  cp "app/$f" "deploy-stage/app/$f"
done
```

# Claude Handoff: Course PowerPoint App

## Current Goal

This repo now has a second app/workspace tab for generating condensed PowerPoint decks from Canvas courses/modules using VAL.

Primary user need:
- Paste a Canvas course URL, e.g. `https://rmit.instructure.com/courses/158310/modules`
- Load the course modules
- Select specific modules, such as:
  - `Module 1: introduction to eaves`
  - `Module 2: Plan and prepare to erect roof trusses`
  - `Module 3: Erect roof trusses`
- Generate a condensed, non-verbatim `.pptx`
- Use course images where possible
- Use the provided RMIT/VAL PowerPoint template, not a hand-styled blank deck

## Important Model / VAL Context

The app is currently configured to use:

```text
VAL_MODEL=openai-gpt-5.4
```

This was verified against VAL's model list. `val-gpt-5.4` produced `Model not found`; the correct model ID exposed by VAL is `openai-gpt-5.4`.

The running local server `/info` endpoint currently reports:

```json
{"ai_provider":"val","model":"openai-gpt-5.4"}
```

Do not print or expose API keys from `.env`.

## Main Files Added / Changed

Backend:
- `app/api/routes/powerpoints.py`
  - `GET /powerpoints/course/modules`
  - `POST /powerpoints/course`
  - `GET /powerpoints/download/{filename}`
- `app/services/powerpoint_generator.py`
  - Reads selected Canvas module content
  - Calls VAL for a JSON slide plan
  - Generates `.pptx` using `python-pptx`
  - Uses the uploaded RMIT template as the base deck
- `app/services/canvas_lms.py`
  - Module summaries now include module item metadata so selected modules can map to pages/files
- `app/main.py`
  - Includes the new `powerpoints` router
- `app/core/config.py`
  - Adds `powerpoint_template_path`
  - Uses `openai-gpt-5.4` as default VAL model

Frontend:
- `app/static/index.html`
  - Adds `Course PowerPoint` tab/workspace
- `app/static/app.js`
  - Handles module loading, module selection, PPTX generation, and download
  - Module picker now displays exact Canvas module names; it does not prepend `Module 1:`
- `app/static/styles.css`
  - Adds styles for the Course PowerPoint workspace and module picker

Template:
- `app/templates/PowerPoint_Template_Showcase.pptx`
- `deploy-stage/app/templates/PowerPoint_Template_Showcase.pptx`

Staging mirror:
- Relevant changes were mirrored to `deploy-stage/app/...`

## RMIT Template Details

The uploaded template was:

```text
/Users/E92501/Downloads/PowerPoint_Template_Showcase.pptx
```

It has 15 showcase slides and 20 named layouts. Key layouts:
- `Title_option_1_text_only`
- `Content_option 1`
- `Content_option 2`
- `Content_option 3`
- `Content with image_option 1`
- `Content with image_option 2`
- `Section divider_option 1`
- `End slide`

The generator now:
- opens `settings.powerpoint_template_path`
- removes the showcase slides
- adds new slides using named template layouts
- preserves template slide dimensions: `9144000 x 5143680`
- preserves RMIT/VAL footer/brand chrome from layouts

## Most Recent Fixes

### Image fitting

There was a bug where images disappeared after changing to proportional fitting. Cause:
- `python-pptx` version here exposes image dimensions as `Image.size`, not `px_width` / `px_height`.

Fixed in `app/services/powerpoint_generator.py`:

```python
image_width, image_height = (int(value) for value in image.size)
```

### Layout variety and image reuse

User generated:

```text
/Users/E92501/Downloads/Erect_Roof_Trusses__Planning__Safety_and_Installat (1).pptx
```

Inspection found:
- 14 slides
- 12 slides used `Content_option 1`
- two images were reused multiple times

Fix implemented:
- `_choose_content_layout(...)` rotates layouts
- image slides use `Content with image_option 1/2`
- `_download_images(...)` dedupes downloaded images by SHA-1
- `_select_image_path(...)` uses each unique image once before returning `None`; it no longer cycles/reuses images

Validation for selector:

```text
[PosixPath('/tmp/a.png'), PosixPath('/tmp/b.png'), PosixPath('/tmp/c.png'), None, None]
unique first three True
```

## Known Limitations / Next Improvements

1. **Layout variety is basic but improved**
   - Current logic rotates variants algorithmically.
   - It does not yet ask VAL to choose a template layout per slide.
   - Better next step: extend `SlideSpec` with `layout_hint` or `layout_type` and prompt VAL to choose from allowed template layout names.

2. **Image relevance is still approximate**
   - VAL picks `source_image_index`, but if it picks an already-used image, the generator picks the next unused image.
   - This reduces repetition but may reduce semantic relevance.
   - Better next step: provide richer image metadata and ask VAL to assign unique images only.

3. **No full visual render QA currently**
   - The presentation skill render tools failed locally because `pdf2image` is not installed.
   - Structural tests and smoke tests passed.
   - If possible, install missing rendering deps or use PowerPoint/LibreOffice export to inspect generated slides.

4. **Template following is done with `python-pptx`, not artifact-tool**
   - The presentation skill says artifact-tool is preferred for one-off deck creation.
   - This app service currently uses `python-pptx` because it must run inside FastAPI and return generated `.pptx` bytes.

## Useful Commands

Run local server:

```bash
python3 -m uvicorn app.main:app --reload --port 8000
```

Check server info:

```bash
curl -s http://127.0.0.1:8000/info
```

Syntax checks:

```bash
python3 -m py_compile app/services/powerpoint_generator.py app/api/routes/powerpoints.py app/core/config.py app/main.py
node --check app/static/app.js
```

Staging syntax checks:

```bash
python3 -m py_compile deploy-stage/app/services/powerpoint_generator.py deploy-stage/app/api/routes/powerpoints.py deploy-stage/app/core/config.py deploy-stage/app/main.py
node --check deploy-stage/app/static/app.js
```

## Worktree Note

The worktree is dirty with many modified/untracked files, some likely pre-existing from earlier work. Do not assume all dirty files belong to this task. Avoid reverting unrelated changes.

Files most relevant to this handoff are:
- `app/api/routes/powerpoints.py`
- `app/services/powerpoint_generator.py`
- `app/templates/PowerPoint_Template_Showcase.pptx`
- `app/static/index.html`
- `app/static/app.js`
- `app/static/styles.css`
- `app/core/config.py`
- `app/main.py`
- matching `deploy-stage/app/...` files

## Suggested Next Task

Regenerate a deck after the latest layout/image changes, then inspect:
- layout counts should no longer be mostly `Content_option 1`
- image hashes should not repeat until unique images are exhausted
- text should not overlap images
- template footers/branding should remain visible


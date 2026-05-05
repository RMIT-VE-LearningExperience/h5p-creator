import json
import logging
import os
from datetime import datetime, timezone
from html import escape

import gspread
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from google.oauth2.service_account import Credentials
from pydantic import BaseModel

from app.api.routes import activities

logger = logging.getLogger("h5p_creator")

SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "16IveIK0v0kzBhTj-kZJzMbVFLCLiyriIop2Xg0qBeOc")
SHEETS_KEY_FILE = os.environ.get("GOOGLE_SHEETS_KEY_FILE", "/tmp/h5p-sheets-key.json")
SHEETS_KEY_JSON = os.environ.get("GOOGLE_SHEETS_KEY_JSON", "")

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

_gc: gspread.Client | None = None


def _get_gc() -> gspread.Client:
    global _gc
    if _gc is None:
        if SHEETS_KEY_JSON:
            info = json.loads(SHEETS_KEY_JSON)
            creds = Credentials.from_service_account_info(info, scopes=_SCOPES)
        else:
            creds = Credentials.from_service_account_file(SHEETS_KEY_FILE, scopes=_SCOPES)
        _gc = gspread.authorize(creds)
    return _gc


def _append_feedback(submitted_at: str, name: str, message: str) -> None:
    try:
        gc = _get_gc()
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.sheet1
        ws.append_row([submitted_at, name, message], value_input_option="RAW")
    except Exception as exc:
        print(f"[FEEDBACK] Sheets write failed: {exc}", flush=True)


def _load_feedback() -> list[dict]:
    try:
        gc = _get_gc()
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.sheet1
        rows = ws.get_all_values()
        entries = []
        for row in rows[1:]:  # skip header
            if len(row) >= 3 and row[2]:
                entries.append({
                    "submitted_at": row[0],
                    "name": row[1] or "Anonymous",
                    "message": row[2],
                })
        return entries
    except Exception as exc:
        print(f"[FEEDBACK] Sheets read failed: {exc}", flush=True)
        return []


app = FastAPI(
    title="H5P Creator",
    description="Convert Word documents into H5P activities for Canvas LMS",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(activities.router)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse("app/static/index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/info", include_in_schema=False)
def info() -> dict:
    from app.core.config import settings
    if settings.val_api_key:
        return {"ai_provider": "val", "model": settings.val_model}
    if settings.openai_api_key:
        return {"ai_provider": "openai", "model": settings.openai_model}
    if settings.anthropic_api_key:
        return {"ai_provider": "anthropic", "model": settings.anthropic_model}
    return {"ai_provider": "unknown", "model": ""}


class FeedbackPayload(BaseModel):
    name: str = ""
    message: str = ""


@app.get("/feedback", include_in_schema=False)
def feedback_page() -> HTMLResponse:
    entries = _load_feedback()
    rows = ""
    for e in reversed(entries):
        ts = e.get("submitted_at", "")[:19].replace("T", " ")
        name = escape(e.get("name", "Anonymous"))
        msg = escape(e.get("message", "")).replace("\n", "<br>")
        rows += f"""
        <tr>
          <td class="ts">{ts}</td>
          <td class="name">{name}</td>
          <td>{msg}</td>
        </tr>"""

    if not rows:
        rows = '<tr><td colspan="3" class="empty">No feedback submitted yet.</td></tr>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Feedback — H5P Creator</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{ font-family: system-ui, sans-serif; background: #f2f2f2; margin: 0; padding: 0; }}
    .topbar {{ background: #e61e2a; height: 6px; }}
    header {{ background: #000054; color: #fff; padding: 20px 32px; }}
    header .eyebrow {{ color: #fac800; font-size: .75rem; font-weight: 700;
                       text-transform: uppercase; letter-spacing: .1em; margin: 0 0 4px; }}
    header h1 {{ margin: 0; font-size: 1.4rem; }}
    main {{ max-width: 860px; margin: 32px auto; padding: 0 16px; }}
    h2 {{ font-size: 1rem; font-weight: 700; margin: 0 0 16px; }}
    .count {{ color: #666; font-weight: 400; margin-left: 6px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff;
             border-radius: 12px; overflow: hidden;
             border: 1px solid #e3e5e0; }}
    th {{ background: #000054; color: #fff; text-align: left;
          padding: 10px 14px; font-size: .8rem; font-weight: 600; }}
    td {{ padding: 12px 14px; border-bottom: 1px solid #e3e5e0;
          vertical-align: top; font-size: .9rem; }}
    tr:last-child td {{ border-bottom: none; }}
    .ts {{ white-space: nowrap; color: #666; font-size: .8rem; width: 160px; }}
    .name {{ white-space: nowrap; font-weight: 600; width: 140px; }}
    .empty {{ text-align: center; color: #888; padding: 32px; }}
  </style>
</head>
<body>
  <div class="topbar"></div>
  <header>
    <p class="eyebrow">RMIT VE Learning Experience</p>
    <h1>H5P Creator — Feedback</h1>
  </header>
  <main>
    <h2>Submissions <span class="count">({len(entries)})</span></h2>
    <table>
      <thead>
        <tr><th>Date</th><th>Name</th><th>Message</th></tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </main>
</body>
</html>"""
    return HTMLResponse(html)


@app.post("/feedback", include_in_schema=False)
async def submit_feedback(payload: FeedbackPayload) -> dict:
    name = payload.name.strip() or "Anonymous"
    message = payload.message.strip()
    if message:
        submitted_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        _append_feedback(submitted_at, name, message)
        print(f"[FEEDBACK] from={name!r}  message={message!r}", flush=True)
    return {"ok": True}

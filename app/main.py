import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.api.routes import activities

logger = logging.getLogger("h5p_creator")

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


class FeedbackPayload(BaseModel):
    name: str = ""
    message: str = ""


@app.get("/feedback", include_in_schema=False)
def feedback_page() -> FileResponse:
    return FileResponse("app/static/index.html")


@app.post("/feedback", include_in_schema=False)
async def submit_feedback(payload: FeedbackPayload) -> dict:
    name = payload.name.strip() or "Anonymous"
    message = payload.message.strip()
    if message:
        print(f"[FEEDBACK] from={name!r}  message={message!r}", flush=True)
    return {"ok": True}

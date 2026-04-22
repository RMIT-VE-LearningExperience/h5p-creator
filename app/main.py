from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import activities

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

app.include_router(activities.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

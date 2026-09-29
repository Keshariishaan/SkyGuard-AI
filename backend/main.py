"""
FastAPI entrypoint. Serves the JSON API under /api/* and, for local
convenience, also serves the frontend/ static files at "/" so the
whole app runs from a single command:

    uvicorn backend.main:app --reload

Then open http://localhost:8000
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database.seed import init_db
from backend.routes import telemetry
from backend.utils.config import settings

app = FastAPI(title="SkyGuard AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telemetry.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "env": settings.APP_ENV}


# Serve the frontend (index.html, css/, js/) as static files at "/".
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

"""Admin CSV upload: lexis, grammar, task. Access via Cloudflare only."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.routers.admin import (
    upload_grammar,
    upload_grammar_item,
    upload_grammar_unit,
    upload_lexis,
    upload_task,
)

router = APIRouter()

_UPLOAD_HTML_PATH = Path(__file__).resolve().parent / "upload.html"


@router.get("", response_class=HTMLResponse)
def upload_page() -> str:
    """Serve upload form (GET). POST endpoints require Bearer token."""
    return _UPLOAD_HTML_PATH.read_text(encoding="utf-8")


router.include_router(upload_lexis.router)
router.include_router(upload_grammar.router)
router.include_router(upload_grammar_unit.router)
router.include_router(upload_grammar_item.router)
router.include_router(upload_task.router)

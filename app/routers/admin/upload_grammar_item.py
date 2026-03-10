"""Admin upload: POST /grammar-item (JSON -> GrammarItem SQLite)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.sqlite import get_session
from app.routers.admin._upload_helpers import save_upload_to_temp
from app.scripts.init_grammar_item import (
    init_from_json as init_grammar_item_from_json,
)

router = APIRouter()


@router.post("/grammar-item")
def upload_grammar_item(
    files: list[UploadFile] = File(...),
    session: Session = Depends(get_session),
):
    """Upload grammar_outlines.json -> GrammarItem (SQLite)."""
    results: list[dict] = []
    for upload in files:
        path = save_upload_to_temp(upload)
        try:
            n = init_grammar_item_from_json(path, session)
            results.append(
                {
                    "filename": upload.filename or "grammar_outlines.json",
                    "sessions_upserted": n,
                }
            )
        except Exception as e:
            path.unlink(missing_ok=True)
            return JSONResponse(
                status_code=500,
                content={"detail": str(e), "filename": upload.filename},
            )
        finally:
            path.unlink(missing_ok=True)
    return {"uploaded": len(results), "results": results}

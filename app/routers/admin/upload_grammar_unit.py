"""Admin upload: POST /grammar-unit (JSON -> GrammarSet + GrammarProfile)."""

from __future__ import annotations

import falkordb
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.falkordb import get_graph_conn
from app.core.sqlite import get_session
from app.routers.admin._upload_helpers import save_upload_to_temp
from app.scripts.init_grammar_unit import (
    init_from_json as init_grammar_unit_from_json,
)

router = APIRouter()


@router.post("/grammar-unit")
def upload_grammar_unit(
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
    session: Session = Depends(get_session),
):
    """Upload grammar-*.json: GrammarSet and GrammarProfile."""
    results: list[dict] = []
    for upload in files:
        path = save_upload_to_temp(upload)
        try:
            n_sets, n_items = init_grammar_unit_from_json(
                path, graph, session, dry_run=False
            )
            results.append(
                {
                    "filename": upload.filename or "grammar.json",
                    "grammar_sets": n_sets,
                    "grammar_links": n_items,
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

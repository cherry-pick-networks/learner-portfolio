"""Admin upload: POST /grammar (CSV -> FalkorDB)."""

from __future__ import annotations

import falkordb
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse

from app.core.falkordb import get_graph_conn
from app.routers.admin._upload_helpers import save_upload_to_temp
from app.scripts.init_english_profile import init_grammar_profile

router = APIRouter()


@router.post("/grammar")
def upload_grammar(
    files: list[UploadFile] = File(...),
    graph: falkordb.Graph = Depends(get_graph_conn),
):
    """Upload CSV: grammar profile -> FalkorDB."""
    results: list[dict] = []
    for upload in files:
        path = save_upload_to_temp(upload)
        try:
            rows = init_grammar_profile(graph, path=path)
            results.append(
                {
                    "filename": upload.filename or "grammar.csv",
                    "rows_loaded": rows,
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

"""Shared helpers for admin upload endpoints."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Callable

import falkordb
from fastapi import BackgroundTasks, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.config import settings
from app.scripts.tag_grammar import tag_tasks
from app.scripts.tag_lexis import tag_tasks as tag_lexis_tasks


def save_upload_to_temp(upload: UploadFile) -> Path:
    """Write upload to a temp file; caller must unlink."""
    suffix = Path(upload.filename or "upload").suffix or ".csv"
    fd = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        content = upload.file.read()
        fd.write(content)
        fd.close()
        return Path(fd.name)
    except Exception:
        fd.close()
        Path(fd.name).unlink(missing_ok=True)
        raise


def upload_lexis_json(
    files: list[UploadFile],
    graph: falkordb.Graph,
    session: Session,
    default_filename: str,
    init_fn: Callable[..., tuple[int, int]],
) -> dict | JSONResponse:
    """Load lexis-*.json via init_fn; return results or error JSONResponse."""
    results: list[dict] = []
    for upload in files:
        path = save_upload_to_temp(upload)
        try:
            n_lists, n_items = init_fn(path, graph, session, dry_run=False)
            results.append(
                {
                    "filename": upload.filename or default_filename,
                    "lexis_sets": n_lists,
                    "lexis_items": n_items,
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


def enqueue_tagging(
    background_tasks: BackgroundTasks,
    graph: falkordb.Graph,
    tagged_list: list[tuple[str, str]],
) -> str:
    """Schedule grammar and lexis tag_tasks as background jobs."""
    if not tagged_list:
        return "skipped"
    if settings.openai_api_key:
        background_tasks.add_task(
            tag_tasks,
            graph,
            tagged_list,
            grammar_csv_path=None,
            openai_api_key=settings.openai_api_key,
        )
    background_tasks.add_task(tag_lexis_tasks, graph, tagged_list)
    return "queued"

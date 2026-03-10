"""Init FalkorDB English inventory and SQLite profile from TSV/CSV.

Re-exports init_lexis_profile and init_grammar_profile; provides
init_english_profile() to run both.
"""

from __future__ import annotations

import logging
from pathlib import Path

import falkordb
from sqlmodel import Session

from app.scripts.init_grammar_profile import (
    DEFAULT_GRAMMAR_PATH,
    init_grammar_profile,
)
from app.scripts.init_lexis_profile import (
    DEFAULT_LEXIS_PATH,
    init_lexis_profile,
)

__all__ = ["init_english_profile", "init_grammar_profile", "init_lexis_profile"]


def init_english_profile(
    graph: falkordb.Graph,
    session: Session,
    *,
    lexis_path: Path | None = None,
    grammar_path: Path | None = None,
) -> None:
    """Load lexis and grammar from TSV/CSV.

    Lexis: FalkorDB (profile + CEFR edges) + SQLite (per-corpus freq).
    Grammar: FalkorDB only (all fields as node properties).
    """
    lexis_src = lexis_path or DEFAULT_LEXIS_PATH
    grammar_src = grammar_path or DEFAULT_GRAMMAR_PATH
    if not lexis_src.exists() or not grammar_src.exists():
        logging.warning(
            "English profile data missing (lexis=%s, grammar=%s); skip load",
            lexis_src,
            grammar_src,
        )
    init_lexis_profile(graph, session, path=lexis_path)
    init_grammar_profile(graph, path=grammar_path)

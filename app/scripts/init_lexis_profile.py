"""Init FalkorDB lexis profile and SQLite per-corpus freq from TSV/CSV."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

import falkordb
from sqlmodel import Session

from app.scripts._lexis_profile_parsers import (
    _TEMP_DIR,
    DEFAULT_LEXIS_PATH,
    KNOWN_LEVIS_COLS,
    LEVELS,
    parse_float,
    parse_int,
)


def init_lexis_profile(
    graph: falkordb.Graph,
    session: Session,
    *,
    path: Path | None = None,
) -> int:
    """Load lexis CSV into FalkorDB (profile + CEFR edges) and SQLite
    (per-corpus frequency table). Returns rows loaded."""
    from app.crud.english.inventory import lexis
    from app.models.english.lexis_corpus_freq import LexisCorpusFreq

    src = path or DEFAULT_LEXIS_PATH
    if not src.exists():
        return 0
    use_direct = path is not None
    if not use_direct:
        _TEMP_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _TEMP_DIR / "lexis_profile.csv"
        shutil.copy(src, tmp)
        src = tmp
    count = 0
    delimiter = "\t" if src.suffix.lower() == ".tsv" else ","
    try:
        with open(src, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                headword = (row.get("word") or "").strip()
                if not headword:
                    continue
                count += 1
                pos = (row.get("tag") or "").strip() or None
                total_freq = parse_float(row.get("total_freq@total") or "")
                total_nb_doc = parse_int(row.get("nb_doc@total") or "")
                levels: list[tuple[str, float, int]] = []
                for lev in LEVELS:
                    freq = parse_float(row.get(f"level_freq@{lev}") or "")
                    nb_doc = parse_int(row.get(f"nb_doc@{lev}") or "")
                    levels.append((lev, freq, nb_doc))
                lexis.upsert_lexis_profile(
                    graph,
                    headword=headword,
                    pos=pos,
                    total_freq=total_freq,
                    total_nb_doc=total_nb_doc,
                    levels=levels,
                )
                for col_name, val in row.items():
                    if col_name in KNOWN_LEVIS_COLS:
                        continue
                    if "@" not in col_name:
                        continue
                    freq = parse_float(val)
                    if freq <= 0:
                        continue
                    parts = col_name.rsplit("@", 1)
                    if len(parts) != 2:
                        continue
                    corpus_name, cefr_level = parts
                    session.merge(
                        LexisCorpusFreq(
                            headword=headword,
                            corpus_name=corpus_name,
                            cefr_level=cefr_level.lower(),
                            freq=freq,
                        )
                    )
        session.commit()
    finally:
        if not use_direct and src.exists():
            src.unlink(missing_ok=True)
    return count

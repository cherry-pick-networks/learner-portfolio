"""Tests for load_textbook script."""

from __future__ import annotations

from pathlib import Path

import kuzu
import pytest

from scripts.load_textbook.load import (
    ensure_passage_table,
    upsert_passages,
)
from scripts.load_textbook.parse import filename_meta, read_text


@pytest.mark.parametrize(
    (
        "rel_path",
        "grade_group",
        "year",
        "curriculum",
        "subject",
        "publisher",
        "unit",
    ),
    [
        (
            "고등_내신/(개정)2022년_영어II_금성(최인철)_3과_본문_OK_hwp.txt",
            "고등_내신",
            2022,
            "2022개정",
            "영어II",
            "금성(최인철)",
            "3과",
        ),
        (
            "중등/temp_2021년_중3_천재(정사열)_6과_본문_OK_hwp.txt",
            "중등",
            2021,
            "2022개정",
            "중3",
            "천재(정사열)",
            "6과",
        ),
        (
            "고등_내신/(개정)2022년_영어I_YBM(박준언)_4과_본문_OK_hwp.txt",
            "고등_내신",
            2022,
            "2022개정",
            "영어I",
            "YBM(박준언)",
            "4과",
        ),
        (
            "중등/temp_2021년_중3_동아(윤정미)_Special Lesson_본문_OK_hwp.txt",
            "중등",
            2021,
            "2022개정",
            "중3",
            "동아(윤정미)",
            "Special Lesson",
        ),
        (
            "고등_내신/(개정)2022년_영어I_금성(최인철)_5과_본문_OK(20220613수정)_hwp.txt",
            "고등_내신",
            2022,
            "2022개정",
            "영어I",
            "금성(최인철)",
            "5과",
        ),
    ],
)
def test_filename_meta(
    tmp_path: Path,
    rel_path: str,
    grade_group: str,
    year: int,
    curriculum: str,
    subject: str,
    publisher: str,
    unit: str,
) -> None:
    bonmun_root = tmp_path / "bonmun"
    bonmun_root.mkdir()
    path = bonmun_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    meta = filename_meta(path, bonmun_root)
    assert meta["grade_group"] == grade_group
    assert meta["year"] == year
    assert meta["curriculum"] == curriculum
    assert meta["subject"] == subject
    assert meta["publisher"] == publisher
    assert meta["unit"] == unit
    assert "passage_id" in meta
    assert meta["passage_id"].startswith(f"{grade_group}__")


def test_filename_meta_source_file(tmp_path: Path) -> None:
    bonmun_root = tmp_path / "bonmun"
    bonmun_root.mkdir()
    path = bonmun_root / "고등_내신" / "2022_영어II_금성_3과_본문_OK_hwp.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    meta = filename_meta(path, bonmun_root)
    assert meta["source_file"] == str(Path("고등_내신") / path.name)


def test_read_text(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("Hello\nWorld", encoding="utf-8")
    assert read_text(f) == "Hello\nWorld"


def test_upsert_passages_in_memory() -> None:
    db = kuzu.Database("")
    conn = kuzu.Connection(db)
    ensure_passage_table(conn)
    records = [
        {
            "passage_id": "test__unit1",
            "year": 2022,
            "grade_group": "고등_내신",
            "curriculum": "2022개정",
            "subject": "영어I",
            "publisher": "YBM(박준언)",
            "unit": "1과",
            "text": "Passage content.",
            "source_file": "고등_내신/unit1.txt",
        },
    ]
    n = upsert_passages(conn, records)
    assert n == 1
    result = conn.execute(
        "MATCH (p:Passage) RETURN p.passage_id, p.curriculum, p.text"
    )
    row = result.get_next()
    assert row[0] == "test__unit1"
    assert row[1] == "2022개정"
    assert row[2] == "Passage content."

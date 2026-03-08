"""Tests for extract_bonmun_only script."""

from __future__ import annotations

from pathlib import Path

from scripts.extract_bonmun_only.extract import (
    extract_english_only,
    find_first_bonmun_idx,
    is_korean_section_start,
)


def test_is_korean_section_start_korean_title() -> None:
    assert is_korean_section_start("스트레스를 즐겨요") is True
    assert is_korean_section_start("나의 역할 모델") is True
    assert is_korean_section_start("큰 기적") is True


def test_is_korean_section_start_english() -> None:
    assert is_korean_section_start("본문 1 – Thrive on Stress") is False
    assert (
        is_korean_section_start("Not all people shy away from stress") is False
    )
    assert is_korean_section_start("FURTHER READING") is False


def test_is_korean_section_start_footnote_or_short() -> None:
    assert is_korean_section_start("*barge 바지선") is False
    assert is_korean_section_start("[IMAGE]") is False
    assert is_korean_section_start("ab") is False


def test_find_first_bonmun_idx() -> None:
    lines = [
        "[IMAGE]",
        "교재명",
        "본문 1 – Thrive on Stress",
        "paragraph",
    ]
    assert find_first_bonmun_idx(lines) == 2


def test_find_first_bonmun_idx_not_found() -> None:
    assert find_first_bonmun_idx(["foo", "bar"]) == -1


def test_extract_english_only_removes_header_and_korean() -> None:
    lines = [
        "[IMAGE]",
        "교재명",
        "본문 1 – Title",
        " English paragraph.",
        "스트레스를 즐겨요",
        " 한글 번역",
    ]
    result = extract_english_only(lines)
    assert result[0] == "본문 1 – Title"
    assert "English paragraph." in result[1]
    assert "스트레스를 즐겨요" not in "\n".join(result)
    assert "한글" not in "\n".join(result)


def test_extract_english_only_removes_image_lines() -> None:
    lines = [
        "본문 1 – Title",
        "[IMAGE]",
        " English text.",
    ]
    result = extract_english_only(lines)
    assert "[IMAGE]" not in result
    assert "English text." in result[1]


def test_extract_english_only_no_bonmun_returns_empty() -> None:
    assert extract_english_only(["foo", "bar"]) == []


def test_extract_english_only_keeps_only_first_title() -> None:
    """Only first '본문 N – Title' kept; subsequent 본문 headers removed."""
    lines = [
        "본문 1 – Thrive on Stress",
        " English paragraph.",
        "본문 2 - Thrive on Stress",
        " More English.",
        "본문 3 – Thrive on Stress",
        " Even more.",
    ]
    result = extract_english_only(lines)
    titles = [ln for ln in result if ln.strip().startswith("본문 ")]
    assert len(titles) == 1
    assert titles[0] == "본문 1 – Thrive on Stress"
    assert "English paragraph." in result[1]
    assert "More English." in result[2]
    assert "Even more." in result[3]


def test_extract_english_only_real_sample(tmp_path: Path) -> None:
    """Integration: sample from 동아 1과 structure."""
    sample = """[IMAGE]
영어 독해와 작문 동아(권혁승)
Lesson 1
본문 1 – Thrive on Stress
 English paragraph here.
본문 2 - Thrive on Stress
 More English.
스트레스를 즐겨요
 한글 번역 시작
"""
    src = tmp_path / "sample.txt"
    src.write_text(sample, encoding="utf-8")
    lines = src.read_text(encoding="utf-8").splitlines()
    result = extract_english_only(lines)
    text = "\n".join(result)
    assert text.startswith("본문 1 – Thrive on Stress")
    assert "English paragraph" in text
    assert "스트레스를 즐겨요" not in text
    assert "한글" not in text

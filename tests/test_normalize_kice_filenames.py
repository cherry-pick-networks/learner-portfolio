"""Tests for scripts.normalize_kice_filenames."""

from __future__ import annotations

from pathlib import Path

from scripts.normalize_kice_filenames import (
    normalize_component,
    normalized_path,
)


def test_normalize_component_mojibake_latin1_to_korean() -> None:
    """Latin-1 mojibake (CP949 decoded as Latin-1) normalizes to Korean."""
    mojibake = "문제지".encode("cp949").decode("latin-1")
    assert normalize_component(mojibake) == "문제지"


def test_normalize_component_mojibake_cp437_to_korean() -> None:
    """CP437-style mojibake (box-drawing chars) normalizes to Korean."""
    # Same bytes as "해설지" in CP949, displayed as CP437 then saved as UTF-8.
    mojibake = "해설지".encode("cp949").decode("cp437")
    assert normalize_component(mojibake) == "해설지"


def test_normalize_component_already_korean_unchanged() -> None:
    """Already-correct Korean is unchanged."""
    assert normalize_component("문제지") == "문제지"


def test_normalize_component_ascii_unchanged() -> None:
    """ASCII-only is unchanged."""
    assert normalize_component("2016_3.pdf") == "2016_3.pdf"


def test_normalize_component_invalid_returns_original() -> None:
    """Invalid bytes that fail CP949 decode return original."""
    # 0x81 0x00 is illegal multibyte in CP949; decode fails, we return original.
    garbage = "\x81\x00"
    assert normalize_component(garbage) == garbage


def test_normalized_path_fixes_one_segment() -> None:
    """Path with one mojibake segment has that segment fixed."""
    root = Path("/root")
    mojibake = "문제지".encode("cp949").decode("latin-1")
    path = root / "folder" / mojibake / "file.pdf"
    got = normalized_path(root, path)
    assert got == root / "folder" / "문제지" / "file.pdf"


def test_normalized_path_unchanged_when_no_mojibake() -> None:
    """Path with no mojibake is unchanged."""
    root = Path("/root")
    path = root / "2023년_11월" / "문제지.pdf"
    assert normalized_path(root, path) == path


def test_normalized_path_root_only_returns_root() -> None:
    """Path equal to root returns root."""
    root = Path("/root")
    assert normalized_path(root, root) == root

"""Output naming for doc extraction (ext suffix avoids same-stem collision)."""

from __future__ import annotations

from pathlib import Path

from scripts.rename_file import output_txt_name


def test_output_txt_name_at_root() -> None:
    assert output_txt_name(Path("a.hwp")) == "a_hwp.txt"
    assert output_txt_name(Path("a.pdf")) == "a_pdf.txt"
    assert output_txt_name(Path("doc")) == "doc.txt"


def test_output_txt_name_same_stem_different_ext_no_collision() -> None:
    """Same stem, different extensions -> distinct output filenames (no folder prefix)."""
    assert output_txt_name(Path("grammar/a.hwp")) == "a_hwp.txt"
    assert output_txt_name(Path("grammar/a.pdf")) == "a_pdf.txt"


def test_output_txt_name_subfolder() -> None:
    """Output name is original file stem only."""
    assert (
        output_txt_name(Path("grammar/present_simple.pdf"))
        == "present_simple_pdf.txt"
    )

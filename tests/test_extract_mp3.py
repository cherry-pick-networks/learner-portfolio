"""Tests for ARPABET extraction (align_audio with mocked ForceAlign)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.extract_mp3.align import align_audio


def _word(phoneme_symbols: list[str]) -> MagicMock:
    """Build a word mock with phonemes that have .phoneme attribute."""
    phonemes = [MagicMock(phoneme=p) for p in phoneme_symbols]
    w = MagicMock()
    w.phonemes = phonemes
    return w


@patch("scripts.extract_mp3.align.ForceAlign")
def test_align_audio_returns_space_separated_arpabet(
    mock_force_align_cls: MagicMock,
) -> None:
    """align_audio returns a single space-separated ARPABET string."""
    mock_align = MagicMock()
    mock_align.inference.return_value = [
        _word(["HH", "AH0", "L"]),
        _word(["OW1", "W", "ER0", "L", "D"]),
    ]
    mock_force_align_cls.return_value = mock_align

    result = align_audio(Path("/tmp/hello.mp3"), "hello world")

    assert result == "HH AH0 L OW1 W ER0 L D"
    mock_force_align_cls.assert_called_once_with(
        audio_file="/tmp/hello.mp3", transcript="hello world"
    )
    mock_align.inference.assert_called_once()


@patch("scripts.extract_mp3.align.ForceAlign")
def test_align_audio_accepts_none_transcript(
    mock_force_align_cls: MagicMock,
) -> None:
    """align_audio can be called with transcript=None (ASR mode)."""
    mock_align = MagicMock()
    mock_align.inference.return_value = [_word(["AH0"])]
    mock_force_align_cls.return_value = mock_align

    result = align_audio(Path("/tmp/a.wav"), None)

    assert result == "AH0"
    mock_force_align_cls.assert_called_once_with(
        audio_file="/tmp/a.wav", transcript=None
    )


@patch("scripts.extract_mp3.align.ForceAlign")
def test_align_audio_empty_inference_returns_empty_string(
    mock_force_align_cls: MagicMock,
) -> None:
    """When inference returns no words, result is empty string."""
    mock_align = MagicMock()
    mock_align.inference.return_value = []
    mock_force_align_cls.return_value = mock_align

    result = align_audio(Path("/tmp/silence.mp3"), "silence")

    assert result == ""

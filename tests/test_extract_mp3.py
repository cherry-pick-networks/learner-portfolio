"""Tests for Vosk transcription (extract_mp3)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.extract_mp3.transcribe import transcribe


@patch("scripts.extract_mp3.transcribe.KaldiRecognizer")
@patch("scripts.extract_mp3.transcribe._audio_to_mono_16k_pcm")
def test_transcribe_returns_concatenated_text(
    mock_pcm: MagicMock,
    mock_kaldi_cls: MagicMock,
) -> None:
    """transcribe returns space-joined text from recognizer results."""
    mock_pcm.return_value = (b"\x00" * 8000, 16000)
    rec = MagicMock()
    rec.AcceptWaveform.return_value = True
    rec.Result.return_value = json.dumps({"text": "hello"})
    rec.FinalResult.return_value = json.dumps({"text": "world"})
    mock_kaldi_cls.return_value = rec

    result = transcribe(Path("/tmp/x.mp3"), MagicMock())

    assert result == "hello world"
    rec.AcceptWaveform.assert_called()
    rec.FinalResult.assert_called_once()


@patch("scripts.extract_mp3.transcribe.KaldiRecognizer")
@patch("scripts.extract_mp3.transcribe._audio_to_mono_16k_pcm")
def test_transcribe_handles_empty_result(
    mock_pcm: MagicMock,
    mock_kaldi_cls: MagicMock,
) -> None:
    """transcribe returns empty string when no text is recognized."""
    mock_pcm.return_value = (b"\x00" * 8000, 16000)
    rec = MagicMock()
    rec.AcceptWaveform.return_value = False
    rec.FinalResult.return_value = json.dumps({"text": ""})
    mock_kaldi_cls.return_value = rec

    result = transcribe(Path("/tmp/silence.wav"), MagicMock())

    assert result == ""

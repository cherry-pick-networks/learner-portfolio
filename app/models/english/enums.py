from __future__ import annotations

from enum import Enum


class EnglishSystem(str, Enum):
    grammar = "grammar"
    lexis = "lexis"
    phonology = "phonology"


class CefrLevel(str, Enum):
    a1 = "a1"
    a2 = "a2"
    b1 = "b1"
    b2 = "b2"
    c1 = "c1"
    c2 = "c2"


class Skill(str, Enum):
    reading = "reading"
    writing = "writing"
    listening = "listening"
    speaking = "speaking"

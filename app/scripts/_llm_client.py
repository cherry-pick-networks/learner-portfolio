"""LLM helpers for grammar tagging: system prompt, build message, call."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openai import OpenAI

SYSTEM_PROMPT = """\
You are a grammar analyst for English learner texts.
Given a passage and a list of grammar structures from the Cambridge Grammar
Profile, identify which structures are ACTUALLY PRESENT in the passage.
Return ONLY a JSON object: {"matches": ["guideword1", "guideword2", ...]}.
Use exact guideword strings from the list. Return {"matches": []} if none apply.
No explanations."""


def build_user_message(
    text: str, super_category: str, entries: list[dict]
) -> str:
    lines = [
        "PASSAGE:",
        text.strip(),
        "",
        f"GRAMMAR STRUCTURES — SuperCategory: {super_category}",
    ]
    for i, e in enumerate(entries, 1):
        lines.append(
            f"{i}. [{e['cefr']}] {e['sub_category']} > {e['guideword']}"
        )
    lines.append("")
    lines.append("Which of these are present in the passage?")
    return "\n".join(lines)


def call_llm(client: OpenAI, user_content: str) -> list[str]:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
        max_tokens=500,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content or "{}"
    try:
        data = json.loads(raw)
        matches = data.get("matches") or []
        return [str(m).strip() for m in matches if m]
    except (json.JSONDecodeError, TypeError):
        return []

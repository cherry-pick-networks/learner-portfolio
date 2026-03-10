"""FSRS spaced-repetition wrapper using Cambridge Assessment terminology."""

from __future__ import annotations

import json
from datetime import datetime

from fsrs import Card, Rating, Scheduler


def initialise_item() -> str:
    """Return initial card state as JSON for a new practice item."""
    return Card().to_json()


def _scheduler_from_w_vector(w_vector_json: str | None) -> Scheduler:
    if w_vector_json is None:
        return Scheduler()
    weights = json.loads(w_vector_json)
    return Scheduler(parameters=tuple(weights))


def schedule_item(
    card_json: str,
    response_rating: int,
    w_vector_json: str | None = None,
) -> tuple[str, datetime, float, float, float | None]:
    """Compute next practice date from response rating (1=Again..4=Easy).

    Returns:
        (card_state_json, due_date, stability, difficulty, retention_estimate)
    """
    card = Card.from_json(card_json)
    rating = Rating(response_rating)
    scheduler = _scheduler_from_w_vector(w_vector_json)
    card, _ = scheduler.review_card(card, rating)
    retention = scheduler.get_card_retrievability(card)
    stability = card.stability if card.stability is not None else 0.0
    difficulty = card.difficulty if card.difficulty is not None else 0.0
    return (
        card.to_json(),
        card.due,
        stability,
        difficulty,
        retention,
    )


def estimate_retention(
    card_json: str,
    w_vector_json: str | None = None,
) -> float:
    """Return current recall probability (0~1) for the item."""
    card = Card.from_json(card_json)
    scheduler = _scheduler_from_w_vector(w_vector_json)
    return scheduler.get_card_retrievability(card)


def build_scheduler(w_vector_json: str) -> Scheduler:
    """Build scheduler from learner weight vector (JSON array of floats)."""
    return _scheduler_from_w_vector(w_vector_json)

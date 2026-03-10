from __future__ import annotations

from fastapi import APIRouter

from app.routers.english.records import (
    acquisition,
    fsrs_config,
    learner_proficiency,
    lexis_review_schedule,
    needs_analysis,
    practice,
    recall_event,
    review_schedule,
    task_outcome,
    writing_assessment,
)

router = APIRouter(prefix="/records")

router.include_router(acquisition.router)
router.include_router(practice.router)
router.include_router(writing_assessment.router)
router.include_router(task_outcome.router)
router.include_router(needs_analysis.router)
router.include_router(learner_proficiency.router)
router.include_router(review_schedule.router)
router.include_router(lexis_review_schedule.router)
router.include_router(recall_event.router)
router.include_router(fsrs_config.router)

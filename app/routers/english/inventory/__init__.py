from __future__ import annotations

from fastapi import APIRouter

from app.routers.english.inventory import (
    grammar,
    grammar_item,
    grammatical_set,
    lexical_set,
    lexis,
    task,
)

router = APIRouter(prefix="/inventory")

# Static sub-paths first (must precede dynamic /{cefr} routes)
router.include_router(grammar_item.router)
router.include_router(grammatical_set.router)
router.include_router(grammar.router)
router.include_router(lexical_set.router)
router.include_router(lexis.router)
router.include_router(task.router)

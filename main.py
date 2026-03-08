from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from sqlmodel import SQLModel

from app.core.config import settings
from app.core.kuzu import init_graph_schema
from app.core.sqlite import engine
from app.routers import english


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    Path(settings.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    Path(settings.kuzu_path).parent.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)
    init_graph_schema()
    yield


app = FastAPI(title="learner-portfolio", lifespan=lifespan)

app.include_router(english.router)

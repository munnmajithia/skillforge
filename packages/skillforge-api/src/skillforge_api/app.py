"""SkillForge FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import init_db
from .routes.skills import router as skills_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown: initialize the database tables."""
    await init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="SkillForge API",
        description="Open-source MCP skill pack ecosystem API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(skills_router)
    return app


app = create_app()

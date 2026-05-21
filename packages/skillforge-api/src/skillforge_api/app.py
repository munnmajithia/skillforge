"""SkillForge FastAPI application factory."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy import func, select
from fastapi import FastAPI

from skillforge_core import parse_skill_md, validate_skill

from .database import init_db, async_session
from .models import SkillModel
from .routes.skills import router as skills_router

# Pre-packaged reference skills — auto-seeded on cold starts
_REFERENCE_SKILLS = [
    "skills/github-code-review/SKILL.md",
    "skills/linear-issue-manager/SKILL.md",
    "skills/postgres-schema-explorer/SKILL.md",
]


def _compute_security_score(manifest: dict) -> float:
    """Compute a naive security score based on declared risks."""
    score = 1.0
    permissions = manifest.get("permissions", {})
    if isinstance(permissions, dict):
        tools = permissions.get("tools", [])
        risk_weights = {"low": 0.0, "medium": 0.1, "high": 0.25, "critical": 0.4}
        for tool in tools:
            if isinstance(tool, dict):
                risk = tool.get("risk", "low")
                score -= risk_weights.get(risk, 0.0)
    security = manifest.get("security", {})
    if isinstance(security, dict):
        if security.get("secrets_required"):
            score -= 0.1
        if security.get("network_egress"):
            score -= 0.1
    return max(0.0, min(1.0, round(score, 2)))


async def _seed_reference_skills() -> None:
    """Seed the reference skills if the DB is empty."""
    async with async_session() as db:
        count_result = await db.execute(
            select(func.count()).select_from(SkillModel)
        )
        count = count_result.scalar()
        if count and count > 0:
            return  # already seeded

        seeded = 0
        for rel_path in _REFERENCE_SKILLS:
            filepath = Path(rel_path)
            if not filepath.exists():
                continue
            content = filepath.read_text(encoding="utf-8")
            try:
                skill = parse_skill_md(content)
            except Exception:
                continue
            errors = validate_skill(skill)
            manifest = skill.manifest
            manifest_dict = manifest.model_dump(exclude_none=True)

            db_model = SkillModel(
                name=manifest.name,
                version=manifest.version,
                description=manifest.description,
                author=manifest.author,
                manifest_json=json.dumps(manifest_dict, default=str),
                body=skill.body,
                raw_skill_md=content,
                tags=",".join(manifest.tags) if manifest.tags else "",
                download_count=0,
                validation_score=1.0 if not errors else 0.0,
                security_score=_compute_security_score(manifest_dict),
            )
            db.add(db_model)
            seeded += 1
        await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown: initialize database and seed reference skills."""
    await init_db()
    await _seed_reference_skills()
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

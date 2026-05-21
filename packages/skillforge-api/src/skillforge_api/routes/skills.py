"""CRUD + search endpoints for skills."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from skillforge_core import parse_skill_md, validate_skill

from ..database import get_db
from ..models import SkillModel
from ..schemas import (
    HealthResponse,
    SkillCreateRequest,
    SkillListResponse,
    SkillResponse,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    return HealthResponse()


# ---------------------------------------------------------------------------
# POST /skills — create a skill by parsing SKILL.md content
# ---------------------------------------------------------------------------
@router.post("/skills", response_model=SkillResponse, status_code=201, tags=["skills"])
async def create_skill(
    body: SkillCreateRequest, db: AsyncSession = Depends(get_db)
) -> SkillResponse:
    content = body.skill_md.strip()
    if not content:
        raise HTTPException(status_code=400, detail="SKILL.md content is required")

    # Parse with core library
    try:
        skill = parse_skill_md(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Validate
    errors = validate_skill(skill)
    if errors:
        raise HTTPException(status_code=422, detail=errors)

    manifest = skill.manifest

    # Serialize manifest to JSON for storage
    manifest_dict = manifest.model_dump(exclude_none=True)
    manifest_json = json.dumps(manifest_dict, default=str)

    # Check for duplicate name+version
    existing = await db.execute(
        select(SkillModel).where(
            SkillModel.name == manifest.name,
            SkillModel.version == manifest.version,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Skill '{manifest.name}@{manifest.version}' already exists",
        )

    db_model = SkillModel(
        name=manifest.name,
        version=manifest.version,
        description=manifest.description,
        author=manifest.author,
        manifest_json=manifest_json,
        body=skill.body,
        raw_skill_md=content,
        tags=",".join(manifest.tags) if manifest.tags else "",
        download_count=0,
        validation_score=1.0 if not errors else 0.0,
        security_score=_compute_security_score(manifest_dict),
    )
    db.add(db_model)
    await db.flush()
    await db.refresh(db_model)

    return _to_response(db_model)


# ---------------------------------------------------------------------------
# GET /skills — list skills (paginated, filterable by tag)
# ---------------------------------------------------------------------------
@router.get("/skills", response_model=SkillListResponse, tags=["skills"])
async def list_skills(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    tag: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> SkillListResponse:
    stmt = select(SkillModel)
    count_stmt = select(func.count()).select_from(SkillModel)

    if tag:
        stmt = stmt.where(SkillModel.tags.contains(tag))
        count_stmt = count_stmt.where(SkillModel.tags.contains(tag))

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = stmt.order_by(SkillModel.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    rows = result.scalars().all()

    return SkillListResponse(
        items=[_to_response(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


# ---------------------------------------------------------------------------
# GET /skills/{skill_id} — get one skill by DB id
# ---------------------------------------------------------------------------
@router.get("/skills/{skill_id}", response_model=SkillResponse, tags=["skills"])
async def get_skill(
    skill_id: int, db: AsyncSession = Depends(get_db)
) -> SkillResponse:
    result = await db.execute(select(SkillModel).where(SkillModel.id == skill_id))
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return _to_response(row)


# ---------------------------------------------------------------------------
# GET /search — full-text search via LIKE
# ---------------------------------------------------------------------------
@router.get("/search", response_model=SkillListResponse, tags=["search"])
async def search_skills(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> SkillListResponse:
    pattern = f"%{q}%"

    # Search across name, description, tags, and body
    stmt = select(SkillModel).where(
        (SkillModel.name.ilike(pattern))
        | (SkillModel.description.ilike(pattern))
        | (SkillModel.tags.ilike(pattern))
        | (SkillModel.body.ilike(pattern))
    )

    count_stmt = select(func.count()).select_from(SkillModel).where(
        (SkillModel.name.ilike(pattern))
        | (SkillModel.description.ilike(pattern))
        | (SkillModel.tags.ilike(pattern))
        | (SkillModel.body.ilike(pattern))
    )

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = stmt.order_by(SkillModel.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    rows = result.scalars().all()

    return SkillListResponse(
        items=[_to_response(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _to_response(model: SkillModel) -> SkillResponse:
    try:
        manifest = json.loads(model.manifest_json)
    except (json.JSONDecodeError, TypeError):
        manifest = {}

    return SkillResponse(
        id=model.id,
        name=model.name,
        version=model.version,
        description=model.description,
        author=model.author,
        tags=[t for t in model.tags.split(",") if t] if model.tags else [],
        manifest=manifest,
        body=model.body,
        download_count=model.download_count,
        validation_score=model.validation_score,
        security_score=model.security_score,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


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

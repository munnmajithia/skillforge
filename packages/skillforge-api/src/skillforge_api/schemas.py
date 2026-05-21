"""Pydantic request/response schemas for the SkillForge API."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SkillCreateRequest(BaseModel):
    """Raw SKILL.md content to parse and store."""

    skill_md: str = Field(..., description="Raw SKILL.md file content")


class SkillResponse(BaseModel):
    """Public skill representation."""

    id: int
    name: str
    version: str
    description: str
    author: str
    tags: list[str] = Field(default_factory=list)
    manifest: dict = Field(default_factory=dict)
    body: str = ""
    download_count: int = 0
    validation_score: Optional[float] = None
    security_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SkillListResponse(BaseModel):
    """Paginated skill list."""

    items: list[SkillResponse]
    total: int
    page: int
    page_size: int


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


class SkillSearchRequest(BaseModel):
    """Search query params (used internally, endpoint uses query string)."""

    q: str = Field(..., min_length=1, description="Search query")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

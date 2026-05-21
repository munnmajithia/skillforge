"""Pydantic models for SkillForge."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class SkillVersion(BaseModel):
    """Semantic version for a skill."""
    major: int = Field(ge=0)
    minor: int = Field(ge=0)
    patch: int = Field(ge=0)
    prerelease: str | None = None

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            return f"{base}-{self.prerelease}"
        return base

    @classmethod
    def from_string(cls, version: str) -> SkillVersion:
        parts = version.split("-")
        nums = parts[0].split(".")
        prerelease = parts[1] if len(parts) > 1 else None
        return cls(
            major=int(nums[0]),
            minor=int(nums[1]) if len(nums) > 1 else 0,
            patch=int(nums[2]) if len(nums) > 2 else 0,
            prerelease=prerelease,
        )


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SkillTool(BaseModel):
    """A tool exposed by a skill."""
    name: str
    description: str
    risk: RiskLevel = RiskLevel.LOW
    data_access: list[str | dict[str, Any]] = Field(default_factory=list)


class SkillPermission(BaseModel):
    """Permissions declared by a skill."""
    tools: list[SkillTool] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)
    environment: list[str] = Field(default_factory=list)


class SkillSecurity(BaseModel):
    """Security metadata for a skill."""
    prompt_injection_surface: RiskLevel = RiskLevel.LOW
    secrets_required: list[str] = Field(default_factory=list)
    network_egress: list[str] = Field(default_factory=list)


class SkillAuthor(BaseModel):
    """Skill author metadata."""
    name: str
    email: str | None = None
    url: str | None = None


class SkillManifest(BaseModel):
    """A parsed SKILL.md frontmatter manifest."""
    name: str
    version: str
    description: str
    author: str
    license: str = "MIT"
    mcp_server: str | None = None
    entry_point: str | None = None
    permissions: SkillPermission = Field(default_factory=SkillPermission)
    security: SkillSecurity = Field(default_factory=SkillSecurity)
    tags: list[str] = Field(default_factory=list)
    homepage: str | None = None
    repository: str | None = None
    icon: str | None = None  # emoji or URL

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Skill name must be alphanumeric with hyphens/underscores")
        if len(v) < 2 or len(v) > 64:
            raise ValueError("Skill name must be 2-64 characters")
        return v.lower()


class Skill(BaseModel):
    """Full skill entity including manifest, body, and metadata."""
    manifest: SkillManifest
    body: str  # Markdown body after frontmatter
    raw: str  # original SKILL.md content

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    download_count: int = 0
    validation_score: float | None = None
    security_score: float | None = None

    @property
    def id(self) -> str:
        return f"{self.manifest.name}@{self.manifest.version}"

    @property
    def version(self) -> SkillVersion:
        return SkillVersion.from_string(self.manifest.version)

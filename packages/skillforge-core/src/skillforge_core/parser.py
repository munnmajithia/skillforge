"""SKILL.md parser — YAML frontmatter + Markdown body."""

from __future__ import annotations

from typing import Any

import yaml
from jsonschema import validate as jsonschema_validate
from jsonschema.exceptions import ValidationError as JsonSchemaError

from .models import Skill, SkillManifest
from .schema import SKILL_SCHEMA


def parse_skill_md(content: str) -> Skill:
    """Parse a SKILL.md string into a Skill object.

    Expected format:
        ---
        name: my-skill
        version: 1.0.0
        ...
        ---

        # My Skill
        ...
    """
    if not content.strip().startswith("---"):
        raise ValueError("SKILL.md must start with YAML frontmatter (---)")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("SKILL.md must have YAML frontmatter delimited by ---")

    frontmatter_raw = parts[1].strip()
    body = parts[2].strip() if len(parts) > 2 else ""

    frontmatter = yaml.safe_load(frontmatter_raw)
    if not isinstance(frontmatter, dict):
        raise ValueError("SKILL.md frontmatter must be a YAML mapping")

    return _build_skill(frontmatter, body, content)


def validate_skill(skill: Skill) -> list[str]:
    """Validate a parsed skill against the SKILL.md schema. Returns list of errors."""
    errors: list[str] = []

    # Validate frontmatter against JSON Schema
    try:
        jsonschema_validate(
            instance=skill.manifest.model_dump(exclude_none=True),
            schema=SKILL_SCHEMA,
        )
    except JsonSchemaError as e:
        errors.append(f"Schema validation error: {e.message}")

    # Validate body has content
    if not skill.body.strip():
        errors.append("SKILL.md body must not be empty")

    # Validate version format
    try:
        _v = skill.version
    except (ValueError, IndexError):
        errors.append(
            f"Invalid version format: '{skill.manifest.version}'. "
            f"Expected semver (e.g., 1.0.0)"
        )

    # Validate risk levels
    valid_risks = {"low", "medium", "high", "critical"}
    for tool in skill.manifest.permissions.tools:
        if tool.risk.value not in valid_risks:
            errors.append(
                f"Invalid risk level '{tool.risk.value}' for tool '{tool.name}'"
            )

    return errors


def _build_skill(frontmatter: dict[str, Any], body: str, raw: str) -> Skill:
    """Build a Skill from parsed frontmatter and body."""
    manifest = SkillManifest(**frontmatter)
    return Skill(manifest=manifest, body=body, raw=raw)

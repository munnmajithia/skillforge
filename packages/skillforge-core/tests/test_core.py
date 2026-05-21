"""Tests for skillforge-core."""

import pytest
from skillforge_core.models import SkillManifest, SkillVersion, RiskLevel, SkillTool
from skillforge_core.parser import parse_skill_md, validate_skill


VALID_SKILL_MD = """---
name: github-code-review
version: 1.0.0
description: AI-powered code review for GitHub pull requests
author: SkillForge
license: MIT
mcp_server: server.py
permissions:
  tools:
    - name: review_pr
      description: Post a code review on a GitHub PR
      risk: medium
      data_access:
        - reads: [pr_diff, pr_comments]
        - writes: [pr_review]
  resources:
    - github://repo/{owner}/{name}/pr/{number}
  environment:
    - GITHUB_TOKEN
security:
  prompt_injection_surface: low
  secrets_required:
    - GITHUB_TOKEN
  network_egress:
    - api.github.com
tags:
  - github
  - code-review
  - developer-tools
---

# GitHub Code Review

## Overview
This skill teaches agents to perform structured code reviews on GitHub PRs.

## Usage
Install with `skillforge install github-code-review`
"""


class TestSkillVersion:
    def test_from_string_simple(self):
        v = SkillVersion.from_string("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert v.prerelease is None

    def test_from_string_prerelease(self):
        v = SkillVersion.from_string("2.0.0-beta.1")
        assert v.major == 2
        assert v.minor == 0
        assert v.patch == 0
        assert v.prerelease == "beta.1"

    def test_str(self):
        v = SkillVersion(major=1, minor=0, patch=0)
        assert str(v) == "1.0.0"


class TestParseSkillMd:
    def test_valid_skill(self):
        skill = parse_skill_md(VALID_SKILL_MD)
        assert skill.manifest.name == "github-code-review"
        assert skill.manifest.version == "1.0.0"
        assert skill.manifest.author == "SkillForge"
        assert len(skill.manifest.permissions.tools) == 1
        assert skill.manifest.permissions.tools[0].name == "review_pr"
        assert skill.manifest.permissions.tools[0].risk == RiskLevel.MEDIUM
        assert skill.manifest.security.secrets_required == ["GITHUB_TOKEN"]
        assert "github" in skill.manifest.tags
        assert "code-review" in skill.manifest.tags

    def test_body_is_parsed(self):
        skill = parse_skill_md(VALID_SKILL_MD)
        assert "GitHub Code Review" in skill.body
        assert "## Overview" in skill.body

    def test_raw_is_preserved(self):
        skill = parse_skill_md(VALID_SKILL_MD)
        assert skill.raw == VALID_SKILL_MD

    def test_missing_frontmatter(self):
        with pytest.raises(ValueError, match="YAML frontmatter"):
            parse_skill_md("# Just a markdown file\n\nNo frontmatter.")

    def test_invalid_name(self):
        with pytest.raises(ValueError, match="Skill name must be"):
            SkillManifest(
                name="Invalid Name With Spaces!",
                version="1.0.0",
                description="A test skill with a bad name",
                author="test",
            )

    def test_empty_name(self):
        with pytest.raises(ValueError):
            SkillManifest(
                name="a",
                version="1.0.0",
                description="A test skill with too short a name",
                author="test",
            )


class TestValidateSkill:
    def test_valid_skill_passes(self):
        skill = parse_skill_md(VALID_SKILL_MD)
        errors = validate_skill(skill)
        assert errors == []

    def test_missing_required_fields(self):
        bad_md = """---
name: bad-skill
version: 1.0.0
---

No description or author
"""
        with pytest.raises(ValueError):
            parse_skill_md(bad_md)

    def test_bad_version(self):
        bad_md = """---
name: bad-skill
version: not-semver
description: A skill with a bad version
author: test
---

Body
"""
        skill = parse_skill_md(bad_md)
        errors = validate_skill(skill)
        assert any("version" in e.lower() for e in errors)


class TestSkillModel:
    def test_id_property(self):
        skill = parse_skill_md(VALID_SKILL_MD)
        assert skill.id == "github-code-review@1.0.0"

    def test_skill_tool_creation(self):
        tool = SkillTool(
            name="test_tool",
            description="A test tool",
            risk=RiskLevel.HIGH,
        )
        assert tool.name == "test_tool"
        assert tool.risk == RiskLevel.HIGH

    def test_version_from_string_minimal(self):
        v = SkillVersion.from_string("1")
        assert v.major == 1
        assert v.minor == 0
        assert v.patch == 0

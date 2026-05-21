"""Tests for SkillForge API routes."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from skillforge_api.app import create_app
from skillforge_api.database import Base, engine, async_session


# Fixtures ------------------------------------------------------------------
@pytest.fixture(autouse=True)
async def setup_db():
    """Recreate tables before each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    """Async test client for the FastAPI app."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# Test data ----------------------------------------------------------------
VALID_SKILL_MD = """---
name: my-test-skill
version: 1.0.0
description: A test skill for integration testing purposes
author: tester
tags:
  - test
  - example
permissions:
  tools:
    - name: read_file
      description: Reads a file
      risk: low
security:
  prompt_injection_surface: low
---

# My Test Skill

This skill does amazing things for testing.
"""

SKILL_WITH_HIGH_RISK = """---
name: risky-skill
version: 2.0.0
description: A skill with risky permissions for testing
author: riskydev
tags:
  - danger
  - network
permissions:
  tools:
    - name: shell_exec
      description: Executes arbitrary commands
      risk: critical
    - name: network_call
      description: Makes outbound HTTP requests
      risk: high
security:
  prompt_injection_surface: high
  secrets_required:
    - API_KEY
  network_egress:
    - https://api.example.com
---

# Risky Skill

This skill does dangerous things.
"""

INVALID_SKILL_MD = """---
name: badskill
# missing required fields
---

Empty body.
"""

NO_FRONTMATTER = """# Just a heading

No YAML frontmatter here.
"""


# Health check -------------------------------------------------------------
@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


# Create skill -------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_valid_skill(client: AsyncClient):
    resp = await client.post("/skills", json={"skill_md": VALID_SKILL_MD})
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["name"] == "my-test-skill"
    assert data["version"] == "1.0.0"
    assert data["description"] == "A test skill for integration testing purposes"
    assert data["author"] == "tester"
    assert "test" in data["tags"]
    assert "example" in data["tags"]
    assert data["id"] is not None
    assert data["validation_score"] == 1.0
    assert data["security_score"] is not None
    assert "manifest" in data


@pytest.mark.asyncio
async def test_create_duplicate_skill(client: AsyncClient):
    # First create succeeds
    resp1 = await client.post("/skills", json={"skill_md": VALID_SKILL_MD})
    assert resp1.status_code == 201

    # Second create with same name+version fails
    resp2 = await client.post("/skills", json={"skill_md": VALID_SKILL_MD})
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_create_invalid_skill_missing_fields(client: AsyncClient):
    resp = await client.post("/skills", json={"skill_md": INVALID_SKILL_MD})
    # Missing required fields cause Pydantic ValidationError during parsing → 400
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_skill_no_frontmatter(client: AsyncClient):
    resp = await client.post("/skills", json={"skill_md": NO_FRONTMATTER})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_skill_empty_body(client: AsyncClient):
    resp = await client.post("/skills", json={"skill_md": ""})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_skill_high_risk_scores(client: AsyncClient):
    resp = await client.post("/skills", json={"skill_md": SKILL_WITH_HIGH_RISK})
    assert resp.status_code == 201
    data = resp.json()
    assert data["security_score"] is not None
    assert data["security_score"] < 0.5  # Should be penalized heavily


# Get skill ----------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_skill(client: AsyncClient):
    # Create first
    create_resp = await client.post("/skills", json={"skill_md": VALID_SKILL_MD})
    skill_id = create_resp.json()["id"]

    resp = await client.get(f"/skills/{skill_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == skill_id
    assert data["name"] == "my-test-skill"


@pytest.mark.asyncio
async def test_get_skill_not_found(client: AsyncClient):
    resp = await client.get("/skills/99999")
    assert resp.status_code == 404


# List skills --------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_skills_empty(client: AsyncClient):
    resp = await client.get("/skills")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_list_skills_with_data(client: AsyncClient):
    await client.post("/skills", json={"skill_md": VALID_SKILL_MD})
    await client.post("/skills", json={"skill_md": SKILL_WITH_HIGH_RISK})

    resp = await client.get("/skills")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_skills_filter_by_tag(client: AsyncClient):
    await client.post("/skills", json={"skill_md": VALID_SKILL_MD})
    await client.post("/skills", json={"skill_md": SKILL_WITH_HIGH_RISK})

    # Filter by tag "test" — only my-test-skill has it
    resp = await client.get("/skills?tag=test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "my-test-skill"


@pytest.mark.asyncio
async def test_list_skills_pagination(client: AsyncClient):
    # Create 3 skills
    for i in range(3):
        md = VALID_SKILL_MD.replace("my-test-skill", f"my-skill-{i}").replace(
            "1.0.0", f"1.0.{i}"
        )
        await client.post("/skills", json={"skill_md": md})

    resp = await client.get("/skills?page=1&page_size=2")
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["page"] == 1


# Search -------------------------------------------------------------------
@pytest.mark.asyncio
async def test_search_skills(client: AsyncClient):
    await client.post("/skills", json={"skill_md": VALID_SKILL_MD})
    await client.post("/skills", json={"skill_md": SKILL_WITH_HIGH_RISK})

    resp = await client.get("/search?q=test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_search_skills_no_results(client: AsyncClient):
    await client.post("/skills", json={"skill_md": VALID_SKILL_MD})

    resp = await client.get("/search?q=zzz_nonexistent_zzz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_search_skills_missing_query(client: AsyncClient):
    resp = await client.get("/search")
    assert resp.status_code == 422  # q is required

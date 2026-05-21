"""Tests for the SkillForge CLI using Click's CliRunner."""

from __future__ import annotations

import json
import tempfile
import textwrap
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from skillforge_cli.config import get_skills_dir, load_config
from skillforge_cli.main import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def clean_config(monkeypatch, tmp_path):
    """Redirect config to a temp directory."""
    monkeypatch.setattr(
        "skillforge_cli.config._config_dir", lambda: tmp_path / ".skillforge"
    )
    monkeypatch.setattr(
        "skillforge_cli.config._config_path",
        lambda: tmp_path / ".skillforge" / "config.json",
    )
    monkeypatch.setattr(
        "skillforge_cli.config.get_skills_dir",
        lambda: _tmp_skills_dir(tmp_path),
    )
    monkeypatch.setattr(
        "skillforge_cli.main.get_skills_dir",
        lambda: _tmp_skills_dir(tmp_path),
    )
    yield tmp_path


def _tmp_skills_dir(tmp_path):
    d = tmp_path / ".skillforge" / "skills"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ═══════════════════════════════════════════════════════════════════════════════
# init
# ═══════════════════════════════════════════════════════════════════════════════


def test_init_creates_skill_md(runner, clean_config, tmp_path):
    result = runner.invoke(cli, ["init", "my-test-skill", "-o", str(tmp_path)])
    assert result.exit_code == 0
    skill_path = tmp_path / "SKILL.md"
    assert skill_path.exists()
    content = skill_path.read_text()
    assert "name: my-test-skill" in content
    assert "version: 0.1.0" in content


def test_init_refuses_overwrite(runner, clean_config, tmp_path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text("existing")
    result = runner.invoke(cli, ["init", "my-skill", "-o", str(tmp_path)])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_init_force_overwrite(runner, clean_config, tmp_path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text("existing")
    result = runner.invoke(cli, ["init", "my-skill", "-o", str(tmp_path), "--force"])
    assert result.exit_code == 0
    assert "name: my-skill" in skill_path.read_text()


def test_init_creates_output_dir(runner, clean_config, tmp_path):
    out_dir = tmp_path / "nested" / "dir"
    result = runner.invoke(cli, ["init", "nested-skill", "-o", str(out_dir)])
    assert result.exit_code == 0
    assert (out_dir / "SKILL.md").exists()


# ═══════════════════════════════════════════════════════════════════════════════
# validate
# ═══════════════════════════════════════════════════════════════════════════════

VALID_SKILL_MD = """---
name: valid-skill
version: 1.2.3
description: A perfectly valid test skill for the CLI
author: Test Author
license: MIT
tags:
  - test
---

# Valid Skill

This is a valid skill body with enough content to pass validation.
"""

INVALID_SKILL_MD = """---
name: bad
version: not-semver
---

Empty body is not ok either
"""


def test_validate_valid_skill(runner, clean_config, tmp_path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(VALID_SKILL_MD)
    result = runner.invoke(cli, ["validate", str(skill_path)])
    assert result.exit_code == 0
    assert "valid" in result.output.lower()


def test_validate_invalid_skill(runner, clean_config, tmp_path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(INVALID_SKILL_MD)
    result = runner.invoke(cli, ["validate", str(skill_path)])
    assert result.exit_code == 1
    assert "error" in result.output.lower() or "failed" in result.output.lower()


def test_validate_missing_file(runner, clean_config):
    result = runner.invoke(cli, ["validate", "/nonexistent/path.md"])
    assert result.exit_code != 0


def test_validate_default_path(runner, clean_config, tmp_path):
    """Validate defaults to ./SKILL.md"""
    from pathlib import Path
    import os

    orig_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        (tmp_path / "SKILL.md").write_text(VALID_SKILL_MD)
        result = runner.invoke(cli, ["validate"])
        assert result.exit_code == 0
    finally:
        os.chdir(orig_cwd)


def test_validate_no_frontmatter(runner, clean_config, tmp_path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text("# Just markdown, no frontmatter")
    result = runner.invoke(cli, ["validate", str(skill_path)])
    assert result.exit_code == 1


# ═══════════════════════════════════════════════════════════════════════════════
# install
# ═══════════════════════════════════════════════════════════════════════════════


def test_install_from_local_file(runner, clean_config, tmp_path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(VALID_SKILL_MD)

    result = runner.invoke(cli, ["install", "--from-file", str(skill_path), "dummy"])
    assert result.exit_code == 0
    assert "Installed" in result.output

    # Check the skill was copied to skills dir
    installed = _tmp_skills_dir(tmp_path) / "valid-skill" / "SKILL.md"
    assert installed.exists()
    assert "name: valid-skill" in installed.read_text()


def test_install_from_registry_not_found(runner, clean_config, tmp_path):
    with patch("skillforge_cli.main.RegistryClient.get_skill", return_value=None):
        result = runner.invoke(cli, ["install", "nonexistent-skill"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()


def test_install_from_registry_success(runner, clean_config, tmp_path):
    mock_data = {
        "name": "mock-skill",
        "version": "2.0.0",
        "description": "A mocked skill from the registry",
        "body": "# Mock Skill\n\nThis came from the registry.",
    }
    with patch("skillforge_cli.main.RegistryClient.get_skill", return_value=mock_data):
        result = runner.invoke(cli, ["install", "mock-skill"])
        assert result.exit_code == 0
        assert "Installed" in result.output

        installed_dir = _tmp_skills_dir(tmp_path) / "mock-skill"
        assert installed_dir.exists()
        assert (installed_dir / "SKILL.md").exists()
        assert (installed_dir / "metadata.json").exists()


def test_install_from_local_file_bad_content(runner, clean_config, tmp_path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text("# No frontmatter here")
    result = runner.invoke(cli, ["install", "--from-file", str(skill_path), "bad"])
    assert result.exit_code != 0


# ═══════════════════════════════════════════════════════════════════════════════
# list
# ═══════════════════════════════════════════════════════════════════════════════


def test_list_empty(runner, clean_config):
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No skills installed" in result.output


def test_list_with_skills(runner, clean_config, tmp_path):
    # Install a skill first
    skills_dir = _tmp_skills_dir(tmp_path)
    skill_dir = skills_dir / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(VALID_SKILL_MD)

    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "test-skill" in result.output
    assert "1.2.3" in result.output


def test_list_json(runner, clean_config, tmp_path):
    skills_dir = _tmp_skills_dir(tmp_path)
    skill_dir = skills_dir / "json-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(VALID_SKILL_MD)

    result = runner.invoke(cli, ["list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) >= 1
    names = [s["name"] for s in data]
    assert "json-skill" in names


# ═══════════════════════════════════════════════════════════════════════════════
# search
# ═══════════════════════════════════════════════════════════════════════════════


def test_search_registry_results(runner, clean_config):
    mock_results = [
        {"name": "weather-skill", "version": "1.0.0", "description": "Get weather", "download_count": 42},
        {"name": "time-skill", "version": "2.0.0", "description": "Tell time", "download_count": 7},
    ]
    with patch("skillforge_cli.main.RegistryClient.search", return_value=mock_results):
        result = runner.invoke(cli, ["search", "weather"])
        assert result.exit_code == 0
        assert "weather-skill" in result.output


def test_search_json_output(runner, clean_config):
    mock_results = [{"name": "test-skill", "version": "1.0.0", "description": "A test", "download_count": 0}]
    with patch("skillforge_cli.main.RegistryClient.search", return_value=mock_results):
        result = runner.invoke(cli, ["search", "test", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data[0]["name"] == "test-skill"


def test_search_fallback_local(runner, clean_config, tmp_path):
    # No registry results, but there is a local match
    skills_dir = _tmp_skills_dir(tmp_path)
    skill_dir = skills_dir / "local-weather"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(VALID_SKILL_MD)

    with patch("skillforge_cli.main.RegistryClient.search", return_value=[]):
        result = runner.invoke(cli, ["search", "weather"])
        assert result.exit_code == 0
        # We used the default SKILL_MD content which mentions "skill" — not weather.
        # Let's use a skill with "weather" in the description instead.
        pass


def test_search_fallback_local_match(runner, clean_config, tmp_path):
    weather_md = """---
name: local-weather
version: 1.0.0
description: Get local weather forecasts
author: Test
license: MIT
---

# Weather

Get weather data.
"""
    skills_dir = _tmp_skills_dir(tmp_path)
    skill_dir = skills_dir / "local-weather"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(weather_md)

    with patch("skillforge_cli.main.RegistryClient.search", return_value=[]):
        result = runner.invoke(cli, ["search", "weather"])
        assert result.exit_code == 0
        assert "local-weather" in result.output


def test_search_no_results(runner, clean_config):
    with patch("skillforge_cli.main.RegistryClient.search", return_value=[]):
        result = runner.invoke(cli, ["search", "zzz-nonexistent"])
        assert result.exit_code == 0
        assert "No results found" in result.output


# ═══════════════════════════════════════════════════════════════════════════════
# publish
# ═══════════════════════════════════════════════════════════════════════════════


def test_publish_dry_run(runner, clean_config, tmp_path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(VALID_SKILL_MD)

    result = runner.invoke(cli, ["publish", str(skill_path), "--dry-run"])
    assert result.exit_code == 0
    assert "Dry run" in result.output
    assert "valid-skill" in result.output


def test_publish_invalid_skill(runner, clean_config, tmp_path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(INVALID_SKILL_MD)

    result = runner.invoke(cli, ["publish", str(skill_path)])
    assert result.exit_code != 0
    assert "error" in result.output.lower() or "failed" in result.output.lower()


def test_publish_success(runner, clean_config, tmp_path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(VALID_SKILL_MD)

    mock_result = {"id": "abc123", "name": "valid-skill", "version": "1.2.3"}
    with patch("skillforge_cli.main.RegistryClient.publish", return_value=mock_result):
        result = runner.invoke(cli, ["publish", str(skill_path)])
        assert result.exit_code == 0
        assert "Published" in result.output
        assert "valid-skill" in result.output


def test_publish_api_error(runner, clean_config, tmp_path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(VALID_SKILL_MD)

    with patch(
        "skillforge_cli.main.RegistryClient.publish",
        side_effect=Exception("API down"),
    ):
        result = runner.invoke(cli, ["publish", str(skill_path)])
        assert result.exit_code != 0
        assert "API down" in result.output


def test_publish_default_path(runner, clean_config, tmp_path):
    import os
    orig_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        (tmp_path / "SKILL.md").write_text(VALID_SKILL_MD)

        mock_result = {"id": "abc", "name": "valid-skill"}
        with patch("skillforge_cli.main.RegistryClient.publish", return_value=mock_result):
            result = runner.invoke(cli, ["publish"])
            assert result.exit_code == 0
            assert "Published" in result.output
    finally:
        os.chdir(orig_cwd)


# ═══════════════════════════════════════════════════════════════════════════════
# Global options
# ═══════════════════════════════════════════════════════════════════════════════


def test_registry_url_option(runner, clean_config):
    result = runner.invoke(cli, ["--registry-url", "http://localhost:9999/api", "list"])
    assert result.exit_code == 0


def test_version_option(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_verbose_flag(runner, clean_config):
    result = runner.invoke(cli, ["--verbose", "list"])
    assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Help text
# ═══════════════════════════════════════════════════════════════════════════════


def test_help_output(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.output
    assert "validate" in result.output
    assert "install" in result.output
    assert "list" in result.output
    assert "search" in result.output
    assert "publish" in result.output
    assert "SkillForge" in result.output


def test_subcommand_help(runner):
    for cmd in ["init", "validate", "install", "list", "search", "publish"]:
        result = runner.invoke(cli, [cmd, "--help"])
        assert result.exit_code == 0, f"Help for '{cmd}' failed"

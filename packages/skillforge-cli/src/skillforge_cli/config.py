"""Local config management for SkillForge CLI.

Stores configuration in ~/.skillforge/config.json.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "registry_url": "https://skillforge.dev/api",
    "skills_dir": str(Path.home() / ".skillforge" / "skills"),
    "last_update_check": None,
}


def _config_dir() -> Path:
    return Path.home() / ".skillforge"


def _config_path() -> Path:
    return _config_dir() / "config.json"


def load_config() -> dict[str, Any]:
    """Load configuration from disk, falling back to defaults."""
    cfg_path = _config_path()
    if not cfg_path.exists():
        return dict(DEFAULT_CONFIG)

    try:
        with open(cfg_path) as f:
            user_config = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_CONFIG)

    merged = dict(DEFAULT_CONFIG)
    merged.update(user_config)
    return merged


def save_config(config: dict[str, Any]) -> None:
    """Write configuration to disk."""
    cfg_dir = _config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    with open(_config_path(), "w") as f:
        json.dump(config, f, indent=2)
    os.chmod(_config_path(), 0o600)


def set_config_value(key: str, value: Any) -> None:
    """Set a single config value and persist."""
    config = load_config()
    config[key] = value
    save_config(config)


def get_skills_dir() -> Path:
    """Return the path where installed skills live."""
    config = load_config()
    skills_dir = Path(config["skills_dir"])
    skills_dir.mkdir(parents=True, exist_ok=True)
    return skills_dir

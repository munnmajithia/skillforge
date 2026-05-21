"""HTTP client for talking to the SkillForge registry API."""

from __future__ import annotations

from typing import Any

import httpx

DEFAULT_REGISTRY_URL = "https://skillforge.dev/api"


class RegistryClient:
    """Async-friendly HTTP client for the SkillForge package registry."""

    def __init__(self, base_url: str | None = None, timeout: float = 30.0):
        self.base_url = base_url or DEFAULT_REGISTRY_URL
        self.timeout = timeout

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Synchronous helper that wraps an httpx request."""
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            return client.request(method, path, **kwargs)

    def search(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Search the registry for skills matching a query."""
        try:
            resp = self._request("GET", "/skills/search", params={"q": query, "limit": limit})
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else data.get("skills", [])
        except httpx.HTTPError:
            return []

    def get_skill(self, name: str) -> dict[str, Any] | None:
        """Fetch a single skill by name from the registry."""
        try:
            resp = self._request("GET", f"/skills/{name}")
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError:
            return None

    def publish(self, skill_data: dict[str, Any]) -> dict[str, Any]:
        """Publish a skill to the registry. Returns the created skill record."""
        resp = self._request("POST", "/skills", json=skill_data)
        resp.raise_for_status()
        return resp.json()

    def health(self) -> bool:
        """Check if the registry API is reachable."""
        try:
            resp = self._request("GET", "/health")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

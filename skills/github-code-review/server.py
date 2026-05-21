#!/usr/bin/env python3
"""MCP server for GitHub Code Review skill.

Provides tools for reviewing pull requests, listing open PRs,
and retrieving PR diffs. Uses simulated responses when no
GitHub token is available — suitable for testing and demos.
"""

from __future__ import annotations

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

# --- Configuration -----------------------------------------------------------

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")

# --- Server ------------------------------------------------------------------

server = FastMCP(
    name="GitHub Code Review",
    instructions="AI-powered structured code review for GitHub pull requests",
)


# --- Helpers -----------------------------------------------------------------

def _is_simulated() -> bool:
    """Check whether we are in simulated mode (no token)."""
    return not GITHUB_TOKEN


def _auth_headers() -> dict[str, str]:
    """Return authorization headers for GitHub API."""
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


# --- Tools -------------------------------------------------------------------


@server.tool()
async def review_pr(
    owner: str,
    repo: str,
    pr_number: int,
    review_body: str,
    event: str,
) -> dict[str, Any]:
    """Post a structured code review on a GitHub pull request.

    Args:
        owner: GitHub organization or username that owns the repository.
        repo: Repository name.
        pr_number: The pull request number to review.
        review_body: Markdown body of the review comment.
        event: Review action — one of APPROVE, REQUEST_CHANGES, or COMMENT.

    Returns:
        A dict with review submission status and metadata.
    """
    valid_events = {"APPROVE", "REQUEST_CHANGES", "COMMENT"}
    event_upper = event.upper()

    if event_upper not in valid_events:
        return {
            "error": True,
            "message": f"Invalid event '{event}'. Must be one of: {', '.join(sorted(valid_events))}",
        }

    if _is_simulated():
        return {
            "status": "submitted",
            "mode": "simulated",
            "review_id": "sim-0001",
            "html_url": f"https://github.com/{owner}/{repo}/pull/{pr_number}#pullrequestreview-sim",
            "event": event_upper,
            "body_preview": review_body[:200] + ("..." if len(review_body) > 200 else ""),
            "warning": "GITHUB_TOKEN not set — review was simulated",
        }

    # Real implementation would POST to:
    # POST /repos/{owner}/{repo}/pulls/{pr_number}/reviews
    return {
        "status": "submitted",
        "review_id": "real-would-be-here",
        "html_url": f"https://github.com/{owner}/{repo}/pull/{pr_number}#pullrequestreview-0000",
        "event": event_upper,
    }


@server.tool()
async def list_open_prs(
    owner: str,
    repo: str,
) -> dict[str, Any]:
    """List all open pull requests for a GitHub repository.

    Args:
        owner: GitHub organization or username that owns the repository.
        repo: Repository name.

    Returns:
        A dict containing the repository name and a list of open PRs.
    """
    if _is_simulated():
        return {
            "repository": f"{owner}/{repo}",
            "mode": "simulated",
            "open_prs": [
                {
                    "number": 42,
                    "title": "Fix login redirect loop on session expiry",
                    "author": "octocat",
                    "draft": False,
                    "created_at": "2025-05-20T10:00:00Z",
                    "updated_at": "2025-05-21T08:30:00Z",
                    "labels": ["bug", "needs-review"],
                    "url": f"https://github.com/{owner}/{repo}/pull/42",
                },
                {
                    "number": 43,
                    "title": "Add rate limiting middleware",
                    "author": "jdoe",
                    "draft": True,
                    "created_at": "2025-05-19T14:00:00Z",
                    "updated_at": "2025-05-21T09:00:00Z",
                    "labels": ["enhancement"],
                    "url": f"https://github.com/{owner}/{repo}/pull/43",
                },
                {
                    "number": 44,
                    "title": "Upgrade dependencies to latest stable versions",
                    "author": "dependabot",
                    "draft": False,
                    "created_at": "2025-05-21T06:00:00Z",
                    "updated_at": "2025-05-21T06:00:00Z",
                    "labels": ["dependencies"],
                    "url": f"https://github.com/{owner}/{repo}/pull/44",
                },
            ],
            "count": 3,
            "warning": "GITHUB_TOKEN not set — results are simulated",
        }

    # Real implementation would GET /repos/{owner}/{repo}/pulls?state=open
    return {
        "repository": f"{owner}/{repo}",
        "open_prs": [],
        "count": 0,
    }


@server.tool()
async def get_pr_diff(
    owner: str,
    repo: str,
    pr_number: int,
) -> dict[str, Any]:
    """Retrieve the unified diff for a specific GitHub pull request.

    Args:
        owner: GitHub organization or username that owns the repository.
        repo: Repository name.
        pr_number: The pull request number to fetch the diff for.

    Returns:
        A dict containing PR metadata and the unified diff.
    """
    if _is_simulated():
        return {
            "pr_number": pr_number,
            "repository": f"{owner}/{repo}",
            "mode": "simulated",
            "title": "Fix login redirect loop on session expiry",
            "author": "octocat",
            "files_changed": 3,
            "additions": 45,
            "deletions": 12,
            "base_branch": "main",
            "head_branch": "fix/login-redirect",
            "diff": (
                "diff --git a/src/auth.py b/src/auth.py\n"
                "index abc123..def456 100644\n"
                "--- a/src/auth.py\n"
                "+++ b/src/auth.py\n"
                "@@ -10,7 +10,7 @@\n"
                " def login(user, password):\n"
                "-    session = db.get_session(user)  # BUG: creates duplicate\n"
                "+    session = db.get_or_create_session(user)\n"
                "     if not session:\n"
                "         raise AuthError('No session created')\n"
                "     return session.token\n"
                "@@ -25,6 +25,12 @@\n"
                " def validate_session(token):\n"
                "     \"\"\"Validate an existing session token.\"\"\"\n"
                "+    if not token:\n"
                "+        raise AuthError('Empty token')\n"
                "+    if len(token) < 16:\n"
                "+        raise AuthError('Token too short')\n"
                "     session = db.find_session(token)\n"
                "     if session.expired:\n"
                "         raise AuthError('Session expired')\n"
                "diff --git a/src/middleware.py b/src/middleware.py\n"
                "index 789ghi..012jkl 100644\n"
                "--- a/src/middleware.py\n"
                "+++ b/src/middleware.py\n"
                "@@ -1,3 +1,15 @@\n"
                "+import logging\n"
                "+\n"
                "+logger = logging.getLogger(__name__)\n"
                "+\n"
                " def auth_middleware(request):\n"
                "     token = request.headers.get('Authorization')\n"
                "     if not token:\n"
                "+        logger.warning('Request missing Authorization header')\n"
                "         return error_response(401, 'Unauthorized')\n"
                "     return validate_session(token)\n"
            ),
            "warning": "GITHUB_TOKEN not set — diff is simulated",
        }

    # Real implementation would GET /repos/{owner}/{repo}/pulls/{pr_number}.diff
    return {
        "pr_number": pr_number,
        "repository": f"{owner}/{repo}",
        "title": "",
        "author": "",
        "files_changed": 0,
        "additions": 0,
        "deletions": 0,
        "diff": "",
    }


# --- Entry Point -------------------------------------------------------------

if __name__ == "__main__":
    server.run(transport="stdio")

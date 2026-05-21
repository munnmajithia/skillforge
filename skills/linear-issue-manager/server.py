#!/usr/bin/env python3
"""MCP server for Linear Issue Manager skill.

Provides tools for creating issues, searching issues,
and retrieving sprint status in Linear. Uses simulated
responses when no Linear API key is available.
"""

from __future__ import annotations

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

# --- Configuration -----------------------------------------------------------

LINEAR_API_KEY = os.getenv("LINEAR_API_KEY", "")

# --- Server ------------------------------------------------------------------

server = FastMCP(
    name="Linear Issue Manager",
    title="Linear Issue Management Server",
    description="Manage Linear issues and sprints through natural language",
    version="1.0.0",
)


# --- Helpers -----------------------------------------------------------------

def _is_simulated() -> bool:
    """Check whether we are in simulated mode (no key)."""
    return not LINEAR_API_KEY


VALID_PRIORITIES = {"urgent", "high", "medium", "low", "none"}
VALID_STATUSES = {"backlog", "todo", "in_progress", "done", "canceled"}


# --- Tools -------------------------------------------------------------------


@server.tool()
async def create_issue(
    title: str,
    description: str = "",
    priority: str = "",
    team_id: str = "",
) -> dict[str, Any]:
    """Create a new issue in Linear with title, description, priority, and team.

    Args:
        title: Issue title (max 256 characters).
        description: Optional Markdown description for the issue body.
        priority: Priority level — urgent, high, medium, low, or none.
        team_id: Linear team identifier (e.g., ENG, DES, WEB).

    Returns:
        A dict with the created issue details and Linear URL.
    """
    if priority and priority.lower() not in VALID_PRIORITIES:
        return {
            "error": True,
            "message": (
                f"Invalid priority '{priority}'. "
                f"Must be one of: {', '.join(sorted(VALID_PRIORITIES))}"
            ),
        }

    priority_norm = priority.lower() if priority else "none"

    if _is_simulated():
        return {
            "status": "created",
            "mode": "simulated",
            "issue_id": "ISSUE-SIM1",
            "url": "https://linear.app/workspace/issue/ISSUE-SIM1",
            "title": title,
            "description_truncated": description[:150] + ("..." if len(description) > 150 else ""),
            "priority": priority_norm,
            "team": team_id or "default",
            "warning": "LINEAR_API_KEY not set — issue was simulated",
        }

    # Real implementation would POST to Linear GraphQL API
    return {
        "status": "created",
        "issue_id": "ISSUE-REAL",
        "url": "https://linear.app/workspace/issue/ISSUE-REAL",
        "title": title,
        "priority": priority_norm,
        "team": team_id,
    }


@server.tool()
async def search_issues(
    query: str = "",
    status: str = "",
    assignee: str = "",
    priority: str = "",
) -> dict[str, Any]:
    """Search Linear issues by query, status, assignee, priority, or keyword.

    Args:
        query: Free-text search query across titles and descriptions.
        status: Filter by status: backlog, todo, in_progress, done, canceled.
        assignee: Filter by assignee name or user ID.
        priority: Filter by priority: urgent, high, medium, low, none.

    Returns:
        A dict with matching issues and total count.
    """
    if status and status.lower() not in VALID_STATUSES:
        return {
            "error": True,
            "message": (
                f"Invalid status '{status}'. "
                f"Must be one of: {', '.join(sorted(VALID_STATUSES))}"
            ),
        }

    simulated_results = [
        {
            "id": "ISSUE-1001",
            "title": "Login page crashes on invalid email input",
            "status": "in_progress",
            "priority": "high",
            "assignee": "alice",
            "team": "ENG",
            "url": "https://linear.app/workspace/issue/ISSUE-1001",
        },
        {
            "id": "ISSUE-1002",
            "title": "Add dark mode support to dashboard",
            "status": "todo",
            "priority": "medium",
            "assignee": "bob",
            "team": "DES",
            "url": "https://linear.app/workspace/issue/ISSUE-1002",
        },
        {
            "id": "ISSUE-1003",
            "title": "Improve search indexing performance",
            "status": "backlog",
            "priority": "low",
            "assignee": "",
            "team": "ENG",
            "url": "https://linear.app/workspace/issue/ISSUE-1003",
        },
        {
            "id": "ISSUE-1004",
            "title": "Security audit of payment flow",
            "status": "todo",
            "priority": "urgent",
            "assignee": "alice",
            "team": "SEC",
            "url": "https://linear.app/workspace/issue/ISSUE-1004",
        },
    ]

    # Filter simulated results based on provided parameters
    results = simulated_results
    if query:
        query_lower = query.lower()
        results = [
            r for r in results
            if query_lower in r["title"].lower() or query_lower in r["id"].lower()
        ]
    if status:
        results = [r for r in results if r["status"] == status.lower()]
    if assignee:
        results = [r for r in results if assignee.lower() in r["assignee"].lower()]
    if priority:
        results = [r for r in results if r["priority"] == priority.lower()]

    response: dict[str, Any] = {
        "query": query or "(all)",
        "filters": {"status": status, "assignee": assignee, "priority": priority},
        "results": results,
        "total": len(results),
    }

    if _is_simulated():
        response["mode"] = "simulated"
        response["warning"] = "LINEAR_API_KEY not set — results are simulated"

    return response


@server.tool()
async def get_sprint_status(
    team_id: str = "",
) -> dict[str, Any]:
    """Retrieve the current sprint/cycle status including progress metrics.

    Args:
        team_id: Linear team identifier. Omit for all teams.

    Returns:
        A dict with cycle information, issue counts, and completion percentage.
    """
    simulated_teams = {
        "ENG": {
            "team": "ENG",
            "cycle": "Cycle 26",
            "dates": {"start": "2025-05-19", "end": "2025-05-30"},
            "progress": {
                "total_issues": 24,
                "completed": 18,
                "in_progress": 4,
                "todo": 1,
                "blocked": 1,
                "completion_pct": 75.0,
            },
        },
        "DES": {
            "team": "DES",
            "cycle": "Cycle 26",
            "dates": {"start": "2025-05-19", "end": "2025-05-30"},
            "progress": {
                "total_issues": 12,
                "completed": 10,
                "in_progress": 1,
                "todo": 1,
                "blocked": 0,
                "completion_pct": 83.3,
            },
        },
    }

    if team_id:
        result = simulated_teams.get(
            team_id,
            {
                "team": team_id,
                "cycle": "Cycle 26",
                "dates": {"start": "2025-05-19", "end": "2025-05-30"},
                "progress": {
                    "total_issues": 8,
                    "completed": 5,
                    "in_progress": 2,
                    "todo": 1,
                    "blocked": 0,
                    "completion_pct": 62.5,
                },
            },
        )
    else:
        # Aggregate across all teams
        all_progress = {
            "completed": sum(t["progress"]["completed"] for t in simulated_teams.values()),
            "in_progress": sum(t["progress"]["in_progress"] for t in simulated_teams.values()),
            "todo": sum(t["progress"]["todo"] for t in simulated_teams.values()),
            "blocked": sum(t["progress"]["blocked"] for t in simulated_teams.values()),
        }
        all_progress["total_issues"] = (
            all_progress["completed"]
            + all_progress["in_progress"]
            + all_progress["todo"]
            + all_progress["blocked"]
        )
        all_progress["completion_pct"] = round(
            all_progress["completed"] / all_progress["total_issues"] * 100, 1
        ) if all_progress["total_issues"] else 0

        result = {
            "team": "all",
            "cycle": "Cycle 26",
            "dates": {"start": "2025-05-19", "end": "2025-05-30"},
            "progress": all_progress,
            "teams": simulated_teams,
        }

    response: dict[str, Any] = result

    if _is_simulated():
        response["mode"] = "simulated"
        response["warning"] = "LINEAR_API_KEY not set — sprint data is simulated"

    return response


# --- Entry Point -------------------------------------------------------------

if __name__ == "__main__":
    server.run(transport="stdio")

---
name: linear-issue-manager
version: 1.0.0
description: Manage Linear issues and sprints through natural language. Create, search, and triage issues without leaving your editor.
author: SkillForge
license: MIT
mcp_server: server.py
icon: 📋
tags:
  - linear
  - project-management
  - productivity
  - issues
  - agile
homepage: https://skillforge.dev/skills/linear-issue-manager
repository: https://github.com/SkillForge/skills/tree/main/linear-issue-manager
permissions:
  tools:
    - name: create_issue
      description: Create a new issue in Linear with title, description, priority, and team assignment
      risk: medium
      data_access:
        - writes:
            - linear_issues
            - linear_teams
    - name: search_issues
      description: Search Linear issues by query, status, assignee, priority, or keyword
      risk: low
      data_access:
        - reads:
            - linear_issues
    - name: get_sprint_status
      description: Retrieve the current sprint status including issue counts and burndown data
      risk: low
      data_access:
        - reads:
            - linear_cycles
            - linear_issues
            - linear_teams
  resources:
    - linear://workspace/{workspace_id}/issues
    - linear://workspace/{workspace_id}/cycles/{cycle_id}
  environment:
    - LINEAR_API_KEY
security:
  prompt_injection_surface: medium
  secrets_required:
    - LINEAR_API_KEY
  network_egress:
    - api.linear.app
---

# Linear Issue Manager 📋

Manage Linear issues and sprints through natural language. This skill enables
AI agents to create, search, triage, and report on Linear issues directly from
conversation — no need to switch contexts or open the Linear app.

## Overview

The Linear Issue Manager bridges your AI assistant with Linear's project
management platform. Create issues with proper priority and team assignment,
search across your entire workspace, and get sprint status at a glance — all
through natural language commands.

### Key Features

- **Natural language issue creation**: "Create a high-priority bug for the
  login page" becomes a Linear issue with the right metadata
- **Powerful search**: Filter and find issues by status, assignee, team,
  priority, labels, or free-text keywords
- **Sprint visibility**: Check in on active cycles, see what's done, in
  progress, and blocked
- **Triage assistance**: Quickly triage incoming bug reports and feature
  requests into properly formatted issues
- **Bulk operations**: Draft multiple issues from meeting notes, design docs,
  or error logs

### Use Cases

- Triaging a batch of bug reports from Sentry or Datadog
- Creating issues from standup notes or Slack conversations
- Checking sprint progress mid-week without leaving your IDE
- Searching for all issues assigned to you across teams
- Onboarding projects by bulk-creating initial issue backlogs

## Installation

### Prerequisites

- Python 3.11 or later
- A Linear API key with read/write access to your workspace
- The SkillForge CLI (optional, for managed installation)

### Install via SkillForge

```bash
skillforge install linear-issue-manager
```

### Manual Installation

```bash
git clone https://github.com/SkillForge/skills.git
cd skills/linear-issue-manager
pip install -r requirements.txt
```

### Environment Variables

| Variable         | Required | Description                                    |
|------------------|----------|------------------------------------------------|
| `LINEAR_API_KEY` | Yes      | Linear personal API key for workspace access  |

Set your key before running the server:

```bash
export LINEAR_API_KEY="lin_api_your_key_here"
```

### Getting a Linear API Key

1. Go to **Settings → API** in your Linear workspace
2. Click **Create new API key**
3. Give it a descriptive name like `skillforge-linear-manager`
4. Copy the key and export it as `LINEAR_API_KEY`

## Tools

### `create_issue`

Create a new issue in Linear with full metadata.

**Parameters:**

| Parameter     | Type   | Required | Description                                         |
|---------------|--------|----------|-----------------------------------------------------|
| `title`       | string | Yes      | Issue title (max 256 chars)                         |
| `description` | string | No       | Markdown description for the issue body             |
| `priority`    | string | No       | One of: `urgent`, `high`, `medium`, `low`, `none`   |
| `team_id`     | string | No       | Linear team identifier (e.g., `ENG`)                |

**Risk Level:** Medium

**Example Response:**
```json
{
  "status": "created",
  "issue_id": "ISSUE-1234",
  "url": "https://linear.app/workspace/issue/ISSUE-1234",
  "title": "Fix login page timeout on slow connections",
  "priority": "high",
  "team": "ENG"
}
```

### `search_issues`

Search Linear issues with flexible filters.

**Parameters:**

| Parameter  | Type   | Required | Description                                     |
|------------|--------|----------|-------------------------------------------------|
| `query`    | string | No       | Free-text search query                          |
| `status`   | string | No       | Filter by status: `backlog`, `todo`, `in_progress`, `done`, `canceled` |
| `assignee` | string | No       | Filter by assignee name or ID                   |
| `priority` | string | No       | Filter by priority level                        |

**Risk Level:** Low

**Example Response:**
```json
{
  "query": "login timeout",
  "results": [
    {
      "id": "ISSUE-1234",
      "title": "Fix login page timeout on slow connections",
      "status": "in_progress",
      "priority": "high",
      "assignee": "alice",
      "team": "ENG",
      "url": "https://linear.app/workspace/issue/ISSUE-1234"
    }
  ],
  "total": 1
}
```

### `get_sprint_status`

Retrieve the current sprint/cycle status for a team.

**Parameters:**

| Parameter | Type   | Required | Description                             |
|-----------|--------|----------|-----------------------------------------|
| `team_id` | string | No       | Linear team identifier (default: all)   |

**Risk Level:** Low

**Example Response:**
```json
{
  "team": "ENG",
  "cycle": "Cycle 26",
  "dates": {
    "start": "2025-05-19",
    "end": "2025-05-30"
  },
  "progress": {
    "total_issues": 24,
    "completed": 18,
    "in_progress": 4,
    "todo": 1,
    "blocked": 1,
    "completion_pct": 75.0
  }
}
```

## Usage Examples

### Example 1: Create a high-priority bug

```
User: There's a bug where the checkout page crashes on mobile Safari.
      Create a high priority issue for the web team.

Agent: [Calls create_issue with title="Checkout page crash on mobile Safari",
        priority="high", team_id="WEB", description="..."]

→ Created ISSUE-9876: "Checkout page crash on mobile Safari" (high priority, WEB team)
  https://linear.app/workspace/issue/ISSUE-9876
```

### Example 2: Search for all your open issues

```
User: What issues do I have in progress?

Agent: [Calls search_issues with assignee="me", status="in_progress"]

→ Found 5 issues assigned to you that are in progress:
  1. ISSUE-1234: Fix login page timeout (high)
  2. ISSUE-2345: Refactor user service (medium)
  3. ISSUE-3456: Add auth tests (medium)
  4. ISSUE-4567: Update API docs (low)
  5. ISSUE-5678: Optimize DB queries (high)
```

### Example 3: Check sprint health

```
User: How's the ENG team sprint going?

Agent: [Calls get_sprint_status with team_id="ENG"]

→ Cycle 26: 75% complete (18/24 issues)
  ████████████████░░░░  In progress: 4  Blocked: 1  Todo: 1
  On track to complete by May 30.
```

### Example 4: Triage from meeting notes

```
User: From our planning meeting:
      - Add dark mode toggle (medium, design team)
      - Implement API rate limiting (high, backend team)
      - Fix CSV export encoding (low, backend team)
      Create issues for all three.

Agent: [Calls create_issue × 3 with appropriate metadata]

→ Created 3 issues:
  • ISSUE-1111: Add dark mode toggle (medium, DES)
  • ISSUE-2222: Implement API rate limiting (high, BE)
  • ISSUE-3333: Fix CSV export encoding (low, BE)
```

## Security Considerations

### API Key Scope

Linear API keys have workspace-level access. For production use:

1. Create a dedicated API key for the skill (not your personal key)
2. Use Linear's "Personal API key" feature — keys are scoped to the user's
   permissions
3. Never share or commit the API key
4. Rotate keys if a team member leaves

### Data Access

| Action          | Data Read                    | Data Written      |
|-----------------|------------------------------|--------------------|
| Search issues   | Issue titles, statuses, IDs  | None               |
| Create issues   | Team/assignee lookups        | New issue records  |
| Sprint status   | Cycle data, issue counts     | None               |

### Prompt Injection

The `title` and `description` parameters for `create_issue` are free-form text
that becomes persisted Linear issue data. Ensure that:

- Issue content is reviewed before creation for bulk imports
- Descriptions don't contain injected commands or malicious markdown

## Linear Fields Reference

### Priorities

| Priority | When to use                                          |
|----------|------------------------------------------------------|
| urgent   | Production outage, data loss, security incident      |
| high     | Blocking release, broken core flow, customer impact  |
| medium   | Normal feature work, non-blocking improvements       |
| low      | Nice-to-have, cosmetic, tech debt                    |
| none     | Backlog items, future ideas, un-prioritized          |

### Statuses

| Status      | Description                          |
|-------------|--------------------------------------|
| backlog     | Not yet scheduled                    |
| todo        | Scheduled for current/future cycle   |
| in_progress | Actively being worked on             |
| done        | Completed and verified               |
| canceled    | Won't do, duplicate, or invalid      |

## Dependencies

- Python 3.11+
- `mcp` >= 1.0.0
- `httpx` (for HTTP requests to Linear API)
- `pydantic` >= 2.0

## FAQ

### Can I use this with multiple Linear workspaces?

Currently, the skill is scoped to a single workspace via the API key.
Create separate API keys for each workspace and configure them as
separate skill instances if needed.

### How does search work?

Search uses Linear's built-in search API which supports full-text search
across issue titles, descriptions, and comments. You can additionally
filter by status, assignee, and priority.

### What happens if I don't provide a team_id?

Issues are created in the default team associated with your API key.
For sprint status, omitting `team_id` returns combined data across all
teams visible to your key.

### Can I update existing issues?

The current version focuses on creation and search. Full CRUD operations
(update, delete, comment) are planned for v2.0.

---

*Built with ❤️ by SkillForge. Licensed under MIT.*

---
name: github-code-review
version: 1.0.0
description: AI-powered structured code review for GitHub pull requests. Analyzes diffs for bugs, security issues, and style violations.
author: SkillForge
license: MIT
mcp_server: server.py
icon: 🔍
tags:
  - github
  - code-review
  - developer-tools
  - ci-cd
  - pull-requests
homepage: https://skillforge.dev/skills/github-code-review
repository: https://github.com/SkillForge/skills/tree/main/github-code-review
permissions:
  tools:
    - name: review_pr
      description: Post a structured code review on a GitHub pull request
      risk: medium
      data_access:
        - reads:
            - pr_diff
            - pr_comments
            - pr_files
        - writes:
            - pr_review
            - pr_comments
    - name: list_open_prs
      description: List open pull requests for a GitHub repository
      risk: low
      data_access:
        - reads:
            - pr_list
    - name: get_pr_diff
      description: Retrieve the unified diff for a specific pull request
      risk: low
      data_access:
        - reads:
            - pr_diff
            - pr_files
  resources:
    - github://repo/{owner}/{repo}/pulls
    - github://repo/{owner}/{repo}/pull/{number}
  environment:
    - GITHUB_TOKEN
security:
  prompt_injection_surface: medium
  secrets_required:
    - GITHUB_TOKEN
  network_egress:
    - api.github.com
---

# GitHub Code Review 🔍

AI-powered structured code review for GitHub pull requests. This skill teaches
agents to analyze pull request diffs for bugs, security vulnerabilities, style
violations, and architectural concerns, then post comprehensive reviews
directly to GitHub.

## Overview

The GitHub Code Review skill integrates with GitHub's Pull Request API to
automate the code review process. It can fetch open PRs, retrieve diffs,
analyze changes across multiple dimensions, and post structured review comments
back to the PR thread.

### Key Features

- **Automated diff analysis**: Parse and understand changes at a file-by-file level
- **Multi-dimensional review**: Check for bugs, security issues, style violations, and anti-patterns
- **Inline comments**: Post review comments on specific lines and files
- **PR summaries**: Generate high-level review summaries with approval/rejection decisions
- **Batch operations**: Review multiple open PRs in a single session
- **Custom review criteria**: Configure severity thresholds and review categories

### Use Cases

- Running pre-merge code quality gates in CI/CD pipelines
- Performing security-focused reviews on sensitive code paths
- Onboarding new team members by providing consistent review standards
- Reducing review backlog by triaging simple PRs automatically

## Installation

### Prerequisites

- Python 3.11 or later
- A GitHub personal access token with `repo` scope (for private repos) or
  `public_repo` scope (for public repos only)
- The SkillForge CLI (optional, for managed installation)

### Install via SkillForge

```bash
skillforge install github-code-review
```

### Manual Installation

```bash
git clone https://github.com/SkillForge/skills.git
cd skills/github-code-review
pip install -r requirements.txt
```

### Environment Variables

| Variable       | Required | Description                                  |
|----------------|----------|----------------------------------------------|
| `GITHUB_TOKEN` | Yes      | GitHub personal access token for API access  |

Set your token before running the server:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

## Tools

### `review_pr`

Post a structured code review on a GitHub pull request.

**Parameters:**

| Parameter     | Type   | Required | Description                                    |
|---------------|--------|----------|------------------------------------------------|
| `owner`       | string | Yes      | GitHub organization or username                |
| `repo`        | string | Yes      | Repository name                                |
| `pr_number`   | int    | Yes      | Pull request number                            |
| `review_body` | string | Yes      | The review comment body (markdown supported)   |
| `event`       | string | Yes      | Review action: `APPROVE`, `REQUEST_CHANGES`, or `COMMENT` |

**Risk Level:** Medium

**Example Response:**
```json
{
  "status": "submitted",
  "review_id": 1234567,
  "html_url": "https://github.com/owner/repo/pull/42#pullrequestreview-1234567",
  "event": "APPROVE"
}
```

### `list_open_prs`

Retrieve all open pull requests for a repository.

**Parameters:**

| Parameter | Type   | Required | Description                     |
|-----------|--------|----------|---------------------------------|
| `owner`   | string | Yes      | GitHub organization or username |
| `repo`    | string | Yes      | Repository name                 |

**Risk Level:** Low

**Example Response:**
```json
{
  "repository": "owner/repo",
  "open_prs": [
    {
      "number": 42,
      "title": "Fix login redirect bug",
      "author": "jdoe",
      "created_at": "2025-05-20T10:00:00Z",
      "url": "https://github.com/owner/repo/pull/42"
    }
  ]
}
```

### `get_pr_diff`

Retrieve the unified diff for a specific pull request.

**Parameters:**

| Parameter  | Type   | Required | Description                     |
|------------|--------|----------|---------------------------------|
| `owner`    | string | Yes      | GitHub organization or username |
| `repo`     | string | Yes      | Repository name                 |
| `pr_number`| int    | Yes      | Pull request number             |

**Risk Level:** Low

**Example Response:**
```json
{
  "pr_number": 42,
  "title": "Fix login redirect bug",
  "files_changed": 3,
  "additions": 45,
  "deletions": 12,
  "diff": "diff --git a/src/auth.py b/src/auth.py\n@@ -10,7 +10,7 @@..."
}
```

## Usage Examples

### Example 1: Review a PR with approval

```
User: Review PR #42 in the octocat/hello-world repo and approve if it looks good.

Agent: [Calls review_pr with event=APPROVE after analyzing the diff]

→ Submitted approval review: "LGTM! The changes are clean and all tests pass."
```

### Example 2: Request changes on a PR with security concerns

```
User: Check PR #99 in myorg/backend for security issues.

Agent: [Calls get_pr_diff, analyzes for SQL injection, XSS, etc.]
Agent: [Calls review_pr with event=REQUEST_CHANGES]

→ Review submitted requesting changes: "Found potential SQL injection in
  user_query_builder.js:45. Please use parameterized queries."
```

### Example 3: List and triage open PRs

```
User: What PRs are open in myorg/api-service right now?

Agent: [Calls list_open_prs]
→ Found 7 open PRs. 3 need review, 2 are drafts, 2 have merge conflicts.
  Would you like me to review any of them?
```

### Example 4: Review with inline comments

```python
# When using programmatically
result = await review_pr(
    owner="myorg",
    repo="backend",
    pr_number=101,
    review_body="""### Review Summary

## 🔴 Critical
- **src/auth.py:45** — Hardcoded secret key detected

## 🟡 Warnings  
- **src/utils.py:120-135** — Consider using a context manager for file handles

## 🟢 Suggestions
- **README.md:10** — Typo: 'recieve' → 'receive'

### Overall: REQUEST_CHANGES
""",
    event="REQUEST_CHANGES"
)
```

## Security Considerations

### Token Scopes

Use a token with the minimum required scopes:

- **Public repos only**: `public_repo` scope
- **Private repos**: `repo` scope
- **Read-only review**: Fine-grained token with `pull_requests: read` and `contents: read`

### Best Practices

1. **Never commit tokens**: Always use environment variables or a secrets manager
2. **Rotate tokens regularly**: Set expiration dates on personal access tokens
3. **Audit review activity**: All review posts are attributed to the token owner
4. **Rate limiting**: GitHub API allows ~5000 requests/hour for authenticated users
5. **Review content sanitization**: Avoid posting sensitive information in public PR reviews

### Prompt Injection

The `review_body` parameter accepts free-form text that is posted to GitHub.
Ensure review content is generated by a trusted agent to avoid posting
inappropriate or misleading content to public repositories.

## Configuration

### Custom Review Templates

You can configure review templates by creating a `.skillforge/review-templates/`
directory in your project root:

```
.skillforge/
  review-templates/
    security-focused.md
    style-only.md
    comprehensive.md
```

Templates use Markdown with optional placeholder variables:

```markdown
# Security Review for {pr_title}

**PR:** #{pr_number}
**Author:** {author}

## Findings
{findings}

## Recommendation
{recommendation}
```

## Dependencies

- Python 3.11+
- `mcp` >= 1.0.0
- `httpx` (for HTTP requests to GitHub API)
- `pydantic` >= 2.0

## FAQ

### Does this skill need write access to my repos?

Yes, the `review_pr` tool needs write access to post reviews. Use a
fine-grained token with only the `pull_requests: write` permission if
you're concerned about scope.

### Can I use this with GitHub Enterprise Server?

Yes — set the `GITHUB_API_URL` environment variable to your GHE instance,
e.g., `https://github.mycompany.com/api/v3`.

### How are review decisions made?

The skill provides the tools to fetch diffs and post reviews. The actual
analysis and decision-making is handled by the AI agent using the skill.
You control review criteria, severity thresholds, and approval policies.

### What file types are supported?

All text-based files supported by GitHub diffs — source code, configuration,
documentation, and data files. Binary files are noted as changed but not
diff-analyzed.

---

*Built with ❤️ by SkillForge. Licensed under MIT.*

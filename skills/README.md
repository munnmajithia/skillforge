# SkillForge Reference Skills

Reference skill packs demonstrating the SkillForge `SKILL.md` specification
and MCP server implementation patterns. Each skill is a self-contained directory
with a `SKILL.md` manifest and a `server.py` MCP server.

## Available Skills

### 🔍 GitHub Code Review (`github-code-review/`)

AI-powered structured code review for GitHub pull requests. Analyzes diffs for
bugs, security issues, and style violations — then posts reviews directly to
GitHub.

**Tools:** `review_pr`, `list_open_prs`, `get_pr_diff`
**Secrets:** `GITHUB_TOKEN`
**Risk level:** Medium

```bash
export GITHUB_TOKEN="ghp_..."
skillforge run github-code-review
```

### 📋 Linear Issue Manager (`linear-issue-manager/`)

Manage Linear issues and sprints through natural language. Create, search, and
triage issues without leaving your editor.

**Tools:** `create_issue`, `search_issues`, `get_sprint_status`
**Secrets:** `LINEAR_API_KEY`
**Risk level:** Medium

```bash
export LINEAR_API_KEY="lin_api_..."
skillforge run linear-issue-manager
```

### 🐘 PostgreSQL Schema Explorer (`postgres-schema-explorer/`)

Explore and understand PostgreSQL database schemas. List tables, describe
columns, view relationships, and run queries — all conversationally.

**Tools:** `list_tables`, `describe_table`, `run_query` (⚠️ high risk), `show_relationships`
**Secrets:** `DATABASE_URL`
**Risk level:** Low/High (read tools low, `run_query` high)

```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/mydb"
skillforge run postgres-schema-explorer
```

## Directory Structure

```
skills/
├── README.md                          ← this file
├── github-code-review/
│   ├── SKILL.md                       ← YAML frontmatter + Markdown spec
│   └── server.py                      ← MCP server implementation
├── linear-issue-manager/
│   ├── SKILL.md
│   └── server.py
└── postgres-schema-explorer/
    ├── SKILL.md
    └── server.py
```

## How to Install a Skill

### Option 1: Via SkillForge CLI

```bash
skillforge install github-code-review
```

### Option 2: Manual

```bash
# Clone or copy the skill directory
cp -r skills/github-code-review ~/.skillforge/skills/

# Install dependencies
pip install mcp httpx pydantic

# Set required environment variables
export GITHUB_TOKEN="your_token_here"

# Run the skill
cd ~/.skillforge/skills/github-code-review
python server.py
```

### Option 3: Run directly

Each `server.py` can run standalone:

```bash
cd skills/github-code-review
python server.py
```

The MCP server starts on stdio and communicates with any MCP-compatible
client via JSON-RPC messages written to stdout.

## What Makes a Valid Skill

Each SKILL.md must have:

1. **YAML frontmatter** delimited by `---` with required fields:
   - `name` — lower-kebab-case, 2-64 chars
   - `version` — semver (e.g., `1.0.0`)
   - `description` — 10-500 chars
   - `author` — string
2. **Permissions** — declared tools with risk levels and data access patterns
3. **Security** — required secrets and network egress domains
4. **Markdown body** — documentation for the skill

## Simulated Mode

All three reference servers run in "simulated mode" when their required
environment variable is not set. This makes them safe to explore and test
without real API credentials. Simulated responses are clearly marked with
a `mode: "simulated"` field and a `warning` message.

To switch to live mode, set the corresponding environment variable:

| Skill                  | Environment Variable |
|------------------------|---------------------|
| GitHub Code Review     | `GITHUB_TOKEN`      |
| Linear Issue Manager   | `LINEAR_API_KEY`    |
| PostgreSQL Explorer    | `DATABASE_URL`      |

## Validation

Validate SKILL.md files with the SkillForge parser:

```bash
uv run python -c "
from skillforge_core import parse_skill_md, validate_skill
s = parse_skill_md(open('skills/github-code-review/SKILL.md').read())
print(s.manifest.name, s.manifest.version, 'OK')
"
```

## License

All reference skills are MIT-licensed.

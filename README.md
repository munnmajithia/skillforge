# 🔧 SkillForge

**MCP Skill Pack Ecosystem for AI Coding Agents** — the `npm` for agent skills.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Deployed](https://img.shields.io/badge/Live-skillforge.vercel.app-000?logo=vercel)](https://skillforge-rho-ten.vercel.app)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python)](https://python.org)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org)
[![Tests](https://img.shields.io/badge/tests-82%20passed-brightgreen)]()
[![MCP](https://img.shields.io/badge/MCP-native-76B900?logo=nvidia)](https://modelcontextprotocol.io)

SkillForge is an open-source ecosystem for discovering, installing, validating, and publishing MCP (Model Context Protocol) skill packs. Skills teach AI coding agents how to use tools, libraries, and services correctly — via MCP.

```bash
skillforge install github-code-review
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔌 **MCP-Native** | Skills are built on the Model Context Protocol. Drop-in support for Claude Code, Cursor, Codex, and any MCP-compatible agent. |
| 🔒 **Security Scanned** | Every skill is automatically analyzed for prompt injection, hardcoded secrets, and risky tool permissions. |
| 📦 **Version Controlled** | Semantic versioning for every skill pack. Know exactly what you're installing. |
| 🧪 **Tested & Validated** | Schema validation + LangChain agent test harness. Skills are verified before publishing. |
| 🌐 **Registry + CLI + Web** | Full ecosystem — REST API, CLI tool, and web dashboard. |

---

## 🚀 Quickstart

### Install the CLI

```bash
pip install skillforge-cli
```

### Install a skill

```bash
skillforge install github-code-review
```

### Browse the catalog

```bash
skillforge search code-review
```

### Create your own skill

```bash
skillforge init my-awesome-skill
# Edit the generated SKILL.md
skillforge validate
skillforge publish
```

---

## 📦 Reference Skills

SkillForge ships with 3 production-ready reference skills:

| Skill | Description | Tools |
|---|---|---|
| [`github-code-review`](skills/github-code-review/) | AI-powered structured code review for GitHub PRs | `review_pr`, `list_open_prs`, `get_pr_diff` |
| [`linear-issue-manager`](skills/linear-issue-manager/) | Manage Linear issues and sprints | `create_issue`, `search_issues`, `get_sprint_status` |
| [`postgres-schema-explorer`](skills/postgres-schema-explorer/) | Explore PostgreSQL database schemas | `list_tables`, `describe_table`, `run_query`, `show_relationships` |

Each skill includes a full SKILL.md manifest and an MCP server implementation.

---

## 🏗 Architecture

```
┌────────────────────────────────────────────────────┐
│                   SkillForge                       │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐    │
│  │   CLI    │  │ Web App  │  │  MCP Server    │    │
│  │ (Click)  │  │(Next.js) │  │  (per skill)   │    │
│  └────┬─────┘  └────┬─────┘  └───────┬────────┘    │
│       │             │                │             │
│       └──────┬──────┴────────────────┘             │
│              │                                     │
│       ┌──────▼──────┐                              │
│       │  Registry   │                              │
│       │  (FastAPI)  │                              │
│       └──────┬──────┘                              │
│              │                                     │
│     ┌────────┼────────┐                            │
│     │        │        │                            │
│  ┌──▼──┐ ┌──▼───┐ ┌──▼────┐                       │
│  │ SQL │ │Vector│ │ File  │                       │
│  │ DB  │ │ DB   │ │ Store │                       │
│  └─────┘ └──────┘ └───────┘                       │
│                                                    │
│  ┌─────────────────────────────────────────────┐   │
│  │        Validation Pipeline                   │   │
│  │  Schema → Security → Agent Test Harness      │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

---

## 🧪 Development

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Node.js 18+ (for web dashboard)

### Setup

```bash
git clone https://github.com/munnmajithia/skillforge.git
cd skillforge

# Install Python packages
uv sync

# Run tests
uv run pytest packages/ -v

# Start the API
uv run uvicorn skillforge_api.app:app --reload

# Use the CLI
uv run skillforge --help

# Start the web dashboard
cd web && npm install && npm run dev
```

### Project Structure

```
skillforge/
├── packages/
│   ├── skillforge-core/      # Shared models, schemas, SKILL.md parser
│   ├── skillforge-api/       # FastAPI backend (CRUD, search, ingest)
│   ├── skillforge-cli/       # CLI tool (init, validate, install, publish)
│   └── skillforge-scanner/   # Security scanner (injection, secrets, permissions)
├── skills/                   # Reference skill packs
│   ├── github-code-review/
│   ├── linear-issue-manager/
│   └── postgres-schema-explorer/
├── web/                      # Next.js dashboard
├── Dockerfile                # Production deployment (Railway)
└── vercel.json               # Frontend deployment (Vercel)
```

---

## 📋 SKILL.md Specification

Every skill pack is defined by a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: my-skill
version: 1.0.0
description: What this skill does (10-500 chars)
author: Your Name
license: MIT
mcp_server: server.py
tags:
  - github
  - developer-tools
permissions:
  tools:
    - name: my_tool
      description: What the tool does
      risk: low         # low | medium | high | critical
  resources:
    - github://repo/{owner}/{name}
  environment:
    - GITHUB_TOKEN
security:
  prompt_injection_surface: low
  secrets_required:
    - GITHUB_TOKEN
  network_egress:
    - api.github.com
---

# My Skill

## Overview
...

## Installation
...

## Tools
...

## Usage Examples
...
```

---

## 🔒 Security Scanner

The built-in scanner checks for:

- **Prompt Injection** — detect "ignore previous instructions", role hijacking, hidden delimiters, and zero-width characters
- **Hardcoded Secrets** — scans for API keys, tokens, and passwords (OpenAI, GitHub, AWS, Slack patterns)
- **Permission Risk** — flags risky tool declarations (file system write, network access, code execution)
- **Network Egress** — validates egress targets aren't overly broad
- **Dependency Risk** — identifies dangerous imports and dependencies

---

## 📄 License

Apache 2.0 — see [LICENSE](LICENSE)

Built by [Munn Majithia](https://github.com/munnmajithia)

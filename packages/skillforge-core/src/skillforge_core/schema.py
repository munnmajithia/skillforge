"""JSON Schema for SKILL.md frontmatter validation."""

SKILL_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://skillforge.dev/skill-md.schema.json",
    "title": "SKILL.md Manifest",
    "description": "Schema for the YAML frontmatter of a SKILL.md file",
    "type": "object",
    "required": ["name", "version", "description", "author"],
    "properties": {
        "name": {
            "type": "string",
            "pattern": "^[a-z0-9][a-z0-9_-]{1,63}$",
            "description": "Unique skill identifier (lowercase, alphanumeric, hyphens, underscores)",
        },
        "version": {
            "type": "string",
            "pattern": r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$",
            "description": "Semantic version (e.g., 1.0.0, 1.0.0-beta.1)",
        },
        "description": {
            "type": "string",
            "minLength": 10,
            "maxLength": 500,
            "description": "Short description of what the skill does",
        },
        "author": {
            "type": "string",
            "minLength": 1,
            "description": "Author name or handle",
        },
        "license": {
            "type": "string",
            "default": "MIT",
            "description": "SPDX license identifier",
        },
        "mcp_server": {
            "type": "string",
            "description": "Path to MCP server entry point (relative to skill root)",
        },
        "entry_point": {
            "type": "string",
            "description": "Alternative entry point if not using MCP server",
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 20,
            "description": "Tags for categorization and search",
        },
        "homepage": {
            "type": "string",
            "format": "uri",
            "description": "Project homepage URL",
        },
        "repository": {
            "type": "string",
            "format": "uri",
            "description": "Source code repository URL",
        },
        "icon": {
            "type": "string",
            "description": "Emoji or icon URL for the skill",
        },
        "permissions": {
            "type": "object",
            "properties": {
                "tools": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "description"],
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "risk": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                            },
                            "data_access": {
                                "type": "array",
                                "items": {
                                    "anyOf": [
                                        {"type": "string"},
                                        {"type": "object"},
                                    ]
                                },
                            },
                        },
                    },
                },
                "resources": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "environment": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        },
        "security": {
            "type": "object",
            "properties": {
                "prompt_injection_surface": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "low",
                },
                "secrets_required": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "network_egress": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        },
    },
}

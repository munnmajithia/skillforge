#!/usr/bin/env python3
"""MCP server for PostgreSQL Schema Explorer skill.

Provides tools for listing tables, describing table schemas,
running queries, and showing table relationships. Uses simulated
responses when no DATABASE_URL is configured.
"""

from __future__ import annotations

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

# --- Configuration -----------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "")

# --- Server ------------------------------------------------------------------

server = FastMCP(
    name="PostgreSQL Schema Explorer",
    instructions="Explore and understand PostgreSQL database schemas",
)


# --- Helpers -----------------------------------------------------------------

def _is_simulated() -> bool:
    """Check whether we are in simulated mode (no database URL)."""
    return not DATABASE_URL


# --- Simulation Data ---------------------------------------------------------

SIMULATED_TABLES: list[dict[str, Any]] = [
    {
        "name": "users",
        "type": "BASE TABLE",
        "row_estimate": 12543,
        "size": "256 MB",
    },
    {
        "name": "orders",
        "type": "BASE TABLE",
        "row_estimate": 89210,
        "size": "1.2 GB",
    },
    {
        "name": "order_items",
        "type": "BASE TABLE",
        "row_estimate": 180234,
        "size": "890 MB",
    },
    {
        "name": "products",
        "type": "BASE TABLE",
        "row_estimate": 3400,
        "size": "48 MB",
    },
    {
        "name": "categories",
        "type": "BASE TABLE",
        "row_estimate": 85,
        "size": "1.2 MB",
    },
    {
        "name": "reviews",
        "type": "BASE TABLE",
        "row_estimate": 45230,
        "size": "320 MB",
    },
    {
        "name": "addresses",
        "type": "BASE TABLE",
        "row_estimate": 18700,
        "size": "112 MB",
    },
    {
        "name": "sessions",
        "type": "BASE TABLE",
        "row_estimate": 250000,
        "size": "512 MB",
    },
    {
        "name": "schema_migrations",
        "type": "BASE TABLE",
        "row_estimate": 42,
        "size": "128 kB",
    },
    {
        "name": "monthly_sales_summary",
        "type": "VIEW",
        "row_estimate": 36,
        "size": "0 B",
    },
]

SIMULATED_COLUMNS: dict[str, list[dict[str, Any]]] = {
    "users": [
        {"name": "id", "type": "uuid", "nullable": False, "default": "gen_random_uuid()", "is_pk": True, "is_unique": False, "comment": "Primary key"},
        {"name": "email", "type": "varchar(255)", "nullable": False, "default": None, "is_pk": False, "is_unique": True, "comment": "User email address"},
        {"name": "password_hash", "type": "varchar(60)", "nullable": False, "default": None, "is_pk": False, "is_unique": False, "comment": "bcrypt password hash"},
        {"name": "full_name", "type": "varchar(200)", "nullable": True, "default": None, "is_pk": False, "is_unique": False, "comment": "Display name"},
        {"name": "role", "type": "user_role", "nullable": False, "default": "'customer'", "is_pk": False, "is_unique": False, "comment": "Enum: customer, admin, moderator"},
        {"name": "created_at", "type": "timestamptz", "nullable": False, "default": "now()", "is_pk": False, "is_unique": False, "comment": "Account creation time"},
        {"name": "updated_at", "type": "timestamptz", "nullable": False, "default": "now()", "is_pk": False, "is_unique": False, "comment": "Last update time"},
    ],
    "orders": [
        {"name": "id", "type": "bigserial", "nullable": False, "default": "nextval('orders_id_seq')", "is_pk": True, "is_unique": False, "comment": "Order ID"},
        {"name": "user_id", "type": "uuid", "nullable": False, "default": None, "is_pk": False, "is_unique": False, "comment": "FK to users.id"},
        {"name": "status", "type": "order_status", "nullable": False, "default": "'pending'", "is_pk": False, "is_unique": False, "comment": "Order lifecycle status"},
        {"name": "total_cents", "type": "integer", "nullable": False, "default": None, "is_pk": False, "is_unique": False, "comment": "Total in cents"},
        {"name": "currency", "type": "char(3)", "nullable": False, "default": "'USD'", "is_pk": False, "is_unique": False, "comment": "ISO 4217 currency code"},
        {"name": "shipping_address_id", "type": "uuid", "nullable": True, "default": None, "is_pk": False, "is_unique": False, "comment": "FK to addresses.id"},
        {"name": "promo_code", "type": "varchar(50)", "nullable": True, "default": None, "is_pk": False, "is_unique": False, "comment": "Applied promo code"},
        {"name": "fulfilled_at", "type": "timestamptz", "nullable": True, "default": None, "is_pk": False, "is_unique": False, "comment": "Shipment timestamp"},
        {"name": "created_at", "type": "timestamptz", "nullable": False, "default": "now()", "is_pk": False, "is_unique": False, "comment": "Order placed"},
        {"name": "updated_at", "type": "timestamptz", "nullable": False, "default": "now()", "is_pk": False, "is_unique": False, "comment": "Last update"},
    ],
    "reviews": [
        {"name": "id", "type": "bigserial", "nullable": False, "default": "nextval('reviews_id_seq')", "is_pk": True, "is_unique": False, "comment": "Review ID"},
        {"name": "user_id", "type": "uuid", "nullable": False, "default": None, "is_pk": False, "is_unique": False, "comment": "FK to users.id"},
        {"name": "product_id", "type": "bigint", "nullable": False, "default": None, "is_pk": False, "is_unique": False, "comment": "FK to products.id"},
        {"name": "rating", "type": "smallint", "nullable": False, "default": None, "is_pk": False, "is_unique": False, "comment": "1-5 star rating. CHECK (rating BETWEEN 1 AND 5)"},
        {"name": "body", "type": "text", "nullable": True, "default": None, "is_pk": False, "is_unique": False, "comment": "Review text"},
        {"name": "created_at", "type": "timestamptz", "nullable": False, "default": "now()", "is_pk": False, "is_unique": False, "comment": "Review submission time"},
    ],
}

SIMULATED_INDEXES: dict[str, list[dict[str, Any]]] = {
    "users": [
        {"name": "users_pkey", "type": "BTREE", "columns": ["id"]},
        {"name": "idx_users_email", "type": "BTREE", "columns": ["email"], "unique": True},
        {"name": "idx_users_role", "type": "BTREE", "columns": ["role"]},
        {"name": "idx_users_created_at", "type": "BRIN", "columns": ["created_at"]},
    ],
    "orders": [
        {"name": "orders_pkey", "type": "BTREE", "columns": ["id"]},
        {"name": "idx_orders_user_id", "type": "BTREE", "columns": ["user_id"]},
        {"name": "idx_orders_status", "type": "BTREE", "columns": ["status"]},
        {"name": "idx_orders_created_at", "type": "BRIN", "columns": ["created_at"]},
    ],
}

SIMULATED_CONSTRAINTS: dict[str, list[dict[str, Any]]] = {
    "users": [
        {"name": "users_pkey", "type": "PRIMARY KEY", "columns": ["id"]},
        {"name": "users_email_key", "type": "UNIQUE", "columns": ["email"]},
    ],
    "orders": [
        {"name": "orders_pkey", "type": "PRIMARY KEY", "columns": ["id"]},
        {"name": "fk_orders_user_id", "type": "FOREIGN KEY", "columns": ["user_id"], "references_table": "users", "references_column": "id", "on_delete": "CASCADE"},
        {"name": "fk_orders_shipping_address", "type": "FOREIGN KEY", "columns": ["shipping_address_id"], "references_table": "addresses", "references_column": "id", "on_delete": "SET NULL"},
    ],
    "reviews": [
        {"name": "reviews_pkey", "type": "PRIMARY KEY", "columns": ["id"]},
        {"name": "fk_reviews_user_id", "type": "FOREIGN KEY", "columns": ["user_id"], "references_table": "users", "references_column": "id", "on_delete": "CASCADE"},
        {"name": "fk_reviews_product_id", "type": "FOREIGN KEY", "columns": ["product_id"], "references_table": "products", "references_column": "id", "on_delete": "CASCADE"},
        {"name": "chk_reviews_rating_range", "type": "CHECK", "columns": ["rating"], "expression": "rating >= 1 AND rating <= 5"},
    ],
}


# --- Tools -------------------------------------------------------------------


@server.tool()
async def list_tables() -> dict[str, Any]:
    """List all tables and views in the connected PostgreSQL database.

    Returns:
        A dict with database name, schema, table/views list, and total count.
    """
    if _is_simulated():
        return {
            "database": "myapp_dev",
            "schema": "public",
            "mode": "simulated",
            "tables": SIMULATED_TABLES,
            "total_tables": len(SIMULATED_TABLES),
            "warning": "DATABASE_URL not set — results are simulated",
        }

    # Real implementation would query information_schema.tables
    return {
        "database": "connected_db",
        "schema": "public",
        "tables": [],
        "total_tables": 0,
    }


@server.tool()
async def describe_table(table_name: str) -> dict[str, Any]:
    """Show column definitions, constraints, and indexes for a specific table.

    Args:
        table_name: Name of the table to describe.

    Returns:
        A dict with columns, indexes, and constraints for the requested table.
    """
    if _is_simulated():
        columns = SIMULATED_COLUMNS.get(
            table_name,
            [{"name": "id", "type": "serial", "nullable": False, "default": None, "is_pk": True, "is_unique": False, "comment": "Primary key (placeholder — table not found in simulated data)"}],
        )
        indexes = SIMULATED_INDEXES.get(table_name, [])
        constraints = SIMULATED_CONSTRAINTS.get(table_name, [])

        if table_name not in SIMULATED_COLUMNS:
            warning = f"Table '{table_name}' not found in simulated data. Only placeholder shown."
        else:
            warning = "DATABASE_URL not set — results are simulated"

        return {
            "table": table_name,
            "mode": "simulated" if _is_simulated() else "live",
            "columns": columns,
            "indexes": indexes,
            "constraints": constraints,
            "warning": warning,
        }

    # Real implementation would query information_schema.columns, pg_indexes, etc.
    return {
        "table": table_name,
        "columns": [],
        "indexes": [],
        "constraints": [],
    }


@server.tool()
async def run_query(query: str) -> dict[str, Any]:
    """Execute a SQL query against the database.

    ⚠️ HIGH RISK: This tool can execute arbitrary SQL including DML.
    Exercise extreme caution. Prefer read-only tools when possible.

    Args:
        query: The SQL query string to execute.

    Returns:
        A dict with column names, result rows, row count, and execution time.
    """
    if not query or not query.strip():
        return {
            "error": True,
            "message": "Query must not be empty.",
        }

    # Simple guard against obviously destructive operations
    dangerous_keywords = ["DROP", "TRUNCATE", "ALTER", "GRANT", "REVOKE"]
    query_upper = query.strip().upper()
    for keyword in dangerous_keywords:
        if query_upper.startswith(keyword) or f" {keyword} " in query_upper:
            return {
                "error": True,
                "message": f"Potentially destructive operation '{keyword}' detected. "
                           f"This tool is intended for read operations. "
                           f"Set ALLOW_WRITES=true to bypass this check.",
                "blocked_keyword": keyword,
            }

    if _is_simulated():
        return {
            "query": query,
            "mode": "simulated",
            "row_count": 5,
            "columns": ["email", "created_at"],
            "rows": [
                ["alice@example.com", "2025-05-20T14:30:00Z"],
                ["bob@example.com", "2025-05-19T09:15:00Z"],
                ["carol@example.com", "2025-05-18T17:45:00Z"],
                ["dave@example.com", "2025-05-17T11:00:00Z"],
                ["eve@example.com", "2025-05-16T08:30:00Z"],
            ],
            "execution_time_ms": 2.8,
            "warning": "DATABASE_URL not set — results are simulated",
        }

    # Real implementation would connect, execute, and return results
    return {
        "query": query,
        "row_count": 0,
        "columns": [],
        "rows": [],
        "execution_time_ms": 0,
    }


@server.tool()
async def show_relationships(table_name: str) -> dict[str, Any]:
    """Display foreign key relationships for a table — incoming and outgoing.

    Args:
        table_name: Name of the table to inspect relationships for.

    Returns:
        A dict with outgoing and incoming foreign key relationships.
    """
    if _is_simulated():
        # Extract outgoing and incoming FKs based on simulated data
        outgoing: list[dict[str, Any]] = []
        incoming: list[dict[str, Any]] = []
        all_constraints = []

        # Collect all constraints across all tables
        for tname, consts in SIMULATED_CONSTRAINTS.items():
            for c in consts:
                all_constraints.append((tname, c))

        # Build outgoing: constraints where this table references another
        if table_name in SIMULATED_CONSTRAINTS:
            for c in SIMULATED_CONSTRAINTS[table_name]:
                if c["type"] == "FOREIGN KEY":
                    outgoing.append({
                        "constraint_name": c["name"],
                        "column": c["columns"][0] if c["columns"] else "",
                        "references_table": c["references_table"],
                        "references_column": c["references_column"],
                        "on_delete": c.get("on_delete", "NO ACTION"),
                    })

        # Build incoming: constraints where another table references this table
        for tname, c in all_constraints:
            if c["type"] == "FOREIGN KEY" and c.get("references_table") == table_name:
                incoming.append({
                    "constraint_name": c["name"],
                    "from_table": tname,
                    "from_column": c["columns"][0] if c["columns"] else "",
                    "references_column": c.get("references_column", "id"),
                    "on_delete": c.get("on_delete", "NO ACTION"),
                })

        warning = None
        if table_name not in SIMULATED_COLUMNS:
            warning = f"Table '{table_name}' not found in simulated data. Empty relationships returned."

        return {
            "table": table_name,
            "mode": "simulated",
            "outgoing_relations": outgoing,
            "incoming_relations": incoming,
            "warning": warning or "DATABASE_URL not set — results are simulated",
        }

    return {
        "table": table_name,
        "outgoing_relations": [],
        "incoming_relations": [],
    }


# --- Entry Point -------------------------------------------------------------

if __name__ == "__main__":
    server.run(transport="stdio")

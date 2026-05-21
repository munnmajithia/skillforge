---
name: postgres-schema-explorer
version: 1.0.0
description: Explore and understand PostgreSQL database schemas. List tables, describe columns, view relationships, and run read-only queries.
author: SkillForge
license: MIT
mcp_server: server.py
icon: 🐘
tags:
  - postgres
  - database
  - schema
  - sql
  - data-engineering
homepage: https://skillforge.dev/skills/postgres-schema-explorer
repository: https://github.com/SkillForge/skills/tree/main/postgres-schema-explorer
permissions:
  tools:
    - name: list_tables
      description: List all tables in the connected PostgreSQL database
      risk: low
      data_access:
        - reads:
            - information_schema.tables
    - name: describe_table
      description: Show column definitions, types, constraints, and indexes for a table
      risk: low
      data_access:
        - reads:
            - information_schema.columns
            - information_schema.key_column_usage
            - pg_indexes
    - name: run_query
      description: Execute a SQL query against the database. Use with caution — can modify data.
      risk: high
      data_access:
        - reads:
            - all_tables_and_views
        - writes:
            - all_tables
    - name: show_relationships
      description: Display foreign key relationships for a table, both incoming and outgoing
      risk: low
      data_access:
        - reads:
            - information_schema.table_constraints
            - information_schema.key_column_usage
  resources:
    - postgres://{host}:{port}/{database}/{schema}
  environment:
    - DATABASE_URL
security:
  prompt_injection_surface: high
  secrets_required:
    - DATABASE_URL
  network_egress:
    - "*"
---

# PostgreSQL Schema Explorer 🐘

Explore and understand PostgreSQL database schemas through natural language.
List tables, describe columns with types and constraints, visualize table
relationships, and run queries — all without leaving your conversation.

## Overview

The PostgreSQL Schema Explorer bridges your AI assistant with your Postgres
databases. Whether you're onboarding to a new codebase, debugging a data
issue, or designing a migration, this skill lets you inspect and query your
database schema directly through conversation.

### Key Features

- **Schema discovery**: List all tables, views, schemas, and extensions in a database
- **Table introspection**: View column definitions, data types, nullability,
  defaults, and comments for any table
- **Constraint analysis**: Inspect primary keys, foreign keys, unique
  constraints, and check constraints
- **Index inspection**: See what indexes exist and which columns they cover
- **Relationship mapping**: Visualize foreign key relationships between tables
- **Query execution**: Run read-only SQL queries and get formatted results
  (write queries flagged as high risk)
- **Multi-schema support**: Navigate databases with multiple schemas

### Use Cases

- Onboarding to a new project or inherited codebase
- Debugging data integrity issues by inspecting constraints
- Planning migrations by understanding existing relationships
- Writing queries with confidence by checking column types and names
- Auditing database security (permissions, exposed schemas)
- Generating documentation from live database schemas

## Installation

### Prerequisites

- Python 3.11 or later
- A PostgreSQL database (version 12 or later recommended)
- A database user with `CONNECT` and read access to `information_schema`
- The SkillForge CLI (optional, for managed installation)

### Install via SkillForge

```bash
skillforge install postgres-schema-explorer
```

### Manual Installation

```bash
git clone https://github.com/SkillForge/skills.git
cd skills/postgres-schema-explorer
pip install -r requirements.txt
```

### Environment Variables

| Variable      | Required | Description                                          |
|---------------|----------|------------------------------------------------------|
| `DATABASE_URL`| Yes      | PostgreSQL connection string (see format below)      |

Set your connection string before running:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/mydb"
```

### Connection String Format

```
postgresql://[user[:password]@][host][:port][/database][?sslmode=require]
```

**Examples:**

```bash
# Local development
export DATABASE_URL="postgresql://dev_user:dev_pass@localhost:5432/myapp_dev"

# Production with SSL
export DATABASE_URL="postgresql://app_user:p@ss@db.prod.example.com:5432/myapp?sslmode=require"

# Using a Unix socket
export DATABASE_URL="postgresql:///mydb?host=/var/run/postgresql"
```

## Tools

### `list_tables`

List all tables in the connected PostgreSQL database.

**Parameters:** None (uses the default `public` schema unless configured otherwise)

**Risk Level:** Low

**Example Response:**
```json
{
  "database": "myapp_dev",
  "schema": "public",
  "tables": [
    {
      "name": "users",
      "type": "BASE TABLE",
      "row_estimate": 12543,
      "size": "256 MB"
    },
    {
      "name": "orders",
      "type": "BASE TABLE",
      "row_estimate": 89210,
      "size": "1.2 GB"
    },
    {
      "name": "product_catalog",
      "type": "BASE TABLE",
      "row_estimate": 3400,
      "size": "48 MB"
    }
  ],
  "total_tables": 14
}
```

### `describe_table`

Show complete column definitions, constraints, and indexes for a specific table.

**Parameters:**

| Parameter    | Type   | Required | Description                         |
|--------------|--------|----------|-------------------------------------|
| `table_name` | string | Yes      | Name of the table to describe       |

**Risk Level:** Low

**Example Response:**
```json
{
  "table": "users",
  "columns": [
    {
      "name": "id",
      "type": "integer",
      "nullable": false,
      "default": "nextval('users_id_seq')",
      "is_pk": true,
      "comment": "Unique user identifier"
    },
    {
      "name": "email",
      "type": "varchar(255)",
      "nullable": false,
      "default": null,
      "is_unique": true,
      "comment": "User's primary email address"
    },
    {
      "name": "created_at",
      "type": "timestamp with time zone",
      "nullable": false,
      "default": "now()",
      "is_pk": false,
      "comment": null
    }
  ],
  "indexes": [
    {"name": "users_pkey", "type": "BTREE", "columns": ["id"]},
    {"name": "idx_users_email", "type": "BTREE", "columns": ["email"]},
    {"name": "idx_users_created_at", "type": "BRIN", "columns": ["created_at"]}
  ],
  "constraints": [
    {"name": "users_pkey", "type": "PRIMARY KEY", "columns": ["id"]},
    {"name": "users_email_key", "type": "UNIQUE", "columns": ["email"]}
  ]
}
```

### `run_query`

Execute a SQL query against the database.

> ⚠️ **High Risk**: This tool can execute arbitrary SQL including data
> modification statements (INSERT, UPDATE, DELETE, DROP). Use with extreme
> caution. Prefer the read-only tools unless you specifically need a custom query.

**Parameters:**

| Parameter | Type   | Required | Description                   |
|-----------|--------|----------|-------------------------------|
| `query`   | string | Yes      | SQL query to execute          |

**Risk Level:** High

**Example Response:**
```json
{
  "query": "SELECT email, created_at FROM users WHERE created_at > '2025-01-01' ORDER BY created_at DESC LIMIT 5",
  "row_count": 5,
  "columns": ["email", "created_at"],
  "rows": [
    ["alice@example.com", "2025-05-20T14:30:00Z"],
    ["bob@example.com", "2025-05-19T09:15:00Z"]
  ],
  "execution_time_ms": 4.2
}
```

### `show_relationships`

Display foreign key relationships for a table — both where this table
references others (outgoing) and where other tables reference this one (incoming).

**Parameters:**

| Parameter    | Type   | Required | Description                         |
|--------------|--------|----------|-------------------------------------|
| `table_name` | string | Yes      | Name of the table to inspect        |

**Risk Level:** Low

**Example Response:**
```json
{
  "table": "orders",
  "outgoing_relations": [
    {
      "constraint_name": "fk_orders_user_id",
      "column": "user_id",
      "references_table": "users",
      "references_column": "id",
      "on_delete": "CASCADE"
    }
  ],
  "incoming_relations": [
    {
      "constraint_name": "fk_line_items_order_id",
      "from_table": "line_items",
      "from_column": "order_id",
      "references_column": "id",
      "on_delete": "CASCADE"
    }
  ]
}
```

## Usage Examples

### Example 1: Explore a new database

```
User: What's in this database? List all the tables.

Agent: [Calls list_tables]

→ Found 14 tables in myapp_dev (public schema):
  • users (12.5K rows, 256 MB)
  • orders (89.2K rows, 1.2 GB) ← largest
  • products (3.4K rows, 48 MB)
  • order_items (180K rows, 890 MB)
  ...
  Largest table: order_items. Most tables in the public schema.
```

### Example 2: Understand a table's structure

```
User: What columns are in the orders table?

Agent: [Calls describe_table with table_name="orders"]

→ orders table has 12 columns:
  • id (serial, PK)
  • user_id (integer, FK → users.id)
  • status (order_status enum)
  • total_cents (integer, NOT NULL)
  • shipping_address_id (integer, FK → addresses.id)
  • promo_code (varchar, nullable)
  • created_at (timestamptz, default: now())
  • updated_at (timestamptz, default: now())

  5 indexes found, including a BRIN index on created_at.
```

### Example 3: Trace relationships

```
User: How are users connected to orders?

Agent: [Calls show_relationships with table_name="users"]

→ users is referenced by:
  • orders.user_id → users.id (CASCADE delete)
  • reviews.user_id → users.id (SET NULL on delete)
  • sessions.user_id → users.id (CASCADE delete)
  • addresses.user_id → users.id (CASCADE delete)

  users has no outgoing foreign keys — it's a root entity.
```

### Example 4: Run a custom query

```
User: Show me the top 5 customers by order count.

Agent: [Calls run_query with:
  SELECT u.email, COUNT(o.id) as order_count
  FROM users u
  JOIN orders o ON o.user_id = u.id
  GROUP BY u.email
  ORDER BY order_count DESC
  LIMIT 5]

→ Results:
  1. alice@example.com — 47 orders
  2. bob@example.com — 32 orders
  3. carol@example.com — 28 orders
  4. dave@example.com — 21 orders
  5. eve@example.com — 18 orders
```

## Security Considerations

### ⚠️ High Risk: `run_query` Tool

The `run_query` tool executes arbitrary SQL. By default in a real
implementation, it should:

1. **Restrict to read-only**: Wrap queries in `READ ONLY` transactions
2. **Statement validation**: Reject DDL (CREATE, ALTER, DROP) and DML
   (INSERT, UPDATE, DELETE) unless explicitly enabled
3. **Query timeout**: Set a statement timeout (e.g., 30 seconds) to
   prevent runaway queries
4. **Row limits**: Impose a maximum row limit (e.g., 1000 rows) to
   prevent excessive data exposure

### Connection Security

| Setting         | Development        | Production              |
|-----------------|---------------------|--------------------------|
| SSL mode        | `prefer`            | `require` or `verify-full` |
| User privileges | Read-write (dev DB) | Read-only user strongly recommended |
| Connection pool | Single connection   | Pooled (PgBouncer)       |
| Statement timeout | 30s                | 10s                      |

### Data Exposure

The `describe_table` and `list_tables` tools expose schema metadata but not
row data. The `run_query` tool exposes actual data — ensure the database user
has only the minimum required permissions.

### Prompt Injection

The `query` parameter in `run_query` is a direct SQL injection surface if
not properly handled. Always:

- Use parameterized queries internally
- Validate and sanitize dynamic identifiers (table names, column names)
- Never interpolate user-supplied values directly into SQL strings

## Recommended Database User Setup

Create a dedicated read-only user for exploration:

```sql
-- Create a read-only role
CREATE ROLE skillforge_readonly WITH LOGIN PASSWORD 'strong_password_here';

-- Grant connect and schema usage
GRANT CONNECT ON DATABASE myapp TO skillforge_readonly;
GRANT USAGE ON SCHEMA public TO skillforge_readonly;

-- Grant read access to all tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO skillforge_readonly;

-- Ensure future tables are readable
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT ON TABLES TO skillforge_readonly;
```

## Dependencies

- Python 3.11+
- `mcp` >= 1.0.0
- `psycopg2-binary` or `asyncpg` (PostgreSQL driver)
- `pydantic` >= 2.0

## FAQ

### Does this skill modify my database?

By default, `run_query` can execute any SQL including writes. In a real
implementation, it should be configured as read-only. The `list_tables`,
`describe_table`, and `show_relationships` tools are strictly read-only.

### Can I connect to multiple databases?

The current version connects to one database specified by `DATABASE_URL`.
For multiple databases, run separate skill instances with different
environment variables.

### What PostgreSQL versions are supported?

PostgreSQL 12, 13, 14, 15, 16, and 17 are tested. The skill uses
`information_schema` which is available in all supported versions.

### How does this compare to pgAdmin or DBeaver?

This skill is complementary to GUI tools. Use pgAdmin/DBeaver for visual
exploration and query building. Use this skill for conversational, natural
language exploration directly within your AI assistant.

### Can I export schema documentation?

The response data from `describe_table` and `show_relationships` can be
fed into documentation generators. Full schema documentation export is
planned for v2.0.

---

*Built with ❤️ by SkillForge. Licensed under MIT.*

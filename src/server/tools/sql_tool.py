from __future__ import annotations

import sqlite3
from pathlib import Path

import sqlglot
from sqlglot import exp


DB_PATH = Path(__file__).resolve().parents[3] / "data" / "enterprise_ops.db"


class SQLSecurityError(ValueError):
    """Raised when a query violates the read-only SQL policy."""


def validate_select_only(sql_query: str) -> exp.Expression:
    """Parse exactly one query and allow only a SELECT/UNION read tree."""
    text = sql_query.strip()
    if not text:
        raise SQLSecurityError("Query cannot be empty")
    if ";" in text.rstrip(";"):
        raise SQLSecurityError("Stacked or multiple SQL statements are blocked")

    try:
        parsed = sqlglot.parse(text, read="sqlite")
    except Exception as exc:
        raise SQLSecurityError("SQL could not be parsed safely") from exc
    if len(parsed) != 1:
        raise SQLSecurityError("Exactly one SQL statement is allowed")

    tree = parsed[0]
    if not isinstance(tree, (exp.Select, exp.Union)):
        raise SQLSecurityError("Only SELECT queries are allowed")

    forbidden = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Create,
        exp.Drop,
        exp.Alter,
        exp.Command,
        exp.Attach,
    )
    if any(tree.find(node_type) is not None for node_type in forbidden):
        raise SQLSecurityError("DDL/DML operations are blocked")
    return tree


def query_database(sql_query: str) -> str:
    """Execute one validated SELECT against SQLite opened in read-only URI mode."""
    validate_select_only(sql_query)
    uri = f"file:{DB_PATH}?mode=ro"
    try:
        with sqlite3.connect(uri, uri=True, timeout=2.0) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA query_only = ON")
            cur = conn.execute(sql_query)
            rows = cur.fetchmany(50)
            columns = [d[0] for d in cur.description or []]
    except sqlite3.Error as exc:
        raise SQLSecurityError("Database query failed safely") from exc

    if not rows:
        return "No rows found."
    lines = [" | ".join(columns)]
    lines.extend(" | ".join(str(row[c]) for c in columns) for row in rows)
    return "\n".join(lines)

"""View-aware SQLite store: strict authorizer + row cap at fetch time.

Authorizer contract (tested by executing real queries, NOT by inspecting
SQL text -- the text check is deliberately disabled in those tests, so a
query that merely mentions a view name cannot pass):
- base-table reads are DENIED; only reads whose authorizer ``source`` arg
  names an allowed view are permitted;
- sqlite_master reads are DENIED;
- writes (INSERT/UPDATE/DELETE), PRAGMA, ATTACH, and load_extension are
  DENIED;
- the authorizer is set on the query connection AFTER setup, so setup
  (table + view creation) uses a separate, unguarded connection.

Row cap: ``fetch_capped`` uses ``fetchmany(MAX + 1)`` and raises when the
result exceeds MAX. No LIMIT rewriting, no fetchall.
"""

from __future__ import annotations

import sqlite3

ALLOWED_VIEWS = frozenset({"v_passages", "v_sources"})
BASE_TABLES = frozenset({"passages", "documents"})


def create_store() -> sqlite3.Connection:
    """Create the store and return a query connection with authorizer set."""
    setup = sqlite3.connect(":memory:")
    setup.execute("CREATE TABLE documents (source_id TEXT PRIMARY KEY, title TEXT)")
    setup.execute(
        "CREATE TABLE passages (chunk_id TEXT PRIMARY KEY, source_id TEXT, text TEXT)")
    setup.execute("CREATE VIEW v_passages AS SELECT chunk_id, source_id, text FROM passages")
    setup.execute("CREATE VIEW v_sources AS SELECT source_id, title FROM documents")
    setup.execute("INSERT INTO documents VALUES ('BB-CDD-01', 'Customer Due Diligence Standard')")
    setup.execute(
        "INSERT INTO passages VALUES ('BB-CDD-01#0', 'BB-CDD-01', "
        "'Identity verification records are retained for seven years.')")
    setup.commit()
    # Re-open via backup so the query connection is a fresh one with the
    # authorizer applied from the start of its life.
    query = sqlite3.connect(":memory:")
    setup.backup(query)
    setup.close()
    query.set_authorizer(_authorizer)
    return query


def _authorizer(action: int, arg1, arg2, _dbname, _trigger_or_view):
    """SQLite authorizer: allow only reads from allowed views."""
    if action == sqlite3.SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ:
        # A read through a view fires TWO authorizer events: one for the
        # underlying base table, tagged with the view name in the
        # trigger/view argument, and one for the view itself. A read is
        # allowed only when one of those two names is an allowed view.
        # A direct base-table read has neither, so it is denied.
        if arg1 in ALLOWED_VIEWS or _trigger_or_view in ALLOWED_VIEWS:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION:
        # arg2 is the function name.
        if arg2 == "load_extension":
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK
    # Everything else: writes, PRAGMA, ATTACH, transactions' DDL, etc.
    if action in (sqlite3.SQLITE_TRANSACTION,):
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


class RowCapExceeded(Exception):
    pass


def fetch_capped(cursor: sqlite3.Cursor, max_rows: int) -> list[tuple]:
    """Fetch at most ``max_rows`` rows; raise if more rows exist."""
    if max_rows < 0:
        raise ValueError("max_rows must be non-negative")
    rows = cursor.fetchmany(max_rows + 1)
    if len(rows) > max_rows:
        raise RowCapExceeded(f"result exceeds row cap of {max_rows}")
    return rows

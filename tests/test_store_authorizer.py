"""View-aware SQLite authorizer tests.

These tests EXECUTE real queries against a connection with the
authorizer set. They do NOT inspect SQL text: a query that merely
mentions an allowed view name in its text must not pass, and a query
that reads a base table must fail even if its text looks harmless.
(That is what "authorizer tests run with the text check disabled" means
here: no string-matching shortcut is used anywhere in this file.)
"""

import sqlite3

import pytest

from compliance_rag.store import RowCapExceeded, create_store, fetch_capped


def test_allowed_view_read_succeeds():
    conn = create_store()
    rows = fetch_capped(conn.execute("SELECT chunk_id FROM v_passages"), 10)
    assert rows and rows[0][0] == "BB-CDD-01#0"


def test_allowed_sources_view_read_succeeds():
    conn = create_store()
    rows = fetch_capped(conn.execute("SELECT source_id FROM v_sources"), 10)
    assert rows


def test_base_table_read_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("SELECT * FROM passages").fetchall()


def test_base_table_read_denied_even_when_view_named_in_text():
    """A base-table read must fail even if the query text mentions a view."""
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute(
            "SELECT * FROM passages -- v_passages is allowed").fetchall()


def test_sqlite_master_read_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("SELECT name FROM sqlite_master").fetchall()


def test_write_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("INSERT INTO passages VALUES ('X', 'Y', 'Z')")


def test_update_and_delete_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("UPDATE passages SET text='x'")
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("DELETE FROM passages")


def test_pragma_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("PRAGMA table_info(passages)").fetchall()


def test_attach_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("ATTACH ':memory:' AS other")


def test_join_with_base_table_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute(
            "SELECT * FROM v_passages JOIN passages USING (chunk_id)").fetchall()


def test_row_cap_enforced_via_fetchmany():
    conn = create_store()
    cursor = conn.execute("SELECT chunk_id FROM v_passages")
    # Cap of 0 with 1 row present must raise.
    with pytest.raises(RowCapExceeded):
        fetch_capped(cursor, 0)


def test_row_cap_allows_within_cap():
    conn = create_store()
    rows = fetch_capped(conn.execute("SELECT chunk_id FROM v_passages"), 10)
    assert len(rows) == 1


def test_row_cap_negative_rejected():
    conn = create_store()
    with pytest.raises(ValueError):
        fetch_capped(conn.execute("SELECT chunk_id FROM v_passages"), -1)

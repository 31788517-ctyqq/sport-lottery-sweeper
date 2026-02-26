#!/usr/bin/env python3
"""One-off data migration from SQLite to PostgreSQL.

Usage:
  python scripts/maintenance/migrate_sqlite_to_postgres.py \
      --sqlite-path /app/data/sport_lottery.db \
      --postgres-url postgresql://postgres:password@postgres:5432/sport_lottery
"""

from __future__ import annotations

import argparse
import sqlite3

import psycopg2
from psycopg2.extras import execute_values


def qident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def sqlite_tables(conn: sqlite3.Connection) -> list[str]:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    return [row[0] for row in cur.fetchall()]


def sqlite_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    cur = conn.execute(f"PRAGMA table_info({qident(table)})")
    return [row[1] for row in cur.fetchall()]


def pg_columns(pg_conn, table: str) -> list[str]:
    with pg_conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
            """,
            (table,),
        )
        return [row[0] for row in cur.fetchall()]


def pg_column_types(pg_conn, table: str) -> dict[str, str]:
    with pg_conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
            """,
            (table,),
        )
        return {row[0]: row[1] for row in cur.fetchall()}


def pg_primary_key_columns(pg_conn, table: str) -> list[str]:
    with pg_conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.attname
            FROM pg_index i
            JOIN pg_class c ON c.oid = i.indrelid
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relname = %s
              AND i.indisprimary
            ORDER BY a.attnum
            """,
            (table,),
        )
        return [row[0] for row in cur.fetchall()]


def _normalize_bool(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(int(value))
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"1", "true", "t", "yes", "y", "on"}:
            return True
        if text in {"0", "false", "f", "no", "n", "off", ""}:
            return False
    return value


def _normalize_int(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if text == "":
            return None
        if text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
            return int(text)
        state_map = {
            "online": 1,
            "active": 1,
            "enabled": 1,
            "running": 1,
            "ready": 1,
            "offline": 0,
            "inactive": 0,
            "disabled": 0,
            "stopped": 0,
            "pending": 0,
            "error": 2,
            "failed": 2,
        }
        mapped = state_map.get(text.lower())
        if mapped is not None:
            return mapped
    return value


def normalize_row(row: tuple, columns: list[str], column_types: dict[str, str]) -> tuple:
    normalized = []
    for idx, item in enumerate(row):
        col = columns[idx]
        col_type = column_types.get(col, "").lower()
        if isinstance(item, memoryview):
            item = bytes(item)
        if col_type == "boolean":
            item = _normalize_bool(item)
        elif col_type in {"smallint", "integer", "bigint"}:
            item = _normalize_int(item)
        normalized.append(item)
    return tuple(normalized)


def sync_serial_sequences(pg_conn, table: str) -> None:
    with pg_conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
              AND column_default LIKE 'nextval(%%'
            """,
            (table,),
        )
        serial_cols = [row[0] for row in cur.fetchall()]

        for col in serial_cols:
            cur.execute(
                f"""
                SELECT setval(
                    pg_get_serial_sequence(%s, %s),
                    COALESCE((SELECT MAX({qident(col)}) FROM {qident(table)}), 0) + 1,
                    false
                )
                """,
                (table, col),
            )


def insert_batches(
    sqlite_conn: sqlite3.Connection,
    pg_conn,
    table: str,
    columns: list[str],
    column_types: dict[str, str],
    pk_columns: list[str],
    batch_size: int,
) -> tuple[int, int]:
    if not columns:
        return 0, 0

    col_ident = ", ".join(qident(c) for c in columns)
    select_sql = f"SELECT {col_ident} FROM {qident(table)}"

    conflict_sql = ""
    if pk_columns and all(pk in columns for pk in pk_columns):
        conflict_cols = ", ".join(qident(c) for c in pk_columns)
        conflict_sql = f" ON CONFLICT ({conflict_cols}) DO NOTHING"

    insert_sql = f"INSERT INTO {qident(table)} ({col_ident}) VALUES %s{conflict_sql}"
    total = 0
    failed = 0

    src_cur = sqlite_conn.execute(select_sql)
    with pg_conn.cursor() as dst_cur:
        while True:
            rows = src_cur.fetchmany(batch_size)
            if not rows:
                break
            payload = [normalize_row(r, columns, column_types) for r in rows]
            dst_cur.execute("SAVEPOINT batch_sp")
            try:
                execute_values(dst_cur, insert_sql, payload, page_size=batch_size)
                dst_cur.execute("RELEASE SAVEPOINT batch_sp")
                total += len(payload)
            except Exception:
                dst_cur.execute("ROLLBACK TO SAVEPOINT batch_sp")
                dst_cur.execute("RELEASE SAVEPOINT batch_sp")
                for one in payload:
                    dst_cur.execute("SAVEPOINT row_sp")
                    try:
                        execute_values(dst_cur, insert_sql, [one], page_size=1)
                        dst_cur.execute("RELEASE SAVEPOINT row_sp")
                        total += 1
                    except Exception:
                        dst_cur.execute("ROLLBACK TO SAVEPOINT row_sp")
                        dst_cur.execute("RELEASE SAVEPOINT row_sp")
                        failed += 1
    return total, failed


def migrate(sqlite_path: str, postgres_url: str, batch_size: int) -> None:
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    pg_conn = psycopg2.connect(postgres_url)

    try:
        pg_conn.autocommit = False
        with pg_conn.cursor() as cur:
            # Keep migration resilient for partial datasets.
            cur.execute("SET session_replication_role = replica")

        migrated_rows = 0
        skipped_tables: list[str] = []

        for table in sqlite_tables(sqlite_conn):
            src_cols = sqlite_columns(sqlite_conn, table)
            dst_cols = pg_columns(pg_conn, table)
            if not dst_cols:
                skipped_tables.append(table)
                continue

            common_cols = [c for c in src_cols if c in dst_cols]
            if not common_cols:
                skipped_tables.append(table)
                continue

            col_types = pg_column_types(pg_conn, table)
            pk_cols = pg_primary_key_columns(pg_conn, table)
            try:
                count, failed = insert_batches(
                    sqlite_conn=sqlite_conn,
                    pg_conn=pg_conn,
                    table=table,
                    columns=common_cols,
                    column_types=col_types,
                    pk_columns=pk_cols,
                    batch_size=batch_size,
                )
                migrated_rows += count
                sync_serial_sequences(pg_conn, table)
                if failed:
                    print(f"[migrate] table={table} rows={count} skipped={failed}")
                else:
                    print(f"[migrate] table={table} rows={count}")
            except Exception as e:
                print(f"[migrate] table={table} skipped_due_to_error={e}")
                continue

        with pg_conn.cursor() as cur:
            cur.execute("SET session_replication_role = origin")
        pg_conn.commit()

        if skipped_tables:
            print(f"[migrate] skipped tables (not in Postgres schema): {', '.join(skipped_tables)}")
        print(f"[migrate] done, total_rows={migrated_rows}")
    except Exception:
        pg_conn.rollback()
        with pg_conn.cursor() as cur:
            cur.execute("SET session_replication_role = origin")
        pg_conn.commit()
        raise
    finally:
        sqlite_conn.close()
        pg_conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate SQLite data to PostgreSQL.")
    parser.add_argument("--sqlite-path", required=True, help="Path to source SQLite db file")
    parser.add_argument("--postgres-url", required=True, help="PostgreSQL URL")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch insert size")
    args = parser.parse_args()

    migrate(args.sqlite_path, args.postgres_url, args.batch_size)


if __name__ == "__main__":
    main()

from __future__ import annotations
import sqlite3
from pathlib import Path
from datetime import datetime
from .config import DB_PATH, APP_DIR

def connect():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            source_root TEXT NOT NULL,
            moved INTEGER NOT NULL DEFAULT 0,
            skipped INTEGER NOT NULL DEFAULT 0,
            errors INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            sha256 TEXT,
            undone INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(operation_id) REFERENCES operations(id)
        )
    """)
    con.commit()
    return con

def create_operation(root):
    with connect() as con:
        cur = con.execute(
            "INSERT INTO operations(created_at, source_root, status) VALUES(?,?,?)",
            (datetime.now().isoformat(timespec="seconds"), str(root), "running")
        )
        return cur.lastrowid

def add_move(op_id, source, destination, digest):
    with connect() as con:
        con.execute(
            "INSERT INTO moves(operation_id,source,destination,sha256) VALUES(?,?,?,?)",
            (op_id, str(source), str(destination), digest)
        )

def finish_operation(op_id, moved, skipped, errors, status="complete"):
    with connect() as con:
        con.execute(
            "UPDATE operations SET moved=?, skipped=?, errors=?, status=? WHERE id=?",
            (moved, skipped, errors, status, op_id)
        )

def history(limit=30):
    with connect() as con:
        return con.execute(
            "SELECT * FROM operations ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()

def moves_for(op_id, only_not_undone=False):
    with connect() as con:
        sql = "SELECT * FROM moves WHERE operation_id=?"
        if only_not_undone:
            sql += " AND undone=0"
        sql += " ORDER BY id DESC"
        return con.execute(sql, (op_id,)).fetchall()

def mark_undone(move_id):
    with connect() as con:
        con.execute("UPDATE moves SET undone=1 WHERE id=?", (move_id,))

def latest_operation():
    with connect() as con:
        return con.execute("SELECT * FROM operations ORDER BY id DESC LIMIT 1").fetchone()

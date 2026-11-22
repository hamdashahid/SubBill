from __future__ import annotations
import hashlib, json, sqlite3
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS register_items(
 item_id INTEGER PRIMARY KEY, user_id TEXT, merchant_key TEXT, amount REAL,
 interval TEXT, next_renewal TEXT, status TEXT DEFAULT 'current', version INTEGER DEFAULT 1,
 source_ref TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, supersedes_id INTEGER);
CREATE TABLE IF NOT EXISTS transactions(
 id INTEGER PRIMARY KEY, user_id TEXT, cycle INTEGER, file_sha256 TEXT, row_ref TEXT,
 date TEXT, description TEXT, amount REAL, merchant_key TEXT, memo TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS tx_unique ON transactions(user_id,file_sha256,row_ref);
CREATE TABLE IF NOT EXISTS source_files(user_id TEXT, sha256 TEXT, name TEXT, version INTEGER, ingested_at TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(user_id,sha256));
CREATE TABLE IF NOT EXISTS decisions(id INTEGER PRIMARY KEY, user_id TEXT, merchant_key TEXT, decision TEXT, reason TEXT, decided_at TEXT DEFAULT CURRENT_TIMESTAMP, status TEXT DEFAULT 'current');
CREATE TABLE IF NOT EXISTS issues(issue_id INTEGER PRIMARY KEY, user_id TEXT, cycle INTEGER, type TEXT, merchant_key TEXT, detail TEXT, status TEXT DEFAULT 'open', resolution TEXT, idempotency_key TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS evidence(id INTEGER PRIMARY KEY, user_id TEXT, merchant_key TEXT, note TEXT, source_ref TEXT, added_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS preferences(user_id TEXT, key TEXT, value TEXT, PRIMARY KEY(user_id,key));
CREATE TABLE IF NOT EXISTS pending_questions(id INTEGER PRIMARY KEY, user_id TEXT, merchant_key TEXT, question TEXT, cycle INTEGER, status TEXT DEFAULT 'open');
CREATE TABLE IF NOT EXISTS drafts(id INTEGER PRIMARY KEY, user_id TEXT, merchant_key TEXT, body TEXT, label TEXT DEFAULT 'UNSENT', idempotency_key TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS corrections(id INTEGER PRIMARY KEY, user_id TEXT, merchant_key TEXT, field TEXT, value TEXT, reason TEXT, confirmed INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS action_log(id INTEGER PRIMARY KEY, ts TEXT DEFAULT CURRENT_TIMESTAMP, user_id TEXT, cycle INTEGER, tool TEXT, args_hash TEXT, memory_reads TEXT, memory_writes TEXT, outcome TEXT, error TEXT, duration_ms REAL);
"""

def connect(path: str | Path) -> sqlite3.Connection:
    db = sqlite3.connect(str(path))
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db

def key(*parts: Any) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()

def log(db, user_id, tool, outcome, cycle=None, error=None):
    db.execute("INSERT INTO action_log(user_id,cycle,tool,args_hash,outcome,error) VALUES(?,?,?,?,?,?)",
               (user_id, cycle, tool, key(user_id, tool), outcome, error))
    db.commit()

def current_register(db, user_id):
    return db.execute("SELECT * FROM register_items WHERE user_id=? AND status='current' ORDER BY merchant_key", (user_id,)).fetchall()

def current_decision(db, user_id, merchant):
    return db.execute("SELECT * FROM decisions WHERE user_id=? AND merchant_key=? AND status='current' ORDER BY id DESC LIMIT 1", (user_id, merchant)).fetchone()

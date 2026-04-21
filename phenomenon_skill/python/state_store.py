#!/usr/bin/env python3
"""SQLite-backed state store for phenomenon skill pack.

Standard library only.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class CaseRecord:
    case_id: int
    mode: str
    title: str
    problem: str
    created_at: str
    updated_at: str


class StateStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mode TEXT NOT NULL CHECK (mode IN ('general', 'computing_debug')),
                    title TEXT NOT NULL,
                    problem TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS case_rounds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER NOT NULL,
                    round_no INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    summary TEXT DEFAULT '',
                    FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE,
                    UNIQUE(case_id, round_no)
                );

                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER NOT NULL,
                    round_no INTEGER NOT NULL,
                    kind TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_notes_case_round ON notes(case_id, round_no);
                CREATE INDEX IF NOT EXISTS idx_notes_kind ON notes(kind);
                """
            )
        self._clear_caches()

    def _clear_caches(self) -> None:
        self.get_case.cache_clear()
        self.list_notes.cache_clear()
        self.max_round.cache_clear()

    def create_case(self, title: str, problem: str, mode: str = "general") -> int:
        if mode not in {"general", "computing_debug"}:
            raise ValueError(f"unsupported mode: {mode}")
        now = utcnow_iso()
        with self.connect() as conn:
            cur = conn.execute(
                "INSERT INTO cases(mode, title, problem, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (mode, title, problem, now, now),
            )
            case_id = int(cur.lastrowid)
        self._clear_caches()
        return case_id

    @lru_cache(maxsize=256)
    def get_case(self, case_id: int) -> CaseRecord:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id, mode, title, problem, created_at, updated_at FROM cases WHERE id = ?",
                (case_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"case not found: {case_id}")
        return CaseRecord(
            case_id=row["id"],
            mode=row["mode"],
            title=row["title"],
            problem=row["problem"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @lru_cache(maxsize=512)
    def max_round(self, case_id: int) -> int:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(round_no), 0) AS max_round FROM case_rounds WHERE case_id = ?",
                (case_id,),
            ).fetchone()
        return int(row["max_round"]) if row else 0

    def ensure_round(self, case_id: int, round_no: Optional[int] = None, summary: str = "") -> int:
        if round_no is None:
            round_no = self.max_round(case_id) + 1
        now = utcnow_iso()
        with self.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO case_rounds(case_id, round_no, created_at, summary) VALUES (?, ?, ?, ?)",
                (case_id, round_no, now, summary),
            )
            conn.execute(
                "UPDATE cases SET updated_at = ? WHERE id = ?",
                (now, case_id),
            )
        self._clear_caches()
        return round_no

    def add_notes(self, case_id: int, round_no: int, items: Iterable[tuple[str, str]]) -> None:
        now = utcnow_iso()
        with self.connect() as conn:
            conn.executemany(
                "INSERT INTO notes(case_id, round_no, kind, content, created_at) VALUES (?, ?, ?, ?, ?)",
                [(case_id, round_no, kind, content.strip(), now) for kind, content in items if content.strip()],
            )
            conn.execute(
                "UPDATE cases SET updated_at = ? WHERE id = ?",
                (now, case_id),
            )
        self._clear_caches()

    @lru_cache(maxsize=2048)
    def list_notes(self, case_id: int) -> List[sqlite3.Row]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT case_id, round_no, kind, content, created_at FROM notes WHERE case_id = ? ORDER BY round_no, id",
                (case_id,),
            ).fetchall()
        return rows

    def get_round_notes(self, case_id: int, round_no: int) -> List[sqlite3.Row]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT case_id, round_no, kind, content, created_at FROM notes WHERE case_id = ? AND round_no = ? ORDER BY id",
                (case_id, round_no),
            ).fetchall()
        return rows

    def latest_state(self, case_id: int) -> dict:
        case = self.get_case(case_id)
        notes = self.list_notes(case_id)
        grouped: dict[str, list[str]] = {}
        for row in notes:
            grouped.setdefault(row["kind"], []).append(row["content"])
        return {
            "case_id": case.case_id,
            "mode": case.mode,
            "title": case.title,
            "problem": case.problem,
            "facts": grouped.get("fact", []),
            "interpretations": grouped.get("interpretation", []),
            "emotions": grouped.get("emotion", []),
            "actors": grouped.get("actor", []),
            "timeline": grouped.get("timeline", []),
            "contradictions": grouped.get("contradiction", []),
            "hypotheses": grouped.get("hypothesis", []),
            "unknowns": grouped.get("unknown", []),
            "questions": grouped.get("question", []),
            "scope": grouped.get("scope", []),
            "environment": grouped.get("environment", []),
            "recent_changes": grouped.get("recent_change", []),
            "signals": grouped.get("signal", []),
            "ruled_out": grouped.get("ruled_out", []),
            "next_actions": grouped.get("next_action", []),
            "rounds": self.max_round(case_id),
        }

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from context_compiler import compile_context
from question_engine import next_questions
from state_store import StateStore


NOTE_KINDS = {
    "facts": "fact",
    "interpretations": "interpretation",
    "emotions": "emotion",
    "actors": "actor",
    "timeline": "timeline",
    "contradictions": "contradiction",
    "hypotheses": "hypothesis",
    "unknowns": "unknown",
    "questions": "question",
    "scope": "scope",
    "environment": "environment",
    "recent_changes": "recent_change",
    "signals": "signal",
    "ruled_out": "ruled_out",
    "next_actions": "next_action",
}


def add_common_db_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument("--db", required=True, help="Path to SQLite database")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phenomenon Skill Pack CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="Initialize SQLite database")
    add_common_db_arg(p)

    p = sub.add_parser("create-case", help="Create a case")
    add_common_db_arg(p)
    p.add_argument("--title", required=True)
    p.add_argument("--problem", required=True)
    p.add_argument("--mode", choices=["general", "computing_debug"], default="general")

    p = sub.add_parser("add-round", help="Create round and attach notes")
    add_common_db_arg(p)
    p.add_argument("--case-id", type=int, required=True)
    p.add_argument("--round-no", type=int)
    p.add_argument("--summary", default="")
    for flag in NOTE_KINDS:
        p.add_argument(f"--{flag}", default="", help=f"Semicolon-separated {flag}")

    p = sub.add_parser("compile-context", help="Render compact next-round context")
    add_common_db_arg(p)
    p.add_argument("--case-id", type=int, required=True)

    p = sub.add_parser("next-questions", help="Generate heuristic next questions")
    add_common_db_arg(p)
    p.add_argument("--case-id", type=int, required=True)
    p.add_argument("--limit", type=int, default=5)

    p = sub.add_parser("show-state", help="Show the latest state as markdown-ish output")
    add_common_db_arg(p)
    p.add_argument("--case-id", type=int, required=True)

    return parser


def parse_list(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(";") if item.strip()]


def cmd_init(args) -> int:
    store = StateStore(args.db)
    store.init_db()
    print(f"Initialized DB: {args.db}")
    return 0


def cmd_create_case(args) -> int:
    store = StateStore(args.db)
    store.init_db()
    case_id = store.create_case(title=args.title, problem=args.problem, mode=args.mode)
    print(case_id)
    return 0


def cmd_add_round(args) -> int:
    store = StateStore(args.db)
    round_no = store.ensure_round(args.case_id, args.round_no, args.summary)
    items: list[tuple[str, str]] = []
    for flag, kind in NOTE_KINDS.items():
        for value in parse_list(getattr(args, flag)):
            items.append((kind, value))
    if items:
        store.add_notes(args.case_id, round_no, items)
    print(round_no)
    return 0


def cmd_compile_context(args) -> int:
    store = StateStore(args.db)
    state = store.latest_state(args.case_id)
    print(compile_context(state))
    return 0


def cmd_next_questions(args) -> int:
    store = StateStore(args.db)
    state = store.latest_state(args.case_id)
    for idx, q in enumerate(next_questions(state, limit=args.limit), start=1):
        print(f"{idx}. {q}")
    return 0


def cmd_show_state(args) -> int:
    store = StateStore(args.db)
    state = store.latest_state(args.case_id)
    for key, value in state.items():
        print(f"## {key}")
        if isinstance(value, list):
            if value:
                for item in value:
                    print(f"- {item}")
            else:
                print("- （暂无）")
        else:
            print(value)
        print()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cmd_map = {
        "init": cmd_init,
        "create-case": cmd_create_case,
        "add-round": cmd_add_round,
        "compile-context": cmd_compile_context,
        "next-questions": cmd_next_questions,
        "show-state": cmd_show_state,
    }
    return cmd_map[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Prepare incremental Codex and OpenCode conversations for daily observation.

The collector uses a two-phase cursor. ``prepare`` creates a private pending
batch without advancing the cursor; ``commit`` advances it only after the
observer has successfully reviewed the batch.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


DEFAULT_CODEX_ROOTS = (
    Path.home() / ".codex" / "sessions",
    Path.home() / ".codex" / "archived_sessions",
)
DEFAULT_OPENCODE_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
DEFAULT_STATE_DIR = Path.home() / ".codex" / "context_observer"


def read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return fallback


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    partial.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(partial, path)


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def timestamp_from_iso(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def collect_codex(
    roots: list[Path], previous: dict[str, int], cutoff: float
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    sessions: list[dict[str, Any]] = []
    next_offsets = dict(previous)

    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.jsonl")):
            key = str(path.resolve())
            size = path.stat().st_size
            is_new_file = key not in previous
            if is_new_file and path.stat().st_mtime < cutoff:
                next_offsets[key] = size
                continue

            offset = previous.get(key, 0)
            if offset > size:
                offset = 0

            metadata: dict[str, Any] = {"path": key, "messages": []}
            response_messages: list[dict[str, Any]] = []
            with path.open("r", encoding="utf-8") as handle:
                # The header is outside the incremental range on later runs.
                try:
                    header = json.loads(handle.readline())
                    if header.get("type") == "session_meta":
                        payload = header.get("payload", {})
                        metadata.update(
                            session_id=payload.get("session_id") or payload.get("id"),
                            cwd=payload.get("cwd"),
                            thread_source=payload.get("thread_source"),
                            source=payload.get("source"),
                        )
                except json.JSONDecodeError:
                    pass
                handle.seek(offset)
                for line in handle:
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    event_type = event.get("type")
                    payload = event.get("payload", {})
                    if event_type == "session_meta":
                        metadata.update(
                            {
                                "session_id": payload.get("session_id") or payload.get("id"),
                                "cwd": payload.get("cwd"),
                                "thread_source": payload.get("thread_source"),
                                "source": payload.get("source"),
                            }
                        )
                        continue
                    if event_type == "response_item" and payload.get("type") == "message":
                        role = payload.get("role")
                        if role not in {"user", "assistant"}:
                            continue
                        if role == "assistant" and payload.get("channel") != "final":
                            continue
                        text = "\n".join(
                            part.get("text", "")
                            for part in payload.get("content", [])
                            if isinstance(part, dict) and isinstance(part.get("text"), str)
                        ).strip()
                        if role == "user" and text.startswith((
                            "# AGENTS.md instructions", "<environment_context>",
                            "<external_codex_apps_open_page>", "<turn_aborted>",
                            "<user_instructions>",
                        )):
                            continue
                        if is_new_file and timestamp_from_iso(event.get("timestamp")) < cutoff:
                            continue
                        if text:
                            response_messages.append(
                                {"timestamp": event.get("timestamp"), "role": role, "text": text}
                            )
                        continue
                    if event_type != "event_msg":
                        continue
                    if payload.get("type") == "user_message":
                        role = "user"
                    elif (
                        payload.get("type") == "agent_message"
                        and payload.get("phase") == "final_answer"
                    ):
                        role = "assistant"
                    else:
                        continue
                    if is_new_file and timestamp_from_iso(event.get("timestamp")) < cutoff:
                        continue
                    text = str(payload.get("message", "")).strip()
                    if text:
                        metadata["messages"].append(
                            {"timestamp": event.get("timestamp"), "role": role, "text": text}
                        )

            next_offsets[key] = size
            if (metadata.get("thread_source") in {"automation", "subagent"}
                    or isinstance(metadata.get("source"), dict)):
                continue
            # Older logs contain both representations. Prefer event messages
            # when available so a turn is not observed twice.
            if not metadata["messages"]:
                metadata["messages"] = response_messages
            if any(message["role"] == "user" for message in metadata["messages"]):
                sessions.append(metadata)

    # A rollout can exist in both active and archived roots.
    by_session: dict[str, dict[str, Any]] = {}
    for session in sessions:
        session_key = session.get("session_id") or session["path"]
        if session_key not in by_session:
            by_session[session_key] = session
            continue
        existing = by_session[session_key]["messages"]
        seen = {(m["timestamp"], m["role"], m["text"]) for m in existing}
        for message in session["messages"]:
            key = (message["timestamp"], message["role"], message["text"])
            if key not in seen:
                existing.append(message)
                seen.add(key)
        existing.sort(key=lambda m: m["timestamp"] or "")
    return list(by_session.values()), next_offsets


def collect_opencode(
    db_path: Path, previous: dict[str, Any], cutoff: float
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not db_path.exists():
        return [], previous

    previous_time = int(previous.get("time_created", cutoff * 1000))
    previous_id = str(previous.get("message_id", ""))
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            """
            SELECT m.id AS message_id, m.time_created, m.session_id,
                   json_extract(m.data, '$.role') AS role,
                   json_extract(p.data, '$.text') AS text,
                   s.title, s.directory
            FROM message m
            JOIN session s ON s.id = m.session_id
            JOIN part p ON p.message_id = m.id
            WHERE s.parent_id IS NULL
              AND json_extract(p.data, '$.type') = 'text'
              AND (m.time_created > ? OR (m.time_created = ? AND m.id > ?))
            ORDER BY m.time_created, m.id, p.time_created, p.id
            """,
            (previous_time, previous_time, previous_id),
        ).fetchall()
        latest = connection.execute(
            """
            SELECT m.time_created, m.id AS message_id
            FROM message m JOIN session s ON s.id = m.session_id
            WHERE s.parent_id IS NULL
            ORDER BY m.time_created DESC, m.id DESC LIMIT 1
            """
        ).fetchone()
    finally:
        connection.close()

    by_session: dict[str, dict[str, Any]] = {}
    for row in rows:
        text = str(row["text"] or "").strip()
        role = str(row["role"] or "")
        if not text or role not in {"user", "assistant"}:
            continue
        session = by_session.setdefault(
            row["session_id"],
            {
                "session_id": row["session_id"],
                "title": row["title"],
                "cwd": row["directory"],
                "messages": [],
            },
        )
        session["messages"].append(
            {
                "timestamp": datetime.fromtimestamp(
                    row["time_created"] / 1000, tz=timezone.utc
                ).isoformat(),
                "role": role,
                "text": text,
            }
        )

    sessions = [
        session
        for session in by_session.values()
        if any(message["role"] == "user" for message in session["messages"])
    ]
    next_cursor = previous
    if latest:
        next_cursor = {
            "time_created": int(latest["time_created"]),
            "message_id": str(latest["message_id"]),
        }
    return sessions, next_cursor


def prepare(args: argparse.Namespace) -> int:
    state_dir = args.state_dir.expanduser().resolve()
    state_path = state_dir / "state.json"
    pending_path = state_dir / "pending.json"
    if pending_path.exists() and not args.replace:
        pending = read_json(pending_path, {})
        print(
            f"Pending batch already exists: {pending_path} "
            f"({pending.get('message_count', 0)} messages)."
        )
        return 0

    state = read_json(state_path, {"codex": {"files": {}}, "opencode": {}})
    cutoff = (
        datetime.now(timezone.utc) - timedelta(hours=args.bootstrap_hours)
    ).timestamp()
    codex_sessions, codex_offsets = collect_codex(
        args.codex_root, state.get("codex", {}).get("files", {}), cutoff
    )
    opencode_sessions, opencode_cursor = collect_opencode(
        args.opencode_db.expanduser(), state.get("opencode", {}), cutoff
    )
    message_count = sum(
        len(session["messages"]) for session in codex_sessions + opencode_sessions
    )
    payload = {
        "generated_at": iso_now(),
        "message_count": message_count,
        "sources": {"codex": codex_sessions, "opencode": opencode_sessions},
        "next_state": {
            "updated_at": iso_now(),
            "codex": {"files": codex_offsets},
            "opencode": opencode_cursor,
        },
    }
    write_json_atomic(pending_path, payload)
    print(
        f"Prepared {message_count} messages from "
        f"{len(codex_sessions)} Codex and {len(opencode_sessions)} OpenCode sessions."
    )
    print(f"Pending batch: {pending_path}")
    return 0


def commit(args: argparse.Namespace) -> int:
    state_dir = args.state_dir.expanduser().resolve()
    pending_path = state_dir / "pending.json"
    pending = read_json(pending_path, None)
    if not pending or "next_state" not in pending:
        print("No valid pending batch to commit.")
        return 1
    write_json_atomic(state_dir / "state.json", pending["next_state"])
    pending_path.unlink()
    print("Observer cursor committed.")
    return 0


def status(args: argparse.Namespace) -> int:
    state_dir = args.state_dir.expanduser().resolve()
    state = read_json(state_dir / "state.json", {})
    pending = read_json(state_dir / "pending.json", None)
    print(json.dumps({"state": state, "pending": pending}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "commit", "status"))
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    parser.add_argument(
        "--codex-root",
        type=Path,
        action="append",
        default=None,
        help="Repeat to scan multiple Codex session roots.",
    )
    parser.add_argument("--opencode-db", type=Path, default=DEFAULT_OPENCODE_DB)
    parser.add_argument("--bootstrap-hours", type=int, default=36)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    args.codex_root = args.codex_root or list(DEFAULT_CODEX_ROOTS)
    return {"prepare": prepare, "commit": commit, "status": status}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())

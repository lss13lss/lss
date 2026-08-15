#!/usr/bin/env python3
"""Archive local Codex and OpenCode conversations to an external drive.

The source stores remain untouched. Files are written to a temporary path,
validated, and then renamed into place so an interrupted copy cannot replace a
good archive with a partial file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_ARCHIVE_ROOT = Path("/Volumes/KESU/AI_Context_Archive")
CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
OPENCODE_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "logs"
LOG_PATH = LOG_DIR / "archive.log"


def log(message: str) -> None:
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    line = f"[{timestamp}] {message}"
    print(line)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_verified(source: Path, destination: Path, dry_run: bool) -> str:
    if destination.exists():
        source_stat = source.stat()
        destination_stat = destination.stat()
        # ExFAT does not preserve nanosecond timestamps reliably. For files of
        # the same size, compare content instead of trusting mtime precision.
        if source_stat.st_size == destination_stat.st_size and sha256(source) == sha256(
            destination
        ):
            return "unchanged"

    if dry_run:
        return "would_copy"

    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".partial")
    partial.unlink(missing_ok=True)
    shutil.copy2(source, partial)

    # Hash after copying. If the source changed while it was being copied, the
    # hashes differ and the partial file is discarded for retry on the next run.
    source_hash = sha256(source)
    partial_hash = sha256(partial)
    if source_hash != partial_hash:
        partial.unlink(missing_ok=True)
        return "changed_during_copy"

    os.replace(partial, destination)
    return "copied"


def archive_codex(archive_root: Path, dry_run: bool) -> dict[str, int]:
    counts = {
        "copied": 0,
        "unchanged": 0,
        "would_copy": 0,
        "changed_during_copy": 0,
    }
    sources = (
        ("active", CODEX_HOME / "sessions"),
        ("archived", CODEX_HOME / "archived_sessions"),
    )

    for category, source_root in sources:
        if not source_root.exists():
            continue
        for source in source_root.rglob("*.jsonl"):
            relative = source.relative_to(source_root)
            destination = archive_root / "raw_sessions" / "codex" / category / relative
            result = copy_verified(source, destination, dry_run)
            counts[result] += 1
    return counts


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    partial.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(partial, path)


def list_opencode_sessions() -> list[dict[str, Any]]:
    if not OPENCODE_DB.exists():
        return []
    connection = sqlite3.connect(f"file:{OPENCODE_DB}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            """
            SELECT id, title, directory, time_created, time_updated
            FROM session
            ORDER BY time_created
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def archive_opencode(archive_root: Path, dry_run: bool) -> dict[str, int]:
    counts = {"exported": 0, "unchanged": 0, "would_export": 0, "failed": 0}
    destination_root = archive_root / "raw_sessions" / "opencode"
    state_path = destination_root / "state.json"
    state = load_json(state_path, {"sessions": {}})
    opencode = shutil.which("opencode")

    sessions = list_opencode_sessions()
    for session in sessions:
        session_id = str(session["id"])
        updated = int(session["time_updated"])
        destination = destination_root / "sessions" / f"{session_id}.json"
        previous = state.get("sessions", {}).get(session_id)
        if previous == updated and destination.exists():
            counts["unchanged"] += 1
            continue
        if dry_run:
            counts["would_export"] += 1
            continue
        if not opencode:
            counts["failed"] += 1
            log(f"OpenCode export skipped: executable not found for {session_id}")
            continue

        export_temp_path: Path | None = None
        try:
            # OpenCode 1.18.7 can truncate larger exports when stdout is a
            # program pipe. A real temporary file avoids that CLI behavior.
            with tempfile.NamedTemporaryFile(
                mode="w+b", prefix="opencode-export-", suffix=".json", delete=False
            ) as export_temp:
                export_temp_path = Path(export_temp.name)
                result = subprocess.run(
                    [opencode, "export", session_id],
                    check=False,
                    stdout=export_temp,
                    stderr=subprocess.PIPE,
                    timeout=300,
                )
            if result.returncode != 0:
                counts["failed"] += 1
                error = result.stderr.decode("utf-8", errors="replace").strip()
                log(f"OpenCode export failed for {session_id}: {error}")
                continue
            payload = json.loads(export_temp_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, subprocess.TimeoutExpired) as error:
            counts["failed"] += 1
            log(f"OpenCode export validation failed for {session_id}: {error}")
            continue
        finally:
            if export_temp_path is not None:
                export_temp_path.unlink(missing_ok=True)

        write_json_atomic(destination, payload)
        state.setdefault("sessions", {})[session_id] = updated
        counts["exported"] += 1

    if not dry_run:
        state["last_run"] = datetime.now().astimezone().isoformat(timespec="seconds")
        write_json_atomic(state_path, state)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Archive Codex and OpenCode sessions to an external drive."
    )
    parser.add_argument(
        "--archive-root",
        type=Path,
        default=DEFAULT_ARCHIVE_ROOT,
        help=f"Archive root (default: {DEFAULT_ARCHIVE_ROOT})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report planned work without writing to the external drive.",
    )
    args = parser.parse_args()
    archive_root = args.archive_root.resolve()

    volume_root = Path("/Volumes") / archive_root.parts[2]
    if not volume_root.is_mount():
        log(f"External drive is not mounted at {volume_root}; nothing changed.")
        return 0

    if not os.access(volume_root, os.W_OK):
        log(f"External drive is not writable at {volume_root}.")
        return 1

    codex_counts = archive_codex(archive_root, args.dry_run)
    opencode_counts = archive_opencode(archive_root, args.dry_run)
    log(
        "Archive completed"
        f" dry_run={args.dry_run}"
        f" codex={json.dumps(codex_counts, ensure_ascii=False)}"
        f" opencode={json.dumps(opencode_counts, ensure_ascii=False)}"
    )
    return 1 if opencode_counts["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())

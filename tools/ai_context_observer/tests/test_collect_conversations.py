import json
import sqlite3
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

import collect_conversations as observer


class ObserverTest(unittest.TestCase):
    def test_prepare_and_commit_are_incremental(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_root = root / "sessions"
            codex_root.mkdir()
            session = codex_root / "session.jsonl"
            events = [
                {
                    "type": "session_meta",
                    "payload": {
                        "session_id": "codex-1",
                        "cwd": "/work",
                        "thread_source": "user",
                    },
                },
                {
                    "timestamp": "2026-08-05T00:00:00Z",
                    "type": "event_msg",
                    "payload": {"type": "user_message", "message": "保留这个偏好"},
                },
                {
                    "timestamp": "2026-08-05T00:00:01Z",
                    "type": "event_msg",
                    "payload": {
                        "type": "agent_message",
                        "phase": "final_answer",
                        "message": "已了解",
                    },
                },
            ]
            session.write_text(
                "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events),
                encoding="utf-8",
            )
            database = root / "opencode.db"
            connection = sqlite3.connect(database)
            connection.executescript(
                """
                CREATE TABLE session (
                    id TEXT PRIMARY KEY, parent_id TEXT, title TEXT, directory TEXT
                );
                CREATE TABLE message (
                    id TEXT PRIMARY KEY, session_id TEXT, time_created INTEGER, data TEXT
                );
                CREATE TABLE part (
                    id TEXT PRIMARY KEY, message_id TEXT, time_created INTEGER, data TEXT
                );
                """
            )
            connection.execute(
                "INSERT INTO session VALUES (?, ?, ?, ?)",
                ("open-1", None, "测试", "/work"),
            )
            connection.execute(
                "INSERT INTO message VALUES (?, ?, ?, ?)",
                ("msg-1", "open-1", 1785888000000, '{"role":"user"}'),
            )
            connection.execute(
                "INSERT INTO part VALUES (?, ?, ?, ?)",
                ("part-1", "msg-1", 1785888000000, '{"type":"text","text":"新的目标"}'),
            )
            connection.commit()
            connection.close()

            args = Namespace(
                state_dir=root / "state",
                codex_root=[codex_root],
                opencode_db=database,
                bootstrap_hours=24 * 365,
                replace=False,
            )
            self.assertEqual(observer.prepare(args), 0)
            pending = observer.read_json(args.state_dir / "pending.json", {})
            self.assertEqual(pending["message_count"], 3)
            self.assertFalse((args.state_dir / "state.json").exists())

            self.assertEqual(observer.commit(args), 0)
            self.assertTrue((args.state_dir / "state.json").exists())
            self.assertFalse((args.state_dir / "pending.json").exists())

            self.assertEqual(observer.prepare(args), 0)
            pending = observer.read_json(args.state_dir / "pending.json", {})
            self.assertEqual(pending["message_count"], 0)


if __name__ == "__main__":
    unittest.main()

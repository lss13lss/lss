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


    def test_response_items_incremental_header_and_automation_filter(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            def put(path, events, mode="w"):
                with path.open(mode, encoding="utf-8") as handle:
                    for event in events:
                        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
            def message(text, role="user", channel=None):
                return {"timestamp": "2026-09-30T00:00:00Z", "type": "response_item",
                        "payload": {"type": "message", "role": role, "channel": channel,
                                    "content": [{"type": "input_text", "text": text}]}}
            header = {"type": "session_meta", "payload": {"id": "fixture-1", "thread_source": "user"}}
            path = root / "user.jsonl"
            put(path, [header, message("# AGENTS.md instructions\n配置"), message("当前做项目B"),
                       message("内部推理", "assistant", "analysis"), message("已记录", "assistant", "final")])
            sessions, offsets = observer.collect_codex([root], {}, 0)
            self.assertEqual([m["text"] for m in sessions[0]["messages"]], ["当前做项目B", "已记录"])
            self.assertEqual(sessions[0]["session_id"], "fixture-1")
            auto = root / "automation.jsonl"
            put(auto, [{"type": "session_meta", "payload": {"id": "auto", "thread_source": "automation"}}, message("自动任务")])
            _, offsets = observer.collect_codex([root], offsets, 0)
            put(auto, [message("后续自动任务")], "a")
            put(path, [message("后续人工确认")], "a")
            sessions, _ = observer.collect_codex([root], offsets, 0)
            self.assertEqual(len(sessions), 1)
            self.assertEqual(sessions[0]["session_id"], "fixture-1")
            self.assertEqual(sessions[0]["messages"][0]["text"], "后续人工确认")

    def test_dual_formats_do_not_duplicate_messages(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "mixed.jsonl"
            path.write_text("\n".join(json.dumps(e) for e in [
                {"type": "session_meta", "payload": {"id": "mixed"}},
                {"type": "response_item", "payload": {"type": "message", "role": "user",
                 "content": [{"text": "确认"}]}},
                {"type": "event_msg", "payload": {"type": "user_message", "message": "确认"}},
            ]) + "\n")
            sessions, _ = observer.collect_codex([Path(temporary)], {}, 0)
            self.assertEqual(len(sessions[0]["messages"]), 1)
            archive = Path(temporary) / "archive"
            archive.mkdir()
            (archive / "copy.jsonl").write_bytes(path.read_bytes())
            sessions, offsets = observer.collect_codex([Path(temporary)], {}, 0)
            self.assertEqual(len(sessions), 1)
            self.assertEqual(len(sessions[0]["messages"]), 1)
            self.assertEqual(len(offsets), 2)


if __name__ == "__main__":
    unittest.main()

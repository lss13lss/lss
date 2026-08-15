# 每日对话 Observer

这个工具为每日 Observer 准备 Codex 与 OpenCode 的增量对话。它只负责采集，
是否写入观察由自动任务按 `OBSERVER_PROMPT.md` 判断。

## 安全边界

- 原始对话不会写入 Obsidian vault。
- 临时批次和游标保存在 `~/.codex/context_observer/`。
- 自动任务第一阶段只允许追加 `OBSERVATIONS.md`。
- `prepare` 不推进游标；只有成功处理后执行 `commit` 才会推进。
- Codex 自动任务、sub-agent 和 OpenCode 子会话不会进入观察批次。

## 手动检查

```bash
python3 tools/ai_context_observer/collect_conversations.py prepare
python3 tools/ai_context_observer/collect_conversations.py status
python3 tools/ai_context_observer/collect_conversations.py commit
```

首次运行只读取最近 36 小时的对话，避免一次载入全部历史记录。后续运行根据
文件偏移量和 OpenCode 消息游标增量读取。

# AI 对话外置硬盘归档

每天将本机保存的 Codex 与 OpenCode 原始会话增量备份到：

`/Volumes/KESU/AI_Context_Archive/raw_sessions/`

## 数据流

1. Codex 的 `~/.codex/sessions/` 与 `~/.codex/archived_sessions/` 按原目录结构复制。
2. OpenCode 会话使用官方 `opencode export <session-id>` 导出为 JSON。
3. 文件先写入 `.partial`，校验成功后才替换正式文件。
4. 硬盘没有挂载时安全跳过，下次运行继续。

当前阶段只做归档，不删除应用自己的会话，也不执行 AI 摘要。这样便于先验证数据完整性。

## 手动运行

```bash
python3 tools/ai_context_archive/archive_ai_sessions.py --dry-run
python3 tools/ai_context_archive/archive_ai_sessions.py
```

运行日志保存在 `tools/ai_context_archive/logs/archive.log`。

## 安全提醒

原始会话可能包含私密信息、文件片段或密钥。外置硬盘应妥善保管；如果需要跨设备携带，建议使用加密卷。

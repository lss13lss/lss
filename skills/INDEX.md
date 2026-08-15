---
title: 本地 Skill 索引
tags:
  - AI/skills
status: active
updated: 2026-08-14
---

# 本地 Skill 索引

Vault `skills/` 下的可复用 Agent Skill。所有 skill 同时暴露给 Agent 发现链
（`~/.agents/skills/<name>/SKILL.md`），这里登记源头与用途，方便定位和更新。

## 已安装

| Skill | 来源 | 用途 |
|---|---|---|
| ai-session-export | [grapeot/ai_session_export](https://github.com/grapeot/ai_session_export)（MIT，vendored，commit `b884cde`，2026-08-14） | 将 OpenCode / Claude Code / Codex / Antigravity / Cursor 等 AI 会话增量导出为统一 Markdown 归档 |
| personal-style-script-writer | 自建 | 按个人风格生成中文口播/图文脚本 |
| bestpractice-ai-programming-mindset | [grapeot/context-infrastructure](https://github.com/grapeot/context-infrastructure)（vendored，commit `8834577e`，2026-08-14） | AI 编程核心方法论：70% 问题、成功标准、反馈闭环、认知外包边界（导师/对照材料） |
| online-media-skill | [grapeot/online-media-skill](https://github.com/grapeot/online-media-skill)（MIT，vendored，commit `794ff6c`，2026-08-14） | 在线媒体处理：下载与 Qwen ASR 转录、medley 歌曲识别、音乐元数据修补、歌源搜索、音乐库去重、双语 SRT 字幕 |
| presentation | [grapeot/presentation_skill](https://github.com/grapeot/presentation_skill)（MIT，vendored，commit `f9881ad`，2026-08-14） | 创建图片生成型或 Reveal.js 演示文稿，支持 deck 规划、视觉规范、演讲者备注与本地预览 |
| image-generation | [grapeot/image-generation-skill](https://github.com/grapeot/image-generation-skill)（public，vendored，commit `5c1b259`，2026-08-14） | 通过统一 CLI 使用 Gemini/OpenAI 进行图片生成、编辑与放大，支持模型、尺寸和多输入控制 |

## 添加新 Skill

1. 将 public repo vendored 到 `skills/<name>/`（保留 README、CLI、tests，不混入私有数据）。
2. 在 `~/.agents/skills/<name>/SKILL.md` 暴露根 skill，私有本地路径写在 overlay 中。
3. 在本索引登记来源、commit 与用途。

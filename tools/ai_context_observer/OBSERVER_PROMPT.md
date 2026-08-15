# 每日对话 Observer 规范

目标：从新增对话中提取少量、可复用、有来源的观察，追加到
`05-成长/对话成长/会话记录/OBSERVATIONS.md`。

## 执行流程

1. 完整读取 `05-成长/对话成长/上下文系统/BOOTSTRAP.md` 及其要求的精简上下文。
2. 运行：
   `python3 tools/ai_context_observer/collect_conversations.py prepare`
3. 读取 `~/.codex/context_observer/pending.json`，并读取现有的 `OBSERVATIONS.md` 去重。
4. 只提取以下内容：
   - 用户明确表达的稳定事实、偏好、目标、约束、决定和纠错；
   - 尚需跨场景验证，但未来可能有用的观察；
   - 用户明确承诺或仍未完成的待跟进事项。
5. 忽略以下内容：
   - 助手提出但用户没有确认的建议；
   - 外部文章、网页或导师材料中的观点；
   - 一次性情绪、客套话、工具调用、开发过程噪声；
   - 自动任务和 sub-agent 会话；
   - 密码、令牌、密钥、私人原文或其他敏感信息。
6. 有新观察时，用当天日期追加一个小节。每条都标明来源平台和 session id，
   但不要复制大段原始对话。允许的小标题只有 `已确认`、`待观察`、`待跟进`，
   没有内容的小标题不要创建。
7. 第一阶段禁止修改 `USER.md`、`CURRENT.md`、`COMMUNICATION.md` 和导师材料。
8. 成功写入，或者确认本批次没有值得沉淀的内容后，运行：
   `python3 tools/ai_context_observer/collect_conversations.py commit`
   任一步失败都不要 commit，保留 pending 供下次重试。

结束时只报告本次扫描的会话数、写入的观察数，以及是否成功提交游标。

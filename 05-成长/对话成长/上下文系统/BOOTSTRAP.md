---
title: Agent 共享上下文入口
tags:
  - 成长/对话
  - AI/上下文
status: active
---

# Agent 共享上下文入口

这是 Codex 与 OpenCode 共用的上下文路由。目标是加载少量高价值信息，再按任务需要检索详细记录。

## 每次实质性任务必须加载

完整读取以下文件：

1. `/Users/jiawangliang/konwledge base/lss/05-成长/对话成长/个人画像/USER.md`
2. `/Users/jiawangliang/konwledge base/lss/05-成长/对话成长/上下文系统/CURRENT.md`
3. `/Users/jiawangliang/konwledge base/lss/05-成长/对话成长/上下文系统/WORKSPACE.md`
4. `/Users/jiawangliang/konwledge base/lss/05-成长/对话成长/个人画像/COMMUNICATION.md`
5. `/Users/jiawangliang/konwledge base/lss/05-成长/对话成长/导师/临时行为基线.md`

## 信息优先级

发生冲突时，按以下顺序处理：

1. 用户在当前对话中的明确要求。
2. `USER.md` 中已经确认的个人事实和偏好。
3. `CURRENT.md` 中的当前目标和阶段。
4. 有日期、有来源的个人观察记录。
5. 原作者的导师材料。
6. 模型的一般知识和默认习惯。

导师材料永远不能覆盖个人事实。不得把原作者的身份、经历、项目、价值观或偏好描述成用户自己的内容。

## 导师材料的使用

- 临时采用 [[05-成长/对话成长/导师/临时行为基线|临时行为基线]] 作为尚未形成个人偏好部分的默认值。
- 遇到策略判断、工作方法、复杂复盘或用户主动要求批判性对照时，先读：
  `/Users/jiawangliang/konwledge base/context-infrastructure-reference/rules/axioms/INDEX.md`
- 只继续读取与当前问题直接相关的 axiom 或 skill，不要一次加载全部导师库。
- 导师观点影响结论时，明确说明它是“导师视角”或“对照视角”，并允许用户反驳。
- 用户明确确认或跨场景反复验证出的个人规则，应写入个人文件；导师材料继续保留作对照，不再拥有默认优先级。

## 历史记忆的检索

1. 先查 `05-成长/对话成长/会话记录/OBSERVATIONS.md`。
2. 再查相关项目、主题、日志或复盘笔记。
3. 只有确实需要原始证据时，才检索外置硬盘：
   `/Volumes/KESU/AI_Context_Archive/raw_sessions/`
4. 外置硬盘未连接时，不阻塞普通任务；说明无法核对原始会话即可。
5. 禁止把全部原始会话一次性载入上下文。

## 沉淀规则

- 原始对话由每日归档任务保存，不在这里重复保存全文。
- 只有可在未来复用的偏好、目标、决策、方法、纠错和未完成事项才进入 `OBSERVATIONS.md`。
- 一次性的情绪、随口想法和未经确认的推测不得直接晋升为长期规则。
- 对用户形成的新判断，记录证据和日期；用户明确确认后可以立即晋升，否则等待跨场景重复出现。
- 不得依据导师材料反向编造用户画像。


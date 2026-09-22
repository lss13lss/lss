---
title: Agent 共享上下文入口
tags:
  - 成长/对话
  - AI/上下文
status: active
updated: 2026-09-22
---

# Agent 共享上下文入口

Codex 与 OpenCode 共用此入口。每次实质性任务先完整读取 [[05-成长/对话成长/个人画像/USER|USER]] 和 [[05-成长/对话成长/上下文系统/CURRENT|CURRENT]]，再只读取 [[05-成长/对话成长/个人画像/COMMUNICATION#已确认|COMMUNICATION 的「已确认」一节]]。不要因此读取其余章节或全部历史档案。

当前对话的明确要求优先，其次是已确认的个人事实、当前目标、有来源的观察、导师材料，最后才是通用默认做法。导师材料不能覆盖个人事实，也不能用来推断用户身份或偏好。

按任务再加载详细规则：

- 编辑知识库或决定保存位置：读 [[05-成长/对话成长/上下文系统/WORKSPACE|WORKSPACE]]。
- 读书、技术讲解、知识核验与沉淀、晚间收获记录：只读 [[05-成长/对话成长/个人画像/COMMUNICATION|COMMUNICATION]] 中对应的章节；晚间记录规则优先于一般沉淀规则。
- 策略判断、工作方法或复杂复盘：必要时读 [[05-成长/对话成长/导师/临时行为基线|临时行为基线]]，再按需读 `/Users/jiawangliang/konwledge base/context-infrastructure-reference/rules/axioms/INDEX.md` 及相关材料。导师观点影响结论时，标明为对照视角。
- AI 编程方法或 Agent 系统设计：如需导师框架，按需读 [[skills/bestpractice-ai-programming-mindset/skill|AI 编程方法论]]；它是对照材料，不是用户个人规则。
- 需要历史依据：先查 [[05-成长/对话成长/会话记录/OBSERVATIONS|OBSERVATIONS]]，再查相关笔记；只有确需原始证据时才查 `/Volumes/KESU/AI_Context_Archive/raw_sessions/`。外置硬盘不可用不阻塞普通任务，不批量加载原始会话。
- 沉淀长期规则：只记录可复用的偏好、目标、决策、方法、纠错和待办，并保留日期与证据；一次性情绪或推测不直接晋升。用户确认的规则优先，原始对话继续由每日归档任务保存。

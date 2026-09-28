---
title: MyContext：开源实现核验与认识修正
created: 2026-09-25
updated: 2026-09-25
tags:
  - AI/Agent
  - AI/记忆
  - 技术/核验
status: verified-snapshot
source: 用户 2026-09-16 至 2026-09-24 口述记录；openTrinity/mycontext 源码快照 23c6f609fb1d392f922e19dae7bee174075a2569
---

# MyContext：开源实现核验与认识修正

## 核心结论

此前对 MyContext 的产品方向把握基本正确：它将工作消息等数据沉淀为个人上下文，供搜索和数字人使用。**需要修正的是把不同的索引、检索和回复路径讲成一条固定流程。**这会影响团队选择 embedding 单位、召回方式以及回复触发策略。

本报告只核验 [[02-主题/AI与LLM/MyContext：口述学习记录|2026-09-16 至 09-24 的口述记录]]中对**开源版实现**的描述。Mio 团队的方案、内部测评及效果由口述记录提供，本次没有团队代码和原始测试数据，不能据此判定其对错。源码证据固定在 [openTrinity/mycontext 的 `23c6f60` 版本](https://github.com/openTrinity/mycontext/tree/23c6f609fb1d392f922e19dae7bee174075a2569)；后续版本可能变化。

## 需要修正的认识

### 1. “阿里把多轮消息拼成 chunk 再 embedding”只适用于图谱链路

[[01-日志/日报/2026-09-24-晚间交流原文#01 MyContext 消息 Embedding 与上下文回拉优化|9 月 24 日的口述]]把多轮 chunk 视为开源版的消息 embedding 做法。源码显示两套单位并存：本地消息向量索引按**单条消息正文**生成向量，跳过过短、空白和 Agent 消息；图谱管线则将同会话的多条消息按会话边界和 token 预算打包成 chunk，再为完整 chunk 建向量。[本地索引](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/packages/ingest/src/local-index.ts#L113-L155)；[会话切块](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/kl-graph/kl_graph/ingest/session_chunker.py#L1-L39)；[图谱向量化](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/kl-graph/kl_graph/ingest/pipeline.py#L1813-L1824)。

同一条口述还说时间和用户信息被剔除；这**不适用于图谱 chunk**。图谱消息渲染会把发送者、会话方向和时间写进正文，供 embedding 和实体抽取使用。[消息渲染源码](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/kl-graph/kl_graph/ingest/loaders/message_loader.py#L37-L45)。本地消息向量索引只取 `contentText`，两者应分开描述。

**对团队方案的影响：**“单条建索引、召回后回拉上下文”和“多条合并建索引”是不同实验条件。前者保留消息级定位，后者让一次向量匹配覆盖较完整的来回对话；应分别测召回相关性、目标消息保留率、索引更新代价和回复质量。

### 2. “人物关系和实体主要由规则归纳、不使用模型”范围过大

[[01-日志/日报/2026-09-16-晚间交流原文#01 MyContext 项目理解|9 月 16 日的口述]]正确注意到回复时延等行为数据可以统计。但图谱实体和事实有明确的**大模型抽取器**；职责、任务、流程等工作画像也有模型抽取实现，不过该部分默认关闭、需启用工作层。统计规则负责活跃时段、回复时延等可计数项。[规则统计](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/packages/distill/src/map/stats.ts#L1-L14)；[实体与事实抽取](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/kl-graph/kl_graph/ingest/llm_extractor.py#L1-L4)；[工作画像抽取](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/packages/distill/src/map/llm-map.ts#L105-L151)；[默认关闭的说明](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/apps/desktop/src/main/services/distill.service.ts#L1-L17)。

建议改写为：**可直接计数的互动行为用规则；需要理解消息含义的实体、事实和工作知识用模型，并回指证据。**

### 3. “私聊或 @ 就一定触发”不是开源版的默认策略

[[01-日志/日报/2026-09-16-晚间交流原文#01 MyContext 项目理解|9 月 16 日]]和[[01-日志/日报/2026-09-22-晚间交流原文#01 MyContext 与 AI suggestion 统一入口及分类模型介入|9 月 22 日]]的叙述容易把团队拟定的入口规则误认为原版规则。开源版中，**未配置的私聊默认不触发**，群聊默认只在 @ 本人时触发；会话可另设“不触发、每条、@、关键词”。[触发源码](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/packages/persona/src/supervisor.ts#L61-L127)。

触发后也不是单靠一个“高／中／低”档位决定发送：草稿、自动发送等模式还受到场景、模型判断、风险、授权、工作时间和频率等条件约束。[回复策略源码](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/packages/persona/src/policy.ts#L201-L220)。团队可以选择“私聊必进入分流”，但应标注为**团队设计**。

### 4. RRF 与图谱检索存在，但并非每次起草的固定前置步骤

[[01-日志/日报/2026-09-16-晚间交流原文#01 MyContext 项目理解|9 月 16 日]]把当前历史、向量/RRF、图谱、分档和生成串成一条流程。图谱问答引擎确实对稠密、关键词和结构扩展结果执行 RRF；但数字人在 Agent 不可用时的直连模型路径，只提供**当前会话内的全文历史召回工具**，并不保证执行图谱检索或 RRF。[图谱 RRF](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/kl-graph/kl_graph/query/engine.py#L821-L872)；[直连起草路径](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/apps/desktop/src/main/services/persona-compose.ts#L247-L293)；[会话隔离](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/apps/desktop/src/main/services/persona-recall-tool.ts#L53-L77)。

建议分别画“搜索/图谱问答”和“数字人起草”两条运行链，再标出 Agent 正常与降级时可调用的工具。

### 5. “本地运行”不等于“所有模型和数据处理都在本地”

[[01-日志/日报/2026-09-18-晚间交流原文#02 MyContext 汇报分歧、云端架构与个人资产思考|9 月 18 日的口述]]提到本地库未加密，这与源码一致：仓库明确说明当前阶段 vault 不加密。[Vault 说明](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/packages/store/src/vault.ts#L1-L15)。但“模型都运行在本地”不能由此推出：消息 embedding 消费者明确区分本地全文索引与**远程 embedding API**；图谱实体抽取也通过配置的模型服务调用。[索引消费者](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/packages/ingest/src/local-index.ts#L1-L15)；[模型抽取器](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/kl-graph/kl_graph/ingest/llm_extractor.py#L1-L35)。

**对上云讨论的影响：**分别核对原始消息、索引/图谱、模型请求内容和回复结果的存放与传输位置。“数据库在本地”不足以判断整个处理链的数据边界。

### 6. “开源”需要注明实际许可

[[01-日志/日报/2026-09-16-晚间交流原文#01 MyContext 项目理解|9 月 16 日]]称项目“开源”，日常交流可这样简称；用于团队复用和上云评估时应写明：仓库使用 **Elastic License 2.0**，README 将其称为“源码可用”，许可文本对向第三方提供托管或管理服务设有限制。[README](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/README.md#L88-L90)；[LICENSE](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/LICENSE#L18-L37)。团队若复用原代码提供云服务，应按实际产品形态核对许可；本报告不判断具体使用是否落入限制。

## 已获支持与仍待验证

- **已获支持：**开源版确有本地 SQLite vault、图谱与 Agent 工具；短时间连续来消息会进入合并窗口，不是必然逐条完整跑一次起草。[本地存储](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/README.md#L43-L57)；[消息合并](https://github.com/openTrinity/mycontext/blob/23c6f609fb1d392f922e19dae7bee174075a2569/packages/persona/src/mailbox.ts#L1-L21)。这回应了[[01-日志/日报/2026-09-16-晚间交流原文#03 MyContext 实践中遇到的坑|9 月 16 日提出的连发问题]]。
- **尚待验证：**“最初是内部项目、做得不错才开源”是来源推测，当前仓库不能证实；“实体出现达到约 5 次就生成蒸馏卡”未从本次核对的源码找到对应的统一规则，可能是团队适配中的设计；“聊天信息一定比文档 RAG 更新、更完整”是需要按数据源和场景实测的假设。它们不应写成开源版已确认机制。

## 下一步用于团队对标

1. 把对标表按**本地消息检索、图谱问答、数字人起草**分列，再填“索引单位、召回范围、证据回指、触发策略、降级行为”。
2. 对团队当前的“问题消息单独被召回”问题，比较消息级索引加上下文回拉、问答对索引、会话 chunk 索引；以同一批真实问题检查答案证据是否完整，而不只看检索命中率。
3. 上云方案单列数据流与许可核对；不要从“本地 vault”或“源码可用”直接推出云端部署结论。

本报告是 **2026-09-25 的源码快照核验**，不是对团队正式架构、线上质量或未来版本的最终评估。

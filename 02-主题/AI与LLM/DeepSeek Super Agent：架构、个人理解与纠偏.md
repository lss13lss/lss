---
title: DeepSeek Super Agent：架构、个人理解与纠偏
aliases:
  - Super-agent 设计探索学习笔记
  - Super Agent 架构与口述纠偏
created: 2026-11-02
updated: 2026-11-02
tags:
  - AI/Agent
  - AI/Harness
  - AI/上下文
  - 学习/理解纠偏
status: researched-with-open-questions
source: 用户本轮口述、官方原型文档、Harness 官方文档；微信公众号正文未能直接访问
related:
  - "[[DeepSeek Harness：亮点、关键机制与成熟度边界]]"
  - "[[Jev 技术与应用调研（2026-09-22）]]"
  - "[[03-项目/工作项目/Agent 记忆与 Harness 优化]]"
  - "[[01-日志/日报/2026-11-02-Super Agent 理解口述原文]]"
---

# DeepSeek Super Agent：架构、个人理解与纠偏

当人在群聊里提出需求、到代码评审里继续讨论、又同时推进其他任务时，系统需要记住每件事交给了谁，把后续信息送到对应执行者，并在有结果或需要决策时找人。Super Agent 的核心是把这些协调动作交给系统，减少用户逐个管理会话的负担。

**Session 仍然存在；Router 负责协调，Worker 负责具体任务，系统通过事件、订阅和持久状态让工作持续推进。统一的是协作对象，不要求所有消息集中在一个窗口或一个上下文里。**

原文副本：[[01-日志/日报/2026-11-02-Super Agent 理解口述原文]]。本篇记录详细架构、用户认识的摘要和助手纠偏，不能反过来作为用户已经独立掌握全部细节的证据。

> [!info] 来源与结论边界
> 用户分享的文章是《Super-agent 设计探索：迈向更自主的 Agent 系统》，[微信公众号链接](https://mp.weixin.qq.com/s/zoS7GlReWPhfCjENGxXCdg)。本次微信正文被验证拦截，官方 X 页面也未能直接读取。
>
> 本篇确认实现行为时以官方仓库为准。仓库明确说明：公开原型与内部版本、文章实现不完全一致，部分文章设计尚未实现。对文章设想的解释、对原型的核验、助手的推论分别标注；实验数值暂按用户提供的材料留档，未升级为已核验结果。[官方 README](https://github.com/deepseek-ai/dsh-superagent-prototype)

## 一、先沿着一项任务看它怎样运行

以下“修复登录报错”是助手构造的解释例子，不是实际运行记录。

1. 用户在群聊提出修复请求。接入程序把消息转成事件，并记录它来自哪个话题、能够向哪里回复。
2. 系统检查来源与工作规则，需要时由主 Session 判断是否接受，并建立一项有明确范围的任务。
3. 任务交给一个 Worker。Worker 在自己的 Session 和工作目录中检查代码、复现与验证。
4. 主 Session 不持续等待这项任务结束，可以继续处理其他候选事件和反馈。
5. 用户在原话题补充“只有安卓端出错”。订阅关系把消息送到负责该任务的 Worker。
6. Worker 创建 PR 后，相关评审与 CI 结果可以继续成为任务输入。程序按关联与订阅投递，Worker 决定下一步。
7. 任务有可审阅结果、缺少资源或需要人决策时，向合适的渠道反馈。一次回复、一次工具结束或一次模型轮次结束，都不自动等于任务永久结束。

这条链依赖系统保存的任务状态和关系，不只是模型记住了一段对话。[官方概念模型](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/001-domain.md)；[执行与恢复](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/003-execution.md)

## 二、设计动机：减少协调成本，Session 退到后台

**用户当时的理解（助手摘要）：** 模型能力已经很强，但上下文依赖单个 Session；跨 Session 同步困难，工程师频繁切换项目背景和等待任务，拖慢工作。通过统一 Session 分派任务，避免前台阻塞。原话见 [[01-日志/日报/2026-11-02-Super Agent 理解口述原文#02 设计初衷与统一分派]]。

**成立的部分：** 用户抓住了人的注意力成本，以及分派之后继续接收其他信息的意义。

**需要收窄的部分：** “无法跨 Session 同步”过于绝对。文件、检索、记忆和消息传递都能帮助跨会话共享；难点是由谁判断该送什么、送给谁，以及何时找人。很多传统工作方式把这些判断留给用户。

协调成本不仅是等待，还包括补背景、检查进度、转交结果、恢复中断任务和处理冲突。因此，把它说成“消除工程师导致的等待”不够准确，也不应把系统问题归责给工程师。

**纠偏后的表达：** 模型的单任务能力提高后，多任务工作的瓶颈可能转向人的协调能力。Super Agent 让系统接管更多会话与任务管理，但没有取消会话，也没有证明模型能力已不再重要。[官方设计原则](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/000-philosophy.md)

## 三、Router、Worker、Thread 与 Session 各自负责什么

### 3.1 两层分工成立，但没有一个共享全部细节的巨大上下文

**用户当时的理解（助手摘要）：** Router 实现共享上下文并分派 Worker；Worker 是上下文隔离的独立 Session，可以订阅 Thread、自主执行、再向 Router 汇报，也可以创建 Subagent。原话见 [[01-日志/日报/2026-11-02-Super Agent 理解口述原文#03 Router、Worker 与独立 Session]]。

这个骨架成立。需要把“共享上下文”改成更具体的分工：Router 持有协调所需的信息，Worker 持有具体任务所需的信息。信息可以被传递、查询和引用，但不会自动复制所有 Worker 的完整执行历史。

例如，Router 需要知道“登录修复正在进行、文档更新在等待接口决定”，不必持续读取全部测试日志。确实有关联时，再发送事实说明或查询原始记录。上下文隔离也不等于操作系统权限隔离，后者需要独立设计。[官方提示词与协作规则](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/004-prompts.md)

### 3.2 区分外部消息话题、业务任务与模型会话

| 对象 | 在这套系统里的含义 |
|---|---|
| Source | 产生事件的来源；公开原型主要是 GitHub 与可选飞书。 |
| Trigger | 一次收到的事件，例如请求、补充消息或 CI 变化。 |
| Thread | 来源定义的一组有序事件，例如一个 PR 或群聊话题。 |
| Ticket | 一项获准开展的工作，保存范围、输入和生命周期。 |
| Subscription | Ticket 与 Thread 的订阅关系，让后续事件进入对应工作。 |
| Assignment | 某项任务与一次执行者实例的绑定。 |
| Session | 承载模型交互、工具调用和会话历史的运行对象。 |
| Channel | 回复的目标和写入渠道。 |

严格说，公开原型的订阅关系连接 Ticket 与 Thread，再把输入交给执行者。一个 Thread 可以关联多个 Ticket，一个 Ticket 也可以订阅多个 Thread；不能固定理解成一个话题等于一个 Worker。

Ticket 的状态独立于 Session。保留这层任务对象，才能表达换执行者、继续讨论、等待人决定等情况，而不是把“模型停止生成”当作“工作结束”。[官方概念定义](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/001-domain.md)

### 3.3 Worker 与 Subagent 的差别要看职责和生命周期

Worker 能创建 Subagent，这一点有官方执行文档支持。但普通 Subagent 也可能有独立上下文或 Session，因此不能用“独立 Session”作为两者唯一差异。

在本系统里，Worker 承接一个持续存在的任务，接收后续事件并报告结果；它创建的 Subagent 可以进一步负责局部工作。关键是上下层由谁管理任务、接收哪些事件、在什么条件下继续或结束。[官方执行文档](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/003-execution.md#the-executor)

## 四、事件驱动：筛选与直通是两组机制

**用户当时的理解（助手摘要）：** 多来源消息先过程序规则，再过模型筛选；把这两轮理解为 Fast／Slow Path，并猜测后续消息继续经过相同过程。原话见 [[01-日志/日报/2026-11-02-Super Agent 理解口述原文#04 事件筛选、上下文组织与提前行动]]。

### 4.1 两层筛选决定是否开展工作

程序层处理能明确判断的条件，例如监听范围、来源身份和工作策略；模型层再判断语义、任务相关性和是否需要行动。

这不等于“过滤掉所有机器人消息”。CI、评审机器人和其他系统通知可以是重要输入；系统自己的输出通常需要排除，防止自我触发。具体条件由来源与策略决定，不是关键词过滤就足够。

“模型筛选之后再交给 Router”也可能多画了一层：公开原型的主 Session 本身就承担候选研判，不必假设旁边还有一个独立模型筛选器。[官方概念文档](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/001-domain.md)；[授权策略](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/002-authorization.md)

### 4.2 快慢路径决定是否还需重新判断接收者

为了理解文章思路，可以先用以下简化模型：

- **Fast Path：** 已有明确订阅或关联，程序把事件交给已负责的任务。
- **Slow Path：** 尚需判断是否建立任务、关联哪项工作或忽略，再经过模型研判。

例如首次提出登录故障，需要判断与派工；随后同话题补充设备信息，可以按订阅直达已有任务。它减少的是重复路由开销，不是取消 Worker 对新信息的理解。

> [!note] 公开原型比二分示意更细
> 已经通过订阅送达 Ticket 的人类消息通常不再进入新的 Eval；其他事件仍可能进入 Eval。因此“所有已订阅事件都永不经过 Router”不能当作原型的完整规则。后续消息超出任务范围时，Worker 也有交回机制。[官方实现说明](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/007-architecture.md#engine)

文字流程：新事件进入系统后，一部分按已有订阅送入任务，一部分需要评估是否产生新工作。两者可以由程序按事件类型分别处理，不能把模型筛选与订阅直通混成同一条两级流水线。

## 五、上下文：Inline、Spill 与沿 ID 读取分别解决什么

**用户当时的理解（助手摘要）：** 把 Inline／“split”类比为 Skill 渐进式加载，通过统一 ID 找 Thread，再逐层读取详情。原话同见 [[01-日志/日报/2026-11-02-Super Agent 理解口述原文#04 事件筛选、上下文组织与提前行动]]。

### 5.1 Inline 是当前直接可见，Spill 是完整内容保存在外部

术语应为 **Inline 与 Spill**，原文副本不修改用户的“split”。

- Inline 可以是一条完整短消息、摘要、任务指令或资料预览，直接进入当前上下文。
- Spill 把长内容保存到当前窗口之外，在窗口里留下预览、地址及读取说明。

示例：一万行测试日志无需每轮完整输入，当前只保留失败摘要和文件地址；需要定位错误时，再读取相关片段。外部可取回不等于模型当下已经知道全部内容，也不保证检索一定成功。

“先少量信息、再按需展开”与 Skill 渐进式加载相似；但 Inline 本身不是索引的同义词，Spill 也不是把所有信息自动转成长期记忆。[Harness 官方 Spill 文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/spill.md)

### 5.2 沿 ID 查找解决的是关联定位

公开原型提供任务、Thread、Trigger、执行报告等资源接口，可以从任务找到相关话题，再定位消息或执行记录。

例如当前提示只放“任务 T 正在处理 PR 42，详情见 Thread X”。模型需要核对评审意见时，再读取 X。**Inline／Spill 管当前放多少；关联引用管去哪里找。** 两者配合，但不是同一个概念。[官方读取接口](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/007-architecture.md#read-resources)

## 六、主动执行：可以提前准备，也可以主动交付

**用户当时的理解（助手摘要）：** 系统观察多个数据源，发现潜在需求并提前运行，等用户来问时已经有结果。

这一理解成立，但只覆盖一种结果：预先准备也可以在产生可用结果时主动通知，而不是必须等待用户来问。比如发现疑似故障，先做有限复现；有可靠结果时交付，无价值时结束。

没有本次显式 @ 不等于没有工作边界。公开原型要求未被直接请求的工作有书面规则作为依据，并提供先记录拟执行行为的模式。不能把“后台观察信息”推导成“可以任意修改、发布和承诺”。[官方原则](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/000-philosophy.md)

这里对“投机执行”的解释是提前付出一定计算成本以减少以后等待。它不是对每次猜测都成功的保证，也不要求每个任务都提前执行多个分支。本次未核验文章中每项投机执行设计是否已经落到公开代码。

## 七、面向人的交互：多个渠道、持续接话、按角色加载能力

### 7.1 统一协作对象不等于唯一聊天窗口

**用户留下的疑问（助手摘要）：** 所有回复是否都集中在一个 Session？这个 Session 如何加载上下文、Skills、Tools 和 Memory？原话见 [[01-日志/日报/2026-11-02-Super Agent 理解口述原文#05 面向人的交互与上下文加载疑问]]。

可以在群聊提出任务，再到 GitHub PR 下讨论细节，系统通过任务关系保持连续性。群里适合简短说明，PR 里适合结构化交付与验证记录。回复位置由对应渠道决定，用户不必跳到唯一窗口才能继续工作。

“Router 统一协调输出”是职责层面的理解，不能推出“实现里只有 Router 能调用回复工具”。公开原型也给执行者提供受约束的回复能力，部分需要人的问题则通过报告转交主 Session。[官方提示词和交接规则](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/004-prompts.md)

### 7.2 异步 ReAct 使后台等待与前台交互解耦

概念上的同步过程是：模型启动长操作，然后一直等到工具返回才继续。异步过程则可以是：

```text
发起后台操作 → 收到已启动状态 → 继续处理消息
后台操作完成 → 结果成为新事件 → 继续对应工作
```

`Started` 只表示操作已启动，不表示工作完成，也不等于每次接单都必须给用户发一条状态消息。`stop()` 表达终止后台操作的能力。

Router／Worker 是分工；工具异步是执行机制。两层都可以有各自的思考、工具调用与观察循环，不能简单说成“两个异步机制”，也不应把分层称为必须同步等待的嵌套。

公开原型提供了更具体的运行规则：Router 与 Worker 的前台命令和任务等待设有短时限，耗时命令转后台，完成结果再唤醒处理。新消息一般仍需等当前步骤结束，不代表能任意打断正在进行的模型计算。文章转述中的“异步功能已存在但默认关闭”本次未取得原文逐字复核，不能拿它代替原型配置说明。[官方执行规则](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/003-execution.md#background-work-and-worker-slots)

### 7.3 能力装配与内容检索分开理解

| 内容 | 由谁提供、怎样使用 |
|---|---|
| 当前上下文 | 每个 Session 按角色、任务和到达事件组成，必要时查询其他记录。 |
| 系统提示词 | 共享规则加角色说明；主 Session 和执行者装配不同部分。 |
| Tools | Harness 和原型按角色注册与约束，决定可以执行哪些动作。 |
| Skills | 操作方法和领域知识，按需要读取；不必全部装入每个任务。 |
| 持久状态 | 保存消息、任务、订阅、报告及配置，支持后续查找和恢复。 |
| 长期记忆 | 还涉及提炼、更新、检索与失效处理，不能仅因数据库有记录就认定已解决。 |

公开原型的执行者还会读取编码指令与仓库 `AGENTS.md`，主 Session 的职责与输入不同。这里要分别问“模型可以做什么”“模型现在知道什么”“系统还保存了什么”。[官方提示词装配](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/004-prompts.md#assembly-and-precedence)

## 八、计算、状态与执行环境分离

用户明确表示未细看、没有理解这一部分；下面是助手补充的概念说明，不写成用户已掌握的内容。原话见 [[01-日志/日报/2026-11-02-Super Agent 理解口述原文#06 计算、状态、环境与 Router 批处理疑问]]。

| 部分 | 回答的问题 |
|---|---|
| 计算 | 谁运行 Agent 循环、调用模型并决定下一步？ |
| 状态 | 消息、进度、订阅、执行结果保存在哪里？ |
| 执行环境 | 到哪台机器读文件、修改代码、运行测试？ |

三者不必固定在同一台设备。按照文章讨论方向，可设想云端运行循环并保存状态，本地轻量 daemon 接受命令、执行并返回结果。模型推理服务本身在哪里，也不必与 Agent 循环部署位置完全一致。

这种分离使“关闭聊天界面”不必等于“所有任务消失”。但是本地电脑离线后，必须依赖它的动作仍然不能执行。其他可运行的工作或状态管理可以继续，依赖该环境的部分等待恢复；不能表述成“电脑关机后本地测试照跑”。

这是对设计思路的解释。公开原型的 README 明确保留未实现设计；本次没有把完整 BYOM 云端部署作为已验证功能。旧 Harness 笔记中的执行环境 Provider 解耦可作为背景，但属于较早调研，不能直接证明此原型已完成全部远程部署能力。参见 [[DeepSeek Harness：亮点、关键机制与成熟度边界#5. Capability Seams 解耦 Provider 与 Agent Loop]]。

## 九、Watchdog 从系统外检查与恢复

用户明确表示未阅读此部分，以下为助手补充。

如果主进程挂起，它可能无法再调用任何工具，也就不能可靠地发现并修复自己。因此需要另一个独立检查者定时查看健康状况，根据结果恢复或报告。

```text
独立检查者 → 查看状态
正常 → 保持安静
运行异常 → 检查诊断信息，尝试恢复
配置缺失或需要人介入 → 提出具体问题
人工主动停止 → 尊重停止，不自动拉起
```

官方部署文档提供了在另一个 Harness profile 中设置定时检查的方案：状态不同，动作也不同，不能遇到任何错误就无限重启。公开方案主要证明运行健康检查与恢复路径，不等于存在能保证代码质量或任务正确性的万能监督者。[官方定时检查方案](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/006-deployment.md#hourly-check)

## 十、Router 批处理、Worker 并发和 Jev 类比

### 10.1 一次处理多条候选是批处理

**用户当时的理解（助手摘要）：** 多个 Trigger 到来时可以共用 Router 上下文，一次判断并输出多个结果，相当于并行处理，类似“GEV”。原话见 [[01-日志/日报/2026-11-02-Super Agent 理解口述原文#06 计算、状态、环境与 Router 批处理疑问]]。

“一次收多条、一次出多个决定”这部分成立。官方原型支持一个路由工具调用提交多个候选的决策；但必须分清以下几种情况：

```text
逐条调用：一次模型请求判断 A，再一次判断 B，再一次判断 C。
批量判断：一次模型请求看到 A、B、C，输出各自的决定。
并发请求：同时发出多个独立模型请求，各自处理输入。
并发执行：派工之后，多个 Worker 各自推进任务。
```

共享上下文与调用开销可能降低每条事件的平均成本，但不证明一次请求内部有多个独立推理过程，也不保证没有排队或所有负载下都低延迟。批次大小、输入长度、推理时长和到达速率仍会影响等待。[官方主 Session 接口](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/007-architecture.md#main-session-tools)

### 10.2 回查旧笔记后，“GEV”可接回 Jev

本轮口头纠偏时，助手曾说不确定“GEV”指什么。入库时回查 [[Jev 技术与应用调研（2026-09-22）#2. 为什么快：省去逐词生成，并合并同一份材料上的判断]] 与 [[GEV 模型与轻量路由：口述学习记录]]，发现旧记录已将这一称呼对应到 TypeSafe 的 Jev。这里补上关联；原话副本保留“GEV”。

TypeSafe 的官方文档支持一次请求提交多个问题，并称各问题并行评估，随后由代码决定使用哪些结果。本轮重新打开该文档核对了这一接口主张。[TypeSafe fan-out](https://docs.typesafe.ai/patterns/fan-out)

**类比成立之处：** 都可以把多项判断合在一次请求里，减少反复调用。

**不能等同之处：** Router 批处理是应用如何组织输入与输出；Jev 的并行评估是特定服务的接口与实现主张。前者不能证明使用了 Jev，也不能证明所有答案彼此隔离，或共享一次内部编码。旧笔记也明确保留了 Jev 闭源结构未公开的边界。

### 10.3 实验数字单独留档，不混入已核验结论

下表来自用户本轮粘贴的另一段解读，**未逐字核对文章原始实验表，也未复现**。保留是为了不丢失讨论材料，不作为独立测评。

| 方案 | p50／p95 完成时长 | 缓存读取 token |
|---|---|---|
| Super-agent | 12.4／15.7 分钟 | 23.2M |
| 去掉直通 | 12.6／15.5 分钟 | 31.8M |
| 单 Session＋Subagent | 20.4／29.5 分钟 | 6.1M |

同一份粘贴材料另称：优先委派提示下 p95 为 29.0 分钟；去掉直通后决策数约增 30%；批处理把摊销推理时间从 6.4 秒降到 1.6 秒；到达率从每分钟 1 条增到 40 条时，请求耗时从 2.5 秒变成 3.9 秒。这些数字的样本、统计口径和原始表仍待核对，不推导吞吐保证。

即便暂时接受表格数值，推论仍需限定：

1. `23.2 ÷ 6.1 ≈ 3.8` 比较的是缓存读取 token，不是总 token 或费用。
2. `31.8 ÷ 23.2 − 1 ≈ 37%` 同样只针对缓存读取这一列。
3. 这次有无直通的延迟接近，不等于直通在任何负载下都不省时间。
4. p95 更低不能证明“没有长尾”。
5. 粘贴材料描述的是约 300 条消息、约 20 项工作的合成负载及简化执行环境。即使原文确认这些设置，也应只用于对应编排机制的分析，不能直接推广为真实编码质量优势。

## 十一、对本轮粘贴解读的审计

以下句子来自用户用于比较的另一段解读，**不视为用户本人已认可的立场**。

| 解读中的论断 | 本轮纠偏 |
|---|---|
| Router 不配 Bash 是硬约束 | 不能用于概括公开原型。当前文档列有 `bash`、`read` 等工具；避免读代码属于提示词规则，等待时限另有程序限制。 |
| 两个 ReAct 是嵌套关系 | 层级职责与异步执行分开理解，避免暗示 Router 必须同步等待 Worker。 |
| 四倍 token 换稳定且没有长尾的延迟 | 混淆缓存读取与总成本，也扩大了 p95 的统计含义。 |
| 静默执行导致没有归因链 | 不发通知不等于不留记录；原型持久化事件、决策、任务、输入与回执。是否足够审计仍需具体检查。 |
| 云端被注入就等于拿到所有设备凭证 | 影响范围取决于实际连接、进程权限与隔离，不能无条件扩大到所有设备。 |
| Agent 的主要矛盾已不在模型而在系统 | 可作为解读者判断；更稳妥的是多任务协调成为突出瓶颈之一。 |
| Router 不分片就必然是瓶颈，分片就必然割裂全局上下文 | 是值得研究的扩展权衡，不是由这组实验已证明的二选一结论。 |

Bash、等待守卫与持久记录可核对[官方架构文档](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/007-architecture.md)。权限文档明确说明两个预设以运行进程的系统用户权限执行，凭证包装器不构成隔离；Worker 能读取该用户主目录。[官方权限说明](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/006-deployment.md#permissions-and-isolation)

“上线一天近 4000 star”等传播数字未核对，且不影响架构理解，不作为成熟度证据。邮件、日历、文档等属于本轮讨论的广义来源设想；不能据此声称公开原型已经提供全部接入。

## 十二、与已有知识的连接及本轮认识变化

### 12.1 与 Harness 运行时笔记的关系

[[DeepSeek Harness：亮点、关键机制与成熟度边界#3. Turn / Step 构成可拦截的任务闭环]] 解释单个执行循环；本篇解释如何在其上组织持续任务和多来源事件。

[[DeepSeek Harness：亮点、关键机制与成熟度边界#4. 追加式 SessionEvent 是模型上下文的事实源]] 解释历史记录与当前上下文投影的区别；本篇进一步区分 Session 历史、Ticket 业务状态、外部 Thread 与当前输入。旧笔记的版本和成熟度判断属于其历史调研日期，未在本轮全部复查。

### 12.2 与 MyContext 和记忆调研的关系

相关项目入口为 [[03-项目/工作项目/MyContext 适配与检索优化]] 与 [[03-项目/工作项目/Agent 记忆与 Harness 优化]]。

助手提出的关联是：检索到相关信息之后，还需要决定它属于哪个进行中的任务、何时投递以及何时触发行动。这是从上下文检索向持续执行衔接的问题。**这里只记录研究联系，不代表用户决定把 MyContext 改造成 Super Agent，也不代表已经开始实现。**

### 12.3 本轮认识变化与证据身份

1. 用户先独立描述五段理解，要求助手等“结束”后再纠偏；助手按约定等待。
2. 用户已经抓住：注意力成本、Router／Worker 分工、Worker 独立上下文、持续事件输入和后台执行。
3. 主要纠偏：Session 没有取消；上下文协调不等于全部共享；两层筛选不等于快慢路径；Inline 不等于索引；批处理不等于并行推理。
4. 主要补充：多渠道交互、按角色加载能力、任务状态与会话状态分离、计算与环境分离、外部健康检查。
5. 入库时新增交叉验证：从旧 Jev 笔记补回“GEV”的上下文，并区分类比与机制等同。
6. 用户授权保存两份文档；**授权保存不视为逐项确认助手的所有技术判断**。后续若有修正，在本篇更新结论并保留依据，不回写原文。

## 十三、仍待核验的问题与来源索引

- 微信文章的完整正文、发布日期和实验原表，本次没有直接取得。
- 文中“异步任务默认未开启”的准确版本范围，以及它与公开原型预设的关系。
- 计算、状态与本地 daemon 分离的完整部署方案，哪些是内部实现、哪些是方向设想。
- 多任务长时间运行的真实质量、成本、恢复表现，不能由本轮阅读代替实测。
- 统一协调层在更大规模下的路由准确率、排队延迟和上下文预算。

主要来源（访问与整理日期：2026-11-02）：

1. [用户提供的微信公众号文章](https://mp.weixin.qq.com/s/zoS7GlReWPhfCjENGxXCdg)：访问受限，只保留入口。
2. [官方原型 README](https://github.com/deepseek-ai/dsh-superagent-prototype)：研究定位及实现差异。
3. [000 Philosophy](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/000-philosophy.md)：注意力、主动工作与沟通原则。
4. [001 Domain](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/001-domain.md)：Source、Trigger、Thread、Ticket、订阅与渠道。
5. [003 Execution](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/003-execution.md)：执行者、后台工作、并发与恢复。
6. [004 Prompts](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/004-prompts.md)：角色提示词、Skills、协作与输出。
7. [006 Deployment](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/006-deployment.md)：权限边界、启动、停止和外部检查。
8. [007 Architecture](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/main/docs/007-architecture.md)：事件处理、工具、读取接口与持久化。
9. [Harness Spill](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/spill.md)：内容外置、预览和可读取地址。
10. [TypeSafe fan-out](https://docs.typesafe.ai/patterns/fan-out)：一次请求中的多问题评估，仅用于 Jev 类比核对。

原型仓库入库时查询到的 `main` 提交为 `6337fc823ce20251c8de8085948165c81aaa701e`。可用[该提交的文档目录](https://github.com/deepseek-ai/dsh-superagent-prototype/tree/6337fc823ce20251c8de8085948165c81aaa701e/docs)回查快照；本次是阅读与文档整理，没有部署原型或复现性能实验。

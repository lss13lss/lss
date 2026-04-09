---
tags: [learning]
title: A2A和多Agent协作功能说明文档
created: '2025-07-09T01:15:04.965Z'
modified: '2025-07-21T10:02:49.913Z'
---

# A2A和多Agent协作功能说明文档

## 1. 概述与定义

### 1.1 A2A协议定义

Agent2Agent (A2A) 是由谷歌于2025年4月推出的首个标准智能体交互协议，旨在打破系统孤岛，使不同AI Agent能够相互"加好友"，提升智能体的跨平台能力和执行效率。A2A提供了一种标准的交互方式，使Agent能够在动态的多Agent生态系统中协作，即使它们由不同的供应商或框架构建，也能相互操作。

### 1.2 多Agent协作系统定义

多Agent系统(MAS)是指多个自主AI代理协同工作，以解决单个模型难以处理的复杂任务。每个代理都可以利用工具（API、数据库）和内存来实现子目标，通过标准化通信方式相互协作。

## 2. A2A协议架构与原理

A2A协议的核心架构基于HTTP和JSON-RPC风格接口，包含以下关键模块：

### 2.1 Agent Card

- 位于`/.well-known/agent.json`，是JSON格式的代理能力说明书
- 包含API端点、技能、认证方式等信息，为能力发现、自动集成提供基础
- 支持智能体自治与动态编排，允许客户端代理识别并利用最佳代理

### 2.2 角色模型

- **服务端**：提供API接口（必须实现`tasks/send`等标准方法），处理任务请求，管理任务状态，推送结果
- **客户端**：作为任务发起方，发现目标Agent能力，构造并发送任务请求，消费结果

### 2.3 任务流程

- 定义了任务的生命周期，状态流转为 `submitted` → `working` → `(input-required)` → `completed/failed`
- 交互单元包括由多类型Part（文本/文件/结构化数据）组成的消息和任务产出的结构化结果（工件）

### 2.4 通信机制

- 基础模式采用HTTP + JSON-RPC风格接口
- 高级功能支持实时推送（SSE协议，`tasks/sendSubscribe`）和异步通知（Webhook回调）
- 通过Part类型实现多模态支持，代理间可预先协商交互形式（如文本/语音/表单）

![A2A通信流程](/usr/local/app/workspace/plan_21ff01474d1ce59618f6ed6d8ded3097/stage_3/a2a_communication_flow.png)

## 3. A2A功能与设计原则

### 3.1 核心功能

- **安全协作**：代理之间可以安全地发送消息，传达上下文、回复、工件或用户指令
- **任务管理**：客户端与远程代理之间的通信以任务完成为导向，任务具有生命周期，代理可以同步任务状态
- **用户体验协商**：消息包含"部分"（内容片段），允许客户端和远程代理协商所需格式
- **能力发现**：代理使用JSON格式的"代理卡"宣传其能力，允许客户端代理识别并利用最佳代理

### 3.2 设计原则

- **拥抱代理能力**：使代理能够以自然、非结构化的模式协作，即使不共享内存、工具和上下文
- **基于现有标准**：建立在HTTP、SSE、JSON-RPC等现有流行标准之上，易于与现有IT堆栈集成
- **默认安全**：支持企业级身份验证和授权，与OpenAPI的身份验证方案相同
- **支持长时间运行的任务**：灵活支持从快速任务到需要数小时甚至数天的深度研究任务
- **与模态无关**：支持各种模态，包括音频和视频流

### 3.3 A2A与MCP的关系

- **MCP（模型上下文协议）**：连接LLM与数据、资源和工具的标准，专注于标准化不同模型和框架之间的"函数调用"
- **A2A**：应用层协议，使代理能够以代理（或用户）身份进行通信，而不是以工具身份
- **关系**：A2A被设计为MCP的补充。建议工具使用MCP，代理使用A2A。MCP用于本地信任连接，A2A是代理之间对话的协议

## 4. A2A协议接口与实现

### 4.1 核心接口

A2A协议定义了以下关键接口和方法：

- **`tasks/send`**：同步发送任务，返回最终任务状态
- **`tasks/sendSubscribe`**：流式发送任务（Server-Sent Events），流式推送任务更新
- **`tasks/get`**：查询任务状态，返回任务对象
- **`tasks/cancel`**：取消任务，返回更新后的任务对象
- **`/.well-known/agent.json`**：（HTTP GET）发现Agent信息，返回Agent卡片（能力描述）

### 4.2 JSON-RPC示例

**请求示例 (`tasks/send`)**：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tasks/send",
  "params": {
    "id": "de38c76d-d54c-436c-8b9f-4c2703648d64",
    "message": {
      "role": "user",
      "data": [{ "type": "text", "text": "tell me a joke" }]
    },
    "metadata": {}
  }
}
```

**响应示例**：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "id": "de38c76d-d54c-436c-8b9f-4c2703648d64",
    "sessionId": "c295ea44-7543-4f78-b524-7a38915ad6e4",
    "status": { "state": "completed" },
    "artifacts": [{ "name": "joke", "parts": [{ "type": "text", "text": "Why did the chicken cross the road? To get to the other side!" }] }],
    "metadata": {}
  }
}
```

### 4.3 Python实现示例

#### 4.3.1 基本回声Agent服务器

```python
from python_a2a import A2AServer, Message, TextContent, MessageRole, run_server

class EchoAgent(A2AServer):
    def handle_message(self, message):
        if message.content.type == "text":
            return Message(
                content=TextContent(text=f"Echo: {message.content.text}"),
                role=MessageRole.AGENT,
                parent_message_id=message.message_id,
                conversation_id=message.conversation_id
            )

if __name__ == "__main__":
    agent = EchoAgent()
    run_server(agent, host="0.0.0.0", port=5000)
```

#### 4.3.2 客户端调用示例

```python
from python_a2a import A2AClient, Message, TextContent, MessageRole

client = A2AClient("http://localhost:5000/a2a")
message = Message(
    content=TextContent(text="Hello, is this thing on?"),
    role=MessageRole.USER
)
response = client.send_message(message)
print(f"Agent says: {response.content.text}")
```

## 5. 多Agent协作系统

### 5.1 多Agent系统优势

- **专业化**：代理可以专注于特定子任务
- **可扩展性**：可以通过添加或移除代理来扩展系统
- **可解释性与鲁棒性**：相较于单一模型，MAS具有更好的可解释性和鲁棒性
- **任务分解**：能够将复杂工作流分解为更小、更易管理的单元
- **容错性**：如果一个代理出现问题，其他代理可以继续工作
- **资源优化**：根据需要分配计算资源，提高系统整体效率
- **更快的创新和集成**：新的专业代理可以独立开发并集成，无需重新训练整个模型
- **增强协作**：不同领域的专家可以协作解决复杂问题

### 5.2 多Agent协作系统架构模式

多Agent协作系统通常采用以下架构模式：

![多Agent协作系统架构模式](/usr/local/app/workspace/plan_21ff01474d1ce59618f6ed6d8ded3097/stage_3/multi_agent_patterns.png)

#### 5.2.1 主从模式 (Master-Slave Pattern)
- **描述**: 一个主Agent负责任务分解和结果整合，多个从Agent执行专门任务
- **优势**: 集中控制、责任明确、易于管理
- **适用场景**: 可明确分解的复杂任务，如文档处理、多维度分析

#### 5.2.2 对等网络模式 (Peer-to-Peer Pattern)
- **描述**: 所有Agent地位平等，直接相互通信，没有中央控制点
- **优势**: 高度自治、无单点故障、可扩展性强
- **适用场景**: 分布式问题解决、创意协作、去中心化应用

#### 5.2.3 专家团队模式 (Expert Team Pattern)
- **描述**: 不同领域专家Agent组成团队，各自负责自己擅长的领域
- **优势**: 专业化分工、高质量输出、适应复杂问题
- **适用场景**: 跨领域问题、需要多专业知识的任务

#### 5.2.4 工作流模式 (Workflow Pattern)
- **描述**: Agent按预定义的工作流顺序协作，前一个Agent的输出是下一个的输入
- **优势**: 流程清晰、可追踪、可预测
- **适用场景**: 标准化业务流程、顺序依赖性强的任务

#### 5.2.5 黑板模式 (Blackboard Pattern)
- **描述**: 多个Agent围绕共享的"黑板"(数据空间)工作，各自贡献解决方案
- **优势**: 灵活协作、增量解决问题、适合复杂问题
- **适用场景**: 复杂问题分析、创新解决方案生成、模式识别

## 6. 应用场景

### 6.1 企业应用

- **企业流程自动化**：不同职能的AI代理协同完成端到端的自动化流程
- **IT服务管理**：员工请求新笔记本电脑时，Agent与负责库存检查、采购审批和设备配置的其他Agent交互
- **供应链管理**：多个Agent分别负责需求预测、库存优化、物流调度和供应商沟通，协同优化供应链
- **客户支持增强**：一线客服Agent将无法解答的专业问题转交给具备相关知识的二线专家Agent
- **企业通信与协同办公**：实现跨部门AI代理的协同，如销售AI通知客服AI跟进客户技术问题

### 6.2 垂直领域应用

- **金融服务**：投资咨询系统（金融数据分析、研究、预测、投资建议）
- **零售运营**：需求预测、库存分配、供应链协调、定价优化
- **社交媒体营销**：内容策略师、参与度预测器
- **个性化旅行规划**：结合LLM推理和外部数据源创建自适应行程
- **自主云运维**：监控代理感知延迟峰值，扩展代理响应
- **医疗健康**：多Agent系统协作诊断、治疗方案制定、医疗记录管理

### 6.3 新兴应用

- **机器人群**：
  - **搜索与救援**：在灾难响应中，机器人群快速覆盖大面积区域，定位幸存者并传输实时数据
  - **农业与精准农业**：用于自动化、高精度农业任务，如监测土壤健康、检测植物病害、优化灌溉
  - **太空探索**：群体机器人用于行星探索，自主机器人可以收集样本、绘制地形图并进行实验
- **个人助理智能化**：用户的个人助理Agent将特定任务委托给更专业的外部Agent
- **个性化学习**：学习平台由多个Agent组成，通过A2A协作为用户提供定制化的学习体验
- **研究系统**：使用多个AI代理探索复杂主题，一个代理规划研究过程，然后创建并行代理同时搜索信息

## 7. 发展趋势

- **Agentic AI的普及**：AI代理将变得更加自主，能够规划、行动并适应动态输入，实现目标驱动的决策
- **标准化与互操作性**：A2A等协议的出现将推动AI代理之间的标准化通信，打破不同平台和框架之间的壁垒
- **复杂任务处理能力增强**：多Agent系统将能够处理更复杂、多步骤的任务，通过代理间的专业化和协作提高效率和准确性
- **人机协作的深化**：人类将更多地参与到多Agent系统的决策支持和结果评估中，实现更高效的人机协作
- **垂直领域应用拓展**：多Agent系统将在更多垂直领域（如医疗、金融、制造、农业等）实现落地应用，推动行业智能化转型

## 参考文献

- [1] Google Developers Blog. (2025, April 9). *Announcing the Agent2Agent Protocol (A2A)*. Retrieved from https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/
- [2] Linux Foundation. (2025, June 23). *Linux Foundation Launches the Agent2Agent Protocol Project*. Retrieved from https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents
- [3] AWS. (2024, December 3). *Introducing multi-agent collaboration capability for Amazon Bedrock*. Retrieved from https://aws.amazon.com/blogs/aws/introducing-multi-agent-collaboration-capability-for-amazon-bedrock/
- [4] Solo.io. (n.d.). *What Is Agent2Agent Protocol (A2A)?*. Retrieved from https://www.solo.io/topics/ai/what-is-a2a
- [5] Anthropic. (2025, June 13). *How we built our multi-agent research system*. Retrieved from https://www.anthropic.com/engineering/built-multi-agent-research-system
- [6] GitHub. (n.d.). *a2aproject/A2A: An open protocol enabling communication...*. Retrieved from https://github.com/a2aproject/A2A
- [7] Google. (n.d.). *Overview - Agent2Agent Protocol (A2A)*. Retrieved from https://google.github.io/A2A/specification/overview/

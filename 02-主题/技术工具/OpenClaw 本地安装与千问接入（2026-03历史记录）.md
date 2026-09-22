---
title: OpenClaw 本地安装与千问接入（2026-03历史记录）
aliases:
  - 装open claw
  - openclaw 命令
  - 安装openclaw
created: 2026-09-21
updated: 2026-09-21
status: historical
tags:
  - 技术工具/OpenClaw
  - 技术工具/排错
  - 知识库/历史整理
source_period: 2026-03-28 至 2026-04-03
verification: 仅核对旧对话中的实际输出，未复测当前版本
---

# OpenClaw 本地安装与千问接入（2026-03历史记录）

> [!abstract] 当时做到哪里
> **本机 Gateway 已运行成功；千问 API 接通未获证实。** 旧对话中的实际输出证明了安装与本地端口连通，但结尾仍在排查 HTTP 401。不能把“默认模型已设置”当成“模型已经能回复”。

本页由助手于 2026-09-21 从旧安装对话与命令速查表整理，保留可复用的排错经验。命令、路径与模型名称均属于当时版本的记录，使用前需核对当前安装；本次没有运行安装、改配置或验证当期产品文档。

## 已有证据与未完成事项

| 项目 | 旧记录中的证据 | 能得出的结论 |
|---|---|---|
| CLI | `OpenClaw 2026.3.24 (cff6dc9)` | 当时 CLI 可以运行 |
| 安装方式 | 实际服务命令使用 `~/.openclaw/tools/node-v22.22.0/bin/node` 与本地 `lib/node_modules/openclaw` | 最终使用用户目录内的 Node/CLI；不是 Python 虚拟环境 |
| 本地 Gateway | `RPC probe: ok`、`Listening: 127.0.0.1:18789` | 当时本地网关正常可达 |
| 千问 OAuth | 向导显示 `Qwen OAuth complete`、`qwen-portal/coder-model` | 账号授权流程完成，不证明推理调用成功 |
| Model Studio | 向导显示 `Default model set to modelstudio/qwen3.5-plus` | 配置写入了模型选项，不证明凭证有效 |
| 模型调用 | TUI 和后续 Dashboard 仍出现 `HTTP 401: invalid access token or token expired` | 本对话未完成模型连通验收；原因未最终定位 |
| 飞书接入 | 原 `openclaw接入飞书.md` 为空，长对话没有完成接入的记录 | 没有可恢复的飞书配置方案 |

## 最有价值的排错经验

### 1. 按实际失败层定位

最初普通安装器卡在 Homebrew 的 sudo 检查，随后改走安装到 `~/.openclaw` 的本地前缀路线。第二次失败先出现 npm 缓存目录的 `EACCES`，再出现重试 `openclaw@next` 的 `ETARGET`。就这份日志而言，先发生的权限错误更值得检查，不能只追着最后一个错误处理。

旧对话提出过修改 npm 缓存属主的修复方法；后续 CLI 已能运行，但没有完整记录每条修复命令的执行结果。保留问题定位，不把建议过的全部命令当作已经验证的步骤。

### 2. 服务已注册，不等于服务可用

曾经同时出现 `LaunchAgent (loaded)`、进程 `running`，但端口没有监听，日志写明 `gateway.mode` 未设置。之后设置本地模式并重启，才出现 RPC 成功与端口监听。

当时起效的配置修复记录：

```bash
# 历史版本命令；本次未重新执行
~/.openclaw/bin/openclaw config set gateway.mode local
~/.openclaw/bin/openclaw gateway restart
~/.openclaw/bin/openclaw gateway status
```

验收应看具体任务：服务层看实际连通，模型层看真实回复，外部渠道层再看消息是否按预期到达。

### 3. PATH 与补全是两类问题

- `command not found: openclaw` 时，用 `~/.openclaw/bin/openclaw --version` 能调用，说明应检查命令搜索路径。
- `command not found: compdef` 发生在 zsh 补全脚本加载时。旧 `.zshrc` 显示 OpenClaw 补全之前没有初始化补全系统；当时提出将 `compinit` 放在补全脚本之前。
- 后续实际输出再次证明 CLI 和 Gateway 正常；没有单独的补全功能验收，不能据此声称 Tab 补全已经完全修好。

### 4. 停止、未加载与卸载不要混为一谈

这台机器当时在停止后出现过 `LaunchAgent (not loaded)`，执行重启也提示 `Gateway service not loaded`。提示中建议重新安装/加载服务。

这只能证明**当时用户服务没有加载**，不能仅凭 `not loaded` 就断言服务文件已删除。旧助手曾在“没有加载”和“已卸载”之间混用表述；重用经验时应先检查状态与服务文件。

当时服务文件为 `~/Library/LaunchAgents/ai.openclaw.gateway.plist`。旧回复早期还出现过 `bot.molt.gateway`，与后续真实输出不一致，不作为本机已验证配置保存。

### 5. 模型配置必须对应真实凭证类型

当时界面存在两个不同入口：`Qwen` 的账号 OAuth，以及 `Qwen (Alibaba Cloud Model Studio)` 的 API Key。后者又区分中国/国际区域、Coding Plan 订阅/Standard 按量付费。

旧助手在没有确认用户持有何种 Key 时，反复建议默认选择 Coding Plan；之后才提出 Key 与端点不匹配的可能性。长对话没有最终证明 401 的根因，也没有成功回复。

值得保留的检查顺序是：核对凭证所属服务、区域、套餐、请求端点与模型权限，再做一次真实请求。`coding.dashscope.aliyuncs.com` 与 `modelstudio/qwen3.5-plus` 仅是当时配置记录，不是当前推荐配置。不能凭位于中国就决定应使用订阅 Key，也不能把“改成 Standard”写成已经验证的修复方案。

TUI 中还保留过缺少 Anthropic Key 的旧错误，同时显示当前模型为 Model Studio。仅凭一屏历史输出，不能断言新的请求仍在走 Anthropic；应按新请求对应的时间和日志判断。

## 历史配置速查

| 配置项 | 当时记录 |
|---|---|
| 主目录 | `~/.openclaw/` |
| CLI | `~/.openclaw/bin/openclaw` |
| 主配置 | `~/.openclaw/openclaw.json` |
| 工作区 | `~/.openclaw/workspace` |
| Gateway | local；loopback `127.0.0.1`；端口 `18789` |
| 服务 | macOS LaunchAgent；实际向导的 runtime 为 `Node (recommended)` |
| 日志 | `~/.openclaw/logs/gateway.log`、`gateway.err.log`；另有 `/tmp/openclaw/` 文件日志 |
| agent 认证位置 | 报错引用 `~/.openclaw/agents/main/agent/auth-profiles.json` |
| 暴露与认证选择 | 向导中选本机 loopback、Token；建议 Tailscale Off，未记录外部访问验收 |

原始输出曾测得 `~/.openclaw` 为 **805 MB**、npm 缓存为 **352 MB**。这是当时 `du` 得到的磁盘占用，**不是运行内存**。早期对内存的区间估算没有实测支持，本页不把它保存为硬件要求。

以下只用于识别历史操作，不是整段顺序执行脚本：

| 用途 | 当时出现的命令 |
|---|---|
| 查版本、总状态 | `openclaw --version`、`openclaw status` |
| 查 Gateway | `openclaw gateway status` |
| 打开界面 | `openclaw dashboard`、`openclaw tui` |
| 配置与检查 | `openclaw configure`、`openclaw models status`、`openclaw doctor` |
| 观察日志 | `openclaw logs --follow` |
| 服务生命周期 | `openclaw gateway stop`、`openclaw gateway restart`、`openclaw gateway install` |

`doctor` 可能进入修复流程，不能一概当成纯只读检查。旧对话中的重装、卸载、目录删除、凭证复制和整份配置输出没有保留为日常速查步骤：这些操作需要结合当时状态与备份范围重新判断。凭证文件可包含秘密，不应直接打印后贴进笔记或聊天。

## 来源与回溯

清理前两份非空来源为：

- `notes/装open claw.md`：3272 行，114508 字节；笔记元数据为 2026-03-31 至 2026-04-03，实际终端日志包含 2026-03-28。
- `notes/openclaw 命令.md`：旧速查表，内容与长对话重复，元数据日期为 2026-03-28。

原文保存在[整理前笔记与配置备份](</Users/jiawangliang/konwledge base/backups/obsidian-cleanup-20260921/整理前笔记与配置.zip>)，完整处理记录见 [[00-整理记录-2026-09-21]]。本页只替代日常查阅入口，不替代原始证据。

| 原长对话行号 | 证据 |
|---|---|
| 253–305 | Homebrew sudo 失败；npm EACCES；后续 ETARGET |
| 565–656 | 未配置本地模式导致启动受阻，修复后 RPC 与监听成功 |
| 735–981 | PATH/补全排错；后续 CLI 与 Gateway 状态 |
| 1337–1360、1510–1513 | LaunchAgent 未加载；重启提示恢复服务 |
| 1412–1413 | 805 MB 与 352 MB 的磁盘测量 |
| 1763–1776、2030 | OAuth 完成与默认模型设置 |
| 2616、2752–2767 | 实际 Node runtime；缺少旧 provider 凭证与后续 401 |
| 2972–2976、3148–3272 | 订阅/按量付费选项；结尾认证问题仍未验收 |

原长对话 SHA-256：`d16eb319cb4a66e5f2f7b574b0fea7911e15db0a56c97401afcd5b10992a12cb`。

原命令速查表 SHA-256：`9093c8f140e15c0b6b4fff5e09f124e92baeac43d08caa309f11851aed4db0c5`。

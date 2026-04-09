---
tags: [daily]
title: openclaw 命令
created: '2026-03-28T13:04:08.411Z'
modified: '2026-03-28T13:04:24.725Z'
---

# openclaw 命令


### 日常最常用

```bash
openclaw --version
openclaw status
openclaw doctor
openclaw dashboard
```

`openclaw dashboard` 是最快开始聊天的方式，会打开本地控制台界面。([OpenClaw][1])

### Gateway 后台服务

```bash
openclaw gateway status
openclaw gateway stop
openclaw gateway restart
```

你现在就是 LaunchAgent 常驻模式。想彻底停后台，用 `openclaw gateway stop`；下次再用，`openclaw gateway restart`。([OpenClaw][2])

### 首次配置 / 重配

```bash
openclaw onboard
openclaw onboard --install-daemon
openclaw configure
```

`onboard` 是引导式初始化；`configure` 适合后面补配模型、网关、工作区这些。([OpenClaw][1])

### 你现在最需要的：模型认证

你刚才报错就是没配 provider 的 key。先配认证，再聊天。

```bash
openclaw configure
```

如果想重新走完整引导：

```bash
openclaw onboard
```

OpenClaw 的首次可用聊天，前提是模型认证已经配好。([OpenClaw][1])

### 渠道接入

```bash
openclaw channels login
```

接 WhatsApp 之类的渠道时用它。快速开始文档把它列为标准步骤之一。([OpenClaw][3])

### 新建 agent

```bash
openclaw agents add <name>
```

适合把不同用途拆开，比如一个做热点整理，一个做内容生成。([OpenClaw][4])

### 发送消息 / 跑一次 agent

```bash
openclaw message send --target <目标> --message "你好"
openclaw agent --message "帮我总结今天热点" --to <目标>
```

前者更像直接发消息，后者是跑一次 agent。([OpenClaw][5])

### 出问题时先查

```bash
openclaw doctor
openclaw gateway status
openclaw logs --follow
tail -n 80 ~/.openclaw/logs/gateway.log
tail -n 80 ~/.openclaw/logs/gateway.err.log
```

`doctor` 是官方修复和迁移工具，适合先跑一遍。([OpenClaw][6])

### 关闭和重开

```bash
openclaw gateway stop
openclaw gateway restart
openclaw dashboard
```

这套最适合你平时开关。([OpenClaw][2])

### 卸载

```bash
openclaw uninstall
openclaw uninstall --all --yes --non-interactive
```

前者会卸服务和本地数据但保留 CLI；后者更彻底。([OpenClaw][2])

### 你当前阶段的推荐顺序

```bash
openclaw configure
openclaw dashboard
openclaw gateway status
```

先把 **API key / 模型认证** 配好，再回 dashboard 聊天。

如果你愿意，我下一条可以给你一份 **“适合你现在的第一天使用流程”**，按“先配 API，再做第一次聊天，再接一个简单任务”来写。

[1]: https://docs.openclaw.ai/zh-CN/start/getting-started?utm_source=chatgpt.com "入门指南 - OpenClaw"
[2]: https://docs.openclaw.ai/zh-CN/gateway?utm_source=chatgpt.com "Gateway 网关运行手册 - OpenClaw"
[3]: https://docs.openclaw.ai/zh-CN/start/quickstart?utm_source=chatgpt.com "快速开始 - OpenClaw"
[4]: https://docs.openclaw.ai/zh-CN/cli/onboard?utm_source=chatgpt.com "onboard - OpenClaw"
[5]: https://docs.openclaw.ai/zh-CN?utm_source=chatgpt.com "OpenClaw - OpenClaw"
[6]: https://docs.openclaw.ai/zh-CN/gateway/doctor?utm_source=chatgpt.com "Doctor - OpenClaw"

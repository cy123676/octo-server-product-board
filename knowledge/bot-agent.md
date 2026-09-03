# Bot / Agent / BotFather / Provision 关系

> Source baseline: `Mininglamp-OSS/octo-server` commit `5437764`

## 结论

在 octo-server 中，Bot 更像消息身份和 API 调用主体；Agent 是背后的智能执行/运行体。Bot 的创建、管理和连接涉及 BotFather、Bot API、bot_provision、botidentity 等模块。

## 关键源码依据

- `modules/botfather/api.go:L83-L115`：BotFather 不再承接 `/v1/bot/*` Bot API；它负责文档、User Bot 管理、User API Key、Robot Apply、runtime onboarding 等。
- `modules/botfather/command.go:L56-L72`：BotFather 会监听发给 BotFather 的私聊命令，命令如 `/newbot`、`/mybots`、`/connect`、`/token` 等由 `handleCommand` 处理。
- `modules/botfather/command.go:L148-L190`：BotFather 命令分发覆盖新建 Bot、查看 Bot、连接/断开、改名、改描述、删除、token、quickstart/install、申请审批等。
- `modules/bot_provision/bot_api.go:L1-L18`：bot_provision 是 octo-server 与 octo-fleet/daemon 的跨服务契约面，包含 `POST /v1/bot/mint` 和 `GET /v1/bot/:uid/token`。
- `modules/bot_provision/bot_api.go:L48-L91`：`mintBot` 由 Web/session 调用，要求登录用户属于目标 Space，再生成 `bf_` token 并调用 `botfather.MintBotOBO`。
- `modules/bot_provision/bot_api.go:L96-L171`：daemon 通过 `api_key Bearer` 获取某个 bot 的 `bot_token`，要求 caller 是 bot creator，且 bot 属于 api_key 绑定的 Space。
- `modules/bot_api/auth.go:L10-L27`：Bot API 认证区分 User Bot（`bf_` token / robot table）和 App Bot（`app_` token / app_bot table）。
- `modules/botidentity/resolver.go:L1-L4`：botidentity 只读取 `robot` 和 `app_bot` 表，明确 `user.robot` 只是展示元数据，不是授权来源。
- `modules/botidentity/resolver.go:L92-L120`：`Resolve` 会判定 User Bot / App Bot，且遇到双表同时活跃会 fail closed。

## 产品理解

可以向考官这样解释：

- **Bot 是账号/消息身份**：它出现在群里，持有 token，调用 `/v1/bot/*` API 收发消息。
- **Agent 是大脑/运行逻辑**：真正负责理解需求、写 issue、生成 PRD、回答问题。
- **BotFather 是管理入口**：用户通过它创建、管理、连接 Bot，或拿到 runtime onboarding 信息。
- **bot_provision 是跨服务开通入口**：让 web/session 或 daemon 安全地开通/获取 bot token。
- **botidentity 是运行时真相源**：判断 UID 是否是有效 Bot，以及属于哪类 Bot。

## 可回答的问题

- Bot 和 Agent 有什么区别？
- User Bot 与 App Bot 区别是什么？
- BotFather 管什么，Bot API 管什么？
- 为什么 `user.robot` 不能作为授权来源？
- daemon 怎么拿到 bot token？

## 风险点

- Bot token 暴露后应轮换。
- 绑定 Bot 与 Agent 时，要避免多个 Bot 私聊复用同一个默认会话上下文。
- 认证/归属判断必须 fail closed，不能因为查不到身份而默认放行。

# API 与错误处理

> Source baseline: `Mininglamp-OSS/octo-server` commit `5437764`

## 结论

octo-server 的错误处理正在从 legacy 兼容的“HTTP 400 + body 里写语义状态”过渡到真实 HTTP status。新/特定端点通过 `ResponseErrorLWithStatus` 保留语义状态；旧端点继续用 `ResponseErrorL` 保持兼容。错误码集中定义在 `pkg/errcode`，并带 i18n 能力。

## 关键源码依据

- `main.go:L197-L204`：API 启动时初始化 i18n 运行时 locale，并给路由设置 error renderer。
- `pkg/httperr/respond.go:L13-L23`：`ResponseErrorL` 是业务侧本地化错误 facade，默认保持 legacy HTTP 400 兼容路径。
- `pkg/httperr/respond.go:L26-L50`：`ResponseErrorLWithStatus` 用于需要保留真实 HTTP transport status 的新端点。
- `pkg/httperr/respond.go:L53-L81`：统一根据 code registry 生成 error spec，`useSemanticStatus` 决定 wire status。
- `modules/bot_api/api_i18n.go:L14-L25`：Bot API 明确要求所有新 helper 走 `httperr.ResponseErrorL` / `ResponseErrorLWithStatus`，并列举保持真实 HTTP status 的错误。
- `pkg/errcode/bot_provision.go:L9-L25`：bot_provision 错误码说明接口、兼容状态和 anti-enumeration 策略。
- `pkg/errcode/bot_provision.go:L45-L55`：daemon token endpoint 的认证失败统一折叠为 `err.server.bot_provision.auth_failed` 401，避免枚举。
- `pkg/errcode/botfather.go:L133-L147`：BotFather/Bot API Key 认证失败也统一成单一 401，不暴露具体失败原因。
- `pkg/errcode/group.go:L64-L145`：群权限错误包括群主/管理员限制、非群成员、外部成员限制、Bot 归属限制等。

## 产品理解

面向产品/考试回答时可以这样概括：

- API 错误不是散落字符串，而是有统一错误码、HTTP status、默认消息和安全 detail key。
- 有些旧接口为了兼容客户端仍返回 HTTP 400；新接口或 adapter 依赖真实状态码时使用 `ResponseErrorLWithStatus`。
- 对认证失败，系统刻意做 anti-enumeration：缺 Bearer、空 token、无效 token、查不到 api key 等外部响应合并，详细原因只写日志。

## 可回答的问题

- 为什么有些错误 HTTP status 是 400，但 body 里有语义状态？
- 哪些路径应该返回真实 401/403/404？
- 为什么认证错误不能告诉调用方“具体哪个因素错了”？
- Bot API 的错误码在哪里定义？

## 风险点

- 如果新增 endpoint 混用 legacy/raw error，会造成客户端分支不一致。
- 如果认证失败返回过细，可能暴露 token 是否存在、bot 是否存在、api key 是否有效等枚举面。

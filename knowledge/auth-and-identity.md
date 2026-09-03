# 认证与身份

> Source baseline: `Mininglamp-OSS/octo-server` commit `5437764`

## 结论

octo-server 的认证分为普通用户 session token、Bot token、App Bot token、User API Key 等多类入口。核心原则是：请求入口先解析身份，再基于用户/空间/群/子区/Bot 归属做授权；Bot 身份不应依赖展示字段，而应依赖权威表。

## 关键源码依据

- `main.go:L205-L227`：启动 API 时替换 TokenParser，使用 `pkg/auth.Decode` 解析 cache value，并注入 language/role resolver；角色按 UID 实时解析 DB/缓存，避免 token 中旧角色长期生效。
- `pkg/auth/parser.go:L59-L72`：`CacheTokenParser` 取代 legacy parser，支持 v2 JSON envelope 和旧格式。
- `pkg/auth/parser.go:L130-L164`：`Parse` 对空 token、Redis 缓存缺失、解码失败、v3 token validator 缺失等情况分别返回错误。
- `pkg/auth/parser.go:L189-L208`：系统角色通过 `RoleResolver` 按请求实时解析，防止管理员降权后旧 token 继续授权。
- `pkg/auth/validator.go:L76-L143`：`TokenValidator` 是 canonical token-read policy；v3 token 要求有限 Redis TTL、绝对过期时间和 session generation 匹配。
- `modules/bot_api/auth.go:L25-L41`：Bot API 通过 token 前缀路由：`app_` 走 App Bot，其他/`bf_` 走 User Bot。
- `modules/bot_api/auth.go:L45-L61`：User Bot 通过 robot table 查 `bot_token`，成功后写入 `robot_id`、`bot_kind`、`robot` 到上下文。
- `modules/bot_api/auth.go:L64-L129`：App Bot 先查共享 registry/cache，miss 后查 DB，并要求 status=1；成功后写入 `robot_id`、`bot_kind`、scope/space。
- `modules/botidentity/resolver.go:L59-L76`：botidentity 一次查询 `robot` 和 `app_bot` 表，避免身份种类和授权元数据漂移。
- `modules/botidentity/resolver.go:L92-L120`：如果同一 UID 同时是 active User Bot 和 App Bot，会返回 ambiguous error，调用方应 fail closed。

## 产品理解

- 普通用户入口：适合 Web/Admin 操作，使用 session token，经 AuthMiddleware 设置登录用户。
- Bot 入口：适合外部 bot/agent runtime 调用，使用 `bf_` 或 `app_` token。
- User API Key：适合 daemon / runtime onboarding 等跨服务场景。
- Bot 身份必须来自 `robot` / `app_bot` 这些生命周期表，而不是 `user.robot` 展示字段。

## 可回答的问题

- 为什么同一个 UID 不能同时是 User Bot 和 App Bot？
- Bot token 怎么区分 User Bot 和 App Bot？
- 用户被降权后，为什么不能只相信 token 里的旧 role？
- v3 token 为什么要求 Redis TTL 和 session generation？

## 风险点

- WebSocket 或 Bot API 认证失败时，如果只返回笼统错误，调用方难以区分 token 失效、权限不足和服务异常；但安全设计上部分 endpoint 会故意做 anti-enumeration，不能把所有原因都暴露给外部调用方。

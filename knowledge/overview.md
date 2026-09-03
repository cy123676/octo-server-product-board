# octo-server 总览

> Source baseline: `Mininglamp-OSS/octo-server` commit `5437764`

## 结论

`octo-server` 是 OCTO 平台的 Go 后端核心，负责 REST + WebSocket API、Lobster/Agent 编排，以及对 WuKongIM 的控制面管理。它不是单纯的 IM 服务，而是把客户端、管理端、Agent、业务模块和 IM 核心连接起来的后端控制面。

## 关键源码 / 文档依据

- `README.md:L27-L37`：项目自述明确 `octo-server` 是 OCTO 的 Go backend，暴露 REST + WebSocket API，并驱动 WuKongIM IM core。
- `README.md:L41-L43`：说明它是整个平台的统一后端锚点，Agent/Lobster 编排是一等能力，存储和 IM 可插拔。
- `README.md:L85-L91`：请求处理链路是 Authenticate → Authorise → Execute → Fan out → Respond。
- `main.go:L138-L156`：服务启动时读取 `configs/tsdd.yaml`，初始化 config，并设置 token TTL。
- `main.go:L185-L227`：API 服务启动时配置错误渲染、TokenParser、语言和角色解析器。
- `internal/modules.go:L22-L78`：通过 blank import 注册业务模块，包括 botfather、bot_api、bot_provision、group、thread、message、usersecret 等。

## 产品理解

从产品视角看，`octo-server` 是“协作空间 + 机器人/Agent + 消息控制面”的中枢：

1. **客户端入口**：为 Web/Admin/移动端提供 REST 和 WebSocket 能力。
2. **身份与权限**：先解析 token，再做组织、群、子区、Bot 归属等权限判断。
3. **Agent/Bot 能力**：Bot API、BotFather、bot_provision、botidentity 等模块共同支持 Bot 创建、连接、鉴权、事件拉取、发消息和 Agent 运行接入。
4. **IM 边界**：消息最终通过 WuKongIM 发送/同步，但 octo-server 负责业务鉴权、路由、成员关系与 payload 安全检查。
5. **错误与国际化**：通过 `httperr` + `errcode` 输出统一错误 envelope，并逐步区分 legacy 400 和真实 HTTP status。

## 可回答的问题

- octo-server 在 OCTO 架构里是什么角色？
- 为什么它既有 REST API，又要对接 WuKongIM？
- Bot/Agent 相关模块大概分布在哪里？
- 一次请求从进入服务到消息发出大致经过哪些阶段？

## 不确定项

- README 中列出了一些历史/概念目录如 `internal/api`、`internal/service`、`internal/im`，当前仓库实际结构已偏模块化；回答时应优先以当前源码目录为准。

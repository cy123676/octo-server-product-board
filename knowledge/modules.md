# 模块清单与边界

> Source baseline: `Mininglamp-OSS/octo-server` commit `5437764`

## 结论

`octo-server` 采用模块注册模式。`internal/modules.go` 通过 blank import 引入各业务模块，每个模块在自己的 `init()` 中注册 API、SQL migration 或事件监听。模块间存在历史依赖顺序说明，但 migration 真正排序依赖 SQL 文件时间戳，而不是 Go import 顺序。

## 关键源码依据

- `internal/modules.go:L1-L18`：说明 migration 顺序由 SQL 文件时间戳决定，Go init 顺序由依赖图决定；import 顺序更多是历史和可读性。
- `internal/modules.go:L22-L78`：集中列出已注册模块：`agentmailgateway`、`backup`、`base`、`robot`、`bot_mention`、`botfather`、`channel`、`file`、`group`、`message`、`oidc`、`openapi`、`space`、`thread`、`user`、`usersecret`、`bot_api`、`app_bot`、`bot_provision` 等。
- `internal/modules.go:L54-L57`：说明 `modules/runtime` 已移除，runtime/bot orchestration 由独立服务 `octo-fleet` 负责。
- `internal/modules.go:L64-L75`：说明 `usersecret` 提供用户外部密钥别名表；`bot_api`、`app_bot`、`bot_provision` 与 bot 运行链路相关。

## 产品理解

高频考试问答可以按以下边界解释：

- **botfather**：偏 Bot 管理、BotFather 命令、用户 API Key、申请审批、runtime onboarding。
- **bot_api**：偏 Bot 对外运行 API，包括注册、心跳、事件、发消息、消息同步、群/子区/文件等 Bot 能力。
- **bot_provision**：偏跨服务开通 Bot 账号/获取 Bot token，服务 octo-fleet/daemon 接入。
- **botidentity**：偏运行期身份解析，判断一个 UID 到底是 User Bot 还是 App Bot。
- **group/thread/message/channel**：协作空间核心对象，决定 Bot 是否有权限进入群、读写 GROUP.md、加入子区或发送消息。
- **usersecret**：用于用户外部密钥别名和 write-only CRUD/resolve，适合放用户密钥而不是直接暴露明文。

## 可回答的问题

- 哪些模块和 Bot/Agent 运行相关？
- 为什么 runtime 相关逻辑不在 octo-server 内？
- 新增 Bot API 能力应该优先看哪个模块？
- 群/子区/消息能力分别落在哪些模块？

## 不确定项

- 每个模块的完整业务语义需要继续按具体 API 文件细读；本文件只提供模块级索引。

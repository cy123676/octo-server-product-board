# IM / WuKongIM 边界

> Source baseline: `Mininglamp-OSS/octo-server` commit `5437764`

## 结论

octo-server 不是直接替代 WuKongIM；它负责业务侧鉴权、成员关系、Bot 能力、payload 安全、事件队列和控制面调用。WuKongIM 负责实际消息投递、同步和实时连接。

## 关键源码依据

- `README.md:L29-L37`：octo-server 暴露 REST + WebSocket API，并驱动 WuKongIM IM core 做实时消息。
- `README.md:L41-L43`：存储和 IM 可插拔，WuKongIM 通过 thin control-plane boundary 被驱动。
- `README.md:L85-L91`：请求处理最后的 fan out 阶段会把消息 enqueue 到 WuKongIM，并在需要时触发 adapter。
- `configs/tsdd.yaml:L21-L24`：配置项包含 `wukongIM.apiURL` 和 `wukongIM.managerToken`。
- `QUICKSTART.md:L52-L58`：本地运行需要可达的 WuKongIM、MySQL、Redis，可选对象存储。
- `QUICKSTART.md:L82-L85`：配置时需要设置 `db.mysqlAddr`、`db.redisAddr`、`wukongIM.apiURL`、`wukongIM.managerToken`。
- `modules/bot_api/register.go:L60-L75`：User Bot 注册时调用 `UpdateIMToken`，把 bot token 作为 IM token 写入 WuKongIM。
- `modules/bot_api/register.go:L143-L154`：App Bot 同样使用 token 作为 API auth 与 IM WebSocket 连接 token。
- `modules/bot_api/send.go:L36-L49`：Bot 发消息请求包含 `channel_id`、`channel_type`、`payload`，可选 `on_behalf_of`。
- `modules/bot_api/send.go:L51-L71`：`sendMessage` 在进入 IM 前先做请求体、channel、payload 校验。
- `modules/bot_api/sync.go:L24-L46`：Bot 通过 `/v1/bot/messages/sync` 拉取某个 channel 的消息，带 seq 范围、limit、pull_mode。
- `modules/bot_api/events.go:L54-L104`：Bot 通过 `/v1/bot/events` 读取自己的事件队列，支持长轮询 wait。

## 产品理解

- **octo-server 负责“能不能做”**：身份、权限、群成员、子区成员、OBO、payload 保留字段、解散守卫等。
- **WuKongIM 负责“消息怎么投递/同步”**：IM token、消息发送、消息同步、订阅关系等。
- Bot 侧长连接/事件拉取依赖 `/v1/bot/register`、`/v1/bot/heartbeat`、`/v1/bot/events` 等接口保持可用。

## 可回答的问题

- octo-server 和 WuKongIM 分工是什么？
- Bot 为什么要 register / heartbeat？
- Bot 发消息前 server 会做哪些校验？
- 消息同步为什么要检查群成员或好友关系？

## 风险点

- register / heartbeat 是 Bot 自愈链路，若被业务流量限流挤掉，会导致 Bot 掉线后无法恢复。
- `sendMessage` 必须先做 payload 保留字段校验，否则可能被恶意 Bot 伪造服务端 OBO 标记。
- 对 App Bot，群/子区场景通常有更严格的 DM-only 限制。

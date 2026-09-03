# 存储与外部依赖

> Source baseline: `Mininglamp-OSS/octo-server` commit `5437764`

## 结论

octo-server 运行依赖 MySQL、Redis、WuKongIM；文件能力可接对象存储。MySQL 承担业务数据，Redis 承担 token/session/cache/队列/限流等运行时状态，WuKongIM 承担消息投递和同步，对象存储承担文件上传下载。

## 关键源码 / 文档依据

- `README.md:L43-L43`：存储与 IM 可插拔，WuKongIM 通过薄控制面边界驱动。
- `README.md:L54-L58`：默认 dev 配置需要本地 WuKongIM、MySQL-compatible database。
- `QUICKSTART.md:L52-L58`：本地 Go 构建运行依赖 Go、WuKongIM、MySQL 8、Redis 7，可选 S3-compatible object store。
- `QUICKSTART.md:L82-L87`：配置重点包括 `db.mysqlAddr`、`db.redisAddr`、`wukongIM.apiURL`、`wukongIM.managerToken`、对象存储配置。
- `configs/tsdd.yaml:L26-L35`：数据库配置字段：MySQL DSN、Redis 地址/密码/TLS、异步任务 Redis。
- `configs/tsdd.yaml:L69-L170`：文件服务配置包含 MinIO、Tencent COS、Aliyun OSS、Qiniu、SeaweedFS 的支持和限制。
- `pkg/auth/validator.go:L76-L143`：token 校验读取 Redis token record，并检查 TTL、payload expiry、session generation。
- `modules/bot_api/events.go:L54-L104`：Bot 事件队列读取接口 `/v1/bot/events` 支持分页和长轮询。
- `modules/bot_api/ratelimit.go:L26-L47`：Bot register/heartbeat 等限流依赖 Redis key，且设计上避免同 IP Bot 互相拖死。

## 产品理解

- MySQL：组织、用户、群、子区、Bot、Issue 相关业务数据的长期存储。
- Redis：token/session 校验、缓存、队列、限流等高频运行时状态。
- WuKongIM：消息通道、消息同步、订阅关系和实时投递。
- 对象存储：文件上传、下载、预签名 URL。

## 可回答的问题

- 本地部署为什么必须有 MySQL、Redis、WuKongIM？
- token 校验为什么依赖 Redis？
- 文件上传为什么不同对象存储能力不一样？
- Bot 事件/心跳为什么需要 Redis 限流和队列状态？

## 风险点

- Redis 不可用会影响 token/session、限流和事件队列等多条链路。
- WuKongIM token 或 managerToken 不一致会导致 Bot 注册/消息发送失败。
- 对象存储的 presigned URL 配置不一致会导致浏览器上传 403。

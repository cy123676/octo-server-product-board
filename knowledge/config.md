# 配置说明

> Source baseline: `Mininglamp-OSS/octo-server` commit `5437764`

## 结论

octo-server 默认通过 `configs/tsdd.yaml` 加载配置，并支持环境变量覆盖。关键配置包括运行模式、Webhook 签名、WuKongIM、MySQL/Redis、外部访问 URL、文件服务、注册策略、内置账号、机器人参数和缓存策略。

## 关键源码 / 文档依据

- `main.go:L138-L145`：启动时读取 `--config` 指定的配置文件，默认是 `configs/tsdd.yaml`；设置 env prefix `TS` 并把 `.` 替换成 `_` 后自动读取环境变量。
- `main.go:L152-L156`：构造 config context 后把 token TTL 写入 `cfg.Cache.TokenExpire`。
- `configs/tsdd.yaml:L1-L13`：基础配置包括 `mode`、监听地址、appName、rootDir、消息跨设备保存、群人数升级阈值、eventPoolSize 等。
- `configs/tsdd.yaml:L15-L19`：Webhook HMAC-SHA256 签名配置 `webhookSecretKey`。
- `configs/tsdd.yaml:L21-L24`：WuKongIM 配置 `wukongIM.apiURL` 和 `managerToken`。
- `configs/tsdd.yaml:L26-L35`：数据库配置包括 MySQL、Redis、Redis TLS、async task Redis。
- `configs/tsdd.yaml:L36-L44`：外网配置 `external.ip`、`external.baseURL`、`webLoginURL`，其中 webLoginURL 影响卡片通知 deep-link。
- `configs/tsdd.yaml:L69-L170`：文件服务配置，支持 MinIO、Tencent COS、Aliyun OSS、Qiniu、SeaweedFS 等，并说明 presigned URL/CORS/签名约束。
- `configs/tsdd.yaml:L233-L238`：机器人配置包括 `messageExpire`、`inlineQueryTimeout`、`eventPoolSize`。
- `configs/tsdd.yaml:L250-L259`：缓存配置包括 token 前缀、token 过期、登录设备缓存、好友申请 token、名称缓存等。
- `QUICKSTART.md:L77-L88`：本地配置重点是 MySQL、Redis、WuKongIM 和对象存储。
- `QUICKSTART.md:L103-L116`：`--config` 必须在子命令前，例如 `./octo-server --config /path/to/tsdd.yaml api`。

## 产品理解

配置可以按“运行基础设施”和“产品能力开关”分两类：

- 基础设施：MySQL、Redis、WuKongIM、对象存储、外部 URL。
- 产品能力：注册、文件上传、Webhook 安全、机器人消息过期、inline query 超时、系统账号。

## 可回答的问题

- 本地部署 octo-server 需要哪些依赖？
- WuKongIM 的配置在哪里？
- 为什么 `--config` 参数要放在子命令前面？
- 文件上传为什么需要 CORS / presigned header 一致？

## 风险点

- `smsCode` 测试码不能在 release 环境随意开启。
- 文件服务签名 URL 对 host、Content-Type、Content-Disposition 等参数敏感，客户端必须按服务端返回的 header 上传。
- `wukongIM.managerToken` 与 WuKongIM 端不一致会导致 IM 控制面调用失败。

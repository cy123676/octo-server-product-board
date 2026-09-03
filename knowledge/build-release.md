# 构建与发布

> Source baseline: `Mininglamp-OSS/octo-server` commit `5437764`

## 结论

octo-server 可以通过本地 Go build 构建，也可以通过官方 `octo-deployment` Docker Compose 栈一键部署。考试场景下，产品管家 Agent 只需要理解构建/部署边界，不需要改目标仓库或实际发布。

## 关键源码 / 文档依据

- `README.md:L45-L52`：快速开始命令为 clone 仓库、`go build -o octo-server .`、再用 `./octo-server --config ./configs/tsdd.yaml` 启动。
- `README.md:L60-L66`：官方 OOTB 部署在 `Mininglamp-OSS/octo-deployment`，旧 compose 栈已迁移到该单一来源。
- `QUICKSTART.md:L3-L15`：推荐两种方式：一键 Docker Compose 栈，或本地 Go build 对接自己的基础设施。
- `QUICKSTART.md:L19-L31`：Docker Compose 试用流程在 `octo-deployment`，包含 server、admin、web、matter、smart-summary、WuKongIM、MySQL、Redis、MinIO、nginx。
- `QUICKSTART.md:L52-L71`：本地构建需要 Go ≥ 1.25，并用 `go build -o octo-server .` 构建根 main package。
- `QUICKSTART.md:L103-L116`：运行时 `--config` 参数要放在子命令前。
- `QUICKSTART.md:L149-L159`：排障包括端口冲突、WuKongIM tokenAuth/managerToken 不匹配、go.sum 缺失等。

## 产品理解

对考官可以这样说明：

- 想快速体验 OCTO，用 `octo-deployment`；它负责整套依赖。
- 想开发 octo-server，用本仓库 Go build；但必须准备 WuKongIM、MySQL、Redis。
- Agent 考试中，我不会修改/发布 `octo-server`，只会读源码、归档问题、写 PRD 和评审建议。

## 可回答的问题

- 怎么本地启动 octo-server？
- 为什么 go build ./... 不等于生成可执行文件？
- 为什么官方推荐 octo-deployment 做 OOTB？
- 常见启动失败点有哪些？

## 风险点

- `docker compose down -v` 会删除数据卷，属于破坏性操作。
- 端口、WuKongIM token、go.sum / cross-repo replace 是常见卡点。

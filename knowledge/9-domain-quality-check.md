# 9 域知识库全量质检

> Source baseline: `Mininglamp-OSS/octo-server` commit `5437764`
> Check time: 2026-09-07

## 结论

当前不是“没有知识库”：已有 10 个知识库文件雏形。但此前缺少一份按考试口径汇总的“9 域全量质检”索引，容易被误判为 9 域未配置。本文用于把现有 10 个文件映射到 9 个产品知识域，并标出缺口。

## 现有知识库文件

1. `knowledge/overview.md`
2. `knowledge/modules.md`
3. `knowledge/auth-and-identity.md`
4. `knowledge/rbac-acl.md`
5. `knowledge/config.md`
6. `knowledge/api-error.md`
7. `knowledge/bot-agent.md`
8. `knowledge/im-boundary.md`
9. `knowledge/storage-dependency.md`
10. `knowledge/build-release.md`

## 9 域映射

| 9 域 | 覆盖文件 | 状态 | 说明 |
|---|---|---|---|
| 1. 项目总览 / 架构定位 | `overview.md` | 已有雏形 | 覆盖 octo-server 角色、请求链路、产品定位。 |
| 2. 模块边界 / 注册机制 | `modules.md` | 已有雏形 | 覆盖 `internal/modules.go`、模块注册、runtime 移除。 |
| 3. 认证 / 身份 / Token | `auth-and-identity.md` | 已有雏形 | 覆盖 session token、Bot token、App Bot token、User API Key、botidentity。 |
| 4. 权限 / RBAC / ACL | `rbac-acl.md` | 已有雏形 | 覆盖 Space、群、子区、Bot 归属、OBO 等授权边界。 |
| 5. 配置 / 部署参数 | `config.md` | 已有雏形 | 覆盖 `configs/tsdd.yaml`、外部 URL、文件服务等配置。 |
| 6. API / 错误处理 | `api-error.md` | 已有雏形 | 覆盖统一错误码、HTTP status 兼容策略、认证错误收敛。 |
| 7. Bot / Agent / BotFather | `bot-agent.md` | 已有雏形 | 覆盖 BotFather、Bot API、bot_provision、botidentity。 |
| 8. IM / WuKongIM 边界 | `im-boundary.md` | 已有雏形 | 覆盖 octo-server 与 WuKongIM 的职责分工。 |
| 9. 存储 / 文件 / 构建发布 | `storage-dependency.md`, `build-release.md` | 已有雏形 | 文件和外部依赖在 `storage-dependency.md`；构建发布单独拆成第 10 个文件。 |

## 质检结果

- 9 域不是空的，已有主题文件可以映射覆盖。
- 实际文件数是 10 个，不是 9 个；原因是“构建发布”被从“存储/外部依赖”里拆成了独立文件。
- 当前仍是“雏形 + 部分高频题可答”，不能说已完成全量知识库。
- 需要继续补：每个域的高频考试题、更多源码行号、交叉引用、过期校验记录。

## 明确缺口

1. 缺少 GitHub/需求池真实推送与落库确认记录。
2. 缺少 cron 自动扫描的真实运行记录；当前只有 `runtime/scan_state.json` 和 `scan-state/issue-*.json` 状态雏形。
3. 缺少正式 `exam-summary.md` 归档。
4. 缺少每个知识域的逐条源码复核日志；本文件只是首次全量映射质检。

## 下一步建议

1. 补 `exam-summary.md`：汇总 Agent 规则、仓库、需求池、标签体系、知识库和缺口。
2. 真跑一次需求池扫描，生成可核验的 scan log。
3. 确认群号和主考人后，再启用 12 小时 cron 外发；群号未确认前只做本地准备，不真实外发。
4. 对 10 个知识库文件逐个补充“最近复核时间 + 源码 baseline + 关键证据”。

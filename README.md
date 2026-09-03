# octo-server 产品管家需求池

AINOL Agent 实操考核用公开需求池，用于围绕 `Mininglamp-OSS/octo-server` 承接：

- 产品功能问答
- Bug 反馈归档
- Feature 需求收集
- PRD 草案撰写
- Review 意见追踪
- 定时扫描与 Octo 群同步

> 目标仓库 `Mininglamp-OSS/octo-server` 只读。本仓库只作为考试产物、需求池和知识库，不直接修改目标仓库代码。

## 工作流

1. 考官/成员在 Octo 群提出问题、Bug 或需求。
2. 产品管家 Agent 判断类型并归档到本仓库 Issue。
3. Agent 自动打标签：类型、优先级、状态、模块。
4. 对 Feature 类需求，Agent 补充 PRD 草案。
5. Agent 定时扫描 Issue 变化，有新增/评论/状态变化时回 Octo 群同步。
6. 无更新时静默，避免刷屏。

## 标签体系

### 类型
- `type/bug`
- `type/feature`
- `type/question`
- `type/prd`
- `type/review`

### 优先级
- `priority/P0`
- `priority/P1`
- `priority/P2`

### 状态
- `status/new`
- `status/triaged`
- `status/prd-draft`
- `status/in-review`
- `status/need-info`
- `status/wontfix`
- `status/done`

### 模块
- `module/auth`
- `module/rbac`
- `module/config`
- `module/api`
- `module/im`
- `module/agent`
- `module/storage`
- `module/build`

## 约束

- 不向目标仓库写 Issue、PR 或代码。
- 不在群聊、文档或 Issue 中泄露 token、cookie、密码等凭证。
- 产品问答必须尽量给出可核验的文件路径/行号。
- 没有证据时明确说“不确定”，不编造引用。

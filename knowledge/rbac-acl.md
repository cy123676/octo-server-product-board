# RBAC / ACL / 权限边界

> Source baseline: `Mininglamp-OSS/octo-server` commit `5437764`

## 结论

octo-server 的权限判断不是单一 RBAC，而是多层组合：用户 session 权限、Space 成员、群成员/管理员、子区成员、Bot 归属、App Bot scope、OBO grant 等共同决定“能不能读/写/发送”。

## 关键源码依据

- `README.md:L85-L91`：请求链路包含 Authorise，说明授权是核心阶段之一。
- `main.go:L205-L227`：TokenParser 注入 RoleResolver，系统角色按 UID 实时解析，减少旧 token 权限滞后。
- `pkg/auth/parser.go:L45-L57`：RoleResolver 说明系统角色应取用户当前角色，而不是只信 token 快照。
- `modules/group/bot_ownership.go:L9-L22`：只有 Bot 创建者能邀请自己的 Bot 进群，普通成员/管理员不能随意拉别人的 Bot。
- `modules/group/bot_ownership.go:L24-L37`：`checkBotOwnership` 定义具体规则，bot row 缺失、停用或 creator 不匹配都拒绝。
- `modules/bot_api/send.go:L588-L620`：DM 发送权限区分 creator、friend、OBO bypass；没有授权关系时拒绝。
- `modules/bot_api/sync.go:L48-L69`：群消息同步要求 Bot 是群成员，App Bot 不允许 group sync。
- `modules/bot_api/sync.go:L70-L112`：个人消息同步要求 friend gate；User Bot creator 可直接同步，其他需要好友关系。
- `modules/bot_api/groups.go:L162-L184`：Bot 读取 GROUP.md 前必须是群成员。
- `modules/bot_api/groups.go:L209-L250`：Bot 更新 GROUP.md 前要求群未解散、Bot 是群成员且具备 Bot Admin 权限。

## 产品理解

可以向考官解释为：

- 普通用户：走 session token + space/group/thread 权限。
- User Bot：受 creator、friend、群成员、Bot Admin 等约束。
- App Bot：有 platform/space scope，且很多群/子区能力被限制为 DM-only。
- OBO：允许特定 Bot 在 grant 范围内代表真实用户行动，但必须验证 grant 和 channel scope。

## 可回答的问题

- 为什么群管理员也不能随便拉别人的 Bot？
- Bot 读 GROUP.md 和写 GROUP.md 权限有什么不同？
- App Bot 为什么不能随便同步群消息？
- 用户被降权后，系统如何避免旧 token 继续授权？

## 风险点

- 如果把 `user.robot` 当授权来源，会被展示字段污染；应使用 robot/app_bot 生命周期表。
- OBO bypass 必须只在明确 OBO 上下文下生效，不能让普通 Bot 借 grant 跳过好友/群成员门禁。

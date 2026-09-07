# 自动扫描 / Cron 证据

## 当前策略

- 扫描对象：GitHub 需求池 `cy123676/octo-server-product-board`
- 扫描内容：Issue 状态、标题、标签、评论数、更新时间
- 执行方式：系统 crontab + flock，定时自动运行 `scripts/run_product_board_scan.sh`
- 外发策略：考试群号和主考人未确认前，**不向任何群外发**；只记录扫描日志和待发送草稿
- 无变化策略：只记录本地/远端运行记录，不发“无更新”消息

## 计划任务

```cron
*/30 * * * * cd /home/mlclaw/.openclaw/workspace-octo-server-product-manager && /usr/bin/flock -n /tmp/octo_server_product_board_scan.lock ./octo-server-product-board/scripts/run_product_board_scan.sh
```

## 运行产物

- `runtime/scan_runs/index.jsonl`：每次扫描摘要
- `runtime/scan_runs/<run_id>.json`：单次扫描详情
- `runtime/scan_state.json`：最近一次扫描状态快照
- `runtime/pending_broadcasts/<run_id>.md`：有变化时生成的待发送群播报草稿
- `runtime/logs/cron_scan.log`：cron 标准输出/错误日志

## 备注

等考试群号和主考人确认后，再启用真实外发配置；未确认前不得猜群号或主考人。

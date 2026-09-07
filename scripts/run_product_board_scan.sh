#!/usr/bin/env bash
set -euo pipefail
cd /home/mlclaw/.openclaw/workspace-octo-server-product-manager
LOG_DIR="octo-server-product-board/runtime/logs"
mkdir -p "$LOG_DIR"
exec ./octo-server-product-board/scripts/scan_product_board.py >> "$LOG_DIR/cron_scan.log" 2>&1

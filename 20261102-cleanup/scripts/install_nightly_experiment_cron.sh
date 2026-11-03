#!/usr/bin/env bash
# 安装每天 20:00 和开机后的夜间窗口恢复任务，保留用户现有 crontab。
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$PROJECT_DIR/scripts/nightly_experiment_window.sh"
CRON_LOG="$PROJECT_DIR/results/nightly_cron.log"
START_MARKER="# BEGIN vlm-rd-detect-nightly"
END_MARKER="# END vlm-rd-detect-nightly"
staging="$(mktemp)"
trap 'rm -f "$staging"' EXIT

crontab -l 2>/dev/null \
    | sed "/^${START_MARKER}$/,/^${END_MARKER}$/d" > "$staging" || true
{
    echo "$START_MARKER"
    echo "0 20 * * * /bin/bash '$RUNNER' >> '$CRON_LOG' 2>&1"
    echo "@reboot /bin/bash -c \"sleep 120; /bin/bash '$RUNNER' >> '$CRON_LOG' 2>&1\""
    echo "$END_MARKER"
} >> "$staging"
crontab "$staging"
echo "已安装：每天 20:00 启动；夜间重启后 120 秒恢复；08:00 由监督器停止。"
crontab -l | sed -n "/^${START_MARKER}$/,/^${END_MARKER}$/p"

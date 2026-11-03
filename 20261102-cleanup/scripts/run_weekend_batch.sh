#!/bin/bash
# ============================================================
# 周末批量训练脚本 v2 — 可中断恢复 + 温度保护
#
# 特性：
#   1. 自动跳过已完成的变体（检查 metrics.json）
#   2. 温度监控：超过阈值自动暂停训练并冷却
#   3. 中断友好：任何时刻 kill/Ctrl-C，重跑同一脚本自动续传
#   4. 状态文件 tracking 当前进度
#
# 用法：
#   ./scripts/run_weekend_batch.sh          # 首次运行或续传
#   touch /tmp/stop_training                # 优雅停止（当前变体完成后不继续）
#   Ctrl-C                                  # 立即中断（已完成变体不受影响）
#
# 在 tmux 中运行：
#   tmux new -s weekend
#   conda activate vlm-rd-detect
#   ./scripts/run_weekend_batch.sh
#   # Ctrl+B D 分离；tmux attach -t weekend 回来查看
# ============================================================
set -euo pipefail

PROJECT=/home/bornshine/workspace/vlm-rd-detect
cd "$PROJECT"

# ---- 可调参数 ----
POWER_LIMIT=200            # GPU 功耗上限 (W)，需 sudo
GPU_CLOCK_MAX=1500         # GPU 核心频率上限 (MHz)，需 sudo。0=不限制
TEMP_COOLDOWN=50           # 变体间 GPU 冷却到 <此温度才继续 (°C)
TEMP_PAUSE=84              # 训练中超过此温度 → 暂停冷却 (°C)
TEMP_CRITICAL=88           # 超过此温度 → 立即 kill 训练进程 (°C)
COOLDOWN_CHECK=30          # 冷却时检查间隔 (秒)
COOLDOWN_MIN=120           # 变体间最短冷却时间 (秒)

LOG_DIR="$PROJECT/results/runs"
MAIN_LOG="$LOG_DIR/weekend_batch_$(date +%m%d_%H%M).log"
STATE_FILE="$LOG_DIR/.batch_state"
STOP_FILE="/tmp/stop_training"

# ---- 训练序列 ----
# 格式: "variant seed"
TRAIN_QUEUE=(
    "p2_cbam 1"
    "p2_only 1"
    "cbam_only 1"
    "baseline 2"
    "p2_cbam 2"
    "p2_only 2"
    "cbam_only 2"
)

# ---- 函数 ----
log() {
    echo "[$(date '+%H:%M:%S')] $*" | tee -a "$MAIN_LOG"
}

gpu_temp() {
    nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader 2>/dev/null || echo "0"
}

gpu_info() {
    nvidia-smi --query-gpu=temperature.gpu,power.draw,power.limit,fan.speed,utilization.gpu --format=csv,noheader 2>/dev/null || echo "N/A"
}

set_power_limit() {
    local current
    current=$(nvidia-smi -q -d POWER 2>/dev/null | grep "Current Power Limit" | head -1 | grep -oP '[\d.]+')
    if [ "${current%.*}" != "$POWER_LIMIT" ]; then
        log "设置 GPU 功耗墙: ${current}W → ${POWER_LIMIT}W (需要 sudo)"
        sudo nvidia-smi -pl "$POWER_LIMIT" 2>/dev/null || {
            log "⚠ 功耗墙设置失败，当前 ${current}W"
            return 1
        }
    fi
    log "功耗墙: ${POWER_LIMIT}W ✅"
}

lock_gpu_clock() {
    if [ "$GPU_CLOCK_MAX" -gt 0 ]; then
        log "锁定 GPU 核心频率上限: ${GPU_CLOCK_MAX}MHz"
        sudo nvidia-smi -lgc 0,"$GPU_CLOCK_MAX" 2>/dev/null || {
            log "⚠ GPU 频率锁失败（可忽略，不影响训练）"
        }
    fi
}

is_completed() {
    local variant=$1 seed=$2
    local metrics="$LOG_DIR/${variant}_seed${seed}/metrics.json"
    if [ -f "$metrics" ]; then
        # 验证 JSON 完整（有 test_mAP50 字段）
        if python3 -c "import json; d=json.load(open('$metrics')); assert 'test_mAP50' in d" 2>/dev/null; then
            return 0
        fi
        log "  ⚠ ${variant}_seed${seed} metrics.json 不完整，将重跑"
        return 1
    fi
    return 1
}

wait_cooldown() {
    local reason=${1:-"变体间冷却"}
    local start_ts=$(date +%s)
    log ""
    log "--- 🧊 ${reason} (目标 <${TEMP_COOLDOWN}°C) ---"
    while true; do
        local t=$(gpu_temp)
        local info=$(gpu_info)
        local elapsed=$(($(date +%s) - start_ts))
        log "   [${elapsed}s] GPU: ${info}"
        if [ "$t" -lt "$TEMP_COOLDOWN" ] && [ "$elapsed" -ge "$COOLDOWN_MIN" ]; then
            log "   温度达标 ✅"
            break
        fi
        sleep "$COOLDOWN_CHECK"
    done
}

emergency_cooldown() {
    log ""
    log "🛑🛑🛑 紧急冷却！GPU 温度达到 ${TEMP_CRITICAL}°C 🛑🛑🛑"
    log "已保存当前 best.pt。正在强制冷却，请勿操作..."
    # 等待温度降到安全范围
    while true; do
        local t=$(gpu_temp)
        log "   当前 ${t}°C"
        if [ "$t" -lt "$TEMP_COOLDOWN" ]; then
            log "   温度恢复安全 ✅"
            break
        fi
        sleep 30
    done
}

run_one_variant() {
    local variant=$1 seed=$2
    local tag="${variant}_seed${seed}"

    log ""
    log "══════════════════════════════════════════════"
    log "  🚀 $tag  |  GPU: $(gpu_info)"
    log "══════════════════════════════════════════════"

    # 更新状态文件
    echo "running $variant seed=$seed started=$(date -Iseconds)" > "$STATE_FILE"

    local start_ts=$(date +%s)
    local train_pid=""

    # 启动训练（后台），同时监控温度
    PYTHONNOUSERSITE=1 conda run -n vlm-rd-detect \
        python experiments/run_experiment.py \
            "$variant" --epochs 100 --batch 16 --patience 30 --seed "$seed" \
        >> "$MAIN_LOG" 2>&1 &
    train_pid=$!

    # 温度监控循环
    local overheated=0
    while kill -0 "$train_pid" 2>/dev/null; do
        sleep 10

        # 检查停止信号
        if [ -f "$STOP_FILE" ]; then
            log "⚠ 检测到停止信号 $STOP_FILE"
            kill -TERM "$train_pid" 2>/dev/null || true
            wait "$train_pid" 2>/dev/null || true
            log "训练已停止。best.pt 已由 YOLO 自动保存"
            rm -f "$STOP_FILE"
            return 2  # 特殊码：用户主动停止
        fi

        local t=$(gpu_temp)
        if [ "$t" -ge "$TEMP_CRITICAL" ]; then
            log "🛑 GPU ${t}°C ≥ ${TEMP_CRITICAL}°C！立即终止训练"
            kill -TERM "$train_pid" 2>/dev/null || true
            sleep 3
            kill -KILL "$train_pid" 2>/dev/null || true
            wait "$train_pid" 2>/dev/null || true
            overheated=1
            break
        elif [ "$t" -ge "$TEMP_PAUSE" ]; then
            log "⚠ GPU ${t}°C ≥ ${TEMP_PAUSE}°C，训练仍在运行（功耗墙=${POWER_LIMIT}W）"
        fi
    done

    # 等训练进程结束
    wait "$train_pid" 2>/dev/null || true
    local rc=$?

    local elapsed=$(($(date +%s) - start_ts))
    local m=$((elapsed / 60))

    if [ "$overheated" -eq 1 ]; then
        log "🔥 $tag 因过热中断 (${m}min) — best.pt 已保存，降温后可从该变体重试"
        emergency_cooldown
        return 1
    elif [ "$rc" -eq 2 ]; then
        log "⏸  $tag 用户主动停止 (${m}min)"
        return 2
    elif [ "$rc" -eq 0 ]; then
        # 验证 metrics.json 是否生成
        if is_completed "$variant" "$seed"; then
            log "✅ $tag 完成 (${m}min) | GPU: $(gpu_temp)°C"
            echo "done $variant seed=$seed" > "$STATE_FILE"
            return 0
        else
            log "⚠ $tag 训练进程正常退出但 metrics.json 缺失"
            return 1
        fi
    else
        log "❌ $tag 异常退出 (exit=$rc, ${m}min)"
        return 1
    fi
}

# ---- 主流程 ----
log "╔══════════════════════════════════════════════════╗"
log "║  周末批量训练 v2  $(date '+%Y-%m-%d %H:%M')              ║"
log "║  功耗墙:${POWER_LIMIT}W  频率锁:${GPU_CLOCK_MAX}MHz  冷却:<${TEMP_COOLDOWN}°C          ║"
log "║  ${#TRAIN_QUEUE[@]} 个待跑变体 | 自动跳过已完成               ║"
log "╚══════════════════════════════════════════════════╝"

# 1. 设置 GPU 保护
conda info --envs 2>/dev/null | grep -q vlm-rd-detect || { log "❌ 环境不可用"; exit 1; }
set_power_limit
lock_gpu_clock
log "GPU 当前: $(gpu_info)"
log ""

# 2. 检查并输出已完成列表
COMPLETED=()
TODO=()
for entry in "${TRAIN_QUEUE[@]}"; do
    read -r var seed <<< "$entry"
    if is_completed "$var" "$seed"; then
        COMPLETED+=("${var}_seed${seed}")
    else
        TODO+=("$entry")
    fi
done

if [ ${#COMPLETED[@]} -gt 0 ]; then
    log "✅ 已完成 (${#COMPLETED[@]}): ${COMPLETED[*]}"
fi
if [ ${#TODO[@]} -eq 0 ]; then
    log "🎉 全部完成，无需训练！"
    log "下一步: python experiments/summarize_detection_results.py"
    exit 0
fi
log "⏳ 待训练 (${#TODO[@]}): ${TODO[*]}"
log ""

# 3. 首次冷却（确保从低温开始）
if [ "$(gpu_temp)" -ge "$TEMP_COOLDOWN" ]; then
    wait_cooldown "初始冷却"
fi

# 4. 逐个训练
FAILED=()
STOPPED=0
for entry in "${TODO[@]}"; do
    read -r var seed <<< "$entry"

    run_one_variant "$var" "$seed"
    rc=$?

    if [ "$rc" -eq 2 ]; then
        STOPPED=1
        break
    elif [ "$rc" -ne 0 ]; then
        FAILED+=("${var}_seed${seed}")
        log "⚠ 继续下一个变体..."
    fi

    # 停止信号检查
    if [ -f "$STOP_FILE" ]; then
        log "检测到停止信号，本轮结束"
        rm -f "$STOP_FILE"
        STOPPED=1
        break
    fi

    # 冷却后继续
    if [ "$var" != "cbam_only" ] || [ "$seed" != "2" ]; then
        wait_cooldown "变体间冷却"
    fi
done

# 5. 汇总
log ""
log "╔══════════════════════════════════════════════════╗"
log "║  本轮训练结束  $(date '+%Y-%m-%d %H:%M')                    ║"
if [ "$STOPPED" -eq 1 ]; then
    log "║  ⏸ 用户主动停止                                       ║"
fi
if [ ${#FAILED[@]} -gt 0 ]; then
    log "║  ❌ 失败 (${#FAILED[@]}): ${FAILED[*]}"
fi

# 统计完成数
DONE_NOW=0
for entry in "${TRAIN_QUEUE[@]}"; do
    read -r var seed <<< "$entry"
    if is_completed "$var" "$seed"; then
        DONE_NOW=$((DONE_NOW + 1))
    fi
done
log "║  总进度: ${DONE_NOW}/${#TRAIN_QUEUE[@]} (共需 7 组)            ║"
log "╚══════════════════════════════════════════════════╝"
log ""

if [ "$DONE_NOW" -eq "${#TRAIN_QUEUE[@]}" ]; then
    log "🎉 全部 7 组完成！下一步："
else
    log "📋 续传命令:  ./scripts/run_weekend_batch.sh"
fi
log "   多 seed 汇总:  python experiments/summarize_detection_results.py"

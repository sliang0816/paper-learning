#!/usr/bin/env bash
# 在低功耗窗口或用户明确授权的无截止模式下运行论文实验队列。
set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUEUE_SCRIPT="${QUEUE_SCRIPT:-$PROJECT_DIR/scripts/run_thesis_core_queue.sh}"
RESULTS_DIR="$PROJECT_DIR/results"
LOG_FILE="${LOG_FILE:-$RESULTS_DIR/nightly_experiment.log}"
LOCK_FILE="${LOCK_FILE:-$RESULTS_DIR/.nightly_experiment.lock}"
GPU_INDEX="${GPU_INDEX:-0}"
POWER_LIMIT_WATTS="${POWER_LIMIT_WATTS:-160}"
PAUSE_TEMPERATURE_C="${PAUSE_TEMPERATURE_C:-76}"
RESUME_TEMPERATURE_C="${RESUME_TEMPERATURE_C:-68}"
CHECK_INTERVAL_SECONDS="${CHECK_INTERVAL_SECONDS:-30}"
GRACEFUL_STOP_SECONDS="${GRACEFUL_STOP_SECONDS:-120}"
ALLOW_DAYTIME="${ALLOW_DAYTIME:-0}"
STOP_HOUR="${STOP_HOUR:-8}"
RUN_UNTIL_STOP="${RUN_UNTIL_STOP:-0}"

if [[ ! "$STOP_HOUR" =~ ^([0-9]|1[0-9]|2[0-3])$ ]]; then
    echo "STOP_HOUR 必须是 0--23 的整数，实际为：$STOP_HOUR" >&2
    exit 2
fi
if [[ ! -f "$QUEUE_SCRIPT" ]]; then
    echo "实验队列脚本不存在：$QUEUE_SCRIPT" >&2
    exit 2
fi

mkdir -p "$RESULTS_DIR"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "$(date '+%F %T') 已有夜间实验监督器运行，退出。" >> "$LOG_FILE"
    exit 0
fi

log() {
    echo "$(date '+%F %T') $*" | tee -a "$LOG_FILE"
}

hour=$((10#$(date +%H)))
if [[ "$RUN_UNTIL_STOP" == "1" ]]; then
    deadline_epoch=""
else
    if (( hour >= STOP_HOUR && hour < 20 )) && [[ "$ALLOW_DAYTIME" != "1" ]]; then
        log "当前不在 20:00--次日 $(printf '%02d' "$STOP_HOUR"):00 训练窗口，退出。"
        exit 0
    fi

    if (( hour >= 20 )) || [[ "$ALLOW_DAYTIME" == "1" && $hour -ge 8 ]]; then
        deadline_epoch="$(date -d "tomorrow $(printf '%02d' "$STOP_HOUR"):00" +%s)"
    else
        deadline_epoch="$(date -d "today $(printf '%02d' "$STOP_HOUR"):00" +%s)"
    fi
fi

initial_power_limit="$(
    nvidia-smi -i "$GPU_INDEX" --query-gpu=power.limit \
        --format=csv,noheader,nounits 2>/dev/null | awk '{printf "%d", $1}'
)"
if [[ -z "$initial_power_limit" ]]; then
    initial_power_limit=""
    log "警告：无法读取 GPU 初始功耗上限。"
fi

if nvidia-smi -i "$GPU_INDEX" -pl "$POWER_LIMIT_WATTS" >> "$LOG_FILE" 2>&1; then
    log "GPU 功耗上限设为 ${POWER_LIMIT_WATTS}W；温控暂停/恢复阈值为 ${PAUSE_TEMPERATURE_C}/${RESUME_TEMPERATURE_C}°C。"
else
    log "警告：设置 ${POWER_LIMIT_WATTS}W 失败；温度看门狗仍然生效。"
fi

restore_power() {
    if [[ -n "$initial_power_limit" ]]; then
        nvidia-smi -i "$GPU_INDEX" -pl "$initial_power_limit" \
            >> "$LOG_FILE" 2>&1 || true
        log "GPU 功耗上限恢复为监督器启动前的 ${initial_power_limit}W。"
    fi
}

job_pid=""
job_paused=0
shutdown_job() {
    if [[ -z "$job_pid" ]] || ! kill -0 "$job_pid" 2>/dev/null; then
        return
    fi
    if (( job_paused )); then
        kill -CONT -- "-$job_pid" 2>/dev/null || true
        job_paused=0
    fi
    log "请求实验进程组 ${job_pid} 在当前 checkpoint 后停止。"
    kill -INT -- "-$job_pid" 2>/dev/null || true
    local waited=0
    while kill -0 "$job_pid" 2>/dev/null \
        && (( waited < GRACEFUL_STOP_SECONDS )); do
        sleep 5
        waited=$((waited + 5))
    done
    if kill -0 "$job_pid" 2>/dev/null; then
        log "优雅停止超时，发送 TERM；last.pt 保留到上一完整 epoch。"
        kill -TERM -- "-$job_pid" 2>/dev/null || true
        sleep 10
    fi
    if kill -0 "$job_pid" 2>/dev/null; then
        log "进程仍未退出，发送 KILL。"
        kill -KILL -- "-$job_pid" 2>/dev/null || true
    fi
}

on_signal() {
    log "监督器收到停止信号。"
    shutdown_job
    restore_power
    exit 143
}
trap on_signal INT TERM HUP

if [[ -n "$deadline_epoch" ]]; then
    log "启动论文实验队列；截止时间 $(date -d "@$deadline_epoch" '+%F %T')。"
else
    log "启动论文实验队列；无固定截止时间，仅在收到停止信号或队列完成时退出。"
fi
setsid bash "$QUEUE_SCRIPT" >> "$LOG_FILE" 2>&1 &
job_pid=$!

while kill -0 "$job_pid" 2>/dev/null; do
    now_epoch="$(date +%s)"
    if [[ -n "$deadline_epoch" ]] && (( now_epoch >= deadline_epoch )); then
        log "到达 $(printf '%02d' "$STOP_HOUR"):00 窗口边界。"
        shutdown_job
        break
    fi

    temperature="$(
        nvidia-smi -i "$GPU_INDEX" --query-gpu=temperature.gpu \
            --format=csv,noheader,nounits 2>/dev/null | awk '{print int($1)}'
    )"
    if [[ "$temperature" =~ ^[0-9]+$ ]]; then
        if (( ! job_paused && temperature >= PAUSE_TEMPERATURE_C )); then
            kill -STOP -- "-$job_pid" 2>/dev/null || true
            job_paused=1
            log "GPU ${temperature}°C，暂停实验进程组冷却。"
        elif (( job_paused && temperature <= RESUME_TEMPERATURE_C )); then
            kill -CONT -- "-$job_pid" 2>/dev/null || true
            job_paused=0
            log "GPU 已降至 ${temperature}°C，恢复实验。"
        fi
    else
        log "警告：本轮无法读取 GPU 温度。"
    fi
    sleep "$CHECK_INTERVAL_SECONDS"
done

if wait "$job_pid" 2>/dev/null; then
    job_status=0
else
    job_status=$?
fi
restore_power
if (( job_status == 0 )); then
    log "论文核心实验队列已正常完成。"
else
    log "实验队列退出码为 $job_status；下个窗口会归档不完整检测运行并干净重跑。"
fi
exit "$job_status"

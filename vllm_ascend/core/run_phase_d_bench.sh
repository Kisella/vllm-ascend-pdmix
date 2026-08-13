#!/usr/bin/env bash
# Phase D benchmark/validation launcher for the NPU CI environment.
# Companion to ../PhaseD_验证与压测清单.md; post-run log audit via audit_pd_logs.py.
#
# Usage:
#   RUN_ID=pd_c1 MODEL_PATH=/data/qwen3.6-27b bash run_phase_d_bench.sh <scenario>
#     scenario: smoke | func | risk1 | risk2 | watchdog | bench | bench_mtp_off | all
#
# Phase C notes:
#   - Both sides MUST run at DEBUG log level (VLLM_LOGGING_LEVEL=DEBUG):
#     the auditor's PDFL conservation check reads the cloud's
#     "PassiveScheduler classified/picked" debug lines and the edge's
#     "[MTP-DEBUG] scheduler picked" lines.
#   - watchdog scenario injects a link failure (kill cloud) with a short
#     prefill_draft_last_watchdog_seconds and asserts the edge raises
#     "[PD] PREFILL_DRAFT_LAST lost" instead of hanging silently.
#
# This is a TEMPLATE: replace the edge/cloud launch commands below with the
# CI's actual launcher (MindIE-style / mpirun / custom harness).  The three
# hooks to keep are: LOG_DIR capture, the wait-for-exit, and the audit call.
set -u

RUN_ID="${RUN_ID:-pd_phase_d}"
MODEL_PATH="${MODEL_PATH:?set MODEL_PATH to the model weights dir}"
LOG_DIR="$(cd "$(dirname "$0")" && pwd)/logs/${RUN_ID}"
mkdir -p "$LOG_DIR"

# --- scenario matrix ------------------------------------------------------- #
SCENARIO="${1:-all}"
EXTRA_ARGS=()
WATCHDOG_SECONDS="30.0"
case "$SCENARIO" in
  smoke)  # single short request, MTP on — functional assertions F1-F12
    PROMPT_LEN=4096; CONCURRENCY=1; MTP="--speculative-config spec_mtp.json"
    EXTRA_ARGS=(--max-model-len 32768)
    ;;
  func)   # short burst, checks slot conservation under cancel/abort
    PROMPT_LEN=8192; CONCURRENCY=4; MTP="--speculative-config spec_mtp.json"
    EXTRA_ARGS=(--max-model-len 65536)
    ;;
  risk1)  # long-seq chunked prefill + MTP chains — channel-order/deadlock probe
    PROMPT_LEN=65536; CONCURRENCY=8; MTP="--speculative-config spec_mtp.json"
    EXTRA_ARGS=(--max-model-len 131072 --enable-chunked-prefill --chunked-prefill-size 8192)
    ;;
  risk2)  # mid-chain cancel storm — slot-leak probe
    PROMPT_LEN=16384; CONCURRENCY=16; MTP="--speculative-config spec_mtp.json"
    EXTRA_ARGS=(--max-model-len 65536)
    ;;
  watchdog)  # Phase C: link-failure injection — edge must raise, not hang.
             # Short threshold + kill cloud mid-run; expect RuntimeError with
             # "[PD] PREFILL_DRAFT_LAST lost" in the edge log (audit FAIL = expected).
    PROMPT_LEN=16384; CONCURRENCY=4; MTP="--speculative-config spec_mtp.json"
    WATCHDOG_SECONDS="2.0"
    EXTRA_ARGS=(--max-model-len 65536)
    ;;
  bench)  # baseline A (no MTP) is a separate run: SCENARIO=bench_mtp_off
    PROMPT_LEN=32768; CONCURRENCY=8; MTP="--speculative-config spec_mtp.json"
    EXTRA_ARGS=(--max-model-len 131072 --enable-chunked-prefill --chunked-prefill-size 8192)
    ;;
  bench_mtp_off)  # §5.1 scenario A baseline
    PROMPT_LEN=32768; CONCURRENCY=8; MTP=""
    EXTRA_ARGS=(--max-model-len 131072 --enable-chunked-prefill --chunked-prefill-size 8192)
    ;;
  all) echo "run scenarios: smoke func risk1 risk2 watchdog bench bench_mtp_off (loop manually)"; exit 0 ;;
  *) echo "unknown scenario: $SCENARIO"; exit 2 ;;
esac

COMMON_ARGS=(
  --model "$MODEL_PATH"
  --enable-edge-cloud --async-scheduling
  --tensor-parallel-size 1 --pipeline-parallel-size 2
  --max-num-seqs 64
  $MTP
  "${EXTRA_ARGS[@]}"
)

echo "[phase-d] scenario=$SCENARIO run=$RUN_ID prompt_len=$PROMPT_LEN concurrency=$CONCURRENCY"
echo "[phase-d] logs -> $LOG_DIR"

# -------------------------------------------------------------------------- #
# TODO(CI): replace the two placeholder commands with the platform launcher.  #
# Requirements:                                                              #
#  1. edge process (PP rank 0) launched with $COMMON_ARGS + --role edge      #
#  2. cloud process (PP rank 1) launched with $COMMON_ARGS + --role cloud    #
#  3. both write stdout/stderr to $LOG_DIR/edge_<ts>.log / cloud_<ts>.log    #
#  4. both run with VLLM_LOGGING_LEVEL=DEBUG (auditor depends on it)         #
#  5. watchdog scenario: after the bench client has dispatched a few chains, #
#     kill -9 the cloud process; the edge must raise within the watchdog     #
#     interval (expected FAIL in the audit for this scenario)                #
#  6. the bench client (vllm benchmark / custom driver) targets the edge     #
#     server with prompts of length ~$PROMPT_LEN at ~$CONCURRENCY            #
# -------------------------------------------------------------------------- #
EDGE_LOG="$LOG_DIR/edge_${SCENARIO}.log"
CLOUD_LOG="$LOG_DIR/cloud_${SCENARIO}.log"
export VLLM_LOGGING_LEVEL=DEBUG

# placeholder — replace with real launch + wait:
echo "LAUNCH_EDGE ${COMMON_ARGS[*]} --role edge > $EDGE_LOG"
echo "LAUNCH_CLOUD ${COMMON_ARGS[*]} --role cloud > $CLOUD_LOG"
echo "BENCH client: prompt_len=$PROMPT_LEN concurrency=$CONCURRENCY"
echo "WATCHDOG_INJECTION: seconds=$WATCHDOG_SECONDS (scenario=$SCENARIO)"

# --- post-run audit -------------------------------------------------------- #
AUDIT="$(cd "$(dirname "$0")" && pwd)/audit_pd_logs.py"
if [[ -s "$EDGE_LOG" ]]; then
  case "$SCENARIO" in
    watchdog)
      # Expected outcome: edge raised "[PD] PREFILL_DRAFT_LAST lost".
      # grep asserts the raise fired; the auditor's own FAIL for it is
      # the expected verdict here, so flip to WARN via the grep gate.
      if grep -q "\[PD\] PREFILL_DRAFT_LAST lost for task_id=" "$EDGE_LOG"; then
        echo "[phase-d] watchdog PASS: edge raised on lost cloud tail"
      else
        echo "[phase-d] watchdog FAIL: edge did NOT raise within threshold"
        exit 1
      fi
      ;;
    risk2|func)
      # closed runs: leaks are FAIL
      python "$AUDIT" "$EDGE_LOG" --cloud-log "$CLOUD_LOG" --strict
      rc=$?
      echo "[phase-d] audit exit=$rc (0=pass 1=fail 2=warn-only)"
      exit $rc
      ;;
    *)
      # long runs may end mid-chain: WARN
      python "$AUDIT" "$EDGE_LOG" --cloud-log "$CLOUD_LOG"
      rc=$?
      echo "[phase-d] audit exit=$rc (0=pass 1=fail 2=warn-only)"
      exit $rc
      ;;
  esac
else
  echo "[phase-d] $EDGE_LOG missing — did the launcher write logs?"
  exit 3
fi

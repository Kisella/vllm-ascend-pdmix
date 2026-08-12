#
# Copyright (c) 2025 Huawei Technologies Co., Ltd. All Rights Reserved.
# This file is a part of the vllm-ascend project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Inject ascend PD-separation / edge-cloud / passive-PP hooks into the
upstream :class:`vllm.v1.engine.core.EngineCore` and
:class:`vllm.v1.engine.core.EngineCoreProc` without modifying upstream
sources.

This patch is the home of every line that the vllm-pdmix downstream fork
used to maintain inside ``vllm/v1/engine/core.py`` of vLLM:

* ``EngineCore.__init__`` — late-stage construction of the optional
  edge-cloud PD-separation channel (``self._pp_pd_channel``).
* ``EngineCore.step`` / ``EngineCore.step_with_batch_queue`` — drain
  cloud-returned batches into the local PD scheduler, publish
  head-segment batches on PRE_OUT, skip ``sample_tokens`` for head
  batches, and assign ``head_token`` ids.
* ``EngineCore._drain_pd_channel_inbox`` /
  ``EngineCore._maybe_publish_pre_out`` /
  ``EngineCore._needs_sample_tokens`` — three new helper methods used by
  the two ``step*`` paths above.
* ``EngineCore.shutdown`` — release the channel before the rest of the
  engine resources.
* ``EngineCoreProc._process_input_queue`` — force a blocking
  ``input_queue.get`` when the engine has nothing local to do, so the
  edge node never busy-spins while waiting for the next client request.

Design notes
------------
1. ``__init__`` and ``shutdown`` only append behavior at the end and at
   the start, respectively, so they are wrapped (call original + extra).
2. ``step`` / ``step_with_batch_queue`` / ``_process_input_queue`` insert
   logic in the middle of the original method body. They are rewritten
   in full here, bytewise-equivalent to upstream when no PD/edge-cloud
   feature flag is on.
3. Every flag read uses ``getattr(parallel_config, ..., default)`` so
   that even if the dest-only ``ParallelConfig`` extension fields are
   absent, this patch behaves identically to upstream.
4. The patch is installed at import time. A guard prevents double
   patching if this module is imported twice (e.g. from a child
   process).

Upstream sync
-------------
The reimplementations of ``step()``, ``step_with_batch_queue()`` and
``_process_input_queue()`` track upstream
``vllm-0.20.2_layerwise/vllm/v1/engine/core.py``. Whenever vLLM moves to
a new minor version, re-diff these methods against the new upstream
source and re-apply the dest-only inserts.
"""
from __future__ import annotations

import functools
import time
from collections import deque
import threading
from concurrent.futures import Future
from typing import cast
from uuid import uuid4

from vllm.config import ParallelConfig
from vllm.logger import logger
from vllm.v1.core.sched.output import BatchType, SchedulerOutput
from vllm.v1.engine.core import EngineCore, EngineCoreProc
from vllm.v1.outputs import EMPTY_MODEL_RUNNER_OUTPUT, ModelRunnerOutput

from vllm_ascend.v1.engine.passive_core import PPSchedulerZmqChannel


# Idempotency guard: re-importing this module (e.g. from a child process)
# must not double-wrap the original methods.
_INSTALLED_FLAG = "_vllm_ascend_engine_core_patched"


# Draft-chain head batches — the two per-domain variants
# (PREFILL_DRAFT_FIRST / DECODE_DRAFT_FIRST). Both share the same
# control-plane treatment: deferred PRE_OUT while the chain is being
# pre-generated.  Since 2026-08-12 the POST_OUT return differs per domain:
# the cloud publishes PREFILL_DRAFT_LAST back for prefill_draft heads,
# while DECODE_DRAFT_FIRST still gets no return (the edge self-posts the
# decode draft tail).
_DRAFT_HEAD_BATCH_TYPES = (
    BatchType.PREFILL_DRAFT_FIRST,
    BatchType.DECODE_DRAFT_FIRST,
)


# -----------------------------------------------------------------------#
# Original method handles captured before any wrapping happens.           #
# -----------------------------------------------------------------------#
_ORIG_ENGINE_CORE_INIT = EngineCore.__init__
_ORIG_ENGINE_CORE_SHUTDOWN = EngineCore.shutdown
_ORIG_RUN_ENGINE_CORE = EngineCoreProc.run_engine_core


# =======================================================================#
# EngineCore.__init__ — append PD/edge-cloud setup at the very end.       #
# =======================================================================#
@functools.wraps(_ORIG_ENGINE_CORE_INIT)
def _patched_engine_core_init(self, *args, **kwargs):
    _ORIG_ENGINE_CORE_INIT(self, *args, **kwargs)

    parallel_config: ParallelConfig = self.vllm_config.parallel_config

    # PD-separation is owned by the ascend plugin and lives under
    # ``additional_config.edge_cloud_config.pd_separation``. ``init_ascend_config``
    # is idempotent and returns the cached singleton if already initialized
    # in the main process; in a freshly-spawned subprocess it re-initializes
    # from the ``vllm_config`` we hold.
    from vllm_ascend.ascend_config import init_ascend_config
    ascend_config = init_ascend_config(self.vllm_config)
    edge_cloud = getattr(ascend_config, "edge_cloud_config", None)
    pd_enabled = bool(
        edge_cloud is not None
        and getattr(edge_cloud, "enabled", False)
        and getattr(edge_cloud, "pd_separation", None) is not None
        and edge_cloud.pd_separation.enabled
    )

    if getattr(parallel_config, "enable_edge_cloud", False):
        logger.info(
            "Edge-cloud mode enabled (pd_separation=%s)",
            pd_enabled,
        )

    # Load PD-separation configuration from environment variables
    from vllm_ascend.pd_separation_config import PDSeparationConfig
    pd_config = PDSeparationConfig.from_env()

    # Edge-cloud PD-separation bidirectional ZMQ channel (edge side).
    self._pp_pd_channel = None
    if pd_enabled and getattr(parallel_config, "is_edge_node", False):
        dp_rank = getattr(parallel_config, "data_parallel_rank", 0)

        # Discover the cloud's IP via a one-shot TCPStore. The edge
        # acts as store master on ``master_port + 1 + dp_rank`` so
        # that each DP rank has its own store port (no EADDRINUSE).
        # The cloud connects once per edge DP rank and writes its
        # ``get_ip()`` result. See passive_core.py for the
        # symmetric writer side.
        import torch.distributed as dist
        from datetime import timedelta
        _addr_store = dist.TCPStore(
            host_name=parallel_config.master_addr,
            port=parallel_config.master_port + 1 + dp_rank,
            world_size=2,
            is_master=True,
            timeout=timedelta(seconds=300),
        )
        cloud_addr = _addr_store.get("cloud_ip").decode()
        del _addr_store

        # Each DP rank needs its own ZMQ port pair to avoid bind
        # conflicts within the same edge process. Offset by 2 per
        # dp_rank: dp_rank 0 → {pre_out, post_out}, dp_rank 1 →
        # {pre_out+2, post_out+2}, etc. The cloud side must mirror
        # this offsetting in its own PPSchedulerZmqChannel setup.
        pre_out_port = pd_config.pre_out_port + dp_rank * 2
        post_out_port = pd_config.post_out_port + dp_rank * 2
        pre_out = f"tcp://*:{pre_out_port}"
        post_out = f"tcp://{cloud_addr}:{post_out_port}"
        self._pp_pd_channel = PPSchedulerZmqChannel(
            send_endpoint=pre_out,
            recv_endpoint=post_out,
            name=f"pd-edge-dp{dp_rank}",
        )
        logger.info(
            "PD-separation edge channel: PRE_OUT=%s, POST_OUT=%s "
            "(cloud_addr=%s auto-discovered)",
            pre_out, post_out, cloud_addr,
        )

    # [EHER §十五] Edge hidden early-receive + P-tail gating flags.  Read from
    # additional_config directly (same source as the worker's
    # _edge_hidden_early_recv_enabled), not from scheduler_config -- on the edge
    # EngineCore the platform's _configure_pd_separation_scheduler may not have
    # run yet, so getattr would silently return the default (off).  The pd obj
    # is already resolved above (edge_cloud.pd_separation).
    if pd_enabled and getattr(parallel_config, "is_edge_node", False):
        _pd = edge_cloud.pd_separation
        _eher = _pd.enable_edge_hidden_early_recv
        _eher_gating = _pd.enable_edge_hidden_early_recv_gating and _eher
        self._eher_enabled = _eher
        self._eher_gating_enabled = _eher_gating
        self._ha_fallback_timeout_ms = _pd.ha_fallback_timeout_ms
    else:
        self._eher_enabled = False
        self._eher_gating_enabled = False
        self._ha_fallback_timeout_ms = 1000.0
    # Gating pending set + ack-ready set (populated by _drain_ha_acks_edge).
    self._prefills_last_ha_pending: deque = deque()
    self._prefills_last_ha_pending_ts: dict[str, float] = {}
    self._ha_ready_head_tokens: set[str] = set()
    self._recv_hint_sent: set[str] = set()
    if self._eher_enabled:
        logger.info(
            "[EHER] edge hidden early-receive enabled on EngineCore "
            "(gating=%s, fallback_timeout_ms=%.0f)",
            self._eher_gating_enabled, self._ha_fallback_timeout_ms,
        )
    else:
        _pd_eher_val = "N/A"
        if pd_enabled and edge_cloud is not None:
            _pd = getattr(edge_cloud, "pd_separation", None)
            if _pd is not None:
                _pd_eher_val = str(
                    getattr(_pd, "enable_edge_hidden_early_recv", "N/A")
                )
        logger.info(
            "[EHER] edge hidden early-receive DISABLED on EngineCore "
            "(pd_enabled=%s, is_edge=%s, enable_edge_hidden_early_recv=%s)",
            pd_enabled,
            getattr(parallel_config, "is_edge_node", False),
            _pd_eher_val,
        )


# =======================================================================#
# Three helper methods bound on EngineCore. Mirror the dest fork.         #
# =======================================================================#
def _drain_pd_channel_inbox(self) -> None:
    """Move cloud-returned SchedulerOutputs into the local PDSeparated
    scheduler's ``prefills_last_ready`` / ``decodes_last_ready`` queues.

    [EHER §十五] When P-tail gating is on, a PREFILL_LAST is NOT scheduled
    immediately: it is parked in ``_prefills_last_ha_pending`` and a recv-hint
    is fired so the edge worker posts the cloud->edge hidden irecv early.  The
    P-tail is unlocked for scheduling only after the early-recv ack arrives
    (``_unlock_prefills_last_with_ha``), or after the fallback timeout.  Decode
    tails and the non-gating baseline path are unchanged.
    """
    # Lazy EHER init: _patched_engine_core_init may not have run (import-order
    # race between vllm-ascend patch install and EngineCore instantiation on the
    # edge).  Resolve the EHER flags directly from additional_config on the
    # first call so the function is self-sufficient — the init block in
    # _patched_engine_core_init is a best-effort early setup, not a hard
    # dependency.
    if not hasattr(self, "_eher_enabled"):
        self._eher_enabled = False
        self._eher_gating_enabled = False
        self._ha_fallback_timeout_ms = 1000.0
        self._prefills_last_ha_pending = deque()
        self._prefills_last_ha_pending_ts = {}
        self._ha_ready_head_tokens = set()
        self._recv_hint_sent = set()
        try:
            _ac = (
                getattr(self.vllm_config, "additional_config", None) or {}
            )
            _ec = _ac.get("edge_cloud_config", {}) if isinstance(_ac, dict) else {}
            _pd_cfg = _ec.get("pd_separation", {}) if isinstance(_ec, dict) else {}
            _pc = self.vllm_config.parallel_config
            if (
                _pd_cfg.get("enabled", False)
                and getattr(_pc, "is_edge_node", False)
            ):
                self._eher_enabled = bool(
                    # Default True matches PDSeparationConfig
                    # (enable_edge_hidden_early_recv default True).  The raw
                    # additional_config read must mirror the dataclass default,
                    # or the EngineCore gates P-tails while no guard thread /
                    # hint MQ exist (the executor reads the same key).
                    _pd_cfg.get("enable_edge_hidden_early_recv", True)
                )
                self._eher_gating_enabled = bool(
                    _pd_cfg.get(
                        "enable_edge_hidden_early_recv_gating", True
                    )
                ) and self._eher_enabled
                self._ha_fallback_timeout_ms = float(
                    _pd_cfg.get("ha_fallback_timeout_ms", 1000.0)
                )
            logger.info(
                "[EHER] init (lazy from additional_config): "
                "enabled=%s gating=%s fallback_ms=%.0f",
                self._eher_enabled,
                self._eher_gating_enabled,
                self._ha_fallback_timeout_ms,
            )
        except Exception:
            logger.exception(
                "[EHER] lazy-init failed; EHER disabled"
            )

    if getattr(self, "_pp_pd_channel", None) is None:
        # Still run the EHER drain/unlock so any acks received before the channel
        # is torn down do not strand gated P-tails.
        if getattr(self, "_eher_gating_enabled", False):
            self._drain_ha_acks_edge()
            self._unlock_prefills_last_with_ha()
        return
    if not (
        hasattr(self.scheduler, "prefills_last_ready")
        and hasattr(self.scheduler, "decodes_last_ready")
        and hasattr(self.scheduler, "prefill_drafts_last_ready")
        and hasattr(self.scheduler, "decode_drafts_last_ready")
    ):
        return
    new_outputs = self._pp_pd_channel.consume_new_outputs()
    for _seq, so in new_outputs:
        bt = so.batch_type
        logger.info(f"Received scheduler_output from cloud, batch_type: {bt}")
        if bt == BatchType.PREFILL_LAST:
            if getattr(self, "_eher_enabled", False) and getattr(
                so, "head_token", None
            ):
                # Gating is UNCONDITIONAL (regardless of decode work): the
                # edge worker is single-threaded, so an eagerly-scheduled
                # P-tail whose c2e hidden has not yet arrived occupies the
                # worker and starves the ahead-scheduled P首
                # (max_chunk_prefill_ahead=1).  With the cloud already
                # dispatched on that P首's PRE_OUT, the P首's e2c isend never
                # fires and the cloud blocks forever in its e2c recv -- a
                # full-pipeline deadlock (the be7c7039 regression; d46b0dc5
                # gated unconditionally and worked).  Parking the P-tail keeps
                # the worker free for P首s; it is unlocked on the ha_ack (c2e
                # irecv completed) or by the idle-only fallback in
                # _unlock_prefills_last_with_ha.
                if getattr(self, "_eher_gating_enabled", False):
                    self._enqueue_prefill_last_ha_pending(so)
                else:
                    # Gating off: fire the hint (guard thread posts irecv
                    # early for overlap) but keep P-tail immediately
                    # schedulable.
                    self._send_eher_recv_hint(so)
                    self.scheduler.prefills_last_ready.append(so)
            else:
                # EHER off / no head_token -> fully baseline (sync recv).
                self.scheduler.prefills_last_ready.append(so)
        elif bt == BatchType.DECODE_LAST:
            self.scheduler.decodes_last_ready.append(so)
        elif bt == BatchType.PREFILL_DRAFT_LAST:
            # 2026-08-12: the cloud publishes PREFILL_DRAFT_LAST via POST_OUT
            # after executing the head — the edge no longer self-posts the
            # prefill_draft tail (the cloud copied the per-request
            # draft_output_req_ids / is_last_prefill_chunk metadata onto the
            # echo).  The scheduler picks it like any other draft tail.
            self.scheduler.prefill_drafts_last_ready.append(so)
        elif bt == BatchType.DECODE_DRAFT_LAST:
            # The decode_draft tail is still self-posted by
            # _pick_draft_first_batch (like DECODE_LAST). If it arrives via
            # POST_OUT (e.g. from an older cloud that still publishes it),
            # drop it -- the edge already has its own copy in the decode
            # draft last queue.
            logger.debug(
                "Dropping POST_OUT %s head_token=%s "
                "(edge self-posts the decode draft tail)",
                bt.value,
                getattr(so, "head_token", None),
            )
        else:
            logger.error(
                "PD-separation POST_OUT received unexpected batch_type=%s; "
                "expected PREFILL_LAST, DECODE_LAST, or a draft LAST. "
                "Dropping.",
                bt.value if bt is not None else "<none>",
            )

    # [EHER §十五.3] After draining POST_OUT, drain acks and unlock gated
    # P-tails whose hidden has arrived (or whose fallback timeout elapsed).
    if getattr(self, "_eher_gating_enabled", False):
        self._drain_ha_acks_edge()
        self._unlock_prefills_last_with_ha()


def _enqueue_prefill_last_ha_pending(self, scheduler_output: SchedulerOutput) -> None:
    """Park a PREFILL_LAST in the gating pending set + fire its recv-hint.

    Idempotent on head_token: a duplicate POST_OUT (rare, e.g. ZMQ redelivery)
    does not double-enqueue.  The hint is fire-and-forget with timeout=0: if
    the guard thread's sideband MQ is full/slow we DROP the hint (mirrors the
    CHER rationale in passive_core.py) -- busy_loop then posts the irecv itself
    via get_or_post_early_recv, losing only the early-post overlap, never
    correctness.  The ack will still fire once that irecv completes.

    [Why PDSeparatedScheduler is NOT modified]
    The scheduler selects a P-tail solely by ``prefills_last_ready.popleft()``
    (pd_separated_scheduler.py:535 / :544).  Gating adds a precondition on *who
    enters* that queue: a gated PREFILL_LAST sits here (not in
    ``prefills_last_ready``) until its ack arrives, then
    ``_unlock_prefills_last_with_ha`` moves it in.  The scheduler's selection
    logic, priority order (LOW: P首 > D尾 > D首 > P尾 > Empty), and
    ``prefill_inflight_count`` state machine (incremented at P首 dispatch
    :778, decremented at P尾 completion :1336) are all untouched --
    ``_prefills_last_ha_pending`` is a third, independent state.  While a
    P-tail is gated (absent from prefills_last_ready) the scheduler naturally
    falls back to P首 / D首 / D尾 / Empty, which is exactly the bubble-fill we
    want.  Gating delays P-tail execution and hence the hidden-channel
    release (``release_prefill`` :1338), but that channel would be occupied
    for the same duration by a synchronous recv on a non-gated P-tail, so no
    new deadlock window is introduced.
    """
    ht = scheduler_output.head_token
    if ht is None:
        # No head_token -> cannot gate; fall back to immediate scheduling.
        self.scheduler.prefills_last_ready.append(scheduler_output)
        return
    if ht in self._prefills_last_ha_pending_ts:
        # Already pending (duplicate POST_OUT) -> do not re-enqueue/re-hint.
        return
    self._prefills_last_ha_pending.append(scheduler_output)
    self._prefills_last_ha_pending_ts[ht] = time.monotonic()
    self._send_eher_recv_hint(scheduler_output)


def _send_eher_recv_hint(self, scheduler_output: SchedulerOutput) -> None:
    """Fire a recv-hint so the edge worker guard thread posts the cloud->edge
    hidden irecv early.  Idempotent on head_token via ``_recv_hint_sent``.

    Called by both the gating path (``_enqueue_prefill_last_ha_pending``) and
    the non-gating early-recv path, so the hint/early-post overlap is present
    regardless of whether scheduling is gated.  Fire-and-forget with timeout=0:
    on a full/slow sideband MQ the hint is DROPPED (busy_loop then posts the
    irecv itself via get_or_post_early_recv) -- loses only the overlap, never
    correctness.
    """
    ht = scheduler_output.head_token
    if ht is None or ht in self._recv_hint_sent:
        return
    _channel = getattr(scheduler_output, "hidden_channel", None)
    _hint = {
        "head_token": ht,
        "hidden_channel": (_channel.value if _channel is not None else None),
        "num_tokens": scheduler_output.total_num_scheduled_tokens,
        # direction tag is informational only (logs); start_early_irecv ignores it.
        "direction": "cloud_to_edge",
    }
    _hint_mq = getattr(self.model_executor, "edge_recv_hint_mq", None)
    if _hint_mq is not None:
        try:
            _hint_mq.enqueue((b"pp_recv_hint", (_hint,), {}, None), timeout=0)
            self._recv_hint_sent.add(ht)
            logger.info(
                "[EHER] send recv-hint head_token=%s channel=%s gating=%s",
                ht, _hint["hidden_channel"],
                getattr(self, "_eher_gating_enabled", False),
            )
        except Exception:
            # MQ full/torn-down -> hint dropped; busy_loop will post the irecv
            # itself when the (gated) P-tail eventually runs (after unlock, or
            # immediately in the non-gating path).
            logger.debug(
                "[EHER] recv-hint dropped for head_token=%s "
                "(guard MQ full/down); will fallback to sync post", ht,
            )
    else:
        logger.debug(
            "[EHER] no edge_recv_hint_mq; head_token=%s gated on timeout only",
            ht,
        )


def _drain_ha_acks_edge(self) -> None:
    """Drain the ha_ack sideband MQ (guard thread -> edge EngineCore)."""
    _ack_mq = getattr(self.model_executor, "ha_ack_mq", None)
    if _ack_mq is None:
        return
    while True:
        try:
            _method, _args, _kw, _out = _ack_mq.dequeue(timeout=0)
        except TimeoutError:
            break
        except Exception:
            logger.exception("[EHER] ha_ack dequeue error")
            break
        if _method != b"ha_ack" or not _args:
            continue
        _ack = _args[0]
        _ht = _ack.get("head_token") if isinstance(_ack, dict) else None
        if _ht is None:
            continue
        self._ha_ready_head_tokens.add(_ht)
        _enq_ts = self._prefills_last_ha_pending_ts.get(_ht)
        if _enq_ts is not None:
            logger.info(
                "[EHER] ha_ack received head_token=%s ready_after_ms=%.1f",
                _ht, (time.monotonic() - _enq_ts) * 1000.0,
            )


def _unlock_prefills_last_with_ha(self) -> None:
    """Move gated P-tails whose ack arrived (or whose timeout elapsed) into
    ``prefills_last_ready`` so the scheduler may pick them."""
    if not self._prefills_last_ha_pending:
        return

    ready: list[SchedulerOutput] = []
    for so in list(self._prefills_last_ha_pending):
        ht = so.head_token
        if ht in self._ha_ready_head_tokens:
            ready.append(so)
    for so in ready:
        self.scheduler.prefills_last_ready.append(so)
        self._ha_ready_head_tokens.discard(so.head_token)
        self._prefills_last_ha_pending_ts.pop(so.head_token, None)
        self._prefills_last_ha_pending.remove(so)

    # Fallback: force-unlock any P-tail whose ack never arrived (guard thread
    # dead / hint dropped / HCCL is_completed() never observed).  Prevents
    # deadlock.  The worker then posts+waits the irecv synchronously in
    # _execute_model_edge_tail (EHER fallback), so results stay correct.
    now = time.monotonic()
    for so in list(self._prefills_last_ha_pending):
        ht = so.head_token
        _enq_ts = self._prefills_last_ha_pending_ts.get(ht, now)
        elapsed_ms = (now - _enq_ts) * 1000.0
        if elapsed_ms > self._ha_fallback_timeout_ms:
            logger.warning(
                "[EHER] gating fallback: head_token=%s ack timeout %.0fms, "
                "force-unlock (worker will sync-recv)", ht, elapsed_ms,
            )
            self.scheduler.prefills_last_ready.append(so)
            self._prefills_last_ha_pending.remove(so)
            self._prefills_last_ha_pending_ts.pop(ht, None)
            self._ha_ready_head_tokens.discard(ht)


def _maybe_publish_pre_out(
    self, scheduler_output: SchedulerOutput
) -> None:
    """Forward head-segment batches on the edge → cloud channel."""
    if getattr(self, "_pp_pd_channel", None) is None:
        return
    bt = scheduler_output.batch_type
    if bt in _DRAFT_HEAD_BATCH_TYPES:
        # Same deferral path for the per-domain variants: a pre-generated
        # chain head must wait for its cloud control stream to open before
        # its PRE_OUT fires.  The open/close bookkeeping
        # (_pd_draft_pre_out_open_tasks / _pd_deferred_draft_pre_out) is
        # keyed by draft_task_id, and task ids are globally unique, so the
        # prefill and decode domains can never tangle here (design §7.6
        # "按域拆分" is satisfied by task keying -- no per-domain set split
        # needed); the open condition is the same for both domains (parent
        # PL/DL tail finalize, see _advance_edge_cloud_draft).
        is_pregenerated = getattr(
            self.scheduler, "is_pre_generated_draft", lambda _so: False
        )(scheduler_output)
        if is_pregenerated:
            task_id = scheduler_output.draft_task_id
            assert task_id is not None
            opened = getattr(
                self, "_pd_draft_pre_out_open_tasks", None
            )
            if opened is None:
                opened = set()
                self._pd_draft_pre_out_open_tasks = opened
            if task_id not in opened:
                # Edge dispatch is intentionally independent of cloud
                # readiness. Queue every cloud control in task order so later
                # placeholder steps cannot overtake step 0 while its
                # accepted-token scalars are still being finalized.
                deferred = getattr(
                    self, "_pd_deferred_draft_pre_out", None
                )
                if deferred is None:
                    deferred = {}
                    self._pd_deferred_draft_pre_out = deferred
                deferred.setdefault(task_id, []).append(scheduler_output)
                return
        self._pp_pd_channel.publish(scheduler_output)
    elif bt in (
        BatchType.PREFILL_FIRST,
        BatchType.DECODE_FIRST,
    ):
        self._pp_pd_channel.publish(scheduler_output)
    elif bt in (
        BatchType.EMPTY,
        BatchType.PREFILL_LAST,
        BatchType.DECODE_LAST,
    ):
        return
    else:
        logger.debug(
            "PD-separation PRE_OUT skipping non-separated batch_type=%s",
            bt.value if bt is not None else "<none>",
        )


def _release_deferred_draft_pre_out(
    self, draft_task_id: str
) -> None:
    """Open one cloud draft control stream and flush it in FIFO order."""
    opened = getattr(self, "_pd_draft_pre_out_open_tasks", None)
    if opened is None:
        opened = set()
        self._pd_draft_pre_out_open_tasks = opened
    opened.add(draft_task_id)

    deferred = getattr(self, "_pd_deferred_draft_pre_out", None)
    queued = [] if deferred is None else deferred.pop(draft_task_id, [])
    channel = getattr(self, "_pp_pd_channel", None)
    if channel is None:
        return
    for scheduler_output in queued:
        channel.publish(scheduler_output)
    if queued:
        logger.info(
            "[PRE_OUT] released %d async draft controls task_id=%s",
            len(queued),
            draft_task_id,
        )


def _close_draft_pre_out(self, draft_task_id: str | None) -> None:
    if not draft_task_id:
        return
    opened = getattr(self, "_pd_draft_pre_out_open_tasks", None)
    if opened is not None:
        opened.discard(draft_task_id)
    deferred = getattr(self, "_pd_deferred_draft_pre_out", None)
    if deferred is not None:
        deferred.pop(draft_task_id, None)


def _ensure_pd_head_token(self, scheduler_output: SchedulerOutput) -> None:
    if getattr(self, "_pp_pd_channel", None) is None:
        return
    if scheduler_output.batch_type not in (
        BatchType.PREFILL_FIRST,
        BatchType.DECODE_FIRST,
        *_DRAFT_HEAD_BATCH_TYPES,
    ):
        return
    if not scheduler_output.head_token:
        scheduler_output.head_token = uuid4().hex


def _needs_sample_tokens(self, scheduler_output: SchedulerOutput) -> bool:
    """Return True if sample_tokens should follow execute_model for this
    batch.

    In edge-cloud PD-separation mode, only tail-segment batches (PL/DL)
    produce logits and need sampling. Head-segment batches (PF/DF) output
    intermediate hidden states and must skip sampling.
    """
    if getattr(self, "_pp_pd_channel", None) is None:
        return True
    bt = scheduler_output.batch_type
    return bt in (BatchType.PREFILL_LAST, BatchType.DECODE_LAST)


def _stash_empty_worker_cleanup(self, scheduler_output: SchedulerOutput) -> None:
    """Keep worker-side cleanup from EMPTY batches for the next real batch."""
    finished_req_ids = getattr(scheduler_output, "finished_req_ids", None)
    free_encoder_mm_hashes = getattr(scheduler_output, "free_encoder_mm_hashes", None)
    if not finished_req_ids and not free_encoder_mm_hashes:
        return

    pending_finished = getattr(self, "_pd_pending_finished_req_ids", None)
    if pending_finished is None:
        pending_finished = set()
        self._pd_pending_finished_req_ids = pending_finished
    pending_finished.update(finished_req_ids or ())

    pending_mm_hashes = getattr(self, "_pd_pending_free_encoder_mm_hashes", None)
    if pending_mm_hashes is None:
        pending_mm_hashes = set()
        self._pd_pending_free_encoder_mm_hashes = pending_mm_hashes
    pending_mm_hashes.update(free_encoder_mm_hashes or ())


def _merge_pending_worker_cleanup(self, scheduler_output: SchedulerOutput) -> None:
    """Attach cleanup skipped with EMPTY batches to the next worker batch."""
    pending_finished = getattr(self, "_pd_pending_finished_req_ids", None)
    if pending_finished:
        scheduler_output.finished_req_ids = set(
            scheduler_output.finished_req_ids
        ).union(pending_finished)
        pending_finished.clear()

    pending_mm_hashes = getattr(self, "_pd_pending_free_encoder_mm_hashes", None)
    if pending_mm_hashes:
        scheduler_output.free_encoder_mm_hashes = list(
            dict.fromkeys([
                *scheduler_output.free_encoder_mm_hashes,
                *pending_mm_hashes,
            ])
        )
        pending_mm_hashes.clear()


def _finish_empty_batch(self, scheduler_output: SchedulerOutput):
    """Complete an EMPTY SchedulerOutput without broadcasting to workers."""
    self._stash_empty_worker_cleanup(scheduler_output)
    self._process_aborts_queue()
    with (
        self.log_error_detail(scheduler_output),
        self.log_iteration_details(scheduler_output),
    ):
        engine_core_outputs = self.scheduler.update_from_output(
            scheduler_output, EMPTY_MODEL_RUNNER_OUTPUT
        )
    self._clear_pending_edge_cloud_draft_for_finished_requests()
    return engine_core_outputs, False


def _defer_empty_batch(self, scheduler_output: SchedulerOutput) -> None:
    """Defer an EMPTY batch when queued model work must complete first."""
    deferred = getattr(self, "_pd_deferred_empty_batches", None)
    if deferred is None:
        deferred = []
        self._pd_deferred_empty_batches = deferred
    deferred.append(scheduler_output)


def _pop_deferred_empty_batch(self) -> SchedulerOutput | None:
    deferred = getattr(self, "_pd_deferred_empty_batches", None)
    if not deferred:
        return None
    return deferred.pop(0)


def _advance_edge_cloud_draft(
    self,
    completed_scheduler_output: SchedulerOutput,
    model_output: ModelRunnerOutput,
) -> None:
    """Advance scheduled draft control state after a completed tail batch.

    Draft SchedulerOutputs are generated by PDSeparatedScheduler, matching
    DECODE_FIRST/DECODE_LAST ownership. Cloud-only step-0 sampling state is
    derived from the already-returned target output. In async mode final draft
    token IDs remain worker-local and the scheduler advances with placeholders.
    """
    if not getattr(self, "use_spec_decode", False):
        return
    enqueue_draft_first = getattr(
        self.scheduler, "enqueue_draft_first", None
    )
    if enqueue_draft_first is None:
        return

    batch_type = completed_scheduler_output.batch_type
    # Every prefill chunk must run the drafter to populate the MTP KV cache.
    # Mid-chunk sampled/draft tokens are discarded by the worker, but their
    # independently scheduled draft chain still needs to be finalized here.
    is_target_tail = batch_type in (
        BatchType.PREFILL_LAST,
        BatchType.DECODE_LAST,
    )
    if is_target_tail:
        state = getattr(model_output, "edge_cloud_draft_state", None)
        if state is None:
            return
        task_id = state["draft_task_id"]
        num_accepted_tokens = state.get("num_accepted_tokens")
        valid_sampled_token_count = state.get(
            "valid_sampled_token_count"
        )
        if num_accepted_tokens is None:
            # AsyncModelRunnerOutput has already materialized and filtered
            # sampled_token_ids before EngineCore receives it. Their row
            # lengths are exactly the accepted counts, so reuse that existing
            # D2H result instead of synchronizing a second copy in the edge
            # worker. The same counts drive async batch-state correction.
            num_accepted_tokens = [
                len(token_ids)
                for token_ids in model_output.sampled_token_ids
            ]
            valid_sampled_token_count = list(num_accepted_tokens)
        finalize = getattr(
            self.scheduler, "finalize_pre_generated_draft_first", None
        )
        if (
            batch_type in (
                BatchType.PREFILL_LAST,
                BatchType.DECODE_LAST,
            )
            and finalize is not None
        ):
            finalized = finalize(
                draft_task_id=task_id,
                num_accepted_tokens=num_accepted_tokens,
                valid_sampled_token_count=valid_sampled_token_count,
            )
            if finalized is not None:
                # This only opens the cloud control stream. Edge DRF/DRL
                # SchedulerOutputs were already dispatched independently and
                # never wait for accepted-token propagation.
                self._release_deferred_draft_pre_out(task_id)
                return
        enqueue_draft_first(
            completed_scheduler_output,
            draft_task_id=task_id,
            draft_step_idx=int(state["draft_step_idx"]),
            num_accepted_tokens=num_accepted_tokens,
            valid_sampled_token_count=valid_sampled_token_count,
        )
        return

    if batch_type not in (
        BatchType.PREFILL_DRAFT_LAST,
        BatchType.DECODE_DRAFT_LAST,
    ):
        return
    draft_step_idx = int(completed_scheduler_output.draft_step_idx or 0)
    if draft_step_idx + 1 >= getattr(
        self.scheduler, "num_spec_tokens", 0
    ):
        self._close_draft_pre_out(
            completed_scheduler_output.draft_task_id
        )
        # The draft chain has fully executed on the cloud; release the KV
        # blocks retained for requests that finished while the chain was
        # in flight.  Both *_DRAFT_LAST kinds reach this branch and both
        # are handled per-task (draft_task_id is globally unique), so the
        # prefill-domain chain additionally unblocking its prefill slot
        # (scheduler _finalize_prefill_slot on the edge, Phase B §5.2) is
        # independent of this cloud-side retention release (design §7.6
        # item 32 -- per-domain trigger is task-keyed, no shared state).
        release = getattr(
            self.scheduler, "release_draft_retained_blocks", None
        )
        task_id = completed_scheduler_output.draft_task_id
        if release is not None and task_id:
            release(task_id)
    draft_token_ids = getattr(
        model_output, "edge_cloud_draft_token_ids", None
    )
    if draft_token_ids is not None:
        self.scheduler.update_draft_token_ids(draft_token_ids)


def _clear_pending_edge_cloud_draft_for_finished_requests(self) -> None:
    """Push draft lifecycle events across the executor boundary.

    Two duties, both driven by scheduler-side state:
      1. Forward finished request ids to the edge worker so it can mark
         pending draft contexts.  A context is dropped there only when
         EVERY request of its parent batch has finished; partial finishes
         keep the chain — the cloud-side cached attention metadata is
         whole-batch and cannot be re-sliced.
      2. Drain draft task ids the scheduler cut from its ready queues:
         release their retained KV blocks, invalidate the cloud-side
         cached draft metadata, and force-drop any runner context still
         held for a cut chain.
    """
    if not getattr(self, "use_spec_decode", False):
        return
    finished_req_ids = set(
        getattr(self.scheduler, "finished_req_ids", set()) or ()
    )
    take_sched_dropped = getattr(
        self.scheduler, "take_dropped_draft_task_ids", None
    )
    sched_dropped = (
        take_sched_dropped() if take_sched_dropped is not None else []
    )
    release = getattr(
        self.scheduler, "release_draft_retained_blocks", None
    )
    if release is not None:
        for task_id in sched_dropped:
            release(task_id)
    invalidate = getattr(
        self.scheduler, "invalidate_cloud_draft_tasks", None
    )
    if invalidate is not None:
        invalidate(sched_dropped)
    if not finished_req_ids and not sched_dropped:
        return
    clear_pending = getattr(
        self.model_executor,
        "clear_pending_edge_cloud_draft_for_req_ids",
        None,
    )
    if clear_pending is not None:
        clear_pending(finished_req_ids, sched_dropped)


def _register_edge_cloud_draft_parent(
    self,
    scheduler_output: SchedulerOutput,
    model_output: ModelRunnerOutput,
) -> None:
    """Retain a parent request when its worker created a draft task."""
    if not getattr(self, "use_spec_decode", False):
        return
    if not self._uses_scheduled_edge_cloud_draft():
        return
    if scheduler_output.batch_type not in (
        BatchType.PREFILL_LAST,
        BatchType.DECODE_LAST,
    ):
        return
    # Pregeneration is only an optimization and can be skipped while another
    # draft chain occupies the local queue.  The worker state is authoritative:
    # _advance_edge_cloud_draft() will enqueue a fallback chain whenever this
    # state exists, so its parent KV must be retained even without a
    # pre-generated SchedulerOutput.
    state = getattr(model_output, "edge_cloud_draft_state", None)
    if state is None:
        return
    task_id = state.get("draft_task_id")
    parent_task_id = getattr(scheduler_output, "head_token", None)
    if task_id != parent_task_id:
        raise RuntimeError(
            "Edge-cloud draft parent task mismatch: "
            f"scheduler={parent_task_id}, worker={task_id}"
        )
    req_ids = set(scheduler_output.num_scheduled_tokens)
    register = getattr(
        self.scheduler, "register_edge_cloud_draft_task", None
    )
    if register is not None and task_id and req_ids:
        register(task_id, req_ids)


def _uses_scheduled_edge_cloud_draft(self) -> bool:
    speculative_config = self.vllm_config.speculative_config
    if (
        getattr(self, "_pp_pd_channel", None) is None
        or speculative_config is None
    ):
        return False
    method = getattr(speculative_config, "method", None)
    if method == "eagle3":
        return True
    if method in ("qwen3_5_mtp", "qwen_mtp"):
        return True
    if method != "mtp":
        return False
    hf_config = getattr(self.vllm_config.model_config, "hf_config", None)
    return "qwen" in str(getattr(hf_config, "model_type", "")).lower()


def _has_unresolved_edge_cloud_draft_parent(self) -> bool:
    """Keep async scheduling behind a prefill tail only.

    Async scheduled-MTP pre-generates the decode draft chain when DECODE_LAST
    is picked, so DECODE_LAST must not hold back local edge dispatch.
    """
    if not self._uses_scheduled_edge_cloud_draft():
        return False
    batch_queue = getattr(self, "batch_queue", None)
    if not batch_queue:
        return False
    for _future, scheduler_output, _exec_future in batch_queue:
        if (
            scheduler_output.batch_type == BatchType.PREFILL_LAST
            and getattr(scheduler_output, "is_last_prefill_chunk", True)
        ):
            is_pregenerated = getattr(
                self.scheduler,
                "is_pre_generated_draft",
                lambda _so: False,
            )(scheduler_output)
            if not is_pregenerated:
                return True
    return False


# =======================================================================#
# EngineCore.step — full replacement, mirrors upstream + dest inserts.    #
# =======================================================================#
def _patched_step(self):
    """Schedule, execute, and make output.

    Returns tuple of outputs and a flag indicating whether the model
    was executed.
    """
    # Check for any requests remaining in the scheduler - unfinished,
    # or finished and not yet removed from the batch.
    if not self.scheduler.has_requests():
        return {}, False

    # [ascend insert] Drain POST_OUT (cloud → edge) into the
    # PDSeparatedScheduler's tail-segment ready queues before scheduling.
    self._drain_pd_channel_inbox()

    scheduler_output = self.scheduler.schedule()
    self._ensure_pd_head_token(scheduler_output)

    # [ascend insert] Forward head-segment batches on the PRE_OUT
    # (edge → cloud) channel.
    self._maybe_publish_pre_out(scheduler_output)

    if scheduler_output.batch_type == BatchType.EMPTY:
        return self._finish_empty_batch(scheduler_output)

    self._merge_pending_worker_cleanup(scheduler_output)

    future = self.model_executor.execute_model(
        scheduler_output, non_block=True
    )
    grammar_output = self.scheduler.get_grammar_bitmask(scheduler_output)
    with (
        self.log_error_detail(scheduler_output),
        self.log_iteration_details(scheduler_output),
    ):
        model_output = _wait_worker_result_with_drain(self, future)
        if model_output is None:
            model_output = self.model_executor.sample_tokens(grammar_output)

    # Before processing the model output, process any aborts that happened
    # during the model execution.
    # Register the deferred draft before abort/model completion can free
    # requests referenced by this parent batch.
    self._register_edge_cloud_draft_parent(scheduler_output, model_output)
    self._process_aborts_queue()
    engine_core_outputs = self.scheduler.update_from_output(
        scheduler_output, model_output
    )
    self._advance_edge_cloud_draft(scheduler_output, model_output)
    self._clear_pending_edge_cloud_draft_for_finished_requests()

    return (
        engine_core_outputs,
        scheduler_output.total_num_scheduled_tokens > 0,
    )


def _wait_worker_result_with_drain(self, future: Future,
                                   poll_s: float = 0.05) -> ModelRunnerOutput:
    """Bounded wait for a worker result, draining the PD channel between polls.

    [PD deadlock hardening] A bare ``future.result()`` freezes the EngineCore
    for as long as the worker batch takes -- and while frozen,
    ``_drain_pd_channel_inbox`` never runs.  That drain is the only path that
    moves cloud POST_OUTs into the scheduler's ready queues and fires the EHER
    fallback unlock, so a slow (or stalled) worker batch would deadlock the
    whole prefill channel: PLs never arrive, ``prefills_last_ready`` stays
    empty, the cloud's next send-back on the channel blocks forever, and the
    edge can never issue the PF the cloud is waiting on.  Keeping the drain
    alive on a poll cadence lets the P-tail return path survive transient
    worker stalls and keeps the EHER 1s fallback firing.

    The multiproc ``FutureWrapper.result()`` (vllm/v1/executor/multiproc_
    executor.py) raises ``RuntimeError("timeout not implemented")`` for any
    non-None timeout, and with none it blocks draining the shared
    ``futures_queue`` on the response MQ -- so resolve the future on a daemon
    thread and poll ``done()`` on this thread instead.  ``FutureWrapper``
    extends ``concurrent.futures.Future``, so ``set_result`` (called from the
    waiter) is lock-protected and ``done()`` is visible here.  Exactly one
    waiter is active at a time -- the collect loop resolves batches strictly in
    queue order and the fill loop is idle during the wait -- so the
    ``futures_queue`` pop inside ``FutureWrapper.result`` cannot race another
    resolver.  On the hard-stall path the waiter parks in the MQ dequeue
    forever (a daemon thread), while this thread keeps draining.
    """
    waiter = threading.Thread(
        target=future.result, daemon=True, name="pd-result-waiter"
    )
    waiter.start()
    while not future.done():
        time.sleep(poll_s)
        self._drain_pd_channel_inbox()
    waiter.join()
    return future.result()


# =======================================================================#
# EngineCore.step_with_batch_queue — full replacement.                    #
# =======================================================================#
def _patched_step_with_batch_queue(self):
    """Continuously fill the local worker FIFO before collecting one result.

    Native async scheduling relies on queue order, not EngineCore seeing each
    token first.  Fill all currently derivable DF/DL/DRF/DRL controls up to
    the executor credit so short edge segments cannot drain the MQ between
    two EngineCore turns.
    """
    batch_queue = self.batch_queue
    assert batch_queue is not None

    assert len(batch_queue) < self.batch_queue_size

    model_executed = False
    fill_async_mtp_placeholders = getattr(
        self.scheduler,
        "_uses_async_scheduled_mtp_placeholders",
        lambda: False,
    )()
    deferred_scheduler_output: tuple[
        SchedulerOutput, Future
    ] | None = None

    while (
        len(batch_queue) < self.batch_queue_size
        and self.scheduler.has_requests()
        and not self._has_unresolved_edge_cloud_draft_parent()
    ):
        self._drain_pd_channel_inbox()
        scheduler_output = self.scheduler.schedule()
        self._ensure_pd_head_token(scheduler_output)

        # [ascend insert] Publish head-segment batches immediately at
        # schedule time to keep the pipeline full.
        if scheduler_output.batch_type in (
            BatchType.PREFILL_FIRST,
            BatchType.DECODE_FIRST,
            *_DRAFT_HEAD_BATCH_TYPES,
        ):
            self._maybe_publish_pre_out(scheduler_output)

        if scheduler_output.batch_type == BatchType.EMPTY:
            if batch_queue:
                self._defer_empty_batch(scheduler_output)
                break
            return self._finish_empty_batch(scheduler_output)

        self._merge_pending_worker_cleanup(scheduler_output)
        with self.log_error_detail(scheduler_output):
            exec_future = self.model_executor.execute_model(
                scheduler_output, non_block=True
            )

        scheduled_model_executed = False
        if self.is_ec_consumer:
            scheduled_model_executed = (
                scheduler_output.total_num_scheduled_tokens > 0
            )
            model_executed |= scheduled_model_executed

        if self.is_pooling_model or not scheduled_model_executed:
            future = cast(Future[ModelRunnerOutput], exec_future)
        elif not self._needs_sample_tokens(scheduler_output):
            future = cast(Future[ModelRunnerOutput], exec_future)
        elif not scheduler_output.pending_structured_output_tokens:
            grammar_output = self.scheduler.get_grammar_bitmask(
                scheduler_output
            )
            future = self.model_executor.sample_tokens(
                grammar_output, non_block=True
            )
        else:
            # This execute must remain ordered in the worker MQ, but sampling
            # waits until the prior async output updates grammar state.
            deferred_scheduler_output = (
                scheduler_output,
                cast(Future, exec_future),
            )
            break

        batch_queue.appendleft((future, scheduler_output, exec_future))
        queue_types = [
            so.batch_type.value
            for _, so, _ in batch_queue
        ]
        logger.info(
            "[BATCH_QUEUE] Enqueued %s, queue_len=%d, types=%s",
            scheduler_output.batch_type.value,
            len(batch_queue),
            queue_types,
        )
        if not fill_async_mtp_placeholders:
            # Preserve the upstream one-schedule-per-turn behavior for every
            # other mode. Only async scheduled-MTP needs one EngineCore turn
            # to materialize the complete placeholder chain.
            if (
                scheduled_model_executed
                and len(batch_queue) < self.batch_queue_size
                and not batch_queue[-1][0].done()
            ):
                return None, True
            break

    if not batch_queue:
        # No completed/in-flight batch is available to collect. This can
        # happen while waiting for a remote prefill tail.
        return None, model_executed

    # Block until the next result is available.
    future, scheduler_output, exec_model_fut = batch_queue.pop()
    bt = scheduler_output.batch_type
    logger.info(
        "[PD] EngineCore blocking on future.result(): "
        "batch_type=%s total_tokens=%d",
        bt.value if bt else "N/A",
        scheduler_output.total_num_scheduled_tokens)
    with (
        self.log_error_detail(scheduler_output),
        self.log_iteration_details(scheduler_output),
    ):
        model_output = _wait_worker_result_with_drain(self, future)
        if model_output is None:
            exec_model_fut.result()
            raise RuntimeError("unexpected error")

    # Register the deferred draft before abort/model completion can free
    # requests referenced by this parent batch.
    self._register_edge_cloud_draft_parent(scheduler_output, model_output)
    self._process_aborts_queue()
    engine_core_outputs = self.scheduler.update_from_output(
        scheduler_output, model_output
    )
    self._advance_edge_cloud_draft(scheduler_output, model_output)
    self._clear_pending_edge_cloud_draft_for_finished_requests()

    if deferred_empty_batch := self._pop_deferred_empty_batch():
        empty_outputs, _ = self._finish_empty_batch(deferred_empty_batch)
        if empty_outputs:
            if engine_core_outputs:
                for client_index, output in empty_outputs.items():
                    existing = engine_core_outputs.get(client_index)
                    if existing is None:
                        engine_core_outputs[client_index] = output
                    elif output.finished_requests:
                        existing_finished = existing.finished_requests or set()
                        existing.finished_requests = existing_finished.union(
                            output.finished_requests
                        )
            else:
                engine_core_outputs = empty_outputs

    if deferred_scheduler_output is not None:
        deferred_output, deferred_exec_future = deferred_scheduler_output
        if (
            self.use_spec_decode
            and not self._uses_scheduled_edge_cloud_draft()
        ):
            draft_token_ids = self.model_executor.take_draft_token_ids()
            if draft_token_ids is not None:
                self.scheduler.update_draft_token_ids_in_output(
                    draft_token_ids, deferred_output
                )
        grammar_output = self.scheduler.get_grammar_bitmask(
            deferred_output
        )
        deferred_future = self.model_executor.sample_tokens(
            grammar_output, non_block=True
        )
        batch_queue.appendleft(
            (
                deferred_future,
                deferred_output,
                deferred_exec_future,
            )
        )

    return engine_core_outputs, model_executed


# =======================================================================#
# EngineCore.shutdown — close PD/ZMQ resources before stopping the rest.  #
# =======================================================================#
@functools.wraps(_ORIG_ENGINE_CORE_SHUTDOWN)
def _patched_engine_core_shutdown(self):
    ch = getattr(self, "_pp_pd_channel", None)
    if ch is not None:
        try:
            ch.shutdown()
        except Exception:
            logger.exception(
                "Error while shutting down PD-separation ZMQ channel"
            )
        self._pp_pd_channel = None

    _ORIG_ENGINE_CORE_SHUTDOWN(self)


# =======================================================================#
# EngineCoreProc.run_engine_core — keep child-process patch import.       #
# =======================================================================#
def _patched_run_engine_core(*args, dp_rank: int = 0, local_dp_rank: int = 0,
                             **kwargs):
    """Delegate to upstream while keeping this patch module as the process
    target so spawn-based child processes import and install the patches.
    """
    return _ORIG_RUN_ENGINE_CORE(
        *args, dp_rank=dp_rank, local_dp_rank=local_dp_rank, **kwargs
    )


_patched_run_engine_core.__module__ = __name__
_patched_run_engine_core.__qualname__ = "_patched_run_engine_core"


# =======================================================================#
# EngineCoreProc._process_input_queue — full replacement to add the       #
# edge-cloud idle-block branch.                                            #
# =======================================================================#
# Imports kept inside the function-scope dict to mirror the upstream
# module-level imports (`queue`, `DEBUG`) without polluting our patch
# module's top-level namespace.
import queue as _queue_mod  # noqa: E402
import time as _time  # noqa: E402
from logging import DEBUG as _DEBUG  # noqa: E402


def _patched_process_engine_step(self) -> bool:
    """Avoid adding a 1 ms bubble while async batches are still in flight."""
    outputs, model_executed = self.step_fn()
    for output in outputs.items() if outputs else ():
        self.output_queue.put_nowait(output)
    self.post_step(model_executed)
    async_mtp_in_flight = bool(self.batch_queue) and getattr(
        self.scheduler,
        "_uses_async_scheduled_mtp_placeholders",
        lambda: False,
    )()
    if (
        not model_executed
        and self.scheduler.has_unfinished_requests()
        and not async_mtp_in_flight
    ):
        _time.sleep(0.001)
    return model_executed


def _patched_process_input_queue(self):
    """Exits when an engine step needs to be performed."""
    waited = False
    while not self.has_work() and self.is_running():
        # Notify callbacks waiting for engine to become idle.
        self._notify_idle_state_callbacks()
        if self.input_queue.empty():
            with self.aborts_queue.mutex:
                self.aborts_queue.queue.clear()
            if logger.isEnabledFor(_DEBUG):
                logger.debug("EngineCore waiting for work.")
                waited = True
        block = self.process_input_queue_block

        # [ascend insert] In edge-cloud mode the edge can be completely
        # idle for long periods while waiting for the next client
        # request. If no local work exists, force a blocking wait even
        # if an earlier mode (e.g. elastic scaling) left the input queue
        # in non-blocking polling mode; otherwise the outer busy loop
        # spins forever.
        if (
            not block
            and not self.scheduler.has_unfinished_requests()
            and not self.engines_running
            and not bool(self.batch_queue)
            and getattr(self, "eep_scaling_state", None) is None
        ):
            block = True

        try:
            if block and self.input_queue.empty():
                logger.info("input_queue is empty, EngineCore waiting for work.")
            req = self.input_queue.get(block=block)
            self._handle_client_request(*req)
        except _queue_mod.Empty:
            break
        if not block:
            break

    if waited:
        logger.debug("EngineCore loop active.")

    # Handle any more client requests.
    while not self.input_queue.empty():
        req = self.input_queue.get_nowait()
        self._handle_client_request(*req)


# =======================================================================#
# Install                                                                  #
# =======================================================================#
def install() -> None:
    if getattr(EngineCore, _INSTALLED_FLAG, False):
        return

    EngineCore.__init__ = _patched_engine_core_init
    EngineCore._drain_pd_channel_inbox = _drain_pd_channel_inbox
    EngineCore._enqueue_prefill_last_ha_pending = _enqueue_prefill_last_ha_pending
    EngineCore._send_eher_recv_hint = _send_eher_recv_hint
    EngineCore._drain_ha_acks_edge = _drain_ha_acks_edge
    EngineCore._unlock_prefills_last_with_ha = _unlock_prefills_last_with_ha
    EngineCore._maybe_publish_pre_out = _maybe_publish_pre_out
    EngineCore._release_deferred_draft_pre_out = (
        _release_deferred_draft_pre_out
    )
    EngineCore._close_draft_pre_out = _close_draft_pre_out
    EngineCore._ensure_pd_head_token = _ensure_pd_head_token
    EngineCore._needs_sample_tokens = _needs_sample_tokens
    EngineCore._stash_empty_worker_cleanup = _stash_empty_worker_cleanup
    EngineCore._merge_pending_worker_cleanup = _merge_pending_worker_cleanup
    EngineCore._finish_empty_batch = _finish_empty_batch
    EngineCore._defer_empty_batch = _defer_empty_batch
    EngineCore._pop_deferred_empty_batch = _pop_deferred_empty_batch
    EngineCore._advance_edge_cloud_draft = _advance_edge_cloud_draft
    EngineCore._clear_pending_edge_cloud_draft_for_finished_requests = (
        _clear_pending_edge_cloud_draft_for_finished_requests
    )
    EngineCore._register_edge_cloud_draft_parent = (
        _register_edge_cloud_draft_parent
    )
    EngineCore._uses_scheduled_edge_cloud_draft = (
        _uses_scheduled_edge_cloud_draft
    )
    EngineCore._has_unresolved_edge_cloud_draft_parent = (
        _has_unresolved_edge_cloud_draft_parent
    )
    EngineCore.step = _patched_step
    EngineCore.step_with_batch_queue = _patched_step_with_batch_queue
    EngineCore.shutdown = _patched_engine_core_shutdown

    EngineCoreProc.run_engine_core = staticmethod(_patched_run_engine_core)
    EngineCoreProc._process_input_queue = _patched_process_input_queue
    EngineCoreProc._process_engine_step = _patched_process_engine_step

    setattr(EngineCore, _INSTALLED_FLAG, True)
    logger.info(
        "vllm-ascend EngineCore PD/edge-cloud patch installed."
    )


install()

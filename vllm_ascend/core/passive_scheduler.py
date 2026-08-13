# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""Passive scheduler for non-leader PP ranks.

A `PassiveScheduler` does not make scheduling decisions. It receives
SchedulerOutputs that have already been decided by the leader rank (rank 0)
over a ZMQ subscriber, classifies them by `batch_type`, and emits ready-to-
dispatch payloads — optionally splitting prefill / PD-mix batches into N
layer slices based on a YAML config.

The class is intentionally minimal: it shares no implementation with
`vllm.v1.core.sched.scheduler.Scheduler` and depends only on the public
`SchedulerOutput` / `BatchType` types.
"""
import enum
import math
import os
import queue
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple

from vllm import envs
from vllm.logger import logger
from vllm.v1.core.sched.output import BatchType, SchedulerOutput

if TYPE_CHECKING:
    from vllm.config import VllmConfig
    from vllm.v1.engine.core import PPSchedulerZmqSubscriber


class DispatchPolicy(enum.Enum):
    """Order in which phase queues are drained inside :meth:`PassiveScheduler.schedule`.

    The three phase queues — PURE_PREFILL, PD_MIX, PURE_DECODE — are polled
    in the order encoded by the policy. One SchedulerOutput is picked per
    non-empty queue per call.
    """
    EXPECT_ALTERNATION = "expect_alternation"  # Phase C: CloudUndesiredState machine (design §6.5).
    PREFILL_FIRST = "prefill_first"   # P  → PD-mix → D
    DECODE_FIRST = "decode_first"     # D  → PD-mix → P
    PDMIX_FIRST = "pdmix_first"       # PD-mix → P → D


class CloudUndesiredState(enum.Enum):
    """Cloud-side three-state "undesired" machine (design §6.5.1).

    Each state names the domain whose work was just served (or which
    should yield): its work is pushed to the tail of the priority table
    so the other channel gets the next dispatch, keeping the prefill and
    DECODE channel data planes busy in parallel.  State persists across
    ticks — it encodes "which domain the next tick should prefer".
    """
    UNDESIRED_PREFILL = "undesired_prefill"
    UNDESIRED_PD = "undesired_pd"
    UNDESIRED_DECODE_OR_DD = "undesired_decode_or_dd"


@dataclass
class LayerSliceInfo:
    """Metadata for a single layer slice in layerwise-disaggregated execution.

    When layer slicing is enabled, the PassiveScheduler splits the local
    layer range of a single SchedulerOutput into N slices. Each slice carries
    this info so the worker / model_runner can run only the assigned layer
    range and decide whether to perform PP communication.
    """
    slice_index: int       # 0, 1, 2, ...
    total_slices: int      # N
    start_layer: int       # local start layer (0-based within local layers)
    end_layer: int         # local end layer
    is_first_slice: bool   # slice_index == 0
    is_last_slice: bool    # slice_index == total_slices - 1


@dataclass
class ScheduledBatch:
    """Output of `PassiveScheduler.schedule()`: one SchedulerOutput plus the
    layer slices to dispatch in this engine tick.

    - For PURE_DECODE / DECODE_FIRST batches, or when slicing is disabled:
      ``slices == [None]`` (single full-layer execution).
    - For sliced PURE_PREFILL / PREFILL_FIRST / PD_MIX batches, ``schedule()``
      returns a single ``LayerSliceInfo`` per call so decode batches can be
      interleaved between prefill middle-layer slices.

    An empty instance (``slices == []``) signals that no SchedulerOutput was
    available to dispatch this round; the caller should typically idle.
    """
    scheduler_output: SchedulerOutput
    slices: list["LayerSliceInfo | None"]

    @classmethod
    def empty(cls) -> "ScheduledBatch":
        return cls(scheduler_output=None, slices=[])  # type: ignore[arg-type]

    def is_empty(self) -> bool:
        return not self.slices


class SliceTask(NamedTuple):
    scheduler_output: SchedulerOutput
    slice_info: LayerSliceInfo | None


class PassiveScheduler:
    """Receive → classify → schedule, for non-leader PP ranks.

    Lifecycle (each tick of the engine-core main loop):

        passive_scheduler.poll_and_classify()
        batch = passive_scheduler.schedule()
        if not batch.is_empty():
            for slice_info in batch.slices:
                executor.rpc_broadcast_mq.enqueue(...)

    `schedule()` returns a `ScheduledBatch` with 1 SchedulerOutput plus
    the slice plan; a single PURE_PREFILL / PD_MIX batch may carry N
    layer slices, while PURE_DECODE / DECODE_FIRST batches always carry
    `[None]` (single full-layer execution).
    """

    _ARRIVAL_SEQ_ATTR = "_passive_scheduler_arrival_seq"

    def __init__(
        self,
        vllm_config: "VllmConfig",
        pp_subscriber: "PPSchedulerZmqSubscriber",
        dispatch_policy: DispatchPolicy = DispatchPolicy.EXPECT_ALTERNATION,
        run_subscriber_thread: bool = True,
    ) -> None:
        self.pp_subscriber = pp_subscriber
        self.dispatch_policy = dispatch_policy
        # Phase C initial state (§6.5.1): the first thing to reach the cloud
        # is always a prefill (draft chains only exist after a parent tail),
        # and UNDESIRED_DECODE_OR_DD serves prefill at priority 2 without the
        # throttle; a decode-first cold start (abnormal/recovery) still works
        # via priority 3/4.
        self.cloud_scheduling_state = (
            CloudUndesiredState.UNDESIRED_DECODE_OR_DD
        )

        self.ready_prefills: deque[SchedulerOutput] = deque()
        self.ready_pdmixes: deque[SchedulerOutput] = deque()
        # Phase C (design §6.5.4): draft heads split by domain — prefill
        # drafts ride the prefill channel, decode drafts the DECODE channel.
        self.ready_prefill_drafts: deque[SchedulerOutput] = deque()
        self.ready_decode_drafts: deque[SchedulerOutput] = deque()
        self.ready_decodes: deque[SchedulerOutput] = deque()

        # Active sliced prefill / PD-mix continuation.  Only one sliced
        # prefill-like batch is allowed to be active at a time because the
        # Ascend model runner keeps layerwise continuation state in single
        # ``_layerwise_*`` fields.  Decode batches may be interleaved between
        # these continuation slices; another prefill-like slice-0 may not.
        self._active_sliced_prefill: SchedulerOutput | None = None
        self._active_prefill_slices: deque[SliceTask] = deque()

        # Cloud-side P/D interleave guard. After dispatching one prefill-middle
        # slice, EXPECT_EXECUTE_DECODE_OR_DRAFT waits up to 10ms for a decode-middle
        # batch before falling back to another prefill-middle slice.
        self._prefill_middle_throttle_started_at: float | None = None
        self._prefill_middle_throttle_seconds = 0.010

        # Whether the prefill_draft domain exists on this deployment (MTP
        # speculative decoding).  Without MTP there is no Prefill_Draft work
        # at all, so the state machine must not park in UNDESIRED_PD (whose
        # priority-3 prefill_draft check can then never fire) after a P tail
        # slice — UNDESIRED_PREFILL is the correct continuation instead.
        # Mirrors platform._is_mtp_speculative_config: only the MTP family of
        # methods produces prefill_draft chains here.
        _spec_cfg = getattr(vllm_config, "speculative_config", None)
        _spec_method = getattr(_spec_cfg, "method", None)
        self._mtp_enabled = bool(
            _spec_method is not None and "mtp" in str(_spec_method).lower()
        )

        # Bridge queue between the (optional) subscriber thread and the
        # main loop. When the thread is enabled, it drains
        # `pp_subscriber.consume_new_outputs()` and pushes each SchedulerOutput
        # into `_inbox`; `poll_and_classify` drains `_inbox` instead of
        # touching the subscriber directly.
        self._inbox: queue.Queue[tuple[int, SchedulerOutput]] = queue.Queue()
        self._subscriber_thread: threading.Thread | None = None
        self._shutdown_event = threading.Event()

        # [DIAG] Track DECODE_FIRST arrival intervals on the cloud side.
        self._last_decode_first_arrival_ts: float | None = None

        # Precompute local layer count.  The actual slice count is resolved
        # per-batch from a YAML config (token threshold -> slice count).
        self._num_local_layers = 0
        self._layer_slice_config: dict[int, int] | None = None
        self._layer_slice_config_mtime: float = 0.0
        self._layer_slice_config_path: str | None = None
        # Use hf_text_config (not the root hf_config) so multimodal models
        # whose layer count lives in a nested text sub-config (e.g. KimiK2.5
        # -> DeepseekV3Config) resolve correctly. For plain-text models
        # hf_text_config == hf_config, so this is a no-op there.
        num_hidden_layers = (
            vllm_config.model_config.hf_text_config.num_hidden_layers
        )
        pp_size = vllm_config.parallel_config.pipeline_parallel_size
        if vllm_config.parallel_config.enable_edge_cloud:
            head_k = tail_k = 1
            additional_config = getattr(
                vllm_config, "additional_config", None
            )
            if isinstance(additional_config, dict):
                ec_cfg = additional_config.get("edge_cloud_config", {})
                htl = ec_cfg.get("edge_head_tail_layers", 1)
                if isinstance(htl, int):
                    head_k = tail_k = htl
                elif isinstance(htl, (list, tuple)) and len(htl) >= 2:
                    head_k = int(htl[0])
                    tail_k = int(htl[1])
            self._num_local_layers = max(
                0, num_hidden_layers - head_k - tail_k
            )
        else:
            from vllm.distributed.utils import get_pp_indices
            start_layer_pp, end_layer = get_pp_indices(
                num_hidden_layers, pp_size - 1, pp_size
            )
            self._num_local_layers = end_layer - start_layer_pp

        if self._num_local_layers > 0:
            cfg = self._load_layer_slice_config()
            if cfg is not None:
                self._layer_slice_config = cfg
                logger.info(
                    f"[PassiveScheduler] Layer-slice config loaded: "
                    f"{self._layer_slice_config}",
                )
            else:
                logger.info(
                    "[PassiveScheduler] Layer-slice YAML not found; "
                    "layer slicing is disabled.",
                )

        if run_subscriber_thread:
            self.start_subscriber_thread()

    # ------------------------------------------------------------------ #
    # Subscriber thread lifecycle                                        #
    # ------------------------------------------------------------------ #
    def start_subscriber_thread(self) -> None:
        """Spawn a daemon thread that pulls from the ZMQ subscriber and
        pushes SchedulerOutputs into `_inbox`. Idempotent.
        """
        if self._subscriber_thread is not None:
            return
        self._shutdown_event.clear()
        self._subscriber_thread = threading.Thread(
            target=self._subscriber_loop,
            name="PassiveScheduler-Subscriber",
            daemon=True,
        )
        self._subscriber_thread.start()
        logger.debug("PassiveScheduler subscriber thread started.")

    def _subscriber_loop(self) -> None:
        while not self._shutdown_event.is_set():
            try:
                new_outputs = self.pp_subscriber.consume_new_outputs()
            except Exception:
                if self._shutdown_event.is_set():
                    return
                logger.exception(
                    "PassiveScheduler subscriber thread failed to consume."
                )
                return
            if not new_outputs:
                # Avoid a tight spin when the subscriber returns nothing.
                self._shutdown_event.wait(0.001)
                continue
            for seq, scheduler_output in new_outputs:
                self._inbox.put((seq, scheduler_output))

    def shutdown(self) -> None:
        """Signal the subscriber thread to stop and join it."""
        self._shutdown_event.set()
        thread = self._subscriber_thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=1.0)
        self._subscriber_thread = None

    # ------------------------------------------------------------------ #
    # Inbox draining + classification                                    #
    # ------------------------------------------------------------------ #
    def poll_and_classify(self) -> None:
        """Drain SchedulerOutputs from the inbox (fed by the subscriber
        thread, or directly by `_drain_subscriber_inline` when the thread
        is disabled) and route each into its phase-specific ready queue.
        """
        if self._subscriber_thread is None:
            # Inline mode: pull from the subscriber directly into _inbox.
            self._drain_subscriber_inline()

        while True:
            try:
                seq, scheduler_output = self._inbox.get_nowait()
            except queue.Empty:
                break
            self._remember_arrival_seq(scheduler_output, seq)
            bt = scheduler_output.batch_type
            # logger.info(
            #     "Received scheduler_output from edge, seq=%d, batch_type: %s",
            #     seq,
            #     bt,
            # )
            if bt == BatchType.EMPTY:
                continue
            elif bt in (BatchType.PURE_PREFILL, BatchType.PREFILL_FIRST):
                # PREFILL_FIRST = edge-cloud "P first" head segment; from the
                # cloud's perspective it is exactly the same workload as a
                # legacy PURE_PREFILL batch (run middle layers, send hidden
                # state back), so route into the same ready queue.
                self.ready_prefills.append(scheduler_output)
            elif bt in (BatchType.PURE_DECODE, BatchType.DECODE_FIRST):
                # Same reasoning as above for decode head segments.
                now = time.monotonic()
                if self._last_decode_first_arrival_ts is not None:
                    interval_ms = (now - self._last_decode_first_arrival_ts) * 1000
                    logger.info(
                        "DECODE_FIRST arrival interval: %.2f ms",
                        interval_ms,
                    )
                self._last_decode_first_arrival_ts = now
                self.ready_decodes.append(scheduler_output)
            elif bt in (BatchType.PREFILL_DRAFT_FIRST,):
                # Phase C (design §6.5.4): prefill drafts ride the prefill
                # channel — own queue, checked at its own state-machine slot.
                self.ready_prefill_drafts.append(scheduler_output)
            elif bt == BatchType.DECODE_DRAFT_FIRST:
                self.ready_decode_drafts.append(scheduler_output)
            elif bt in (
                BatchType.PREFILL_LAST,
                BatchType.DECODE_LAST,
                BatchType.PREFILL_DRAFT_LAST,
                BatchType.DECODE_DRAFT_LAST,
            ):
                # Tail-segment batches are edge-only and must never be
                # dispatched on the cloud. If one shows up here it is a
                # routing bug at the publisher side — drop with a loud log.
                logger.error(
                    "PassiveScheduler received tail-segment batch_type=%s; "
                    "tail segments are edge-only and will be dropped.",
                    bt.value,
                )
                continue
            else:  # PD_MIX (or anything unrecognized — treat as mix)
                self.ready_pdmixes.append(scheduler_output)
            logger.debug(
                "PassiveScheduler classified seq=%s batch_type=%s "
                "(prefills=%d, pdmixes=%d, prefill_drafts=%d, "
                "decode_drafts=%d, decodes=%d)",
                self._arrival_seq(scheduler_output),
                bt.value if bt is not None else "<none>",
                len(self.ready_prefills),
                len(self.ready_pdmixes),
                len(self.ready_prefill_drafts),
                len(self.ready_decode_drafts),
                len(self.ready_decodes),
            )

    def _remember_arrival_seq(
        self, scheduler_output: SchedulerOutput, seq: int
    ) -> None:
        try:
            setattr(scheduler_output, self._ARRIVAL_SEQ_ATTR, seq)
        except Exception:
            logger.debug(
                "Unable to attach arrival seq=%d to SchedulerOutput.",
                seq,
                exc_info=True,
            )

    def _arrival_seq(self, scheduler_output: SchedulerOutput) -> int | None:
        seq = getattr(scheduler_output, self._ARRIVAL_SEQ_ATTR, None)
        return seq if isinstance(seq, int) else None

    def _drain_subscriber_inline(self) -> None:
        """Used only when the subscriber thread is disabled (e.g. tests)."""
        new_outputs = self.pp_subscriber.consume_new_outputs()
        for seq, scheduler_output in new_outputs:
            self._inbox.put((seq, scheduler_output))

    # ------------------------------------------------------------------ #
    # Layer-slice config loading                                         #
    # ------------------------------------------------------------------ #
    def _load_layer_slice_config(self) -> dict[int, int] | None:
        """Load token-threshold -> slice-count mapping from YAML.

        The YAML is expected to contain entries like::

            16: 24
            8: 10
            4: 4
            1: 5
            0: 5

        where the key is the token count in *thousands* and the value is
        the total number of slices.

        The file path resolution order is:
        1. ``VLLM_LAYER_SLICE_CONFIG`` env var if set.
        2. ``layer_slice_config.yaml`` in the same directory as this module.

        On success the path and mtime are cached on ``self`` for hot-reload
        tracking.  Returns ``None`` when the file does not exist or cannot
        be parsed.
        """
        yaml_path = os.environ.get("VLLM_LAYER_SLICE_CONFIG")
        if yaml_path is None:
            yaml_path = os.path.join(
                os.path.dirname(__file__), "layer_slice_config.yaml"
            )
        if not os.path.exists(yaml_path):
            self._layer_slice_config_path = None
            self._layer_slice_config_mtime = 0.0
            return None
        try:
            import yaml
            with open(yaml_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
            if not isinstance(raw, dict):
                logger.warning(
                    "Layer-slice config %s is not a dict; ignoring.", yaml_path
                )
                return None
            # Extract optional prefill_middle_throttle_ms (milliseconds) before filtering.
            _throttle_key = "prefill_middle_throttle_ms"
            if _throttle_key in raw:
                try:
                    self._prefill_middle_throttle_seconds = float(raw[_throttle_key]) / 1000.0
                    logger.info(
                        "[PassiveScheduler] %s set to %.1f ms (%.3f s) from %s",
                        _throttle_key, float(raw[_throttle_key]),
                        self._prefill_middle_throttle_seconds, yaml_path,
                    )
                except (ValueError, TypeError):
                    logger.warning(
                        "Invalid %s value %r in %s; keeping %.3f s",
                        _throttle_key, raw[_throttle_key], yaml_path,
                        self._prefill_middle_throttle_seconds,
                    )

            # Normalize to int keys / values and sort descending by token threshold.
            config = {
                int(k): int(v) for k, v in raw.items() if isinstance(k, (int, str)) and str(k).lstrip('-').isdigit()
            }
            self._layer_slice_config_path = yaml_path
            self._layer_slice_config_mtime = os.path.getmtime(yaml_path)
            return dict(sorted(config.items(), key=lambda item: item[0], reverse=True))
        except Exception:
            logger.exception("Failed to load layer-slice config from %s", yaml_path)
            return None

    def _maybe_hot_reload_layer_slice_config(self) -> None:
        """Check whether the YAML config file has changed on disk and reload."""
        path = self._layer_slice_config_path
        if path is None:
            return
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            return
        if mtime != self._layer_slice_config_mtime:
            new_cfg = self._load_layer_slice_config()
            if new_cfg is not None:
                self._layer_slice_config = new_cfg
                logger.info(
                    f"[PassiveScheduler] Layer-slice config hot-reloaded: "
                    f"{self._layer_slice_config}",
                )

    def _resolve_slice_count(self, total_tokens: int) -> int:
        """Map a prefill batch size (in tokens) to the desired slice count.

        Uses the loaded YAML config (token-threshold in **thousands** ->
        slice-count).  The thresholds are checked from largest to smallest;
        the first threshold that ``total_tokens`` meets or exceeds wins.

        If no YAML config is present, layer slicing is disabled.
        """
        self._maybe_hot_reload_layer_slice_config()
        if self._layer_slice_config is not None:
            for token_k, slice_num in self._layer_slice_config.items():
                if total_tokens >= token_k * 1000:
                    return slice_num
        return 0

    # ------------------------------------------------------------------ #
    # Slicing                                                            #
    # ------------------------------------------------------------------ #
    def _make_slice_info(
        self,
        slice_idx: int,
        total_slices: int,
        boundaries: list[tuple[int, int]],
    ) -> LayerSliceInfo:
        slice_start, slice_end = boundaries[slice_idx]
        return LayerSliceInfo(
            slice_index=slice_idx,
            total_slices=total_slices,
            start_layer=slice_start,
            end_layer=slice_end,
            is_first_slice=(slice_idx == 0),
            is_last_slice=(slice_idx == total_slices - 1),
        )

    def _do_slice(
        self, so: SchedulerOutput
    ) -> list["LayerSliceInfo | None"]:
        """Compute layer slices for a prefill-like batch."""
        total_slices = self._resolve_slice_count(
            so.total_num_scheduled_tokens
        )
        if total_slices <= 1:
            return [None]
        boundaries = self._compute_slice_boundaries(
            self._num_local_layers, total_slices
        )
        return [
            self._make_slice_info(i, total_slices, boundaries)
            for i in range(total_slices)
        ]

    def _slice_for(
        self, so: SchedulerOutput
    ) -> list["LayerSliceInfo | None"]:
        # Decode-like and empty batches are never sliced. DECODE_FIRST is the
        # edge-cloud head segment of a decode step — same per-token shape as
        # PURE_DECODE, so it follows the same no-slice rule.
        if so.batch_type in (
            BatchType.PURE_DECODE,
            BatchType.DECODE_FIRST,
            BatchType.PREFILL_DRAFT_FIRST,
            BatchType.DECODE_DRAFT_FIRST,
        ):
            return [None]

        # [方案B] Cloud 侧决策：
        # 1. 已有 decode 到达 Cloud → 强制切层（确定性收益）
        if self.ready_decodes:
            return self._do_slice(so)

        # 2. Edge 建议切层（decode 正在路上）→ 切层
        if getattr(so, "cloud_suggest_slicing", False):
            return self._do_slice(so)

        # 3. Edge 建议不切层 + Cloud 无 decode → 明确不切层（冷启动优化）
        # 短 prefill（<8k）执行太快，decode 来不及穿插，同样不切层
        return [None]

    # ------------------------------------------------------------------ #
    # Dispatch                                                           #
    # ------------------------------------------------------------------ #
    _POLICY_ORDER: dict[DispatchPolicy, tuple[str, ...]] = {
        DispatchPolicy.EXPECT_ALTERNATION: (
            # Unused — EXPECT_ALTERNATION dispatches via the
            # CloudUndesiredState machine (`_schedule_undesired`).
            "ready_prefills", "ready_pdmixes", "ready_prefill_drafts",
            "ready_decode_drafts", "ready_decodes",
        ),
        DispatchPolicy.PREFILL_FIRST: (
            "ready_prefills", "ready_pdmixes", "ready_prefill_drafts",
            "ready_decode_drafts", "ready_decodes",
        ),
        DispatchPolicy.DECODE_FIRST: (
            "ready_decodes", "ready_decode_drafts", "ready_pdmixes",
            "ready_prefills", "ready_prefill_drafts",
        ),
        DispatchPolicy.PDMIX_FIRST: (
            "ready_pdmixes", "ready_prefills", "ready_prefill_drafts",
            "ready_decode_drafts", "ready_decodes",
        ),
    }

    def _start_prefill_middle_throttle(self) -> None:
        self._prefill_middle_throttle_started_at = time.monotonic()
        # logger.info(
        #     f"[PD-PASSIVE] Prefill throttle started: waiting up to "
        #     f"{self._prefill_middle_throttle_seconds * 1000:.0f}ms for decode",
        # )

    def _clear_prefill_middle_throttle(self) -> None:
        started_at = self._prefill_middle_throttle_started_at
        if started_at is not None:
            elapsed_ms = (time.monotonic() - started_at) * 1000
            # logger.info(
            #     f"[PD-PASSIVE] Prefill throttle cleared after "
            #     f"{elapsed_ms:.1f}ms",
            # )
        self._prefill_middle_throttle_started_at = None

    def _prefill_schedulable_in_undesired_prefill(self) -> bool:
        """Prefill gate for UNDESIRED_PREFILL priority 4 (design §6.5.2).

        The throttle forces consecutive prefill dispatches to be spaced by
        ``prefill_middle_throttle_seconds`` (leaving a window for PD
        alternation and DDF/D parallel work).  Dispatches of PD/DDF/D clear
        the throttle, so the next prefill is unconstrained.

        Optimization kept from the old machine: when the next prefill (or
        pdmix) has ``cloud_suggest_slicing=False``, the edge signaled "no
        running decode in flight" -> decode is not about to arrive, so
        waiting for it is pure idle; dispatch immediately.  This also means
        the P-middle is unsliced (see _slice_for), so there is no slice
        interleaving to protect either.
        """
        # Gate the head _pick_prefill_batch will actually dispatch
        # (continuation slice first, else prefill head, else pdmix head).
        # Checking the two fresh-prefill heads alone would let a non-sliced
        # pdmix behind a slicing prefill open the gate for that very prefill
        # the throttle was meant to hold; the continuation slice must be the
        # head when it is the only prefill work present (the global
        # continuation branch was removed 2026-08-13).
        head: SchedulerOutput | None = None
        if self._active_prefill_slices:
            head = self._active_prefill_slices[0].scheduler_output
        elif self.ready_prefills:
            head = self.ready_prefills[0]
        elif self.ready_pdmixes:
            head = self.ready_pdmixes[0]
        if head is None or not getattr(head, "cloud_suggest_slicing", False):
            return True
        started_at = self._prefill_middle_throttle_started_at
        if started_at is None:
            return True
        elapsed_ms = (time.monotonic() - started_at) * 1000
        limit_ms = self._prefill_middle_throttle_seconds * 1000
        if elapsed_ms >= limit_ms:
            return True
        logger.debug(
            f"[PD-PASSIVE] Throttle active: {elapsed_ms:.1f}ms / {limit_ms:.0f}ms, "
            f"still waiting for decode/draft",
        )
        return False

    def schedule(self) -> ScheduledBatch:
        """Pick the next SchedulerOutput to dispatch.

        ``EXPECT_ALTERNATION`` implements the Phase C cloud-side
        CloudUndesiredState machine (design §6.5): prefill-channel work
        (P / PD) and DECODE-channel work (D / DDF) take turns so both
        channel data planes stay busy.  Sliced prefill-like batches are
        dispatched one slice per call so decode/draft batches can be
        interleaved between the remaining slices.  Draft priority is
        enforced inside the state machine, not via an early out-of-band
        check.
        """
        if self.dispatch_policy == DispatchPolicy.EXPECT_ALTERNATION:
            return self._schedule_undesired()

        for queue_name in self._POLICY_ORDER[self.dispatch_policy]:
            batch = self._schedule_from_queue(queue_name)
            if not batch.is_empty():
                return batch

        return ScheduledBatch.empty()

    @staticmethod
    def _compute_slice_boundaries(
        num_local_layers: int, layer_slice_num: int
    ) -> list[tuple[int, int]]:
        """Compute layer slice boundaries for a fixed slice count.

        Distributes ``num_local_layers`` into ``layer_slice_num`` slices
        as evenly as possible.  Larger slices come first; the size
        difference between any two slices is at most 1.

        Returns a list of ``(start_layer, end_layer)`` tuples where
        ``end_layer`` is exclusive.
        """
        if num_local_layers <= 0 or layer_slice_num <= 0:
            return []
        boundaries: list[tuple[int, int]] = []
        base = num_local_layers // layer_slice_num
        rem = num_local_layers % layer_slice_num
        start = 0
        for i in range(layer_slice_num):
            size = base + 1 if i < rem else base
            boundaries.append((start, start + size))
            start += size
        return boundaries

    # ------------------------------------------------------------------ #
    # Pick methods (analogous to edge-side PDSeparatedScheduler)         #
    # ------------------------------------------------------------------ #
    def _pick_prefill_batch(self) -> ScheduledBatch:
        """Pick a prefill or prefill-like batch from the ready queues.

        Checks in priority order: active prefill slices (continuation of
        a previously sliced prefill), fresh prefills from ``ready_prefills``,
        then PD-mix batches from ``ready_pdmixes``.

        Caller must ensure at least one source is non-empty before calling.
        """
        if self._active_prefill_slices:
            return self._build_active_prefill_slice_batch()
        if self.ready_prefills:
            return self._build_batch(self.ready_prefills.popleft())
        assert self.ready_pdmixes, (
            "_pick_prefill_batch called with no prefill work available"
        )
        return self._build_batch(self.ready_pdmixes.popleft())

    def _dispatch_active_prefill_slice(self) -> ScheduledBatch:
        """Dispatch the next queued prefill slice (continuation).

        Slice continuation is the same logical prefill dispatch as the
        already-sent slice-0 (risk-free: its tensor is already on the
        cloud), so it is preferred wherever a prefill is dispatched.

        Transition after the dispatch (design §6.5.3-3 / 2026-08-13 fixes):
          * non-tail slice -> UNDESIRED_PREFILL, so decode is re-checked at
            priority 1 on the next tick — a sliced prefill is interleaved
            with decode, never dispatched back-to-back;
          * tail slice -> UNDESIRED_PD **only when the prefill_draft domain
            exists (MTP enabled)** — that state's priority-3 prefill_draft
            check is then live, giving the P→PD alternation the machine
            expects.  Without MTP there is no Prefill_Draft work at all, so
            parking in UNDESIRED_PD would leave its priority-3 check dead;
            UNDESIRED_PREFILL is the correct continuation (decode still wins
            at priority 1 there too).

        Caller must ensure ``_active_prefill_slices`` is non-empty.
        """
        if len(self._active_prefill_slices) == 1:
            if self._mtp_enabled:
                self.cloud_scheduling_state = (
                    CloudUndesiredState.UNDESIRED_PD
                )
            else:
                self.cloud_scheduling_state = (
                    CloudUndesiredState.UNDESIRED_PREFILL
                )
        else:
            self.cloud_scheduling_state = (
                CloudUndesiredState.UNDESIRED_PREFILL
            )
        self._start_prefill_middle_throttle()
        return self._pick_prefill_batch()

    def _pick_decode_batch(self) -> ScheduledBatch:
        """Pick a decode batch from ``ready_decodes``.

        Caller must ensure ``ready_decodes`` is non-empty before calling.
        """
        return self._build_batch(self.ready_decodes.popleft())

    def _pick_prefill_draft_batch(self) -> ScheduledBatch:
        """Pick a prefill-draft head from ``ready_prefill_drafts``.

        Caller must ensure ``ready_prefill_drafts`` is non-empty.
        """
        return self._build_batch(self.ready_prefill_drafts.popleft())

    def _pick_decode_draft_batch(self) -> ScheduledBatch:
        """Pick a decode-draft head from ``ready_decode_drafts``.

        Caller must ensure ``ready_decode_drafts`` is non-empty.
        """
        return self._build_batch(self.ready_decode_drafts.popleft())

    def _pick_decode_or_draft_by_arrival(self) -> ScheduledBatch:
        """Pick between the head decode and head decode-draft by arrival.

        DECODE_FIRST and DECODE_DRAFT_FIRST payloads share the DECODE
        hidden channel, and the edge publishes control messages in exactly
        the order its data plane requires.  Letting a later-arrived draft
        overtake an earlier decode (unconditional draft priority) makes
        the cloud post a recv for the draft payload while the edge's
        next in-flight message is a decode payload of a different size;
        the cloud then never produces the decode response the edge is
        blocked on, and the edge never sends the draft payload the cloud
        is blocked on -- a cross-side deadlock.  Fall back to draft
        priority (the state machine's ordering) only when an arrival seq
        is unavailable.  Prefill drafts ride the prefill channel and are
        exempt from this same-channel constraint.

        Caller must ensure at least one of the two queues is non-empty.
        """
        decode_seq = (
            self._arrival_seq(self.ready_decodes[0])
            if self.ready_decodes
            else None
        )
        draft_seq = (
            self._arrival_seq(self.ready_decode_drafts[0])
            if self.ready_decode_drafts
            else None
        )
        if (
            decode_seq is not None
            and draft_seq is not None
            and decode_seq < draft_seq
        ):
            return self._pick_decode_batch()
        if self.ready_decode_drafts:
            return self._pick_decode_draft_batch()
        return self._pick_decode_batch()

    def _schedule_undesired(self) -> ScheduledBatch:
        """Phase C three-state "undesired" machine (design §6.5.1).

        Channel model: prefill work (P / PD) rides per-chunk prefill
        channels; decode work (D / DDF) rides the single DECODE channel.
        Cross-channel dispatch order is a preference; same-channel order is
        a correctness constraint (positional pairing).  D vs DDF is
        resolved by arrival seq.  PF vs PDF can never coexist in the ready
        queues: a PDF requires its parent PL, which requires every parent
        PF slice to have been dispatched (PF leaves ``ready_prefills`` at
        its first dispatch), and a different chunk's PF rides a different
        prefill channel.

        The table checks queues in priority order; adjacent same-channel
        checks (DDF / D) are merged into one arrival-ordered pick.
        Slice continuation is not a global top priority: it is the highest
        check in UNDESIRED_DECODE_OR_DD — the state that just served decode
        and expects prefill-channel work — and is otherwise folded into the
        prefill priority of the other two states, where decode outranks it.
        ``_pick_prefill_batch`` prefers a continuation slice over a fresh
        prefill whenever a prefill dispatch is chosen.  The LAST slice
        leaves UNDESIRED_PD so decode wins the next tick (fix 2026-08-13),
        but **only when MTP is enabled** (the prefill_draft domain exists
        and its priority-3 check is live there); without MTP there is no
        Prefill_Draft, so the tail slice leaves UNDESIRED_PREFILL instead —
        decode still wins at priority 1 in both states.  A non-tail slice
        leaves UNDESIRED_PREFILL so decode is re-checked at priority 1 — a
        multi-slice prefill is interleaved with decode, never dispatched on
        consecutive ticks.
        Throttle semantics (design §6.5.2): started on every prefill
        dispatch (including slice continuation), cleared on every PD /
        DDF / D dispatch, and enforced only at UNDESIRED_PREFILL
        priority 3 via ``_prefill_schedulable_in_undesired_prefill``.
        """
        state = self.cloud_scheduling_state

        if state == CloudUndesiredState.UNDESIRED_PREFILL:
            # 1: decode channel work, by arrival — decode wins over
            # prefill_draft.  A prefill_draft's tensor only exists once the
            # edge worker has executed it; while the edge is blocked on a
            # decode response its DDF is queued right here, so dispatching
            # the prefill_draft would stall cloud and edge indefinitely.
            # Running the ready decode first breaks that cycle (fix
            # 2026-08-13).
            if self.ready_decode_drafts or self.ready_decodes:
                self.cloud_scheduling_state = (
                    CloudUndesiredState.UNDESIRED_DECODE_OR_DD
                )
                self._clear_prefill_middle_throttle()
                return self._pick_decode_or_draft_by_arrival()
            # 2: prefill_draft (prefill channel).
            if self.ready_prefill_drafts:
                self.cloud_scheduling_state = CloudUndesiredState.UNDESIRED_PD
                self._clear_prefill_middle_throttle()
                return self._pick_prefill_draft_batch()
            # 3: prefill (+ active-slice continuation, + pdmixes, design
            # §6.5.3-4) — throttle-gated.  Continuation is preferred by
            # ``_pick_prefill_batch``; its dispatch helper leaves
            # UNDESIRED_PD on the tail slice when MTP is enabled (decode
            # wins next), else UNDESIRED_PREFILL — no Prefill_Draft exists
            # without MTP (2026-08-13); a non-tail slice / fresh prefill
            # leaves UNDESIRED_PREFILL.
            if (
                self._active_prefill_slices
                or self.ready_prefills
                or self.ready_pdmixes
            ):
                if not self._prefill_schedulable_in_undesired_prefill():
                    return ScheduledBatch.empty()
                if self._active_prefill_slices:
                    return self._dispatch_active_prefill_slice()
                self._start_prefill_middle_throttle()
                return self._pick_prefill_batch()
            return ScheduledBatch.empty()

        if state == CloudUndesiredState.UNDESIRED_PD:
            # 1/2: decode channel work, by arrival.
            if self.ready_decode_drafts or self.ready_decodes:
                self.cloud_scheduling_state = (
                    CloudUndesiredState.UNDESIRED_DECODE_OR_DD
                )
                self._clear_prefill_middle_throttle()
                return self._pick_decode_or_draft_by_arrival()
            # 3: prefill (+ active-slice continuation, + pdmixes),
            # unconditional.  Continuation preferred by ``_pick_prefill_batch``;
            # its dispatch helper leaves UNDESIRED_PD on the tail slice only
            # with MTP enabled (else UNDESIRED_PREFILL, 2026-08-13).
            if (
                self._active_prefill_slices
                or self.ready_prefills
                or self.ready_pdmixes
            ):
                if self._active_prefill_slices:
                    return self._dispatch_active_prefill_slice()
                self.cloud_scheduling_state = (
                    CloudUndesiredState.UNDESIRED_PREFILL
                )
                self._start_prefill_middle_throttle()
                return self._pick_prefill_batch()
            # 4: prefill_draft — same-domain continuation, state unchanged.
            if self.ready_prefill_drafts:
                self._clear_prefill_middle_throttle()
                return self._pick_prefill_draft_batch()
            return ScheduledBatch.empty()

        # UNDESIRED_DECODE_OR_DD
        # 1: active-slice continuation — risk-free (its tensor is already
        # on the cloud), so it runs ahead of decode here: this state just
        # served decode and wants prefill-channel work.  The dispatch
        # helper leaves UNDESIRED_PD on the tail slice (decode wins next)
        # only when MTP is enabled — no Prefill_Draft exists otherwise, so
        # the tail leaves UNDESIRED_PREFILL (2026-08-13) — and
        # UNDESIRED_PREFILL on a non-tail slice, so a sliced prefill is
        # interleaved with decode instead of dispatched back-to-back.
        if self._active_prefill_slices:
            return self._dispatch_active_prefill_slice()
        # 2: decode channel work, by arrival — decode wins over
        # prefill_draft (same deadlock fix as UNDESIRED_PREFILL).
        if self.ready_decode_drafts or self.ready_decodes:
            self._clear_prefill_middle_throttle()
            return self._pick_decode_or_draft_by_arrival()
        # 3: prefill_draft (prefill channel).
        if self.ready_prefill_drafts:
            self.cloud_scheduling_state = CloudUndesiredState.UNDESIRED_PD
            self._clear_prefill_middle_throttle()
            return self._pick_prefill_draft_batch()
        # 4: prefill (+ pdmixes), fresh first slice only — a sliced prefill's
        # continuation is already handled at priority 1 above.
        if self.ready_prefills or self.ready_pdmixes:
            self.cloud_scheduling_state = CloudUndesiredState.UNDESIRED_PREFILL
            self._start_prefill_middle_throttle()
            return self._pick_prefill_batch()
        return ScheduledBatch.empty()

    def _schedule_from_queue(self, queue_name: str) -> ScheduledBatch:
        if self._active_prefill_slices:
            # Draft heads are channel work like decode — dispatchable while
            # prefill slices continue.
            if queue_name == "ready_decodes" and self.ready_decodes:
                return self._pick_decode_batch()
            if queue_name == "ready_prefill_drafts" and self.ready_prefill_drafts:
                return self._pick_prefill_draft_batch()
            if queue_name == "ready_decode_drafts" and self.ready_decode_drafts:
                return self._pick_decode_draft_batch()
            if queue_name in ("ready_prefills", "ready_pdmixes"):
                return self._pick_prefill_batch()
            return ScheduledBatch.empty()

        if queue_name == "ready_prefills":
            if self.ready_prefills:
                return self._build_batch(self.ready_prefills.popleft())
            return ScheduledBatch.empty()
        if queue_name == "ready_decodes":
            if self.ready_decodes:
                return self._pick_decode_batch()
            return ScheduledBatch.empty()
        if queue_name == "ready_prefill_drafts":
            if self.ready_prefill_drafts:
                return self._pick_prefill_draft_batch()
            return ScheduledBatch.empty()
        if queue_name == "ready_decode_drafts":
            if self.ready_decode_drafts:
                return self._pick_decode_draft_batch()
            return ScheduledBatch.empty()
        if queue_name == "ready_pdmixes":
            if self.ready_pdmixes:
                return self._pick_prefill_batch()
            return ScheduledBatch.empty()

        q: deque[SchedulerOutput] = getattr(self, queue_name)
        if q:
            return self._build_batch(q.popleft())
        return ScheduledBatch.empty()

    def _build_batch(self, so: SchedulerOutput) -> ScheduledBatch:
        slices = self._slice_for(so)
        if len(slices) <= 1:
            batch = ScheduledBatch(scheduler_output=so, slices=slices)
        else:
            first_slice = slices[0]
            assert isinstance(first_slice, LayerSliceInfo)
            self._active_sliced_prefill = so
            self._active_prefill_slices.extend(
                SliceTask(so, slice_info)
                for slice_info in slices[1:]
                if isinstance(slice_info, LayerSliceInfo)
            )
            batch = ScheduledBatch(scheduler_output=so, slices=[first_slice])

        self._log_picked_batch(batch)
        return batch

    def _build_active_prefill_slice_batch(self) -> ScheduledBatch:
        task = self._active_prefill_slices.popleft()
        if not self._active_prefill_slices:
            self._active_sliced_prefill = None
        batch = ScheduledBatch(
            scheduler_output=task.scheduler_output,
            slices=[task.slice_info],
        )
        self._log_picked_batch(batch)
        return batch

    def _log_picked_batch(self, batch: ScheduledBatch) -> None:
        so = batch.scheduler_output
        logger.debug(
            "PassiveScheduler.schedule[%s] picked batch_type=%s slices=%d; "
            "pending=(prefills=%d, active_prefill_slices=%d, pdmixes=%d, "
            "prefill_drafts=%d, decode_drafts=%d, decodes=%d) seq=%s",
            self.dispatch_policy.value,
            so.batch_type.value if so.batch_type is not None else "<none>",
            len(batch.slices),
            len(self.ready_prefills),
            len(self._active_prefill_slices),
            len(self.ready_pdmixes),
            len(self.ready_prefill_drafts),
            len(self.ready_decode_drafts),
            len(self.ready_decodes),
            self._arrival_seq(so),
        )

    # ------------------------------------------------------------------ #
    # Introspection                                                      #
    # ------------------------------------------------------------------ #
    def has_pending(self) -> bool:
        return bool(
            self.ready_prefills
            or self._active_prefill_slices
            or self.ready_pdmixes
            or self.ready_prefill_drafts
            or self.ready_decode_drafts
            or self.ready_decodes
        )

    @property
    def num_pending(self) -> int:
        return (
            len(self.ready_prefills)
            + len(self._active_prefill_slices)
            + len(self.ready_pdmixes)
            + len(self.ready_prefill_drafts)
            + len(self.ready_decode_drafts)
            + len(self.ready_decodes)
        )

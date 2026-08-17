# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
import enum
import os
import time
from collections import deque
from dataclasses import dataclass, replace

import numpy as np
from collections.abc import Iterable
from typing import Any
from uuid import uuid4

from vllm.logger import logger
from vllm.v1.core.sched.async_scheduler import AsyncScheduler
from vllm.v1.core.sched.interface import PauseState
from vllm.v1.core.sched.output import BatchType, HiddenChannelType, SchedulerOutput
from vllm.v1.core.sched.request_queue import SchedulingPolicy, create_request_queue
from vllm.v1.core.sched.scheduler import Scheduler
from vllm.v1.core.sched.utils import remove_all
from vllm.v1.outputs import ModelRunnerOutput
from vllm.v1.request import Request, RequestStatus


class PrefillState(enum.Enum):
    """Edge-side prefill in-flight state machine.

    See Phase5 design in ``PDbatch分离边云协同Phase5&7详细设计.md``.
    """
    IDLE = "idle"       # prefill_inflight_count == 0
    LOW = "low"         # prefill_inflight_count == 1
    HIGH = "high"       # prefill_inflight_count >= prefill_inflight_limit


@dataclass
class PrefillChunkFlight:
    """Per-chunk in-flight tracking for chunk-prefill-prior scheduling.

    When ``chunk_prefill_prior_enable`` is True, each PREFILL_FIRST batch
    creates one ``PrefillChunkFlight`` keyed by its ``head_token``.  This
    allows the same request to have multiple chunks in-flight
    simultaneously — the next chunk's PF can be dispatched before the
    previous chunk's PL returns.

    Fields
    ------
    request_id : str
        The owning request.
    head_token : str
        Unique token assigned to this chunk's PREFILL_FIRST batch.
        PREFILL_LAST echoes it back so the flight can be located.
    hidden_channel : HiddenChannelType
        Prefill data-plane channel allocated for this chunk.
    chunk_index : int
        0-based index of this chunk within the request.
    is_last_chunk : bool
        True when this chunk consumes the last remaining prompt tokens.
    num_scheduled_tokens : int
        Number of tokens scheduled in this chunk.
    """
    request_id: str
    head_token: str
    hidden_channel: HiddenChannelType
    chunk_index: int
    is_last_chunk: bool
    num_scheduled_tokens: int


@dataclass(frozen=True)
class PDActiveFlight:
    """A protected edge-cloud transaction from First creation to Last finish."""

    request_ids: tuple[str, ...]
    first_batch_type: BatchType
    last_batch_type: BatchType
    flight_id: str
    created_at: float


_PD_FIRST_TO_LAST = {
    BatchType.PREFILL_FIRST: BatchType.PREFILL_LAST,
    BatchType.DECODE_FIRST: BatchType.DECODE_LAST,
    BatchType.PREFILL_DRAFT_FIRST: BatchType.PREFILL_DRAFT_LAST,
    BatchType.DECODE_DRAFT_FIRST: BatchType.DECODE_DRAFT_LAST,
}
_PD_LAST_TO_FIRST = {last: first for first, last in _PD_FIRST_TO_LAST.items()}


# DP-scalable hidden-channel allocation.
_PREFILL_CHANNELS_PER_DP = 2
_DECODE_CHANNELS_PER_DP = 1


class HiddenChannelManager:
    """Manages data-plane hidden tensor channels for edge-cloud PD separation.

    Shared-model DP ranks receive disjoint channel slices. In the per-rank
    topology each DP has its own physical process-group world and reuses the
    first channel slice.
    """

    def __init__(
        self,
        dp_rank: int = 0,
        prefill_per_dp: int = _PREFILL_CHANNELS_PER_DP,
        is_shared_model_edge: bool = False,
    ) -> None:
        if not is_shared_model_edge:
            dp_rank = 0
        prefill_start = dp_rank * prefill_per_dp + 1
        self._free_prefills: deque[HiddenChannelType] = deque(
            HiddenChannelType.prefill(i)
            for i in range(prefill_start, prefill_start + prefill_per_dp)
        )
        self._decode_channel = HiddenChannelType.decode(dp_rank + 1)
        # MTP draft data plane: DECODE_DRAFT_* batches travel on their own
        # channel so the draft chain never contends with the shared DECODE
        # channel.  One draft channel per dp_rank, fixed like decode (no
        # free-list).
        self._draft_channel = HiddenChannelType.draft(dp_rank + 1)
        self._head_token_to_channel: dict[str, HiddenChannelType] = {}

    # ------------------------------------------------------------------ #
    # Prefill channel allocation / release                               #
    # ------------------------------------------------------------------ #
    def allocate_prefill(self, head_token: str) -> HiddenChannelType:
        """Allocate a free prefill channel for the batch identified by
        ``head_token``. Raises if none available."""
        if not self._free_prefills:
            raise RuntimeError(
                "No free prefill hidden channel available"
            )
        channel = self._free_prefills.popleft()
        self._head_token_to_channel[head_token] = channel
        logger.info(
            "[PD] allocate_prefill: channel=%s head_token=%s free_left=%s",
            channel.value, head_token, list(self._free_prefills),
        )
        return channel

    def release_prefill(self, head_token: str) -> HiddenChannelType | None:
        """Release the prefill channel previously allocated for
        ``head_token``. Returns the freed channel (or None if not found)."""
        channel = self._head_token_to_channel.pop(head_token, None)
        if channel is None:
            return None
        self._free_prefills.append(channel)
        logger.info(
            "[PD] release_prefill: channel=%s head_token=%s free=%s",
            channel.value, head_token, list(self._free_prefills),
        )
        return channel

    def has_free_prefill(self) -> bool:
        return bool(self._free_prefills)

    # ------------------------------------------------------------------ #
    # Decode channel (fixed per DP, no free-list)                         #
    # ------------------------------------------------------------------ #
    def decode_channel(self) -> HiddenChannelType:
        return self._decode_channel

    def draft_channel(self) -> HiddenChannelType:
        """Dedicated MTP draft channel for this dp_rank."""
        return self._draft_channel

    # ------------------------------------------------------------------ #
    # Introspection                                                      #
    # ------------------------------------------------------------------ #
    def get_channel(self, head_token: str) -> HiddenChannelType | None:
        return self._head_token_to_channel.get(head_token)

    @property
    def in_use_prefills(self) -> list[HiddenChannelType]:
        return [
            channel
            for channel in self._head_token_to_channel.values()
            if channel.value.startswith("prefill_")
        ]

    @property
    def prefill_pool(self) -> frozenset[HiddenChannelType]:
        return frozenset(self._free_prefills) | frozenset(self.in_use_prefills)

    @property
    def decode_pool(self) -> frozenset[HiddenChannelType]:
        return frozenset((self._decode_channel,))

    @staticmethod
    def prefill_inflight_limit() -> int:
        return _PREFILL_CHANNELS_PER_DP

    @staticmethod
    def required_prefill_groups(dp_size: int) -> int:
        return dp_size * _PREFILL_CHANNELS_PER_DP

    @staticmethod
    def required_decode_groups(dp_size: int) -> int:
        return dp_size * _DECODE_CHANNELS_PER_DP


class EdgeForceStateMachine:
    """FORCE 状态机（设计 §6.3.2）：边侧强制调度逻辑的唯一宿主。

    收编两类强制机制（原散落为 3 个交替 bool + 2 个 first-only 窗口 +
    4 处门控查询 + 2 个消费函数）：

    * 交替标记：F pick 置 L-pending，L pick 解除——保证 DF->DL、
      DDF->DDL、PDFF->PDFL 严格交替时序；
    * first-only 窗口：DL/DDL/PL(仅 MTP)/非末跳 PDFL pick 后，下一拍
      只允许对应域的 first（选中即解除；超时自动解除并打 warning）。

    范围（用户确认，仅"交替+窗口"）：延迟 pacing 计时器（decode_last
    30ms、decode_draft_last 5ms）与 PDFL watchdog 不在此状态机内，
    保留原位（pacing / 故障检测非强制语义）。

    两域独立（正确性要求）：prefill 域强制 PDFL 与 decode 域强制
    first-only 可叠加存在，故按域建字段而非单枚举；每域内"F->L 交替"
    与"L->F 窗口"天然时序互斥，同一时刻至多一个激活（与窗口互斥注释
    一致）。
    """

    def __init__(
        self,
        *,
        decode_first_only_window_ms: int = 30,
        prefill_draft_first_only_window_ms: int = 15,
        prefill_first_only_enabled: bool = True,
    ) -> None:
        # decode 域交替：DF/DDF pick 置位，DL/DDL pick 解除。
        self.decode_last_pending: bool = False
        self.decode_draft_last_pending: bool = False
        # decode 域 first-only 窗口（绝对截止时刻；None = 未激活）。
        self.decode_first_only_deadline: float | None = None
        # prefill 域交替：PDFF pick 置位，PDFL pick 解除。
        self.prefill_draft_last_pending: bool = False
        # prefill 域 first-only 窗口（绝对截止时刻；None = 未激活）。
        self.prefill_first_only_deadline: float | None = None

        self._decode_first_only_window_ms: int = decode_first_only_window_ms
        self._prefill_draft_first_only_window_ms: int = (
            prefill_draft_first_only_window_ms
        )
        # 非 MTP 无链可等：PL 后启动 prefill 窗口只会白白锁住 15ms。
        self._prefill_first_only_enabled: bool = prefill_first_only_enabled

    # ------------------------------------------------------------------ #
    # 事件转移：pick 后通知（batch_type 为实际派发类型）                  #
    # ------------------------------------------------------------------ #
    def on_pick(
        self,
        batch_type: BatchType,
        *,
        prefill_chain_has_more: bool = False,
    ) -> None:
        if batch_type == BatchType.DECODE_FIRST:
            self.decode_last_pending = True
        elif batch_type == BatchType.DECODE_DRAFT_FIRST:
            self.decode_draft_last_pending = True
        elif batch_type == BatchType.DECODE_LAST:
            self._start_decode_first_only()
            self.decode_last_pending = False
        elif batch_type == BatchType.DECODE_DRAFT_LAST:
            self._start_decode_first_only()
            self.decode_draft_last_pending = False
        elif batch_type == BatchType.PREFILL_DRAFT_FIRST:
            self.prefill_draft_last_pending = True
        elif batch_type == BatchType.PREFILL_DRAFT_LAST:
            # 非末跳（同 task 仍有未派发 PDFF 在队）才启动窗口强制跟随；
            # 末跳后无首可等，清窗口（防御性，防残留误锁）。
            if prefill_chain_has_more:
                self._start_prefill_draft_first_only()
            else:
                self.prefill_first_only_deadline = None
            self.prefill_draft_last_pending = False
        elif batch_type == BatchType.PREFILL_LAST:
            # 第 3 点强制等待（仅 MTP 场景生效——构造时判定，等价现状
            # _uses_async_scheduled_mtp_placeholders 运行时门控）。
            if self._prefill_first_only_enabled:
                self._start_prefill_draft_first_only()
        # PREFILL_FIRST / EMPTY：无转移。

    # ------------------------------------------------------------------ #
    # 门控查询（替代 _can_schedule_* 中的 not self._force_* 检查）       #
    # ------------------------------------------------------------------ #
    def can_pick_decode_first(self) -> bool:
        return (
            not self.decode_last_pending
            and not self.decode_draft_last_pending
        )

    def can_pick_decode_draft_first(self) -> bool:
        return self.can_pick_decode_first()

    def can_pick_prefill_draft_first(self) -> bool:
        return not self.prefill_draft_last_pending

    def can_pick_decode_last(self) -> bool:
        # 现状仅受延迟 pacing 计时器约束（不在 FORCE 范围），无强制门控。
        return True

    def can_pick_decode_draft_last(self) -> bool:
        return True

    # ------------------------------------------------------------------ #
    # first-only 窗口活性：未激活/未超时返回 True 语义相反（active），    #
    # 超时自动解除并打 warning（文案与现状逐字一致）                     #
    # ------------------------------------------------------------------ #
    def decode_first_only_active(self) -> bool:
        deadline = self.decode_first_only_deadline
        if deadline is None:
            return False
        if time.monotonic() < deadline:
            return True
        self.decode_first_only_deadline = None
        logger.warning(
            "[PD] decode-first-only window expired after %dms "
            "without a DECODE_FIRST / DECODE_DRAFT_FIRST pick "
            "(scheduling anomaly: decode domain stalled or first "
            "gated too long)",
            self._decode_first_only_window_ms,
        )
        return False

    def prefill_draft_first_only_active(self) -> bool:
        deadline = self.prefill_first_only_deadline
        if deadline is None:
            return False
        if time.monotonic() < deadline:
            return True
        self.prefill_first_only_deadline = None
        logger.warning(
            "[PD] prefill-draft-first-only window expired after %dms "
            "without a PREFILL_DRAFT_FIRST pick (scheduling anomaly: "
            "prefill draft chain stalled or first gated too long)",
            self._prefill_draft_first_only_window_ms,
        )
        return False

    # ------------------------------------------------------------------ #
    # 消费：选中 first 即解除对应窗口                                    #
    # ------------------------------------------------------------------ #
    def clear_decode_first_only(self) -> None:
        self.decode_first_only_deadline = None

    def clear_prefill_draft_first_only(self) -> None:
        self.prefill_first_only_deadline = None

    def release_for_draft_work(self) -> None:
        """_has_draft_work 接管：链 FIFO 即节奏（§6.3 域间互不阻塞），
        且链排空后无残留窗口可误报超时。"""
        self.clear_decode_first_only()
        self.clear_prefill_draft_first_only()

    def _start_decode_first_only(self) -> None:
        self.decode_first_only_deadline = (
            time.monotonic()
            + self._decode_first_only_window_ms / 1000.0
        )

    def _start_prefill_draft_first_only(self) -> None:
        self.prefill_first_only_deadline = (
            time.monotonic()
            + self._prefill_draft_first_only_window_ms / 1000.0
        )


class PDSeparatedScheduler(Scheduler):
    """Scheduler that separates prefill and decode into distinct steps.

    In edge-cloud PD-separated mode the four cardinal phases are:
      - PREFILL_FIRST  (edge head segment)
      - PREFILL_LAST   (edge tail segment, sourced from cloud-returned outputs)
      - DECODE_FIRST   (Phase 4)
      - DECODE_LAST    (Phase 4)

    This class owns the request bookkeeping for *first* segments
    (``chunk_prefill_first`` + parent's ``waiting`` / ``running``) and the
    ready queues for *last* segments (``prefills_last_ready`` /
    ``decodes_last_ready``), which are filled by the EngineCore from the
    POST_OUT channel before each ``schedule()`` call.

    Chunk-prefill-prior (Phase 1)
    -----------------------------
    When ``chunk_prefill_prior_enable`` is True, per-chunk flight tracking
    replaces the request-granularity ``prefill_last_pending`` list.  This
    allows the next chunk's PREFILL_FIRST to be dispatched before the
    previous chunk's PREFILL_LAST returns, achieving the same pipeline
    interleaving that MindIE's ``generate_send_metadata_to_queue()``
    provides.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Requests that have started their P-first segment but have not yet
        # been fully consumed (still chunking, or still in flight on cloud).
        self.chunk_prefill_first: list[Request] = []

        # SchedulerOutputs returned from cloud (POST_OUT channel) carrying
        # the metadata needed to execute the edge tail segment.
        # Populated by EngineCore.step() before calling self.schedule().
        self.prefills_last_ready: deque[SchedulerOutput] = deque()
        self.decodes_first_ready: deque[SchedulerOutput] = deque()
        self.decodes_last_ready: deque[SchedulerOutput] = deque()
        # 4 域拆分（设计 §3.2）：prefill_draft 链与 decode_draft 链的就绪
        # 队列彼此独立，调度互不阻塞。
        self.prefill_drafts_first_ready: deque[SchedulerOutput] = deque()
        self.prefill_drafts_last_ready: deque[SchedulerOutput] = deque()
        self.decode_drafts_first_ready: deque[SchedulerOutput] = deque()
        self.decode_drafts_last_ready: deque[SchedulerOutput] = deque()

        self._step_counter: int = 0

        # In-flight prefill limit (head-segment batches).
        self.prefill_inflight_limit: int = getattr(
            self.scheduler_config, "pd_prefill_inflight_limit",
            _PREFILL_CHANNELS_PER_DP,
        )
        self.prefill_inflight_count: int = 0
        self.decode_or_draft_inflight_limit: int = 1
        self.decode_or_draft_inflight_count: int = 0
        # DECODE_FIRST heads picked but not yet completed (update_from_output).
        # DECODE_DRAFT_FIRST and DECODE_FIRST use different recv primitives
        # but share the DECODE stream, so they must not be in flight
        # simultaneously (the cloud's recv order could mismatch the edge's
        # send order).  DECODE_DRAFT_FIRST+DECODE_DRAFT_FIRST is safe (same
        # primitive, FIFO), so draft pipelining only needs to gate on decode
        # heads, not total heads.
        self.decode_head_inflight_count: int = 0
        # 4 域拆分（设计 §5.4）：prefill_draft 与 decode_draft 各自计数、
        # 各自限额，互不影响。Phase A 中 prefill_draft 仍走 DECODE 通道，
        # 因此 decode_or_draft_inflight_count 仍被两域共同占用。
        self.prefill_draft_remote_pending_count: int = 0
        self.decode_draft_remote_pending_count: int = 0

        # Phase B（设计 §5.2）：prefill 槽推迟释放记账。prefill_draft 链
        # 继承父 chunk 的 Prefill 通道，通道与 prefill_inflight_count 须
        # 保持占用到整条草稿链完成（PL + 全部 PDFL 都从云端返回）后才能
        # 释放。pending[head] 初始 1（PL 哨兵），链的每个步入队 +1，
        # 每个 PDFL 完成/被 drop -1；pl_done[head] 记录 PL 是否已完成。
        # pending==0 且 pl_done → _finalize_prefill_slot(head)。
        self._prefill_slot_pending: dict[str, int] = {}
        self._prefill_slot_pl_done: dict[str, bool] = {}

        # Phase B（设计 §5.5）：请求级 running 门控记账。请求必须在其
        # prefill_draft 全部完成（final PREFILL_DRAFT_LAST）后才允许进入
        # running 推进 decode——否则链后首个 DECODE_FIRST 的 verify 会读到
        # 未完成的草稿行（Phase A 的共享计数/队列门禁恰好挡住了该窗口，
        # Phase B 放开后必须由本机制接管）。计数按 draft_output_req_ids
        # 成员记（pregenerate +num_spec；fallback 每步入队 +1；每个 PDFL
        # 完成 -1）。被门控推迟的请求记入 _running_gated_req_ids，链终结
        # 时由 _migrate_ready_prefill_pending 移入 running。
        self._req_pending_prefill_draft_steps: dict[str, int] = {}
        self._running_gated_req_ids: set[str] = set()
        # 对抗 review A1：计数键 req_id 生命周期跨越请求寿命——同 id 重提交
        # （本文件 finish 路径显式支持）后，旧链残余 PDFL 的递减会侵蚀新
        # 请求的计数（提前放行）或 +1 泄漏（永久门控）。以"链代"（本请求
        # 生命周期内曾对其计费的草稿链 task_id 集合）隔离：+1 时登记
        # task_id，-1 时仅当 PDFL 的 task_id 在本集合内才递减。请求
        # finished 时整键清账（drop_stale 统一 pop）。
        self._req_charged_draft_tasks: dict[str, set[str]] = {}

        # Phase6 data-plane channel manager — per-dp_rank slice.
        dp_rank = getattr(self.vllm_config.parallel_config,
                          "data_parallel_rank", 0)
        is_shared = getattr(self.vllm_config.parallel_config,
                            "is_shared_model_edge", False)
        self.hidden_channel_manager = HiddenChannelManager(
            dp_rank=dp_rank,
            is_shared_model_edge=is_shared,
        )
        logger.info(
            "[PD] HiddenChannelManager(dp_rank=%d): prefill_pool=%s decode_pool=%s",
            dp_rank,
            self.hidden_channel_manager.prefill_pool,
            self.hidden_channel_manager.decode_pool,
        )

        # Buffer queue: requests whose P-first segment is done but P-last
        # segment has not yet returned from the cloud.  Not eligible for
        # decode scheduling until PL completes and they are moved to running.
        # When chunk_prefill_prior_enable is True, this is supplemented by
        # per-chunk flight tracking.
        self.prefill_last_pending: list[Request] = []

        # ------------------------------------------------------------------ #
        # Chunk-prefill-prior fields                                          #
        # ------------------------------------------------------------------ #
        # Enabled via pd_separation.next_prefill_prior_enable. When True the
        # scheduler yields a freed prefill slot to a *different* request
        # (cross-request head-prior, MindIE-style P1首->P2首) instead of
        # ahead-dispatching the same request's next chunk.
        self.next_prefill_prior_enable: bool = getattr(
            self.scheduler_config, "pd_next_prefill_prior_enable", False
        )
        # Enabled via pd_separation.chunk_prefill_prior_enable.
        self.chunk_prefill_prior_enable: bool = getattr(
            self.scheduler_config, "pd_chunk_prefill_prior_enable", False
        )
        self.max_chunk_prefill_ahead: int = getattr(
            self.scheduler_config, "pd_max_chunk_prefill_ahead", 1
        )

        # Per-chunk flight tracking: head_token → PrefillChunkFlight.
        # Populated on PF, consumed on PL.
        self._prefill_flight_by_token: dict[str, PrefillChunkFlight] = {}

        # Per-request count of chunks still waiting for PL.
        # request_id → count.  When count reaches 0, the request is
        # eligible to enter decode.
        self._pending_tail_count: dict[str, int] = {}

        # Per-request count of chunks whose PF was dispatched ahead
        # (before the previous chunk's PL returned).  Decremented on
        # PL return so the request is not re-added to chunk_prefill_first.
        self._ahead_chunk_count: dict[str, int] = {}

        # A request is protected from preemption from the moment a First batch
        # is created until the matching Last batch finishes update_from_output.
        # The count (rather than a bool) supports multiple ahead-scheduled
        # prefill chunks for the same request.
        self._pd_active_flight_count: dict[str, int] = {}
        self._pd_active_flight_by_key: dict[
            tuple[BatchType, str], PDActiveFlight
        ] = {}

        # 限制 PREFILL_FIRST 每个 batch 最多只组 1 个请求。
        # 配置路径: additional_config.edge_cloud_config.pd_separation.limit_prefill_batch_size
        self.limit_prefill_batch_size: bool = False
        _additional = getattr(self.vllm_config, "additional_config", None)
        if isinstance(_additional, dict):
            _ec = _additional.get("edge_cloud_config", {})
            _pd = _ec.get("pd_separation", {})
            self.limit_prefill_batch_size = bool(
                _pd.get("limit_prefill_batch_size", False)
            )

        # [新增] DECODE_LAST 延迟调度计时器。
        # D首 pick 后启动，D尾 在延迟到期前不可被调度。
        self._decode_last_delay_start_ts: float | None = None
        self._decode_last_delay_schedule_ms: int = 30

        # [FORCE] 强制调度状态机（设计 §6.3.2）：交替标记与 first-only
        # 窗口全部收敛于此（替代 3 个 _force_* bool + 2 个窗口组）。
        # prefill_first_only_enabled = MTP 使能——非 MTP 无链可等，PL 后
        # 启动 prefill 窗口只会白白锁 15ms（等价现状的运行时门控，
        # 依赖的配置在构造后不变，故可构造时计算）。
        self._force: EdgeForceStateMachine = EdgeForceStateMachine(
            decode_first_only_window_ms=30,
            prefill_draft_first_only_window_ms=15,
            prefill_first_only_enabled=(
                self._uses_async_scheduled_mtp_placeholders()
            ),
        )

        self._layer_slice_config_path: str | None = None
        self._layer_slice_config_mtime: float = 0.0
        self._load_layer_slice_config()

        # [MTP] DECODE_DRAFT_LAST delay scheduling (mirrors
        # decode_last_delay)。边侧自生成 decode_draft_last 后延迟 5ms
        # （默认）再调度，保留解码域 pacing（设计 §6.2）。
        self._decode_draft_last_delay_start_ts: float | None = None
        self._decode_draft_last_delay_schedule_ms: int = 15

        # [EHER-draft] DDL recv-readiness ack gate: when enabled, a queued
        # DECODE_DRAFT_LAST is schedulable the moment the edge TP0 worker
        # reports its return irecv complete (worker report thread ->
        # edge_recv_ready_mq -> EngineCore._drain_draft_recv_acks ->
        # notify_draft_recv_ready), replacing fixed-delay pacing with
        # data-plane readiness.  A timeout fallback (10x the delay, min
        # 100ms) keeps the gate safe when no ack ever arrives (TP1-only
        # worker mix, SP compat path, or sideband MQ not attached).
        # Default off: legacy delay pacing unless the deployment yaml sets
        # decode_draft_recv_ack_enable.
        self._decode_draft_recv_ack_enable: bool = False
        self._draft_recv_ready_acks: set[str] = set()

        # [MTP] PREFILL_DRAFT_LAST delay scheduling。
        # Phase A：prefill_draft 保持旧行为（边侧自贴尾 + 延迟，默认 10ms
        # 与旧 draft_last 一致）；Phase C 迁移为云侧 POST_OUT 发布后，
        # 本延迟不再使用（设计 §6.2）。
        self._prefill_draft_last_delay_start_ts: float | None = None
        self._prefill_draft_last_delay_schedule_ms: int = 10

        # Async scheduled-MTP keeps real draft token IDs in the edge worker.
        # The scheduler only needs fixed-length placeholder SchedulerOutputs,
        # which can be generated and dispatched before the preceding worker
        # result is returned to EngineCore.  Cloud publication is finalized
        # separately once the target sampling scalars are available.
        self._draft_first_cloud_publish_pending: SchedulerOutput | None = None
        self._draft_first_scalars_patched: bool = False
        self._draft_first_dispatched: bool = False
        self._pregenerated_draft_task_ids: set[str] = set()
        self._pregenerated_draft_req_ids: dict[str, set[str]] = {}
        # 4 域拆分（设计 §5.4）：两域各自限额，默认各 2；Phase C 起可经
        # PDSeparationConfig 配置（design §7.7 #37，platform 穿线）。
        self._prefill_draft_remote_pending_limit: int = int(
            getattr(
                self.scheduler_config,
                "pd_prefill_draft_remote_pending_limit",
                2,
            )
        )
        self._decode_draft_remote_pending_limit: int = int(
            getattr(
                self.scheduler_config,
                "pd_decode_draft_remote_pending_limit",
                2,
            )
        )
        # Phase C review: PDFL 云发布 watchdog。云侧经 POST_OUT（ZMQ PUSH
        # 背压会丢包的 control 通道）发布 PDFL；丢包不是正常场景，尾
        # 丢失说明边云链路或云侧已故障——静默等待会永久卡死（force
        # 标记不清除 + prefill 通道泄漏），超时后直接报错让部署层
        # 重启整个实例。
        self._prefill_draft_last_watchdog: dict[str, float] = {}
        self._prefill_draft_last_watchdog_seconds: float = float(
            getattr(
                self.scheduler_config,
                "pd_prefill_draft_last_watchdog_seconds",
                30.0,
            )
        )
        self._decode_first_placeholder_parent: SchedulerOutput | None = None

        # ------------------------------------------------------------------ #
        # Edge-cloud deferred-draft KV retention                             #
        # ------------------------------------------------------------------ #
        # Non-edge-cloud proposes draft tokens inside the same execute_model
        # call, i.e. strictly BEFORE update_from_output frees the finished
        # requests' KV blocks.  Edge-cloud defers the draft to a later
        # draft-FIRST batch, so without retention the blocks could be freed
        # and reused before the cloud-side draft steps read/write them.
        # The EngineCore registers each deferred task locally from the parent
        # SchedulerOutput's head_token before update_from_output. _free_request
        # then delays _free_blocks for referenced requests until the draft task
        # completes or is dropped (release_draft_retained_blocks).
        # Everything is gated on `_edge_cloud_draft_retention_enabled` so
        # deployments without the scheduled edge-cloud draft behave exactly
        # as upstream.
        self._edge_cloud_draft_retention_enabled: bool = (
            self._check_scheduled_edge_cloud_draft()
        )
        self._edge_cloud_draft_req_tasks: dict[str, set[str]] = {}
        self._edge_cloud_draft_task_reqs: dict[str, set[str]] = {}
        self._draft_retained_requests: dict[str, dict[str, Request]] = {}
        # Draft task ids this scheduler dropped from its ready queues
        # while the runner still held the (enqueued) context.  Drained by
        # the EngineCore patch, which forwards them to the runner so the
        # orphaned context is reaped and the retention released.
        self._dropped_draft_task_ids_to_report: list[str] = []
        # Draft task ids whose cloud-side cached metadata will never be
        # (fully) consumed.  Stamped onto outgoing SchedulerOutputs so
        # the cloud model runner can purge the entries instead of
        # leaking them until the bounded cache evicts.
        self._pending_cloud_draft_invalidations: list[str] = []
        # Finishes deliberately withheld from the cloud: the edge keeps a
        # finished-but-chain-referenced request in self.requests and
        # retains its KV blocks, but upstream _free_request has already
        # added it to finished_req_ids, so the next published FIRST batch
        # would tell the cloud runner to remove the row mid-chain.  The
        # cloud's cached whole-batch draft metadata (block tables, seq
        # lens, positions) is laid out by the batch at chain creation;
        # removing a row condenses the live batch and shifts every
        # positional lookup behind it (recycled rows reading another
        # request's KV -> shifted/garbage draft rows).  Withhold the
        # finish on the cloud-bound copy until the chain releases the
        # request, then re-emit it on the next published batch.
        self._cloud_withheld_finished_req_ids: set[str] = set()
        self._cloud_released_finished_req_ids: set[str] = set()

    def invalidate_cloud_draft_tasks(self, task_ids: list[str]) -> None:
        """Queue cloud-side draft metadata invalidations (edge only)."""
        if not self._edge_cloud_draft_retention_enabled:
            return
        self._pending_cloud_draft_invalidations.extend(task_ids)

    def filter_cloud_finished_req_ids(
        self, finished_req_ids: set[str]
    ) -> set[str]:
        """Compute the finished_req_ids a cloud-bound batch should carry.

        The edge retains finished requests that are still referenced by an
        in-flight draft chain (see _free_request): their KV blocks stay
        allocated and they remain in self.requests until the chain
        releases them.  The cloud must apply the SAME retention for its
        batch rows: its cached whole-batch draft metadata is laid out by
        the batch at chain creation, so removing a row mid-chain shifts
        every positional lookup behind it (condense recycles the row for
        another request, and later chain steps then read/write the wrong
        request's KV -- observed as shifted/garbage draft rows and
        verify-time device faults).  Withhold such finishes here and
        re-emit them once release_draft_retained_blocks() drops the last
        referencing task.

        Only the published copy is filtered; the edge worker keeps
        receiving the unmodified SchedulerOutput and cleans up its own
        batch immediately, exactly as before.
        """
        if not self._edge_cloud_draft_retention_enabled:
            return finished_req_ids
        cloud_finished = set(finished_req_ids)
        for req_id in finished_req_ids:
            if not self._edge_cloud_draft_req_tasks.get(req_id):
                continue
            request = self.requests.get(req_id)
            if request is not None and not request.is_finished():
                # req_id was resubmitted while the old request's finish
                # was pending; the new request owns the row now, so the
                # stale finish must reach the cloud before its PREFILL.
                # Withholding it would strand the old row on the cloud.
                logger.error(
                    "[PD] req=%s finished while referenced by draft "
                    "tasks %s but a live request owns the id; NOT "
                    "withholding the finish from the cloud",
                    req_id,
                    self._edge_cloud_draft_req_tasks.get(req_id),
                )
                continue
            cloud_finished.discard(req_id)
            self._cloud_withheld_finished_req_ids.add(req_id)
            logger.info(
                "[PD] withholding cloud finish for req=%s until draft "
                "tasks %s release it",
                req_id,
                self._edge_cloud_draft_req_tasks.get(req_id),
            )
        if self._cloud_released_finished_req_ids:
            still_valid: set[str] = set()
            for req_id in self._cloud_released_finished_req_ids:
                request = self.requests.get(req_id)
                if request is not None and not request.is_finished():
                    # resubmitted while withheld: the new request adopted
                    # the cloud row; emitting the stale finish would
                    # remove the live request's row instead.
                    logger.error(
                        "[PD] withheld finish for req=%s became stale "
                        "(id resubmitted); the cloud row was adopted by "
                        "the new request",
                        req_id,
                    )
                    continue
                still_valid.add(req_id)
            cloud_finished |= still_valid
            self._cloud_released_finished_req_ids = set()
        return cloud_finished

    def schedule(self) -> SchedulerOutput:
        self._recover_stale_prefill_draft_lasts()
        scheduler_output = self._schedule_pd_separated()
        # Only FIRST-segment batches are published to the cloud over PRE_OUT
        # (the publish hook drops PL/DL/DRL tails), and only batches whose
        # cloud-side execution runs the purge hook can deliver the
        # invalidations.  EMPTY batches are not broadcast either.  Stamping
        # any other batch type would silently discard the pending list, so
        # keep the invalidations queued until a cloud-bound batch can carry
        # them.
        if self._pending_cloud_draft_invalidations and (
            scheduler_output.batch_type
            in (
                BatchType.PREFILL_FIRST,
                BatchType.DECODE_FIRST,
                BatchType.PREFILL_DRAFT_FIRST,
                BatchType.DECODE_DRAFT_FIRST,
            )
        ):
            scheduler_output.cloud_draft_invalidate_task_ids = (
                self._pending_cloud_draft_invalidations
            )
            self._pending_cloud_draft_invalidations = []
        return scheduler_output

    def _recover_stale_prefill_draft_lasts(self) -> None:
        """Watchdog for cloud-published PREFILL_DRAFT_LAST (Phase C review).

        The cloud publishes PDFL over POST_OUT (a ZMQ PUSH control
        channel that drops under backpressure) after its worker finishes
        the PDFF middle segment.  Losing a tail is not a normal
        scenario: it wedges the edge permanently (``_force_prefill_
        draft_last`` never clears, the prefill channel stays pinned,
        gated requests freeze) and abort cannot recover it.  There is no
        safe edge-side fallback either -- a self-posted tail would need
        the cloud's isent payload, and re-recv of a late cloud tail
        would hang the channel.  So a tail missing past the watchdog
        interval is treated as an edge-cloud link failure: raise and let
        the deployment layer restart the instance.
        """
        if not self._prefill_draft_last_watchdog:
            return
        now = time.monotonic()
        for task_id in list(self._prefill_draft_last_watchdog):
            deadline = self._prefill_draft_last_watchdog[task_id]
            if now < deadline:
                continue
            if any(
                t.draft_task_id == task_id
                for t in self.prefill_drafts_last_ready
            ):
                # A cloud-published tail is already queued but not yet
                # picked; the normal pick path will complete it.
                self._prefill_draft_last_watchdog.pop(task_id, None)
                continue
            raise RuntimeError(
                f"[PD] PREFILL_DRAFT_LAST lost for task_id={task_id}: "
                f"no cloud tail arrived within "
                f"{self._prefill_draft_last_watchdog_seconds:.1f}s of "
                f"PDFF dispatch.  Edge-cloud link failure (POST_OUT "
                f"dropped or cloud core dead) -- restarting the "
                f"instance is required."
            )

    # ------------------------------------------------------------------ #
    # Chunk-prefill-prior helpers                                         #
    # ------------------------------------------------------------------ #
    def _can_ahead_schedule(self, req_id: str) -> bool:
        """True when the request can have one more chunk PF dispatched ahead."""
        return (
            self._ahead_chunk_count.get(req_id, 0) < self.max_chunk_prefill_ahead
        )

    def _has_other_prefill_request(self, current_req_id: str) -> bool:
        """True if a different request has prefill work ready to fill the next
        prefill slot (a cross-request head-prior candidate).

        Only called from the ahead-decision point inside
        ``_pick_prefill_first_batch``, where ``self.running`` temporarily
        holds the drained ``chunk_prefill_first`` (so other mid-prefill
        requests appear there); the ``is_prefill_chunk`` filter excludes
        decode requests that normally live in ``running``.

        Returns True when any of the following holds:
          - ``chunk_prefill_first`` contains a request with a different id;
          - ``running`` contains a still-prefilling request with a different
            id (drained-window case);
          - ``waiting`` is non-empty (a new request is available).
        """
        for req in self.chunk_prefill_first:
            if req.request_id != current_req_id:
                return True
        running = getattr(self, "running", None)
        if running:
            for req in running:
                if (req.request_id != current_req_id
                        and getattr(req, "is_prefill_chunk", False)):
                    return True
        return len(self.waiting) > 0

    def _should_ahead_schedule(self, req: Request, is_last: bool) -> bool:
        """Decide whether to ahead-dispatch ``req``'s next chunk (intra-request
        pipeline) or yield the prefill slot to another request (cross-request
        head-prior, MindIE-style P1首 -> P2首).

        Ahead (re-add ``req`` to ``chunk_prefill_first``) iff:
          - this is not the last chunk, AND
          - the request's ahead budget allows it, AND
          - next_prefill_prior_enable is off, OR no other request is
            available to fill the slot (single-request pipeline).

        Yield (send ``req`` to ``prefill_last_pending``; the PL-return path
        re-adds it for its next chunk when the tail returns) when
        ``next_prefill_prior_enable`` is on and another request has prefill
        work ready.
        """
        if is_last or not self._can_ahead_schedule(req.request_id):
            return False
        if (self.next_prefill_prior_enable
                and self._has_other_prefill_request(req.request_id)):
            return False
        return True

    def _select_single_prefill_candidate(
        self, candidates: list[Request],
    ) -> tuple[list[Request], list[Request]]:
        """Pick at most one prefill candidate to expose to ``super().schedule()``.

        Enforces the one-request-per-PF-batch invariant. chunk-prefill-prior
        keys one ``PrefillChunkFlight`` per ``head_token`` and the sampler
        consumes a batch-level ``is_last_prefill_chunk`` flag, so a PF batch
        must contain exactly one request. If two requests shared a batch they
        would share one ``head_token`` (the second overwrites the first in
        ``_prefill_flight_by_token``, losing its PL tracking) and the
        batch-level ``is_last`` flag could not represent both requests'
        last-chunk state, stalling the overwritten request.

        Returns ``(exposed, rest)`` where ``exposed`` has 0 or 1 request and
        ``rest`` holds the remaining candidates to be scheduled in their own
        PF batches on subsequent calls.
        """
        if not candidates:
            return [], []
        return [candidates[0]], list(candidates[1:])

    def _select_pf_candidate_head_prior(
        self, candidates: list[Request],
    ) -> tuple[Request | None, list[Request]]:
        """Pick at most one PF candidate for cross-request head-prior.

        Prefers a *fresh* candidate -- one with no in-flight chunk
        (``_pending_tail_count[req] == 0``), i.e. its previous chunk's PL has
        returned and it has no other chunk on the cloud. Refilling a freed
        slot with a fresh candidate keeps one in-flight chunk per request, so
        the two 2P1D prefill slots spread across different requests
        (MindIE-style ``P1首 / P2首`` interleaving).

        Decision order:
          1. First fresh candidate in ``candidates`` -> expose it (refill its
             slot with its next chunk).
          2. No fresh candidate but ``waiting`` is non-empty -> return
             ``(None, candidates)`` so the caller admits a *new* request from
             waiting instead of clustering another chunk on an already
             in-flight request (cross-request head-prior).
          3. No fresh candidate and no waiting request -> fall back to the
             first (in-flight) candidate: ahead-dispatch its next chunk so
             both 2P1D slots serve the single request (intra-request
             pipeline).

        Returns ``(exposed_or_None, rest)`` where ``exposed_or_None`` is 0 or
        1 request. ``rest`` holds the remaining candidates (untouched when
        admitting new, so they stay eligible for later batches).
        """
        for req in candidates:
            if self._pending_tail_count.get(req.request_id, 0) == 0:
                return req, [r for r in candidates if r is not req]
        if len(self.waiting) > 0:
            return None, list(candidates)
        exposed_list, rest = self._select_single_prefill_candidate(candidates)
        return (exposed_list[0] if exposed_list else None), rest

    def _prepare_pf_running_state(
        self,
        saved_chunk_prefill_first: list[Request],
        saved_running: list[Request],
        saved_max_num_running_reqs: int,
    ) -> tuple[list[Request], int, list[Request]]:
        """Decide ``(running, max_num_running_reqs, rest_candidates)`` for the
        ``super().schedule()`` call in ``_pick_prefill_first_batch``.

        - ``chunk_prefill_prior_enable``: enforce one-request-per-PF-batch (the
          flight map keys one flight per ``head_token`` and the sampler reads
          a batch-level ``is_last_prefill_chunk`` flag, so a PF batch must
          contain exactly one request). Candidate selection prefers a fresh
          head (no in-flight chunk) or a new waiting request over clustering
          on an in-flight request -- cross-request head-prior. ``max`` is
          capped at 1 (continue one candidate, no new admission) or a
          capacity-gated 0/1 (admit one new request from waiting).
        - Legacy (``chunk_prefill_prior_enable`` off): no per-chunk flight
          tracking, so multi-request PF batches are safe (PL routes by
          ``req_id``) and preferred for token-budget utilization. Expose all
          candidates and cap by system capacity -- the original behavior.

        The base scheduler caps scheduled running reqs by
        ``max_num_running_reqs`` (vllm ``Scheduler.schedule`` line ~390), so
        the value returned here directly bounds the PF batch size.
        """
        if self.chunk_prefill_prior_enable:
            # 设计 §5.5：被 running 门控推迟的请求（prefill_draft 链未完）
            # 无剩余 prompt 且可能已带 output placeholders，暴露给
            # super().schedule() 会被 base 按 decode 调度进 PF 批次，须从
            # 候选剔除（保留在 chunk_prefill_first 中等链终结迁移）。
            selectable = [
                r for r in saved_chunk_prefill_first
                if r.request_id not in self._running_gated_req_ids
            ]
            deferred = [
                r for r in saved_chunk_prefill_first
                if r.request_id in self._running_gated_req_ids
            ]
            exposed, rest_candidates = self._select_pf_candidate_head_prior(
                selectable
            )
            rest_candidates = rest_candidates + deferred
            if exposed is not None:
                # Continue one candidate; cap at 1 so the base does not admit
                # a new request alongside it (one-per-batch).
                return [exposed], 1, rest_candidates
            # No candidate to continue: admit at most one new request from
            # waiting, gated by system capacity (saved_running occupy their
            # slots) so we never exceed max_num_running_reqs system-wide.
            available = saved_max_num_running_reqs - len(saved_running)
            max_num_running_reqs = 1 if available >= 1 else 0
            return [], max_num_running_reqs, rest_candidates
        if self.limit_prefill_batch_size:
            if saved_chunk_prefill_first:
                return (
                    [saved_chunk_prefill_first[0]],
                    saved_max_num_running_reqs - len(saved_running),
                    [],
                )
            else:
                return (
                    [],
                    saved_max_num_running_reqs - len(saved_running),
                    [],
                )
        return (
            list(saved_chunk_prefill_first),
            saved_max_num_running_reqs - len(saved_running),
            [],
        )

    def _total_pending_tails(self) -> int:
        """Total number of chunks waiting for PL across all requests."""
        return sum(self._pending_tail_count.values())

    def _cleanup_request_flight_state(self, req_id: str) -> None:
        """Remove all tracking state for a finished request."""
        self._pending_tail_count.pop(req_id, None)
        self._ahead_chunk_count.pop(req_id, None)
        # Remove flights for this request.
        to_remove = [
            token for token, flight in self._prefill_flight_by_token.items()
            if flight.request_id == req_id
        ]
        for token in to_remove:
            self._prefill_flight_by_token.pop(token, None)
            # Phase B（设计 §5.2/§9 风险 2）：abort/finish 兜底。只在该槽
            # 已无未完成步且 PL 已完成时 finalize（幂等）；PL/PDFL 仍在飞
            # 时不动作——通道配对由它们完成后的正常递减保证。
            self._try_finalize_prefill_slot(token)

    def _note_prefill_draft_chain_cut(
        self, task_id: str, step_dropped: bool = False
    ) -> None:
        """prefill_draft 链被切断时的记账与 finalize（设计 §5.2）。

        ``step_dropped=True``：一个已入队未派发的 fallback PDFF 被 stale
        drop，其配对 PDFL 从未 self-post，入队时的 +1 无完成事件配对，
        须在此补 -1（pregenerated 步的 PDFL 在 tail 队列必然完成，由
        调用方保证不重复记账）。

        随后若 pending==0 且 PL 已完成，finalize 父 prefill 槽（幂等）。
        """
        if task_id not in self._prefill_slot_pending:
            return
        if step_dropped and self._prefill_slot_pending[task_id] > 0:
            self._prefill_slot_pending[task_id] -= 1
        self._try_finalize_prefill_slot(task_id)

    def _try_finalize_prefill_slot(self, task_id: str) -> None:
        """Finalize the prefill slot when its whole draft chain is done.

        pending==0（PL 哨兵已消费且无未完成步）且 PL 已完成时释放。
        幂等：finalize 后记账 dict 被清理，重复调用 no-op。
        """
        if (
            self._prefill_slot_pending.get(task_id) == 0
            and self._prefill_slot_pl_done.get(task_id, False)
        ):
            self._finalize_prefill_slot(task_id)

    def _finalize_prefill_slot(self, head_token: str) -> None:
        """Release a prefill slot deferred until its draft chain completes.

        Phase B（设计 §5.2）：PF 分配的 Prefill 通道与 prefill_inflight
        计数保持占用到 PL + 全部 PDFL 完成后才在此统一释放（旧逻辑在
        PL 完成时无条件释放，会与同 chunk 复用通道的草稿链 S/R 配对
        冲突）。
        """
        if head_token not in self._prefill_slot_pending:
            return
        if self.prefill_inflight_count > 0:
            self.prefill_inflight_count -= 1
        self.hidden_channel_manager.release_prefill(head_token)
        self._prefill_slot_pending.pop(head_token, None)
        self._prefill_slot_pl_done.pop(head_token, None)
        logger.info(
            "[PD] prefill slot finalized (draft chain complete): "
            "head_token=%s prefill_inflight=%d/%d",
            head_token,
            self.prefill_inflight_count,
            self.prefill_inflight_limit,
        )

    def _migrate_ready_prefill_pending(self) -> None:
        """Move running-gate-deferred requests to running (设计 §5.5).

        PL 完成时被门控推迟的请求（counter>0 或 fallback 链预注册）在链
        终结（final PDFL、`_enqueue_next_draft_first` 返回 False）时由
        update_from_output 调用本函数移入 running。迁移条件只查 counter：
        release_draft_retained_blocks 在 update_from_output 之后才 pop
        `_edge_cloud_draft_task_reqs`，查注册表会误挡 final PDFL 时点的
        迁移（fallback 链在此刻 counter 已 1→0，链确已终结）。触发点唯一
        （PDFL 终结），不依赖每-schedule 扫描——`_update_after_schedule`
        在 pick 函数内以替换态运行，扫描会在 finally 恢复中被丢弃。
        """
        if not self._running_gated_req_ids:
            return
        ready = [
            req_id for req_id in self._running_gated_req_ids
            if self._req_pending_prefill_draft_steps.get(req_id, 0) == 0
        ]
        for req_id in ready:
            self._running_gated_req_ids.discard(req_id)
            req = self.requests.get(req_id)
            if req is None or req.is_finished():
                continue
            # 对抗 review E1：请求被抢占后重新进入 prefill（新 PL 在飞）
            # 时，旧链 final PDFL 的扫描不得把其拖入 running——否则与新
            # PL 完成路径的 append 形成 running 双份。gated 解除后其作为
            # 普通 chunk_prefill_first 候选继续被 PF 调度。
            if req.is_prefill_chunk:
                continue
            # 从两处 defer 目的地（legacy: prefill_last_pending；chunk-
            # prior: chunk_prefill_first）摘除后移入 running。
            self.prefill_last_pending = [
                r for r in self.prefill_last_pending
                if r.request_id != req_id
            ]
            self.chunk_prefill_first = [
                r for r in self.chunk_prefill_first
                if r.request_id != req_id
            ]
            self.running.append(req)
            # 链代记账随迁移一并清空（counter==0 无未结计费）。
            self._req_charged_draft_tasks.pop(req_id, None)
            logger.info(
                "[PD] running gate opened: request=%s moved to running[] "
                "(prefill_draft chain complete, running=%d)",
                req_id,
                len(self.running),
            )

    @staticmethod
    def _pd_flight_key(
        scheduler_output: SchedulerOutput,
        first_batch_type: BatchType,
    ) -> tuple[BatchType, str]:
        if first_batch_type in (
            BatchType.PREFILL_DRAFT_FIRST,
            BatchType.DECODE_DRAFT_FIRST,
        ):
            draft_task_id = scheduler_output.draft_task_id
            if not draft_task_id:
                raise RuntimeError("draft flight is missing draft_task_id")
            if scheduler_output.draft_step_idx is None:
                raise RuntimeError("draft flight is missing draft_step_idx")
            # A speculative chain reuses draft_task_id across multiple steps.
            # Include the step so asynchronously pipelined draft flights do not
            # collide in the active-flight map.
            flight_id = f"{draft_task_id}:{scheduler_output.draft_step_idx}"
        else:
            flight_id = scheduler_output.head_token
            if not flight_id:
                raise RuntimeError(
                    f"{first_batch_type.value} flight is missing head_token"
                )
        return first_batch_type, str(flight_id)

    @staticmethod
    def _pd_flight_request_ids(
        scheduler_output: SchedulerOutput,
    ) -> tuple[str, ...]:
        request_ids = dict.fromkeys(scheduler_output.num_scheduled_tokens)
        if scheduler_output.parent_req_id:
            request_ids.setdefault(scheduler_output.parent_req_id, None)
        return tuple(request_ids)

    def _register_pd_flight(self, scheduler_output: SchedulerOutput) -> None:
        """Protect requests in a First batch until its Last batch finishes."""
        first_batch_type = scheduler_output.batch_type
        last_batch_type = _PD_FIRST_TO_LAST.get(first_batch_type)
        if last_batch_type is None:
            raise RuntimeError(
                f"Cannot register non-First PD batch: {first_batch_type}"
            )

        key = self._pd_flight_key(scheduler_output, first_batch_type)
        if key in self._pd_active_flight_by_key:
            raise RuntimeError(f"Duplicate active PD flight: {key}")

        request_ids = self._pd_flight_request_ids(scheduler_output)
        if not request_ids:
            raise RuntimeError(
                f"{first_batch_type.value} flight has no associated requests"
            )

        self._pd_active_flight_by_key[key] = PDActiveFlight(
            request_ids=request_ids,
            first_batch_type=first_batch_type,
            last_batch_type=last_batch_type,
            flight_id=key[1],
            created_at=time.monotonic(),
        )
        for req_id in request_ids:
            self._pd_active_flight_count[req_id] = (
                self._pd_active_flight_count.get(req_id, 0) + 1
            )

    def _complete_pd_flight(self, scheduler_output: SchedulerOutput) -> bool:
        """Unprotect requests after a matching Last batch has completed."""
        last_batch_type = scheduler_output.batch_type
        first_batch_type = _PD_LAST_TO_FIRST.get(last_batch_type)
        if first_batch_type is None:
            raise RuntimeError(
                f"Cannot complete non-Last PD batch: {last_batch_type}"
            )

        key = self._pd_flight_key(scheduler_output, first_batch_type)
        flight = self._pd_active_flight_by_key.pop(key, None)
        if flight is None:
            logger.warning(
                "Ignoring stale or duplicate %s flight completion: key=%s",
                last_batch_type.value,
                key,
            )
            return False
        if flight.last_batch_type != last_batch_type:
            raise RuntimeError(
                "PD flight type mismatch: "
                f"expected={flight.last_batch_type}, got={last_batch_type}, "
                f"key={key}"
            )

        for req_id in flight.request_ids:
            count = self._pd_active_flight_count.get(req_id, 0)
            if count <= 0:
                raise RuntimeError(
                    "PD active flight count underflow: "
                    f"request_id={req_id}, key={key}"
                )
            if count == 1:
                self._pd_active_flight_count.pop(req_id)
            else:
                self._pd_active_flight_count[req_id] = count - 1
        return True

    def _is_request_preemptible(self, request: Request) -> bool:
        """Only idle RUNNING requests are safe preemption candidates."""
        return (
            request.status == RequestStatus.RUNNING
            and self._pd_active_flight_count.get(request.request_id, 0) == 0
            # 对抗 review E1：running 门控推迟中的请求（prefill_draft 链
            # 未完）不可抢占——其链仍在飞且 KV 保留被链引用，抢占后重
            # prefill 会与旧链 final PDFL 的迁移扫描形成 running 双份。
            and request.request_id not in self._running_gated_req_ids
        )

    def _select_preemption_candidate(self) -> Request | None:
        """Select an idle request without touching active edge-cloud work."""
        if self.policy == SchedulingPolicy.PRIORITY:
            candidates = (
                request
                for request in self.running
                if self._is_request_preemptible(request)
            )
            return max(
                candidates,
                key=lambda request: (request.priority, request.arrival_time),
                default=None,
            )

        return next(
            (
                request
                for request in reversed(self.running)
                if self._is_request_preemptible(request)
            ),
            None,
        )

    def _make_empty_batch(self) -> SchedulerOutput:
        scheduler_output = SchedulerOutput.make_empty()
        scheduler_output.finished_req_ids = self.finished_req_ids
        self.finished_req_ids = set()
        return scheduler_output

    def _schedule_pd_separated(self) -> SchedulerOutput:
        state = self._prefill_state()
        scheduler_output = self._pick_by_state(state)
        has_work = scheduler_output.total_num_scheduled_tokens > 0
        is_tail = scheduler_output.batch_type in (
            BatchType.PREFILL_LAST,
            BatchType.DECODE_LAST,
        )
        if has_work or is_tail:
            self._log_scheduler_state(state, scheduler_output.batch_type)
        # Stamp whether this batch carries any multimodal request so the
        # cloud's CHER early-recv hint (built in PassiveEC.step from this SO)
        # can decide whether to irecv mrope_positions. The passive cloud has
        # NO request registry (mm_features do not cross the edge->cloud SO
        # boundary for cached reqs - scheduled_cached_reqs carries only
        # req_ids), so the edge scheduler - which owns self.requests - is the
        # only place this can be computed. The expression mirrors
        # NPUModelRunner.step_has_multimodal_req exactly; self.requests here
        # (at scheduling time) == model_runner.requests at execute time (both
        # reflect this step), so the cloud hint's has_mrope matches the edge
        # sender's include_mrope bit-for-bit (eliminates the mixed-batch
        # mismatch). Dynamic attr; survives the edge->cloud SO pickle
        # (SchedulerOutput has no __slots__ - PassiveScheduler already relies
        # on this for _ARRIVAL_SEQ_ATTR).
        scheduler_output.has_mrope = (
            any(req.mm_features for req in self.requests.values())
            or any(getattr(nr, "mm_features", None)
                   for nr in scheduler_output.scheduled_new_reqs)
        )
        return scheduler_output

    def _pick_by_state(self, state: PrefillState) -> SchedulerOutput:
        if self._decode_first_placeholder_parent is not None:
            self._prepare_next_decode_first_placeholder(
                self._decode_first_placeholder_parent
            )
        # A placeholder DECODE_FIRST prepared when the final draft tail was
        # dispatched must stay immediately behind that draft tail.  Its real
        # draft token IDs are filled from the worker-local _draft_token_ids
        # buffer when it executes, exactly like native async spec decode.
        # Dispatch is gated on both remote-pending counts == 0 only: the
        # channel invariant is that no draft FIRST may still be at the cloud
        # when a DECODE_FIRST goes out (they use different recv primitives
        # on the same stream).  Ordering against *queued* draft steps of an
        # interleaved chain is enforced at creation time instead (see
        # _prepare_next_decode_first_placeholder): the placeholder is only
        # pre-built once no other draft work remains, because its creation
        # already claims decode_or_draft_inflight/decode_head_inflight --
        # gating the pop on empty draft queues would deadlock against the
        # draft picks waiting for those very counters.
        # Do NOT gate on decode_or_draft_inflight_count here either: it was
        # incremented by the placeholder's own creation.  Gating costs no
        # extra round trip (the placeholder is pre-built); it only removes
        # the unsafe overlap window.  Fall through to the normal priority
        # picks while gated.
        # Phase B（设计 §6.2）：prefill_draft 已迁出 DECODE 通道，placeholder
        # 窗口只需 gate decode 域；prefill 域的 remote pending 不再占用
        # DECODE 通道，无需参与本门控。
        # Phase B（设计 §5.5）：_can_schedule_decode_first 已不再要求
        # "无任何 draft 工作"（旧注释的互斥依据已失效）——请求级安全改由
        # running 门控保证：prefill_draft 链未完成的请求不会进入 running，
        # 故不会被 DECODE_FIRST 调度；placeholder 的父请求链已终结，其
        # verify 只受 decode 域交替约束。
        if (
            self.decodes_first_ready
            and self.decode_draft_remote_pending_count == 0
        ):
            return self.decodes_first_ready.popleft()

        # [FORCE] decode 域 first-only 窗口（设计 §6.3.2）：DL/DDL pick
        # 后 30ms 内只允许 DF/DDF。draft 链排队时释放窗口（链 FIFO 即
        # 节奏，且防链排空后残留超时误报——原消费函数内联于此）；选中
        # first 即解除；超时自动解除并打 warning（状态机内）。
        if self._has_draft_work():
            self._force.release_for_draft_work()
        elif self._force.decode_first_only_active():
            if self._can_schedule_decode_draft_first():
                self._force.clear_decode_first_only()
                return self._pick_decode_draft_first_batch()
            if self._can_schedule_decode_first():
                self._force.clear_decode_first_only()
                return self._pick_decode_first_batch()
            return self._make_empty_batch()

        # [FORCE] prefill 域 first-only 窗口（第 3/4 点强制等待）：PL(MTP)/
        # 非末跳 PDFL pick 后 15ms 内只允许 PREFILL_DRAFT_FIRST。与
        # decode 窗口互斥（窗口均在选中 first 或超时时解除，同一时刻
        # 至多一个激活）。
        if self._has_draft_work():
            self._force.release_for_draft_work()
        elif self._force.prefill_draft_first_only_active():
            if self._can_schedule_prefill_draft_first():
                self._force.clear_prefill_draft_first_only()
                return self._pick_prefill_draft_first_batch()
            return self._make_empty_batch()

        if state == PrefillState.IDLE:
            # IDLE: prefill_draft首 > prefill_draft尾 > P首 > decode_draft首
            #       > decode_draft尾 > D首 > D尾 > P尾 > Empty
            # prefill_draft 链在服时其父槽已释放（Phase A 计数），尽快跑完
            # 链再起新 P首，避免草稿堆积。
            if (
                self.prefill_drafts_first_ready
                and self._can_schedule_prefill_draft_first()
            ):
                return self._pick_prefill_draft_first_batch()
            if (
                self.prefill_drafts_last_ready
                and self._can_schedule_prefill_draft_last()
            ):
                return self._pick_prefill_draft_last_batch()
            if self._can_schedule_prefill_first():
                so = self._pick_prefill_first_batch()
                if so.total_num_scheduled_tokens > 0:
                    return so
                logger.warning(
                    "PREFILL_FIRST returned empty batch (total_num_scheduled_tokens=0). "
                    "This usually means KV cache blocks are exhausted by running decode "
                    "requests. Prefill work will be deferred until resources are freed."
                )
                self.finished_req_ids.update(so.finished_req_ids)
            if (
                self.decode_drafts_first_ready
                and self._can_schedule_decode_draft_first()
            ):
                return self._pick_decode_draft_first_batch()
            if (
                self.decode_drafts_last_ready
                and self._can_schedule_decode_draft_last()
            ):
                return self._pick_decode_draft_last_batch()
            if self._can_schedule_decode_first():
                return self._pick_decode_first_batch()
            # A queued placeholder DECODE_FIRST already self-posted its tail
            # into decodes_last_ready at creation time; while the head is
            # gated above, the tail must not overtake it (the worker would
            # find no suspended HeadState for it).
            if (
                self.decodes_last_ready
                and not self.decodes_first_ready
                and self._can_schedule_decode_last()
            ):
                return self._pick_decode_last_batch()
            if self.prefills_last_ready:
                return self._pick_prefill_last_batch()
            return self._make_empty_batch()

        if state == PrefillState.LOW:
            # LOW: P首(若槽可用) > P尾 > prefill_draft首 > prefill_draft尾
            #      > decode_draft首 > decode_draft尾 > D首 > D尾 > Empty
            if self._can_schedule_prefill_first():
                so = self._pick_prefill_first_batch()
                if so.total_num_scheduled_tokens > 0:
                    return so
                logger.warning(
                    "PREFILL_FIRST returned empty batch (total_num_scheduled_tokens=0). "
                    "This usually means KV cache blocks are exhausted by running decode "
                    "requests. Prefill work will be deferred until resources are freed."
                )
                self.finished_req_ids.update(so.finished_req_ids)
            if self.prefills_last_ready:
                return self._pick_prefill_last_batch()
            if (
                self.prefill_drafts_first_ready
                and self._can_schedule_prefill_draft_first()
            ):
                return self._pick_prefill_draft_first_batch()
            if (
                self.prefill_drafts_last_ready
                and self._can_schedule_prefill_draft_last()
            ):
                return self._pick_prefill_draft_last_batch()
            if (
                self.decode_drafts_first_ready
                and self._can_schedule_decode_draft_first()
            ):
                return self._pick_decode_draft_first_batch()
            if (
                self.decode_drafts_last_ready
                and self._can_schedule_decode_draft_last()
            ):
                return self._pick_decode_draft_last_batch()
            if self._can_schedule_decode_first():
                return self._pick_decode_first_batch()
            if (
                self.decodes_last_ready
                and not self.decodes_first_ready
                and self._can_schedule_decode_last()
            ):
                return self._pick_decode_last_batch()
            return self._make_empty_batch()

        # HIGH: P尾 > prefill_draft首 > prefill_draft尾 > decode_draft首
        #       > decode_draft尾 > D首 > D尾 > Empty
        if self.prefills_last_ready:
            return self._pick_prefill_last_batch()
        if (
            self.prefill_drafts_first_ready
            and self._can_schedule_prefill_draft_first()
        ):
            return self._pick_prefill_draft_first_batch()
        if (
            self.prefill_drafts_last_ready
            and self._can_schedule_prefill_draft_last()
        ):
            return self._pick_prefill_draft_last_batch()
        if (
            self.decode_drafts_first_ready
            and self._can_schedule_decode_draft_first()
        ):
            return self._pick_decode_draft_first_batch()
        if (
            self.decode_drafts_last_ready
            and self._can_schedule_decode_draft_last()
        ):
            return self._pick_decode_draft_last_batch()
        if self._can_schedule_decode_first():
            return self._pick_decode_first_batch()
        # Same overtake guard as the IDLE branch above: a queued placeholder
        # DECODE_FIRST's self-posted tail must wait for its head.
        if (
            self.decodes_last_ready
            and not self.decodes_first_ready
            and self._can_schedule_decode_last()
        ):
            return self._pick_decode_last_batch()
        return self._make_empty_batch()

    def is_waiting_for_remote_tail(self) -> bool:
        """True when local requests exist only as remote in-flight work.

        In this state the edge has no local batch to execute until POST_OUT
        returns a PREFILL_LAST/DECODE_LAST, so the EngineCore should yield
        instead of tight-loop scheduling EMPTY batches.
        """
        return bool(
            (
                self.prefill_inflight_count > 0
                or self.decode_or_draft_inflight_count > 0
                or self.prefill_draft_remote_pending_count > 0
                or self.decode_draft_remote_pending_count > 0
            )
            and not self.prefills_last_ready
            and not self.decodes_last_ready
            and not self.prefill_drafts_last_ready
            and not self.decode_drafts_last_ready
            and not self._can_schedule_prefill_first()
            and not self._can_schedule_prefill_draft_first()
            and not self._can_schedule_decode_draft_first()
            and not self._can_schedule_decode_first()
        )

    def _prefill_state(self) -> PrefillState:
        if self.prefill_inflight_count <= 0:
            return PrefillState.IDLE
        if (
            self.prefill_inflight_limit > 1
            and self.prefill_inflight_count >= self.prefill_inflight_limit
        ):
            return PrefillState.HIGH
        return PrefillState.LOW

    def _has_prefill_work(self) -> bool:
        # gated（prefill_draft 链未完）请求驻留 chunk_prefill_first 期间
        # 不应触发 PF 尝试：尝试必空（_prepare_pf_running_state 会将其
        # 剔除），只产生空返回 warning 与空转。判定与
        # _prepare_pf_running_state 的 selectable 构造逐位一致——非 gated
        # 候选（其他请求的 chunk）或 waiting 新请求仍允许调度，2P/多请求
        # 行为不变。
        return bool(
            self.waiting
            or any(
                r.request_id not in self._running_gated_req_ids
                for r in self.chunk_prefill_first
            )
        )

    def _can_schedule_prefill_first(self) -> bool:
        # When running decode requests already fill max_num_running_reqs,
        # super().schedule() inside _pick_prefill_first_batch will return an
        # empty batch, causing a tight-loop.  Pre-check capacity to avoid
        # the useless call.
        effective_capacity = self.max_num_running_reqs - len(self.running)
        return (
            self._has_prefill_work()
            and self.prefill_inflight_count < self.prefill_inflight_limit
            and self.hidden_channel_manager.has_free_prefill()
            and effective_capacity > 0
        )

    def _can_schedule_decode_first(self) -> bool:
        # 4 域拆分（设计 §6.1）：decode 只受 decode 域标记/队列约束；
        # Phase B 后 prefill_draft 已迁出 DECODE 通道，prefill 域队列
        # 与 remote pending 不再 gate decode 域。
        # [FORCE] 交替门控收敛到状态机（设计 §6.3.2）。
        return bool(
            self.running
            and self.decode_or_draft_inflight_count == 0
            and self.decode_draft_remote_pending_count == 0
            and not self.decode_drafts_first_ready
            and not self.decode_drafts_last_ready
            and self._force.can_pick_decode_first()
        )

    def _can_schedule_prefill_draft_first(self) -> bool:
        if not self.prefill_drafts_first_ready:
            return False
        next_output = self.prefill_drafts_first_ready[0]
        is_pregenerated = (
            next_output.draft_task_id in self._pregenerated_draft_task_ids
        )
        if is_pregenerated:
            # 语义与旧 _can_schedule_draft_first pregenerated 分支一致：
            # PDFF -> PDFL 交替由 FORCE 状态机保证
            # （[FORCE] can_pick_prefill_draft_first，设计 §6.3.2）；
            # 草稿链可流水：下一个 PDFF 在前一个 PDFL 在飞时即可派发。
            # Phase B（设计 §6.1）：prefill 域已迁出 DECODE 通道，decode
            # 头/标记不再 gate prefill 域。
            return bool(
                self.prefill_draft_remote_pending_count
                < self._prefill_draft_remote_pending_limit
                and not self.prefill_drafts_last_ready
                and self._force.can_pick_prefill_draft_first()
            )

        # Phase B（设计 §4.1）：scheduled draft head/tail 负载走继承的
        # prefill 通道，不再与 DECODE 通道争用；只保留 prefill 域自身
        # 的 remote pending / 队列交替约束。
        return bool(
            self.prefill_draft_remote_pending_count == 0
            and not self.prefill_drafts_last_ready
            and self._force.can_pick_prefill_draft_first()
        )

    def _can_schedule_decode_draft_first(self) -> bool:
        if not self.decode_drafts_first_ready:
            return False
        next_output = self.decode_drafts_first_ready[0]
        is_pregenerated = (
            next_output.draft_task_id in self._pregenerated_draft_task_ids
        )
        if is_pregenerated:
            # 与 _can_schedule_prefill_draft_first 的 pregenerated 分支
            # 同构，仅作用于 decode 域计数/标记（设计 §6.1）。
            # [FORCE] 交替门控收敛到状态机（设计 §6.3.2）。
            return bool(
                self.decode_head_inflight_count == 0
                and self.decode_draft_remote_pending_count
                < self._decode_draft_remote_pending_limit
                and not self.decode_drafts_last_ready
                and self._force.can_pick_decode_draft_first()
            )

        # Scheduled draft head/tail payloads used to share the DECODE
        # channel, forcing full serialization (==0 gate): with a second
        # chain in flight, edge and cloud could each wait for the
        # opposite-direction send before posting the matching recv.  With
        # the dedicated DRAFT channel (P0) per-direction FIFO matching
        # makes concurrent chains safe, so when pipelining is enabled the
        # gate relaxes to the pregenerated form: inflight < limit and
        # remote_pending < limit (default 2).  Off (legacy ==0) by default.
        self._decode_draft_pipeline_enable: bool = False
        if self._decode_draft_pipeline_enable:
            # inflight_limit is hardcoded 1 (legacy); under pipelining the
            # effective cap is the same remote-pending limit (default 2)
            # that governs the pregenerated branch.
            return bool(
                self.decode_or_draft_inflight_count
                < self._decode_draft_remote_pending_limit
                and self.decode_draft_remote_pending_count
                < self._decode_draft_remote_pending_limit
                and not self.decode_drafts_last_ready
                and self._force.can_pick_decode_draft_first()
            )
        return bool(
            self.decode_or_draft_inflight_count == 0
            and self.decode_draft_remote_pending_count == 0
            and not self.decode_drafts_last_ready
            and self._force.can_pick_decode_draft_first()
        )

    def _log_scheduler_state(self, state: PrefillState, batch_type: BatchType) -> None:
        self._step_counter += 1
        if self.chunk_prefill_prior_enable:
            logger.info(
                f"[PD] Step{self._step_counter}, state is {state}, batch_type is {batch_type}, "
                f"waiting[]: {len(self.waiting)}, "
                f"chunk_prefill_first[]: {len(self.chunk_prefill_first)}, "
                f"prefill_last_pending[]: {len(self.prefill_last_pending)}, "
                f"running[]: {len(self.running)}, "
                f"prefills_last_ready[]: {len(self.prefills_last_ready)}, "
                f"prefill_drafts_first_ready[]: {len(self.prefill_drafts_first_ready)}, "
                f"prefill_drafts_last_ready[]: {len(self.prefill_drafts_last_ready)}, "
                f"decode_drafts_first_ready[]: {len(self.decode_drafts_first_ready)}, "
                f"decode_drafts_last_ready[]: {len(self.decode_drafts_last_ready)}, "
                f"decodes_last_ready[]: {len(self.decodes_last_ready)}, "
                f"prefill_inflight: {self.prefill_inflight_count}/{self.prefill_inflight_limit}, "
                f"prefill_draft_remote_pending: {self.prefill_draft_remote_pending_count}, "
                f"decode_draft_remote_pending: {self.decode_draft_remote_pending_count}, "
                f"decode_or_draft_inflight: {self.decode_or_draft_inflight_count}/{self.decode_or_draft_inflight_limit}, "
                f"chunk_flights: {len(self._prefill_flight_by_token)}, "
                f"pending_tails: {self._total_pending_tails()}, "
                f"ahead_chunks: {sum(self._ahead_chunk_count.values())}",
            )
        else:
            logger.info(
                f"[PD] Step{self._step_counter}, state is {state}, batch_type is {batch_type}, "
                f"waiting[]: {len(self.waiting)}, "
                f"chunk_prefill_first[]: {len(self.chunk_prefill_first)}, "
                f"prefill_last_pending[]: {len(self.prefill_last_pending)}, "
                f"running[]: {len(self.running)}, "
                f"prefills_last_ready[]: {len(self.prefills_last_ready)}, "
                f"prefill_drafts_first_ready[]: {len(self.prefill_drafts_first_ready)}, "
                f"prefill_drafts_last_ready[]: {len(self.prefill_drafts_last_ready)}, "
                f"decode_drafts_first_ready[]: {len(self.decode_drafts_first_ready)}, "
                f"decode_drafts_last_ready[]: {len(self.decode_drafts_last_ready)}, "
                f"decodes_last_ready[]: {len(self.decodes_last_ready)}, "
                f"prefill_inflight: {self.prefill_inflight_count}/{self.prefill_inflight_limit}, "
                f"prefill_draft_remote_pending: {self.prefill_draft_remote_pending_count}, "
                f"decode_draft_remote_pending: {self.decode_draft_remote_pending_count}, "
                f"decode_or_draft_inflight: {self.decode_or_draft_inflight_count}/{self.decode_or_draft_inflight_limit}",
            )

    # ------------------------------------------------------------------ #
    # Layer-slice config loading (Edge side)                             #
    # ------------------------------------------------------------------ #
    def _load_layer_slice_config(self) -> None:
        """Load decode_last_delay_schedule_ms from layer_slice_config.yaml."""
        yaml_path = os.environ.get("VLLM_LAYER_SLICE_CONFIG")
        if yaml_path is None:
            yaml_path = os.path.join(
                os.path.dirname(__file__), "layer_slice_config.yaml"
            )
        if not os.path.exists(yaml_path):
            self._layer_slice_config_path = None
            self._layer_slice_config_mtime = 0.0
            return
        try:
            import yaml
            with open(yaml_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
            if not isinstance(raw, dict):
                logger.warning(
                    "Layer-slice config %s is not a dict; ignoring.", yaml_path
                )
                return
            _key = "decode_last_delay_schedule_ms"
            if _key in raw:
                try:
                    self._decode_last_delay_schedule_ms = int(raw[_key])
                    logger.info(
                        "[PDSeparatedScheduler] %s set to %d from %s",
                        _key, self._decode_last_delay_schedule_ms, yaml_path,
                    )
                except (ValueError, TypeError):
                    logger.warning(
                        "Invalid %s value %r in %s; keeping %d",
                        _key, raw[_key], yaml_path,
                        self._decode_last_delay_schedule_ms,
                    )
            # 4 域拆分（设计 §6.2）：旧键 draft_last_delay_schedule_ms 作为
            # 兼容别名同时设置两个新值；新键逐个覆盖。
            for _key, _attr in (
                ("draft_last_delay_schedule_ms",
                 ("_prefill_draft_last_delay_schedule_ms",
                  "_decode_draft_last_delay_schedule_ms")),
            ):
                if _key in raw:
                    try:
                        _value = int(raw[_key])
                        for _name in _attr:
                            setattr(self, _name, _value)
                        logger.info(
                            "[PDSeparatedScheduler] %s set to %d from %s",
                            _key, _value, yaml_path,
                        )
                    except (ValueError, TypeError):
                        logger.warning(
                            "Invalid %s value %r in %s; keeping %d",
                            _key, raw[_key], yaml_path,
                            getattr(self, _attr[0]),
                        )
            for _key, _attr in (
                ("prefill_draft_last_delay_schedule_ms",
                 "_prefill_draft_last_delay_schedule_ms"),
                ("decode_draft_last_delay_schedule_ms",
                 "_decode_draft_last_delay_schedule_ms"),
            ):
                if _key in raw:
                    try:
                        setattr(self, _attr, int(raw[_key]))
                        logger.info(
                            "[PDSeparatedScheduler] %s set to %d from %s",
                            _key, getattr(self, _attr), yaml_path,
                        )
                    except (ValueError, TypeError):
                        logger.warning(
                            "Invalid %s value %r in %s; keeping %d",
                            _key, raw[_key], yaml_path,
                            getattr(self, _attr),
                        )
            # [EHER-draft] Readiness-ack gate switch: replace the fixed
            # DDL delay pacing with worker-reported recv readiness (see
            # _can_schedule_decode_draft_last).  Off by default.
            _ack_raw = raw.get("decode_draft_recv_ack_enable")
            if _ack_raw is not None:
                self._decode_draft_recv_ack_enable = bool(_ack_raw)
                logger.info(
                    "[PDSeparatedScheduler] decode_draft_recv_ack_enable "
                    "set to %s from %s",
                    self._decode_draft_recv_ack_enable, yaml_path,
                )
            # [P2] Decode-draft pipelining switch: relax the serial ==0
            # draft-first gate to < limit now that drafts own the DRAFT
            # channel (see _can_schedule_decode_draft_first).  Off by
            # default.
            _pipe_raw = raw.get("decode_draft_pipeline_enable")
            if _pipe_raw is not None:
                self._decode_draft_pipeline_enable = bool(_pipe_raw)
                logger.info(
                    "[PDSeparatedScheduler] decode_draft_pipeline_enable "
                    "set to %s from %s",
                    self._decode_draft_pipeline_enable, yaml_path,
                )
            self._layer_slice_config_path = yaml_path
            self._layer_slice_config_mtime = os.path.getmtime(yaml_path)
        except Exception:
            logger.exception("Failed to load layer-slice config from %s", yaml_path)

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
            old_value = self._decode_last_delay_schedule_ms
            self._load_layer_slice_config()
            if self._decode_last_delay_schedule_ms != old_value:
                logger.info(
                    "[PDSeparatedScheduler] Layer-slice config hot-reloaded: "
                    "%s=%d",
                    "decode_last_delay_schedule_ms",
                    self._decode_last_delay_schedule_ms,
                )

    # ------------------------------------------------------------------ #
    # DECODE_LAST delay scheduling                                       #
    # ------------------------------------------------------------------ #
    def _start_decode_last_delay(self) -> None:
        """Start the timer when DECODE_FIRST is picked.
        DECODE_LAST cannot be scheduled until the delay expires."""
        self._decode_last_delay_start_ts = time.monotonic()

    def _can_schedule_decode_last(self) -> bool:
        """Return True if the delay since DECODE_FIRST has elapsed."""
        if self._decode_last_delay_start_ts is None:
            return True
        elapsed_ms = (time.monotonic() - self._decode_last_delay_start_ts) * 1000
        if elapsed_ms >= self._decode_last_delay_schedule_ms:
            self._decode_last_delay_start_ts = None
            return True
        # logger.info(
        #     "[PD] DECODE_LAST delayed: elapsed=%.1f ms < limit=%d ms",
        #     elapsed_ms, self._decode_last_delay_schedule_ms,
        # )
        return False

    # ------------------------------------------------------------------ #
    # Draft-last delay scheduling (4 域拆分，设计 §6.2)                    #
    # ------------------------------------------------------------------ #
    def _start_decode_draft_last_delay(self) -> None:
        """decode_draft首 pick 后启动，decode_draft尾 在延迟到期前不可调度。

        解码域尾由边侧自生成，保留 5ms（默认）延迟 pacing。
        """
        self._decode_draft_last_delay_start_ts = time.monotonic()

    def notify_draft_recv_ready(self, head_token: str) -> None:
        """[EHER-draft] Worker reported a DDL return irecv complete."""
        self._draft_recv_ready_acks.add(head_token)

    def _can_schedule_decode_draft_last(self) -> bool:
        """Return True if the delay since DECODE_DRAFT_FIRST has elapsed."""
        if self._decode_draft_recv_ack_enable:
            # Readiness gate: the oldest queued DDL is schedulable once its
            # return transfer has landed (worker ack).  Fallback to the
            # delay timer after a safety timeout so a missing ack path
            # (no early post / sideband not attached) can never stall the
            # pipeline -- tails must always eventually execute to keep the
            # hidden channel paired.
            if not self.decode_drafts_last_ready:
                return True
            front = self.decode_drafts_last_ready[0]
            head_token = getattr(front, "head_token", None)
            if head_token is None or head_token in self._draft_recv_ready_acks:
                return True
            if self._decode_draft_last_delay_start_ts is not None:
                elapsed_ms = (
                    time.monotonic()
                    - self._decode_draft_last_delay_start_ts
                ) * 1000
                timeout_ms = max(
                    10 * self._decode_draft_last_delay_schedule_ms, 100
                )
                if elapsed_ms >= timeout_ms:
                    logger.warning(
                        "[EHER-draft] DDL head_token=%s ack timeout after "
                        "%.0fms; dispatching on the delay fallback",
                        head_token, elapsed_ms,
                    )
                    return True
            return False
        if self._decode_draft_last_delay_start_ts is None:
            return True
        elapsed_ms = (
            time.monotonic() - self._decode_draft_last_delay_start_ts
        ) * 1000
        if elapsed_ms >= self._decode_draft_last_delay_schedule_ms:
            self._decode_draft_last_delay_start_ts = None
            return True
        return False

    def _can_schedule_prefill_draft_last(self) -> bool:
        """Return True if the prefill draft tail is schedulable.

        Phase C（设计 §6.2）：PDFL 由云侧 POST_OUT 发布，云侧往返即
        pacing——边侧不再自贴尾、无延迟计时，恒可调度。保留此门控
        （恒 True）以维持 `_pick_by_state` 的结构与回退路径。
        """
        return True

    def _pick_prefill_first_batch(self) -> SchedulerOutput:
        saved_running = self.running
        saved_chunk_prefill_first = self.chunk_prefill_first
        saved_max_num_running_reqs = self.max_num_running_reqs

        # Decide what to expose to super().schedule() and the running cap.
        # With chunk_prefill_prior_enable this enforces one-request-per-PF-batch
        # (prevents head_token collision / is_last ambiguity); legacy keeps the
        # original multi-request batching. See _prepare_pf_running_state.
        self.running, self.max_num_running_reqs, rest_candidates = self._prepare_pf_running_state(
            saved_chunk_prefill_first, saved_running, saved_max_num_running_reqs
        )

        if self.limit_prefill_batch_size:
            # 限制每个 P首 batch 最多只包含 1 个请求。
            # 1. chunk_prefill_first 非空时，取第一个请求到 running，
            #    清空 waiting 防止 super().schedule() 再取更多。
            # 2. chunk_prefill_first 为空时，从 waiting 中只保留 1 个请求，
            #    让 super().schedule() 在 waiting 中正常调度（生成 NewRequestData）。
            #    其余 waiting 请求暂存，在 finally 中恢复。
            if saved_chunk_prefill_first:
                self.chunk_prefill_first = list(saved_chunk_prefill_first[1:])
                saved_waiting_rest = []
            else:
                self.chunk_prefill_first = []
                if len(self.waiting) > 0:
                    first_req = self.waiting.pop_request()
                    saved_waiting_rest = list(self.waiting)
                    self.waiting.clear()
                    self.waiting.append(first_req)
                else:
                    saved_waiting_rest = []
        else:
            self.chunk_prefill_first = []
            saved_waiting_rest = []


        # Snapshot num_computed_tokens before super().schedule() so that
        # the is_last computation below uses the pre-schedule value.
        # (super().schedule() → _update_after_schedule increments
        # num_computed_tokens; without the snapshot we would double-count
        # the current chunk's tokens.)
        _num_computed_before: dict[str, int] = {
            req.request_id: req.num_computed_tokens
            for req in self.running
        }

        scheduler_output = None
        try:
            scheduler_output = super().schedule()
        finally:
            self.max_num_running_reqs = saved_max_num_running_reqs

            if scheduler_output is not None:
                if scheduler_output.total_num_scheduled_tokens == 0:
                    scheduler_output.batch_type = BatchType.EMPTY
                    for req in self.running:
                        if req.is_prefill_chunk:
                            self.chunk_prefill_first.append(req)
                        else:
                            self.prefill_last_pending.append(req)
                    # KV cache exhausted: super().schedule() scheduled nothing.
                    # _prepare_pf_running_state swapped self.running for the
                    # prefill candidate(s), so we MUST restore self.running =
                    # saved_running here too (the non-empty branch restores
                    # below).  Without this restore the decode requests that
                    # were in self.running are lost -- _can_schedule_decode_first
                    # never sees them, KV is never freed by finished decodes, and
                    # prefill keeps returning empty -> deadlock.  rest_candidates
                    # (candidates not exposed to super() this round, incl.
                    # running-gate-deferred requests) are re-prepended once by
                    # the shared restore below -- do NOT add them again here or
                    # chunk_prefill_first doubles every empty round.
                    self.running = saved_running
                else:
                    scheduler_output.batch_type = BatchType.PREFILL_FIRST
                    scheduler_output.head_token = uuid4().hex
                    scheduler_output.hidden_channel = (
                        self.hidden_channel_manager.allocate_prefill(
                            scheduler_output.head_token
                        )
                    )
                    self.prefill_inflight_count += 1
                    # Phase B（设计 §5.2）：槽推迟释放记账——pending 记 1
                    # 等待 PL 完成，pl_done 置 False。
                    self._prefill_slot_pending[
                        scheduler_output.head_token
                    ] = 1
                    self._prefill_slot_pl_done[
                        scheduler_output.head_token
                    ] = False
                    self._register_pd_flight(scheduler_output)

                    scheduled_req_ids = set(
                        scheduler_output.num_scheduled_tokens.keys()
                    )

                    if self.chunk_prefill_prior_enable:
                        # === Chunk-prefill-prior routing ===
                        # Each scheduled request gets a PerfillChunkFlight.
                        # If the request still has more chunks after this
                        # PF, it may be re-added to chunk_prefill_first
                        # immediately (ahead), allowing the next chunk's PF
                        # before the current chunk's PL returns.
                        for req in self.running:
                            if req.request_id in scheduled_req_ids:
                                num_scheduled = (
                                    scheduler_output.num_scheduled_tokens[
                                        req.request_id
                                    ]
                                )
                                # Use pre-schedule num_computed_tokens
                                # to avoid double-counting the current
                                # chunk's tokens.
                                num_comp_before = (
                                    _num_computed_before.get(
                                        req.request_id, 0
                                    )
                                )
                                remaining = (
                                    req.num_prompt_tokens
                                    - num_comp_before
                                    - num_scheduled
                                )
                                is_last = remaining <= 0
                                flight = PrefillChunkFlight(
                                    request_id=req.request_id,
                                    head_token=scheduler_output.head_token,
                                    hidden_channel=(
                                        scheduler_output.hidden_channel
                                    ),
                                    chunk_index=max(0, req.chunk_num - 1),
                                    is_last_chunk=is_last,
                                    num_scheduled_tokens=num_scheduled,
                                )
                                self._prefill_flight_by_token[
                                    scheduler_output.head_token
                                ] = flight
                                self._pending_tail_count[req.request_id] = (
                                    self._pending_tail_count.get(
                                        req.request_id, 0
                                    )
                                    + 1
                                )

                                if self._should_ahead_schedule(req, is_last):
                                    # Ahead: re-add to chunk_prefill_first
                                    # so the next chunk PF can be dispatched
                                    # before this chunk's PL returns. Used for
                                    # the single-request pipeline (both 2P1D
                                    # slots serve the same request).
                                    self.chunk_prefill_first.append(req)
                                    self._ahead_chunk_count[
                                        req.request_id
                                    ] = (
                                        self._ahead_chunk_count.get(
                                            req.request_id, 0
                                        )
                                        + 1
                                    )
                                    logger.info(
                                        "[PD-CHUNK-PRIOR] Ahead-scheduled "
                                        "chunk %d of request %s "
                                        "(head_token=%s, %d tokens, "
                                        "ahead_count=%d)",
                                        flight.chunk_index,
                                        req.request_id,
                                        scheduler_output.head_token,
                                        num_scheduled,
                                        self._ahead_chunk_count[
                                            req.request_id
                                        ],
                                    )
                                else:
                                    # Wait for PL before next chunk. Reasons:
                                    #   - last chunk (is_last);
                                    #   - ahead budget exhausted;
                                    #   - yield: next_prefill_prior_enable is
                                    #     on and another request can fill the
                                    #     slot (cross-request head-prior).
                                    if (
                                        self.next_prefill_prior_enable
                                        and not is_last
                                        and self._can_ahead_schedule(
                                            req.request_id
                                        )
                                        and self._has_other_prefill_request(
                                            req.request_id
                                        )
                                    ):
                                        wait_reason = "yield"
                                    elif is_last:
                                        wait_reason = "last"
                                    else:
                                        wait_reason = "ahead_full"
                                    self.prefill_last_pending.append(req)
                                    logger.info(
                                        "[PD-CHUNK-PRIOR] Chunk %d of "
                                        "request %s waiting for PL "
                                        "(head_token=%s, %d tokens, "
                                        "is_last=%s, "
                                        "pending_tails=%d, reason=%s)",
                                        flight.chunk_index,
                                        req.request_id,
                                        scheduler_output.head_token,
                                        num_scheduled,
                                        is_last,
                                        self._pending_tail_count.get(
                                            req.request_id, 0
                                        ),
                                        wait_reason,
                                    )
                            elif req.is_prefill_chunk:
                                # Not scheduled this round (token budget
                                # exhausted), keep for next round.
                                self.chunk_prefill_first.append(req)
                            else:
                                # Completed but not scheduled – defensive.
                                self.prefill_last_pending.append(req)
                    else:
                        # === Legacy routing (no chunk-prefill-prior) ===
                        for req in self.running:
                            if req.request_id in scheduled_req_ids:
                                self.prefill_last_pending.append(req)
                            elif req.is_prefill_chunk:
                                # Not scheduled this round (e.g. token budget
                                # exhausted), keep in chunk_prefill_first.
                                self.chunk_prefill_first.append(req)
                            else:
                                # Completed but not scheduled – defensive.
                                self.prefill_last_pending.append(req)

                # Restore prefill candidates not exposed to super() this round
                # so each is scheduled in its own PF batch (one-per-batch).
                self.chunk_prefill_first = (
                    rest_candidates + self.chunk_prefill_first
                )
                self.running = saved_running

                # [方案B] Edge 侧建议 Cloud 是否切层。
                # 必须在 self.running 恢复为 saved_running 之后检查，
                # 否则 self.running 被临时替换为 prefill 请求，永远为 False。
                if scheduler_output.total_num_scheduled_tokens > 0:
                    suggest = len(self.running) > 0
                    scheduler_output.cloud_suggest_slicing = suggest
                    if not suggest:
                        logger.info(
                            "[PD-EDGE-NO-SLICE] PREFILL_FIRST "
                            "cloud_suggest_slicing=False, running=%d, "
                            "chunk_prefill_first=%d, total_tokens=%d",
                            len(self.running),
                            len(self.chunk_prefill_first),
                            scheduler_output.total_num_scheduled_tokens,
                        )

            else:
                self.chunk_prefill_first = saved_chunk_prefill_first
                self.running = saved_running

            # 恢复 waiting 中其余请求（仅在 limit_prefill_batch_size 时）
            if self.limit_prefill_batch_size and saved_waiting_rest:
                for req in saved_waiting_rest:
                    self.waiting.append(req)

        if (
            self.limit_prefill_batch_size
            and scheduler_output is not None
            and scheduler_output.total_num_scheduled_tokens > 0
        ):
            logger.info(
                "[PD-LIMIT-PREFILL] PREFILL_FIRST batch_size=%d, "
                "total_tokens=%d, chunk_first_remaining=%d, waiting_remaining=%d",
                len(scheduler_output.num_scheduled_tokens),
                scheduler_output.total_num_scheduled_tokens,
                len(self.chunk_prefill_first),
                len(self.waiting),
            )

        return scheduler_output  # type: ignore[return-value]

    def _pick_prefill_last_batch(self) -> SchedulerOutput:
        """Pop one cloud-returned SchedulerOutput from prefills_last_ready.

        The cloud has already rewritten ``batch_type=PREFILL_LAST`` and kept
        all original KV / sampling metadata intact, so the edge worker can
        directly run segment_e + sampler on it. We also remove the involved
        requests from ``chunk_prefill_first`` so the parent class's
        ``update_from_output`` does not double-account them.
        """
        if not self.prefills_last_ready:
            return self._make_empty_batch()
        so = self.prefills_last_ready.popleft()
        assert so.batch_type == BatchType.PREFILL_LAST, (
            f"prefills_last_ready expects PREFILL_LAST, got {so.batch_type}"
        )
        # Mark whether this PL is the request's last prefill chunk.  Mid-chunk
        # PL still has to run the drafter so that the MTP layer populates its
        # KV cache for every prompt chunk; its sampled/draft tokens are only
        # discarded after the draft forward.  The flight is still in the map
        # here and is popped later in
        # _update_from_output_prefill_last_chunk_prior.
        flight = (
            self._prefill_flight_by_token.get(so.head_token)
            if so.head_token else None
        )
        batch_req_ids = tuple(so.num_scheduled_tokens)
        if flight is not None:
            draft_output_req_ids = (
                batch_req_ids if flight.is_last_chunk else ()
            )
        else:
            # Legacy mode may batch several prefill requests.  Preserve the
            # per-request distinction: every row warms draft KV, while only
            # requests whose prompt is complete may publish proposals.
            draft_output_req_ids = tuple(
                req_id
                for req_id in batch_req_ids
                if (request := self.requests.get(req_id)) is not None
                and not request.is_prefill_chunk
            )
        so.draft_output_req_ids = draft_output_req_ids
        so.is_last_prefill_chunk = bool(draft_output_req_ids)
        # Drop these reqs from chunk_prefill_first. Keep them in
        # prefill_last_pending until update_from_output() moves them to running.
        last_req_ids = set(so.num_scheduled_tokens.keys())
        if last_req_ids:
            self.chunk_prefill_first = [
                req for req in self.chunk_prefill_first
                if req.request_id not in last_req_ids
            ]
        self._validate_prefill_tail_channel(so)
        # Every chunk needs a draft-prefill pass.  Only the last chunk's draft
        # tokens are published to the following target verify batch; the
        # worker uses draft_output_req_ids to discard mid-chunk outputs.
        self._pregenerate_draft_chain(so)
        # 第 3 点强制等待（[FORCE] 设计 §6.3.2）：PL 后下一拍必须紧跟
        # PREFILL_DRAFT_FIRST（链由 _pregenerate_draft_chain 生成）。状态机
        # 按构造时的 MTP 使能决定是否启动 prefill 窗口——非 MTP 无链可等，
        # 启动只会白白锁 15ms（等价现状运行时门控，配置构造后不变）。
        self._force.on_pick(BatchType.PREFILL_LAST)
        return so

    def _validate_prefill_tail_channel(self, scheduler_output: SchedulerOutput) -> None:
        token = scheduler_output.head_token
        channel = scheduler_output.hidden_channel
        if not token:
            raise RuntimeError("PREFILL_LAST missing head_token")
        pool = self.hidden_channel_manager.prefill_pool
        if channel not in pool:
            raise RuntimeError(
                f"PREFILL_LAST expects a prefill hidden channel from "
                f"{pool}, got {channel}"
            )
        expected = self.hidden_channel_manager.get_channel(token)
        if expected != channel:
            raise RuntimeError(
                f"PREFILL_LAST hidden channel mismatch: expected {expected}, "
                f"got {channel}, head_token={token}"
            )

    def _validate_decode_tail_channel(self, scheduler_output: SchedulerOutput) -> None:
        pool = self.hidden_channel_manager.decode_pool
        if scheduler_output.hidden_channel not in pool:
            raise RuntimeError(
                f"DECODE_LAST expects a decode hidden channel from "
                f"{pool}, got {scheduler_output.hidden_channel}"
            )

    def _validate_prefill_draft_tail_channel(
        self, scheduler_output: SchedulerOutput
    ) -> None:
        """PREFILL_DRAFT_LAST must carry its parent chunk's prefill channel.

        Phase B（设计 §4.3）：prefill_draft 链继承父 chunk 的 Prefill 通道，
        draft_task_id == 父 chunk head_token，通道必须仍挂在 manager 上
        （§5.2 推迟释放到草稿链完成，PL 完成不再立即释放）。
        """
        if not scheduler_output.head_token:
            raise RuntimeError("PREFILL_DRAFT_LAST missing head_token")
        if not scheduler_output.draft_task_id:
            raise RuntimeError("PREFILL_DRAFT_LAST missing draft_task_id")
        if scheduler_output.draft_step_idx is None:
            raise RuntimeError("PREFILL_DRAFT_LAST missing draft_step_idx")
        channel = scheduler_output.hidden_channel
        pool = self.hidden_channel_manager.prefill_pool
        if channel not in pool:
            raise RuntimeError(
                f"PREFILL_DRAFT_LAST expects a prefill hidden channel "
                f"from {pool}, got {channel}"
            )
        expected = self.hidden_channel_manager.get_channel(
            scheduler_output.draft_task_id
        )
        if expected != channel:
            raise RuntimeError(
                "PREFILL_DRAFT_LAST hidden channel mismatch: expected "
                f"{expected}, got {channel}, "
                f"draft_task_id={scheduler_output.draft_task_id}"
            )

    def _validate_decode_draft_tail_channel(
        self, scheduler_output: SchedulerOutput
    ) -> None:
        if not scheduler_output.head_token:
            raise RuntimeError("DECODE_DRAFT_LAST missing head_token")
        if not scheduler_output.draft_task_id:
            raise RuntimeError("DECODE_DRAFT_LAST missing draft_task_id")
        if scheduler_output.draft_step_idx is None:
            raise RuntimeError("DECODE_DRAFT_LAST missing draft_step_idx")
        if scheduler_output.hidden_channel != (
            self.hidden_channel_manager.draft_channel()
        ):
            raise RuntimeError(
                "DECODE_DRAFT_LAST expects the dedicated draft hidden "
                f"channel {self.hidden_channel_manager.draft_channel()}, "
                f"got {scheduler_output.hidden_channel}"
            )

    def _pick_prefill_draft_first_batch(self) -> SchedulerOutput:
        """Pick one PREFILL_DRAFT_FIRST from the prefill-draft domain.

        Phase A：prefill_draft 链仍走 DECODE 通道（旧行为），仅队列/计数/
        标记按域拆分；通道迁移到 Prefill 双通道属 Phase B。
        """
        return self._pick_draft_first_batch_by_kind("prefill")

    def _pick_decode_draft_first_batch(self) -> SchedulerOutput:
        """Pick one DECODE_DRAFT_FIRST from the decode-draft domain."""
        return self._pick_draft_first_batch_by_kind("decode")

    def _pick_draft_first_batch_by_kind(self, kind: str) -> SchedulerOutput:
        if kind == "prefill":
            ready_queue = self.prefill_drafts_first_ready
            first_type = BatchType.PREFILL_DRAFT_FIRST
            last_type = BatchType.PREFILL_DRAFT_LAST
        else:
            ready_queue = self.decode_drafts_first_ready
            first_type = BatchType.DECODE_DRAFT_FIRST
            last_type = BatchType.DECODE_DRAFT_LAST
        while ready_queue:
            scheduler_output = ready_queue.popleft()
            if self._is_stale_draft_output(scheduler_output):
                if scheduler_output.draft_task_id:
                    self._pregenerated_draft_task_ids.discard(
                        scheduler_output.draft_task_id
                    )
                    self._pregenerated_draft_req_ids.pop(
                        scheduler_output.draft_task_id, None
                    )
                    # Report the cut chain so EngineCore can release the
                    # retained KV blocks and invalidate the cloud-side
                    # cached draft metadata (which will never be fully
                    # consumed now).
                    self._dropped_draft_task_ids_to_report.append(
                        scheduler_output.draft_task_id
                    )
                    if kind == "prefill":
                        # Phase B（设计 §5.2）：PDFF 在队未派发 ⇒ 其配对
                        # PDFL 尚未 self-post（PDFL 只在 PDFF pick 时生成），
                        # 入队时的 +1 无完成事件配对，须在此补 -1。pregenerated
                        # 与 fallback 链同理（pregenerated 链只预入队 PDFF）。
                        self._note_prefill_draft_chain_cut(
                            scheduler_output.draft_task_id,
                            step_dropped=True,
                        )
                if scheduler_output is self._draft_first_cloud_publish_pending:
                    self._draft_first_cloud_publish_pending = None
                    self._draft_first_scalars_patched = False
                    self._draft_first_dispatched = False
                logger.info(
                    "[PD] drop stale %s task_id=%s step=%s",
                    first_type.value,
                    scheduler_output.draft_task_id,
                    scheduler_output.draft_step_idx,
                )
                continue
            break
        else:
            return self._make_empty_batch()

        if scheduler_output is self._draft_first_cloud_publish_pending:
            self._draft_first_dispatched = True
            if self._draft_first_scalars_patched:
                self._draft_first_cloud_publish_pending = None
                self._draft_first_scalars_patched = False

        scheduler_output.batch_type = first_type
        if scheduler_output.head_token is None:
            scheduler_output.head_token = uuid4().hex
        if kind == "decode":
            # decode_draft 域走独立 DRAFT 通道（不再与 DECODE 共享，这是
            # 放宽 draft 串行门控的前提：共享通道时边云可能互相等对方
            # 方向的 send 才 post 匹配 recv，会死锁）。
            scheduler_output.hidden_channel = (
                self.hidden_channel_manager.draft_channel()
            )
        elif scheduler_output.hidden_channel is None:
            # Phase B（设计 §4.1）：prefill 域链在 enqueue 时已继承父 chunk
            # 的 Prefill 通道；缺失说明链创建路径漏了继承。
            raise RuntimeError(
                f"{first_type.value} missing inherited prefill "
                f"hidden_channel (task_id={scheduler_output.draft_task_id})"
            )
        self._register_pd_flight(scheduler_output)
        if kind == "prefill":
            # Phase C（设计 §6.2/§7.5）：PDFL 由云侧在 PDFF 完成后经
            # POST_OUT 发布——云侧往返即 pacing，边侧不再自贴尾、不再
            # 延迟计时。派发仍 +1 remote pending，云侧发布的 PDFL 完成
            # 时 -1（flight 键 draft_task_id:draft_step_idx 配对）。
            # 通道校验在 PDFL 到达 `_pick_draft_last_batch_by_kind` 时进行。
            self.prefill_draft_remote_pending_count += 1
            # [FORCE] PDFF pick → prefill_draft_last_pending（交替门控）
            self._force.on_pick(BatchType.PREFILL_DRAFT_FIRST)
            # Phase C review: 登记 watchdog 截止时间——云发 PDFL 超过
            # 阈值未到即判定链路故障（丢包/云侧故障），报错退出。
            self._prefill_draft_last_watchdog[
                scheduler_output.draft_task_id
            ] = (
                time.monotonic()
                + self._prefill_draft_last_watchdog_seconds
            )
        else:
            # Decode 域保留边侧自贴尾（设计 §6.2）：DDL 在 DDF 头完成后
            # 即可本地生成，无云侧往返。Worker FIFO 顺序 + 每通道
            # send-work 等待保证 head → tail 数据面顺序。
            draft_last = replace(
                scheduler_output,
                batch_type=last_type,
                num_accepted_tokens=None,
                valid_sampled_token_count=None,
            )
            # is_last_prefill_chunk / draft_output_req_ids 是下游动态
            # SchedulerOutput 属性，dataclasses.replace() 不保留，须回填。
            draft_last.is_last_prefill_chunk = getattr(
                scheduler_output, "is_last_prefill_chunk", True
            )
            draft_last.draft_output_req_ids = getattr(
                scheduler_output,
                "draft_output_req_ids",
                tuple(scheduler_output.num_scheduled_tokens),
            )
            self._validate_decode_draft_tail_channel(draft_last)
            self.decode_drafts_last_ready.append(draft_last)
            self.decode_draft_remote_pending_count += 1
            # [FORCE] DDF pick → decode_draft_last_pending（交替门控）
            self._force.on_pick(BatchType.DECODE_DRAFT_FIRST)
            self._start_decode_draft_last_delay()
            self.decode_or_draft_inflight_count += 1

        logger.info(
            "[MTP-DEBUG] scheduler picked %s: task_id=%s, "
            "parent_req_id=%s, draft_step_idx=%s, head_token=%s, "
            "remaining_ready=%d, decode_or_draft_inflight=%d, "
            "%s_pending=%d",
            first_type.value,
            scheduler_output.draft_task_id,
            scheduler_output.parent_req_id,
            scheduler_output.draft_step_idx,
            scheduler_output.head_token,
            len(ready_queue),
            self.decode_or_draft_inflight_count,
            kind,
            (self.prefill_draft_remote_pending_count
             if kind == "prefill" else self.decode_draft_remote_pending_count),
        )
        return scheduler_output

    def _uses_async_scheduled_mtp_placeholders(self) -> bool:
        """Whether scheduled MTP can use native async placeholder semantics."""
        if not getattr(self.scheduler_config, "async_scheduling", False):
            return False
        speculative_config = self.vllm_config.speculative_config
        if speculative_config is None or self.num_spec_tokens <= 0:
            return False
        method = getattr(speculative_config, "method", None)
        if method in ("qwen3_5_mtp", "qwen_mtp"):
            return True
        if method != "mtp":
            return False
        hf_config = getattr(self.vllm_config.model_config, "hf_config", None)
        return "qwen" in str(
            getattr(hf_config, "model_type", "")
        ).lower()

    @staticmethod
    def _draft_kind_of(batch_type: BatchType) -> str:
        """Classify a parent batch into its draft domain (设计 §3.3).

        PREFILL_LAST 与其自身派生的 PREFILL_DRAFT_LAST 产生 prefill_draft
        链；DECODE_LAST / DECODE_DRAFT_LAST 产生 decode_draft 链
        （DECODE 通道域）。
        """
        if batch_type in (
            BatchType.PREFILL_LAST,
            BatchType.PREFILL_DRAFT_LAST,
        ):
            return "prefill"
        return "decode"

    def _pregenerate_draft_chain(
        self, target_tail: SchedulerOutput
    ) -> None:
        """Create fixed-length placeholder draft tasks at target-tail pick
        time, classified into the parent tail's domain (设计 §3.3).

        The real token IDs remain in the edge worker.  FIFO ordering ensures
        every draft head executes after the tail that produces its local
        inputs.  Only the step-0 accepted-token scalars are finalized later
        for the cloud; they are not consumed by the edge worker.

        Phase B（设计 §4.1）：prefill_draft 链继承父 chunk 的 Prefill 通道；
        decode_draft 链仍为 DECODE。
        """
        if not self._uses_async_scheduled_mtp_placeholders():
            return
        if (
            self.prefill_drafts_first_ready
            or self.prefill_drafts_last_ready
            or self.decode_drafts_first_ready
            or self.decode_drafts_last_ready
            or self._draft_first_cloud_publish_pending is not None
        ):
            return
        kind = self._draft_kind_of(target_tail.batch_type)
        if kind == "prefill":
            first_type = BatchType.PREFILL_DRAFT_FIRST
            ready_queue = self.prefill_drafts_first_ready
            # Phase B（设计 §4.1/要点 3）：prefill_draft 链继承父 chunk 的
            # Prefill 通道，PF(head) → PL(head) → prefill_draft*(head) 全程
            # 同通道。通道释放已推迟到草稿链完成（§5.2），故此处通道
            # 必在 manager 中。
            inherited_channel = target_tail.hidden_channel
        else:
            first_type = BatchType.DECODE_DRAFT_FIRST
            ready_queue = self.decode_drafts_first_ready
            # decode_draft 占位链继承 DRAFT 通道（与 _pick_draft_first_
            # batch_by_kind 的 decode 分支一致）。
            inherited_channel = (
                self.hidden_channel_manager.draft_channel()
            )
        req_ids = list(target_tail.num_scheduled_tokens)
        if not req_ids or any(
            req_id not in self.requests for req_id in req_ids
        ):
            return
        task_id = target_tail.head_token
        if not task_id:
            return

        for step_idx in range(self.num_spec_tokens):
            draft_first = replace(
                target_tail,
                batch_type=first_type,
                head_token=None,
                hidden_channel=inherited_channel,
                parent_req_id=req_ids[0],
                draft_task_id=task_id,
                draft_step_idx=step_idx,
                num_accepted_tokens=None,
                valid_sampled_token_count=None,
            )
            # Preserve the parent prefill phase across the independently
            # scheduled draft chain.  Mid-chunk chains warm the draft KV but
            # must not seed a target decode placeholder.
            draft_first.is_last_prefill_chunk = getattr(
                target_tail, "is_last_prefill_chunk", True
            )
            draft_first.draft_output_req_ids = getattr(
                target_tail,
                "draft_output_req_ids",
                tuple(target_tail.num_scheduled_tokens),
            )
            ready_queue.append(draft_first)
            if step_idx == 0:
                self._draft_first_cloud_publish_pending = draft_first
                self._draft_first_scalars_patched = False
                self._draft_first_dispatched = False

        self._pregenerated_draft_task_ids.add(task_id)
        self._pregenerated_draft_req_ids[task_id] = set(req_ids)
        if kind == "prefill":
            # Phase B（设计 §5.2）：链创建即入队，一步一记，保证 PL 完成
            # 时 pending 精确反映未完成步数（含在队未派发步），不会提前
            # finalize 释放通道。每步的 -1 由其 PDFL 完成（tail 队列
            # never-drop，必然完成）配对。
            self._prefill_slot_pending[task_id] = (
                self._prefill_slot_pending.get(task_id, 0)
                + self.num_spec_tokens
            )
            # 设计 §5.5：running 门控 per-req 计数，按 draft_output_req_ids
            # 成员 +num_spec（与 PDFL 完成时的递减同键配对；mid-chunk 链
            # draft_output_req_ids 为 ()，不计数）。注意：() 是合法值
            # （mid-chunk 链），不能用 `or` 回退——须用显式 None 判断，
            # 否则 mid-chunk 链会把 num_scheduled_tokens 误计进来，与其
            # PDFL 的 () 递减失配（泄漏或提前放行）。
            gate_req_ids = getattr(
                target_tail, "draft_output_req_ids", None
            )
            if gate_req_ids is None:
                gate_req_ids = tuple(target_tail.num_scheduled_tokens)
            for req_id in gate_req_ids:
                # 对抗 review A2：finished（retention 保留）成员跳过计费，
                # 否则其 +1 无配对递减（链被 stale-drop 时只修槽记账）。
                member = self.requests.get(req_id)
                if member is None or member.is_finished():
                    continue
                self._req_pending_prefill_draft_steps[req_id] = (
                    self._req_pending_prefill_draft_steps.get(req_id, 0)
                    + self.num_spec_tokens
                )
                # 对抗 review A1：登记链代，PDFL 递减按代校验。
                self._req_charged_draft_tasks.setdefault(
                    req_id, set()
                ).add(task_id)
        logger.info(
            "[PD] pre-generated async MTP placeholders task_id=%s steps=%d "
            "kind=%s",
            task_id,
            self.num_spec_tokens,
            kind,
        )

    def finalize_pre_generated_draft_first(
        self,
        *,
        draft_task_id: str,
        num_accepted_tokens: list[int] | None,
        valid_sampled_token_count: list[int] | None,
    ) -> SchedulerOutput | None:
        """Patch cloud-only sampling state into the queued step-0 control."""
        pending = self._draft_first_cloud_publish_pending
        if (
            pending is None
            or pending.draft_task_id != draft_task_id
        ):
            return None
        pending.num_accepted_tokens = num_accepted_tokens
        pending.valid_sampled_token_count = valid_sampled_token_count
        if not self._draft_first_dispatched:
            self._draft_first_scalars_patched = True
            return pending
        self._draft_first_cloud_publish_pending = None
        self._draft_first_scalars_patched = False
        return pending

    def is_pre_generated_draft(
        self, scheduler_output: SchedulerOutput
    ) -> bool:
        task_id = (
            scheduler_output.draft_task_id
            or scheduler_output.head_token
        )
        return bool(task_id and task_id in self._pregenerated_draft_task_ids)

    def active_pre_generated_draft_req_ids(self) -> set[str]:
        active: set[str] = set()
        for task_id in self._pregenerated_draft_task_ids:
            active.update(
                self._pregenerated_draft_req_ids.get(task_id, ())
            )
        return active

    def enqueue_draft_first(
        self,
        source: SchedulerOutput,
        *,
        draft_task_id: str,
        draft_step_idx: int,
        num_accepted_tokens: list[int] | None = None,
        valid_sampled_token_count: list[int] | None = None,
    ) -> bool:
        """Generate a draft head locally, mirroring decode head generation.

        The worker owns the mutable draft tensors, but the scheduler owns all
        draft control-plane SchedulerOutputs. The initial step receives only
        the rejection-corrected scalar state from the worker; follow-up steps
        are derived directly from the completed draft tail.

        The chain kind is inherited from ``source.batch_type``（设计 §3.3）：
        PL/PDFL 源产生 prefill_draft，DL/DDL 源产生 decode_draft。
        """
        kind = self._draft_kind_of(source.batch_type)
        if kind == "prefill":
            first_type = BatchType.PREFILL_DRAFT_FIRST
            ready_queue = self.prefill_drafts_first_ready
            # Phase B（设计 §4.1）：prefill_draft 链继承父批（PL/PDFL）的
            # Prefill 通道；fallback 链的 task_id == 父批 head_token，通道
            # 与其一致（§5.2 推迟释放保证此处仍可查）。
            inherited_channel = source.hidden_channel
        else:
            first_type = BatchType.DECODE_DRAFT_FIRST
            ready_queue = self.decode_drafts_first_ready
            # decode_draft 链固定 DRAFT 通道（独立数据面，见
            # HiddenChannelManager.draft_channel）。
            inherited_channel = (
                self.hidden_channel_manager.draft_channel()
            )
        req_ids = list(source.num_scheduled_tokens)
        # With KV retention, finished requests stay in self.requests until
        # their draft chain releases them, so this refusal only fires when
        # a request is genuinely gone (e.g. aborted before the parent
        # output was processed).  The chain then can never (fully) run:
        # report the task so EngineCore releases the retained KV blocks
        # and invalidates the cloud-side cached metadata.
        if not req_ids or any(
            req_id not in self.requests for req_id in req_ids
        ):
            if draft_task_id:
                self._dropped_draft_task_ids_to_report.append(draft_task_id)
                if kind == "prefill":
                    # Phase B（设计 §5.2）：fallback 链不会入队，父槽没有
                    # 未完成步且 PL 已完成时须立即 finalize（幂等）。
                    self._note_prefill_draft_chain_cut(draft_task_id)
            return False
        if kind == "prefill" and (
            draft_task_id not in self._prefill_slot_pending
        ):
            # Phase B（设计 §4.1/§5.2）：prefill 域 fallback 链的 task_id
            # == 父批 head_token，其槽必须仍被持有（PL 完成时判定
            # has_fallback 就不 finalize）。槽已释放却仍入队说明 PL 完成
            # 判定漏了 fallback 状态（调度器 bug），拒绝入队防止通道
            # 错配死锁，而非静默派发到已归还的通道上。
            logger.error(
                "[PD] refusing prefill fallback enqueue: task_id=%s slot "
                "already finalized",
                draft_task_id,
            )
            self._dropped_draft_task_ids_to_report.append(draft_task_id)
            return False

        draft_first = replace(
            source,
            batch_type=first_type,
            head_token=None,
            hidden_channel=inherited_channel,
            parent_req_id=req_ids[0],
            draft_task_id=draft_task_id,
            draft_step_idx=draft_step_idx,
            num_accepted_tokens=num_accepted_tokens,
            valid_sampled_token_count=valid_sampled_token_count,
        )
        draft_first.is_last_prefill_chunk = getattr(
            source, "is_last_prefill_chunk", True
        )
        draft_first.draft_output_req_ids = getattr(
            source,
            "draft_output_req_ids",
            tuple(source.num_scheduled_tokens),
        )
        ready_queue.append(draft_first)
        if kind == "prefill":
            # Phase B（设计 §5.2）：入队即记账（+1）。每个 fallback PDFF
            # 的 -1 由其 PDFL 完成配对；PDFF 在队未派发被 stale drop 时
            # 由 _note_prefill_draft_chain_cut 补 -1（其配对 PDFL 不会
            # 产生）。
            self._prefill_slot_pending[draft_task_id] = (
                self._prefill_slot_pending.get(draft_task_id, 0) + 1
            )
            # 设计 §5.5：running 门控 per-req 计数每步 +1（与 PDFL 完成
            # 时的递减同键配对；() 是 mid-chunk 链的合法值，显式 None
            # 判断，勿用 `or` 回退）。
            gate_req_ids = getattr(
                draft_first, "draft_output_req_ids", None
            )
            if gate_req_ids is None:
                gate_req_ids = tuple(draft_first.num_scheduled_tokens)
            for req_id in gate_req_ids:
                # 对抗 review A2：finished（retention 保留）成员跳过计费，
                # 否则其 +1 无配对递减（链被 stale-drop 时只修槽记账）。
                member = self.requests.get(req_id)
                if member is None or member.is_finished():
                    continue
                self._req_pending_prefill_draft_steps[req_id] = (
                    self._req_pending_prefill_draft_steps.get(req_id, 0) + 1
                )
                # 对抗 review A1：登记链代，PDFL 递减按代校验。
                self._req_charged_draft_tasks.setdefault(
                    req_id, set()
                ).add(draft_task_id)
        return True

    def _enqueue_next_draft_first(
        self, draft_last: SchedulerOutput
    ) -> bool:
        draft_step_idx = int(draft_last.draft_step_idx or 0)
        next_step_idx = draft_step_idx + 1
        task_id = draft_last.draft_task_id
        if task_id in self._pregenerated_draft_task_ids:
            if next_step_idx >= self.num_spec_tokens:
                self._pregenerated_draft_task_ids.discard(task_id)
                self._pregenerated_draft_req_ids.pop(task_id, None)
            return False
        if next_step_idx >= self.num_spec_tokens:
            return False
        if task_id is None:
            raise RuntimeError("draft LAST missing draft_task_id")
        return self.enqueue_draft_first(
            draft_last,
            draft_task_id=task_id,
            draft_step_idx=next_step_idx,
        )

    def _pick_prefill_draft_last_batch(self) -> SchedulerOutput:
        """Pick one PREFILL_DRAFT_LAST from the prefill-draft domain.

        Phase A：仍由边侧自贴（旧行为）+ 延迟计时；Phase C 起改由云侧
        POST_OUT 发布（不延迟）。
        """
        return self._pick_draft_last_batch_by_kind("prefill")

    def _pick_decode_draft_last_batch(self) -> SchedulerOutput:
        """Pick one DECODE_DRAFT_LAST from the decode-draft domain.

        边侧自生成 + 5ms 默认延迟调度（设计 §6.2）。
        """
        return self._pick_draft_last_batch_by_kind("decode")

    def _pick_draft_last_batch_by_kind(self, kind: str) -> SchedulerOutput:
        if kind == "prefill":
            ready_queue = self.prefill_drafts_last_ready
            last_type = BatchType.PREFILL_DRAFT_LAST
        else:
            ready_queue = self.decode_drafts_last_ready
            last_type = BatchType.DECODE_DRAFT_LAST
        while ready_queue:
            scheduler_output = ready_queue.popleft()
            if scheduler_output.batch_type != last_type:
                raise RuntimeError(
                    f"{kind}_drafts_last_ready expects {last_type}, got "
                    f"{scheduler_output.batch_type}"
                )
            if kind == "prefill":
                self._validate_prefill_draft_tail_channel(scheduler_output)
            else:
                self._validate_decode_draft_tail_channel(scheduler_output)
            # A draft tail here always has its matching head already
            # dispatched to the cloud (decode domain: self-posted when the
            # head was picked; prefill domain, Phase C: published by the
            # cloud after its worker finished the PDFF).  The cloud does
            # not track request lifecycle, so it will isend a response even
            # if the owning request has since finished/aborted.  The edge
            # MUST still execute this tail (recv) to keep the hidden channel
            # paired -- never drop it.  When the request is gone the worker
            # drains the recv and skips the tail-segment compute (see
            # _run_edge_cloud_draft_last_segment); we also must not spawn a
            # verify placeholder for a dead request.
            if kind == "prefill":
                # 尾已到手（云发或 watchdog 自贴），清 watchdog 条目。
                self._prefill_draft_last_watchdog.pop(
                    scheduler_output.draft_task_id, None
                )
                # 第 4 点强制等待（[FORCE] 设计 §6.3.2）：非最后一个 PDFL
                # （同 task 仍有未派发的剩余 step PDFF 在队）才启动 15ms
                # prefill-first-only 窗口强制跟随；最后一跳后无首可等，
                # 状态机按 prefill_chain_has_more 判定（末跳全清）。
                self._force.on_pick(
                    BatchType.PREFILL_DRAFT_LAST,
                    prefill_chain_has_more=any(
                        t.draft_task_id == scheduler_output.draft_task_id
                        for t in self.prefill_drafts_first_ready
                    ),
                )
            else:
                # [FORCE] DDL pick → 30ms decode first-only 窗口 + 解除
                # decode_draft_last_pending 交替（设计 §6.3.2）。
                # [EHER-draft] Consume the readiness ack for this flight
                # (bounds _draft_recv_ready_acks growth; a re-posted DDF
                # under the same head_token starts with a clean marker).
                self._draft_recv_ready_acks.discard(
                    scheduler_output.head_token
                )
                self._force.on_pick(BatchType.DECODE_DRAFT_LAST)
            output_req_ids = getattr(
                scheduler_output,
                "draft_output_req_ids",
                tuple(scheduler_output.num_scheduled_tokens),
            )
            has_live_output_req = any(
                (request := self.requests.get(req_id)) is not None
                and not request.is_finished()
                for req_id in output_req_ids
            )
            if has_live_output_req:
                self._prepare_next_decode_first_placeholder(scheduler_output)
            elif not output_req_ids:
                logger.info(
                    "[PD] finish %s task_id=%s step=%s "
                    "(mid-prefill KV warmup; no verify placeholder)",
                    last_type.value,
                    scheduler_output.draft_task_id,
                    scheduler_output.draft_step_idx,
                )
            else:
                logger.info(
                    "[PD] drain %s task_id=%s step=%s "
                    "(request gone; worker will drain cloud response)",
                    last_type.value,
                    scheduler_output.draft_task_id,
                    scheduler_output.draft_step_idx,
                )
            return scheduler_output
        return self._make_empty_batch()

    def _prepare_next_decode_first_placeholder(
        self, draft_last: SchedulerOutput
    ) -> None:
        """Prepare the next target verify batch behind the final draft tail.

        Scheduler-side spec token values are placeholders.  The edge worker
        replaces them with its local ``_draft_token_ids`` after this DRL has
        executed, so no DraftTokenIds round-trip through EngineCore is needed.
        """
        if not self._uses_async_scheduled_mtp_placeholders():
            return
        if draft_last.draft_task_id not in self._pregenerated_draft_task_ids:
            self._decode_first_placeholder_parent = None
            return
        step_idx = int(draft_last.draft_step_idx or 0)
        if step_idx + 1 < self.num_spec_tokens:
            return
        self._decode_first_placeholder_parent = draft_last
        if self.decodes_first_ready:
            self._decode_first_placeholder_parent = None
            return
        if not self.running:
            # A chain pre-generated from the final PREFILL_LAST can reach its
            # final DRL before EngineCore has applied the prefill result. Retry
            # on the next schedule turn after that request moves to running.
            return
        if (
            self.prefill_drafts_first_ready
            or self.prefill_drafts_last_ready
            or self.decode_drafts_first_ready
            or self.decode_drafts_last_ready
            or (self.prefill_draft_remote_pending_count
                + self.decode_draft_remote_pending_count) > 1
        ):
            # Another draft chain still has steps queued or a head in flight
            # behind this tail (chains interleave when a newly admitted
            # request's prefill-warmup chain overlaps the decode chain).
            # Pre-building the placeholder now would dispatch the verify
            # before that chain has produced its drafts -- the verify's spec
            # rows would be filled from stale/crossed worker-side entries,
            # permanently poisoning the affected requests' draft KV
            # (observed: zero-valid verify rounds, then [0,0,0] drafts).
            # Deferring is also required for liveness: creation claims
            # decode_or_draft_inflight/decode_head_inflight, which the queued
            # draft picks wait on, so creating now would deadlock.  Keep the
            # parent set so a later turn retries once the queues drain; if
            # the other chain was not pre-generated, its own final tail
            # clears the parent above and the normal
            # _can_schedule_decode_first() path schedules the verify instead.
            return

        next_decode = self._pick_decode_first_batch()
        if (
            next_decode is not None
            and next_decode.batch_type == BatchType.DECODE_FIRST
            and next_decode.total_num_scheduled_tokens > 0
        ):
            self.decodes_first_ready.append(next_decode)
            self._decode_first_placeholder_parent = None

    @staticmethod
    def _scheduler_output_intersects_req_ids(
        scheduler_output: SchedulerOutput, req_ids: set[str]
    ) -> bool:
        if scheduler_output.parent_req_id in req_ids:
            return True
        return any(
            req_id in req_ids
            for req_id in scheduler_output.num_scheduled_tokens
        )

    # ------------------------------------------------------------------ #
    # Edge-cloud deferred-draft KV retention                              #
    # ------------------------------------------------------------------ #
    def _check_scheduled_edge_cloud_draft(self) -> bool:
        """Mirror of the runner/engine-core scheduled edge-cloud draft
        predicate.  Gates the retention logic so schedulers without the
        edge-cloud draft methods behave exactly as upstream.
        """
        speculative_config = self.vllm_config.speculative_config
        if speculative_config is None:
            return False
        if not getattr(
            self.vllm_config.parallel_config, "enable_edge_cloud", False
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

    def register_edge_cloud_draft_task(
        self, task_id: str, req_ids: set[str]
    ) -> None:
        """Register a deferred draft before its parent output is applied."""
        if (
            not self._edge_cloud_draft_retention_enabled
            or not task_id
            or not req_ids
        ):
            return
        previous_req_ids = self._edge_cloud_draft_task_reqs.get(task_id)
        if previous_req_ids is not None:
            if previous_req_ids != req_ids:
                raise RuntimeError(
                    "Deferred draft task registration changed request set: "
                    f"task_id={task_id}, previous={previous_req_ids}, "
                    f"new={req_ids}"
                )
            return
        self._edge_cloud_draft_task_reqs[task_id] = set(req_ids)
        for req_id in req_ids:
            self._edge_cloud_draft_req_tasks.setdefault(req_id, set()).add(
                task_id
            )

    def _free_request(
        self, request: Request, delay_free_blocks: bool = False
    ) -> dict[str, Any] | None:
        task_ids = (
            self._edge_cloud_draft_req_tasks.get(request.request_id)
            if self._edge_cloud_draft_retention_enabled
            else None
        )
        if not task_ids:
            return super()._free_request(request, delay_free_blocks)
        # The request is referenced by a pending/in-flight deferred draft.
        # Finish it normally (outputs, finished_req_ids) but keep its KV
        # blocks until the draft chain completes on the cloud — same
        # ordering guarantee the non-edge-cloud path gets for free by
        # proposing drafts inside execute_model.
        for task_id in task_ids:
            self._draft_retained_requests.setdefault(task_id, {})[
                request.request_id
            ] = request
        return super()._free_request(request, delay_free_blocks=True)

    def release_draft_retained_blocks(self, task_id: str) -> None:
        """Free KV blocks retained for a completed/dropped draft task.

        Idempotent.  A request referenced by several in-flight draft
        tasks is only freed once its last referencing task releases.
        """
        task_req_ids = self._edge_cloud_draft_task_reqs.pop(task_id, set())
        retained = self._draft_retained_requests.pop(task_id, {})
        for req_id in task_req_ids:
            req_tasks = self._edge_cloud_draft_req_tasks.get(req_id)
            if req_tasks is not None:
                req_tasks.discard(task_id)
                if req_tasks:
                    # Still referenced by another in-flight draft task.
                    continue
                self._edge_cloud_draft_req_tasks.pop(req_id, None)
            # The request is no longer referenced by any in-flight chain.
            # If its finish was withheld from the cloud (see
            # filter_cloud_finished_req_ids), queue it for re-emission on
            # the next cloud-bound batch so the cloud runner finally
            # removes the row.
            if req_id in self._cloud_withheld_finished_req_ids:
                self._cloud_withheld_finished_req_ids.discard(req_id)
                self._cloud_released_finished_req_ids.add(req_id)
            request = retained.get(req_id)
            if request is None:
                continue
            current = self.requests.get(req_id)
            if current is request and request.is_finished():
                self._free_blocks(request)
            elif current is not None and current is not request:
                # req_id resubmitted after finishing: free the old
                # request's blocks without evicting the new entry.
                self.kv_cache_manager.free(request)

    def _scheduler_output_all_requests_finished(
        self, scheduler_output: SchedulerOutput
    ) -> bool:
        batch_req_ids = self._edge_cloud_draft_task_reqs.get(
            scheduler_output.draft_task_id or ""
        )
        if batch_req_ids is None:
            batch_req_ids = set(scheduler_output.num_scheduled_tokens)
        else:
            batch_req_ids = set(batch_req_ids)
        if scheduler_output.parent_req_id is not None:
            batch_req_ids.add(scheduler_output.parent_req_id)
        return bool(batch_req_ids) and all(
            (request := self.requests.get(req_id)) is None
            or request.is_finished()
            for req_id in batch_req_ids
        )

    def _drop_stale_drafts_for_req_ids(self, req_ids: set[str]) -> None:
        if not req_ids:
            return
        # Aligned with the model runner's deferred-draft policy: a draft
        # batch is dropped only when EVERY request it covers has finished.
        # Partial finishes keep the draft — the cloud-side cached
        # attention metadata is whole-batch and cannot be re-sliced.
        # Dropped task ids are reported to the runner (which may still
        # hold the enqueued context) via take_dropped_draft_task_ids().
        # 4 域拆分（设计 §3.2）：两域 first 队列分别执行 stale-drop。
        for first_queue_name in (
            "prefill_drafts_first_ready",
            "decode_drafts_first_ready",
        ):
            first_queue = getattr(self, first_queue_name)
            kept_first: deque[SchedulerOutput] = deque()
            for output in first_queue:
                if (
                    self._scheduler_output_intersects_req_ids(
                        output, req_ids
                    )
                    and self._scheduler_output_all_requests_finished(
                        output
                    )
                ):
                    task_id = output.draft_task_id
                    if task_id is not None:
                        self._pregenerated_draft_task_ids.discard(task_id)
                        self._pregenerated_draft_req_ids.pop(task_id, None)
                        self._dropped_draft_task_ids_to_report.append(
                            task_id
                        )
                        if first_queue_name == "prefill_drafts_first_ready":
                            # Phase B（设计 §5.2）：PDFF 在队未派发被 drop，
                            # 其配对 PDFL 尚未 self-post，补 -1 记账（见
                            # _pick_draft_first_batch_by_kind 的 stale-drop
                            # 分支注释）。
                            self._note_prefill_draft_chain_cut(
                                task_id, step_dropped=True
                            )
                    if output is self._draft_first_cloud_publish_pending:
                        self._draft_first_cloud_publish_pending = None
                        self._draft_first_scalars_patched = False
                        self._draft_first_dispatched = False
                else:
                    kept_first.append(output)
            setattr(self, first_queue_name, kept_first)

        self.decodes_first_ready = deque(
            output
            for output in self.decodes_first_ready
            if not self._scheduler_output_intersects_req_ids(
                output, req_ids
            )
        )
        pending_decode = self._decode_first_placeholder_parent
        if (
            pending_decode is not None
            and self._scheduler_output_intersects_req_ids(
                pending_decode, req_ids
            )
        ):
            self._decode_first_placeholder_parent = None
        # Never drop a queued draft tail (either domain).  Decode tails are
        # self-posted at the moment their head is picked; prefill tails are
        # published by the cloud (Phase C) after its worker finished the
        # PDFF — in both cases a tail queued here means its draft FIRST was
        # already dispatched to the cloud.  The cloud does not track request
        # lifecycle, so it will still isend the response; the edge MUST
        # execute (drain) the tail to keep the hidden channel paired (see
        # _pick_draft_last_batch and the drain path in the worker's
        # _run_edge_cloud_draft_last_segment).  Dropping the tail also
        # strands the per-domain _force_*_draft_last=True -- the flag is
        # only cleared when the tail is picked -- which then blocks every
        # future draft/decode FIRST and deadlocks the scheduler.
        for last_queue_name in (
            "prefill_drafts_last_ready",
            "decode_drafts_last_ready",
        ):
            for output in getattr(self, last_queue_name):
                if self._scheduler_output_intersects_req_ids(
                    output, req_ids
                ):
                    gone = {
                        rid
                        for rid in output.num_scheduled_tokens
                        if rid in req_ids
                    }
                    if output.parent_req_id in req_ids:
                        gone.add(output.parent_req_id)
                    logger.info(
                        "[PD] keep %s task_id=%s step=%s for drain "
                        "(%d member request(s) gone; its head was "
                        "already dispatched to the cloud)",
                        output.batch_type.value,
                        output.draft_task_id,
                        output.draft_step_idx,
                        len(gone),
                    )
        # 设计 §5.5：finished 请求的 running 门控记账清账（自然完成与
        # abort 两条路径都在此汇合）。finished 请求不再需要门控，其
        # 未完结链的剩余步由上面的 drop/keep 处理。
        for req_id in req_ids:
            self._req_pending_prefill_draft_steps.pop(req_id, None)
            self._req_charged_draft_tasks.pop(req_id, None)
            self._running_gated_req_ids.discard(req_id)

    def take_dropped_draft_task_ids(self) -> list[str]:
        """Drain draft task ids dropped from the ready queues since the
        last call (EngineCore patch forwards them to the runner)."""
        dropped = self._dropped_draft_task_ids_to_report
        self._dropped_draft_task_ids_to_report = []
        return dropped

    def _is_stale_draft_output(
        self, scheduler_output: SchedulerOutput
    ) -> bool:
        # A draft output is stale when EVERY backing request has finished.
        # This drives the draft-head skip in _pick_*_draft_first_batch:
        # once all owning requests are gone, future (not-yet-dispatched)
        # draft heads must not be picked -- the edge can no longer produce
        # their payload (the draft context was cleared on finish/abort) and
        # the cloud would be left waiting for data that never arrives.
        # Partial finishes keep the draft alive: the cloud-side cached
        # attention metadata is whole-batch and cannot be re-sliced, so the
        # chain runs to completion and the dead rows' draft tokens are
        # discarded by the worker (_run_edge_cloud_draft_last_segment).
        # Already-dispatched heads are handled separately: their matching
        # draft tail is always executed (drained) in
        # _pick_*_draft_last_batch to pair the cloud's response, so this
        # check intentionally does NOT exempt pre-generated dispatched
        # chains the way it used to.
        # NOTE: finished requests may still be present in self.requests
        # while their KV blocks are retained for an in-flight draft chain,
        # so liveness must go through is_finished() (via
        # _scheduler_output_all_requests_finished), not dict membership.
        return self._scheduler_output_all_requests_finished(scheduler_output)

    def _draft_output_reqs_live(
        self, scheduler_output: SchedulerOutput
    ) -> bool:
        """True if any request backing this draft output is still active.

        Used both to decide whether a draft LAST may spawn a verify
        placeholder and (inverted) whether a draft FIRST is stale.
        """
        return not self._scheduler_output_all_requests_finished(
            scheduler_output
        )

    def _pick_decode_last_batch(self) -> SchedulerOutput:
        if not self.decodes_last_ready:
            return self._make_empty_batch()
        so = self.decodes_last_ready.popleft()
        assert so.batch_type == BatchType.DECODE_LAST, (
            f"decodes_last_ready expects DECODE_LAST, got {so.batch_type}"
        )
        self._validate_decode_tail_channel(so)
        # [FORCE] DL pick → 30ms decode first-only 窗口 + 解除
        # decode_last_pending 交替（设计 §6.3.2）。
        self._force.on_pick(BatchType.DECODE_LAST)
        self._pregenerate_draft_chain(so)
        return so

    def _ensure_cached_all_token_ids(
        self, scheduler_output: SchedulerOutput,
    ) -> None:
        """Ensure every cached decode req carries all_token_ids.

        In PD-separated mode the edge worker's persistent input_batch may not
        retain a request across the PF → PL → DF transitions (the tail segment
        may have been skipped by ``_update_states``), yet the async-scheduling
        model runner requires ``all_token_ids`` to reconstruct
        ``output_token_ids`` for any resumed (req_index is None) request with
        ``num_output_tokens > 0``.

        The base ``_make_cached_request_data`` only fills ``all_token_ids``
        when the request was *not* scheduled in the previous step
        (``prev_step_scheduled_req_ids``).  Because PD separation interleaves
        PF / PL / DF / DL phases — and PL/DL are popped from cloud-returned
        queues without going through ``super().schedule()`` — the scheduler's
        ``prev_step_scheduled_req_ids`` can be stale or misleading, causing
        ``all_token_ids`` to be omitted for requests that the worker actually
        needs it for.

        This helper unconditionally back-fills ``all_token_ids`` for any
        cached request that has output tokens but is missing from the dict.
        The extra payload is cheap (control-plane only) and avoids the
        ``KeyError`` in ``gpu_model_runner._update_states``.
        """
        cached_reqs = scheduler_output.scheduled_cached_reqs
        for req_id, num_output_tokens in zip(
            cached_reqs.req_ids,
            cached_reqs.num_output_tokens,
        ):
            if req_id not in cached_reqs.all_token_ids:
                # Use the Request-level cached np.ndarray to avoid repeated
                # np.asarray() conversion of the Python list (dominant
                # bottleneck on long-sequence decode batches).
                cached_reqs.all_token_ids[req_id] = (
                    self.requests[req_id].cached_all_token_ids_np)

    def _pick_decode_first_batch(self) -> SchedulerOutput:
        if not self.running:
            return self._make_empty_batch()

        saved_chunk_prefill_first = self.chunk_prefill_first
        saved_waiting = self.waiting
        saved_skipped = self.skipped_waiting

        self.chunk_prefill_first = []
        self.waiting = create_request_queue(self.policy)
        self.skipped_waiting = create_request_queue(self.policy)

        scheduler_output = None
        try:
            scheduler_output = super().schedule()
        finally:
            if scheduler_output is not None:
                if scheduler_output.total_num_scheduled_tokens == 0:
                    scheduler_output.batch_type = BatchType.EMPTY
                    logger.debug(
                        "DECODE_FIRST race: empty batch due to async "
                        "update_from_output delay, running=%d",
                        len(self.running),
                    )
                else:
                    scheduler_output.batch_type = BatchType.DECODE_FIRST
                    scheduler_output.head_token = uuid4().hex
                    scheduler_output.hidden_channel = (
                        self.hidden_channel_manager.decode_channel()
                    )
                    self._ensure_cached_all_token_ids(scheduler_output)
                    self.decode_or_draft_inflight_count += 1
                    self.decode_head_inflight_count += 1
                    self._register_pd_flight(scheduler_output)
                    # [FORCE] DF pick → decode_last_pending（交替门控）
                    self._force.on_pick(BatchType.DECODE_FIRST)
                    self._start_decode_last_delay()

                    # === Decode-first self-posting optimization ===
                    # Cloud's _maybe_publish_post_out merely replaces
                    # batch_type with DECODE_LAST.  We pre-generate it on
                    # the edge side and stash it in decodes_last_ready so
                    # that scheduling DECODE_LAST needs no round-trip
                    # through POST_OUT.  The cloud unconditionally skips
                    # POST_OUT for all DECODE_FIRST batches.
                    decode_last = replace(
                        scheduler_output,
                        batch_type=BatchType.DECODE_LAST,
                    )
                    self.decodes_last_ready.append(decode_last)
                    # ===============================================
                for req in list(self.waiting):
                    saved_waiting.prepend_request(req)
                self.chunk_prefill_first = saved_chunk_prefill_first
                self.waiting = saved_waiting
                self.skipped_waiting = saved_skipped
            else:
                self.chunk_prefill_first = saved_chunk_prefill_first
                self.waiting = saved_waiting
                self.skipped_waiting = saved_skipped

        return scheduler_output  # type: ignore[return-value]

    def _migrate_prefill_to_running(self) -> None:
        """Move fully-prefilled requests from chunk_prefill_first to running.

        When chunk_prefill_prior is enabled, a request stays in
        chunk_prefill_first even after ``is_prefill_chunk`` becomes False
        if it still has pending PL returns.  Only requests with zero
        pending tails are eligible to enter decode.
        """
        completed = [
            req for req in self.chunk_prefill_first
            if not req.is_prefill_chunk
            and self._pending_tail_count.get(req.request_id, 0) == 0
            # 设计 §5.5：running 门控——prefill_draft 链未完成的请求不得
            # 迁移（chunk-prior 的 defer 目的地即本队列）。
            and req.request_id not in self._running_gated_req_ids
            and self._req_pending_prefill_draft_steps.get(
                req.request_id, 0
            ) == 0
        ]
        for req in completed:
            self.chunk_prefill_first.remove(req)
            self.running.append(req)
            # A preempted request lands in chunk_prefill_first (status
            # stays PREEMPTED) and may be re-added to running here.  If
            # super().schedule() later selects it for preemption again,
            # _preempt_request asserts status == RUNNING.  Restore the
            # status unconditionally: the request was fully prefilled and
            # is entering decode — it must be RUNNING.
            if req.status != RequestStatus.RUNNING:
                req.status = RequestStatus.RUNNING

    def _preempt_request(self, request: Request, timestamp: float) -> None:
        if not self._is_request_preemptible(request):
            raise RuntimeError(
                "Cannot preempt an active edge-cloud request: "
                f"request_id={request.request_id}, status={request.status}, "
                "active_flights="
                f"{self._pd_active_flight_count.get(request.request_id, 0)}"
            )

        # Use the upstream recovery path so KV ownership, computed progress,
        # request status, and resumed-request metadata stay consistent.
        super()._preempt_request(request, timestamp)
        # 对抗 review E1（防御）：抢占后重 prefill 的请求，其旧链计费
        # 不再属于本生命周期——清空计数/链代/gated。当前 _is_request_preemptible
        # 已排除 gated 请求，此处仅在既有链路变更时兜底；KV 失效路径
        # （_handle_invalid_blocks）单独清账。
        self._req_pending_prefill_draft_steps.pop(request.request_id, None)
        self._req_charged_draft_tasks.pop(request.request_id, None)
        self._running_gated_req_ids.discard(request.request_id)
        self._cleanup_request_flight_state(request.request_id)
        request.chunk_num = 1
        request.is_prefill_chunk = False

    def _update_after_schedule(self, scheduler_output: SchedulerOutput) -> None:
        was_prefill_map = {}
        for req_id in scheduler_output.num_scheduled_tokens:
            was_prefill_map[req_id] = self.requests[req_id].is_prefill_chunk

        super()._update_after_schedule(scheduler_output)

        for req_id, num_scheduled_token in scheduler_output.num_scheduled_tokens.items():
            if was_prefill_map[req_id] and num_scheduled_token > 0:
                self.requests[req_id].chunk_num += 1

        self._migrate_prefill_to_running()
        self.finished_req_ids = set()

    # ------------------------------------------------------------------ #
    # update_from_output — chunk-prefill-prior routing                    #
    # ------------------------------------------------------------------ #
    def _update_from_output_prefill_last_legacy(
        self,
        scheduler_output: SchedulerOutput,
        has_fallback_chain: bool = False,
    ) -> None:
        """Legacy PL routing: request-granularity pending list."""
        completed_req_ids = set(scheduler_output.num_scheduled_tokens.keys())
        newly_running: list[Request] = []
        newly_chunked: list[Request] = []
        remaining_pending: list[Request] = []
        for req in self.prefill_last_pending:
            if req.request_id in completed_req_ids:
                if req.is_prefill_chunk:
                    self.chunk_prefill_first.append(req)
                    newly_chunked.append(req)
                elif (
                    # 设计 §5.5：running 门控——per-req 计数未完（
                    # pregenerated 链）或 fallback 链预注册（counter 尚为
                    # 0，链将由 EngineCore _advance_edge_cloud_draft 在
                    # 本 update 之后入队）⇒ 留在 prefill_last_pending，
                    # 链终结时由 _migrate_ready_prefill_pending 移入
                    # running。
                    self._req_pending_prefill_draft_steps.get(
                        req.request_id, 0
                    ) > 0
                    or has_fallback_chain
                ):
                    self._running_gated_req_ids.add(req.request_id)
                    remaining_pending.append(req)
                else:
                    self.running.append(req)
                    newly_running.append(req)
            else:
                remaining_pending.append(req)
        self.prefill_last_pending = remaining_pending

        # logger.info(
        #     f"[PD] update_from_output PREFILL_LAST done, "
        #     f"prefill_inflight: {self.prefill_inflight_count}/{self.prefill_inflight_limit}, "
        #     f"moved {len(newly_running)} reqs to running[], "
        #     f"moved {len(newly_chunked)} reqs to chunk_prefill_first[], "
        #     f"running[]: {len(self.running)}, "
        #     f"chunk_prefill_first[]: {len(self.chunk_prefill_first)}",
        # )

    def _update_from_output_prefill_last_chunk_prior(
        self,
        scheduler_output: SchedulerOutput,
        has_fallback_chain: bool = False,
    ) -> None:
        """Chunk-prefill-prior PL routing: head_token → flight lookup."""
        head_token = scheduler_output.head_token
        if not head_token:
            logger.warning(
                "[PD-CHUNK-PRIOR] PREFILL_LAST missing head_token; "
                "falling back to legacy routing."
            )
            self._update_from_output_prefill_last_legacy(
                scheduler_output, has_fallback_chain
            )
            return

        flight = self._prefill_flight_by_token.pop(head_token, None)
        if flight is None:
            logger.warning(
                "[PD-CHUNK-PRIOR] PREFILL_LAST head_token=%s not found "
                "in flight map; falling back to legacy routing.",
                head_token,
            )
            self._update_from_output_prefill_last_legacy(
                scheduler_output, has_fallback_chain
            )
            return

        req_id = flight.request_id
        req = self.requests.get(req_id)

        # Decrement pending tail count.
        prev_count = self._pending_tail_count.get(req_id, 0)
        if prev_count > 0:
            self._pending_tail_count[req_id] = prev_count - 1
        remaining = self._pending_tail_count.get(req_id, 0)

        # Decrement ahead count if this chunk was pre-scheduled.
        ahead_before = self._ahead_chunk_count.get(req_id, 0)
        if ahead_before > 0:
            self._ahead_chunk_count[req_id] = ahead_before - 1

        logger.info(
            "[PD-CHUNK-PRIOR] PL returned: request=%s chunk=%d/%s "
            "head_token=%s tokens=%d "
            "pending_tails: %d→%d ahead: %d→%d",
            req_id,
            flight.chunk_index,
            "last" if flight.is_last_chunk else "mid",
            head_token,
            flight.num_scheduled_tokens,
            prev_count,
            remaining,
            ahead_before,
            self._ahead_chunk_count.get(req_id, 0),
        )

        if flight.is_last_chunk and remaining == 0:
            # All chunks complete → request enters decode.
            if (
                # 设计 §5.5：running 门控——prefill_draft 链未完（per-req
                # 计数未完或 fallback 链预注册）⇒ 推迟到
                # chunk_prefill_first，链终结时由
                # _migrate_ready_prefill_pending 移入 running。该队列
                # 中被门控的请求已从 PF 候选剔除（_prepare_pf_running_state），
                # 不会再次被调度 prefill。
                self._req_pending_prefill_draft_steps.get(req_id, 0) > 0
                or has_fallback_chain
            ):
                self._running_gated_req_ids.add(req_id)
                if req is not None:
                    self.chunk_prefill_first.append(req)
                self._cleanup_request_flight_state(req_id)
                logger.info(
                    "[PD-CHUNK-PRIOR] Request %s all chunks done but "
                    "prefill_draft chain incomplete: deferred in "
                    "chunk_prefill_first[] until chain completes.",
                    req_id,
                )
            else:
                if req is not None:
                    self.running.append(req)
                self._cleanup_request_flight_state(req_id)
                logger.info(
                    "[PD-CHUNK-PRIOR] Request %s all chunks done, "
                    "moved to running[] (%d total).",
                    req_id,
                    len(self.running),
                )
        else:
            # Mid-chunk PL returned, or last chunk but other tails still
            # pending.  Re-add for the next chunk IF there are more chunks
            # to schedule AND the request is not already queued.  This keeps
            # the pipeline continuous across >2 chunks: the next chunk's PF
            # fills the prefill slot freed by this PL, overlapping other
            # in-flight PLs (e.g. 4 chunks -> chunk2 PF starts as soon as
            # chunk0 PL returns, overlapping chunk1's PL, instead of waiting
            # for chunk1's PL).  The old logic skipped re-add whenever
            # ahead_before > 0, which forced pair-wise scheduling
            # ((0,1) then (2,3)) and left a slot idle between pairs.
            # Do NOT call _cleanup_request_flight_state here: ahead count
            # and in-flight flights are still needed for outstanding chunks.
            has_more_chunks = (
                req is not None
                and req.num_computed_tokens < req.num_prompt_tokens
            )
            already_queued = (
                req is not None and req in self.chunk_prefill_first
            )
            if has_more_chunks and not already_queued:
                self.chunk_prefill_first.append(req)
                logger.info(
                    "[PD-CHUNK-PRIOR] Request %s chunk %d PL: "
                    "re-added to chunk_prefill_first[] for next chunk "
                    "(remaining=%d, ahead=%d).",
                    req_id,
                    flight.chunk_index,
                    remaining,
                    self._ahead_chunk_count.get(req_id, 0),
                )
            else:
                logger.info(
                    "[PD-CHUNK-PRIOR] Request %s chunk %d PL: "
                    "skip re-add (remaining=%d, ahead=%d, more=%s, "
                    "queued=%s).",
                    req_id,
                    flight.chunk_index,
                    remaining,
                    self._ahead_chunk_count.get(req_id, 0),
                    has_more_chunks,
                    already_queued,
                )

    def update_from_output(
        self,
        scheduler_output: SchedulerOutput,
        model_runner_output: ModelRunnerOutput,
    ) -> dict[int, Any]:
        if scheduler_output.batch_type == BatchType.PREFILL_LAST:
            # Phase B（设计 §5.2）：PL 完成不再无条件释放 prefill 槽，改
            # 为消费 PL 哨兵后按 pending 决定。若本次 PL 输出携带
            # deferred draft state（fallback 链起点，task_id == head_token），
            # 链将在 EngineCore 的 _advance_edge_cloud_draft 中入队——
            # 须保持槽占用，否则其入队后派发的 PDFF 会写到已归还的
            # 通道上。
            # 同 turn 原子性（review Bug 3）：本函数与
            # _advance_edge_cloud_draft 在 EngineCore 同一 step 内先后
            # 执行（patch_engine_core.py update_from_output 之后立即
            # _advance），has_fallback_chain 为真 ⇒ 同 turn 内
            # enqueue_draft_first 必然补 +1（槽记账与 §5.5 per-req 计数
            # 皆依赖此配对）；若 _advance 因 use_spec_decode/state 缺失
            # 早退，worker 亦不会产生 state，本判定恒为 False，无泄漏。
            head_token = scheduler_output.head_token
            state = getattr(model_runner_output, "edge_cloud_draft_state", None)
            has_fallback_chain = bool(
                head_token
                and state is not None
                and state.get("draft_task_id") == head_token
            )
            if head_token in self._prefill_slot_pending:
                self._prefill_slot_pl_done[head_token] = True
                if self._prefill_slot_pending[head_token] > 0:
                    self._prefill_slot_pending[head_token] -= 1
                if not has_fallback_chain:
                    self._try_finalize_prefill_slot(head_token)

            # logger.info(
            #     f"[PD] update_from_output PREFILL_LAST done, "
            #     f"prefill_inflight: {self.prefill_inflight_count}/{self.prefill_inflight_limit}, "
            #     f"moved {len(newly_running)} reqs to running[], "
            #     f"moved {len(newly_chunked)} reqs to chunk_prefill_first[], "
            #     f"running[]: {len(self.running)}, "
            #     f"chunk_prefill_first[]: {len(self.chunk_prefill_first)}",
            # )
            if self.chunk_prefill_prior_enable:
                self._update_from_output_prefill_last_chunk_prior(
                    scheduler_output, has_fallback_chain
                )
            else:
                self._update_from_output_prefill_last_legacy(
                    scheduler_output, has_fallback_chain
                )

        if scheduler_output.batch_type == BatchType.DECODE_FIRST:
            # D首完成后立即释放 inflight 计数，使下一个 D首可以
            # 在 D尾仍在 batch_queue 中时就被调度，消除 Cloud idle gap。
            if self.decode_or_draft_inflight_count > 0:
                self.decode_or_draft_inflight_count -= 1
            if self.decode_head_inflight_count > 0:
                self.decode_head_inflight_count -= 1
            logger.info(
                f"[PD] update_from_output DECODE_FIRST done, "
                f"decode_or_draft_inflight: {self.decode_or_draft_inflight_count}/{self.decode_or_draft_inflight_limit}",
            )
        if scheduler_output.batch_type in (
            BatchType.DECODE_DRAFT_FIRST,
        ):
            # decode 域草稿占用 DECODE 通道，head 完成后即释放共享
            # inflight 计数。
            self.decode_or_draft_inflight_count = max(
                0, self.decode_or_draft_inflight_count - 1
            )
            logger.info(
                "[PD] update_from_output %s done, "
                "decode_or_draft_inflight: %d/%d",
                scheduler_output.batch_type.value,
                self.decode_or_draft_inflight_count,
                self.decode_or_draft_inflight_limit,
            )
        elif scheduler_output.batch_type == BatchType.PREFILL_DRAFT_FIRST:
            # Phase B（设计 §4.1/§5.4）：prefill 域草稿走父 chunk 的
            # Prefill 通道，派发时未占用 decode_or_draft_inflight，完成
            # 时也不释放（否则会破坏 decode 域计数/负账）。
            logger.info(
                "[PD] update_from_output PREFILL_DRAFT_FIRST done "
                "(prefill domain, no shared inflight release)"
            )
        enqueue_next_draft = (
            scheduler_output.batch_type
            in (
                BatchType.PREFILL_DRAFT_LAST,
                BatchType.DECODE_DRAFT_LAST,
            )
        )
        if enqueue_next_draft:
            # 4 域拆分（设计 §5.4）：remote pending 按域各自递减。
            if scheduler_output.batch_type in (
                BatchType.PREFILL_DRAFT_LAST,
            ):
                self.prefill_draft_remote_pending_count = max(
                    0, self.prefill_draft_remote_pending_count - 1
                )
                # Phase B（设计 §5.2）：该步完成，pending -1。finalize
                # 判断推迟到 _enqueue_next_draft_first 之后（fallback 链
                # 的下一步在 PDFL 完成时才入队 +1；此处立即 finalize 会
                # 在下一步入队前提前释放通道）。
                task_id = scheduler_output.draft_task_id
                if (
                    task_id in self._prefill_slot_pending
                    and self._prefill_slot_pending[task_id] > 0
                ):
                    self._prefill_slot_pending[task_id] -= 1
                # 设计 §5.5：running 门控 per-req 计数按链成员（与入队时
                # 同键：draft_output_req_ids）递减。归零请求的迁移推迟到
                # _enqueue_next_draft_first 之后统一处理（fallback 链下一步
                # 在此刻才入队，提前迁移会放行链未完成的请求）。() 是
                # mid-chunk 链的合法值（无成员可减），显式 None 判断。
                gate_req_ids = getattr(
                    scheduler_output, "draft_output_req_ids", None
                )
                if gate_req_ids is None:
                    gate_req_ids = tuple(scheduler_output.num_scheduled_tokens)
                for req_id in gate_req_ids:
                    # 对抗 review A1：链代校验——仅当本 PDFL 的 task_id
                    # 曾在"当前请求生命周期"内计费（+1 时登记）才递减。
                    # 旧链残余 PDFL（同 id 重提交后）不会侵蚀新请求计数；
                    # finished 请求的账已在 drop_stale 清空，此处跳过。
                    if (
                        task_id
                        not in self._req_charged_draft_tasks.get(
                            req_id, set()
                        )
                    ):
                        continue
                    cnt = self._req_pending_prefill_draft_steps.get(
                        req_id, 0
                    )
                    if cnt > 0:
                        self._req_pending_prefill_draft_steps[req_id] = (
                            cnt - 1
                        )
            else:
                self.decode_draft_remote_pending_count = max(
                    0, self.decode_draft_remote_pending_count - 1
                )
        if scheduler_output.batch_type == BatchType.DECODE_LAST:
            # decode_or_draft_inflight_count 已在 DECODE_FIRST 的 update_from_output
            # 中释放，此处不再重复减 1。
            logger.info(
                f"[PD] update_from_output DECODE_LAST done, "
                f"decode_or_draft_inflight: {self.decode_or_draft_inflight_count}/{self.decode_or_draft_inflight_limit}",
            )
        outputs = super().update_from_output(scheduler_output, model_runner_output)
        if scheduler_output.batch_type in _PD_LAST_TO_FIRST:
            self._complete_pd_flight(scheduler_output)
        if self.finished_req_ids:
            # Natural completion is handled inside the base update path and
            # does not pass through finish_requests().  Do not dispatch any
            # not-yet-enqueued placeholder tasks for those requests.
            self._drop_stale_drafts_for_req_ids(self.finished_req_ids)
        if enqueue_next_draft:
            next_draft_ready = self._enqueue_next_draft_first(
                scheduler_output
            )
            if (
                scheduler_output.batch_type
                == BatchType.PREFILL_DRAFT_LAST
                and not next_draft_ready
            ):
                # Phase B（设计 §5.2）：无下一步入队（链终结或入队被拒），
                # pending 已无未完成步则 finalize 父 prefill 槽（幂等）。
                self._try_finalize_prefill_slot(
                    scheduler_output.draft_task_id
                )
                # 设计 §5.5：链终结（final PDFL）→ 计数器归零的被门控
                # 请求移入 running（含 fallback 链：此步 -1 后计数恰为
                # 0，且注册表在 update_from_output 之后才被 release，
                # 故迁移只查计数）。
                self._migrate_ready_prefill_pending()
            logger.info(
                "[PD] update_from_output %s done, "
                "prefill_draft_remote_pending: %d, "
                "decode_draft_remote_pending: %d, next_draft_ready: %s",
                scheduler_output.batch_type.value,
                self.prefill_draft_remote_pending_count,
                self.decode_draft_remote_pending_count,
                next_draft_ready,
            )
        self.chunk_prefill_first = [
            req for req in self.chunk_prefill_first if not req.is_finished()
        ]
        self.prefill_last_pending = [
            req for req in self.prefill_last_pending if not req.is_finished()
        ]
        # Drain finished requests from running: update_from_output removes
        # completed requests from self.requests, but they may still be in
        # running.  That causes KeyError in super().schedule() /
        # _update_after_schedule when the base scheduler accesses
        # self.requests[req_id].  Clean them up here, once per step.
        self.running = [
            req for req in self.running
            if req.request_id in self.requests
        ]
        return outputs

    def get_request_counts(self) -> tuple[int, int]:
        num_running, num_waiting = super().get_request_counts()
        if self.chunk_prefill_prior_enable:
            # Use a set to avoid double-counting requests that appear in
            # multiple tracking structures (e.g. a request in
            # prefill_last_pending also has _pending_tail_count > 0).
            pending_ids: set[str] = set()
            pending_ids.update(
                req.request_id for req in self.chunk_prefill_first
            )
            pending_ids.update(
                req.request_id for req in self.prefill_last_pending
            )
            pending_ids.update(self._pending_tail_count.keys())
            return (num_running + len(pending_ids), num_waiting)
        return (
            num_running
            + len(self.chunk_prefill_first)
            + len(self.prefill_last_pending),
            num_waiting,
        )

    def get_num_unfinished_requests(self) -> int:
        if self._pause_state == PauseState.PAUSED_ALL:
            return 0
        base = super().get_num_unfinished_requests()
        if self.chunk_prefill_prior_enable:
            pending_ids: set[str] = set()
            pending_ids.update(
                req.request_id for req in self.chunk_prefill_first
            )
            pending_ids.update(
                req.request_id for req in self.prefill_last_pending
            )
            pending_ids.update(self._pending_tail_count.keys())
            return base + len(pending_ids)
        return (
            base
            + len(self.chunk_prefill_first)
            + len(self.prefill_last_pending)
        )

    def _has_draft_work(self) -> bool:
        return bool(
            self.decodes_first_ready
            or self.prefill_drafts_first_ready
            or self.prefill_drafts_last_ready
            or self.decode_drafts_first_ready
            or self.decode_drafts_last_ready
            # review Bug 2（活性）：PF/PL 在飞或 PL 尾在 inbox 等待时，
            # has_requests() 必须为 True——否则 abort 后引擎空闲，
            # _patched_step 早退不再 drain POST_OUT inbox，PL 滞留永不
            # 释放通道。prefill_inflight_count>0 同时覆盖 running 门控
            # 推迟中的请求（其槽由 §5.2 记账保持占用）。
            or bool(self.prefills_last_ready)
            or self.prefill_inflight_count > 0
            or self.decode_or_draft_inflight_count > 0
            or self.prefill_draft_remote_pending_count > 0
            or self.decode_draft_remote_pending_count > 0
        )

    def has_requests(self) -> bool:
        return super().has_requests() or self._has_draft_work()

    def finish_requests(
        self, request_ids: str | Iterable[str] | None, finished_status: RequestStatus
    ) -> list[tuple[str, int]]:
        result = super().finish_requests(request_ids, finished_status)
        finished_req_ids = {req_id for req_id, _client_index in result}
        self._drop_stale_drafts_for_req_ids(finished_req_ids)
        if isinstance(request_ids, str):
            request_ids = (request_ids,)
        elif request_ids is not None:
            request_ids = set(request_ids)
        else:
            request_ids = self.requests.keys()

        to_remove = set()
        for req_id in request_ids:
            req = self.requests.get(req_id)
            if req and req.is_finished():
                to_remove.add(req)
                # Clean up chunk-prefill-prior flight state.
                self._cleanup_request_flight_state(req_id)

        if to_remove:
            self.chunk_prefill_first = remove_all(
                self.chunk_prefill_first, to_remove
            )

        return result

    def reset_prefix_cache(
        self, reset_running_requests: bool = False, reset_connector: bool = False
    ) -> bool:
        if reset_running_requests:
            if self._pd_active_flight_count:
                logger.warning(
                    "Cannot reset running requests while edge-cloud flights "
                    "are active: %s",
                    self._pd_active_flight_count,
                )
                return False

            if any(
                not self._is_request_preemptible(request)
                for request in self.chunk_prefill_first
            ):
                logger.warning(
                    "Cannot reset edge-cloud prefill requests because at least "
                    "one request is not safely preemptible"
                )
                return False

            timestamp = time.monotonic()
            while self.chunk_prefill_first:
                request = self.chunk_prefill_first.pop()
                self._preempt_request(request, timestamp)
                request.async_tokens_to_discard = (
                    request.num_output_placeholders
                )
                request.num_output_placeholders = 0

        return super().reset_prefix_cache(reset_running_requests, reset_connector)

    def make_stats(self, *args, **kwargs):
        stats = super().make_stats(*args, **kwargs)
        if stats is not None:
            stats.num_running_reqs += len(self.chunk_prefill_first)
        return stats

    def _handle_invalid_blocks(self, invalid_block_ids: set[int]) -> set[str]:
        saved_running = self.running
        self.running = list(self.running) + [
            r for r in self.chunk_prefill_first if r not in self.running
        ]
        try:
            result = super()._handle_invalid_blocks(invalid_block_ids)
        finally:
            self.running = saved_running
        # 对抗 review E1：KV 失效强制重 prefill 的请求，其旧链已无意义——
        # 清空 running 门控记账（计数/链代/gated），旧链残余 PDFL 的递减
        # 不得侵蚀重 prefill 后新链的计数（跨链递减 → 提前放行）。槽记账
        # 不受影响：旧链步仍占通道，由 _prefill_slot_pending 独立清账。
        for req_id in result:
            self._req_pending_prefill_draft_steps.pop(req_id, None)
            self._req_charged_draft_tasks.pop(req_id, None)
            self._running_gated_req_ids.discard(req_id)
        return result


class AsyncPDSeparatedScheduler(PDSeparatedScheduler, AsyncScheduler):
    """Async scheduler with PD separation."""
    pass

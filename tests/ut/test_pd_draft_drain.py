# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the draft FIRST -> draft LAST alternation invariant and the
drain path that pairs the cloud's draft response when the owning request
finishes or is aborted mid-chain.

Phase A: the single-domain draft API was split into prefill-draft and
decode-draft domains.  These tests cover the decode-draft domain (still on
the DECODE channel); the prefill-draft domain is the same logic keyed by
its own queues/counters/flags, exercised indirectly via
_pregenerate_draft_chain in TestMidPrefillDraftChain.

Regression coverage for the edge-side MTP draft deadlock fixes:

  * ``_can_schedule_decode_draft_first`` (pre-generated branch) now respects
    the FORCE state machine's ``decode_draft_last_pending`` (design §6.3.2)
    -- a second DECODE_DRAFT_FIRST may not be picked until the preceding
    DECODE_DRAFT_LAST is picked (which clears it).  Previously the
    pre-generated branch omitted this guard, so a draft LAST dropped without
    clearing the flag let a second draft FIRST through (two heads with no
    tail on the shared DECODE channel -> cloud ``irecv`` deadlock).
  * ``_is_stale_draft_output`` no longer exempts pre-generated dispatched
    chains: once the owning request is gone, future (not-yet-dispatched)
    draft FIRST heads are stale and must be skipped -- the edge can no longer
    produce their payload (draft context cleared) and the cloud would otherwise
    wait forever for data.
  * ``_pick_decode_draft_last_batch`` never drops a dispatched draft LAST; it
    drains it (the cloud always ``isend``s a response, so the edge must
    ``irecv`` to keep the DECODE channel paired) and only spawns a verify
    placeholder for a live request.
  * ``_run_edge_cloud_draft_last_segment`` drains (recv already done by the
    caller, skip tail compute, return a token-less placeholder) when the draft
    context is gone, instead of raising.
  * Every middle prefill chunk runs a complete draft chain to populate MTP KV,
    while its proposals are discarded and no target verify placeholder is
    created.
"""

from collections import deque
import time
from unittest.mock import MagicMock

import pytest

from vllm.v1.core.sched.output import (
    BatchType,
    HiddenChannelType,
    SchedulerOutput,
)


# ------------------------------------------------------------------ #
# Helpers                                                            #
# ------------------------------------------------------------------ #


def _make_bare_scheduler():
    from vllm_ascend.core.pd_separated_scheduler import (
        EdgeForceStateMachine,
        PDSeparatedScheduler,
    )

    s = PDSeparatedScheduler.__new__(PDSeparatedScheduler)
    s.decode_drafts_first_ready = deque()
    s.decode_drafts_last_ready = deque()
    s.prefill_drafts_first_ready = deque()
    s.prefill_drafts_last_ready = deque()
    s.requests = {}
    s._pregenerated_draft_task_ids = set()
    s._pregenerated_draft_req_ids = {}
    s._draft_first_dispatched = False
    s._draft_first_cloud_publish_pending = None
    s._draft_first_scalars_patched = False
    s._decode_draft_remote_pending_limit = 2
    s.decode_draft_remote_pending_count = 0
    s.decode_or_draft_inflight_count = 0
    s.decode_or_draft_inflight_limit = 1
    s.decode_head_inflight_count = 0
    # [EHER-draft] P1/P2 gate state: ack set + switches + delay fallback
    # baseline (see _can_schedule_decode_draft_first/_last).
    s._decode_draft_pipeline_enable = False
    s._decode_draft_recv_ack_enable = False
    s._draft_recv_ready_acks = set()
    s._decode_draft_last_delay_start_ts = None
    s._decode_draft_last_delay_schedule_ms = 15
    # [FORCE] 状态机（设计 §6.3.2）：交替与窗口状态在此驱动/断言。
    s._force = EdgeForceStateMachine()
    s.num_spec_tokens = 3
    return s


def _make_draft_first(task_id="task-0", req_id="req-0", step=0):
    so = MagicMock()
    so.batch_type = BatchType.DECODE_DRAFT_FIRST
    so.draft_task_id = task_id
    so.draft_step_idx = step
    so.head_token = f"tok-{task_id}-{step}"
    so.hidden_channel = HiddenChannelType.DRAFT
    so.num_scheduled_tokens = {req_id: 1}
    so.parent_req_id = req_id
    so.num_accepted_tokens = None
    so.valid_sampled_token_count = None
    so.is_last_prefill_chunk = True
    so.draft_output_req_ids = (req_id,)
    return so


def _make_draft_last(task_id="task-0", req_id="req-0", step=0):
    so = MagicMock()
    so.batch_type = BatchType.DECODE_DRAFT_LAST
    so.draft_task_id = task_id
    so.draft_step_idx = step
    so.head_token = f"tok-{task_id}-{step}"
    so.hidden_channel = HiddenChannelType.DRAFT
    so.num_scheduled_tokens = {req_id: 1}
    so.parent_req_id = req_id
    so.is_last_prefill_chunk = True
    so.draft_output_req_ids = (req_id,)
    return so


def _make_real_output(
    batch_type=BatchType.PREFILL_LAST,
    task_id="task-0",
    req_id="req-0",
):
    so = SchedulerOutput.make_empty()
    so.batch_type = batch_type
    so.head_token = task_id
    so.num_scheduled_tokens = {req_id: 8}
    so.total_num_scheduled_tokens = 8
    return so


# ------------------------------------------------------------------ #
# Test: _can_schedule_decode_draft_first honors force flag (fix ①)   #
# ------------------------------------------------------------------ #


class TestCanScheduleDecodeDraftFirstForceGuard:
    """The pre-generated branch must gate on the FORCE state machine's
    ``decode_draft_last_pending`` just like the non-pre-generated branch,
    so DECODE_DRAFT_FIRST -> DECODE_DRAFT_LAST alternation is
    guaranteed."""

    def _setup(self, pregenerated=True):
        s = _make_bare_scheduler()
        drf = _make_draft_first()
        s.decode_drafts_first_ready.append(drf)
        if pregenerated:
            s._pregenerated_draft_task_ids.add(drf.draft_task_id)
        # Conditions that would otherwise allow scheduling.
        s.decode_drafts_last_ready = deque()
        s._force.decode_last_pending = False
        s._force.decode_draft_last_pending = False
        s.decode_draft_remote_pending_count = 0
        s.decode_or_draft_inflight_count = 0
        return s

    def test_preGen_blocked_when_force_draft_last_true(self):
        s = self._setup(pregenerated=True)
        s._force.decode_draft_last_pending = True
        assert s._can_schedule_decode_draft_first() is False

    def test_preGen_allowed_when_force_draft_last_false(self):
        s = self._setup(pregenerated=True)
        s._force.decode_draft_last_pending = False
        assert s._can_schedule_decode_draft_first() is True

    def test_preGen_blocked_by_drafts_last_ready(self):
        s = self._setup(pregenerated=True)
        s._force.decode_draft_last_pending = False
        s.decode_drafts_last_ready.append(_make_draft_last())
        assert s._can_schedule_decode_draft_first() is False

    def test_preGen_blocked_when_decode_head_in_flight(self):
        """Regression for decode_or_draft_inflight=2/1: DECODE_DRAFT_FIRST and
        DECODE_FIRST use different recv primitives but share the DECODE
        stream, so a draft FIRST must not be dispatched while a DECODE_FIRST
        head is in flight (the cloud's recv order could mismatch the edge's
        send order).  Gate on decode heads, not total heads."""
        s = self._setup(pregenerated=True)
        s._force.decode_draft_last_pending = False
        s.decode_head_inflight_count = 1  # a DECODE_FIRST in flight
        assert s._can_schedule_decode_draft_first() is False
        s.decode_head_inflight_count = 0
        assert s._can_schedule_decode_draft_first() is True

    def test_preGen_allows_draft_pipeline_while_draft_in_flight(self):
        """The next DECODE_DRAFT_FIRST MAY be dispatched while a previous
        draft FIRST is still in flight (draft pipelining): draft FIRST is an
        edge->cloud send while draft LAST is a cloud->edge recv (opposite
        stream directions), and draft+draft uses the same recv primitive
        (FIFO).  Only a DECODE_FIRST head blocks it, not another draft head."""
        s = self._setup(pregenerated=True)
        s._force.decode_draft_last_pending = False  # prev draft LAST already picked
        s.decode_drafts_last_ready = deque()  # prev draft LAST popped (in flight)
        s.decode_head_inflight_count = 0  # no DECODE_FIRST in flight
        s.decode_or_draft_inflight_count = 1  # a draft FIRST in flight
        s.decode_draft_remote_pending_count = 1  # under the pipeline credit (<2)
        assert s._can_schedule_decode_draft_first() is True

    def test_non_pregenerated_branch_also_blocked_by_force_draft_last(self):
        """Non-pre-generated branch already had the guard (unchanged)."""
        s = self._setup(pregenerated=False)
        s._force.decode_draft_last_pending = True
        assert s._can_schedule_decode_draft_first() is False


class TestDecodeDraftPipelineGate:
    """[P2-1] With decode_draft_pipeline_enable, the serial ==0 gate relaxes
    to < limit (drafts own the dedicated DRAFT channel; per-direction FIFO
    matching makes concurrent chains safe).  Legacy behavior is unchanged
    while the switch is off."""

    def _setup(self):
        s = _make_bare_scheduler()
        s.decode_drafts_first_ready.append(_make_draft_first())
        s._force.decode_last_pending = False
        s._force.decode_draft_last_pending = False
        return s

    def test_legacy_serial_gate_blocks_second_head(self):
        s = self._setup()
        s.decode_or_draft_inflight_count = 1
        s.decode_draft_remote_pending_count = 1
        assert s._can_schedule_decode_draft_first() is False

    def test_pipeline_allows_second_head_under_limit(self):
        s = self._setup()
        s._decode_draft_pipeline_enable = True
        s.decode_or_draft_inflight_count = 1
        s.decode_draft_remote_pending_count = 1
        assert s._can_schedule_decode_draft_first() is True

    def test_pipeline_blocked_at_limit(self):
        s = self._setup()
        s._decode_draft_pipeline_enable = True
        s.decode_draft_remote_pending_count = 2  # == limit (2)
        assert s._can_schedule_decode_draft_first() is False

    def test_pipeline_blocked_when_last_ready_unpicked(self):
        s = self._setup()
        s._decode_draft_pipeline_enable = True
        s.decode_drafts_last_ready.append(_make_draft_last())
        assert s._can_schedule_decode_draft_first() is False


class TestDecodeDraftRecvAckGate:
    """[P1-5] With decode_draft_recv_ack_enable, a queued DDL is schedulable
    once the worker acks its return irecv, with a timeout fallback so a
    missing ack path can never stall the pipeline."""

    def _setup(self):
        s = _make_bare_scheduler()
        ddl = _make_draft_last()
        s.decode_drafts_last_ready.append(ddl)
        s._decode_draft_recv_ack_enable = True
        s._decode_draft_last_delay_start_ts = time.monotonic()
        return s, ddl.head_token

    def test_blocked_until_acked(self):
        s, _ = self._setup()
        assert s._can_schedule_decode_draft_last() is False

    def test_schedulable_on_ack(self):
        s, tok = self._setup()
        s.notify_draft_recv_ready(tok)
        assert s._can_schedule_decode_draft_last() is True

    def test_timeout_fallback_dispatches_without_ack(self):
        s, _ = self._setup()
        s._decode_draft_last_delay_start_ts = (
            time.monotonic() - 1.0
        )  # >> max(10*15ms, 100ms)
        assert s._can_schedule_decode_draft_last() is True

    def test_empty_queue_passes(self):
        s, _ = self._setup()
        s.decode_drafts_last_ready.clear()
        assert s._can_schedule_decode_draft_last() is True


class TestDraftFirstLastAlternation:
    """End-to-end gate check: a second draft FIRST is blocked while the first
    draft LAST is pending, and admitted only after the tail is picked."""

    def test_second_head_blocked_until_tail_picked(self):
        s = _make_bare_scheduler()
        s._pregenerated_draft_task_ids.add("task-0")
        # step-0 head already picked; step-1 is next in decode_drafts_first_ready.
        s.decode_drafts_first_ready.append(_make_draft_first(step=1))
        s._force.decode_last_pending = False
        s.decode_draft_remote_pending_count = 0

        # draft FIRST step-0 in force + its draft LAST pending -> step-1 blocked.
        s._force.decode_draft_last_pending = True
        s.decode_drafts_last_ready.append(_make_draft_last(step=0))
        assert s._can_schedule_decode_draft_first() is False

        # draft LAST step-0 picked -> flag cleared, no tail pending -> allowed.
        s._force.decode_draft_last_pending = False
        s.decode_drafts_last_ready.clear()
        assert s._can_schedule_decode_draft_first() is True


class TestMidPrefillDraftChain:
    """Every chunk warms MTP KV, but only the last chunk may seed verify.

    Phase A: a PREFILL_LAST parent classifies into the prefill-draft domain,
    so its pre-generated chain lands in prefill_drafts_first_ready (design
    §3.3 ``_draft_kind_of``)."""

    def test_pick_mid_prefill_tail_starts_draft_chain(self):
        s = _make_bare_scheduler()
        target = _make_real_output()
        flight = MagicMock()
        flight.is_last_chunk = False
        s.prefills_last_ready = deque([target])
        s._prefill_flight_by_token = {target.head_token: flight}
        s.chunk_prefill_first = []
        s._validate_prefill_tail_channel = MagicMock()
        s._pregenerate_draft_chain = MagicMock()

        result = s._pick_prefill_last_batch()

        assert result is target
        assert result.is_last_prefill_chunk is False
        assert result.draft_output_req_ids == ()
        s._pregenerate_draft_chain.assert_called_once_with(target)

    def test_pregenerates_mid_chunk_and_preserves_marker(self):
        s = _make_bare_scheduler()
        request = MagicMock()
        request.is_finished.return_value = False
        s.requests["req-0"] = request
        s._uses_async_scheduled_mtp_placeholders = MagicMock(
            return_value=True
        )

        target = _make_real_output()
        target.is_last_prefill_chunk = False
        target.draft_output_req_ids = ()
        s._pregenerate_draft_chain(target)

        assert len(s.prefill_drafts_first_ready) == s.num_spec_tokens
        assert all(
            getattr(output, "is_last_prefill_chunk", True) is False
            for output in s.prefill_drafts_first_ready
        )
        assert all(
            output.draft_output_req_ids == ()
            for output in s.prefill_drafts_first_ready
        )

    def test_mid_chunk_draft_tail_does_not_prepare_verify(self):
        s = _make_bare_scheduler()
        request = MagicMock()
        request.is_finished.return_value = False
        s.requests["req-0"] = request
        tail = _make_draft_last()
        tail.is_last_prefill_chunk = False
        tail.draft_output_req_ids = ()
        s.decode_drafts_last_ready.append(tail)
        s._force.decode_draft_last_pending = True
        s._validate_decode_draft_tail_channel = MagicMock()
        s._prepare_next_decode_first_placeholder = MagicMock()

        assert s._pick_decode_draft_last_batch() is tail
        s._prepare_next_decode_first_placeholder.assert_not_called()

    def test_engine_advances_mid_prefill_draft(self):
        from vllm_ascend.patch.platform.patch_engine_core import (
            _advance_edge_cloud_draft,
        )

        engine = MagicMock()
        engine.use_spec_decode = True
        finalized = _make_real_output(BatchType.DECODE_DRAFT_FIRST)
        engine.scheduler.finalize_pre_generated_draft_first.return_value = (
            finalized
        )
        completed = _make_real_output()
        completed.is_last_prefill_chunk = False
        model_output = MagicMock()
        model_output.edge_cloud_draft_state = {
            "draft_task_id": completed.head_token,
            "draft_step_idx": 0,
        }
        model_output.sampled_token_ids = [[]]

        _advance_edge_cloud_draft(engine, completed, model_output)

        engine.scheduler.finalize_pre_generated_draft_first.assert_called_once_with(
            draft_task_id=completed.head_token,
            num_accepted_tokens=[0],
            valid_sampled_token_count=[0],
        )
        engine._release_deferred_draft_pre_out.assert_called_once_with(
            completed.head_token
        )
        engine.scheduler.enqueue_draft_first.assert_not_called()

    def test_registers_worker_created_fallback_draft(self):
        from vllm_ascend.patch.platform.patch_engine_core import (
            _register_edge_cloud_draft_parent,
        )

        engine = MagicMock()
        engine.use_spec_decode = True
        engine._uses_scheduled_edge_cloud_draft.return_value = True
        completed = _make_real_output()
        model_output = MagicMock()
        model_output.edge_cloud_draft_state = {
            "draft_task_id": completed.head_token,
            "draft_step_idx": 0,
        }

        _register_edge_cloud_draft_parent(engine, completed, model_output)

        engine.scheduler.register_edge_cloud_draft_task.assert_called_once_with(
            completed.head_token, {"req-0"}
        )

    def test_does_not_register_without_worker_draft_state(self):
        from vllm_ascend.patch.platform.patch_engine_core import (
            _register_edge_cloud_draft_parent,
        )

        engine = MagicMock()
        engine.use_spec_decode = True
        engine._uses_scheduled_edge_cloud_draft.return_value = True
        completed = _make_real_output()
        model_output = MagicMock(spec=[])

        _register_edge_cloud_draft_parent(engine, completed, model_output)

        engine.scheduler.register_edge_cloud_draft_task.assert_not_called()


# ------------------------------------------------------------------ #
# Test: _draft_output_reqs_live / _is_stale_draft_output (fix ②d)    #
# ------------------------------------------------------------------ #


class TestDraftReqsLiveAndStale:
    def _setup(self, req_present=True, req_id="req-0"):
        s = _make_bare_scheduler()
        if req_present:
            s.requests[req_id] = MagicMock()
        so = _make_draft_last(req_id=req_id)
        return s, so

    def test_live_request_reqs_live_true(self):
        s, so = self._setup(req_present=True)
        assert s._draft_output_reqs_live(so) is True

    def test_dead_request_reqs_live_false(self):
        s, so = self._setup(req_present=False)
        assert s._draft_output_reqs_live(so) is False

    def test_live_request_not_stale(self):
        s, so = self._setup(req_present=True)
        assert s._is_stale_draft_output(so) is False

    def test_dead_request_stale(self):
        s, so = self._setup(req_present=False)
        assert s._is_stale_draft_output(so) is True

    def test_preGen_dispatched_dead_request_still_stale(self):
        """Regression for the removed override: a pre-generated, step-0-
        dispatched chain whose request has since gone must still be treated
        as stale for not-yet-dispatched heads.  Otherwise the edge picks and
        dispatches heads it can no longer produce payload for (context
        cleared) -> cloud waits forever for data that never arrives."""
        s, so = self._setup(req_present=False)
        s._pregenerated_draft_task_ids.add(so.draft_task_id)
        s._draft_first_dispatched = True
        assert s._is_stale_draft_output(so) is True


# ------------------------------------------------------------------ #
# Test: _pick_decode_draft_last_batch drains instead of dropping      #
# ------------------------------------------------------------------ #


class TestPickDecodeDraftLastBatchDrain:
    """A DECODE_DRAFT_LAST in decode_drafts_last_ready always has its
    DECODE_DRAFT_FIRST already dispatched to the cloud, so the cloud will
    isend a response -- the edge must execute (drain) the tail to pair it,
    never drop it."""

    def _setup(self, req_present=True):
        s = _make_bare_scheduler()
        if req_present:
            s.requests["req-0"] = MagicMock()
        s.decode_drafts_last_ready.append(_make_draft_last())
        s._force.decode_draft_last_pending = True
        s.decode_draft_remote_pending_count = 1
        # Stub side-effecting helpers to isolate the drain decision.
        s._validate_decode_draft_tail_channel = MagicMock()
        s._prepare_next_decode_first_placeholder = MagicMock()
        s._make_empty_batch = MagicMock(return_value="EMPTY")
        return s

    def test_dead_request_drained_not_dropped(self):
        s = self._setup(req_present=False)
        before = s.decode_draft_remote_pending_count
        result = s._pick_decode_draft_last_batch()

        # The tail is returned (dispatched to the worker for drain), not
        # dropped -- the cloud's response must be paired on the DECODE channel.
        assert result.batch_type == BatchType.DECODE_DRAFT_LAST
        assert len(s.decode_drafts_last_ready) == 0
        # decode_draft_last_pending is always reset now (old stale-drop skipped).
        assert s._force.decode_draft_last_pending is False
        # The decrement moved to update_from_output; the pick no longer
        # decrements (the old stale-drop did).
        assert s.decode_draft_remote_pending_count == before
        # No verify placeholder for a gone request.
        s._prepare_next_decode_first_placeholder.assert_not_called()
        s._validate_decode_draft_tail_channel.assert_called_once()

    def test_live_request_prepares_placeholder(self):
        s = self._setup(req_present=True)
        result = s._pick_decode_draft_last_batch()
        assert result.batch_type == BatchType.DECODE_DRAFT_LAST
        assert s._force.decode_draft_last_pending is False
        s._prepare_next_decode_first_placeholder.assert_called_once()

    def test_empty_returns_empty_batch(self):
        s = self._setup(req_present=True)
        s.decode_drafts_last_ready.clear()
        assert s._pick_decode_draft_last_batch() == "EMPTY"
        s._make_empty_batch.assert_called_once()


# ------------------------------------------------------------------ #
# Test: worker _run_edge_cloud_draft_last_segment drain (fix ②c)    #
# ------------------------------------------------------------------ #


class TestRunDraftLastSegmentDrain:
    """When the draft context is gone (request finished/aborted after its
    draft FIRST was dispatched), the tail segment must drain (the recv in
    _execute_model_edge_draft_tail already paired the cloud response) and
    return a token-less placeholder instead of raising."""

    def _make_runner(self, context_present=False):
        from vllm_ascend.worker.model_runner_v1 import NPUModelRunner

        runner = NPUModelRunner.__new__(NPUModelRunner)
        runner._pending_edge_cloud_draft_contexts = {}
        if context_present:
            runner._pending_edge_cloud_draft_contexts["task-0"] = MagicMock()
        return runner

    @staticmethod
    def _make_so(task_id="task-0"):
        so = MagicMock()
        so.draft_task_id = task_id
        so.draft_step_idx = 0
        so.num_scheduled_tokens = {"req-0": 1}
        return so

    def test_drains_when_context_gone(self):
        from vllm.v1.outputs import ModelRunnerOutput

        runner = self._make_runner(context_present=False)
        result = runner._run_edge_cloud_draft_last_segment(
            self._make_so(), MagicMock()
        )
        assert isinstance(result, ModelRunnerOutput)
        assert result.req_ids == ["req-0"]
        assert result.req_id_to_index == {"req-0": 0}

        assert result.req_id_to_index == {"req-0": 0}

    def test_drains_when_task_id_none(self):
        from vllm.v1.outputs import ModelRunnerOutput

        runner = self._make_runner(context_present=False)
        result = runner._run_edge_cloud_draft_last_segment(
            self._make_so(task_id=None), MagicMock()
        )
        assert isinstance(result, ModelRunnerOutput)
        assert result.req_ids == ["req-0"]

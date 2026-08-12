# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the draft-head -> draft-tail alternation invariant and the
drain path that pairs the cloud's draft-tail response when the owning request
finishes or is aborted mid-chain.

Regression coverage for the edge-side MTP draft deadlock fixes:

  * ``_can_schedule_draft_first`` (pre-generated branch) now respects
    ``_force_draft_last`` -- a second draft head may not be picked until the
    preceding draft tail is picked (which clears the flag).  Previously the
    pre-generated branch omitted this guard, so a draft tail dropped without
    clearing the flag let a second draft head through (two heads with no tail
    on the shared DECODE channel -> cloud ``irecv`` deadlock).
  * ``_is_stale_draft_output`` no longer exempts pre-generated dispatched
    chains: once the owning request is gone, future (not-yet-dispatched)
    draft heads are stale and must be skipped -- the edge can no longer
    produce their payload (draft context cleared) and the cloud would otherwise
    wait forever for data.
  * ``_pick_draft_last_batch`` never drops a dispatched draft tail; it drains
    it (the cloud always ``isend``s a response, so the edge must ``irecv`` to
    keep the DECODE channel paired) and only spawns a verify placeholder for a
    live request.
  * ``_run_edge_cloud_draft_last_segment`` drains (recv already done by the
    caller, skip tail compute, return a token-less placeholder) when the draft
    context is gone, instead of raising.
  * Every middle prefill chunk runs a complete draft chain to populate MTP KV,
    while its proposals are discarded and no target verify placeholder is
    created.

Phase B domain split (design §3/§4/§6): draft chains are classified by their
parent tail batch type into prefill_draft (PREFILL_DRAFT_*) and decode_draft
(DECODE_DRAFT_*) scheduling domains.  Each domain owns its ready queues /
alternation flags / delay timers / remote-pending credits, and the core pick /
guard methods are kind-parameterized (``_can_schedule_draft_first(kind)``,
``_pick_draft_last_batch(kind)``).  Since Phase B, prefill_draft rides the
inherited prefill channel and the decode domain rides DECODE, so each domain
only gates on its own alternation flag, never the other domain's — and
prefill_draft never gates on ``_force_decode_last``.  A prefill slot now spans
PF -> PL -> the whole draft chain (§5.2): the channel is released only when
the chain completes.
"""

from collections import deque
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

# Draft-domain kind constants, mirrored from pd_separated_scheduler's
# _DRAFT_KIND_PREFILL / _DRAFT_KIND_DECODE.
_PREFILL = "prefill"
_DECODE = "decode"


def _draft_first_type(kind=_DECODE) -> BatchType:
    return (
        BatchType.PREFILL_DRAFT_FIRST
        if kind == _PREFILL
        else BatchType.DECODE_DRAFT_FIRST
    )


def _draft_last_type(kind=_DECODE) -> BatchType:
    return (
        BatchType.PREFILL_DRAFT_LAST
        if kind == _PREFILL
        else BatchType.DECODE_DRAFT_LAST
    )


def _first_ready(s, kind=_DECODE):
    return (
        s.prefill_drafts_first_ready
        if kind == _PREFILL
        else s.decode_drafts_first_ready
    )


def _last_ready(s, kind=_DECODE):
    return (
        s.prefill_drafts_last_ready
        if kind == _PREFILL
        else s.decode_drafts_last_ready
    )


def _force_last(s, kind=_DECODE) -> bool:
    return (
        s._force_prefill_draft_last
        if kind == _PREFILL
        else s._force_decode_draft_last
    )


def _set_force_last(s, kind, value) -> None:
    if kind == _PREFILL:
        s._force_prefill_draft_last = value
    else:
        s._force_decode_draft_last = value


def _set_remote_pending(s, kind, value) -> None:
    if kind == _PREFILL:
        s.prefill_draft_remote_pending_count = value
    else:
        s.decode_draft_remote_pending_count = value


def _make_live_request():
    req = MagicMock()
    req.is_finished.return_value = False
    return req


def _make_bare_scheduler():
    from vllm_ascend.core.pd_separated_scheduler import PDSeparatedScheduler

    s = PDSeparatedScheduler.__new__(PDSeparatedScheduler)
    s.prefill_drafts_first_ready = deque()
    s.prefill_drafts_last_ready = deque()
    s.decode_drafts_first_ready = deque()
    s.decode_drafts_last_ready = deque()
    s.requests = {}
    s._pregenerated_draft_task_ids = set()
    s._pregenerated_draft_req_ids = {}
    s._edge_cloud_draft_task_reqs = {}
    s._dropped_draft_task_ids_to_report = []
    s._draft_first_dispatched = False
    s._draft_first_cloud_publish_pending = None
    s._draft_first_scalars_patched = False
    s._prefill_draft_remote_pending_limit = 2
    s._decode_draft_remote_pending_limit = 2
    s.prefill_draft_remote_pending_count = 0
    s.decode_draft_remote_pending_count = 0
    s.decode_or_draft_inflight_count = 0
    s.decode_or_draft_inflight_limit = 1
    s.decode_head_inflight_count = 0
    s._force_prefill_draft_last = False
    s._force_decode_draft_last = False
    s._force_decode_last = False
    s._prefill_draft_last_delay_start_ts = None
    s._decode_draft_last_delay_start_ts = None
    s._prefill_draft_last_delay_schedule_ms = 5
    s._decode_draft_last_delay_schedule_ms = 5
    s.num_spec_tokens = 3
    s._decode_or_draft_first_only_start_ts = None
    # Phase B fields (design §5.2): prefill slot refcount + per-domain
    # channel manager.  prefill_draft heads/tails resolve their channel
    # through the manager (inherited prefill channel), so a real manager
    # keeps the prefill-domain paths testable.
    s._prefill_slot_pending = {}
    s._prefill_slot_pl_done = {}
    s.prefill_inflight_count = 0
    s.prefill_inflight_limit = 2
    from vllm_ascend.core.pd_separated_scheduler import HiddenChannelManager

    s.hidden_channel_manager = HiddenChannelManager(
        dp_rank=0, is_shared_model_edge=False
    )
    return s


def _make_draft_first(task_id="task-0", req_id="req-0", step=0, kind=_DECODE):
    so = MagicMock()
    so.batch_type = _draft_first_type(kind)
    so.draft_task_id = task_id
    so.draft_step_idx = step
    so.head_token = f"tok-{task_id}-{step}"
    # Phase B: prefill_draft rides the inherited prefill channel;
    # decode_draft rides DECODE.
    so.hidden_channel = (
        HiddenChannelType.PREFILL_1
        if kind == _PREFILL
        else HiddenChannelType.DECODE
    )
    so.num_scheduled_tokens = {req_id: 1}
    so.parent_req_id = req_id
    so.num_accepted_tokens = None
    so.valid_sampled_token_count = None
    so.is_last_prefill_chunk = True
    so.draft_output_req_ids = (req_id,)
    return so


def _make_draft_last(task_id="task-0", req_id="req-0", step=0, kind=_DECODE):
    so = MagicMock()
    so.batch_type = _draft_last_type(kind)
    so.draft_task_id = task_id
    so.draft_step_idx = step
    so.head_token = f"tok-{task_id}-{step}"
    # Phase B: prefill_draft rides the inherited prefill channel;
    # decode_draft rides DECODE.
    so.hidden_channel = (
        HiddenChannelType.PREFILL_1
        if kind == _PREFILL
        else HiddenChannelType.DECODE
    )
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
# Test: draft-domain classification (design §3)                       #
# ------------------------------------------------------------------ #


class TestDomainClassification:
    def _sched(self):
        from vllm_ascend.core.pd_separated_scheduler import (
            PDSeparatedScheduler,
        )

        return PDSeparatedScheduler.__new__(PDSeparatedScheduler)

    def test_parent_tails_classify_their_domain(self):
        s = self._sched()
        assert (
            s._draft_kind_for_batch_type(BatchType.PREFILL_LAST) == _PREFILL
        )
        assert s._draft_kind_for_batch_type(BatchType.DECODE_LAST) == _DECODE

    def test_domain_types_round_trip(self):
        s = self._sched()
        assert (
            s._draft_kind_for_batch_type(BatchType.PREFILL_DRAFT_FIRST)
            == _PREFILL
        )
        assert (
            s._draft_kind_for_batch_type(BatchType.PREFILL_DRAFT_LAST)
            == _PREFILL
        )
        assert (
            s._draft_kind_for_batch_type(BatchType.DECODE_DRAFT_FIRST)
            == _DECODE
        )
        assert (
            s._draft_kind_for_batch_type(BatchType.DECODE_DRAFT_LAST)
            == _DECODE
        )


# ------------------------------------------------------------------ #
# Test: _can_schedule_draft_first honors _force_draft_last (fix ①)   #
# ------------------------------------------------------------------ #


class TestCanScheduleDraftFirstForceGuard:
    """The pre-generated branch must gate on the per-domain _force_draft_last,
    so draft head -> draft tail alternation is guaranteed within each draft
    domain."""

    def _setup(self, pregenerated=True, kind=_DECODE):
        s = _make_bare_scheduler()
        drf = _make_draft_first(kind=kind)
        _first_ready(s, kind).append(drf)
        if pregenerated:
            s._pregenerated_draft_task_ids.add(drf.draft_task_id)
        # Conditions that would otherwise allow scheduling.
        s._force_decode_last = False
        _set_force_last(s, kind, False)
        _set_remote_pending(s, kind, 0)
        s.decode_or_draft_inflight_count = 0
        return s

    def _can_schedule(self, s, kind=_DECODE):
        if kind == _PREFILL:
            return s._can_schedule_prefill_draft_first()
        return s._can_schedule_decode_draft_first()

    def test_preGen_blocked_when_force_draft_last_true(self):
        s = self._setup(pregenerated=True)
        _set_force_last(s, _DECODE, True)
        assert self._can_schedule(s) is False

    def test_preGen_allowed_when_force_draft_last_false(self):
        s = self._setup(pregenerated=True)
        _set_force_last(s, _DECODE, False)
        assert self._can_schedule(s) is True

    def test_preGen_blocked_by_drafts_last_ready(self):
        s = self._setup(pregenerated=True)
        _set_force_last(s, _DECODE, False)
        _last_ready(s, _DECODE).append(_make_draft_last(kind=_DECODE))
        assert self._can_schedule(s) is False

    def test_preGen_blocked_when_decode_head_in_flight(self):
        """Regression for decode_or_draft_inflight=2/1: draft heads and
        DECODE_FIRST use different recv primitives but share the DECODE
        stream, so a draft head must not be dispatched while a DECODE_FIRST
        head is in flight (the cloud's recv order could mismatch the edge's
        send order).  Gate on decode heads, not total heads."""
        s = self._setup(pregenerated=True)
        _set_force_last(s, _DECODE, False)
        s.decode_head_inflight_count = 1  # a DECODE_FIRST in flight
        assert self._can_schedule(s) is False
        s.decode_head_inflight_count = 0
        assert self._can_schedule(s) is True

    def test_preGen_allows_draft_pipeline_while_draft_in_flight(self):
        """The next draft head MAY be dispatched while a previous draft head
        is still in flight (draft pipelining): a draft head is an edge->cloud
        send while a draft tail is a cloud->edge recv (opposite stream
        directions), and draft+draft uses the same recv primitive (FIFO).
        Only a DECODE_FIRST head blocks it, not another draft head."""
        s = self._setup(pregenerated=True)
        _set_force_last(s, _DECODE, False)  # previous draft tail picked
        s.decode_head_inflight_count = 0  # no DECODE_FIRST in flight
        s.decode_or_draft_inflight_count = 1  # a draft head in flight
        _set_remote_pending(s, _DECODE, 1)  # under the pipeline credit (<2)
        assert self._can_schedule(s) is True

    def test_legacy_branch_also_blocked_by_force_draft_last(self):
        """Non-pre-generated branch already had the guard (unchanged)."""
        s = self._setup(pregenerated=False)
        _set_force_last(s, _DECODE, True)
        assert self._can_schedule(s) is False

    def test_domains_gate_only_on_their_own_flag(self):
        """Phase A invariant (design §6.1): prefill_draft and decode_draft
        alternate independently -- one domain's pending tail must not block
        the other domain's head (cross-domain draft+draft uses the same
        stream primitive, FIFO)."""
        s = self._setup(pregenerated=True, kind=_DECODE)
        _set_force_last(s, _DECODE, True)
        # decode head blocked by its own pending tail...
        assert self._can_schedule(s, _DECODE) is False
        # ...while a prefill-domain head is admitted regardless.
        pf = _make_draft_first(kind=_PREFILL)
        s.prefill_drafts_first_ready.append(pf)
        s._pregenerated_draft_task_ids.add(pf.draft_task_id)
        assert self._can_schedule(s, _PREFILL) is True


class TestDraftFirstLastAlternation:
    """End-to-end gate check: a second draft head is blocked while the first
    draft tail is pending, and admitted only after the tail is picked."""

    def test_second_head_blocked_until_tail_picked(self):
        s = _make_bare_scheduler()
        s._pregenerated_draft_task_ids.add("task-0")
        # step-0 head already picked; step-1 is next in decode_drafts_first_ready.
        s.decode_drafts_first_ready.append(_make_draft_first(step=1))
        s._force_decode_last = False
        s.decode_draft_remote_pending_count = 0

        # draft head step-0 in force + its draft tail pending -> step-1 blocked.
        s._force_decode_draft_last = True
        s.decode_drafts_last_ready.append(_make_draft_last(step=0))
        assert s._can_schedule_decode_draft_first() is False

        # draft tail step-0 picked -> flag cleared, no tail pending -> allowed.
        s._force_decode_draft_last = False
        s.decode_drafts_last_ready.clear()
        assert s._can_schedule_decode_draft_first() is True


class TestMidPrefillDraftChain:
    """Every chunk warms MTP KV, but only the last chunk may seed verify."""

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
        request = _make_live_request()
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
        request = _make_live_request()
        s.requests["req-0"] = request
        tail = _make_draft_last(kind=_PREFILL)
        tail.is_last_prefill_chunk = False
        tail.draft_output_req_ids = ()
        s.prefill_drafts_last_ready.append(tail)
        s._force_prefill_draft_last = True
        s._validate_draft_tail_channel = MagicMock()
        s._start_decode_or_draft_first_only_window = MagicMock()
        s._prepare_next_decode_first_placeholder = MagicMock()

        assert s._pick_prefill_draft_last_batch() is tail
        s._prepare_next_decode_first_placeholder.assert_not_called()

    def test_engine_advances_mid_prefill_draft(self):
        from vllm_ascend.patch.platform.patch_engine_core import (
            _advance_edge_cloud_draft,
        )

        engine = MagicMock()
        engine.use_spec_decode = True
        finalized = _make_real_output(BatchType.PREFILL_DRAFT_FIRST)
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
    def _setup(self, req_present=True, req_id="req-0", req_finished=False):
        s = _make_bare_scheduler()
        if req_present:
            req = MagicMock()
            req.is_finished.return_value = req_finished
            s.requests[req_id] = req
        so = _make_draft_last(req_id=req_id)
        return s, so

    def test_live_request_reqs_live_true(self):
        s, so = self._setup(req_present=True, req_finished=False)
        assert s._draft_output_reqs_live(so) is True

    def test_finished_request_reqs_live_false(self):
        s, so = self._setup(req_present=True, req_finished=True)
        assert s._draft_output_reqs_live(so) is False

    def test_dead_request_reqs_live_false(self):
        s, so = self._setup(req_present=False)
        assert s._draft_output_reqs_live(so) is False

    def test_live_request_not_stale(self):
        s, so = self._setup(req_present=True, req_finished=False)
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
# Test: _pick_draft_last_batch drains instead of dropping (fix ②a)   #
# ------------------------------------------------------------------ #


class TestPickDraftLastBatchDrain:
    """A draft tail in the domain last queue always has its draft head
    already dispatched to the cloud, so the cloud will isend a response --
    the edge must execute (drain) the tail to pair it, never drop it."""

    def _setup(self, req_present=True, kind=_DECODE, req_finished=False):
        s = _make_bare_scheduler()
        if req_present:
            req = MagicMock()
            req.is_finished.return_value = req_finished
            s.requests["req-0"] = req
        _last_ready(s, kind).append(_make_draft_last(kind=kind))
        _set_force_last(s, kind, True)
        _set_remote_pending(s, kind, 1)
        # Stub side-effecting helpers to isolate the drain decision.
        s._validate_draft_tail_channel = MagicMock()
        s._start_decode_or_draft_first_only_window = MagicMock()
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
        # _force_draft_last is always reset now (the old stale-drop skipped it).
        assert s._force_decode_draft_last is False
        # The decrement moved to update_from_output; _pick_draft_last_batch no
        # longer decrements (the old stale-drop did).
        assert s.decode_draft_remote_pending_count == before
        # No verify placeholder for a gone request.
        s._prepare_next_decode_first_placeholder.assert_not_called()
        s._validate_draft_tail_channel.assert_called_once()

    def test_live_request_prepares_placeholder(self):
        s = self._setup(req_present=True, req_finished=False)
        result = s._pick_decode_draft_last_batch()
        assert result.batch_type == BatchType.DECODE_DRAFT_LAST
        assert s._force_decode_draft_last is False
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
    draft head was dispatched), the tail segment must drain (the recv in
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

    def test_drains_when_task_id_none(self):
        from vllm.v1.outputs import ModelRunnerOutput

        runner = self._make_runner(context_present=False)
        result = runner._run_edge_cloud_draft_last_segment(
            self._make_so(task_id=None), MagicMock()
        )
        assert isinstance(result, ModelRunnerOutput)
        assert result.req_ids == ["req-0"]

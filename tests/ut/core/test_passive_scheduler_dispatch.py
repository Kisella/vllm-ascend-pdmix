# SPDX-License-Identifier: Apache-2.0

from collections import deque
from types import SimpleNamespace

from vllm.v1.core.sched.output import BatchType
from vllm_ascend.core.passive_scheduler import (
    CloudSchedulingState,
    PassiveScheduler,
)


def _make_scheduler_for_dispatch_test():
    scheduler = PassiveScheduler.__new__(PassiveScheduler)
    scheduler.cloud_scheduling_state = CloudSchedulingState.EXPECT_EXECUTE_PREFILL
    scheduler.ready_prefills = deque()
    scheduler.ready_pdmixes = deque()
    scheduler.ready_decodes = deque()
    scheduler._active_sliced_prefill = None
    scheduler._active_prefill_slices = deque()
    scheduler._prefill_middle_throttle_started_at = None
    scheduler._prefill_middle_throttle_seconds = 0.010
    scheduler._num_local_layers = 0
    scheduler._layer_slice_config = None
    scheduler._layer_slice_config_mtime = 0.0
    scheduler._layer_slice_config_path = None
    return scheduler


def _scheduler_output(batch_type: BatchType):
    return SimpleNamespace(
        batch_type=batch_type,
        total_num_scheduled_tokens=1,
    )


def test_schedule_uses_expect_alternation_without_dispatch_policy_attribute():
    scheduler = _make_scheduler_for_dispatch_test()
    scheduler.ready_prefills.append(_scheduler_output(BatchType.PREFILL_FIRST))
    scheduler.ready_decodes.append(_scheduler_output(BatchType.DECODE_FIRST))

    first = scheduler.schedule()
    second = scheduler.schedule()

    assert first.scheduler_output.batch_type == BatchType.PREFILL_FIRST
    assert second.scheduler_output.batch_type == BatchType.DECODE_FIRST

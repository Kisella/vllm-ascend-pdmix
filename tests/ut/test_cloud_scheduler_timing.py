# SPDX-License-Identifier: Apache-2.0
"""Unit tests for edge-cloud scheduler timing helpers."""

from types import SimpleNamespace
from unittest.mock import patch

from vllm_ascend.v1.engine.passive_core import PPSchedulerZmqSubscriber


def test_mark_cloud_zmq_recv_time_sets_perf_counter_value():
    scheduler_output = SimpleNamespace()

    with patch(
        "vllm_ascend.v1.engine.passive_core.time.perf_counter",
        return_value=123.456,
    ):
        PPSchedulerZmqSubscriber._mark_cloud_zmq_recv_time(scheduler_output)

    assert scheduler_output.cloud_zmq_recv_time == 123.456

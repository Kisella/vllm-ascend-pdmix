# SPDX-License-Identifier: Apache-2.0

from vllm_ascend.pd_separation_config import PDSeparationConfig


def test_pd_separation_config_ignores_passive_dispatch_policy_env(monkeypatch):
    monkeypatch.setenv("VLLM_PP_PASSIVE_DISPATCH_POLICY", "decode_first")

    config = PDSeparationConfig.from_env()

    assert not hasattr(config, "dispatch_policy")


def test_pd_separation_config_still_reads_zmq_ports(monkeypatch):
    monkeypatch.setenv("VLLM_PP_PRE_OUT_ZMQ_PORT", "6008")
    monkeypatch.setenv("VLLM_PP_POST_OUT_ZMQ_PORT", "6009")

    config = PDSeparationConfig.from_env()

    assert config.pre_out_port == 6008
    assert config.post_out_port == 6009
    assert config.get_pre_out_bind_addr() == "tcp://*:6008"
    assert config.get_post_out_bind_addr() == "tcp://*:6009"
    assert config.get_pre_out_connect_addr("10.0.0.1") == "tcp://10.0.0.1:6008"
    assert config.get_post_out_connect_addr("10.0.0.2") == "tcp://10.0.0.2:6009"

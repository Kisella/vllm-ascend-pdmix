# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project

from __future__ import annotations

from typing import TYPE_CHECKING

from vllm.config import VllmConfig
from vllm.compilation.cuda_graph import CUDAGraphOptions
from vllm.config import CUDAGraphMode

from vllm_ascend.compilation.acl_graph import (
    ACLGraphWrapper,
    GraphParams,
    make_graph_params,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


# ============================================================
#  边云分段 ACLGraphWrapper
#  —— 继承标准 ACLGraphWrapper，由父类 __call__ 中的
#     graph_params_scope 激活本 segment 独立 GraphParams。
# ============================================================

class EdgeCloudACLGraphWrapper(ACLGraphWrapper):
    """边云分段 ACL 图包装器。

    每个 segment wrapper 持有独立的 GraphParams。父类
    ACLGraphWrapper.__call__ 会在 capture/replay 期间通过
    acl_graph.graph_params_scope 激活这些参数，避免 segment_a /
    segment_e / segment_c 的 task handle / event / attn_params 混入
    同一全局列表。
    """

    def __init__(
        self,
        runnable: Callable,
        vllm_config: VllmConfig,
        runtime_mode: CUDAGraphMode,
        cudagraph_options: CUDAGraphOptions | None = None,
        *,
        use_eagle: bool = False,
        enable_enpu: bool = False,
    ):
        super().__init__(
            runnable, vllm_config, runtime_mode, cudagraph_options,
            use_eagle=use_eagle, enable_enpu=enable_enpu,
        )
        # 每个 segment wrapper 持有独立的 GraphParams，
        # 避免 segment_a / segment_e / segment_c 的
        # task handle / event / attn_params 混入同一全局列表
        self.graph_params: GraphParams | None = None
        self.draft_graph_params: GraphParams | None = None


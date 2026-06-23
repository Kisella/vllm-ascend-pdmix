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

_ASCEND_PASSIVE_ENGINE_CORE_ATTR = "_ascend_is_non_leader_passive_engine_core"


def mark_ascend_non_leader_passive_engine_core(vllm_config) -> None:
    setattr(vllm_config, _ASCEND_PASSIVE_ENGINE_CORE_ATTR, True)


def is_ascend_non_leader_passive_engine_core(vllm_config) -> bool:
    return bool(getattr(vllm_config, _ASCEND_PASSIVE_ENGINE_CORE_ATTR, False))

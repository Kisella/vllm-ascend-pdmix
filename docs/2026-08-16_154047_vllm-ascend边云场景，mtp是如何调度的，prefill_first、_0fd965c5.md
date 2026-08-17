# Claude Code Session

> **Resume in CLI:** `claude --resume 0fd965c5-f091-41ab-b346-446569638fa9`

| Field | Value |
|---|---|
| **Project** | `c:\kisella-mtp` |
| **Session ID** | `0fd965c5-f091-41ab-b346-446569638fa9` |
| **Working Dir** | `c:\kisella_mtp` |
| **Started** | 2026/8/14 16:50:14 |
| **Last Updated** | 2026/8/17 09:17:36 |
| **Messages** | 766 |

---

## User <sup>2026/8/14 16:50:14</sup>

vllm-ascend边云场景，mtp是如何调度的，prefill_first、prefill_last、decode_first、decode_last、mtp prefill_first，mtp prefill_last、mtp decode_first、mtp decode_last


---

## Assistant <sup>2026/8/14 16:50:18</sup>


---

## Assistant <sup>2026/8/14 16:50:18</sup>

我将探索代码库，以了解 vllm-ascend 中 MTP 在边云场景下的调度方式。


---

## Assistant <sup>2026/8/14 16:50:19</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "ls c:/vllm_gitcode_new 2>/dev/null | head -50; echo \"---\"; ls c:/kisella_mtp 2>/dev/null | head -50",
  "description": "List contents of working directories"
}
```

</details>


---

## User <sup>2026/8/14 16:50:26</sup>

<details>
<summary>Tool Result</summary>

```
vllm
vllm-ascend
---
vllm-ascend-pdmix
vllm-pdmix
```

</details>


---

## Assistant <sup>2026/8/14 16:50:28</sup>


---

## Assistant <sup>2026/8/14 16:50:29</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "echo \"=== vllm-ascend-pdmix ===\"; ls c:/kisella_mtp/vllm-ascend-pdmix 2>/dev/null; echo \"=== vllm-pdmix ===\"; ls c:/kisella_mtp/vllm-pdmix 2>/dev/null; echo \"=== vllm-ascend (gitcode) ===\"; ls c:/vllm_gitcode_new/vllm-ascend 2>/dev/null; echo \"=== vllm (gitcode) ===\"; ls c:/vllm_gitcode_new/vllm 2>/dev/null | head -30",
  "description": "Explore directory structures"
}
```

</details>


---

## User <sup>2026/8/14 16:50:31</sup>

<details>
<summary>Tool Result</summary>

```
=== vllm-ascend-pdmix ===
AGENTS.md
CLAUDE.md
CMakeLists.txt
CODE_OF_CONDUCT.md
CONTRIBUTING.md
DCO
Dockerfile
Dockerfile.310p
Dockerfile.310p.openEuler
Dockerfile.a3
Dockerfile.a3.openEuler
Dockerfile.a5
Dockerfile.a5.openEuler
Dockerfile.openEuler
LICENSE
README.md
README.zh.md
benchmarks
cmake
codecov.yml
collect_env.py
csrc
docs
examples
format.sh
mypy.ini
packages.txt
pyproject.toml
requirements-dev.txt
requirements-lint.txt
requirements.txt
setup.py
tests
tools
typos.toml
vllm_ascend
=== vllm-pdmix ===
AGENTS.md
CLAUDE.md
CMakeLists.txt
CODE_OF_CONDUCT.md
CONTRIBUTING.md
DCO
LICENSE
MANIFEST.in
README.md
RELEASE.md
SECURITY.md
benchmarks
build_rust.sh
cmake
codecov.yml
csrc
docker
docs
examples
mkdocs.yaml
pyproject.toml
requirements
rust
rust-toolchain.toml
scripts
setup.py
tests
tools
use_existing_torch.py
vllm
=== vllm-ascend (gitcode) ===
AGENTS.md
CLAUDE.md
CMakeLists.txt
CODE_OF_CONDUCT.md
CONTRIBUTING.md
DCO
Dockerfile
Dockerfile.310p
Dockerfile.310p.openEuler
Dockerfile.a
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:50:35</sup>


---

## Assistant <sup>2026/8/14 16:50:35</sup>

我来搜索一下这些调度相关的术语，并了解其架构。


---

## Assistant <sup>2026/8/14 16:50:36</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "head_limit": 50,
  "output_mode": "files_with_matches",
  "path": "c:/kisella_mtp",
  "pattern": "prefill_first|prefill_last|decode_first|decode_last"
}
```

</details>


---

## User <sup>2026/8/14 16:50:36</sup>

<details>
<summary>Tool Result</summary>

```
Found 16 files
vllm-pdmix\vllm\v1\core\sched\output.py
vllm-pdmix\vllm\config\scheduler.py
vllm-pdmix\tests\v1\core\utils.py
vllm-pdmix\docs\hidden_channel_call_flow_extended.md
vllm-ascend-pdmix\vllm_ascend\worker\model_runner_v1.py
vllm-ascend-pdmix\vllm_ascend\worker\pcp_utils.py
vllm-ascend-pdmix\vllm_ascend\worker\edge_cloud\batched_model_runner.py
vllm-ascend-pdmix\vllm_ascend\spec_decode\llm_base_proposer.py
vllm-ascend-pdmix\vllm_ascend\pd_separation_config.py
vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py
vllm-ascend-pdmix\vllm_ascend\core\layer_slice_config.yaml
vllm-ascend-pdmix\vllm_ascend\core\passive_scheduler.py
vllm-ascend-pdmix\tests\ut\test_pd_draft_drain.py
vllm-ascend-pdmix\tests\ut\test_pd_chunk_prefill_prior.py
vllm-ascend-pdmix\tests\ut\spec_decode\a2\test_eagle_proposer.py
vllm-pdmix\docs\hidden_channel_call_flow_original.md
```

</details>


---

## Assistant <sup>2026/8/14 16:50:36</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "head_limit": 50,
  "output_mode": "files_with_matches",
  "path": "c:/kisella_mtp",
  "pattern": "mtp.*prefill|mtp.*decode|prefill.*mtp|decode.*mtp"
}
```

</details>


---

## User <sup>2026/8/14 16:50:36</sup>

<details>
<summary>Tool Result</summary>

```
Found 29 files
vllm-pdmix\vllm\v1\worker\gpu\spec_decode\__init__.py
vllm-pdmix\tests\distributed\test_eplb_spec_decode.py
vllm-pdmix\.buildkite\test_areas\spec_decode.yaml
vllm-pdmix\.buildkite\test_areas\model_runner_v2.yaml
vllm-pdmix\.buildkite\test-amd.yaml
vllm-ascend-pdmix\vllm_ascend\worker\model_runner_v1.py
vllm-ascend-pdmix\vllm_ascend\worker\pcp_utils.py
vllm-ascend-pdmix\vllm_ascend\spec_decode\llm_base_proposer.py
vllm-ascend-pdmix\vllm_ascend\quantization\modelslim_config.py
vllm-ascend-pdmix\vllm_ascend\ops\triton\fla\chunk.py
vllm-ascend-pdmix\vllm_ascend\attention\context_parallel\mla_cp.py
vllm-ascend-pdmix\vllm_ascend\attention\context_parallel\attention_cp.py
vllm-ascend-pdmix\tests\ut\test_platform.py
vllm-ascend-pdmix\tests\ut\kv_offload\test_mooncake_connector.py
vllm-ascend-pdmix\tests\ut\attention\a2\test_sfa_cp_precision.py
vllm-ascend-pdmix\tests\ut\attention\a2\test_mla_cp_precision.py
vllm-ascend-pdmix\tests\ut\attention\a2\test_attention_cp_precision.py
v
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:50:40</sup>


---

## Assistant <sup>2026/8/14 16:50:41</sup>

`vllm-*-pdmix` 目录是相关的（PDMIX = 边云分离）。让我派遣并行 agent 去探索关键文件。


---

## Assistant <sup>2026/8/14 16:50:48</sup>

<details>
<summary>Tool: <code>Agent</code></summary>

```json
{
  "description": "Explore edge-cloud MTP scheduling",
  "prompt": "I'm investigating how MTP (Multi-Token Prediction) is scheduled in vllm-ascend edge-cloud (边云) scenarios. The codebase is at c:\\kisella_mtp\\vllm-ascend-pdmix and c:\\kisella_mtp\\vllm-pdmix.\n\nThe user is asking specifically about these scheduling policies/terms:\n- prefill_first, prefill_last, decode_first, decode_last\n- mtp prefill_first, mtp prefill_last, mtp decode_first, mtp decode_last\n\nPlease thoroughly explore these files and any related ones:\n1. c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\edge_cloud\\batched_model_runner.py\n2. c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\edge_cloud\\ (whole directory - list and read all files)\n3. c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\pcp_utils.py\n4. c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\pd_separation_config.py\n5. c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py\n6. c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\passive_scheduler.py\n7. c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\layer_slice_config.yaml\n8. c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\spec_decode\\llm_base_proposer.py\n\nI need to understand:\n- What is the edge-cloud (边云) architecture in this pdmix codebase? What are the roles (active/passive, prefill/decode instances)?\n- How are these scheduling policies defined and selected? Search for the exact strings \"prefill_first\", \"prefill_last\", \"decode_first\", \"decode_last\" and their mtp variants.\n- How does MTP interact with these scheduling policies? What does \"mtp prefill_first\" etc. mean concretely?\n- What is PCP (look at pcp_utils.py)?\n- What is the relationship between edge and cloud instances?\n\nRead the files thoroughly and report back with:\n- The exact definitions/enums of these scheduling policies (with file:line references)\n- The logic that selects/uses each policy\n- How MTP slots/tokens are schedul
...(truncated)
```

</details>


---

## User <sup>2026/8/14 16:50:48</sup>

<details>
<summary>Tool Result</summary>

```
Async agent launched successfully. (This tool result is internal metadata — never quote or paste any part of it, including the agentId below, into a user-facing reply.)
agentId: a2be6cf1848833fed (internal ID - do not mention to user. Use SendMessage with to: 'a2be6cf1848833fed', summary: '<5-10 word recap>' to continue this agent.)
The agent is working in the background. You will be notified automatically when it completes. You know nothing about its results until that notification arrives — do not report, assume, or predict them; continue other work or respond to the user in the meantime.
Do not duplicate this agent's work — avoid working with the same files or topics it is using.
output_file: C:\Users\root\AppData\Local\Temp\claude\c--kisella-mtp\0fd965c5-f091-41ab-b346-446569638fa9\tasks\a2be6cf1848833fed.output
Do NOT Read or tail this file via the shell tool — it is the full subagent JSONL transcript and reading it will overflow your context. If the user asks for progress, say th
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:50:55</sup>

<details>
<summary>Tool: <code>Agent</code></summary>

```json
{
  "description": "Explore scheduler config & docs",
  "prompt": "I'm investigating how MTP (Multi-Token Prediction) is scheduled in vllm-ascend edge-cloud (边云) scenarios. The codebase is at c:\\kisella_mtp\\vllm-ascend-pdmix and c:\\kisella_mtp\\vllm-pdmix.\n\nThe user is asking specifically about these scheduling policies/terms:\n- prefill_first, prefill_last, decode_first, decode_last\n- mtp prefill_first, mtp prefill_last, mtp decode_first, mtp decode_last\n\nPlease thoroughly explore these files and any related ones:\n1. c:\\kisella_mtp\\vllm-pdmix\\vllm\\config\\scheduler.py - search for the scheduling policy definitions\n2. c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\core\\sched\\output.py\n3. c:\\kisella_mtp\\vllm-ascend-pdmix\\tests\\ut\\test_pd_draft_drain.py\n4. c:\\kisella_mtp\\vllm-ascend-pdmix\\tests\\ut\\test_pd_chunk_prefill_prior.py\n5. c:\\kisella_mtp\\vllm-pdmix\\docs\\hidden_channel_call_flow_extended.md\n6. c:\\kisella_mtp\\vllm-pdmix\\docs\\hidden_channel_call_flow_original.md\n7. c:\\kisella_mtp\\vllm-ascend-pdmix\\docs\\ (list the docs directory and find any edge-cloud / pd-separation / mtp related docs)\n\nAlso do a broad search across c:\\kisella_mtp for these exact enum-like strings to find where these policies are defined as enums or config options:\n- \"prefill_first\" \n- \"prefill_last\"\n- \"decode_first\"\n- \"decode_last\"\n- grep for class/enum definitions containing these, e.g. \"Enum\" near these terms, or \"prior\" / \"priority\" / \"policy\"\n\nI need to understand:\n- Where are these scheduling policies (prefill_first, prefill_last, decode_first, decode_last, and their mtp variants) defined as config options or enums?\n- What does each one mean / how is it documented?\n- How is the MTP variant different from the non-MTP variant?\n- What does the test_pd_chunk_prefill_prior test reveal about the priority logic?\n\nRead the files thoroughly and report back with exact definitions (file:line references), docstrings, and the meaning of
...(truncated)
```

</details>


---

## User <sup>2026/8/14 16:50:55</sup>

<details>
<summary>Tool Result</summary>

```
Async agent launched successfully. (This tool result is internal metadata — never quote or paste any part of it, including the agentId below, into a user-facing reply.)
agentId: a58465f5f1be22fd1 (internal ID - do not mention to user. Use SendMessage with to: 'a58465f5f1be22fd1', summary: '<5-10 word recap>' to continue this agent.)
The agent is working in the background. You will be notified automatically when it completes. You know nothing about its results until that notification arrives — do not report, assume, or predict them; continue other work or respond to the user in the meantime.
Do not duplicate this agent's work — avoid working with the same files or topics it is using.
output_file: C:\Users\root\AppData\Local\Temp\claude\c--kisella-mtp\0fd965c5-f091-41ab-b346-446569638fa9\tasks\a58465f5f1be22fd1.output
Do NOT Read or tail this file via the shell tool — it is the full subagent JSONL transcript and reading it will overflow your context. If the user asks for progress, say th
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:51:01</sup>


---

## Assistant <sup>2026/8/14 16:51:01</sup>

在智能体进行深度挖掘的同时，我先读取一下项目概览文件，以获取高层级的上下文信息。


---

## Assistant <sup>2026/8/14 16:51:02</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\CLAUDE.md"
}
```

</details>


---

## User <sup>2026/8/14 16:51:02</sup>

<details>
<summary>Tool Result</summary>

```
1	IMPORTANT: Ensure you've thoroughly reviewed the [AGENTS.md](AGENTS.md) file before beginning any work.
2
```

</details>


---

## Assistant <sup>2026/8/14 16:51:02</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\CLAUDE.md"
}
```

</details>


---

## User <sup>2026/8/14 16:51:02</sup>

<details>
<summary>Tool Result</summary>

```
1	@AGENTS.md
2
```

</details>


---

## Assistant <sup>2026/8/14 16:51:03</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\AGENTS.md"
}
```

</details>


---

## User <sup>2026/8/14 16:51:03</sup>

<details>
<summary>Tool Result</summary>

```
1	# vLLM Ascend Development Guidelines
2	
3	This document provides instructions for contributors to the vLLM Ascend project. Please read and follow these guidelines to ensure code quality, maintainability, and consistency.
4	
5	---
6	
7	## Table of Contents
8	
9	- [Setup and Environment](#setup-and-environment)
10	    - [Environment Variables](#environment-variables)
11	    - [Environment Variable Review Requirement](#environment-variable-review-requirement)
12	- [Testing](#testing)
13	    - [Unit and System Tests](#unit-and-system-tests)
14	    - [Running Tests](#running-tests)
15	- [Code Style](#code-style)
16	    - [Python Conventions](#python-conventions)
17	    - [Naming Conventions](#naming-conventions)
18	- [NPU-Specific Considerations](#npu-specific-considerations)
19	    - [Tensor item() Operations](#tensor-item-operations)
20	    - [Memory and Performance](#memory-and-performance)
21	- [Model and Plugin Architecture](#model-and-plugin-architecture)
22	    - [vLLM Ascend Plugi
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:51:10</sup>


---

## Assistant <sup>2026/8/14 16:51:10</sup>

我先执行针对性的搜索以补充 Agent 的分析，同时查找这些策略字符串的定义位置以及任何相关文档。


---

## Assistant <sup>2026/8/14 16:51:10</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 80,
  "output_mode": "content",
  "path": "c:/kisella_mtp",
  "pattern": "(prefill_first|prefill_last|decode_first|decode_last)"
}
```

</details>


---

## User <sup>2026/8/14 16:51:11</sup>

<details>
<summary>Tool Result</summary>

```
vllm-ascend-pdmix\vllm_ascend\worker\pcp_utils.py:1110:    def prepare_spec_decode_first_pass_inputs(
vllm-ascend-pdmix\vllm_ascend\worker\model_runner_v1.py:2969:                # prefill_last_pending -> running migration gap) returns to
vllm-ascend-pdmix\vllm_ascend\worker\edge_cloud\batched_model_runner.py:1365:    def _apply_decode_first_reorder(
vllm-ascend-pdmix\vllm_ascend\worker\edge_cloud\batched_model_runner.py:1811:        # ``_apply_decode_first_reorder`` short-circuits in
vllm-ascend-pdmix\vllm_ascend\worker\edge_cloud\batched_model_runner.py:1818:            "calling _apply_decode_first_reorder "
vllm-ascend-pdmix\vllm_ascend\worker\edge_cloud\batched_model_runner.py:1833:        ) = self._apply_decode_first_reorder(
vllm-ascend-pdmix\vllm_ascend\spec_decode\llm_base_proposer.py:1494:                first_pass_inputs = pcp_manager.prepare_spec_decode_first_pass_inputs(
vllm-pdmix\vllm\config\scheduler.py:158:    pd_scheduling_policy: Literal["prefill_first", "decode_first
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:51:12</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "echo \"=== edge_cloud dir ===\"; ls -la c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/worker/edge_cloud/ 2>/dev/null; echo \"=== docs source ===\"; ls c:/kisella_mtp/vllm-ascend-pdmix/docs/source/ 2>/dev/null; echo \"=== find pd/edge/mtp docs ===\"; find c:/kisella_mtp/vllm-ascend-pdmix/docs -type f -iname \"*.md\" 2>/dev/null | grep -iE \"edge|pd|separat|mtp|cloud|disagg\" | head -40",
  "description": "List edge_cloud dir and find related docs"
}
```

</details>


---

## User <sup>2026/8/14 16:51:14</sup>

<details>
<summary>Tool Result</summary>

```
=== edge_cloud dir ===
total 201
drwxr-xr-x 1 root 197121      0 Aug 14 16:47 .
drwxr-xr-x 1 root 197121      0 Aug 14 16:47 ..
-rw-r--r-- 1 root 197121    382 Aug  7 16:59 __init__.py
-rw-r--r-- 1 root 197121 119308 Aug 14 16:47 batched_model_runner.py
-rw-r--r-- 1 root 197121  11692 Aug 14 16:47 execute_model_bundle.py
-rw-r--r-- 1 root 197121  59807 Aug 14 16:47 shared_model_edge_worker.py
=== docs source ===
_templates
assets
community
conf.py
developer_guide
faqs.md
index.md
installation.md
llms.txt
locale
logos
quick_start.md
tutorials
user_guide
=== find pd/edge/mtp docs ===
c:/kisella_mtp/vllm-ascend-pdmix/docs/README.md
c:/kisella_mtp/vllm-ascend-pdmix/docs/source/community/contributors.md
c:/kisella_mtp/vllm-ascend-pdmix/docs/source/community/governance.md
c:/kisella_mtp/vllm-ascend-pdmix/docs/source/community/issue-workflow-guidelines.md
c:/kisella_mtp/vllm-ascend-pdmix/docs/source/community/slash-commands.md
c:/kisella_mtp/vllm-ascend-pdmix/docs/source/community/user_storie
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:51:22</sup>


---

## Assistant <sup>2026/8/14 16:51:23</sup>

在 [output.py](vllm-pdmix/vllm/v1/core/sched/output.py) 中找到了策略枚举。现在让我专门搜索一下 MTP 变体，并阅读设计文档。


---

## Assistant <sup>2026/8/14 16:51:23</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\core\\sched\\output.py",
  "limit": 120,
  "offset": 100
}
```

</details>


---

## User <sup>2026/8/14 16:51:23</sup>

<details>
<summary>Tool Result</summary>

```
100	def _hidden_channel_from_value(value: str) -> HiddenChannelType:
101	    """Return a hidden-channel instance during pickle deserialization."""
102	    return HiddenChannelType(value)
103	
104	
105	class BatchType(enum.Enum):
106	    """Composition of a single SchedulerOutput batch.
107	
108	    Tagged by the producing scheduler so that the non-leader PP rank's
109	    PassiveScheduler can route the batch without re-inspecting per-request
110	    state.
111	
112	    - PD_MIX:        prefill and decode requests in the same batch (default
113	                     for the legacy mixed scheduler)
114	    - PURE_PREFILL:  every scheduled request is in its prefill phase
115	                     (legacy PP / PDmix mode)
116	    - PURE_DECODE:   every scheduled request is in its decode phase
117	                     (legacy PP / PDmix mode)
118	    - EMPTY:         no tokens scheduled this step (sync-only batch, e.g.
119	                     propagating finished_req_ids)
120	    - PREFILL_F
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:51:24</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-i": true,
  "-n": true,
  "head_limit": 60,
  "output_mode": "content",
  "path": "c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py",
  "pattern": "mtp|draft|spec_decode|num_spec"
}
```

</details>


---

## User <sup>2026/8/14 16:51:24</sup>

<details>
<summary>Tool Result</summary>

```
83:    BatchType.PREFILL_DRAFT_FIRST: BatchType.PREFILL_DRAFT_LAST,
84:    BatchType.DECODE_DRAFT_FIRST: BatchType.DECODE_DRAFT_LAST,
230:        # 4 域拆分（设计 §3.2）：prefill_draft 链与 decode_draft 链的就绪
232:        self.prefill_drafts_first_ready: deque[SchedulerOutput] = deque()
233:        self.prefill_drafts_last_ready: deque[SchedulerOutput] = deque()
234:        self.decode_drafts_first_ready: deque[SchedulerOutput] = deque()
235:        self.decode_drafts_last_ready: deque[SchedulerOutput] = deque()
245:        self.decode_or_draft_inflight_limit: int = 1
246:        self.decode_or_draft_inflight_count: int = 0
248:        # DECODE_DRAFT_FIRST and DECODE_FIRST use different recv primitives
251:        # send order).  DECODE_DRAFT_FIRST+DECODE_DRAFT_FIRST is safe (same
252:        # primitive, FIFO), so draft pipelining only needs to gate on decode
255:        # 4 域拆分（设计 §5.4）：prefill_draft 与 decode_draft 各自计数、
256:        # 各自限额，互不影响。Phase A 中 prefill_draft 仍走 DECODE 通道，
257:        #
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:51:37</sup>


---

## Assistant <sup>2026/8/14 16:51:38</sup>

这8种 batch types 已在 `BatchType` 枚举中明确定义。所谓 "mtp" 变体，即 `*_DRAFT_*` 的 batch types。我来阅读一下 disaggregated prefill 设计文档，以了解 edge-cloud 架构（segments, phases）。


---

## Assistant <sup>2026/8/14 16:51:38</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\docs\\source\\developer_guide\\Design_Documents\\disaggregated_prefill.md"
}
```

</details>


---

## User <sup>2026/8/14 16:51:38</sup>

<details>
<summary>Tool Result</summary>

```
1	# Disaggregated-prefill
2	
3	## Why disaggregated-prefill?
4	
5	This feature addresses the need to optimize the **Time Per Output Token (TPOT)** and **Time To First Token (TTFT)** in large-scale inference tasks. The motivation is two-fold:
6	
7	1. **Adjusting Parallel Strategy and Instance Count for P and D Nodes**  
8	   Using the disaggregated-prefill strategy, this feature allows the system to flexibly adjust the parallelization strategy (e.g., data parallelism (dp), tensor parallelism (tp), and expert parallelism (ep)) and the instance count for both P (Prefiller) and D (Decoder) nodes. This leads to better system performance tuning, particularly for **TTFT** and **TPOT**.
9	
10	2. **Optimizing TPOT**
11	   Without the disaggregated-prefill strategy, prefill tasks are inserted during decoding, which results in inefficiencies and delays. Disaggregated-prefill solves this by allowing for better control over the system's **TPOT**. By managing chunked prefill tasks effectively, the s
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:51:45</sup>


---

## Assistant <sup>2026/8/14 16:51:45</sup>

让我先阅读一下动态分块流水线并行（dynamic chunked pipeline parallel）的设计文档——这很可能是边云（edge-cloud）切片架构的基础。


---

## Assistant <sup>2026/8/14 16:51:45</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\docs\\source\\developer_guide\\Design_Documents\\dynamic_chunked_pipeline_parallel.md"
}
```

</details>


---

## User <sup>2026/8/14 16:51:45</sup>

<details>
<summary>Tool Result</summary>

```
1	# Dynamic Chunked Pipeline Parallel (CPP)
2	
3	TL;DR CPP uses profiling-based dynamic chunking to equalize per-chunk latency and eliminate pipeline bubbles in PP scenarios.
4	
5	## Background
6	
7	### Problem Statement
8	
9	In Pipeline Parallelism (PP) + Chunked Prefill scenarios, long sequences are split into fixed-size chunks that pass through the pipeline sequentially. Due to the O(n²) computational complexity of Self-Attention, **chunks of the same size take increasingly longer to process as the prefix sequence grows**:
10	
11	```text
12	Chunk 1 (history=0):     ██████         → Time T1
13	Chunk 2 (history=4K):    ████████       → Time T2 > T1
14	Chunk 3 (history=8K):    ██████████     → Time T3 > T2
15	Chunk 4 (history=12K):   ████████████   → Time T4 > T3
16	```
17	
18	This time variance propagates across pipeline stages, causing increased idle waiting (Pipeline Bubble) and significantly reducing GPU utilization.
19	
20	### Solution Overview
21	
22	Dynamic Chunked Pipeline Para
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:51:51</sup>


---

## Assistant <sup>2026/8/14 16:51:51</sup>

让我搜索一下是否有具体的“边云”（edge-cloud）或“layer-slice”）设计文档，以及“调度策略”（scheduling policies）的配置选项是如何定义的。


---

## Assistant <sup>2026/8/14 16:51:53</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "cd c:/kisella_mtp && grep -rIl --include=\"*.md\" -iE \"边云|edge.?cloud|layer.?slice|pdmix|segment_a|segment_e|edge.*head|edge.*tail\" . 2>/dev/null | head -30; echo \"=== layer_slice_config.yaml ===\"; cat c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/core/layer_slice_config.yaml 2>/dev/null | head -80",
  "description": "Find edge-cloud design docs and read layer slice config"
}
```

</details>


---

## User <sup>2026/8/14 16:51:54</sup>

<details>
<summary>Tool Result</summary>

```
./vllm-ascend-pdmix/docs/source/user_guide/feature_guide/kv_pool.md
./vllm-pdmix/docs/contributing/editing-agent-instructions.md
./vllm-pdmix/docs/execute_model_batched_pre_call_flow.md
./vllm-pdmix/docs/hidden_channel_call_flow_extended.md
./vllm-pdmix/docs/hidden_channel_call_flow_original.md
./vllm-pdmix/docs/hidden_channel_dp_extension.md
./vllm-pdmix/docs/pd_separation_modification_plan.md
./vllm-pdmix/docs/single_card_multi_dp_pd_separation_analysis.md
=== layer_slice_config.yaml ===
# Layer-slice dynamic configuration for cloud-side PassiveScheduler.
#
# Format:
#   <token_threshold_k>: <total_slice_count>
#
# The key is the prefill batch size in *thousands* of tokens.
# The value is the total number of layer slices for that batch.
#
# Matching rule (largest-threshold-first):
#   total_num_scheduled_tokens >= key * 1000  ->  use value
#
# Example: a 62-layer model (after removing head/tail) with the config below:
#   - 16k tokens -> 5 slices -> ~13 layers per slice
#   - 8k  tok
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:52:02</sup>


---

## Assistant <sup>2026/8/14 16:52:02</sup>

我来阅读一下 PD 分离修改计划，该计划很可能记录了调度策略的设计。


---

## Assistant <sup>2026/8/14 16:52:02</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\docs\\pd_separation_modification_plan.md"
}
```

</details>


---

## User <sup>2026/8/14 16:52:02</sup>

<details>
<summary>Tool Result</summary>

```
1	# 单卡多 DP 非MoE 适配 PD 分离调度框架 — 修改分析
2	
3	> 基于 [`SharedModelWorkerProc.worker_busy_loop`](../../vllm/v1/executor/shared_model_multiproc_executor.py#L319-L606) 入口，
4	> 分析非MoE 模型在 `--edge-npu-count 1 --dp 2` 下适配 PD 分离调度需要修改的点。
5	
6	---
7	
8	## 1. 问题定义
9	
10	### 1.1 当前状态：不分首尾，一个 round 走完
11	
12	```python
13	# _dispatch (line 634-635):
14	if method == "execute_model" and hasattr(vw, "execute_model_batched_pre"):
15	    output = vw.execute_model_batched_pre(args[0])
16	    # DECODE_FIRST → 也是同一个 execute_model_batched_pre！
17	    # DECODE_LAST  → 也是同一个 execute_model_batched_pre！
18	```
19	
20	end-of-round 流程：
21	
22	```
23	run_batched_head        ← head forward + send → 1 次 _model_forward
24	drive_batched_round     ← isend to cloud + recv closure
25	drain_batched_round     ← recv + tail forward + logits + handle_output
26	```
27	
28	**问题**：DECODE_FIRST 就该只做 head+send 返回空结果，但当前把 tail+logits 也做了。DECODE_LAST 又来一遍完整的 head+send+recv+tail，重复执行。
29	
30	### 1.2 目标状态：首尾分离，两轮完成
31	
32	```
33	Round N (F
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:52:14</sup>


---

## Assistant <sup>2026/8/14 16:52:14</sup>

这份设计文档将架构阐述得很清楚。现在让我亲自阅读核心调度调度逻辑（`schedule()` 分发）以理解优先级顺序，补充代理（agents）的深度阅读。


---

## Assistant <sup>2026/8/14 16:52:14</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 320,
  "offset": 1090
}
```

</details>


---

## User <sup>2026/8/14 16:52:14</sup>

<details>
<summary>Tool Result</summary>

```
1090	            self._log_scheduler_state(state, scheduler_output.batch_type)
1091	        # Stamp whether this batch carries any multimodal request so the
1092	        # cloud's CHER early-recv hint (built in PassiveEC.step from this SO)
1093	        # can decide whether to irecv mrope_positions. The passive cloud has
1094	        # NO request registry (mm_features do not cross the edge->cloud SO
1095	        # boundary for cached reqs - scheduled_cached_reqs carries only
1096	        # req_ids), so the edge scheduler - which owns self.requests - is the
1097	        # only place this can be computed. The expression mirrors
1098	        # NPUModelRunner.step_has_multimodal_req exactly; self.requests here
1099	        # (at scheduling time) == model_runner.requests at execute time (both
1100	        # reflect this step), so the cloud hint's has_mrope matches the edge
1101	        # sender's include_mrope bit-for-bit (eliminates the mixed-batch
1102	        # mismatch). Dynamic attr; su
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:52:29</sup>


---

## Assistant <sup>2026/8/14 16:52:30</sup>

我已经有了清晰的认识。核心调度调度逻辑揭示了确切的优先级顺序。让我等待这两个深度分析智能体完成任务，以确认架构细节并补充延迟、KV-retention 和 config 的详细信息。


---

## Assistant <sup>2026/8/14 16:52:31</sup>

<details>
<summary>Tool: <code>TodoWrite</code></summary>

```json
{
  "todos": [
    {
      "activeForm": "Exploring edge-cloud architecture & BatchType enum",
      "content": "Explore edge-cloud architecture & BatchType enum",
      "status": "completed"
    },
    {
      "activeForm": "Reading core schedule dispatch logic",
      "content": "Read core schedule dispatch logic (_pick_by_state)",
      "status": "completed"
    },
    {
      "activeForm": "Awaiting deep-read agents",
      "content": "Await deep-read agents (edge_cloud dir, config, docs)",
      "status": "in_progress"
    },
    {
      "activeForm": "Synthesizing full MTP scheduling explanation",
      "content": "Synthesize full MTP scheduling explanation",
      "status": "pending"
    }
  ]
}
```

</details>


---

## User <sup>2026/8/14 16:52:31</sup>

<details>
<summary>Tool Result</summary>

```
Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable
```

</details>


---

## Assistant <sup>2026/8/14 16:53:08</sup>


---

## Assistant <sup>2026/8/14 16:53:49</sup>

我已经通过亲自阅读相关内容（`BatchType` 枚举 + 文档字符串、`_pick_by_state` 调度逻辑、PD 分离设计文档以及 `layer_slice_config`）掌握了足够的信息，能够给出详尽且准确的解答。目前那两个负责深入阅读的 agent 仍在确认细节；待它们返回后，若发现有补充内容，我再进行整合。以下内容均基于我所阅读的实际源码。

---

# vllm-ascend 边云场景下 MTP 的调度机制

## 一、先理解"边云"(edge-cloud)架构:模型层切片

在 `pdmix` 这套代码里,边云不是传统 P/D 分离(那样是 P 节点算 prefill、D 节点算 decode、KV 跨机搬),而是**把一个模型按层切成三段,跨边/云协同**:

| 位置 | 跑哪些层 | 职责 |
|---|---|---|
| **边侧 (edge)** | 头段 `segment_a` + 尾段 `segment_e` + sampler | head forward(发 hidden 给云) / recv 云结果 + tail forward + 取 logits + 采样 |
| **云侧 (cloud)** | 中间层(动态切片,见 [layer_slice_config.yaml](vllm-ascend-pdmix/vllm_ascend/core/layer_slice_config.yaml)) | 接收边侧 hidden,跑中间 N 层,把结果回发边侧 |

云侧中间层按 prefill batch 大小动态切片(`16k→6 片`、`8k→6 片`…`<1k→1 片`)。边↔云通过 `edge_cloud_isend / recv` 在 **hidden channel** 上做 P2P。

**关键:每个 batch 拆成两轮完成** (见 [pd_separation_modification_plan.md](vllm-pdmix/docs/pd_separation_modification_plan.md) §9):
- **FIRST 轮**:边侧跑 head 段 → `isend` 给云 → 返回**空结果**(只告诉 EngineCore "head 完成")
- **LAST 轮**:从云侧 `recv` 中间层结果 → 边侧跑 tail 段 + logits + sampler → 返回**完整结果**

所以 `*_FIRST` = "走头段、发云",`*_LAST` = "收云、走尾段、出结果"。

---

## 二、8 种 BatchType 的定义

调度输出打一个 `batch_type` 标签,枚举在 [output.py:105-149](vllm-pdmix/vllm/v1/core/sched/output.py#L105-L149):

```python
class BatchType(enum.Enum):
    # ── 普通 4 种 (非 MTP) ──
    PREFILL_FIRST = "prefill_first"   # prefill 批,边侧跑头段 segment_a
    PREFILL_LAST  = "prefill_last"    # prefill 批,边侧跑尾段 segment_e + sampler
    DECODE_FIRST  = "decode_first"    # decode 批,边侧跑头段 (Phase 4)
    DECODE_LAST   = "decode_last"     # decode 批,边侧跑尾段 (Phase 4)

    # ── MTP / draft 4 种 (你问的 "mtp xxx") ──
    PREFILL_DRAFT_FIRST = "prefill_draft_first"  # prefill 阶段 draft 链头 (边→云)
    PREFILL_DRAFT_LAST  = "prefill_draft_last"   # prefill 阶段 draft 链尾 (云→边)
    DECODE_DRAFT_FIRST  = "decode_draft_first"   # decode 阶段 draft 链头 (边→云)
    DECODE_DRAFT_LAST   = "decode_draft_last"     # decode 阶段 draft 链尾 (云→边)
```

**你列的 8 个词和这里的映射**:

| 你的叫法 | 枚举 | 含义 |
|---|---|---|
| `prefill_first` | `PREFILL_FIRST` | prefill 批的"头段轮"(边→云) |
| `prefill_last` | `PREFILL_LAST` | prefill 批的"尾段轮"(云→边,出 token) |
| `decode_first` | `DECODE_FIRST` | decode 批的"头段轮"(边→云) |
| `decode_last` | `DECODE_LAST` | decode 批的"尾段轮"(云→边,出 token) |
| `mtp prefill_first` | `PREFILL_DRAFT_FIRST` | MTP 草稿链在 **prefill 阶段**的头(边→云,复用父 chunk 的 prefill 通道) |
| `mtp prefill_last` | `PREFILL_DRAFT_LAST` | MTP 草稿链在 prefill 阶段的尾(云→边,同通道) |
| `mtp decode_first` | `DECODE_DRAFT_FIRST` | MTP 草稿链在 **decode 阶段**的头(边→云,走 DECODE 通道) |
| `mtp decode_last` | `DECODE_DRAFT_LAST` | MTP 草稿链在 decode 阶段的尾(云→边,走 DECODE 通道) |

> **"draft" = MTP 草稿链**。源码里 `[MTP]` 注释和这 4 个 DRAFT 类型一一对应(见 [pd_separated_scheduler.py:386-397](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L386-L397):`[MTP] DECODE_DRAFT_LAST delay scheduling`、`[MTP] PREFILL_DRAFT_LAST delay scheduling`、`Async scheduled-MTP keeps real draft token IDs in the edge worker`)。MTP 自生成的 draft token 留在边侧,草稿链本身也是边→云→边两段。

两个维度正交:
- **prefill / decode** = 该 batch 处于请求的哪个阶段
- **FIRST / LAST** = 在边云两段流水里,这一步是头段还是尾段
- **DRAFT** 与否 = 是正常请求,还是 MTP 草稿链

---

## 三、调度优先级(核心)

调度入口 `_pick_by_state(state)` 根据 prefill 在途量(`PrefillState`)分三档,每档有不同的优先顺序。注释直接给出了优先级,见 [pd_separated_scheduler.py:1190-1320](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1190-L1320):

```
IDLE (无 prefill 在途):
  prefill_draft首 > prefill_draft尾 > P首 > decode_draft首 > decode_draft尾 > D首 > D尾 > P尾 > Empty

LOW  (有 prefill 在途但未满):
  P首 > P尾 > prefill_draft首 > prefill_draft尾 > decode_draft首 > decode_draft尾 > D首 > D尾 > Empty

HIGH (prefill 在途达上限):
  P尾 > prefill_draft首 > prefill_draft尾 > decode_draft首 > decode_draft尾 > D首 > D尾 > Empty
```

读法(以 P=Prefill、D=Decode、首=FIRST、尾=LAST 为例):

1. **MTP 草稿链总是尽量先跑完**——`prefill_draft首/尾`、`decode_draft首/尾` 在绝大多数档位里排在对应的 `P/D 首/尾` 前面或紧随其后。原因在 IDLE 分支注释里 ([pd_separated_scheduler.py:1192-1194](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1192-L1194)):草稿链在服时其父槽已释放(Phase A 计数),要尽快跑完链再起新 P首,避免草稿堆积。

2. **`*_FIRST` 与 `*_LAST` 的交替约束**:草稿链可流水(下一个 `PDFF` 可在前一个 `PDFL` 在飞时派发),但要靠 `not _force_*_draft_last` 保证 `PDFF → PDFL` 交替([pd_separated_scheduler.py:1405-1408](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1405-L1408))。同理 decode 域 `D首→D尾` 也有"尾不得抢在头前"的 overtake guard([pd_separated_scheduler.py:1231-1236](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1231-L1236))。

3. **IDLE 时 `P尾` 排最后**——因为没在途 prefill,优先把新 prefill 头起起来(`P首`),把资源让给草稿和 decode。

4. **HIGH 时 `P尾` 排第一**——prefill 在途已满,不能再起 `P首`,优先把已起的 prefill 收尾出 token。

5. **decode_or_draft_first_only 窗口**:在 `DECODE_LAST` 或 `DECODE_DRAFT_LAST` 之后,会开一个短窗口(默认 30ms,`_decode_or_draft_first_only_window_ms`)只允许 `decode_draft首` 或 `D首`,给云侧留出中间层 + P2P 时间([pd_separated_scheduler.py:1112-1146](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1112-L1146))。但若**有 draft 链待跑**,这个窗口会被绕过(注释:草稿链不能被 decode-first-only 窗口卡住,否则 prefill 草稿占位链到不了 worker MQ)。

---

## 四、延迟与门控(让边云流水不打架)

边云两段流水最大的风险是云侧中间层还没算完、边侧就抢跑尾段。所以每对 FIRST→LAST 之间都有"延迟调度" + "在途计数"门控,配置在 [layer_slice_config.yaml](vllm-ascend-pdmix/vllm_ascend/core/layer_slice_config.yaml) 和 scheduler 初始参数里:

| 门控 | 值 | 作用 |
|---|---|---|
| `decode_last_delay_schedule_ms` | 15ms(配置默认 30) | `DECODE_FIRST` 后,`DECODE_LAST` 至少等这么久才排,给云侧 DM + P2P 时间 |
| `draft_last_delay_schedule_ms` | 5ms | decode draft FIRST 后,其 draft LAST 至少等这么久(给云侧 Draft-middle + P2P) |
| `_prefill_draft_last_delay_schedule_ms` | 10ms | `[MTP]` prefill draft LAST 延迟(Phase A 边侧自贴尾 + 延迟) |
| `prefill_middle_throttle_ms` | 500ms | 云侧 prefill-middle 节流:等 decode-middle 这么久还没来,才再排一片 prefill-middle |
| `prefill_draft_remote_pending_limit` | 配置 | prefill 域草稿在云侧未回的最大在途数 |
| `decode_draft_remote_pending_limit` | 配置 | decode 域草稿在云侧未回的最大在途数 |
| `decode_or_draft_inflight_limit` | 1 | decode + draft 共享的在途上限(Phase A prefill_draft 仍走 DECODE 通道,故两域共占) |
| `prefill_inflight_limit` | — | prefill 在途上限,决定 IDLE/LOW/HIGH 档 |

Phase B 之后(4 域拆分,见 [pd_separated_scheduler.py:372-397](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L372-L397)):`prefill_draft` 已迁出 DECODE 通道,prefill 域和 decode 域各自计数、各自限额、互不影响。`_can_schedule_decode_first` 不再要求"无任何 draft 工作",请求级安全改由 `running` 门控保证(prefill_draft 链未完成的请求不会进 running,故不会被 DECODE_FIRST 调度)。

---

## 五、边云 MTP 的特殊点:KV retention

非边云场景,MTP draft 在同一个 `execute_model` 里就地把 draft token 生成完。边云把 draft **延迟到后续一个 draft-FIRST batch** 才算,这带来一个风险:父请求的 KV block 可能在草稿算完前就被释放并复用。

所以边云有 **deferred-draft KV retention**([pd_separated_scheduler.py:441-452](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L441-L452)):云侧草稿步骤要读写的那些请求的 KV block,会被推迟 `_free_blocks`,直到 draft task 完成或被丢弃(`release_draft_retained_blocks`)才释放。整体由 `_edge_cloud_draft_retention_enabled` 开关控制。

另外,async scheduled-MTP 的**真实 draft token ID 留在边侧**(`Async scheduled-MTP keeps real draft token IDs in the edge worker`),占位 DECODE_FIRST 的真实 draft token 从 worker 本地 `_draft_token_ids` buffer 填充——和原生 async spec decode 一致。

---

## 六、一句话总结

边云把模型按层切成"边头 + 云中 + 边尾",每个请求批拆成 **FIRST(边头→云,空回)→ LAST(云→边尾,出 token)** 两轮。把 **{prefill, decode} × {first, last}** 四种正常 batch,再叠加 **MTP 草稿链**就得到 8 种 `BatchType`——草稿链复用同样的边→云→边两段流水,只是走 draft 通道。调度器按 prefill 在途量分 IDLE/LOW/HIGH 三档排优先级,**MTP 草稿链整体被优先排空**(避免草稿堆积),再用 FIRST↔LAST 交替约束、延迟调度、在途计数和 KV retention 把边云两段流水安全地叠在一起。

---

两个深度阅读 agent 还在跑(覆盖 `edge_cloud/` 目录、`pcp_utils.py`、`pd_separation_config.py`、`passive_scheduler.py`、`llm_base_proposer.py` 和隐藏通道文档),回来后我会补充 PCP 机制、`pd_scheduling_policy` 配置项、以及草稿链在 proposer 侧的具体生成细节。


---

## User <sup>2026/8/14 16:53:49</sup>

<task-notification>
<task-id>a58465f5f1be22fd1</task-id>
<tool-use-id>call_a2e060047ec64e8484fd6e31</tool-use-id>
<output-file>C:\Users\root\AppData\Local\Temp\claude\c--kisella-mtp\0fd965c5-f091-41ab-b346-446569638fa9\tasks\a58465f5f1be22fd1.output</output-file>
<status>completed</status>
<summary>Agent "Explore scheduler config &amp; docs" finished</summary>
<note>A task-notification fires each time this agent stops with no live background children of its own. The user can send it another message and resume it, so the same task-id may notify more than once.</note>
<result>I now have a complete and thorough understanding of the entire MTP scheduling policy system. Here is my comprehensive report.

---

# MTP Scheduling Policies in vLLM-Ascend Edge-Cloud (边云) — Findings

There are **three distinct layers** where the terms `prefill_first`, `prefill_last`, `decode_first`, `decode_last` (and their MTP/draft variants) are defined. They are not a single enum — they live in different config classes and serve different roles. Below is each one with exact file:line references, docstrings, and meaning.

---

## Layer 1 — The `BatchType` enum (core batch-tagging system)

**File:** `c:\kisella_mtp\vllm-pdmix\vllm\v1\core\sched\output.py:105-149`

This is the single source of truth for the eight edge-cloud batch "kinds". Every `SchedulerOutput` is tagged with one of these so downstream consumers (notably the non-leader PP rank's `PassiveScheduler`) can route the batch without re-inspecting per-request state.

```python
class BatchType(enum.Enum):
    PD_MIX = "pd_mix"
    PURE_PREFILL = "pure_prefill"
    PURE_DECODE = "pure_decode"
    EMPTY = "empty"

    PREFILL_FIRST = "prefill_first"
    PREFILL_LAST = "prefill_last"
    DECODE_FIRST = "decode_first"
    DECODE_LAST = "decode_last"
    PREFILL_DRAFT_FIRST = "prefill_draft_first"
    PREFILL_DRAFT_LAST = "prefill_draft_last"
    DECODE_DRAFT_FIRST = "decode_draft_first"
    DECODE_DRAFT_LAST = "decode_draft_last"
```

The class docstring (`output.py:106-136`) gives the canonical meaning of each:

| Enum member | Docstring meaning |
|---|---|
| `PREFILL_FIRST` | edge-cloud PD separation — prefill batch executing the **edge head segment (segment_a)** |
| `PREFILL_LAST` | edge-cloud PD separation — prefill batch executing the **edge tail segment (segment_e + sampler)** |
| `DECODE_FIRST` | edge-cloud PD separation — decode batch executing the **edge head segment (Phase 4)** |
| `DECODE_LAST` | edge-cloud PD separation — decode batch executing the **edge tail segment (Phase 4)** |
| `PREFILL_DRAFT_FIRST` | prefill-phase draft chain **head (edge→cloud, reuses the parent chunk's prefill channel)** |
| `PREFILL_DRAFT_LAST` | prefill-phase draft chain **tail (cloud→edge, same channel as its PREFILL_DRAFT_FIRST)** |
| `DECODE_DRAFT_FIRST` | decode-phase draft chain **head (edge→cloud, DECODE channel)** |
| `DECODE_DRAFT_LAST` | decode-phase draft chain **tail (cloud→edge, DECODE channel)** |

The `SchedulerOutput` dataclass (`output.py:306-415`) carries the matching fields: `batch_type` (line 373), `head_token` (line 380), `hidden_channel` (line 386), and the MTP/draft fields `parent_req_id`, `draft_task_id`, `draft_step_idx` (lines 392-394).

The `HiddenChannelType` class (`output.py:30-97`) defines the data-plane channels these batches ride: a pool of `PREFILL_i` channels and `DECODE_i` channels, generated at import time via `HiddenChannelType.init(dp_size=8)` (line 97).

---

## Layer 2 — `pd_scheduling_policy` (user-facing high-level policy on SchedulerConfig)

**File:** `c:\kisella_mtp\vllm-pdmix\vllm\config\scheduler.py:158-162`

```python
pd_scheduling_policy: Literal["prefill_first", "decode_first", "strict_alternation"] = "prefill_first"
"""The scheduling policy to use when PD separation is enabled:
- "prefill_first": prioritize prefill requests over decode requests.
- "decode_first": prioritize decode requests over prefill requests.
- "strict_alternation": strictly alternate between prefill and decode steps."""
```

This is a base-vLLM config field. It is wired through `EngineArgs` (`vllm-pdmix\vllm\engine\arg_utils.py:605, 1436, 2075`) as the `--pd-scheduling-policy` CLI flag, and surfaced in test helpers (`vllm-pdmix\tests\v1\core\utils.py:61, 94`).

Important nuance: the ascend `PDSeparatedScheduler` does **not** directly read `pd_scheduling_policy`. Instead it implements its own `PrefillState` (IDLE/LOW/HIGH) state machine + `_pick_by_state` priority table (see Layer 4). So this field is a declarative/user-facing selector; the real edge-side ordering is encoded in the `_pick_by_state` priority comments (pd_separated_scheduler.py:1191-1320).

---

## Layer 3 — `DispatchPolicy` enum (cloud-side PassiveScheduler)

**File:** `c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\passive_scheduler.py:34-44`

```python
class DispatchPolicy(enum.Enum):
    """Order in which phase queues are drained inside schedule()."""
    EXPECT_ALTERNATION = "expect_alternation"  # Phase C: CloudUndesiredState machine (design §6.5).
    PREFILL_FIRST = "prefill_first"   # P  -&gt; PD-mix -&gt; D
    DECODE_FIRST = "decode_first"     # D  -&gt; PD-mix -&gt; P
    PDMIX_FIRST = "pdmix_first"       # PD-mix -&gt; P -&gt; D
```

This is the **cloud-side** dispatch policy. It determines the order the cloud's `PassiveScheduler` drains its ready queues (`ready_prefills`, `ready_pdmixes`, `ready_prefill_drafts`, `ready_decode_drafts`, `ready_decodes`). The `_POLICY_ORDER` dict (`passive_scheduler.py:562-581`) encodes each policy's queue-drain order.

- `EXPECT_ALTERNATION` (default) does NOT use `_POLICY_ORDER`; it dispatches via the `CloudUndesiredState` three-state machine (`passive_scheduler.py:47-58, 808-940`), which makes prefill-channel work (P/PD) and DECODE-channel work (D/DDF) take turns so both channel data planes stay busy.
- `PREFILL_FIRST` / `DECODE_FIRST` / `PDMIX_FIRST` are the simpler static-order policies.

It is configured via the **`PDSeparationConfig` (ZMQ channel config)**:

**File:** `c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\pd_separation_config.py:29-74`

```python
@dataclass
class PDSeparationConfig:
    # Dispatch policy for PassiveScheduler on the cloud side.
    # Valid options: "expect_alternation", "prefill_first", "decode_first", "pdmix_first"
    # Default: "expect_alternation" - Phase C: CloudUndesiredState three-state machine
    dispatch_policy: str = "expect_alternation"
```

Loaded from env var `VLLM_PP_PASSIVE_DISPATCH_POLICY` (pd_separation_config.py:71-73).

---

## Layer 4 — ascend `PDSeparationConfig` (edge-cloud sub-config: the booleans/limits)

**File:** `c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\ascend_config.py:892-964`

This is the edge-side sub-config under `additional_config.edge_cloud_config.pd_separation`. It defines the knobs that actually control the edge scheduler's priority/alternation behavior:

```python
class PDSeparationConfig:
    """Configured via:
        additional_config = {
            "edge_cloud_config": {
                "pd_separation": {
                    "enabled": true,
                    "next_prefill_prior_enable": true,
                    "chunk_prefill_prior_enable": true,
                    "max_chunk_prefill_ahead": 1,
                    "prefill_draft_remote_pending_limit": 2,
                    "decode_draft_remote_pending_limit": 2,
                    "prefill_draft_last_watchdog_seconds": 30.0,
                }
            }
        }
    """
```

Key fields (ascend_config.py:912-941):
- `next_prefill_prior_enable` (bool, default False) — when True, the edge scheduler may launch a **second PREFILL_FIRST while the previous one is still in flight (2P1D)**; when False, stays at 1P1D. (comment, ascend_config.py:883-889)
- `chunk_prefill_prior_enable` (bool, default False) — enables per-chunk flight tracking so the next chunk's PF can be dispatched before the previous chunk's PL returns.
- `max_chunk_prefill_ahead` (int, default 1) — cap on ahead-scheduled chunks per request.
- `prefill_draft_remote_pending_limit` / `decode_draft_remote_pending_limit` (int, default 2) — per-domain in-flight draft-step caps (Phase C, design §7.7 #37).
- `prefill_draft_last_watchdog_seconds` (float, default 30.0) — watchdog for cloud-published PREFILL_DRAFT_LAST; raises on timeout (link failure).
- `prefill_inflight_limit` (property, line 943-950) — returns 2 (2P1D) if `next_prefill_prior_enable` else 1 (1P1D).

These are wired into `scheduler_config` by `NPUPlatform._configure_pd_separation_scheduler`:

**File:** `c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\platform.py:353-405`

It copies `pd.prefill_inflight_limit → scheduler_config.pd_prefill_inflight_limit`, `pd.next_prefill_prior_enable → scheduler_config.pd_next_prefill_prior_enable`, `pd.chunk_prefill_prior_enable → scheduler_config.pd_chunk_prefill_prior_enable`, etc., and selects the scheduler class (`PDSeparatedScheduler` or `AsyncPDSeparatedScheduler`).

The scheduler reads them back at `pd_separated_scheduler.py:240-243, 318-327, 411-437`.

---

## How the MTP variant differs from the non-MTP variant

The MTP (Multi-Token Prediction) variants are the four `*_DRAFT_*` batch types. The non-MTP variants are the plain `PREFILL_FIRST/LAST` and `DECODE_FIRST/LAST`. Key differences, drawn from the enum docstring and the scheduler code:

### 1. What they represent
- **Non-MTP** batches carry the actual prefill/decode of the **target model**. `PREFILL_FIRST` = edge head segment of a prefill; `PREFILL_LAST` = edge tail segment + sampler; `DECODE_FIRST/LAST` = decode head/tail (Phase 4).
- **MTP** batches carry **speculative draft chain steps** produced by the MTP draft model to propose tokens for the target to verify. `PREFILL_DRAFT_FIRST/LAST` = prefill-phase draft chain head/tail; `DECODE_DRAFT_FIRST/LAST` = decode-phase draft chain head/tail.

### 2. Hidden channel usage (data plane)
- `PREFILL_FIRST/LAST` use one of the **prefill channels** (`PREFILL_1`, `PREFILL_2`, …) from the `HiddenChannelManager` pool (`pd_separated_scheduler.py:121-150`).
- `DECODE_FIRST/LAST` use the **dedicated DECODE channel** (`decode_channel()`, line 155-156).
- `PREFILL_DRAFT_FIRST/LAST` **reuse the parent chunk's prefill channel** (Phase B, design §4.3 — validated by `_validate_prefill_draft_tail_channel`, line 2019-2049; the channel stays pinned until the whole draft chain completes via `_finalize_prefill_slot`, line 865-886).
- `DECODE_DRAFT_FIRST/LAST` use the **DECODE channel** (same as decode — validated by `_validate_decode_draft_tail_channel`, line 2051-2064).

### 3. State machine / alternation invariants
The edge scheduler enforces strict First→Last alternation **per domain** via separate force-flags (`pd_separated_scheduler.py:371-375`):
- `_force_decode_last` — gates `DECODE_FIRST → DECODE_LAST`
- `_force_prefill_draft_last` — gates `PREFILL_DRAFT_FIRST → PREFILL_DRAFT_LAST`
- `_force_decode_draft_last` — gates `DECODE_DRAFT_FIRST → DECODE_DRAFT_LAST`

The `_pick_by_state` priority table (lines 1190-1320) shows the ordering differs by `PrefillState`:
- **IDLE**: prefill_draft首 &gt; prefill_draft尾 &gt; P首 &gt; decode_draft首 &gt; decode_draft尾 &gt; D首 &gt; D尾 &gt; P尾
- **LOW**: P首(若槽可用) &gt; P尾 &gt; prefill_draft首 &gt; prefill_draft尾 &gt; decode_draft首 &gt; decode_draft尾 &gt; D首 &gt; D尾
- **HIGH**: P尾 &gt; prefill_draft首 &gt; prefill_draft尾 &gt; decode_draft首 &gt; decode_draft尾 &gt; D首 &gt; D尾

### 4. Critical channel-sharing constraint (from test_pd_draft_drain.py:164-189)
`DECODE_DRAFT_FIRST` and `DECODE_FIRST` use **different recv primitives but share the DECODE stream**, so a draft FIRST must NOT be dispatched while a `DECODE_FIRST` head is in flight (cloud recv order could mismatch edge send order). `DECODE_DRAFT_FIRST + DECODE_DRAFT_FIRST` is safe (same primitive, FIFO), so draft pipelining only gates on **decode heads**, not total heads (`_can_schedule_decode_draft_first`, line 1427-1456). Prefill drafts ride the prefill channel and are exempt from this constraint.

### 5. Drain-not-drop invariant (from test_pd_draft_drain.py:402-450)
A `DECODE_DRAFT_LAST` in `decode_drafts_last_ready` always has its `DECODE_DRAFT_FIRST` already dispatched to the cloud, so the cloud will `isend` a response — the edge **must execute (drain) the tail to pair it, never drop it**, even when the owning request has finished/aborted (`_pick_decode_draft_last_batch`, line 2544-2620; `_run_edge_cloud_draft_last_segment` drains and returns a token-less placeholder instead of raising).

### 6. Per-domain remote-pending caps
Separate limits: `_prefill_draft_remote_pending_limit` and `_decode_draft_remote_pending_limit` (default 2 each, configurable via Phase C design §7.7 #37). They bound in-flight draft steps per domain before the edge stalls further head dispatch (`pd_separated_scheduler.py:411-424`).

### 7. Mid-prefill draft warmup (from test_pd_draft_drain.py:221-353)
Every middle prefill chunk runs a complete draft chain to **populate MTP KV**, while its proposals are discarded and no target verify placeholder is created (`draft_output_req_ids == ()` for mid-chunk, line 1963-1977). Only the **last** chunk's draft tokens are published to the following target verify batch.

---

## What `test_pd_chunk_prefill_prior.py` reveals about the priority logic

**File:** `c:\kisella_mtp\vllm-ascend-pdmix\tests\ut\test_pd_chunk_prefill_prior.py`

This test suite documents the **chunk-prefill-prior** scheduling logic (Phase 1) in `PDSeparatedScheduler`. Key revelations:

### Config wiring (TestConfigWiring, lines 94-158)
`ascend_config.edge_cloud_config.pd_separation` → `NPUPlatform._configure_pd_separation_scheduler` → `scheduler_config.pd_*` fields. `chunk_prefill_prior_enable` defaults to **False**.

### One-request-per-PF-batch invariant (TestSinglePrefillCandidate + TestPreparePFBatchState, lines 363-566)
When `chunk_prefill_prior_enable=True`, a PF batch is limited to **exactly one request** (`_select_single_prefill_candidate`, line 685-705; `_prepare_pf_running_state`, line 743-813). This is a regression guard for the **head_token collision bug**: two requests in one PF batch would share one `head_token`, the second overwrites the first in `_prefill_flight_by_token`, and the first request's PL is never matched — stalling it. Legacy mode (`chunk_prefill_prior_enable=False`) preserves multi-request batching (PL routes by `req_id`, no flight map to collide).

### Cross-request head-prior (TestCrossRequestHeadPrior + head-prior tests, lines 241-534)
`_select_pf_candidate_head_prior` (line 707-741) prefers a **fresh** candidate — one with no in-flight chunk (`_pending_tail_count[req] == 0`), i.e. its previous chunk's PL has returned. Decision order:
1. First fresh candidate → expose it (refill its slot with its next chunk).
2. No fresh candidate but `waiting` non-empty → return `None` so the caller **admits a new request** from waiting (cross-request head-prior, MindIE-style `P1首 → P2首`).
3. No fresh and no waiting → fall back to **ahead-dispatch** the in-flight candidate (single-request 2P1D pipeline).

`_should_ahead_schedule` (line 662-683): ahead (re-add to `chunk_prefill_first`) iff NOT last chunk AND ahead budget allows AND (`next_prefill_prior_enable` off OR no other request available).

### Ahead scheduling budget (lines 220-234, 335-355)
`_can_ahead_schedule` (line 629-633): bounded by `max_chunk_prefill_ahead` (default 1). Allows the next chunk's PF to dispatch before the previous chunk's PL returns. The last chunk never aheads (line 352-355).

### PL routing by head_token (TestPLLRoutingChunkPrior, lines 637-817)
`_update_from_output_prefill_last_chunk_prior` routes by `head_token`:
- **Last chunk's PL** → request enters `running` (line 661-695).
- **Mid-chunk PL, ahead-scheduled** → do NOT re-add to `chunk_prefill_first` (already ahead) (line 697-735).
- **Mid-chunk PL, NOT ahead** → re-add to `chunk_prefill_first` (line 737-771).
- Missing/unknown `head_token` → fall back to legacy routing (line 773-817).

### Running-migration guard (TestMigratePrefillToRunning, lines 825-885)
Requests with pending tails (`_pending_tail_count &gt; 0`) are **NOT** moved to `running` — they must wait for all in-flight PLs to complete. Also gates on `_running_gated_req_ids` and `_req_pending_prefill_draft_steps` (prefill_draft chain must complete before decode, line 3080-3110).

### Preemption protection (TestPDPreemptionProtection, lines 1065-1237)
Requests are protected from preemption from **First batch creation until matching Last batch finishes** via `_pd_active_flight_count` (line 972-1039). `_select_preemption_candidate` skips active requests for both FCFS and PRIORITY policies (line 1052-1073). An active request cannot be preempted (raises `RuntimeError`, line 1228-1237).

### KV-exhaustion deadlock fix (TestPickPrefillFirstEmptyRestoresRunning, lines 1245-1317)
When `super().schedule()` returns an empty batch (KV cache exhausted by running decode requests), `_pick_prefill_first_batch` **must restore `self.running = saved_running`**. Without this, decode requests in `self.running` are lost → `_can_schedule_decode_first` never sees them → KV never freed by finished decodes → prefill keeps returning empty → deadlock. The cloud eventually evicts unconsumed draft metadata as a downstream symptom.

---

## Relevant docs

- `c:\kisella_mtp\vllm-pdmix\docs\hidden_channel_call_flow_original.md` — original (dp=1) hidden channel call flow: describes PREFILL_FIRST/LAST using PREFILL_1/PREFILL_2 channels and DECODE_FIRST/LAST using the DECODE channel, with full call chains from process startup through per-step channel allocation.
- `c:\kisella_mtp\vllm-pdmix\docs\hidden_channel_call_flow_extended.md` — extended (dp&gt;1, `edge_npu_count==1`) version: per-dp_rank channel slicing, `HiddenChannelManager(dp_rank)`, `allocate_decode`/`release_decode` queue, PREFILL_FIRST/DECODE_FIRST allocation, PREFILL_LAST/DECODE_LAST validation against the local dp slice.

Neither doc uses the literal strings "mtp prefill_first" etc. — the MTP/draft variants are documented inline in the `BatchType` enum docstring and the `PDSeparatedScheduler` code comments. The `vllm-ascend-pdmix\docs\source\` tree contains the standard ascend docs (Design_Documents, etc.) but no dedicated edge-cloud/MTP scheduling doc was found beyond the two `hidden_channel_call_flow_*.md` files in `vllm-pdmix\docs\`.

---

## Summary of where each "policy term" is defined

| Term | Defined at | Kind | Side |
|---|---|---|---|
| `prefill_first` / `prefill_last` / `decode_first` / `decode_last` (batch tags) | `vllm-pdmix\vllm\v1\core\sched\output.py:142-145` | `BatchType` enum values | shared (edge tags, cloud routes) |
| `prefill_draft_first` / `prefill_draft_last` / `decode_draft_first` / `decode_draft_last` (MTP batch tags) | `vllm-pdmix\vllm\v1\core\sched\output.py:146-149` | `BatchType` enum values (MTP) | shared |
| `pd_scheduling_policy` = `prefill_first`/`decode_first`/`strict_alternation` | `vllm-pdmix\vllm\config\scheduler.py:158-162` | `SchedulerConfig` Literal field | edge (declarative) |
| `DispatchPolicy` = `expect_alternation`/`prefill_first`/`decode_first`/`pdmix_first` | `vllm-ascend-pdmix\vllm_ascend\core\passive_scheduler.py:34-44` | enum | cloud |
| `dispatch_policy` (ZMQ config) | `vllm-ascend-pdmix\vllm_ascend\pd_separation_config.py:48-51` | `PDSeparationConfig` field (env-driven) | cloud |
| `next_prefill_prior_enable`, `chunk_prefill_prior_enable`, `max_chunk_prefill_ahead`, `prefill_draft_remote_pending_limit`, `decode_draft_remote_pending_limit`, `prefill_draft_last_watchdog_seconds` | `vllm-ascend-pdmix\vllm_ascend\ascend_config.py:892-964` | ascend `PDSeparationConfig` | edge |
| wiring of the above into `scheduler_config` | `vllm-ascend-pdmix\vllm_ascend\platform.py:353-405` | `NPUPlatform._configure_pd_separation_scheduler` | edge bootstrap |</result>
<usage><subagent_tokens>0</subagent_tokens><tool_uses>23</tool_uses><duration_ms>158756</duration_ms></usage>
</task-notification>


---

## Assistant <sup>2026/8/14 16:54:21</sup>


---

## Assistant <sup>2026/8/14 16:54:23</sup>

The config/docs agent finished with a rich report. It surfaced something important I'd missed: these 8 terms actually span **4 distinct config layers**, including a separate *cloud-side* `DispatchPolicy` that reuses the names `prefill_first`/`decode_first`. Let me verify that cloud-side policy and the edge-side config knobs myself (non-overlapping with the still-running agent), then I'll consolidate.


---

## Assistant <sup>2026/8/14 16:54:23</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\passive_scheduler.py",
  "limit": 70,
  "offset": 30
}
```

</details>


---

## User <sup>2026/8/14 16:54:23</sup>

<details>
<summary>Tool Result</summary>

```
30	    from vllm.config import VllmConfig
31	    from vllm.v1.engine.core import PPSchedulerZmqSubscriber
32	
33	
34	class DispatchPolicy(enum.Enum):
35	    """Order in which phase queues are drained inside :meth:`PassiveScheduler.schedule`.
36	
37	    The three phase queues — PURE_PREFILL, PD_MIX, PURE_DECODE — are polled
38	    in the order encoded by the policy. One SchedulerOutput is picked per
39	    non-empty queue per call.
40	    """
41	    EXPECT_ALTERNATION = "expect_alternation"  # Phase C: CloudUndesiredState machine (design §6.5).
42	    PREFILL_FIRST = "prefill_first"   # P  → PD-mix → D
43	    DECODE_FIRST = "decode_first"     # D  → PD-mix → P
44	    PDMIX_FIRST = "pdmix_first"       # PD-mix → P → D
45	
46	
47	class CloudUndesiredState(enum.Enum):
48	    """Cloud-side three-state "undesired" machine (design §6.5.1).
49	
50	    Each state names the domain whose work was just served (or which
51	    should yield): its work is pushed to the tail of the priority table
52	 
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:54:23</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\ascend_config.py",
  "limit": 90,
  "offset": 880
}
```

</details>


---

## User <sup>2026/8/14 16:54:23</sup>

<details>
<summary>Tool Result</summary>

```
880	        logger.info("The number of redundant experts is %s", self.config["num_redundant_experts"])
881	
882	
883	# Mapping table for ``PDSeparationConfig.next_prefill_prior_enable``.
884	# When True, the edge scheduler is allowed to launch a second PREFILL_FIRST
885	# batch while the previous one is still in flight (2P1D); otherwise the
886	# scheduler stays at 1P1D. Kept as named constants so the mapping is easy to
887	# grep and adjust if the channel pool grows in the future.
888	_PD_PREFILL_INFLIGHT_WHEN_NEXT_PRIOR = 2  # 2P1D
889	_PD_PREFILL_INFLIGHT_DEFAULT = 1          # 1P1D
890	
891	
892	class PDSeparationConfig:
893	    """PD-separation sub-config under ``edge_cloud_config``.
894	
895	    Configured via::
896	
897	        additional_config = {
898	            "edge_cloud_config": {
899	                "pd_separation": {
900	                    "enabled": true,
901	                    "next_prefill_prior_enable": true,
902	                    "chunk_prefill_prior_enable": t
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 16:54:43</sup>


---

## Assistant <sup>2026/8/14 16:55:10</sup>

Verified both — the cloud-side `DispatchPolicy` ([passive_scheduler.py:34-44](vllm-ascend-pdmix/vllm_ascend/core/passive_scheduler.py#L34-L44)) and the edge-side `PDSeparationConfig` ([ascend_config.py:892-964](vllm-ascend-pdmix/vllm_ascend/ascend_config.py#L892-L964)). The second agent surfaced an important correction to my first answer, so here's a focused supplement.

---

# 重要补充:你列的 8 个词其实横跨 4 层配置

我第一版回答把 8 个词都归到 `BatchType` 枚举,这不完整。实际上 `prefill_first` / `decode_first` 这些字符串在代码里出现在**4 个不同的地方**,含义不同,容易混淆:

| 层 | 位置 | 是什么 | 作用于哪侧 |
|---|---|---|---|
| **L1 BatchType** | [output.py:142-149](vllm-pdmix/vllm/v1/core/sched/output.py#L142-L149) | batch 标签(批的"种类") | 边侧打标、云侧按标路由 |
| **L2 pd_scheduling_policy** | [scheduler.py:158-162](vllm-pdmix/vllm/config/scheduler.py#L158-L162) | 声明式高层策略 `prefill_first`/`decode_first`/`strict_alternation` | 边侧(声明性,ascend 调度器不直接读) |
| **L3 DispatchPolicy** | [passive_scheduler.py:34-44](vllm-ascend-pdmix/vllm_ascend/core/passive_scheduler.py#L34-L44) | **云侧**队列排空顺序 `expect_alternation`/`prefill_first`/`decode_first`/`pdmix_first` | **云侧** |
| **L4 PDSeparationConfig** | [ascend_config.py:892-964](vllm-ascend-pdmix/vllm_ascend/ascend_config.py#L892-L964) | 边侧真正生效的旋钮(2P1D、chunk-prior、ahead、draft 限额) | 边侧 |

**你问的 8 个词(`prefill_first`…`mtp decode_last`)精确对应 L1 的 `BatchType`**。但要理解"怎么调度",L3(云侧)和 L4(边侧旋钮)同样关键。

## L3 — 云侧 DispatchPolicy(和边侧是两套"prefill_first/decode_first")

云侧 `PassiveScheduler` 有自己的一套策略,排空 `PURE_PREFILL / PD_MIX / PURE_DECODE` 三个队列的顺序:

```
EXPECT_ALTERNATION  默认  CloudUndesiredState 三态机(设计 §6.5),让 prefill 通道和 DECODE 通道的活儿轮流跑,两条数据面都不闲
PREFILL_FIRST       P -> PD-mix -> D
DECODE_FIRST         D -> PD-mix -> P
PDMIX_FIRST          PD-mix -> P -> D
```

`CloudUndesiredState` 三态([passive_scheduler.py:47-58](vylm-ascend-pdmix/vllm_ascend/core/passive_scheduler.py#L47-L58))记录"上一拍喂饱了哪个域",下一拍就把该域压到队尾、把另一条通道顶上来——目的是让 **prefill 通道的活(P/PD)和 DECODE 通道的活(D/DDF)交替**,两条数据面并行不饿。配在 `VLLM_PP_PASSIVE_DISPATCH_POLICY` 环境变量。

> 注意:这里云侧的 `prefill_first/decode_first` 和 L1 的 batch 标签同名但不同物——一个是"云侧队列排空顺序",一个是"边侧批的种类标签"。

## L4 — 边侧真正生效的旋钮(`ascend_config.PDSeparationConfig`)

```python
edge_cloud_config.pd_separation = {
  "enabled": true,
  "next_prefill_prior_enable":   True/False,  # True=2P1D, False=1P1D
  "chunk_prefill_prior_enable":  True/False,  # 按chunk追踪在途,下个chunk的PF可超前派发
  "max_chunk_prefill_ahead":     1,          # 超前chunk数上限
  "prefill_draft_remote_pending_limit": 2,    # prefill域草稿在途上限
  "decode_draft_remote_pending_limit": 2,     # decode域草稿在途上限
  "prefill_draft_last_watchdog_seconds": 30.0,# 等云发回PDFL超时即判链路故障
}
```

- `next_prefill_prior_enable` → `prefill_inflight_limit` 返回 2(2P1D)或 1(1P1D)([ascend_config.py:943-950](vllm-ascend-pdmix/vllm_ascend/ascend_config.py#L943-L950))。2P1D 允许在前一个 `PREFILL_FIRST` 还在途时起第二个,把 IDLE/LOW/HIGH 的档位往前推。
- `chunk_prefill_prior_enable` 开启后,**一个 PF 批只装一个请求**([pd_separated_scheduler.py:685-705](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L685-L705))——这是 `head_token` 碰撞回归保护:两请求同批会共享一个 head_token,后者覆盖前者致其 PL 永远匹配不上而卡死。
- 跨请求头优先(MindIE 式 `P1首->P2首`):无 fresh 候选(上一 chunk 的 PL 已回)但有 waiting 时,优先放新请求,而不是对在途候选超前排。
- 抢占保护:从 FIRST 创建到匹配 LAST 完成之间(`_pd_active_flight_count`),请求不可被抢占。
- KV 耗尽死锁修复:`_pick_prefill_first_batch` 若 `super().schedule()` 返回空,**必须恢复 `self.running`**,否则 decode 请求丢失、KV 永不释放、prefill 持续空转而死锁。

## MTP(draft)特有的几条硬约束

这些是 4 个 `*_DRAFT_*` 类型区别于普通 4 类的地方:

1. **通道复用**:`PREFILL_DRAFT_FIRST/LAST` **复用父 chunk 的 prefill 通道**(Phase B 设计 §4.3,`_validate_prefill_draft_tail_channel` 钉住直到整条 draft 链完成);`DECODE_DRAFT_FIRST/LAST` 走 **DECODE 通道**(和 decode 同)。

2. **DECODE 流共享冲突**:`DECODE_DRAFT_FIRST` 和 `DECODE_FIRST` 用**不同 recv primitive 但共享 DECODE 流**——所以 draft FIRST 绝不能在 `DECODE_FIRST` head 在途时派发(云侧 recv 顺序会错)。`DECODE_DRAFT_FIRST + DECODE_DRAFT_FIRST` 安全(同 primitive、FIFO),所以 draft 流水只 gate decode head,不 gate 总 head。

3. **必须 drain 不可丢**:一个 `DECODE_DRAFT_LAST` 进了 ready 队列,说明它的 `DECODE_DRAFT_FIRST` 已经发到云、云一定会 `isend` 回应——边侧**必须把尾 drain 掉配对**,哪怕所属请求已 finish/abort,也要跑一个无 token 的占位而不是抛错。

4. **prefill 中段草稿热身**:每个 prefill 中间 chunk 都跑一条完整 draft 链来**填 MTP KV**,但这些 proposal 被丢弃、不生成 target verify 占位(`draft_output_req_ids == ()`)。**只有最后一个 chunk 的 draft token 才发布给后续 target verify 批**。

5. **每域在途上限**:`prefill_draft_remote_pending_limit` / `decode_draft_remote_pending_limit`(默认各 2)分别限 prefill 域、decode 域草稿在云侧未回的步数,超过就停发该域新 head。Phase B 后两域独立计数互不影响。

6. **占位 DECODE_FIRST**:async scheduled-MTP 的真实 draft token ID 留在边侧,占位 `DECODE_FIRST` 从 worker 本地 `_draft_token_ids` buffer 填充,和原生 async spec decode 一致;它创建时就把自己的 tail 自投进 `decodes_last_ready`,但调度时受 overtake guard 约束(尾不得抢在头前)。

---

第一个 agent(执行侧:`batched_model_runner.py` 的 `_apply_decode_first_reorder` / `execute_model_tail_pre`、`shared_model_edge_worker.py` 的 head/tail marker、`pcp_utils.py` 的 PCP、`llm_base_proposer.py` 的草稿生成)还在跑,回来后我补充 worker 层"草稿链怎么实际生成 + decode_first 怎么重排"的部分。


---

## User <sup>2026/8/14 20:07:26</sup>

C:\kisella_mtp\log\0814-1.txt是实际调度情况，为什么batch_queue会出现持续为1情况


---

## Assistant <sup>2026/8/14 20:07:40</sup>


---

## Assistant <sup>2026/8/14 20:07:41</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "ls -la \"C:/kisella_mtp/log/0814-1.txt\" 2>/dev/null; echo \"---wc---\"; wc -l \"C:/kisella_mtp/log/0814-1.txt\" 2>/dev/null",
  "description": "Check log file size and line count"
}
```

</details>


---

## User <sup>2026/8/14 20:07:42</sup>

<details>
<summary>Tool Result</summary>

```
-rw-r--r-- 1 root 197121 13893 Aug 14 20:04 C:/kisella_mtp/log/0814-1.txt
---wc---
90 C:/kisella_mtp/log/0814-1.txt
```

</details>


---

## Assistant <sup>2026/8/14 20:07:44</sup>


---

## Assistant <sup>2026/8/14 20:07:44</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "C:\\kisella_mtp\\log\\0814-1.txt"
}
```

</details>


---

## User <sup>2026/8/14 20:07:44</sup>

<details>
<summary>Tool Result</summary>

```
1	(EngineCore pid=88208) ERROR 08-14 11:24:36 [patch_engine_core.py:895] [BATCH_QUEUE] Enqueued prefill_draft_first, queue_len=3, types=['prefill_draft_first', 'prefill_last', 'decode_first']
2	(EngineCore pid=88208) ERROR 08-14 11:24:36 [patch_engine_core.py:895] [BATCH_QUEUE] Enqueued decode_last, queue_len=4, types=['decode_last', 'prefill_draft_first', 'prefill_last', 'decode_first']
3	(Worker_TP1 pid=88242) ERROR 08-14 11:24:36 [multiproc_executor.py:1232] [EDGE-DEQUEUE] dequeue took 0.383 ms batch_type: prefill_last
4	(Worker_PP0_TP0 pid=88241) ERROR 08-14 11:24:36 [multiproc_executor.py:1232] [EDGE-DEQUEUE] dequeue took 0.381 ms batch_type: prefill_last
5	(EngineCore pid=88208) ERROR 08-14 11:24:36 [patch_engine_core.py:895] [BATCH_QUEUE] Enqueued decode_first, queue_len=4, types=['decode_first', 'decode_last', 'prefill_draft_first', 'prefill_last']
6	(Worker_TP1 pid=88242) ERROR 08-14 11:24:36 [multiproc_executor.py:1232] [EDGE-DEQUEUE] dequeue took 0.364 ms batch_type: prefill
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 20:09:17</sup>


---

## Assistant <sup>2026/8/14 20:09:18</sup>

这是一个边云（edge-cloud）调度追踪记录。我来分析一下队列长度的模式，并通过阅读调度门控（scheduling gating）代码和 `batch_queue` 的实现来验证其原因。


---

## Assistant <sup>2026/8/14 20:09:19</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "cd c:/kisella_mtp && grep -rn \"batch_queue\\|BATCH_QUEUE\\|batch_queue_len\\|def.*enqueue\\|appendleft\\|\\.append\\|popleft\\|\\.pop(\" vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py 2>/dev/null | head -40; echo \"=== find patch_engine_core ===\"; find c:/kisella_mtp -name \"patch_engine_core.py\" 2>/dev/null | head",
  "description": "Locate batch_queue implementation"
}
```

</details>


---

## User <sup>2026/8/14 20:09:20</sup>

<details>
<summary>Tool Result</summary>

```
27:* ``EngineCore.step`` / ``EngineCore.step_with_batch_queue`` — drain
45:2. ``step`` / ``step_with_batch_queue`` / ``_process_input_queue`` insert
58:The reimplementations of ``step()``, ``step_with_batch_queue()`` and
195:            self.scheduler.prefills_last_ready.append(so)
197:            self.scheduler.decodes_last_ready.append(so)
203:            self.scheduler.prefill_drafts_last_ready.append(so)
303:                deferred.setdefault(task_id, []).append(scheduler_output)
340:    queued = [] if deferred is None else deferred.pop(draft_task_id, [])
362:        deferred.pop(draft_task_id, None)
471:    deferred.append(scheduler_output)
478:    return deferred.pop(0)
717:    batch_queue = getattr(self, "batch_queue", None)
718:    if not batch_queue:
720:    for _future, scheduler_output, _exec_future in batch_queue:
801:# EngineCore.step_with_batch_queue — full replacement.                    #
803:def _patched_step_with_batch_queue(self):
811:    batch_queue = self.batch_qu
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 20:09:46</sup>


---

## Assistant <sup>2026/8/14 20:09:47</sup>

我现在明白了 `batch_queue` 的结构：`appendleft`（在头部插入新的）+ `pop()`（从尾部取出最旧的）= FIFO，并且 `types` 是从新到旧排列的。让我阅读一下核心的 `step_with_batch_queue` 逻辑和调度器的 inflight 限制，以精准定位其运行机制。


---

## Assistant <sup>2026/8/14 20:09:47</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_engine_core.py",
  "limit": 130,
  "offset": 801
}
```

</details>


---

## User <sup>2026/8/14 20:09:47</sup>

<details>
<summary>Tool Result</summary>

```
801	# EngineCore.step_with_batch_queue — full replacement.                    #
802	# =======================================================================#
803	def _patched_step_with_batch_queue(self):
804	    """Continuously fill the local worker FIFO before collecting one result.
805	
806	    Native async scheduling relies on queue order, not EngineCore seeing each
807	    token first.  Fill all currently derivable DF/DL/DRF/DRL controls up to
808	    the executor credit so short edge segments cannot drain the MQ between
809	    two EngineCore turns.
810	    """
811	    batch_queue = self.batch_queue
812	    assert batch_queue is not None
813	
814	    assert len(batch_queue) < self.batch_queue_size
815	
816	    model_executed = False
817	    fill_async_mtp_placeholders = getattr(
818	        self.scheduler,
819	        "_uses_async_scheduled_mtp_placeholders",
820	        lambda: False,
821	    )()
822	    deferred_scheduler_output: tuple[
823	        SchedulerOutput, Future
824	 
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 20:09:48</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 130,
  "offset": 1398
}
```

</details>


---

## User <sup>2026/8/14 20:09:48</sup>

<details>
<summary>Tool Result</summary>

```
1398	    def _can_schedule_prefill_draft_first(self) -> bool:
1399	        if not self.prefill_drafts_first_ready:
1400	            return False
1401	        next_output = self.prefill_drafts_first_ready[0]
1402	        is_pregenerated = (
1403	            next_output.draft_task_id in self._pregenerated_draft_task_ids
1404	        )
1405	        if is_pregenerated:
1406	            # 语义与旧 _can_schedule_draft_first pregenerated 分支一致：
1407	            # `not _force_prefill_draft_last` 保证 PDFF -> PDFL 交替；
1408	            # 草稿链可流水：下一个 PDFF 在前一个 PDFL 在飞时即可派发。
1409	            # Phase B（设计 §6.1）：prefill 域已迁出 DECODE 通道，decode
1410	            # 头/标记不再 gate prefill 域。
1411	            return bool(
1412	                self.prefill_draft_remote_pending_count
1413	                < self._prefill_draft_remote_pending_limit
1414	                and not self.prefill_drafts_last_ready
1415	                and not self._force_prefill_draft_last
1416	            )
1417	
1418	        # Phase B（设计 §4.1
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 20:10:34</sup>


---

## Assistant <sup>2026/8/14 20:10:35</sup>

机制现在很清楚了。让我核实一下 "dequeue took X ms" 测量的是什么（以确认 LAST 的慢速是由于云端的往返造成的），并确认 inflight-limit 的默认值/可配置性。


---

## Assistant <sup>2026/8/14 20:10:36</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "cd c:/kisella_mtp && grep -rn \"EDGE-DEQUEUE\\|dequeue took\" vllm-pdmix/vllm/v1/executor/ vllm-ascend-pdmix/ 2>/dev/null | head; echo \"=== context of dequeue log ===\"; grep -rn \"EDGE-DEQUEUE\" vllm-pdmix/vllm/v1/executor/multiproc_executor.py 2>/dev/null",
  "description": "Find EDGE-DEQUEUE log source"
}
```

</details>


---

## User <sup>2026/8/14 20:10:37</sup>

<details>
<summary>Tool Result</summary>

```
vllm-pdmix/vllm/v1/executor/multiproc_executor.py:1233:                        "[EDGE-DEQUEUE] dequeue took %.3f ms batch_type: %s",
=== context of dequeue log ===
1233:                        "[EDGE-DEQUEUE] dequeue took %.3f ms batch_type: %s",
```

</details>


---

## Assistant <sup>2026/8/14 20:10:40</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\executor\\multiproc_executor.py",
  "limit": 75,
  "offset": 1195
}
```

</details>


---

## User <sup>2026/8/14 20:10:40</sup>

<details>
<summary>Tool Result</summary>

```
1195	                                    (WorkerProc.ResponseStatus.SUCCESS, ack)
1196	                                )
1197	                        continue
1198	                except Exception:
1199	                    pass  # TimeoutError or empty queue
1200	
1201	            # Poll cross-node MQ with short timeout so we can
1202	            # periodically check the local MQ.
1203	            try:
1204	                _t0 = time.monotonic()
1205	                method, args, kwargs, output_rank = self.rpc_broadcast_mq.dequeue(
1206	                    timeout=0.1
1207	                )
1208	                _dt_ms = (time.monotonic() - _t0) * 1000
1209	            except TimeoutError:
1210	                continue
1211	
1212	            # Skip execute_model from cross-node MQ on pp rank1 workers.
1213	            # These workers execute model only when triggered by their
1214	            # local passive EngineCore via local_rpc_broadcast_mq.
1215	            if (
1216	             
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 20:11:14</sup>


---

## Assistant <sup>2026/8/14 20:11:15</sup>

关键修正：“dequeue took”实际上是指 `_dt_ms = time.monotonic() - _t0`，这是在 `dequeue()` 调用**内部**测量的（第 1204-1208 行），即在执行（第 1237 行）**之前**。因此，数值大意味着 worker 处于 **空闲等待下一个 batch 的状态**，而不是在忙于计算。让我确认一下 inflight-count 的递增过程以及控制填充循环的 draft-parent 门控机制。


---

## Assistant <sup>2026/8/14 20:11:17</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "cd c:/kisella_mtp && grep -n \"decode_or_draft_inflight_count\" vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py | head -30; echo \"=== draft parent gate ===\"; grep -n \"_has_unresolved_edge_cloud_draft_parent\\|def _has_unresolved\" vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py vllm-ascend-pdmix/vllm_ascend/core/*.py 2>/dev/null | head",
  "description": "Find inflight count increments and draft-parent gate"
}
```

</details>


---

## User <sup>2026/8/14 20:11:18</sup>

<details>
<summary>Tool Result</summary>

```
246:        self.decode_or_draft_inflight_count: int = 0
257:        # 因此 decode_or_draft_inflight_count 仍被两域共同占用。
1167:        # Do NOT gate on decode_or_draft_inflight_count here either: it was
1332:                or self.decode_or_draft_inflight_count > 0
1390:            and self.decode_or_draft_inflight_count == 0
1451:            self.decode_or_draft_inflight_count == 0
1476:                f"decode_or_draft_inflight: {self.decode_or_draft_inflight_count}/{self.decode_or_draft_inflight_limit}, "
1497:                f"decode_or_draft_inflight: {self.decode_or_draft_inflight_count}/{self.decode_or_draft_inflight_limit}",
2189:            self.decode_or_draft_inflight_count += 1
2202:            self.decode_or_draft_inflight_count,
3049:                    self.decode_or_draft_inflight_count += 1
3383:            if self.decode_or_draft_inflight_count > 0:
3384:                self.decode_or_draft_inflight_count -= 1
3389:                f"decode_or_draft_inflight: {self.decode_or
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 20:11:21</sup>


---

## Assistant <sup>2026/8/14 20:11:21</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 35,
  "offset": 2178
}
```

</details>


---

## User <sup>2026/8/14 20:11:21</sup>

<details>
<summary>Tool Result</summary>

```
2178	            )
2179	            draft_last.draft_output_req_ids = getattr(
2180	                scheduler_output,
2181	                "draft_output_req_ids",
2182	                tuple(scheduler_output.num_scheduled_tokens),
2183	            )
2184	            self._validate_decode_draft_tail_channel(draft_last)
2185	            self.decode_drafts_last_ready.append(draft_last)
2186	            self.decode_draft_remote_pending_count += 1
2187	            self._force_decode_draft_last = True
2188	            self._start_decode_draft_last_delay()
2189	            self.decode_or_draft_inflight_count += 1
2190	
2191	        logger.info(
2192	            "[MTP-DEBUG] scheduler picked %s: task_id=%s, "
2193	            "parent_req_id=%s, draft_step_idx=%s, head_token=%s, "
2194	            "remaining_ready=%d, decode_or_draft_inflight=%d, "
2195	            "%s_pending=%d",
2196	            first_type.value,
2197	            scheduler_output.draft_task_id,
2198	            scheduler_outp
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 20:11:22</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_engine_core.py",
  "limit": 30,
  "offset": 709
}
```

</details>


---

## User <sup>2026/8/14 20:11:22</sup>

<details>
<summary>Tool Result</summary>

```
709	def _has_unresolved_edge_cloud_draft_parent(self) -> bool:
710	    """Keep async scheduling behind a prefill tail only.
711	
712	    Async scheduled-MTP pre-generates the decode draft chain when DECODE_LAST
713	    is picked, so DECODE_LAST must not hold back local edge dispatch.
714	    """
715	    if not self._uses_scheduled_edge_cloud_draft():
716	        return False
717	    batch_queue = getattr(self, "batch_queue", None)
718	    if not batch_queue:
719	        return False
720	    for _future, scheduler_output, _exec_future in batch_queue:
721	        if (
722	            scheduler_output.batch_type == BatchType.PREFILL_LAST
723	            and getattr(scheduler_output, "is_last_prefill_chunk", True)
724	        ):
725	            is_pregenerated = getattr(
726	                self.scheduler,
727	                "is_pre_generated_draft",
728	                lambda _so: False,
729	            )(scheduler_output)
730	            if not is_pregenerated:
731	                retur
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 20:11:53</sup>


---

## Assistant <sup>2026/8/14 20:12:16</sup>

确认。现在我已经掌握了完整、有据可查的情况。以下是分析结果。

---

# batch_queue 持续为 1 的原因:生产端被节流到 1 在途,worker 反而空转等

## 直接结论

`batch_queue` 稳态停在 1(入队时永远是 `queue_len=1`)**不是 worker 算得慢,而是生产端(EngineCore + scheduler)被三重门控节流到"每次只准 1 个 decode/draft 批在途"**。worker 因此经常空转等下一批。

关键证据在日志里的 `dequeue took` 字段——它量的是 **worker 在 `dequeue()` 里阻塞等下一批的时间**,不是执行时间。代码在 [multiproc_executor.py:1204-1208](vllm-pdmix/vllm/v1/executor/multiproc_executor.py#L1204-L1208):`_t0` 取在 `dequeue()` 之前,执行 `func()` 在 1237 行之后。所以:

| 批类型 | dequeue took | 含义 |
|---|---|---|
| `*_FIRST`(ddf、pdf_first、decode_first) | 0.2~1.5 ms | MQ 里已有批等着,worker 抓得快 |
| `*_LAST`(ddl、prefill_draft_last、decode_last) | 5~13 ms | **worker 空转等下一批**——等调度器的 `decode_last_delay`/`draft_last_delay` 延迟窗 + 云侧中间层算完回传 |

worker 大段空等 = 生产端是瓶颈,queue 自然填不起来。

## 日志的三段式正好对应三种状态

| 行段 | queue_len | dequeue took | 状态 | 为什么 |
|---|---|---|---|---|
| 1-45 | 3-4 | 0.2-0.4 ms(小) | **prefill 阶段**,消费受限 | prefill 域(`prefill_inflight`,1 或 2)和 decode/draft 域(`decode_or_draft_inflight`,1)**计数器分离**,两域可同时在途,调度器能连续产 prefill+decode+draft 多批,worker 来不及 drain,queue 堆到 3-4 |
| **46-74** | **1** | 5-13 ms(大,LAST) | **稳态 decode+MTP,生产受限** | 只剩 decode/draft 单域,见下三重门控 |
| 76-90 | 2-3 | 0.2 ms(小) | **草稿流水 burst** | pregenerated 草稿走 `decode_head_inflight_count` 门控([L1434-1444](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1434-L1444)),不限 `decode_or_draft_inflight==0`,多个 draft_first 可同时在途,queue 又能堆起来 |

## 稳态"持续为 1"的三重生产端门控(均已对照源码)

### 门控 1:`decode_or_draft_inflight_limit = 1`(硬上限)

[pd_separated_scheduler.py:245](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L245) 写死 `= 1`,非配置驱动。于是:

- `_can_schedule_decode_first` 要求 `decode_or_draft_inflight_count == 0`([L1390](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1390))
- `_can_schedule_decode_draft_first`(**scheduled/非 pregenerated 路径**)也要求 `== 0`([L1451](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1451))
- 挑出一个 decode_draft_first 后 `decode_or_draft_inflight_count += 1`([L2189](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L2189))

→ 只要有 1 个 decode/draft 批在途,`schedule()` 就返回 EMPTY。

### 门控 2:EMPTY 即跳出填充循环 + 一轮一调度

[patch_engine_core.py:852-855](vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py#L852-L855):`schedule()` 返回 EMPTY 时,只要 batch_queue 非空就 `break`。再加上 [L901-911](vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py#L901-L911) 非 async-MTP 模式的"一轮一调度"`break`——EngineCore 每轮只产 ~1 个 SchedulerOutput。

### 门控 3:产完即 `pop()+future.result()` 阻塞

[patch_engine_core.py:919-924](vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py#L919-L924):填充后立即 `batch_queue.pop()` 取最老的并 `future.result()` **阻塞等它返回**,才进下一轮。对 `*_LAST` 这一等就是云侧中间层往返(5-13 ms)。阻塞期间 queue=0,worker 也跟着空等。

### 叠加:强制 ddf→ddl 交替 + 延迟窗

挑出 draft_first 后立刻 `_force_decode_draft_last = True`([L2187](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L2187))且 `_start_decode_draft_last_delay()`([L2188](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L2188))——下一个必须是 draft_last 且至少等 `draft_last_delay`(5 ms);`DECODE_LAST` 同理有 `decode_last_delay`(15 ms,见 [layer_slice_config.yaml](vllm-ascend-pdmix/vllm_ascend/core/layer_slice_config.yaml))。这段强制空窗里 queue 就是空的。

### 叠加:MTP 草稿链的串行依赖

每一步 draft 都是 edge→cloud→edge 一个完整往返,下一步的草稿通常依赖上一步返回的 token,本身可重叠度就低——scheduled 模式下基本串行。

## 一句话锁步链

```
入队 ddf_first(len 1, inflight=1)→ pop+future.result() 等 ~1ms(FIRST 快,只发云)→ inflight=0
→ 入队 ddl_last(len 1, inflight=1)→ pop+future.result() 阻塞 ~10ms 等 云算完+回传 → inflight=0
→ 入队下一个 ddf_first(len 1)→ ……
```
每轮填 1、马上 pop 干掉、阻塞等云往返,所以入队瞬间永远是 `queue_len=1`,worker 在中间空等 5-13 ms。

## 这是 bug 吗 / 怎么提升重叠

基本是 scheduled-MTP + 边云默认值的**预期行为**,但确实让边侧 worker 闲置等云。可调杠杆(按收益排序):

1. **async scheduled-MTP 占位链**(`fill_async_mtp_placeholders`,[L817-821](vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py#L817-L821)/[L901-904](vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py#L901-L904)):一个 EngineCore turn 里把整条 draft 占位链 materialize 出来——这正是日志 76-90 行 len 能堆到 2-3 的原因。需要 `async_scheduling=True`。
2. **抬 `decode_draft_remote_pending_limit`**(默认 2,[ascend_config.py:931-933](vllm-ascend-pdmix/vllm_ascend/ascend_config.py#L931-L933)):允许更多 draft 步同时在云侧在途,配合 pregenerated 路径才能让草稿链流水堆起来。
3. **缩短 `decode_last_delay` / `draft_last_delay`**([layer_slice_config.yaml](vllm-ascend-pdmix/vllm_ascend/core/layer_slice_config.yaml)):压缩强制空窗;但太短会让 LAST 的 recv 撞上云没算完而 stall,要实测。
4. `next_prefill_prior_enable`(2P1D)只对 prefill 域有效,**对稳态 decode+MTP 的 len=1 无帮助**。

注意:MTP 每步"下一步依赖上一步验证/草稿 token"的串行性是固有的,即便把上面全开,单请求草稿链的重叠度也有上限;真正能把 queue 填满的是**多请求并发**(多个请求的 draft/decode 交错),所以稳态单请求场景 len=1 在某种程度上是正常的。

---

需要的话我可以再对照日志逐行画一张"入队→pop→阻塞→空等"的时间轴,或者去翻 `async_scheduling` 当前在这套部署里是否开了(决定你看到的 46-74 是不是 scheduled 模式)。


---

## User <sup>2026/8/14 21:22:29</sup>

C:\kisella_mtp\log\0814-2.txt 是不开mtp的，queue_len能保持不低于2，这个pp并行的机制


---

## Assistant <sup>2026/8/14 21:22:44</sup>


---

## Assistant <sup>2026/8/14 21:22:44</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "C:\\kisella_mtp\\log\\0814-2.txt"
}
```

</details>


---

## User <sup>2026/8/14 21:22:44</sup>

<details>
<summary>Tool Result</summary>

```
1	(Worker_TP1 pid=88961) ERROR 08-14 12:19:30 [multiproc_executor.py:1232] [EDGE-DEQUEUE] dequeue took 1.009 ms batch_type: decode_first
2	(Worker_PP0_TP0 pid=88960) ERROR 08-14 12:19:30 [multiproc_executor.py:1232] [EDGE-DEQUEUE] dequeue took 0.852 ms batch_type: decode_first
3	(EngineCore pid=88927) ERROR 08-14 12:19:30 [patch_engine_core.py:895] [BATCH_QUEUE] Enqueued decode_last, queue_len=2, types=['decode_last', 'decode_first']
4	(Worker_TP1 pid=88961) ERROR 08-14 12:19:30 [multiproc_executor.py:1232] [EDGE-DEQUEUE] dequeue took 1.017 ms batch_type: decode_last
5	(Worker_PP0_TP0 pid=88960) ERROR 08-14 12:19:30 [multiproc_executor.py:1232] [EDGE-DEQUEUE] dequeue took 0.790 ms batch_type: decode_last
6	(EngineCore pid=88927) ERROR 08-14 12:19:30 [patch_engine_core.py:895] [BATCH_QUEUE] Enqueued decode_first, queue_len=2, types=['decode_first', 'decode_last']
7	(Worker_TP1 pid=88961) ERROR 08-14 12:19:30 [multiproc_executor.py:1232] [EDGE-DEQUEUE] dequeue took 0.994 ms batch_type: d
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 21:23:51</sup>


---

## Assistant <sup>2026/8/14 21:23:52</sup>

现在我可以看出明显的差异。让我读取实际的 `decode_first`/`decode_last` 选取以及进行途更新逻辑，以精确确定 `no-MTP` 是如何允许 `inflight depth=2` 的。


---

## Assistant <sup>2026/8/14 21:23:53</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "cd c:/kisella_mtp && grep -n \"def _pick_decode_first_batch\\|def _pick_decode_last_batch\\|def _update_from_output\\|def update_from_output\\|_force_decode_last\\b\\|decode_or_draft_inflight_count +=\\|decode_or_draft_inflight_count -=\\|def _on_decode_first\\|def _on_decode_last\\|def _handle_decode\" vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py | head -50",
  "description": "Find decode pick and update functions"
}
```

</details>


---

## User <sup>2026/8/14 21:23:54</sup>

<details>
<summary>Tool Result</summary>

```
371:        self._force_decode_last: bool = False
1394:            and not self._force_decode_last
1442:                and not self._force_decode_last
1454:            and not self._force_decode_last
2189:            self.decode_or_draft_inflight_count += 1
2967:    def _pick_decode_last_batch(self) -> SchedulerOutput:
2976:        self._force_decode_last = False
3018:    def _pick_decode_first_batch(self) -> SchedulerOutput:
3049:                    self.decode_or_draft_inflight_count += 1
3052:                    self._force_decode_last = True
3151:    def _update_from_output_prefill_last_legacy(
3196:    def _update_from_output_prefill_last_chunk_prior(
3330:    def update_from_output(
3384:                self.decode_or_draft_inflight_count -= 1
```

</details>


---

## Assistant <sup>2026/8/14 21:23:57</sup>


---

## Assistant <sup>2026/8/14 21:23:58</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 100,
  "offset": 2967
}
```

</details>


---

## User <sup>2026/8/14 21:23:58</sup>

<details>
<summary>Tool Result</summary>

```
2967	    def _pick_decode_last_batch(self) -> SchedulerOutput:
2968	        if not self.decodes_last_ready:
2969	            return self._make_empty_batch()
2970	        so = self.decodes_last_ready.popleft()
2971	        assert so.batch_type == BatchType.DECODE_LAST, (
2972	            f"decodes_last_ready expects DECODE_LAST, got {so.batch_type}"
2973	        )
2974	        self._validate_decode_tail_channel(so)
2975	        self._start_decode_or_draft_first_only_window()
2976	        self._force_decode_last = False
2977	        self._pregenerate_draft_chain(so)
2978	        return so
2979	
2980	    def _ensure_cached_all_token_ids(
2981	        self, scheduler_output: SchedulerOutput,
2982	    ) -> None:
2983	        """Ensure every cached decode req carries all_token_ids.
2984	
2985	        In PD-separated mode the edge worker's persistent input_batch may not
2986	        retain a request across the PF → PL → DF transitions (the tail segment
2987	        may have been skipped by ``
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 21:24:39</sup>


---

## Assistant <sup>2026/8/14 21:24:41</sup>

关键发现：`_pick_decode_first_batch` 会立即 **自发布匹配的 `decode_last`** 到 `decodes_last_ready` (第 3062-3066 行) 中，并增加两个计数器（`decode_or_draft_inflight_count` 和 `decode_head_inflight_count`），同时 `_pick_decode_last_batch` 完全没有增加任何在途计数器。让我确认一下减少逻辑，以确定生命周期。


---

## Assistant <sup>2026/8/14 21:24:41</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 95,
  "offset": 3330
}
```

</details>


---

## User <sup>2026/8/14 21:24:41</sup>

<details>
<summary>Tool Result</summary>

```
3330	    def update_from_output(
3331	        self,
3332	        scheduler_output: SchedulerOutput,
3333	        model_runner_output: ModelRunnerOutput,
3334	    ) -> dict[int, Any]:
3335	        if scheduler_output.batch_type == BatchType.PREFILL_LAST:
3336	            # Phase B（设计 §5.2）：PL 完成不再无条件释放 prefill 槽，改
3337	            # 为消费 PL 哨兵后按 pending 决定。若本次 PL 输出携带
3338	            # deferred draft state（fallback 链起点，task_id == head_token），
3339	            # 链将在 EngineCore 的 _advance_edge_cloud_draft 中入队——
3340	            # 须保持槽占用，否则其入队后派发的 PDFF 会写到已归还的
3341	            # 通道上。
3342	            # 同 turn 原子性（review Bug 3）：本函数与
3343	            # _advance_edge_cloud_draft 在 EngineCore 同一 step 内先后
3344	            # 执行（patch_engine_core.py update_from_output 之后立即
3345	            # _advance），has_fallback_chain 为真 ⇒ 同 turn 内
3346	            # enqueue_draft_first 必然补 +1（槽记账与 §5.5 per-req 计数
3347	            # 皆依赖此配对）；若 _advance 因 use_spec_decode/state 缺失
3348	            # 早退，worker 亦不会产
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 21:25:33</sup>


---

## Assistant <sup>2026/8/14 21:25:33</sup>

找到了关键线索。第 3380-3384 行的注释直接解释了 PP 机制。我来确认一下 `draft remote-pending` 的递减过程，以明确说明为什么 MTP 会打破流水线。


---

## Assistant <sup>2026/8/14 21:25:34</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 35,
  "offset": 3421
}
```

</details>


---

## User <sup>2026/8/14 21:25:34</sup>

<details>
<summary>Tool Result</summary>

```
3421	        if enqueue_next_draft:
3422	            # 4 域拆分（设计 §5.4）：remote pending 按域各自递减。
3423	            if scheduler_output.batch_type in (
3424	                BatchType.PREFILL_DRAFT_LAST,
3425	            ):
3426	                self.prefill_draft_remote_pending_count = max(
3427	                    0, self.prefill_draft_remote_pending_count - 1
3428	                )
3429	                # Phase B（设计 §5.2）：该步完成，pending -1。finalize
3430	                # 判断推迟到 _enqueue_next_draft_first 之后（fallback 链
3431	                # 的下一步在 PDFL 完成时才入队 +1；此处立即 finalize 会
3432	                # 在下一步入队前提前释放通道）。
3433	                task_id = scheduler_output.draft_task_id
3434	                if (
3435	                    task_id in self._prefill_slot_pending
3436	                    and self._prefill_slot_pending[task_id] > 0
3437	                ):
3438	                    self._prefill_slot_pending[task_id] -= 1
3439	                # 设计 §5.5：running 门控 per-req 计数按链成员（与入队时
3440	          
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/14 21:25:55</sup>


---

## Assistant <sup>2026/8/14 21:26:19</sup>

确认。注释 [pd_separated_scheduler.py:3381-3382](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L3381-L3382) 的注释原话就写明了这个机制。这是完整的 PP 机制。

---

# 不开 MTP 时 queue_len≥2 的 PP 机制

## 核心一句话

**"D首 一完成就立刻释放 inflight 计数 + D首顺手把 D尾预贴进 ready 队列 + D尾本身不占 inflight"**——于是 `D首(N+1)` 能在 `D尾(N)` 还卡在 batch_queue 里阻塞等云中间层时就被调度,实现 **边头(N+1) ∥ 云中(N)+边尾(N)** 的流水,queue 深度自然 = 2。源码注释自己写明了目的:**"消除 Cloud idle gap"**。

## 完整流水(无 MTP),逐步对照代码

设 N 步进行中:

**① 挑 D首(N)** — [pd_separated_scheduler.py:3049-3066](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L3049-L3066)
```
decode_or_draft_inflight_count += 1   # ->1
decode_head_inflight_count   += 1
_force_decode_last = True
_start_decode_last_delay()
decode_last = replace(so, batch_type=DECODE_LAST)
self.decodes_last_ready.append(decode_last)   # ★ D首顺手自贴 D尾,无需 POST_OUT 往返
```

**② EngineCore 立即把 D首 发布给云** — [patch_engine_core.py:844-850](vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py#L844-L850)
`_maybe_publish_pre_out` 对所有 `*_FIRST` 批在 schedule 时就 publish。云提前收到 hidden,**边还没开始跑尾,云就开始算中段**——这是"云不 idle"的关键。

**③ worker 跑 D首(N)** = 边头 forward + isend 给云,返回 EMPTY(快 ~1ms,日志里 `decode_first dequeue ~0.9ms`)。

**④ D首一返回,立刻释放 inflight** — [pd_separated_scheduler.py:3380-3390](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L3380-L3390)
```python
if scheduler_output.batch_type == BatchType.DECODE_FIRST:
    # D首完成后立即释放 inflight 计数,使下一个 D首可以
    # 在 D尾仍在 batch_queue 中时就被调度,消除 Cloud idle gap。
    if self.decode_or_draft_inflight_count > 0:
        self.decode_or_draft_inflight_count -= 1   # ->0,尽管 D尾(N)还没跑
    if self.decode_head_inflight_count > 0:
        self.decode_head_inflight_count -= 1
```
此时 **inflight=0,但 D尾(N) 还在 ready 队列里没执行**。

**⑤ fill loop 继续填,不阻塞** — [patch_engine_core.py:905-910](vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py#L905-L910)
```python
if (scheduled_model_executed
    and len(batch_queue) < self.batch_queue_size
    and not batch_queue[-1][0].done()):   # 最老的那批还没完 → 不 pop 不阻塞
    return None, True                     # 下一轮继续填
```
这就是 `_patched_step_with_batch_queue` 的宗旨([docstring L804-809](vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py#L804-L809)):**"Continuously fill the local worker FIFO before collecting one result"**——趁 worker 还在跑上一批,把下一批预排进 MQ。

**⑥ decode_last_delay 到点,挑 D尾(N)** — [pd_separated_scheduler.py:2967-2978](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L2967-L2978)
```
so = self.decodes_last_ready.popleft()
self._force_decode_last = False          # ★ 清掉 force
# 注意:_pick_decode_last_batch 不碰 inflight_count
```
dispatch。worker 跑 D尾(N) = **recv 云中段(阻塞等云算完)+ 边尾 + 采样**(慢)。

**⑦ D尾(N) 在途(阻塞等云)期间,D首(N+1) 可调度!** — [pd_separated_scheduler.py:1384-1396](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1384-L1396)
```python
def _can_schedule_decode_first(self) -> bool:
    return bool(
        self.running
        and self.decode_or_draft_inflight_count == 0   # ④ 已释放 ✓
        and self.decode_draft_remote_pending_count == 0  # 无 MTP 恒 0 ✓
        and not self.decode_drafts_first_ready
        and not self.decode_drafts_last_ready
        and not self._force_decode_last               # ⑥ 已清 ✓
        and not self._force_decode_draft_last
    )
```
→ EngineCore 填 `D首(N+1)`,dispatch。**queue = [D尾(N) 在跑(阻塞等云), D首(N+1) 已排] = depth 2**。边头(N+1) 与 云中(N) 重叠;云算完 N 中段后,因 ② 已提前收到 N+1 hidden,接着算 N+1 中段,云不 idle。

如此交替 → 稳态 depth 2。

## 日志 0814-2 证据

| 现象 | 含义 |
|---|---|
| `types` 始终在 `['decode_last','decode_first']` ↔ `['decode_first','decode_last']` 交替(depth 2-3) | queue 里始终握着"一个 first + 一个 last",即跨步流水 |
| `dequeue took` first 和 last **都是 ~0.9ms** | worker 每次抓批都有预排好的,生产端领先消费端(对比 0814-1 的 last 5-13ms=worker 空等) |

## 为什么 MTP 把它压回 depth 1

差别全在 `_can_schedule_decode_draft_first` 多一道门 — [pd_separated_scheduler.py:1450-1456](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1450-L1456):
```python
# scheduled(非pregenerated)草稿首:
return bool(
    self.decode_or_draft_inflight_count == 0
    and self.decode_draft_remote_pending_count == 0   # ★ 多这道
    ...
)
```
而 `decode_draft_remote_pending_count`:
- D草稿首 派发时 `+= 1`([L2186](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L2186))
- **只有 D草稿尾 从云返回时才 `-1`**([L3421-3428](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L3421-L3428) 等)

所以 `D草稿首(N+1)` 必须等 `D草稿尾(N)` 从云回来(remote_pending 归 0)才能起 → **草稿链强制串行 → depth 1**。再叠加 `_force_decode_draft_last` 的 首↔尾 强制交替 + `draft_last_delay` 空窗。

**本质对比**:

| | D尾(N) 阻塞等的是什么 | 占 `remote_pending`? | 下一个 D首/草稿首 |
|---|---|---|---|
| 无 MTP | 云**主模型中段** | **否** | 可立即调度 → depth 2 |
| 有 MTP | 云**草稿模型** | **是**(草稿首派发即 +1,草稿尾返回才 -1) | 被卡到草稿尾返回 → depth 1 |

## 时序对比

```
无 MTP (depth 2, 云不 idle):
  edge:  [D首N][D尾N 等云中N........][D首N+1][D尾N+1 等........]
  cloud:        [中段N][中段N+1][中段N+2]...   ← 因 ② 提前收 hidden,无 gap
  queue:     df  dl+df  dl+df  dl+df ...        ← 始终 depth 2

有 MTP (depth 1, 串行):
  edge:  [DD首N][等云草稿N........][DD尾N][DD首N+1][等云草稿N+1........]...
  cloud:        [草稿N][草稿N+1]...            ← 草稿链串行,remote_pending 挡死
  queue:        1     1     1     1             ← 始终 depth 1
```

---

一句话:不开 MTP 时,`D首完成即释放 inflight` + `D首自贴D尾` + `D尾不占inflight` + `主模型中段不算 remote_pending`,让 `D首(N+1)` 能在 `D尾(N)` 等云时提前入队,边/云双向流水填满 → queue≥2;开了 MTP 后,草稿链靠 `decode_draft_remote_pending_count` 串行门控,下一条草稿首必须等上一条草稿尾从云返回,流水被打回 depth 1。

要的话我可以再去翻这套部署里 `decode_last_delay` / `draft_last_delay` 的实际取值和 `async_scheduling` 是否开启,确认 0814-1 走的是 scheduled 还是 async placeholder 路径。


---

## User <sup>2026/8/16 14:23:36</sup>

非边云场景，使能mtp性能是提升的；边云场景，使能mtp性能是下降的，分析原因是mtp在执行时间短，掩盖不了通信，你再具体分析一下


---

## Assistant <sup>2026/8/16 14:25:08</sup>


---

## Assistant <sup>2026/8/16 14:25:39</sup>

你的判断方向是对的，但“执行时间短掩盖不了通信”只是表象之一。把前面的代码分析和两条日志放在一起算账，边云 MTP 变慢其实是**三重效应叠加**：通信被**暴露**、通信被**倍增**、MTP 省的恰恰是边云里**不稀缺的资源**。逐一展开。

---

## 一、先看非边云为什么赚(基准账)

非边云(单机)MTP 的每步成本：

```
T_cycle = T_draft(本地,极小,~1层+head) + T_verify(≈T_fwd,多 num_spec 个 token,略涨)
产出     = A 个 token(A = 接受长度,典型 1.8~2.5)
```

每 token:`T_cycle / A ≈ T_fwd × (1+ε) / A`,只要 A>1 就赚，而且**没有一毫米线上时间**——draft 再小也无妨，因为它不付通信。**省的是算力，系统瓶颈恰好是算力，所以赚。**

## 二、边云为什么亏：三重效应

### 效应 1:流水线塌缩——原本被“藏起来”的通信变成裸露的串行延迟

这是最关键的一条，前两轮已经从代码+日志证实：

- **不开 MTP**:depth-2 流水。`D首完成即释放 inflight`([pd_separated_scheduler.py:3380-3390](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L3380-L3390))+ `D首自贴D尾` + 主模型中段不占 `remote_pending` → `D首(N+1)` 在 `D尾(N)` 等云时提前入队。**边头(N+1) ∥ 云中(N),双向 P2P 被算力盖住**。日志 0814-2:queue 恒 ≥2,dequeue 全 ~0.9ms,边云两侧都满载。
- **开 MTP**:`_can_schedule_decode_draft_first` 多一道 `decode_draft_remote_pending_count == 0`([L1450-1456](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1450-L1456)),该计数**草稿首派发即 +1([L2186](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L2186)),草稿尾从云返回才 -1**。下一条草稿必须等上一条回来 → 链彻底串行 → depth 1。日志 0814-1:queue 恒 1,LAST 批 worker 空等 5~13ms。

也就是说：**不开 MTP 时通信是“零边际成本”(被流水线吃掉)；开 MTP 后同样这条 P2P 变成每步全额串行支付**。通信没变多变少，是“藏”与“露”变了。

### 效应 2:通信次数倍增——每接受 A 个 token 要付 (m+1) 次完整往返

边云里 draft 模块也被层切片，草稿链同样走 边→云→边。日志 0814-1 的稳态序列是 `DDF→DDL→DDF→DDL→…→DF→DL`:

```
每个 MTP 周期 = m 次草稿往返 + 1 次 verify 往返   (m ≥ 1,自回归草稿则更多)
非 MTP 周期   = 1 个流水化步骤/token
```

而且 **draft 与 verify 有硬数据依赖**(verify 的输入就是草稿 token),这两段往返之间也无法重叠。非边云里这两段是背靠背的本地算子，间隔~微秒级；边云里每段都是一次 RTT。

### 效应 3:瓶颈错位——MTP 省的是算力，边云串行后缺的是 RTT

把每步拆开看边云 decode 的算力构成：decode batch 只有几个 token,步骤计算是**访存受限**(搬权重)，大头在云侧中段；而 MTP 草稿模块只有 ~1 层 + head,**云侧草稿计算 <1ms**。于是每个草稿往返里：

```
RTT_draft ≈ 边头(~1ms) + 上行 P2P + 云草稿(<1ms) + 下行 P2P + 边尾(~1ms) + draft_last_delay(5ms 下限)
         ≈ 几乎纯通信
```

这正是你说的“**MTP 执行时间短，掩盖不了通信**”——但注意因果的方向：不是“短”本身有害，而是**短意味着 RTT 里没有可重叠的算力去填管道，同时串行门控又禁止别的工作来填**。系统从算力瓶颈变成了 RTT 瓶颈，此时：

- 不开 MTP:省不了算力，但算力本来就不是瓶颈——流水线让每 token ≈ max(边段， 云段)，很便宜；
- 开 MTP:省了 verify 步数(算力)，但算力不稀缺；**多付的 RTT 却是唯一稀缺资源** → 净亏。

## 三、量化对账(用两条日志的指示值)

| | 0814-2(无 MTP) | 0814-1(有 MTP) |
|---|---|---|
| queue 深度 | 2(流水满) | 1(锁步) |
| worker 每步等待 | ~0.9ms(批已预排) | 5~13ms(等云) |
| 每周期构成 | DF+DL 流水化，边云重叠 | m×(DDF+DDL) + DF+DL,全串行 |
| 每周期指示耗时* | ~2-4ms | ~11ms/草稿步 + ~11ms/verify |
| 云侧利用率 | 持续有活(HEAD 预发布) | 算 <1ms 草稿 → 闲 ~9ms |

*注：日志的 `dequeue took` 是等待而非执行时间，周期时长是由等待+流水节奏推出的指示值，不是实测执行耗时。

粗算：A≈2 时，MTP 每 token ≈ (11+11)/2 ≈ 11ms;非 MTP 每 token ≈ 2-4ms。**约 3~5 倍劣化**，和你观察到的“性能下降”量级吻合。

## 四、判据：边云 MTP 什么时候才可能不亏

```
A × T_pipe  >  m×RTT_draft + RTT_verify
```

代入:`T_pipe ≈ max(C_edge, C_cloud)`(通信已隐藏)，`RTT ≈ 2L + C + delay`。边云 MTP 翻身的必要条件：

1. **云中段很贵**(大模型、长上下文、大 batch)→ 左边变大。单请求短序列 decode 恰好是最不利场景；
2. **接受率高**(A→3+)→ 草稿质量好；
3. **L 和 delay 小** → 链路快、`draft_last_delay`/`decode_last_delay` 压低；
4. **草稿步数 m=1**(一次并行出多 token,而不是自回归多步往返)。

当前日志场景(小 batch decode、L 数 ms、串行链)四条全不满足。

## 五、代码级根因链(汇总)

1. `decode_draft_remote_pending_count == 0` 串行门 → 草稿链零重叠([L1452](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1452));
2. draft→verify 数据依赖 → 两段往返也串行；
3. 流水线 depth 2→1 → 边云双侧 idle(日志实证)；
4. `draft_last_delay`(5ms)/`decode_last_delay`(15ms)每步强制空窗([layer_slice_config.yaml](vllm-ascend-pdmix/vllm_ascend/core/layer_slice_config.yaml));
5. prefill 期每个中间 chunk 跑完整草稿链只为填 MTP KV(`draft_output_req_ids == ()`),纯开销往返；
6. deferred-draft KV retention 推迟块释放，内存周转变差；
7. 小 batch 下每步固定开销(调度、序列化、MQ、通道校验)被摊到更少的 token 上，MTP 还增加了步数。

## 六、优化方向(按预期收益排序)

1. **草稿模块整体放边侧**：MTP head 本来就 ~1 层，若层切片把草稿层划给边段，draft 变成本地算子(0 RTT),只有 verify 走边云——这直接消掉效应 2 的大头，是最根本的修法；
2. **开 async scheduled-MTP 占位链**(`fill_async_mtp_placeholders`):一个 EngineCore turn 把整条 draft 占位链 materialize,pregenerated 路径走 `decode_head_inflight_count` 门控([L1434-1444](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1434-L1444)),可部分恢复流水——日志 76-90 行 len 能到 2-3 就是它；
3. **抬 `decode_draft_remote_pending_limit`**(默认 2)允许草稿步在云侧多在途，配合 2 才有效(数据依赖仍在，收益有限)；
4. **多请求并发填管道**：单请求串行是死穴，多请求的 draft/verify 交错才能真正填满 RTT——这也是测性能时最该控制的变量；
5. **压 delay 窗**：链路快的前提下调低 `draft_last_delay`/`decode_last_delay`;
6. **场景路由**：短序列/小 batch 走非 MTP,长上下文(云中段贵、A×T_pipe 大)才开 MTP——按上面的判据动态开关。

---

**一句话总结**：非边云里 MTP 用“极便宜的本地 draft”换“少跑 verify”,稳赚；边云里这同一条 draft 变成一次全额 RTT,串行门控又把原来 depth-2 流水线对通信的隐藏拆掉了——MTP 省的是不缺的算力，多付的是唯一稀缺的往返时延，所以性能不升反降。你说的“执行时间短掩盖不了通信”是对的，完整的表述是：**短的执行时间 × 串行的链 = RTT 里既没有算力可填，也没有别的工作可填**。


---

## User <sup>2026/8/16 14:42:53</sup>

你先阅读一下 C:\theroadtofree_github\vllm-ascend\docs\PDbatch分离边云协同多实例调度详细设计.md中  边侧尾recv和计算分开，增加worker层调度方案


---

## Assistant <sup>2026/8/16 14:43:09</sup>


---

## Assistant <sup>2026/8/16 14:43:10</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "ls -la \"C:/theroadtofree_github/vllm-ascend/docs/PDbatch分离边云协同多实例调度详细设计.md\" 2>/dev/null; wc -l \"C:/theroadtofree_github/vllm-ascend/docs/PDbatch分离边云协同多实例调度详细设计.md\" 2>/dev/null",
  "description": "Check design doc existence and line count"
}
```

</details>


---

## User <sup>2026/8/16 14:43:11</sup>

<details>
<summary>Tool Result</summary>

```
-rw-r--r-- 1 root 197121 61975 Aug 15 11:34 C:/theroadtofree_github/vllm-ascend/docs/PDbatch分离边云协同多实例调度详细设计.md
840 C:/theroadtofree_github/vllm-ascend/docs/PDbatch分离边云协同多实例调度详细设计.md
```

</details>


---

## Assistant <sup>2026/8/16 14:43:19</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "C:\\theroadtofree_github\\vllm-ascend\\docs\\PDbatch分离边云协同多实例调度详细设计.md"
}
```

</details>


---

## User <sup>2026/8/16 14:43:19</sup>

<details>
<summary>Tool Result</summary>

```
1	# PD batch 分离边云协同推理 - 多实例调度详细设计
2	
3	> 本文档将边云 PD 分离架构从 **"1 边 : 1 云"** 扩展为 **"1 边 : N 云"**（N 个云实例）。
4	> 目标是提升边侧算力利用率：边侧 1–2 卡只做 embedding + 首 x 层 + 尾 x 层，
5	> 在 1:1 时长期空闲等待云侧中间层；引入 N 个云实例后，边侧作为 N 流共享的单一首/尾处理器，
6	> 在一个实例的尾层等待云回包期间，可首层喂给另一个实例，从而把边侧空闲窗口填满。
7	>
8	> **多实例 N 是与现有 data_parallel_size(D) 正交的新维度**：实例间松耦合、请求级分发、
9	> **无集合通信**；实例内部保留现有 dp+tp / tp 配置与跨 DP batch_type 协调不变。
10	> N 间无集合通信可乱序；D 内（2DP）紧耦合 EP all-toall 配对。
11	>
12	> 适用前提：本文档为**方案设计阶段**（不修改代码）。所有结论均经代码核实，引用处标注文件:行号。
13	
14	---
15	
16	## 0 术语与上下文
17	
18	| 术语 | 含义 |
19	|------|------|
20	| **N** | 云实例数（新维度）。边侧 1 个、云侧 N 个实例 |
21	| **D** | data_parallel_size，实例内 DP 并行度（现有，如 dp=2） |
22	| **C** | cloud_npu_count，每实例云侧 TP 卡数 |
23	| **E** | 边侧 rank 数：shared-model 1 卡 E=1（1 进程 host D virtual）；per-rank 2 卡 E=D |
24	| **实例** | 一个完整的云侧 deployment（含 D×C 个云 rank），端到端承载一组请求的中间层 |
25	| **PF/PL/DF/DL** | PREFILL_FIRST / PREFILL_LAST / DECODE_FIRST / DECODE_LAST 四段独立调度 |
26	| **HEAD batch** | FIRST 段（PF/DF）：边侧首层 forward + isend 到云 |
27	|
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:43:57</sup>


---

## Assistant <sup>2026/8/16 14:44:18</sup>

已通读全文(840 行)。这份文档是把边云从 **1 边：1 云扩展到 1 边：N 云**的多实例调度设计，你指的“**边侧尾 recv 和计算分开，增加 worker 层调度**”就是 §5.2(worker 层异步调度，核心改造)+ §5.3(2DP 协调论证)+ §5.3.5/§5.3.6(per-rank 两卡两种方案)。以下是我消化后的理解。

---

## 一、方案本质：把 TAIL 的“等云”和“算尾层”拆开

**现状的病根**(§5.2.1):TAIL 在 round barrier 后同步 drain,唯一阻塞点在：

```
drain_batched_round
  ① deferred() -> AsyncIntermediateTensors   (irecv 已发起、未 wait)   ← 本来就是异步的 ✅
  ② execute_model_batched_tail -> it["hidden_states"]
       -> wait_for_comm -> handle.wait()                                  ← 阻塞在这 ❌
```

即：**irecv 本来就不阻塞，阻塞的是"取 hidden 前的 wait_for_comm"**。worker 一进尾层计算就必须等云回包到齐，整个进程挂起，什么都干不了——这正是我们前几轮在日志里看到的“LAST 批 worker 空等 5~13ms”的代码级根源。

**改造思路**：利用 `irecv` 已异步这一点，补一个**非阻塞就绪检测**(irecv 后在 `_HC_STREAM_RECV` 流上 record NPU event,`event.query()` 轮询，不依赖不确定的 HCCL Work.is_completed),然后把“收到 TAIL”和“执行尾层计算”解耦：

```
改造后 worker_busy_loop 每循环:
  ① poll pending_tails:哪个实例的 hidden 就绪(2DP 齐)→ 就地 batched_tail
  ② MQ poll + dispatch:TAIL 只做 irecv+record_event,存 pending,不阻塞
  ③ round barrier 放宽:不要求 TAIL drain,2DP dispatch 完即开新 round
```

**收益落点**(§5.2.4):实例 i 的 TAIL 等 hidden 期间，worker 不挂起，继续 dispatch 实例 j 的 HEAD;等 event ready 再回头做实例 i 的尾层。这就是“边侧作为 N 流共享的单一首/尾处理器，用实例 j 的首层填实例 i 等回包的空闲窗口”(§0 开篇的目标)。

## 二、六个改造点(§5.2.3)

| # | 位置 | 改造 |
|---|------|------|
| 1 | `edge_cloud_irecv_tensor_dict` | irecv 后在 `_HC_STREAM_RECV` 流内 record NPU event,返回 +event |
| 2 | `AsyncIntermediateTensors` | 加 `_comm_event` + `is_ready()=event.query()`;`wait_for_comm` 不变(就绪后调立即返回) |
| 3 | 新增 `pending_tails` | `dict[instance_id, deque[TailEntry]]` |
| 4 | `drain_batched_round` 步骤② | 删除立即调 `execute_model_batched_tail`,改存 pending;步骤①不变 |
| 5 | `worker_busy_loop` | 每循环新增 poll 阶段(MQ poll 之前)，队首 2DP 全 is_ready 才 popleft 执行尾层 |
| 6 | round barrier | 放宽：TAIL 异步存 pending;HEAD round(head+isend 同步)不变 |

## 三、正确性/约束的三根硬骨头

1. **2DP lockstep 语义平移**(§5.2.5/§5.3.2):同步点从 round barrier 挪到“**recv 就绪**"——不是 forward。实例内不乱序(deque 队首未就绪不跳队，保 token 序+云 bt 配对)，实例间乱序(独立队列独立 poll)。shared-model 下尾层是 **leader 1× 代算**(2DP hidden cat 后 leader 单独 forward),所以本来就不存在“2DP 各自 forward 要同步”的问题，barrier 换 poll 语义等价。

2. **NPU event ≠ recv 完成**(§5.2.6,标了"关键正确性")：event 只盖 irecv 传输本身；merge fast path 之后还有 CPU 驱动的 postprocess 链(TP broadcast 集合通信 + `_split_into_dict` + sp_chunk 拆分)，其中 `_record_recv_buffer_on_consumer_stream` 被跳过会导致 allocator 提前复用 buffer = 数据错乱。**event-only 判定只在 TP=1 且无 SP 时安全**；否则 lockstep 锚点要上移到“postprocess 完成”(event ready 后主线程先串行跑 postprocess 再 forward)。

3. **重叠深度天花板在 EngineCore 层**(§5.3.4):worker 层解除 `wait_for_comm` 后，**batch_queue collect + coord all_reduce 的 2DP 同步仍是硬约束**——异步重叠深度 = batch_queue_size − 1 = pp_size − 1 = **1**(边云 PP=2)。实例 i 的 tail 延迟期间 EngineCore 最多再填 1 个(实例 j)。**worker 层单独突破不了，要配合调大 batch_queue_size**(代价是 inflight/内存/KV 压力，§7.2)。

## 四、per-rank 两卡的两个分支

- **§5.3.5 worker 层 gloo lockstep**:每卡各自 forward、EP=2 跨 2DP,死结是“dp0 先 forward → EP all-toall 阻塞等 dp1 → dp0 卡死"。解法 = 跨进程 gloo isend/irecv 交换 ready_flag(含 instance_id/head_token 防串配),本地 event ready AND 对端 ready 才同时 forward。**只有 irecv 阶段能重叠，forward 阶段因 EP all-toall 仍阻塞**。
- **§5.3.6 scheduler 驱动 + worker 监控线程**(替代方案)：irecv 就绪检测移到 worker 进程内监控线程，**recv 任务不进 batch_queue**;scheduler 在调度 first 后**立即**下发 last recv(irecv 提前到云 isend 之前 pending,重叠云中间层计算);POST_OUT(控制面)+ irecv ready(数据面，coord all_reduce 扩展 recv_ready 做 2DP 交换)**双重 gate**后才调度 last forward,此时 `wait_for_comm` 立即返回。相对 §5.3.5 的三个关键改进：irecv 提前、forward 不 wait、不引入 worker gloo。

## 五、和我们前面 MTP 分析的直接关联

这份设计其实正面接上了前面定位的边云 MTP 劣化问题，两处强相关：

1. **§3.4 的 MTP pinning 红线**："draft/MTP verify batch 必须继承请求 pinning(关键)——DL tail 产出的 draft token 及其 KV 驻留在云实例 i,verify(DRAFT_FIRST)必须路由回实例 i;若 verify batch 重组时丢 instance 标注按负载重分发，draft KV miss → verify 全拒收(accept=0),**MTP 退化为纯开销**"。§7.3 风险表也把它列为"效率(严重退化)"级。这正是多实例下 MTP 的第一颗雷。
2. **多实例是对“RTT 里没活可填”的直接回应**：我们之前的结论是“串行链 = RTT 里既没有算力可填、也没有别的工作可填”，优化方向第 4 条就是“多请求/多流并发填管道"。§5.2 的 worker 层调度 + N 实例 = 用**实例 j 的 HEAD** 填**实例 i 的等回包窗口**，把单流的串行 RTT 变成 N 流时分复用。但注意两点：**(a)** 它填的是跨实例窗口，单实例内 MTP 草稿链的 `decode_draft_remote_pending_count == 0` 串行门控(请求级)这个方案本身不动；**(b)** 重叠深度受 batch_queue_size=PP-1=1 限制，N 实例的收益要放大必须同步调 batch_queue_size。

---

已读完并建立好与前面分析的联系。你接下来是想深入讨论哪部分——比如这个 worker 层方案对 MTP 场景的具体收益边界、§5.2.6 的 SP postprocess 正确性问题、还是多实例下 MTP 调度(草稿链 pinning / remote_pending 门控在 N 实例下的语义)？


---

## User <sup>2026/8/16 14:47:49</sup>

不考虑多实例和多dp，当前mtp没有单独的数据通道，首先为mtp创建单独的数据通道，然后增加边侧尾 recv 和计算分开，增加 worker 层调度，enginecore的scheduler调度针对此场景优化可以下发其他任务，mtp场景的收益有多大


---

## Assistant <sup>2026/8/16 14:48:48</sup>

---

**⟫ Conversation compacted (auto) — 167,854 tokens before compact**

---


---

## User <sup>2026/8/16 14:48:48</sup>

<details>
<summary><b>Compact Summary (auto-generated context from previous conversation)</b></summary>

This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.

Summary:
1. Primary Request and Intent:
   The user is investigating MTP (Multi-Token Prediction / speculative decoding) scheduling behavior in vllm-ascend edge-cloud (边云) collaborative inference. The conversation progressed through five explicit requests, all in Chinese, all analysis-oriented (no code changes requested):
   
   a. Explain how MTP is scheduled in vllm-ascend edge-cloud scenarios, specifically the meaning of 8 terms: prefill_first, prefill_last, decode_first, decode_last, mtp prefill_first, mtp prefill_last, mtp decode_first, mtp decode_last.
   
   b. Analyze actual scheduling log C:\kisella_mtp\log\0814-1.txt (MTP enabled) — why does batch_queue persistently show queue_len=1?
   
   c. Compare with C:\kisella_mtp\log\0814-2.txt (MTP disabled, queue_len stays ≥2) — explain the PP (pipeline parallel) mechanism that achieves this.
   
   d. Analyze why MTP improves performance in non-edge-cloud scenarios but degrades it in edge-cloud; user's hypothesis: “MTP execution time is short, cannot cover/hide the communication” (mtp在执行时间短，掩盖不了通信) — asked for deeper concrete analysis.
   
   e. (MOST RECENT) Read C:\theroadtofree_github\vllm-ascend\docs\PDbatch分离边云协同多实例调度详细设计.md, specifically the section “边侧尾recv和计算分开，增加worker层调度方案” (separating edge-side tail recv and compute, adding worker-layer scheduling). I read the full document but had NOT yet provided my analysis to the user when the summary request arrived.

2. Key Technical Concepts:
   - Edge-cloud layer slicing: model split into edge head (segment_a) + cloud middle layers (dynamically sliced per layer_slice_config.yaml) + edge tail (segment_e + sampler)
   - FIRST/LAST two-round execution: FIRST = edge head forward + isend to cloud (returns EMPTY); LAST = recv from cloud + edge tail + logits + sampler
   - BatchType enum (8 edge-cloud types): PREFILL_FIRST/LAST, DECODE_FIRST/LAST + 4 MTP DRAFT variants (PREFILL_DRAFT_FIRST/LAST, DECODE_DRAFT_FIRST/LAST); "draft" = MTP draft chain
   - 4 config layers: L1 BatchType enum, L2 pd_scheduling_policy (SchedulerConfig), L3 cloud-side DispatchPolicy (expect_alternation/prefill_first/decode_first/pdmix_first + CloudUndesiredState 3-state machine), L4 ascend PDSeparationConfig (edge knobs)
   - _pick_by_state priority dispatch: IDLE (prefill_draft首 > prefill_draft尾 > P首 > decode_draft首 > decode_draft尾 > D首 > D尾 > P尾), LOW, HIGH variants
   - Inflight gating: decode_or_draft_inflight_limit=1 (hardcoded); decode_draft additionally gated by decode_draft_remote_pending_count==0 (only cleared when draft_last returns from cloud)
   - PP depth-2 pipeline (no MTP): DECODE_FIRST completion immediately releases inflight (“消除 Cloud idle gap”); decode_first self-posts decode_last; decode_last doesn't hold inflight → decode_first(N+1) schedulable while decode_last(N) blocks on cloud
   - batch_queue mechanics: appendleft (newest front) + pop (oldest back) = FIFO; types list newest-first; _patched_step_with_batch_queue "fill worker FIFO before collecting one result"; one-schedule-per-turn break; `not batch_queue[-1][0].done()` early return
   - "dequeue took" log semantics: measures time inside dequeue() BEFORE execution → large value = worker idle-waiting (producer-throttled)
   - Delay windows: decode_last_delay (15ms), draft_last_delay (5ms), prefill_middle_throttle (500ms)
   - MTP edge-cloud degradation: 3 effects — pipeline collapse (communication exposed), communication multiplication ((m+1) RTTs per accepted batch), bottleneck mismatch (MTP saves compute which isn't scarce; pays RTT which is)
   - Win condition formula: A × T_pipe > m×RTT_draft + RTT_verify (A = accept length)
   - Multi-instance design (1:N): per-instance HiddenChannelManager, leader InstanceDispatcher, request pinning, draft/verify must inherit instance pinning, G0-G5 process groups, per-instance KV partitioning
   - Worker-layer async scheduling design: irecv + NPU event polling (torch.npu.Event, event.query()), pending_tails per-instance deques, AsyncIntermediateTensors._comm_event + is_ready(), relaxed round barrier, 2DP lockstep on readiness (shared-model: leader 1× tail, EP=1; per-rank 2-card: gloo isend/irecv ready_flag or scheduler-driven monitor thread with dual gate POST_OUT AND recv_ready)
   - SP postprocess chain risk: NPU event only covers irecv, not TP broadcast + _split_into_dict + _apply_sp_chunk_inplace (safe only when TP=1, sp_chunk=1)

3. Files and Code Sections:
   - c:\kisella_mtp\vllm-pdmix\vllm\v1\core\sched\output.py (L105-149)
     - BatchType enum definition with docstrings; the authoritative mapping of user's 8 terms
     - PREFILL_FIRST="prefill_first" ... DECODE_DRAFT_LAST="decode_draft_last"
   - c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py (THE core file, ~3500+ lines)
     - L245: `self.decode_or_draft_inflight_limit: int = 1` (hardcoded)
     - L1148-1320: _pick_by_state priority dispatch (IDLE/LOW/HIGH)
     - L1371-1456: _can_schedule_prefill_first/_can_schedule_decode_first/_can_schedule_prefill_draft_first/_can_schedule_decode_draft_first
     - L1450-1456: draft gate requires `decode_or_draft_inflight_count == 0 AND decode_draft_remote_pending_count == 0`
     - L2186-2189: draft pick increments remote_pending and inflight, sets _force_decode_draft_last, starts draft_last_delay
     - L2967-2978: _pick_decode_last_batch — clears _force_decode_last, does NOT touch inflight
     - L3018-3066: _pick_decode_first_batch — increments both counters, self-posts decode_last to decodes_last_ready (“Decode-first self-posting optimization”)
     - L3380-3390: THE smoking gun:
       ```python
       if scheduler_output.batch_type == BatchType.DECODE_FIRST:
           # D首完成后立即释放 inflight 计数，使下一个 D首可以
           # 在 D尾仍在 batch_queue 中时就被调度，消除 Cloud idle gap。
           if self.decode_or_draft_inflight_count > 0:
               self.decode_or_draft_inflight_count -= 1
           if self.decode_head_inflight_count > 0:
               self.decode_head_inflight_count -= 1
       ```
     - L3421-3428: draft_last returns → remote_pending decremented per domain
   - c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_engine_core.py
     - L803-919: _patched_step_with_batch_queue (fill loop, appendleft L890, log L895, one-per-turn break L901-911, pop+future.result() block L919-924)
     - L709-732: _has_unresolved_edge_cloud_draft_parent
   - c:\kisella_mtp\vllm-pdmix\vllm\v1\executor\multiproc_executor.py
     - L1204-1237: EDGE-DEQUEUE log — `_t0` before dequeue(), `_dt_ms` measured after; proves "dequeue took" = wait time, not execution time
   - c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\passive_scheduler.py (L34-58)
     - Cloud-side DispatchPolicy enum + CloudUndesiredState 3-state machine
   - c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\ascend_config.py (L883-964)
     - Edge-side PDSeparationConfig: next_prefill_prior_enable (2P1D/1P1D), chunk_prefill_prior_enable, max_chunk_prefill_ahead, prefill_draft_remote_pending_limit=2, decode_draft_remote_pending_limit=2, prefill_draft_last_watchdog_seconds=30
   - c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\layer_slice_config.yaml
     - Dynamic cloud layer slicing thresholds + decode_last_delay_schedule_ms: 15, draft_last_delay_schedule_ms: 5, prefill_middle_throttle_ms: 500
   - c:\kisella_mtp\vllm-pdmix\docs\pd_separation_modification_plan.md
     - Design doc explaining FIRST/LAST split, _FirstRoundMarker/_LastRoundMarker, cross-round state caching
   - c:\kisella_mtp\vllm-pdmix\vllm\config\scheduler.py (L158-162)
     - pd_scheduling_policy Literal field
   - C:\kisella_mtp\log\0814-1.txt (90 lines): MTP-on log; queue_len=1 steady state lines 46-74; LAST dequeue 5-13ms
   - C:\kisella_mtp\log\0814-2.txt (57 lines): MTP-off log; queue_len 2-4; types alternate ['decode_last','decode_first']↔['decode_first','decode_last']; all dequeue ~0.9ms
   - C:\theroadtofree_github\vllm-ascend\docs\PDbatch分离边云协同多实例调度详细设计.md (840 lines, MOST RECENT READ)
     - Multi-instance (1 edge : N cloud) scheduling design doc
     - §5.2: worker-layer async scheduling — blocking point drain_batched_round (shared_model_edge_worker.py:367) ② execute_model_batched_tail:417 → wait_for_comm → handle.wait() (gpu_worker.py:97); 6 modification points: (1) edge_cloud_irecv_tensor_dict (:1416) record NPU event in _HC_STREAM_RECV ctx, (2) AsyncIntermediateTensors (gpu_worker.py:73) add _comm_event + is_ready()=event.query(), (3) new pending_tails dict[instance_id, deque[TailEntry]], (4) drain step ② stores to pending instead of immediate call, (5) worker_busy_loop (:334) poll phase before MQ poll, (6) round barrier (:485) relaxed
     - §5.2.5: 实例内不乱序 (deque head-block), 实例间乱序， 2DP lockstep = 队首 all(is_ready)
     - §5.2.6: SP/merge_payload postprocess (TP broadcast :1724-1730 + _split_into_dict :1733 + _apply_sp_chunk_inplace :1631) NOT covered by NPU event — event-only safe only when TP=1 & sp_chunk=1
     - §5.3.1-5.3.4: shared-model 1-card — tail is leader 1× 代算 (merged_hidden cat :1058, _model_forward :1222), EP=1, sync point is recv-readiness not forward; EngineCore overlap depth = batch_queue_size − 1 = 1
     - §5.3.5: per-rank 2-card — each card forwards own tail with EP=2 all-toall (blocking); cross-process 2DP lockstep via gloo isend/irecv ready_flag(instance_id/head_token); worker_busy_loop pseudocode with poll ① + MQ poll ②
     - §5.3.6: alternative scheduler-driven + worker monitor thread (_recv_monitor_thread): irecv issued immediately after first (overlaps cloud middle), recv task doesn't enter batch_queue, response_mq "__pp_irecv_ready__" acks, coord all_reduce extended with recv_ready, dual gate (POST_OUT last SO AND irecv complete), tail forward reads _recv_store without waiting
     - §3.4: InstanceDispatcher (leader dp0) decides HEAD instance; TAIL instance = cloud as-arrived; draft/MTP verify MUST inherit request pinning else draft KV miss → accept=0 → MTP pure overhead
     - §6: per-instance KV partition (per_dp_num_blocks/N), R ratios, N*=R flip point, instance cap ~4
     - No edits were made to any file in this entire conversation — all work was reading/analysis.

4. Errors and fixes:
   - Initial misinterpretation of "dequeue took": I first interpreted large values (5-13ms for LAST) as execution time including cloud round-trip. After reading multiproc_executor.py:1204-1208 I corrected: it measures time INSIDE the dequeue() call (waiting for next item) BEFORE func() execution — large value = worker IDLE, producer-throttled. This correction flipped the bottleneck direction analysis (producer-limited, not consumer-limited) and was communicated in the answer.
   - Initial conflation of the 8 policy terms with just the BatchType enum: The second background agent surfaced (and I verified) that "prefill_first/decode_first" strings appear in 4 distinct config layers including a separate cloud-side DispatchPolicy. I issued an explicit correction supplement (“重要补充：这8个词其实跨4层配置”).
   - Queue discipline confusion: while tracing log types lists I initially mismatched FIFO order; resolved by reading patch_engine_core.py (appendleft L890 + pop L919) proving FIFO with newest-first display.
   - One background agent (edge-cloud deep-read, agent a2be6cf1848833fed) never returned results within the conversation; I explicitly noted to the user that its execution-side findings (batched_model_runner reorder, pcp_utils, llm_base_proposer) were still pending and never fabricated them.

5. Problem Solving:
   - Fully mapped the 8 BatchTypes to user's terminology (mtp xxx = *_DRAFT_* variants) with docstring evidence.
   - Root-caused batch_queue=1 (MTP on): producer throttled by decode_or_draft_inflight_limit=1 + remote_pending==0 gate + one-schedule-per-turn + pop/future.result() block + forced ddf→ddl alternation + delays; worker starves (5-13ms idle waits).
   - Root-caused queue≥2 (MTP off): PP depth-2 pipeline via inflight-release-at-DECODE_FIRST-completion + self-posted decode_last + decode_last not holding inflight → decode_first(N+1) overlaps decode_last(N)'s cloud wait (“消除 Cloud idle gap”).
   - Explained MTP edge-cloud degradation with 3-effect model + win-condition inequality A × T_pipe > m×RTT_draft + RTT_verify, log-based estimate ~3-5x degradation, 6 optimization directions (draft module on edge as most fundamental).
   - Read the multi-instance design doc; analysis of its worker-layer scheduling scheme is the current work.

6. All user messages:
   - “vllm-ascend边云场景，mtp是如何调度的，prefill_first、prefill_last、decode_first、decode_last、mtp prefill_first，mtp prefill_last、mtp decode_first、mtp decode_last”
   - “C:\kisella_mtp\log\0814-1.txt是实际调度情况，为什么batch_queue会出现持续为1情况”
   - “C:\kisella_mtp\log\0814-2.txt 是不开mtp的，queue_len能保持不低于2，这个pp并行的机制”
   - “非边云场景，使能mtp性能是提升的；边云场景，使能mtp性能是下降的，分析原因是mtp在执行时间短，掩盖不了通信，你再具体分析一下”
   - “你先阅读一下 C:\theroadtofree_github\vllm-ascend\docs\PDbatch分离边云协同多实例调度详细设计.md中  边侧尾recv和计算分开，增加worker层调度方案”
   (No security-relevant instructions or constraints were stated by the user in any message.)

7. Pending Tasks:
   - Respond to the user with an analysis/explanation of the “边侧尾recv和计算分开，增加worker层调度方案” (edge-side tail recv/compute separation + worker-layer scheduling) section of the multi-instance design document — the document has been read in full but no analysis has been delivered yet.
   - (Previously noted as outstanding, lower priority): the first background agent's execution-side findings (batched_model_runner._apply_decode_first_reorder / execute_model_tail_pre, shared_model_edge_worker head/tail markers, pcp_utils PCP, llm_base_proposer draft generation) never arrived; verification of actual decode_last_delay/draft_last_delay deployment values and whether async_scheduling is enabled was offered but not requested.

8. Current Work:
   Immediately before this summary request, I had just finished reading the full 840-line design document C:\theroadtofree_github\vllm-ascend\docs\PDbatch分离边云协同多实例调度详细设计.md per the user's instruction “你先阅读一下...边侧尾recv和计算分开，增加worker层调度方案”. The document describes extending edge-cloud from 1:1 to 1:N cloud instances, with the specifically-requested worker-layer scheduling content in §5.2 (six modification points for async tail: irecv + NPU event on _HC_STREAM_RECV, AsyncIntermediateTensors.is_ready(), pending_tails per-instance deques, deferred tail execution, worker_busy_loop poll phase, relaxed round barrier), §5.2.6 (SP postprocess correctness risk), §5.3.1-5.3.4 (shared-model 1-card feasibility: leader 1× tail, EP=1, overlap depth = batch_queue_size−1 = 1), §5.3.5 (per-rank 2-card cross-process gloo lockstep), and §5.3.6 (scheduler-driven + worker monitor thread alternative with dual gate and early irecv). The read completed successfully but I had NOT yet composed or delivered my analysis of this document to the user — that response is the immediate outstanding deliverable.

9. Optional Next Step:
   Compose and deliver the analysis of the requested document section, directly answering the user's most recent message: “你先阅读一下 C:\theroadtofree_github\vllm-ascend\docs\PDbatch分离边云协同多实例调度详细设计.md中 边侧尾recv和计算分开，增加worker层调度方案”. The analysis should cover: the single blocking point (drain_batched_round → execute_model_batched_tail → wait_for_comm → handle.wait()); the 6 modification points (irecv + NPU event, is_ready(), pending_tails, deferred tail, poll phase, relaxed barrier); the cross-round overlap benefit (round k instance-i TAIL pending → round k+1 instance-j HEAD → poll ready → batched tail); the 2DP lockstep-on-readiness semantics; and notably how this worker-layer scheme connects to the earlier conversation findings — it attacks exactly the exposed-communication problem identified in the MTP degradation analysis (moving the tail recv wait off the critical path so the worker can fill other instances' work), while §5.3.4 notes the EngineCore batch_queue_size=2 hard cap on overlap depth and §5.2.6 flags the TP=1/sp_chunk=1-only safety of the event-based readiness check.

If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: C:\Users\root\.claude\projects\c--kisella-mtp\0fd965c5-f091-41ab-b346-446569638fa9.jsonl
Continue the conversation from where it left off without asking the user any further questions. Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar. Pick up the last task as if the break never happened.

</details>


---

## Assistant <sup>2026/8/16 14:50:09</sup>


---

## Assistant <sup>2026/8/16 14:50:10</sup>

先快速核实两个直接影响收益估算的事实：draft_last_delay 是否每轮真实施加、以及 `decode_draft_remote_pending_limit` 这个配置到底有没有被用上。


---

## Assistant <sup>2026/8/16 14:50:10</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-C": 3,
  "-n": true,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-ascend-pdmix",
  "pattern": "draft_last_delay"
}
```

</details>


---

## Assistant <sup>2026/8/16 14:50:12</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-C": 2,
  "-n": true,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-ascend-pdmix",
  "pattern": "decode_draft_remote_pending_limit"
}
```

</details>


---

## User <sup>2026/8/16 14:50:13</sup>

<details>
<summary>Tool Result</summary>

```
c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py-551-        # [MTP] DECODE_DRAFT_LAST delay scheduling (mirrors
c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py-552-        # decode_last_delay)。边侧自生成 decode_draft_last 后延迟 5ms
c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py-553-        # （默认）再调度，保留解码域 pacing（设计 §6.2）。
vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py:554:        self._decode_draft_last_delay_start_ts: float | None = None
vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py:555:        self._decode_draft_last_delay_schedule_ms: int = 15
c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py-556-
c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py-557-        # [MTP] PREFILL_DRAFT_LAST delay scheduling。
c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py-558-        # Phase A：prefill_draft 保持旧行为（边侧自贴尾 + 
...(truncated)
```

</details>


---

## User <sup>2026/8/16 14:50:13</sup>

<details>
<summary>Tool Result</summary>

```
c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\platform.py-387-            pd.prefill_draft_remote_pending_limit
c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\platform.py-388-        )
vllm-ascend-pdmix\vllm_ascend\platform.py:389:        scheduler_config.pd_decode_draft_remote_pending_limit = (
vllm-ascend-pdmix\vllm_ascend\platform.py:390:            pd.decode_draft_remote_pending_limit
c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\platform.py-391-        )
vllm-ascend-pdmix\vllm_ascend\platform.py-392-        # Phase C review: watchdog interval for cloud-published PDFL;
--
vllm-ascend-pdmix\vllm_ascend\ascend_config.py-903-                    "max_chunk_prefill_ahead": 1,
vllm-ascend-pdmix\vllm_ascend\ascend_config.py-904-                    "prefill_draft_remote_pending_limit": 2,
vllm-ascend-pdmix\vllm_ascend\ascend_config.py:905:                    "decode_draft_remote_pending_limit": 2,
vllm-ascend-pdmix\vllm_ascend\ascend_config.py-906-                    "prefill_draft_last_watchd
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:50:17</sup>


---

## Assistant <sup>2026/8/16 14:50:18</sup>

配置项确实生效了(门控是 `< limit=2` 而非 `==0`)。再看一下 `_force` 交替门控和 `decode_drafts_last_ready` 的语义，这决定收益上限：


---

## Assistant <sup>2026/8/16 14:50:18</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 80,
  "offset": 1560
}
```

</details>


---

## User <sup>2026/8/16 14:50:18</sup>

<details>
<summary>Tool Result</summary>

```
1560	            # （[FORCE] can_pick_prefill_draft_first，设计 §6.3.2）；
1561	            # 草稿链可流水：下一个 PDFF 在前一个 PDFL 在飞时即可派发。
1562	            # Phase B（设计 §6.1）：prefill 域已迁出 DECODE 通道，decode
1563	            # 头/标记不再 gate prefill 域。
1564	            return bool(
1565	                self.prefill_draft_remote_pending_count
1566	                < self._prefill_draft_remote_pending_limit
1567	                and not self.prefill_drafts_last_ready
1568	                and self._force.can_pick_prefill_draft_first()
1569	            )
1570	
1571	        # Phase B（设计 §4.1）：scheduled draft head/tail 负载走继承的
1572	        # prefill 通道，不再与 DECODE 通道争用；只保留 prefill 域自身
1573	        # 的 remote pending / 队列交替约束。
1574	        return bool(
1575	            self.prefill_draft_remote_pending_count == 0
1576	            and not self.prefill_drafts_last_ready
1577	            and self._force.can_pick_prefill_draft_first()
1578	        )
1579	
1580	    def _can_schedule_decode_draft_first(self) -> bool:
1581	 
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:50:19</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 30,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "pattern": "class _ForceState|def can_pick_decode_draft_first|def on_pick"
}
```

</details>


---

## User <sup>2026/8/16 14:50:19</sup>

<details>
<summary>Tool Result</summary>

```
241:    def on_pick(
283:    def can_pick_decode_draft_first(self) -> bool:
```

</details>


---

## Assistant <sup>2026/8/16 14:50:21</sup>


---

## Assistant <sup>2026/8/16 14:50:22</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 85,
  "offset": 225
}
```

</details>


---

## User <sup>2026/8/16 14:50:22</sup>

<details>
<summary>Tool Result</summary>

```
225	        self.decode_first_only_deadline: float | None = None
226	        # prefill 域交替：PDFF pick 置位，PDFL pick 解除。
227	        self.prefill_draft_last_pending: bool = False
228	        # prefill 域 first-only 窗口（绝对截止时刻；None = 未激活）。
229	        self.prefill_first_only_deadline: float | None = None
230	
231	        self._decode_first_only_window_ms: int = decode_first_only_window_ms
232	        self._prefill_draft_first_only_window_ms: int = (
233	            prefill_draft_first_only_window_ms
234	        )
235	        # 非 MTP 无链可等：PL 后启动 prefill 窗口只会白白锁住 15ms。
236	        self._prefill_first_only_enabled: bool = prefill_first_only_enabled
237	
238	    # ------------------------------------------------------------------ #
239	    # 事件转移：pick 后通知（batch_type 为实际派发类型）                  #
240	    # ------------------------------------------------------------------ #
241	    def on_pick(
242	        self,
243	        batch_type: BatchType,
244	        *,
245	        prefill_chain_has_more: b
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:51:39</sup>


---

## Assistant <sup>2026/8/16 14:51:59</sup>

两个关键事实已确认，正好支撑收益估算：

1. **`==0` 串行门控存在的原因就是“没有独立通道”**——[pd_separated_scheduler.py:1599-1608](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1599-L1608) 的注释写得很明白：scheduled draft 的 head/tail 载荷**共享 DECODE 通道**，“否则边和云可能互相等对方方向的 send 才 post 匹配的 recv”(会锁死)。所以非预生成 draft 被迫 `inflight==0 AND remote_pending==0` 全串行；而**预生成分支([L1591-1597](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1591-L1597))已经放宽到 `< limit=2` 可流水**——这就是你建独立通道后能解锁的目标语义。
2. **延迟 pacing 真实存在**:DDF pick 后启动 `draft_last_delay`(yaml 5ms / 代码默认 15ms),DDL 到期前不可调度；外加 `_force` 交替门控(DDF pick 后 `decode_draft_last_pending=True`,封死一切 first 类 pick 直到 DDL 被挑走)。

---

## 一、三项改造各自买到什么(机制层)

| 改造 | 解锁的东西 | 代码/设计依据 |
|---|---|---|
| ① MTP 独立数据通道 | `==0` 串行门控的**死锁理由消失**→ draft 链可放宽到 `< limit=2` 流水(预生成分支已是这个语义)；draft 通信不再和普通 P/D 批抢通道、抢 recv buffer | L1599-1608 注释直接说明该门控是共享通道的产物 |
| ② 尾 recv/计算分离 + worker 调度 | worker 不再阻塞在 `wait_for_comm`;等 hidden 期间可以 dispatch/poll 其他活。单独看收益≈0(没活可填时 worker 横竖是闲的)，**它是③的使能器** | 设计文档 §5.2 六个改造点 |
| ③ EngineCore scheduler 优化 | batch_queue 填充、放松 one-schedule-per-turn、DDL 在飞时下发下一个任务——**收益真正的落地点**。但深度受 `batch_queue_size−1` 限制，需同步调大 | §5.3.4;0814-1 里 queue_len=1 的直接病灶 |

## 二、量化：时间线模型

用日志反推的参数：边侧每轮计算 E ≈ 2-4ms(小 batch、边侧切片薄)；云中段+网络往返 W ≈ 8-13ms(0814-1 中 LAST 批 worker 空等 5-13ms 即该窗口全暴露)。设 m=1(一个 draft token),接受长度 A≈1.7(理论上限 m+1=2)。

| 场景 | 每接受 token 时间 | 相对非 MTP |
|---|---|---|
| 非 MTP 现状(PP 已工作，0814-2) | ≈ max(E, W) ≈ **9-12ms** | 1× 基准 |
| MTP 现状(串行+延迟+门控) | (m+1)(E+W+pacing)/A ≈ **15-20ms+** | 劣化 1.5-2×(实测叠加队列坍塌效应到 3-5×) |
| **三项改造后·单请求纯 decode** | 链条仍数据串行(draft token k+1 依赖 k),只省掉 pacing/调度开销：≈ **13-17ms** | **仍劣化 ~1.2-1.4×** |
| **三项改造后·预生成 draft 或有并发请求填窗口** | 每轮 ≈ max(E, W) ≈ 10ms → (m+1)·max(E,W)/A ≈ **11-12ms** | **≈ 打平** |
| 多请求并发(B 路，吞吐) | 窗口被其他请求的 DDF/PF 填满，聚合吞吐 ≈ min(B, W/E ≈ 3-5)×,直到云侧饱和 | 相对当前 MTP 吞吐 **2-4×** |

## 三、必须说透的天花板：这三项改造不减 (m+1)

三项改造修复的是我们之前三效应模型里的**效应①(流水线坍塌)**、大部分**效应②(通信乘法中的暴露部分)**——它把 RTT 从关键路径上“藏”到其他工作后面。但算术上：

1. **每个接受批，云侧仍要执行 m+1 次中段 forward**(m 次 draft 轮 + 1 次 verify 轮)，每次都是全量中间层；
2. 边云场景的瓶颈资源**恰好就是云侧算力+网络**——这正是边云架构成立的前提；
3. 云侧吞吐上限比 = A/(m+1),而 **A ≤ m+1 恒成立**(接受率 100% 才取等)。

所以：**当云是瓶颈时，MTP 吞吐天花板 = 非MTP 的 A/(m+1) ≤ 1**。三项改造把 MTP 从实测 3-5× 劣化拉回到接近打平(高接受率、且有并发/预生成把窗口填满时)，但要**净赢**，光靠这三项不够——必须同时减少每接受 token 的网络往返次数，即之前说的最根本方向：**draft 模块 + draft KV 全落边侧，draft 步 0 RTT**,此时每迭代只剩 1 次 verify 往返，云侧负载比 = 1/A < 1,才是真正的赢面。

## 四、结论(直接回答“收益有多大”)

- **单请求、scheduled draft、纯 decode**:收益约 **1.2-1.5×**(去 pacing + 门控开销)，但 MTP 相对非 MTP 仍略劣——draft 链的数据依赖靠这三项藏不掉，RTT 仍在关键路径上。
- **预生成 draft 或 ≥2-4 路并发请求**：窗口被填满后，MTP 场景吞吐相对当前 **2-4×**,基本追平非 MTP;此时 A>1 的每 token 增益才开始兑现。
- **相对非 MTP 净收益**：≈0 或略负，直到补上第四刀(draft 本地化)。
- 两个落地前提别忘了：§5.2.6 的 NPU event 就绪判定只在 **TP=1 且无 SP** 时安全；重叠深度要调大 **batch_queue_size**(§5.3.4),否则 worker 层解耦了、EngineCore 层还是深度 1。

一句话：这三项是**必要条件，把 MTP 从“明显负资产”修到“盈亏平衡线附近”**；决定它能不能变成正资产的是第四项——draft 链的 RTT 归零。


---

## User <sup>2026/8/16 14:58:07</sup>

目标是先到盈亏平衡线附近，按上述设计方案梳理代码修改方案


---

## Assistant <sup>2026/8/16 14:58:32</sup>


---

## Assistant <sup>2026/8/16 14:58:32</sup>

<details>
<summary>Tool: <code>Glob</code></summary>

```json
{
  "path": "c:\\kisella_mtp",
  "pattern": "**/shared_model_edge_worker.py"
}
```

</details>


---

## Assistant <sup>2026/8/16 14:58:33</sup>

<details>
<summary>Tool: <code>Glob</code></summary>

```json
{
  "path": "c:\\kisella_mtp",
  "pattern": "**/shared_model_multiproc_executor.py"
}
```

</details>


---

## User <sup>2026/8/16 14:58:33</sup>

<details>
<summary>Tool Result</summary>

```
vllm-ascend-pdmix\vllm_ascend\worker\edge_cloud\shared_model_edge_worker.py
```

</details>


---

## Assistant <sup>2026/8/16 14:58:33</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "head_limit": 10,
  "path": "c:\\kisella_mtp",
  "pattern": "edge_cloud_irecv_tensor_dict"
}
```

</details>


---

## User <sup>2026/8/16 14:58:33</sup>

<details>
<summary>Tool Result</summary>

```
vllm-pdmix\vllm\v1\executor\shared_model_multiproc_executor.py
```

</details>


---

## User <sup>2026/8/16 14:58:33</sup>

<details>
<summary>Tool Result</summary>

```
Found 3 files
vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py
vllm-ascend-pdmix\tests\ut\distributed\test_edge_cloud_merge.py
vllm-pdmix\docs\hidden_channel_call_flow_original.md
```

</details>


---

## Assistant <sup>2026/8/16 14:58:36</sup>


---

## Assistant <sup>2026/8/16 14:58:37</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 40,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "pattern": "def edge_cloud_irecv_tensor_dict|def edge_cloud_isend_tensor_dict|_HC_STREAM_RECV|_HC_STREAM_SEND|def wait_for_comm|class AsyncIntermediateTensors|def is_ready|record_stream|Stream\\("
}
```

</details>


---

## User <sup>2026/8/16 14:58:37</sup>

<details>
<summary>Tool Result</summary>

```
69:            stream = torch.npu.Stream()
111:        tensor.record_stream(torch.cuda.current_stream(tensor.device))
113:        tensor.record_stream(torch.npu.current_stream(tensor.device))
1159:def edge_cloud_isend_tensor_dict(
1317:                merged.record_stream(torch.cuda.current_stream(merged.device))
1319:                merged.record_stream(torch.npu.current_stream(merged.device))
1350:                value.record_stream(torch.cuda.current_stream(value.device))
1352:                value.record_stream(torch.npu.current_stream(value.device))
1434:def edge_cloud_irecv_tensor_dict(
1505:                recv_view.record_stream(torch.npu.current_stream(recv_view.device))
1558:                        recv_view.record_stream(
1575:def edge_cloud_isend_tensor_dict_on_hidden_channel(
1592:def edge_cloud_irecv_tensor_dict_on_hidden_channel(
1683:                    tensor.record_stream(
1687:                    tensor.record_stream(
2127:                            tensor.record_st
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:58:37</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 30,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\edge_cloud\\shared_model_edge_worker.py",
  "pattern": "def drain_batched_round|def execute_model_batched_tail|def _dispatch|_pending_deferred|def deferred|wait_for_comm|handle\\.wait"
}
```

</details>


---

## User <sup>2026/8/16 14:58:37</sup>

<details>
<summary>Tool Result</summary>

```
107:    and accumulates them in ``self._pending_deferred``,
338:    def drain_batched_round(
891:                handle.wait()
930:        # callables in ``_pending_deferred`` and invokes them
1007:                handle.wait()
1044:                handle.wait()
1081:                handle.wait()
1109:        the busy_loop in ``_pending_deferred``; the upstream busy_loop
```

</details>


---

## Assistant <sup>2026/8/16 14:58:39</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\edge_cloud\\shared_model_edge_worker.py",
  "limit": 130,
  "offset": 300
}
```

</details>


---

## User <sup>2026/8/16 14:58:39</sup>

<details>
<summary>Tool Result</summary>

```
300	        assert per_dp_hidden is not None, (
301	            "_BatchedExecuteMarker.drive_batched_round called before "
302	            "run_batched_head populated _per_dp_hidden")
303	        # ``_per_dp_hidden`` is keyed by dp_rank (not by position
304	        # in ``batched_dp_ranks``), so the per-dp_rank slice for
305	        # this marker is a direct lookup with the marker's own
306	        # dp_rank.
307	        dp_rank = self.worker.local_rank
308	        hidden_k = per_dp_hidden[dp_rank]
309	        # Edge-cloud with heterogeneous SP: aggregate SP shards to full
310	        # sequence before cross-PP send so cloud can re-chunk by its SP.
311	        if enable_sp() and (self.worker.model_runner.edge_cloud_cfg.mode != "embedding_only"
312	            or not self.worker.model_runner.supports_mm_inputs):
313	            _gathered = self.worker._all_gather_tensor_dict(hidden_k.tensors)
314	        else:
315	            _gathered = hidden_k.tensors
316	        # Mirror ``execute_m
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:58:42</sup>


---

## Assistant <sup>2026/8/16 14:58:42</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "head_limit": 10,
  "path": "c:\\kisella_mtp",
  "pattern": "class AsyncIntermediateTensors|def wait_for_comm"
}
```

</details>


---

## User <sup>2026/8/16 14:58:42</sup>

<details>
<summary>Tool Result</summary>

```
Found 1 file
vllm-pdmix\vllm\v1\worker\gpu_worker.py
```

</details>


---

## Assistant <sup>2026/8/16 14:58:42</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "limit": 160,
  "offset": 1434
}
```

</details>


---

## User <sup>2026/8/16 14:58:42</sup>

<details>
<summary>Tool Result</summary>

```
1434	def edge_cloud_irecv_tensor_dict(
1435	    num_tokens: int,
1436	    src: int | None = None,
1437	    use_alt_group: bool = False,
1438	    channel: HiddenChannelType | None = None,
1439	    include_mrope: bool = True,
1440	) -> tuple[dict[str, torch.Tensor | Any], list[Handle], list[Callable[[], None]]]:
1441	    """Receive tensor dict without metadata sync (edge-cloud optimized).
1442	
1443	    Computes metadata locally from num_tokens + the pre-computed
1444	    EdgeCloudTensorMeta, pre-allocates tensors, then issues irecv
1445	    for each. This eliminates the inter-node pickle+Gloo metadata
1446	    exchange that the standard GroupCoordinator.irecv_tensor_dict
1447	    performs.
1448	
1449	    When SP is enabled, the receive buffer is padded up to the nearest
1450	    multiple of the local TP size.  The sender still transmits only the
1451	    actual ``num_tokens`` rows, so we issue ``irecv`` into a view of the
1452	    first ``num_tokens`` rows of the larger buffer.  This ke
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:58:45</sup>


---

## Assistant <sup>2026/8/16 14:58:46</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 50,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "pattern": "class HiddenChannelType|HIDDEN_CHANNEL|def _hidden_channel_stream_ctx|def _get_edge_cloud_hidden_channel_device_group|alt_group|def _select_edge_cloud_meta_for_recv"
}
```

</details>


---

## User <sup>2026/8/16 14:58:46</sup>

<details>
<summary>Tool Result</summary>

```
79:def _hidden_channel_stream_ctx(
515:def _select_edge_cloud_meta_for_recv() -> EdgeCloudTensorMeta:
980:def _get_edge_cloud_hidden_channel_device_group(
983:    use_alt_group: bool = False,
1001:    if use_alt_group:
1163:    use_alt_group: bool = False,
1205:        pp_group, channel=channel, use_alt_group=use_alt_group
1437:    use_alt_group: bool = False,
1471:        pp_group, channel=channel, use_alt_group=use_alt_group
```

</details>


---

## Assistant <sup>2026/8/16 14:58:46</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 60,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\worker\\gpu_worker.py",
  "pattern": "class AsyncIntermediateTensors|def wait_for_comm|def is_completed|_comm_event|is_completed\\(\\)|def make_batched_recv_closure"
}
```

</details>


---

## User <sup>2026/8/16 14:58:47</sup>

<details>
<summary>Tool Result</summary>

```
85:class AsyncIntermediateTensors(IntermediateTensors):
99:    def wait_for_comm(self) -> None:
```

</details>


---

## Assistant <sup>2026/8/16 14:58:49</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\worker\\gpu_worker.py",
  "limit": 75,
  "offset": 60
}
```

</details>


---

## User <sup>2026/8/16 14:58:49</sup>

<details>
<summary>Tool Result</summary>

```
60	from vllm.utils.mem_utils import MemorySnapshot, format_gib, memory_profiling
61	from vllm.utils.torch_utils import set_random_seed
62	from vllm.v1.core.sched.output import GrammarOutput, SchedulerOutput
63	from vllm.v1.kv_cache_interface import KVCacheConfig, KVCacheSpec
64	from vllm.v1.outputs import (
65	    AsyncModelRunnerOutput,
66	    DraftTokenIds,
67	    ModelRunnerOutput,
68	)
69	from vllm.v1.utils import compute_iteration_details, report_usage_stats
70	from vllm.v1.worker.utils import is_residual_scattered_for_sp
71	from vllm.v1.worker.worker_base import CompilationTimes, WorkerBase
72	from vllm.v1.worker.workspace import init_workspace_manager
73	
74	from ...model_executor.model_loader import TensorizerLoader
75	from .gpu.warmup import warmup_kernels
76	from .utils import request_memory
77	
78	logger = init_logger(__name__)
79	
80	if TYPE_CHECKING:
81	    from vllm.model_executor.model_loader.tensorizer import TensorizerConfig
82	    from vllm.v1.worker.gpu_model_runner 
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:58:50</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "limit": 120,
  "offset": 60
}
```

</details>


---

## User <sup>2026/8/16 14:58:50</sup>

<details>
<summary>Tool Result</summary>

```
60	def _get_hidden_channel_stream(channel: Any) -> Any:
61	    """Return the dedicated NPU stream for *channel*, creating it lazily.
62	    Thread-safe (double-checked locking)."""
63	    stream = _hidden_channel_streams.get(channel)
64	    if stream is not None:
65	        return stream
66	    with _hidden_channel_stream_lock:
67	        stream = _hidden_channel_streams.get(channel)
68	        if stream is None:
69	            stream = torch.npu.Stream()
70	            _hidden_channel_streams[channel] = stream
71	            logger.info(
72	                "[edge-cloud] created dedicated stream for hidden "
73	                "channel %s", channel,
74	            )
75	        return stream
76	
77	
78	@contextlib.contextmanager
79	def _hidden_channel_stream_ctx(
80	    channel: Any | None, *, wait_for_default: bool = True,
81	):
82	    """Switch to the channel's dedicated stream for P2P isend/irecv.
83	
84	    *wait_for_default* – True for the **send** path (the tensor being
85	    sen
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:58:53</sup>


---

## Assistant <sup>2026/8/16 14:58:54</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 40,
  "output_mode": "content",
  "path": "c:\\kisella_mtp",
  "pattern": "class HiddenChannelType|HiddenChannelType\\."
}
```

</details>


---

## User <sup>2026/8/16 14:58:54</sup>

<details>
<summary>Tool Result</summary>

```
vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py:597:                HiddenChannelType.init(dp_size=num_decode)
vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py:602:                HiddenChannelType.init(dp_size=1)
vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py:826:            HiddenChannelType.init(dp_size=1)
vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py:989:        if channel == HiddenChannelType.PREFILL_1:
vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py:991:        if channel == HiddenChannelType.DECODE:
vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py:1068:                        HiddenChannelType.prefill(channel_idx),
vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py:1078:                        HiddenChannelType.decode(channel_idx),
vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py:1095:                (HiddenChannelType.prefill(channel_idx), 1)
vllm-ascend-pdmix\vllm_ascend\distributed\pa
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:58:56</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\core\\sched\\output.py",
  "limit": 80,
  "offset": 25
}
```

</details>


---

## User <sup>2026/8/16 14:58:56</sup>

<details>
<summary>Tool Result</summary>

```
25	    MultiModalFeatureSpec = object
26	    PoolingParams = object
27	    SamplingParams = object
28	    Request = object
29	
30	class HiddenChannelType:
31	    """Data-plane hidden tensor channel for edge-cloud PD separation.
32	
33	    A generous PREFILL/DECODE pool is generated at import time. ``init`` is
34	    idempotent and can be called again during engine bootstrap.
35	    """
36	
37	    _initialized: bool = False
38	    _MIN_PREFILL_POOL: int = 16
39	    _MIN_DECODE_POOL: int = 8
40	
41	    def __init__(self, value: str) -> None:
42	        self._value = value
43	
44	    @property
45	    def value(self) -> str:
46	        return self._value
47	
48	    def __eq__(self, other: object) -> bool:
49	        if isinstance(other, HiddenChannelType):
50	            return self._value == other._value
51	        return NotImplemented
52	
53	    def __hash__(self) -> int:
54	        return hash(self._value)
55	
56	    def __repr__(self) -> str:
57	        return f"<HiddenChannelType.{se
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:58:57</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "limit": 40,
  "offset": 1040
}
```

</details>


---

## User <sup>2026/8/16 14:58:57</sup>

<details>
<summary>Tool Result</summary>

```
1040	                return self._execute_model_edge_draft_tail(scheduler_output)
1041	            if bt in (BatchType.PREFILL_FIRST, BatchType.DECODE_FIRST):
1042	                return self._execute_model_edge_head(
1043	                    scheduler_output, layer_slice_info
1044	                )
1045	            if bt in (BatchType.PREFILL_LAST, BatchType.DECODE_LAST):
1046	                return self._execute_model_edge_tail(
1047	                    scheduler_output, layer_slice_info
1048	                )
1049	
1050	        # Fallback: original path for non-edge-cloud or unhandled batch types.
1051	        return self._execute_model_legacy(
1052	            scheduler_output, layer_slice_info, use_alt_group
1053	        )
1054	
1055	    def _hidden_channel_for(self, scheduler_output: "SchedulerOutput") -> HiddenChannelType:
1056	        channel = scheduler_output.hidden_channel
1057	        if channel is not None:
1058	            return channel
1059	        bt = scheduler_output
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:59:06</sup>


---

## Assistant <sup>2026/8/16 14:59:06</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "limit": 135,
  "offset": 980
}
```

</details>


---

## User <sup>2026/8/16 14:59:06</sup>

<details>
<summary>Tool Result</summary>

```
980	def _get_edge_cloud_hidden_channel_device_group(
981	    pp_group: GroupCoordinator,
982	    channel: HiddenChannelType | None = None,
983	    use_alt_group: bool = False,
984	):
985	    if channel is not None:
986	        if hasattr(pp_group, "_hidden_channel_groups"):
987	            device_group, _ = pp_group._hidden_channel_groups(channel)
988	            return device_group
989	        if channel == HiddenChannelType.PREFILL_1:
990	            return pp_group.device_group
991	        if channel == HiddenChannelType.DECODE:
992	            assert pp_group.alt_device_group is not None, (
993	                "Alternate groups not created. "
994	                "Call create_alternate_groups() first."
995	            )
996	            return pp_group.alt_device_group
997	        raise RuntimeError(
998	            "PREFILL_2 hidden channel requires create_hidden_channel_groups()"
999	        )
1000	
1001	    if use_alt_group:
1002	        assert pp_group.alt_device_group is not Non
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:59:07</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 20,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\executor\\shared_model_multiproc_executor.py",
  "pattern": "def worker_busy_loop|round_barrier|drain_batched_round|SYNC_METHODS|def _dispatch"
}
```

</details>


---

## User <sup>2026/8/16 14:59:07</sup>

<details>
<summary>Tool Result</summary>

```
173:    SYNC_METHODS: frozenset[str] = frozenset(
334:    def worker_busy_loop(self) -> None:
350:        loop runs a "round barrier" over :attr:`SYNC_METHODS`:
353:          :attr:`SYNC_METHODS`, the dispatching dp_rank is
449:                if (method in self.SYNC_METHODS
584:                            marker_cls.drain_batched_round(
630:    def _dispatch(
838:            "[PD] LAST drain_batched_round START: dp_ranks=%s "
843:        last_marker_cls.drain_batched_round(
850:            "[PD] LAST drain_batched_round DONE: dp_ranks=%s",
```

</details>


---

## Assistant <sup>2026/8/16 14:59:11</sup>


---

## Assistant <sup>2026/8/16 14:59:11</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\executor\\shared_model_multiproc_executor.py",
  "limit": 160,
  "offset": 400
}
```

</details>


---

## User <sup>2026/8/16 14:59:11</sup>

<details>
<summary>Tool Result</summary>

```
400	        paused = [False] * dp_size
401	
402	        init_kv_cache = False
403	        while True:
404	            dispatched = False
405	            for k, mq in enumerate(self.rpc_broadcast_mqs):
406	                if paused[k]:
407	                    continue
408	                try:
409	                    # ``dequeue`` is the upstream high-level API
410	                    # used by the standard ``MultiprocExecutor``
411	                    # busy loop. Using the low-level
412	                    # ``acquire_read`` would bypass the
413	                    # status / timeout semantics that the rest of
414	                    # vLLM's executor protocol depends on.
415	                    method, args, kwargs, output_rank = mq.dequeue(
416	                        timeout=0.001)
417	                except TimeoutError:
418	                    continue
419	                # outer enumerate index k is the dp_rank
420	                self._dispatch(k, method, args, kwargs, output_ra
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:59:12</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 15,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker",
  "pattern": "def make_batched_recv_closure"
}
```

</details>


---

## User <sup>2026/8/16 14:59:12</sup>

<details>
<summary>Tool Result</summary>

```
vllm-ascend-pdmix\vllm_ascend\worker\edge_cloud\shared_model_edge_worker.py:1099:    def make_batched_recv_closure(
```

</details>


---

## Assistant <sup>2026/8/16 14:59:15</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\edge_cloud\\shared_model_edge_worker.py",
  "limit": 110,
  "offset": 1099
}
```

</details>


---

## User <sup>2026/8/16 14:59:15</sup>

<details>
<summary>Tool Result</summary>

```
1099	    def make_batched_recv_closure(
1100	        self,
1101	        src: int,
1102	        num_tokens: int,
1103	        sp_chunk: bool,
1104	    ):
1105	        """Return a no-arg closure that receives the cloud middle
1106	        output for the batched compute path.
1107	
1108	        The closure is created here (in vllm_ascend) and stored by
1109	        the busy_loop in ``_pending_deferred``; the upstream busy_loop
1110	        does not import vllm_ascend and just calls the closure like
1111	        any other deferred marker.
1112	
1113	        ``src`` is the in-group rank of the cloud first-worker for
1114	        this dp_rank (``local_rank + 1`` on the shared PP group).
1115	        ``num_tokens`` / ``sp_chunk`` mirror the recv call in
1116	        :meth:`SharedModelEdgeWorker.execute_model`'s
1117	        ``_tail_postprocess``. The closure stores the received
1118	        ``comm_postprocess`` handles on the returned
1119	        ``AsyncIntermediateTensors``; the batched tai
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:59:18</sup>


---

## Assistant <sup>2026/8/16 14:59:19</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-A": 30,
  "-n": true,
  "head_limit": 60,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "pattern": "def edge_cloud_broadcast_recv"
}
```

</details>


---

## User <sup>2026/8/16 14:59:19</sup>

<details>
<summary>Tool Result</summary>

```
1749:def edge_cloud_broadcast_recv(
1750-    num_tokens: int,
1751-    channel: HiddenChannelType = HiddenChannelType.PREFILL_1,
1752-    sp_chunk: bool = False,
1753-    src: int | None = None,
1754-    include_mrope: bool = True,
1755-) -> tuple[
1756-    dict[str, torch.Tensor | Any] | None,
1757-    list[Handle],
1758-    list[Callable[[], None]],
1759-]:
1760-    """Receive PP tensors on the selected Phase6 channel and broadcast them
1761-    within the local edge/cloud TP group.
1762-
1763-    Uses locally computed metadata instead of receiving it from the sender.
1764-    This eliminates the inter-node pickle+Gloo metadata exchange, while
1765-    still broadcasting metadata within the local TP group (intra-node)
1766-    so that non-NPU0 TP ranks can allocate tensors.
1767-    Args:
1768-        sp_chunk: Whether to split the fully received tensors across the local
1769-            TP/SP ranks. The split is deferred until after receive and TP
1770-            broadcast completi
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:59:19</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 40,
  "offset": 2280
}
```

</details>


---

## User <sup>2026/8/16 14:59:19</sup>

<details>
<summary>Tool Result</summary>

```
2280	                )
2281	                continue
2282	            break
2283	        else:
2284	            return self._make_empty_batch()
2285	
2286	        if scheduler_output is self._draft_first_cloud_publish_pending:
2287	            self._draft_first_dispatched = True
2288	            if self._draft_first_scalars_patched:
2289	                self._draft_first_cloud_publish_pending = None
2290	                self._draft_first_scalars_patched = False
2291	
2292	        scheduler_output.batch_type = first_type
2293	        if scheduler_output.head_token is None:
2294	            scheduler_output.head_token = uuid4().hex
2295	        if kind == "decode":
2296	            # decode 域固定 DECODE 通道（设计 §4.2）。
2297	            scheduler_output.hidden_channel = HiddenChannelType.DECODE
2298	        elif scheduler_output.hidden_channel is None:
2299	            # Phase B（设计 §4.1）：prefill 域链在 enqueue 时已继承父 chunk
2300	            # 的 Prefill 通道；缺失说明链创建路径漏了继承。
2301	            raise Runti
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:59:34</sup>


---

## Assistant <sup>2026/8/16 14:59:35</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 30,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "pattern": "hidden_channel|edge_cloud_isend_tensor_dict|edge_cloud_irecv_tensor_dict"
}
```

</details>


---

## User <sup>2026/8/16 14:59:35</sup>

<details>
<summary>Tool Result</summary>

```
238:        # are direction-agnostic (driven by hidden_channel + num_tokens).
821:    # agnostic: the hidden_channel + num_tokens fully determine the recv, so
862:        channel_str = hint.get("hidden_channel")
868:                {k: hint.get(k) for k in ("head_token", "hidden_channel",
967:        ``num_tokens`` rows (sliced in edge_cloud_isend_tensor_dict via the
1013:                self._wait_pp_send_work(self._hidden_channel_for(scheduler_output))
1055:    def _hidden_channel_for(self, scheduler_output: "SchedulerOutput") -> HiddenChannelType:
1056:        channel = scheduler_output.hidden_channel
1074:            # 通道，调度器在 enqueue/pick 时必定写入 hidden_channel；
1078:                f"{bt.value} is missing its inherited prefill hidden_channel"
1157:            channel = self._hidden_channel_for(scheduler_output)
1180:        channel = self._hidden_channel_for(scheduler_output)
1274:                _channel = self._hidden_channel_for(scheduler_output)
1302:                channel = s
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:59:39</sup>


---

## Assistant <sup>2026/8/16 14:59:40</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 20,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\distributed\\parallel_state.py",
  "pattern": "def create_hidden_channel_groups|_decode_device_groups|_prefill_device_groups|def _hidden_channel_groups|decode_per_dp|prefill_per_dp"
}
```

</details>


---

## User <sup>2026/8/16 14:59:40</sup>

<details>
<summary>Tool Result</summary>

```
No matches found
```

</details>


---

## Assistant <sup>2026/8/16 14:59:42</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 25,
  "output_mode": "content",
  "path": "c:\\kisella_mtp",
  "pattern": "def create_hidden_channel_groups|def _hidden_channel_groups"
}
```

</details>


---

## User <sup>2026/8/16 14:59:43</sup>

<details>
<summary>Tool Result</summary>

```
vllm-pdmix\docs\hidden_channel_dp_extension.md:146:def create_hidden_channel_groups(
vllm-pdmix\docs\hidden_channel_dp_extension.md:231:def _hidden_channel_groups(self, channel: Any):
vllm-ascend-pdmix\vllm_ascend\patch\worker\patch_distributed.py:348:    def create_hidden_channel_groups(
vllm-ascend-pdmix\vllm_ascend\patch\worker\patch_distributed.py:465:    def _hidden_channel_groups(self, channel: Any):
```

</details>


---

## Assistant <sup>2026/8/16 14:59:45</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\worker\\patch_distributed.py",
  "limit": 190,
  "offset": 348
}
```

</details>


---

## User <sup>2026/8/16 14:59:45</sup>

<details>
<summary>Tool Result</summary>

```
348	    def create_hidden_channel_groups(
349	        self,
350	        torch_distributed_backend: str | Backend,
351	        num_prefill: int = 2,
352	        num_decode: int = 1,
353	    ) -> None:
354	        """Create extra hidden-channel groups for DP-scalable PD separation.
355	
356	        The default device/cpu groups are PREFILL_1.
357	        ``_decode_device_groups[0]`` (DECODE_1) is created by
358	        ``create_alternate_groups``.
359	
360	        This method adds:
361	          - PREFILL_2..num_prefill  (append to ``_prefill_device_groups``)
362	          - DECODE_2..num_decode    (append to ``_decode_device_groups``)
363	
364	        Each group uses a unique ``pg_options`` name for HCCL stream isolation.
365	        """
366	        # --- PREFILL groups (2..N) ---
367	        # PREFILL_1 uses device_group; PREFILL_2 uses existing prefill2 alias.
368	        for i in range(len(self._prefill_device_groups) + 1, num_prefill + 1):
369	            self._create_one_hidden_cha
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 14:59:49</sup>


---

## Assistant <sup>2026/8/16 14:59:50</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "limit": 55,
  "offset": 575
}
```

</details>


---

## User <sup>2026/8/16 14:59:50</sup>

<details>
<summary>Tool Result</summary>

```
575	        # PREFILL_2..N and DECODE_2..M when dp_size > 1.
576	        pp_group = get_pp_group()
577	        if pp_group.world_size > 1:
578	            pp_group.create_alternate_groups(backend)
579	            if hasattr(pp_group, "create_hidden_channel_groups"):
580	                dp_size = parallel_config.data_parallel_size
581	                # Create extra hidden-channel groups based on dp_size.
582	                if parallel_config.is_shared_model_edge:
583	                    num_prefill = dp_size * 2
584	                    num_decode = dp_size
585	                else:
586	                    num_prefill = 2
587	                    num_decode = 1
588	                logger.info(
589	                    "[PD] create_hidden_channel_groups: "
590	                    "dp_size=%s dp_rank=%s num_prefill=%s num_decode=%s, "
591	                    "edge_npu_count=%s",
592	                    dp_size,
593	                    getattr(parallel_config, "data_parallel_rank", 0),
594	 
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:00:34</sup>


---

## Assistant <sup>2026/8/16 15:01:16</sup>

代码锚点都已核实，而且有个重要发现：**通道基础设施是现成的**(多通道 device group、per-channel NPU stream、warmup、`SchedulerOutput.hidden_channel` 全链路透传)，draft 目前只是被映射到了共享的 DECODE 通道。这让第一刀的成本远低于从零建。以下是按“到盈亏平衡线”目标梳理的修改方案。

---

# 边云 MTP 盈亏平衡改造：代码修改方案

**范围**：单实例、单 DP、TP=1(§5.2.6 的 event 就绪判定安全前提)；shared-model 边侧 worker 路径。
**目标**：非 MTP 基线的 max(E, W) 流水 -- 0814-2 的 queue_len≥2 / dequeue≈0.9ms 形态在 MTP 下复现。

## 现状锚点(已核实)

| 事实 | 位置 |
|---|---|
| DECODE_DRAFT_* 批被映射到共享 DECODE 通道 | [worker.py:1064-1068](vllm-ascend-pdmix/vllm_ascend/worker/worker.py#L1064-L1068) |
| 调度器 decode 域(含 draft)固定写 `HiddenChannelType.DECODE` | [pd_separated_scheduler.py:2295-2297](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L2295-L2297) |
| `==0` 串行门控的存在理由 = draft 共享 DECODE 通道(注释明说会互相等 send/recv 锁死) | [pd_separated_scheduler.py:1599-1609](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1599-L1609) |
| 预生成分支已有目标语义:`< limit=2` 可流水 | [pd_separated_scheduler.py:1591-1597](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1591-L1597) |
| 通道→进程组解析、懒建 stream、启动 warmup 全部现成 | [patch_distributed.py:348-490](vllm-ascend-pdmix/vllm_ascend/patch/worker/patch_distributed.py#L348-L490)、[parallel_state.py:60-100](vllm-ascend-pdmix/vllm_ascend/distributed/parallel_state.py#L60-L100)、[parallel_state.py:1009](vllm-ascend-pdmix/vllm_ascend/distributed/parallel_state.py#L1009) |
| recv 闭包在 head 阶段创建、但 irecv 要到 round 末 drain 才发出 | [shared_model_edge_worker.py:328-332](vllm-ascend-pdmix/vllm_ascend/worker/edge_cloud/shared_model_edge_worker.py#L328-L332) → [1099-1135](vllm-ascend-pdmix/vllm_ascend/worker/edge_cloud/shared_model_edge_worker.py#L1099-L1135) |
| 阻塞点：drain ② `execute_model_batched_tail` 内 `wait_for_comm` → `handle.wait()` | [shared_model_edge_worker.py:338-425](vllm-ascend-pdmix/vllm_ascend/worker/edge_cloud/shared_model_edge_worker.py#L338-L425)、[gpu_worker.py:99-108](vllm-pdmix/vllm/v1/worker/gpu_worker.py#L99-L108) |
| 云侧 recv 通道由请求 hint 携带(`hidden_channel`),回包同通道 | [worker.py:862-868](vllm-ascend-pdmix/vllm_ascend/worker/worker.py#L862-L868) |
| round barrier:LAST marker 阻塞 drain | [shared_model_multiproc_executor.py:449-533](vllm-pdmix/vllm/v1/executor/shared_model_multiproc_executor.py#L449-L533) |
| draft pacing:DDF pick 启动 `draft_last_delay`(yaml 5ms/代码 15ms)+ `_force` 交替 | [pd_separated_scheduler.py:1781-1798](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1781-L1798)、[225-294](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L225-L294) |
| inflight 在 DECODE_FIRST 完成即释放，draft 无此分支 | [pd_separated_scheduler.py:3380-3390](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L3380-L3390) |

---

## 第一刀：MTP 独立数据通道(DRAFT 通道)

**改 5 处，全部是“接现成管线”：**

1. **[output.py:30](vllm-pdmix/vllm/v1/core/sched/output.py#L30) `HiddenChannelType`**:仿照 `prefill()/decode()` 增加 `draft(i)` 静态方法和 `DRAFT` 别名(独立 `_draft_pool`)。不建议复用 DECODE_2 --语义混用会让后续 DP 扩展(每 dp 一条 draft 通道)无处安放。

2. **[patch_distributed.py:348](vllm-ascend-pdmix/vllm_ascend/patch/worker/patch_distributed.py#L348) `create_hidden_channel_groups`**:加 `num_draft` 参数和 `_draft_device_groups/_draft_cpu_groups` 列表，复用 `_create_one_hidden_channel`(pg_name=`pp_draft{i}`,HCCL stream 隔离自动获得);`_hidden_channel_groups` 加 `"draft_M"` 分支。

3. **[parallel_state.py:582-600](vllm-ascend-pdmix/vllm_ascend/distributed/parallel_state.py#L582-L600)** 调用点:`num_draft = dp_size`(本场景=1);`HiddenChannelType.init` 加 draft 池;**[warmup_edge_cloud_hidden_channels](vllm-ascend-pdmix/vllm_ascend/distributed/parallel_state.py#L1037-L1101) 的 `channel_peers` 构造纳入 draft 通道** -- 这条不能漏，否则首次 DDF 的 rendezvous 顺序不定，恰好复现 L1599 注释警告的死锁。

4. **[worker.py:1055-1078](vllm-ascend-pdmix/vllm_ascend/worker/worker.py#L1055-L1078) `_hidden_channel_for`**:`DECODE_DRAFT_FIRST/LAST → HiddenChannelType.DRAFT`。云侧 hint 驱动，自动跟随，无需改。

5. **[pd_separated_scheduler.py:112-115](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L112-L115)**:加 `self._draft_channel`,在 DDF pick 处(对应 L2297 的 decode 分支，以及 L2437/L2590 的 `inherited_channel=DECODE`)改写为 `_draft_channel`。**注意 PDFL 已有“通道缺失即 raise”的先例([worker.py:1069-1078](vllm-ascend-pdmix/vllm_ascend/worker/worker.py#L1069-L1078)),draft 尾也照此办理**，通道错配是不可超时死锁，宁可炸。

此刀完成后门控**先不动**，跑基线验证：无死锁、日志确认 draft 走 `pp_draft1`、性能应与现状持平或略好(少了和普通 decode 的队头阻塞)。

## 第二刀：尾 recv/计算分离 + worker 层调度

对应设计 §5.2 六点，映射到本仓库实际结构：

**(1) irecv 后记 NPU event** -- [parallel_state.py:1434-1572](vllm-ascend-pdmix/vllm_ascend/distributed/parallel_state.py#L1434-L1572) `edge_cloud_irecv_tensor_dict`:两处 irecv(merge 主路径 L1501、逐 key 路径 L1554)之后，在**同一个** `_hidden_channel_stream_ctx(channel, wait_for_default=False)` 内 `event.record(torch.npu.current_stream(...))`,把 event 附加到返回值。

**(2) `AsyncIntermediateTensors.is_ready()`** -- [gpu_worker.py:85-114](vllm-pdmix/vllm/v1/worker/gpu_worker.py#L85-L114):加 `_comm_event` 与 `is_ready()`(`event.query()`,无 event 时 True);`wait_for_comm` 不动(event 已完成时 `handle.wait()` 立即返回)。**护栏**：TP>1 或 sp_chunk 开启时 `is_ready()` 恒 False(§5.2.6:TP broadcast 集合通信不被 event 覆盖)，整体功能用配置开关锁死在 TP=1。

**(3) irecv 提前 + pending_tails** -- 关键本地化修正：设计文档假设“irecv 已发出未 wait”,但本仓库 [shared_model_edge_worker.py:328-332](vllm-ascend-pdmix/vllm_ascend/worker/edge_cloud/shared_model_edge_worker.py#L328-L332) 是把 recv **闭包**存进 `_pending_deferred`,irecv 实际到 round 末 drain 才发。所以改法是:`drive_batched_round`(head+isend 之后)**立即调用闭包**发出 irecv(顺带吃到 §5.3.6 的“irecv 重叠云中段计算”收益)，返回的 `AsyncIntermediateTensors`(自带 event)存入新的 `pending_tails: deque[TailEntry]`;`TailEntry = (bundles, intermediates, dp_ranks)`。单 DP 单实例就是一条 deque,队首阻塞保序。

**(4) drain 拆分** -- [drain_batched_round](vllm-ascend-pdmix/vllm_ascend/worker/edge_cloud/shared_model_edge_worker.py#L338-L425):现在的步骤 1(调闭包)/2(batched tail)/3(切片回投)拆成“存 pending”(1 变为 head 期已做)和“执行尾”两段，步骤 2/3 提为独立方法 `execute_pending_tail(entry, on_dp_rank_output)`,供 poll 调用，内部逻辑零改动。

**(5) busy_loop 加 poll 阶段** -- [shared_model_multiproc_executor.py:403](vllm-pdmix/vllm/v1/executor/shared_model_multiproc_executor.py#L403) 每轮循环开头(MQ dequeue 之前)：duck-typing 检查 marker 类是否有 `poll_pending_tails`,有则调用(实现在 vllm_ascend 侧，保持上游模块不 import vllm_ascend 的既有分层)。`dequeue(timeout=0.001)` 天然给出 poll 节拍。

**(6) round barrier 放宽** -- [shared_model_multiproc_executor.py:533](vllm-pdmix/vllm/v1/executor/shared_model_multiproc_executor.py#L533) `_process_last_markers`:LAST marker 处理改为“只存 pending 不执行尾”，新 round 不再等尾完成；FIRST marker 的 head+isend 同步语义不变。

**验收**：MTP 开启时 LAST 批的 "dequeue took" 从 5-13ms 降到 ~1ms 量级(对齐 0814-2),worker 空等窗口消失。此刀独立可回退(开关关掉即回到同步 drain)。

## 第三刀：EngineCore scheduler 优化

**(1) 门控放宽** -- [pd_separated_scheduler.py:1604-1609](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1604-L1609) 非预生成分支改成预生成分支同款:

```python
return bool(
    self.decode_head_inflight_count == 0
    and self.decode_draft_remote_pending_count
        < self._decode_draft_remote_pending_limit   # ==0 -> <limit
    and not self.decode_drafts_last_ready
    and self._force.can_pick_decode_draft_first())  # Phase 2 再松
```

用配置开关(建议放 [ascend_config.py PDSeparationConfig](vllm-ascend-pdmix/vllm_ascend/ascend_config.py#L883-L964),如 `decode_draft_pipeline_enable`) gated on DRAFT 通道已建立，默认关。

**(2) `_force` 交替放松** -- [pd_separated_scheduler.py:283-284](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L283-L284) `can_pick_decode_draft_first` 目前被 `decode_draft_last_pending` 一票封死;流水模式下改为“允许 1 个 DDL 在飞”(即 remote_pending < limit 时可再 pick DDF)。放第二阶段，等(1)验证后做。

**(3) draft 的 inflight 提前释放** -- [pd_separated_scheduler.py:3380-3390](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L3380-L3390) 加 `DECODE_DRAFT_FIRST` 分支，与 `DECODE_FIRST` 同款：DDF 完成即减 inflight,而不是等 DDL 归来。这是复刻非 MTP “消除 Cloud idle gap” 的核心一行。

**(4) pacing 归零** -- [layer_slice_config.yaml](vllm-ascend-pdmix/vllm_ascend/core/layer_slice_config.yaml#L33) `draft_last_delay_schedule_ms: 0`(异步模式下就绪由 event poll 保证，延迟 pacing 失去意义且纯占 5-15ms);decode_first_only 窗口在流水模式下禁用([pd_separated_scheduler.py:235](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L235) 已有同款先例注释)。

**(5) batch_queue 深度与填充** -- [patch_engine_core.py `_patched_step_with_batch_queue`](vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py#L803-L919):重叠深度 = batch_queue_size − 1,当前 =2(深度 1);draft 流水模式下提到 3-4(可配置);放宽 one-schedule-per-turn 的 break(队列未满时继续填);`not batch_queue[-1][0].done()` 的提前返回改为仅队列满时阻塞。**代价评估**：每多 1 深度多一份 in-flight hidden buffer + KV 压力，深度 3-4 在单实例下可接受。

**(6) watchdog 补齐**：remote pending 上限升到 2 后，给 decode 域补上 prefill 域已有的 last watchdog([L2317](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L2317) 先例)。

---

## 分阶段落地与验收

| 阶段 | 内容 | 验收指标 |
|---|---|---|
| P0 | 第一刀(通道)+ warmup | 无死锁；日志见 `pp_draft1`;性能 ≥ 现状 |
| P1 | 第二刀(recv/计算分离) | LAST 批 dequeue ~1ms;worker 利用率对齐非 MTP |
| P2 | 第三刀(门控/延迟/batch_queue) | MTP 下 queue_len≥2;DDF(N+1) 与 DDL(N) 在飞重叠可见 |
| P3 | 联调压测 | **MTP tokens/s ≈ 非 MTP(盈亏平衡线)**；单请求 TPOT 改善 ≥1.2× |

**回归测试更新**:[test_pd_draft_drain.py](vllm-ascend-pdmix/tests/ut/test_pd_draft_drain.py)(hidden_channel 改 DRAFT)、[test_pd_chunk_prefill_prior.py](vllm-ascend-pdmix/tests/ut/test_pd_chunk_prefill_prior.py)(门控语义)；新增：pending_tails 保序 UT、event 就绪护栏 UT(TP>1 恒 False)、draft 通道 warmup 集成测试。

**两个已知风险点**：① P2 的 limit=2 流水依赖“同通道两次 isend/irecv 顺序配对”--单 worker 线程按序 dispatch 保证了这一点，但若未来引入多线程 dispatch 需重新论证；② `is_ready()` 的 TP=1 硬护栏必须做成 assert 级而非 warning,通道/流配置错误是静默数据错乱，不是性能问题。

方案与三刀的收益边界一致:P0-P1 修复流水线坍塌，P2 兑现窗口填充，合计预期把 MTP 从 3-5× 劣化拉回盈亏线附近；再往上(净赢)就需要第四刀 draft 本地化，不在本方案范围。


---

## User <sup>2026/8/16 15:03:08</sup>

不考虑sharemodel，就先按边侧两卡（tp=2）来考虑


---

## Assistant <sup>2026/8/16 15:03:47</sup>


---

## Assistant <sup>2026/8/16 15:03:49</sup>

边侧 TP=2(非 shared-model)改变了两件事：worker 层从“单进程多虚拟 worker”变成“两卡两进程”，且 recv 就绪判定跨进了 §5.2.6 的风险区(TP broadcast 是集合通信，NPU event 盖不住)。先把非 shared 路径的关键代码锚点核一遍再修订方案：


---

## Assistant <sup>2026/8/16 15:03:49</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "limit": 120,
  "offset": 1290
}
```

</details>


---

## User <sup>2026/8/16 15:03:49</sup>

<details>
<summary>Tool Result</summary>

```
1290	            else:
1291	                # Fallback: synchronous recv (CHER off, or get_or_post failed).
1292	                # Pre-compute input preparation while edge runs segment_a.
1293	                # This overlaps cloud's _update_states, _prepare_inputs,
1294	                # _determine_batch_execution_and_padding, and
1295	                # _build_attention_metadata with edge's segment_a forward.
1296	                # SP chunking is part of edge_cloud_broadcast_recv's
1297	                # postprocess for both merged and non-merged payloads. It must
1298	                # run only after the receive and TP broadcast have completed.
1299	                do_sp_chunk = enable_sp() and (
1300	                    self.model_runner.edge_cloud_cfg.mode != "embedding_only"
1301	                    or not self.model_runner.supports_mm_inputs)
1302	                channel = self._hidden_channel_for(scheduler_output)
1303	                # In the shared-model edge-cloud topology the
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:03:49</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "limit": 115,
  "offset": 1780
}
```

</details>


---

## User <sup>2026/8/16 15:03:49</sup>

<details>
<summary>Tool Result</summary>

```
1780	            communicates with a different cloud peer based on
1781	            ``local_rank``). The parameter is only consulted when
1782	            the local PP group is the PP pair (i.e. it participates
1783	            in the PP receive); the singleton-PP TP-broadcast-only
1784	            branch is unchanged.
1785	        include_mrope: must match the sender's edge_cloud_isend_tensor_dict
1786	            argument (both derived from step_has_multimodal_req). When False,
1787	            mrope_positions is neither received nor broadcast (text-only batch).
1788	    """
1789	    pp_group = get_pp_group()
1790	    tp_group = get_tp_group()
1791	    is_pp_npu0 = pp_group.world_size > 1
1792	    ec_meta = _select_edge_cloud_meta_for_recv()
1793	
1794	    logger.info(
1795	        "[PD] edge_cloud_broadcast_recv: channel=%s num_tokens=%s src=%s "
1796	        "pp_world=%d is_pp_npu0=%s",
1797	        channel.value, num_tokens, src,
1798	        pp_group.world_size, is_pp_npu0,
1799	
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:04:29</sup>


---

## Assistant <sup>2026/8/16 15:04:30</sup>

还需确认 TP1(非 PP-NPU0 rank)在 recv 路径里到底走哪段代码——这决定两卡的解耦方式：


---

## Assistant <sup>2026/8/16 15:04:30</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "limit": 100,
  "offset": 1890
}
```

</details>


---

## User <sup>2026/8/16 15:04:30</sup>

<details>
<summary>Tool Result</summary>

```
1890	        return tensor_dict, comm_handles, comm_postprocess
1891	
1892	    # Non-PP-NPU0 ranks: receive metadata from NPU 0 via TP broadcast,
1893	    # allocate tensors, then broadcast-recv actual data
1894	    ###broadcast_data = tp_group.broadcast_object(None, src=0)
1895	    #recv_num_tokens = broadcast_data[0]
1896	    #metadata_list = broadcast_data[1]
1897	
1898	    if ec_meta.merge_payload:
1899	        # Non-PP-rank-0 path on the merged fast path: allocate a single
1900	        # merged buffer with the same shape as PP rank 0's, broadcast-recv
1901	        # into it, then split.  Avoids one broadcast per key.
1902	        merged_buf = _allocate_merged_recv_buffer(ec_meta, num_tokens)
1903	        recv_tensor_dict: dict[str, torch.Tensor | Any] = {
1904	            key: value
1905	            for key, value in ec_meta.metadata_list
1906	            if not isinstance(value, TensorMetadata)
1907	        }
1908	        # Non-merge keys (e.g. mrope_positions) are NOT inside mer
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:05:41</sup>


---

## Assistant <sup>2026/8/16 15:06:13</sup>

TP1 的路径确认了--[parallel_state.py:1892-1990](vllm-ascend-pdmix/vllm_ascend/distributed/parallel_state.py#L1892-L1990):TP1 不做 irecv,自己分配同形 buffer,然后在 `broadcast_postprocess` 里**阻塞在同一场 TP broadcast 里等 TP0**。这决定了 TP=2 方案的形态。以下是相对上一版的修订。

---

# 修订：边侧两卡(TP=2,非 shared-model)方案

## 一、TP=2 带来的三个结构性变化

1. **两卡两进程**：worker 层从 shared-model 的“单进程 busy_loop + marker 分组”变成标准 [multiproc_executor.py](vllm-pdmix/vllm/v1/executor/multiproc_executor.py) 的每进程 busy loop(就是我们看 "dequeue took" 日志的那个)。**上一版刀2的 5/6 两点(busy_loop poll + round barrier 放宽)不适用**，替换为下述 ack 机制。

2. **两卡被广播 rendezvous 绑死**：LAST 批到达时，TP0 阻塞在 `handle.wait()`([gpu_worker.py:99-108](vllm-pdmix/vllm/v1/worker/gpu_worker.py#L99-L108)),TP1 阻塞在同一场 broadcast 里([parallel_state.py:1927-1938](vllm-ascend-pdmix/vllm_ascend/distributed/parallel_state.py#L1927-L1938))。**只解耦 TP0 没用**--TP1 卡在 broadcast 里就不能处理下一个 FIRST 的 MQ 项，而 FIRST 的头层计算是 TP 集合操作、两卡必须同时到场。所以 worker 层“各自 poll 各自的 event”在 TP=2 下不成立(TP1 没有 event 可 poll)。

3. **但调度器 MQ 广播是天然的两卡同步点**：execute_model 由 EngineCore 经 MQ 广播同时落到两卡。**只要 LAST 批不被派发、直到数据已到，两卡的阻塞同时塌缩为节点内 broadcast 拷贝(亚毫秒)**。这正是设计文档 §5.3.6(scheduler 驱动 + 双重 gate)相对 §5.3.5(worker 层 gloo ready_flag)的优势在 TP 场景的重演--而且比 §5.3.5 干净：**不需要跨进程 gloo 信令，TP1 零改动**。

**结论：刀2 从“worker 层 poll+执行”改为“TP0 提前 irecv + event + busy-loop poll + ack 上报，调度器 ack-gated 派发 LAST”。**

## 二、修订后的刀2:recv/计算分离(TP=2 版)

执行序列(以 decode draft 一轮为例)：

```
现状:  调度器派 DDF ──► 两卡头层+isend ──► 调度器派 DDL ──► TP0 阻塞 handle.wait ═══网络═══
                                                              TP1 阻塞 broadcast ═══同上═══
       (两卡全程被绑死,queue_len=1 的根源)

改后:  调度器派 DDF ──► TP0 头层+isend,随即发 return-irecv + record event,按 head_token 入 stash
       │  (irecv 与云中段计算重叠;云侧 isend 到达时 recv 已挂出,连云侧的 rendezvous 等待都省了)
       ├─ 两卡 free,调度器可派 DDF(N+1)/其他批 ◄── 刀3 的门控放宽在这里兑现
       ▼
       TP0 busy_loop 每轮 poll event.query() ──ready──► response MQ 发 "__draft_recv_ready__" ack
       ▼
       调度器 DDL pick 门控 = ack 已到 ──► 派 DDL ──► 两卡执行尾层
       (TP0 wait_for_comm 立即返回;TP1 进 broadcast,TP0 数据已在 buffer,只剩节点内拷贝)
```

**改动点(按文件)：**

**(a) [parallel_state.py:1434-1572](vllm-ascend-pdmix/vllm_ascend/distributed/parallel_state.py#L1434-L1572) `edge_cloud_irecv_tensor_dict`**:与上一版相同--两处 irecv 之后在同一 `_hidden_channel_stream_ctx(channel, wait_for_default=False)` 内 `event.record()`,event 随返回值带出。

**(b) [gpu_worker.py:85-114](vllm-pdmix/vllm/v1/worker/gpu_worker.py#L85-L114) `AsyncIntermediateTensors`**:加 `_comm_event` + `is_ready()`(仅 TP0 有意义；TP1 无 event 恒 False,不影响正确性，因为 gate 在调度器)。

**(c) [worker.py](vllm-ascend-pdmix/vllm_ascend/worker/worker.py) TP0 的 FIRST 路径(`_execute_model_edge_head`)**:`_record_pp_send_work` 之后，若 batch 属 draft 域(P0 先只做 DRAFT 通道)，**立即对云侧回包发 irecv**(draft 域 FIRST/LAST 同一批、num_tokens 相同、C2E 方向 meta 现成，[L1366-1403](vllm-ascend-pdmix/vllm_ascend/worker/worker.py#L1366-L1403) 的 `ScheduledDraftTensorMeta` 正是为此准备的)，得到的 `AsyncIntermediateTensors`(带 event)按 `scheduler_output.head_token` 存入 worker 级 stash。

**(d) TP0 的 LAST 路径(`_execute_model_edge_draft_tail`)**：按 head_token 从 stash 取预挂的 `AsyncIntermediateTensors`,不再现场调 `edge_cloud_broadcast_recv` 的 irecv 分支；TP1 分支**原样保留**(分配 buffer + broadcast-recv)。

**(e) [multiproc_executor.py](vllm-pdmix/vllm/v1/executor/multiproc_executor.py) TP0 busy loop**:每轮 `dequeue(timeout=...)` 前加 poll 阶段：stash 中有 event ready → 经现有 `handle_output`/response MQ 通道发 ack(head_token)。**注意 ack 要走既有响应协议的扩展**(先例:Phase C 云侧发布的 PDFL POST_OUT 就是同一条通路)，不要新开通道。

**(f) TP1:零改动。**

**先决校验一项**：确认 DDL 今天实际走的 recv 是否已是 meta-free 快速路径([worker.py:1309](vllm-ascend-pdmix/vllm_ascend/worker/worker.py#L1309) 是普通 LAST;draft tail 若还在 `edge_cloud_broadcast_recv_draft` 的元数据交换老路上，提前 irecv 无法套用，需先把 scheduled draft 迁到 `ScheduledDraftTensorMeta` 快速路径--这是独立的前置小任务)。

## 三、刀1、刀3 的增补

**刀1(DRAFT 通道)**：与上一版完全相同，拓扑无关。TP=2 下多一个注意点:`enable_sp()` 时 [worker.py:1378-1379](vllm-ascend-pdmix/vllm_ascend/worker/worker.py#L1378-L1379) draft 张量保留动态分片形状(兼容路径)，P0 阶段建议 draft 域关 SP,避免异构 TP 的形状协商复杂度。

**刀3(调度器优化)**：上一版的 (1)门控 `<limit`、(2)`_force` 放松、(3)DDF 完成即释放 inflight([L3380-3390](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L3380-L3390) 加 DECODE_DRAFT_FIRST 分支)、(6)watchdog 全部保留；**(4) pacing 部分换血**：

- `draft_last_delay_schedule_ms` 与 DDL 自贴/延迟派发机制，在 ack 路径启用时**整体旁路**--DDL 的派发时机由数据面就绪(ack)决定，5-15ms 的人为 pacing 和“猜云侧何时回包”的语义一并消失。配置开关(如 `decode_draft_recv_ack_enable`)关闭时回落现状，保回退性。
- DDL pick 门控改为:`head_token ∈ _draft_recv_ready_acks`(engine 输出处理侧把 ack 路由给调度器，[patch_engine_core.py](vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py) 的输出分发处加一类 marker)。
- batch_queue 深度：ack 模式下 LAST 在就绪前**根本不进队列**，队列不被阻塞的 LAST 占坑，深度压力比上一版小；batch_queue_size 仍建议 3,但优先级降低，P2 末再调。

## 四、风险与护栏(TP=2 特有)

| 风险 | 对策 |
|---|---|
| ack 延迟(response MQ + 调度循环 + 1ms poll 粒度) | 合计 ~1-2ms,远小于被消掉的 5-13ms 网络暴露;poll 放 dequeue 前保证节拍 |
| 提前 irecv 的 buffer 生命周期 | channel stream 上分配、`record_stream` 护住，stash 强引用直到消费；深度 2 时两块 live buffer,显存开销可忽略 |
| limit=2 下同通道两个在飞 irecv 的顺序配对 | 单线程按序 post,HCCL 同 PG 点对点按序匹配；**禁止未来在 dispatch 侧引入乱序** |
| event 永不触发(云故障/丢包) | 刀3(6) 的 decode 域 watchdog(对齐 prefill 域 [L2317](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L2317) 先例) |
| head_token 串配 | stash 与 ack 都携带 head_token,DDL pick 时严格匹配；复用 PDFL 的 flight 键配对机制(`draft_task_id:draft_step_idx`) |

## 五、阶段划分(更新)

| 阶段 | 内容 | 验收 |
|---|---|---|
| P0 | 刀1 DRAFT 通道 + warmup + (前置)scheduled draft recv 迁快速路径 | 无死锁；日志见 `pp_draft1`;性能 ≥ 现状 |
| P1 | 刀2 提前 irecv + event + ack + 调度器 ack 门控 | LAST 批两卡 dequeue ~1ms;DDF(N+1) 与 DDL(N) 重叠可见 |
| P2 | 刀3 门控 `<limit`、`_force` 放松、inflight 提前释放、delay 旁路 | MTP 下 queue_len≥2;两卡利用率对齐非 MTP |
| P3 | 压测调参(batch_queue_size 等) | **MTP tokens/s ≈ 非 MTP**；TPOT 改善 ≥1.2× |

与前版的核心差异一句话：**TP=2 下“计算与 recv 分离”的执行点从 worker 层上移到调度器层--TP0 只负责“提前挂 irecv + 报就绪”，派发时机由 ack 决定，两卡的同步复用调度器 MQ 广播这个现成机制，TP1 一行不改。** 这也顺带把 §5.2.6 的 postprocess 风险消掉了：TP broadcast 留在晚派发的 LAST 里串行执行，锚点自然落在“event ready + broadcast 完成”上。


---

## User <sup>2026/8/16 15:13:00</sup>

阅读一下C:\theroadtofree_github\vllm-ascend\docs\PDbatch分离边云协同多实例调度详细设计_NEW.md中recv和计算分离，采用的方案是worker增加监控线程，上报scheduler； 与当前方案比哪个更好，哪个更容易实现


---

## Assistant <sup>2026/8/16 15:13:12</sup>


---

## Assistant <sup>2026/8/16 15:13:13</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 40,
  "output_mode": "content",
  "path": "C:\\theroadtofree_github\\vllm-ascend\\docs\\PDbatch分离边云协同多实例调度详细设计_NEW.md",
  "pattern": "^#{1,4} "
}
```

</details>


---

## User <sup>2026/8/16 15:13:13</sup>

<details>
<summary>Tool Result</summary>

```
1:# PD batch 分离边云协同推理 - 多实例调度详细设计
16:## 0 术语与上下文
37:### 当前基线（1:1 已落地）
46:### 设计原则
55:## 1 需求背景
57:### 1.1 1:1 瓶颈
65:### 1.2 N 实例重叠收益
74:### 1.3 收益约束
81:### 1.4 场景范围
99:## 2 配置方案
101:### 2.1 新增配置项
138:### 2.2 端口 / 通信 store 编码扩展
157:### 2.3 边侧模式
166:### 2.4 部署形态（边 2 卡，云 4 服务器 × 8 卡）
170:#### 形态一：四实例，dp=1（每实例单机 tp8，边 2 卡 tp2）
194:#### 形态二：2 实例，dp=2，dp 云双机
224:#### 形态三：四实例，dp=2，dp 云单机
250:#### 汇总对比
258:### 2.5 部署形态（边 1 卡，云 4 服务器 × 8 卡）
262:#### 形态一：四实例，dp=1（每实例单机 tp8，边单 rank）
284:#### 形态二：2 实例，dp=2，dp 云双机（边 1 卡 host 2 virtual worker）
317:#### 形态三：四实例，dp=2，dp 云单机（边 1 卡 host 2 virtual worker）
345:#### 汇总对比
355:### 2.6 部署形态（边 2 卡，云 2 服务器 × 16 卡，dp=1）--含每服务器多实例（新场景）
359:#### 形态一：2 实例（每服务器 1 实例，tp16）--标准形态，完全支持
381:#### 形态二：4 实例（每服务器 2 实例，tp8）--每服务器多实例，此前未考虑
404:#### 形态二支持项 / 不支持项分析
432:## 3 控制面方案
434:### 3.1 队列结构：per-instance 队列（方案 A）
446:### 3.2 两级结构
456:### 3.3 请求路由：两级层级分发
464:### 3.4 实例调度分层（方案 c，已选）
484:### 3.5 负载统计：InstanceLoadStats
497:### 3.6 balance_gather 前提（致命约束已核实）
510:### 3.7 ZMQ 收发
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:13:16</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 50,
  "output_mode": "content",
  "path": "C:\\theroadtofree_github\\vllm-ascend\\docs\\PDbatch分离边云协同多实例调度详细设计_NEW.md",
  "pattern": "监控线程|monitor|recv和计算分离|recv 与计算分离|recv_ready|irecv_ready"
}
```

</details>


---

## User <sup>2026/8/16 15:13:17</sup>

<details>
<summary>Tool Result</summary>

```
No matches found
```

</details>


---

## Assistant <sup>2026/8/16 15:13:19</sup>


---

## Assistant <sup>2026/8/16 15:13:20</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 60,
  "offset": 40,
  "output_mode": "content",
  "path": "C:\\theroadtofree_github\\vllm-ascend\\docs\\PDbatch分离边云协同多实例调度详细设计_NEW.md",
  "pattern": "^#{1,4} |^\\*\\*|^### "
}
```

</details>


---

## User <sup>2026/8/16 15:13:20</sup>

<details>
<summary>Tool Result</summary>

```
488:**关键纠正**：边侧是 **D 个 EngineCore/executor 进程**（每 DP rank 一个，`shared_model_multiproc_executor.py` "one edge executor process per DP rank"），不是 1 进程。"shared-model 1 进程"指 `SharedModelWorkerProc`（worker，1 进程 host D virtual 共享 nn.Module），EngineCore 是 D 个。
497:### 3.6 balance_gather 前提（致命约束已核实）
503:**替代方案（推荐 b）**：不引入 `BalanceDPEngineCoreProc`，在边云已 coord 适配的 `DPEngineCoreProc.run_busy_loop` **直接加一行 balance_gather**（复用已适配 run_busy_loop 避开 dummy 死锁，每步多 1 all_gather 与 coord all_reduce 不同信息 1:1 对齐可共存）。
510:### 3.7 ZMQ 收发线程：方案 1（沿用 per-channel）
518:### 3.8 控制通道可靠性
522:### 3.9 云侧双机相互感知（coord group）
528:### 3.10 启动期控制面：边 EngineCore ↔ 云实例 worker 的 method 链
530:**现状（1:1）**：借用 PP 下边是唯一 active EngineCore，云是 passive EngineCore；启动期边经 rpc_broadcast_mq 广播 -> 云 passive executor 落到云 worker -> 结果经 peer_worker_response_mqs 回收（patch_multiproc_executor.py:202-247）。启动链（core.py:231-291）：
539:**多实例（N=4）风险与要求**：
549:**结论**：collective_rpc 广播 + response 回收机制天然支持更多 rank，启动期改动集中在三处：§2.2 端口/store 偏移（硬前提）、启动编排逐实例串行握手（缓解 #2
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:13:24</sup>


---

## Assistant <sup>2026/8/16 15:13:24</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "C:\\theroadtofree_github\\vllm-ascend\\docs\\PDbatch分离边云协同多实例调度详细设计_NEW.md",
  "limit": 150,
  "offset": 714
}
```

</details>


---

## User <sup>2026/8/16 15:13:24</sup>

<details>
<summary>Tool Result</summary>

```
714	### 5.2 调度层计算/通信分离（核心改造）
715	
716	> 目标：TAIL 等 hidden 期间 worker 继续 dispatch 其它 round/实例，填满边侧空闲窗口。落地方式是把「recv」从 tail 计算里拆成**调度器可见的独立任务**，由调度器调度，依赖关系由「数据面完成信号」门控——即「通信任务完成后，才允许下发依赖该通信任务的计算任务」。
717	
718	#### 5.2.1 现状与阻塞点（fence 语义修正）
719	
720	当前 TAIL 在 round barrier 后同步 drain，worker 在等云 hidden 期间无法处理其它实例。代码路径：
721	
722	```
723	drain_batched_round (shared_model_edge_worker.py:367)
724	  ① deferred():373 -> AsyncIntermediateTensors(irecv 已发起未 wait)   [异步 ✅]
725	  ② execute_model_batched_tail:417 -> it["hidden_states"](:1058)
726	       -> wait_for_comm -> handle.wait() (gpu_worker.py:97)
727	```
728	
729	**fence 语义修正**：`handle.wait()` 对 NCCL/HCCL 设备通信**不阻塞 CPU**——它只做 `current_stream.wait_event(nccl_end_event)` + tensor `record_stream`，立即返回；真正阻塞 CPU 的是 `synchronize()`。所以 ② 不是「CPU 阻塞等 hidden」。
730	
731	**真正的串行点**（多实例无法重叠的根因，需实现期核实其一或若干）：
732	1. `round barrier`（:485）的 2DP lockstep——两 DP 都 drain 完 tail 才进下一 round；
733	2. tail 路径 sampler 的 D2H（`.item()` / `.cpu()`）——取采样结果回 CPU 的同步；
734	3. Engi
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:13:27</sup>


---

## Assistant <sup>2026/8/16 15:13:27</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "C:\\theroadtofree_github\\vllm-ascend\\docs\\PDbatch分离边云协同多实例调度详细设计_NEW.md",
  "limit": 14,
  "offset": 899
}
```

</details>


---

## User <sup>2026/8/16 15:13:27</sup>

<details>
<summary>Tool Result</summary>

```
899	
900	### 5.6 decode 单通道 send fence 与 DL 下发时机（计算/通信分离补充）
901	
902	**decode 单通道 send fence**：decode 每 (instance,dp) **单通道 + 单发送缓冲**，DF2 的 head compute 会覆盖 DF1 还在读的发送缓冲，必须在 DF2 head compute 前放一条设备侧 fence（非阻塞 `handle.wait()`）。per-instance 隔离：instance i 的 DF 与 instance j 的 DF 走不同 channel，互不干扰。
903	
904	**DL 30ms → recv fence**：现状 DL 被 `_can_schedule_decode_last` 的 30ms 延迟（`pd_separated_scheduler.py:1095`）同时推迟「irecv post」与「tail forward」。分离后：
905	- irecv（`COMM_RECV` 阶段1）在 DF isend 后**立即 post**，无需 30ms；
906	- tail forward（`COMPUTE`）由 **recv fence** 门控，无需 30ms。
907	
908	即 DL 的下发时机从「定时器」换成「数据面就绪」，与 §5.2.3 的 `COMM_RECV`/`COMPUTE` 依赖一致。严格交替 `DF isend → DL irecv → DF isend → DL irecv` 仍须保留（单 channel stream，否则跨侧死锁，见 `worker.py:1185-1190` 注释）。
909	
910	---
911	
912	## 6 KV 方案
```

</details>


---

## Assistant <sup>2026/8/16 15:14:17</sup>


---

## Assistant <sup>2026/8/16 15:14:42</sup>

NEW 文档的 §5.2(调度层计算/通信分离)+ §5.6 已读完。先速读归纳，再对比。

---

## 一、NEW 方案速读：它和当前方案是同一家族

NEW 方案的核心链路：

```
scheduler 派 COMPUTE(head) ──► 同时自投递 COMM_RECV(c2e)(post irecv + record event,立即返回)
        │                              │
        │                   worker 新增 per-(instance,dp) 完成线程(监控线程)
        │                   event.synchronize()/query() 等到就绪 ──► 写 recv_done_mq(新 sideband 队列)
        ▼                              ▼
COMPUTE(tail).depends_on={COMM_RECV} ◄── EngineCore 从 recv_done_mq drain 就绪信号,标记 ready 才下发
```

关键设计决定：**"worker 不 poll-and-run tail,tail 下发决策在 scheduler"**;`recv_done_mq` 明确**不复用 response_mq**(避免与 batch_queue 的 model output future 冲突)；DL 的 30ms 定时延迟换成 recv fence(数据面就绪门控)。

这与当前方案(TP0 busy-loop poll + ack 上报 + 调度器 ack-gated 派发)**在架构上是同一选择**：都是“数据面就绪 → 上报 scheduler → scheduler 门控尾层派发”。真正的差异只有三点：

| 维度 | NEW 方案 | 当前方案(TP=2 版) |
|---|---|---|
| **完成检测** | 专职监控线程，`event.synchronize()` 阻塞等待，就绪即报，时延≈0 | TP0 busy_loop 每轮 poll `event.query()`,时延 0~1ms(受 dequeue timeout 节拍限制；worker 忙于长 prefill 时被拉长) |
| **通知通道** | 新建 sideband `recv_done_mq`(仿 `cloud_recv_hint_mq` 先例) | 复用 response MQ + marker 过滤(引 PDFL POST_OUT 先例) |
| **任务模型** | 正式化:`TaskKind`/`WorkerTask`/`depends_on` 进 core 的 output.py;`execute_comm_recv` 独立 RPC | 不引入新抽象：扩展现有 `*_ready` 门控 + head_token stash,irecv 搭 FIRST 的车(比 NEW 方案还少一次 MQ 往返) |

另注意：NEW 方案的**原生语境是 shared-model 多实例**(round barrier 放宽、leader 1× 代算、2DP coord all_reduce lockstep、per-instance 完成线程)；它的 §5.2.1 还有一个重要的 **fence 语义修正**--`handle.wait()` 对 HCCL 设备通信不阻塞 CPU,真正卡 CPU 的是 sampler 的 D2H(`.item()`)和 EngineCore 的 `future.result()`。这个修正我上一轮表述不严谨(说“TP0 阻塞在 handle.wait”),但工程效果等价：worker 的 CPU 卡死在 LAST 执行内部 5-13ms,直到数据到齐+尾层完成，病灶定位不变，方案不受影响。

## 二、哪个更好

**架构完备性上 NEW 方案更好**，三个理由都站得住：

1. **检测时延**：监控线程与 busy-loop 完全解耦。当前方案的 poll 夹在 MQ dispatch 之间，worker 在跑一个长 prefill 时检测被推迟整个 forward 时长；单请求 MTP 场景 worker 大多空闲，差距 ~1ms,是二阶量，但多请求混合负载下会被放大。
2. **`recv_done_mq` 的警告是对的**：response_mq 的消息被 executor 按 future 配对消费，插入 ack 消息要么精心 tag+filter、要么就是隐患。我上一轮“复用 response MQ”低估了这一点--真要做安全过滤，工作量趋近于新建 sideband,那不如直接新建。
3. **路线一致性**：NEW 文档就是多-instance 路线图，现在按它的机制建，后续上多实例不用推倒重来。

**但就“TP=2 单实例打到盈亏平衡线”这个当前目标**，两方案的收益差距就是那 ~1ms 检测时延，相对被消掉的 5-13ms 网络暴露是二阶项。当前方案还有一处比 NEW 更优：irecv 搭 FIRST 执行的车，比“scheduler 下发 COMM_RECV 独立 RPC”**更早挂出**，还省一次 MQ 广播往返。

## 三、哪个更容易实现

**当前方案明显更容易**，差距不小：

| 成本项 | NEW 方案 | 当前方案 |
|---|---|---|
| core 层改动 | `TaskKind`/`WorkerTask`/`depends_on` 进 [output.py](vllm-pdmix/vllm/v1/core/sched/output.py),EngineCore 加 sideband drain 循环 | 零 core 抽象，scheduler 加一个 ack 集合 + pick 门控 |
| worker 层 | 新 RPC `execute_comm_recv` + **线程生命周期管理**(启停、异常、与主线程的 NPU 上下文交叉) | FIRST 路径加 ~20 行(irecv+event+stash) |
| 新增基础设施 | `recv_done_mq` 全套(创建/drain/关闭) | 无(sideband 仍需要一个，见下) |
| 拓扑适配 | 原生为 shared-model 写的：round barrier/leader tail/coord lockstep 在非 shared TP=2 下不存在，port 需重新论证 §5.3 全节 | 直接按 TP=2 结构设计(TP1 零改动) |
| 测试面 | 任务模型 + 线程 + 新 MQ 三层新 UT | 门控语义 + stash 配对 UT |

监控线程本身还有两个实现期风险 NEW 文档没有展开：非主线程调用 `event.query()`/`synchronize()` 的 torch-NPU 线程安全性，以及完成线程写 MQ 与主线程 dispatch 的顺序交织(它自己标注“需实现期核实”)。

## 四、建议：融合，分两步走

两方案核心相同，差异点可以按“先易后优”拆开吸收：

1. **P1 就用当前方案的骨架**(busy-loop poll + scheduler 门控)，但**吸收 NEW 的通道纪律**：就绪通知走独立 sideband(最小实现：一个专用 ZMQ pair 或复用 `cloud_recv_hint_mq` 的建法)，不走 response_mq。同时按 §5.2.1 的修正打点验证--确认阻塞消除要看 sampler D2H 前后的时间戳和 `future.result()` collect 时长，而不是 handle.wait。
2. **P3 视 profile 升级为监控线程**：如果压测显示 poll 节拍(尤其混合 prefill 负载)成为可见延迟，把“poll+写 sideband”原位替换为完成线程，sideband 协议和 scheduler 门控**不动**--这正是 NEW 方案里值钱的部分，而且是增量替换不是重构。
3. NEW 的 §5.6 两条直接采纳：DL/DL 相关定时延迟(pacing)换成数据面就绪门控(与刀3(4)一致)；单通道严格交替 `DF isend -> DL irecv` 的约束在 decode 通道保留，draft 通道独立后按 limit=2 论证。

一句话：**论最终形态，NEW 方案(监控线程 + recv_done_mq + 任务模型)更完备、是多实例路线的正确方向；论眼下 TP=2 打盈亏平衡线，当前轻量方案更务实--以它落地，把 NEW 的 sideband 纪律立即吸收、监控线程留作 profile 驱动的升级项，两边不冲突。**


---

## User <sup>2026/8/16 15:22:25</sup>

按方案实现逐步修改代码


---

## Assistant <sup>2026/8/16 15:22:53</sup>


---

## Assistant <sup>2026/8/16 15:22:54</sup>

开始实施。先建任务清单，然后从 P0(DRAFT 独立通道)动手。


---

## Assistant <sup>2026/8/16 15:22:58</sup>

<details>
<summary>Tool: <code>TodoWrite</code></summary>

```json
{
  "todos": [
    {
      "activeForm": "改造 HiddenChannelType 增加 draft 池",
      "content": "P0-1 output.py: HiddenChannelType 增加 draft 池 + draft()/DRAFT",
      "status": "in_progress"
    },
    {
      "activeForm": "改造 patch_distributed 增加 draft 通道组",
      "content": "P0-2 patch_distributed.py: create_hidden_channel_groups 增加 num_draft + _draft_*_groups",
      "status": "pending"
    },
    {
      "activeForm": "接入 draft 通道组创建与 warmup",
      "content": "P0-3 parallel_state.py: 创建 draft 组 + warmup 纳入 draft 通道",
      "status": "pending"
    },
    {
      "activeForm": "映射 DRAFT 批到独立通道",
      "content": "P0-4 worker.py + scheduler: DECODE_DRAFT 批映射/写入 DRAFT 通道",
      "status": "pending"
    },
    {
      "activeForm": "irecv 路径记录 NPU event",
      "content": "P1-1 parallel_state.py: irecv 后 record NPU event 并返回",
      "status": "pending"
    },
    {
      "activeForm": "增加 is_ready() 就绪判定",
      "content": "P1-2 gpu_worker.py: AsyncIntermediateTensors 加 _comm_event + is_ready()",
      "status": "pending"
    },
    {
      "activeForm": "实现提前 irecv 与 stash",
      "content": "P1-3 worker.py FIRST 路径: 提前挂 return-irecv + head_token stash",
      "status": "pending"
    },
    {
      "activeForm": "实现 busy-loop poll 与就绪上报",
      "content": "P1-4 multiproc_executor busy loop: poll 阶段 + sideband 就绪上报",
      "status": "pending"
    },
    {
      "activeForm": "实现 scheduler 就绪门控",
      "content": "P1-5 scheduler: DDL pick 门控改为 recv 就绪 ack",
      "status": "pending"
    },
    {
      "activeForm": "放宽调度门控",
      "content": "P2-1 scheduler: draft 门控 ==0 -> <limit + inflight 提前释放",
      "status": "pending"
    },
    {
      "activeForm": "旁路 pacing 延迟",
      "content": "P2-2 pacing 延迟旁路 + watchdog",
      "status": "pending"
    }
  ]
}
```

</details>


---

## User <sup>2026/8/16 15:22:58</sup>

<details>
<summary>Tool Result</summary>

```
Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable
```

</details>


---

## Assistant <sup>2026/8/16 15:23:00</sup>


---

## Assistant <sup>2026/8/16 15:23:01</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 30,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\worker\\patch_distributed.py",
  "pattern": "_prefill_device_groups|_decode_device_groups|def create_alternate_groups|def patch|_init_ "
}
```

</details>


---

## User <sup>2026/8/16 15:23:01</sup>

<details>
<summary>Tool Result</summary>

```
157:            # PREFILL channels: _prefill_device_groups[idx] / _prefill_cpu_groups[idx]
162:            # DECODE channels: _decode_device_groups[idx] / _decode_cpu_groups[idx]
167:            #   alt_device_group       -> _decode_device_groups[0]
169:            #   prefill2_device_group  -> _prefill_device_groups[1]
171:            self._prefill_device_groups: list[torch.distributed.ProcessGroup] = []
173:            self._decode_device_groups: list[torch.distributed.ProcessGroup] = []
177:            # len(_prefill_device_groups) is 1 and the range in
180:            self._prefill_device_groups.append(self.device_group)
279:        for groups in (self._prefill_device_groups, self._prefill_cpu_groups,
280:                       self._decode_device_groups, self._decode_cpu_groups):
284:        self._prefill_device_groups.clear()
286:        self._decode_device_groups.clear()
307:    def create_alternate_groups(
313:        Populates ``_decode_device_groups[0]`` / ``_decode_cpu_group
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:23:05</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\worker\\patch_distributed.py",
  "limit": 140,
  "offset": 150
}
```

</details>


---

## User <sup>2026/8/16 15:23:05</sup>

<details>
<summary>Tool Result</summary>

```
150	                group_name, self.ranks, self.world_size,
151	                self.backend,
152	            )
153	
154	            # Phase6 hidden data-plane channel groups (array-based for DP
155	            # scalability).
156	            #
157	            # PREFILL channels: _prefill_device_groups[idx] / _prefill_cpu_groups[idx]
158	            #   idx 0 -> PREFILL_1  (device_group / cpu_group)
159	            #   idx 1 -> PREFILL_2  (pg_options="pp_prefill2")
160	            #   idx N -> PREFILL_{N+1}(pg_options="pp_prefill{N+1}")
161	            #
162	            # DECODE channels: _decode_device_groups[idx] / _decode_cpu_groups[idx]
163	            #   idx 0 -> DECODE_1   (pg_options="pp_alt")
164	            #   idx M -> DECODE_{M+1}(pg_options="pp_decode{M+1}")
165	            #
166	            # Backward-compat aliases (via @property):
167	            #   alt_device_group       -> _decode_device_groups[0]
168	            #   alt_cpu_group          -> _decode_cpu_groups[0]
1
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:23:08</sup>


---

## Assistant <sup>2026/8/16 15:23:08</sup>

结构清楚了，开始 P0-1:给 `HiddenChannelType` 增加 draft 池。


---

## Assistant <sup>2026/8/16 15:23:09</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\core\\sched\\output.py",
  "old_string": "    _initialized: bool = False\n    _MIN_PREFILL_POOL: int = 16\n    _MIN_DECODE_POOL: int = 8",
  "new_string": "    _initialized: bool = False\n    _MIN_PREFILL_POOL: int = 16\n    _MIN_DECODE_POOL: int = 8\n    _MIN_DRAFT_POOL: int = 4"
}
```

</details>


---

## User <sup>2026/8/16 15:23:14</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-pdmix\vllm\v1\core\sched\output.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:23:22</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\core\\sched\\output.py",
  "old_string": "    @classmethod\n    def init(\n        cls,\n        dp_size: int,\n        prefill_per_dp: int = 2,\n        decode_per_dp: int = 1,\n    ) -> None:\n        if cls._initialized:\n            return\n        cls._initialized = True\n\n        need_prefill = dp_size * prefill_per_dp\n        need_decode = dp_size * decode_per_dp\n        prefill_pool = cls._MIN_PREFILL_POOL\n        decode_pool = cls._MIN_DECODE_POOL\n        while prefill_pool < need_prefill:\n            prefill_pool *= 2\n        while decode_pool < need_decode:\n            decode_pool *= 2\n\n        for i in range(1, prefill_pool + 1):\n            setattr(cls, f\"PREFILL_{i}\", cls(f\"prefill_{i}\"))\n        for i in range(1, decode_pool + 1):\n            setattr(cls, f\"DECODE_{i}\", cls(f\"decode_{i}\"))\n        setattr(cls, \"DECODE\", getattr(cls, \"DECODE_1\"))",
  "new_string": "    @classmethod\n    def init(\n        cls,\n        dp_size: int,\n        prefill_per_dp: int = 2,\n        decode_per_dp: int = 1,\n        draft_per_dp: int = 1,\n    ) -> None:\n        if cls._initialized:\n            return\n        cls._initialized = True\n\n        need_prefill = dp_size * prefill_per_dp\n        need_decode = dp_size * decode_per_dp\n        need_draft = dp_size * draft_per_dp\n        prefill_pool = cls._MIN_PREFILL_POOL\n        decode_pool = cls._MIN_DECODE_POOL\n        draft_pool = cls._MIN_DRAFT_POOL\n        while prefill_pool < need_prefill:\n            prefill_pool *= 2\n        while decode_pool < need_decode:\n            decode_pool *= 2\n        while draft_pool < need_draft:\n            draft_pool *= 2\n\n        for i in range(1, prefill_pool + 1):\n            setattr(cls, f\"PREFILL_{i}\", cls(f\"prefill_{i}\"))\n        for i in range(1, decode_pool + 1):\n            setattr(cls, f\"DECODE_{i}\", cls(f\"decode_{i}\"))\n        setattr(c
...(truncated)
```

</details>


---

## User <sup>2026/8/16 15:23:23</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-pdmix\vllm\v1\core\sched\output.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:23:27</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\core\\sched\\output.py",
  "old_string": "    @staticmethod\n    def decode(i: int) -> \"HiddenChannelType\":\n        return getattr(HiddenChannelType, f\"DECODE_{i}\")",
  "new_string": "    @staticmethod\n    def decode(i: int) -> \"HiddenChannelType\":\n        return getattr(HiddenChannelType, f\"DECODE_{i}\")\n\n    @staticmethod\n    def draft(i: int) -> \"HiddenChannelType\":\n        return getattr(HiddenChannelType, f\"DRAFT_{i}\")"
}
```

</details>


---

## User <sup>2026/8/16 15:23:28</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-pdmix\vllm\v1\core\sched\output.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:23:31</sup>

P0-1 完成。接着 P0-2:patch_distributed.py 增加 draft 通道组。


---

## Assistant <sup>2026/8/16 15:23:32</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\worker\\patch_distributed.py",
  "old_string": "            self._prefill_device_groups: list[torch.distributed.ProcessGroup] = []\n            self._prefill_cpu_groups: list[torch.distributed.ProcessGroup] = []\n            self._decode_device_groups: list[torch.distributed.ProcessGroup] = []\n            self._decode_cpu_groups: list[torch.distributed.ProcessGroup] = []",
  "new_string": "            self._prefill_device_groups: list[torch.distributed.ProcessGroup] = []\n            self._prefill_cpu_groups: list[torch.distributed.ProcessGroup] = []\n            self._decode_device_groups: list[torch.distributed.ProcessGroup] = []\n            self._decode_cpu_groups: list[torch.distributed.ProcessGroup] = []\n            # DRAFT channels (MTP draft data plane): _draft_device_groups[idx]\n            # idx 0 -> DRAFT_1 (pg_options=\"pp_draft1\")\n            self._draft_device_groups: list[torch.distributed.ProcessGroup] = []\n            self._draft_cpu_groups: list[torch.distributed.ProcessGroup] = []"
}
```

</details>


---

## User <sup>2026/8/16 15:23:33</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\worker\patch_distributed.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:23:37</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\worker\\patch_distributed.py",
  "old_string": "        # Destroy hidden channel groups (array-based).\n        for groups in (self._prefill_device_groups, self._prefill_cpu_groups,\n                       self._decode_device_groups, self._decode_cpu_groups):\n            for pg in groups:\n                if pg is not None:\n                    torch.distributed.destroy_process_group(pg)\n        self._prefill_device_groups.clear()\n        self._prefill_cpu_groups.clear()\n        self._decode_device_groups.clear()\n        self._decode_cpu_groups.clear()",
  "new_string": "        # Destroy hidden channel groups (array-based).\n        for groups in (self._prefill_device_groups, self._prefill_cpu_groups,\n                       self._decode_device_groups, self._decode_cpu_groups,\n                       self._draft_device_groups, self._draft_cpu_groups):\n            for pg in groups:\n                if pg is not None:\n                    torch.distributed.destroy_process_group(pg)\n        self._prefill_device_groups.clear()\n        self._prefill_cpu_groups.clear()\n        self._decode_device_groups.clear()\n        self._decode_cpu_groups.clear()\n        self._draft_device_groups.clear()\n        self._draft_cpu_groups.clear()"
}
```

</details>


---

## User <sup>2026/8/16 15:23:38</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\worker\patch_distributed.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:23:46</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\worker\\patch_distributed.py",
  "old_string": "    def create_hidden_channel_groups(\n        self,\n        torch_distributed_backend: str | Backend,\n        num_prefill: int = 2,\n        num_decode: int = 1,\n    ) -> None:\n        \"\"\"Create extra hidden-channel groups for DP-scalable PD separation.\n\n        The default device/cpu groups are PREFILL_1.\n        ``_decode_device_groups[0]`` (DECODE_1) is created by\n        ``create_alternate_groups``.\n\n        This method adds:\n          - PREFILL_2..num_prefill  (append to ``_prefill_device_groups``)\n          - DECODE_2..num_decode    (append to ``_decode_device_groups``)\n\n        Each group uses a unique ``pg_options`` name for HCCL stream isolation.\n        \"\"\"\n        # --- PREFILL groups (2..N) ---\n        # PREFILL_1 uses device_group; PREFILL_2 uses existing prefill2 alias.\n        for i in range(len(self._prefill_device_groups) + 1, num_prefill + 1):\n            self._create_one_hidden_channel(\n                f\"pp_prefill{i}\", torch_distributed_backend,\n                self._prefill_device_groups, self._prefill_cpu_groups,\n            )\n\n        # --- DECODE groups (2..M) ---\n        for i in range(len(self._decode_device_groups) + 1, num_decode + 1):\n            self._create_one_hidden_channel(\n                f\"pp_decode{i}\", torch_distributed_backend,\n                self._decode_device_groups, self._decode_cpu_groups,\n            )",
  "new_string": "    def create_hidden_channel_groups(\n        self,\n        torch_distributed_backend: str | Backend,\n        num_prefill: int = 2,\n        num_decode: int = 1,\n        num_draft: int = 0,\n    ) -> None:\n        \"\"\"Create extra hidden-channel groups for DP-scalable PD separation.\n\n        The default device/cpu groups are PREFILL_1.\n        ``_decode_device_groups[0]`` (DECODE_1) is created by\n        ``crea
...(truncated)
```

</details>


---

## User <sup>2026/8/16 15:23:47</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\worker\patch_distributed.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:23:51</sup>

现在我来修改 `_hidden_channel_groups` 以处理 `draft_M`：


---

## Assistant <sup>2026/8/16 15:23:53</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\worker\\patch_distributed.py",
  "old_string": "        value = getattr(channel, \"value\", channel)\n        logger.debug(\"[PP Group] _hidden_channel_groups: channel=%s -> value=%s\",\n                     channel, value)\n        if value == \"prefill_1\":\n            return self.device_group, self.cpu_group\n        if value == \"decode\":\n            # backward-compat: old DECODE alias\n            value = \"decode_1\"\n        if value.startswith(\"prefill_\"):\n            idx = int(value.split(\"_\")[1]) - 1\n            return self._prefill_device_groups[idx], self._prefill_cpu_groups[idx]\n        if value.startswith(\"decode_\"):\n            idx = int(value.split(\"_\")[1]) - 1\n            return self._decode_device_groups[idx], self._decode_cpu_groups[idx]\n        raise ValueError(f\"Unknown hidden channel: {channel}\")",
  "new_string": "        value = getattr(channel, \"value\", channel)\n        logger.debug(\"[PP Group] _hidden_channel_groups: channel=%s -> value=%s\",\n                     channel, value)\n        if value == \"prefill_1\":\n            return self.device_group, self.cpu_group\n        if value == \"decode\":\n            # backward-compat: old DECODE alias\n            value = \"decode_1\"\n        if value.startswith(\"prefill_\"):\n            idx = int(value.split(\"_\")[1]) - 1\n            return self._prefill_device_groups[idx], self._prefill_cpu_groups[idx]\n        if value.startswith(\"decode_\"):\n            idx = int(value.split(\"_\")[1]) - 1\n            return self._decode_device_groups[idx], self._decode_cpu_groups[idx]\n        if value.startswith(\"draft_\"):\n            idx = int(value.split(\"_\")[1]) - 1\n            return self._draft_device_groups[idx], self._draft_cpu_groups[idx]\n        raise ValueError(f\"Unknown hidden channel: {channel}\")"
}
```

</details>


---

## User <sup>2026/8/16 15:23:54</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\worker\patch_distributed.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:24:01</sup>


---

## Assistant <sup>2026/8/16 15:24:01</sup>

P0-2 完成。P0-3:parallel_state.py 调用点创建 draft 组，warmup 纳入 draft 通道。


---

## Assistant <sup>2026/8/16 15:24:04</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "old_string": "            if hasattr(pp_group, \"create_hidden_channel_groups\"):\n                dp_size = parallel_config.data_parallel_size\n                # Create extra hidden-channel groups based on dp_size.\n                if parallel_config.is_shared_model_edge:\n                    num_prefill = dp_size * 2\n                    num_decode = dp_size\n                else:\n                    num_prefill = 2\n                    num_decode = 1\n                logger.info(\n                    \"[PD] create_hidden_channel_groups: \"\n                    \"dp_size=%s dp_rank=%s num_prefill=%s num_decode=%s, \"\n                    \"edge_npu_count=%s\",\n                    dp_size,\n                    getattr(parallel_config, \"data_parallel_rank\", 0),\n                    num_prefill, num_decode,\n                    edge_npu_count,\n                )\n                HiddenChannelType.init(dp_size=num_decode)\n                pp_group.create_hidden_channel_groups(\n                    backend, num_prefill, num_decode,\n                )",
  "new_string": "            if hasattr(pp_group, \"create_hidden_channel_groups\"):\n                dp_size = parallel_config.data_parallel_size\n                # Create extra hidden-channel groups based on dp_size.\n                if parallel_config.is_shared_model_edge:\n                    num_prefill = dp_size * 2\n                    num_decode = dp_size\n                    num_draft = dp_size\n                else:\n                    num_prefill = 2\n                    num_decode = 1\n                    num_draft = 1\n                logger.info(\n                    \"[PD] create_hidden_channel_groups: \"\n                    \"dp_size=%s dp_rank=%s num_prefill=%s num_decode=%s \"\n                    \"num_draft=%s, edge_npu_count=%s\",\n                    dp_size,\n        
...(truncated)
```

</details>


---

## User <sup>2026/8/16 15:24:05</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:24:08</sup>

现在处理 `warmup` —— 将 `draft channels` 添加到 `channel_peers` 构建过程中：


---

## Assistant <sup>2026/8/16 15:24:16</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "old_string": "    prefill_groups = getattr(pp_group, \"_prefill_device_groups\", None)\n    decode_groups = getattr(pp_group, \"_decode_device_groups\", None)\n    channel_peers: list[tuple[HiddenChannelType, int]] = []\n    if prefill_groups is not None and decode_groups is not None:\n        num_prefill = len(prefill_groups)\n        num_decode = len(decode_groups)\n        if parallel_config.is_shared_model_edge:\n            dp_size = parallel_config.data_parallel_size\n            expected_world_size = dp_size + 1\n            if pp_group.world_size != expected_world_size:\n                logger.warning(\n                    \"[edge-cloud] hidden-channel warmup skipped: shared \"\n                    \"PP group size=%s, expected=%s\",\n                    pp_group.world_size, expected_world_size,\n                )\n                return\n            if num_prefill % dp_size or num_decode % dp_size:\n                raise RuntimeError(\n                    \"[edge-cloud] hidden-channel counts cannot be mapped \"\n                    f\"to shared DP peers: prefill={num_prefill}, \"\n                    f\"decode={num_decode}, dp_size={dp_size}\"\n                )\n            prefill_per_dp = num_prefill // dp_size\n            decode_per_dp = num_decode // dp_size\n            for dp_rank in range(dp_size):\n                peer_rank = dp_rank + 1\n                prefill_start = dp_rank * prefill_per_dp + 1\n                decode_start = dp_rank * decode_per_dp + 1\n                channel_peers.extend(\n                    (\n                        HiddenChannelType.prefill(channel_idx),\n                        peer_rank,\n                    )\n                    for channel_idx in range(\n                        prefill_start,\n                        prefill_start + prefill_per_dp,\n                    )\n                )\n
...(truncated)
```

</details>


---

## User <sup>2026/8/16 15:24:16</sup>

<details>
<summary>Tool Result</summary>

```
<tool_use_error>String to replace not found in file.
String:     prefill_groups = getattr(pp_group, "_prefill_device_groups", None)
    decode_groups = getattr(pp_group, "_decode_device_groups", None)
    channel_peers: list[tuple[HiddenChannelType, int]] = []
    if prefill_groups is not None and decode_groups is not None:
        num_prefill = len(prefill_groups)
        num_decode = len(decode_groups)
        if parallel_config.is_shared_model_edge:
            dp_size = parallel_config.data_parallel_size
            expected_world_size = dp_size + 1
            if pp_group.world_size != expected_world_size:
                logger.warning(
                    "[edge-cloud] hidden-channel warmup skipped: shared "
                    "PP group size=%s, expected=%s",
                    pp_group.world_size, expected_world_size,
                )
                return
            if num_prefill % dp_size or num_decode % dp_size:
                raise RuntimeError(
                    "
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:24:20</sup>


---

## Assistant <sup>2026/8/16 15:24:20</sup>

字符串不匹配，重新读取该段确认精确内容：


---

## Assistant <sup>2026/8/16 15:24:20</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "limit": 75,
  "offset": 1037
}
```

</details>


---

## User <sup>2026/8/16 15:24:20</sup>

<details>
<summary>Tool Result</summary>

```
1037	        return
1038	
1039	    prefill_groups = getattr(pp_group, "_prefill_device_groups", None)
1040	    decode_groups = getattr(pp_group, "_decode_device_groups", None)
1041	    channel_peers: list[tuple[HiddenChannelType, int]] = []
1042	    if prefill_groups is not None and decode_groups is not None:
1043	        num_prefill = len(prefill_groups)
1044	        num_decode = len(decode_groups)
1045	        if parallel_config.is_shared_model_edge:
1046	            dp_size = parallel_config.data_parallel_size
1047	            expected_world_size = dp_size + 1
1048	            if pp_group.world_size != expected_world_size:
1049	                logger.warning(
1050	                    "[edge-cloud] hidden-channel warmup skipped: shared "
1051	                    "PP group size=%s, expected=%s",
1052	                    pp_group.world_size,
1053	                    expected_world_size,
1054	                )
1055	                return
1056	            if num_prefill % dp_size or num_
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:24:22</sup>


---

## Assistant <sup>2026/8/16 15:24:23</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "old_string": "    prefill_groups = getattr(pp_group, \"_prefill_device_groups\", None)\n    decode_groups = getattr(pp_group, \"_decode_device_groups\", None)\n    channel_peers: list[tuple[HiddenChannelType, int]] = []",
  "new_string": "    prefill_groups = getattr(pp_group, \"_prefill_device_groups\", None)\n    decode_groups = getattr(pp_group, \"_decode_device_groups\", None)\n    draft_groups = getattr(pp_group, \"_draft_device_groups\", None)\n    channel_peers: list[tuple[HiddenChannelType, int]] = []"
}
```

</details>


---

## User <sup>2026/8/16 15:24:24</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:24:30</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "old_string": "                channel_peers.extend(\n                    (\n                        HiddenChannelType.decode(channel_idx),\n                        peer_rank,\n                    )\n                    for channel_idx in range(\n                        decode_start,\n                        decode_start + decode_per_dp,\n                    )\n                )\n        else:\n            if pp_group.world_size != 2:\n                logger.warning(\n                    \"[edge-cloud] hidden-channel warmup skipped: \"\n                    \"non-shared PP group size=%s, expected=2\",\n                    pp_group.world_size,\n                )\n                return\n            channel_peers.extend(\n                (HiddenChannelType.prefill(channel_idx), 1)\n                for channel_idx in range(1, num_prefill + 1)\n            )\n            channel_peers.extend(\n                (HiddenChannelType.decode(channel_idx), 1)\n                for channel_idx in range(1, num_decode + 1)\n            )",
  "new_string": "                channel_peers.extend(\n                    (\n                        HiddenChannelType.decode(channel_idx),\n                        peer_rank,\n                    )\n                    for channel_idx in range(\n                        decode_start,\n                        decode_start + decode_per_dp,\n                    )\n                )\n            # DRAFT channels (MTP draft data plane): one per dp_rank, peer =\n            # that dp_rank's cloud first-worker (same mapping as decode).\n            if draft_groups:\n                for dp_rank in range(min(len(draft_groups), dp_size)):\n                    channel_peers.append(\n                        (HiddenChannelType.draft(dp_rank + 1), dp_rank + 1)\n                    )\n        else:\n            if pp_group.world_size !=
...(truncated)
```

</details>


---

## User <sup>2026/8/16 15:24:31</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:24:43</sup>


---

## Assistant <sup>2026/8/16 15:24:44</sup>

P0-3 完成。P0-4 前先看 scheduler 里所有 decode-draft 通道赋值点：


---

## Assistant <sup>2026/8/16 15:24:44</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 55,
  "offset": 2195
}
```

</details>


---

## User <sup>2026/8/16 15:24:44</sup>

<details>
<summary>Tool Result</summary>

```
2195	            raise RuntimeError(
2196	                f"PREFILL_DRAFT_LAST expects a prefill hidden channel "
2197	                f"from {pool}, got {channel}"
2198	            )
2199	        expected = self.hidden_channel_manager.get_channel(
2200	            scheduler_output.draft_task_id
2201	        )
2202	        if expected != channel:
2203	            raise RuntimeError(
2204	                "PREFILL_DRAFT_LAST hidden channel mismatch: expected "
2205	                f"{expected}, got {channel}, "
2206	                f"draft_task_id={scheduler_output.draft_task_id}"
2207	            )
2208	
2209	    def _validate_decode_draft_tail_channel(
2210	        self, scheduler_output: SchedulerOutput
2211	    ) -> None:
2212	        if not scheduler_output.head_token:
2213	            raise RuntimeError("DECODE_DRAFT_LAST missing head_token")
2214	        if not scheduler_output.draft_task_id:
2215	            raise RuntimeError("DECODE_DRAFT_LAST missing draft_task_id")
2216	     
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:24:44</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 50,
  "offset": 2415
}
```

</details>


---

## User <sup>2026/8/16 15:24:44</sup>

<details>
<summary>Tool Result</summary>

```
2415	        if not self._uses_async_scheduled_mtp_placeholders():
2416	            return
2417	        if (
2418	            self.prefill_drafts_first_ready
2419	            or self.prefill_drafts_last_ready
2420	            or self.decode_drafts_first_ready
2421	            or self.decode_drafts_last_ready
2422	            or self._draft_first_cloud_publish_pending is not None
2423	        ):
2424	            return
2425	        kind = self._draft_kind_of(target_tail.batch_type)
2426	        if kind == "prefill":
2427	            first_type = BatchType.PREFILL_DRAFT_FIRST
2428	            ready_queue = self.prefill_drafts_first_ready
2429	            # Phase B（设计 §4.1/要点 3）：prefill_draft 链继承父 chunk 的
2430	            # Prefill 通道，PF(head) → PL(head) → prefill_draft*(head) 全程
2431	            # 同通道。通道释放已推迟到草稿链完成（§5.2），故此处通道
2432	            # 必在 manager 中。
2433	            inherited_channel = target_tail.hidden_channel
2434	        else:
2435	            first_type = BatchType.DECODE_
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:24:48</sup>


---

## Assistant <sup>2026/8/16 15:24:48</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 65,
  "offset": 2560
}
```

</details>


---

## User <sup>2026/8/16 15:24:48</sup>

<details>
<summary>Tool Result</summary>

```
2560	    def enqueue_draft_first(
2561	        self,
2562	        source: SchedulerOutput,
2563	        *,
2564	        draft_task_id: str,
2565	        draft_step_idx: int,
2566	        num_accepted_tokens: list[int] | None = None,
2567	        valid_sampled_token_count: list[int] | None = None,
2568	    ) -> bool:
2569	        """Generate a draft head locally, mirroring decode head generation.
2570	
2571	        The worker owns the mutable draft tensors, but the scheduler owns all
2572	        draft control-plane SchedulerOutputs. The initial step receives only
2573	        the rejection-corrected scalar state from the worker; follow-up steps
2574	        are derived directly from the completed draft tail.
2575	
2576	        The chain kind is inherited from ``source.batch_type``（设计 §3.3）：
2577	        PL/PDFL 源产生 prefill_draft，DL/DDL 源产生 decode_draft。
2578	        """
2579	        kind = self._draft_kind_of(source.batch_type)
2580	        if kind == "prefill":
2581	            first_
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:24:54</sup>


---

## Assistant <sup>2026/8/16 15:24:55</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 40,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "pattern": "hidden_channel|_decode_channel|_prefill_channel"
}
```

</details>


---

## User <sup>2026/8/16 15:24:55</sup>

<details>
<summary>Tool Result</summary>

```
52:    hidden_channel : HiddenChannelType
63:    hidden_channel: HiddenChannelType
115:        self._decode_channel = HiddenChannelType.decode(dp_rank + 1)
156:        return self._decode_channel
178:        return frozenset((self._decode_channel,))
459:        self.hidden_channel_manager = HiddenChannelManager(
466:            self.hidden_channel_manager.prefill_pool,
467:            self.hidden_channel_manager.decode_pool,
1042:        self.hidden_channel_manager.release_prefill(head_token)
1532:            and self.hidden_channel_manager.has_free_prefill()
1886:                    scheduler_output.hidden_channel = (
1887:                        self.hidden_channel_manager.allocate_prefill(
1937:                                    hidden_channel=(
1938:                                        scheduler_output.hidden_channel
2153:        channel = scheduler_output.hidden_channel
2156:        pool = self.hidden_channel_manager.prefill_pool
2162:        expected = self.hidden_channel_man
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:24:58</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 80,
  "offset": 105
}
```

</details>


---

## User <sup>2026/8/16 15:24:58</sup>

<details>
<summary>Tool Result</summary>

```
105	        prefill_per_dp: int = _PREFILL_CHANNELS_PER_DP,
106	        is_shared_model_edge: bool = False,
107	    ) -> None:
108	        if not is_shared_model_edge:
109	            dp_rank = 0
110	        prefill_start = dp_rank * prefill_per_dp + 1
111	        self._free_prefills: deque[HiddenChannelType] = deque(
112	            HiddenChannelType.prefill(i)
113	            for i in range(prefill_start, prefill_start + prefill_per_dp)
114	        )
115	        self._decode_channel = HiddenChannelType.decode(dp_rank + 1)
116	        self._head_token_to_channel: dict[str, HiddenChannelType] = {}
117	
118	    # ------------------------------------------------------------------ #
119	    # Prefill channel allocation / release                               #
120	    # ------------------------------------------------------------------ #
121	    def allocate_prefill(self, head_token: str) -> HiddenChannelType:
122	        """Allocate a free prefill channel for the batch identified by
123	
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:24:58</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 45,
  "offset": 2145
}
```

</details>


---

## User <sup>2026/8/16 15:24:58</sup>

<details>
<summary>Tool Result</summary>

```
2145	        # PREFILL_DRAFT_FIRST（链由 _pregenerate_draft_chain 生成）。状态机
2146	        # 按构造时的 MTP 使能决定是否启动 prefill 窗口——非 MTP 无链可等，
2147	        # 启动只会白白锁 15ms（等价现状运行时门控，配置构造后不变）。
2148	        self._force.on_pick(BatchType.PREFILL_LAST)
2149	        return so
2150	
2151	    def _validate_prefill_tail_channel(self, scheduler_output: SchedulerOutput) -> None:
2152	        token = scheduler_output.head_token
2153	        channel = scheduler_output.hidden_channel
2154	        if not token:
2155	            raise RuntimeError("PREFILL_LAST missing head_token")
2156	        pool = self.hidden_channel_manager.prefill_pool
2157	        if channel not in pool:
2158	            raise RuntimeError(
2159	                f"PREFILL_LAST expects a prefill hidden channel from "
2160	                f"{pool}, got {channel}"
2161	            )
2162	        expected = self.hidden_channel_manager.get_channel(token)
2163	        if expected != channel:
2164	            raise RuntimeError(
2165	               
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:25:04</sup>


---

## Assistant <sup>2026/8/16 15:25:04</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 35,
  "offset": 3195
}
```

</details>


---

## User <sup>2026/8/16 15:25:04</sup>

<details>
<summary>Tool Result</summary>

```
3195	
3196	        self.chunk_prefill_first = []
3197	        self.waiting = create_request_queue(self.policy)
3198	        self.skipped_waiting = create_request_queue(self.policy)
3199	
3200	        scheduler_output = None
3201	        try:
3202	            scheduler_output = super().schedule()
3203	        finally:
3204	            if scheduler_output is not None:
3205	                if scheduler_output.total_num_scheduled_tokens == 0:
3206	                    scheduler_output.batch_type = BatchType.EMPTY
3207	                    logger.debug(
3208	                        "DECODE_FIRST race: empty batch due to async "
3209	                        "update_from_output delay, running=%d",
3210	                        len(self.running),
3211	                    )
3212	                else:
3213	                    scheduler_output.batch_type = BatchType.DECODE_FIRST
3214	                    scheduler_output.head_token = uuid4().hex
3215	                    scheduler_output.hidden_channe
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:25:07</sup>


---

## Assistant <sup>2026/8/16 15:25:07</sup>

现在依次修改。HiddenChannelManager 加 draft 通道:


---

## Assistant <sup>2026/8/16 15:25:08</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "        self._decode_channel = HiddenChannelType.decode(dp_rank + 1)\n        self._head_token_to_channel: dict[str, HiddenChannelType] = {}",
  "new_string": "        self._decode_channel = HiddenChannelType.decode(dp_rank + 1)\n        # MTP draft data plane: DECODE_DRAFT_* batches travel on their own\n        # channel so the draft chain never contends with the shared DECODE\n        # channel.  One draft channel per dp_rank, fixed like decode (no\n        # free-list).\n        self._draft_channel = HiddenChannelType.draft(dp_rank + 1)\n        self._head_token_to_channel: dict[str, HiddenChannelType] = {}"
}
```

</details>


---

## User <sup>2026/8/16 15:25:09</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:25:13</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "    def decode_channel(self) -> HiddenChannelType:\n        return self._decode_channel",
  "new_string": "    def decode_channel(self) -> HiddenChannelType:\n        return self._decode_channel\n\n    def draft_channel(self) -> HiddenChannelType:\n        \"\"\"Dedicated MTP draft channel for this dp_rank.\"\"\"\n        return self._draft_channel"
}
```

</details>


---

## User <sup>2026/8/16 15:25:14</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:25:16</sup>

现在更新三个赋值点和校验点：


---

## Assistant <sup>2026/8/16 15:25:17</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "        if scheduler_output.hidden_channel != HiddenChannelType.DECODE:\n            raise RuntimeError(\n                \"DECODE_DRAFT_LAST expects decode hidden channel, got \"\n                f\"{scheduler_output.hidden_channel}\"\n            )",
  "new_string": "        if scheduler_output.hidden_channel != self.draft_channel:\n            raise RuntimeError(\n                \"DECODE_DRAFT_LAST expects the dedicated draft hidden \"\n                f\"channel {self.draft_channel}, got \"\n                f\"{scheduler_output.hidden_channel}\"\n            )"
}
```

</details>


---

## User <sup>2026/8/16 15:25:18</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:25:22</sup>


---

## Assistant <sup>2026/8/16 15:25:23</sup>

修正：校验函数在 scheduler 类里,要走 `hidden_channel_manager`:


---

## Assistant <sup>2026/8/16 15:25:23</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "        if scheduler_output.hidden_channel != self.draft_channel:\n            raise RuntimeError(\n                \"DECODE_DRAFT_LAST expects the dedicated draft hidden \"\n                f\"channel {self.draft_channel}, got \"\n                f\"{scheduler_output.hidden_channel}\"\n            )",
  "new_string": "        if scheduler_output.hidden_channel != (\n            self.hidden_channel_manager.draft_channel()\n        ):\n            raise RuntimeError(\n                \"DECODE_DRAFT_LAST expects the dedicated draft hidden \"\n                f\"channel {self.hidden_channel_manager.draft_channel()}, \"\n                f\"got {scheduler_output.hidden_channel}\"\n            )"
}
```

</details>


---

## User <sup>2026/8/16 15:25:25</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:25:28</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "        if kind == \"decode\":\n            # decode 域固定 DECODE 通道（设计 §4.2）。\n            scheduler_output.hidden_channel = HiddenChannelType.DECODE",
  "new_string": "        if kind == \"decode\":\n            # decode_draft 域走独立 DRAFT 通道（不再与 DECODE 共享，这是\n            # 放宽 draft 串行门控的前提：共享通道时边云可能互相等对方\n            # 方向的 send 才 post 匹配 recv，会死锁）。\n            scheduler_output.hidden_channel = (\n                self.hidden_channel_manager.draft_channel()\n            )"
}
```

</details>


---

## User <sup>2026/8/16 15:25:29</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:25:33</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "        else:\n            first_type = BatchType.DECODE_DRAFT_FIRST\n            ready_queue = self.decode_drafts_first_ready\n            inherited_channel = HiddenChannelType.DECODE\n        req_ids = list(target_tail.num_scheduled_tokens)",
  "new_string": "        else:\n            first_type = BatchType.DECODE_DRAFT_FIRST\n            ready_queue = self.decode_drafts_first_ready\n            # decode_draft 占位链继承 DRAFT 通道（与 _pick_draft_first_\n            # batch_by_kind 的 decode 分支一致）。\n            inherited_channel = (\n                self.hidden_channel_manager.draft_channel()\n            )\n        req_ids = list(target_tail.num_scheduled_tokens)"
}
```

</details>


---

## User <sup>2026/8/16 15:25:34</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:25:38</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "        else:\n            first_type = BatchType.DECODE_DRAFT_FIRST\n            ready_queue = self.decode_drafts_first_ready\n            inherited_channel = HiddenChannelType.DECODE\n        req_ids = list(source.num_scheduled_tokens)",
  "new_string": "        else:\n            first_type = BatchType.DECODE_DRAFT_FIRST\n            ready_queue = self.decode_drafts_first_ready\n            # decode_draft 链固定 DRAFT 通道（独立数据面，见\n            # HiddenChannelManager.draft_channel）。\n            inherited_channel = (\n                self.hidden_channel_manager.draft_channel()\n            )\n        req_ids = list(source.num_scheduled_tokens)"
}
```

</details>


---

## User <sup>2026/8/16 15:25:39</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:25:47</sup>


---

## Assistant <sup>2026/8/16 15:25:47</sup>

worker.py 的 `_hidden_channel_for` 映射:


---

## Assistant <sup>2026/8/16 15:25:48</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "old_string": "        if bt in (\n            BatchType.DECODE_DRAFT_FIRST,\n            BatchType.DECODE_DRAFT_LAST,\n        ):\n            return HiddenChannelType.DECODE",
  "new_string": "        if bt in (BatchType.DREF_FIRST_ALIAS\n                  if False else (BatchType.DECODE_DRAFT_FIRST,\n                                 BatchType.DECODE_DRAFT_LAST)):\n            # MTP draft data plane travels on its dedicated DRAFT channel\n            # (scheduler writes it at pick time; this is the fallback when\n            # the SchedulerOutput carries no channel).  Sharing the DECODE\n            # channel would force the scheduler's draft serialization gate.\n            return HiddenChannelType.DRAFT"
}
```

</details>


---

## User <sup>2026/8/16 15:25:49</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\worker\worker.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:25:53</sup>


---

## Assistant <sup>2026/8/16 15:25:53</sup>

写入了一段残渣代码，立即清理：


---

## Assistant <sup>2026/8/16 15:25:55</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "old_string": "        if bt in (BatchType.DREF_FIRST_ALIAS\n                  if False else (BatchType.DECODE_DRAFT_FIRST,\n                                 BatchType.DECODE_DRAFT_LAST)):\n            # MTP draft data plane travels on its dedicated DRAFT channel\n            # (scheduler writes it at pick time; this is the fallback when\n            # the SchedulerOutput carries no channel).  Sharing the DECODE\n            # channel would force the scheduler's draft serialization gate.\n            return HiddenChannelType.DRAFT",
  "new_string": "        if bt in (\n            BatchType.DECODE_DRAFT_FIRST,\n            BatchType.DECODE_DRAFT_LAST,\n        ):\n            # MTP draft data plane travels on its dedicated DRAFT channel\n            # (scheduler writes it at pick time; this is the fallback when\n            # the SchedulerOutput carries no channel).  Sharing the DECODE\n            # channel would force the scheduler's draft serialization gate.\n            return HiddenChannelType.DRAFT"
}
```

</details>


---

## User <sup>2026/8/16 15:25:56</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\worker\worker.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:26:08</sup>


---

## Assistant <sup>2026/8/16 15:26:08</sup>

P0-4 主体完成。更新受影响的单测(test_pd_draft_drain.py 里 DDL 的通道断言):


---

## Assistant <sup>2026/8/16 15:26:08</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\tests\\ut\\test_pd_draft_drain.py",
  "limit": 130,
  "offset": 30
}
```

</details>


---

## User <sup>2026/8/16 15:26:08</sup>

<details>
<summary>Tool Result</summary>

```
30	  * ``_run_edge_cloud_draft_last_segment`` drains (recv already done by the
31	    caller, skip tail compute, return a token-less placeholder) when the draft
32	    context is gone, instead of raising.
33	  * Every middle prefill chunk runs a complete draft chain to populate MTP KV,
34	    while its proposals are discarded and no target verify placeholder is
35	    created.
36	"""
37	
38	from collections import deque
39	from unittest.mock import MagicMock
40	
41	import pytest
42	
43	from vllm.v1.core.sched.output import (
44	    BatchType,
45	    HiddenChannelType,
46	    SchedulerOutput,
47	)
48	
49	
50	# ------------------------------------------------------------------ #
51	# Helpers                                                            #
52	# ------------------------------------------------------------------ #
53	
54	
55	def _make_bare_scheduler():
56	    from vllm_ascend.core.pd_separated_scheduler import (
57	        EdgeForceStateMachine,
58	        PDSeparatedScheduler,
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:26:12</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "cd /c/kisella_mtp/vllm-ascend-pdmix && sed -i 's/so.hidden_channel = HiddenChannelType.DECODE$/so.hidden_channel = HiddenChannelType.DRAFT/' tests/ut/test_pd_draft_drain.py && grep -n \"hidden_channel = HiddenChannelType\" tests/ut/test_pd_draft_drain.py",
  "description": "将测试中 draft SO 的通道从 DECODE 改为 DRAFT"
}
```

</details>


---

## User <sup>2026/8/16 15:26:16</sup>

<details>
<summary>Tool Result</summary>

```
89:    so.hidden_channel = HiddenChannelType.DRAFT
105:    so.hidden_channel = HiddenChannelType.DRAFT
```

</details>


---

## Assistant <sup>2026/8/16 15:26:20</sup>


---

## Assistant <sup>2026/8/16 15:26:20</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "python -m pytest tests/ut/test_pd_draft_drain.py -x -q 2>&1 | tail -20",
  "description": "运行 draft drain 单测验证改动",
  "timeout": 300000
}
```

</details>


---

## User <sup>2026/8/16 15:26:25</sup>

<details>
<summary>Tool Result</summary>

```
C:\Users\root\AppData\Local\Programs\Python\Python314\python.exe: No module named pytest
```

</details>


---

## Assistant <sup>2026/8/16 15:26:29</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "ls /c/kisella_mtp/ | head -30; ls /c/kisella_mtp/*.txt 2>/dev/null; find /c/kisella_mtp -maxdepth 2 -name \"*.cfg\" -o -maxdepth 2 -name \"requirements*.txt\" 2>/dev/null | head; which python3 python; python --version",
  "description": "查找可用的 Python 测试环境"
}
```

</details>


---

## User <sup>2026/8/16 15:26:31</sup>

<details>
<summary>Tool Result</summary>

```
log
vllm-ascend-pdmix
vllm-pdmix
/c/kisella_mtp/vllm-ascend-pdmix/requirements-dev.txt
/c/kisella_mtp/vllm-ascend-pdmix/requirements-lint.txt
/c/kisella_mtp/vllm-ascend-pdmix/requirements.txt
/c/Users/root/AppData/Local/Microsoft/WindowsApps/python3
/c/Users/root/AppData/Local/Programs/Python/Python314/python
Python 3.14.2
```

</details>


---

## Assistant <sup>2026/8/16 15:26:34</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "ls /c/ | head -20; ls /c/vllm_gitcode_new 2>/dev/null | head; find /c -maxdepth 2 -name \"python.exe\" -path \"*conda*\" 2>/dev/null | head -5; find /c -maxdepth 3 -name \"activate\" -path \"*venv*\" 2>/dev/null | head -5",
  "description": "查找 conda/venv 环境"
}
```

</details>


---

## User <sup>2026/8/16 15:26:40</sup>

<details>
<summary>Tool Result</summary>

```
$360Honeypot
$360LockFile
$360Section
$Recycle.Bin
0804bug
1120
1124
1125
1126
360SANDBOX
Documents and Settings
DumpStack.log.tmp
Kisella
Kisella_aclgraph
Kisella_debug
Kisella_dev
Kisella_ds
Kisella_github
Kisella_layer_update
Lapi
vllm
vllm-ascend
```

</details>


---

## Assistant <sup>2026/8/16 15:26:44</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "ls /c/Kisella 2>/dev/null | head; ls /c/Miniconda3 /c/Anaconda3 2>/dev/null | head -3; find /c/Users/root -maxdepth 3 -name \"python.exe\" 2>/dev/null | grep -iv \"WindowsApps\\|Python3\" | head -5",
  "description": "继续查找可用的 Python 环境"
}
```

</details>


---

## User <sup>2026/8/16 15:26:45</sup>

<details>
<summary>Tool Result</summary>

```
MindIE-LLM_open_ds_double
```

</details>


---

## Assistant <sup>2026/8/16 15:26:49</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "find /c/Users/root/AppData/Local/Programs -maxdepth 2 -name \"python.exe\" 2>/dev/null; ls /c/vllm_gitcode_new 2>/dev/null | head; find /d /e -maxdepth 3 -name \"python.exe\" -path \"*conda*\" 2>/dev/null | head -3",
  "description": "查找其他盘符的 Python 环境"
}
```

</details>


---

## User <sup>2026/8/16 15:26:53</sup>

<details>
<summary>Tool Result</summary>

```
vllm
vllm-ascend
```

</details>


---

## Assistant <sup>2026/8/16 15:26:57</sup>


---

## Assistant <sup>2026/8/16 15:26:57</sup>

本机没有带 pytest 的环境(实际验证需在 NPU 机器)，先用编译检查做语法级验证：


---

## Assistant <sup>2026/8/16 15:26:58</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "python -m py_compile vllm_ascend/core/pd_separated_scheduler.py vllm_ascend/worker/worker.py vllm_ascend/distributed/parallel_state.py vllm_ascend/patch/worker/patch_distributed.py ../vllm-pdmix/vllm/v1/core/sched/output.py tests/ut/test_pd_draft_drain.py && echo SYNTAX_OK",
  "description": "py_compile 验证已改文件语法"
}
```

</details>


---

## User <sup>2026/8/16 15:27:44</sup>

<details>
<summary>Tool Result</summary>

```
vllm_ascend/worker/worker.py:300: SyntaxWarning: 'return' in a 'finally' block
  return
SYNTAX_OK
```

</details>


---

## Assistant <sup>2026/8/16 15:28:08</sup>


---

## Assistant <sup>2026/8/16 15:28:09</sup>

P0 全部完成，语法通过。进入 P1-1:irecv 路径记录 NPU event。


---

## Assistant <sup>2026/8/16 15:28:12</sup>

<details>
<summary>Tool: <code>TodoWrite</code></summary>

```json
{
  "todos": [
    {
      "activeForm": "改造 HiddenChannelType 增加 draft 池",
      "content": "P0-1 output.py: HiddenChannelType 增加 draft 池 + draft()/DRAFT",
      "status": "completed"
    },
    {
      "activeForm": "改造 patch_distributed 增加 draft 通道组",
      "content": "P0-2 patch_distributed.py: create_hidden_channel_groups 增加 num_draft + _draft_*_groups",
      "status": "completed"
    },
    {
      "activeForm": "接入 draft 通道组创建与 warmup",
      "content": "P0-3 parallel_state.py: 创建 draft 组 + warmup 纳入 draft 通道",
      "status": "completed"
    },
    {
      "activeForm": "映射 DRAFT 批到独立通道",
      "content": "P0-4 worker.py + scheduler: DECODE_DRAFT 批映射/写入 DRAFT 通道",
      "status": "completed"
    },
    {
      "activeForm": "irecv 路径记录 NPU event",
      "content": "P1-1 parallel_state.py: irecv 后 record NPU event 并返回",
      "status": "in_progress"
    },
    {
      "activeForm": "增加 is_ready() 就绪判定",
      "content": "P1-2 gpu_worker.py: AsyncIntermediateTensors 加 _comm_event + is_ready()",
      "status": "pending"
    },
    {
      "activeForm": "实现提前 irecv 与 stash",
      "content": "P1-3 worker.py FIRST 路径: 提前挂 return-irecv + head_token stash",
      "status": "pending"
    },
    {
      "activeForm": "实现 busy-loop poll 与就绪上报",
      "content": "P1-4 multiproc_executor busy loop: poll 阶段 + sideband 就绪上报",
      "status": "pending"
    },
    {
      "activeForm": "实现 scheduler 就绪门控",
      "content": "P1-5 scheduler: DDL pick 门控改为 recv 就绪 ack",
      "status": "pending"
    },
    {
      "activeForm": "放宽调度门控",
      "content": "P2-1 scheduler: draft 门控 ==0 -> <limit + inflight 提前释放",
      "status": "pending"
    },
    {
      "activeForm": "旁路 pacing 延迟",
      "content": "P2-2 pacing 延迟旁路 + watchdog",
      "status": "pending"
    }
  ]
}
```

</details>


---

## User <sup>2026/8/16 15:28:12</sup>

<details>
<summary>Tool Result</summary>

```
Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable
```

</details>


---

## Assistant <sup>2026/8/16 15:28:17</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "old_string": "        else:\n            full_tensor = torch.empty(\n                full_size, dtype=value.dtype, device=value.device\n            )\n            if full_tensor.numel() > 0:\n                full_tensor.zero_()\n        tensor_dict[key] = full_tensor\n\n    return tensor_dict, handles, postprocess",
  "new_string": "        else:\n            full_tensor = torch.empty(\n                full_size, dtype=value.dtype, device=value.device\n            )\n            if full_tensor.numel() > 0:\n                full_tensor.zero_()\n        tensor_dict[key] = full_tensor\n\n    # [MTP async tail] Record one NPU event on the channel stream covering\n    # every irecv issued above (they all share the channel stream, so a\n    # single event suffices).  ``event.query()`` then provides a\n    # non-blocking \"recv done\" signal the worker can poll - we use an\n    # explicit device event because HCCL ``Work.is_completed`` support is\n    # uncertain.  The event rides on the dict under a private key; the\n    # edge worker pops it when constructing AsyncIntermediateTensors.\n    if handles:\n        with _hidden_channel_stream_ctx(\n            channel, wait_for_default=False\n        ):\n            comm_event = torch.npu.Event()\n            comm_event.record()\n        tensor_dict[\"__comm_event__\"] = comm_event\n\n    return tensor_dict, handles, postprocess"
}
```

</details>


---

## User <sup>2026/8/16 15:28:18</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:28:29</sup>


---

## Assistant <sup>2026/8/16 15:28:29</sup>

P1-1 完成。P1-2:`AsyncIntermediateTensors` 加 event 与 `is_ready()`:


---

## Assistant <sup>2026/8/16 15:28:34</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\worker\\gpu_worker.py",
  "old_string": "class AsyncIntermediateTensors(IntermediateTensors):\n    \"\"\"IntermediateTensors with lazy comm synchronization\"\"\"\n\n    def __init__(\n        self,\n        tensors: dict[str, torch.Tensor],\n        comm_handles: list[Handle] | None = None,\n        comm_postprocess: list[Callable[[], None]] | None = None,\n    ) -> None:\n        super().__init__(tensors)\n        self._comm_handles = comm_handles\n        self._comm_postprocess = comm_postprocess\n        self._comm_waited = False\n\n    def wait_for_comm(self) -> None:\n        if self._comm_waited:\n            return\n        if self._comm_handles:\n            for handle in self._comm_handles:\n                handle.wait()\n        if self._comm_postprocess:\n            for fn in self._comm_postprocess:\n                fn()\n        self._comm_waited = True",
  "new_string": "class AsyncIntermediateTensors(IntermediateTensors):\n    \"\"\"IntermediateTensors with lazy comm synchronization\"\"\"\n\n    def __init__(\n        self,\n        tensors: dict[str, torch.Tensor],\n        comm_handles: list[Handle] | None = None,\n        comm_postprocess: list[Callable[[], None]] | None = None,\n        comm_event: Any = None,\n    ) -> None:\n        super().__init__(tensors)\n        self._comm_handles = comm_handles\n        self._comm_postprocess = comm_postprocess\n        # Optional device event recorded on the recv stream right after the\n        # irecv(s) were issued (edge-cloud PD separation).  When present,\n        # ``is_ready()`` gives a non-blocking readiness probe for the *recv\n        # transfer only* - the TP broadcast / split postprocess chain is NOT\n        # covered by this event and still requires ``wait_for_comm()``.\n        self._comm_event = comm_event\n        self._comm_waited = False\n\n    def is_ready(self) -> bool:\n        \"\"\"Non-blocking probe: h
...(truncated)
```

</details>


---

## User <sup>2026/8/16 15:28:35</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-pdmix\vllm\v1\worker\gpu_worker.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:28:39</sup>


---

## Assistant <sup>2026/8/16 15:28:40</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"^from typing\\|^import typing\\|from typing import\" /c/kisella_mtp/vllm-pdmix/vllm/v1/worker/gpu_worker.py | head -3; grep -rn \"AsyncIntermediateTensors\" /c/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/worker/edge_cloud/shared_model_edge_worker.py | head -5",
  "description": "检查 typing 导入与 AsyncIntermediateTensors 引用来源"
}
```

</details>


---

## User <sup>2026/8/16 15:28:41</sup>

<details>
<summary>Tool Result</summary>

```
11:from typing import TYPE_CHECKING, Any
60:from vllm.v1.worker.gpu_worker import AsyncIntermediateTensors
611:    def do_direct_recv(self) -> "AsyncIntermediateTensors":
640:        return AsyncIntermediateTensors(
948:            intermediate_tensors = AsyncIntermediateTensors(
1119:        ``AsyncIntermediateTensors``; the batched tail call in the
```

</details>


---

## Assistant <sup>2026/8/16 15:28:49</sup>


---

## Assistant <sup>2026/8/16 15:28:49</sup>

P1-2 完成。P1-3 之前必须搞清 worker.py 里已有的 CHER(cloud hint early recv)机制和 draft tail 的执行路径：


---

## Assistant <sup>2026/8/16 15:28:49</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "limit": 120,
  "offset": 800
}
```

</details>


---

## User <sup>2026/8/16 15:28:49</sup>

<details>
<summary>Tool Result</summary>

```
800	            for handles in self._pp_send_work_by_channel.values():
801	                for handle in handles:
802	                    handle.wait()
803	            self._pp_send_work_by_channel.clear()
804	            return
805	
806	        handles = self._pp_send_work_by_channel.pop(channel.value, [])
807	        logger.info(
808	            "[PD] _wait_pp_send_work: channel=%s handles=%d",
809	            channel.value,
810	            len(handles),
811	        )
812	        for handle in handles:
813	            handle.wait()
814	
815	    # ------------------------------------------------------------------ #
816	    # [CHER/EHER] Cloud/edge hidden early-receive primitives             #
817	    # ------------------------------------------------------------------ #
818	    # The guard thread calls start_early_irecv() to post an irecv ahead of
819	    # the batch's execute_model (keyed by head_token); execute_model calls
820	    # get_or_post_early_recv() to consume/reuse it.  The
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:28:57</sup>


---

## Assistant <sup>2026/8/16 15:28:57</sup>

**重大发现：CHER/EHER 早收基础设施已经存在**(`start_early_irecv` + `get_or_post_early_recv`,按 head_token 幂等挂 irecv)。P1-3/4 的工作量大幅下降。先看 guard 线程与 draft tail 消费点：


---

## Assistant <sup>2026/8/16 15:28:58</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 30,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-ascend-pdmix",
  "pattern": "start_early_irecv|get_or_post_early_recv|_early_recv_handles|cloud_recv_hint|_guard_thread|guard_thread"
}
```

</details>


---

## User <sup>2026/8/16 15:28:58</sup>

<details>
<summary>Tool Result</summary>

```
vllm_ascend\worker\worker.py:239:        self._early_recv_handles: dict[str, AsyncIntermediateTensors] = {}
vllm_ascend\worker\worker.py:241:        # head_tokens already consumed by busy_loop (get_or_post_early_recv).
vllm_ascend\worker\worker.py:642:            # early-recv cache via get_or_post_early_recv.  Stays False on the
vllm_ascend\worker\worker.py:666:            # cache at this size (see start_early_irecv): it posts ahead-of-time
vllm_ascend\worker\worker.py:818:    # The guard thread calls start_early_irecv() to post an irecv ahead of
vllm_ascend\worker\worker.py:820:    # get_or_post_early_recv() to consume/reuse it.  These are direction-
vllm_ascend\worker\worker.py:829:        ``_early_recv_lock``.  Does NOT cache in ``_early_recv_handles`` --
vllm_ascend\worker\worker.py:850:    def start_early_irecv(self, hint: dict) -> None:
vllm_ascend\worker\worker.py:855:        get_or_post_early_recv) is a no-op -- exactly one irecv is ever posted
vllm_ascend\worker\worker.py:867:
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:29:01</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "limit": 130,
  "offset": 100
}
```

</details>


---

## User <sup>2026/8/16 15:29:01</sup>

<details>
<summary>Tool Result</summary>

```
100	            )
101	            scheduler_output_handle = self.rpc_broadcast_mq.export_handle()
102	        elif envs.VLLM_PP_NON_LEADER_ENGINE_CORE:
103	            # For non-leader PP rank running with a passive EngineCore,
104	            # create a local rpc_broadcast_mq to broadcast SchedulerOutput
105	            # to local workers. Workers will use this MQ instead of
106	            # inner_dp_world_group to receive scheduler_output.
107	            max_chunk_bytes = envs.VLLM_MQ_MAX_CHUNK_BYTES_MB * 1024 * 1024
108	            self.rpc_broadcast_mq = MessageQueue(
109	                self.local_world_size,
110	                self.local_world_size,
111	                max_chunk_bytes=max_chunk_bytes,
112	                connect_ip=get_loopback_ip(),
113	            )
114	            scheduler_output_handle = self.rpc_broadcast_mq.export_handle()
115	
116	        # [CHER] Cloud-side hidden early-receive: build a sideband MQ that
117	        # PassiveEC writes recv-hints to and
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:29:11</sup>


---

## Assistant <sup>2026/8/16 15:29:12</sup>

<details>
<summary>Tool: <code>Grep</code></summary>

```json
{
  "-n": true,
  "head_limit": 25,
  "output_mode": "content",
  "path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend",
  "pattern": "_CLOUD_RECV_HINT_MQ_ENV|def _cher_guard|cher|CHER_GUARD|recv_hint_thread|hint_guard"
}
```

</details>


---

## User <sup>2026/8/16 15:29:12</sup>

<details>
<summary>Tool Result</summary>

```
vllm_ascend\core\run_phase_d_bench.sh:2:# Phase D benchmark/validation launcher for the NPU CI environment.
vllm_ascend\core\run_phase_d_bench.sh:19:# CI's actual launcher (MindIE-style / mpirun / custom harness).  The three
vllm_ascend\core\run_phase_d_bench.sh:81:# TODO(CI): replace the two placeholder commands with the platform launcher.  #
vllm_ascend\core\run_phase_d_bench.sh:134:  echo "[phase-d] $EDGE_LOG missing — did the launcher write logs?"
vllm_ascend\distributed\parallel_state.py:957:       - For MoE DP / external_launcher the world group spans all DP ranks, so
vllm_ascend\attention\dsa_v1.py:1532:        # dispatcher (only LinearMethodBase subclasses are). OTP buffers are
vllm_ascend\patch\__init__.py:758:#   1. `vllm.v1.cudagraph_dispatcher.CudagraphDispatcher._create_padded_batch_descriptor`
vllm_ascend\profiling_config.py:41:  handler: ms_service_profiler.patcher.vllm.handlers.v1.batch_handlers:schedule
vllm_ascend\profiling_config.py:46:  handler: ms_service_profiler.
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:29:16</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -rn \"_CLOUD_RECV_HINT_MQ_ENV\" vllm_ascend/ | head; grep -rn \"start_early_irecv\" vllm_ascend/ --include=\"*.py\" | grep -v \"def start_early_irecv\" | head",
  "description": "定位 CHER hint MQ 环境变量消费点与 guard 线程"
}
```

</details>


---

## User <sup>2026/8/16 15:29:17</sup>

<details>
<summary>Tool Result</summary>

```
vllm_ascend/patch/platform/patch_multiproc_executor.py:31:_CLOUD_RECV_HINT_MQ_ENV = "VLLM_ASCEND_CLOUD_RECV_HINT_MQ_HANDLE"
vllm_ascend/patch/platform/patch_multiproc_executor.py:144:            os.environ[_CLOUD_RECV_HINT_MQ_ENV] = base64.b64encode(
vllm_ascend/patch/platform/patch_multiproc_executor.py:153:            os.environ.pop(_CLOUD_RECV_HINT_MQ_ENV, None)
vllm_ascend/patch/platform/patch_multiproc_executor.py:444:    _raw = os.environ.get(_CLOUD_RECV_HINT_MQ_ENV)
vllm_ascend/patch/platform/patch_multiproc_executor.py:135:            # posting once the cache holds that many (see start_early_irecv),
vllm_ascend/worker/worker.py:666:            # cache at this size (see start_early_irecv): it posts ahead-of-time
vllm_ascend/worker/worker.py:818:    # The guard thread calls start_early_irecv() to post an irecv ahead of
vllm_ascend/worker/worker.py:867:                "[CHER] start_early_irecv: incomplete hint %s, skipping.",
vllm_ascend/worker/worker.py:876:                "[CHER
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:29:20</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "limit": 90,
  "offset": 420
}
```

</details>


---

## User <sup>2026/8/16 15:29:20</sup>

<details>
<summary>Tool Result</summary>

```
420	#    don't reach the plain WorkerProc instances worker_main creates;
421	#  - capturing _orig after `WorkerProc = AscendWorkerProc` would grab the
422	#    subclass's own _init_message_queues, causing infinite recursion when the
423	#    subclass calls super().
424	# AscendWorkerProc._init_message_queues is kept for the executor-side path
425	# (it also rebuilds); the wrapper early-returns if cloud_recv_hint_mq is
426	# already set, so there is no double-rebuild / clobber.
427	_OrigWorkerProc = AscendWorkerProc.__bases__[0]
428	_orig_init_message_queues = _OrigWorkerProc._init_message_queues
429	
430	
431	def _cher_init_message_queues(self, input_shm_handle, vllm_config):
432	    _orig_init_message_queues(self, input_shm_handle, vllm_config)
433	    # Only rebuild if not already done by AscendWorkerProc._init_message_queues.
434	    if getattr(self, "cloud_recv_hint_mq", None) is not None:
435	        return
436	    self.cloud_recv_hint_mq = None
437	    if not (
438	        envs.V
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:29:23</sup>


---

## Assistant <sup>2026/8/16 15:29:24</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -rn \"cloud_recv_hint_mq\" vllm_ascend/ --include=\"*.py\" | grep -v patch_multiproc | head; echo ---; grep -rn \"_recv_hint_guard\\|def _cher\\|cher_guard_loop\\|recv_hint\" vllm_ascend/worker/*.py vllm_ascend/patch/worker/*.py 2>/dev/null | head -20",
  "description": "定位 guard 线程消费 cloud_recv_hint_mq 的位置"
}
```

</details>


---

## User <sup>2026/8/16 15:29:26</sup>

<details>
<summary>Tool Result</summary>

```
vllm_ascend/patch/platform/__init__.py:60:# cloud_recv_hint_mq (CHER silently disabled, no [CHER] logs).  The patched
vllm_ascend/patch/worker/__init__.py:96:# plain WorkerProc whose _init_message_queues never rebuilt cloud_recv_hint_mq,
vllm_ascend/v1/engine/passive_core.py:520:            # recv-hint to the cloud worker's sideband cloud_recv_hint_mq so
vllm_ascend/v1/engine/passive_core.py:704:                _hint_mq = getattr(self.executor, "cloud_recv_hint_mq", None)
---
vllm_ascend/patch/worker/__init__.py:96:# plain WorkerProc whose _init_message_queues never rebuilt cloud_recv_hint_mq,
```

</details>


---

## Assistant <sup>2026/8/16 15:29:28</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\v1\\engine\\passive_core.py",
  "limit": 80,
  "offset": 480
}
```

</details>


---

## User <sup>2026/8/16 15:29:28</sup>

<details>
<summary>Tool Result</summary>

```
480	        dispatch_policy=None,
481	        pp_pd_channel: Optional["PPSchedulerZmqChannel"] = None,
482	    ) -> None:
483	        passive_scheduler_module = _import_passive_scheduler_module()
484	        if dispatch_policy is None:
485	            dispatch_policy = (
486	                passive_scheduler_module.DispatchPolicy.EXPECT_ALTERNATION
487	            )
488	        self.vllm_config = vllm_config
489	        self.executor = executor
490	        # scheduler_input is any object exposing consume_new_outputs(); in
491	        # PD-separation mode this is the cloud-side PPSchedulerZmqChannel.
492	        self.passive_scheduler = passive_scheduler_module.PassiveScheduler(
493	            vllm_config, scheduler_input, dispatch_policy=dispatch_policy
494	        )
495	        # Optional POST_OUT (cloud → edge) channel. Only set on the cloud
496	        # side in PD-separation mode; left None for the legacy PP path.
497	        self._pp_pd_channel = pp_pd_channel
498	        if geta
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:29:34</sup>


---

## Assistant <sup>2026/8/16 15:29:34</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -rn \"recv_hint\" vllm_ascend/ --include=\"*.py\" -l; echo ---; grep -rn \"Thread(\" vllm_ascend/worker/*.py vllm_ascend/patch/worker/*.py 2>/dev/null | head",
  "description": "查找 hint MQ 的 worker 侧消费线程"
}
```

</details>


---

## User <sup>2026/8/16 15:29:36</sup>

<details>
<summary>Tool Result</summary>

```
vllm_ascend/patch/platform/patch_multiproc_executor.py
vllm_ascend/patch/platform/__init__.py
vllm_ascend/patch/worker/__init__.py
vllm_ascend/v1/engine/passive_core.py
---
```

</details>


---

## Assistant <sup>2026/8/16 15:29:38</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -rn \"cloud_recv_hint_mq\\|start_early_irecv\" vllm_ascend/patch/worker/__init__.py | head; echo ===; grep -n \"hint\" vllm_ascend/patch/worker/__init__.py | head -20",
  "description": "查看 worker patch 中 hint 消费逻辑"
}
```

</details>


---

## User <sup>2026/8/16 15:29:40</sup>

<details>
<summary>Tool Result</summary>

```
96:# plain WorkerProc whose _init_message_queues never rebuilt cloud_recv_hint_mq,
===
96:# plain WorkerProc whose _init_message_queues never rebuilt cloud_recv_hint_mq,
97:# the guard thread never started, and every recv-hint was dropped (CHER silently
```

</details>


---

## Assistant <sup>2026/8/16 15:29:44</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -rn \"start_early_irecv\\|hint_mq\" vllm_ascend/v1/worker/*.py vllm_ascend/worker/worker_proc.py 2>/dev/null | head; ls vllm_ascend/worker/ | head -20; grep -rln \"start_early_irecv\" vllm_ascend/ ../vllm-pdmix/vllm/ 2>/dev/null",
  "description": "全局定位 start_early_irecv 调用方"
}
```

</details>


---

## User <sup>2026/8/16 15:29:45</sup>

<details>
<summary>Tool Result</summary>

```
__init__.py
__pycache__
block_table.py
edge_cloud
encoder_acl_graph.py
kvcomp_utils.py
model_runner_v1.py
npu_input_batch.py
pcp_utils.py
utils.py
v2
worker.py
vllm_ascend/patch/platform/patch_multiproc_executor.py
vllm_ascend/worker/worker.py
vllm_ascend/worker/__pycache__/worker.cpython-314.pyc
../vllm-pdmix/vllm/v1/executor/multiproc_executor.py
```

</details>


---

## Assistant <sup>2026/8/16 15:29:49</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"start_early_irecv\\|hint\" ../vllm-pdmix/vllm/v1/executor/multiproc_executor.py | head -20",
  "description": "查看 multiproc_executor 中的 hint 消费"
}
```

</details>


---

## User <sup>2026/8/16 15:29:50</sup>

<details>
<summary>Tool Result</summary>

```
780:        # masking.  When this cloud worker owns the sideband recv-hint MQ, start
783:        # thread (not busy_loop) owns cloud_recv_hint_mq: it drains recv-hints,
787:        if getattr(self, "cloud_recv_hint_mq", None) is not None:
1259:        masking: the PassiveEC fires recv-hints on the sideband
1260:        ``cloud_recv_hint_mq``, and this guard thread (not busy_loop) owns that
1263:        (start_early_irecv); it never wait()s -- waiting is left to
1273:        if worker is None or not hasattr(worker, "start_early_irecv"):
1286:        """Drain recv-hints and post early irecv (NO wait).
1288:        Drains ``cloud_recv_hint_mq`` (a sideband MQ the PassiveEC writes
1289:        fire-and-forget recv-hints to) and calls ``start_early_irecv`` so the
1292:        P-middle batch, so a hint queued on rpc_broadcast_mq would not be
1313:        hint_mq = getattr(self, "cloud_recv_hint_mq", None)
1317:            # [CHER] Post any new recv-hints that arrived on the sideband MQ.
1319
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:29:52</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\executor\\multiproc_executor.py",
  "limit": 130,
  "offset": 770
}
```

</details>


---

## User <sup>2026/8/16 15:29:52</sup>

<details>
<summary>Tool Result</summary>

```
770	            self.async_output_copy_thread.start()
771	
772	        # Set block size based on the attention backends
773	        current_platform.update_block_size_for_backend(vllm_config)
774	
775	        # Initialize message queues after init_device() since multi-node setups
776	        # (nnodes_within_dp > 1) require distributed groups to be initialized
777	        self._init_message_queues(input_shm_handle, vllm_config)
778	
779	        # [CHER] Cloud-side hidden early-receive: a built-in part of PD-separation
780	        # masking.  When this cloud worker owns the sideband recv-hint MQ, start
781	        # the early-irecv guard thread eagerly.  busy_loop is single-threaded and
782	        # blocks inside execute_model for a long P-middle batch, so the guard
783	        # thread (not busy_loop) owns cloud_recv_hint_mq: it drains recv-hints,
784	        # posts irecv, and waits it to completion while busy_loop is blocked on
785	        # the previous P-middle.  CHER does not gat
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:29:55</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\executor\\multiproc_executor.py",
  "limit": 120,
  "offset": 1245
}
```

</details>


---

## User <sup>2026/8/16 15:29:55</sup>

<details>
<summary>Tool Result</summary>

```
1245	                if output_rank is None or self.rank == output_rank:
1246	                    self.handle_output(e)
1247	                continue
1248	
1249	            if output_rank is None or self.rank == output_rank:
1250	                self.handle_output(output)
1251	
1252	    # ------------------------------------------------------------------ #
1253	    # [CHER] Cloud-side hidden early-receive guard thread.               #
1254	    # ------------------------------------------------------------------ #
1255	    def _start_early_recv_guard(self) -> None:
1256	        """Start the early-irecv guard thread (CHER, cloud-side only).
1257	
1258	        Cloud-side hidden early-receive is a built-in part of PD-separation
1259	        masking: the PassiveEC fires recv-hints on the sideband
1260	        ``cloud_recv_hint_mq``, and this guard thread (not busy_loop) owns that
1261	        MQ so irecv is posted even while busy_loop is blocked inside the
1262	        previous P-middle's e
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:30:25</sup>


---

## Assistant <sup>2026/8/16 15:30:26</sup>

已有 CHER guard 线程模式可镜像。关键前置问题:DDL 与 DDF 的 head_token 是否相同(决定 stash 键)。看 decode draft first pick 之后 DDL 怎么产生：


---

## Assistant <sup>2026/8/16 15:30:26</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 115,
  "offset": 2345
}
```

</details>


---

## User <sup>2026/8/16 15:30:26</sup>

<details>
<summary>Tool Result</summary>

```
2345	                batch_type=last_type,
2346	                num_accepted_tokens=None,
2347	                valid_sampled_token_count=None,
2348	            )
2349	            # is_last_prefill_chunk / draft_output_req_ids 是下游动态
2350	            # SchedulerOutput 属性，dataclasses.replace() 不保留，须回填。
2351	            draft_last.is_last_prefill_chunk = getattr(
2352	                scheduler_output, "is_last_prefill_chunk", True
2353	            )
2354	            draft_last.draft_output_req_ids = getattr(
2355	                scheduler_output,
2356	                "draft_output_req_ids",
2357	                tuple(scheduler_output.num_scheduled_tokens),
2358	            )
2359	            self._validate_decode_draft_tail_channel(draft_last)
2360	            self.decode_drafts_last_ready.append(draft_last)
2361	            self.decode_draft_remote_pending_count += 1
2362	            # [FORCE] DDF pick → decode_draft_last_pending（交替门控）
2363	            self._force.on_pick(BatchType.DECODE
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:30:31</sup>


---

## Assistant <sup>2026/8/16 15:30:31</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 45,
  "offset": 2306
}
```

</details>


---

## User <sup>2026/8/16 15:30:31</sup>

<details>
<summary>Tool Result</summary>

```
2306	            scheduler_output.head_token = uuid4().hex
2307	        if kind == "decode":
2308	            # decode_draft 域走独立 DRAFT 通道（不再与 DECODE 共享，这是
2309	            # 放宽 draft 串行门控的前提：共享通道时边云可能互相等对方
2310	            # 方向的 send 才 post 匹配 recv，会死锁）。
2311	            scheduler_output.hidden_channel = (
2312	                self.hidden_channel_manager.draft_channel()
2313	            )
2314	        elif scheduler_output.hidden_channel is None:
2315	            # Phase B（设计 §4.1）：prefill 域链在 enqueue 时已继承父 chunk
2316	            # 的 Prefill 通道；缺失说明链创建路径漏了继承。
2317	            raise RuntimeError(
2318	                f"{first_type.value} missing inherited prefill "
2319	                f"hidden_channel (task_id={scheduler_output.draft_task_id})"
2320	            )
2321	        self._register_pd_flight(scheduler_output)
2322	        if kind == "prefill":
2323	            # Phase C（设计 §6.2/§7.5）：PDFL 由云侧在 PDFF 完成后经
2324	            # POST_OUT 发布——云侧往返即 pacing，边侧不再自贴尾、不再
2325	            
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:30:43</sup>


---

## Assistant <sup>2026/8/16 15:30:44</sup>

确认了关键事实:DDL 由边侧自贴(`replace(DDF)` 保留 head_token),且尾路径已用 `get_or_post_early_recv` 消费缓存——缺的只是“谁提前挂 + 谁报就绪”。看尾路径的现状细节：


---

## Assistant <sup>2026/8/16 15:30:45</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "limit": 100,
  "offset": 1195
}
```

</details>


---

## User <sup>2026/8/16 15:30:45</sup>

<details>
<summary>Tool Result</summary>

```
1195	            include_mrope=False,
1196	        )
1197	
1198	        intermediate_tensors = AsyncIntermediateTensors(
1199	            tensor_dict,
1200	            comm_handles=comm_handles,
1201	            comm_postprocess=comm_postprocess,
1202	        )
1203	        output = self.model_runner.execute_model(
1204	            scheduler_output, intermediate_tensors,
1205	            layer_slice_info=layer_slice_info,
1206	        )
1207	
1208	        is_last_slice = (
1209	            layer_slice_info is None or layer_slice_info.is_last_slice
1210	        )
1211	        if not is_last_slice:
1212	            return None
1213	
1214	        if isinstance(output, (ModelRunnerOutput, AsyncModelRunnerOutput, NoneType)):
1215	            return output
1216	        return output
1217	
1218	    def _execute_model_cloud(
1219	        self,
1220	        scheduler_output: "SchedulerOutput",
1221	        layer_slice_info: Any,
1222	    ) -> ModelRunnerOutput | AsyncModelRunnerOutput | None:
1
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:30:47</sup>


---

## Assistant <sup>2026/8/16 15:30:48</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"_execute_model_edge_draft_tail\\|_execute_model_edge_head\\|_execute_model_edge_tail\" vllm_ascend/worker/worker.py | head",
  "description": "定位 edge draft tail 执行函数"
}
```

</details>


---

## User <sup>2026/8/16 15:30:49</sup>

<details>
<summary>Tool Result</summary>

```
1040:                return self._execute_model_edge_draft_tail(scheduler_output)
1042:                return self._execute_model_edge_head(
1046:                return self._execute_model_edge_tail(
1086:    def _execute_model_edge_head(
1176:    def _execute_model_edge_tail(
1544:    def _execute_model_edge_draft_tail(
```

</details>


---

## Assistant <sup>2026/8/16 15:30:52</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "limit": 115,
  "offset": 1544
}
```

</details>


---

## User <sup>2026/8/16 15:30:52</sup>

<details>
<summary>Tool Result</summary>

```
1544	    def _execute_model_edge_draft_tail(
1545	        self, scheduler_output: "SchedulerOutput"
1546	    ) -> ModelRunnerOutput:
1547	        """Receive and finish one edge-side scheduled draft step."""
1548	        logger.info(f"Execute model, batch_type: {scheduler_output.batch_type}")
1549	        recv_tensor_meta = self._scheduled_draft_tensor_meta(
1550	            scheduler_output,
1551	            "c2e",
1552	        )
1553	        channel = self._hidden_channel_for(scheduler_output)
1554	        tensor_dict, comm_handles, comm_postprocess = (
1555	            edge_cloud_broadcast_recv_scheduled_draft(
1556	                tensor_meta=recv_tensor_meta,
1557	                channel=channel,
1558	            )
1559	        )
1560	        for handle in comm_handles:
1561	            handle.wait()
1562	        for postprocess in comm_postprocess:
1563	            postprocess()
1564	        logger.info(
1565	            "Receive intermediate tensors from cloud after, "
1566	     
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:31:17</sup>


---

## Assistant <sup>2026/8/16 15:31:18</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"def edge_cloud_broadcast_recv_scheduled_draft\" vllm_ascend/distributed/parallel_state.py",
  "description": "定位 scheduled_draft recv 函数"
}
```

</details>


---

## User <sup>2026/8/16 15:31:18</sup>

<details>
<summary>Tool Result</summary>

```
2105:def edge_cloud_broadcast_recv_scheduled_draft(
```

</details>


---

## Assistant <sup>2026/8/16 15:31:21</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "limit": 120,
  "offset": 2105
}
```

</details>


---

## User <sup>2026/8/16 15:31:21</sup>

<details>
<summary>Tool Result</summary>

```
2105	def edge_cloud_broadcast_recv_scheduled_draft(
2106	    channel: HiddenChannelType = HiddenChannelType.DECODE,
2107	    tensor_meta: ScheduledDraftTensorMeta | None = None,
2108	) -> tuple[
2109	    dict[str, torch.Tensor | Any] | None,
2110	    list[Handle],
2111	    list[Callable[[], None]],
2112	]:
2113	    """Receive and TP-broadcast a scheduled draft payload.
2114	
2115	    A locally-derived ``tensor_meta`` skips both the cross-node Gloo metadata
2116	    exchange and the local TP object broadcast. ``None`` retains the dynamic
2117	    compatibility path.
2118	    """
2119	    pp_group = get_pp_group()
2120	    tp_group = get_tp_group()
2121	    is_pp_npu0 = pp_group.world_size == 2
2122	
2123	    if tensor_meta is not None:
2124	        recv_tensor_dict: dict[str, torch.Tensor | Any] = {}
2125	        comm_handles: list[Handle] = []
2126	        if is_pp_npu0:
2127	            src = (pp_group.rank_in_group - 1) % pp_group.world_size
2128	            group = _get_edge_cloud_h
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:31:39</sup>


---

## Assistant <sup>2026/8/16 15:31:40</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "limit": 95,
  "offset": 1086
}
```

</details>


---

## User <sup>2026/8/16 15:31:40</sup>

<details>
<summary>Tool Result</summary>

```
1086	    def _execute_model_edge_head(
1087	        self,
1088	        scheduler_output: "SchedulerOutput",
1089	        layer_slice_info: Any,
1090	    ) -> ModelRunnerOutput | AsyncModelRunnerOutput | None:
1091	        """Edge head segment (PF/DF): segment_a -> isend -> suspend -> return EMPTY."""
1092	        output = self.model_runner.execute_model(
1093	            scheduler_output, intermediate_tensors=None,
1094	            layer_slice_info=layer_slice_info,
1095	        )
1096	        is_last_slice = (
1097	            layer_slice_info is None or layer_slice_info.is_last_slice
1098	        )
1099	        if not is_last_slice:
1100	            return None
1101	
1102	        if isinstance(output, (ModelRunnerOutput, AsyncModelRunnerOutput, NoneType)):
1103	            return output
1104	
1105	        assert isinstance(output, IntermediateTensors)
1106	        # Edge-cloud with heterogeneous SP: aggregate SP shards to full
1107	        # sequence before cross-PP send so cloud can
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:31:51</sup>


---

## Assistant <sup>2026/8/16 15:31:52</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -rn \"def _run_edge_cloud_draft_last_segment\" vllm_ascend/ --include=\"*.py\"",
  "description": "定位 _run_edge_cloud_draft_last_segment"
}
```

</details>


---

## User <sup>2026/8/16 15:31:53</sup>

<details>
<summary>Tool Result</summary>

```
vllm_ascend/worker/model_runner_v1.py:4440:    def _run_edge_cloud_draft_last_segment(
```

</details>


---

## Assistant <sup>2026/8/16 15:31:55</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\model_runner_v1.py",
  "limit": 60,
  "offset": 4440
}
```

</details>


---

## User <sup>2026/8/16 15:31:56</sup>

<details>
<summary>Tool Result</summary>

```
4440	    def _run_edge_cloud_draft_last_segment(
4441	        self,
4442	        scheduler_output: "SchedulerOutput",
4443	        intermediate_tensors: IntermediateTensors,
4444	    ) -> ModelRunnerOutput:
4445	        task_id = scheduler_output.draft_task_id
4446	        context = (
4447	            self._pending_edge_cloud_draft_contexts.get(task_id)
4448	            if task_id else None
4449	        )
4450	        if context is None:
4451	            # Drain: the owning request finished/aborted after its
4452	            # draft FIRST was already dispatched to the cloud.  The cloud
4453	            # does not track request lifecycle, so it still ran the draft
4454	            # middle segment and isend the draft LAST response; the recv in
4455	            # _execute_model_edge_draft_tail already consumed it to keep the
4456	            # DECODE hidden channel paired.  With no draft context there is
4457	            # no tail-segment compute to run (the result would be discarded
445
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:32:01</sup>


---

## Assistant <sup>2026/8/16 15:32:01</sup>

路径确认可行。开始实现。Edit 1:scheduled_draft recv 的快速路径补记 event:


---

## Assistant <sup>2026/8/16 15:32:03</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\distributed\\parallel_state.py",
  "old_string": "            else:\n                tensor = torch.empty(\n                    value.size,\n                    dtype=value.dtype,\n                    device=value.device,\n                )\n            recv_tensor_dict[key] = tensor\n\n        def broadcast_postprocess():",
  "new_string": "            else:\n                tensor = torch.empty(\n                    value.size,\n                    dtype=value.dtype,\n                    device=value.device,\n                )\n            recv_tensor_dict[key] = tensor\n\n        # [EHER] Record one NPU event on the channel stream covering every\n        # draft irecv issued above.  ``event.query()`` gives the edge worker\n        # a non-blocking readiness probe so the scheduler can gate the draft\n        # LAST dispatch on data-plane readiness instead of a fixed delay.\n        if comm_handles:\n            with _hidden_channel_stream_ctx(\n                channel, wait_for_default=False\n            ):\n                comm_event = torch.npu.Event()\n                comm_event.record()\n            recv_tensor_dict[\"__comm_event__\"] = comm_event\n\n        def broadcast_postprocess():"
}
```

</details>


---

## User <sup>2026/8/16 15:32:04</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:33:06</sup>

---

**⟫ Conversation compacted (auto) — 168,404 tokens before compact**

---


---

## User <sup>2026/8/16 15:33:06</sup>

<details>
<summary><b>Compact Summary (auto-generated context from previous conversation)</b></summary>

This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.

Summary:
1. Primary Request and Intent:
   The user is working on vllm-ascend edge-cloud (边云) collaborative inference MTP performance optimization in c:\kisella_mtp (two repos: vllm-pdmix = upstream vllm fork, vllm-ascend-pdmix = ascend fork). The conversation progressed through these explicit requests (all in Chinese):
   
   a. (from prior session, delivered at start) Analyze the design doc section “边侧尾recv和计算分开，增加worker层调度方案”.
   
   b. “不考虑多实例和多dp,当前mtp没有单独的数据通道，首先为mtp创建单独的数据通道，然后增加边侧尾 recv 和计算分开，增加 worker 层调度，enginecore的scheduler调度针对此场景优化可以下发其他任务，mtp场景的收益有多大” — quantify benefit of 3 modifications.
   
   c. “目标是先到盈亏平衡线，按上述设计方案梳理代码修改方案” — produce a code modification plan targeting break-even.
   
   d. “不考虑sharemodel,就先按边侧两卡(tp=2)来考虑” — revise plan for edge TP=2 non-shared-model topology.
   
   e. “阅读一下C:\theroadtofree_github\vllm-ascend\docs\PDbatch分离边云协同多实例调度详细设计_NEW.md中recv和计算分离，采用的方案是worker增加监控线程，上报scheduler; 与当前方案比哪个更好，哪个更容易实现” — compare NEW doc's monitor-thread scheme vs current plan.
   
   f. (MOST RECENT, ACTIVE) “按方案实现逐步修改代码” — implement the modifications step by step. Implementation follows the agreed hybrid plan: P0 = MTP dedicated DRAFT channel; P1 = early irecv + NPU event + readiness poll + sideband ack to scheduler (scheduler-gated DDL dispatch); P2 = scheduler gate relaxation (<limit), inflight early release, pacing bypass, watchdog.

2. Key Technical Concepts:
   - BatchType 8 edge-cloud types; DECODE_DRAFT_FIRST/LAST = “mtp decode_first/last”; decode-domain DDL is edge-self-posted (自贴尾) via `replace(DDF_SO)` preserving head_token — no cloud POST_OUT needed
   - HiddenChannelType: pool-based channel enum (PREFILL_i/DECODE_i pools generated in init()); channels flow via SchedulerOutput.hidden_channel; cloud side derives recv channel from hint
   - ==0 serialization gate at pd_separated_scheduler L1604-1609 exists BECAUSE draft shared DECODE channel (deadlock risk: “edge and cloud can each wait for the opposite-direction send before posting the matching recv”); pregenerated branch already has target semantics (`< limit=2`)
   - CHER (Cloud-side Hidden Early Receive): cloud_recv_hint_mq sideband MQ created on cloud executor, PassiveEC fires hints, guard thread on cloud worker local_rank==0 drains and calls start_early_irecv; CRITICAL constraint: guard thread NEVER wait()s — “HCCL does not tolerate a cross-thread wait() on a hidden-channel irecv while busy_loop issues isend on that same channel (deadlock)”; CHER does not gate scheduling (no ack)
   - EHER primitives (direction-agnostic, currently unused for cloud->edge): worker.start_early_irecv(hint dict), get_or_post_early_recv(head_token, channel, num_tokens) — atomic one-irecv-per-head_token guarantee, _early_recv_handles cache capped at _early_recv_max_inflight=2
   - TP=2 structure: TP0 (PP-NPU0, pp_group.world_size==2) does irecv; TP1 (singleton PP group) allocates buffers and blocks in broadcast_postprocess TP broadcast rendezvous — so only scheduler-driven dispatch (MQ broadcast lands both ranks together) can collapse both cards' blocking; TP1 needs zero changes
   - NPU event readiness: event.record() in _hidden_channel_stream_ctx covers irecv transfer only; TP broadcast postprocess NOT covered (§5.2.6); fence semantics correction: handle.wait() doesn't block CPU (device fence only); real CPU blocks are sampler D2H (.item()) and EngineCore future.result()
   - NEW doc §5.2 scheme: TaskKind (COMPUTE/COMM_RECV) + WorkerTask + depends_on; per-(instance,dp) completion thread (event.synchronize/query) writes recv_done_mq (dedicated sideband, NOT response_mq to avoid batch_queue future conflicts); EngineCore drains and gates COMPUTE(tail) dispatch; DL 30ms timer replaced by recv fence
   - Break-even math: cloud executes m+1 middle passes per accepted batch; A ≤ m+1 always; when cloud is bottleneck MTP throughput ceiling = A/(m+1) ≤ 1 — the 3 changes fix pipeline collapse (3-5× degradation → break-even) but net win requires draft localization (0 RTT draft steps)
   - MTP degradation model: single-request draft chain data-serial (token dependency), only pregenerated drafts or concurrent requests can fill RTT windows

3. Files and Code Sections:
   - c:\kisella_mtp\vllm-pdmix\vllm\v1\core\sched\output.py (EDITED, P0-1)
      - HiddenChannelType: added `_MIN_DRAFT_POOL: int = 4`; init() gained `draft_per_dp: int = 1` param, `need_draft`, pool doubling loop, and:
        ```python
        for i in range(1, draft_pool + 1):
            setattr(cls, f"DRAFT_{i}", cls(f"draft_{i}"))
        setattr(cls, "DRAFT", getattr(cls, "DRAFT_1"))
        ```
        plus `draft(i)` static method mirroring `decode(i)`.
   
   - c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\worker\patch_distributed.py (EDITED, P0-2)
      - Added `self._draft_device_groups` / `self._draft_cpu_groups` lists in __init__ (with comment "idx 0 -> DRAFT_1 (pg_options=\"pp_draft1\")"); destroy() cleans them; create_hidden_channel_groups gained `num_draft: int = 0` param + DRAFT creation loop:
        ```python
        for i in range(len(self._draft_device_groups) + 1, num_draft + 1):
            self._create_one_hidden_channel(
                f"pp_draft{i}", torch_distributed_backend,
                self._draft_device_groups, self._draft_cpu_groups,
            )
        ```
      - `_hidden_channel_groups`: added `if value.startswith("draft_"): idx = int(value.split("_")[1]) - 1; return self._draft_device_groups[idx], self._draft_cpu_groups[idx]`
   
   - c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\distributed\parallel_state.py (EDITED, P0-3 + P1-1)
      - Call site (~L580): `num_draft = dp_size` (shared) / `1` (non-shared); logging includes num_draft; `pp_group.create_hidden_channel_groups(backend, num_prefill, num_decode, num_draft)`
      - warmup_edge_cloud_hidden_channels: `draft_groups = getattr(pp_group, "_draft_device_groups", None)`; shared branch appends `(HiddenChannelType.draft(dp_rank + 1), dp_rank + 1)` per dp; non-shared appends draft channels with peer 1
      - P1-1 in edge_cloud_irecv_tensor_dict (before final return):
        ```python
        if handles:
            with _hidden_channel_stream_ctx(
                channel, wait_for_default=False
            ):
                comm_event = torch.npu.Event()
                comm_event.record()
            tensor_dict["__comm_event__"] = comm_event
        ```
      - KEY UNREAD-BUT-NEEDED: `edge_cloud_broadcast_recv_scheduled_draft` (L2105-2207) — fast path (tensor_meta present): per-key irecv on channel stream (TP0 only, is_pp_npu0), returns (recv_tensor_dict, comm_handles, [broadcast_postprocess]); NO event recording yet (P1-3 must add it there)
   
   - c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py (EDITED, P0-4)
      - HiddenChannelManager.__init__ (~L115): added `self._draft_channel = HiddenChannelType.draft(dp_rank + 1)`; new `draft_channel()` accessor
      - `_validate_decode_draft_tail_channel`: now checks `scheduler_output.hidden_channel != self.hidden_channel_manager.draft_channel()`
      - `_pick_draft_first_batch_by_kind` decode branch (~L2307): `scheduler_output.hidden_channel = self.hidden_channel_manager.draft_channel()`
      - L~2450 (placeholder chain) and L~2590 (enqueue_draft_first): `inherited_channel = self.hidden_channel_manager.draft_channel()` for decode kind
      - Key locations for P1-5/P2: `_can_schedule_decode_draft_first` L1580-1609 (==0 gate at L1604-1609); `_pick_draft_first_batch_by_kind` decode branch L2339-2365 (DDL replace + self-post + `_start_decode_draft_last_delay()`); L3380-3390 DECODE_FIRST inflight release (needs DECODE_DRAFT_FIRST branch); `_decode_draft_last_delay_schedule_ms` (yaml 5ms/code 15ms)
   
   - c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\worker\worker.py (EDITED P0-4; P1-3 edits pending)
      - `_hidden_channel_for`: DECODE_DRAFT_FIRST/LAST → `return HiddenChannelType.DRAFT`
      - Read & critical for P1-3: `_execute_model_edge_head` (L1086-1174) — send block `if get_pp_group().world_size == 2:` (only TP0) ends with `self._record_pp_send_work(edge_cloud_send_tensor_dict(...), channel=channel)` at L1160-1166; early-post hook goes right after inside that block, gated on batch_type == DECODE_DRAFT_FIRST
      - `_execute_model_edge_draft_tail` (L1544-1571) — current synchronous blocking path:
        ```python
        recv_tensor_meta = self._scheduled_draft_tensor_meta(scheduler_output, "c2e")
        channel = self._hidden_channel_for(scheduler_output)
        tensor_dict, comm_handles, comm_postprocess = (
            edge_cloud_broadcast_recv_scheduled_draft(
                tensor_meta=recv_tensor_meta, channel=channel))
        for handle in comm_handles: handle.wait()
        for postprocess in comm_postprocess: postprocess()
        return self.model_runner._run_edge_cloud_draft_last_segment(
            scheduler_output, IntermediateTensors(tensor_dict))
        ```
      - CHER primitives at L824-952: `_post_early_irecv_locked`, `start_early_irecv(hint)`, `get_or_post_early_recv`; cloud consume at L1276-1286 (PREFILL_FIRST only, DECODE excluded due to single-channel stream race)
      - `_scheduled_draft_tensor_meta` L1366-1403: returns None when enable_sp() (compat path — no early post possible under SP)
   
   - c:\kisella_mtp\vllm-pdmix\vllm\v1\worker\gpu_worker.py (EDITED, P1-2)
      - AsyncIntermediateTensors: added `comm_event: Any = None` param, `self._comm_event`, and:
        ```python
        def is_ready(self) -> bool:
            event = self._comm_event
            if event is None:
                return False
            return bool(event.query())
        ```
        wait_for_comm unchanged. `Any` already imported (L11).
   
   - c:\kisella_mtp\vllm-pdmix\vllm\v1\executor\multiproc_executor.py (READ; P1-4 pending)
      - busy_loop ~L403+ with dequeue(timeout=0.001); EDGE-DEQUEUE log ~L1204
      - CHER guard thread: `_start_early_recv_guard` (L1255) started when cloud_recv_hint_mq present (L787-788); `_early_recv_guard_loop` (L1285) drains hints, calls start_early_irecv, NEVER waits, sleeps 0.0001 when idle
   
   - c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py (READ; P1 edit pending)
      - `_CLOUD_RECV_HINT_MQ_ENV = "VLLM_ASCEND_CLOUD_RECV_HINT_MQ_HANDLE"`; cloud_recv_hint_mq created on cloud executor (L126-153) `MessageQueue(1, 1, max_chunk_bytes=1024, max_chunks=8)`, handle via base64 env var; worker rebuild in `_cher_init_message_queues` (L431-465) gated on VLLM_PP_NON_LEADER_ENGINE_CORE + local_rank==0 + not edge_node
   
   - c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\worker\model_runner_v1.py (READ)
      - `_run_edge_cloud_draft_last_segment` (L4440): accepts IntermediateTensors, accesses `.tensors` lazily at L4474 (`intermediate_tensors.tensors.get("positions")`) — AsyncIntermediateTensors subclass works via lazy wait_for_comm on .tensors access
   
   - c:\kisella_mtp\vllm-ascend-pdmix\tests\ut\test_pd_draft_drain.py (EDITED via sed)
      - L89/L105: `so.hidden_channel = HiddenChannelType.DRAFT` (was DECODE)
   
   - C:\theroadtofree_github\vllm-ascend\docs\PDbatch分离边云协同多实例调度详细设计_NEW.md (READ)
      - §5.2 调度层计算/通信分离： TaskKind/WorkerTask/depends_on, execute_comm_recv RPC, recv_done_mq sideband (“不复用 response_mq”), per-(instance,dp) completion thread, “worker 不 poll-and-run tail”;§5.2.1 fence semantics correction (handle.wait doesn't block CPU; real serial points = round barrier / sampler D2H / future.result collect); §5.3.4 overlap depth = batch_queue_size − 1; §5.6 DL 30ms → recv fence, strict alternation DF isend → DL irecv must be preserved on single channel

4. Errors and fixes:
   - Garbage code in worker.py edit: wrote `if bt in (BatchType.DREF_FIRST_ALIAS if False else (BatchType.DECODE_DRAFT_FIRST, ...))` — immediately fixed with a clean Edit to plain tuple membership.
   - Edit string mismatch in parallel_state.py warmup (trailing-comma formatting differences vs my constructed old_string) — fixed by re-reading the exact region and applying smaller precise edits.
   - Wrong attribute scope in scheduler validation: used `self.draft_channel` but the field lives on HiddenChannelManager, not PDSeparatedScheduler — fixed to `self.hidden_channel_manager.draft_channel()`.
   - pytest unavailable (system Python 3.14, no pytest; no conda/venv found) — fell back to `python -m py_compile` on all edited files: SYNTAX_OK (only pre-existing SyntaxWarning at worker.py:300 'return' in 'finally'). Real testing must happen on NPU machines.
   - Conceptual correction (communicated to user): earlier claim "TP0 blocks in handle.wait()" was imprecise per NEW doc §5.2.1 — handle.wait() is a device fence; the real CPU blocks are sampler D2H and future.result collect; engineering effect (worker stuck inside LAST 5-13ms) unchanged.

5. Problem Solving:
   - Delivered break-even quantification: 3 changes fix pipeline collapse; single-request gain ~1.2-1.5×; concurrent/pregenerated 2-4× throughput; net win vs non-MTP requires draft localization (A ≤ m+1 ceiling when cloud is bottleneck).
   - Produced and twice-revised (shared-model → TP=2) the 3-knife code modification plan, all code anchors verified in-repo.
   - Compared NEW doc monitor-thread scheme vs lightweight plan: same family (scheduler-gated tail dispatch on data-plane readiness); recommended hybrid — busy-loop poll first, sideband MQ discipline adopted from doc, monitor thread as profile-driven upgrade.
   - Implementation discovery that dramatically reduces P1 scope: CHER/EHER early-recv cache (head_token-keyed, idempotent) already exists; only missing pieces are (a) an early-post trigger for the DDL return irecv at DDF execution on TP0, (b) readiness poll + sideband ack to scheduler, (c) scheduler ack gate.
   - Confirmed DDL head_token == DDF head_token (replace preserves it; validation requires it present).

6. All user messages:
   - “不考虑多实例和多dp,当前mtp没有单独的数据通道，首先为mtp创建单独的数据通道，然后增加边侧尾 recv 和计算分开，增加 worker 层调度，enginecore的scheduler调度针对此场景优化可以下发其他任务，mtp场景的收益有多大”
   - “目标是先到盈亏平衡线，按上述设计方案梳理代码修改方案”
   - “不考虑sharemodel,就先按边侧两卡(tp=2)来考虑”
   - “阅读一下C:\theroadtofree_github\vllm-ascend\docs\PDbatch分离边云协同多实例调度详细设计_NEW.md中recv和计算分离，采用的方案是worker增加监控线程，上报scheduler; 与当前方案比哪个更好，哪个更容易实现”
   - “按方案实现逐步修改代码”
   (No security-relevant instructions or constraints were stated by the user in any message.)

7. Pending Tasks (todo list state):
   - P0-1..P0-4: COMPLETED (DRAFT channel end-to-end)
   - P1-1 COMPLETED (irecv NPU event in edge_cloud_irecv_tensor_dict)
   - P1-2 COMPLETED (AsyncIntermediateTensors.is_ready())
   - P1-3 IN PROGRESS: worker.py FIRST path early return-irecv + head_token stash
   - P1-4 PENDING: multiproc_executor busy loop poll phase + sideband readiness report
   - P1-5 PENDING: scheduler DDL pick gate = recv ready ack
   - P2-1 PENDING: draft gate ==0 → <limit + inflight early release (DECODE_DRAFT_FIRST branch at L3380-3390)
   - P2-2 PENDING: pacing delay bypass + watchdog
   - After all: py_compile verification of each edited file; report to user that runtime testing requires NPU machines

8. Current Work:
   Implementing P1-3 under the active task “按方案实现逐步修改代码”. Just finished the final exploration read: `_run_edge_cloud_draft_last_segment` (model_runner_v1.py:4440) confirming lazy `.tensors` access (L4474), so AsyncIntermediateTensors can replace IntermediateTensors in the draft tail call. The formulated P1-3/P1-4/P1-5 edit plan (not yet written):
   
   (1) parallel_state.py `edge_cloud_broadcast_recv_scheduled_draft` fast path: add NPU event recording after the per-key irecv loop (same `__comm_event__` private-key pattern as P1-1).
   
   (2) worker.py `__init__` (~L239 area): add `self._draft_recv_cache: dict[str, AsyncIntermediateTensors] = {}` (+ simple lock + `_draft_recv_reported` set for ack dedup).
   
   (3) worker.py new helpers on Worker: `_post_draft_return_irecv(scheduler_output)` — gated on `get_pp_group().is_first_rank` (TP0) + batch_type DECODE_DRAFT_FIRST + `_scheduled_draft_tensor_meta(...) is not None` (SP off), calls edge_cloud_broadcast_recv_scheduled_draft with c2e meta + DRAFT channel, pops `__comm_event__`, caches AsyncIntermediateTensors by head_token; `_consume_draft_recv(scheduler_output)` — cache lookup/pop.
   
   (4) worker.py `_execute_model_edge_head`: inside the `if get_pp_group().world_size == 2:` send block (after `_record_pp_send_work`, ~L1166), call the early-post hook for DECODE_DRAFT_FIRST — runs only on TP0 since TP1 has singleton PP group.
   
   (5) worker.py `_execute_model_edge_draft_tail`: first try `_consume_draft_recv`; on hit pass the AsyncIntermediateTensors to `_run_edge_cloud_draft_last_segment` (lazy wait); on miss (TP1 / SP compat) keep current synchronous fallback.
   
   (6) patch_multiproc_executor.py: create `edge_recv_ready_mq` on EDGE executor mirroring cloud_recv_hint_mq pattern (env var handle e.g. `VLLM_ASCEND_EDGE_RECV_READY_MQ_HANDLE`, rebuilt on edge worker local_rank==0); multiproc_executor.py busy_loop poll phase: check `_draft_recv_cache` entries' `is_ready()` → enqueue ack head_tokens; patch_engine_core.py drain acks → scheduler notify; pd_separated_scheduler.py: `_draft_recv_ready_acks` set + notify method + config-gated DDL pick gate (flag in PDSeparationConfig, e.g. `decode_draft_recv_ack_enable`, default False for safe rollout).

9. Optional Next Step:
   Continue P1-3 implementation exactly per the formulated edit plan above, starting with the parallel_state.py event recording in `edge_cloud_broadcast_recv_scheduled_draft`, then the worker.py cache/helpers/head-hook/tail-consume edits, each followed by py_compile verification. This directly continues the user's instruction “按方案实现逐步修改代码” and the in-progress todo "P1-3 worker.py FIRST 路径: 提前挂 return-irecv + head_token stash". Verbatim context of where I left off: my last message stated “现在依次修改。HiddenChannelManager 加 draft 通道” phase is done; the current todo marked in_progress is “P1-3 worker.py FIRST 路径: 提前挂 return-irecv + head_token stash”， and my final action was reading `_run_edge_cloud_draft_last_segment` to confirm "Passing AsyncIntermediateTensors should work via the lazy attr" before writing the worker.py edits.

If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: C:\Users\root\.claude\projects\c--kisella-mtp\0fd965c5-f091-41ab-b346-446569638fa9.jsonl
Continue the conversation from where it left off without asking the user any further questions. Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar. Pick up the last task as if the break never happened.

</details>


---

## Assistant <sup>2026/8/16 15:33:16</sup>


---

## Assistant <sup>2026/8/16 15:33:17</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "python - <<'EOF'\nimport re\nsrc = open('vllm_ascend/distributed/parallel_state.py', encoding='utf-8').read()\ni = src.index('def edge_cloud_broadcast_recv_scheduled_draft')\nseg = src[i:i+9000]\nj = seg.index('__comm_event__')\nprint(seg[j-2500:j+700])\nEOF",
  "description": "Verify event edit landed in scheduled_draft fast path"
}
```

</details>


---

## User <sup>2026/8/16 15:33:47</sup>

<details>
<summary>Tool Result</summary>

```
ny] = {}
        comm_handles: list[Handle] = []
        if is_pp_npu0:
            src = (pp_group.rank_in_group - 1) % pp_group.world_size
            group = _get_edge_cloud_hidden_channel_device_group(
                pp_group,
                channel=channel,
            )

        send_keys = set(tensor_meta.send_tensor_keys)
        for key, value in tensor_meta.metadata_list:
            if not isinstance(value, TensorMetadata):
                recv_tensor_dict[key] = value
                continue

            if is_pp_npu0 and key in send_keys:
                with _hidden_channel_stream_ctx(
                    channel, wait_for_default=False
                ):
                    # Scheduled-draft buffers follow the same allocation-
                    # stream rule as the generic receive path.
                    tensor = torch.empty(
                        value.size,
                        dtype=value.dtype,
                        device=value.
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:33:51</sup>


---

## Assistant <sup>2026/8/16 15:33:51</sup>

Edit 1 落点正确。接下来 worker.py — 先看导入与 `__init__` 区域：


---

## Assistant <sup>2026/8/16 15:33:52</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"AsyncIntermediateTensors\\|from vllm.worker.gpu_worker import\\|^import\\|^from\" vllm_ascend/worker/worker.py | head -40; echo ---; grep -n \"_early_recv_handles\\|_early_recv_lock\\|_early_recv_max_inflight\" vllm_ascend/worker/worker.py | head",
  "description": "Check imports and early-recv fields in worker.py"
}
```

</details>


---

## User <sup>2026/8/16 15:33:53</sup>

<details>
<summary>Tool Result</summary>

```
20:from enum import Enum
21:from typing import Any
22:import copy
23:import gc
24:import logging
25:import threading
26:import time
27:from datetime import timedelta
28:from types import NoneType
30:import torch
31:import torch.nn as nn
32:import torch_npu
33:from torch_npu.op_plugin.atb._atb_ops import _register_atb_extensions
34:from torch_npu.profiler import dynamic_profile as dp
35:from vllm.config import CUDAGraphMode, VllmConfig, set_current_vllm_config
36:from vllm.distributed import ensure_model_parallel_initialized, get_pcp_group, init_distributed_environment
37:from vllm.distributed.ec_transfer import ensure_ec_transfer_initialized
38:from vllm.distributed.kv_transfer import (
44:from vllm.distributed.kv_transfer.kv_connector.v1.base import KVConnectorHandshakeMetadata
45:from vllm.distributed.parallel_state import (
52:from vllm.logger import logger
53:from vllm.lora.request import LoRARequest
54:from vllm.platforms import current_platform
55:from vllm.sequence import Interm
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:33:56</sup>


---

## Assistant <sup>2026/8/16 15:33:56</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "limit": 30,
  "offset": 225
}
```

</details>


---

## User <sup>2026/8/16 15:33:56</sup>

<details>
<summary>Tool Result</summary>

```
225	        if self.use_v2_model_runner and vllm_version_is("0.23.0"):
226	            logger.warning("VLLM_USE_V2_MODEL_RUNNER is not supported on vllm 0.23.0; falling back to v1 model runner.")
227	            self.use_v2_model_runner = False
228	        self._pp_send_work: list[Handle] = []
229	        self._pp_send_work_by_channel: dict[str, list[Handle]] = {}
230	
231	        # [CHER/EHER] Cloud-side hidden early-receive (and its edge-side
232	        # mirror) cache.  The guard thread posts irecv ahead of the batch's
233	        # execute_model (keyed by head_token); execute_model pops the cached
234	        # AsyncIntermediateTensors and runs wait_for_comm() (which both
235	        # waits the HCCL handles and runs comm_postprocess, the latter being
236	        # a TP collective that must run inside execute_model on all ranks).
237	        # Shared by CHER (cloud) and EHER (edge) since the recv primitives
238	        # are direction-agnostic (driven by hidden_channel + num_token
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:34:00</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "old_string": "        self._cloud_hidden_early_recv_enabled: bool = False",
  "new_string": "        self._cloud_hidden_early_recv_enabled: bool = False\n\n        # [EHER-draft] Edge-side early irecv of the DECODE_DRAFT_LAST (DDL)\n        # return tensors.  Keyed by head_token; posted by TP0 at the end of\n        # the matching DECODE_DRAFT_FIRST (DDF) send block, consumed by\n        # _execute_model_edge_draft_tail.  The AsyncIntermediateTensors\n        # carries the ``__comm_event__`` NPU event so busy_loop can poll\n        # readiness and ack the scheduler without touching HCCL.\n        self._draft_recv_cache: dict[str, AsyncIntermediateTensors] = {}\n        self._draft_recv_lock = threading.Lock()\n        # head_tokens whose readiness has already been reported through\n        # edge_recv_ready_mq (poll-phase dedup).\n        self._draft_recv_reported: set[str] = set()"
}
```

</details>


---

## User <sup>2026/8/16 15:34:01</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\worker\worker.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:34:03</sup>


---

## Assistant <sup>2026/8/16 15:34:03</sup>

现在加两个 helper。先定位 CHER 原语块结尾：


---

## Assistant <sup>2026/8/16 15:34:04</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"def get_or_post_early_recv\\|def _execute_model_edge_head\\|def _scheduled_draft_tensor_meta\\|def _execute_model_edge_draft_tail\\|def _record_pp_send_work\\|def _hidden_channel_for\" vllm_ascend/worker/worker.py",
  "description": "Locate helper anchor points in worker.py"
}
```

</details>


---

## User <sup>2026/8/16 15:34:05</sup>

<details>
<summary>Tool Result</summary>

```
794:    def _record_pp_send_work(
922:    def get_or_post_early_recv(
1067:    def _hidden_channel_for(self, scheduler_output: "SchedulerOutput") -> HiddenChannelType:
1098:    def _execute_model_edge_head(
1382:    def _scheduled_draft_tensor_meta(
1556:    def _execute_model_edge_draft_tail(
```

</details>


---

## Assistant <sup>2026/8/16 15:34:06</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "limit": 70,
  "offset": 922
}
```

</details>


---

## User <sup>2026/8/16 15:34:06</sup>

<details>
<summary>Tool Result</summary>

```
922	    def get_or_post_early_recv(
923	        self, head_token: str | None, channel: "HiddenChannelType",
924	        num_tokens: int, include_mrope: bool = True,
925	    ) -> AsyncIntermediateTensors | None:
926	        """Atomically reuse the guard-thread's early-recv entry, or post one.
927	
928	        execute_model calls this instead of pop-then-fallback: under
929	        ``_early_recv_lock`` it pops a cached entry if the guard thread
930	        already posted one, otherwise it posts the irecv itself and returns
931	        it.  This guarantees at most one irecv per head_token even when the
932	        guard thread's hint dequeue races ahead of (or lags behind)
933	        execute_model's pp_scheduler_output dequeue -- the original
934	        pop-then-fallback path posted a second irecv when the guard had not
935	        posted yet, and both irecvs then raced for the sender's single isend,
936	        deadlocking (the losing irecv waits forever -> no ack -> no POST_OUT
937	  
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:34:11</sup>


---

## Assistant <sup>2026/8/16 15:34:11</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "limit": 130,
  "offset": 1382
}
```

</details>


---

## User <sup>2026/8/16 15:34:11</sup>

<details>
<summary>Tool Result</summary>

```
1382	    def _scheduled_draft_tensor_meta(
1383	        self,
1384	        scheduler_output: "SchedulerOutput",
1385	        direction: str,
1386	    ) -> ScheduledDraftTensorMeta | None:
1387	        """Derive the scheduled draft wire schema on both peers.
1388	
1389	        Sequence-parallel draft tensors currently retain their dynamic
1390	        sender-side shard shapes, which can differ between heterogeneous edge
1391	        and cloud TP groups. Keep that configuration on the compatibility path
1392	        until draft transfer mirrors the main model's all-gather/re-chunk flow.
1393	        """
1394	        if enable_sp():
1395	            return None
1396	
1397	        speculative_config = self.model_runner.speculative_config
1398	        drafter = self.model_runner.drafter
1399	        if (
1400	            speculative_config is None
1401	            or speculative_config.method is None
1402	            or drafter is None
1403	        ):
1404	            return None
1405	
1406
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:34:13</sup>


---

## Assistant <sup>2026/8/16 15:34:13</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "limit": 100,
  "offset": 1098
}
```

</details>


---

## User <sup>2026/8/16 15:34:13</sup>

<details>
<summary>Tool Result</summary>

```
1098	    def _execute_model_edge_head(
1099	        self,
1100	        scheduler_output: "SchedulerOutput",
1101	        layer_slice_info: Any,
1102	    ) -> ModelRunnerOutput | AsyncModelRunnerOutput | None:
1103	        """Edge head segment (PF/DF): segment_a -> isend -> suspend -> return EMPTY."""
1104	        output = self.model_runner.execute_model(
1105	            scheduler_output, intermediate_tensors=None,
1106	            layer_slice_info=layer_slice_info,
1107	        )
1108	        is_last_slice = (
1109	            layer_slice_info is None or layer_slice_info.is_last_slice
1110	        )
1111	        if not is_last_slice:
1112	            return None
1113	
1114	        if isinstance(output, (ModelRunnerOutput, AsyncModelRunnerOutput, NoneType)):
1115	            return output
1116	
1117	        assert isinstance(output, IntermediateTensors)
1118	        # Edge-cloud with heterogeneous SP: aggregate SP shards to full
1119	        # sequence before cross-PP send so cloud can
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:34:17</sup>


---

## Assistant <sup>2026/8/16 15:34:18</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"DECODE_DRAFT_FIRST\\|DRAFT_FIRST\\|draft_first\" vllm_ascend/worker/worker.py | head -20",
  "description": "Find DDF execution path in worker.py"
}
```

</details>


---

## User <sup>2026/8/16 15:34:19</sup>

<details>
<summary>Tool Result</summary>

```
254:        # the matching DECODE_DRAFT_FIRST (DDF) send block, consumed by
1020:                BatchType.PREFILL_DRAFT_FIRST,
1022:                BatchType.DECODE_DRAFT_FIRST,
1036:                    BatchType.PREFILL_DRAFT_FIRST,
1037:                    BatchType.DECODE_DRAFT_FIRST,
1044:                BatchType.PREFILL_DRAFT_FIRST,
1045:                BatchType.DECODE_DRAFT_FIRST,
1077:            BatchType.DECODE_DRAFT_FIRST,
1086:            BatchType.PREFILL_DRAFT_FIRST,
1238:        # (DECODE_FIRST / PREFILL_FIRST here vs the *_DRAFT_FIRST path).
1521:        output = self.model_runner._run_edge_cloud_draft_first_segment(
```

</details>


---

## Assistant <sup>2026/8/16 15:34:21</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "limit": 90,
  "offset": 1060
}
```

</details>


---

## User <sup>2026/8/16 15:34:21</sup>

<details>
<summary>Tool Result</summary>

```
1060	                )
1061	
1062	        # Fallback: original path for non-edge-cloud or unhandled batch types.
1063	        return self._execute_model_legacy(
1064	            scheduler_output, layer_slice_info, use_alt_group
1065	        )
1066	
1067	    def _hidden_channel_for(self, scheduler_output: "SchedulerOutput") -> HiddenChannelType:
1068	        channel = scheduler_output.hidden_channel
1069	        if channel is not None:
1070	            return channel
1071	        bt = scheduler_output.batch_type
1072	        if bt in (BatchType.PREFILL_FIRST, BatchType.PREFILL_LAST):
1073	            return HiddenChannelType.PREFILL_1
1074	        if bt in (BatchType.DECODE_FIRST, BatchType.DECODE_LAST):
1075	            return HiddenChannelType.DECODE
1076	        if bt in (
1077	            BatchType.DECODE_DRAFT_FIRST,
1078	            BatchType.DECODE_DRAFT_LAST,
1079	        ):
1080	            # MTP draft data plane travels on its dedicated DRAFT channel
1081	            # (schedu
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:34:23</sup>


---

## Assistant <sup>2026/8/16 15:34:23</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "limit": 75,
  "offset": 1513
}
```

</details>


---

## User <sup>2026/8/16 15:34:23</sup>

<details>
<summary>Tool Result</summary>

```
1513	            req_id_to_index={req_id: i for i, req_id in enumerate(req_ids)},
1514	        )
1515	
1516	    def _execute_model_edge_draft_head(
1517	        self, scheduler_output: "SchedulerOutput"
1518	    ) -> ModelRunnerOutput:
1519	        """Run and send one edge-side scheduled draft first segment."""
1520	        logger.info(f"Execute model, batch_type: {scheduler_output.batch_type}")
1521	        output = self.model_runner._run_edge_cloud_draft_first_segment(
1522	            scheduler_output
1523	        )
1524	        if not isinstance(output, IntermediateTensors):
1525	            raise RuntimeError("draft FIRST did not produce intermediates")
1526	        if get_pp_group().world_size == 2:
1527	            tensor_dict = {
1528	                key: value.contiguous()
1529	                if isinstance(value, torch.Tensor)
1530	                else value
1531	                for key, value in output.items()
1532	            }
1533	            send_tensor_meta = self._sche
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:34:26</sup>


---

## Assistant <sup>2026/8/16 15:34:27</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"head_token\" vllm_ascend/worker/worker.py | head -20; echo ---; grep -n \"def edge_cloud_broadcast_recv_scheduled_draft\\|__comm_event__\" vllm_ascend/distributed/parallel_state.py | head; echo ---; grep -n \"__comm_event__\\|_comm_event\" vllm-pdmix/vllm/v1/worker/gpu_worker.py",
  "description": "Check head_token usage and comm_event plumbing"
}
```

</details>


---

## User <sup>2026/8/16 15:34:28</sup>

<details>
<summary>Tool Result</summary>

```
Exit code 2
233:        # execute_model (keyed by head_token); execute_model pops the cached
241:        # head_tokens already consumed by busy_loop (get_or_post_early_recv).
253:        # return tensors.  Keyed by head_token; posted by TP0 at the end of
260:        # head_tokens whose readiness has already been reported through
831:    # the batch's execute_model (keyed by head_token); execute_model calls
866:        the same head_token (or one that execute_model already posted via
868:        per head_token, avoiding the double-post deadlock where two irecvs on
871:        ht = hint.get("head_token")
880:                {k: hint.get(k) for k in ("head_token", "hidden_channel",
913:                    "[CHER] start_early_irecv failed head_token=%s channel=%s",
918:            "[CHER] early-recv posted head_token=%s channel=%s num_tokens=%d",
923:        self, head_token: str | None, channel: "HiddenChannelType",
931:        it.  This guarantees at most one irecv per head_token even wh
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:34:31</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"_comm_event\\|def wait_for_comm\\|def is_ready\\|class AsyncIntermediateTensors\" ../vllm-pdmix/vllm/v1/worker/gpu_worker.py | head; echo ---; grep -n \"head_token\" ../vllm-pdmix/vllm/v1/core/sched/output.py | head -5; echo ---; grep -n \"scheduler_output.head_token\\|\\.head_token\" vllm_ascend/worker/worker.py | grep -v \"#\" | head",
  "description": "Check AsyncIntermediateTensors API and head_token field"
}
```

</details>


---

## User <sup>2026/8/16 15:34:33</sup>

<details>
<summary>Tool Result</summary>

```
85:class AsyncIntermediateTensors(IntermediateTensors):
103:        self._comm_event = comm_event
106:    def is_ready(self) -> bool:
115:        event = self._comm_event
120:    def wait_for_comm(self) -> None:
---
399:    head_token: str | None = None
408:    # head_token for edge/cloud pairing; the fields below identify the parent
---
```

</details>


---

## Assistant <sup>2026/8/16 15:34:35</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\worker\\gpu_worker.py",
  "limit": 60,
  "offset": 85
}
```

</details>


---

## User <sup>2026/8/16 15:34:35</sup>

<details>
<summary>Tool Result</summary>

```
85	class AsyncIntermediateTensors(IntermediateTensors):
86	    """IntermediateTensors with lazy comm synchronization"""
87	
88	    def __init__(
89	        self,
90	        tensors: dict[str, torch.Tensor],
91	        comm_handles: list[Handle] | None = None,
92	        comm_postprocess: list[Callable[[], None]] | None = None,
93	        comm_event: Any = None,
94	    ) -> None:
95	        super().__init__(tensors)
96	        self._comm_handles = comm_handles
97	        self._comm_postprocess = comm_postprocess
98	        # Optional device event recorded on the recv stream right after the
99	        # irecv(s) were issued (edge-cloud PD separation).  When present,
100	        # ``is_ready()`` gives a non-blocking readiness probe for the *recv
101	        # transfer only* - the TP broadcast / split postprocess chain is NOT
102	        # covered by this event and still requires ``wait_for_comm()``.
103	        self._comm_event = comm_event
104	        self._comm_waited = False
105	
106	 
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:34:39</sup>


---

## Assistant <sup>2026/8/16 15:34:40</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -rn \"__comm_event__\" ../vllm-pdmix/vllm vllm_ascend --include=*.py",
  "description": "Find all __comm_event__ consumers"
}
```

</details>


---

## User <sup>2026/8/16 15:34:40</sup>

<details>
<summary>Tool Result</summary>

```
vllm_ascend/distributed/parallel_state.py:1600:        tensor_dict["__comm_event__"] = comm_event
vllm_ascend/distributed/parallel_state.py:2183:            recv_tensor_dict["__comm_event__"] = comm_event
vllm_ascend/worker/worker.py:256:        # carries the ``__comm_event__`` NPU event so busy_loop can poll
```

</details>


---

## Assistant <sup>2026/8/16 15:35:01</sup>


---

## Assistant <sup>2026/8/16 15:35:01</sup>

现在确认一个关键正确性点：DDL 的 `draft_step_idx` 是否与 DDF 一致(决定提前挂的 irecv 形状是否匹配)：


---

## Assistant <sup>2026/8/16 15:35:01</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"draft_step_idx\" vllm_ascend/core/pd_separated_scheduler.py | head -30",
  "description": "Check draft_step_idx handling in scheduler"
}
```

</details>


---

## User <sup>2026/8/16 15:35:02</sup>

<details>
<summary>Tool Result</summary>

```
1123:            if scheduler_output.draft_step_idx is None:
1124:                raise RuntimeError("draft flight is missing draft_step_idx")
1128:            flight_id = f"{draft_task_id}:{scheduler_output.draft_step_idx}"
2199:        if scheduler_output.draft_step_idx is None:
2200:            raise RuntimeError("PREFILL_DRAFT_LAST missing draft_step_idx")
2225:        if scheduler_output.draft_step_idx is None:
2226:            raise RuntimeError("DECODE_DRAFT_LAST missing draft_step_idx")
2291:                    scheduler_output.draft_step_idx,
2326:            # 时 -1（flight 键 draft_task_id:draft_step_idx 配对）。
2369:            "parent_req_id=%s, draft_step_idx=%s, head_token=%s, "
2375:            scheduler_output.draft_step_idx,
2475:                draft_step_idx=step_idx,
2585:        draft_step_idx: int,
2655:            draft_step_idx=draft_step_idx,
2702:        draft_step_idx = int(draft_last.draft_step_idx or 0)
2703:        next_step_idx = draft_step_idx + 1
2717:      
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:35:05</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 70,
  "offset": 2218
}
```

</details>


---

## User <sup>2026/8/16 15:35:05</sup>

<details>
<summary>Tool Result</summary>

```
2218	    def _validate_decode_draft_tail_channel(
2219	        self, scheduler_output: SchedulerOutput
2220	    ) -> None:
2221	        if not scheduler_output.head_token:
2222	            raise RuntimeError("DECODE_DRAFT_LAST missing head_token")
2223	        if not scheduler_output.draft_task_id:
2224	            raise RuntimeError("DECODE_DRAFT_LAST missing draft_task_id")
2225	        if scheduler_output.draft_step_idx is None:
2226	            raise RuntimeError("DECODE_DRAFT_LAST missing draft_step_idx")
2227	        if scheduler_output.hidden_channel != (
2228	            self.hidden_channel_manager.draft_channel()
2229	        ):
2230	            raise RuntimeError(
2231	                "DECODE_DRAFT_LAST expects the dedicated draft hidden "
2232	                f"channel {self.hidden_channel_manager.draft_channel()}, "
2233	                f"got {scheduler_output.hidden_channel}"
2234	            )
2235	
2236	    def _pick_prefill_draft_first_batch(self) -> SchedulerOutput:
22
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:35:08</sup>


---

## Assistant <sup>2026/8/16 15:35:09</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"_start_decode_draft_last_delay\\|DECODE_DRAFT_LAST\\|self_post\\|self-post\" vllm_ascend/core/pd_separated_scheduler.py | sed -n 1,40p",
  "description": "Find DDL self-post creation site"
}
```

</details>


---

## User <sup>2026/8/16 15:35:10</sup>

<details>
<summary>Tool Result</summary>

```
84:    BatchType.DECODE_DRAFT_FIRST: BatchType.DECODE_DRAFT_LAST,
263:        elif batch_type == BatchType.DECODE_DRAFT_LAST:
560:        # [MTP] DECODE_DRAFT_LAST delay scheduling (mirrors
770:        safe edge-side fallback either -- a self-posted tail would need
1015:        drop，其配对 PDFL 从未 self-post，入队时的 +1 无完成事件配对，
1388:            # A queued placeholder DECODE_FIRST already self-posted its tail
1474:        # DECODE_FIRST's self-posted tail must wait for its head.
1790:    def _start_decode_draft_last_delay(self) -> None:
2222:            raise RuntimeError("DECODE_DRAFT_LAST missing head_token")
2224:            raise RuntimeError("DECODE_DRAFT_LAST missing draft_task_id")
2226:            raise RuntimeError("DECODE_DRAFT_LAST missing draft_step_idx")
2231:                "DECODE_DRAFT_LAST expects the dedicated draft hidden "
2256:            last_type = BatchType.DECODE_DRAFT_LAST
2276:                        # PDFL 尚未 self-post（PDFL 只在 PDFF pick 时生成），
2364:            self._
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:35:13</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 70,
  "offset": 2320
}
```

</details>


---

## User <sup>2026/8/16 15:35:13</sup>

<details>
<summary>Tool Result</summary>

```
2320	            )
2321	        self._register_pd_flight(scheduler_output)
2322	        if kind == "prefill":
2323	            # Phase C（设计 §6.2/§7.5）：PDFL 由云侧在 PDFF 完成后经
2324	            # POST_OUT 发布——云侧往返即 pacing，边侧不再自贴尾、不再
2325	            # 延迟计时。派发仍 +1 remote pending，云侧发布的 PDFL 完成
2326	            # 时 -1（flight 键 draft_task_id:draft_step_idx 配对）。
2327	            # 通道校验在 PDFL 到达 `_pick_draft_last_batch_by_kind` 时进行。
2328	            self.prefill_draft_remote_pending_count += 1
2329	            # [FORCE] PDFF pick → prefill_draft_last_pending（交替门控）
2330	            self._force.on_pick(BatchType.PREFILL_DRAFT_FIRST)
2331	            # Phase C review: 登记 watchdog 截止时间——云发 PDFL 超过
2332	            # 阈值未到即判定链路故障（丢包/云侧故障），报错退出。
2333	            self._prefill_draft_last_watchdog[
2334	                scheduler_output.draft_task_id
2335	            ] = (
2336	                time.monotonic()
2337	                + self._prefill_draft_last_watchdog_seconds
2338	            )
2339	        e
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:35:15</sup>


---

## Assistant <sup>2026/8/16 15:35:16</sup>

`replace()` 保留全部字段——DDL 与 DDF 的 c2e meta 完全一致，提前挂的 irecv 形状必然匹配。写入 helper:


---

## Assistant <sup>2026/8/16 15:35:24</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "old_string": "    def cleanup_early_recv(self, head_token: str) -> None:\n        \"\"\"Drop a leaked early-recv entry (e.g. request aborted mid-prefill).\"\"\"\n        with self._early_recv_lock:\n            self._early_recv_handles.pop(head_token, None)\n            self._early_recv_consumed.discard(head_token)\n",
  "new_string": "    def cleanup_early_recv(self, head_token: str) -> None:\n        \"\"\"Drop a leaked early-recv entry (e.g. request aborted mid-prefill).\"\"\"\n        with self._early_recv_lock:\n            self._early_recv_handles.pop(head_token, None)\n            self._early_recv_consumed.discard(head_token, None)\n\n    def _post_draft_return_irecv(\n        self, scheduler_output: \"SchedulerOutput\",\n    ) -> None:\n        \"\"\"[EHER-draft] Post the DDL return irecv while the DDF send drains.\n\n        Called at the end of the DECODE_DRAFT_FIRST (DDF) send block, on the\n        PP rank with world_size==2 only (edge TP0; TP1 receives the DDL via\n        the TP broadcast postprocess, so no early post there).  The decode-\n        domain DDL is self-posted by the edge scheduler at DDF pick time via\n        ``replace()`` -- which preserves draft_step_idx / token counts /\n        head_token -- so the c2e meta derived here is byte-identical to the\n        one the DDL execute would derive, and the posted irecv shapes always\n        match the cloud's isend.  The recv now overlaps the remaining DDF\n        work plus the scheduler round trip instead of serializing behind\n        the DDL dispatch.\n\n        Fails soft: any error keeps the sync fallback path in\n        ``_execute_model_edge_draft_tail`` (a second irecv would only be\n        posted if the cached entry is absent, which the exception path\n        guarantees by not caching).\n        \"\"\"\n        if get_pp_group().world_size != 2:\n            return\n     
...(truncated)
```

</details>


---

## User <sup>2026/8/16 15:35:25</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\worker\worker.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:35:28</sup>


---

## Assistant <sup>2026/8/16 15:35:29</sup>

修正我误改的一处 `discard` 签名:


---

## Assistant <sup>2026/8/16 15:35:29</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "old_string": "        with self._early_recv_lock:\n            self._early_recv_handles.pop(head_token, None)\n            self._early_recv_consumed.discard(head_token, None)\n\n    def _post_draft_return_irecv(",
  "new_string": "        with self._early_recv_lock:\n            self._early_recv_handles.pop(head_token, None)\n            self._early_recv_consumed.discard(head_token)\n\n    def _post_draft_return_irecv("
}
```

</details>


---

## User <sup>2026/8/16 15:35:30</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\worker\worker.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:35:32</sup>

现在改 DDF 发送块挂 early-post 钩子，以及 DDL 尾部消费缓存：


---

## Assistant <sup>2026/8/16 15:35:35</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "old_string": "            self._record_pp_send_work(\n                edge_cloud_send_tensor_dict_scheduled_draft(\n                    tensor_dict,\n                    tensor_meta=send_tensor_meta,\n                    channel=channel,\n                ),\n                channel=channel,\n            )\n            logger.info(\n                \"Send intermediate tensors to cloud, \"\n                f\"hidden_channel: {channel.value}\"\n            )",
  "new_string": "            self._record_pp_send_work(\n                edge_cloud_send_tensor_dict_scheduled_draft(\n                    tensor_dict,\n                    tensor_meta=send_tensor_meta,\n                    channel=channel,\n                ),\n                channel=channel,\n            )\n            # [EHER-draft] DDF send recorded; the matching decode-domain DDL\n            # is already self-posted on the edge scheduler, so the cloud's\n            # return isend can land any moment -- post our side of the DDL\n            # recv now (TP0 only) so the transfer overlaps the remaining\n            # work instead of starting at DDL dispatch.\n            self._post_draft_return_irecv(scheduler_output)\n            logger.info(\n                \"Send intermediate tensors to cloud, \"\n                f\"hidden_channel: {channel.value}\"\n            )"
}
```

</details>


---

## User <sup>2026/8/16 15:35:36</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\worker\worker.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:35:41</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\worker\\worker.py",
  "old_string": "    def _execute_model_edge_draft_tail(\n        self, scheduler_output: \"SchedulerOutput\"\n    ) -> ModelRunnerOutput:\n        \"\"\"Receive and finish one edge-side scheduled draft step.\"\"\"\n        logger.info(f\"Execute model, batch_type: {scheduler_output.batch_type}\")\n        recv_tensor_meta = self._scheduled_draft_tensor_meta(\n            scheduler_output,\n            \"c2e\",\n        )\n        channel = self._hidden_channel_for(scheduler_output)\n        tensor_dict, comm_handles, comm_postprocess = (\n            edge_cloud_broadcast_recv_scheduled_draft(\n                tensor_meta=recv_tensor_meta,\n                channel=channel,\n            )\n        )\n        for handle in comm_handles:\n            handle.wait()\n        for postprocess in comm_postprocess:\n            postprocess()\n        logger.info(\n            \"Receive intermediate tensors from cloud after, \"\n            f\"hidden_channel: {channel.value}\"\n        )\n        assert tensor_dict is not None\n        return self.model_runner._run_edge_cloud_draft_last_segment(\n            scheduler_output, IntermediateTensors(tensor_dict)\n        )",
  "new_string": "    def _execute_model_edge_draft_tail(\n        self, scheduler_output: \"SchedulerOutput\"\n    ) -> ModelRunnerOutput:\n        \"\"\"Receive and finish one edge-side scheduled draft step.\"\"\"\n        logger.info(f\"Execute model, batch_type: {scheduler_output.batch_type}\")\n        channel = self._hidden_channel_for(scheduler_output)\n        # [EHER-draft] Prefer the entry TP0 posted at DDF time: the NPU\n        # transfer has been overlapping since then, and wait_for_comm()\n        # (inside the lazy .tensors access) degenerates to a no-op wait\n        # when the event already fired.  Miss => sync fallback below.\n        entry = self._consume_draft_recv(scheduler_output
...(truncated)
```

</details>


---

## User <sup>2026/8/16 15:35:42</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\worker\worker.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:35:45</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "python -m py_compile vllm_ascend/worker/worker.py vllm_ascend/distributed/parallel_state.py && echo SYNTAX_OK",
  "description": "Compile-check worker.py and parallel_state.py"
}
```

</details>


---

## User <sup>2026/8/16 15:35:55</sup>

<details>
<summary>Tool Result</summary>

```
vllm_ascend/worker/worker.py:312: SyntaxWarning: 'return' in a 'finally' block
  return
SYNTAX_OK
```

</details>


---

## Assistant <sup>2026/8/16 15:35:58</sup>


---

## Assistant <sup>2026/8/16 15:35:59</sup>

P1-3 完成(警告为存量问题)。进入 P1-4:边侧 sideband MQ。先看 CHER 的 MQ 创建/重建代码：


---

## Assistant <sup>2026/8/16 15:36:01</sup>

<details>
<summary>Tool: <code>TodoWrite</code></summary>

```json
{
  "todos": [
    {
      "activeForm": "Creating DRAFT channel",
      "content": "P0-1..P0-4: DRAFT 专用通道端到端",
      "status": "completed"
    },
    {
      "activeForm": "Adding irecv NPU event",
      "content": "P1-1 irecv NPU event (parallel_state)",
      "status": "completed"
    },
    {
      "activeForm": "Adding is_ready()",
      "content": "P1-2 AsyncIntermediateTensors.is_ready()",
      "status": "completed"
    },
    {
      "activeForm": "Posting early DDL irecv at DDF",
      "content": "P1-3 worker.py: DDF 时提前挂 DDL return-irecv + head_token stash",
      "status": "completed"
    },
    {
      "activeForm": "Adding busy-loop poll and sideband MQ",
      "content": "P1-4 边侧 sideband MQ + busy_loop 就绪轮询上报",
      "status": "in_progress"
    },
    {
      "activeForm": "Adding scheduler DDL ack gate",
      "content": "P1-5 scheduler: DDL 派发门 = recv 就绪 ack",
      "status": "pending"
    },
    {
      "activeForm": "Relaxing draft gate",
      "content": "P2-1 draft 门 ==0 -> <limit + inflight 提前释放",
      "status": "pending"
    },
    {
      "activeForm": "Bypassing pacing delay",
      "content": "P2-2 pacing delay 旁路 + watchdog",
      "status": "pending"
    }
  ]
}
```

</details>


---

## User <sup>2026/8/16 15:36:01</sup>

<details>
<summary>Tool Result</summary>

```
Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable
```

</details>


---

## Assistant <sup>2026/8/16 15:36:04</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "limit": 80,
  "offset": 100
}
```

</details>


---

## User <sup>2026/8/16 15:36:04</sup>

<details>
<summary>Tool Result</summary>

```
100	            )
101	            scheduler_output_handle = self.rpc_broadcast_mq.export_handle()
102	        elif envs.VLLM_PP_NON_LEADER_ENGINE_CORE:
103	            # For non-leader PP rank running with a passive EngineCore,
104	            # create a local rpc_broadcast_mq to broadcast SchedulerOutput
105	            # to local workers. Workers will use this MQ instead of
106	            # inner_dp_world_group to receive scheduler_output.
107	            max_chunk_bytes = envs.VLLM_MQ_MAX_CHUNK_BYTES_MB * 1024 * 1024
108	            self.rpc_broadcast_mq = MessageQueue(
109	                self.local_world_size,
110	                self.local_world_size,
111	                max_chunk_bytes=max_chunk_bytes,
112	                connect_ip=get_loopback_ip(),
113	            )
114	            scheduler_output_handle = self.rpc_broadcast_mq.export_handle()
115	
116	        # [CHER] Cloud-side hidden early-receive: build a sideband MQ that
117	        # PassiveEC writes recv-hints to and
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:36:06</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "limit": 60,
  "offset": 425
}
```

</details>


---

## User <sup>2026/8/16 15:36:06</sup>

<details>
<summary>Tool Result</summary>

```
425	# (it also rebuilds); the wrapper early-returns if cloud_recv_hint_mq is
426	# already set, so there is no double-rebuild / clobber.
427	_OrigWorkerProc = AscendWorkerProc.__bases__[0]
428	_orig_init_message_queues = _OrigWorkerProc._init_message_queues
429	
430	
431	def _cher_init_message_queues(self, input_shm_handle, vllm_config):
432	    _orig_init_message_queues(self, input_shm_handle, vllm_config)
433	    # Only rebuild if not already done by AscendWorkerProc._init_message_queues.
434	    if getattr(self, "cloud_recv_hint_mq", None) is not None:
435	        return
436	    self.cloud_recv_hint_mq = None
437	    if not (
438	        envs.VLLM_PP_NON_LEADER_ENGINE_CORE
439	        and self.local_rank == 0
440	        and not vllm_config.parallel_config.is_edge_node
441	        and _cloud_pd_enabled(vllm_config)
442	    ):
443	        return
444	    _raw = os.environ.get(_CLOUD_RECV_HINT_MQ_ENV)
445	    if _raw is None:
446	        return
447	    try:
448	        _handle = pickle
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:36:20</sup>


---

## Assistant <sup>2026/8/16 15:36:20</sup>

MQ 方向与 CHER 相反(worker -> EngineCore)。看 EngineCore 侧结构：


---

## Assistant <sup>2026/8/16 15:36:21</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"class \\|def \\|scheduler\\b\" vllm_ascend/patch/engine_core/patch_engine_core.py 2>/dev/null | head -40 || ls vllm_ascend/patch/engine_core/ 2>/dev/null || find vllm_ascend -name \"patch_engine_core*\"",
  "description": "Locate patch_engine_core.py structure"
}
```

</details>


---

## User <sup>2026/8/16 15:36:22</sup>

<details>
<summary>Tool Result</summary>

```
(Bash completed with no output)
```

</details>


---

## Assistant <sup>2026/8/16 15:36:24</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "find vllm_ascend ../vllm-pdmix/vllm -name \"*engine_core*\" | head; echo ---; grep -rn \"busy_loop\" ../vllm-pdmix/vllm/v1/executor/multiproc_executor.py | head",
  "description": "Find engine core files and busy_loop"
}
```

</details>


---

## User <sup>2026/8/16 15:36:25</sup>

<details>
<summary>Tool Result</summary>

```
vllm_ascend/patch/platform/patch_engine_core.py
---
766:                target=self.async_output_busy_loop,
781:        # the early-irecv guard thread eagerly.  busy_loop is single-threaded and
783:        # thread (not busy_loop) owns cloud_recv_hint_mq: it drains recv-hints,
784:        # posts irecv, and waits it to completion while busy_loop is blocked on
1042:            worker.worker_busy_loop()
1045:            # NOTE: if an Exception arises in busy_loop, we send
1106:        it is passed to the async_output_busy_loop thread. Otherwise, it is
1114:    def async_output_busy_loop(self):
1132:    def worker_busy_loop(self):
1260:        ``cloud_recv_hint_mq``, and this guard thread (not busy_loop) owns that
```

</details>


---

## Assistant <sup>2026/8/16 15:36:27</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"class \\|    def \\|scheduler\" vllm_ascend/patch/platform/patch_engine_core.py | head -50",
  "description": "Structure of patch_engine_core.py"
}
```

</details>


---

## User <sup>2026/8/16 15:36:28</sup>

<details>
<summary>Tool Result</summary>

```
28:  cloud-returned batches into the local PD scheduler, publish
179:    scheduler's ``prefills_last_ready`` / ``decodes_last_ready`` queues.
184:        hasattr(self.scheduler, "prefills_last_ready")
185:        and hasattr(self.scheduler, "decodes_last_ready")
186:        and hasattr(self.scheduler, "prefill_drafts_last_ready")
187:        and hasattr(self.scheduler, "decode_drafts_last_ready")
193:        logger.info(f"Received scheduler_output from cloud, batch_type: {bt}")
195:            self.scheduler.prefills_last_ready.append(so)
197:            self.scheduler.decodes_last_ready.append(so)
203:            self.scheduler.prefill_drafts_last_ready.append(so)
224:    self, scheduler_output: SchedulerOutput
230:    the scheduler registry).  The cloud must keep the matching batch row
242:        self.scheduler, "filter_cloud_finished_req_ids", None
245:        channel.publish(scheduler_output)
247:    finished = set(getattr(scheduler_output, "finished_req_ids", None) or ())
249:   
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:36:30</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_engine_core.py",
  "limit": 120,
  "offset": 100
}
```

</details>


---

## User <sup>2026/8/16 15:36:30</sup>

<details>
<summary>Tool Result</summary>

```
100	def _patched_engine_core_init(self, *args, **kwargs):
101	    _ORIG_ENGINE_CORE_INIT(self, *args, **kwargs)
102	
103	    parallel_config: ParallelConfig = self.vllm_config.parallel_config
104	
105	    # PD-separation is owned by the ascend plugin and lives under
106	    # ``additional_config.edge_cloud_config.pd_separation``. ``init_ascend_config``
107	    # is idempotent and returns the cached singleton if already initialized
108	    # in the main process; in a freshly-spawned subprocess it re-initializes
109	    # from the ``vllm_config`` we hold.
110	    from vllm_ascend.ascend_config import init_ascend_config
111	    ascend_config = init_ascend_config(self.vllm_config)
112	    edge_cloud = getattr(ascend_config, "edge_cloud_config", None)
113	    pd_enabled = bool(
114	        edge_cloud is not None
115	        and getattr(edge_cloud, "enabled", False)
116	        and getattr(edge_cloud, "pd_separation", None) is not None
117	        and edge_cloud.pd_separation.enabled
118	   
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:36:32</sup>


---

## Assistant <sup>2026/8/16 15:36:33</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -rn \"_drain_pd_channel_inbox\" vllm_ascend ../vllm-pdmix/vllm | grep -v Binary",
  "description": "Find drain call sites"
}
```

</details>


---

## User <sup>2026/8/16 15:36:34</sup>

<details>
<summary>Tool Result</summary>

```
vllm_ascend/patch/platform/patch_engine_core.py:31:* ``EngineCore._drain_pd_channel_inbox`` /
vllm_ascend/patch/platform/patch_engine_core.py:177:def _drain_pd_channel_inbox(self) -> None:
vllm_ascend/patch/platform/patch_engine_core.py:751:    self._drain_pd_channel_inbox()
vllm_ascend/patch/platform/patch_engine_core.py:831:        self._drain_pd_channel_inbox()
vllm_ascend/patch/platform/patch_engine_core.py:1106:    EngineCore._drain_pd_channel_inbox = _drain_pd_channel_inbox
```

</details>


---

## Assistant <sup>2026/8/16 15:36:36</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_engine_core.py",
  "limit": 110,
  "offset": 725
}
```

</details>


---

## User <sup>2026/8/16 15:36:36</sup>

<details>
<summary>Tool Result</summary>

```
725	            is_pregenerated = getattr(
726	                self.scheduler,
727	                "is_pre_generated_draft",
728	                lambda _so: False,
729	            )(scheduler_output)
730	            if not is_pregenerated:
731	                return True
732	    return False
733	
734	
735	# =======================================================================#
736	# EngineCore.step — full replacement, mirrors upstream + dest inserts.    #
737	# =======================================================================#
738	def _patched_step(self):
739	    """Schedule, execute, and make output.
740	
741	    Returns tuple of outputs and a flag indicating whether the model
742	    was executed.
743	    """
744	    # Check for any requests remaining in the scheduler - unfinished,
745	    # or finished and not yet removed from the batch.
746	    if not self.scheduler.has_requests():
747	        return {}, False
748	
749	    # [ascend insert] Drain POST_OUT (cloud → edge) int
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:36:44</sup>


---

## Assistant <sup>2026/8/16 15:36:44</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\executor\\multiproc_executor.py",
  "limit": 120,
  "offset": 740
}
```

</details>


---

## User <sup>2026/8/16 15:36:44</sup>

<details>
<summary>Tool Result</summary>

```
740	            "is_driver_worker": is_driver_worker,
741	            "shared_worker_lock": shared_worker_lock,
742	        }
743	        wrapper.init_worker(all_kwargs)
744	        self.worker = wrapper
745	
746	        self.setup_proc_title_and_log_prefix(
747	            enable_ep=vllm_config.parallel_config.enable_expert_parallel
748	        )
749	
750	        # Load model
751	        self.worker.init_device()
752	        # Update process title now that parallel groups are initialized
753	        self.setup_proc_title_and_log_prefix(
754	            enable_ep=vllm_config.parallel_config.enable_expert_parallel
755	        )
756	        if envs.VLLM_ELASTIC_EP_SCALE_UP_LAUNCH:
757	            self.worker.elastic_ep_execute("load_model")
758	        else:
759	            self.worker.load_model()
760	
761	        scheduler_config = vllm_config.scheduler_config
762	        self.use_async_scheduling = scheduler_config.async_scheduling
763	        if self.use_async_scheduling:
764	       
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:36:46</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\executor\\multiproc_executor.py",
  "limit": 180,
  "offset": 1132
}
```

</details>


---

## User <sup>2026/8/16 15:36:46</sup>

<details>
<summary>Tool Result</summary>

```
1132	    def worker_busy_loop(self):
1133	        """Main busy loop for Multiprocessing Workers"""
1134	        assert self.rpc_broadcast_mq is not None
1135	        while True:
1136	            # Poll local MQ for pp scheduler output from passive
1137	            # EngineCore (non-blocking).
1138	            if self.local_rpc_broadcast_mq is not None:
1139	                try:
1140	                    method, args, kwargs, output_rank = (
1141	                        self.local_rpc_broadcast_mq.dequeue(timeout=0.1)
1142	                    )
1143	                    if isinstance(method, bytes) and method == b"pp_scheduler_output":
1144	                        scheduler_output = args[0]
1145	                        slice_info = args[1] if len(args) > 1 else None
1146	                        # Execute model with the received SchedulerOutput.
1147	                        try:
1148	                            func = getattr(self.worker, "execute_model")
1149	                            o
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:37:00</sup>


---

## Assistant <sup>2026/8/16 15:37:00</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\executor\\multiproc_executor.py",
  "limit": 80,
  "offset": 1311
}
```

</details>


---

## User <sup>2026/8/16 15:37:00</sup>

<details>
<summary>Tool Result</summary>

```
1311	            logger.exception("[CHER] guard thread failed to set device")
1312	
1313	        hint_mq = getattr(self, "cloud_recv_hint_mq", None)
1314	
1315	        while not getattr(self, "_early_recv_guard_shutdown", False):
1316	            posted = False
1317	            # [CHER] Post any new recv-hints that arrived on the sideband MQ.
1318	            # Non-blocking: post only, never wait here (see docstring).
1319	            if hint_mq is not None:
1320	                while True:
1321	                    try:
1322	                        method, args, _kwargs, _output_rank = (
1323	                            hint_mq.dequeue(timeout=0)
1324	                        )
1325	                    except TimeoutError:
1326	                        break
1327	                    except Exception:
1328	                        # Anything other than TimeoutError (e.g. a torn-down
1329	                        # MQ at shutdown) -> stop draining this round.
1330	                        log
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:37:13</sup>


---

## Assistant <sup>2026/8/16 15:37:14</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"class AscendWorkerProc\\|_init_message_queues\\|cloud_recv_hint_mq\\|_CLOUD_RECV_HINT_MQ_ENV\\|_cloud_pd_enabled\" vllm_ascend/patch/platform/patch_multiproc_executor.py",
  "description": "Map MQ rebuild structure in ascend patch"
}
```

</details>


---

## User <sup>2026/8/16 15:37:14</sup>

<details>
<summary>Tool Result</summary>

```
27:# cloud_recv_hint_mq, so the cloud worker process (spawned by
31:_CLOUD_RECV_HINT_MQ_ENV = "VLLM_ASCEND_CLOUD_RECV_HINT_MQ_HANDLE"
34:def _cloud_pd_enabled(vllm_config: VllmConfig) -> bool:
126:        self.cloud_recv_hint_mq: MessageQueue | None = None
130:            and _cloud_pd_enabled(self.vllm_config)
140:            self.cloud_recv_hint_mq = MessageQueue(
143:            _hint_handle = self.cloud_recv_hint_mq.export_handle()
144:            os.environ[_CLOUD_RECV_HINT_MQ_ENV] = base64.b64encode(
148:                "[CHER] cloud_recv_hint_mq created on cloud executor "
153:            os.environ.pop(_CLOUD_RECV_HINT_MQ_ENV, None)
232:            # [CHER] cloud_recv_hint_mq is a fire-and-forget hint channel
235:            # _init_message_queues, which runs after distributed init; the
320:class AscendWorkerProc(WorkerProc):
321:    def _init_message_queues(
356:            super()._init_message_queues(input_shm_handle, vllm_config)
357:        # cloud_recv_hint_mq is rebuilt 
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:37:16</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "limit": 100,
  "offset": 320
}
```

</details>


---

## User <sup>2026/8/16 15:37:16</sup>

<details>
<summary>Tool Result</summary>

```
320	class AscendWorkerProc(WorkerProc):
321	    def _init_message_queues(
322	        self, input_shm_handle: Handle, vllm_config: VllmConfig
323	    ) -> None:
324	        if vllm_config.parallel_config.nnodes_within_dp == 1:
325	            # Single-node: use local MQ
326	            self.rpc_broadcast_mq = MessageQueue.create_from_handle(
327	                input_shm_handle, self.worker.rank
328	            )
329	            self.worker_response_mq = MessageQueue(1, 1)
330	            self.peer_response_handles = []
331	            self.local_rpc_broadcast_mq = None
332	            self.local_worker_response_mq = None
333	        elif envs.VLLM_PP_NON_LEADER_ENGINE_CORE:
334	            # Non-leader PP rank with passive EngineCore:
335	            # Dual MQ — local MQ for passive enginecore handshake +
336	            # cross-node MQ for actual communication with pp rank0.
337	            from vllm.distributed.parallel_state import get_inner_dp_world_group
338	            # Local M
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/16 15:37:20</sup>


---

## Assistant <sup>2026/8/16 15:37:20</sup>

实现 executor 侧 MQ 创建:


---

## Assistant <sup>2026/8/16 15:37:24</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "old_string": "        else:\n            # Clean any stale handle so a non-cloud worker does not pick it up.\n            os.environ.pop(_CLOUD_RECV_HINT_MQ_ENV, None)",
  "new_string": "        else:\n            # Clean any stale handle so a non-cloud worker does not pick it up.\n            os.environ.pop(_CLOUD_RECV_HINT_MQ_ENV, None)\n\n        # [EHER-draft] Edge-side draft-recv readiness sideband: the edge TP0\n        # worker posts the DDL return irecv at DDF time (see\n        # Worker._post_draft_return_irecv) and a report thread probes the\n        # recorded NPU event, publishing \"recv ready\" head_tokens here.  The\n        # EngineCore (this process) drains them next to _drain_pd_channel\n        # _inbox and the PDSeparatedScheduler gates its DDL dispatch on the\n        # ack instead of a fixed delay.  Dedicated MQ (not rpc_broadcast_mq\n        # / response_mq) for the same reason as cloud_recv_hint_mq:\n        # busy_loop and the batch_queue future collect must not be on this\n        # path.  64 slots x 1KB: at most a handful of DDL recvs are ever in\n        # flight; the ring absorbs EngineCore scheduling latency.\n        self.edge_recv_ready_mq: MessageQueue | None = None\n        if (\n            self.parallel_config.enable_edge_cloud\n            and self.parallel_config.is_edge_node\n            and _cloud_pd_enabled(self.vllm_config)\n        ):\n            self.edge_recv_ready_mq = MessageQueue(\n                1, 1, max_chunk_bytes=1024, max_chunks=64,\n            )\n            _ready_handle = self.edge_recv_ready_mq.export_handle()\n            os.environ[_EDGE_RECV_READY_MQ_ENV] = base64.b64encode(\n                pickle.dumps(_ready_handle)\n            ).decode()\n            logger.info(\n                \"[EHER-draft] edge_recv_ready_mq created on edge executor \"\n                \"(
...(truncated)
```

</details>


---

## User <sup>2026/8/16 15:37:25</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:37:28</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "old_string": "_CLOUD_RECV_HINT_MQ_ENV = \"VLLM_ASCEND_CLOUD_RECV_HINT_MQ_HANDLE\"",
  "new_string": "_CLOUD_RECV_HINT_MQ_ENV = \"VLLM_ASCEND_CLOUD_RECV_HINT_MQ_HANDLE\"\n# [EHER-draft] Edge-side DDL recv readiness ack channel (worker -> EngineCore).\n_EDGE_RECV_READY_MQ_ENV = \"VLLM_ASCEND_EDGE_RECV_READY_MQ_HANDLE\""
}
```

</details>


---

## User <sup>2026/8/16 15:37:29</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:37:31</sup>

Worker 进程侧重建(扩展 `_cher_init_message_queues`):


---

## Assistant <sup>2026/8/16 15:37:38</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "old_string": "def _cher_init_message_queues(self, input_shm_handle, vllm_config):\n    _orig_init_message_queues(self, input_shm_handle, vllm_config)\n    # Only rebuild if not already done by AscendWorkerProc._init_message_queues.\n    if getattr(self, \"cloud_recv_hint_mq\", None) is not None:\n        return\n    self.cloud_recv_hint_mq = None\n    if not (\n        envs.VLLM_PP_NON_LEADER_ENGINE_CORE\n        and self.local_rank == 0\n        and not vllm_config.parallel_config.is_edge_node\n        and _cloud_pd_enabled(vllm_config)\n    ):\n        return\n    _raw = os.environ.get(_CLOUD_RECV_HINT_MQ_ENV)\n    if _raw is None:\n        return\n    try:\n        _handle = pickle.loads(base64.b64decode(_raw))\n        self.cloud_recv_hint_mq = MessageQueue.create_from_handle(\n            _handle, self.local_rank\n        )\n        logger.info(\n            \"[CHER] cloud_recv_hint_mq rebuilt on worker local_rank=%d\",\n            self.local_rank,\n        )\n    except Exception:\n        logger.exception(\n            \"[CHER] failed to rebuild cloud_recv_hint_mq on worker \"\n            \"local_rank=%d; CHER will fall back to sync recv\",\n            self.local_rank,\n        )\n        self.cloud_recv_hint_mq = None",
  "new_string": "def _cher_init_message_queues(self, input_shm_handle, vllm_config):\n    _orig_init_message_queues(self, input_shm_handle, vllm_config)\n    # Only rebuild if not already done by AscendWorkerProc._init_message_queues.\n    if getattr(self, \"cloud_recv_hint_mq\", None) is not None:\n        return\n    self.cloud_recv_hint_mq = None\n    if not (\n        envs.VLLM_PP_NON_LEADER_ENGINE_CORE\n        and self.local_rank == 0\n        and not vllm_config.parallel_config.is_edge_node\n        and _cloud_pd_enabled(vllm_config)\n    ):\n        return\n    _raw = os.environ.get(_CLOUD_REC
...(truncated)
```

</details>


---

## User <sup>2026/8/16 15:37:39</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:37:44</sup>


---

## Assistant <sup>2026/8/16 15:37:46</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "old_string": "def _eher_init_edge_recv_ready_mq(self):\n    \"\"\"[EHER-draft] Rebuild edge_recv_ready_mq on the edge TP0 worker.\n\n    Runs after every _init_message_queues pass (the wrapper below chains\n    it); idempotent and side-effect free on non-qualifying workers so it\n    does not interfere with the CHER rebuild order above.\n    \"\"\"\n    self.edge_recv_ready_mq: MessageQueue | None = None\n    if not (\n        self.local_rank == 0\n        and getattr(\n            getattr(self, \"vllm_config\", None), \"parallel_config\", None\n        ) is not None\n        and self.vllm_config.parallel_config.is_edge_node\n    ):\n        return\n    _raw = os.environ.get(_EDGE_RECV_READY_MQ_ENV)",
  "new_string": "def _eher_init_edge_recv_ready_mq(self, vllm_config):\n    \"\"\"[EHER-draft] Rebuild edge_recv_ready_mq on the edge TP0 worker.\n\n    Runs after every _init_message_queues pass (the wrapper below chains\n    it); idempotent and side-effect free on non-qualifying workers so it\n    does not interfere with the CHER rebuild order above.\n    \"\"\"\n    self.edge_recv_ready_mq: MessageQueue | None = None\n    if not (\n        self.local_rank == 0\n        and vllm_config.parallel_config.is_edge_node\n    ):\n        return\n    _raw = os.environ.get(_EDGE_RECV_READY_MQ_ENV)"
}
```

</details>


---

## User <sup>2026/8/16 15:37:47</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:37:51</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "old_string": "def _cher_init_message_queues(self, input_shm_handle, vllm_config):\n    _orig_init_message_queues(self, input_shm_handle, vllm_config)\n    # Only rebuild if not already done by AscendWorkerProc._init_message_queues.\n    if getattr(self, \"cloud_recv_hint_mq\", None) is not None:\n        return",
  "new_string": "def _cher_init_message_queues(self, input_shm_handle, vllm_config):\n    _orig_init_message_queues(self, input_shm_handle, vllm_config)\n    # [EHER-draft] Chain the edge readiness-MQ rebuild (no-op on cloud /\n    # non-rank0 workers, so the CHER early-return below is unaffected).\n    _eher_init_edge_recv_ready_mq(self, vllm_config)\n    # Only rebuild if not already done by AscendWorkerProc._init_message_queues.\n    if getattr(self, \"cloud_recv_hint_mq\", None) is not None:\n        return"
}
```

</details>


---

## User <sup>2026/8/16 15:37:52</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:37:56</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "old_string": "        # cloud_recv_hint_mq is rebuilt by the base-class wrapper\n        # (_cher_init_message_queues applied below) which runs for plain\n        # WorkerProc instances that worker_main actually creates.  Initialize\n        # the attribute here for the AscendWorkerProc path (if ever taken).\n        self.cloud_recv_hint_mq: MessageQueue | None = None",
  "new_string": "        # cloud_recv_hint_mq is rebuilt by the base-class wrapper\n        # (_cher_init_message_queues applied below) which runs for plain\n        # WorkerProc instances that worker_main actually creates.  Initialize\n        # the attribute here for the AscendWorkerProc path (if ever taken).\n        self.cloud_recv_hint_mq: MessageQueue | None = None\n        self.edge_recv_ready_mq: MessageQueue | None = None"
}
```

</details>


---

## User <sup>2026/8/16 15:37:57</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:38:03</sup>


---

## Assistant <sup>2026/8/16 15:38:04</sup>

现在 vllm-pdmix 侧：报告线程启动钩子 + 线程实现：


---

## Assistant <sup>2026/8/16 15:38:07</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\executor\\multiproc_executor.py",
  "old_string": "        if getattr(self, \"cloud_recv_hint_mq\", None) is not None:\n            self._start_early_recv_guard()",
  "new_string": "        if getattr(self, \"cloud_recv_hint_mq\", None) is not None:\n            self._start_early_recv_guard()\n\n        # [EHER-draft] Edge-side draft-recv readiness reporting: when this\n        # edge worker (TP0 by construction - the MQ is only rebuilt on\n        # local_rank==0 and only the PP-NPU0 rank posts draft recvs) owns\n        # edge_recv_ready_mq, start the readiness report thread.  busy_loop\n        # blocks inside execute_model for whole batch durations and inside\n        # dequeue(0.1) when idle, so the report thread (not busy_loop) owns\n        # the probe: it polls the cached entries' NPU events and publishes\n        # ready head_tokens so the scheduler can dispatch the matching DDL\n        # the moment the transfer lands.  query() only - never wait(): the\n        # HCCL cross-thread constraint from the CHER guard applies here too.\n        if getattr(self, \"edge_recv_ready_mq\", None) is not None:\n            self._start_draft_ready_report()"
}
```

</details>


---

## User <sup>2026/8/16 15:38:08</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-pdmix\vllm\v1\executor\multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:38:17</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\executor\\multiproc_executor.py",
  "old_string": "            if not posted:\n                time.sleep(0.0001)\n\n    @staticmethod\n    def setup_proc_title_and_log_prefix(enable_ep: bool) -> None:",
  "new_string": "            if not posted:\n                time.sleep(0.0001)\n\n    # ------------------------------------------------------------------ #\n    # [EHER-draft] Edge-side draft-recv readiness report thread.         #\n    # ------------------------------------------------------------------ #\n    def _start_draft_ready_report(self) -> None:\n        \"\"\"Start the DDL recv readiness report thread (edge TP0 only).\n\n        The worker posts the DDL return irecv at DDF time and caches the\n        AsyncIntermediateTensors by head_token; this thread probes each\n        cached entry's ``__comm_event__`` (``event.query()``, non-blocking)\n        and publishes head_tokens whose transfer has completed onto the\n        sideband ``edge_recv_ready_mq``.  The EngineCore drains them next\n        to the POST_OUT inbox and the PDSeparatedScheduler gates its DDL\n        dispatch on the ack.\n        \"\"\"\n        if getattr(self, \"_draft_ready_report_started\", False):\n            return\n        worker = getattr(self, \"worker\", None)\n        if worker is None or not hasattr(worker, \"_draft_recv_cache\"):\n            return\n        self._draft_ready_report_started = True\n        self._draft_ready_report_shutdown = False\n        self._draft_ready_report_thread = threading.Thread(\n            target=self._draft_ready_report_loop,\n            name=\"eher-draft-ready-report\",\n            daemon=True,\n        )\n        self._draft_ready_report_thread.start()\n        logger.info(\"[EHER-draft] readiness report thread started\")\n\n    def _draft_ready_report_loop(self) -> None:\n        \"\"\"Probe cached draft recvs and ack the ready ones (query only).\n\n        
...(truncated)
```

</details>


---

## User <sup>2026/8/16 15:38:18</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-pdmix\vllm\v1\executor\multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/16 15:38:21</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "python -m py_compile ../vllm-pdmix/vllm/v1/executor/multiproc_executor.py vllm_ascend/patch/platform/patch_multiproc_executor.py && echo SYNTAX_OK",
  "description": "Compile-check executor files"
}
```

</details>


---

## User <sup>2026/8/16 15:40:47</sup>

<details>
<summary>Tool Result</summary>

```
Tool permission request failed: AbortError: Tool permission stream closed before response received
```

</details>


---

## Assistant <sup>2026/8/17 08:56:48</sup>

No response requested.


---

## User <sup>2026/8/17 08:57:02</sup>

继续


---

## Assistant <sup>2026/8/17 08:57:06</sup>


---

## Assistant <sup>2026/8/17 08:57:06</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "python -m py_compile ../vllm-pdmix/vllm/v1/executor/multiproc_executor.py vllm_ascend/patch/platform/patch_multiproc_executor.py && echo SYNTAX_OK",
  "description": "Compile-check executor files"
}
```

</details>


---

## User <sup>2026/8/17 08:57:15</sup>

<details>
<summary>Tool Result</summary>

```
Exit code 1
[Errno 2] No such file or directory: '../vllm-pdmix/vllm/v1/executor/multiproc_executor.py'
```

</details>


---

## Assistant <sup>2026/8/17 08:57:18</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "python -m py_compile c:/kisella_mtp/vllm-pdmix/vllm/v1/executor/multiproc_executor.py c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_multiproc_executor.py && echo SYNTAX_OK",
  "description": "Compile-check executor files with absolute paths"
}
```

</details>


---

## User <sup>2026/8/17 08:57:21</sup>

<details>
<summary>Tool Result</summary>

```
SYNTAX_OK
```

</details>


---

## Assistant <sup>2026/8/17 08:57:39</sup>


---

## Assistant <sup>2026/8/17 08:57:39</sup>

EngineCore 侧 drain。先确认 MessageQueue 创建实例本身能否直接作为 reader:


---

## Assistant <sup>2026/8/17 08:57:39</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -rn \"class MessageQueue\" c:/kisella_mtp/vllm-pdmix/vllm/ | head -3",
  "description": "Locate MessageQueue class"
}
```

</details>


---

## User <sup>2026/8/17 08:57:40</sup>

<details>
<summary>Tool Result</summary>

```
c:/kisella_mtp/vllm-pdmix/vllm/distributed/device_communicators/shm_broadcast.py:367:class MessageQueue:
```

</details>


---

## Assistant <sup>2026/8/17 08:57:43</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\distributed\\device_communicators\\shm_broadcast.py",
  "limit": 120,
  "offset": 367
}
```

</details>


---

## User <sup>2026/8/17 08:57:43</sup>

<details>
<summary>Tool Result</summary>

```
367	class MessageQueue:
368	    def __init__(
369	        self,
370	        n_reader,  # number of all readers
371	        n_local_reader,  # number of local readers through shared memory
372	        local_reader_ranks: list[int] | None = None,
373	        # Default of 24MiB chosen to be large enough to accommodate grammar
374	        # bitmask tensors for large batches (1024 requests).
375	        max_chunk_bytes: int = 1024 * 1024 * 24,
376	        max_chunks: int = 10,
377	        connect_ip: str | None = None,
378	    ):
379	        if local_reader_ranks is None:
380	            local_reader_ranks = list(range(n_local_reader))
381	        else:
382	            assert len(local_reader_ranks) == n_local_reader
383	        self.n_local_reader = n_local_reader
384	        n_remote_reader = n_reader - n_local_reader
385	        self.n_remote_reader = n_remote_reader
386	        self.shutting_down = False
387	        context = Context()
388	
389	        if n_local_reader > 0:
390	       
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 08:58:17</sup>


---

## Assistant <sup>2026/8/17 08:58:17</sup>

MQ 方向问题：writer 必须在 worker 进程。看 WorkerProc 就绪握手如何把 MQ handle 传回父进程：


---

## Assistant <sup>2026/8/17 08:58:18</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"peer_response_handles\\|export_handle\\|ready_pipe\\|def init_worker\\|handles = \\|handles\\[\" c:/kisella_mtp/vllm-pdmix/vllm/v1/executor/multiproc_executor.py | sed -n 1,40p",
  "description": "Find handle handshake in multiproc executor"
}
```

</details>


---

## User <sup>2026/8/17 08:58:19</sup>

<details>
<summary>Tool Result</summary>

```
158:            scheduler_output_handle = self.rpc_broadcast_mq.export_handle()
184:            scheduler_output_handle = self.rpc_broadcast_mq.export_handle()
229:                    inherited_fds.append(unready_worker_handle.ready_pipe.fileno())
622:    ready_pipe: Connection
672:            self.peer_response_handles = []
684:            self.local_peer_response_handles: list = []
690:            self.worker_response_mq, self.peer_response_handles = (
707:            # driver worker, exposing peer_response_handles for driver worker
709:            self.worker_response_mq, self.peer_response_handles = (
832:            "ready_pipe": ready_writer,
864:        response_handle = handles["handle"]
868:        peer_response_handles = handles["peer_response_handles"]
873:            for handle in peer_response_handles
890:        pipes = {handle.ready_pipe: handle for handle in unready_proc_handles}
906:                    ready_proc_handles[idx] = WorkerProc.wait_for_response_handle_ready
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 08:58:22</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-pdmix\\vllm\\v1\\executor\\multiproc_executor.py",
  "limit": 70,
  "offset": 985
}
```

</details>


---

## User <sup>2026/8/17 08:58:22</sup>

<details>
<summary>Tool Result</summary>

```
985	        # Either SIGTERM or SIGINT will terminate the worker
986	        signal.signal(signal.SIGTERM, signal_handler)
987	        signal.signal(signal.SIGINT, signal_handler)
988	
989	        # Set net device env vars for the worker if VLLM_GPU_NIC_PCIE_MAPPING is set
990	        set_worker_net_device(kwargs.get("local_rank", 0), kwargs["vllm_config"])
991	
992	        worker = None
993	        ready_writer = kwargs.pop("ready_pipe")
994	        death_pipe = kwargs.pop("death_pipe", None)
995	
996	        # Close inherited pipes from parent (incl. other worker pipes)
997	        # Explicitly passing in existing pipes and closing them makes the pipe
998	        # behave when using fork. Otherwise, a hidden reference to the pipes
999	        # exist in the child process and prevents EOF closure.
1000	        for fd in kwargs.pop("inherited_fds", []):
1001	            try:
1002	                os.close(fd)
1003	            except Exception as e:
1004	                logger.warning("E
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 08:59:05</sup>


---

## Assistant <sup>2026/8/17 08:59:06</sup>

MQ writer 必须在 worker 进程(与 CHER 方向相反)。查 `enqueue` 是否强制 writer 实例:


---

## Assistant <sup>2026/8/17 08:59:06</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"_is_writer\\|def enqueue\\|def dequeue\" c:/kisella_mtp/vllm-pdmix/vllm/distributed/device_communicators/shm_broadcast.py | sed -n 1,25p",
  "description": "Check writer enforcement in MessageQueue"
}
```

</details>


---

## User <sup>2026/8/17 08:59:07</sup>

<details>
<summary>Tool Result</summary>

```
442:        self._is_writer = True
466:        self._is_writer = False
514:        if self._is_writer:
552:        assert self._is_writer, "Only writers can acquire write"
729:    def enqueue(
742:        assert self._is_writer, "Only writers can enqueue"
785:    def dequeue(
821:        if self._is_writer:
```

</details>


---

## Assistant <sup>2026/8/17 08:59:14</sup>


---

## Assistant <sup>2026/8/17 08:59:15</sup>

确认：只有创建实例可 enqueue。改为 worker 侧创建 + 文件交换 handle。先看 executor init 末尾(workers ready 之后的位置)：


---

## Assistant <sup>2026/8/17 08:59:15</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "limit": 75,
  "offset": 210
}
```

</details>


---

## User <sup>2026/8/17 08:59:15</sup>

<details>
<summary>Tool Result</summary>

```
210	                unready_worker_handle = AscendWorkerProc.make_worker_process(
211	                    vllm_config=self.vllm_config,
212	                    local_rank=local_rank,
213	                    rank=global_rank,
214	                    distributed_init_method=distributed_init_method,
215	                    input_shm_handle=scheduler_output_handle,
216	                    shared_worker_lock=shared_worker_lock,
217	                    is_driver_worker=is_driver_worker,
218	                    inherited_fds=inherited_fds,
219	                )
220	                unready_workers.append(unready_worker_handle)
221	                if inherited_fds is not None:
222	                    inherited_fds.append(unready_worker_handle.death_writer.fileno())
223	                    inherited_fds.append(unready_worker_handle.ready_pipe.fileno())
224	
225	            # Workers must be created before wait_for_ready to avoid
226	            # deadlock, since worker.init_device() does a devic
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 08:59:27</sup>


---

## Assistant <sup>2026/8/17 08:59:27</sup>

改写 executor 侧：删除创建、改为 workers ready 后读 handle 文件:


---

## Assistant <sup>2026/8/17 08:59:34</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "old_string": "        else:\n            # Clean any stale handle so a non-cloud worker does not pick it up.\n            os.environ.pop(_CLOUD_RECV_HINT_MQ_ENV, None)\n\n        # [EHER-draft] Edge-side draft-recv readiness sideband: the edge TP0\n        # worker posts the DDL return irecv at DDF time (see\n        # Worker._post_draft_return_irecv) and a report thread probes the\n        # recorded NPU event, publishing \"recv ready\" head_tokens here.  The\n        # EngineCore (this process) drains them next to _drain_pd_channel\n        # _inbox and the PDSeparatedScheduler gates its DDL dispatch on the\n        # ack instead of a fixed delay.  Dedicated MQ (not rpc_broadcast_mq\n        # / response_mq) for the same reason as cloud_recv_hint_mq:\n        # busy_loop and the batch_queue future collect must not be on this\n        # path.  64 slots x 1KB: at most a handful of DDL recvs are ever in\n        # flight; the ring absorbs EngineCore scheduling latency.\n        self.edge_recv_ready_mq: MessageQueue | None = None\n        if (\n            self.parallel_config.enable_edge_cloud\n            and self.parallel_config.is_edge_node\n            and _cloud_pd_enabled(self.vllm_config)\n        ):\n            self.edge_recv_ready_mq = MessageQueue(\n                1, 1, max_chunk_bytes=1024, max_chunks=64,\n            )\n            _ready_handle = self.edge_recv_ready_mq.export_handle()\n            os.environ[_EDGE_RECV_READY_MQ_ENV] = base64.b64encode(\n                pickle.dumps(_ready_handle)\n            ).decode()\n            logger.info(\n                \"[EHER-draft] edge_recv_ready_mq created on edge executor \"\n                \"(local_world_size=%d)\", self.local_world_size,\n            )\n        else:\n            os.environ.pop(_EDGE_RECV_READY_MQ_ENV, None)",
  "new_string": "        else:\n   
...(truncated)
```

</details>


---

## User <sup>2026/8/17 09:00:06</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:00:11</sup>


---

## Assistant <sup>2026/8/17 09:00:11</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "old_string": "        # must not be on this path.\n        self.edge_recv_ready_mq: MessageQueue | None = None\n        _is_edge_pd = (\n            self.parallel_config.enable_edge_cloud\n            and self.parallel_config.is_edge_node\n            and _cloud_pd_enabled(self.vllm_config)\n        )",
  "new_string": "        # must not be on this path.\n        self.edge_recv_ready_mq: MessageQueue | None = None"
}
```

</details>


---

## User <sup>2026/8/17 09:00:12</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:00:16</sup>

Worker 侧 `_eher_init_edge_recv_ready_mq` 改为创建者(writer)并写 handle 文件:


---

## Assistant <sup>2026/8/17 09:00:25</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "old_string": "def _eher_init_edge_recv_ready_mq(self, vllm_config):\n    \"\"\"[EHER-draft] Rebuild edge_recv_ready_mq on the edge TP0 worker.\n\n    Runs after every _init_message_queues pass (the wrapper below chains\n    it); idempotent and side-effect free on non-qualifying workers so it\n    does not interfere with the CHER rebuild order above.\n    \"\"\"\n    self.edge_recv_ready_mq: MessageQueue | None = None\n    if not (\n        self.local_rank == 0\n        and vllm_config.parallel_config.is_edge_node\n    ):\n        return\n    _raw = os.environ.get(_EDGE_RECV_READY_MQ_ENV)\n    if _raw is None:\n        return\n    try:\n        _handle = pickle.loads(base64.b64decode(_raw))\n        self.edge_recv_ready_mq = MessageQueue.create_from_handle(\n            _handle, self.local_rank\n        )\n        logger.info(\n            \"[EHER-draft] edge_recv_ready_mq rebuilt on worker \"\n            \"local_rank=%d\", self.local_rank,\n        )\n    except Exception:\n        logger.exception(\n            \"[EHER-draft] failed to rebuild edge_recv_ready_mq on \"\n            \"worker local_rank=%d; readiness acks disabled (scheduler \"\n            \"falls back to the delay gate)\", self.local_rank,\n        )\n        self.edge_recv_ready_mq = None",
  "new_string": "def _eher_ready_handle_path(vllm_config) -> str:\n    \"\"\"Node-local file the edge TP0 worker exports its MQ handle through.\n\n    Keyed on master_port + dp_rank so concurrent deployments on one host do\n    not collide; the parent (EngineCore's executor) reads it after the\n    workers are ready and then removes it.\n    \"\"\"\n    import tempfile\n    pc = vllm_config.parallel_config\n    dp_rank = getattr(pc, \"data_parallel_rank\", 0)\n    return os.path.join(\n        tempfile.gettempdir(),\n        f\"vllm_eher_ready_{pc.master_port}_{dp_rank}.ha
...(truncated)
```

</details>


---

## User <sup>2026/8/17 09:00:26</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:00:31</sup>


---

## Assistant <sup>2026/8/17 09:00:32</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"^class \\|    def \\|_EDGE_RECV_READY_MQ_ENV\" c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_multiproc_executor.py | head -30",
  "description": "Map class structure of patch file"
}
```

</details>


---

## User <sup>2026/8/17 09:00:33</sup>

<details>
<summary>Tool Result</summary>

```
33:_EDGE_RECV_READY_MQ_ENV = "VLLM_ASCEND_EDGE_RECV_READY_MQ_HANDLE"
65:class AscendMultiprocExecutor(MultiprocExecutor):
66:    def _init_executor(self) -> None:
281:    def _get_parallel_sizes(self) -> tuple[int, int, int]:
295:    def _post_init_executor(self) -> None:
298:    def _is_driver_worker(self, rank: int) -> bool:
307:    def _get_output_rank(self) -> int:
312:    def _edge_local_only(self) -> bool:
319:    def clear_pending_edge_cloud_draft_for_req_ids(
337:class AscendWorkerProc(WorkerProc):
338:    def _init_message_queues(
382:    def make_worker_process(
```

</details>


---

## Assistant <sup>2026/8/17 09:00:39</sup>


---

## Assistant <sup>2026/8/17 09:00:40</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "old_string": "_CLOUD_RECV_HINT_MQ_ENV = \"VLLM_ASCEND_CLOUD_RECV_HINT_MQ_HANDLE\"\n# [EHER-draft] Edge-side DDL recv readiness ack channel (worker -> EngineCore).\n_EDGE_RECV_READY_MQ_ENV = \"VLLM_ASCEND_EDGE_RECV_READY_MQ_HANDLE\"",
  "new_string": "_CLOUD_RECV_HINT_MQ_ENV = \"VLLM_ASCEND_CLOUD_RECV_HINT_MQ_HANDLE\""
}
```

</details>


---

## User <sup>2026/8/17 09:00:41</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:00:45</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "old_string": "            # Wait for all local workers to be ready.\n            self.workers = AscendWorkerProc.wait_for_ready(unready_workers)",
  "new_string": "            # Wait for all local workers to be ready.\n            self.workers = AscendWorkerProc.wait_for_ready(unready_workers)\n\n            # [EHER-draft] Attach the EngineCore-side reader of the DDL\n            # recv-readiness sideband (written by the TP0 worker during\n            # _init_message_queues, i.e. before it signalled READY above).\n            self._eher_attach_edge_recv_ready_mq()"
}
```

</details>


---

## User <sup>2026/8/17 09:00:46</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:00:55</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "old_string": "    def _get_parallel_sizes(self) -> tuple[int, int, int]:",
  "new_string": "    def _eher_attach_edge_recv_ready_mq(self) -> None:\n        \"\"\"[EHER-draft] Create the reader side of edge_recv_ready_mq.\n\n        The edge TP0 worker created the MQ (writer) during\n        _init_message_queues and exported its handle to a node-local file;\n        by the time workers are READY that file exists.  Read it once\n        (short retry for robustness), build the reader instance, and\n        remove the file.  Failure is soft: the scheduler falls back to the\n        fixed DDL dispatch delay.\n        \"\"\"\n        if not (\n            self.parallel_config.enable_edge_cloud\n            and self.parallel_config.is_edge_node\n            and _cloud_pd_enabled(self.vllm_config)\n        ):\n            return\n        _path = _eher_ready_handle_path(self.vllm_config)\n        _raw = None\n        _deadline = time.monotonic() + 30.0\n        while _raw is None and time.monotonic() < _deadline:\n            try:\n                with open(_path, \"r\", encoding=\"utf-8\") as _f:\n                    _raw = _f.read().strip()\n            except FileNotFoundError:\n                time.sleep(0.05)\n        if not _raw:\n            logger.warning(\n                \"[EHER-draft] no ready-handle file at %s; readiness acks \"\n                \"disabled (scheduler falls back to the delay gate)\",\n                _path,\n            )\n            return\n        try:\n            _handle = pickle.loads(base64.b64decode(_raw))\n            self.edge_recv_ready_mq = MessageQueue.create_from_handle(\n                _handle, 0\n            )\n            os.remove(_path)\n            logger.info(\n                \"[EHER-draft] edge_recv_ready_mq reader attached on edge \"\n                \"executor\"\n            )\n     
...(truncated)
```

</details>


---

## User <sup>2026/8/17 09:00:56</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:00:58</sup>


---

## Assistant <sup>2026/8/17 09:00:58</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "head -25 c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_multiproc_executor.py; python -m py_compile c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_multiproc_executor.py && echo SYNTAX_OK",
  "description": "Check imports and compile"
}
```

</details>


---

## User <sup>2026/8/17 09:07:08</sup>

<details>
<summary>Tool Result</summary>

```
from __future__ import annotations

import base64
import os
import pickle
import weakref
from collections import deque
from collections.abc import Callable
from multiprocessing.synchronize import Lock as LockType

import vllm.v1.executor.multiproc_executor
from vllm import envs
from vllm.config import VllmConfig
from vllm.distributed.device_communicators.shm_broadcast import Handle, MessageQueue
from vllm.logger import logger
from vllm.utils.network_utils import get_distributed_init_method, get_loopback_ip, get_open_port
from vllm.utils.system_utils import get_mp_context
from vllm.v1.executor.abstract import FailureCallback
from vllm.v1.executor.multiproc_executor import (
    FutureWrapper,
    MultiprocExecutor,
    UnreadyWorkerProcHandle,
    WorkerProc,
    set_multiprocessing_worker_envs,
)
SYNTAX_OK
```

</details>


---

## Assistant <sup>2026/8/17 09:07:19</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_multiproc_executor.py",
  "old_string": "import base64\nimport os\nimport pickle\nimport weakref",
  "new_string": "import base64\nimport os\nimport pickle\nimport time\nimport weakref"
}
```

</details>


---

## User <sup>2026/8/17 09:07:20</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_multiproc_executor.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:07:23</sup>


---

## Assistant <sup>2026/8/17 09:07:24</sup>

现在 patch_engine_core.py:加 drain 方法并挂到两个 step 路径。先看末尾的绑定块：


---

## Assistant <sup>2026/8/17 09:07:24</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_engine_core.py",
  "limit": 40,
  "offset": 1090
}
```

</details>


---

## User <sup>2026/8/17 09:07:24</sup>

<details>
<summary>Tool Result</summary>

```
1090	        logger.debug("EngineCore loop active.")
1091	
1092	    # Handle any more client requests.
1093	    while not self.input_queue.empty():
1094	        req = self.input_queue.get_nowait()
1095	        self._handle_client_request(*req)
1096	
1097	
1098	# =======================================================================#
1099	# Install                                                                  #
1100	# =======================================================================#
1101	def install() -> None:
1102	    if getattr(EngineCore, _INSTALLED_FLAG, False):
1103	        return
1104	
1105	    EngineCore.__init__ = _patched_engine_core_init
1106	    EngineCore._drain_pd_channel_inbox = _drain_pd_channel_inbox
1107	    EngineCore._publish_to_cloud = _publish_to_cloud
1108	    EngineCore._maybe_publish_pre_out = _maybe_publish_pre_out
1109	    EngineCore._release_deferred_draft_pre_out = (
1110	        _release_deferred_draft_pre_out
1111	    )
1112	    EngineCore._close
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 09:07:29</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_engine_core.py",
  "old_string": "def _drain_pd_channel_inbox(self) -> None:\n    \"\"\"Move cloud-returned SchedulerOutputs into the local PDSeparated\n    scheduler's ``prefills_last_ready`` / ``decodes_last_ready`` queues.\n    \"\"\"",
  "new_string": "def _drain_pd_channel_inbox(self) -> None:"
}
```

</details>


---

## User <sup>2026/8/17 09:07:30</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_engine_core.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:07:33</sup>


---

## Assistant <sup>2026/8/17 09:07:33</sup>

误删了 docstring,恢复并正确插入新函数：


---

## Assistant <sup>2026/8/17 09:07:37</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_engine_core.py",
  "old_string": "def _drain_pd_channel_inbox(self) -> None:",
  "new_string": "def _drain_draft_recv_acks(self) -> None:\n    \"\"\"[EHER-draft] Drain DDL recv-readiness acks into the scheduler.\n\n    The edge TP0 worker's report thread publishes head_tokens whose DDL\n    return irecv has landed on the ``edge_recv_ready_mq`` sideband; hand\n    them to the scheduler's notify hook so its DDL pick gate can fire on\n    data-plane readiness instead of the fixed delay.  No-op (and no MQ\n    traffic) when the sideband was not attached.\n    \"\"\"\n    mq = getattr(\n        getattr(self, \"model_executor\", None), \"edge_recv_ready_mq\", None\n    )\n    if mq is None:\n        return\n    notify = getattr(self.scheduler, \"notify_draft_recv_ready\", None)\n    if notify is None:\n        return\n    while True:\n        try:\n            method, args, _kwargs, _output_rank = mq.dequeue(timeout=0)\n        except TimeoutError:\n            break\n        except Exception:\n            logger.exception(\"[EHER-draft] ack dequeue error\")\n            break\n        if method == b\"draft_recv_ready\" and args:\n            notify(args[0])\n\n\ndef _drain_pd_channel_inbox(self) -> None:\n    \"\"\"Move cloud-returned SchedulerOutputs into the local PDSeparated\n    scheduler's ``prefills_last_ready`` / ``decodes_last_ready`` queues.\n    \"\"\""
}
```

</details>


---

## User <sup>2026/8/17 09:07:38</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_engine_core.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:07:43</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_engine_core.py",
  "old_string": "    # [ascend insert] Drain POST_OUT (cloud -> edge) into the\n    # PDSeparatedScheduler's tail-segment ready queues before scheduling.\n    self._drain_pd_channel_inbox()\n\n    scheduler_output = self.scheduler.schedule()\n    self._ensure_pd_head_token(scheduler_output)\n\n    # [ascend insert] Merge worker cleanup stashed from EMPTY batches",
  "new_string": "    # [ascend insert] Drain POST_OUT (cloud -> edge) into the\n    # PDSeparatedScheduler's tail-segment ready queues before scheduling.\n    self._drain_pd_channel_inbox()\n    # [ascend insert] Drain DDL recv-readiness acks (worker -> scheduler)\n    # before scheduling so the DDL pick gate sees fresh events.\n    self._drain_draft_recv_acks()\n\n    scheduler_output = self.scheduler.schedule()\n    self._ensure_pd_head_token(scheduler_output)\n\n    # [ascend insert] Merge worker cleanup stashed from EMPTY batches"
}
```

</details>


---

## User <sup>2026/8/17 09:07:43</sup>

<details>
<summary>Tool Result</summary>

```
<tool_use_error>String to replace not found in file.
String:     # [ascend insert] Drain POST_OUT (cloud -> edge) into the
    # PDSeparatedScheduler's tail-segment ready queues before scheduling.
    self._drain_pd_channel_inbox()

    scheduler_output = self.scheduler.schedule()
    self._ensure_pd_head_token(scheduler_output)

    # [ascend insert] Merge worker cleanup stashed from EMPTY batches</tool_use_error>
```

</details>


---

## Assistant <sup>2026/8/17 09:07:47</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"_drain_pd_channel_inbox()\" c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py",
  "description": "Find drain call sites"
}
```

</details>


---

## User <sup>2026/8/17 09:07:48</sup>

<details>
<summary>Tool Result</summary>

```
780:    self._drain_pd_channel_inbox()
860:        self._drain_pd_channel_inbox()
```

</details>


---

## Assistant <sup>2026/8/17 09:07:50</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_engine_core.py",
  "limit": 14,
  "offset": 773
}
```

</details>


---

## User <sup>2026/8/17 09:07:50</sup>

<details>
<summary>Tool Result</summary>

```
773	    # Check for any requests remaining in the scheduler - unfinished,
774	    # or finished and not yet removed from the batch.
775	    if not self.scheduler.has_requests():
776	        return {}, False
777	
778	    # [ascend insert] Drain POST_OUT (cloud → edge) into the
779	    # PDSeparatedScheduler's tail-segment ready queues before scheduling.
780	    self._drain_pd_channel_inbox()
781	
782	    scheduler_output = self.scheduler.schedule()
783	    self._ensure_pd_head_token(scheduler_output)
784	
785	    # [ascend insert] Merge worker cleanup stashed from EMPTY batches
786	    # BEFORE publishing to the cloud, so the published SO also carries
```

</details>


---

## Assistant <sup>2026/8/17 09:07:56</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_engine_core.py",
  "old_string": "    # [ascend insert] Drain POST_OUT (cloud -> edge) into the\n    # PDSeparatedScheduler's tail-segment ready queues before scheduling.\n    self._drain_pd_channel_inbox()\n\n    scheduler_output = self.scheduler.schedule()\n    self._ensure_pd_head_token(scheduler_output)\n\n    # [ascend insert] Merge worker cleanup stashed from EMPTY batches",
  "new_string": "    # [ascend insert] Drain POST_OUT (cloud -> edge) into the\n    # PDSeparatedScheduler's tail-segment ready queues before scheduling.\n    self._drain_pd_channel_inbox()\n    # [ascend insert] Drain DDL recv-readiness acks (worker -> scheduler)\n    # so the DDL pick gate sees fresh events before scheduling.\n    self._drain_draft_recv_acks()\n\n    scheduler_output = self.scheduler.schedule()\n    self._ensure_pd_head_token(scheduler_output)\n\n    # [ascend insert] Merge worker cleanup stashed from EMPTY batches"
}
```

</details>


---

## User <sup>2026/8/17 09:07:56</sup>

<details>
<summary>Tool Result</summary>

```
<tool_use_error>String to replace not found in file.
String:     # [ascend insert] Drain POST_OUT (cloud -> edge) into the
    # PDSeparatedScheduler's tail-segment ready queues before scheduling.
    self._drain_pd_channel_inbox()

    scheduler_output = self.scheduler.schedule()
    self._ensure_pd_head_token(scheduler_output)

    # [ascend insert] Merge worker cleanup stashed from EMPTY batches</tool_use_error>
```

</details>


---

## Assistant <sup>2026/8/17 09:08:01</sup>


---

## Assistant <sup>2026/8/17 09:08:02</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_engine_core.py",
  "old_string": "    self._drain_pd_channel_inbox()\n\n    scheduler_output = self.scheduler.schedule()",
  "new_string": "    self._drain_pd_channel_inbox()\n    # [ascend insert] Drain DDL recv-readiness acks (worker -> scheduler)\n    # so the DDL pick gate sees fresh events before scheduling.\n    self._drain_draft_recv_acks()\n\n    scheduler_output = self.scheduler.schedule()"
}
```

</details>


---

## User <sup>2026/8/17 09:08:03</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_engine_core.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:08:06</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_engine_core.py",
  "old_string": "        self._drain_pd_channel_inbox()",
  "new_string": "        self._drain_pd_channel_inbox()\n        self._drain_draft_recv_acks()"
}
```

</details>


---

## User <sup>2026/8/17 09:08:07</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_engine_core.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:08:11</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\patch\\platform\\patch_engine_core.py",
  "old_string": "    EngineCore.__init__ = _patched_engine_core_init\n    EngineCore._drain_pd_channel_inbox = _drain_pd_channel_inbox",
  "new_string": "    EngineCore.__init__ = _patched_engine_core_init\n    EngineCore._drain_pd_channel_inbox = _drain_pd_channel_inbox\n    EngineCore._drain_draft_recv_acks = _drain_draft_recv_acks"
}
```

</details>


---

## User <sup>2026/8/17 09:08:12</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\patch\platform\patch_engine_core.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:08:15</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "python -m py_compile c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_multiproc_executor.py && echo SYNTAX_OK",
  "description": "Compile-check engine core and executor patches"
}
```

</details>


---

## User <sup>2026/8/17 09:09:44</sup>

<details>
<summary>Tool Result</summary>

```
SYNTAX_OK
```

</details>


---

## Assistant <sup>2026/8/17 09:09:49</sup>


---

## Assistant <sup>2026/8/17 09:09:49</sup>

P1-4 完成。进入 P1-5:调度器侧。读 DDL pick 与 delay 逻辑：


---

## Assistant <sup>2026/8/17 09:09:50</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 60,
  "offset": 1790
}
```

</details>


---

## User <sup>2026/8/17 09:09:50</sup>

<details>
<summary>Tool Result</summary>

```
1790	    def _start_decode_draft_last_delay(self) -> None:
1791	        """decode_draft首 pick 后启动，decode_draft尾 在延迟到期前不可调度。
1792	
1793	        解码域尾由边侧自生成，保留 5ms（默认）延迟 pacing。
1794	        """
1795	        self._decode_draft_last_delay_start_ts = time.monotonic()
1796	
1797	    def _can_schedule_decode_draft_last(self) -> bool:
1798	        """Return True if the delay since DECODE_DRAFT_FIRST has elapsed."""
1799	        if self._decode_draft_last_delay_start_ts is None:
1800	            return True
1801	        elapsed_ms = (
1802	            time.monotonic() - self._decode_draft_last_delay_start_ts
1803	        ) * 1000
1804	        if elapsed_ms >= self._decode_draft_last_delay_schedule_ms:
1805	            self._decode_draft_last_delay_start_ts = None
1806	            return True
1807	        return False
1808	
1809	    def _can_schedule_prefill_draft_last(self) -> bool:
1810	        """Return True if the prefill draft tail is schedulable.
1811	
1812	        Phase C（设计 §6.2）：PDFL 由云
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 09:09:52</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 85,
  "offset": 2729
}
```

</details>


---

## User <sup>2026/8/17 09:09:52</sup>

<details>
<summary>Tool Result</summary>

```
2729	        """Pick one DECODE_DRAFT_LAST from the decode-draft domain.
2730	
2731	        边侧自生成 + 5ms 默认延迟调度（设计 §6.2）。
2732	        """
2733	        return self._pick_draft_last_batch_by_kind("decode")
2734	
2735	    def _pick_draft_last_batch_by_kind(self, kind: str) -> SchedulerOutput:
2736	        if kind == "prefill":
2737	            ready_queue = self.prefill_drafts_last_ready
2738	            last_type = BatchType.PREFILL_DRAFT_LAST
2739	        else:
2740	            ready_queue = self.decode_drafts_last_ready
2741	            last_type = BatchType.DECODE_DRAFT_LAST
2742	        while ready_queue:
2743	            scheduler_output = ready_queue.popleft()
2744	            if scheduler_output.batch_type != last_type:
2745	                raise RuntimeError(
2746	                    f"{kind}_drafts_last_ready expects {last_type}, got "
2747	                    f"{scheduler_output.batch_type}"
2748	                )
2749	            if kind == "prefill":
2750	                self
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 09:09:56</sup>


---

## Assistant <sup>2026/8/17 09:09:57</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"_can_schedule_decode_draft_last\\|_decode_draft_last_delay_schedule_ms\\|_decode_draft_last_delay_start_ts\" c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py; echo ---; grep -n \"class PDSeparationConfig\\|draft\" c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/pd_separation_config.py | head -30",
  "description": "Find delay gate callers and config class"
}
```

</details>


---

## User <sup>2026/8/17 09:09:58</sup>

<details>
<summary>Tool Result</summary>

```
563:        self._decode_draft_last_delay_start_ts: float | None = None
564:        self._decode_draft_last_delay_schedule_ms: int = 15
1383:                and self._can_schedule_decode_draft_last()
1434:                and self._can_schedule_decode_draft_last()
1468:            and self._can_schedule_decode_draft_last()
1704:                  "_decode_draft_last_delay_schedule_ms")),
1725:                 "_decode_draft_last_delay_schedule_ms"),
1795:        self._decode_draft_last_delay_start_ts = time.monotonic()
1797:    def _can_schedule_decode_draft_last(self) -> bool:
1799:        if self._decode_draft_last_delay_start_ts is None:
1802:            time.monotonic() - self._decode_draft_last_delay_start_ts
1804:        if elapsed_ms >= self._decode_draft_last_delay_schedule_ms:
1805:            self._decode_draft_last_delay_start_ts = None
---
30:class PDSeparationConfig:
```

</details>


---

## Assistant <sup>2026/8/17 09:10:02</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 45,
  "offset": 1690
}
```

</details>


---

## User <sup>2026/8/17 09:10:02</sup>

<details>
<summary>Tool Result</summary>

```
1690	                        "[PDSeparatedScheduler] %s set to %d from %s",
1691	                        _key, self._decode_last_delay_schedule_ms, yaml_path,
1692	                    )
1693	                except (ValueError, TypeError):
1694	                    logger.warning(
1695	                        "Invalid %s value %r in %s; keeping %d",
1696	                        _key, raw[_key], yaml_path,
1697	                        self._decode_last_delay_schedule_ms,
1698	                    )
1699	            # 4 域拆分（设计 §6.2）：旧键 draft_last_delay_schedule_ms 作为
1700	            # 兼容别名同时设置两个新值；新键逐个覆盖。
1701	            for _key, _attr in (
1702	                ("draft_last_delay_schedule_ms",
1703	                 ("_prefill_draft_last_delay_schedule_ms",
1704	                  "_decode_draft_last_delay_schedule_ms")),
1705	            ):
1706	                if _key in raw:
1707	                    try:
1708	                        _value = int(raw[_key])
1709	                        f
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 09:10:27</sup>


---

## Assistant <sup>2026/8/17 09:10:28</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 30,
  "offset": 550
}
```

</details>


---

## User <sup>2026/8/17 09:10:28</sup>

<details>
<summary>Tool Result</summary>

```
550	            prefill_draft_first_only_window_ms=15,
551	            prefill_first_only_enabled=(
552	                self._uses_async_scheduled_mtp_placeholders()
553	            ),
554	        )
555	
556	        self._layer_slice_config_path: str | None = None
557	        self._layer_slice_config_mtime: float = 0.0
558	        self._load_layer_slice_config()
559	
560	        # [MTP] DECODE_DRAFT_LAST delay scheduling (mirrors
561	        # decode_last_delay)。边侧自生成 decode_draft_last 后延迟 5ms
562	        # （默认）再调度，保留解码域 pacing（设计 §6.2）。
563	        self._decode_draft_last_delay_start_ts: float | None = None
564	        self._decode_draft_last_delay_schedule_ms: int = 15
565	
566	        # [MTP] PREFILL_DRAFT_LAST delay scheduling。
567	        # Phase A：prefill_draft 保持旧行为（边侧自贴尾 + 延迟，默认 10ms
568	        # 与旧 draft_last 一致）；Phase C 迁移为云侧 POST_OUT 发布后，
569	        # 本延迟不再使用（设计 §6.2）。
570	        self._prefill_draft_last_delay_start_ts: float | None = None
571	        self._prefill_draft_
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 09:10:33</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "        self._decode_draft_last_delay_start_ts: float | None = None\n        self._decode_draft_last_delay_schedule_ms: int = 15",
  "new_string": "        self._decode_draft_last_delay_start_ts: float | None = None\n        self._decode_draft_last_delay_schedule_ms: int = 15\n\n        # [EHER-draft] DDL recv-readiness ack gate: when enabled, a queued\n        # DECODE_DRAFT_LAST is schedulable the moment the edge TP0 worker\n        # reports its return irecv complete (worker report thread ->\n        # edge_recv_ready_mq -> EngineCore._drain_draft_recv_acks ->\n        # notify_draft_recv_ready), replacing fixed-delay pacing with\n        # data-plane readiness.  A timeout fallback (10x the delay, min\n        # 100ms) keeps the gate safe when no ack ever arrives (TP1-only\n        # worker mix, SP compat path, or sideband MQ not attached).\n        # Default off: legacy delay pacing unless the deployment yaml sets\n        # decode_draft_recv_ack_enable.\n        self._decode_draft_recv_ack_enable: bool = False\n        self._draft_recv_ready_acks: set[str] = set()"
}
```

</details>


---

## User <sup>2026/8/17 09:10:34</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:10:38</sup>

现在修改 gate 本身，并加上 notify 方法：


---

## Assistant <sup>2026/8/17 09:10:44</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "    def _can_schedule_decode_draft_last(self) -> bool:\n        \"\"\"Return True if the delay since DECODE_DRAFT_FIRST has elapsed.\"\"\"\n        if self._decode_draft_last_delay_start_ts is None:\n            return True\n        elapsed_ms = (\n            time.monotonic() - self._decode_draft_last_delay_start_ts\n        ) * 1000\n        if elapsed_ms >= self._decode_draft_last_delay_schedule_ms:\n            self._decode_draft_last_delay_start_ts = None\n            return True\n        return False",
  "new_string": "    def notify_draft_recv_ready(self, head_token: str) -> None:\n        \"\"\"[EHER-draft] Worker reported a DDL return irecv complete.\"\"\"\n        self._draft_recv_ready_acks.add(head_token)\n\n    def _can_schedule_decode_draft_last(self) -> bool:\n        \"\"\"Return True if the delay since DECODE_DRAFT_FIRST has elapsed.\"\"\"\n        if self._decode_draft_recv_ack_enable:\n            # Readiness gate: the oldest queued DDL is schedulable once its\n            # return transfer has landed (worker ack).  Fallback to the\n            # delay timer after a safety timeout so a missing ack path\n            # (no early post / sideband not attached) can never stall the\n            # pipeline -- tails must always eventually execute to keep the\n            # hidden channel paired.\n            if not self.decode_drafts_last_ready:\n                return True\n            front = self.decode_drafts_last_ready[0]\n            head_token = getattr(front, \"head_token\", None)\n            if head_token is None or head_token in self._draft_recv_ready_acks:\n                return True\n            if self._decode_draft_last_delay_start_ts is not None:\n                elapsed_ms = (\n                    time.monotonic()\n                    - self._decode_draft_last_delay_start_ts\n                ) * 10
...(truncated)
```

</details>


---

## User <sup>2026/8/17 09:10:45</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:10:48</sup>


---

## Assistant <sup>2026/8/17 09:10:48</sup>

pick 时消费 ack,并加载 yaml 开关：


---

## Assistant <sup>2026/8/17 09:10:50</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "            else:\n                # [FORCE] DDL pick -> 30ms decode first-only 窗口 + 解除\n                # decode_draft_last_pending 交替（设计 §6.3.2）。\n                self._force.on_pick(BatchType.DECODE_DRAFT_LAST)",
  "new_string": "            else:\n                # [EHER-draft] Consume the readiness ack for this flight.\n                self._draft_recv_ready_acks.discard(\n                    scheduler_output.head_token\n                )\n                # [FORCE] DDL pick -> 30ms decode first-only 窗口 + 解除\n                # decode_draft_last_pending 交替（设计 §6.3.2）。\n                self._force.on_pick(BatchType.DECODE_DRAFT_LAST)"
}
```

</details>


---

## User <sup>2026/8/17 09:10:50</sup>

<details>
<summary>Tool Result</summary>

```
<tool_use_error>String to replace not found in file.
String:             else:
                # [FORCE] DDL pick -> 30ms decode first-only 窗口 + 解除
                # decode_draft_last_pending 交替（设计 §6.3.2）。
                self._force.on_pick(BatchType.DECODE_DRAFT_LAST)
(note: Edit also tried swapping \uXXXX escapes and their characters; neither form matched, so the mismatch is likely elsewhere in old_string. Re-read the file and copy the exact surrounding text.)</tool_use_error>
```

</details>


---

## Assistant <sup>2026/8/17 09:10:54</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 12,
  "offset": 2830
}
```

</details>


---

## User <sup>2026/8/17 09:10:54</sup>

<details>
<summary>Tool Result</summary>

```
2830	            output_req_ids = getattr(
2831	                scheduler_output,
2832	                "draft_output_req_ids",
2833	                tuple(scheduler_output.num_scheduled_tokens),
2834	            )
2835	            has_live_output_req = any(
2836	                (request := self.requests.get(req_id)) is not None
2837	                and not request.is_finished()
2838	                for req_id in output_req_ids
2839	            )
2840	            if has_live_output_req:
2841	                self._prepare_next_decode_first_placeholder(scheduler_output)
```

</details>


---

## Assistant <sup>2026/8/17 09:10:57</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 10,
  "offset": 2821
}
```

</details>


---

## User <sup>2026/8/17 09:10:57</sup>

<details>
<summary>Tool Result</summary>

```
2821	                    prefill_chain_has_more=any(
2822	                        t.draft_task_id == scheduler_output.draft_task_id
2823	                        for t in self.prefill_drafts_first_ready
2824	                    ),
2825	                )
2826	            else:
2827	                # [FORCE] DDL pick → 30ms decode first-only 窗口 + 解除
2828	                # decode_draft_last_pending 交替（设计 §6.3.2）。
2829	                self._force.on_pick(BatchType.DECODE_DRAFT_LAST)
2830	            output_req_ids = getattr(
```

</details>


---

## Assistant <sup>2026/8/17 09:11:03</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "            else:\n                # [FORCE] DDL pick -> 30ms decode first-only 窗口 + 解除\n                # decode_draft_last_pending 交替（设计 §6.3.2）。\n                self._force.on_pick(BatchType.DECODE_DRAFT_LAST)\n            output_req_ids = getattr(",
  "new_string": "            else:\n                # [EHER-draft] Consume the readiness ack for this flight\n                # (bounds _draft_recv_ready_acks growth; a never-picked\n                # re-ack would be stale anyway since consumption of the\n                # worker-side cache resets the report marker).\n                self._draft_recv_ready_acks.discard(\n                    scheduler_output.head_token\n                )\n                # [FORCE] DDL pick -> 30ms decode first-only 窗口 + 解除\n                # decode_draft_last_pending 交替（设计 §6.3.2）。\n                self._force.on_pick(BatchType.DECODE_DRAFT_LAST)\n            output_req_ids = getattr("
}
```

</details>


---

## User <sup>2026/8/17 09:11:03</sup>

<details>
<summary>Tool Result</summary>

```
<tool_use_error>String to replace not found in file.
String:             else:
                # [FORCE] DDL pick -> 30ms decode first-only 窗口 + 解除
                # decode_draft_last_pending 交替（设计 §6.3.2）。
                self._force.on_pick(BatchType.DECODE_DRAFT_LAST)
            output_req_ids = getattr(
(note: Edit also tried swapping \uXXXX escapes and their characters; neither form matched, so the mismatch is likely elsewhere in old_string. Re-read the file and copy the exact surrounding text.)</tool_use_error>
```

</details>


---

## Assistant <sup>2026/8/17 09:11:07</sup>


---

## Assistant <sup>2026/8/17 09:11:08</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"on_pick(BatchType.DECODE_DRAFT_LAST)\" c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py | cat -A | head -5",
  "description": "Check for hidden characters around anchor"
}
```

</details>


---

## User <sup>2026/8/17 09:11:09</sup>

<details>
<summary>Tool Result</summary>

```
2829:                self._force.on_pick(BatchType.DECODE_DRAFT_LAST)$
```

</details>


---

## Assistant <sup>2026/8/17 09:11:15</sup>


---

## Assistant <sup>2026/8/17 09:11:17</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "                self._force.on_pick(BatchType.DECODE_DRAFT_LAST)",
  "new_string": "                # [EHER-draft] Consume the readiness ack for this flight\n                # (bounds _draft_recv_ready_acks growth; a re-posted DDF\n                # under the same head_token starts with a clean marker).\n                self._draft_recv_ready_acks.discard(\n                    scheduler_output.head_token\n                )\n                self._force.on_pick(BatchType.DECODE_DRAFT_LAST)"
}
```

</details>


---

## User <sup>2026/8/17 09:11:18</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:11:23</sup>


---

## Assistant <sup>2026/8/17 09:11:23</sup>

yaml 开关加载。看 delay 键加载块现状：


---

## Assistant <sup>2026/8/17 09:11:24</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"decode_draft_last_delay_schedule_ms\" c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py",
  "description": "Locate yaml key loading lines"
}
```

</details>


---

## User <sup>2026/8/17 09:11:24</sup>

<details>
<summary>Tool Result</summary>

```
564:        self._decode_draft_last_delay_schedule_ms: int = 15
1717:                  "_decode_draft_last_delay_schedule_ms")),
1737:                ("decode_draft_last_delay_schedule_ms",
1738:                 "_decode_draft_last_delay_schedule_ms"),
1835:                    10 * self._decode_draft_last_delay_schedule_ms, 100
1850:        if elapsed_ms >= self._decode_draft_last_delay_schedule_ms:
```

</details>


---

## Assistant <sup>2026/8/17 09:11:27</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 45,
  "offset": 1733
}
```

</details>


---

## User <sup>2026/8/17 09:11:27</sup>

<details>
<summary>Tool Result</summary>

```
1733	                        )
1734	            for _key, _attr in (
1735	                ("prefill_draft_last_delay_schedule_ms",
1736	                 "_prefill_draft_last_delay_schedule_ms"),
1737	                ("decode_draft_last_delay_schedule_ms",
1738	                 "_decode_draft_last_delay_schedule_ms"),
1739	            ):
1740	                if _key in raw:
1741	                    try:
1742	                        setattr(self, _attr, int(raw[_key]))
1743	                        logger.info(
1744	                            "[PDSeparatedScheduler] %s set to %d from %s",
1745	                            _key, getattr(self, _attr), yaml_path,
1746	                        )
1747	                    except (ValueError, TypeError):
1748	                        logger.warning(
1749	                            "Invalid %s value %r in %s; keeping %d",
1750	                            _key, raw[_key], yaml_path,
1751	                            getattr(self, _attr),
1752	      
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 09:11:33</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "                    except (ValueError, TypeError):\n                        logger.warning(\n                            \"Invalid %s value %r in %s; keeping %d\",\n                            _key, raw[_key], yaml_path,\n                            getattr(self, _attr),\n                        )\n            self._layer_slice_config_path = yaml_path",
  "new_string": "                    except (ValueError, TypeError):\n                        logger.warning(\n                            \"Invalid %s value %r in %s; keeping %d\",\n                            _key, raw[_key], yaml_path,\n                            getattr(self, _attr),\n                        )\n            # [EHER-draft] Readiness-ack gate switch: replace the fixed\n            # DDL delay pacing with worker-reported recv readiness (see\n            # _can_schedule_decode_draft_last).  Off by default.\n            _ack_raw = raw.get(\"decode_draft_recv_ack_enable\")\n            if _ack_raw is not None:\n                self._decode_draft_recv_ack_enable = bool(_ack_raw)\n                logger.info(\n                    \"[PDSeparatedScheduler] decode_draft_recv_ack_enable \"\n                    \"set to %s from %s\",\n                    self._decode_draft_recv_ack_enable, yaml_path,\n                )\n            self._layer_slice_config_path = yaml_path"
}
```

</details>


---

## User <sup>2026/8/17 09:11:34</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:11:37</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "python -m py_compile c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py && echo SYNTAX_OK",
  "description": "Compile-check scheduler"
}
```

</details>


---

## User <sup>2026/8/17 09:12:57</sup>

<details>
<summary>Tool Result</summary>

```
SYNTAX_OK
```

</details>


---

## Assistant <sup>2026/8/17 09:13:02</sup>


---

## Assistant <sup>2026/8/17 09:13:02</sup>

P1 全部完成。进入 P2-1:先读 `==0` 门与 inflight 释放点：


---

## Assistant <sup>2026/8/17 09:13:03</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"_can_schedule_decode_draft_first\\|decode_or_draft_inflight_count\" c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py | head -20",
  "description": "Locate draft-first gate and inflight counter sites"
}
```

</details>


---

## User <sup>2026/8/17 09:13:04</sup>

<details>
<summary>Tool Result</summary>

```
421:        self.decode_or_draft_inflight_count: int = 0
432:        # 因此 decode_or_draft_inflight_count 仍被两域共同占用。
1318:        # Do NOT gate on decode_or_draft_inflight_count here either: it was
1344:            if self._can_schedule_decode_draft_first():
1391:                and self._can_schedule_decode_draft_first()
1442:                and self._can_schedule_decode_draft_first()
1476:            and self._can_schedule_decode_draft_first()
1506:                or self.decode_or_draft_inflight_count > 0
1516:            and not self._can_schedule_decode_draft_first()
1565:            and self.decode_or_draft_inflight_count == 0
1602:    def _can_schedule_decode_draft_first(self) -> bool:
1627:            self.decode_or_draft_inflight_count == 0
1651:                f"decode_or_draft_inflight: {self.decode_or_draft_inflight_count}/{self.decode_or_draft_inflight_limit}, "
1672:                f"decode_or_draft_inflight: {self.decode_or_draft_inflight_count}/{self.decode_or_draft_infli
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 09:13:10</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 75,
  "offset": 1602
}
```

</details>


---

## User <sup>2026/8/17 09:13:10</sup>

<details>
<summary>Tool Result</summary>

```
1602	    def _can_schedule_decode_draft_first(self) -> bool:
1603	        if not self.decode_drafts_first_ready:
1604	            return False
1605	        next_output = self.decode_drafts_first_ready[0]
1606	        is_pregenerated = (
1607	            next_output.draft_task_id in self._pregenerated_draft_task_ids
1608	        )
1609	        if is_pregenerated:
1610	            # 与 _can_schedule_prefill_draft_first 的 pregenerated 分支
1611	            # 同构，仅作用于 decode 域计数/标记（设计 §6.1）。
1612	            # [FORCE] 交替门控收敛到状态机（设计 §6.3.2）。
1613	            return bool(
1614	                self.decode_head_inflight_count == 0
1615	                and self.decode_draft_remote_pending_count
1616	                < self._decode_draft_remote_pending_limit
1617	                and not self.decode_drafts_last_ready
1618	                and self._force.can_pick_decode_draft_first()
1619	            )
1620	
1621	        # Scheduled draft head/tail payloads share the DECODE channel.
1622	        # Do n
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 09:13:31</sup>


---

## Assistant <sup>2026/8/17 09:13:31</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 55,
  "offset": 400
}
```

</details>


---

## User <sup>2026/8/17 09:13:31</sup>

<details>
<summary>Tool Result</summary>

```
400	        # the metadata needed to execute the edge tail segment.
401	        # Populated by EngineCore.step() before calling self.schedule().
402	        self.prefills_last_ready: deque[SchedulerOutput] = deque()
403	        self.decodes_first_ready: deque[SchedulerOutput] = deque()
404	        self.decodes_last_ready: deque[SchedulerOutput] = deque()
405	        # 4 域拆分（设计 §3.2）：prefill_draft 链与 decode_draft 链的就绪
406	        # 队列彼此独立，调度互不阻塞。
407	        self.prefill_drafts_first_ready: deque[SchedulerOutput] = deque()
408	        self.prefill_drafts_last_ready: deque[SchedulerOutput] = deque()
409	        self.decode_drafts_first_ready: deque[SchedulerOutput] = deque()
410	        self.decode_drafts_last_ready: deque[SchedulerOutput] = deque()
411	
412	        self._step_counter: int = 0
413	
414	        # In-flight prefill limit (head-segment batches).
415	        self.prefill_inflight_limit: int = getattr(
416	            self.scheduler_config, "pd_prefill_inflight_limit",
417	  
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 09:13:36</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 65,
  "offset": 3600
}
```

</details>


---

## User <sup>2026/8/17 09:13:36</sup>

<details>
<summary>Tool Result</summary>

```
3600	            # 同 turn 原子性（review Bug 3）：本函数与
3601	            # _advance_edge_cloud_draft 在 EngineCore 同一 step 内先后
3602	            # 执行（patch_engine_core.py update_from_output 之后立即
3603	            # _advance），has_fallback_chain 为真 ⇒ 同 turn 内
3604	            # enqueue_draft_first 必然补 +1（槽记账与 §5.5 per-req 计数
3605	            # 皆依赖此配对）；若 _advance 因 use_spec_decode/state 缺失
3606	            # 早退，worker 亦不会产生 state，本判定恒为 False，无泄漏。
3607	            head_token = scheduler_output.head_token
3608	            state = getattr(model_runner_output, "edge_cloud_draft_state", None)
3609	            has_fallback_chain = bool(
3610	                head_token
3611	                and state is not None
3612	                and state.get("draft_task_id") == head_token
3613	            )
3614	            if head_token in self._prefill_slot_pending:
3615	                self._prefill_slot_pl_done[head_token] = True
3616	                if self._prefill_slot_pending[head_token] > 0:
3617	            
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 09:13:57</sup>


---

## Assistant <sup>2026/8/17 09:13:59</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "grep -n \"_decode_draft_remote_pending_limit\" c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py | head; echo ---; grep -n \"decode_draft_pipeline\\|_force.can_pick_decode_draft_first\" c:/kisella_mtp/vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py | head",
  "description": "Check pending limit value"
}
```

</details>


---

## User <sup>2026/8/17 09:14:00</sup>

<details>
<summary>Tool Result</summary>

```
605:        self._decode_draft_remote_pending_limit: int = int(
608:                "pd_decode_draft_remote_pending_limit",
1616:                < self._decode_draft_remote_pending_limit
---
1618:                and self._force.can_pick_decode_draft_first()
1630:            and self._force.can_pick_decode_draft_first()
```

</details>


---

## Assistant <sup>2026/8/17 09:14:03</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "limit": 12,
  "offset": 600
}
```

</details>


---

## User <sup>2026/8/17 09:14:03</sup>

<details>
<summary>Tool Result</summary>

```
600	                self.scheduler_config,
601	                "pd_prefill_draft_remote_pending_limit",
602	                2,
603	            )
604	        )
605	        self._decode_draft_remote_pending_limit: int = int(
606	            getattr(
607	                self.scheduler_config,
608	                "pd_decode_draft_remote_pending_limit",
609	                2,
610	            )
611	        )
```

</details>


---

## Assistant <sup>2026/8/17 09:14:09</sup>


---

## Assistant <sup>2026/8/17 09:14:09</sup>

实现 P2-1 门放宽:


---

## Assistant <sup>2026/8/17 09:14:14</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "        # Scheduled draft head/tail payloads share the DECODE channel.\n        # Do not start another head while an earlier head is still remote or\n        # its tail is ready locally: otherwise edge and cloud can each wait\n        # for the opposite-direction send before posting the matching recv.\n        # [FORCE] 交替门控收敛到状态机（设计 §6.3.2）。\n        return bool(\n            self.decode_or_draft_inflight_count == 0\n            and self.decode_draft_remote_pending_count == 0\n            and not self.decode_drafts_last_ready\n            and self._force.can_pick_decode_draft_first()\n        )",
  "new_string": "        # Scheduled draft head/tail payloads used to share the DECODE\n        # channel, forcing full serialization (==0 gate): with a second\n        # chain in flight, edge and cloud could each wait for the\n        # opposite-direction send before posting the matching recv.  With\n        # the dedicated DRAFT channel (P0) per-direction FIFO matching\n        # makes concurrent chains safe, so when pipelining is enabled the\n        # gate relaxes to the pregenerated form: inflight < limit and\n        # remote_pending < limit (default 2).  Off (legacy ==0) by default.\n        self._decode_draft_pipeline_enable: bool = False\n        if self._decode_draft_pipeline_enable:\n            return bool(\n                self.decode_or_draft_inflight_count\n                < self.decode_or_draft_inflight_limit\n                and self.decode_draft_remote_pending_count\n                < self._decode_draft_remote_pending_limit\n                and not self.decode_drafts_last_ready\n                and self._force.can_pick_decode_draft_first()\n            )\n        return bool(\n            self.decode_or_draft_inflight_count == 0\n            and self.decode_draft_remote_pending_count == 0\n            and not self.d
...(truncated)
```

</details>


---

## User <sup>2026/8/17 09:14:15</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:14:22</sup>


---

## Assistant <sup>2026/8/17 09:14:22</sup>

修正：inflight_limit 硬编码为 1,流水分支需用同一上限：


---

## Assistant <sup>2026/8/17 09:14:25</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "        if self._decode_draft_pipeline_enable:\n            return bool(\n                self.decode_or_draft_inflight_count\n                < self.decode_or_draft_inflight_limit\n                and self.decode_draft_remote_pending_count\n                < self._decode_draft_remote_pending_limit\n                and not self.decode_drafts_last_ready\n                and self._force.can_pick_decode_draft_first()\n            )",
  "new_string": "        if self._decode_draft_pipeline_enable:\n            # inflight_limit is hardcoded 1 (legacy); under pipelining the\n            # effective cap is the same remote-pending limit (default 2)\n            # that governs the pregenerated branch.\n            return bool(\n                self.decode_or_draft_inflight_count\n                < self._decode_draft_remote_pending_limit\n                and self.decode_draft_remote_pending_count\n                < self._decode_draft_remote_pending_limit\n                and not self.decode_drafts_last_ready\n                and self._force.can_pick_decode_draft_first()\n            )"
}
```

</details>


---

## User <sup>2026/8/17 09:14:26</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:14:29</sup>

yaml 开关加载(pipeline):


---

## Assistant <sup>2026/8/17 09:14:33</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\vllm_ascend\\core\\pd_separated_scheduler.py",
  "old_string": "            # [EHER-draft] Readiness-ack gate switch: replace the fixed\n            # DDL delay pacing with worker-reported recv readiness (see\n            # _can_schedule_decode_draft_last).  Off by default.\n            _ack_raw = raw.get(\"decode_draft_recv_ack_enable\")\n            if _ack_raw is not None:\n                self._decode_draft_recv_ack_enable = bool(_ack_raw)\n                logger.info(\n                    \"[PDSeparatedScheduler] decode_draft_recv_ack_enable \"\n                    \"set to %s from %s\",\n                    self._decode_draft_recv_ack_enable, yaml_path,\n                )\n            self._layer_slice_config_path = yaml_path",
  "new_string": "            # [EHER-draft] Readiness-ack gate switch: replace the fixed\n            # DDL delay pacing with worker-reported recv readiness (see\n            # _can_schedule_decode_draft_last).  Off by default.\n            _ack_raw = raw.get(\"decode_draft_recv_ack_enable\")\n            if _ack_raw is not None:\n                self._decode_draft_recv_ack_enable = bool(_ack_raw)\n                logger.info(\n                    \"[PDSeparatedScheduler] decode_draft_recv_ack_enable \"\n                    \"set to %s from %s\",\n                    self._decode_draft_recv_ack_enable, yaml_path,\n                )\n            # [P2] Decode-draft pipelining switch: relax the serial ==0\n            # draft-first gate to < limit now that drafts own the DRAFT\n            # channel (see _can_schedule_decode_draft_first).  Off by\n            # default.\n            _pipe_raw = raw.get(\"decode_draft_pipeline_enable\")\n            if _pipe_raw is not None:\n                self._decode_draft_pipeline_enable = bool(_pipe_raw)\n                logger.info(\n                    \"[PDSeparatedScheduler] decode_draft_pipeline_enable \"\n            
...(truncated)
```

</details>


---

## User <sup>2026/8/17 09:14:34</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\vllm_ascend\core\pd_separated_scheduler.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:14:52</sup>


---

## Assistant <sup>2026/8/17 09:14:52</sup>

P2-2 中 pacing 旁路由 ack 门即时派发实现、watchdog 由超时回落承担(派发时告警日志)。全量编译验证：


---

## Assistant <sup>2026/8/17 09:14:54</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "cd c:/kisella_mtp && python -m py_compile \\\n  vllm-pdmix/vllm/v1/core/sched/output.py \\\n  vllm-pdmix/vllm/v1/worker/gpu_worker.py \\\n  vllm-pdmix/vllm/v1/executor/multiproc_executor.py \\\n  vllm-ascend-pdmix/vllm_ascend/distributed/parallel_state.py \\\n  vllm-ascend-pdmix/vllm_ascend/patch/worker/patch_distributed.py \\\n  vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_multiproc_executor.py \\\n  vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py \\\n  vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py \\\n  vllm-ascend-pdmix/vllm_ascend/worker/worker.py \\\n  && echo ALL_SYNTAX_OK",
  "description": "Compile all modified files"
}
```

</details>


---

## User <sup>2026/8/17 09:15:49</sup>

<details>
<summary>Tool Result</summary>

```
vllm-ascend-pdmix/vllm_ascend/worker/worker.py:312: SyntaxWarning: 'return' in a 'finally' block
  return
ALL_SYNTAX_OK
```

</details>


---

## Assistant <sup>2026/8/17 09:16:04</sup>


---

## Assistant <sup>2026/8/17 09:16:05</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "cd c:/kisella_mtp/vllm-ascend-pdmix && grep -rln \"_can_schedule_decode_draft_first\\|_draft_recv\\|edge_recv_ready\" tests/ 2>/dev/null; echo ---done",
  "description": "Check tests touching new code paths"
}
```

</details>


---

## User <sup>2026/8/17 09:16:06</sup>

<details>
<summary>Tool Result</summary>

```
tests/ut/test_pd_draft_drain.py
tests/ut/__pycache__/test_pd_draft_drain.cpython-314.pyc
---done
```

</details>


---

## Assistant <sup>2026/8/17 09:16:12</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "cd c:/kisella_mtp/vllm-ascend-pdmix && grep -n \"_can_schedule_decode_draft_first\\|_draft_recv\\|edge_recv_ready\\|DECODE\\b\" tests/ut/test_pd_draft_drain.py | head -20",
  "description": "See what the UT references"
}
```

</details>


---

## User <sup>2026/8/17 09:16:13</sup>

<details>
<summary>Tool Result</summary>

```
8:the DECODE channel); the prefill-draft domain is the same logic keyed by
14:  * ``_can_schedule_decode_draft_first`` (pre-generated branch) now respects
20:    tail on the shared DECODE channel -> cloud ``irecv`` deadlock).
28:    ``irecv`` to keep the DECODE channel paired) and only spawns a verify
127:# Test: _can_schedule_decode_draft_first honors force flag (fix ①)   #
154:        assert s._can_schedule_decode_draft_first() is False
159:        assert s._can_schedule_decode_draft_first() is True
165:        assert s._can_schedule_decode_draft_first() is False
169:        DECODE_FIRST use different recv primitives but share the DECODE
176:        assert s._can_schedule_decode_draft_first() is False
178:        assert s._can_schedule_decode_draft_first() is True
192:        assert s._can_schedule_decode_draft_first() is True
198:        assert s._can_schedule_decode_draft_first() is False
216:        assert s._can_schedule_decode_draft_first() is False
221:        assert s._can_sch
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 09:16:15</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\tests\\ut\\test_pd_draft_drain.py",
  "limit": 110,
  "offset": 120
}
```

</details>


---

## User <sup>2026/8/17 09:16:15</sup>

<details>
<summary>Tool Result</summary>

```
120	    so.head_token = task_id
121	    so.num_scheduled_tokens = {req_id: 8}
122	    so.total_num_scheduled_tokens = 8
123	    return so
124	
125	
126	# ------------------------------------------------------------------ #
127	# Test: _can_schedule_decode_draft_first honors force flag (fix ①)   #
128	# ------------------------------------------------------------------ #
129	
130	
131	class TestCanScheduleDecodeDraftFirstForceGuard:
132	    """The pre-generated branch must gate on the FORCE state machine's
133	    ``decode_draft_last_pending`` just like the non-pre-generated branch,
134	    so DECODE_DRAFT_FIRST -> DECODE_DRAFT_LAST alternation is
135	    guaranteed."""
136	
137	    def _setup(self, pregenerated=True):
138	        s = _make_bare_scheduler()
139	        drf = _make_draft_first()
140	        s.decode_drafts_first_ready.append(drf)
141	        if pregenerated:
142	            s._pregenerated_draft_task_ids.add(drf.draft_task_id)
143	        # Conditions that would otherwis
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 09:16:23</sup>


---

## Assistant <sup>2026/8/17 09:16:24</sup>

UT 补两个新分支的用例。看 helper 定义:


---

## Assistant <sup>2026/8/17 09:16:24</sup>

<details>
<summary>Tool: <code>Read</code></summary>

```json
{
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\tests\\ut\\test_pd_draft_drain.py",
  "limit": 75,
  "offset": 45
}
```

</details>


---

## User <sup>2026/8/17 09:16:24</sup>

<details>
<summary>Tool Result</summary>

```
45	    HiddenChannelType,
46	    SchedulerOutput,
47	)
48	
49	
50	# ------------------------------------------------------------------ #
51	# Helpers                                                            #
52	# ------------------------------------------------------------------ #
53	
54	
55	def _make_bare_scheduler():
56	    from vllm_ascend.core.pd_separated_scheduler import (
57	        EdgeForceStateMachine,
58	        PDSeparatedScheduler,
59	    )
60	
61	    s = PDSeparatedScheduler.__new__(PDSeparatedScheduler)
62	    s.decode_drafts_first_ready = deque()
63	    s.decode_drafts_last_ready = deque()
64	    s.prefill_drafts_first_ready = deque()
65	    s.prefill_drafts_last_ready = deque()
66	    s.requests = {}
67	    s._pregenerated_draft_task_ids = set()
68	    s._pregenerated_draft_req_ids = {}
69	    s._draft_first_dispatched = False
70	    s._draft_first_cloud_publish_pending = None
71	    s._draft_first_scalars_patched = False
72	    s._decode_draft_remote_pending_limit 
...(truncated)
```

</details>


---

## Assistant <sup>2026/8/17 09:16:28</sup>


---

## Assistant <sup>2026/8/17 09:16:29</sup>

新字段会破坏 bare scheduler 的既有用例，补齐 helper 并加新用例：


---

## Assistant <sup>2026/8/17 09:16:32</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\tests\\ut\\test_pd_draft_drain.py",
  "old_string": "    s.decode_or_draft_inflight_count = 0\n    s.decode_or_draft_inflight_limit = 1\n    s.decode_head_inflight_count = 0\n    # [FORCE] 状态机（设计 §6.3.2）：交替与窗口状态在此驱动/断言。\n    s._force = EdgeForceStateMachine()\n    s.num_spec_tokens = 3\n    return s",
  "new_string": "    s.decode_or_draft_inflight_count = 0\n    s.decode_or_draft_inflight_limit = 1\n    s.decode_head_inflight_count = 0\n    # [EHER-draft] P1/P2 gate state: ack set + switches + delay fallback\n    # baseline (see _can_schedule_decode_draft_first/_last).\n    s._decode_draft_pipeline_enable = False\n    s._decode_draft_recv_ack_enable = False\n    s._draft_recv_ready_acks = set()\n    s._decode_draft_last_delay_start_ts = None\n    s._decode_draft_last_delay_schedule_ms = 15\n    # [FORCE] 状态机（设计 §6.3.2）：交替与窗口状态在此驱动/断言。\n    s._force = EdgeForceStateMachine()\n    s.num_spec_tokens = 3\n    return s"
}
```

</details>


---

## User <sup>2026/8/17 09:16:33</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\tests\ut\test_pd_draft_drain.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:16:45</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\tests\\ut\\test_pd_draft_drain.py",
  "old_string": "    def test_non_pregenerated_branch_also_blocked_by_force_draft_last(self):\n        \"\"\"Non-pre-generated branch already had the guard (unchanged).\"\"\"\n        s = self._setup(pregenerated=False)\n        s._force.decode_draft_last_pending = True\n        assert s._can_schedule_decode_draft_first() is False",
  "new_string": "    def test_non_pregenerated_branch_also_blocked_by_force_draft_last(self):\n        \"\"\"Non-pre-generated branch already had the guard (unchanged).\"\"\"\n        s = self._setup(pregenerated=False)\n        s._force.decode_draft_last_pending = True\n        assert s._can_schedule_decode_draft_first() is False\n\n\nclass TestDecodeDraftPipelineGate:\n    \"\"\"[P2-1] With decode_draft_pipeline_enable, the serial ==0 gate relaxes\n    to < limit (drafts own the dedicated DRAFT channel; per-direction FIFO\n    matching makes concurrent chains safe).  Legacy behavior is unchanged\n    while the switch is off.\"\"\"\n\n    def _setup(self):\n        s = _make_bare_scheduler()\n        s.decode_drafts_first_ready.append(_make_draft_first())\n        s._force.decode_last_pending = False\n        s._force.decode_draft_last_pending = False\n        return s\n\n    def test_legacy_serial_gate_blocks_second_head(self):\n        s = self._setup()\n        s.decode_or_draft_inflight_count = 1\n        s.decode_draft_remote_pending_count = 1\n        assert s._can_schedule_decode_draft_first() is False\n\n    def test_pipeline_allows_second_head_under_limit(self):\n        s = self._setup()\n        s._decode_draft_pipeline_enable = True\n        s.decode_or_draft_inflight_count = 1\n        s.decode_draft_remote_pending_count = 1\n        assert s._can_schedule_decode_draft_first() is True\n\n    def test_pipeline_blocked_at_limit(self):\n        s = self._setup()\n        s._decode_draft_pipeline_enable = True\n    
...(truncated)
```

</details>


---

## User <sup>2026/8/17 09:16:46</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\tests\ut\test_pd_draft_drain.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:16:52</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "cd c:/kisella_mtp/vllm-ascend-pdmix && grep -n \"^import\\|^from\" tests/ut/test_pd_draft_drain.py | head",
  "description": "Check time import in test file"
}
```

</details>


---

## User <sup>2026/8/17 09:16:52</sup>

<details>
<summary>Tool Result</summary>

```
38:from collections import deque
39:from unittest.mock import MagicMock
41:import pytest
43:from vllm.v1.core.sched.output import (
```

</details>


---

## Assistant <sup>2026/8/17 09:16:56</sup>

<details>
<summary>Tool: <code>Edit</code></summary>

```json
{
  "replace_all": false,
  "file_path": "c:\\kisella_mtp\\vllm-ascend-pdmix\\tests\\ut\\test_pd_draft_drain.py",
  "old_string": "from collections import deque\nfrom unittest.mock import MagicMock",
  "new_string": "from collections import deque\nimport time\nfrom unittest.mock import MagicMock"
}
```

</details>


---

## User <sup>2026/8/17 09:16:57</sup>

<details>
<summary>Tool Result</summary>

```
The file c:\kisella_mtp\vllm-ascend-pdmix\tests\ut\test_pd_draft_drain.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>


---

## Assistant <sup>2026/8/17 09:17:01</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "cd c:/kisella_mtp/vllm-ascend-pdmix && python -m py_compile tests/ut/test_pd_draft_drain.py && echo SYNTAX_OK && python -c \"\nimport sys, types, time\nfrom unittest.mock import MagicMock\nsys.path.insert(0, 'tests/ut')\n# stub external deps not installed locally\nsys.modules.setdefault('vllm', types.ModuleType('vllm'))\n\" && echo STUB_OK",
  "description": "Compile-check test file"
}
```

</details>


---

## User <sup>2026/8/17 09:17:06</sup>

<details>
<summary>Tool Result</summary>

```
SYNTAX_OK
STUB_OK
```

</details>


---

## Assistant <sup>2026/8/17 09:17:10</sup>


---

## Assistant <sup>2026/8/17 09:17:11</sup>

<details>
<summary>Tool: <code>Bash</code></summary>

```json
{
  "command": "cd c:/kisella_mtp/vllm-ascend-pdmix && python -m pytest tests/ut/test_pd_draft_drain.py -x -q 2>&1 | tail -5",
  "description": "Attempt pytest run"
}
```

</details>


---

## User <sup>2026/8/17 09:17:12</sup>

<details>
<summary>Tool Result</summary>

```
C:\Users\root\AppData\Local\Programs\Python\Python314\python.exe: No module named pytest
```

</details>


---

## Assistant <sup>2026/8/17 09:17:17</sup>

<details>
<summary>Tool: <code>TodoWrite</code></summary>

```json
{
  "todos": [
    {
      "activeForm": "Creating DRAFT channel",
      "content": "P0-1..P0-4: DRAFT 专用通道端到端",
      "status": "completed"
    },
    {
      "activeForm": "Adding irecv NPU event",
      "content": "P1-1 irecv NPU event (parallel_state)",
      "status": "completed"
    },
    {
      "activeForm": "Adding is_ready()",
      "content": "P1-2 AsyncIntermediateTensors.is_ready()",
      "status": "completed"
    },
    {
      "activeForm": "Posting early DDL irecv at DDF",
      "content": "P1-3 worker.py: DDF 时提前挂 DDL return-irecv + head_token stash",
      "status": "completed"
    },
    {
      "activeForm": "Adding busy-loop poll and sideband MQ",
      "content": "P1-4 边侧 sideband MQ + 就绪轮询上报",
      "status": "completed"
    },
    {
      "activeForm": "Adding scheduler DDL ack gate",
      "content": "P1-5 scheduler: DDL 派发门 = recv 就绪 ack",
      "status": "completed"
    },
    {
      "activeForm": "Relaxing draft gate",
      "content": "P2-1 draft 门 ==0 -> <limit + inflight 提前释放",
      "status": "completed"
    },
    {
      "activeForm": "Bypassing pacing delay",
      "content": "P2-2 pacing 旁路(ack 门即时派发) + 超时回落 watchdog",
      "status": "completed"
    },
    {
      "activeForm": "Verifying compile and UT",
      "content": "全量 py_compile + UT 更新",
      "status": "completed"
    }
  ]
}
```

</details>


---

## User <sup>2026/8/17 09:17:17</sup>

<details>
<summary>Tool Result</summary>

```
Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable
```

</details>


---

## Assistant <sup>2026/8/17 09:17:20</sup>


---

## Assistant <sup>2026/8/17 09:17:36</sup>

实现全部完成。以下是本次(从 P1-3 继续)完成的修改总结：

## P1-3 提前挂 DDL return-irecv(边侧 TP0)

- [parallel_state.py](vllm-ascend-pdmix/vllm_ascend/distributed/parallel_state.py#L2169-L2183) `edge_cloud_broadcast_recv_scheduled_draft` 快速路径：irecv 循环后在通道流上记 NPU event(`__comm_event__` 私有键)，供就绪探测。
- [worker.py](vllm-ascend-pdmix/vllm_ascend/worker/worker.py#L239-L262) `__init__` 增加 `_draft_recv_cache`(按 head_token 缓存 AsyncIntermediateTensors)+ `_draft_recv_lock` + `_draft_recv_reported`。
- 新增两个 helper:
  - `_post_draft_return_irecv`(worker.py:967):仅 TP0(`pp_group.world_size == 2`)、仅 DECODE_DRAFT_FIRST、SP-off 时生效；用 DDF 的 SO 推导 c2e meta。**正确性关键**：DDL 由 `replace()` 自贴(保留 `draft_step_idx`/token 计数/head_token),两边 meta 逐字节一致，irecv 形状必然匹配。失败软回落(不缓存 → 尾部走同步路径)。
  - `_consume_draft_recv`:按 head_token pop 缓存，同时清 reported 标记。
- `_execute_model_edge_draft_head` 发送块末尾挂 early-post 钩子；`_execute_model_edge_draft_tail` 优先消费缓存(`.tensors` 懒等待，miss 回落同步 recv)——TP1 与 SP 兼容路径零改动。

## P1-4 就绪轮询上报(worker → EngineCore sideband)

方向与 CHER 相反，而 MessageQueue 只有创建实例能 enqueue,因此采用 **worker 创建 + handle 文件交换**：

- [patch_multiproc_executor.py](vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_multiproc_executor.py):`_eher_init_edge_recv_ready_mq` 在边侧 TP0 worker 的 `_init_message_queues` 里创建 MQ(writer)并把 handle 写到节点本地文件(按 master_port+dp_rank 命名);`_eher_attach_edge_recv_ready_mq` 在 executor 侧 workers-ready 之后读文件建 reader 并删除文件。失败均软禁用。
- [multiproc_executor.py](vllm-pdmix/vllm/v1/executor/multiproc_executor.py#L1398-L1485) 新增 `eher-draft-ready-report` 报告线程(镜像 CHER guard):**只做 `event.query()`,绝不 wait()**(HCCL 跨线程约束)；ack 每航次至多上报一次，空闲退避 0.2ms。
- [patch_engine_core.py](vllm-ascend-pdmix/vllm_ascend/patch/platform/patch_engine_core.py):`_drain_draft_recv_acks` 排在 `_drain_pd_channel_inbox` 旁，两个 step 路径都已接入，调 `scheduler.notify_draft_recv_ready()`。

## P1-5 / P2 调度器

- [pd_separated_scheduler.py](vllm-ascend-pdmix/vllm_ascend/core/pd_separated_scheduler.py#L1815-L1852) `notify_draft_recv_ready` + ack 门：开关 `decode_draft_recv_ack_enable`(yaml,**默认关**)打开后，DDL 派发改为“队首 head_token 已 ack 即可派发”(替代 5/15ms 固定延迟即 pacing 旁路)，并带**超时回落 watchdog**(max(10×delay, 100ms) 后强制派发并告警——缺 ack 路径不会卡死，尾必须执行以保通道配对)。pick 时消费 ack 防集合增长。
- `_can_schedule_decode_draft_first` 非 pregenerated 分支：开关 `decode_draft_pipeline_enable`(yaml,默认关)打开后 `==0` 串行门放宽为 `< limit=2`(P0 专用 DRAFT 通道 + 按方向 FIFO 匹配使并发链安全)，形式与 pregenerated 分支一致。DDF 完成时的 inflight 提前释放已存在(L3649 分支)，无需改。

## 验证

- 9 个改动文件全部 `py_compile` 通过(worker.py:312 的 SyntaxWarning 为存量问题)。
- [test_pd_draft_drain.py](vllm-ascend-pdmix/tests/ut/test_pd_draft_drain.py) 补齐 bare-scheduler 新字段，新增 `TestDecodeDraftPipelineGate`(4 例)与 `TestDecodeDraftRecvAckGate`(4 例)覆盖两个新门。本机无 pytest/torch,**需在 NPU 机器上跑 UT 与联调**。

**联调建议顺序**：先默认开关跑通回归(DRAFT 通道 + 提前 irecv 本身即有收益，行为兼容)→ 打开 `decode_draft_recv_ack_enable` 验证 ack 门日志(`[EHER-draft]`)→ 最后打开 `decode_draft_pipeline_enable` 验证双链流水。


---

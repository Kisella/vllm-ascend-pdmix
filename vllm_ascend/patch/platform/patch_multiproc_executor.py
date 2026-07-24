from __future__ import annotations

import base64
import os
import pickle
import tempfile
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
# [CHER] Environment variable carrying the pickled+base64'd Handle of the
# cloud_recv_hint_mq, so the cloud worker process (spawned by
# make_worker_process) can rebuild the sideband MQ without changing
# make_worker_process/WorkerProc.__init__ signatures.  Fork inherits env
# directly; spawn gets it via the env copied at process start.
_CLOUD_RECV_HINT_MQ_ENV = "VLLM_ASCEND_CLOUD_RECV_HINT_MQ_HANDLE"

# [EHER] Sideband MQs on the EDGE executor (mirrors CHER's cloud side):
#   edge_recv_hint_mq : edge EngineCore -> edge worker guard thread (recv-hints)
#                     Follows the CHER pattern: executor=writer, worker=reader.
#   ha_ack_mq          : edge worker guard thread -> edge EngineCore (recv-done acks)
#                     Direction is REVERSED (worker writes, EngineCore reads).
#                     The MessageQueue API is strictly unidirectional (creator is
#                     always writer, create_from_handle always gives reader), so
#                     the worker CREATES ha_ack_mq (as writer) and passes the
#                     handle back to the executor via a temp file; the executor
#                     then calls create_from_handle to get a reader proxy.
_EDGE_RECV_HINT_MQ_ENV = "VLLM_ASCEND_EDGE_RECV_HINT_MQ_HANDLE"
_EDGE_HA_ACK_MQ_ENV = "VLLM_ASCEND_EDGE_HA_ACK_MQ_HANDLE"
# Temp-file path for the worker->executor ha_ack_mq handle handoff.  Set by the
# executor before spawning workers so the worker knows where to write the handle.
_EDGE_HA_ACK_HANDLE_PATH_ENV = "VLLM_ASCEND_EDGE_HA_ACK_HANDLE_PATH"


def _edge_eher_enabled(vllm_config: VllmConfig) -> bool:
    """True iff EHER (edge hidden early-receive) is active on this edge node.

    EHER requires: edge role + PD enabled + `enable_edge_hidden_early_recv`.
    The sideband MQs are built whenever early-recv is on (gating only adds the
    ack MQ on top of the hint MQ).  Reads config the same way as
    ``_cloud_pd_enabled`` so the gate is stable across processes.
    """
    pc = getattr(vllm_config, "parallel_config", None)
    if pc is None:
        return False
    if not getattr(pc, "enable_edge_cloud", False):
        return False
    # edge role == is_edge_node (mirrors model_runner_v1 role inference).
    if not getattr(pc, "is_edge_node", False):
        return False
    ac = getattr(vllm_config, "additional_config", None) or {}
    ec = ac.get("edge_cloud_config", {}) if isinstance(ac, dict) else {}
    pd = ec.get("pd_separation", {}) if isinstance(ec, dict) else {}
    if not bool(pd.get("enabled", False)):
        return False
    return bool(pd.get("enable_edge_hidden_early_recv", False))


def _edge_eher_gating_enabled(vllm_config: VllmConfig) -> bool:
    """True iff P-tail scheduling gating is on (requires EHER)."""
    if not _edge_eher_enabled(vllm_config):
        return False
    ac = getattr(vllm_config, "additional_config", None) or {}
    ec = ac.get("edge_cloud_config", {}) if isinstance(ac, dict) else {}
    pd = ec.get("pd_separation", {}) if isinstance(ec, dict) else {}
    return bool(pd.get("enable_edge_hidden_early_recv_gating", True))


def _cloud_pd_enabled(vllm_config: VllmConfig) -> bool:
    """True iff this is a PD-separated cloud node.

    Cloud-side hidden early-receive (CHER) is a built-in part of PD-separation
    masking -- it is always on whenever PD-separation is enabled on the cloud,
    so this gate is simply "cloud role + PD enabled" (no separate flag).

    Reads ``enable_edge_cloud``/``is_edge_node`` from parallel_config (config-
    level fields set from --headless, available in every process) and PD-enabled
    from ``additional_config`` (a dict field that survives cross-process
    pickling).  It deliberately does NOT read ``scheduler_config
    .pd_separation_enabled``: that is a dynamic attribute platform threads at
    runtime, and the cloud executor runs ``_init_executor`` in the
    PassiveEngineCore process before that attribute is reliably present there.
    """
    pc = getattr(vllm_config, "parallel_config", None)
    if pc is None:
        return False
    if not getattr(pc, "enable_edge_cloud", False):
        return False
    # cloud role == not edge node (mirrors model_runner_v1 role inference).
    if getattr(pc, "is_edge_node", True):
        return False
    ac = getattr(vllm_config, "additional_config", None) or {}
    ec = ac.get("edge_cloud_config", {}) if isinstance(ac, dict) else {}
    pd = ec.get("pd_separation", {}) if isinstance(ec, dict) else {}
    return bool(pd.get("enabled", False))


class AscendMultiprocExecutor(MultiprocExecutor):
    def _init_executor(self) -> None:
        # Call self.shutdown at exit to clean up
        # and ensure workers will be terminated.
        self._finalizer = weakref.finalize(self, self.shutdown)
        self.is_failed = False
        self.failure_callback: FailureCallback | None = None

        tensor_parallel_size, pp_parallel_size, pcp_parallel_size = self._get_parallel_sizes()
        if not self.parallel_config.enable_edge_cloud:
            assert self.world_size == tensor_parallel_size * pp_parallel_size * pcp_parallel_size, (
                f"world_size ({self.world_size}) must be equal to the "
                f"tensor_parallel_size ({tensor_parallel_size}) x pipeline"
                f"_parallel_size ({pp_parallel_size}) x prefill_context"
                f"_parallel_size ({pcp_parallel_size}). "
            )

        # Set multiprocessing envs
        set_multiprocessing_worker_envs()

        # Multiprocessing-based executor does not support multi-node setting.
        # Since it only works for single node, we can use the loopback address
        # get_loopback_ip() for communication.
        distributed_init_method = get_distributed_init_method(get_loopback_ip(), get_open_port())
        self.rpc_broadcast_mq: MessageQueue | None = None
        scheduler_output_handle: Handle | None = None
        # Initialize worker and set up message queues for SchedulerOutputs
        # and ModelRunnerOutputs
        if self.parallel_config.node_rank_within_dp == 0:
            # For leader node within each dp rank,
            # each dp will have its own leader multiproc executor.
            max_chunk_bytes = envs.VLLM_MQ_MAX_CHUNK_BYTES_MB * 1024 * 1024
            self.rpc_broadcast_mq = MessageQueue(
                self.world_size,
                self.local_world_size,
                max_chunk_bytes=max_chunk_bytes,
                connect_ip=self.parallel_config.master_addr,
            )
            scheduler_output_handle = self.rpc_broadcast_mq.export_handle()
        elif envs.VLLM_PP_NON_LEADER_ENGINE_CORE:
            # For non-leader PP rank running with a passive EngineCore,
            # create a local rpc_broadcast_mq to broadcast SchedulerOutput
            # to local workers. Workers will use this MQ instead of
            # inner_dp_world_group to receive scheduler_output.
            max_chunk_bytes = envs.VLLM_MQ_MAX_CHUNK_BYTES_MB * 1024 * 1024
            self.rpc_broadcast_mq = MessageQueue(
                self.local_world_size,
                self.local_world_size,
                max_chunk_bytes=max_chunk_bytes,
                connect_ip=get_loopback_ip(),
            )
            scheduler_output_handle = self.rpc_broadcast_mq.export_handle()

        # [CHER] Cloud-side hidden early-receive: build a sideband MQ that
        # PassiveEC writes recv-hints to and a guard thread on the cloud
        # worker (the one issuing the cross-node irecv, i.e. PP NPU0 /
        # local_rank==0) drains.  Using a dedicated MQ (not the
        # rpc_broadcast_mq that busy_loop consumes) is essential: busy_loop is
        # single-threaded and blocks inside execute_model for a long P-middle
        # batch, so a hint queued there would not be dequeued until that batch
        # finishes -- defeating the overlap.  Always created on a PD-separated
        # cloud node (CHER is a built-in part of PD masking); left None and
        # hints are never sent otherwise.
        self.cloud_recv_hint_mq: MessageQueue | None = None
        if (
            self.parallel_config.enable_edge_cloud
            and not self.parallel_config.is_edge_node
            and _cloud_pd_enabled(self.vllm_config)
        ):
            # Small ring buffer: at most prefill_inflight_limit (<=2) P-middle
            # batches are in flight on the cloud at once, so at most that many
            # early-recv entries are ever useful -- the guard thread skips
            # posting once the cache holds that many (see start_early_irecv),
            # so it drains hints fast and the ring never fills.  8 slots x
            # 1KB absorb the burst when the guard briefly stalls on a post or
            # on _early_recv_lock; a larger ring would only mask a slow guard
            # and let the cache grow unbounded (the earlier OOM).
            self.cloud_recv_hint_mq = MessageQueue(
                1, 1, max_chunk_bytes=1024, max_chunks=8,
            )
            _hint_handle = self.cloud_recv_hint_mq.export_handle()
            os.environ[_CLOUD_RECV_HINT_MQ_ENV] = base64.b64encode(
                pickle.dumps(_hint_handle)
            ).decode()
            logger.info(
                "[CHER] cloud_recv_hint_mq created on cloud executor "
                "(local_world_size=%d)", self.local_world_size,
            )
        else:
            # Clean any stale handle so a non-cloud worker does not pick it up.
            os.environ.pop(_CLOUD_RECV_HINT_MQ_ENV, None)

        # [EHER] Edge-side hidden early-receive + P-tail gating.  Build the
        # sideband MQs on the EDGE leader:
        #   edge_recv_hint_mq : edge EngineCore -> edge worker guard thread
        #                        Standard CHER pattern: executor=writer (enqueues
        #                        hints), worker=reader (guard dequeues).
        #   ha_ack_mq          : edge worker guard thread -> edge EngineCore
        #                        REVERSE direction (worker=writer, EngineCore=
        #                        reader).  The MessageQueue API is strictly
        #                        unidirectional (creator is always writer), so
        #                        the WORKER creates ha_ack_mq and passes the
        #                        handle back to the executor via a temp file;
        #                        after wait_for_ready the executor calls
        #                        create_from_handle to get a reader proxy.
        self.edge_recv_hint_mq: MessageQueue | None = None
        self.ha_ack_mq: MessageQueue | None = None
        # Clean any stale env handles first.
        os.environ.pop(_EDGE_RECV_HINT_MQ_ENV, None)
        os.environ.pop(_EDGE_HA_ACK_MQ_ENV, None)
        os.environ.pop(_EDGE_HA_ACK_HANDLE_PATH_ENV, None)
        if (
            self.parallel_config.enable_edge_cloud
            and self.parallel_config.is_edge_node
            and _edge_eher_enabled(self.vllm_config)
        ):
            self.edge_recv_hint_mq = MessageQueue(
                1, 1, max_chunk_bytes=1024, max_chunks=8,
            )
            _hint_handle = self.edge_recv_hint_mq.export_handle()
            os.environ[_EDGE_RECV_HINT_MQ_ENV] = base64.b64encode(
                pickle.dumps(_hint_handle)
            ).decode()
            # ha_ack_mq: reverse direction — worker creates it (writer) and
            # writes its handle to a temp file.  Set the file path BEFORE
            # spawning workers so the worker's _init_message_queues can find
            # it via env and write the handle there.  After wait_for_ready
            # (workers have finished init), we read the handle back and call
            # create_from_handle to get a reader proxy.
            if _edge_eher_gating_enabled(self.vllm_config):
                _ack_path = os.path.join(
                    tempfile.gettempdir(),
                    f"vllm_eher_ha_ack_{os.getpid()}_{id(self)}.handle",
                )
                os.environ[_EDGE_HA_ACK_HANDLE_PATH_ENV] = _ack_path
            logger.info(
                "[EHER] edge_recv_hint_mq created on edge executor "
                "(local_world_size=%d, gating=%s)",
                self.local_world_size,
                _edge_eher_gating_enabled(self.vllm_config),
            )
        # Create workers
        context = get_mp_context()
        shared_worker_lock = context.Lock()
        unready_workers: list[UnreadyWorkerProcHandle] = []
        success = False
        try:
            if self.parallel_config.enable_edge_cloud:
                global_start_rank = (
                    0
                    if self.parallel_config.is_edge_node
                    else self.parallel_config.edge_npu_count
                )
            else:
                global_start_rank = self.local_world_size * self.parallel_config.node_rank_within_dp

            # When using fork, keep track of socket file descriptors that are
            # inherited by the worker, so that we can close them in subsequent
            # workers
            inherited_fds: list[int] | None = [] if context.get_start_method() == "fork" else None

            for local_rank in range(self.local_world_size):
                global_rank = global_start_rank + local_rank
                is_driver_worker = self._is_driver_worker(global_rank)
                unready_worker_handle = AscendWorkerProc.make_worker_process(
                    vllm_config=self.vllm_config,
                    local_rank=local_rank,
                    rank=global_rank,
                    distributed_init_method=distributed_init_method,
                    input_shm_handle=scheduler_output_handle,
                    shared_worker_lock=shared_worker_lock,
                    is_driver_worker=is_driver_worker,
                    inherited_fds=inherited_fds,
                )
                unready_workers.append(unready_worker_handle)
                if inherited_fds is not None:
                    inherited_fds.append(unready_worker_handle.death_writer.fileno())
                    inherited_fds.append(unready_worker_handle.ready_pipe.fileno())

            # Workers must be created before wait_for_ready to avoid
            # deadlock, since worker.init_device() does a device sync.

            # Wait for all local workers to be ready.
            self.workers = AscendWorkerProc.wait_for_ready(unready_workers)

            # [EHER ha_ack_mq] The worker created ha_ack_mq (reverse direction:
            # worker=writer, EngineCore=reader) and wrote its Handle to the
            # temp file set before spawning.  Read it back now that the worker
            # has finished init, and create a READER proxy on the executor.
            _ack_handle_path = os.environ.pop(
                _EDGE_HA_ACK_HANDLE_PATH_ENV, None
            )
            if _ack_handle_path is not None:
                try:
                    with open(_ack_handle_path, "rb") as _fh:
                        _ack_handle_raw = _fh.read()
                    _ack_handle = pickle.loads(_ack_handle_raw)
                    self.ha_ack_mq = MessageQueue.create_from_handle(
                        _ack_handle, 0,
                    )
                    os.unlink(_ack_handle_path)
                    logger.info(
                        "[EHER] ha_ack_mq reader proxy created on executor "
                        "(worker=writer, executor=reader)"
                    )
                except Exception:
                    logger.exception(
                        "[EHER] failed to read ha_ack_mq handle from %s; "
                        "gating acks will not be received (fallback timeout "
                        "will force-unlock P-tails)",
                        _ack_handle_path,
                    )
                    self.ha_ack_mq = None

            # Start background thread to monitor worker health if not in headless mode.
            if self.monitor_workers:
                self.start_worker_monitor()

            self.response_mqs = []
            # Only leader node have remote response mqs
            if self.parallel_config.node_rank_within_dp == 0 and (
                not self.parallel_config.enable_edge_cloud
                or self.parallel_config.is_edge_node
            ):
                for rank in range(self.world_size):
                    local_idx = rank - global_start_rank
                    if 0 <= local_idx < self.local_world_size:
                        local_message_queue = self.workers[local_idx].worker_response_mq
                        assert local_message_queue is not None
                        self.response_mqs.append(local_message_queue)
                    else:
                        remote_message_queue = self.workers[0].peer_worker_response_mqs[rank]
                        assert remote_message_queue is not None
                        self.response_mqs.append(remote_message_queue)
            elif envs.VLLM_PP_NON_LEADER_ENGINE_CORE:
                # For non-leader PP rank with passive EngineCore,
                # collect local worker response mqs only.
                for rank in range(self.local_world_size):
                    local_message_queue = self.workers[rank].worker_response_mq
                    assert local_message_queue is not None
                    self.response_mqs.append(local_message_queue)

            # Ensure message queues are ready. Will deadlock if re-ordered
            # Must be kept consistent with the WorkerProc.

            # Wait for all input mqs to be ready.
            if self.rpc_broadcast_mq is not None:
                self.rpc_broadcast_mq.wait_until_ready()
            # [CHER] cloud_recv_hint_mq is a fire-and-forget hint channel
            # (PassiveEC -> guard thread).  Do NOT wait_until_ready() here:
            # the reader (cloud worker local_rank==0) rebuilds it inside
            # _init_message_queues, which runs after distributed init; the
            # cloud worker's distributed init waits for the edge's NCCL
            # rendezvous, which only starts after the edge's PD TCPStore
            # (patch_engine_core.py line ~138) completes; and that TCPStore
            # waits for the cloud to write cloud_ip (passive_core.py line
            # ~863), which runs AFTER this executor init.  Waiting here would
            # deadlock the whole startup.  If the reader is not connected yet
            # when PassiveEC enqueues a hint, the hint is simply dropped
            # (ZMQ pub-sub) and execute_model falls back to sync recv; CHER
            # activates once the reader connects.
            # Wait for all remote response mqs to be ready.
            for response_mq in self.response_mqs:
                response_mq.wait_until_ready()
            self.futures_queue = deque[tuple[FutureWrapper, Callable]]()
            self._post_init_executor()

            success = True
        finally:
            if not success:
                # Clean up the worker procs if there was a failure.
                # Close death_writers first to signal workers to exit
                for uw in unready_workers:
                    if uw.death_writer is not None:
                        uw.death_writer.close()
                        uw.death_writer = None
                self._ensure_worker_termination([uw.proc for uw in unready_workers])

        self.output_rank = self._get_output_rank()

    def _get_parallel_sizes(self) -> tuple[int, int, int]:
        self.world_size = self.parallel_config.world_size
        if not self.parallel_config.enable_edge_cloud:
            assert self.world_size % self.parallel_config.nnodes_within_dp == 0, (
                f"global world_size ({self.parallel_config.world_size}) must be "
                f"divisible by nnodes_within_dp "
                f"({self.parallel_config.nnodes_within_dp}). "
            )
        self.local_world_size = self.parallel_config.local_world_size
        tp_size = self.parallel_config.tensor_parallel_size
        pp_size = self.parallel_config.pipeline_parallel_size
        pcp_size = self.parallel_config.prefill_context_parallel_size
        return tp_size, pp_size, pcp_size

    def _post_init_executor(self) -> None:
        pass

    def _is_driver_worker(self, rank: int) -> bool:
        if self.parallel_config.enable_edge_cloud:
            return rank == (
                0
                if self.parallel_config.is_edge_node
                else self.parallel_config.edge_npu_count
            )
        return rank % self.parallel_config.tensor_parallel_size == 0

    def _get_output_rank(self) -> int:
        if self.parallel_config.enable_edge_cloud:
            return 0
        return super()._get_output_rank()

    def _edge_local_only(self) -> bool:
        """Keep edge-owned control RPCs off the cross-node work queue."""
        return bool(
            getattr(self.parallel_config, "enable_edge_cloud", False)
            and getattr(self.parallel_config, "is_edge_node", False)
        )

    def clear_pending_edge_cloud_draft_for_req_ids(
        self,
        req_ids: set[str] | list[str],
        force_drop_task_ids: set[str] | list[str] = (),
    ) -> None:
        self.collective_rpc(
            "clear_pending_edge_cloud_draft_for_req_ids",
            args=(req_ids, force_drop_task_ids),
            # local_only=True keeps this RPC off the cross-node queue, so the
            # cloud workers never execute it and never reply.  Without
            # unique_reply_rank the engine would wait for replies from ALL
            # global ranks (edge + cloud response_mqs) and deadlock forever
            # on the first request finish.
            unique_reply_rank=self.output_rank,
            local_only=self._edge_local_only(),
        )


class AscendWorkerProc(WorkerProc):
    def _init_message_queues(
        self, input_shm_handle: Handle, vllm_config: VllmConfig
    ) -> None:
        if vllm_config.parallel_config.nnodes_within_dp == 1:
            # Single-node: use local MQ
            self.rpc_broadcast_mq = MessageQueue.create_from_handle(
                input_shm_handle, self.worker.rank
            )
            self.worker_response_mq = MessageQueue(1, 1)
            self.peer_response_handles = []
            self.local_rpc_broadcast_mq = None
            self.local_worker_response_mq = None
        elif envs.VLLM_PP_NON_LEADER_ENGINE_CORE:
            # Non-leader PP rank with passive EngineCore:
            # Dual MQ — local MQ for passive enginecore handshake +
            # cross-node MQ for actual communication with pp rank0.
            from vllm.distributed.parallel_state import get_inner_dp_world_group
            # Local MQs (for passive enginecore handshake only)
            self.local_rpc_broadcast_mq = MessageQueue.create_from_handle(
                input_shm_handle, self.local_rank
            )
            self.local_worker_response_mq = MessageQueue(1, 1)
            self.local_peer_response_handles: list = []
            # Cross-node MQs (for actual work with pp rank0)
            self.rpc_broadcast_mq = get_inner_dp_world_group().create_mq_broadcaster(
                external_writer_handle=None,
                blocking=False,
            )
            self.worker_response_mq, self.peer_response_handles = (
                get_inner_dp_world_group().create_single_reader_mq_broadcasters(
                    reader_rank_in_group=0, vllm_config=vllm_config
                )
            )
        else:
            # Delegate to parent class for the inner_dp_world_group path
            super()._init_message_queues(input_shm_handle, vllm_config)
        # cloud_recv_hint_mq is rebuilt by the base-class wrapper
        # (_cher_init_message_queues applied below) which runs for plain
        # WorkerProc instances that worker_main actually creates.  Initialize
        # the attribute here for the AscendWorkerProc path (if ever taken).
        self.cloud_recv_hint_mq: MessageQueue | None = None
        # [EHER] Edge sideband MQs, rebuilt by the chained _eher wrapper below.
        if not hasattr(self, "edge_recv_hint_mq"):
            self.edge_recv_hint_mq: MessageQueue | None = None
        if not hasattr(self, "ha_ack_mq"):
            self.ha_ack_mq: MessageQueue | None = None

    @staticmethod
    def make_worker_process(
        vllm_config: VllmConfig,
        local_rank: int,
        rank: int,
        distributed_init_method: str,
        input_shm_handle,  # Receive SchedulerOutput
        shared_worker_lock: LockType,
        is_driver_worker: bool = False,
        inherited_fds: list[int] | None = None,
    ) -> UnreadyWorkerProcHandle:
        context = get_mp_context()
        # Ready pipe to communicate readiness from child to parent
        ready_reader, ready_writer = context.Pipe(duplex=False)
        # Death pipe to let child detect parent process exit
        death_reader, death_writer = context.Pipe(duplex=False)
        if inherited_fds is not None:
            inherited_fds = inherited_fds.copy()
            inherited_fds.extend((ready_reader.fileno(), death_writer.fileno()))
        process_kwargs = {
            "vllm_config": vllm_config,
            "local_rank": local_rank,
            "rank": rank,
            "distributed_init_method": distributed_init_method,
            "input_shm_handle": input_shm_handle,
            "ready_pipe": ready_writer,
            "death_pipe": death_reader,
            "shared_worker_lock": shared_worker_lock,
            "is_driver_worker": is_driver_worker,
            # Have the worker close parent end of this worker's pipes too
            "inherited_fds": inherited_fds if inherited_fds is not None else [],
        }
        # Run EngineCore busy loop in background process.
        proc = context.Process(
            target=WorkerProc.worker_main,
            kwargs=process_kwargs,
            name=f"VllmWorker-{rank}",
            daemon=False,
        )

        proc.start()
        # Close child ends of pipes here in the parent
        ready_writer.close()
        death_reader.close()
        # Keep death_writer open in parent - when parent exits,
        # death_reader in child will get EOFError
        return UnreadyWorkerProcHandle(proc, rank, ready_reader, death_writer)


vllm.v1.executor.multiproc_executor.MultiprocExecutor = AscendMultiprocExecutor

# [CHER] Wrap the ORIGINAL WorkerProc._init_message_queues to rebuild
# cloud_recv_hint_mq on the cloud worker.  We must wrap the base class
# directly (AscendWorkerProc.__bases__[0]) and capture the original method
# BEFORE any replacement, because:
#  - worker_main (spawned) resolves `WorkerProc` to the original base class,
#    NOT a module-level name we might replace, so class-replacement tricks
#    don't reach the plain WorkerProc instances worker_main creates;
#  - capturing _orig after `WorkerProc = AscendWorkerProc` would grab the
#    subclass's own _init_message_queues, causing infinite recursion when the
#    subclass calls super().
# AscendWorkerProc._init_message_queues is kept for the executor-side path
# (it also rebuilds); the wrapper early-returns if cloud_recv_hint_mq is
# already set, so there is no double-rebuild / clobber.
_OrigWorkerProc = AscendWorkerProc.__bases__[0]
_orig_init_message_queues = _OrigWorkerProc._init_message_queues


def _cher_init_message_queues(self, input_shm_handle, vllm_config):
    _orig_init_message_queues(self, input_shm_handle, vllm_config)
    # Only rebuild if not already done by AscendWorkerProc._init_message_queues.
    if getattr(self, "cloud_recv_hint_mq", None) is not None:
        return
    self.cloud_recv_hint_mq = None
    if not (
        envs.VLLM_PP_NON_LEADER_ENGINE_CORE
        and self.local_rank == 0
        and not vllm_config.parallel_config.is_edge_node
        and _cloud_pd_enabled(vllm_config)
    ):
        return
    _raw = os.environ.get(_CLOUD_RECV_HINT_MQ_ENV)
    if _raw is None:
        return
    try:
        _handle = pickle.loads(base64.b64decode(_raw))
        self.cloud_recv_hint_mq = MessageQueue.create_from_handle(
            _handle, self.local_rank
        )
        logger.info(
            "[CHER] cloud_recv_hint_mq rebuilt on worker local_rank=%d",
            self.local_rank,
        )
    except Exception:
        logger.exception(
            "[CHER] failed to rebuild cloud_recv_hint_mq on worker "
            "local_rank=%d; CHER will fall back to sync recv",
            self.local_rank,
        )
        self.cloud_recv_hint_mq = None


_OrigWorkerProc._init_message_queues = _cher_init_message_queues


# [EHER] Edge-side mirror of the CHER wrapper: rebuild edge_recv_hint_mq and
# (when gating is on) ha_ack_mq on the edge worker (local_rank==0).  Same
# rationale as the cloud wrapper: the spawned WorkerProc resolves to the base
# class, so we patch _OrigWorkerProc._init_message_queues a SECOND time by
# chaining after the CHER wrapper.  Keep both rebuilds idempotent so the order
# (CHER then EHER) and a possible AscendWorkerProc early-set both work.
_eher_orig_init_message_queues = _OrigWorkerProc._init_message_queues


def _eher_init_message_queues(self, input_shm_handle, vllm_config):
    _eher_orig_init_message_queues(self, input_shm_handle, vllm_config)
    if getattr(self, "edge_recv_hint_mq", None) is not None:
        return
    self.edge_recv_hint_mq = None
    self.ha_ack_mq = None
    # Edge worker rebuilds the sideband MQs only on the leader (local_rank==0
    # issues the cross-node irecv) and only when the edge executor built them.
    # The edge runs WITHOUT VLLM_PP_NON_LEADER_ENGINE_CORE (edge is the PP
    # rank-0 of the shared-model group), so unlike CHER we do not gate on it.
    if not (
        vllm_config.parallel_config.enable_edge_cloud
        and vllm_config.parallel_config.is_edge_node
        and self.local_rank == 0
        and _edge_eher_enabled(vllm_config)
    ):
        return
    _hint_raw = os.environ.get(_EDGE_RECV_HINT_MQ_ENV)
    if _hint_raw is not None:
        try:
            _hint_handle = pickle.loads(base64.b64decode(_hint_raw))
            self.edge_recv_hint_mq = MessageQueue.create_from_handle(
                _hint_handle, self.local_rank
            )
            logger.info(
                "[EHER] edge_recv_hint_mq rebuilt on worker local_rank=%d",
                self.local_rank,
            )
        except Exception:
            logger.exception(
                "[EHER] failed to rebuild edge_recv_hint_mq on worker "
                "local_rank=%d; EHER will fall back to sync recv",
                self.local_rank,
            )
            self.edge_recv_hint_mq = None
    # ha_ack_mq: reverse direction (worker=writer, EngineCore=reader).
    # The MessageQueue API is strictly unidirectional (creator is always
    # writer), so the WORKER creates it and passes the Handle back to the
    # executor via a temp file (path in _EDGE_HA_ACK_HANDLE_PATH_ENV); the
    # executor then calls create_from_handle to get a reader proxy.
    if _edge_eher_gating_enabled(vllm_config):
        _ack_path = os.environ.get(_EDGE_HA_ACK_HANDLE_PATH_ENV)
        if _ack_path is None:
            logger.warning(
                "[EHER] gating on but ha_ack handle path env missing; "
                "P-tails will force-unlock after fallback timeout"
            )
        else:
            try:
                self.ha_ack_mq = MessageQueue(
                    1, 1, max_chunk_bytes=1024, max_chunks=8,
                )
                _ack_handle = self.ha_ack_mq.export_handle()
                with open(_ack_path, "wb") as _fh:
                    _fh.write(pickle.dumps(_ack_handle))
                logger.info(
                    "[EHER] ha_ack_mq created on worker local_rank=%d "
                    "(worker=writer, handle written to %s)",
                    self.local_rank, _ack_path,
                )
            except Exception:
                logger.exception(
                    "[EHER] failed to create ha_ack_mq on worker "
                    "local_rank=%d; gating acks will be lost (force-unlock "
                    "fallback applies)",
                    self.local_rank,
                )
                self.ha_ack_mq = None

        # [EHER] Start the guard thread on the edge.  The upstream guard-start
        # trigger (_init_worker line 767) only fires when ``cloud_recv_hint_mq``
        # is not None (CHER), which is always None on the edge.  Call the
        # wrapper (which checks idempotency + the dual-MQ condition) to start
        # the guard on the edge.
        if getattr(self, "edge_recv_hint_mq", None) is not None:
            self._start_early_recv_guard()


_OrigWorkerProc._init_message_queues = _eher_init_message_queues


# [EHER §十五.4] Extend the early-recv guard thread to also serve the edge:
#   - drain ``edge_recv_hint_mq`` (edge EngineCore -> guard) and post the
#     cloud->edge irecv early (mirrors CHER's cloud side);
#   - when gating is on, run a NON-BLOCKING ``is_completed()`` probe over the
#     posted edge early-recv entries and, for each newly-complete one, enqueue a
#     recv-done ack to ``ha_ack_mq`` (edge guard -> edge EngineCore) so the
#     gated P-tail is unlocked for scheduling.
# The guard thread NEVER calls ``wait()`` (HCCL cross-thread wait on a hidden-
# channel irecv while busy_loop isends on that channel deadlocks -- see the
# upstream ``_early_recv_guard_loop`` docstring). ``is_completed()`` is a poll,
# not a block, so it does not stall the busy_loop isend. Gating is feasible
# precisely because the upstream ``Handle`` Protocol exposes ``is_completed()``
# (vllm/vllm/distributed/parallel_state.py: class Handle).
# We wrap _OrigWorkerProc (the base class worker_main actually instantiates),
# calling the original loop body for the CHER path then appending the EHER path.
_eher_orig_start_early_recv_guard = _OrigWorkerProc._start_early_recv_guard
_eher_orig_early_recv_guard_loop = _OrigWorkerProc._early_recv_guard_loop


def _eher_start_early_recv_guard(self) -> None:
    """Start the guard thread if either sideband hint MQ exists (CHER or EHER).

    The upstream gate (``cloud_recv_hint_mq is not None``) only starts it on
    the cloud; this wrapper also starts it on the edge when ``edge_recv_hint_mq``
    was rebuilt, so the same single guard thread serves both directions.
    """
    has_cloud = getattr(self, "cloud_recv_hint_mq", None) is not None
    has_edge = getattr(self, "edge_recv_hint_mq", None) is not None
    if not (has_cloud or has_edge):
        # No sideband MQ on this worker -> upstream guard returns early via the
        # ``hasattr(worker, "start_early_irecv")`` check anyway; call it so the
        # upstream idempotency flag is set consistently.
        _eher_orig_start_early_recv_guard(self)
        return
    if getattr(self, "_early_recv_guard_started", False):
        return
    worker = getattr(self, "worker", None)
    if worker is None or not hasattr(worker, "start_early_irecv"):
        return
    import threading
    self._early_recv_guard_started = True
    self._early_recv_guard_shutdown = False
    self._early_recv_guard_thread = threading.Thread(
        target=self._early_recv_guard_loop,
        name="cher-eher-early-recv-guard",
        daemon=True,
    )
    self._early_recv_guard_thread.start()
    logger.info(
        "[CHER/EHER] early-irecv guard thread started "
        "(cloud_mq=%s edge_mq=%s ha_ack_mq=%s)",
        has_cloud, has_edge,
        getattr(self, "ha_ack_mq", None) is not None,
    )


def _eher_early_recv_guard_loop(self) -> None:
    """Guard loop: CHER path (drain cloud hints + post) + EHER path
    (drain edge hints + post + non-blocking test -> ack).

    Wraps the upstream loop: it calls the original body first (which posts any
    cloud recv-hints), then runs the EHER additions.  No wait() anywhere.
    """
    # --- device context (same as upstream) ---
    try:
        from vllm.platforms import current_platform
        worker = getattr(self, "worker", None)
        if worker is not None and hasattr(worker, "device"):
            current_platform.set_device(worker.device)
    except Exception:
        logger.exception("[CHER/EHER] guard thread failed to set device")

    edge_hint_mq = getattr(self, "edge_recv_hint_mq", None)
    ha_ack_mq = getattr(self, "ha_ack_mq", None)
    worker = getattr(self, "worker", None)
    # Gating probes are only meaningful when the ack channel exists; otherwise
    # the EngineCore unlocks via the fallback timeout and we skip probing.
    gating_on = ha_ack_mq is not None

    import time
    while not getattr(self, "_early_recv_guard_shutdown", False):
        did_something = False

        # [CHER] Drain cloud recv-hints + post (upstream body, isolated).
        cloud_mq = getattr(self, "cloud_recv_hint_mq", None)
        if cloud_mq is not None:
            while True:
                try:
                    method, args, _kw, _out = cloud_mq.dequeue(timeout=0)
                except TimeoutError:
                    break
                except Exception:
                    logger.exception("[CHER] guard dequeue error")
                    break
                if method == b"pp_recv_hint" and args:
                    try:
                        worker.start_early_irecv(args[0])
                        did_something = True
                    except Exception:
                        logger.exception("[CHER] start_early_irecv failed")

        # [EHER] Drain edge recv-hints + post (mirrors the cloud path).
        if edge_hint_mq is not None:
            while True:
                try:
                    method, args, _kw, _out = edge_hint_mq.dequeue(timeout=0)
                except TimeoutError:
                    break
                except Exception:
                    logger.exception("[EHER] guard dequeue error")
                    break
                if method == b"pp_recv_hint" and args:
                    try:
                        worker.start_early_irecv(args[0])
                        did_something = True
                    except Exception:
                        logger.exception("[EHER] start_early_irecv failed")

        # [EHER §十五.4] Non-blocking completion probe -> post ack (gating).
        # Does NOT wait(); only acks entries that are already complete so the
        # gated P-tail can be unlocked.  Skipped entirely when gating is off.
        if gating_on and worker is not None and hasattr(
            worker, "test_unacked_early_recv"
        ):
            try:
                ready = worker.test_unacked_early_recv()
            except Exception:
                logger.exception("[EHER] test_unacked_early_recv failed")
                ready = []
            for ht, _entry in ready:
                try:
                    _ack = {
                        "__ha_ack__": True,
                        "head_token": ht,
                        "direction": "received",
                    }
                    ha_ack_mq.enqueue(
                        (b"ha_ack", (_ack,), {}, None)
                    )
                    worker.mark_early_recv_acked(ht)
                    did_something = True
                    logger.debug(
                        "[EHER] posted ha_ack head_token=%s", ht,
                    )
                except Exception:
                    logger.exception(
                        "[EHER] ha_ack enqueue failed head_token=%s", ht,
                    )

        if not did_something:
            time.sleep(0.00005)


_OrigWorkerProc._start_early_recv_guard = _eher_start_early_recv_guard
_OrigWorkerProc._early_recv_guard_loop = _eher_early_recv_guard_loop

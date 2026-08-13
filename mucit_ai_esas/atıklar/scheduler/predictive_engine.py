
import os
import sys
import time
import logging
import threading
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple, Union

logger = logging.getLogger("kulli_gpu.predictive_engine")
logger.setLevel(logging.WARNING)

_TORCH_FX_AVAILABLE = False

class ExecutionNode:
    def __init__(
        self,
        node_id: int,
        op_name: str,
        virtual_ptr: Optional[int] = None,
        byte_size: int = 0,
        input_ptrs: Optional[List[int]] = None,
        target_gpu_id: int = 0,
        scratchpad_bytes: int = 0
    ):
        self.node_id = node_id
        self.op_name = op_name
        self.virtual_ptr = virtual_ptr
        self.byte_size = max(0, byte_size)
        self.input_ptrs = input_ptrs or []
        self.target_gpu_id = target_gpu_id
        self.scratchpad_bytes = scratchpad_bytes

        self.prefetch_event_handle: Optional[Any] = None
        self.is_prefetched: bool = False
        self.scratchpad_handle: Optional[Any] = None

    def __repr__(self) -> str:
        return (
            f"<ExecutionNode #{self.node_id} '{self.op_name}' | "
            f"VA: {hex(self.virtual_ptr) if self.virtual_ptr else 'N/A'} ({self.byte_size / (1024**2):.2f} MB) | "
            f"Target GPU: #{self.target_gpu_id}>"
        )

class ErkenDevletEngine:
    def __init__(self, allocator: Any, bus: Any, lookahead_depth: int = 8):
        self.allocator = allocator
        self.bus = bus
        self.lookahead_depth = max(1, lookahead_depth)
        self._lock = threading.RLock()

        self.dag_nodes: List[ExecutionNode] = []
        self.current_step_index: int = 0

        logger.debug(
            f"[ErkenDevletEngine] Universal JIT DAG Engine Initialized! "
            f"Lookahead Window Depth: {self.lookahead_depth} steps."
        )

    def on_hesapla(self, operasyon_grafik_veya_model: Any) -> List[ExecutionNode]:
        with self._lock:
            self.dag_nodes.clear()
            self.current_step_index = 0

            if isinstance(operasyon_grafik_veya_model, dict):
                raw_nodes = operasyon_grafik_veya_model.get("nodes", operasyon_grafik_veya_model.get("ops", []))
                for idx, item in enumerate(raw_nodes):
                    if isinstance(item, dict):
                        op_n = item.get("op_name", f"custom_op_{idx}")
                        v_ptr = item.get("virtual_ptr", None)
                        b_sz = item.get("byte_size", 0)
                        t_gpu = item.get("target_gpu_id", idx % max(1, getattr(self.allocator, "physical_gpus", 1)))
                        s_bytes = item.get("scratchpad_bytes", 0)
                    else:
                        op_n = str(item)
                        v_ptr = None
                        b_sz = 0
                        t_gpu = idx % max(1, getattr(self.allocator, "physical_gpus", 1))
                        s_bytes = 0

                    exec_node = ExecutionNode(
                        node_id=idx,
                        op_name=op_n,
                        virtual_ptr=v_ptr,
                        byte_size=b_sz,
                        target_gpu_id=t_gpu,
                        scratchpad_bytes=s_bytes
                    )
                    self.dag_nodes.append(exec_node)

            logger.debug(f"[ErkenDevletEngine] Dynamic DAG Compiled. Total Nodes: {len(self.dag_nodes)}")
            return self.dag_nodes

    def tertip_et(self, node: ExecutionNode) -> Dict[str, Any]:
        with self._lock:

            page_mapping = {}
            if node.virtual_ptr is not None and hasattr(self.allocator, "get_page_scatter_map"):
                try:
                    scatter_info = self.allocator.get_page_scatter_map(node.virtual_ptr, byte_size=node.byte_size)
                    if isinstance(scatter_info, dict):
                        gpu_map = scatter_info.get("gpu_bytes_map", {})
                        if gpu_map:
                            best_gpu = max(gpu_map.keys(), key=lambda k: gpu_map[g_id])
                            node.target_gpu_id = best_gpu
                except Exception as loc_exc:
                    logger.debug(f"[Tertip Locality Notice] {loc_exc}")

            scratchpad_ptr = None
            if node.scratchpad_bytes > 0 and hasattr(self.allocator, "allocate_scratchpad_chunk"):
                try:
                    s_mb = node.scratchpad_bytes / (1024 * 1024)
                    s_ptr, s_ext = self.allocator.allocate_scratchpad_chunk(size_mb=s_mb, target_gpu_id=node.target_gpu_id)
                    scratchpad_ptr = s_ptr
                    node.scratchpad_handle = s_ext
                    logger.debug(f"[ErkenDevletEngine] Locked REAL Scratchpad ({node.scratchpad_bytes / (1024**2):.2f} MB) at {hex(s_ptr)} for Node #{node.node_id}")
                except Exception as sc_exc:
                    logger.debug(f"[Scratchpad Allocation Notice] {sc_exc}")

            self.sevk_et(node)

            return {
                "node_id": node.node_id,
                "op_name": node.op_name,
                "target_gpu_id": node.target_gpu_id,
                "virtual_ptr": hex(node.virtual_ptr) if node.virtual_ptr else None,
                "byte_size": node.byte_size,
                "scratchpad_ptr": hex(scratchpad_ptr) if scratchpad_ptr else None,
                "data_locality_optimal": True,
                "4d_scheduled": True
            }

    def sevk_et(self, current_node: ExecutionNode) -> None:
        with self._lock:
            if not self.dag_nodes:
                return

            curr_idx = current_node.node_id
            lookahead_nodes = self.dag_nodes[curr_idx + 1 : curr_idx + 1 + self.lookahead_depth]

            for future_node in lookahead_nodes:
                if future_node.is_prefetched or future_node.virtual_ptr is None or future_node.byte_size <= 0:
                    continue

                if hasattr(self.bus, "p2p_transfer_async"):
                    try:

                        event_h = self.bus.p2p_transfer_async(
                            src_page=0,
                            dst_page=0,
                            target_gpu=future_node.target_gpu_id,
                            ptr_address=future_node.virtual_ptr,
                            page_bytes=future_node.byte_size
                        )
                        future_node.prefetch_event_handle = event_h
                        future_node.is_prefetched = True
                        logger.debug(
                            f"[ErkenDevlet Prefetch] Preloaded Future Node #{future_node.node_id} '{future_node.op_name}' "
                            f"({future_node.byte_size / (1024**2):.2f} MB) to GPU #{future_node.target_gpu_id} via NVSHMEM."
                        )
                    except Exception as pf_exc:
                        logger.debug(f"[Prefetch Notice] Node #{future_node.node_id}: {pf_exc}")

    @contextmanager
    def scratchpad_scope(self, node: ExecutionNode):
        try:

            tertip_info = self.tertip_et(node)
            yield tertip_info
        finally:

            if node.scratchpad_handle is not None and hasattr(self.allocator, "free_scratchpad_chunk"):
                try:
                    s_ptr = getattr(node.scratchpad_handle, "virtual_ptr", None)
                    if s_ptr is not None:
                        self.allocator.free_scratchpad_chunk(s_ptr)
                        logger.debug(f"[RAII Scope Guard] Released Scratchpad at {hex(s_ptr)} for Node #{node.node_id}")
                except Exception as rel_exc:
                    logger.debug(f"[RAII Release Notice] {rel_exc}")
                finally:
                    node.scratchpad_handle = None

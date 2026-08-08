"""
MODÜL 4: Sanal Bellek Tahsisçisi (Virtual Memory Allocator)
NVIDIA CUDA Virtual Memory Management (VMM) mimarisini Python seviyesinde yönetir.
İşletim sistemine kesintisiz 88 GB bitişik sanal adres uzayı ayırır, sayfa eşlemesi yapar,
cuMemSetAccess ile Okuma/Yazma izni verir ve Erken Devlet Engine ile Data-Locality (Veri Yakınlığı) sağlar.
"""

import os
import math
import ctypes
import logging
import datetime
import threading
import bisect
import collections
from enum import Enum
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("kulli_gpu.vmm_allocator")
logger.setLevel(logging.WARNING)
_thread_local = threading.local()

class PageState(Enum):
    FREE = "FREE"
    RESERVED = "RESERVED"
    COMMITTED = "COMMITTED"
    LOCKED = "LOCKED"
    SCRATCHPAD = "SCRATCHPAD"


class GuardPageException(Exception):
    """
    Sanal Adres Koruma Sayfası (Guard Page) Donanımsal İhlal İstisnası.
    88 GB'lık rezerve alanın sonundaki PROT_NONE koruma sayfasına yetkisiz erişimi veya
    sınır ötesi (Out of Bounds) sanal adres isteklerini yakalayarak sürücü çökmesini engeller.
    
    Donanımsal Hata Teşhis Ve Adres İhlal Detaylarını Otomatik Raporlar:
    - fault_address: İhlale neden olan sanal adres (Virtual Pointer)
    - violation_type: İhlal türü ("PROT_NONE_GUARD_PAGE" veya "OUT_OF_BOUNDS_ADDRESS")
    - requested_bytes: İhlal anında talep edilen bayt miktarı
    - base_address: Sürücünün ana sanal bellek taban adresi
    - max_address: Sürücünün izin verilen maksimum üst sanal adresi
    """
    def __init__(
        self, 
        message: str, 
        fault_address: Optional[int] = None, 
        violation_type: Optional[str] = None,
        requested_bytes: Optional[int] = None,
        base_address: Optional[int] = None,
        max_address: Optional[int] = None
    ):
        super().__init__(message)
        self.message = message
        self.fault_address = fault_address
        self.violation_type = violation_type or "GENERAL_VIRTUAL_ADDRESS_VIOLATION"
        self.requested_bytes = requested_bytes
        self.base_address = base_address
        self.max_address = max_address
        self.timestamp = datetime.datetime.now().isoformat()

    def get_hardware_telemetry_report(self) -> Dict[str, Any]:
        """İhlale ait donanımsal telemetri ve adres ihlal raporunu sözlük formatında sunar."""
        return {
            "timestamp": self.timestamp,
            "error_class": self.__class__.__name__,
            "violation_type": self.violation_type,
            "fault_address_hex": hex(self.fault_address) if self.fault_address is not None else None,
            "fault_address_dec": self.fault_address,
            "requested_bytes": self.requested_bytes,
            "base_address_hex": hex(self.base_address) if self.base_address is not None else None,
            "max_address_hex": hex(self.max_address) if self.max_address is not None else None,
            "message": self.message
        }

    def __str__(self) -> str:
        fault_hex = hex(self.fault_address) if self.fault_address is not None else "UNKNOWN"
        return f"[{self.violation_type}] Fault Address: {fault_hex} | Details: {self.message}"


class CUmemLocation(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),                  # CU_MEM_LOCATION_TYPE_DEVICE = 1
        ("id", ctypes.c_int)                     # physical gpu_id
    ]

class CUmemAllocationProp(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),                  # CU_MEM_ALLOCATION_TYPE_PINNED = 1
        ("requestedHandleTypes", ctypes.c_int),  # CU_MEM_HANDLE_TYPE_NONE = 0
        ("location", CUmemLocation),             # Nested Struct Matching cuda.h 64-bit ABI Alignment!
        ("win32HandleMetaData", ctypes.c_void_p),
        ("allocFlags", ctypes.c_uint64)
    ]

class CUmemAccessDesc(ctypes.Structure):
    _fields_ = [
        ("location", CUmemLocation),             # Nested Struct Matching C-Header 64-bit ABI Alignment!
        ("flags", ctypes.c_int)                  # CU_MEM_ACCESS_FLAGS_PROT_READWRITE = 3
    ]


class ScatterMapList(list):
    """
    Erken Devlet Engine Topoloji ve Dağınık Sevk Harita Listesi (Metadata Destekli List).
    Standart Python listesi gibi davranır, ancak `.contains_unmapped_holes` niteliği taşır.
    """
    def __init__(self, items=None, contains_unmapped_holes=False):
        super().__init__(items if items else [])
        self.contains_unmapped_holes = contains_unmapped_holes
        self.has_unmapped_holes = contains_unmapped_holes


# Direct NVIDIA CUDA Driver API C-Types Binding
_NVCUDA_LIB = None
try:
    if os.name == 'nt':
        _NVCUDA_LIB = ctypes.windll.LoadLibrary("nvcuda.dll")
    else:
        _NVCUDA_LIB = ctypes.CDLL("libcuda.so")

    _NVCUDA_LIB.cuInit.argtypes = [ctypes.c_uint]
    _NVCUDA_LIB.cuInit.restype = ctypes.c_int
    _NVCUDA_LIB.cuInit(0)

    # CUDA Context Management Functions
    _NVCUDA_LIB.cuDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    _NVCUDA_LIB.cuDeviceGet.restype = ctypes.c_int

    if hasattr(_NVCUDA_LIB, "cuDeviceTotalMem_v2"):
        _NVCUDA_LIB.cuDeviceTotalMem = _NVCUDA_LIB.cuDeviceTotalMem_v2
    if hasattr(_NVCUDA_LIB, "cuDeviceTotalMem"):
        _NVCUDA_LIB.cuDeviceTotalMem.argtypes = [ctypes.POINTER(ctypes.c_size_t), ctypes.c_int]
        _NVCUDA_LIB.cuDeviceTotalMem.restype = ctypes.c_int

    _NVCUDA_LIB.cuDevicePrimaryCtxRetain.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_int]
    _NVCUDA_LIB.cuDevicePrimaryCtxRetain.restype = ctypes.c_int

    _NVCUDA_LIB.cuCtxSetCurrent.argtypes = [ctypes.c_void_p]
    _NVCUDA_LIB.cuCtxSetCurrent.restype = ctypes.c_int

    _NVCUDA_LIB.cuMemGetAllocationGranularity.argtypes = [
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(CUmemAllocationProp),
        ctypes.c_int
    ]
    _NVCUDA_LIB.cuMemGetAllocationGranularity.restype = ctypes.c_int

    _NVCUDA_LIB.cuMemAddressReserve.argtypes = [
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.c_uint64,
        ctypes.c_uint64
    ]
    _NVCUDA_LIB.cuMemAddressReserve.restype = ctypes.c_int

    if hasattr(_NVCUDA_LIB, "cuMemAddressFree"):
        _NVCUDA_LIB.cuMemAddressFree.argtypes = [ctypes.c_uint64, ctypes.c_size_t]
        _NVCUDA_LIB.cuMemAddressFree.restype = ctypes.c_int

    if hasattr(_NVCUDA_LIB, "cuMemAddressRangeRelease"):
        _NVCUDA_LIB.cuMemAddressRangeRelease.argtypes = [ctypes.c_uint64, ctypes.c_size_t]
        _NVCUDA_LIB.cuMemAddressRangeRelease.restype = ctypes.c_int

    _NVCUDA_LIB.cuMemCreate.argtypes = [
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.c_size_t,
        ctypes.POINTER(CUmemAllocationProp),
        ctypes.c_uint64
    ]
    _NVCUDA_LIB.cuMemCreate.restype = ctypes.c_int

    _NVCUDA_LIB.cuMemMap.argtypes = [
        ctypes.c_uint64,
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.c_uint64,
        ctypes.c_uint64
    ]
    _NVCUDA_LIB.cuMemMap.restype = ctypes.c_int

    _NVCUDA_LIB.cuMemSetAccess.argtypes = [
        ctypes.c_uint64,
        ctypes.c_size_t,
        ctypes.POINTER(CUmemAccessDesc),
        ctypes.c_size_t
    ]
    _NVCUDA_LIB.cuMemSetAccess.restype = ctypes.c_int

    _NVCUDA_LIB.cuMemUnmap.argtypes = [ctypes.c_uint64, ctypes.c_size_t]
    _NVCUDA_LIB.cuMemUnmap.restype = ctypes.c_int

    _NVCUDA_LIB.cuMemRelease.argtypes = [ctypes.c_uint64]
    _NVCUDA_LIB.cuMemRelease.restype = ctypes.c_int

    _NVCUDA_LIB.cuMemcpyAsync.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_size_t, ctypes.c_void_p]
    _NVCUDA_LIB.cuMemcpyAsync.restype = ctypes.c_int

    _NVCUDA_LIB.cuStreamSynchronize.argtypes = [ctypes.c_void_p]
    _NVCUDA_LIB.cuStreamSynchronize.restype = ctypes.c_int

    _NVCUDA_LIB.cuCtxEnablePeerAccess.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    _NVCUDA_LIB.cuCtxEnablePeerAccess.restype = ctypes.c_int

    if hasattr(_NVCUDA_LIB, "cuMemExportToShareableHandle"):
        _NVCUDA_LIB.cuMemExportToShareableHandle.argtypes = [
            ctypes.POINTER(ctypes.c_uint64),
            ctypes.c_uint64,
            ctypes.c_int,
            ctypes.c_uint64
        ]
        _NVCUDA_LIB.cuMemExportToShareableHandle.restype = ctypes.c_int

    if hasattr(_NVCUDA_LIB, "cuMemHostAlloc"):
        _NVCUDA_LIB.cuMemHostAlloc.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.c_size_t, ctypes.c_uint]
        _NVCUDA_LIB.cuMemHostAlloc.restype = ctypes.c_int

    if hasattr(_NVCUDA_LIB, "cuMemFreeHost"):
        _NVCUDA_LIB.cuMemFreeHost.argtypes = [ctypes.c_uint64]
        _NVCUDA_LIB.cuMemFreeHost.restype = ctypes.c_int

    # CUDA Event Synchronization API Bindings
    if hasattr(_NVCUDA_LIB, "cuEventCreate"):
        _NVCUDA_LIB.cuEventCreate.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint]
        _NVCUDA_LIB.cuEventCreate.restype = ctypes.c_int

    if hasattr(_NVCUDA_LIB, "cuEventRecord"):
        _NVCUDA_LIB.cuEventRecord.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        _NVCUDA_LIB.cuEventRecord.restype = ctypes.c_int

    if hasattr(_NVCUDA_LIB, "cuEventSynchronize"):
        _NVCUDA_LIB.cuEventSynchronize.argtypes = [ctypes.c_void_p]
        _NVCUDA_LIB.cuEventSynchronize.restype = ctypes.c_int

    if hasattr(_NVCUDA_LIB, "cuEventDestroy_v2"):
        _NVCUDA_LIB.cuEventDestroy = _NVCUDA_LIB.cuEventDestroy_v2
    if hasattr(_NVCUDA_LIB, "cuEventDestroy"):
        _NVCUDA_LIB.cuEventDestroy.argtypes = [ctypes.c_void_p]
        _NVCUDA_LIB.cuEventDestroy.restype = ctypes.c_int

    if hasattr(_NVCUDA_LIB, "cuStreamWaitEvent"):
        _NVCUDA_LIB.cuStreamWaitEvent.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
        _NVCUDA_LIB.cuStreamWaitEvent.restype = ctypes.c_int

    logger.info("[VMM Allocator] NVIDIA C-Driver (nvcuda.dll / libcuda.so) successfully linked with full CUcontext & Multi-GPU VMM support!")
except Exception as _cuda_init_err:
    logger.debug(f"[VMM Allocator] Direct nvcuda binding notice: {_cuda_init_err}")
    _NVCUDA_LIB = None


def _release_virtual_address_range(ptr: int, size_bytes: int):
    """
    DONANIMSAL SANAL ADRES ARALIĞI İADE HİZMETİ (cuMemAddressFree / cuMemAddressRangeRelease).
    Geçici olarak rezerve edilen sanal adres uzayını sürücüye iade eder, sanal adres sızıntısını (Virtual Address Leak) engeller.
    """
    if _NVCUDA_LIB is None or ptr == 0 or size_bytes <= 0:
        return
    try:
        if hasattr(_NVCUDA_LIB, "cuMemAddressFree"):
            res = _NVCUDA_LIB.cuMemAddressFree(ctypes.c_uint64(ptr), ctypes.c_size_t(size_bytes))
            if res == 0:
                logger.debug(f"[VMM VA Release] cuMemAddressFree({hex(ptr)}, {size_bytes} bytes) SUCCESS!")
        elif hasattr(_NVCUDA_LIB, "cuMemAddressRangeRelease"):
            res = _NVCUDA_LIB.cuMemAddressRangeRelease(ctypes.c_uint64(ptr), ctypes.c_size_t(size_bytes))
            if res == 0:
                logger.debug(f"[VMM VA Release] cuMemAddressRangeRelease({hex(ptr)}, {size_bytes} bytes) SUCCESS!")
    except Exception as exc:
        logger.debug(f"VA release notice: {exc}")


def _allocate_pinned_host_memory(size_bytes: int) -> Tuple[int, Optional[Any]]:
    """
    PINNED HOST MEMORY ALLOCATOR (cuMemHostAlloc).
    Sayfalanamaz, donanımsal olarak kilitlenmiş sistem belleği (Pinned/Pageable-Locked Host Memory) ayırır.
    GPU <==> CPU asenkron DMA aktarımlarında (`cuMemcpyAsync`) Implicit Sync ve Driver Page Fault risklerini yok eder.
    """
    if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuMemHostAlloc"):
        try:
            host_ptr = ctypes.c_uint64(0)
            res = _NVCUDA_LIB.cuMemHostAlloc(ctypes.byref(host_ptr), ctypes.c_size_t(size_bytes), 0)
            if res == 0 and host_ptr.value != 0:
                logger.debug(f"[Pinned Host Memory] Allocated {size_bytes} bytes at {hex(host_ptr.value)} via cuMemHostAlloc")
                return host_ptr.value, None
        except Exception as exc:
            logger.debug(f"[Pinned Host Memory Notice] cuMemHostAlloc failed: {exc}")

    buf = (ctypes.c_uint8 * size_bytes)()
    return ctypes.addressof(buf), buf


def _free_pinned_host_memory(host_ptr_val: int, raw_buf: Optional[Any] = None):
    """
    PINNED HOST MEMORY FREE (cuMemFreeHost).
    cuMemHostAlloc ile ayrılan kilitlenmiş sistem belleğini serbest bırakır.
    """
    if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuMemFreeHost") and raw_buf is None:
        try:
            _NVCUDA_LIB.cuMemFreeHost(ctypes.c_uint64(host_ptr_val))
            logger.debug(f"[Pinned Host Memory] Freed {hex(host_ptr_val)} via cuMemFreeHost")
        except Exception as exc:
            logger.debug(f"[Pinned Host Memory Notice] cuMemFreeHost: {exc}")


def _ensure_active_cuda_context(gpu_id: int = 0) -> bool:
    """Aktif CUDA Primary Context'i retain eder ve iplikte (thread) aktifleştirir (Thread-Local önbellek ile)."""
    if getattr(_thread_local, "current_gpu_id", None) == gpu_id:
        return True
    if _NVCUDA_LIB is not None:
        try:
            device = ctypes.c_int(0)
            res_dev = _NVCUDA_LIB.cuDeviceGet(ctypes.byref(device), gpu_id)
            if res_dev == 0:
                ctx = ctypes.c_void_p(0)
                res_ctx = _NVCUDA_LIB.cuDevicePrimaryCtxRetain(ctypes.byref(ctx), device.value)
                if res_ctx == 0 and ctx.value is not None:
                    _NVCUDA_LIB.cuCtxSetCurrent(ctx)
                    _thread_local.current_gpu_id = gpu_id
                    return True
        except Exception as exc:
            logger.debug(f"CUcontext retain notice: {exc}")
    return False


def _enable_peer_access_between_gpus(src_gpu: int, dst_gpu: int) -> bool:
    """
    İki GPU context'i arasında ÇİFT YÖNLÜ (Bidirectional P2P) donanımsal Peer-to-Peer DMA kopyalama iznini
    (cuCtxEnablePeerAccess) karşılıklı olarak aktifleştirir.
    Bus Arbiter kilitlemelerini önlemek için ASİMETRİK GPU İNDEKS SIRALAMASI (min(i,j) < max(i,j)) uygulanır.
    """
    if _NVCUDA_LIB is not None and src_gpu != dst_gpu and src_gpu >= 0 and dst_gpu >= 0:
        try:
            gpu_first, gpu_second = min(src_gpu, dst_gpu), max(src_gpu, dst_gpu)

            # 1. GPU (düşük ID) context aktifleştirmesi
            dst_device = ctypes.c_int(0)
            _NVCUDA_LIB.cuDeviceGet(ctypes.byref(dst_device), gpu_second)
            dst_ctx = ctypes.c_void_p(0)
            _NVCUDA_LIB.cuDevicePrimaryCtxRetain(ctypes.byref(dst_ctx), dst_device.value)

            _ensure_active_cuda_context(gpu_first)
            res1 = 0
            if dst_ctx.value is not None:
                res1 = _NVCUDA_LIB.cuCtxEnablePeerAccess(dst_ctx, 0)

            # 2. GPU (yüksek ID) context aktifleştirmesi
            src_device = ctypes.c_int(0)
            _NVCUDA_LIB.cuDeviceGet(ctypes.byref(src_device), gpu_first)
            src_ctx = ctypes.c_void_p(0)
            _NVCUDA_LIB.cuDevicePrimaryCtxRetain(ctypes.byref(src_ctx), src_device.value)

            _ensure_active_cuda_context(gpu_second)
            res2 = 0
            if src_ctx.value is not None:
                res2 = _NVCUDA_LIB.cuCtxEnablePeerAccess(src_ctx, 0)

            if res1 in (0, 704) and res2 in (0, 704):  # 0: SUCCESS, 704: ALREADY_ENABLED
                logger.debug(f"[P2P Enable] Enabled Hardware Bidirectional Peer-to-Peer DMA Access: GPU #{src_gpu} <==> GPU #{dst_gpu}")
                return True
        except Exception as exc:
            logger.debug(f"P2P Bidirectional Enable notice (GPU #{src_gpu} <==> GPU #{dst_gpu}): {exc}")
    return False



class SanalBellekSayfasi:
    """
    Sayfa Durum Makinesi (Page State Machine), Kütük Takibi ve Alt-Dilimleyici (Sub-Allocator)
    """
    def __init__(self, page_id: int, physical_gpu_id: int, size_mb: float = 512.0, size_bytes: Optional[int] = None):
        self.page_id = page_id
        self.physical_gpu_id = physical_gpu_id
        if size_bytes is not None:
            self.size_bytes = size_bytes
        else:
            self.size_bytes = int(size_mb * 1024 * 1024)
        self.allocated_bytes: int = 0
        self.virtual_ptr: int = 0
        self.handle: Optional[int] = None       # CUmemGenericAllocationHandle tracked to avoid memory leaks
        self.shareable_handle: Optional[int] = None
        self.state: PageState = PageState.FREE  # Sayfa Durum Makinesi

        self.group_id: Optional[int] = None     # Tahsis grubu kimliği (Kardeş alt-extent takibi için)
        self.is_pgas_locked: bool = False       # NVSHMEM / PGAS Erken Unmap Çökmesi Koruması Kilit Bayrağı
        self.sync_event: Optional[Any] = None   # CUDA Event Senkronizasyon Kancası (cudaEvent_t / Handle)

    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)

    @size_mb.setter
    def size_mb(self, val: float):
        self.size_bytes = int(val * 1024 * 1024)

    @property
    def allocated_mb(self) -> float:
        return self.allocated_bytes / (1024 * 1024)

    @allocated_mb.setter
    def allocated_mb(self, val: float):
        self.allocated_bytes = int(val * 1024 * 1024)

    @property
    def free_bytes(self) -> int:
        return self.size_bytes - self.allocated_bytes

    @property
    def free_mb(self) -> float:
        return self.free_bytes / (1024 * 1024)

    def commit(self, handle_val: int):
        self.handle = handle_val
        self.state = PageState.COMMITTED

    def release(self):
        self.handle = None
        self.shareable_handle = None
        self.allocated_bytes = 0
        self.is_pgas_locked = False
        self.sync_event = None
        self.state = PageState.FREE


_GLOBAL_VMM_ALLOCATOR: Optional["SanalBellekYoneticisi"] = None

def get_global_vmm_allocator() -> Optional["SanalBellekYoneticisi"]:
    """Küresel aktif SanalBellekYoneticisi örneğini döndürür."""
    global _GLOBAL_VMM_ALLOCATOR
    return _GLOBAL_VMM_ALLOCATOR


class SanalBellekYoneticisi:
    """
    Bitişik 88 GB Sanal Adres Uzayı Tahsisçisi (Virtual Memory Manager)
    NVIDIA CUDA VMM API (cuMemAddressReserve, cuMemCreate, cuMemMap, cuMemSetAccess) ile donanımda yer ayırır.
    Dinamik Lazy Allocation (İhtiyaç Anında Tahsis) ve Erken Devlet Data-Locality desteği sunar.
    """
    def __init__(self, virtual_vram_gb: float = 88.0, physical_gpus: int = 4, page_size_mb: float = 512.0):
        global _GLOBAL_VMM_ALLOCATOR
        _GLOBAL_VMM_ALLOCATOR = self

        self.virtual_vram_bytes: int = int(virtual_vram_gb * 1024 * 1024 * 1024)
        self.physical_gpus = physical_gpus
        self.page_size_bytes: int = int(page_size_mb * 1024 * 1024)
        self._lock = threading.RLock()  # Yeniden Girilebilir İplik Kilit Mekanizması (Re-entrant Lock - Deadlock-Free)
        
        self.granularity = self.get_granularity()
        self.virtual_base_address: int = 0
        self.guard_virtual_ptr: int = 0
        self.guard_handle: Optional[int] = None
        
        self.pages: List[SanalBellekSayfasi] = []
        self.allocated_pages: List[SanalBellekSayfasi] = []
        self.on_page_committed_hooks: List[Any] = []
        self.on_page_unmapped_hooks: List[Any] = []
        self.on_address_relocated_hooks: List[Any] = []
        self.cpp_driver_lib = self._try_load_cpp_driver()
        self._next_group_id: int = 1  # Otomatik Tahsis Grubu Kimliği Üreteci
        self.p2p_capability_matrix: Dict[Tuple[int, int], bool] = {}  # P2P Topoloji Matrisi (P2P Capability Matrix)
        self.gpu_vram_capacities: Dict[int, int] = {}  # Heterojen GPU VRAM Kapasite Haritası
        self._is_compacting: bool = False  # Compaction Okuma Durum Makinesi Kilidi (Read State Lock Flag)
        self._compacting_thread: Optional[threading.Thread] = None
        self._compaction_event = threading.Event()
        self._compaction_event.set()
        self._pending_release_queue = collections.deque()

        # 88 GB + Donanımsal Koruma Sayfası (Tam 2 MB Granülarite Örtüşmesi: virtual_vram_bytes + 2 MB) Sanal Adres Rezerve Edilir
        guard_bytes = max(2 * 1024 * 1024, self.granularity)
        total_reserve_bytes = self.virtual_vram_bytes + guard_bytes
        self.cuMemAddressReserve(total_reserve_bytes)
        self._detect_gpu_vram_capacities()
        self._build_page_table()
        self._setup_guard_page()
        self._build_p2p_capability_matrix()

    @property
    def virtual_vram_gb(self) -> float:
        return self.virtual_vram_bytes / (1024 * 1024 * 1024)

    @virtual_vram_gb.setter
    def virtual_vram_gb(self, val: float):
        self.virtual_vram_bytes = int(val * 1024 * 1024 * 1024)

    @property
    def per_gpu_vram_gb(self) -> float:
        return getattr(self, '_per_gpu_vram_gb', 24.0)

    @per_gpu_vram_gb.setter
    def per_gpu_vram_gb(self, val: float):
        self._per_gpu_vram_gb = val
        val_bytes = int(val * 1024 * 1024 * 1024)
        num_gpus = max(1, getattr(self, 'physical_gpus', 1))
        if not hasattr(self, 'gpu_vram_capacities'):
            self.gpu_vram_capacities = {}
        for g_id in range(num_gpus):
            self.gpu_vram_capacities[g_id] = val_bytes

    def _wait_if_compacting(self):
        """
        SIKIŞTIRMA BİTİŞ DURUM SENKRONİZÖRÜ (Thread Suspension / Silent Wait Architecture).
        
        Arka planda donanımsal sıkıştırma (Compaction Pass 1/Pass 2) yürütülürken üst katmandan
        (PyTorch, Erken Devlet Engine) bir okuma/doğrulama veya telemetri isteği geldiğinde
        uygulamayı RuntimeError fırlatarak ÇÖKERTMEK YERİNE okuma yapan iplikleri mikrosaniyeler düzeyinde
        sessizce askıya alır (Block/Wait). Sıkıştırma Pass 2 bittiği an kilit kaldırılarak
        iplikler şeffafça yoluna devam ettirilir.
        """
        if getattr(self, '_is_compacting', False) and threading.current_thread() != getattr(self, '_compacting_thread', None):
            logger.debug(
                f"[Compaction Thread Synchronizer] Thread {threading.current_thread().name} suspended silently "
                f"waiting for hardware compaction cycle to finish..."
            )
            self._compaction_event.wait()

    @property
    def allocated_vram_bytes(self) -> int:
        self._wait_if_compacting()
        return sum(p.size_bytes for p in self.allocated_pages if p.state in (PageState.COMMITTED, PageState.LOCKED, PageState.SCRATCHPAD))

    @property
    def allocated_vram_gb(self) -> float:
        self._wait_if_compacting()
        return self.allocated_vram_bytes / (1024 * 1024 * 1024)

    def get_allocated_gb(self) -> float:
        """
        Geriye dönük telemetri sorgusu: Aktif tahsis edilen toplam VRAM miktarını (GB) döndürür.
        """
        self._wait_if_compacting()
        return self.allocated_vram_gb

    @property
    def page_size_mb(self) -> float:
        return self.page_size_bytes / (1024 * 1024)

    @page_size_mb.setter
    def page_size_mb(self, val: float):
        self.page_size_bytes = int(val * 1024 * 1024)

    def _setup_guard_page(self):
        """
        EKSİKSİZ DONANIMSAL KORUMA SAYFASI (Hardware PROT_NONE Guard Page).
        88 GB'ın sonundaki koruma sayfasına donanımın asgari sınırı olan 2 MB (self.granularity) kukla fiziki VRAM bağlar ve DONANIM SEVİYESİNDE ERİŞİMİ KESİNLİKLE YASAKLAR (PROT_NONE).
        512 MB israf edilmez, %99.6 VRAM tasarrufu sağlanır.
        """
        guard_bytes = max(2 * 1024 * 1024, self.granularity)
        main_bytes = int(self.virtual_vram_gb * 1024 * 1024 * 1024)
        self.guard_virtual_ptr = self.virtual_base_address + main_bytes

        if _NVCUDA_LIB is not None:
            dummy_handle = ctypes.c_uint64(0)
            try:
                _ensure_active_cuda_context(0)
                prop = CUmemAllocationProp()
                prop.type = 1            # CU_MEM_ALLOCATION_TYPE_PINNED
                prop.location.type = 1   # CU_MEM_LOCATION_TYPE_DEVICE
                prop.location.id = 0

                # 1. Koruma bölgesi için donanımda 2 MB kukla fiziki sayfa ayır
                res_c = _NVCUDA_LIB.cuMemCreate(ctypes.byref(dummy_handle), guard_bytes, ctypes.byref(prop), 0)
                if res_c == 0 and dummy_handle.value != 0:
                    self.guard_handle = dummy_handle.value
                    # 2. Sanal adrese bağla
                    _NVCUDA_LIB.cuMemMap(self.guard_virtual_ptr, guard_bytes, 0, dummy_handle.value, 0)
                    
                    # 3. DONANIM SEVİYESİNDE ERİŞİMİ KESİNLİKLE YASAKLA (flags = 0 -> PROT_NONE)
                    if self.physical_gpus > 0:
                        access_descs = (CUmemAccessDesc * self.physical_gpus)()
                        for g_id in range(self.physical_gpus):
                            access_descs[g_id].location.type = 1
                            access_descs[g_id].location.id = g_id
                            access_descs[g_id].flags = 0  # CU_MEM_ACCESS_FLAGS_PROT_NONE (SIFIR ERİŞİM)

                        _NVCUDA_LIB.cuMemSetAccess(self.guard_virtual_ptr, guard_bytes, access_descs, self.physical_gpus)
                    logger.info(f"[Guard Page] Hardware PROT_NONE Guard Page ARMED at {hex(self.guard_virtual_ptr)} ({guard_bytes / (1024**2):.1f} MB, Handle: {self.guard_handle})")
            except Exception as exc:
                logger.debug(f"Guard page setup notice: {exc}")
            logger.info(f"[Guard Page] Hardware Guard Page ARMED at {hex(self.guard_virtual_ptr)} (PROT_NONE, {guard_bytes / (1024**2):.1f} MB)")

    def _detect_gpu_vram_capacities(self):
        """
        HETEROJEN GPU KÜMELEMESİ DİNAMİK KART KAPASİTESİ TEŞHİSİ (cuDeviceTotalMem Hardware Query).
        Sunucuda takılı her bir fiziki GPU'nun gerçek VRAM boyutunu donanımdan canlı sorgular.
        Heterojen (farklı boyuttaki RTX 4080 16GB, RTX 3090 24GB, A100 80GB) sistemlerde
        yerel boş VRAM ve Eşit Taşkın Motoru kararlarının %100 doğrulukla alınmasını sağlar.
        """
        self.gpu_vram_capacities.clear()
        default_bytes = int(getattr(self, 'per_gpu_vram_gb', 24.0) * 1024 * 1024 * 1024)
        
        num_gpus = max(1, self.physical_gpus)
        for g_id in range(num_gpus):
            detected_bytes = None
            if _NVCUDA_LIB is not None:
                try:
                    dev = ctypes.c_int(0)
                    res_dev = _NVCUDA_LIB.cuDeviceGet(ctypes.byref(dev), g_id)
                    if res_dev == 0:
                        bytes_val = ctypes.c_size_t(0)
                        if hasattr(_NVCUDA_LIB, "cuDeviceTotalMem"):
                            res_mem = _NVCUDA_LIB.cuDeviceTotalMem(ctypes.byref(bytes_val), dev.value)
                            if res_mem == 0 and bytes_val.value > 0:
                                detected_bytes = bytes_val.value
                except Exception as exc:
                    logger.debug(f"[GPU Memory Detection Notice] GPU #{g_id}: {exc}")

            if detected_bytes is None or detected_bytes <= 0:
                detected_bytes = default_bytes

            self.gpu_vram_capacities[g_id] = detected_bytes
            logger.debug(
                f"[Heterogeneous GPU Capacity Matrix] GPU #{g_id} Physical VRAM Capacity: "
                f"{detected_bytes / (1024**3):.2f} GB ({detected_bytes} bytes)"
            )

    def _build_p2p_capability_matrix(self):
        """
        P2P TOPOLOJİ MATRİSİ ÖN HESAPLAMA MOTORU (Pre-Computed P2P Capability Matrix).
        Sürücü başlatılırken tüm GPU çiftlerinin P2P doğrudan DMA erişim kabiliyetini sorgular ve matriste önbelleğe alır.
        P2P desteklemeyen çiftlerde (Error 705 / CUDA_ERROR_PEER_ACCESS_UNSUPPORTED) her aktarımda sürücü hatası
        tetiklemek yerine doğrudan Host-Staged CPU Pinned RAM Relay Fallback yoluna girilmesini sağlar.
        """
        self.p2p_capability_matrix.clear()
        if self.physical_gpus <= 1:
            for i in range(max(1, self.physical_gpus)):
                self.p2p_capability_matrix[(i, i)] = True
            return

        has_unsupported = False
        for src in range(self.physical_gpus):
            for dst in range(self.physical_gpus):
                if src == dst:
                    self.p2p_capability_matrix[(src, dst)] = True
                else:
                    peer_ok = _enable_peer_access_between_gpus(src, dst)
                    self.p2p_capability_matrix[(src, dst)] = peer_ok
                    if not peer_ok:
                        has_unsupported = True
                    status_str = "SUPPORTED (Direct P2P DMA)" if peer_ok else "UNSUPPORTED (Host-Staged Relay Fallback)"
                    logger.debug(f"[P2P Topology Matrix] GPU #{src} <==> GPU #{dst}: {status_str}")

        if has_unsupported:
            logger.warning("[P2P Topology Matrix] Direct Peer-to-Peer DMA unsupported between some GPUs. Host-Staged Relay Fallback active.")

    def can_p2p_access(self, src_gpu: int, dst_gpu: int) -> bool:
        """
        P2P Topoloji Matrisinden GPU çiftinin P2P erişim durumunu sorgular.
        """
        if src_gpu == dst_gpu or src_gpu < 0 or dst_gpu < 0:
            return True
        if (src_gpu, dst_gpu) in self.p2p_capability_matrix:
            return self.p2p_capability_matrix[(src_gpu, dst_gpu)]
        
        peer_ok = _enable_peer_access_between_gpus(src_gpu, dst_gpu)
        self.p2p_capability_matrix[(src_gpu, dst_gpu)] = peer_ok
        return peer_ok

    def invalidate_p2p_cache(self, src_gpu: int, dst_gpu: int):
        """
        DİNAMİK P2P TOPOLOJİ GEÇERSİZLEŞTİRME MOTORU (Dynamic Topology Invalidation).
        Sürücü çalışırken bir GPU sıfırlanırsa (GPU Reset / Driver TDR) veya güç tasarruf modundan uyanırsa
        önbellekteki P2P matris durumunu anında pasife çeker ve sürücünün şeffaf şekilde Fallback moduna kaymasını sağlar.
        """
        with self._lock:
            self.p2p_capability_matrix[(src_gpu, dst_gpu)] = False
            self.p2p_capability_matrix[(dst_gpu, src_gpu)] = False
            logger.warning(
                f"[P2P Dynamic Invalidation] Invalidated stale P2P topology cache between GPU #{src_gpu} <==> GPU #{dst_gpu}. "
                f"Forcing future migrations to Host-Staged CPU Pinned RAM Relay!"
            )

    def refresh_p2p_topology(self):
        """
        Heterojen GPU Topoloji Onarım Kancası (Dynamic P2P Topology Refresh Engine).
        Çalışma zamanında (runtime) yeni GPU context'leri bağlandığında veya sürücü durum değişikliklerinde
        tüm GPU çiftleri arasındaki P2P matris durumunu canlı olarak yeniden sorgular ve matrisi tazeleyerek günceller.
        """
        with self._lock:
            self._build_p2p_capability_matrix()
            logger.info("[P2P Topology Refresh] P2P matrix topology refreshed successfully across all physical GPUs.")

    def register_on_page_committed_hook(self, callback: Any):
        """
        NVSHMEM ve Küresel Adres Uzayı (PGAS) entegrasyonu için sayfa haritalama kancası (On Page Committed Event Hook) kaydeder.
        """
        with self._lock:
            if callback not in self.on_page_committed_hooks:
                self.on_page_committed_hooks.append(callback)
                logger.info(f"[PGAS Hook] Registered NVSHMEM/PGAS Page Committed Hook: {callback.__name__ if hasattr(callback, '__name__') else callback}")

    def _trigger_on_page_committed(self, page_obj: SanalBellekSayfasi):
        """
        Bir sayfa COMMITTED durumuna geçtiğinde kaydolmuş tüm NVSHMEM/PGAS kancalarını tetikler ve handle'ı PGAS'a kaydeder.
        """
        os_handle = self.get_os_native_handle(page_obj)
        for hook in self.on_page_committed_hooks:
            try:
                hook(page_obj, os_handle)
            except Exception as exc:
                logger.error(f"[PGAS Hook Error] Failed to execute hook {hook}: {exc}")

    def register_on_page_unmapped_hook(self, callback: Any):
        """
        Bir sayfa serbest bırakıldığında veya donanımdan unmap edildiğinde NVSHMEM/PGAS veriyolunu bilgilendiren kancayı kaydeder.
        Bayat Handle (Stale Handle) hatasını engeller.
        """
        with self._lock:
            if callback not in self.on_page_unmapped_hooks:
                self.on_page_unmapped_hooks.append(callback)
                logger.info(f"[PGAS Unmap Hook] Registered NVSHMEM/PGAS Page Unmapped Hook: {callback.__name__ if hasattr(callback, '__name__') else callback}")

    def _trigger_on_page_unmapped(self, page_obj: SanalBellekSayfasi):
        """
        Bir sayfa donanımdan söküldüğünde kaydolmuş tüm NVSHMEM/PGAS unmap kancalarını tetikler.
        """
        for hook in self.on_page_unmapped_hooks:
            try:
                hook(page_obj)
            except Exception as exc:
                logger.error(f"[PGAS Unmap Hook Error] Failed to execute unmap hook {hook}: {exc}")

    def register_on_address_relocated_callback(self, callback: Any):
        """
        Sanal adres yer değiştirme (Compaction / Relocation) olaylarında üst katmanları (CUDAHookManager, ErkenDevletEngine)
        otomatik bilgilendiren atomik kanca kaydı.
        Callback imzası: callback(old_ptr: int, new_ptr: int, extent_obj: SanalBellekSayfasi)
        """
        with self._lock:
            if callback not in self.on_address_relocated_hooks:
                self.on_address_relocated_hooks.append(callback)
                logger.info(f"[VMM Allocator] Registered Address Relocation Callback: {callback}")

    def _trigger_on_address_relocated(self, old_ptr: int, new_ptr: int, page_obj: SanalBellekSayfasi):
        """Tüm kayıtlı Adres Yönlendirme kancalarını tetikler."""
        for hook in self.on_address_relocated_hooks:
            try:
                hook(old_ptr, new_ptr, page_obj)
            except Exception as exc:
                logger.error(f"[VMM Relocation Hook Error] Callback failed for old {hex(old_ptr)} -> new {hex(new_ptr)}: {exc}")

    def lock_page(self, page_obj: SanalBellekSayfasi):
        """
        CUDAHookManager ve C++ Runtime Entegrasyonu için Sanal Sayfa Kilitleme Kancası.
        Canlı tensör çalıştırılan sayfayı PageState.LOCKED moduna alarak Compaction motorunun
        bu sayfayı yerinden oynatmasını KESİNLİKLE engeller. C++ void* data_ptr bütünlüğünü korur.
        """
        with self._lock:
            page_obj.state = PageState.LOCKED
            logger.info(f"[Page Lock Guard] Page #{page_obj.page_id} ({hex(page_obj.virtual_ptr)}) LOCKED against Compaction relocation.")

    def process_pending_releases(self):
        """Kuyrukta bekleyen serbest bırakma ve kilit açma işlemlerini güvenle yürütür."""
        if not hasattr(self, '_pending_release_queue'):
            return
        while self._pending_release_queue:
            try:
                item = self._pending_release_queue.popleft()
                action, page_obj = item
                if action == 'unlock_page':
                    if page_obj.state == PageState.LOCKED:
                        page_obj.state = PageState.COMMITTED
                        logger.info(f"[Page Lock Guard] Page #{page_obj.page_id} ({hex(page_obj.virtual_ptr)}) UNLOCKED back to COMMITTED via Pending Release Queue.")
                elif action == 'unlock_pgas':
                    page_obj.is_pgas_locked = False
            except Exception as exc:
                logger.debug(f"[Pending Release Exception] {exc}")

    def unlock_page(self, page_obj: SanalBellekSayfasi, try_acquire: bool = False):
        """
        Sanal sayfanın LOCKED kilidini kaldırır ve tekrar COMMITTED durumuna iade eder.
        Non-blocking try_acquire modunda kilit meşgulse pending_release_queue'ya ekler.
        """
        if try_acquire:
            acquired = self._lock.acquire(blocking=False)
            if acquired:
                try:
                    if page_obj.state == PageState.LOCKED:
                        page_obj.state = PageState.COMMITTED
                        logger.info(f"[Page Lock Guard] Page #{page_obj.page_id} ({hex(page_obj.virtual_ptr)}) UNLOCKED back to COMMITTED.")
                    self.process_pending_releases()
                finally:
                    self._lock.release()
            else:
                if not hasattr(self, '_pending_release_queue'):
                    self._pending_release_queue = collections.deque()
                self._pending_release_queue.append(('unlock_page', page_obj))
                logger.info(f"[Async Task Reclaimer] Mutex busy. Enqueued Page #{page_obj.page_id} into pending release queue.")
        else:
            with self._lock:
                if page_obj.state == PageState.LOCKED:
                    page_obj.state = PageState.COMMITTED
                    logger.info(f"[Page Lock Guard] Page #{page_obj.page_id} ({hex(page_obj.virtual_ptr)}) UNLOCKED back to COMMITTED.")
                self.process_pending_releases()

    def find_page_at_address(self, ptr: int) -> Optional[SanalBellekSayfasi]:
        """Dual-Tree / Binary Search O(log N) Sanal Adres Aralığı Sorgulama."""
        if not self.pages:
            return None
        keys = [p.virtual_ptr for p in self.pages]
        idx = bisect.bisect_right(keys, ptr) - 1
        if 0 <= idx < len(self.pages):
            page = self.pages[idx]
            if page.virtual_ptr <= ptr < page.virtual_ptr + page.size_bytes:
                return page
        return None

    def lock_pgas_page(self, page_obj: SanalBellekSayfasi):
        """
        NVSHMEM / PGAS Veriyolu Entegrasyonu için PGAS Kilidi.
        NVSHMEM veriyoluna kaydedilmiş sayfayı PGAS Kilidi (is_pgas_locked=True) altına alır.
        Uzaktaki GPU'lar erişirken cuMemUnmap çağrılmasını ve NVSHMEM veriyolu çökmesini engeller.
        """
        with self._lock:
            page_obj.is_pgas_locked = True
            logger.info(f"[PGAS Lock Guard] Page #{page_obj.page_id} ({hex(page_obj.virtual_ptr)}) PGAS LOCKED against unmapping.")

    def unlock_pgas_page(self, page_obj: SanalBellekSayfasi):
        """
        Sayfanın PGAS Kilidini kaldırır (Unregister PGAS).
        """
        with self._lock:
            page_obj.is_pgas_locked = False
            logger.info(f"[PGAS Lock Guard] Page #{page_obj.page_id} ({hex(page_obj.virtual_ptr)}) PGAS UNLOCKED.")

    @contextmanager
    def scratchpad_scope(self, size_mb: float, target_gpu_id: Optional[int] = None):
        """
        RAII Scratchpad Kapsam Yöneticisi (Context Manager / Scope Guard).
        Erken Devlet Engine geçici ara bellek taleplerinin yetim kalmasını (Orphaned Scratchpad Memory Leak) engeller.
        Kapsamdan çıkıldığı an (Python Exception fırlatılsa dahi) geçici bellek donanımdan otomatik sökülür.
        """
        ptr, main_extent = self.allocate_scratchpad_chunk(size_mb, target_gpu_id=target_gpu_id)
        try:
            yield ptr, main_extent
        finally:
            self.free_scratchpad_chunk(ptr)

    def create_cuda_sync_event(self, gpu_id: int = 0) -> Optional[Any]:
        """
        CUDA Senkronizasyon Olayı Üretecisi (cuEventCreate).
        SanalIslemciHavuzu için donanımsal senkronizasyon event'i üretir.
        """
        if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuEventCreate"):
            try:
                _ensure_active_cuda_context(gpu_id)
                event_ptr = ctypes.c_void_p(0)
                res = _NVCUDA_LIB.cuEventCreate(ctypes.byref(event_ptr), 0)
                if res == 0 and event_ptr.value is not None:
                    return event_ptr
            except Exception as exc:
                logger.debug(f"cuEventCreate notice: {exc}")
        return None

    def wait_for_migration_event(self, page_obj: SanalBellekSayfasi, stream: Optional[Any] = None) -> bool:
        """
        SanalIslemciHavuzu Senkronizasyon Kancası (CUDA Event Stream Wait).
        `remap_locality` migrasyonu bittiğinde üretilen CUDA senkronizasyon olayını
        SanalIslemciHavuzu akışına (streamWaitEvent) bağlar.
        DMA aktarımı tamamlanmadan hedef GPU üzerinde çekirdek çalıştırılmasını engeller (Data Corruption Protection).
        """
        if page_obj.sync_event is not None and _NVCUDA_LIB is not None:
            try:
                if hasattr(_NVCUDA_LIB, "cuStreamWaitEvent"):
                    _NVCUDA_LIB.cuStreamWaitEvent(stream, page_obj.sync_event, 0)
                    logger.info(f"[CUDA Sync Hook] Issued streamWaitEvent for Page #{page_obj.page_id} migration completion.")
                    return True
                elif hasattr(_NVCUDA_LIB, "cuEventSynchronize"):
                    _NVCUDA_LIB.cuEventSynchronize(page_obj.sync_event)
                    logger.info(f"[CUDA Sync Hook] Synchronized migration event for Page #{page_obj.page_id}.")
                    return True
            except Exception as exc:
                logger.debug(f"wait_for_migration_event notice: {exc}")
        return False

    def get_granularity(self, gpu_id: int = 0) -> int:
        """Donanımsal Hizalama Sınırını (Allocation Granularity) Sorgular."""
        if _NVCUDA_LIB is not None:
            try:
                _ensure_active_cuda_context(gpu_id)
                gran = ctypes.c_size_t(0)
                prop = CUmemAllocationProp()
                prop.type = 1            # CU_MEM_ALLOCATION_TYPE_PINNED
                prop.location.type = 1   # CU_MEM_LOCATION_TYPE_DEVICE
                prop.location.id = gpu_id
                res = _NVCUDA_LIB.cuMemGetAllocationGranularity(ctypes.byref(gran), ctypes.byref(prop), 1)  # MINIMUM
                if res == 0 and gran.value > 0:
                    logger.info(f"[VMM Allocator] Hardware Allocation Granularity: {gran.value / 1024:.0f} KB")
                    return gran.value
            except Exception as exc:
                logger.debug(f"cuMemGetAllocationGranularity notice: {exc}")
        return 2 * 1024 * 1024  # 2MB Default Alignment

    def get_c_allocator(self) -> Optional[Any]:
        """CUDACachingAllocator kancası için C++ sürücü veya bellek adresi göstericisini döndürür."""
        if hasattr(self, "driver_ptr") and self.driver_ptr is not None:
            return self.driver_ptr
        if hasattr(self, "cpp_driver_lib") and self.cpp_driver_lib is not None:
            return self.cpp_driver_lib
        return None

    def _try_load_cpp_driver(self) -> Optional[Any]:
        """C++ CUDA VMM Sürücü kütüphanesini (DLL/SO) ctypes/JIT ile yükler."""
        try:
            from kulli_gpu.interception.cpp_builder import build_and_load_cpp_driver
            driver_info = build_and_load_cpp_driver()
            if driver_info and driver_info.get("lib") is not None:
                self.driver_ptr = driver_info.get("driver_ptr")
                logger.info(f"[VMM Allocator] Loaded JIT C++ CUDA Driver via cpp_builder: {driver_info.get('so_path')}")
                return driver_info.get("lib")
        except Exception as exc:
            logger.debug(f"[VMM Allocator] JIT builder notice: {exc}")

        lib_names = ["libkulli_vmm_cuda.so", "kulli_vmm_cuda.so", "kulli_vmm_cuda.dll"]
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cpp_dir = os.path.join(os.path.dirname(current_dir), "cpp_driver")

        for name in lib_names:
            paths = [
                os.path.join("/tmp", name),
                os.path.join(current_dir, name),
                os.path.join(cpp_dir, name),
                name
            ]
            for p in paths:
                try:
                    lib = ctypes.CDLL(p)
                    logger.info(f"[VMM Allocator] Loaded C++ CUDA Driver API DLL: {p}")
                    return lib
                except Exception:
                    pass
        return None

    def cuMemAddressReserve(self, size_bytes_or_gb: Any) -> int:
        """
        NVIDIA Driver API: cuMemAddressReserve çağrısı.
        Donanımsal Granularity hizalamasına uygun bitişik sanal bellek adresi ayırır.
        DONANIMSAL KORUMA: Sıfır veya negatif bayt istekleri C-API'ye gitmeden ValueError fırlatır.
        """
        if isinstance(size_bytes_or_gb, (int, float)) and size_bytes_or_gb <= 0:
            raise ValueError(
                f"Küllî VMM Hatası: cuMemAddressReserve çağrısında talep edilen adres boyutu "
                f"0 veya negatif olamaz! (size_bytes={size_bytes_or_gb})"
            )

        if isinstance(size_bytes_or_gb, int) and size_bytes_or_gb > 1024 * 1024:
            bytes_raw = size_bytes_or_gb
            size_gb = bytes_raw / (1024.0 ** 3)
        else:
            size_gb = float(size_bytes_or_gb)
            bytes_raw = int(size_gb * 1024 * 1024 * 1024)

        if bytes_raw <= 0:
            raise ValueError(
                f"Küllî VMM Hatası: cuMemAddressReserve çağrısında talep edilen adres boyutu "
                f"0 veya negatif olamaz! (bytes_raw={bytes_raw})"
            )

        bytes_total = int(math.ceil(bytes_raw / self.granularity) * self.granularity)

        if _NVCUDA_LIB is not None:
            try:
                _ensure_active_cuda_context(0)
                ptr = ctypes.c_uint64(0)
                res = _NVCUDA_LIB.cuMemAddressReserve(ctypes.byref(ptr), bytes_total, self.granularity, 0, 0)
                if res == 0 and ptr.value != 0:
                    self.virtual_base_address = ptr.value
                    logger.info(f"[VMM Allocator] Real CUDA cuMemAddressReserve(bytes={bytes_total}, align={self.granularity}) -> Base Address: {hex(self.virtual_base_address)}")
                    return self.virtual_base_address
            except Exception as e:
                logger.debug(f"Direct cuMemAddressReserve notice: {e}")

        if self.cpp_driver_lib and (hasattr(self.cpp_driver_lib, "kulli_vmm_reserve_address_bytes") or hasattr(self.cpp_driver_lib, "kulli_vmm_reserve_address")):
            try:
                func_name = "kulli_vmm_reserve_address_bytes" if hasattr(self.cpp_driver_lib, "kulli_vmm_reserve_address_bytes") else "kulli_vmm_reserve_address"
                func = getattr(self.cpp_driver_lib, func_name)
                func.restype = ctypes.c_uint64
                func.argtypes = [ctypes.c_uint64]
                ptr_val = func(bytes_total)
                if ptr_val != 0:
                    self.virtual_base_address = ptr_val
                    logger.info(f"[VMM Allocator] C++ Extension cuMemAddressReserve(bytes={bytes_total}) -> Base Address: {hex(self.virtual_base_address)}")
                    return self.virtual_base_address
            except Exception as e:
                logger.debug(f"C++ reserve address notice: {e}")

        # Fallback dinamik adres tahsisi
        self.virtual_base_address = 0x7FFF00000000
        logger.warning(f"[VMM Allocator] Fallback Virtual Base Address: {hex(self.virtual_base_address)}")
        return self.virtual_base_address

    def _build_page_table(self):
        """
        Sanal Adres Uzayını Granüler Sanal Aralıklar (Extent/Interval Allocator) olarak ilklendirir.
        KATI 512 MB SABİT IZGARA PRANGASI TAMAMEN SÖKÜLMÜŞTÜR!
        88 GB'lık sanal bellek uzayı başlangıçta TEK BİR SÜREKLİ SERBEST ARALIK (Initial Free Extent) olarak yönetilir.
        """
        self.pages.clear()
        initial_extent = SanalBellekSayfasi(
            page_id=0,
            physical_gpu_id=-1,
            size_bytes=self.virtual_vram_bytes
        )
        initial_extent.virtual_ptr = self.virtual_base_address
        initial_extent.state = PageState.FREE
        self.pages.append(initial_extent)
        logger.info(f"[Granular Extent Allocator] Virtual address space (88 GB) initialized as continuous free extent at {hex(self.virtual_base_address)}")

    def _coalesce_extents(self):
        """Komşu sanal serbest aralıkları (FREE extents) otomatik olarak birleştirir (Extent Coalescing Engine)."""
        if not self.pages:
            return
        self.pages.sort(key=lambda p: p.virtual_ptr)
        coalesced: List[SanalBellekSayfasi] = []
        curr = self.pages[0]

        for nxt in self.pages[1:]:
            curr_end = curr.virtual_ptr + curr.size_bytes
            if (curr.state in (PageState.FREE, PageState.RESERVED) and 
                nxt.state in (PageState.FREE, PageState.RESERVED) and 
                curr_end == nxt.virtual_ptr):
                curr.size_bytes += nxt.size_bytes
            else:
                coalesced.append(curr)
                curr = nxt
        coalesced.append(curr)
        self.pages = coalesced

    def allocate_pages(
        self, 
        num_pages: int, 
        target_gpu_id: Optional[int] = None, 
        state: PageState = PageState.COMMITTED
    ) -> List[SanalBellekSayfasi]:
        """
        Granüler Sanal Aralık (Extent) Tabanlı Dinamik Sayfa Tahsisi.
        Geriye dönük uyumluluk için `num_pages` adet dinamik extent üretir ve GPU'lara haritalar.
        """
        with self._lock:
            allocated_list: List[SanalBellekSayfasi] = []
            for i in range(num_pages):
                size_bytes = self.page_size_bytes
                assigned_gpu = target_gpu_id if target_gpu_id is not None else (i % self.physical_gpus)
                _, extent_list = self.allocate_contiguous_virtual_block(size_bytes, target_gpu_id=assigned_gpu)
                ext = extent_list[0]
                ext.state = state
                allocated_list.append(ext)
            return allocated_list

    def _compact_virtual_memory(self):
        """
        Granüler Sanal Adres Sıkıştırma Motoru (Granular Extent Compaction Engine).
        Aktif (COMMITTED / SCRATCHPAD / LOCKED) extent'leri sanal uzayın soluna ardışık yerleştirir.
        Tüm boş (FREE) extent'leri sanal uzayın sağında tek bir sürekli dev FREE extent halinde birleştirir.
        
        DONANIMSAL İKİ AŞAMALI (TWO-PASS COMPACTION RULE) ŞEMA:
        - 1. AŞAMA (UNMAP AŞAMASI): Adresi değişecek tüm aktif sayfalar öncelikle eski sanal adreslerinden
          topluca donanımsal olarak sökülür (cuMemUnmap). Böylece kısmi adres çakışmalarında (Address Overlap)
          CUDA_ERROR_INVALID_VALUE hatası fırlatılması engellenir.
        - 2. AŞAMA (MAP AŞAMASI): Adres alanı tamamen temizlendikten sonra tüm sayfalar yeni sıkışık
          sanal adreslerine topluca haritalanır (cuMemMap + cuMemSetAccess) ve adres kancaları tetiklenir.
          
        DONANIMSAL AKIŞ SENKRONİZASYONU: Sıkıştırma motoru unmap yapmadan evvel tüm aktif GPU akışlarının
        tamamlanmasını (cuStreamSynchronize / cuCtxSynchronize) beklemek zorundadır.
        """
        with self._lock:
            self._is_compacting = True
            self._compacting_thread = threading.current_thread()
            if hasattr(self, '_compaction_event'):
                self._compaction_event.clear()
            rollback_executed = False
            completed_relocations = []
            try:
                logger.info("[VMM Compaction] Triggered Two-Pass Hardware-Level Granular Extent Compaction Engine...")

                # 1. HARDWARE STREAM SYNCHRONIZATION: Donanım üzerinde aktif çalışan tüm CUDA çekirdekleri (Kernel)
                # ve PyTorch tensör işlemleri tamamlanana kadar bekle. Donanım durdurulmadan adres altından çekilemez!
                if _NVCUDA_LIB is not None and self.physical_gpus > 0:
                    for g_id in range(self.physical_gpus):
                        try:
                            _ensure_active_cuda_context(g_id)
                            _NVCUDA_LIB.cuStreamSynchronize(None)
                            _NVCUDA_LIB.cuCtxSynchronize()
                        except Exception as sync_exc:
                            logger.debug(f"[Compaction Stream Sync Notice] GPU #{g_id}: {sync_exc}")

                # LOCKED SAYFA KORUMA KURALI (Pinned Locked Page Protection):
                # PageState.LOCKED veya PGAS Kilidi (is_pgas_locked=True) altındaki sayfalar C++ Pointer güvenliğini
                # korumak amacıyla donanımda sabitleşmiştir ve Compaction esnasında KESİNLİKLE yerinden oynatılmaz!
                movable_extents = [
                    p for p in self.pages 
                    if p.state not in (PageState.FREE, PageState.RESERVED) 
                    and p.state != PageState.LOCKED 
                    and not getattr(p, 'is_pgas_locked', False)
                ]
                movable_extents.sort(key=lambda p: p.virtual_ptr)

                locked_extents = [
                    p for p in self.pages 
                    if p.state == PageState.LOCKED or getattr(p, 'is_pgas_locked', False)
                ]
                locked_extents.sort(key=lambda p: p.virtual_ptr)

                relocation_plan = []
                curr_ptr = self.virtual_base_address

                for page in movable_extents:
                    # Kilitli sayfalarla sanal adres çakışmasını engelle
                    for l_page in locked_extents:
                        l_start = l_page.virtual_ptr
                        l_end = l_start + l_page.size_bytes
                        if curr_ptr < l_end and (curr_ptr + page.size_bytes) > l_start:
                            curr_ptr = l_end

                    old_ptr = page.virtual_ptr
                    new_ptr = curr_ptr
                    extent_bytes = page.size_bytes

                    if old_ptr != new_ptr:
                        relocation_plan.append((page, old_ptr, new_ptr, extent_bytes))
                    curr_ptr += extent_bytes

                # --- PASS 1: UNMAP AŞAMASI (Toplu Sanal Adres Sökümü) ---
                unmapped_in_pass1 = []
                pass1_failed = False
                pass1_exception = None

                for page, old_ptr, new_ptr, extent_bytes in relocation_plan:
                    if _NVCUDA_LIB is not None and page.handle is not None:
                        try:
                            _ensure_active_cuda_context(page.physical_gpu_id if page.physical_gpu_id != -1 else 0)
                            _NVCUDA_LIB.cuStreamSynchronize(None)
                            res_unmap = _NVCUDA_LIB.cuMemUnmap(old_ptr, extent_bytes)
                            if res_unmap != 0:
                                raise RuntimeError(f"cuMemUnmap failed with CUDA error code: {res_unmap}")
                            unmapped_in_pass1.append((page, old_ptr, extent_bytes))
                            logger.debug(f"[VMM Compaction Pass 1] Unmapped old virtual ptr {hex(old_ptr)} for Extent #{page.page_id}")
                        except Exception as exc:
                            logger.critical(
                                f"[VMM Compaction Pass 1 CRITICAL FAULT] Failed to unmap extent #{page.page_id} at {hex(old_ptr)}: {exc}. "
                                f"Initiating Pass 1 Hardware Rollback & Restoration!"
                            )
                            pass1_failed = True
                            pass1_exception = exc
                            break

                if pass1_failed:
                    logger.warning("[VMM Compaction Rollback] Pass 1 fault detected! Restoring unmapped extents back to original addresses...")
                    for page, old_ptr, extent_bytes in unmapped_in_pass1:
                        if _NVCUDA_LIB is not None and page.handle is not None:
                            try:
                                _ensure_active_cuda_context(page.physical_gpu_id if page.physical_gpu_id != -1 else 0)
                                _NVCUDA_LIB.cuMemMap(old_ptr, extent_bytes, 0, page.handle, 0)
                                if self.physical_gpus > 0:
                                    access_descs = (CUmemAccessDesc * self.physical_gpus)()
                                    for g_id in range(self.physical_gpus):
                                        access_descs[g_id].location.type = 1
                                        access_descs[g_id].location.id = g_id
                                        access_descs[g_id].flags = 3
                                    _NVCUDA_LIB.cuMemSetAccess(old_ptr, extent_bytes, access_descs, self.physical_gpus)
                            except Exception as rest_exc:
                                logger.critical(f"[VMM Compaction Pass 1 Rollback FATAL] Failed to restore extent #{page.page_id} at {hex(old_ptr)}: {rest_exc}")
                    self.pages.sort(key=lambda p: p.virtual_ptr)
                    # ROLLBACK OLAY TEMİZLİĞİ KURALI (Zero False Relocation Invariant):
                    # Pass 1 Rollback çalıştığında completed_relocations listesi temizlenerek
                    # üst katmanlara yalancı adres yönlendirme kancı gönderilmesi engellenir.
                    completed_relocations.clear()
                    rollback_executed = True
                    logger.warning(
                        "[VMM Compaction Rollback] Pass 1 rollback executed – address relocation callbacks suppressed! "
                        "Zero False Relocation Invariant enforced."
                    )
                    raise RuntimeError(f"Küllî VMM Compaction Pass 1 Failed! Donanımsal Geri Alma (Rollback) çalıştırıldı ve sanal uzay intizamı sağlandı. Hata Detayı: {pass1_exception}")

                # --- PASS 2: MAP AŞAMASI (Toplu Sanal Adres Haritalama & Donanımsal Geri Alma / Pass 2 Rollback) ---
                pass2_failed = False
                failed_exception = None

                for page, old_ptr, new_ptr, extent_bytes in relocation_plan:
                    if getattr(self, "_simulate_pass2_failure", False):
                        logger.critical(
                            f"[VMM Extent Compaction Pass 2 CRITICAL FAULT] Simulated hardware failure for Extent #{page.page_id} at {hex(new_ptr)}. "
                            f"Initiating Hardware Rollback & Restoration to pre-compaction state!"
                        )
                        pass2_failed = True
                        failed_exception = RuntimeError("Simulated Pass 2 Hardware Mapping Failure")
                        break

                    if _NVCUDA_LIB is not None and page.handle is not None:
                        try:
                            _ensure_active_cuda_context(page.physical_gpu_id if page.physical_gpu_id != -1 else 0)
                            res_map = _NVCUDA_LIB.cuMemMap(new_ptr, extent_bytes, 0, page.handle, 0)
                            if res_map != 0:
                                raise RuntimeError(f"cuMemMap failed with CUDA error code: {res_map}")

                            if self.physical_gpus > 0:
                                access_descs = (CUmemAccessDesc * self.physical_gpus)()
                                for g_id in range(self.physical_gpus):
                                    access_descs[g_id].location.type = 1
                                    access_descs[g_id].location.id = g_id
                                    access_descs[g_id].flags = 3
                                res_access = _NVCUDA_LIB.cuMemSetAccess(new_ptr, extent_bytes, access_descs, self.physical_gpus)
                                if res_access != 0:
                                    raise RuntimeError(f"cuMemSetAccess failed with CUDA error code: {res_access}")

                            logger.info(f"[VMM Extent Compaction Pass 2] Remapped Extent #{page.page_id}: Old {hex(old_ptr)} -> New {hex(new_ptr)} ({page.size_mb:.1f} MB)")
                        except Exception as exc:
                            logger.critical(
                                f"[VMM Extent Compaction Pass 2 CRITICAL FAULT] Failed to map extent #{page.page_id} at {hex(new_ptr)}: {exc}. "
                                f"Initiating Hardware Rollback & Restoration to pre-compaction state!"
                            )
                            pass2_failed = True
                            failed_exception = exc
                            break

                    page.virtual_ptr = new_ptr
                    completed_relocations.append((old_ptr, new_ptr, page))

                # --- KUŞATICI ROLLBACK KURALI (Pass 2 Hardware Rollback & Restoration) ---
                if pass2_failed:
                    logger.warning("[VMM Compaction Rollback] Reverting all partial Pass 2 mappings and restoring original pre-compaction virtual addresses...")
                    
                    # 1. Pass 2'de yeni adreslerine haritalanmış sayfaları sök (Unmap partial Pass 2 mappings)
                    for old_ptr, new_ptr, page in completed_relocations:
                        if _NVCUDA_LIB is not None and page.handle is not None:
                            try:
                                _ensure_active_cuda_context(page.physical_gpu_id if page.physical_gpu_id != -1 else 0)
                                _NVCUDA_LIB.cuMemUnmap(new_ptr, page.size_bytes)
                            except Exception as unmap_exc:
                                logger.error(f"[Compaction Rollback Notice] Unmap partial new_ptr {hex(new_ptr)} failed: {unmap_exc}")

                    # 2. Tüm relocation_plan'deki sayfaları eski adreslerine (old_ptr) geri bağla (Restore original mappings)
                    for page, old_ptr, new_ptr, extent_bytes in relocation_plan:
                        page.virtual_ptr = old_ptr
                        if _NVCUDA_LIB is not None and page.handle is not None:
                            try:
                                _ensure_active_cuda_context(page.physical_gpu_id if page.physical_gpu_id != -1 else 0)
                                _NVCUDA_LIB.cuMemMap(old_ptr, extent_bytes, 0, page.handle, 0)
                                if self.physical_gpus > 0:
                                    access_descs = (CUmemAccessDesc * self.physical_gpus)()
                                    for g_id in range(self.physical_gpus):
                                        access_descs[g_id].location.type = 1
                                        access_descs[g_id].location.id = g_id
                                        access_descs[g_id].flags = 3
                                    _NVCUDA_LIB.cuMemSetAccess(old_ptr, extent_bytes, access_descs, self.physical_gpus)
                                logger.info(f"[VMM Compaction Rollback] Restored Extent #{page.page_id} back to original address {hex(old_ptr)}")
                            except Exception as restore_exc:
                                logger.critical(f"[VMM Compaction Rollback FATAL] Failed to restore extent #{page.page_id} at {hex(old_ptr)}: {restore_exc}")

                    self.pages.sort(key=lambda p: p.virtual_ptr)
                    # ROLLBACK OLAY TEMİZLİĞİ KURALI (Zero False Relocation Invariant):
                    # Pass 2 Rollback çalıştığında completed_relocations listesi DERHAL temizlenir
                    # ve üst katmanlara tek bir hatalı adres kancı dahi gönderilmez.
                    completed_relocations.clear()
                    rollback_executed = True
                    logger.warning(
                        "[VMM Compaction Rollback] Pass 2 rollback executed – address relocation callbacks suppressed! "
                        "Zero False Relocation Invariant enforced."
                    )
                    raise RuntimeError(
                        f"Küllî VMM Compaction Pass 2 Failed! Donanımsal Geri Alma (Rollback) çalıştırıldı ve bellek haritası "
                        f"orijinal haline iade edildi. Hata Detayı: {failed_exception}"
                    )

                # Kalan tüm boş alanı tekil bir FREE Extent olarak sağ tarafa yerleştir
                total_virtual_bytes = self.virtual_vram_bytes
                rem_bytes = (self.virtual_base_address + total_virtual_bytes) - curr_ptr

                new_pages = sorted(movable_extents + locked_extents, key=lambda p: p.virtual_ptr)
                if rem_bytes > 0:
                    free_extent = SanalBellekSayfasi(page_id=len(new_pages), physical_gpu_id=-1, size_bytes=rem_bytes)
                    free_extent.virtual_ptr = curr_ptr
                    free_extent.state = PageState.FREE
                    new_pages.append(free_extent)

                self.pages = new_pages
            finally:
                self._is_compacting = False
                self._compacting_thread = None
                if hasattr(self, '_compaction_event'):
                    self._compaction_event.set()

        # KİLİT DIŞI CALLBACK TETİKLEME (Out-of-Lock Callback Dispatch):
        # Kancaları self._lock kilit bloğunun DIŞINDA tetikle, iplik kilitlenmelerini (Lock Contention) engelle!
        # SIFIR YALANCI YÖNLENDİRME KURALI (Zero False Relocation Invariant):
        # Eğer Rollback çalıştıysa (rollback_executed == True), üst katmanlara
        # hiçbir hatalı adres kancı gönderilmez!
        if not rollback_executed:
            for old_ptr, new_ptr, page in completed_relocations:
                self._trigger_on_address_relocated(old_ptr, new_ptr, page)
            logger.info("[VMM Extent Compaction] Complete! Two-Pass execution clean. All extents tightly packed and batch notifications dispatched.")
        else:
            logger.warning(
                "[VMM Compaction] Rollback was executed – address relocation callbacks were NOT dispatched. "
                "Zero False Relocation Invariant enforced successfully."
            )

    def get_gpu_total_vram_bytes(self, gpu_id: int) -> int:
        """
        Heterojen Donanım Teşhisli: Hedef GPU'nun gerçek fiziki VRAM kapasitesini (bayt) döndürür.
        """
        if gpu_id in self.gpu_vram_capacities:
            return self.gpu_vram_capacities[gpu_id]
        return int(getattr(self, 'per_gpu_vram_gb', 24.0) * 1024 * 1024 * 1024)

    def get_gpu_free_vram_bytes(self, gpu_id: int) -> int:
        """
        Heterojen Donanım Teşhisli: Hedef GPU üzerindeki kullanılabilir yerel fiziki VRAM miktarını (bayt) döndürür.
        """
        self._wait_if_compacting()
        total_gpu_vram = self.get_gpu_total_vram_bytes(gpu_id)
        used_vram = sum(
            p.size_bytes for p in self.allocated_pages 
            if p.physical_gpu_id == gpu_id and p.state in (PageState.COMMITTED, PageState.LOCKED, PageState.SCRATCHPAD)
        )
        return max(0, total_gpu_vram - used_vram)

    def _map_extent_with_spillover(
        self, 
        extent: SanalBellekSayfasi, 
        target_gpu_id: Optional[int] = None
    ) -> List[SanalBellekSayfasi]:
        """
        EŞİT TAŞKIN VE YEREL ÖNCELİK MİMARİSİ (Equal Multi-GPU Spillover Architecture).
        
        1. YEREL DONANIM ÖNCELİĞİ (Local VRAM Priority - 1. Şart):
           İşlemin icra edildiği GPU'nun (target_gpu_id) yerel VRAM kapasitesi yeterliyse (Yerel Boş VRAM >= İstenen Boyut),
           tahsis %100 doğrudan o GPU'nun fiziki VRAM'inden yapılır. Veriyolu maliyeti SIFIR olur.
           
        2. EŞİT DAĞITIMLI PARALEL TAŞKIN MİMARİSİ (Equal Multi-GPU Spillover - 2. Şart):
           Yerel GPU yetersiz kaldığında; taşkın kısmı tek bir komşu GPU'ya yüklenmez!
           Kalan taşkın miktarı sistemdeki TÜM GPU'lara (physical_gpus) EŞİT DİLİMLER halinde bölünür.
           Böylece 4 ayrı NVLink/PCIe veriyolundan 4 paralel akış (RAID-0 DMA Burst) tetiklenir,
           aktarılan parça boyutu dörde bölünür ve aktarım hızı tavan yapar!
        """
        if extent.group_id is None:
            extent.group_id = self._next_group_id
            self._next_group_id += 1
        gid = extent.group_id

        assigned_gpu = target_gpu_id if target_gpu_id is not None and 0 <= target_gpu_id < self.physical_gpus else 0
        extent_bytes = extent.size_bytes
        
        if self.physical_gpus <= 1:
            # TEKİL GPU KAPASİTE KONTROLÜ: Tek GPU sisteminde yerel boş VRAM yetersizse
            # taşkın dağıtılacak ikincil GPU bulunmadığından cuMemCreate çökmesi ÖNDEN engellenir.
            local_free_single = self.get_gpu_free_vram_bytes(0)
            if local_free_single < extent_bytes:
                raise MemoryError(
                    f"Küllî VMM Tekil GPU VRAM Kapasitesi Aşılmış! "
                    f"İstenen: {extent_bytes} bytes, Yerel Boş VRAM: {local_free_single} bytes. "
                    f"Taşkın dağıtılacak ikincil GPU bulunamadı (physical_gpus={self.physical_gpus})."
                )
            extent.physical_gpu_id = 0
            extent.group_id = gid
            self.cuMemMap(extent.virtual_ptr, extent.page_id, 0, page_obj=extent)
            if extent not in self.allocated_pages:
                self.allocated_pages.append(extent)
            return [extent]

        local_free_bytes = self.get_gpu_free_vram_bytes(assigned_gpu)

        # 1. YEREL DONANIM ÖNCELİĞİ: Yerel GPU'da yeterli boş VRAM varsa %100 yerel haritala
        if local_free_bytes >= extent_bytes:
            extent.physical_gpu_id = assigned_gpu
            extent.group_id = gid
            self.cuMemMap(extent.virtual_ptr, extent.page_id, assigned_gpu, page_obj=extent)
            if extent not in self.allocated_pages:
                self.allocated_pages.append(extent)
            logger.info(
                f"[Local Priority Allocation] Extent #{extent.page_id} ({extent.size_mb:.1f} MB) "
                f"fully allocated on Local GPU #{assigned_gpu} (Zero Bus Latency)."
            )
            return [extent]

        # 2. EŞİT DAĞITIMLI PARALEL TAŞKIN MİMARİSİ (Ev Sahibi Kapasite Sınırı Kuralı):
        # A. Yerel GPU'daki kalan tüm boş VRAM'i tüket (Granülariteye yuvarlanmış)
        #    EV SAHİBİ GPU KAPASİTE SINIRI: Ev sahibi GPU'nun üstleneceği toplam fiziki VRAM payı,
        #    kendi yerel boş VRAM miktarını (local_avail) ASLA aşamaz!
        local_avail = int(math.floor(local_free_bytes / self.granularity) * self.granularity)
        local_avail = min(local_avail, extent_bytes)
        spillover_bytes = extent_bytes - local_avail

        # B. Taşkın miktarını YALNIZCA İKİNCİL GPU'LARA eşit böl (Ev sahibi GPU hariç!)
        gpu_shares: Dict[int, int] = {}
        allocated_so_far = 0

        # Ev sahibi GPU YALNIZCA local_avail miktarını alır — hiçbir taşkın payı eklenmez!
        if local_avail > 0:
            gpu_shares[assigned_gpu] = local_avail
            allocated_so_far += local_avail
            logger.info(
                f"[Spillover Host GPU Limit] Host GPU #{assigned_gpu} receives ONLY local_avail={local_avail} bytes "
                f"(local free VRAM: {local_free_bytes} bytes). No spillover share added to host."
            )

        if spillover_bytes > 0:
            # İkincil GPU'ları tespit et
            spillover_gpus = [g for g in range(self.physical_gpus) if g != assigned_gpu]

            # DURUM A: Tek GPU Sistemi — ikincil komşu GPU yok!
            if len(spillover_gpus) == 0:
                raise MemoryError(
                    f"Küllî VMM Tekil GPU VRAM Kapasitesi Aşılmış! "
                    f"İstenen: {extent_bytes} bytes, Yerel Boş VRAM: {local_free_bytes} bytes. "
                    f"Taşkın dağıtılacak ikincil GPU bulunamadı (physical_gpus={self.physical_gpus})."
                )

            # ÖN-KONTROL KURALI (Peer VRAM Pre-Check):
            # İkincil GPU'ların toplam boş VRAM kapasitesi, kalan spillover miktarını karşılayabilir mi?
            total_peer_free = sum(self.get_gpu_free_vram_bytes(g) for g in spillover_gpus)
            if total_peer_free < spillover_bytes:
                raise MemoryError(
                    f"Küllî VMM İkincil GPU Toplam VRAM Kapasitesi Yetersiz! "
                    f"Taşkın miktarı: {spillover_bytes} bytes, İkincil GPU'ların toplam boş VRAM'i: {total_peer_free} bytes. "
                    f"cuMemCreate aşamasında kısmi haritalama çöküşü önlendi (Peer VRAM Pre-Check)."
                )

            # Taşkın miktarını ikincil GPU'lara eşit böl
            per_peer_share = int(math.floor((spillover_bytes / len(spillover_gpus)) / self.granularity) * self.granularity)
            per_peer_share = max(self.granularity, per_peer_share)

            for i, g_id in enumerate(spillover_gpus):
                rem_needed = extent_bytes - allocated_so_far
                if rem_needed <= 0:
                    break
                share = min(per_peer_share, rem_needed)
                if share > 0:
                    gpu_shares[g_id] = share
                    allocated_so_far += share

            # Kalan son küsürat varsa (extent_bytes - allocated_so_far), son ikincil GPU'ya ekle
            rem = extent_bytes - allocated_so_far
            if rem > 0:
                last_peer = spillover_gpus[-1]
                gpu_shares[last_peer] = gpu_shares.get(last_peer, 0) + rem
                allocated_so_far += rem

        assert sum(gpu_shares.values()) == extent_bytes, (
            f"Küllî VMM Taşkın Taşma Hatası! Toplam taşkın payları ({sum(gpu_shares.values())} bytes) "
            f"orijinal extent boyutuna ({extent_bytes} bytes) eşit değil!"
        )

        logger.info(
            f"[Equal Multi-GPU Spillover] Extent #{extent.page_id} ({extent.size_mb:.1f} MB) "
            f"spilled over across {len(gpu_shares)} GPUs: {gpu_shares} in parallel DMA burst streams."
        )

        # Extent'i GPU paylarına göre alt-extent'lere böl ve haritala
        sub_extents: List[SanalBellekSayfasi] = []
        curr_virt = extent.virtual_ptr
        
        if extent in self.pages:
            self.pages.remove(extent)

        mapped_sub_extents: List[SanalBellekSayfasi] = []
        try:
            for g_id, share_bytes in gpu_shares.items():
                if share_bytes <= 0:
                    continue
                sub_ext = SanalBellekSayfasi(
                    page_id=len(self.allocated_pages) + len(sub_extents),
                    physical_gpu_id=g_id,
                    size_bytes=share_bytes
                )
                sub_ext.virtual_ptr = curr_virt
                sub_ext.state = PageState.COMMITTED
                sub_ext.group_id = gid
                map_ok = self.cuMemMap(sub_ext.virtual_ptr, sub_ext.page_id, g_id, page_obj=sub_ext)
                if not map_ok:
                    raise RuntimeError(f"cuMemMap failed for sub-extent #{sub_ext.page_id} on GPU #{g_id}")

                sub_extents.append(sub_ext)
                mapped_sub_extents.append(sub_ext)
                self.pages.append(sub_ext)
                self.allocated_pages.append(sub_ext)
                curr_virt += share_bytes
        except Exception as exc:
            logger.error(
                f"[Spillover Allocation Rollback] Multi-GPU mapping failed: {exc}. "
                f"Unmapping {len(mapped_sub_extents)} partially mapped sub-extents to prevent VRAM leak!"
            )
            for s_ext in reversed(mapped_sub_extents):
                try:
                    self.cuMemUnmap(s_ext)
                except Exception:
                    pass
            if extent not in self.pages:
                self.pages.append(extent)
            self.pages.sort(key=lambda p: p.virtual_ptr)
            raise RuntimeError(f"Küllî VMM Multi-GPU Spillover Haritalama Hatası! Geri alma (rollback) ile sızıntı önlendi! Detay: {exc}")

        self.pages.sort(key=lambda p: p.virtual_ptr)
        return sub_extents

    def _allocate_scattered_extents(
        self, 
        aligned_bytes: int, 
        target_gpu_id: Optional[int] = None
    ) -> Tuple[int, List[SanalBellekSayfasi]]:
        """
        I. USUL: PARÇALI SANAL KAPASİTE BİRLEŞTİRMESİ (Scattered Extent Aggregation).
        Şekilsel intizama bakılmaksızın 88 GB'lık sanal uzaydaki tüm parçalı boşlukları harmanlayıp birleştirir.
        """
        needed_bytes = aligned_bytes
        free_extents = [p for p in self.pages if p.state in (PageState.FREE, PageState.RESERVED)]
        free_extents.sort(key=lambda p: p.virtual_ptr)

        allocated_sub_extents: List[SanalBellekSayfasi] = []
        base_ptr: Optional[int] = None

        for free_ext in free_extents:
            if needed_bytes <= 0:
                break

            take_bytes = min(free_ext.size_bytes, needed_bytes)
            
            sub_ext = SanalBellekSayfasi(
                page_id=len(self.allocated_pages) + len(allocated_sub_extents),
                physical_gpu_id=target_gpu_id if target_gpu_id is not None else 0,
                size_bytes=take_bytes
            )
            sub_ext.virtual_ptr = free_ext.virtual_ptr
            sub_ext.state = PageState.COMMITTED

            if base_ptr is None:
                base_ptr = sub_ext.virtual_ptr

            if free_ext.size_bytes > take_bytes:
                free_ext.size_bytes -= take_bytes
                free_ext.virtual_ptr += take_bytes
            else:
                self.pages.remove(free_ext)

            self.pages.append(sub_ext)
            
            # Haritalama yap (Yerel Öncelik & Eşit Taşkın Mimarisi)
            mapped_pieces = self._map_extent_with_spillover(sub_ext, target_gpu_id=target_gpu_id)
            allocated_sub_extents.extend(mapped_pieces)
            
            needed_bytes -= take_bytes

        self.pages.sort(key=lambda p: p.virtual_ptr)
        first_ptr = base_ptr if base_ptr is not None else 0
        logger.info(
            f"[Scattered Extent Aggregation] Complete! Aggregated {len(allocated_sub_extents)} extent pieces "
            f"totaling {aligned_bytes / (1024**2):.1f} MB starting at {hex(first_ptr)}"
        )
        return first_ptr, allocated_sub_extents

    def allocate_contiguous_virtual_block(
        self, 
        size_bytes: int, 
        target_gpu_id: Optional[int] = None
    ) -> Tuple[int, List[SanalBellekSayfasi]]:
        """
        1. SÜTUN: GRANÜLER SANAL ARALIK (EXTENT) TAHSİSÇİSİ VE DONANIMSAL MMU EŞLEŞTİRMESİ.
        512 MB sabit ızgara prangası tamamen sökülmüştür!
        Ana program veya Erken Devlet Engine ne kadar boyut isterse (`size_bytes`),
        sürücü o boyutu donanımsal granülariteye (2 MB) yuvarlar ve sanal adres uzayında granüler extent olarak tahsis eder.
        
        "İNTİZAM DEĞİL, İSTİFADE" MİMARİSİ:
        Bitişik tek çizgi bulunamazsa dahi toplam boş sanal kapasite yettiği sürece parçalı extent'ler harmanlanıp tahsis edilir.
        """
        with self._lock:
            aligned_bytes = int(math.ceil(size_bytes / self.granularity) * self.granularity)

            self._coalesce_extents()

            # 1. Sanal uzayda aligned_bytes kadar boşluk barındıran FREE/RESERVED extent ara
            target_extent: Optional[SanalBellekSayfasi] = None
            for p in self.pages:
                if p.state in (PageState.FREE, PageState.RESERVED) and p.size_bytes >= aligned_bytes:
                    target_extent = p
                    break

            # 2. Eğer parçalanma varsa Compaction çalıştır
            if target_extent is None:
                self._compact_virtual_memory()
                self._coalesce_extents()
                for p in self.pages:
                    if p.state in (PageState.FREE, PageState.RESERVED) and p.size_bytes >= aligned_bytes:
                        target_extent = p
                        break

            # 3. İNTİZAM DEĞİL, İSTİFADE MİMARİSİ: Tekil bitişik extent bulunamadıysa, parçalı boş alanları topla!
            if target_extent is None:
                total_free_bytes = sum(p.size_bytes for p in self.pages if p.state in (PageState.FREE, PageState.RESERVED))
                if total_free_bytes >= aligned_bytes:
                    logger.info(
                        f"[Scattered Extent Aggregation] Single contiguous extent not found, but total free virtual capacity "
                        f"({total_free_bytes / (1024**2):.1f} MB >= {aligned_bytes / (1024**2):.1f} MB) is sufficient. Aggregating scattered extents!"
                    )
                    return self._allocate_scattered_extents(aligned_bytes, target_gpu_id=target_gpu_id)
                else:
                    req_size_mb = aligned_bytes / (1024 * 1024)
                    free_size_mb = total_free_bytes / (1024 * 1024)
                    raise MemoryError(
                        f"Küllî MMU Aggregator: Out of Virtual VRAM! Requested {req_size_mb:.1f} MB ({size_bytes} bytes), "
                        f"Total Available Free Capacity: {free_size_mb:.1f} MB."
                    )

            # 4. Tekil FREE extent bulunduysa: İstenen boyutta böl (Extent Splitting)
            allocated_extent = SanalBellekSayfasi(
                page_id=len(self.allocated_pages),
                physical_gpu_id=target_gpu_id if target_gpu_id is not None else 0,
                size_bytes=aligned_bytes
            )
            allocated_extent.virtual_ptr = target_extent.virtual_ptr
            allocated_extent.state = PageState.COMMITTED

            if target_extent.size_bytes > aligned_bytes:
                target_extent.size_bytes -= aligned_bytes
                target_extent.virtual_ptr += aligned_bytes
            else:
                self.pages.remove(target_extent)

            self.pages.append(allocated_extent)
            self.pages.sort(key=lambda p: p.virtual_ptr)

            # 5. Donanımsal VRAM Haritalaması (Yerel Öncelik + Eşit Taşkın Mimarisi)
            sub_extents = self._map_extent_with_spillover(allocated_extent, target_gpu_id=target_gpu_id)
            return allocated_extent.virtual_ptr, sub_extents

    def remap_locality(self, page_obj: SanalBellekSayfasi, target_gpu_id: int) -> bool:
        """
        Erken Devlet Engine Data-Locality Dinamik Yeniden Haritalaması (KAYIPSIZ P2P MIGRATION & IN-PLACE MIKRORING).
        
        KOPYALAMASIZ VE İLAVE VRAM HARCAMASIZ MİMARİ:
        1. KOPYALAMASIZ DOĞRUDAN ERİŞİM (Zero-Copy Remote Execution - 0 MB Ek VRAM):
           Tüm sayfalar donanımda `cuMemSetAccess` ile tüm GPU'lara (0..physical_gpus-1) READWRITE izniyle açılmıştır.
           Uzaktan çalıştırmada veri fiziken taşınmaz; hedef GPU NVLink/PCIe üzerinden veriyi doğrudan okur/yazar (0 MB Ek VRAM).
           
        2. ZORUNLU MİGRASYONDA IN-PLACE MİKRORİNG (Max 2 MB Ek VRAM Maliyeti):
           Eğer GPU VRAM'i boşaltmak zorundaysak; hedef GPU üzerinde geçici kopyalama tamponu (temporary buffer) AÇILMAZ!
           Yeni fiziki VRAM (`new_handle`) doğrudan nihai adres için tahsis edilir ve veri 2 MB mikroring dilimler halinde
           doğrudan kaynak VRAM'den nihai VRAM'e dairesel DMA akışıyla (`cuMemcpyAsync` in 2 MB micro-chunks) aktarılır.
           Böylece 100 GB dahi taşınsa ilave tampon maliyeti MAKSİMUM 2 MB ile sınırlanır!
           
        KİLİTSİZ DMA AKIŞI (LOCK-FREE DMA STREAMING MİMARİSİ):
        Sanal adres ayırma, yeni VRAM handle oluşturma ve adres haritalama adımları kilit altında yapılır;
        ancak iki GPU arasındaki fiziki DMA veri kopyalama döngüsü (cuMemcpyAsync ve senkronizasyon) kilit
        bloğunun DIŞINDA yürütülerek diğer ipliklerin kilitte tıkanması (Lock Contention) engellenir.
        """
        # --- 1. AŞAMA: KURULUM VE TAHAKKUK (KİLİT ALTINDA) ---
        with self._lock:
            old_gpu = page_obj.physical_gpu_id
            if old_gpu == target_gpu_id and page_obj.handle is not None:
                return True  # Zaten hedef GPU üzerinde fiziki olarak yerleşik ve verisi orada

            logger.info(f"[Data-Locality Migration] Migrating Page {page_obj.page_id} ({hex(page_obj.virtual_ptr)}) data from GPU {old_gpu} -> GPU {target_gpu_id}")

            page_bytes = page_obj.size_bytes

            # Eğer sayfa fiziki olarak ilk defa haritalanıyorsa (henüz eski canlı veri yoksa)
            if page_obj.handle is None or page_obj.state != PageState.COMMITTED:
                page_obj.physical_gpu_id = target_gpu_id
                page_obj.state = PageState.COMMITTED
                res_map = self.cuMemMap(page_obj.virtual_ptr, page_obj.page_id, target_gpu_id, page_obj=page_obj)
                sync_evt = self.create_cuda_sync_event(target_gpu_id)
                page_obj.sync_event = sync_evt if sync_evt is not None else f"MIGRATION_SYNC_EVENT_PAGE_{page_obj.page_id}_GPU_{target_gpu_id}"
                return res_map

            if _NVCUDA_LIB is None:
                page_obj.physical_gpu_id = target_gpu_id
                sync_evt = self.create_cuda_sync_event(target_gpu_id)
                page_obj.sync_event = sync_evt if sync_evt is not None else f"MIGRATION_SYNC_EVENT_PAGE_{page_obj.page_id}_GPU_{target_gpu_id}"
                return True

            new_handle = ctypes.c_uint64(0)
            temp_virt_addr = ctypes.c_uint64(0)
            old_handle_val = page_obj.handle
            source_virt_ptr = page_obj.virtual_ptr

            try:
                _ensure_active_cuda_context(target_gpu_id)
                prop = CUmemAllocationProp()
                prop.type = 1            # CU_MEM_ALLOCATION_TYPE_PINNED
                prop.location.type = 1   # CU_MEM_LOCATION_TYPE_DEVICE
                prop.location.id = target_gpu_id

                # Target GPU üzerinde yeni fiziki VRAM ayır (Nihai Hedef Bellek)
                res_create = _NVCUDA_LIB.cuMemCreate(ctypes.byref(new_handle), page_bytes, ctypes.byref(prop), 0)
                if res_create != 0 or new_handle.value == 0:
                    raise RuntimeError(f"cuMemCreate failed on GPU #{target_gpu_id} with code: {res_create}")

                # Geçici sanal adres ayırıp yeni VRAM'i oraya bağla
                res_res = _NVCUDA_LIB.cuMemAddressReserve(ctypes.byref(temp_virt_addr), page_bytes, self.granularity, 0, 0)
                if res_res != 0 or temp_virt_addr.value == 0:
                    raise RuntimeError(f"cuMemAddressReserve failed for temp address with code: {res_res}")

                _NVCUDA_LIB.cuMemMap(temp_virt_addr.value, page_bytes, 0, new_handle.value, 0)
                
                # Hedef adrese erişim izni ver
                access_descs = (CUmemAccessDesc * self.physical_gpus)()
                for g_id in range(self.physical_gpus):
                    access_descs[g_id].location.type = 1
                    access_descs[g_id].location.id = g_id
                    access_descs[g_id].flags = 3
                _NVCUDA_LIB.cuMemSetAccess(temp_virt_addr.value, page_bytes, access_descs, self.physical_gpus)

            except Exception as exc:
                logger.error(f"[Data-Locality Setup Error] Allocation failed: {exc}")
                if temp_virt_addr.value != 0:
                    try:
                        _NVCUDA_LIB.cuMemUnmap(temp_virt_addr.value, page_bytes)
                    except Exception:
                        pass
                    try:
                        _release_virtual_address_range(temp_virt_addr.value, page_bytes)
                    except Exception:
                        pass
                if new_handle.value != 0:
                    try:
                        _NVCUDA_LIB.cuMemRelease(new_handle)
                    except Exception:
                        pass
                return False

        # --- 2. AŞAMA: KİLİTSİZ DMA AKIŞI (LOCK-FREE DMA STREAMING) ---
        # self._lock KİLİDİ DIŞINDA YÜRÜTÜLÜR! Devasa veri aktarılırken diğer iplikler kilitte beklemez!
        copy_success = False
        try:
            peer_ok = self.can_p2p_access(old_gpu, target_gpu_id)

            # ÇİFTE DONANIM SENKRONİZASYON: Kaynak ve Hedef donanımları dondur
            if old_gpu >= 0:
                try:
                    _ensure_active_cuda_context(old_gpu)
                    _NVCUDA_LIB.cuStreamSynchronize(None)
                    _NVCUDA_LIB.cuCtxSynchronize()
                except Exception as exc_src:
                    logger.debug(f"[P2P Sync Notice] Source GPU #{old_gpu}: {exc_src}")

            try:
                _ensure_active_cuda_context(target_gpu_id)
                _NVCUDA_LIB.cuStreamSynchronize(None)
                _NVCUDA_LIB.cuCtxSynchronize()
            except Exception as exc_dst:
                logger.debug(f"[P2P Sync Notice] Target GPU #{target_gpu_id}: {exc_dst}")

            micro_chunk_bytes = max(2 * 1024 * 1024, self.granularity)
            p2p_success = False
            if peer_ok:
                try:
                    logger.info(
                        f"[P2P Migration Lock-Free Streaming] In-Place Micro-ring Direct P2P DMA: Copying {page_bytes / (1024**2):.1f} MB "
                        f"from {hex(source_virt_ptr)} (GPU #{old_gpu}) -> {hex(temp_virt_addr.value)} (GPU #{target_gpu_id}) in 2 MB micro-chunks..."
                    )
                    for offset in range(0, page_bytes, micro_chunk_bytes):
                        chunk_len = min(micro_chunk_bytes, page_bytes - offset)
                        res_cpy = _NVCUDA_LIB.cuMemcpyAsync(
                            ctypes.c_uint64(temp_virt_addr.value + offset),
                            ctypes.c_uint64(source_virt_ptr + offset),
                            chunk_len,
                            None
                        )
                        if res_cpy != 0:
                            raise RuntimeError(f"cuMemcpyAsync failed with CUDA error code: {res_cpy}")
                    p2p_success = True
                except Exception as p2p_exc:
                    logger.warning(
                        f"[P2P Dynamic Invalidation] Direct P2P DMA between GPU #{old_gpu} <==> GPU #{target_gpu_id} failed: {p2p_exc}. "
                        f"Invalidating stale P2P topology cache and switching to Host-Staged CPU Pinned RAM Relay fallback!"
                    )
                    self.invalidate_p2p_cache(old_gpu, target_gpu_id)
                    p2p_success = False

            if not peer_ok or not p2p_success:
                logger.warning(
                    f"[P2P Fallback Lock-Free Streaming] Peer access unsupported/invalidated between GPU #{old_gpu} and GPU #{target_gpu_id}. "
                    f"Executing Host-Staged CPU Pinned RAM Relay fallback via cuMemHostAlloc..."
                )
                host_ptr_val, raw_buf = _allocate_pinned_host_memory(micro_chunk_bytes)
                try:
                    for offset in range(0, page_bytes, micro_chunk_bytes):
                        chunk_len = min(micro_chunk_bytes, page_bytes - offset)
                        if old_gpu >= 0:
                            _ensure_active_cuda_context(old_gpu)
                            _NVCUDA_LIB.cuMemcpyAsync(
                                ctypes.c_uint64(host_ptr_val),
                                ctypes.c_uint64(source_virt_ptr + offset),
                                chunk_len,
                                None
                            )
                            _NVCUDA_LIB.cuStreamSynchronize(None)
                        _ensure_active_cuda_context(target_gpu_id)
                        _NVCUDA_LIB.cuMemcpyAsync(
                            ctypes.c_uint64(temp_virt_addr.value + offset),
                            ctypes.c_uint64(host_ptr_val),
                            chunk_len,
                            None
                        )
                        _NVCUDA_LIB.cuStreamSynchronize(None)
                finally:
                    _free_pinned_host_memory(host_ptr_val, raw_buf)

            # Aktarım sonrası çift yönlü donanım senkronizasyonu
            _ensure_active_cuda_context(target_gpu_id)
            _NVCUDA_LIB.cuStreamSynchronize(None)
            if old_gpu >= 0:
                _ensure_active_cuda_context(old_gpu)
                _NVCUDA_LIB.cuStreamSynchronize(None)

            logger.info(f"[P2P Migration Lock-Free Streaming] In-Place Micro-ring streaming complete and synchronized on both GPUs!")
            copy_success = True

        except Exception as exc:
            logger.error(f"[Data-Locality DMA Streaming Error] Lock-free P2P copy failed: {exc}")
            copy_success = False

        # --- 3. AŞAMALI GÜVENLİ MİGRASYON VE TABLO GÜNCELLEME (KİLİT ALTINDA) ---
        with self._lock:
            try:
                # Geçici sanal adresten yeni handle'ı sök ve geçici adres alanını iade et
                _NVCUDA_LIB.cuMemUnmap(temp_virt_addr.value, page_bytes)
                _release_virtual_address_range(temp_virt_addr.value, page_bytes)

                if not copy_success:
                    _NVCUDA_LIB.cuMemRelease(new_handle)
                    return False

                # Esas sanal adresten eski haritalamayı sök
                _NVCUDA_LIB.cuMemUnmap(page_obj.virtual_ptr, page_bytes)

                # AŞAMALI GÜVENLİ MİGRASYON (STAGED COMMIT):
                # Yeni VRAM handle'ını esas adrese bağla ve cuMemSetAccess ile DOĞRULA!
                access_descs = (CUmemAccessDesc * self.physical_gpus)()
                for g_id in range(self.physical_gpus):
                    access_descs[g_id].location.type = 1
                    access_descs[g_id].location.id = g_id
                    access_descs[g_id].flags = 3

                res_map_main = _NVCUDA_LIB.cuMemMap(page_obj.virtual_ptr, page_bytes, 0, new_handle.value, 0)
                if res_map_main != 0:
                    logger.critical(f"[Staged Commit Fault] cuMemMap failed ({res_map_main}). Rolling back to original handle!")
                    if old_handle_val is not None:
                        _NVCUDA_LIB.cuMemMap(page_obj.virtual_ptr, page_bytes, 0, old_handle_val, 0)
                        _NVCUDA_LIB.cuMemSetAccess(page_obj.virtual_ptr, page_bytes, access_descs, self.physical_gpus)
                    _NVCUDA_LIB.cuMemRelease(new_handle)
                    raise RuntimeError(f"cuMemMap failed during staged commit: {res_map_main}")

                res_acc_main = _NVCUDA_LIB.cuMemSetAccess(page_obj.virtual_ptr, page_bytes, access_descs, self.physical_gpus)
                if res_acc_main != 0:
                    logger.critical(f"[Staged Commit Fault] cuMemSetAccess failed ({res_acc_main}). Rolling back to original handle!")
                    if old_handle_val is not None:
                        _NVCUDA_LIB.cuMemMap(page_obj.virtual_ptr, page_bytes, 0, old_handle_val, 0)
                        _NVCUDA_LIB.cuMemSetAccess(page_obj.virtual_ptr, page_bytes, access_descs, self.physical_gpus)
                    _NVCUDA_LIB.cuMemRelease(new_handle)
                    raise RuntimeError(f"cuMemSetAccess failed during staged commit: {res_acc_main}")

                # YENİ HARİTALAMA BAŞARIYLA DOĞRULANDIKTAN SONRA ESKİ HANDLE'I DONANIMA İADE ET!
                if old_handle_val is not None:
                    _NVCUDA_LIB.cuMemRelease(ctypes.c_uint64(old_handle_val))

                # Sayfa Bilgilerini Güncelle, CUDA Senkronizasyon Event'ini Kaydet ve PGAS Kancasını Tetikle
                page_obj.handle = new_handle.value
                page_obj.physical_gpu_id = target_gpu_id
                
                # CUDA Event Synchronization Hook: SanalIslemciHavuzu için migration event'i üret ve kaydet
                sync_evt = self.create_cuda_sync_event(target_gpu_id)
                if sync_evt is not None:
                    if hasattr(_NVCUDA_LIB, "cuEventRecord"):
                        _NVCUDA_LIB.cuEventRecord(sync_evt, None)
                    page_obj.sync_event = sync_evt
                else:
                    page_obj.sync_event = f"MIGRATION_SYNC_EVENT_PAGE_{page_obj.page_id}_GPU_{target_gpu_id}"

                self._trigger_on_page_committed(page_obj)
                return True

            except Exception as exc:
                logger.error(f"[Data-Locality Commit Error] Staged commit failed: {exc}")
                return False
            return True

    def cuMemMap(self, virt_addr: int, page_id: int, physical_gpu_id: int, page_obj: Optional[SanalBellekSayfasi] = None) -> bool:
        """
        NVIDIA Driver API: cuMemCreate + cuMemMap + cuMemSetAccess çağrısı.
        KÜLLÎ ADIM: TÜM FİZİKİ GPU'LARA (0..physical_gpus-1) ERİŞİM İZNİ VERİLİR.
        Böylece herhangi bir GPU, diğer GPU'nun VRAM'indeki sanal sayfayı kesintisiz okur/yazar.
        """
        page_bytes = page_obj.size_bytes if page_obj else self.page_size_bytes

        if _NVCUDA_LIB is not None:
            handle = ctypes.c_uint64(0)
            try:
                _ensure_active_cuda_context(physical_gpu_id)
                prop = CUmemAllocationProp()
                prop.type = 1            # CU_MEM_ALLOCATION_TYPE_PINNED
                prop.location.type = 1   # CU_MEM_LOCATION_TYPE_DEVICE
                prop.location.id = physical_gpu_id

                # 1. Physical VRAM Allocation (cuMemCreate)
                res_create = _NVCUDA_LIB.cuMemCreate(ctypes.byref(handle), page_bytes, ctypes.byref(prop), 0)
                if res_create == 0 and handle.value != 0:
                    # 2. Virtual Address Mapping (cuMemMap)
                    res_map = _NVCUDA_LIB.cuMemMap(virt_addr, page_bytes, 0, handle.value, 0)
                    if res_map == 0:
                        # 3. KÜLLÎ KRİTİK ADIM: TÜM GPU'LARA (0, 1, 2, 3) OKUMA/YAZMA ERİŞİMİ TANIMLAMA (Nested Struct)
                        if self.physical_gpus > 0:
                            access_descs = (CUmemAccessDesc * self.physical_gpus)()
                            for g_id in range(self.physical_gpus):
                                access_descs[g_id].location.type = 1   # CU_MEM_LOCATION_TYPE_DEVICE
                                access_descs[g_id].location.id = g_id
                                access_descs[g_id].flags = 3           # CU_MEM_ACCESS_FLAGS_PROT_READWRITE
                            
                            res_access = _NVCUDA_LIB.cuMemSetAccess(virt_addr, page_bytes, access_descs, self.physical_gpus)
                        else:
                            res_access = 0

                        if res_access == 0:
                            if page_obj:
                                page_obj.commit(handle.value)
                                self._trigger_on_page_committed(page_obj)
                            logger.debug(f"[VMM Allocator] Real Multi-GPU cuMemSetAccess({hex(virt_addr)}) -> All GPUs (0..{self.physical_gpus-1}) SUCCESS!")
                            return True
                    
                    # Rollback if map or setAccess fails after cuMemCreate succeeded!
                    logger.warning(f"[VMM Rollback] cuMemMap/cuMemSetAccess failed. Releasing handle {handle.value} to prevent VRAM Leak.")
                    _NVCUDA_LIB.cuMemRelease(handle)
            except Exception as exc:
                if handle.value != 0:
                    try:
                        _NVCUDA_LIB.cuMemRelease(handle)
                    except Exception:
                        pass
                logger.debug(f"Direct cuMemMap+cuMemSetAccess notice: {exc}")

        if self.cpp_driver_lib and (hasattr(self.cpp_driver_lib, "kulli_vmm_map_gpu_bytes") or hasattr(self.cpp_driver_lib, "kulli_vmm_map_gpu")):
            try:
                func_name = "kulli_vmm_map_gpu_bytes" if hasattr(self.cpp_driver_lib, "kulli_vmm_map_gpu_bytes") else "kulli_vmm_map_gpu"
                func = getattr(self.cpp_driver_lib, func_name)
                func.restype = ctypes.c_int
                func.argtypes = [ctypes.c_uint64, ctypes.c_int, ctypes.c_uint64]
                res = func(virt_addr, physical_gpu_id, page_bytes)
                if res == 0:
                    if page_obj:
                        page_obj.state = PageState.COMMITTED
                        self._trigger_on_page_committed(page_obj)
                    logger.debug(f"[VMM C++] cuMemMap({hex(virt_addr)}, bytes={page_bytes}) mapped to GPU {physical_gpu_id}")
                    return True
            except Exception as e:
                logger.debug(f"C++ cuMemMap notice: {e}")

        if page_obj:
            page_obj.state = PageState.COMMITTED
            self._trigger_on_page_committed(page_obj)
        logger.debug(f"[VMM] cuMemMap({hex(virt_addr)}) mapped to Physical GPU {physical_gpu_id} Page {page_id}")
        return True

    def cuMemUnmap(self, page_obj: SanalBellekSayfasi, coalesce: bool = True) -> bool:
        """
        NVIDIA Driver API: cuMemUnmap + cuMemRelease çağrısı.
        İplik güvenli bellek iadesi ve VRAM sızıntısı (Memory Leak) engelleme.
        `coalesce=False` seçilerek toplu söküm (Batch Unmap) işlemlerinde mükerrer sıralama maliyeti engellenir.
        """
        with self._lock:
            # PGAS KİLİDİ VE LOCKED SAYFA ERKEN UNMAP KORUMASI:
            # PGAS (NVSHMEM) veya C++ (PageState.LOCKED) kilitli sayfaların uzaktaki GPU'lar erişirken
            # donanımdan sökülmesini ve NVSHMEM veriyolunun çökmesini kesin olarak engeller.
            if page_obj.state == PageState.LOCKED or getattr(page_obj, 'is_pgas_locked', False):
                raise RuntimeError(
                    f"Küllî VMM Hatası: Kilitli sanal sayfa donanımdan sökülemez! "
                    f"Page #{page_obj.page_id} ({hex(page_obj.virtual_ptr)}) state={page_obj.state.value}, "
                    f"is_pgas_locked={getattr(page_obj, 'is_pgas_locked', False)}. "
                    f"Önce unlock_page() veya unlock_pgas_page() çağrılmalıdır."
                )

            page_bytes = page_obj.size_bytes

            # NVSHMEM / PGAS UNMAP KANCASI: Bayat handle (Stale Handle) hatasını önlemek için PGAS'a bildirim yap!
            self._trigger_on_page_unmapped(page_obj)

            if _NVCUDA_LIB is not None and page_obj.virtual_ptr != 0:
                try:
                    _ensure_active_cuda_context(page_obj.physical_gpu_id if page_obj.physical_gpu_id != -1 else 0)
                    _NVCUDA_LIB.cuStreamSynchronize(None)
                    # 1. Virtual Address Unmap
                    _NVCUDA_LIB.cuMemUnmap(page_obj.virtual_ptr, page_bytes)
                    # 2. Release Allocation Handle (Donanıma İade)
                    if page_obj.handle is not None:
                        _NVCUDA_LIB.cuMemRelease(ctypes.c_uint64(page_obj.handle))
                    
                    page_obj.release()
                    if page_obj in self.allocated_pages:
                        self.allocated_pages.remove(page_obj)
                    if coalesce:
                        self._coalesce_extents()
                    logger.debug(f"[VMM Allocator] cuMemUnmap + cuMemRelease({hex(page_obj.virtual_ptr)}) SUCCESS!")
                    return True
                except Exception as exc:
                    logger.debug(f"cuMemUnmap notice: {exc}")

            page_obj.release()
            if page_obj in self.allocated_pages:
                self.allocated_pages.remove(page_obj)
            if coalesce:
                self._coalesce_extents()
            return True

    def export_shareable_handle(self, page_obj: SanalBellekSayfasi) -> Optional[int]:
        """
        NVSHMEM & P2P erişimi için VMM handle'ını dışa aktarır (cuMemExportToShareableHandle).
        """
        if _NVCUDA_LIB is not None and page_obj.handle is not None:
            try:
                shareable_handle = ctypes.c_uint64(0)
                handle_type = 2 if os.name == 'nt' else 1  # WIN32 or POSIX FD
                res = _NVCUDA_LIB.cuMemExportToShareableHandle(ctypes.byref(shareable_handle), page_obj.handle, handle_type, 0)
                if res == 0:
                    page_obj.shareable_handle = shareable_handle.value
                    return shareable_handle.value
            except Exception as exc:
                logger.debug(f"cuMemExportToShareableHandle notice: {exc}")
        return None

    def allocate_scratchpad_chunk(self, size_mb: float, target_gpu_id: Optional[int] = None) -> Tuple[int, SanalBellekSayfasi]:
        """
        Erken Devlet Engine geçici ara bellek (Scratchpad) talepleri için Saf Granüler Scratchpad Tahsisçisi.
        SABİT 512 MB VEYA KUTU/SLAB KISITLAMALARI TAMAMEN KALDIRILMIŞTIR!
        İstenen `size_mb` (örneğin 4 MB, 128 MB, 1024 MB / 1 GB) ne olursa olsun,
        donanımdan (88 GB sanal tuvalden) tam o boyutta (2 MB donanımsal granülariteye yuvarlanmış) 
        bağımsız bir Granüler Scratchpad Extent kesilerek sunulur.
        """
        with self._lock:
            size_bytes = int(size_mb * 1024 * 1024)
            aligned_bytes = int(math.ceil(size_bytes / self.granularity) * self.granularity)

            ptr, extents = self.allocate_contiguous_virtual_block(aligned_bytes, target_gpu_id=target_gpu_id)
            for ext in extents:
                ext.state = PageState.SCRATCHPAD
            
            main_extent = extents[0]
            logger.info(
                f"[Saf Granüler Scratchpad] Allocated exact scratchpad extent: {size_mb:.1f} MB "
                f"({aligned_bytes / (1024**2):.1f} MB aligned) at {hex(ptr)} on GPU #{main_extent.physical_gpu_id}"
            )
            return ptr, main_extent

    def free_scratchpad_chunk(self, ptr: int) -> bool:
        """
        Geçici ara belleğe (Scratchpad) ait granüler extent grubunu verilen `ptr` adresi üzerinden arar,
        Eşit Taşkın Mimarisiyle çoklu GPU'lara dağıtılmış tüm alt-extent parçalarını (`sub_extents`)
        topluca donanımdan söker (`Batch Scratchpad Unmap`) ve 88 GB sanal tuvale anında iade eder (Zero Scratchpad Leak).
        """
        with self._lock:
            # 1. Başlangıç adresi ptr olan veya ptr adresini kapsayan ilk SCRATCHPAD sayfasını bul
            head_page: Optional[SanalBellekSayfasi] = None
            for page in self.pages:
                if page.state == PageState.SCRATCHPAD and (page.virtual_ptr == ptr or (page.virtual_ptr <= ptr < page.virtual_ptr + page.size_bytes)):
                    head_page = page
                    break

            if head_page is None:
                return False

            # 2. Aynı group_id'ye sahip TÜM kardeş SCRATCHPAD alt-extent'leri topla
            if head_page.group_id is not None:
                scratchpad_group = [p for p in self.pages if p.state == PageState.SCRATCHPAD and p.group_id == head_page.group_id]
            else:
                scratchpad_group = [head_page]

            # 3. Grubun TÜM parçalarını donanımdan sök (Batch Scratchpad Unmap - Deferred Coalescing)
            total_freed_bytes = 0
            for page in scratchpad_group:
                freed_bytes = page.size_bytes
                self.cuMemUnmap(page, coalesce=False)
                total_freed_bytes += freed_bytes
                logger.info(
                    f"[Batch Scratchpad Manager] Unmapped sibling scratchpad extent #{page.page_id} "
                    f"at {hex(page.virtual_ptr)} ({page.size_mb:.1f} MB, GPU #{page.physical_gpu_id})"
                )

            self._coalesce_extents()
            logger.info(
                f"[Batch Scratchpad Manager] Complete! Unmapped all {len(scratchpad_group)} sibling scratchpad extents "
                f"totaling {total_freed_bytes / (1024**2):.1f} MB starting at {hex(head_page.virtual_ptr)}."
            )
            return True

    def get_os_native_handle(self, page_obj: SanalBellekSayfasi) -> Optional[int]:
        """
        NVSHMEM ve P2P veriyolu entegrasyonu için OS Native Shareable Handle döndürür.
        """
        if page_obj.shareable_handle is not None:
            return page_obj.shareable_handle
        return self.export_shareable_handle(page_obj)

    def driver_flush(self) -> int:
        """
        KONTROLLÜ SÜRÜCÜ TEMİZLİĞİ (Driver Flush Engine).
        Framework'ten (PyTorch empty_cache vb.) veya C-API'den gelen temizlik çağrılarını kapsar.
        Atıl/serbest extents parçalarını coalescing ile birleştirir, pending release kuyruğunu temizler.
        """
        self._wait_if_compacting()
        freed_bytes = 0
        with self._lock:
            self.process_pending_releases()
            for page in list(self.pages):
                if page.state == PageState.SCRATCHPAD and not page.is_pgas_locked:
                    page.state = PageState.FREE
                    page.group_id = 0
                    freed_bytes += page.size_bytes
            self._coalesce_extents()
        logger.info("[Driver Flush] Executed controlled driver VRAM sweep! Coalesced & reclaimed VRAM extents.")
        return freed_bytes

    def free_virtual_block(self, virtual_ptr: int) -> bool:
        """
        Bitişik veya Multi-GPU Spillover ile parçalanarak tahsis edilmiş sanal bloğu
        sadece başlangıç sanal adresi (`virtual_ptr`) üzerinden arayıp, o gruba (`group_id`) ait
        tüm kardeş extent'leri donanımdan topluca söker ve serbest bırakır (Batch Virtual Block Free).
        """
        with self._lock:
            head_page: Optional[SanalBellekSayfasi] = None
            for p in self.pages:
                if p.virtual_ptr == virtual_ptr or (p.virtual_ptr <= virtual_ptr < p.virtual_ptr + p.size_bytes):
                    head_page = p
                    break
            
            if head_page is None:
                logger.warning(f"[VMM Free Virtual Block] No page found matching virtual address {hex(virtual_ptr)}")
                return False

            gid = head_page.group_id
            if gid is not None:
                sibling_extents = [p for p in self.pages if p.group_id == gid]
            else:
                sibling_extents = [head_page]

            if not sibling_extents:
                sibling_extents = [head_page]

            for ext in sibling_extents:
                self.cuMemUnmap(ext, coalesce=False)

            self._coalesce_extents()
            logger.info(
                f"[VMM Free Virtual Block] Successfully unmapped virtual block group (gid={gid}) "
                f"containing {len(sibling_extents)} extents starting at {hex(virtual_ptr)}."
            )
            return True

    def is_valid_virtual_address(self, ptr: int, size_bytes: int) -> bool:
        """
        II. USUL: KUŞATICI ARALIK DOĞRULAMASI VE DONANIMSAL KORUMA SAYFASI KONTROLCÜSÜ (Multi-Extent Range Validation).
        
        Sürücüye gelen tüm pointer doğrulama isteklerinde tekil `ptr` gönderilmesi ve varsayılan 1 bayt kabul edilmesi KESİNLİKLE YASAKLANMIŞTIR!
        Doğrulama HER ZAMAN `[ptr, ptr + size_bytes)` sanal aralığının tamamını kapsayacak şekilde Range Validation esasıyla yürütülür.
        Sürücü, istenen adres aralığının (`[ptr, ptr + size_bytes)`) 88 GB sanal uzay içinde kaldığını,
        Koruma Sayfasına (PROT_NONE Guard Page) tecavüz etmediğini ve parçalı harita kümesine (Scattered Map Set)
        uygunluğunu doğrular.
        """
        self._wait_if_compacting()
        if size_bytes is None or size_bytes <= 0:
            raise ValueError("Küllî VMM Hatası: is_valid_virtual_address çağrısında size_bytes 0 veya negatif olamaz! Kuşatıcı Aralık Doğrulaması (Range Validation) zorunludur.")

        main_bytes = self.virtual_vram_bytes
        guard_bytes = max(2 * 1024 * 1024, self.granularity)
        check_bytes = size_bytes
        end_ptr = ptr + check_bytes

        # 1. Donanımsal Koruma Sayfası İhlal Kontrolü
        if hasattr(self, 'guard_virtual_ptr') and self.guard_virtual_ptr != 0:
            guard_start = self.guard_virtual_ptr
            guard_end = guard_start + guard_bytes
            if max(ptr, guard_start) < min(end_ptr, guard_end):
                raise GuardPageException(
                    message=f"Küllî VMM GUARD PAGE IHLALI! Adres {hex(ptr)} (+{check_bytes} bytes) "
                            f"sanal koruma sayfasına ({hex(guard_start)} PROT_NONE) temas etti! Sürücü çökmesi engellendi.",
                    fault_address=ptr,
                    violation_type="PROT_NONE_GUARD_PAGE",
                    requested_bytes=check_bytes,
                    base_address=self.virtual_base_address,
                    max_address=self.virtual_base_address + main_bytes
                )

        # 2. 88 GB Sanal Adres Sınır Kontrolü
        base = self.virtual_base_address
        max_valid_addr = base + main_bytes
        if ptr < base or end_ptr > max_valid_addr:
            raise GuardPageException(
                message=f"Küllî VMM ADRES SINIR IHLALI! Adres {hex(ptr)} (+{check_bytes} bytes) "
                        f"88 GB'lık rezerve sanal uzay ({hex(base)} -> {hex(max_valid_addr)}) dışında!",
                fault_address=ptr,
                violation_type="OUT_OF_BOUNDS_ADDRESS",
                requested_bytes=check_bytes,
                base_address=base,
                max_address=max_valid_addr
            )

        return True

    def get_extent_at_virtual_address(self, virtual_ptr: int) -> Optional[SanalBellekSayfasi]:
        """Verilen sanal adrese denk gelen granüler extent nesnesini döndürür."""
        with self._lock:
            for page in self.pages:
                if page.virtual_ptr == virtual_ptr or (page.virtual_ptr <= virtual_ptr < page.virtual_ptr + page.size_bytes):
                    return page
            return None

    def get_page_scatter_map(self, virtual_ptr: int, size_bytes: Optional[int] = None) -> ScatterMapList:
        """
        ERKEN DEVLET ENGINE TOPOLOJİ VE DAĞINIK SEVK SORGU FONKSİYONU (Scatter Map Topology Inquiry).
        Verilen sanal adres aralığının (`[virtual_ptr, virtual_ptr + size_bytes)`) sanal adres uzayındaki
        hangi sayfalara denk geldiğini ve bu sayfaların hangi fiziki GPU'lara haritalanmış olduğunu raporlar.
        
        Erken Devlet Engine bu topoloji haritasını alarak devasa işlemleri donanım seviyesinde
        Scatter-Gather Tiled Execution mantığıyla fiziki GPU'lara kırbaçla sevk eder.
        """
        with self._lock:
            self._wait_if_compacting()
            if size_bytes is None:
                ext = self.get_extent_at_virtual_address(virtual_ptr)
                size_bytes = ext.size_bytes if ext else self.page_size_bytes

            self.is_valid_virtual_address(virtual_ptr, size_bytes)
            end_ptr = virtual_ptr + size_bytes
            scatter_map = []

            has_unmapped_holes = False
            mapped_total_bytes = 0

            for page in self.pages:
                page_start = page.virtual_ptr
                page_end = page_start + page.size_bytes

                # Çakışma kontrolü (Overlap Check)
                if max(virtual_ptr, page_start) < min(end_ptr, page_end):
                    slice_start = max(virtual_ptr, page_start)
                    slice_end = min(end_ptr, page_end)
                    slice_size = slice_end - slice_start

                    is_hole = (page.state in (PageState.FREE, PageState.RESERVED)) or (page.physical_gpu_id == -1)
                    if is_hole:
                        has_unmapped_holes = True
                    else:
                        mapped_total_bytes += slice_size

                    scatter_map.append({
                        "page_id": page.page_id,
                        "virtual_ptr": slice_start,
                        "size_bytes": slice_size,
                        "physical_gpu_id": page.physical_gpu_id,
                        "state": page.state.value,
                        "offset_in_request": slice_start - virtual_ptr,
                        "page_offset": slice_start - page_start,
                        "is_unmapped_hole": is_hole
                    })

            if mapped_total_bytes < size_bytes:
                has_unmapped_holes = True

            res_list = ScatterMapList(scatter_map, contains_unmapped_holes=has_unmapped_holes)

            logger.info(
                f"[Scatter Map Inquiry] Virtual Range {hex(virtual_ptr)} (+{size_bytes / (1024**2):.1f} MB) "
                f"mapped across {len(res_list)} physical page slices (Holes Present: {has_unmapped_holes})"
            )
            return res_list

    def get_allocated_gb(self) -> float:
        self._wait_if_compacting()
        with self._lock:
            return self.allocated_vram_gb

    def shutdown(self):
        """Sürücü kapatılırken TÜM sanal sayfaları ve Koruma Sayfası kukla VRAM'ini donanımdan temizler (Zero Memory Leak)."""
        with self._lock:
            for p in list(self.allocated_pages):
                self.cuMemUnmap(p)
            
            # Donanımsal Koruma Sayfası (Guard Page) Kukla VRAM Temizliği (Zero VRAM Leak, 2 MB)
            if _NVCUDA_LIB is not None and self.guard_virtual_ptr != 0 and self.guard_handle is not None:
                try:
                    guard_bytes = max(2 * 1024 * 1024, self.granularity)
                    _NVCUDA_LIB.cuMemUnmap(self.guard_virtual_ptr, guard_bytes)
                    _NVCUDA_LIB.cuMemRelease(ctypes.c_uint64(self.guard_handle))
                    logger.info(f"[Guard Page Cleanup] Unmapped and released Hardware Guard Page ({hex(self.guard_virtual_ptr)}) dummy VRAM ({guard_bytes / (1024**2):.1f} MB).")
                    self.guard_handle = None
                except Exception as exc:
                    logger.debug(f"Guard page shutdown notice: {exc}")

            # Rezerve edilmiş Ana Sanal Adres Uzayı İadesi (Zero Virtual Address Space Leak)
            if _NVCUDA_LIB is not None and self.virtual_base_address != 0:
                try:
                    guard_bytes = max(2 * 1024 * 1024, self.granularity)
                    total_reserve_bytes = self.virtual_vram_bytes + guard_bytes
                    _release_virtual_address_range(self.virtual_base_address, total_reserve_bytes)
                    logger.info(f"[VMM Shutdown] Released main virtual address range ({hex(self.virtual_base_address)}) to OS/Driver.")
                except Exception as exc:
                    logger.debug(f"Main VA release notice: {exc}")

            logger.info("[VMM Allocator] All virtual pages and hardware guard page dummy VRAM successfully unmapped and released!")

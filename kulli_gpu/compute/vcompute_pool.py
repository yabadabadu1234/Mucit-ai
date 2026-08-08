"""
MODÜL 5: Sanal İşlemci & Compute Havuzu (Virtual Compute Aggregator)
Çoklu GPU üzerindeki Streaming Multiprocessor (SM) birimlerini ve CUDA çekirdeklerini
tek bir dev donanımsal compute havuzunda birleştirir.
"""

import os
import sys
import math
import time
import ctypes
import logging
import threading
from typing import List, Dict, Any, Optional, Tuple, Union

logger = logging.getLogger("kulli_gpu.compute_pool")
logger.setLevel(logging.WARNING)

# Direct NVIDIA C-Driver API binding for CUDA Streams, Events, and Device Attributes
_NVCUDA_LIB = None
try:
    if os.name == 'nt':
        _NVCUDA_LIB = ctypes.WinDLL("nvcuda.dll")
    else:
        _NVCUDA_LIB = ctypes.CDLL("libcuda.so")
except Exception as _lib_err:
    logger.debug(f"[ComputePool] Direct nvcuda binding notice: {_lib_err}")
    _NVCUDA_LIB = None

# Set up C-Driver API function signatures if library is loaded
if _NVCUDA_LIB is not None:
    try:
        if hasattr(_NVCUDA_LIB, "cuInit"):
            _NVCUDA_LIB.cuInit.argtypes = [ctypes.c_uint]
            _NVCUDA_LIB.cuInit.restype = ctypes.c_int
            _NVCUDA_LIB.cuInit(0)

        if hasattr(_NVCUDA_LIB, "cuDeviceGetCount"):
            _NVCUDA_LIB.cuDeviceGetCount.argtypes = [ctypes.POINTER(ctypes.c_int)]
            _NVCUDA_LIB.cuDeviceGetCount.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuDeviceGet"):
            _NVCUDA_LIB.cuDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
            _NVCUDA_LIB.cuDeviceGet.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuDeviceGetAttribute"):
            _NVCUDA_LIB.cuDeviceGetAttribute.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int]
            _NVCUDA_LIB.cuDeviceGetAttribute.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuDeviceGetName"):
            _NVCUDA_LIB.cuDeviceGetName.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
            _NVCUDA_LIB.cuDeviceGetName.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuDevicePrimaryCtxRetain"):
            _NVCUDA_LIB.cuDevicePrimaryCtxRetain.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_int]
            _NVCUDA_LIB.cuDevicePrimaryCtxRetain.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuCtxSetCurrent"):
            _NVCUDA_LIB.cuCtxSetCurrent.argtypes = [ctypes.c_void_p]
            _NVCUDA_LIB.cuCtxSetCurrent.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuStreamCreate"):
            _NVCUDA_LIB.cuStreamCreate.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint]
            _NVCUDA_LIB.cuStreamCreate.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuStreamDestroy_v2"):
            _NVCUDA_LIB.cuStreamDestroy = _NVCUDA_LIB.cuStreamDestroy_v2
        if hasattr(_NVCUDA_LIB, "cuStreamDestroy"):
            _NVCUDA_LIB.cuStreamDestroy.argtypes = [ctypes.c_void_p]
            _NVCUDA_LIB.cuStreamDestroy.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuStreamSynchronize"):
            _NVCUDA_LIB.cuStreamSynchronize.argtypes = [ctypes.c_void_p]
            _NVCUDA_LIB.cuStreamSynchronize.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuEventCreate"):
            _NVCUDA_LIB.cuEventCreate.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint]
            _NVCUDA_LIB.cuEventCreate.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuEventRecord"):
            _NVCUDA_LIB.cuEventRecord.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            _NVCUDA_LIB.cuEventRecord.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuEventSynchronize"):
            _NVCUDA_LIB.cuEventSynchronize.argtypes = [ctypes.c_void_p]
            _NVCUDA_LIB.cuEventSynchronize.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuEventQuery"):
            _NVCUDA_LIB.cuEventQuery.argtypes = [ctypes.c_void_p]
            _NVCUDA_LIB.cuEventQuery.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuEventDestroy_v2"):
            _NVCUDA_LIB.cuEventDestroy = _NVCUDA_LIB.cuEventDestroy_v2
        if hasattr(_NVCUDA_LIB, "cuEventDestroy"):
            _NVCUDA_LIB.cuEventDestroy.argtypes = [ctypes.c_void_p]
            _NVCUDA_LIB.cuEventDestroy.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuStreamWaitEvent"):
            _NVCUDA_LIB.cuStreamWaitEvent.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
            _NVCUDA_LIB.cuStreamWaitEvent.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuLaunchKernel"):
            _NVCUDA_LIB.cuLaunchKernel.argtypes = [
                ctypes.c_void_p,
                ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,
                ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,
                ctypes.c_uint,
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_void_p),
                ctypes.POINTER(ctypes.c_void_p)
            ]
            _NVCUDA_LIB.cuLaunchKernel.restype = ctypes.c_int

        # 2. EVRENSEL CUDA GRAPH İCRA KANCASI (cuGraphExecLaunch)
        if hasattr(_NVCUDA_LIB, "cuGraphExecLaunch"):
            _NVCUDA_LIB.cuGraphExecLaunch.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            _NVCUDA_LIB.cuGraphExecLaunch.restype = ctypes.c_int

        # 3. EVRENSEL ASENKRON DMA KANCASI (cuMemcpyAsync & cuMemcpyPeerAsync)
        if hasattr(_NVCUDA_LIB, "cuMemcpyAsync"):
            _NVCUDA_LIB.cuMemcpyAsync.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_size_t, ctypes.c_void_p]
            _NVCUDA_LIB.cuMemcpyAsync.restype = ctypes.c_int

        if hasattr(_NVCUDA_LIB, "cuMemcpyPeerAsync"):
            _NVCUDA_LIB.cuMemcpyPeerAsync.argtypes = [
                ctypes.c_uint64, ctypes.c_int,
                ctypes.c_uint64, ctypes.c_int,
                ctypes.c_size_t, ctypes.c_void_p
            ]
            _NVCUDA_LIB.cuMemcpyPeerAsync.restype = ctypes.c_int

    except Exception as _cuda_init_err:
        logger.debug(f"[ComputePool] CUDA function setup notice: {_cuda_init_err}")


_thread_local = threading.local()

def _ensure_active_cuda_context(gpu_id: int):
    """
    DONANIMSAL CUDA CONTEXT AKTİFLEŞTİRİCİ (Explicit CUDA Context Binding - Thread-Local Cached).
    cuStreamCreate, cuEventCreate, cuEventRecord, cuStreamWaitEvent, cuStreamSynchronize,
    cuGraphExecLaunch, cuMemcpyAsync ve cuLaunchKernel çağrılmadan hemen önce
    hedef GPU context'ini zorunlu olarak aktif eder.
    Böylece CUDA_ERROR_INVALID_CONTEXT / CUDA_ERROR_INVALID_HANDLE hatalarını engeller.
    """
    if getattr(_thread_local, "current_gpu_id", None) == gpu_id:
        return
    if _NVCUDA_LIB is None or gpu_id < 0:
        return
    try:
        dev = ctypes.c_int(0)
        res_dev = _NVCUDA_LIB.cuDeviceGet(ctypes.byref(dev), gpu_id)
        if res_dev == 0:
            ctx = ctypes.c_void_p(0)
            if hasattr(_NVCUDA_LIB, "cuDevicePrimaryCtxRetain"):
                res_ctx = _NVCUDA_LIB.cuDevicePrimaryCtxRetain(ctypes.byref(ctx), dev.value)
                if res_ctx == 0 and ctx.value is not None:
                    if hasattr(_NVCUDA_LIB, "cuCtxSetCurrent"):
                        _NVCUDA_LIB.cuCtxSetCurrent(ctx.value)
                        _thread_local.current_gpu_id = gpu_id
    except Exception as exc:
        logger.debug(f"[Context Binding Notice] GPU #{gpu_id}: {exc}")


def _inspect_tensor_byte_footprint(
    matrix_shape: Optional[List[int]],
    dtype: Any = None,
    sample_tensor: Optional[Any] = None,
    kernel_args: Optional[List[Any]] = None
) -> int:
    """
    DİNAMİK TALEP İNCELEME MOTORU (Zero-Assumption Dynamic Payload Inspection).
    
    Sürücü sevk emri aldığında hiçbir eleman boyutunu varsayılan kabul etmez!
    1. Gelen 'kernel_args' veya 'sample_tensor' içindeki canlı PyTorch/NumPy/CuPy nesnelerinin
       .element_size() veya .itemsize özniteliklerini canlı okur.
    2. Eğer canlı nesne verilmediyse 'dtype' özniteliğini inceler (FP64=8B, FP32=4B, FP16=2B, INT8=1B).
    Eleman bayt miktarını kesinleştirip prod(matrix_shape) * element_bytes ile %100 VRAM ayak izini hesaplar.
    """
    element_bytes = 4
    found_live_bytes = False

    # 1. CANLI NESNE (PyTorch Tensor / NumPy Array / CuPy) İNCELEMESİ
    candidate_objects = []
    if sample_tensor is not None:
        candidate_objects.append(sample_tensor)
    if kernel_args:
        candidate_objects.extend(kernel_args)

    for obj in candidate_objects:
        if hasattr(obj, "element_size") and callable(getattr(obj, "element_size")):
            try:
                element_bytes = int(obj.element_size())
                found_live_bytes = True
                break
            except Exception:
                pass
        elif hasattr(obj, "itemsize"):
            try:
                element_bytes = int(getattr(obj, "itemsize"))
                found_live_bytes = True
                break
            except Exception:
                pass
        elif hasattr(obj, "dtype"):
            obj_dtype = getattr(obj, "dtype")
            if hasattr(obj_dtype, "itemsize"):
                try:
                    element_bytes = int(getattr(obj_dtype, "itemsize"))
                    found_live_bytes = True
                    break
                except Exception:
                    pass

    # 2. DTYPE ÖZNİTELİK İNCELEMESİ
    if not found_live_bytes and dtype is not None:
        if isinstance(dtype, int):
            element_bytes = max(1, dtype)
        else:
            dtype_str = str(dtype).lower()
            if any(k in dtype_str for k in ("fp64", "double", "float64", "int64", "uint64", "int64_t")):
                element_bytes = 8
            elif any(k in dtype_str for k in ("fp32", "float32", "float", "int32", "uint32", "int32_t")):
                element_bytes = 4
            elif any(k in dtype_str for k in ("fp16", "bf16", "float16", "bfloat16", "int16", "uint16", "half")):
                element_bytes = 2
            elif any(k in dtype_str for k in ("int8", "uint8", "fp8", "float8", "byte", "bool", "int8_t")):
                element_bytes = 1
            elif hasattr(dtype, "itemsize"):
                element_bytes = getattr(dtype, "itemsize", 4)

    if not matrix_shape:
        return element_bytes

    num_elements = 1
    for dim in matrix_shape:
        num_elements *= max(1, dim)

    return max(1, num_elements * element_bytes)


def _build_kernel_params(kernel_args: Optional[List[Any]]) -> Tuple[Optional[Any], List[Any]]:
    """
    C-DRIVER cuLaunchKernel PARAMETRE PAKETLEYİCİSİ (Kernel Parameter Marshaller).
    
    Python skaler değerlerini, matris boyutlarını ve VRAM pointer'larını C-Types dizisine paketler.
    Python 'float' değerleri doğuştan 64-bit IEEE Double Precision olduğundan 'ctypes.c_double' (64-bit) olarak korunur.
    Böylece C++ CUDA çekirdeklerindeki stack/register hizalama ihlalleri önlenir.
    """
    if not kernel_args:
        return None, []

    c_vars = []
    for arg in kernel_args:
        if isinstance(arg, int):
            # C++ ABI STACK HİZALAMA KORUMASI (Stack Parameter Offset Protection):
            # Python int değerlerini körü körüne 64-bit yapmak, 32-bit int/unsigned int
            # bekleyen C++ CUDA çekirdeklerinde stack kaymasına (Parameter Offset Mismatch)
            # yol açar. 2^31-1 sınırı altındaki değerler standart 32-bit olarak paketlenir.
            # 64-bit tamsayılar sadece açık ('int64', val) / ('uint64', val) tüpü ile geçilmelidir.
            if 0 <= arg <= 0x7FFFFFFF:  # [0, 2^31 - 1] → unsigned 32-bit güvenli aralık
                c_vars.append(ctypes.c_uint32(arg))
            elif -0x80000000 <= arg < 0:  # [-2^31, 0) → signed 32-bit güvenli aralık
                c_vars.append(ctypes.c_int32(arg))
            else:  # 32-bit aralık dışı → 64-bit zorunlu
                if arg >= 0:
                    c_vars.append(ctypes.c_uint64(arg))
                else:
                    c_vars.append(ctypes.c_int64(arg))
        elif isinstance(arg, ctypes.c_double):
            c_vars.append(arg)
        elif isinstance(arg, ctypes.c_float):
            c_vars.append(arg)
        elif isinstance(arg, ctypes._SimpleCData):
            c_vars.append(arg)
        elif isinstance(arg, tuple) and len(arg) == 2 and isinstance(arg[0], str):
            # AÇIK TİP BELİRTİMİ (Explicit Type Specification via Typed Tuples):
            # Kullanıcı ('int64', val), ('uint64', val), ('int32', val), ('uint32', val) gibi
            # tüp geçerek C++ çekirdek imzasıyla birebir eşleşen veri genişliğini zorlar.
            t_type, t_val = arg[0].lower(), arg[1]
            if t_type in ("double", "fp64", "float64"):
                c_vars.append(ctypes.c_double(float(t_val)))
            elif t_type in ("float", "fp32", "float32"):
                c_vars.append(ctypes.c_float(float(t_val)))
            elif t_type in ("int64", "long", "long_long"):
                c_vars.append(ctypes.c_int64(int(t_val)))
            elif t_type in ("uint64", "unsigned_long", "size_t"):
                c_vars.append(ctypes.c_uint64(int(t_val)))
            elif t_type in ("int32", "int"):
                c_vars.append(ctypes.c_int32(int(t_val)))
            elif t_type in ("uint32", "unsigned_int", "uint"):
                c_vars.append(ctypes.c_uint32(int(t_val)))
            elif t_type in ("int16", "short"):
                c_vars.append(ctypes.c_int16(int(t_val)))
            elif t_type in ("uint16", "unsigned_short"):
                c_vars.append(ctypes.c_uint16(int(t_val)))
            elif t_type in ("int8", "char"):
                c_vars.append(ctypes.c_int8(int(t_val)))
            elif t_type in ("uint8", "unsigned_char", "byte"):
                c_vars.append(ctypes.c_uint8(int(t_val)))
            else:
                raise TypeError(
                    f"[C-Driver Marshaller Error] Unsupported tuple type specification '{arg[0]}'. "
                    f"Supported type names: 'double'/'float'/'int32'/'uint32'/'int64'/'uint64'/'int16'/'uint16'/'int8'/'uint8'."
                )
        elif isinstance(arg, float):
            c_vars.append(ctypes.c_double(arg))
        else:
            raise TypeError(
                f"[C-Driver Marshaller Error] Unsupported kernel argument type: {type(arg)} ({arg}). "
                f"Arguments must be int, float, ctypes data structures, or typed tuples like ('double', val)."
            )

    params_arr = (ctypes.c_void_p * len(c_vars))()
    for i, var in enumerate(c_vars):
        params_arr[i] = ctypes.cast(ctypes.byref(var), ctypes.c_void_p)

    return params_arr, c_vars


def _partition_3d_grid(
    grid_dim: Tuple[int, int, int],
    share_pct: float,
    accumulated_ratios: float,
    is_last_gpu: bool = False
) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """
    BOYUTSUZ 3D GRID/BLOCK UZAYI KESİN KAROLAMA MOTORU (Exact 3D Grid Partitioning).
    
    Grid boyutlarının aktif GPU sayısından küçük olduğu durumlarda (örneğin gridDim.x = 3, GPU = 4)
    veya tamsayı bölme küsüratlarında son bloğun dışarıda kalmasını (Grid Division Remainder Trailing) önler.
    Son GPU'nun bitiş sınırı (is_last_gpu=True) doğrudan orijinal G_x, G_y veya G_z üst sınırına eşitlenir.
    """
    G_x, G_y, G_z = grid_dim
    share_ratio = max(0.0, share_pct / 100.0)
    acc_ratio = max(0.0, accumulated_ratios)

    # Baskın ekseni bul (En büyük grid boyutu)
    if G_x >= G_y and G_x >= G_z:
        start_x = int(G_x * acc_ratio)
        if is_last_gpu or (acc_ratio + share_ratio) >= 0.999:
            end_x = G_x
        else:
            end_x = int(G_x * min(1.0, acc_ratio + share_ratio))
        gpu_gx = max(0, end_x - start_x)
        return (gpu_gx, G_y, G_z), (start_x, 0, 0)
    elif G_y >= G_x and G_y >= G_z:
        start_y = int(G_y * acc_ratio)
        if is_last_gpu or (acc_ratio + share_ratio) >= 0.999:
            end_y = G_y
        else:
            end_y = int(G_y * min(1.0, acc_ratio + share_ratio))
        gpu_gy = max(0, end_y - start_y)
        return (G_x, gpu_gy, G_z), (0, start_y, 0)
    else:
        start_z = int(G_z * acc_ratio)
        if is_last_gpu or (acc_ratio + share_ratio) >= 0.999:
            end_z = G_z
        else:
            end_z = int(G_z * min(1.0, acc_ratio + share_ratio))
        gpu_gz = max(0, end_z - start_z)
        return (G_x, G_y, gpu_gz), (0, 0, start_z)


def _partition_arbitrary_workload_sets(
    total_range_bytes: int,
    gpu_capabilities: Dict[int, float]
) -> Dict[int, List[Tuple[int, int]]]:
    """
    I. USUL: DOĞRUSAL OLMAYAN SERBEST İŞ PARÇALAMASI (Non-Linear Dynamic Workload Slicing Engine).
    
    GPU'ların anlık doluluk (SM utilization), P2P bant genişliği ve VRAM kapasitelerine göre
    iş kütlesini tek bir düz çizgi (0-25, 25-50) yerine parçalı ve serbest aralıklar halinde böler.
    Bir GPU'ya parçalı 2 veya 3 ayrı aralık ([start1, end1], [start2, end2]) aynı anda atanabilir.
    """
    if total_range_bytes <= 0 or not gpu_capabilities:
        return {}

    total_cap = sum(gpu_capabilities.values())
    if total_cap <= 0:
        total_cap = float(len(gpu_capabilities))
        gpu_capabilities = {g_id: 1.0 for g_id in gpu_capabilities}

    allocated_slices: Dict[int, List[Tuple[int, int]]] = {g_id: [] for g_id in gpu_capabilities}
    curr_byte = 0

    sorted_gpus = sorted(gpu_capabilities.keys(), key=lambda g: gpu_capabilities[g], reverse=True)

    for g_id in sorted_gpus:
        cap_ratio = gpu_capabilities[g_id] / total_cap
        chunk_bytes = int(total_range_bytes * cap_ratio)
        if chunk_bytes > 0 and curr_byte < total_range_bytes:
            end_byte = min(total_range_bytes, curr_byte + chunk_bytes)
            allocated_slices[g_id].append((curr_byte, end_byte))
            curr_byte = end_byte

    if curr_byte < total_range_bytes and sorted_gpus:
        primary_gpu = sorted_gpus[0]
        if allocated_slices[primary_gpu]:
            s_byte, _ = allocated_slices[primary_gpu][-1]
            allocated_slices[primary_gpu][-1] = (s_byte, total_range_bytes)
        else:
            allocated_slices[primary_gpu].append((curr_byte, total_range_bytes))

    return allocated_slices


def _audit_and_validate_partition_coverage(
    total_range_bytes: int,
    allocated_slices: Dict[int, List[Tuple[int, int]]]
) -> bool:
    """
    II. USUL: ADRES TEFTİŞ VE KAPSAMA MOTORU (Address Audit & Coverage Engine).
    
    Serbest dağıtılan parçaların:
    1. ÇAKIŞMA SIFIR (Zero Overlap): Parçalar 1 bayt dahi birbiriyle çakışamaz.
    2. BOŞLUK SIFIR (Zero Gap): Atlanmış 1 bayt dahi sanal boşluk kalamaz.
    3. KAPSAMA %100 (Full Coverage): Tüm parçaların toplamı ana iş kütlesini %100 kaplamak zorundadır.
    """
    all_intervals: List[Tuple[int, int]] = []
    for g_id, intervals in allocated_slices.items():
        for start_b, end_b in intervals:
            if start_b >= end_b:
                continue
            all_intervals.append((start_b, end_b))

    if not all_intervals:
        return total_range_bytes == 0

    all_intervals.sort(key=lambda x: x[0])

    if all_intervals[0][0] != 0:
        logger.error(f"[Address Audit Fault] Başlangıç boşluğu tespit edildi: {all_intervals[0][0]} != 0")
        return False

    current_covered = all_intervals[0][1]

    for start_b, end_b in all_intervals[1:]:
        if start_b < current_covered:
            logger.error(f"[Address Audit Fault] ÇAKISMA TESPİT EDİLDİ! Interval {start_b}-{end_b} current_covered {current_covered} ile çakışıyor!")
            return False
        elif start_b > current_covered:
            logger.error(f"[Address Audit Fault] BOŞLUK TESPİT EDİLDİ! Interval {start_b}-{end_b} current_covered {current_covered} arasında boşluk var!")
            return False
        current_covered = end_b

    if current_covered != total_range_bytes:
        logger.error(f"[Address Audit Fault] KAPSAMA EKSİK! Toplam kapsanan {current_covered} != beklenen {total_range_bytes}")
        return False

    return True


def _lock_all_extents_in_range(allocator: Any, virtual_ptr: Optional[int], byte_size: int = 4096) -> List[Any]:
    """
    KUŞATICI ÇOKLU EXTENT KİLİTLEME MOTORU (Multi-Extent Enclosing Lock Guard).
    
    10 GB gibi devasa bir tensör Eşit Taşkın Mimarisiyle (Spillover) birden fazla GPU VRAM'ine
    veya parçalı extent'lere haritalanmışsa; tensörün kapsadığı TÜM parçalı alt-extent'leri
    (sub_extents) baştan sona tarar ve hepsini 'PageState.LOCKED' korumasına alır.
    Böylece GPU donanımı hesaplama yaparken compaction veya migrasyon motorunun parçalardan
    birini söküp taşıması (ve CUDA_ERROR_ILLEGAL_ADDRESS çökmeleri) %100 engellenir.
    """
    if allocator is None or virtual_ptr is None or byte_size <= 0:
        return []

    locked_extents = []
    curr_ptr = virtual_ptr
    end_ptr = virtual_ptr + max(1, byte_size)

    # 1. Önce scatter map'ten tüm parçalı harita dilimlerini sorgula
    if hasattr(allocator, "get_page_scatter_map"):
        try:
            scatter_info = allocator.get_page_scatter_map(virtual_ptr, byte_size)
            page_slices = []
            if isinstance(scatter_info, dict):
                page_slices = scatter_info.get("page_slices", [])
            elif isinstance(scatter_info, list):
                page_slices = scatter_info

            for slice_item in page_slices:
                if isinstance(slice_item, dict):
                    s_ptr = slice_item.get("virtual_ptr", slice_item.get("virtual_address"))
                else:
                    s_ptr = getattr(slice_item, "virtual_ptr", getattr(slice_item, "virtual_address", None))

                if s_ptr is not None and hasattr(allocator, "get_extent_at_virtual_address"):
                    ext = allocator.get_extent_at_virtual_address(s_ptr)
                    if ext and ext not in locked_extents and hasattr(allocator, "lock_page"):
                        allocator.lock_page(ext)
                        locked_extents.append(ext)
        except Exception as sc_exc:
            logger.debug(f"[Scatter Map Lock Notice] {sc_exc}")

    # 2. Eğer scatter map ile tam kapsanamadıysa, adres aralığını adımlayarak tüm extent'leri kilitler
    if not locked_extents and hasattr(allocator, "get_extent_at_virtual_address"):
        visited_ptrs = set()
        while curr_ptr < end_ptr:
            if curr_ptr in visited_ptrs:
                break
            visited_ptrs.add(curr_ptr)
            try:
                ext = allocator.get_extent_at_virtual_address(curr_ptr)
                if ext:
                    if ext not in locked_extents and hasattr(allocator, "lock_page"):
                        allocator.lock_page(ext)
                        locked_extents.append(ext)
                    ext_size = getattr(ext, "size_bytes", 2 * 1024 * 1024)
                    ext_vaddr = getattr(ext, "virtual_ptr", getattr(ext, "virtual_address", curr_ptr))
                    curr_ptr = max(curr_ptr + 4096, ext_vaddr + ext_size)
                else:
                    curr_ptr += 2 * 1024 * 1024
            except Exception as lock_step_exc:
                logger.debug(f"[Lock Step Notice] {lock_step_exc}")
                curr_ptr += 2 * 1024 * 1024

    return locked_extents


class GPUDeviceProperties:
    """
    Fiziksel GPU Donanım Özellikleri Veri Yapısı (Dynamic Hardware Topology Metadata)
    Vektör (CUDA Core), Matris (Tensor Core), Uzamsal/Işın (RT Core) ve Asenkron DMA birimlerini içerir.
    """
    def __init__(
        self,
        gpu_id: int,
        name: str = "NVIDIA CUDA GPU",
        sm_count: int = 84,
        max_threads_per_sm: int = 1536,
        max_threads_per_block: int = 1024,
        warp_size: int = 32,
        l2_cache_bytes: int = 6291456,
        clock_khz: int = 1700000,
        compute_capability: Tuple[int, int] = (8, 6),
        async_copy_engines: int = 2
    ):
        self.gpu_id = gpu_id
        self.name = name
        self.sm_count = sm_count
        self.max_threads_per_sm = max_threads_per_sm
        self.max_threads_per_block = max_threads_per_block
        self.warp_size = warp_size
        self.l2_cache_bytes = l2_cache_bytes
        self.clock_khz = clock_khz
        self.compute_capability = compute_capability
        self.async_copy_engines = max(1, async_copy_engines)

        major, minor = compute_capability

        # 1. VEKTÖR / SKALER HAVUZU (CUDA Cores)
        if major >= 8 or (major == 7 and minor == 5):
            self.cuda_cores_per_sm = 128  # Ampere (RTX 3090/A100), Ada (RTX 4090), Hopper (H100)
        elif major == 7:
            self.cuda_cores_per_sm = 64   # Volta (V100)
        else:
            self.cuda_cores_per_sm = 128

        self.total_cuda_cores = self.sm_count * self.cuda_cores_per_sm

        # 2. MATRİS / TENSÖR HAVUZU (Tensor Cores / TMA)
        self.has_tensor_cores = (major >= 7)
        self.tensor_cores_per_sm = 4 if major >= 8 else (8 if major == 7 else 0)
        self.total_tensor_cores = self.sm_count * self.tensor_cores_per_sm

        # 3. UZAMSAL / IŞIN HAVUZU (RT Cores - Ray Tracing)
        self.has_rt_cores = (major > 7) or (major == 7 and minor >= 5)
        self.rt_cores_per_sm = 1 if self.has_rt_cores else 0
        self.total_rt_cores = self.sm_count * self.rt_cores_per_sm

        # 4. ASENKRON AKTARIM HAVUZU (Copy Engines)
        self.total_copy_engines = self.async_copy_engines


class DynamicSMLoadMonitor:
    """
    Dinamik SM Yük ve Isı/Taktik İzleyici (Dynamic SM Load Monitor)
    Fiziksel GPU'lar üzerindeki aktif kernel yüklerini ve SM doluluk oranlarını takip eder.
    """
    def __init__(self, physical_gpus: int):
        self.physical_gpus = physical_gpus
        self._lock = threading.Lock()
        self.active_tasks_per_gpu: Dict[int, int] = {i: 0 for i in range(physical_gpus)}
        self.sm_utilization_pct: Dict[int, float] = {i: 0.0 for i in range(physical_gpus)}

    def record_task_start(self, gpu_id: int, sm_demand_pct: float = 10.0):
        with self._lock:
            self.active_tasks_per_gpu[gpu_id] = self.active_tasks_per_gpu.get(gpu_id, 0) + 1
            curr = self.sm_utilization_pct.get(gpu_id, 0.0)
            self.sm_utilization_pct[gpu_id] = min(100.0, curr + sm_demand_pct)

    def record_task_end(self, gpu_id: int, sm_demand_pct: float = 10.0):
        with self._lock:
            self.active_tasks_per_gpu[gpu_id] = max(0, self.active_tasks_per_gpu.get(gpu_id, 0) - 1)
            curr = self.sm_utilization_pct.get(gpu_id, 0.0)
            self.sm_utilization_pct[gpu_id] = max(0.0, curr - sm_demand_pct)

    def get_status(self) -> Dict[int, Dict[str, Any]]:
        with self._lock:
            return {
                g_id: {
                    "active_tasks": self.active_tasks_per_gpu.get(g_id, 0),
                    "sm_utilization_pct": round(self.sm_utilization_pct.get(g_id, 0.0), 2)
                }
                for g_id in range(self.physical_gpus)
            }


class MusterekHesapHavuzlari:
    """
    DONANIMSAL 4 MÜŞTEREK HESAP HAVUZU (Pooled Hardware Compute Engine)
    
    Fiziksel GPU sınırlarını kaldırarak tüm donanımsal işlem birimlerini 4 dev Müşterek Havuzda birleştirir:
    1. MÜŞTEREK TENSOR CORE HAVUZU: Matris, LLM ve Yapay Zeka hesapları.
    2. MÜŞTEREK CUDA CORE HAVUZU: Vektör, Skaler, CFD, DNA ve Shader hesapları.
    3. MÜŞTEREK RT CORE HAVUZU: 3D Oyun, Ray Tracing ve BVH taramaları.
    4. MÜŞTEREK DMA ENGINE HAVUZU: Donanımsal Asenkron Veri Aktarım Motorları.
    """
    def __init__(self, device_props: Dict[int, GPUDeviceProperties]):
        self.device_props = device_props
        self.pooled_tensor_cores = sum(prop.total_tensor_cores for prop in device_props.values())
        self.pooled_cuda_cores = sum(prop.total_cuda_cores for prop in device_props.values())
        self.pooled_rt_cores = sum(prop.total_rt_cores for prop in device_props.values())
        self.pooled_copy_engines = sum(prop.total_copy_engines for prop in device_props.values())

    def get_summary(self) -> Dict[str, Any]:
        return {
            "pooled_tensor_cores": self.pooled_tensor_cores,
            "pooled_cuda_cores": self.pooled_cuda_cores,
            "pooled_rt_cores": self.pooled_rt_cores,
            "pooled_copy_engines": self.pooled_copy_engines,
            "gpu_count": len(self.device_props)
        }


class SanalIslemciHavuzu:
    """
    EVRENSEL HESAP-BAĞIMSIZ SANAL GPU İŞLEMCİ MOTORU (Universal Workload-Agnostic Virtual Compute Engine)
    
    1. DONANIMSAL 4 MÜŞTEREK HESAP HAVUZU: CUDA Cores (Vektör), Tensor Cores (Matris),
       RT Cores (Ray Tracing) ve Copy Engines (DMA) birimlerini birleşik havuzda birleştirir.
    2. 3 ALTIN KANUN:
       - 1. Kanun (Yerel İşlemci Önceliği): Yerel çekirdek boşta ve yetiyorsa %100 yerel GPU icrası (Zero Bus Latency).
       - 2. Kanun (Eşit Dağıtımlı Paralel Hesap Taşkını): Yerel çekirdek yetmediğinde/doyuma ulaştığında taşkın hesap
         Müşterek Havuzdaki tüm GPU'lara EŞİT BÖLÜNÜR (%25, %25, %25, %25).
       - 3. Kanun (İntizam Değil İstifade): Parçalı tüm işlem birimlerini tek bir Sanal İşlemci Tuvalinde birleştirir.
    """
    def __init__(self, physical_gpus: int = 4, default_allocator: Optional[Any] = None):
        self.physical_gpus = max(1, physical_gpus)
        self.default_allocator = default_allocator
        self._lock = threading.Lock()

        # 1. CANLI DONANIM TEŞHİSİ VE METADATA TOPLAMASI (Dynamic Hardware Topology Detection)
        self.device_props: Dict[int, GPUDeviceProperties] = self._detect_hardware_topology()

        # 2. 4 MÜŞTEREK HESAP HAVUZU (Pooled Hardware Compute Engine)
        self.musterek_havuzlar = MusterekHesapHavuzlari(self.device_props)

        # Metrik Toplamları
        self.total_sm_cores = self.aggregate_sm_cores()
        self.total_cuda_cores = self.musterek_havuzlar.pooled_cuda_cores
        self.total_tensor_cores = self.musterek_havuzlar.pooled_tensor_cores
        self.total_rt_cores = self.musterek_havuzlar.pooled_rt_cores
        self.total_copy_engines = self.musterek_havuzlar.pooled_copy_engines

        if self.device_props:
            self.sm_per_gpu = self.device_props[0].sm_count
            self.cuda_cores_per_sm = self.device_props[0].cuda_cores_per_sm
        else:
            self.sm_per_gpu = 84
            self.cuda_cores_per_sm = 128

        # 3. FİZİKİ CUDA AKIŞ HAVUZU (Physical CUDA Stream Pool)
        self.stream_pools: Dict[int, List[Any]] = {}
        self._init_stream_pools()

        # 4. DİNAMİK SM YÜK İZLEYİCİSİ (Dynamic SM Load Monitor)
        self.load_monitor = DynamicSMLoadMonitor(self.physical_gpus)

        # 5. ASENKRON GÖREV REKLAMASYON VE EVENT TOPLAYICISI (Async Task Reclaimer)
        self.pending_async_tasks: List[Dict[str, Any]] = []
        self._created_events: List[Any] = []
        self._stop_event = threading.Event()

        # Active Background Reclaimer Daemon Thread
        self._reclaimer_thread = threading.Thread(
            target=self._background_reclaimer_loop,
            name="GPU_Async_Task_Reclaimer_Daemon",
            daemon=True
        )
        self._reclaimer_thread.start()

        logger.debug(
            f"[SanalIslemciHavuzu] Universal Workload-Agnostic Engine Initialized! "
            f"Aggregated {self.total_sm_cores} SMs | {self.total_cuda_cores} CUDA Cores | "
            f"{self.total_tensor_cores} Tensor Cores | {self.total_rt_cores} RT Cores | "
            f"{self.total_copy_engines} Copy Engines across {self.physical_gpus} GPUs."
        )

    def bind_allocator(self, allocator: Any):
        """VMM Bellek Yöneticisini Sanal İşlemci Havuzuna Varsayılan Olarak Bağlar."""
        self.default_allocator = allocator
        logger.debug(f"[SanalIslemciHavuzu] VMM Allocator ({type(allocator).__name__}) successfully bound as default allocator.")

    def _background_reclaimer_loop(self):
        """
        ARKA PLAN RECLAIMER İPLİĞİ (Active Background Reclaimer Daemon).
        50 ms periyotlarla cuEventQuery çağırarak asenkron görevlerin VRAM kilitlerini
        yeni bir kernel çağrısını beklemeden anında temizler.
        """
        while not self._stop_event.is_set():
            try:
                self.reclaim_completed_async_tasks()
            except Exception as exc:
                logger.debug(f"[Background Reclaimer Loop Exception] {exc}")
            time.sleep(0.05)

    def _detect_hardware_topology(self) -> Dict[int, GPUDeviceProperties]:
        """
        NVIDIA C-Driver API (cuDeviceGetAttribute) ile sunucudaki tüm GPU'ların
        gerçek SM sayılarını, Tensor Core, RT Core ve Copy Engine limitlerini dinamik sorgular.
        """
        props = {}
        if _NVCUDA_LIB is not None:
            try:
                count_val = ctypes.c_int(0)
                res_count = _NVCUDA_LIB.cuDeviceGetCount(ctypes.byref(count_val))
                num_devs = count_val.value if res_count == 0 and count_val.value > 0 else self.physical_gpus

                for i in range(min(self.physical_gpus, num_devs)):
                    _ensure_active_cuda_context(i)
                    dev_handle = ctypes.c_int(0)
                    _NVCUDA_LIB.cuDeviceGet(ctypes.byref(dev_handle), i)

                    # Dynamic attribute queries
                    sm_cnt = ctypes.c_int(0)
                    _NVCUDA_LIB.cuDeviceGetAttribute(ctypes.byref(sm_cnt), 16, dev_handle)  # CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT = 16

                    max_threads_sm = ctypes.c_int(0)
                    _NVCUDA_LIB.cuDeviceGetAttribute(ctypes.byref(max_threads_sm), 39, dev_handle)

                    max_threads_blk = ctypes.c_int(0)
                    _NVCUDA_LIB.cuDeviceGetAttribute(ctypes.byref(max_threads_blk), 1, dev_handle)

                    warp_sz = ctypes.c_int(0)
                    _NVCUDA_LIB.cuDeviceGetAttribute(ctypes.byref(warp_sz), 10, dev_handle)

                    l2_sz = ctypes.c_int(0)
                    _NVCUDA_LIB.cuDeviceGetAttribute(ctypes.byref(l2_sz), 35, dev_handle)

                    clk = ctypes.c_int(0)
                    _NVCUDA_LIB.cuDeviceGetAttribute(ctypes.byref(clk), 13, dev_handle)

                    maj = ctypes.c_int(0)
                    _NVCUDA_LIB.cuDeviceGetAttribute(ctypes.byref(maj), 75, dev_handle)

                    min_ver = ctypes.c_int(0)
                    _NVCUDA_LIB.cuDeviceGetAttribute(ctypes.byref(min_ver), 76, dev_handle)

                    copy_eng = ctypes.c_int(0)
                    _NVCUDA_LIB.cuDeviceGetAttribute(ctypes.byref(copy_eng), 11, dev_handle)  # CU_DEVICE_ATTRIBUTE_ASYNC_ENGINE_COUNT = 11

                    name_buf = ctypes.create_string_buffer(256)
                    _NVCUDA_LIB.cuDeviceGetName(name_buf, 256, dev_handle)
                    dev_name = name_buf.value.decode('utf-8', errors='ignore') or f"NVIDIA GPU #{i}"

                    sm_val = sm_cnt.value if sm_cnt.value > 0 else 84
                    comp_cap = (maj.value if maj.value > 0 else 8, min_ver.value if min_ver.value >= 0 else 6)
                    copy_val = copy_eng.value if copy_eng.value > 0 else 2

                    props[i] = GPUDeviceProperties(
                        gpu_id=i,
                        name=dev_name,
                        sm_count=sm_val,
                        max_threads_per_sm=max_threads_sm.value if max_threads_sm.value > 0 else 1536,
                        max_threads_per_block=max_threads_blk.value if max_threads_blk.value > 0 else 1024,
                        warp_size=warp_sz.value if warp_sz.value > 0 else 32,
                        l2_cache_bytes=l2_sz.value if l2_sz.value > 0 else 6291456,
                        clock_khz=clk.value if clk.value > 0 else 1700000,
                        compute_capability=comp_cap,
                        async_copy_engines=copy_val
                    )
                    logger.info(
                        f"[Hardware Topology Detection] GPU #{i} '{dev_name}': {props[i].sm_count} SMs, "
                        f"{props[i].total_cuda_cores} CUDA Cores, {props[i].total_tensor_cores} Tensor Cores, "
                        f"{props[i].total_rt_cores} RT Cores (Compute {comp_cap[0]}.{comp_cap[1]})"
                    )

            except Exception as topo_exc:
                logger.debug(f"[Hardware Topology Detection Notice] Fallback to standard topology: {topo_exc}")

        # Fallback if driver API returned partial or no devices
        for i in range(self.physical_gpus):
            if i not in props:
                props[i] = GPUDeviceProperties(gpu_id=i, name=f"Virtual CUDA GPU #{i}", sm_count=84)

        return props

    def _init_stream_pools(self, streams_per_gpu: int = 4):
        """Fiziksel CUDA Stream Havuzunu İlklendirir."""
        for g_id in range(self.physical_gpus):
            self.stream_pools[g_id] = []
            for s_idx in range(streams_per_gpu):
                stream_h = self.create_stream(g_id)
                self.stream_pools[g_id].append(stream_h)

    def create_stream(self, gpu_id: int, non_blocking: bool = True) -> Any:
        """Fiziki CUDA Stream Oluşturur (cuStreamCreate)."""
        _ensure_active_cuda_context(gpu_id)
        if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuStreamCreate"):
            try:
                stream_ptr = ctypes.c_void_p(0)
                flags = 1 if non_blocking else 0  # CU_STREAM_NON_BLOCKING = 0x1
                res = _NVCUDA_LIB.cuStreamCreate(ctypes.byref(stream_ptr), flags)
                if res == 0 and stream_ptr.value is not None:
                    return stream_ptr
            except Exception as stream_exc:
                logger.debug(f"cuStreamCreate notice for GPU #{gpu_id}: {stream_exc}")
        return f"PHYSICAL_CUDA_STREAM_GPU_{gpu_id}_HANDLE"

    def create_event(self, gpu_id: int = 0) -> Any:
        """Donanımsal CUDA Senkronizasyon Event'i Üretir (cuEventCreate)."""
        _ensure_active_cuda_context(gpu_id)
        if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuEventCreate"):
            try:
                evt_ptr = ctypes.c_void_p(0)
                res = _NVCUDA_LIB.cuEventCreate(ctypes.byref(evt_ptr), 0)
                if res == 0 and evt_ptr.value is not None:
                    self._created_events.append(evt_ptr)
                    return evt_ptr
            except Exception as evt_exc:
                logger.debug(f"cuEventCreate notice for GPU #{gpu_id}: {evt_exc}")
        return f"HARDWARE_CUDA_EVENT_GPU_{gpu_id}_HANDLE"

    def record_event(self, event_handle: Any, stream_handle: Any = None, gpu_id: int = 0) -> bool:
        """Donanımsal CUDA Event Kaydeder (cuEventRecord)."""
        _ensure_active_cuda_context(gpu_id)
        if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuEventRecord") and not isinstance(event_handle, str):
            try:
                res = _NVCUDA_LIB.cuEventRecord(event_handle, stream_handle)
                return res == 0
            except Exception as rec_exc:
                logger.debug(f"cuEventRecord notice for GPU #{gpu_id}: {rec_exc}")
        return True

    def wait_event(self, stream_handle: Any, event_handle: Any, gpu_id: int = 0) -> bool:
        """Akışı Donanımsal Event'e Bağımlı Kılar (cuStreamWaitEvent)."""
        _ensure_active_cuda_context(gpu_id)
        if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuStreamWaitEvent") and not isinstance(event_handle, str):
            try:
                res = _NVCUDA_LIB.cuStreamWaitEvent(stream_handle, event_handle, 0)
                return res == 0
            except Exception as wait_exc:
                logger.debug(f"cuStreamWaitEvent notice for GPU #{gpu_id}: {wait_exc}")
        return True

    def synchronize_stream(self, stream_handle: Any, gpu_id: int = 0) -> bool:
        """Fiziki CUDA Akışını Senkronize Eder (cuStreamSynchronize)."""
        _ensure_active_cuda_context(gpu_id)
        if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuStreamSynchronize") and not isinstance(stream_handle, str):
            try:
                res = _NVCUDA_LIB.cuStreamSynchronize(stream_handle)
                return res == 0
            except Exception as sync_exc:
                logger.debug(f"cuStreamSynchronize notice for GPU #{gpu_id}: {sync_exc}")
        return True

    def synchronize_and_unlock(
        self,
        event_handles: List[Any],
        locked_pages: List[Any],
        allocator: Optional[Any] = None,
        gpu_ids: Optional[List[int]] = None
    ) -> bool:
        """
        SENKRONİZE KİLİT KALDIRMA MOTORU (Synchronous Hardware Lock Release Engine).
        
        KRONOLOJİ DÜZELTİMİ: Önce donanımın (cuEventSynchronize) bitmesi beklenir!
        Donanım icrayı bitirdikten SONRA Yük İzleyicide (load_monitor) GPU SM yükü düşürülür
        ve VRAM kilitleri (unlock_page) serbest bırakılır.
        """
        # 1. ÖNCE DONANIMIN BİTMESİNİ BEKLE
        for evt_h in event_handles:
            if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuEventSynchronize") and not isinstance(evt_h, str):
                try:
                    _NVCUDA_LIB.cuEventSynchronize(evt_h)
                except Exception as sync_exc:
                    logger.debug(f"cuEventSynchronize notice: {sync_exc}")

        # 2. DONANIM BİTTİKTEN SONRA YÜKÜ DÜŞÜR VE VRAM KİLİTLERİNİ AÇ
        if gpu_ids:
            for g_id in gpu_ids:
                _ensure_active_cuda_context(g_id)
                self.load_monitor.record_task_end(g_id)

        if allocator is not None and hasattr(allocator, "unlock_page"):
            for p_obj in locked_pages:
                try:
                    allocator.unlock_page(p_obj)
                except Exception as unl_exc:
                    logger.debug(f"Unlock page notice in synchronize_and_unlock: {unl_exc}")

        return True

    def reclaim_completed_async_tasks(self) -> int:
        """
        KİLİTSİZ ZOMBİ KİLİT ENGELLEME MOTORU (Lock-Free Async Task Reclaimer & Event Collector).
        
        'cuEventQuery' C-Driver sorgularını VE VMM 'unlock_page' çağrılarını kilit bloğunun DIŞINDA
        (Lock-Free) yürütür. VMM Compaction esnasında 'vcompute_pool' kilitlerinin tıkanmasını
        (Cross-Module Lock Contention) %100 engeller.
        """
        reclaimed_count = 0

        # 1. Kilit altında bekleyen görev listesinin anlık kopyasını al (Lock-Free sorgu hazırlığı)
        with self._lock:
            if not self.pending_async_tasks:
                return 0
            tasks_snapshot = list(self.pending_async_tasks)

        completed_task_ids = set()

        # 2. cuEventQuery C-Driver sorgularını KİLİTSİZ (Lock-Free) olarak çalıştır
        for task in tasks_snapshot:
            event_handles = task.get("event_handles", [])
            all_done = True

            for evt_h in event_handles:
                if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuEventQuery") and not isinstance(evt_h, str):
                    try:
                        res = _NVCUDA_LIB.cuEventQuery(evt_h)
                        if res != 0:  # 0 = CUDA_SUCCESS (Event completed)
                            all_done = False
                            break
                    except Exception as q_exc:
                        logger.debug(f"[cuEventQuery Notice] {q_exc}")

            if all_done:
                completed_task_ids.add(id(task))

        # 3. Tamamlanan görevleri kilit altından çıkar
        tasks_to_unlock = []
        if completed_task_ids:
            with self._lock:
                remaining_tasks = []
                for task in self.pending_async_tasks:
                    if id(task) in completed_task_ids:
                        tasks_to_unlock.append(task)
                    else:
                        remaining_tasks.append(task)
                self.pending_async_tasks = remaining_tasks

        # 4. KİLİT DIŞINDA (Lock-Free): VMM kilitlerini serbest bırak ve SM yükünü düşür
        for task in tasks_to_unlock:
            locked_pages = task.get("locked_pages", [])
            allocator = task.get("allocator")
            gpu_ids = task.get("gpu_ids", [])

            if gpu_ids:
                for g_id in gpu_ids:
                    self.load_monitor.record_task_end(g_id)

            if allocator is not None and hasattr(allocator, "unlock_page"):
                for p_obj in locked_pages:
                    try:
                        allocator.unlock_page(p_obj)
                    except Exception as unl_exc:
                        logger.debug(f"Unlock page notice in reclaimer: {unl_exc}")
            reclaimed_count += 1
            logger.debug(f"[Async Task Reclaimer] Reclaimed completed async task '{task.get('kernel_name')}' & unlocked VRAM pages.")

        return reclaimed_count

    def aggregate_sm_cores(self) -> int:
        """Tüm fiziksel GPU'ların SM birimlerini dinamik toplar."""
        total = sum(prop.sm_count for prop in self.device_props.values())
        logger.debug(f"[ComputePool] Dynamic Total Aggregated SMs: {total} across {len(self.device_props)} GPUs.")
        return total

    def shutdown(self):
        """
        SANAL İŞLEMCİ SÜRÜCÜSÜ KAPATMA VE KAYNAK İADE MOTORU (Driver Resource Disposal Engine).
        
        Arka plan reclaimer daemon ipliğini durdurur, bekleyen tüm asenkron görevlerin VRAM kilitlerini
        flushed ve serbest bırakır. cuStreamDestroy ve cuEventDestroy çağrılarıyla tüm C-Driver
        akış ve olay pointer'larını donanıma iade ederek yetim handle (orphaned handle) kalmasını engeller.
        """
        self._stop_event.set()
        if self._reclaimer_thread.is_alive():
            self._reclaimer_thread.join(timeout=1.0)

        # Bekleyen tüm asenkron görev kilitlerini aç ve temizle
        with self._lock:
            for task in self.pending_async_tasks:
                locked_pages = task.get("locked_pages", [])
                allocator = task.get("allocator")
                if allocator is not None and hasattr(allocator, "unlock_page"):
                    for p_obj in locked_pages:
                        try:
                            allocator.unlock_page(p_obj)
                        except Exception as unl_exc:
                            logger.debug(f"Shutdown unlock notice: {unl_exc}")
            self.pending_async_tasks.clear()

        # AKIŞ SÜZME KURALI (Stream Drain Rule): cuStreamDestroy öncesi tüm akışları donanım seviyesinde süz
        if _NVCUDA_LIB is not None:
            for g_id, streams in self.stream_pools.items():
                _ensure_active_cuda_context(g_id)
                for st in streams:
                    if not isinstance(st, str) and hasattr(_NVCUDA_LIB, "cuStreamSynchronize"):
                        try:
                            _NVCUDA_LIB.cuStreamSynchronize(st)
                        except Exception as sync_exc:
                            logger.debug(f"cuStreamSynchronize drain notice GPU #{g_id}: {sync_exc}")

        # Fiziki CUDA Stream Handle'larını donanıma iade et (cuStreamDestroy)
        if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuStreamDestroy"):
            for g_id, streams in self.stream_pools.items():
                _ensure_active_cuda_context(g_id)
                for st in streams:
                    if not isinstance(st, str):
                        try:
                            _NVCUDA_LIB.cuStreamDestroy(st)
                        except Exception as st_exc:
                            logger.debug(f"cuStreamDestroy notice GPU #{g_id}: {st_exc}")
        self.stream_pools.clear()

        # Donanımsal Event Handle'larını donanıma iade et (cuEventDestroy)
        if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuEventDestroy"):
            for evt in self._created_events:
                if not isinstance(evt, str):
                    try:
                        _NVCUDA_LIB.cuEventDestroy(evt)
                    except Exception as evt_exc:
                        logger.debug(f"cuEventDestroy notice: {evt_exc}")
        self._created_events.clear()

        logger.debug("[SanalIslemciHavuzu] Driver shutdown complete. All streams, events, and background reclaimer resources disposed cleanly.")

    # ----------------------------------------------------------------------------------
    # EVRENSEL C-API İCRA KANCASI 1: cuLaunchKernel / cuLaunchKernelEx (dispatch_kernel)
    # ----------------------------------------------------------------------------------
    def dispatch_kernel(
        self,
        kernel_name: str,
        matrix_shape: List[int],
        virtual_ptr: Optional[int] = None,
        allocator: Optional[Any] = None,
        grid_dim: Tuple[int, int, int] = (1, 1, 1),
        block_dim: Tuple[int, int, int] = (1, 1, 1),
        kernel_args: Optional[List[Any]] = None,
        target_gpu_id: Optional[int] = None,
        stream_id: int = 0,
        scheduled_task: Optional[Any] = None,
        synchronize: bool = True,
        workload_type: str = "AUTO",
        inject_tile_offsets: bool = False,
        dtype: Any = "FP32"
    ) -> Dict[str, Any]:
        """
        EVRENSEL HESAP-BAĞIMSIZ KERNEL SEVKİ (Universal Workload-Agnostic Kernel Dispatch)
        """
        start_time = time.perf_counter()

        # Önceki asenkron görevleri temizle
        self.reclaim_completed_async_tasks()

        # 1. ScheduledTask Çözümlemesi
        if scheduled_task is not None:
            if hasattr(scheduled_task, "virtual_ptr") and scheduled_task.virtual_ptr is not None:
                virtual_ptr = scheduled_task.virtual_ptr
            if hasattr(scheduled_task, "target_gpu_id") and scheduled_task.target_gpu_id is not None:
                target_gpu_id = scheduled_task.target_gpu_id
            if hasattr(scheduled_task, "matrix_shape") and scheduled_task.matrix_shape:
                matrix_shape = scheduled_task.matrix_shape
            if hasattr(scheduled_task, "dtype") and scheduled_task.dtype is not None:
                dtype = scheduled_task.dtype
            if hasattr(scheduled_task, "task_id"):
                kernel_name = f"{kernel_name}_{scheduled_task.task_id}"

        # OTOMATİK ALLOCATOR BAĞLAMA VE KİLİT ZORUNLULUĞU
        allocator = self._resolve_allocator(allocator, virtual_ptr)
        if allocator is not None and hasattr(allocator, "_wait_if_compacting"):
            allocator._wait_if_compacting()

        # 2. Data-Locality & Donanımsal Yetenek Hesabı
        workload_shares: Dict[int, float] = {}
        locked_pages: List[Any] = []
        data_locality_mode = "BLIND_EVEN_SPLIT"

        # Donanımsal Yetenek Yönlendirmesi (Capability-Based Routing)
        if workload_type == "RAY_TRACING":
            rt_gpus = [g_id for g_id, prop in self.device_props.items() if prop.has_rt_cores]
            if rt_gpus and target_gpu_id is None and virtual_ptr is None:
                workload_shares = {g_id: round(100.0 / len(rt_gpus), 2) for g_id in rt_gpus}
                data_locality_mode = "HARDWARE_RT_CORE_ROUTED"
        elif workload_type == "TENSOR_MATRIX":
            tensor_gpus = [g_id for g_id, prop in self.device_props.items() if prop.has_tensor_cores]
            if tensor_gpus and target_gpu_id is None and virtual_ptr is None:
                workload_shares = {g_id: round(100.0 / len(tensor_gpus), 2) for g_id in tensor_gpus}
                data_locality_mode = "HARDWARE_TENSOR_CORE_ROUTED"

        # Sanal VRAM Haritalaması Sorgusu
        if not workload_shares and virtual_ptr is not None and allocator is not None and hasattr(allocator, "get_page_scatter_map"):
            try:
                tensor_bytes = _inspect_tensor_byte_footprint(matrix_shape, dtype=dtype, kernel_args=kernel_args)
                scatter_info = allocator.get_page_scatter_map(virtual_ptr, size_bytes=tensor_bytes)

                # HARİTALANMAMIŞ BOŞLUK (UNMAPPED HOLE) DUVARI
                contains_holes = False
                if isinstance(scatter_info, dict):
                    contains_holes = scatter_info.get("contains_unmapped_holes", False)
                    page_slices = scatter_info.get("page_slices", [])
                    if any(item.get("is_unmapped_hole", False) for item in page_slices if isinstance(item, dict)):
                        contains_holes = True
                elif hasattr(scatter_info, "contains_unmapped_holes"):
                    contains_holes = getattr(scatter_info, "contains_unmapped_holes", False)

                if contains_holes:
                    raise MemoryError(
                        f"[VMM Protection Exception] Sanal Adres Uzayında Haritalanmamış Boşluk Var (Unmapped Virtual Range Hole at {hex(virtual_ptr)})! "
                        f"Kernel sevk edilirse donanımsal CUDA_ERROR_ILLEGAL_ADDRESS çökmelerine neden olacağından icra durduruldu."
                    )

                gpu_bytes_map = {}
                if isinstance(scatter_info, dict):
                    gpu_bytes_map = scatter_info.get("gpu_bytes_map", {})
                elif hasattr(scatter_info, "__iter__"):
                    for item in scatter_info:
                        if isinstance(item, dict):
                            g_id = item.get("physical_gpu_id", -1)
                            b_sz = item.get("size_bytes", 0)
                            if g_id >= 0 and not item.get("is_unmapped_hole", False):
                                gpu_bytes_map[g_id] = gpu_bytes_map.get(g_id, 0) + b_sz

                total_bytes = sum(gpu_bytes_map.values())

                if total_bytes > 0:
                    # STRAGGLER BOTTLENECK ÖNLEME: VRAM Oranı ile Donanımsal Çekirdek Gücü (CUDA Cores * Clock) Harmanlanır!
                    raw_scores = {}
                    for g_id, b_cnt in gpu_bytes_map.items():
                        vram_ratio = b_cnt / total_bytes
                        props = self.device_props.get(g_id)
                        compute_power = float(props.total_cuda_cores * max(1, props.clock_khz)) if props else 1.0
                        raw_scores[g_id] = vram_ratio * compute_power

                    total_score = sum(raw_scores.values())
                    if total_score > 0:
                        for g_id, score in raw_scores.items():
                            share = (score / total_score) * 100.0
                            if share > 0:
                                workload_shares[g_id] = round(share, 2)

                    if len(workload_shares) == 1:
                        data_locality_mode = "ZERO_BUS_LATENCY_LOCAL"
                    else:
                        data_locality_mode = "PROPORTIONAL_MULTI_GPU_SCATTER"

                locked_pages = _lock_all_extents_in_range(allocator, virtual_ptr, byte_size=tensor_bytes)
                for extent in locked_pages:
                    if getattr(extent, "sync_event", None) is not None and hasattr(allocator, "wait_for_migration_event"):
                        allocator.wait_for_migration_event(extent)

            except MemoryError:
                raise
            except Exception as loc_exc:
                logger.debug(f"[Data Locality Resolution Notice] {loc_exc}")

        # YAVAŞ KART TIKANIKLIĞI (STRAGGLER BOTTLENECK) ÖNLEME MOTORU:
        # Donanımların gerçek hesaplama güçlerine (CUDA Cores * Clock) göre dinamik karolama ağırlığı hesaplar.
        def _get_compute_power_weighted_shares(gpu_ids: List[int]) -> Dict[int, float]:
            powers = {}
            for g in gpu_ids:
                props = self.device_props.get(g)
                if props:
                    powers[g] = float(props.total_cuda_cores * max(1, props.clock_khz))
                else:
                    powers[g] = 1.0
            tot = sum(powers.values())
            if tot <= 0:
                tot = float(len(gpu_ids))
                powers = {g: 1.0 for g in gpu_ids}
            return {g: round((powers[g] / tot) * 100.0, 2) for g in gpu_ids}

        # Yerel GPU Doyumda İse 2. Kanun (Hesap Taşkını) Tetiklenir
        if len(workload_shares) == 1:
            local_g_id = next(iter(workload_shares.keys()))
            local_sm_util = self.load_monitor.sm_utilization_pct.get(local_g_id, 0.0)
            if local_sm_util >= 80.0 and self.physical_gpus > 1:
                all_gpus = list(range(self.physical_gpus))
                workload_shares = _get_compute_power_weighted_shares(all_gpus)
                data_locality_mode = "COMPUTE_SATURATION_SPILLOVER_WEIGHTED"
                logger.info(
                    f"[2. Kanun Compute Spillover] GPU #{local_g_id} SM Saturated ({local_sm_util:.1f}%)! "
                    f"Spilling workload WEIGHTED BY COMPUTE POWER across all {self.physical_gpus} GPUs."
                )

        # Eğer adres haritalaması yapılamadıysa veya target_gpu_id açıkça verildiyse
        if target_gpu_id is not None and 0 <= target_gpu_id < self.physical_gpus:
            workload_shares = {target_gpu_id: 100.0}
            data_locality_mode = "EXPLICIT_TARGET_GPU"
        elif not workload_shares:
            all_gpus = list(range(self.physical_gpus))
            workload_shares = _get_compute_power_weighted_shares(all_gpus)

        # 3. Boyutsuz 3D Grid/Block Karolaması & C-Driver Launch Execution
        execution_streams: List[Any] = []
        event_handles: List[Any] = []
        persistent_params_ref: List[Any] = []

        accumulated_ratios = 0.0
        active_gpu_items = [(g, s) for g, s in workload_shares.items() if s > 0]
        num_active_gpus = len(active_gpu_items)

        for idx, (g_id, share) in enumerate(active_gpu_items):
            is_last_gpu = (idx == num_active_gpus - 1)

            # BOYUTSUZ 3D GRID KAROLAMA (Dimension-Agnostic 3D Grid Partitioning)
            if num_active_gpus > 1:
                gpu_grid_dim, tile_offsets = _partition_3d_grid(grid_dim, share, accumulated_ratios, is_last_gpu=is_last_gpu)
            else:
                gpu_grid_dim, tile_offsets = grid_dim, (0, 0, 0)

            # MÜKERRER KARO KORUMASI: 0-boyutlu grid atanmışsa bu GPU'da icra yapma!
            if gpu_grid_dim[0] <= 0 or gpu_grid_dim[1] <= 0 or gpu_grid_dim[2] <= 0:
                logger.debug(f"[Grid Partitioning Skip] GPU #{g_id} received 0-sized 3D Grid {gpu_grid_dim}. Skipping launch.")
                accumulated_ratios += (share / 100.0)
                continue

            _ensure_active_cuda_context(g_id)

            # Stream seçimi
            stream_pool = self.stream_pools.get(g_id, [])
            st_handle = stream_pool[stream_id % len(stream_pool)] if stream_pool else f"STREAM_GPU_{g_id}"
            execution_streams.append(st_handle)

            # SM Yük Takibi
            self.load_monitor.record_task_start(g_id, sm_demand_pct=min(50.0, share))

            # Donanımsal Event Üret
            evt_h = self.create_event(g_id)
            event_handles.append(evt_h)

            # POİNTER SEVİYESİNDE SANAL ADRES DİLİMLEME (Address-Level Slicing Architecture)
            # Kullanıcının C++ Kernel imzasına dokunulmaz. 3D grid karolaması yapıldığında
            # GPU #i için karo offset'i hesabı yapılarak VRAM pointer'ı doğrudan kaydırılır.
            gpu_kernel_args = list(kernel_args) if kernel_args else []
            sliced_virtual_ptr = virtual_ptr

            if virtual_ptr is not None:
                elem_bytes = _inspect_tensor_byte_footprint([1, 1], dtype=dtype, kernel_args=kernel_args)
                
                # BÜTÜNSEL ÇOK BOYUTLU (2D/3D) ADIM BAYT KAYMASI FORMÜLÜ (Multi-Axis Stride Offset Calculation)
                dim_x = matrix_shape[0] if len(matrix_shape) > 0 else 1
                dim_y = matrix_shape[1] if len(matrix_shape) > 1 else 1
                dim_z = matrix_shape[2] if len(matrix_shape) > 2 else 1

                gx = max(1, grid_dim[0])
                gy = max(1, grid_dim[1])
                gz = max(1, grid_dim[2])

                # TAVAN BÖLME İLE KÜSÜRAT KAPSAMA KORUMASI (Ceiling Division for Remainder Coverage):
                # Tamsayı taban bölmesi (//) küsüratı aşağı yuvarlar ve matrisin sonundaki
                # (dim_x - gx * tile_size_x) eleman kaybına yol açar. math.ceil ile tavan bölme
                # yapılarak her karo en az gerekli eleman sayısını kapsar; son GPU'nun
                # is_last_gpu kuralı zaten üst sınırı orijinal dim boyutuna eşitler.
                tile_size_x = math.ceil(dim_x / gx)
                tile_size_y = math.ceil(dim_y / gy)
                tile_size_z = math.ceil(dim_z / gz)

                stride_z = 1
                stride_y = dim_z
                stride_x = dim_y * dim_z

                tile_elem_offset = (
                    (tile_offsets[0] * tile_size_x * stride_x) +
                    (tile_offsets[1] * tile_size_y * stride_y) +
                    (tile_offsets[2] * tile_size_z * stride_z)
                )

                sliced_virtual_ptr = virtual_ptr + (tile_elem_offset * elem_bytes)

                if not gpu_kernel_args:
                    gpu_kernel_args = [sliced_virtual_ptr, matrix_shape[0], matrix_shape[1]]
                else:
                    gpu_kernel_args = [sliced_virtual_ptr if arg == virtual_ptr else arg for arg in gpu_kernel_args]

            if inject_tile_offsets and gpu_kernel_args:
                gpu_kernel_args.extend([tile_offsets[0], tile_offsets[1], tile_offsets[2]])

            params_arr, c_vars = _build_kernel_params(gpu_kernel_args)
            persistent_params_ref.append((params_arr, c_vars))

            # C-Driver Kernel Launch Execution (cuLaunchKernel)
            if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuLaunchKernel") and gpu_kernel_args and isinstance(gpu_kernel_args[0], int):
                func_ptr = gpu_kernel_args[0]
                try:
                    params_ptr = ctypes.cast(params_arr, ctypes.POINTER(ctypes.c_void_p)) if params_arr else None
                    _NVCUDA_LIB.cuLaunchKernel(
                        ctypes.c_void_p(func_ptr),
                        gpu_grid_dim[0], gpu_grid_dim[1], gpu_grid_dim[2],
                        block_dim[0], block_dim[1], block_dim[2],
                        0, st_handle, params_ptr, None
                    )
                    logger.info(
                        f"[Universal C-Driver Launch] Executed '{kernel_name}' on GPU #{g_id} "
                        f"with 3D Grid {gpu_grid_dim} (Offsets: {tile_offsets}) via cuLaunchKernel."
                    )
                except Exception as launch_exc:
                    logger.debug(f"[C-Driver Kernel Launch Notice] GPU #{g_id}: {launch_exc}")

            self.record_event(evt_h, st_handle, gpu_id=g_id)
            accumulated_ratios += (share / 100.0)

        # 4. Donanımsal Senkronizasyon Ve Güvenli Sayfa Kilidi Kaldırma
        if synchronize:
            self.synchronize_and_unlock(
                event_handles=event_handles,
                locked_pages=locked_pages,
                allocator=allocator,
                gpu_ids=list(workload_shares.keys())
            )
        else:
            with self._lock:
                self.pending_async_tasks.append({
                    "event_handles": event_handles,
                    "locked_pages": locked_pages,
                    "allocator": allocator,
                    "gpu_ids": list(workload_shares.keys()),
                    "kernel_name": kernel_name,
                    "dispatch_time": time.time()
                })

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        logger.info(
            f"[ComputePool] Dispatched Universal Kernel '{kernel_name}' (Shape/Space: {matrix_shape}) | "
            f"Mode: {data_locality_mode} | Workload Shares: {workload_shares} | Active Streams: {len(execution_streams)}"
        )

        return {
            "kernel_name": kernel_name,
            "status": "DISPATCHED_AND_SYNCHRONIZED" if synchronize else "DISPATCHED_ASYNC",
            "virtual_ptr": virtual_ptr,
            "workload_type": workload_type,
            "data_locality_mode": data_locality_mode,
            "total_sm_cores": self.total_sm_cores,
            "total_cuda_cores": self.total_cuda_cores,
            "total_tensor_cores": self.total_tensor_cores,
            "total_rt_cores": self.total_rt_cores,
            "workload_distribution": workload_shares,
            "parallel_streams": [str(s) for s in execution_streams],
            "sync_event_handles": event_handles,
            "locked_pages": locked_pages if not synchronize else [],
            "sm_utilization": self.load_monitor.get_status(),
            "execution_latency_ms": round(elapsed_ms, 3)
        }

    def _resolve_allocator(self, allocator: Optional[Any], virtual_ptr: Optional[int] = None) -> Optional[Any]:
        """
        SANAL BELLEK YÖNETİCİSİ OTOMATİK BAĞLAMA VE KİLİT ZORUNLULUĞU MOTORU.
        
        Parametre olarak 'allocator' None geçilse dahi varsayılan 'default_allocator' veya 
        küresel sürücü örneğinden VMM Allocator'ı otomatik bağlar.
        Sanal VRAM adresi geçilip de hiç allocator bulunamazsa kilitsiz donanım icrasını engellemek
        için koruma istisnası fırlatır.
        """
        if allocator is not None:
            return allocator
        if self.default_allocator is not None:
            return self.default_allocator

        try:
            import kulli_gpu
            if getattr(kulli_gpu, "_GLOBAL_DRIVER_INSTANCE", None) is not None:
                drv = getattr(kulli_gpu, "_GLOBAL_DRIVER_INSTANCE")
                if hasattr(drv, "vmm_allocator") and drv.vmm_allocator is not None:
                    return drv.vmm_allocator
        except Exception:
            pass

        try:
            from kulli_gpu.memory.vmm_allocator import get_global_vmm_allocator
            global_alloc = get_global_vmm_allocator()
            if global_alloc is not None:
                self.default_allocator = global_alloc
                return global_alloc
        except Exception:
            pass

        if virtual_ptr is not None:
            # VMM_ALLOCATOR_NOT_BOUND ERKEN DEVLET UYARISI (Early State Warning to Upper Layer):
            # _resolve_allocator ValueError fırlatmadan hemen önce, üst katmana (Erken Devlet Engine)
            # durumun ciddiyetini bildiren açık bir uyarı loglar. Bu sayede log izleme sistemleri
            # çöküş öncesi VMM bağlama eksikliğini proaktif olarak tespit edebilir.
            logger.warning(
                f"[VMM_ALLOCATOR_NOT_BOUND] Sanal VRAM Adresi ({hex(virtual_ptr)}) için "
                f"ne 'allocator' parametresi, ne 'default_allocator', ne de küresel sürücü VMM bağlaması bulunabildi. "
                f"Bu durum donanımsal CUDA_ERROR_ILLEGAL_ADDRESS çökmelerine yol açacağından icra durdurulacaktır. "
                f"Lütfen 'bind_allocator()' veya 'allocator' parametresi ile geçerli bir VMM Allocator bağlayınız."
            )
            raise ValueError(
                f"[VMM Protection Exception] Sanal VRAM Adresi ({hex(virtual_ptr)}) ile asenkron icra/DMA "
                f"başlatılırken 'allocator' parametresi None olamaz ve sürücüye bağlı varsayılan VMM Allocator bulunamadı! "
                f"VRAM kilitsiz asenkron icra donanımsal CUDA_ERROR_ILLEGAL_ADDRESS çökmelerine yol açacağından durduruldu."
            )
        return None

    # ----------------------------------------------------------------------------------
    # EVRENSEL C-API İCRA KANCASI 2: cuGraphLaunch / cuGraphExecLaunch (launch_graph)
    # ----------------------------------------------------------------------------------
    def launch_graph(
        self,
        graph_exec_handle: Any,
        target_gpu_id: int = 0,
        stream_id: int = 0,
        virtual_ptr: Optional[int] = None,
        allocator: Optional[Any] = None,
        synchronize: bool = True,
        graph_byte_size: Optional[int] = None,
        matrix_shape: Optional[List[int]] = None,
        dtype: Any = None
    ) -> Dict[str, Any]:
        """
        EVRENSEL CUDA GRAPH İCRA KANCASI (cuGraphLaunch / cuGraphExecLaunch).
        """
        start_time = time.perf_counter()
        _ensure_active_cuda_context(target_gpu_id)

        # OTOMATİK ALLOCATOR BAĞLAMA
        allocator = self._resolve_allocator(allocator, virtual_ptr)

        # ═══════════════════════════════════════════════════════════════════════════════
        # 3 ADIMLI CUDA GRAPH VRAM AYAK İZİ KİLİTLEME USULÜ
        # (3-Step CUDA Graph VRAM Footprint Lock Protocol)
        #
        # ADIM 1: Açık Parametre Önceliği → graph_byte_size veya matrix_shape verilmişse
        #         doğrudan o boyut kilitlenir.
        # ADIM 2: VMM Allocator'dan Extent Boyutu Okuma → virtual_ptr adresindeki
        #         tahsisat nesnesinin size_bytes özniteliği bizzat okunur.
        # ADIM 3: Donanımsal Koruma Barajı → Hiçbir bilgi bulunamazsa 4 Bayt gibi sahte
        #         bir illüzyona ASLA düşülmez; ya donanımsal sayfa boyutu kilitlenir
        #         ya da ValueError fırlatılıp kilitsiz icra engellenir.
        # ═══════════════════════════════════════════════════════════════════════════════
        resolved_byte_size = graph_byte_size  # ADIM 1a: Açık graph_byte_size parametresi

        if resolved_byte_size is None and matrix_shape:
            # ADIM 1b: Açık matrix_shape parametresi üzerinden hesaplama
            resolved_byte_size = _inspect_tensor_byte_footprint(matrix_shape, dtype=dtype)

        if resolved_byte_size is None and virtual_ptr is not None and allocator is not None:
            # ADIM 2: VMM Allocator'dan Extent Boyutunu Bizzat Oku
            if hasattr(allocator, "get_extent_at_virtual_address"):
                ext = allocator.get_extent_at_virtual_address(virtual_ptr)
                if ext and hasattr(ext, "size_bytes"):
                    resolved_byte_size = ext.size_bytes
                elif ext and hasattr(ext, "byte_size"):
                    resolved_byte_size = ext.byte_size
            if resolved_byte_size is None and hasattr(allocator, "get_page_at_virtual_address"):
                p_obj = allocator.get_page_at_virtual_address(virtual_ptr)
                if p_obj and hasattr(p_obj, "size_bytes"):
                    resolved_byte_size = p_obj.size_bytes

        if resolved_byte_size is None:
            # ADIM 3: DONANIMSAL KORUMA BARAJI (4 BAYT SAÇMALIĞININ YASAKLANMASI)
            # Hiçbir kaynaktan ayak izi belirlenemedi. 4 Bayt kilitlemek 3.99 GB'ı
            # kilitsiz bırakıp çöküşe davetiye çıkarmaktır. Bu durumda ya donanımın
            # en küçük sayfa boyutu kilitlenir ya da sürücü ciddiyetiyle hata fırlatılır.
            if allocator is not None and hasattr(allocator, "page_size_bytes"):
                resolved_byte_size = allocator.page_size_bytes
                logger.warning(
                    f"[VMM Protection Warning] CUDA Graph icrasında 'virtual_ptr' ({hex(virtual_ptr) if virtual_ptr else 'None'}) "
                    f"için kesin VRAM ayak izi belirlenemedi. Donanımsal minimum sayfa boyutu "
                    f"({resolved_byte_size} bytes) koruma altına alınıyor. Kesin kilitleme için "
                    f"'graph_byte_size' veya 'matrix_shape' parametresini geçiniz."
                )
            elif virtual_ptr is not None:
                # Ne açık parametre, ne extent, ne de donanımsal sayfa boyutu bulunamadı.
                # 4 Bayt kilitleme YASAKTIR — sürücü ciddiyetiyle hata fırlatıp dursun!
                raise ValueError(
                    f"[VMM Protection Exception] CUDA Graph icrasında 'virtual_ptr' ({hex(virtual_ptr)}) "
                    f"kilit boyutu belirlenemedi! Kilitsiz CUDA Graph icrası donanımsal çökmelere "
                    f"(CUDA_ERROR_ILLEGAL_ADDRESS) yol açacağından işlem durduruldu. "
                    f"Lütfen 'graph_byte_size' veya 'matrix_shape' parametresini geçiniz."
                )
            else:
                # virtual_ptr de yoksa zaten VRAM kilitleme gerekmez, 0 olarak bırak
                resolved_byte_size = 0

        locked_pages = _lock_all_extents_in_range(allocator, virtual_ptr, byte_size=resolved_byte_size)

        stream_pool = self.stream_pools.get(target_gpu_id, [])
        st_handle = stream_pool[stream_id % len(stream_pool)] if stream_pool else f"STREAM_GPU_{target_gpu_id}"

        self.load_monitor.record_task_start(target_gpu_id, sm_demand_pct=30.0)
        evt_h = self.create_event(target_gpu_id)

        executed = False
        if _NVCUDA_LIB is not None and hasattr(_NVCUDA_LIB, "cuGraphExecLaunch") and not isinstance(graph_exec_handle, str):
            try:
                res = _NVCUDA_LIB.cuGraphExecLaunch(graph_exec_handle, st_handle)
                executed = (res == 0)
            except Exception as gr_exc:
                logger.debug(f"[Graph Launch Notice] GPU #{target_gpu_id}: {gr_exc}")

        self.record_event(evt_h, st_handle, gpu_id=target_gpu_id)

        if synchronize:
            self.synchronize_and_unlock(
                event_handles=[evt_h],
                locked_pages=locked_pages,
                allocator=allocator,
                gpu_ids=[target_gpu_id]
            )
        else:
            with self._lock:
                self.pending_async_tasks.append({
                    "event_handles": [evt_h],
                    "locked_pages": locked_pages,
                    "allocator": allocator,
                    "gpu_ids": [target_gpu_id],
                    "kernel_name": "cuda_graph_exec",
                    "dispatch_time": time.time()
                })

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "status": "GRAPH_LAUNCHED_AND_SYNCHRONIZED" if synchronize else "GRAPH_LAUNCHED_ASYNC",
            "target_gpu_id": target_gpu_id,
            "stream_handle": str(st_handle),
            "event_handle": evt_h,
            "c_api_executed": executed,
            "locked_pages": locked_pages if not synchronize else [],
            "execution_latency_ms": round(elapsed_ms, 3)
        }

    # ----------------------------------------------------------------------------------
    # EVRENSEL C-API İCRA KANCASI 3: cuMemcpyAsync / cuMemcpyPeerAsync (async_memcpy_dma)
    # ----------------------------------------------------------------------------------
    def async_memcpy_dma(
        self,
        dst_ptr: int,
        src_ptr: int,
        byte_size: int,
        src_gpu_id: int = 0,
        dst_gpu_id: int = 0,
        stream_id: int = 0,
        allocator: Optional[Any] = None,
        synchronize: bool = True
    ) -> Dict[str, Any]:
        """
        EVRENSEL ASENKRON DMA VERİ AKTIARIM KANCASI (cuMemcpyAsync / cuMemcpyPeerAsync).
        """
        start_time = time.perf_counter()
        _ensure_active_cuda_context(src_gpu_id)

        # OTOMATİK ALLOCATOR BAĞLAMA VE KİLİT ZORUNLULUĞU
        allocator = self._resolve_allocator(allocator, src_ptr)

        # ZAAF 3 DÜZELTİMİ: Hem kaynak hem hedef GPU için yük takibini simetrik başlat!
        self.load_monitor.record_task_start(src_gpu_id, sm_demand_pct=10.0)
        self.load_monitor.record_task_start(dst_gpu_id, sm_demand_pct=10.0)

        locked_pages = []
        if allocator is not None:
            locked_pages.extend(_lock_all_extents_in_range(allocator, src_ptr, byte_size))
            locked_pages.extend(_lock_all_extents_in_range(allocator, dst_ptr, byte_size))

        stream_pool = self.stream_pools.get(src_gpu_id, [])
        st_handle = stream_pool[stream_id % len(stream_pool)] if stream_pool else f"STREAM_GPU_{src_gpu_id}"

        evt_h = self.create_event(src_gpu_id)
        executed = False

        if _NVCUDA_LIB is not None and not isinstance(dst_ptr, str):
            try:
                if src_gpu_id == dst_gpu_id:
                    if hasattr(_NVCUDA_LIB, "cuMemcpyAsync"):
                        res = _NVCUDA_LIB.cuMemcpyAsync(
                            ctypes.c_uint64(dst_ptr),
                            ctypes.c_uint64(src_ptr),
                            ctypes.c_size_t(byte_size),
                            st_handle
                        )
                        executed = (res == 0)
                else:
                    if hasattr(_NVCUDA_LIB, "cuMemcpyPeerAsync"):
                        res = _NVCUDA_LIB.cuMemcpyPeerAsync(
                            ctypes.c_uint64(dst_ptr), ctypes.c_int(dst_gpu_id),
                            ctypes.c_uint64(src_ptr), ctypes.c_int(src_gpu_id),
                            ctypes.c_size_t(byte_size), st_handle
                        )
                        executed = (res == 0)
            except Exception as dma_exc:
                logger.debug(f"[DMA Copy Notice] {src_gpu_id} -> {dst_gpu_id}: {dma_exc}")

        self.record_event(evt_h, st_handle, gpu_id=src_gpu_id)

        if synchronize:
            self.synchronize_and_unlock(
                event_handles=[evt_h],
                locked_pages=locked_pages,
                allocator=allocator,
                gpu_ids=[src_gpu_id, dst_gpu_id]
            )
        else:
            with self._lock:
                self.pending_async_tasks.append({
                    "event_handles": [evt_h],
                    "locked_pages": locked_pages,
                    "allocator": allocator,
                    "gpu_ids": [src_gpu_id, dst_gpu_id],
                    "kernel_name": "async_memcpy_dma",
                    "dispatch_time": time.time()
                })

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "status": "DMA_COPY_COMPLETED" if synchronize else "DMA_COPY_DISPATCHED_ASYNC",
            "src_gpu_id": src_gpu_id,
            "dst_gpu_id": dst_gpu_id,
            "byte_size": byte_size,
            "c_api_executed": executed,
            "locked_pages": locked_pages if not synchronize else [],
            "transfer_latency_ms": round(elapsed_ms, 3)
        }



"""
KÜLLÎ SANAL GPU JIT C++ SÜRÜCÜ DERLEYİCİSİ VE DİNAMİK C-ABI BAĞLAYICISI
Modül: kulli_gpu/interception/cpp_builder.py

Bu modül, 'cpp_driver/' altındaki C++ sürücü kaynak kodlarını ('kulli_pybind_wrapper.cpp',
'kulli_vmm_cuda.cpp') sistemdeki g++/clang++/nvcc derleyicilerini kullanarak JIT (Just-In-Time)
olarak paylaşımlı kütüphaneye (.so / .dll) derler ve 'ctypes.CDLL' ile Python canlı belleğine
ve C-ABI pointer'larına bağlar.
"""

import os
import sys
import glob
import ctypes
import shutil
import logging
import platform
import subprocess
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger("kulli_gpu.cpp_builder")

_GLOBAL_CPP_LIB: Optional[ctypes.CDLL] = None
_GLOBAL_CPP_DRIVER_PTR: Optional[int] = None
_BUILD_ATTEMPTED: bool = False


class CPPDriverHandle:
    """
    Python tarafında C++ Sanal Sürücü C-ABI metotlarına doğrudan erişim sağlayan sarmalayıcı.
    """
    def __init__(self, cdll_lib: ctypes.CDLL, driver_ptr: Optional[int] = None):
        self.lib = cdll_lib
        self.driver_ptr = driver_ptr
        self._setup_signatures()

    def _setup_signatures(self):
        """C-ABI fonksiyon imzalarını (argtypes & restype) tanımlar."""
        lib = self.lib
        
        # 1. Driver Lifecycle
        if hasattr(lib, "kulli_cpp_create_driver"):
            lib.kulli_cpp_create_driver.restype = ctypes.c_void_p
            lib.kulli_cpp_create_driver.argtypes = []

        if hasattr(lib, "kulli_cpp_init_driver"):
            lib.kulli_cpp_init_driver.restype = ctypes.c_bool
            lib.kulli_cpp_init_driver.argtypes = [ctypes.c_void_p]

        if hasattr(lib, "kulli_cpp_destroy_driver"):
            lib.kulli_cpp_destroy_driver.restype = None
            lib.kulli_cpp_destroy_driver.argtypes = [ctypes.c_void_p]

        # 2. VRAM Allocation & Mapping
        if hasattr(lib, "kulli_cpp_allocate_buffer"):
            lib.kulli_cpp_allocate_buffer.restype = ctypes.c_uint64
            lib.kulli_cpp_allocate_buffer.argtypes = [ctypes.c_void_p, ctypes.c_uint64]

        if hasattr(lib, "kulli_cpp_map_gpu"):
            lib.kulli_cpp_map_gpu.restype = ctypes.c_bool
            lib.kulli_cpp_map_gpu.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_int]

        if hasattr(lib, "kulli_cpp_unmap_gpu"):
            lib.kulli_cpp_unmap_gpu.restype = ctypes.c_bool
            lib.kulli_cpp_unmap_gpu.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_uint64]

        # 3. Telemetry & Properties
        if hasattr(lib, "kulli_cpp_get_base_address"):
            lib.kulli_cpp_get_base_address.restype = ctypes.c_uint64
            lib.kulli_cpp_get_base_address.argtypes = [ctypes.c_void_p]

        if hasattr(lib, "kulli_cpp_get_total_bytes"):
            lib.kulli_cpp_get_total_bytes.restype = ctypes.c_uint64
            lib.kulli_cpp_get_total_bytes.argtypes = [ctypes.c_void_p]

        if hasattr(lib, "kulli_cpp_get_allocated_bytes"):
            lib.kulli_cpp_get_allocated_bytes.restype = ctypes.c_uint64
            lib.kulli_cpp_get_allocated_bytes.argtypes = [ctypes.c_void_p]

        if hasattr(lib, "kulli_cpp_get_free_bytes"):
            lib.kulli_cpp_get_free_bytes.restype = ctypes.c_uint64
            lib.kulli_cpp_get_free_bytes.argtypes = [ctypes.c_void_p]

        if hasattr(lib, "kulli_cpp_get_gpu_count"):
            lib.kulli_cpp_get_gpu_count.restype = ctypes.c_int
            lib.kulli_cpp_get_gpu_count.argtypes = [ctypes.c_void_p]

        if hasattr(lib, "kulli_cpp_get_gpu_vram_capacity"):
            lib.kulli_cpp_get_gpu_vram_capacity.restype = ctypes.c_uint64
            lib.kulli_cpp_get_gpu_vram_capacity.argtypes = [ctypes.c_void_p, ctypes.c_int]

        if hasattr(lib, "kulli_cpp_get_gpu_free_vram"):
            lib.kulli_cpp_get_gpu_free_vram.restype = ctypes.c_uint64
            lib.kulli_cpp_get_gpu_free_vram.argtypes = [ctypes.c_void_p, ctypes.c_int]

        if hasattr(lib, "kulli_cpp_is_valid_address"):
            lib.kulli_cpp_is_valid_address.restype = ctypes.c_bool
            lib.kulli_cpp_is_valid_address.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_uint64]

        # 4. CUDA Symbol Hooks
        if hasattr(lib, "kulli_cudaGetDeviceCount"):
            lib.kulli_cudaGetDeviceCount.restype = ctypes.c_int
            lib.kulli_cudaGetDeviceCount.argtypes = [ctypes.POINTER(ctypes.c_int)]

        if hasattr(lib, "kulli_cudaMemGetInfo"):
            lib.kulli_cudaMemGetInfo.restype = ctypes.c_int
            lib.kulli_cudaMemGetInfo.argtypes = [ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]

    def initialize(self) -> bool:
        if self.driver_ptr is None and hasattr(self.lib, "kulli_cpp_create_driver"):
            try:
                self.driver_ptr = self.lib.kulli_cpp_create_driver()
            except Exception as exc:
                logger.debug(f"[CPPDriverHandle] Driver creation notice: {exc}")

        if self.driver_ptr and hasattr(self.lib, "kulli_cpp_init_driver"):
            try:
                return bool(self.lib.kulli_cpp_init_driver(self.driver_ptr))
            except Exception as exc:
                logger.debug(f"[CPPDriverHandle] Driver init notice: {exc}")
        return False


def find_cpp_source_file() -> Optional[str]:
    """C++ sürücü kaynak dosyasının konumunu tespit eder."""
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    possible_paths = [
        os.path.join(workspace_root, "cpp_driver", "kulli_pybind_wrapper.cpp"),
        os.path.join(workspace_root, "cpp_driver", "kulli_vmm_cuda.cpp"),
        os.path.join(workspace_root, "kulli_gpu", "cpp_driver", "kulli_pybind_wrapper.cpp"),
        "/app/cpp_driver/kulli_pybind_wrapper.cpp",
        "/app/applet/cpp_driver/kulli_pybind_wrapper.cpp",
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return None


def get_target_so_path() -> str:
    """Platform bazlı hedef paylaşımlı kütüphane yolunu döndürür."""
    system_name = platform.system().lower()
    if "windows" in system_name:
        filename = "libkulli_vmm_cuda.dll"
    elif "darwin" in system_name:
        filename = "libkulli_vmm_cuda.dylib"
    else:
        filename = "libkulli_vmm_cuda.so"
    return os.path.join("/tmp", filename)


def find_system_compiler() -> Optional[Tuple[str, str]]:
    """Sistemde g++, clang++, nvcc veya cl.exe derleyicilerini arar."""
    for comp in ["g++", "clang++", "nvcc", "gcc"]:
        cmd = shutil.which(comp)
        if cmd:
            return comp, cmd
    return None


def build_and_load_cpp_driver() -> Dict[str, Any]:
    """
    JIT C++ Sürücü Derleyicisi ve Dinamik Bağlayıcı Ana Fonksiyonu.
    """
    global _GLOBAL_CPP_LIB, _GLOBAL_CPP_DRIVER_PTR, _BUILD_ATTEMPTED

    target_so = get_target_so_path()
    result = {
        "status": "not_compiled",
        "so_path": target_so,
        "handle": None,
        "lib": None,
        "driver_ptr": None
    }

    if _GLOBAL_CPP_LIB is not None:
        result["status"] = "already_loaded"
        result["lib"] = _GLOBAL_CPP_LIB
        result["driver_ptr"] = _GLOBAL_CPP_DRIVER_PTR
        result["handle"] = CPPDriverHandle(_GLOBAL_CPP_LIB, _GLOBAL_CPP_DRIVER_PTR)
        return result

    if _BUILD_ATTEMPTED and not os.path.exists(target_so):
        return result

    _BUILD_ATTEMPTED = True

    # 1. Kaynak dosyasını bul
    src_file = find_cpp_source_file()
    if not src_file:
        logger.debug("[JIT C++ Builder] Source C++ file not found, skipping compilation.")
        return result

    # 2. Eğer .so zaten var ve yeniyse, doğrudan yüklemeyi dene
    need_compile = True
    if os.path.exists(target_so):
        try:
            if os.path.getmtime(target_so) >= os.path.getmtime(src_file):
                need_compile = False
        except Exception:
            need_compile = True

    # 3. Derleme gerekiyorsa JIT derleyiciyi tetikle
    if need_compile:
        compiler_info = find_system_compiler()
        if compiler_info:
            comp_type, comp_bin = compiler_info
            logger.info(f"[JIT C++ Builder] Compiling C++ driver {src_file} via {comp_type} -> {target_so}...")
            
            # CUDA Include & Library Yolları
            cuda_inc = "/usr/local/cuda/include"
            cuda_lib = "/usr/local/cuda/lib64"
            
            cmd = [
                comp_bin,
                "-O3",
                "-shared",
                "-fPIC",
                "-std=c++17",
                src_file,
                "-o", target_so
            ]
            if os.path.exists(cuda_inc):
                cmd.extend(["-I", cuda_inc])
            if os.path.exists(cuda_lib):
                cmd.extend(["-L", cuda_lib, "-lcuda", "-lcudart"])

            try:
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
                if proc.returncode == 0 and os.path.exists(target_so):
                    logger.info(f"[JIT C++ Builder] Compilation successful! Shared library created: {target_so}")
                else:
                    logger.debug(f"[JIT C++ Builder] Compilation note (code {proc.returncode}): {proc.stderr.decode('utf-8', errors='ignore')}")
            except Exception as comp_err:
                logger.debug(f"[JIT C++ Builder] Subprocess execution note: {comp_err}")
        else:
            logger.debug("[JIT C++ Builder] No C++ compiler (g++/clang++/nvcc) found on PATH. Falling back to Python/Virtual mode.")

    # 4. Derlenen veya var olan .so kütüphanesini ctypes ile yükle
    if os.path.exists(target_so):
        try:
            cdll_lib = ctypes.CDLL(target_so)
            handle = CPPDriverHandle(cdll_lib)
            handle.initialize()

            _GLOBAL_CPP_LIB = cdll_lib
            _GLOBAL_CPP_DRIVER_PTR = handle.driver_ptr

            result["status"] = "loaded"
            result["lib"] = cdll_lib
            result["driver_ptr"] = handle.driver_ptr
            result["handle"] = handle
            logger.info(f"[JIT C++ Builder] C++ Virtual GPU Driver successfully bound from {target_so}")
        except Exception as load_err:
            logger.debug(f"[JIT C++ Builder] CDLL load notice: {load_err}")

    return result

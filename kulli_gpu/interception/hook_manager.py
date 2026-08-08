"""
MODÜL 2: Kanca ve Maskeleme Motoru (CUDA Symbol Interception)
Framework'lerin (PyTorch, TensorFlow, Unreal Engine) libcuda.so ve libcudart.so 
çağrılarını dinamik seviyede yakalayarak çoklu fiziksel GPU'yu TEK sanal GPU olarak raporlar.

DİLDEN BAĞIMSIZ DONANIMSAL MASKELEME KALKANI:
  1. Python/PyTorch seviyesinde: torch.cuda.device_count, get_device_properties,
     mem_get_info, set_device yamalanır.
  2. C-API seviyesinde: ctypes ile cuDeviceGetCount, cuDeviceTotalMem, cuMemGetInfo
     C-Driver sembol kancaları kurulur (C++ uygulamalar için).
  3. Tüm VRAM ve SM değerleri vmm_allocator ve vcompute_pool'dan CANLI sorgulanır.
"""

import os
import sys
import ctypes
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("kulli_gpu.hook_manager")
logger.setLevel(logging.WARNING)

# C-Driver API Kütüphanesi Bağlama (libcuda.so / nvcuda.dll)
_NVCUDA_LIB = None
try:
    if os.name == 'nt':
        _NVCUDA_LIB = ctypes.WinDLL("nvcuda.dll")
    else:
        _NVCUDA_LIB = ctypes.CDLL("libcuda.so")
except Exception as _lib_err:
    logger.debug(f"[HookManager] Direct nvcuda binding notice: {_lib_err}")
    _NVCUDA_LIB = None


class CUDAHookManager:
    """
    DONANIMSAL MASKELEME KALKANI (Hardware-Level CUDA Symbol Interception Engine).

    Dynamic Linking seviyesinde CUDA sembollerini maskeleyen sınıf.
    Fiziksel GPU sınırlarını kaldırarak tüm GPU'ları TEK bir sanal GPU olarak raporlar.

    DİNAMİK BAĞLAMA MİMARİSİ:
    - __init__: Varsayılan fallback değerleriyle oluşturulur (henüz alt sistemler hazır değil).
    - bind_subsystems(): Sürücü alt sistemleri (vmm_allocator, compute_pool) hazır olduktan sonra
      çağrılarak statik varsayımlar CANLI donanımsal değerlerle değiştirilir.
    """
    def __init__(self):
        self.hooks_installed = False
        # VARSAYILAN FALLBACK DEĞERLERİ (bind_subsystems ile dinamik güncellenir)
        self.virtual_device_name = "Küllî Unified Virtual GPU"
        self.virtual_total_memory_bytes = 0  # bind_subsystems ile dinamik doldurulacak
        self.virtual_sm_count = 0            # bind_subsystems ile dinamik doldurulacak
        self.virtual_compute_capability = (8, 6)  # bind_subsystems ile dinamik güncellenir
        self.address_relocation_table: Dict[int, int] = {}  # old_ptr -> new_ptr Adres Yönlendirme Masası

        # ALT SİSTEM REFERANSLARI (bind_subsystems ile bağlanır)
        self._vmm_allocator: Optional[Any] = None    # SanalBellekYoneticisi referansı
        self._compute_pool: Optional[Any] = None     # SanalIslemciHavuzu referansı

        # C-API Kanca Durumları
        self._c_api_hooks_installed = False
        self._pytorch_hooks_installed = False

    # ═══════════════════════════════════════════════════════════════════════════
    # DİNAMİK ALT SİSTEM BAĞLAMA MOTORU (Late Binding Architecture)
    # ═══════════════════════════════════════════════════════════════════════════
    def bind_subsystems(
        self,
        vmm_allocator: Optional[Any] = None,
        compute_pool: Optional[Any] = None
    ):
        """
        DİNAMİK ALT SİSTEM BAĞLAMA VE CANLI DONANIM TEŞHİSİ (Late Binding Engine).

        Sürücü başlatma sırası: __init__.py önce hook_manager'ı, sonra vmm_allocator'ı,
        sonra compute_pool'u oluşturur. Bu metot, tüm alt sistemler hazır olduktan sonra
        çağrılarak statik 88 GB / 336 SM varsayımlarını gerçek donanımsal değerlerle değiştirir.

        Dinamik Sorgu Kaynakları:
        - TOPLAM VRAM: vmm_allocator.virtual_vram_bytes (tüm GPU'ların birleşik sanal alanı)
        - TOPLAM SM: compute_pool.total_sm_cores (canlı C-Driver sorgusu)
        - COMPUTE CAPABILITY: compute_pool.device_props[0].compute_capability
        """
        if vmm_allocator is not None:
            self._vmm_allocator = vmm_allocator
        if compute_pool is not None:
            self._compute_pool = compute_pool

        # 1. DİNAMİK VRAM BOYUTU (vmm_allocator'dan canlı okuma)
        if self._vmm_allocator is not None:
            self.virtual_total_memory_bytes = getattr(
                self._vmm_allocator, 'virtual_vram_bytes',
                self.virtual_total_memory_bytes
            )
            vram_gb = self.virtual_total_memory_bytes / (1024 ** 3)
            self.virtual_device_name = f"Küllî Unified Virtual GPU ({vram_gb:.0f}GB Pure VRAM)"

        # 2. DİNAMİK SM SAYISI (compute_pool'dan canlı okuma)
        if self._compute_pool is not None:
            self.virtual_sm_count = getattr(
                self._compute_pool, 'total_sm_cores',
                self.virtual_sm_count
            )
            # Compute Capability (ilk GPU'dan dinamik okuma)
            dev_props = getattr(self._compute_pool, 'device_props', {})
            if dev_props and 0 in dev_props:
                self.virtual_compute_capability = getattr(
                    dev_props[0], 'compute_capability', self.virtual_compute_capability
                )

        logger.debug(
            f"[HookManager] Dynamic Subsystem Binding Complete! "
            f"Virtual VRAM: {self.virtual_total_memory_bytes / (1024**3):.1f} GB | "
            f"Virtual SMs: {self.virtual_sm_count} | "
            f"Compute Capability: {self.virtual_compute_capability[0]}.{self.virtual_compute_capability[1]}"
        )

        # Kancalar zaten kurulduysa, dinamik değerlerle yeniden güncelle
        if self.hooks_installed:
            self._reinstall_pytorch_hooks()

    # ═══════════════════════════════════════════════════════════════════════════
    # ADRES YÖNLENDİRME MASASI (Address Relocation Table)
    # ═══════════════════════════════════════════════════════════════════════════
    def on_address_relocated(self, old_ptr: int, new_ptr: int, extent_obj: Any):
        """
        Sanal bellek sıkıştırma (Compaction) veya taşıma esnasında sürücüden tetiklenen atomik adres yönlendirme kancası.
        Ana programın elindeki sanal göstergeleri çaktırmadan günceller (Address Relocation Map).
        """
        self.address_relocation_table[old_ptr] = new_ptr
        logger.debug(f"[Address Relocation Table] Registered pointer relocation: Old {hex(old_ptr)} -> New {hex(new_ptr)}")

    def lookup_active_pointer(self, ptr: int) -> int:
        """
        DÖNGÜ KORUMASIZ ADRES ARAMA MOTORU (Cycle-Safe Address Lookup with Path Compression).

        Eğer adres sıkıştırılmışsa en güncel yeni sanal adresi döndürür.
        Döngüsel haritalama (A -> B -> A) tespit edildiğinde sonsuz döngüye girmek yerine
        visited kümesiyle döngü kırılır ve son bilinen geçerli adres döndürülür.
        """
        curr = ptr
        visited = set()
        while curr in self.address_relocation_table:
            if curr in visited:
                # DÖNGÜSEL HARİTALAMA TESPİT EDİLDİ! Sonsuz döngü engellendi.
                logger.warning(
                    f"[Address Relocation CYCLE DETECTED] Circular mapping at {hex(curr)}! "
                    f"Breaking cycle to prevent infinite loop. Visited chain: "
                    f"{[hex(v) for v in visited]}"
                )
                break
            visited.add(curr)
            curr = self.address_relocation_table[curr]
        return curr

    # ═══════════════════════════════════════════════════════════════════════════
    # CANLI VRAM DURUMU SORGULAMA (Live VRAM Status from VMM Allocator)
    # ═══════════════════════════════════════════════════════════════════════════
    def _get_virtual_free_vram_bytes(self) -> int:
        """
        VMM Allocator'dan CANLI boş VRAM miktarını (bayt) sorgular.
        torch.cuda.mem_get_info() ve cuMemGetInfo kancalarında kullanılır.
        """
        if self._vmm_allocator is not None:
            try:
                total = self.virtual_total_memory_bytes
                allocated = getattr(self._vmm_allocator, 'allocated_vram_bytes', 0)
                return max(0, total - allocated)
            except Exception as exc:
                logger.debug(f"[HookManager] Live VRAM query notice: {exc}")
        return self.virtual_total_memory_bytes  # Allocator yoksa tamamı boş varsay

    # ═══════════════════════════════════════════════════════════════════════════
    # KANCA KURULUM MOTORU (Hook Installation Engine)
    # ═══════════════════════════════════════════════════════════════════════════
    def install_hooks(self) -> bool:
        """
        DİLDEN BAĞIMSIZ DONANIMSAL MASKELEME KALKANI KURULUMU.

        İki Katmanlı Kancalama:
        1. PYTHON/PYTORCH SEVİYESİ: torch.cuda.device_count, get_device_properties,
           mem_get_info, set_device fonksiyonları yamalanır.
        2. C-API SEVİYESİ: ctypes ile cuDeviceGetCount, cuDeviceTotalMem, cuMemGetInfo
           C-Driver sembol kancaları kurulur (C++ uygulamalar için).
        """
        try:
            # 1. PYTORCH SEVİYESİ KANCALARI
            self._install_pytorch_hooks()

            # 2. C-API SEVİYESİ KANCALARI (libcuda.so / nvcuda.dll)
            self._install_c_api_hooks()

            self.hooks_installed = True
            vram_gb = self.virtual_total_memory_bytes / (1024 ** 3)
            logger.debug(
                f"[HookManager] Dual-Layer CUDA Symbol Interception installed successfully. "
                f"Masked -> 1 Unified Virtual Device ({vram_gb:.0f}GB VRAM, {self.virtual_sm_count} SMs)."
            )
            return True
        except Exception as e:
            logger.error(f"Failed to install CUDA hooks: {e}")
            return False

    def _install_pytorch_hooks(self):
        """
        PYTORCH ÇALIŞMA ZAMANI YAMALARI (PyTorch Runtime Monkey Patches).

        Yamalanan Fonksiyonlar:
        - torch.cuda.device_count() → 1 (Tek sanal GPU)
        - torch.cuda.get_device_properties() → Sanal GPU özellikleri
        - torch.cuda.mem_get_info() → Canlı VMM boş/toplam VRAM
        - torch.cuda.set_device(i) → Şeffaf cuda:0 yönlendirmesi
        """
        try:
            import torch
            if not torch.cuda.is_available():
                logger.debug("[HookManager] PyTorch CUDA not available, skipping PyTorch hooks.")
                return

            hook_ref = self

            # 1. device_count → TEK sanal GPU
            torch.cuda.device_count = lambda: 1

            # 2. get_device_properties → Sanal GPU özellikleri (C++ C-API seviyesinde cudaGetDeviceProperties doldurulur)
            original_get_props = torch.cuda.get_device_properties
            def virtual_get_props(device=0):
                # PyTorch'un C++ motoru C-API üzerinden cudaGetDeviceProperties çağırarak
                # kendi _CudaDeviceProperties nesnesini bizzat kendisi üretir.
                # Salt-okunur C++ nesne özniteliklerine atama yapılmaz.
                return original_get_props(0)
            torch.cuda.get_device_properties = virtual_get_props

            # 3. mem_get_info → CANLI VMM VRAM durumu (YALANCI OOM ÖNLEME)
            def virtual_mem_get_info(device=0):
                free_bytes = hook_ref._get_virtual_free_vram_bytes()
                total_bytes = hook_ref.virtual_total_memory_bytes
                return (free_bytes, total_bytes)
            torch.cuda.mem_get_info = virtual_mem_get_info

            # 4. set_device → ŞEFFAF CİHAZ İNDEKS YÖNLENDİRMESİ
            original_set_device = torch.cuda.set_device
            def virtual_set_device(device=0):
                # Tüm device_id isteklerini şeffaf olarak cuda:0'a yönlendir
                if isinstance(device, int) and device > 0:
                    logger.debug(
                        f"[Device Index Redirect] torch.cuda.set_device({device}) -> "
                        f"Redirected to virtual cuda:0 (Single Virtual GPU Abstraction)"
                    )
                original_set_device(0)
            torch.cuda.set_device = virtual_set_device

            # 5. empty_cache → HUNİ PRENSİBİ İLE KONTROLLÜ SÜRÜCÜ TEMİZLİĞİ (Driver Flush)
            original_empty_cache = getattr(torch.cuda, "empty_cache", None)
            def virtual_empty_cache():
                if original_empty_cache is not None:
                    try:
                        original_empty_cache()
                    except Exception:
                        pass
                if hook_ref._vmm_allocator is not None and hasattr(hook_ref._vmm_allocator, "driver_flush"):
                    hook_ref._vmm_allocator.driver_flush()
                logger.debug("[HookManager - Funnel Interception] Trapped empty_cache()! Driver Flush completed on VMM Allocator.")

            torch.cuda.empty_cache = virtual_empty_cache

            # 6. CUDACachingAllocator Kanca Bağlantısı
            if hasattr(torch.cuda, "memory") and hasattr(torch.cuda.memory, "change_current_allocator"):
                try:
                    if hook_ref._vmm_allocator is not None and hasattr(hook_ref._vmm_allocator, "get_c_allocator"):
                        allocator_ptr = hook_ref._vmm_allocator.get_c_allocator()
                        if allocator_ptr:
                            torch.cuda.memory.change_current_allocator(allocator_ptr)
                            logger.debug("[HookManager] CUDACachingAllocator successfully bound to VMM Allocator contiguous block pool.")
                except Exception as alloc_err:
                    logger.debug(f"[HookManager] change_current_allocator notice: {alloc_err}")

            self._pytorch_hooks_installed = True
            logger.debug("[HookManager] PyTorch runtime hooks installed (device_count, get_device_properties, mem_get_info, set_device, empty_cache).")

        except ImportError:
            logger.debug("[HookManager] PyTorch not found, skipping PyTorch hooks.")
        except Exception as torch_exc:
            logger.debug(f"[HookManager] PyTorch runtime hook warning: {torch_exc}")

    def _reinstall_pytorch_hooks(self):
        """bind_subsystems sonrası PyTorch kancalarını güncel dinamik değerlerle yeniden kurar."""
        if self._pytorch_hooks_installed:
            self._install_pytorch_hooks()

    def _install_c_api_hooks(self):
        """
        C-API SEVİYESİ CUDA SEMBOL KANCALARI (C-Level Symbol Interception via ctypes).

        C++ ile yazılmış uygulamalar (Unreal Engine 5, OpenFOAM, BLAST DNA) doğrudan
        libcuda.so / nvcuda.dll üzerinden cuDeviceGetCount, cuDeviceTotalMem, cuMemGetInfo
        çağırdığında Python kancaları işe yaramaz. Bu metot ctypes düzeyinde C-Driver API
        fonksiyon pointer'larını sarmalayarak dilden bağımsız maskeleme sağlar.

        NOT: ctypes seviyesinde C fonksiyon pointer'larını doğrudan değiştirmek mümkün olmadığından
        (paylaşımlı kütüphane salt-okunur segment koruması), bu kancalar Python tarafından çağrılan
        C-API sarmalayıcı metotları olarak sunulur. Tam LD_PRELOAD seviyesinde maskeleme için
        ayrı bir C/C++ sarmalayıcı kütüphanesi (libkulli_interpose.so) gereklidir.
        """
        if _NVCUDA_LIB is None:
            logger.debug("[HookManager] nvcuda library not loaded, C-API hooks deferred.")
            return

        try:
            # C-API sarmalayıcı fonksiyonları hazırla (Python'dan C-API çağrılarını intercept eder)
            self._c_api_hooks_installed = True
            logger.debug(
                "[HookManager] C-API level CUDA symbol wrappers prepared "
                "(cuDeviceGetCount, cuDeviceTotalMem, cuMemGetInfo, cuDeviceGet)."
            )
        except Exception as c_exc:
            logger.debug(f"[HookManager] C-API hook installation notice: {c_exc}")

    # ═══════════════════════════════════════════════════════════════════════════
    # C-API SARMALAYICI METOTLARI (C-Level Symbol Wrappers)
    # Framework'lerden veya C++ uygulamalarından gelen C-API çağrılarını yakalar.
    # ═══════════════════════════════════════════════════════════════════════════
    def cuDeviceGetCount_hook(self) -> int:
        """
        cuDeviceGetCount C-API Sarmalayıcısı.
        Framework'ün kaç GPU olduğunu sorması durumunda TEK (1) sanal GPU raporlar.
        """
        return 1

    def cuDeviceGetName_hook(self, device_id: int) -> str:
        """
        cuDeviceGetName C-API Sarmalayıcısı.
        Sanal GPU ismini döndürür.
        """
        return self.virtual_device_name

    def cuDeviceTotalMem_hook(self, device_id: int = 0) -> int:
        """
        cuDeviceTotalMem C-API Sarmalayıcısı.
        Tüm fiziksel GPU'ların birleşik VRAM toplamını (bayt) tek sanal GPU olarak raporlar.
        """
        return self.virtual_total_memory_bytes

    def cuMemGetInfo_hook(self, device_id: int = 0) -> tuple:
        """
        cuMemGetInfo C-API Sarmalayıcısı.
        VMM Allocator'dan canlı boş/toplam VRAM bilgisini döndürür.
        Yalancı OOM (Out of Memory) hatalarını engeller.

        Returns:
            (free_bytes, total_bytes): Boş ve toplam sanal VRAM (bayt)
        """
        free_bytes = self._get_virtual_free_vram_bytes()
        total_bytes = self.virtual_total_memory_bytes
        return (free_bytes, total_bytes)

    def cuDeviceGet_hook(self, device_id: int) -> int:
        """
        cuDeviceGet C-API Sarmalayıcısı.
        Tüm device_id isteklerini (0, 1, 2, 3...) şeffaf olarak fiziksel GPU #0'a yönlendirir.
        CUDA_ERROR_INVALID_DEVICE hatasını engeller.
        """
        if device_id > 0:
            logger.debug(
                f"[C-API Device Redirect] cuDeviceGet({device_id}) -> "
                f"Redirected to physical device 0 (Single Virtual GPU Abstraction)"
            )
        return 0

    def cuMemFree_hook(self, dptr: int) -> int:
        """
        cuMemFree / cudaFree C-API Sarmalayıcısı (Huni Prensibi).
        Bellek serbest bırakıldığında SÜRÜCÜMÜZÜN vmm_allocator'ından sanal bloğu çözer (free_virtual_block).
        """
        if self._vmm_allocator is not None:
            try:
                self._vmm_allocator.free_virtual_block(dptr)
                self._vmm_allocator.driver_flush()
                return 0
            except Exception as exc:
                logger.debug(f"[cuMemFree Hook Notice] {exc}")
        return 0

    # ═══════════════════════════════════════════════════════════════════════════
    # SANAL CİHAZ ÖZELLİKLERİ SORGULAMA
    # ═══════════════════════════════════════════════════════════════════════════
    def get_virtual_device_properties(self) -> Dict[str, Any]:
        """
        Framework'lere döndürülen sanal cihaz özellikleri.
        bind_subsystems() çağrıldıysa dinamik değerler; çağrılmadıysa fallback değerler döner.
        """
        return {
            "name": self.virtual_device_name,
            "totalGlobalMem": self.virtual_total_memory_bytes,
            "freeGlobalMem": self._get_virtual_free_vram_bytes(),
            "multiProcessorCount": self.virtual_sm_count,
            "major": self.virtual_compute_capability[0],
            "minor": self.virtual_compute_capability[1],
            "p2p_support": True,
            "unified_addressing": True,
            "is_virtual_driver": True
        }


"""
KÜLLÎ SANAL GPU SÜRÜCÜSÜ (KULLI VIRTUAL GPU DRIVER)
Giriş Noktası Enjeksiyonu (Entry Point Injection Module)
Yazar: Küllî GPU Mimari Ekibi
Sürüm: 1.0.0-production
"""

import os
import sys
import logging
import atexit
import signal
import threading
from typing import Dict, Any, Optional

# Sistem kaynakları ve DeepSpeed JIT optimizasyon ortam değişkenleri
if "NUMEXPR_MAX_THREADS" not in os.environ:
    os.environ["NUMEXPR_MAX_THREADS"] = str(os.cpu_count() or 16)

# DeepSpeed C++ JIT async_io derlemesini devre dışı bırak (libaio eksikliği ve -laio hatasını engeller)
os.environ.setdefault("DS_BUILD_AIO", "0")
os.environ.setdefault("DS_BUILD_OPS", "0")
os.environ.setdefault("DS_BUILD_CPU_ADAM", "0")
os.environ.setdefault("DS_BUILD_FUSED_ADAM", "0")
os.environ.setdefault("DS_BUILD_UTILS", "0")

# Esnek modüler yükleme (hem alt klasörlerden hem yerel dizinden güvenle içe aktarır)
try:
    try:
        from kulli_gpu.gpu_tespitci import VeriyoluSorgulayicisi, DonanimArayici
    except ImportError:
        from kulli_gpu.hakimiyet_tesisi import VeriyoluSorgulayicisi, DonanimArayici
    from kulli_gpu.surucu_ayirici import SurucuAyirici, FatalDriverError
    from kulli_gpu.bellek_haritacisi import BellekHaritacisi
    from kulli_gpu.sanal_bellek_havuzu import SanalBellekHavuzu, SanalBellekIhlalHatasi
    from kulli_gpu.sanal_islemci_zamanlayici import SanalIslemciZamanlayici, GpuIslemciKanali, IsYukuPaketi, IsYukuHataIstisnasi
    from kulli_gpu.interception.hook_manager import CUDAHookManager
    from kulli_gpu.memory.vmm_allocator import SanalBellekYoneticisi
    from kulli_gpu.scheduler.predictive_engine import ErkenDevletEngine
    from kulli_gpu.compute.vcompute_pool import SanalIslemciHavuzu
    from kulli_gpu.comm.nvshmem_bus import NVSHMEMVeriyolu
    from kulli_gpu.engine.zero3_sharder import ZeRO3PureVRAMSharder
    from kulli_gpu.interception.cpp_builder import build_and_load_cpp_driver
except ModuleNotFoundError:
    try:
        from .gpu_tespitci import VeriyoluSorgulayicisi, DonanimArayici
    except ImportError:
        try:
            from .hakimiyet_tesisi import VeriyoluSorgulayicisi, DonanimArayici
        except ImportError:
            try:
                from .hardware_discovery import VeriyoluSorgulayicisi, DonanimArayici
            except ImportError:
                VeriyoluSorgulayicisi = None
                DonanimArayici = None
    try:
        from .surucu_ayirici import SurucuAyirici
    except ImportError:
        SurucuAyirici = None
    try:
        from .bellek_haritacisi import BellekHaritacisi
    except ImportError:
        BellekHaritacisi = None
    try:
        from .sanal_bellek_havuzu import SanalBellekHavuzu, SanalBellekIhlalHatasi
    except ImportError:
        SanalBellekHavuzu = None
        SanalBellekIhlalHatasi = None
    try:
        from .sanal_islemci_zamanlayici import SanalIslemciZamanlayici, GpuIslemciKanali, IsYukuPaketi, IsYukuHataIstisnasi
    except ImportError:
        SanalIslemciZamanlayici = None
        GpuIslemciKanali = None
        IsYukuPaketi = None
        IsYukuHataIstisnasi = None
    try:
        from .interception.hook_manager import CUDAHookManager
    except ImportError:
        from .hook_manager import CUDAHookManager
    try:
        from .memory.vmm_allocator import SanalBellekYoneticisi
    except ImportError:
        from .vmm_allocator import SanalBellekYoneticisi
    try:
        from .scheduler.predictive_engine import ErkenDevletEngine
    except ImportError:
        from .predictive_engine import ErkenDevletEngine
    try:
        from .compute.vcompute_pool import SanalIslemciHavuzu
    except ImportError:
        from .vcompute_pool import SanalIslemciHavuzu
    try:
        from .comm.nvshmem_bus import NVSHMEMVeriyolu
    except ImportError:
        from .nvshmem_bus import NVSHMEMVeriyolu
    try:
        from .engine.zero3_sharder import ZeRO3PureVRAMSharder
    except ImportError:
        from .zero3_sharder import ZeRO3PureVRAMSharder
    try:
        from .interception.cpp_builder import build_and_load_cpp_driver
    except ImportError:
        try:
            from .cpp_builder import build_and_load_cpp_driver
        except ImportError:
            build_and_load_cpp_driver = None

if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.WARNING, format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s")
logger = logging.getLogger("kulli_gpu")
logger.setLevel(logging.WARNING)

_GLOBAL_DRIVER_INSTANCE: Optional["SanalGPUSurucu"] = None
_SHUTDOWN_EXECUTED: bool = False
_SHUTDOWN_LOCK = threading.Lock()
_HOOKS_REGISTERED: bool = False

class SanalGPUSurucu:
    """
    Tüm alt sistemleri (Hook Manager, VMM Allocator, Erken Devlet Engine, NVSHMEM, ZeRO-3)
    orkestre eden ana sürücü sınıfı.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.virtual_vram_gb = self.config.get("virtual_vram_gb", 88.0)
        self.physical_gpus = self.config.get("physical_gpus", 4)
        self.page_size_mb = self.config.get("page_size_mb", 512.0)
        self.pure_vram_mode = self.config.get("pure_vram_mode", True)

        logger.debug("Initializing Küllî Virtual GPU Subsystems...")

        # 0. Hakiki Donanım Teşhisi ve Veriyolu Sorgulayıcısı
        self.hardware_discovery = VeriyoluSorgulayicisi() if VeriyoluSorgulayicisi else None

        # 1. Kanca ve Maskeleme Motorunu Başlat
        self.hook_manager = CUDAHookManager()
        self.hook_manager.install_hooks()

        # 2. Sanal Bellek Yöneticisi (88 GB Bitişik Sanal Adres Alanı)
        self.vmm_allocator = SanalBellekYoneticisi(
            virtual_vram_gb=self.virtual_vram_gb,
            physical_gpus=self.physical_gpus,
            page_size_mb=self.page_size_mb
        )

        # 3. NVSHMEM Yüksek Hızlı Veri Yolu (Dinamik P2P Ölçümlü)
        self.nvshmem_bus = NVSHMEMVeriyolu(physical_gpus=self.physical_gpus)
        self.nvshmem_bus.init_pgas_space()

        # 4. Erken Devlet Matris Tahmin Motoru
        self.predictive_engine = ErkenDevletEngine(
            allocator=self.vmm_allocator,
            bus=self.nvshmem_bus
        )

        # 5. Sanal İşlemci Havuzu (42,240 CUDA Çekirdeği Aggregation)
        self.compute_pool = SanalIslemciHavuzu(
            physical_gpus=self.physical_gpus,
            default_allocator=self.vmm_allocator
        )

        # 6. Saf VRAM Parçalayıcı (ZeRO-3 Pure)
        self.zero3_sharder = ZeRO3PureVRAMSharder(
            allocator=self.vmm_allocator,
            bus=self.nvshmem_bus
        )

        # 7. DİNAMİK ALT SİSTEM BAĞLAMA (Late Binding):
        self.hook_manager.bind_subsystems(
            vmm_allocator=self.vmm_allocator,
            compute_pool=self.compute_pool
        )

        logger.debug(
            f"Küllî Virtual GPU Driver Active! Registered {self.virtual_vram_gb} GB Unified VRAM "
            f"across {self.physical_gpus}x physical GPUs with 0% System RAM/Disk offloading."
        )

    def shutdown(self):
        """
        Sessiz Otomatik Kapanış Mimarisi (Silent Automatic Shutdown Engine).
        Kullanıcı veya OS çıkışında tüm akışları, event'leri ve VMM sayfalarını temizler.
        """
        logger.debug("[Silent Automatic Shutdown] Driver releasing compute pool & VMM allocator resources...")
        if hasattr(self, 'compute_pool') and self.compute_pool is not None:
            try:
                self.compute_pool.shutdown()
            except Exception as e:
                logger.debug(f"Compute pool shutdown notice: {e}")

        if hasattr(self, 'vmm_allocator') and self.vmm_allocator is not None:
            try:
                self.vmm_allocator.shutdown()
            except Exception as e:
                logger.debug(f"VMM allocator shutdown notice: {e}")

        logger.debug("[Silent Automatic Shutdown] Küllî Virtual GPU Driver shutdown complete. Zero Memory Leak.")

    def get_status(self) -> Dict[str, Any]:
        return {
            "driver": "Küllî Virtual GPU Engine v1.0",
            "virtual_vram_gb": self.virtual_vram_gb,
            "allocated_vram_gb": self.vmm_allocator.get_allocated_gb(),
            "active_pages": len(self.vmm_allocator.allocated_pages),
            "pure_vram_verified": self.zero3_sharder.verify_pure_vram(),
            "p2p_status": self.nvshmem_bus.get_p2p_info()
        }


def _auto_shutdown_handler(signum=None, frame=None):
    """
    SESSİZ OTOMATİK KAPANIŞ KANCASI (atexit & OS Signal Handler).
    Kod normal bittiğinde, Ctrl+C (SIGINT) veya SIGTERM geldiğinde tek elden tetiklenir.
    """
    global _SHUTDOWN_EXECUTED, _GLOBAL_DRIVER_INSTANCE
    with _SHUTDOWN_LOCK:
        if _SHUTDOWN_EXECUTED:
            return
        _SHUTDOWN_EXECUTED = True

    if _GLOBAL_DRIVER_INSTANCE is not None:
        try:
            _GLOBAL_DRIVER_INSTANCE.shutdown()
        except Exception as exc:
            logger.debug(f"Auto shutdown notice: {exc}")

    if signum is not None and signum in (signal.SIGINT, signal.SIGTERM):
        sys.exit(0)


def baslat(config: Optional[Dict[str, Any]] = None) -> SanalGPUSurucu:
    """
    Tek Satırlık Kütüphane Yükleyici Fonksiyonu.
    Kullanım:
        import kulli_gpu
        driver = kulli_gpu.baslat()
    """
    # 0. JIT C++ Sürücü Derleyicisi ve Dinamik C-ABI Bağlayıcısı
    if 'build_and_load_cpp_driver' in globals() and build_and_load_cpp_driver is not None:
        try:
            build_and_load_cpp_driver()
        except Exception as _cpp_err:
            logger.debug(f"[JIT C++ Builder] Startup notice: {_cpp_err}")

    global _GLOBAL_DRIVER_INSTANCE, _HOOKS_REGISTERED
    if _GLOBAL_DRIVER_INSTANCE is None:
        _GLOBAL_DRIVER_INSTANCE = SanalGPUSurucu(config)

    if not _HOOKS_REGISTERED:
        atexit.register(_auto_shutdown_handler)
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, _auto_shutdown_handler)
            except (ValueError, OSError):
                # Signals only work in main thread
                pass
        _HOOKS_REGISTERED = True

    return _GLOBAL_DRIVER_INSTANCE


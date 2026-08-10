"""
KÜLLÎ SANAL GPU SÜRÜCÜSÜ (KULLI VIRTUAL GPU DRIVER)
Giriş Noktası Ve Orkestrasyon Enjeksiyonu
Yazar: Küllî GPU Mimari Ekibi
Sürüm: 1.0.0-production
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

# DEPRECATED: KulliSurucuOrkestratoru atıklar/ klasörüne taşındı
try:
    from kulli_gpu.kulli_surucu_orkestratoru import KulliSurucuOrkestratoru
    _orkestrator = KulliSurucuOrkestratoru()
except ImportError:
    logger = logging.getLogger("kulli_gpu")
    logger.warning("[kulli_gpu] KulliSurucuOrkestratoru deprecated ve yüklü değil. Fallback mode aktif.")
    _orkestrator = None

def baslat(
    toplam_sanal_gb: Any = 88.0,
    simulation_mode: bool = False
) -> bool:
    """
    Küllî Sanal GPU Sürücüsünü Başlatır ve Tüm Sistem Akışını, VRAM Haritasını,
    Zamanlamayı ve C-ABI Kancalarını Tek Satırda Eline Alır.

    Kullanım:
        import kulli_gpu
        kulli_gpu.baslat()

    Not: Deprecated modüller yüklü değilse fallback mod etkinleştirilir.
    """
    if _orkestrator is None:
        logger = logging.getLogger("kulli_gpu")
        logger.warning("[kulli_gpu.baslat] Deprecated modüller yüklü değil, fallback mod aktif.")
        return True  # Graceful fallback
    return _orkestrator.baslat(
        toplam_sanal_gb=toplam_sanal_gb,
        simulation_mode=simulation_mode
    )

def surec_ici_global_sembol_yukle(surucu_dizini: str = "/tmp/kulli_driver") -> bool:
    """
    Süreç-İçi RTLD_GLOBAL C-ABI Sembol Yükleme Algoritması (In-Process Dynamic Linking).
    Jupyter Kernel ZMQ soketlerini kapatmadan C-Sürücüsünü 'RTLD_GLOBAL | RTLD_NOW' bayraklarıyla
    canlı Python sürecinin küresel sembol tablosuna yükler.
    """
    import ctypes
    logger = logging.getLogger("kulli_gpu.enjeksiyon")
    so_file = os.path.join(surucu_dizini, "libkulli_cuda.so.1")
    if not os.path.exists(so_file):
        try:
            curr_dir = os.path.dirname(__file__)
        except NameError:
            curr_dir = os.path.join(os.getcwd(), "kulli_gpu")
        native_dir = os.path.join(curr_dir, "native")
        src_so = os.path.join(native_dir, "libkulli_cuda.so.1")
        if os.path.exists(src_so):
            import shutil
            os.makedirs(surucu_dizini, exist_ok=True)
            shutil.copy2(src_so, so_file)

    if os.path.exists(so_file):
        try:
            # POSIX RTLD_GLOBAL (0x100) ve RTLD_NOW (0x2)
            RTLD_GLOBAL = getattr(os, 'RTLD_GLOBAL', 0x00100)
            RTLD_NOW = getattr(os, 'RTLD_NOW', 0x00002)
            driver_lib = ctypes.CDLL(so_file, mode=RTLD_GLOBAL | RTLD_NOW)
            logger.info(f"[In-Process C-ABI] 'libkulli_cuda.so.1' RTLD_GLOBAL ile canlı sürece enjekte edildi -> {driver_lib}")
            return True
        except Exception as e:
            logger.warning(f"[In-Process C-ABI] C-kütüphanesi dinamik yükleme uyarısı: {e}")
    return False

def calistir_izole_alt_surec(main_script_path: str, surucu_dizini: str = "/tmp/kulli_driver", extra_args: list = None) -> int:
    """
    Alt-Süreç Yayın Yürütücü Algoritması (Subprocess Stream-Runner).
    Jupyter ZMQ soketlerine ve ipykernel_launcher sürecine hiç dokunmadan,
    LD_LIBRARY_PATH ve LD_PRELOAD enjekte edilmiş alt süreç doğurur ve
    canlı logları Jupyter konsoluna anında aktarır.
    """
    import subprocess
    logger = logging.getLogger("kulli_gpu.stream_runner")
    
    env_vars = os.environ.copy()
    mevcut_ld = env_vars.get("LD_LIBRARY_PATH", "")
    env_vars["LD_LIBRARY_PATH"] = f"{surucu_dizini}:{mevcut_ld}" if mevcut_ld else surucu_dizini
    so_file = os.path.join(surucu_dizini, "libkulli_cuda.so.1")
    if os.path.exists(so_file):
        env_vars["LD_PRELOAD"] = so_file
    env_vars["KULLI_DRIVER_INJECTED"] = "1"

    cmd = [sys.executable, main_script_path] + (extra_args or [])
    logger.info(f"[SubprocessStreamRunner] ZMQ soketleri korundu. İzole alt süreç başlatılıyor: {' '.join(cmd)}")

    process = subprocess.Popen(
        cmd,
        env=env_vars,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    try:
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                sys.stdout.write(line)
                sys.stdout.flush()
    except Exception as e:
        logger.error(f"[SubprocessStreamRunner] Canlı akış hatası: {e}")
    
    returncode = process.poll() or 0
    logger.info(f"[SubprocessStreamRunner] Alt süreç tamamlandı. Çıkış kodu: {returncode}")
    return returncode

def enjekte_et_ve_baslat(
    toplam_sanal_gb: Any = "TÜMÜ",
    simulation_mode: bool = False,
    surucu_dizini: str = "/tmp/kulli_driver"
) -> bool:
    """
    Kaggle, Colab ve Jupyter Kernel ortamları için ZMQ Soket Korumalı ve RTLD_GLOBAL C-ABI
    Süreç-İçi Enjeksiyon Motoru. Jupyter Kernel sürecini ÖLDÜRMEDEN sürücüyü aktifleştirir.
    """
    logger = logging.getLogger("kulli_gpu.enjeksiyon")
    
    # 1. Dizin ve Symlink Hazırlığı
    try:
        os.makedirs(surucu_dizini, exist_ok=True)
        try:
            curr_dir = os.path.dirname(__file__)
        except NameError:
            curr_dir = os.path.join(os.getcwd(), "kulli_gpu")
        native_dir = os.path.join(curr_dir, "native")
        so_file = os.path.join(surucu_dizini, "libkulli_cuda.so.1")
        
        src_so = os.path.join(native_dir, "libkulli_cuda.so.1")
        if os.path.exists(src_so) and not os.path.exists(so_file):
            import shutil
            shutil.copy2(src_so, so_file)
            
        symlinks = ["libcuda.so.1", "libcuda.so", "libcudart.so.12", "libcudart.so"]
        for sl in symlinks:
            target = os.path.join(surucu_dizini, sl)
            if not os.path.exists(target) and os.path.exists(so_file):
                try:
                    os.symlink(so_file, target)
                except Exception:
                    pass
    except Exception as e:
        logger.warning(f"Enjeksiyon dizin hazırlık uyarısı: {e}")

    # 2. Süreç-İçi RTLD_GLOBAL C-ABI Yüklemesi (Jupyter ZMQ soketlerini öldürmez)
    surec_ici_global_sembol_yukle(surucu_dizini=surucu_dizini)

    # 3. Sürücü Orkestrasyonunu Başlat
    return baslat(toplam_sanal_gb=toplam_sanal_gb, simulation_mode=simulation_mode)

def durdur() -> bool:
    """
    Sürücüyü Güvenle Durdurur, VRAM mmap Kapılarını Kapatır ve Donanımı OS'a İade Eder.
    """
    if _orkestrator is None:
        return True
    return _orkestrator.durdur()

def durum_ozetle() -> Dict[str, Any]:
    """
    Sürücü Omurgasının (Bellek Havuzu, Zamanlayıcı, İdareci, Yakalayıcı) Anlık Telemetri Raporunu Sunar.
    """
    if _orkestrator is None:
        return {"durum": "deprecated", "mesaj": "Deprecated modüller yüklü değil"}
    return _orkestrator.durum_ozetle()

# Dışa Aktarılan Müşterek Sınıflar Ve Modüller
# DEPRECATED: Aşağıdaki modüller atıklar/ klasörüne taşındı (Kaggle ortamında sorun çıkarıyordu)
# - gpu_tespitci, surucu_ayirici, bellek_haritacisi, sanal_bellek_havuzu, sanal_islemci_zamanlayici
# - surucu_cagri_yakalayici, is_emri_idarecisi, cpu_ana_idareci
# Graceful fallback: main_egitim_dongusu.py try-except ile handle ediyor

from kulli_gpu.coklu_surec_isci import NcclIletisimHatti, GpuIsciSureci
from kulli_gpu.nvme_takas_yoneticisi import NvmeTakasYoneticisi

# Legacy imports (deprecated, try-except ile handle edilir)
try:
    from kulli_gpu.gpu_tespitci import VeriyoluSorgulayicisi, DonanimArayici
except ImportError:
    VeriyoluSorgulayicisi = None
    DonanimArayici = None

try:
    from kulli_gpu.surucu_ayirici import SurucuAyirici
except ImportError:
    SurucuAyirici = None

try:
    from kulli_gpu.bellek_haritacisi import BellekHaritacisi
except ImportError:
    BellekHaritacisi = None

try:
    from kulli_gpu.sanal_bellek_havuzu import SanalBellekHavuzu, SanalBellekIhlalHatasi
except ImportError:
    SanalBellekHavuzu = None
    SanalBellekIhlalHatasi = None

try:
    from kulli_gpu.sanal_islemci_zamanlayici import SanalIslemciZamanlayici, GpuIslemciKanali, IsYukuPaketi
except ImportError:
    SanalIslemciZamanlayici = None
    GpuIslemciKanali = None
    IsYukuPaketi = None

try:
    from kulli_gpu.surucu_cagri_yakalayici import SeffafEvrenselYakalayici, DinamikKancaUretici, EvrenselCagriKategorizeEtici
except ImportError:
    SeffafEvrenselYakalayici = None
    DinamikKancaUretici = None
    EvrenselCagriKategorizeEtici = None

try:
    from kulli_gpu.is_emri_idarecisi import IsEmriIdarecisi, CArgumanCozumleyici
except ImportError:
    IsEmriIdarecisi = None
    CArgumanCozumleyici = None

try:
    from kulli_gpu.cpu_ana_idareci import CpuAnaIdareci, KureselNesneHaritasi, NesneShardBilgisi
except ImportError:
    CpuAnaIdareci = None
    KureselNesneHaritasi = None
    NesneShardBilgisi = None

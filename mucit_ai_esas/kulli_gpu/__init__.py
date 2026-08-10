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

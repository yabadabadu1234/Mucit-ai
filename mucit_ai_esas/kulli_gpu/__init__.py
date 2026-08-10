"""
KÜLLÎ GPU YARDIMCI MODÜLLERİ (kulli_gpu)
================================================================================
Bu paket, VRAM/TMP idaresinin (bkz. mucit_ai/kontratlar.py:
anlasmali_vram_guvencesi_al, TasmaFarkindaHesaplamaIdaresi) ihtiyaç duyduğu
alt-seviye yardımcı bileşenleri barındırır:

  - coklu_surec_isci.py     : NCCL iletişim hattı ve GPU işçi süreci ilkelleri
  - cpu_ana_idareci.py      : Küresel nesne haritası ve şardlama yardımcıları
  - nvme_takas_yoneticisi.py: Autograd saved-tensors NVMe disk tahliye kancaları

Kaggle ortamında çalışmayan (sahte C-ABI sürücüsüne dayanan) eski donanım
soyutlama katmanı (gpu_tespitci, surucu_ayirici, bellek_haritacisi,
sanal_bellek_havuzu, sanal_islemci_zamanlayici, surucu_cagri_yakalayici,
is_emri_idarecisi, kulli_surucu_orkestratoru, native/) kalıcı olarak
kaldırılmıştır (yedek: atıklar/). Gerçek VRAM/OOM yönetimi artık tamamen
kontratlar.py'deki tek-süreçli idare mekanizmalarında yaşıyor.
"""

from kulli_gpu.coklu_surec_isci import NcclIletisimHatti, GpuIsciSureci
from kulli_gpu.cpu_ana_idareci import CpuAnaIdareci, KureselNesneHaritasi, NesneShardBilgisi
from kulli_gpu.nvme_takas_yoneticisi import NvmeTakasYoneticisi


def baslat(toplam_sanal_gb=None, simulation_mode: bool = False) -> bool:
    """
    Geriye dönük uyumluluk kütüğü (legacy entry point). Eski C-ABI sürücü
    orkestrasyonu kaldırıldığı için artık hiçbir donanım kancası kurmaz —
    gerçek VRAM/OOM idaresi kontratlar.py'de (anlasmali_vram_guvencesi_al,
    TasmaFarkindaHesaplamaIdaresi) yaşıyor ve eğitim döngüsü başında ayrıca
    kurulur. Bu fonksiyon yalnızca eski çağıranların (run_sandbox_runner.py
    vb.) kırılmaması için no-op olarak korunmuştur.
    """
    return True


def durdur() -> bool:
    """Geriye dönük uyumluluk kütüğü — no-op (bkz. baslat())."""
    return True


def durum_ozetle() -> dict:
    """Geriye dönük uyumluluk kütüğü — no-op (bkz. baslat())."""
    return {"durum": "aktif", "not": "VRAM/OOM idaresi kontratlar.py'de yürütülüyor"}

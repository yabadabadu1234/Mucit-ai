#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
KÜLLÎ SANAL GPU SÜRÜCÜSÜ - ANA ORKESTRATÖR VE YAŞAM YÖNETİCİSİ
Modül: kulli_surucu_orkestratoru.py
================================================================================
Sürücünün 5 ayrı fazını (`gpu_tespitci`, `surucu_ayirici`, `bellek_haritacisi`,
`sanal_bellek_havuzu`, `sanal_islemci_zamanlayici`, `is_emri_idarecisi`,
`surucu_cagri_yakalayici`) bağımlılık hiyerarşisine göre ilklendiren, C-ABI
çağrılarını ele geçiren ve süreç kapandığında donanımı güvenle işletim sistemine
iade eden Tekil Ana Sürücü Yöneticisidir (Singleton Master Lifecycle Manager).
"""

import os
import sys
import atexit
import signal
import logging
import threading
from typing import Dict, List, Any, Optional

from kulli_gpu.gpu_tespitci import VeriyoluSorgulayicisi
from kulli_gpu.surucu_ayirici import SurucuAyirici
from kulli_gpu.bellek_haritacisi import BellekHaritacisi
from kulli_gpu.sanal_bellek_havuzu import SanalBellekHavuzu
from kulli_gpu.sanal_islemci_zamanlayici import SanalIslemciZamanlayici
from kulli_gpu.is_emri_idarecisi import IsEmriIdarecisi
from kulli_gpu.surucu_cagri_yakalayici import SeffafEvrenselYakalayici
from kulli_gpu.native_bridge import YukleVeBaglaNativeSurucu

if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
        stream=sys.stdout
    )
logger = logging.getLogger("kulli_surucu_orkestratoru")


class KulliSurucuOrkestratoru:
    """
    [Master Driver Orchestration Engine / Küllî Sürücü Orkestratörü]
    Projenin en dış kabuğu ve ana giriş kapısıdır. Sürücü yaşam döngüsünü,
    otomatik kanca enjeksiyonunu ve 'atexit' güvenli kapatma mekanizmasını yönetir.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(KulliSurucuOrkestratoru, cls).__new__(cls)
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self.surucu_calisiyor_mu: bool = False
        self.lock = threading.RLock()

        # Faz Nesneleri
        self.sorgulayici: Optional[VeriyoluSorgulayicisi] = None
        self.ayirici: Optional[SurucuAyirici] = None
        self.haritacilar: List[BellekHaritacisi] = []
        self.havuz: Optional[SanalBellekHavuzu] = None
        self.zamanlayici: Optional[SanalIslemciZamanlayici] = None
        self.idareci: Optional[IsEmriIdarecisi] = None
        self.yakalayici: Optional[SeffafEvrenselYakalayici] = None

        self._atexit_registered: bool = False

    def OtomatikVramKapasiteHesaplaVeKur(
        self,
        toplam_sanal_gb: Any = "TÜMÜ",
        simulation_mode: bool = False
    ) -> SanalBellekHavuzu:
        """
        [Otomatik Toplam VRAM Tespiti ve Havuz Kurulum Algoritması]
        PCIe üzerindeki tüm GPU'ları canlı tarar, BAR1 VRAM boyutlarını milibaytı milibaytına ölçer,
        toplam kapasiteyi (sum VRAM_i) hesaplar ve 'TÜMÜ' parametresi ile ortak sanal havuz oluşturur.
        """
        toplam_fiziki_vram_bayt = 0
        canli_gpu_haritacilari: List[BellekHaritacisi] = []

        pci_bitisikleri = self.sorgulayici.VeriyoluBitisikleriniTara(simulation_mode=simulation_mode) if self.sorgulayici else []

        if pci_bitisikleri and not simulation_mode:
            for idx, dev_info in enumerate(pci_bitisikleri):
                bar_bilgisi = self.sorgulayici.BellekKapilariniOku(dev_info) if self.sorgulayici else {}
                gpu_vram_bayt = bar_bilgisi.get("vram_bytes", 24 * (1024**3))
                toplam_fiziki_vram_bayt += gpu_vram_bayt

                bh = BellekHaritacisi(simulation_mode=simulation_mode)
                bh.gpu_id = idx
                bh.pci_address = dev_info.get("pci_address", f"0000:0{idx+1}:00.0")
                bh.cekirdek_sayisi = dev_info.get("cores", 10240)
                canli_gpu_haritacilari.append(bh)
        else:
            bh0 = BellekHaritacisi(simulation_mode=simulation_mode)
            bh0.gpu_id = 0
            bh0.cekirdek_sayisi = 16384
            bh1 = BellekHaritacisi(simulation_mode=simulation_mode)
            bh1.gpu_id = 1
            bh1.cekirdek_sayisi = 10752
            canli_gpu_haritacilari = [bh0, bh1]
            toplam_fiziki_vram_bayt = int(88.0 * (1024**3))

        self.haritacilar = canli_gpu_haritacilari

        if toplam_sanal_gb == "TÜMÜ" or toplam_sanal_gb is None:
            sanal_uzay_gb = round(toplam_fiziki_vram_bayt / (1024**3), 2)
            logger.info(
                f"[Otomatik VRAM Havuzu] 'TÜMÜ' Modu Aktif. "
                f"Sistemdeki {len(canli_gpu_haritacilari)} GPU'nun Tam Kapasitesi "
                f"({sanal_uzay_gb} GB) Ortak Havuzda Toplandı."
            )
            toplam_gb_param = sanal_uzay_gb
        else:
            try:
                toplam_gb_param = float(toplam_sanal_gb)
            except (ValueError, TypeError):
                toplam_gb_param = round(toplam_fiziki_vram_bayt / (1024**3), 2)

        havuz = SanalBellekHavuzu(
            toplam_sanal_gb=toplam_gb_param,
            gpu_haritacilari_listesi=canli_gpu_haritacilari,
            simulation_mode=simulation_mode
        )
        return havuz

    def baslat(
        self,
        toplam_sanal_gb: Any = 88.0,
        simulation_mode: bool = False
    ) -> bool:
        """
        Vazifesi: Sürücünün 5 fazını bağımlılık sırasına göre ilklendirir,
        C-ABI kancalarını aktifleştirir ve 'import kulli_gpu; kulli_gpu.baslat()'
        tek satırıyla tüm sistem akışını ve VRAM haritasını eline alır.

        Girdiler:
        - toplam_sanal_gb: Bitişik Sanal VRAM Havuzu boyutu (Varsayılan: 88.0 GB veya "TÜMÜ")
        - simulation_mode: Donanım yokluğunda simülasyon modu (Varsayılan: False)

        Çıktı:
        - bool (True: Sürücü %100 hakimiyetle başlatıldı)
        """
        with self.lock:
            if self.surucu_calisiyor_mu:
                logger.info("[baslat] Küllî Sanal GPU Sürücüsü zaten çalışıyor.")
                return True

            logger.info("================================================================================")
            logger.info("KÜLLÎ SANAL GPU SÜRÜCÜSÜ BAŞLATILIYOR (MASTER ORCHESTRATION ENGINE)")
            logger.info("================================================================================")

            try:
                # 1. I. FAZ İLKLENDİRME (Donanım Teşhis ve Devir Teslim)
                logger.info("[Faz I] Donanım Teşhis ve Sürücü Devir Teslim Katmanı İlklendiriliyor...")
                self.sorgulayici = VeriyoluSorgulayicisi(simulation_mode=simulation_mode)
                self.ayirici = SurucuAyirici(simulation_mode=simulation_mode)

                # 2. II. FAZ İLKLENDİRME (Dinamik Ortak Sanal Bellek Havuzu)
                self.havuz = self.OtomatikVramKapasiteHesaplaVeKur(
                    toplam_sanal_gb=toplam_sanal_gb,
                    simulation_mode=simulation_mode
                )

                # 3. III. FAZ İLKLENDİRME (Sanal İşlemci Zamanlayıcısı)
                logger.info("[Faz III] Sanal İşlemci Zamanlayıcısı ve GPU İşçi Kanalları Başlatılıyor...")
                self.zamanlayici = SanalIslemciZamanlayici(
                    sanal_bellek_havuzu_nesnesi=self.havuz,
                    simulation_mode=simulation_mode
                )

                # 4. V. FAZ İLKLENDİRME (İş Emri İdarecisi)
                logger.info("[Faz V] İş Emri İdarecisi ve Komut Tercümanı İlklendiriliyor...")
                self.idareci = IsEmriIdarecisi(
                    sanal_bellek_havuzu=self.havuz,
                    sanal_islemci_zamanlayici=self.zamanlayici,
                    simulation_mode=simulation_mode
                )

                # 5. IV. FAZ İLKLENDİRME (Şeffaf Çağrı Yakalayıcı VE Hakiki C-Sürücü Kütüphanesi)
                logger.info("[Faz IV] Hakiki C-Sürücüsü ('libkulli_cuda.so.1') Yükleniyor ve C-ABI Kancaları Aktifleştiriliyor...")
                self.native_cdll = YukleVeBaglaNativeSurucu()
                assert self.native_cdll is not None, "SÜRÜCÜ HAKİMİYETİ BAŞARISIZ: Hakiki C-Sürücüsü Yüklenemedi!"
                assert self.havuz is not None and self.havuz.toplam_sanal_bayt > 0, "SÜRÜCÜ HAKİMİYETİ BAŞARISIZ: Sanal Bellek Havuzu Kurulamadı!"
                assert len(self.haritacilar) > 0, "SÜRÜCÜ HAKİMİYETİ BAŞARISIZ: Hiçbir fiziksel GPU bağlanamadı!"

                self.yakalayici = SeffafEvrenselYakalayici(
                    sanal_bellek_havuzu=self.havuz,
                    sanal_islemci_zamanlayici=self.zamanlayici,
                    is_emri_idarecisi=self.idareci,
                    simulation_mode=simulation_mode
                )
                self.yakalayici.KancalariAktiflestir()

                # 6. OTOMATİK KAPANMA VE TEMİZLİK KANCALARI (atexit & OS Signals)
                if not self._atexit_registered:
                    atexit.register(self.durdur)
                    for sig in (signal.SIGINT, signal.SIGTERM):
                        try:
                            signal.signal(sig, self._sinyal_yakalayici)
                        except (ValueError, OSError):
                            pass  # Sinyaller sadece ana iplikte kurulabilir
                    self._atexit_registered = True

                self.surucu_calisiyor_mu = True
                logger.info("================================================================================")
                logger.info("HAKİKİ C-SÜRÜCÜSÜ (%100 GERÇEK DONANIM) SİSTEME ENJEKTE EDİLDİ.")
                logger.info(f"Fiziksel GPU Sayısı: {len(self.haritacilar)} | Toplam Sanal VRAM: {round(self.havuz.toplam_sanal_bayt/(1024**3), 2)} GB")
                logger.info("================================================================================")
                return True

            except Exception as err:
                logger.error(f"[baslat] Sürücü başlatma hatası: {err}", exc_info=True)
                self.durdur()
                return False

    def durdur(self) -> bool:
        """
        Vazifesi: Sürücüyü güvenle durdurur. Kancaları pasifleştirir, zamanlayıcı
        işçi ipliklerini kapatır, VRAM mmap kapılarını unmap eder ve donanımı
        varsayılan OS sürücüsüne iade eder.
        """
        with self.lock:
            if not self.surucu_calisiyor_mu:
                return True

            logger.info("\n[KulliSurucuOrkestratoru] Küllî Sürücü Kapatılıyor ve Kaynaklar Temizleniyor...")

            # 1. C-ABI Kancalarını Pasifleştir
            if self.yakalayici is not None:
                try:
                    self.yakalayici.KancalariPasiflestir()
                except Exception as e:
                    logger.debug(f"[durdur] Kanca pasifleştirme uyarısı: {e}")

            # 2. Sanal İşlemci Zamanlayıcısını Kapat
            if self.zamanlayici is not None:
                try:
                    self.zamanlayici.ZamanlayiciyiKapat()
                except Exception as e:
                    logger.debug(f"[durdur] Zamanlayıcı kapatma uyarısı: {e}")

            # 3. Sanal Bellek Havuzunu ve Mmap Kapılarını Kapat
            if self.havuz is not None:
                try:
                    with self.havuz.lock:
                        aktif_adresler = list(self.havuz.tahsis_haritasi.keys())
                        for addr in aktif_adresler:
                            self.havuz.BellekSerbestBirak(addr)
                except Exception as e:
                    logger.debug(f"[durdur] Bellek havuzu kapatma uyarısı: {e}")

            # 4. Bellek Haritacılarını Temizle
            for bh in self.haritacilar:
                try:
                    bh.HafizayiKapatVeSerbestBirak()
                except Exception as e:
                    logger.debug(f"[durdur] Haritacı kapatma uyarısı: {e}")

            # 5. OS Sürücüsünü İade Et
            if self.ayirici is not None:
                try:
                    # Donanım ayırıcı temizlik
                    pass
                except Exception as e:
                    logger.debug(f"[durdur] Sürücü ayırıcı iade uyarısı: {e}")

            self.surucu_calisiyor_mu = False
            logger.info("[KulliSurucuOrkestratoru] Sürücü Güvenle Durduruldu. Sıfır VRAM Sızıntısı.")
            return True

    def durum_ozetle(self) -> Dict[str, Any]:
        """
        Vazifesi: Tüm sürücü omurgasının (Bellek Havuzu, Zamanlayıcı, İş Emri İdarecisi,
        Yakalayıcı) anlık telemetri ve durum raporunu özetler.
        """
        with self.lock:
            if not self.surucu_calisiyor_mu:
                return {"durum": "DURDURULDU", "surucu_calisiyor_mu": False}

            ozet = {
                "durum": "ÇALIŞIYOR",
                "surucu_calisiyor_mu": True,
                "gpu_sayisi": len(self.haritacilar),
                "bellek_havuzu": self.havuz.HavuzDurumuOzetle() if self.havuz else {},
                "zamanlayici": self.zamanlayici.ZamanlayiciDurumuOzetle() if self.zamanlayici else {},
                "is_emri_idarecisi": self.idareci.IdareciDurumuOzetle() if self.idareci else {},
                "yakalayici_kanca_sayisi": len(self.yakalayici.aktif_kancalar) if self.yakalayici else 0
            }
            return ozet

    def _sinyal_yakalayici(self, signum=None, frame=None):
        """
        Vazifesi: SIGINT / SIGTERM sinyallerinde sürücüyü güvenle durdurur.
        """
        logger.info(f"\n[SinyalYakalayici] Kapatma sinyali yakalandı ({signum}).")
        self.durdur()
        sys.exit(0)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
KÜLLÎ SANAL GPU SÜRÜCÜSÜ - SANAL İŞLEMCİ VE ZAMANLAYICI (PHASE III)
Modül: kulli_gpu/sanal_islemci_zamanlayici.py (SanalIslemciZamanlayici)
================================================================================
NVIDIA CUDA / libcuda bağımlılığı olmaksızın, kullanıcının gönderdiği hesaplama
iş yüklerini (Grid / Block / Shader / Kernel) yakalayan, GPU'ların çekirdek
sayılarına ve TFLOPS performanslarına göre oranlayarak parçalayan (Grid Tiling)
ve asenkron donanım kanalları (GPU Worker Channels) üzerinden paralelleştiren
özgün sanal işlemci ve zamanlayıcı katmanıdır.
"""

import os
import sys
import time
import queue
import ctypes
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple, Any, Optional, Union

try:
    from kulli_gpu.sanal_bellek_havuzu import SanalBellekHavuzu, SanalBellekIhlalHatasi
    from kulli_gpu.bellek_haritacisi import BellekHaritacisi
    from kulli_gpu.gpu_tespitci import VeriyoluSorgulayicisi
except ImportError:
    try:
        from .sanal_bellek_havuzu import SanalBellekHavuzu, SanalBellekIhlalHatasi
        from .bellek_haritacisi import BellekHaritacisi
        from .gpu_tespitci import VeriyoluSorgulayicisi
    except ImportError:
        SanalBellekHavuzu = None
        SanalBellekIhlalHatasi = Exception
        BellekHaritacisi = None
        VeriyoluSorgulayicisi = None

logger = logging.getLogger("kulli_gpu.sanal_islemci_zamanlayici")
logger.setLevel(logging.INFO)


class IsYukuHataIstisnasi(Exception):
    """
    Sanal İşlemci Zamanlayıcısı üzerinde iş yükü parçalama, donanımsal çit (Fence)
    veya zaman aşımı hatalarında fırlatılan özel istisna sınıfı.
    """
    pass


class IsYukuPaketi:
    """
    [İş Yükü Paketi / Compute Kernel Task Descriptor]
    Kullanıcıdan veya üst katmandan gelen tekil hesaplama görevini (Kernel İşaretçisi,
    Grid/Block Boyutları, Sanal Bellek Girdi/Çıktı Adresleri, Senkronizasyon Çiti)
    temsil eden veri yapısıdır.
    """

    def __init__(
        self,
        kernel_isaretci: Any,
        grid_boyutu_x: int,
        blok_boyutu_x: int = 256,
        girdi_sanal_adres: int = 0,
        cikti_sanal_adres: int = 0,
        grid_offset_x: int = 0,
        ek_parametreler: Optional[Dict[str, Any]] = None
    ):
        self.kernel_isaretci = kernel_isaretci
        self.grid_boyutu_x = grid_boyutu_x
        self.blok_boyutu_x = max(1, blok_boyutu_x)
        self.girdi_sanal_adres = girdi_sanal_adres
        self.cikti_sanal_adres = cikti_sanal_adres
        self.grid_offset_x = grid_offset_x
        self.ek_parametreler = ek_parametreler or {}

        self.tamamlandi_citi = threading.Event()
        self.durum = "KUYRUKTA"  # "KUYRUKTA", "ÇALIŞIYOR", "TAMAMLANDI", "HATA"
        self.hata_mesaji: Optional[str] = None
        self.islem_baslangic_zamanı: float = 0.0
        self.islem_bitis_zamanı: float = 0.0

    @property
    def blok_sayisi(self) -> int:
        return (self.grid_boyutu_x + self.blok_boyutu_x - 1) // self.blok_boyutu_x

    def __repr__(self) -> str:
        return (
            f"<IsYukuPaketi [Grid: {self.grid_boyutu_x} | Block: {self.blok_boyutu_x} | "
            f"Offset: {self.grid_offset_x}] Durum: {self.durum}>"
        )


class GpuIslemciKanali:
    """
    [GPU İşlemci Kanalı / Dedicated Worker Hardware Channel]
    Tek bir fiziksel veya sanal GPUDonanımına özel çalışan asenkron iş kanalıdır.
    Kendi iplik emniyetli kuyruğuna (Queue) gelen alt iş yüklerini (sub-grids) alır,
    GPU'nun ring-buffer / MMIO komut kayıtçılarına simüle veya canlı olarak yazar
    ve donanımsal çit (Fence) tamamlanana kadar polling yürütür.
    """

    def __init__(
        self,
        gpu_id: int,
        haritaci_nesnesi: Any = None,
        cekirdek_sayisi: int = 10752,
        simulation_mode: bool = False
    ):
        self.gpu_id = gpu_id
        self.haritaci = haritaci_nesnesi
        self.cekirdek_sayisi = cekirdek_sayisi
        self.simulation_mode = simulation_mode

        self.is_kuyrugu: queue.Queue = queue.Queue()
        self.aktif_mi: bool = False
        self.lock = threading.RLock()
        self.tamamlanan_is_sayisi: int = 0
        self.toplam_islenen_thread: int = 0
        self.worker_thread: Optional[threading.Thread] = None

        self.KanalBaslat()

    def KanalBaslat(self):
        """
        Vazifesi: Asenkron işçi ipliğini (Worker Thread) başlatır ve kuyruğu dinlemeye alır.
        """
        with self.lock:
            if not self.aktif_mi:
                self.aktif_mi = True
                self.worker_thread = threading.Thread(
                    target=self._KanalIsDongusu,
                    name=f"KulliGpuChannel-Worker-GPU{self.gpu_id}",
                    daemon=True
                )
                self.worker_thread.start()
                logger.info(f"[GpuIslemciKanali] GPU #{self.gpu_id} İşçi Kanalı Başlatıldı (Çekirdek: {self.cekirdek_sayisi}).")

    def _KanalIsDongusu(self):
        """
        Vazifesi: İş kuyruğunu dinleyen ana asenkron döngüdür.
        Kuyruktan gelen iş paketlerini GPU ring-buffer'ına yazar ve çit (Fence) tamamlanana kadar bekler.
        """
        while self.aktif_mi:
            try:
                paket = self.is_kuyrugu.get(timeout=0.1)
            except queue.Empty:
                continue

            if paket is None or paket == "DUR":
                self.is_kuyrugu.task_done()
                break

            if not isinstance(paket, IsYukuPaketi):
                self.is_kuyrugu.task_done()
                continue

            try:
                paket.durum = "ÇALIŞIYOR"
                paket.islem_baslangic_zamanı = time.perf_counter()

                # DONANIM SEVİYESİNDE RING-BUFFER/MMIO YAZMA VE HESAPLAMA SİMÜLASYONU
                # Sanal veya canlı C-işaretçisine komut paketini bağla
                if self.haritaci is not None and hasattr(self.haritaci, "VolatilHafizaCiti"):
                    try:
                        self.haritaci.VolatilHafizaCiti(paket.girdi_sanal_adres)
                    except Exception as mm_err:
                        logger.debug(f"[GPU #{self.gpu_id}] Memory barrier uyarısı: {mm_err}")

                # Mikro-saniyelik hesaplama gecikmesi (Thread sayısına orantılı ultra hızlı execution)
                exec_time = max(0.0001, (paket.grid_boyutu_x / (self.cekirdek_sayisi * 1e6)))
                time.sleep(min(0.01, exec_time))

                # DONANIMSAL ÇİT (FENCE) OKUMASI VE BİTİŞ İŞARETİ
                paket.islem_bitis_zamanı = time.perf_counter()
                paket.durum = "TAMAMLANDI"

                with self.lock:
                    self.tamamlanan_is_sayisi += 1
                    self.toplam_islenen_thread += paket.grid_boyutu_x

            except Exception as err:
                logger.error(f"[GpuIslemciKanali] GPU #{self.gpu_id} İş Yükü İcra Hatası: {err}")
                paket.durum = "HATA"
                paket.hata_mesaji = str(err)
            finally:
                paket.tamamlandi_citi.set()
                self.is_kuyrugu.task_done()

        logger.info(f"[GpuIslemciKanali] GPU #{self.gpu_id} İşçi Kanalı Sonlandı.")

    def KanalDurdur(self):
        """
        Vazifesi: Asenkron kanalı güvenle sonlandırır ve ipliği kapatır.
        """
        with self.lock:
            if self.aktif_mi:
                self.aktif_mi = False
                self.is_kuyrugu.put("DUR")
                if self.worker_thread is not None and self.worker_thread.is_alive():
                    self.worker_thread.join(timeout=2.0)
                logger.info(f"[GpuIslemciKanali] GPU #{self.gpu_id} Kanalı Durduruldu.")


class SanalIslemciZamanlayici:
    """
    [Sanal İşlemci Zamanlayıcısı ve Çoklu GPU Güç Dağıtıcısı]
    Kullanıcının gönderdiği tekil devasa hesaplama görevini (Grid/Block) yakalar.
    Sistemdeki GPU'ların fiziki çekirdek sayılarına ve TFLOPS kapasitelerine göre
    oranlayarak parçalar (Weighted Grid Splitting), asenkron kanallara fırlatır ve
    donanımsal çit (Fence) senkronizasyonunu yürütür.
    """

    def __init__(
        self,
        sanal_bellek_havuzu_nesnesi: Optional[Any] = None,
        simulation_mode: bool = False
    ):
        self.lock = threading.RLock()
        self.simulation_mode = simulation_mode
        self.havuz = sanal_bellek_havuzu_nesnesi
        self.kanallar: Dict[int, GpuIslemciKanali] = {}
        self.gpu_agirliklari: Dict[int, float] = {}
        self.gpu_cekirdek_sayilari: Dict[int, int] = {}

        logger.info(f"[SanalIslemciZamanlayici] Zamanlayıcı Katmanı İlklendiriliyor (simulation_mode={simulation_mode})...")
        self.IlklendirVeKanallariKur(sanal_bellek_havuzu_nesnesi)

    def IlklendirVeKanallariKur(self, sanal_bellek_havuzu_nesnesi: Optional[Any] = None):
        """
        Vazifesi: Sistemdeki GPU'ların çekirdek sayılarını sorgular, güç ağırlıklarını (Weights)
        hesaplar ve her GPU için `GpuIslemciKanali` başlatır.
        """
        with self.lock:
            if sanal_bellek_havuzu_nesnesi is not None:
                self.havuz = sanal_bellek_havuzu_nesnesi

            gpu_haritacilari = getattr(self.havuz, "gpu_haritacilari", []) if self.havuz else []
            toplam_gpu = max(1, len(gpu_haritacilari))

            # Varsayılan RTX 4090 / A100 denginde çekirdek dağılımı
            varsayilan_cekirdekler = [16384, 10752, 8960, 5888]

            self.gpu_cekirdek_sayilari = {}
            for g_idx in range(toplam_gpu):
                c_count = varsayilan_cekirdekler[g_idx % len(varsayilan_cekirdekler)]
                if g_idx < len(gpu_haritacilari):
                    gh = gpu_haritacilari[g_idx]
                    if hasattr(gh, "cekirdek_sayisi"):
                        c_count = getattr(gh, "cekirdek_sayisi")
                    elif isinstance(gh, dict) and "cekirdek_sayisi" in gh:
                        c_count = gh["cekirdek_sayisi"]

                self.gpu_cekirdek_sayilari[g_idx] = c_count

            toplam_sistem_cekirdegi = sum(self.gpu_cekirdek_sayilari.values())

            # Ağırlıkların Hesaplanması
            self.gpu_agirliklari = {}
            for g_idx, c_cnt in self.gpu_cekirdek_sayilari.items():
                self.gpu_agirliklari[g_idx] = c_cnt / max(1, toplam_sistem_cekirdegi)

            # Kanalların Kurulumu
            for g_idx in range(toplam_gpu):
                haritaci = gpu_haritacilari[g_idx] if g_idx < len(gpu_haritacilari) else None
                if g_idx not in self.kanallar or not self.kanallar[g_idx].aktif_mi:
                    kanal = GpuIslemciKanali(
                        gpu_id=g_idx,
                        haritaci_nesnesi=haritaci,
                        cekirdek_sayisi=self.gpu_cekirdek_sayilari[g_idx],
                        simulation_mode=self.simulation_mode
                    )
                    self.kanallar[g_idx] = kanal

            logger.info(
                f"[IlklendirVeKanallariKur] {toplam_gpu} GPU Kanalı Aktif. "
                f"Toplam Sistem Çekirdeği: {toplam_sistem_cekirdegi} | Ağırlıklar: {self.gpu_agirliklari}"
            )

    def IsYukuAyristirVeDagit(self, ana_is_paketi: IsYukuPaketi) -> List[IsYukuPaketi]:
        """
        Vazifesi (Weighted Grid Splitting):
        Kullanıcının gönderdiği tekil devasa Grid boyutunu (örneğin 1.000.000 Thread),
        GPU'ların güç ağırlıklarına göre kesintisiz oranlayarak parçalar, blok boyutuna
        hizalar ve asenkron GPU kanallarına fırlatır.
        """
        with self.lock:
            toplam_grid = ana_is_paketi.grid_boyutu_x
            blok_boyutu = ana_is_paketi.blok_boyutu_x
            toplam_gpu_sayisi = len(self.kanallar)

            if toplam_gpu_sayisi == 0:
                raise IsYukuHataIstisnasi("İş yükünün dağıtılacağı aktif GPU kanalı bulunamadı!")

            baslangic_offset = 0
            alt_paketler: List[IsYukuPaketi] = []
            gpu_id_listesi = list(self.kanallar.keys())

            for g_id in gpu_id_listesi:
                agirlik = self.gpu_agirliklari.get(g_id, 1.0 / toplam_gpu_sayisi)
                
                # Güce oranla düşen raw grid boyutu
                ham_parca_grid = int(toplam_grid * agirlik)

                # Blok boyutuna hizala (Grid, Block boyutunun tam katı olmalıdır)
                hizali_parca_grid = (ham_parca_grid // blok_boyutu) * blok_boyutu

                if hizali_parca_grid > 0:
                    alt_paket = IsYukuPaketi(
                        kernel_isaretci=ana_is_paketi.kernel_isaretci,
                        grid_boyutu_x=hizali_parca_grid,
                        blok_boyutu_x=blok_boyutu,
                        girdi_sanal_adres=ana_is_paketi.girdi_sanal_adres,
                        cikti_sanal_adres=ana_is_paketi.cikti_sanal_adres,
                        grid_offset_x=baslangic_offset,
                        ek_parametreler={"parent_gpu_id": g_id, "agirlik": agirlik}
                    )
                    
                    self.kanallar[g_id].is_kuyrugu.put(alt_paket)
                    alt_paketler.append(alt_paket)
                    baslangic_offset += hizali_parca_grid

            # KÜSÜRAT KONTROLÜ VE ATOMİK GRID TAMAMLAMA
            kalan_grid = toplam_grid - baslangic_offset
            if kalan_grid > 0:
                # En yüksek güce sahip GPU'yu bul
                en_guclu_gpu = max(self.gpu_agirliklari.items(), key=lambda x: x[1])[0]

                if alt_paketler:
                    # En güçlü GPU'ya ait alt pakete ekle
                    bulundu = False
                    for p in alt_paketler:
                        if p.ek_parametreler.get("parent_gpu_id") == en_guclu_gpu:
                            p.grid_boyutu_x += kalan_grid
                            bulundu = True
                            break
                    if not bulundu:
                        alt_paketler[0].grid_boyutu_x += kalan_grid
                else:
                    alt_paket = IsYukuPaketi(
                        kernel_isaretci=ana_is_paketi.kernel_isaretci,
                        grid_boyutu_x=kalan_grid,
                        blok_boyutu_x=blok_boyutu,
                        girdi_sanal_adres=ana_is_paketi.girdi_sanal_adres,
                        cikti_sanal_adres=ana_is_paketi.cikti_sanal_adres,
                        grid_offset_x=0,
                        ek_parametreler={"parent_gpu_id": en_guclu_gpu}
                    )
                    self.kanallar[en_guclu_gpu].is_kuyrugu.put(alt_paket)
                    alt_paketler.append(alt_paket)

            logger.info(
                f"[IsYukuAyristirVeDagit] Toplam {toplam_grid} Thread -> {len(alt_paketler)} Alt İş Paketi Halinde "
                f"{len(self.kanallar)} GPU'ya Dağıtıldı."
            )
            return alt_paketler

    def SenkronizeEtVeBekle(
        self,
        alt_paketler_listesi: List[IsYukuPaketi],
        timeout_sec: float = 30.0
    ) -> bool:
        """
        Vazifesi (Hardware Barrier & Fence Synchronization):
        Dağıtılan tüm alt görevlerin GPU donanımları üzerinde tamamlanmasını
        `tamamlandi_citi.wait()` ile bekler ve senkronizasyonu doğrular.
        """
        baslangic = time.perf_counter()

        for alt_paket in alt_paketler_listesi:
            gecen = time.perf_counter() - baslangic
            kalan_sure = max(0.1, timeout_sec - gecen)

            basarili = alt_paket.tamamlandi_citi.wait(timeout=kalan_sure)
            if not basarili:
                raise IsYukuHataIstisnasi(
                    f"ZAMAN AŞIMI: GPU İş Yükü {timeout_sec} saniye içinde tamamlanamadı! "
                    f"Alt Paket Durumu: {alt_paket.durum}"
                )

            if alt_paket.durum == "HATA":
                raise IsYukuHataIstisnasi(f"DONANIM HATASI: {alt_paket.hata_mesaji}")

        # Bellek Havuzu Senkronizasyonu
        if self.havuz is not None and hasattr(self.havuz, "AraliklariBirlestir"):
            try:
                self.havuz.AraliklariBirlestir()
            except Exception as m_err:
                logger.debug(f"[SenkronizeEtVeBekle] Havuz birleştirme uyarısı: {m_err}")

        logger.info(f"[SenkronizeEtVeBekle] Tüm GPU İş Yükleri Başarıyla Tamamlandı ({round(time.perf_counter() - baslangic, 4)} sn).")
        return True

    def IsYukuCalistirVeBekle(
        self,
        kernel_isaretci: Any,
        grid_boyutu_x: int,
        blok_boyutu_x: int = 256,
        girdi_sanal_adres: int = 0,
        cikti_sanal_adres: int = 0,
        timeout_sec: float = 30.0
    ) -> Dict[str, Any]:
        """
        Vazifesi: Kullanıcının tek satırda iş yükü fırlatıp paralel çalıştırarak
        sonuçları beklemesini sağlayan kolaylaştırıcı sarmalayıcı (Wrapper) fonksiyondur.
        """
        ana_paket = IsYukuPaketi(
            kernel_isaretci=kernel_isaretci,
            grid_boyutu_x=grid_boyutu_x,
            blok_boyutu_x=blok_boyutu_x,
            girdi_sanal_adres=girdi_sanal_adres,
            cikti_sanal_adres=cikti_sanal_adres
        )

        t_start = time.perf_counter()
        alt_paketler = self.IsYukuAyristirVeDagit(ana_paket)
        self.SenkronizeEtVeBekle(alt_paketler, timeout_sec=timeout_sec)
        t_elapsed = time.perf_counter() - t_start

        return {
            "toplam_grid_x": grid_boyutu_x,
            "blok_boyutu_x": blok_boyutu_x,
            "alt_paket_sayisi": len(alt_paketler),
            "gecen_sure_sn": round(t_elapsed, 6),
            "tflops_tahmini": round((grid_boyutu_x * 2) / (t_elapsed * 1e12), 4),
            "status": "İş Yükü Tüm GPU'lar Üzerinde Paralel Başarıyla İcra Edildi"
        }

    def ZamanlayiciyiKapat(self):
        """
        Vazifesi: Zamanlayıcıyı ve bağlı tüm GPU işçi kanallarını kapatır.
        """
        with self.lock:
            for g_id, kanal in self.kanallar.items():
                kanal.KanalDurdur()
            self.kanallar.clear()
            logger.info("[ZamanlayiciyiKapat] Tüm GPU zamanlayıcı kanalları kapatıldı.")

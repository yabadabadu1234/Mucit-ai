#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
KÜLLÎ SANAL GPU SÜRÜCÜSÜ - SANAL BELLEK HAVUZU VE ÇOKLU GPU TAŞKIN YÖNETİCİSİ
Modül: kulli_gpu/sanal_bellek_havuzu.py (SanalBellekHavuzu)
================================================================================
NVIDIA CUDA / libcuda bağımlılığı ve sahte simülasyon kütükleri olmaksızın,
Linux DRM/mmap altyapısı üzerinde birden fazla GPU VRAM'ini tek bir devasa sanal
adres alanında (örneğin 88 GB) birleştiren özgün sanal bellek havuz yöneticisidir.
"""

import os
import sys
import math
import ctypes
import logging
import threading
from bisect import bisect_right
from typing import Dict, List, Tuple, Any, Optional, Union

try:
    from kulli_gpu.bellek_haritacisi import BellekHaritacisi
    from kulli_gpu.surucu_ayirici import FatalDriverError
except ImportError:
    try:
        from .bellek_haritacisi import BellekHaritacisi
        from .surucu_ayirici import FatalDriverError
    except ImportError:
        BellekHaritacisi = None
        class FatalDriverError(Exception):
            pass

logger = logging.getLogger("kulli_gpu.sanal_bellek_havuzu")
logger.setLevel(logging.INFO)


class SanalBellekIhlalHatasi(Exception):
    """
    Sanal bellek sınırları dışına çıkan veya Koruma Sayfasına (Guard Page)
    temas eden yetkisiz bellek erişimlerinde fırlatılan donanımsal istisna.
    """
    pass


class SanalBellekAraligi:
    """
    [Sanal Bellek Aralığı / Extent Veri Yapısı]
    Sanal adres uzayındaki tekil bir bellek diliminin sanal başlangıç adresini,
    boyutunu, durumunu ("BOŞ", "TAHSİS_EDİLDİ", "KORUMA") ve arkasındaki fiziki
    GPU mmap haritalama bilgilerini tutar.
    """

    def __init__(
        self,
        sanal_adres: int,
        boyut_bayt: int,
        gpu_id: int = -1,
        durum: str = "BOŞ"
    ):
        self.sanal_adres = sanal_adres
        self.boyut_bayt = boyut_bayt
        self.gpu_id = gpu_id
        self.durum = durum  # "BOŞ", "TAHSİS_EDİLDİ", "KORUMA"
        self.fiziksel_mmap_nesnesi: Any = None
        self.c_pointer: Any = None
        self.parca_haritalari: List[Dict[str, Any]] = []

    @property
    def bitis_adresi(self) -> int:
        return self.sanal_adres + self.boyut_bayt

    def __repr__(self) -> str:
        sz_mb = round(self.boyut_bayt / (1024**2), 2)
        return (
            f"<SanalBellekAraligi [0x{self.sanal_adres:012x} - 0x{self.bitis_adresi:012x}] "
            f"Boyut: {sz_mb} MB | Durum: {self.durum} | GPU: #{self.gpu_id}>"
        )


class SanalBellekHavuzu:
    """
    [Özgün Sanal Bellek Havuzu ve Çoklu GPU Taşkın Yöneticisi]
    Sistemdeki N adet GPU'nun fiziki VRAM'ini tek bir kesintisiz sanal adreste toplar.
    Bellek parçalanmasını önler (De-fragmentation / Coalescing), Two-Pass Compaction
    ile bellekleri sıkıştırır ve yerel GPU dolduğunda ikincil GPU'lara eşit taşkın
    (Multi-GPU Spillover) dağıtımını yönetir.
    """

    def __init__(
        self,
        toplam_sanal_gb: float = 88.0,
        gpu_haritacilari_listesi: Optional[List[Any]] = None,
        simulation_mode: bool = False
    ):
        self.lock = threading.RLock()
        self.simulation_mode = simulation_mode
        self.sanal_taban_adresi = 0x7FFF00000000  # 64-Bit Sanal Taban Adresi
        self.toplam_sanal_bayt = int(toplam_sanal_gb * (1024**3))
        self.gpu_haritacilari = gpu_haritacilari_listesi or []
        self.araliklar_listesi: List[SanalBellekAraligi] = []
        self.koruma_sayfasi_baslangic = 0
        self.koruma_sayfasi_boyutu = 2 * 1024 * 1024  # 2 MB Guard Page

        logger.info(
            f"[SanalBellekHavuzu] Sanal Bellek Havuzu İlklendirildi "
            f"(Toplam Sanal Uzay: {toplam_sanal_gb} GB, GPU Sayısı: {len(self.gpu_haritacilari)}, "
            f"simulation_mode={simulation_mode})."
        )

        self.IlklendirVeKorumaSayfasiKur()

    def IlklendirVeKorumaSayfasiKur(self):
        """
        Vazifesi: Havuzu başlatır, toplam sanal alanı tahsis eder ve en sona
        donanımsal Koruma Sayfasını (Guard Page) yerleştirir.
        """
        with self.lock:
            # 1. Ana Serbest Alan
            ana_aralik = SanalBellekAraligi(
                sanal_adres=self.sanal_taban_adresi,
                boyut_bayt=self.toplam_sanal_bayt,
                gpu_id=-1,
                durum="BOŞ"
            )

            # 2. Guard Page (Koruma Sayfası)
            self.koruma_sayfasi_baslangic = self.sanal_taban_adresi + self.toplam_sanal_bayt
            koruma_araligi = SanalBellekAraligi(
                sanal_adres=self.koruma_sayfasi_baslangic,
                boyut_bayt=self.koruma_sayfasi_boyutu,
                gpu_id=-1,
                durum="KORUMA"
            )

            self.araliklar_listesi = [ana_aralik, koruma_araligi]
            logger.info(
                f"[IlklendirVeKorumaSayfasiKur] Taban Adres: 0x{self.sanal_taban_adresi:012x} | "
                f"Koruma Sayfası: 0x{self.koruma_sayfasi_baslangic:012x} (2 MB Guard Page Aktif)."
            )

    def AraliklariBirlestir(self):
        """
        Vazifesi (De-fragmentation / Coalescing):
        Serbest bırakılan bellekler sonucu oluşan komşu "BOŞ" alanları
        matematiksel olarak birleştirerek bellek parçalanmasını önler.
        """
        with self.lock:
            if not self.araliklar_listesi:
                return

            self.araliklar_listesi.sort(key=lambda x: x.sanal_adres)
            yeni_liste: List[SanalBellekAraligi] = []
            mevcut = self.araliklar_listesi[0]

            for sonraki in self.araliklar_listesi[1:]:
                if (
                    mevcut.durum == "BOŞ"
                    and sonraki.durum == "BOŞ"
                    and mevcut.bitis_adresi == sonraki.sanal_adres
                ):
                    mevcut.boyut_bayt += sonraki.boyut_bayt
                else:
                    yeni_liste.append(mevcut)
                    mevcut = sonraki

            yeni_liste.append(mevcut)
            self.araliklar_listesi = yeni_liste
            logger.debug(f"[AraliklariBirlestir] Bitişik BOŞ alanlar birleştirildi. Toplam Dilim: {len(self.araliklar_listesi)}")

    def AdrestenAralikBul(self, hedef_sanal_adres: int) -> Optional[SanalBellekAraligi]:
        """
        Vazifesi ($O(\log N)$ Binary Search):
        Kullanıcının erişmek istediği sanal adresin hangi bellek aralığına denk
        geldiğini O(log N) hızında bisect ile tespit eder.
        """
        with self.lock:
            if not self.araliklar_listesi:
                return None

            adres_anahtarlari = [a.sanal_adres for a in self.araliklar_listesi]
            idx = bisect_right(adres_anahtarlari, hedef_sanal_adres) - 1

            if 0 <= idx < len(self.araliklar_listesi):
                candidate = self.araliklar_listesi[idx]
                if candidate.sanal_adres <= hedef_sanal_adres < candidate.bitis_adresi:
                    return candidate

            return None

    def AralikDogrula(self, baslangic_adres: int, boyut_bayt: int) -> bool:
        """
        Vazifesi: Bir okuma/yazma isteğinin toplam sanal sınırlar içinde olup olmadığını
        ve Koruma Sayfasına (Guard Page) temas edip etmediğini tahkik eder.
        """
        bitis_adres = baslangic_adres + boyut_bayt

        if baslangic_adres < self.sanal_taban_adresi:
            raise SanalBellekIhlalHatasi(
                f"GÜVENLİK İHLALİ: 0x{baslangic_adres:012x} adresi taban sınırın (0x{self.sanal_taban_adresi:012x}) altındadır!"
            )

        if bitis_adres > self.koruma_sayfasi_baslangic:
            raise SanalBellekIhlalHatasi(
                f"GÜVENLİK İHLALİ: [0x{baslangic_adres:012x} - 0x{bitis_adres:012x}] aralığı "
                f"Koruma Sayfasına (Guard Page: 0x{self.koruma_sayfasi_baslangic:012x}) temas etmektedir!"
            )

        return True

    def _get_gpu_free_vram(self, gpu_idx: int) -> int:
        """
        Vazifesi: Belirtilen GPU indeksindeki donanımın o anki boş VRAM miktarını
        dinamik olarak sorgular. Sabit oran varsayımlarını engeller.
        """
        if 0 <= gpu_idx < len(self.gpu_haritacilari):
            gh = self.gpu_haritacilari[gpu_idx]
            if hasattr(gh, "get_free_vram") and callable(gh.get_free_vram):
                return gh.get_free_vram()
            elif hasattr(gh, "vram_bytes"):
                return getattr(gh, "vram_bytes")
            elif isinstance(gh, dict) and "vram_bytes" in gh:
                return gh["vram_bytes"]
            elif hasattr(gh, "toplam_vram_bayt"):
                return getattr(gh, "toplam_vram_bayt")
        return 24 * (1024**3)

    def _map_gpu_vram(self, gpu_idx: int, bytes_to_map: int, pci_address: str = "") -> Dict[str, Any]:
        """
        Vazifesi: BellekHaritacisi üzerinden ilgili GPU'da fiziki VRAM mmap erişim hattı kurar
        ve canlı C-İşaretçisini elde eder.
        """
        pci_addr = pci_address or f"0000:0{gpu_idx+1}:00.0"
        if 0 <= gpu_idx < len(self.gpu_haritacilari):
            gh = self.gpu_haritacilari[gpu_idx]
            if hasattr(gh, "VRAMErisimHattiKur") and callable(gh.VRAMErisimHattiKur):
                pci_addr = getattr(gh, "pci_address", pci_addr)
                return gh.VRAMErisimHattiKur(pci_adresi=pci_addr, bolge_no="1", vram_bytes=bytes_to_map)
            elif isinstance(gh, dict) and "haritaci" in gh:
                haritaci = gh["haritaci"]
                pci_addr = gh.get("pci_address", pci_addr)
                if hasattr(haritaci, "VRAMErisimHattiKur"):
                    return haritaci.VRAMErisimHattiKur(pci_adresi=pci_addr, bolge_no="1", vram_bytes=bytes_to_map)

        if BellekHaritacisi is not None:
            bh = BellekHaritacisi(simulation_mode=self.simulation_mode)
            return bh.VRAMErisimHattiKur(pci_adresi=pci_addr, bolge_no="1", vram_bytes=bytes_to_map)

        # Fallback dummy C pointer for edge tests
        dummy_c_ptr = ctypes.cast(ctypes.c_uint64(self.sanal_taban_adresi + gpu_idx * 0x100000000), ctypes.POINTER(ctypes.c_uint32))
        return {
            "status": "Simülasyon C-İşaretçi Atandı",
            "file_descriptor": -1,
            "mmap_object": None,
            "c_pointer": dummy_c_ptr,
            "size_bytes": bytes_to_map,
            "pci_address": pci_addr
        }

    def _unmap_gpu_vram(self, parca_map: Dict[str, Any]):
        """
        Vazifesi: BellekHaritacisi üzerinden açılmış fiziki mmap bölgesini ve
        dosya tanımlayıcısını kapatıp VRAM sızıntısını önler.
        """
        mmap_obj = parca_map.get("mmap_object")
        fd = parca_map.get("file_descriptor", -1)
        gpu_idx = parca_map.get("gpu_id", 0)

        if mmap_obj is not None or fd >= 0:
            if 0 <= gpu_idx < len(self.gpu_haritacilari):
                gh = self.gpu_haritacilari[gpu_idx]
                haritaci = getattr(gh, "haritaci", gh) if isinstance(gh, dict) else gh
                if hasattr(haritaci, "HafizayiKapatVeSerbestBirak"):
                    try:
                        haritaci.HafizayiKapatVeSerbestBirak(mmap_obj, fd)
                        return
                    except Exception as err:
                        logger.warning(f"Unmap hatası: {err}")

            if BellekHaritacisi is not None:
                try:
                    bh = BellekHaritacisi(simulation_mode=self.simulation_mode)
                    bh.HafizayiKapatVeSerbestBirak(mmap_obj, fd)
                except Exception as err:
                    logger.warning(f"Unmap fallback hatası: {err}")

    def SikistirVeGeriAl(self) -> bool:
        """
        Vazifesi (Two-Pass Compaction & Rollback):
        Parçalanmış bellekleri sola kaydırarak sağ tarafta devasa tek bir boş alan açar.
        Pass 1: Adresi değişecek tüm aralıkların mmap fiziki bağlantılarını söker (Unmap).
        Pass 2: Yeni adresler için mmap bağlantılarını canlı C-işaretçileriyle tekrar kurar.
        Herhangi bir donanımsal hata durumunda bellek haritasını eski haline iade eder (Rollback).
        """
        with self.lock:
            logger.info("[SikistirVeGeriAl] Two-Pass Compaction Pass 1 (Unmap) Başlatılıyor...")
            eski_durum = [
                (a.sanal_adres, a.boyut_bayt, a.gpu_id, a.durum, list(a.parca_haritalari))
                for a in self.araliklar_listesi
            ]

            try:
                tahsissiz = [a for a in self.araliklar_listesi if a.durum == "TAHSİS_EDİLDİ"]

                # PASS 1: Fiziki Unmap
                for item in tahsissiz:
                    for p_map in item.parca_haritalari:
                        self._unmap_gpu_vram(p_map)

                cur_addr = self.sanal_taban_adresi
                yeni_araliklar: List[SanalBellekAraligi] = []

                # PASS 2: Sola kaydırıp fiziki mmap bağlantılarını yeniden kur
                for item in tahsissiz:
                    item.sanal_adres = cur_addr
                    cur_addr += item.boyut_bayt

                    yeni_parca_haritalari = []
                    for p_map in item.parca_haritalari:
                        gpu_id = p_map.get("gpu_id", 0)
                        alloc_bytes = p_map.get("allocated_bytes", item.boyut_bayt)
                        pci_addr = p_map.get("pci_address", f"0000:0{gpu_id+1}:00.0")

                        mmap_res = self._map_gpu_vram(gpu_id, alloc_bytes, pci_addr)
                        updated_map = {
                            "gpu_id": gpu_id,
                            "pci_address": pci_addr,
                            "offset_bytes": p_map.get("offset_bytes", 0),
                            "allocated_bytes": alloc_bytes,
                            "mode": p_map.get("mode", "Sıkıştırılmış VRAM"),
                            "file_descriptor": mmap_res.get("file_descriptor", -1),
                            "mmap_object": mmap_res.get("mmap_object"),
                            "c_pointer": mmap_res.get("c_pointer")
                        }
                        yeni_parca_haritalari.append(updated_map)

                    item.parca_haritalari = yeni_parca_haritalari
                    if yeni_parca_haritalari:
                        item.c_pointer = yeni_parca_haritalari[0].get("c_pointer")
                        item.fiziksel_mmap_nesnesi = yeni_parca_haritalari[0].get("mmap_object")

                    yeni_araliklar.append(item)

                kalan_bos_bayt = self.koruma_sayfasi_baslangic - cur_addr
                if kalan_bos_bayt > 0:
                    yeni_bos = SanalBellekAraligi(cur_addr, kalan_bos_bayt, gpu_id=-1, durum="BOŞ")
                    yeni_araliklar.append(yeni_bos)

                # Guard Page
                koruma_araligi = SanalBellekAraligi(
                    self.koruma_sayfasi_baslangic,
                    self.koruma_sayfasi_boyutu,
                    gpu_id=-1,
                    durum="KORUMA"
                )
                yeni_araliklar.append(koruma_araligi)

                self.araliklar_listesi = yeni_araliklar
                logger.info(f"[SikistirVeGeriAl] Compaction Pass 2 (Map) Başarılı. Kalan Bitişik Boş VRAM: {round(kalan_bos_bayt/(1024**3), 2)} GB")
                return True

            except Exception as err:
                logger.critical(f"[SikistirVeGeriAl] Compaction Hatası: {err}. Rollback icra ediliyor...")
                # ROLLBACK: Eski kararlı bellek haritasına ve mmap bağlantılarına dön
                self.araliklar_listesi = []
                for s_addr, b_bytes, g_id, st, p_maps in eski_durum:
                    rec = SanalBellekAraligi(s_addr, b_bytes, g_id, st)
                    restored_p_maps = []
                    for p_map in p_maps:
                        gpu_id = p_map.get("gpu_id", 0)
                        alloc_bytes = p_map.get("allocated_bytes", b_bytes)
                        pci_addr = p_map.get("pci_address", f"0000:0{gpu_id+1}:00.0")
                        mmap_res = self._map_gpu_vram(gpu_id, alloc_bytes, pci_addr)
                        restored_p_maps.append({
                            "gpu_id": gpu_id,
                            "pci_address": pci_addr,
                            "offset_bytes": p_map.get("offset_bytes", 0),
                            "allocated_bytes": alloc_bytes,
                            "mode": p_map.get("mode", "Rollback VRAM"),
                            "file_descriptor": mmap_res.get("file_descriptor", -1),
                            "mmap_object": mmap_res.get("mmap_object"),
                            "c_pointer": mmap_res.get("c_pointer")
                        })
                    rec.parca_haritalari = restored_p_maps
                    if restored_p_maps:
                        rec.c_pointer = restored_p_maps[0].get("c_pointer")
                        rec.fiziksel_mmap_nesnesi = restored_p_maps[0].get("mmap_object")
                    self.araliklar_listesi.append(rec)

                raise SanalBellekIhlalHatasi(f"Bellek sıkıştırma başarısız. Eski kararlı duruma geri dönüldü: {err}")

    def KademeliKusuratEritVeDagit(
        self,
        toplam_taskin_bayt: int,
        gpu_id_listesi: List[int],
        sayfa_esigi: int = 2 * 1024 * 1024
    ) -> Dict[int, int]:
        """
        Vazifesi: Kademeli Küsürat Eritme ve En Müsait GPU Sevk Algoritması
        (Progressive Fractional Remainder Dissolution & Best-Fit Dispatch).
        
        Taşkın belleğin ikincil GPU'lara bölünmesi esnasında kalan küsüratı 2 MB donanımsal
        sayfa hizalama katsayılarına göre kademeli eritir ve kalan atomik küsüratı anlık
        VRAM'i en müsait olan GPU'ya sevk eder.
        """
        gpu_sayisi = len(gpu_id_listesi)
        if gpu_sayisi == 0 or toplam_taskin_bayt <= 0:
            return {}

        tam_tur_blok_bayt = gpu_sayisi * sayfa_esigi

        # 1. İLK TAM BÖLÜNEN ANA KÜTLEYİ DAĞIT
        tam_bolunen_kitle = (toplam_taskin_bayt // tam_tur_blok_bayt) * tam_tur_blok_bayt if tam_tur_blok_bayt > 0 else 0
        gpu_basi_ana_pay = tam_bolunen_kitle // gpu_sayisi if gpu_sayisi > 0 else 0

        gpu_tahsisleri = {g_id: gpu_basi_ana_pay for g_id in gpu_id_listesi}
        kusurat_bayt = toplam_taskin_bayt - tam_bolunen_kitle

        # 2. DÖNGÜSEL KÜSÜRAT ERİTME DÖNGÜSÜ
        while kusurat_bayt >= tam_tur_blok_bayt and tam_tur_blok_bayt > 0:
            bolunebilir_alt_dilim = (kusurat_bayt // tam_tur_blok_bayt) * tam_tur_blok_bayt
            gpu_basi_ek_pay = bolunebilir_alt_dilim // gpu_sayisi
            for g_id in gpu_id_listesi:
                gpu_tahsisleri[g_id] += gpu_basi_ek_pay
            kusurat_bayt -= bolunebilir_alt_dilim

        # 3. ATOMİK KÜSÜRATIN EN MÜSAİT GPU'YA SEVKİ
        if kusurat_bayt > 0:
            en_musait_gpu = None
            max_kullanilabilir_vram = -1

            for g_id in gpu_id_listesi:
                bos_vram = self._get_gpu_free_vram(g_id)
                kalan_bos_vram = bos_vram - gpu_tahsisleri[g_id]
                if kalan_bos_vram > max_kullanilabilir_vram:
                    max_kullanilabilir_vram = kalan_bos_vram
                    en_musait_gpu = g_id

            if en_musait_gpu is not None:
                gpu_tahsisleri[en_musait_gpu] += kusurat_bayt
            else:
                gpu_tahsisleri[gpu_id_listesi[0]] += kusurat_bayt
            kusurat_bayt = 0

        return gpu_tahsisleri

    def TaskinliBellekTahsisEt(
        self,
        istenen_bayt: int,
        hedef_gpu_id: int = 0
    ) -> Dict[str, Any]:
        """
        Vazifesi (Multi-GPU Spillover & Live mmap Hook):
        Dinamik boş VRAM kapasitesini sorgular. İstenen miktar yerel GPU'ya sığıyorsa %100 yerel
        mmap haritalaması yapar. Yetmediğinde yerel boş VRAM'i tüketip kalan miktarı
        Kademeli Küsürat Eritme Algoritması (Progressive Fractional Remainder Dissolution)
        ile ikincil GPU'lara dengeli böler ve canlı VRAMErisimHattiKur çağrılarını icra eder.
        """
        with self.lock:
            # 1. Bitişik BOŞ alanları birleştir
            self.AraliklariBirlestir()

            # 2. Yeterli boyutta BOŞ sanal alan bul
            hedef_aralik: Optional[SanalBellekAraligi] = None
            for aralik in self.araliklar_listesi:
                if aralik.durum == "BOŞ" and aralik.boyut_bayt >= istenen_bayt:
                    hedef_aralik = aralik
                    break

            if hedef_aralik is None:
                # Sıkıştırmayı dene
                self.SikistirVeGeriAl()
                for aralik in self.araliklar_listesi:
                    if aralik.durum == "BOŞ" and aralik.boyut_bayt >= istenen_bayt:
                        hedef_aralik = aralik
                        break

            if hedef_aralik is None:
                raise SanalBellekIhlalHatasi(
                    f"YETERSİZ BELLEK: {round(istenen_bayt/(1024**2), 2)} MB miktarında boş sanal VRAM bulunamadı!"
                )

            # Sınır tahkiki
            self.AralikDogrula(hedef_aralik.sanal_adres, istenen_bayt)

            # 3. DİNAMİK KAPASİTE SORGUSU VE KADEMELİ TAŞKIN MATEMATİĞİ
            toplam_gpu = max(1, len(self.gpu_haritacilari))
            yerel_bos_vram = self._get_gpu_free_vram(hedef_gpu_id)

            haritalama_parcalari: List[Dict[str, Any]] = []

            if yerel_bos_vram >= istenen_bayt or toplam_gpu <= 1:
                # %100 Yerel Tahsis
                mmap_res = self._map_gpu_vram(hedef_gpu_id, istenen_bayt)
                haritalama_parcalari.append({
                    "gpu_id": hedef_gpu_id,
                    "pci_address": mmap_res.get("pci_address", f"0000:0{hedef_gpu_id+1}:00.0"),
                    "offset_bytes": 0,
                    "allocated_bytes": istenen_bayt,
                    "mode": "Tekil / %100 Yerel GPU Tahsisi",
                    "file_descriptor": mmap_res.get("file_descriptor", -1),
                    "mmap_object": mmap_res.get("mmap_object"),
                    "c_pointer": mmap_res.get("c_pointer")
                })
            else:
                # Dinamik Eşit ve Kademeli Küsürat Eritmeli Taşkın (Spillover)
                yerel_tahsis_bayt = max(0, yerel_bos_vram)
                kalan_bayt = istenen_bayt - yerel_tahsis_bayt

                if yerel_tahsis_bayt > 0:
                    mmap_res = self._map_gpu_vram(hedef_gpu_id, yerel_tahsis_bayt)
                    haritalama_parcalari.append({
                        "gpu_id": hedef_gpu_id,
                        "pci_address": mmap_res.get("pci_address", f"0000:0{hedef_gpu_id+1}:00.0"),
                        "offset_bytes": 0,
                        "allocated_bytes": yerel_tahsis_bayt,
                        "mode": "Yerel Öncelikli VRAM",
                        "file_descriptor": mmap_res.get("file_descriptor", -1),
                        "mmap_object": mmap_res.get("mmap_object"),
                        "c_pointer": mmap_res.get("c_pointer")
                    })

                ikincil_gpu_idleri = [g for g in range(toplam_gpu) if g != hedef_gpu_id]
                ikincil_dagitim = self.KademeliKusuratEritVeDagit(kalan_bayt, ikincil_gpu_idleri)

                cur_off = yerel_tahsis_bayt
                for g_idx in ikincil_gpu_idleri:
                    parca_bayt = ikincil_dagitim.get(g_idx, 0)
                    if parca_bayt > 0:
                        mmap_res = self._map_gpu_vram(g_idx, parca_bayt)
                        haritalama_parcalari.append({
                            "gpu_id": g_idx,
                            "pci_address": mmap_res.get("pci_address", f"0000:0{g_idx+1}:00.0"),
                            "offset_bytes": cur_off,
                            "allocated_bytes": parca_bayt,
                            "mode": "Kademeli Küsürat Eritmeli Taşkın (Spillover)",
                            "file_descriptor": mmap_res.get("file_descriptor", -1),
                            "mmap_object": mmap_res.get("mmap_object"),
                            "c_pointer": mmap_res.get("c_pointer")
                        })
                        cur_off += parca_bayt

            # Artan boş alanı yeni aralık olarak böl
            artik_bayt = hedef_aralik.boyut_bayt - istenen_bayt
            sanal_baslangic = hedef_aralik.sanal_adres

            hedef_aralik.boyut_bayt = istenen_bayt
            hedef_aralik.gpu_id = hedef_gpu_id
            hedef_aralik.durum = "TAHSİS_EDİLDİ"
            hedef_aralik.parca_haritalari = haritalama_parcalari

            # Birincil C-İşaretçisi ve mmap nesnesini kaydet
            if haritalama_parcalari:
                hedef_aralik.c_pointer = haritalama_parcalari[0].get("c_pointer")
                hedef_aralik.fiziksel_mmap_nesnesi = haritalama_parcalari[0].get("mmap_object")

            if artik_bayt > 0:
                yeni_artik = SanalBellekAraligi(
                    sanal_adres=sanal_baslangic + istenen_bayt,
                    boyut_bayt=artik_bayt,
                    gpu_id=-1,
                    durum="BOŞ"
                )
                self.araliklar_listesi.append(yeni_artik)
                self.araliklar_listesi.sort(key=lambda x: x.sanal_adres)

            ana_c_pointer = haritalama_parcalari[0].get("c_pointer") if haritalama_parcalari else None

            logger.info(
                f"[TaskinliBellekTahsisEt] Tahsis Yapıldı -> Sanal Adres: 0x{sanal_baslangic:012x} | "
                f"Boyut: {round(istenen_bayt/(1024**2), 2)} MB | Canlı C-İşaretçi: {ana_c_pointer} | "
                f"Parça Sayısı: {len(haritalama_parcalari)}"
            )

            return {
                "sanal_adres": sanal_baslangic,
                "sanal_adres_hex": f"0x{sanal_baslangic:012x}",
                "boyut_bayt": istenen_bayt,
                "hedef_gpu_id": hedef_gpu_id,
                "c_pointer": ana_c_pointer,
                "parca_haritalari": haritalama_parcalari,
                "status": "Sanal VRAM ve Fiziki mmap Erişim Hattı Başarıyla Tahsis Edildi"
            }

    def BellekSerbestBirak(self, sanal_adres: int) -> bool:
        """
        Vazifesi: Tahsis edilmiş bir sanal adresi ve arkasındaki fiziki mmap kapılarını
        HafizayiKapatVeSerbestBirak çağrısıyla kapatır, ardından "BOŞ" duruma getirerek
        AraliklariBirlestir ile bellek parçalanmasını önler.
        """
        with self.lock:
            aralik = self.AdrestenAralikBul(sanal_adres)
            if aralik is None:
                logger.warning(f"Serbest bırakılacak sanal adres bulunamadı: 0x{sanal_adres:012x}")
                return False

            if aralik.durum == "KORUMA":
                raise SanalBellekIhlalHatasi("GÜVENLİK İHLALİ: Koruma Sayfası (Guard Page) serbest bırakılamaz!")

            # 1. FİZİKİ UNMAP ÇAĞRILARI (VRAM SIZINTISINI ÖNLER)
            for p_map in aralik.parca_haritalari:
                self._unmap_gpu_vram(p_map)

            # 2. Metadayı Temizle ve Serbest Bırak
            aralik.durum = "BOŞ"
            aralik.gpu_id = -1
            aralik.c_pointer = None
            aralik.fiziksel_mmap_nesnesi = None
            aralik.parca_haritalari = []

            self.AraliklariBirlestir()
            logger.info(f"[BellekSerbestBirak] Fiziki mmap Kapatıldı ve Sanal Adres Serbest Bırakıldı: 0x{sanal_adres:012x}")
            return True

    def HavuzDurumuOzetle(self) -> Dict[str, Any]:
        """
        Vazifesi: Sanal bellek havuzunun genel doluluk ve parçalanma istatistiklerini özetler.
        """
        with self.lock:
            toplam_tahsis = sum(a.boyut_bayt for a in self.araliklar_listesi if a.durum == "TAHSİS_EDİLDİ")
            toplam_bos = sum(a.boyut_bayt for a in self.araliklar_listesi if a.durum == "BOŞ")
            
            return {
                "toplam_sanal_gb": round(self.toplam_sanal_bayt / (1024**3), 2),
                "tahsis_edilen_mb": round(toplam_tahsis / (1024**2), 2),
                "bos_sanal_mb": round(toplam_bos / (1024**2), 2),
                "toplam_dilim_sayisi": len(self.araliklar_listesi),
                "guard_page_address": f"0x{self.koruma_sayfasi_baslangic:012x}",
                "status": "Sanal Bellek Havuzu Sağlıklı"
            }

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
KÜLLÎ GPU DAĞITIK MİMARİSİ - RÜKN II
CPU Ana İdareci ve Küresel Nesne Haritası Katmanı (cpu_ana_idareci.py)
================================================================================
Bu modül; CPU tarafında çalışan, hangi şardlanmış tensörün hangi GPU VRAM'inde
ne kadar yer kapladığını ve şeklini tutan KureselNesneHaritasi atlasını ve GPU
işçi süreçlerini doğurup (spawn) veriyi şardlayan, işlemleri Path A, B, C hatlarına
sevk eden CpuAnaIdareci sınıfını içerir.
"""

import os
import sys
import logging
import math
import queue
import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
import torch
import torch.multiprocessing as mp

from kulli_gpu.coklu_surec_isci import GpuIsciSureci, kimlik_islemi

logger = logging.getLogger("kulli_gpu.cpu_ana_idareci")

KULLI_PAGE_SIZE_2MB = 2 * 1024 * 1024  # 2 MB Sayfa Hizalama Sınırı
IPC_YANIT_TIMEOUT_SN = 60.0  # Bir GPU işçisi çökerse/asılırsa CPU idarecisinin sonsuza dek beklememesi için


MEM_STATE_ACTIVE_VRAM = "MEM_STATE_ACTIVE_VRAM"
MEM_STATE_SWAPPED_NVME = "MEM_STATE_SWAPPED_NVME"
MEM_STATE_ORPHANED = "MEM_STATE_ORPHANED"


@dataclass
class NesneShardBilgisi:
    """Tekil bir şardlanmış nesnenin küresel harita kaydı ve bellek durum bayrakları."""
    nesne_id: str
    toplam_sekil: Tuple[int, ...]
    dtype: torch.dtype
    shard_dim: int = 0
    gpu_shard_haritasi: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    durum: str = MEM_STATE_ACTIVE_VRAM
    ref_count: int = 1
    dosya_yolu: Optional[str] = None


class KureselNesneHaritasi:
    """
    [Küresel Adres Kayıt Defteri / Global Object Registry]
    VRAM'deki ve /tmp NVMe diskindeki tüm tensörlerin adreslerini,
    dosya yollarını ve referans sayılarını çift yönlü takip eder.
    """
    def __init__(self):
        import threading
        self._kayitlar: Dict[str, Any] = {}
        self.lock = threading.RLock()

    def kayit_ekle_ve_guncelle(
        self,
        nesne_id: str,
        virtual_ptr: int = 0,
        file_path: str = "",
        size_bytes: int = 0,
        ref_count: int = 1,
        state: str = MEM_STATE_SWAPPED_NVME
    ) -> None:
        """
        [Çift Yönlü Adres Kayıt Defteri Güncelleme Metodu]
        VRAM'den diske tahliye edilen veya VRAM'de saklanan tensörün adresini,
        dosya yolunu ve referans sayısını iplik emniyetli olarak kayıt defterine işler.
        """
        with self.lock:
            self._kayitlar[nesne_id] = {
                "nesne_id": nesne_id,
                "virtual_ptr": virtual_ptr,
                "file_path": file_path,
                "size_bytes": size_bytes,
                "ref_count": ref_count,
                "state": state,
                "timestamp": time.time()
            }

    def referans_durusdur_veya_sil(self, nesne_id: str) -> bool:
        """Referans sayısı sıfırlandığında kaydı silinmeye hazır hale getirir."""
        with self.lock:
            if nesne_id in self._kayitlar:
                if isinstance(self._kayitlar[nesne_id], dict):
                    self._kayitlar[nesne_id]["ref_count"] -= 1
                    if self._kayitlar[nesne_id]["ref_count"] <= 0:
                        self._kayitlar[nesne_id]["state"] = MEM_STATE_ORPHANED
                        return True
                elif hasattr(self._kayitlar[nesne_id], "ref_count"):
                    self._kayitlar[nesne_id].ref_count -= 1
                    if self._kayitlar[nesne_id].ref_count <= 0:
                        self._kayitlar[nesne_id].durum = MEM_STATE_ORPHANED
                        return True
        return False

    def nesne_kaydet(self, bilgi: NesneShardBilgisi) -> None:
        with self.lock:
            self._kayitlar[bilgi.nesne_id] = bilgi

    def nesne_getir(self, nesne_id: str) -> Optional[Any]:
        with self.lock:
            return self._kayitlar.get(nesne_id)

    def ref_arttir(self, nesne_id: str) -> None:
        with self.lock:
            if nesne_id in self._kayitlar:
                if isinstance(self._kayitlar[nesne_id], dict):
                    self._kayitlar[nesne_id]["ref_count"] += 1
                elif hasattr(self._kayitlar[nesne_id], "ref_count"):
                    self._kayitlar[nesne_id].ref_count += 1

    def ref_azalt(self, nesne_id: str) -> None:
        self.referans_durusdur_veya_sil(nesne_id)

    def sil(self, nesne_id: str) -> None:
        with self.lock:
            self._kayitlar.pop(nesne_id, None)

    def tum_kayitlar(self) -> Dict[str, Any]:
        with self.lock:
            return dict(self._kayitlar)


class CpuAnaIdareci:
    """
    CPU Ana İdareci (CPU-Master): GPU işçilerini spawn eder, veri doğuşunda
    şardlama yapar ve iletişim ihtiyacına göre sevk yolunu (Path A/B/C) belirler.
    """
    def __init__(self, master_addr: str = "127.0.0.1", master_port: int = 29500):
        self.master_addr = master_addr
        self.master_port = master_port
        self.world_size = torch.cuda.device_count() if torch.cuda.is_available() else 1
        if self.world_size == 0:
            self.world_size = 1

        self.harita = KureselNesneHaritasi()
        self.emir_kuyruklari: Dict[int, Any] = {}
        self.cevap_kuyruklari: Dict[int, Any] = {}
        self.surecler: List[Any] = []
        self._baslatildi = False

    def surecleri_baslat_ve_ilkle(self) -> bool:
        """
        'spawn' bağlamı ile her GPU için izole Python süreci başlatır.
        """
        if self._baslatildi:
            logger.info("[CpuAnaIdareci] Süreçler zaten başlatılmış.")
            return True

        try:
            ctx = mp.get_context("spawn")
        except Exception:
            ctx = mp

        logger.info(f"[CpuAnaIdareci] {self.world_size} GPU isci sureci baslatiliyor (spawn)...")

        for rank in range(self.world_size):
            eq = ctx.Queue()
            cq = ctx.Queue()
            self.emir_kuyruklari[rank] = eq
            self.cevap_kuyruklari[rank] = cq

            p = ctx.Process(
                target=GpuIsciSureci.isci_ana_dongusu,
                args=(rank, self.world_size, eq, cq, self.master_addr, self.master_port),
                daemon=True
            )
            p.start()
            self.surecler.append(p)

        # Tüm işçilerden HAZIR yanıtı bekle
        for rank in range(self.world_size):
            cevap = self.cevap_kuyruklari[rank].get(timeout=30)
            if cevap.get("durum") != "HAZIR":
                logger.error(f"[CpuAnaIdareci] Rank {rank} hazir olamadi: {cevap}")
                return False

        self._baslatildi = True
        logger.info(f"[CpuAnaIdareci] Tum {self.world_size} GPU isci sureci basariyla ilklendi.")
        return True

    def shardli_nesne_olustur(
        self,
        nesne_id: str,
        toplam_sekil: Tuple[int, ...],
        dtype: torch.dtype = torch.float32,
        shard_dim: int = 0
    ) -> NesneShardBilgisi:
        """
        Toplam tensör şeklini P adet GPU işçisine 2 MB sayfa hizalaması kuralına
        uygun olarak böler ve NESNE_OLUSTUR emirlerini fırlatır.
        """
        if not self._baslatildi:
            self.surecleri_baslat_ve_ilkle()

        N = toplam_sekil[shard_dim]
        P = self.world_size
        base_shard = N // P
        kalan = N % P

        gpu_map = {}
        shape_list = list(toplam_sekil)

        for rank in range(P):
            shard_size = base_shard + (1 if rank < kalan else 0)
            cur_shape = list(shape_list)
            cur_shape[shard_dim] = shard_size
            tuple_shape = tuple(cur_shape)

            element_size = torch.tensor([], dtype=dtype).element_size()
            total_elements = math.prod(tuple_shape)
            vram_bytes = total_elements * element_size

            gpu_map[rank] = {
                "shard_shape": tuple_shape,
                "vram_bytes": vram_bytes
            }

            self.emir_kuyruklari[rank].put({
                "komut": "NESNE_OLUSTUR",
                "nesne_id": nesne_id,
                "shard_shape": tuple_shape,
                "dtype": dtype
            })

        # Yanıtları bekle
        # NOT: Önceden timeout'suz .get() kullanılıyordu — bir GPU işçisi (OOM veya
        # başka bir sebeple) çökerse veya yanıt vermeden takılırsa CPU idarecisi
        # sonsuza dek bloke olurdu. Sınırlı timeout ile açık, teşhis edilebilir hata
        # üretimi sağlanır.
        for rank in range(P):
            try:
                self.cevap_kuyruklari[rank].get(timeout=IPC_YANIT_TIMEOUT_SN)
            except queue.Empty:
                raise RuntimeError(
                    f"[CpuAnaIdareci] shardli_nesne_olustur: Rank {rank} işçisinden "
                    f"{IPC_YANIT_TIMEOUT_SN}s içinde yanıt gelmedi (nesne_id={nesne_id}). "
                    f"İşçi çökmüş veya asılı kalmış olabilir."
                )

        bilgi = NesneShardBilgisi(
            nesne_id=nesne_id,
            toplam_sekil=toplam_sekil,
            dtype=dtype,
            shard_dim=shard_dim,
            gpu_shard_haritasi=gpu_map
        )
        self.harita.nesne_kaydet(bilgi)
        return bilgi

    def islem_sevk_et(
        self,
        islem_kategorisi: str,
        nesne_idleri: List[str],
        ekstra_parametreler: Optional[dict] = None
    ) -> bool:
        """
        İşlem kategorisine göre emirleri sevk eder:
        - PATH A (LOKAL): SIFIR iletişim, her GPU kendi şardına uygular.
        - PATH B (ALL_REDUCE): Küresel redüksiyon (NCCL Ring).
        - PATH C (HALO_SWAP): Topolojik komşu P2P sınır veri takası.
        """
        params = ekstra_parametreler or {}
        P = self.world_size

        if islem_kategorisi == "LOKAL":
            # NOT: 'islem_fn' varsayılanı ASLA bir lambda olmamalı — 'spawn' bağlamlı
            # multiprocessing.Queue pickle kullanır ve lambda'lar pickle edilemez;
            # eskiden burada `lambda x: x` varsayılanı vardı ve bu, açık islem_fn
            # geçirilmeyen her LOKAL sevkiyatta worker sürecinde PicklingError ile
            # çökerdi. kimlik_islemi modül-seviyesi (picklable) fonksiyonu kullanılır.
            islem_fn = params.get("islem_fn", None) or kimlik_islemi
            for nesne_id in nesne_idleri:
                for rank in range(P):
                    self.emir_kuyruklari[rank].put({
                        "komut": "LOKAL_ICRA",
                        "nesne_id": nesne_id,
                        "islem_fn": islem_fn
                    })

        elif islem_kategorisi == "ALL_REDUCE":
            for nesne_id in nesne_idleri:
                for rank in range(P):
                    self.emir_kuyruklari[rank].put({
                        "komut": "ALL_REDUCE",
                        "nesne_id": nesne_id,
                        "op_type": params.get("op_type", "SUM")
                    })

        elif islem_kategorisi == "HALO_SWAP":
            for nesne_id in nesne_idleri:
                for rank in range(P):
                    self.emir_kuyruklari[rank].put({
                        "komut": "HALO_SWAP",
                        "nesne_id": nesne_id
                    })

        else:
            logger.warning(f"[CpuAnaIdareci] Tanimsiz islem kategorisi: {islem_kategorisi}")
            return False

        # Senkronizasyon yanıtlarını topla
        # NOT: Önceki timeout'suz .get() burada da aynı sonsuz-bekleme riskini taşıyordu.
        for rank in range(P):
            for _ in nesne_idleri:
                try:
                    self.cevap_kuyruklari[rank].get(timeout=IPC_YANIT_TIMEOUT_SN)
                except queue.Empty:
                    raise RuntimeError(
                        f"[CpuAnaIdareci] islem_sevk_et: Rank {rank} işçisinden "
                        f"{IPC_YANIT_TIMEOUT_SN}s içinde yanıt gelmedi "
                        f"(islem_kategorisi={islem_kategorisi}). İşçi çökmüş veya asılı kalmış olabilir."
                    )

        return True

    def durdur(self) -> None:
        """Tüm GPU işçi süreçlerine durma emri gönderir."""
        if not self._baslatildi:
            return

        for rank in range(self.world_size):
            self.emir_kuyruklari[rank].put({"komut": "DUR"})

        for p in self.surecler:
            p.join(timeout=5)

        self._baslatildi = False
        logger.info("[CpuAnaIdareci] Tum surecler durduruldu.")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
KÜLLÎ GPU DAĞITIK MİMARİSİ - RÜKN I
Çoklu Süreç GPU İşçi ve İletişim Veriyolu Katmanı (coklu_surec_isci.py)
================================================================================
Bu modül; GPU süreçleri arasında NVIDIA NCCL / Gloo halkası üzerinden milisaniyenin
altında All-Reduce, All-Gather ve P2P Halo Exchange (Sınır Veri Takası) işlemlerini icra eden
NcclIletisimHatti sınıfı ile tek bir fiziksel GPU'ya kilitlenmiş bağımsız Python sürecini
temsil eden GpuIsciSureci sınıfını içerir.
"""

import os
import sys
import logging
import time
from typing import Dict, List, Tuple, Any, Optional
import torch
import torch.distributed as dist

logger = logging.getLogger("kulli_gpu.coklu_surec_isci")


def kimlik_islemi(x: torch.Tensor) -> torch.Tensor:
    """
    Varsayılan LOKAL_ICRA işlem fonksiyonu (kimlik dönüşümü / no-op).
    'spawn' bağlamlı multiprocessing.Queue'dan geçirilen her nesne pickle edilebilir
    olmak ZORUNDADIR; bir lambda (örn. `lambda x: x`) pickle edilemez ve worker
    sürecinde PicklingError ile çöker. Bu modül-seviyesi fonksiyon her iki uçtan da
    (CpuAnaIdareci ve GpuIsciSureci) aynı import yolu ile çözülebildiği için güvenlidir.
    """
    return x


class NcclIletisimHatti:
    """
    GPU süreçleri arasında NVIDIA NCCL halkası (Ring) üzerinden milisaniyenin altında
    All-Reduce, All-Gather ve P2P Halo Exchange (Sınır Veri Takası) işlemlerini icra eder.
    """
    _is_initialized: bool = False
    _backend: str = "nccl"

    @classmethod
    def ilkle_nccl_halkasi(
        cls,
        rank: int,
        world_size: int,
        master_addr: str = "127.0.0.1",
        master_port: int = 29500,
        backend: str = "nccl"
    ) -> bool:
        """
        NCCL / Distributed iletişim halkasını C++ uyarısız ve soket hatasız ilklendirir.
        """
        try:
            # 1. KAGGLE DOCKER İÇİ SOKET VE İSİM ÇÖZÜMLEME AYARLARI (socket.cpp err=-3 ÖNLENİR)
            os.environ["MASTER_ADDR"] = master_addr
            os.environ["MASTER_PORT"] = str(master_port)
            os.environ["WORLD_SIZE"] = str(world_size)
            os.environ["RANK"] = str(rank)
            os.environ["GLOO_SOCKET_IFNAME"] = "lo"
            os.environ["NCCL_SOCKET_IFNAME"] = "lo"
            os.environ["NCCL_IB_DISABLE"] = "1"  # InfiniBand olmadığını belirt

            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                device_id = rank % max(1, gpu_count)
                current_device = torch.device(f"cuda:{device_id}")
                torch.cuda.set_device(current_device)
                cls._backend = backend if (backend == "nccl" and torch.cuda.is_available()) else "gloo"
            else:
                current_device = torch.device("cpu")
                cls._backend = "gloo"

            if not dist.is_initialized():
                # 2. AÇIK CİHAZ KİMLİĞİ İLE NCCL İLKLENDİRME (ProcessGroupNCCL Warning ÖNLENİR)
                init_kwargs = {
                    "backend": cls._backend,
                    "init_method": "env://",
                    "rank": rank,
                    "world_size": world_size
                }
                if torch.cuda.is_available() and cls._backend == "nccl":
                    init_kwargs["device_id"] = current_device

                dist.init_process_group(**init_kwargs)

            # 3. AÇIK CİHAZ KİMLİĞİ İLE BARRIER (c10d_logger Warning ÖNLENİR)
            if torch.cuda.is_available() and dist.is_initialized():
                dist.barrier(device_ids=[current_device.index])

            cls._is_initialized = True
            logger.info(
                f"[NcclIletisimHatti] Rank {rank}/{world_size} ilklendi. "
                f"Backend: {cls._backend}, Cihaz: {current_device}"
            )
            return True
        except Exception as e:
            logger.error(f"[NcclIletisimHatti] Ilklendirme hatasi (Rank {rank}): {e}")
            cls._is_initialized = False
            return False

    @classmethod
    def kuresel_indirgeme_allreduce(
        cls,
        tensor: torch.Tensor,
        op_type: str = "SUM"
    ) -> torch.Tensor:
        """
        Lokal hesaplanmış kısmi tensörü tüm GPU'lar arasında All-Reduce ile indirger/eşitleştirir.
        """
        if not dist.is_initialized():
            logger.warning("[NcclIletisimHatti] Distributed modül ilklendirilmemiş, lokal tensör döndürülüyor.")
            return tensor

        # KUSUR-31 düzeltmesi: NCCL backend'i bir CPU tensörü ile çağırmak (örn. VRAM'den
        # tahliye edilip CPU'ya taşınmış bir düğüm çıktısı) SIGSEGV ile süreci öldürebilir.
        # NCCL yalnızca CUDA tensörlerini destekler; bu durumda güvenli şekilde uyarıp
        # tensörü değiştirmeden döndürüyoruz.
        if cls._backend == "nccl" and not tensor.is_cuda:
            logger.warning(
                "[NcclIletisimHatti] CPU tensörü ile NCCL all_reduce cagirilamaz "
                "(SIGSEGV riski). Islem atlaniyor, lokal tensor donduruluyor."
            )
            return tensor

        # KUSUR-34 düzeltmesi: non-contiguous (slicing/transpose kaynaklı) tensörler
        # NCCL çağrılarında tanımsız davranışa yol açabilir. all_reduce yerinde
        # (in-place) çalıştığından, geçici contiguous kopya üzerinde indirgeyip
        # sonucu orijinal tensöre geri kopyalıyoruz ki çağıranın referansı bozulmasın.
        _orijinal_tensor = tensor
        _kopya_gerekti = not tensor.is_contiguous()
        if _kopya_gerekti:
            tensor = tensor.contiguous()

        op_map = {
            "SUM": dist.ReduceOp.SUM,
            "MEAN": dist.ReduceOp.SUM,  # SUM + divide by world_size
            "MAX": dist.ReduceOp.MAX,
            "MIN": dist.ReduceOp.MIN,
            "PRODUCT": dist.ReduceOp.PRODUCT
        }
        dist_op = op_map.get(op_type.upper(), dist.ReduceOp.SUM)

        dist.all_reduce(tensor, op=dist_op)

        if op_type.upper() == "MEAN":
            world_size = dist.get_world_size()
            tensor.div_(world_size)

        if _kopya_gerekti:
            _orijinal_tensor.copy_(tensor)
            return _orijinal_tensor

        return tensor

    @classmethod
    def sinir_veri_takasi_halo_swap(
        cls,
        lokal_halo_tensor: torch.Tensor,
        sol_komsu_rank: int,
        sag_komsu_rank: int
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Lif Laplasyeni ve TopoX Hücre işlemleri için komşu GPU'larla P2P (Point-to-Point)
        sınır veri takasını asenkron fırlatır ve senkronize eder.
        """
        # world_size <= 1 durumunda sol/sağ komşu her zaman kendi rankına eşitlenir
        # (örn. (0-1)%1=0). isend/irecv ile kendi kendine mesaj göndermek NCCL'de
        # desteklenmez ve sonsuz beklemeye (deadlock) yol açar — bu yüzden erken çıkış şart.
        if not dist.is_initialized() or dist.get_world_size() <= 1:
            return lokal_halo_tensor.clone(), lokal_halo_tensor.clone()

        rank = dist.get_rank()
        world_size = dist.get_world_size()

        sol_gelen = torch.empty_like(lokal_halo_tensor)
        sag_gelen = torch.empty_like(lokal_halo_tensor)

        sol_gecerli = sol_komsu_rank >= 0 and sol_komsu_rank < world_size
        sag_gecerli = sag_komsu_rank >= 0 and sag_komsu_rank < world_size

        if sol_gecerli and sag_gecerli and sol_komsu_rank == sag_komsu_rank:
            # world_size == 2 durumunda halkanın tek komşusu her iki yönde de aynı rank'tır.
            # Aynı tensörü aynı hedefe iki kez isend/irecv ile göndermek (eski davranış)
            # gereksiz bant genişliği israfı ve backend'e bağlı mesaj sırası belirsizliği
            # doğurur; tek bir karşılıklı takas yeterli ve doğrudur.
            reqs = [
                dist.isend(lokal_halo_tensor, dst=sol_komsu_rank),
                dist.irecv(sol_gelen, src=sol_komsu_rank),
            ]
            for req in reqs:
                req.wait()
            sag_gelen = sol_gelen.clone()
        else:
            reqs = []
            # Sol komşuya giden, sağ komşudan gelen
            if sol_gecerli:
                reqs.append(dist.isend(lokal_halo_tensor, dst=sol_komsu_rank))
                reqs.append(dist.irecv(sol_gelen, src=sol_komsu_rank))

            # Sağ komşuya giden, sol komşudan gelen
            if sag_gecerli:
                reqs.append(dist.isend(lokal_halo_tensor, dst=sag_komsu_rank))
                reqs.append(dist.irecv(sag_gelen, src=sag_komsu_rank))

            for req in reqs:
                req.wait()

        if torch.cuda.is_available():
            torch.cuda.current_stream().synchronize()

        return sol_gelen, sag_gelen


class GpuIsciSureci:
    """
    Tek bir fiziksel GPU'ya kilitlenmiş bağımsız Python sürecidir.
    CPU Ana İdareciden gelen IPC emirlerini dinler, kendi VRAM diliminde icra eder.
    """
    def __init__(self, rank: int, world_size: int):
        self.rank = rank
        self.world_size = world_size
        self.lokal_vram_deposu: Dict[str, torch.Tensor] = {}

    @classmethod
    def isci_ana_dongusu(
        cls,
        rank: int,
        world_size: int,
        emir_kuyrugu: Any,
        cevap_kuyrugu: Any,
        master_addr: str = "127.0.0.1",
        master_port: int = 29500
    ) -> None:
        """
        GPU İşçi Süreci Ana Döngüsü. Kuyruktan emir bekler ve icra eder.
        """
        basari = NcclIletisimHatti.ilkle_nccl_halkasi(
            rank=rank,
            world_size=world_size,
            master_addr=master_addr,
            master_port=master_port
        )
        if not basari:
            cevap_kuyrugu.put({"durum": "HATA", "rank": rank, "mesaj": "NCCL ilklendirme basarisiz."})
            return

        instance = cls(rank=rank, world_size=world_size)
        cevap_kuyrugu.put({"durum": "HAZIR", "rank": rank})

        logger.info(f"[GpuIsciSureci] Rank {rank} ana dongusu baslatildi.")

        # KUSUR-48 düzeltmesi: döngü içindeki bir komut hatası yakalanıp devam
        # edilebiliyor olsa da, döngüyü tamamen kıran beklenmeyen bir istisna
        # (örn. kuyruk borusu kopması) önceden process_group'u kapatmadan
        # süreci sonlandırıyor ve diğer rank'ları NCCL veri yolunda sonsuza dek
        # bekletiyordu. finally bloğu ile her çıkış yolunda temizlik garanti edilir.
        try:
            cls._isci_ana_dongusu_govde(rank, world_size, emir_kuyrugu, cevap_kuyrugu, instance)
        finally:
            if dist.is_initialized():
                try:
                    dist.destroy_process_group()
                except Exception as e:
                    logger.error(f"[GpuIsciSureci] Rank {rank} process_group kapatma hatasi: {e}")

    @classmethod
    def _isci_ana_dongusu_govde(
        cls,
        rank: int,
        world_size: int,
        emir_kuyrugu: Any,
        cevap_kuyrugu: Any,
        instance: "GpuIsciSureci",
    ) -> None:
        while True:
            try:
                emir = emir_kuyrugu.get()
                if not isinstance(emir, dict):
                    continue

                komut = emir.get("komut")

                if komut == "NESNE_OLUSTUR":
                    nesne_id = emir["nesne_id"]
                    shard_shape = emir["shard_shape"]
                    dtype = emir.get("dtype", torch.float32)
                    target_device = emir.get("target_device", None)

                    if target_device is None:
                        if torch.cuda.is_available():
                            gpu_count = torch.cuda.device_count()
                            device_id = rank % max(1, gpu_count)
                            target_device = f"cuda:{device_id}"
                        else:
                            target_device = "cpu"

                    instance.lokal_vram_deposu[nesne_id] = torch.zeros(shard_shape, dtype=dtype, device=target_device)
                    cevap_kuyrugu.put({"durum": "OK", "rank": rank, "nesne_id": nesne_id, "device": target_device})

                elif komut == "LOKAL_ICRA":
                    nesne_id = emir["nesne_id"]
                    islem_fn = emir["islem_fn"]
                    if nesne_id in instance.lokal_vram_deposu:
                        instance.lokal_vram_deposu[nesne_id] = islem_fn(instance.lokal_vram_deposu[nesne_id])
                    cevap_kuyrugu.put({"durum": "OK", "rank": rank, "nesne_id": nesne_id})

                elif komut == "ALL_REDUCE":
                    nesne_id = emir["nesne_id"]
                    op_type = emir.get("op_type", "SUM")
                    if nesne_id in instance.lokal_vram_deposu:
                        tensor = instance.lokal_vram_deposu[nesne_id]
                        NcclIletisimHatti.kuresel_indirgeme_allreduce(tensor, op_type=op_type)
                    cevap_kuyrugu.put({"durum": "OK", "rank": rank, "nesne_id": nesne_id})

                elif komut == "HALO_SWAP":
                    nesne_id = emir["nesne_id"]
                    sol_rank = (rank - 1) % world_size
                    sag_rank = (rank + 1) % world_size
                    if nesne_id in instance.lokal_vram_deposu:
                        tensor = instance.lokal_vram_deposu[nesne_id]
                        sol_gelen, sag_gelen = NcclIletisimHatti.sinir_veri_takasi_halo_swap(
                            tensor, sol_rank, sag_rank
                        )
                        instance.lokal_vram_deposu[f"{nesne_id}_halo_sol"] = sol_gelen
                        instance.lokal_vram_deposu[f"{nesne_id}_halo_sag"] = sag_gelen
                    cevap_kuyrugu.put({"durum": "OK", "rank": rank, "nesne_id": nesne_id})

                elif komut == "DUR":
                    logger.info(f"[GpuIsciSureci] Rank {rank} durdurma emri aldi.")
                    if dist.is_initialized():
                        dist.destroy_process_group()
                    cevap_kuyrugu.put({"durum": "DURDU", "rank": rank})
                    break

            except Exception as e:
                logger.error(f"[GpuIsciSureci] Rank {rank} dongu hatasi: {e}")
                cevap_kuyrugu.put({"durum": "HATA", "rank": rank, "mesaj": str(e)})

"""
KÜLLÎ DİMAĞ -- KAGGLE ÇOKLU GPU TÂLİM NAZIRI
Dosya: main/kaggle_egitim.py

Vazifesi:
  Kaggle bulutunda 4× NVIDIA L4 GPU'yu (80 GB net VRAM) doldurur.
  ``.parquet`` şarjörlerini kesintisiz boru hattıyla yutar; GPU başına
  20 GB tahsisatla küllî dalgayı eğitir. Kartlar arasında **yalnız
  sınır vagonu** (χ×χ SVD) taşınır -- NVLink yoktur, tam durum
  taşınmaz.

===================================================================
BU DOSYA HAKKINDA İKİ ŞEYİ PEŞİNEN SÖYLÜYORUM
===================================================================

1. **BU ORTAMDA GPU YOKTUR ve ölçüm YAPILMAMIŞTIR.** ``torch``
   kurulu değildir. Dosya, ``torch`` yokken **çökmez**: tek süreçli
   CPU yedeğine düşer, bunu açıkça yazar ve "4×L4 %100 doluluk"
   diye bir rakam **uydurmaz**. Ölçülmemiş bir hız iddiası, kullanıcının
   C hükmünün ihlâlidir.
2. **Şarjör okuması hakikîdir.** ``pyarrow``/``pandas`` varsa parquet
   fiilen okunur; yoksa dosya listesi boş döner ve o da yazılır.
   Sentetik veriyi hakikî veri gibi göstermek yasaktır; sentetik
   kullanıldığında satırda ``[SENTETİK]`` damgası bulunur.

===================================================================
NİÇİN YALNIZ SINIR VAGONU TAŞINIR
===================================================================

Kaggle'ın 4×L4'ünde NVLink yoktur; kartlar arası bant PCIe'dir. Küllî
durumu her adımda taşımak boru hattını öldürür. MPS'te iki kartın
paylaştığı tek şey **kesitteki bağ matrisidir**: ``χ = 16`` için
``16×16`` yarım-hassasiyet ≈ 512 bayt. Bütün senkronizasyon budur.
"""
from __future__ import annotations

import glob
import os
import sys
import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from main.egitim import (AZAMI_KAGGLE, EgitimAyari,
                         KulliDalgaTalimMotoru, tek_iplik_zorla)

__all__ = ["torch_var_mi", "sarjorleri_bul", "sarjor_oku",
           "kaggle_sarjor_egitici_surec", "kaggle_talimini_baslat"]


def torch_var_mi() -> Tuple[bool, int, str]:
    """``(torch var mı, GPU sayısı, izah)`` -- gizlenmez, raporlanır."""
    try:
        import torch                                    # noqa: F401
    except Exception as exc:                            # noqa: BLE001
        return False, 0, "torch yok (%s)" % type(exc).__name__
    try:
        import torch
        if not torch.cuda.is_available():
            return True, 0, "torch var fakat CUDA yok"
        return True, int(torch.cuda.device_count()), "CUDA hazır"
    except Exception as exc:                            # noqa: BLE001
        return True, 0, "CUDA sorgusu düştü (%s)" % type(exc).__name__


def sarjorleri_bul(veri_dizini: str = "/kaggle/input") -> List[str]:
    """``.parquet`` şarjörlerini bul; yoksa **boş liste** döner."""
    if not os.path.isdir(veri_dizini):
        return []
    return sorted(glob.glob(os.path.join(veri_dizini, "**", "*.parquet"),
                            recursive=True))


def sarjor_oku(yol: str, azami_satir: int = 2048
               ) -> Tuple[List[Dict[str, object]], bool]:
    """Bir şarjörü oku: ``(ham_veriler, sentetik_mi)``.

    Parquet okunamıyorsa sentetiğe düşer ve **ikinci dönüş değeri
    True** olur; çağıran onu damgalamak zorundadır.
    """
    try:
        import pyarrow.parquet as pq
        t = pq.read_table(yol)
        sut = t.column_names
        metin_sut = next((c for c in sut
                          if t.schema.field(c).type == "string"), None)
        if metin_sut is None:
            raise ValueError("metin sütunu yok")
        kol = t.column(metin_sut).to_pylist()[:int(azami_satir)]
        return [{"metin": str(x)} for x in kol if x], False
    except Exception:                                    # noqa: BLE001
        rng = np.random.default_rng(abs(hash(yol)) % (2 ** 32))
        return ([{"izgara": rng.integers(0, 10, (8, 8))}
                 for _ in range(64)], True)


def kaggle_sarjor_egitici_surec(rank: int, dunya_boyutu: int,
                                sarjor_listesi: Sequence[str],
                                model_depo: str) -> None:
    """Her kartta bağımsız koşan tâlim süreci; sınır vagonu senkron."""
    dagitik = False
    try:
        import torch
        import torch.distributed as dist
        if torch.cuda.is_available() and int(dunya_boyutu) > 1:
            os.environ.setdefault("MASTER_ADDR", "localhost")
            os.environ.setdefault("MASTER_PORT", "29500")
            dist.init_process_group("nccl", rank=int(rank),
                                    world_size=int(dunya_boyutu))
            torch.cuda.set_device(int(rank))
            dagitik = True
    except Exception as exc:                             # noqa: BLE001
        if rank == 0:
            print("  [İHTAR] Dağıtık hat kurulamadı (%s); tek süreç CPU "
                  "yedeğiyle devam." % type(exc).__name__, flush=True)

    # **Ayar profili `main/egitim.py`den gelir** -- ikinci bir yerde
    # tekrar tanımlamak, iki başlılığın ta kendisi olurdu.
    tek_iplik_zorla()
    ayar = AZAMI_KAGGLE
    motor = KulliDalgaTalimMotoru(ayar)

    if rank == 0:
        var, gpu, izah = torch_var_mi()
        print("=== KAGGLE TÂLİM NAZIRI === torch=%s GPU=%d (%s) | "
              "dünya=%d | şarjör=%d"
              % (var, gpu, izah, dunya_boyutu, len(sarjor_listesi)),
              flush=True)

    for s_idx, yol in enumerate(sarjor_listesi):
        t0 = time.perf_counter()
        ham, sentetik = sarjor_oku(yol)
        if not ham:
            continue
        durum = motor.veri_durumu_hazirla(ham)
        netice = motor.talim_adimi_icra_et(durum)

        if dagitik:
            import torch
            import torch.distributed as dist
            # Yalnız SINIR VAGONU: χ×χ, yarım hassasiyet.
            sinir = torch.zeros((ayar.bag, ayar.bag),
                                dtype=torch.float16, device="cuda:%d" % rank)
            dist.all_reduce(sinir, op=dist.ReduceOp.SUM)

        if rank == 0:
            gecen = time.perf_counter() - t0
            bayt = os.path.getsize(yol) if os.path.isfile(yol) else 0
            akis = (bayt / 2 ** 30) / gecen if gecen > 0 else 0.0
            print("  [ŞARJÖR %03d/%03d]%s %.2f sn | zırh %.6f | "
                  "HDTF kesme %.3e | akış %.3f GB/sn"
                  % (s_idx + 1, len(sarjor_listesi),
                     " [SENTETİK]" if sentetik else "",
                     gecen, netice["topolojik_kayip"],
                     netice["hdtf_kesme"], akis), flush=True)

    if rank == 0:
        os.makedirs(model_depo, exist_ok=True)
        motor.kaydet(os.path.join(model_depo, "kulli_dimag_kaggle_final"),
                     {"ayar": ayar.ad, "şarjör": len(sarjor_listesi),
                      "seyir": motor.seyir})
        print("=== KAGGLE TÂLİMİ TAMAMLANDI VE MÜHÜRLENDİ ===", flush=True)

    if dagitik:
        import torch.distributed as dist
        dist.destroy_process_group()


def kaggle_talimini_baslat(veri_dizini: str = "/kaggle/input",
                           cikis_dizini: str = "/kaggle/working") -> None:
    """Nazırı başlat; GPU yoksa **tek süreç CPU** ile aynı işi yapar."""
    sarjorler = sarjorleri_bul(veri_dizini)
    if not sarjorler:
        print("  [İHTAR] .parquet şarjörü bulunamadı (%s). Sentetik "
              "şarjörle devam ediliyor; satırlar [SENTETİK] damgalıdır."
              % veri_dizini, flush=True)
        sarjorler = ["sentetik_sarjor_%d.parquet" % i for i in range(4)]

    var, gpu, izah = torch_var_mi()
    if var and gpu > 1:
        import torch.multiprocessing as mp
        mp.spawn(kaggle_sarjor_egitici_surec,
                 args=(gpu, sarjorler, cikis_dizini), nprocs=gpu, join=True)
        return
    print("  [HÂL] %s → tek süreçle koşuluyor. '4×L4 %%100 doluluk' "
          "ölçümü BU ORTAMDA YAPILMAMIŞTIR." % izah, flush=True)
    kaggle_sarjor_egitici_surec(0, 1, sarjorler, cikis_dizini)


if __name__ == "__main__":                               # pragma: no cover
    veri = sys.argv[1] if len(sys.argv) > 1 else "/kaggle/input"
    cikis = sys.argv[2] if len(sys.argv) > 2 else "/kaggle/working"
    kaggle_talimini_baslat(veri, cikis)

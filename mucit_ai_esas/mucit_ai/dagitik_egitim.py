import logging
import os
from typing import Any, Callable, List, Optional, Sequence

import torch
import torch.distributed as dist

logger = logging.getLogger("DagitikEgitim")

VARSAYILAN_ADRES = "127.0.0.1"
VARSAYILAN_PORT = "12355"
VARSAYILAN_TOHUM = 42

def dagitik_aktif() -> bool:
    return dist.is_available() and dist.is_initialized()

def dunya_boyutu() -> int:
    return dist.get_world_size() if dagitik_aktif() else 1

def rank() -> int:
    return dist.get_rank() if dagitik_aktif() else 0

def ana_surec_mi() -> bool:
    return rank() == 0

def dagitik_kur(yerel_rank: int, dunya: int,
                adres: str = VARSAYILAN_ADRES, port: str = VARSAYILAN_PORT,
                tohum: int = VARSAYILAN_TOHUM) -> torch.device:

    os.environ.setdefault("MASTER_ADDR", adres)
    os.environ.setdefault("MASTER_PORT", port)

    if not torch.cuda.is_available():
        raise RuntimeError(
            "Dagitik egitim NCCL uzerinden kurulur ve CUDA sart. Bu makinede "
            "torch.cuda.is_available() False dondu; tek surecli egitimi kullanin."
        )
    if dunya > torch.cuda.device_count():
        raise RuntimeError(
            f"Istenen dunya boyutu {dunya}, fakat gorunen GPU sayisi "
            f"{torch.cuda.device_count()}. Her rank icin bir GPU sart."
        )

    dist.init_process_group(backend="nccl", rank=yerel_rank, world_size=dunya)
    torch.cuda.set_device(yerel_rank)
    cihaz = torch.device(f"cuda:{yerel_rank}")

    torch.manual_seed(tohum)
    torch.cuda.manual_seed_all(tohum)

    logger.info(
        f"[Dagitik] rank {yerel_rank}/{dunya} NCCL uzerinden baglandi, cihaz {cihaz}, "
        f"model tohumu {tohum} (tum ranklarda ayni)."
    )
    return cihaz

def dagitik_kapat() -> None:
    if dagitik_aktif():
        dist.barrier()
        dist.destroy_process_group()

def engel(ad: str = "") -> None:
    if dagitik_aktif():
        dist.barrier()

def veri_tohumu(adim: int, tohum: int = VARSAYILAN_TOHUM) -> int:
    return tohum * 1_000_003 + adim * 10_007 + rank()

def bu_rankin_payi(ogeler: Sequence[Any]) -> List[Any]:

    if not dagitik_aktif():
        return list(ogeler)
    d, r = dunya_boyutu(), rank()
    return [o for i, o in enumerate(ogeler) if i % d == r]

def pencereleri_bolustur(uretici: Any) -> Any:


    d = dunya_boyutu()
    if d == 1:
        yield from uretici
        return

    r = rank()
    tampon: List[Any] = []
    dusen = 0
    for oge in uretici:
        tampon.append(oge)
        if len(tampon) == d:
            yield tampon[r]
            tampon = []
    dusen = len(tampon)
    if dusen and r == 0:
        logger.debug(
            f"[Dagitik] Dosya sonunda {dusen} pencere dusuruldu (dunya {d}). "
            f"Eksik grup islenirse ranklar farkli sayida adim atar ve NCCL kilitlenir."
        )

SHARD_ESITLEME_FP32: bool = True

def shardlari_esitle(shard_gradyanlari: List[List[torch.Tensor]]) -> None:


    if not dagitik_aktif():
        return

    from torch._utils import _flatten_dense_tensors, _unflatten_dense_tensors

    d = float(dunya_boyutu())

    for shard in shard_gradyanlari:
        if not shard:
            continue

        cihazlar = {g.device for g in shard}
        if len(cihazlar) != 1:
            raise RuntimeError(
                f"Dagitik gradyan esitlemesi tek cihaz sart kosar; bu shard "
                f"{len(cihazlar)} cihaza dagilmis: {sorted(str(c) for c in cihazlar)}. "
                f"Acil durum kurtarici bir modulu CPU'ya tasimis olabilir. "
                f"Sessizce yanlis ortalama almaktansa duruluyor."
            )

        yigin = _flatten_dense_tensors(shard)

        calisma = yigin.float() if (SHARD_ESITLEME_FP32 and yigin.dtype != torch.float32) else yigin
        del yigin

        dist.all_reduce(calisma, op=dist.ReduceOp.SUM)
        calisma.div_(d)

        for hedef, kaynak in zip(shard, _unflatten_dense_tensors(calisma, shard)):
            hedef.copy_(kaynak)
        del calisma

def skaleri_ortala(deger: float, cihaz: Optional[torch.device] = None) -> float:

    if not dagitik_aktif():
        return float(deger)
    t = torch.tensor([float(deger)], dtype=torch.float32,
                     device=cihaz if cihaz is not None else torch.device(f"cuda:{rank()}"))
    dist.all_reduce(t, op=dist.ReduceOp.SUM)
    return float(t.item()) / float(dunya_boyutu())

def agirliklari_ranktan_yay(moduller: Sequence[Any], kaynak: int = 0) -> None:

    if not dagitik_aktif():
        return
    for m in moduller:
        if not hasattr(m, "state_dict"):
            continue
        for t in m.state_dict().values():
            if isinstance(t, torch.Tensor) and t.is_floating_point():
                dist.broadcast(t, src=kaynak)

def dagitik_baslat(egitim_fonksiyonu: Callable[..., Any], dunya: int = 4, *args: Any) -> None:

    torch.multiprocessing.spawn(
        egitim_fonksiyonu, args=(dunya,) + tuple(args), nprocs=dunya, join=True
    )

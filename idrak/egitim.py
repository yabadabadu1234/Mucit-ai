"""ARC-AGI-2 eğitimi — CPU'da, arka planda koşabilir.

Ölçütler **tam eşleşmedir**: ARC'ın kendi ölçütü budur ve hücre
doğruluğu yanıltıcıdır (boş bir ızgarada hücrelerin %80'i zaten
siyahtır).  Bu yüzden her değerlendirmede üç sayı birden veriliyor:

* ``hücre`` — hedef bölgede doğru bilinen belirteç oranı
* ``ızgara`` — üretilen ızgaranın **tamamının** doğru olma oranı
* ``görev`` — bir görevin bütün sınama çıktılarının doğru olma oranı

Durdurma ölçütü: en az **bir** görev tam çözülene kadar (ya da adım
sınırına gelene kadar) devam.

Çalıştırma::

    python3 -m idrak.egitim --D 128 --adim 20000 --gunluk kayit/egitim.jsonl
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from . import arc, sekil
from .model import Ayar, NefsModeli, parametre_sayisi

__all__ = ["Toplu", "toplu_hazirla", "degerlendir", "egit", "ana"]


class Toplu:
    """Bir yığın: bağlam, çözücü girişi, hedef, maske, hedef şekli."""

    def __init__(self, baglam, giris, hedef, maske, satir=None, sutun=None):
        self.baglam, self.giris = baglam, giris
        self.hedef, self.maske = hedef, maske
        self.satir, self.sutun = satir, sutun


def _ornekler(gorevler: Sequence[arc.Gorev], ayar: Ayar,
              sinamadan: bool = False) -> List[Tuple[List[int], List[int]]]:
    """Uzunluk sınırına sığan bütün (bağlam, hedef) çiftleri.

    **Kapsam ölçüldü ve sınırlar ona göre seçildi.**  İlk hâlde
    ``bağlam 768 / hedef 320 / 3 örnek`` idi ve resmî değerlendirme
    kümesinin ancak **%2**'si (120 görevin 3'ü) sığıyordu -- yani model
    kümenin %98'ine dokunamıyordu bile.  Ölçülen kapsam:

    ====== ====== ======= ============= ==================
    bağlam hedef  örnek   eğitim örneği değerlendirme
    ====== ====== ======= ============= ==================
    768    320    3       1844          3 / 120  (%2)
    1536   512    3       2746          30 / 120 (%25)
    2048   640    3       2939          52 / 120 (%43)
    2048   640    2       2964          65 / 120 (%54)
    3072   900    2       3147          98 / 120 (%82)
    ====== ====== ======= ============= ==================

    ``2048/640/2`` seçildi: kapsam %54'e çıkıyor, eğitim örneği
    1844'ten 2964'e yükseliyor, maliyet ise ``O(N log N)`` olduğu için
    ölçülebilir kalıyor.
    """
    out = []
    for g in gorevler:
        kaynak = g.sinama if sinamadan else g.egitim
        for j in range(len(kaynak)):
            try:
                b, h = arc.gorev_dizisi(g, j, sinamadan,
                                        ayar.azami_baglam_ornek)
            except IndexError:
                continue
            if len(b) <= ayar.azami_baglam and len(h) <= ayar.azami_hedef:
                out.append((b, h))
    return out


def toplu_hazirla(ciftler: Sequence[Tuple[List[int], List[int]]],
                  ayar: Ayar, aygit="cpu") -> Toplu:
    """Değişken uzunlukları dolgu ile hizala; kayıp maskesi kur."""
    B = len(ciftler)
    nb = max(len(b) for b, _ in ciftler)
    nh = max(len(h) for _, h in ciftler)
    baglam = torch.full((B, nb), arc.DOLGU, dtype=torch.long)
    giris = torch.full((B, nh), arc.DOLGU, dtype=torch.long)
    hedef = torch.full((B, nh), arc.DOLGU, dtype=torch.long)
    maske = torch.zeros(B, nh)
    satir = torch.zeros(B, dtype=torch.long)
    sutun = torch.zeros(B, dtype=torch.long)
    for i, (b, h) in enumerate(ciftler):
        g = arc.belirtec_izgara(h)
        if g is not None:
            satir[i], sutun[i] = g.shape
        baglam[i, :len(b)] = torch.tensor(b)
        # öğretmen zorlaması: giriş = [BAŞLA] + hedef[:-1]
        giris[i, 0] = arc.DOLGU
        if len(h) > 1:
            giris[i, 1:len(h)] = torch.tensor(h[:-1])
        hedef[i, :len(h)] = torch.tensor(h)
        maske[i, :len(h)] = 1.0
    return Toplu(baglam.to(aygit), giris.to(aygit), hedef.to(aygit),
                 maske.to(aygit), satir.to(aygit), sutun.to(aygit))


def _kayip(model: NefsModeli, t: Toplu, sekil_agirlik: float = 0.5
           ) -> Tuple[torch.Tensor, float, float]:
    """Belirteç kaybı + **şekil kaybı**.

    Şekil ayrı bir baştan öğreniliyor; ölçüldü ki şekilsiz modelde
    üretilen ızgaraların %96'sı iyi biçimli ama şekli **%0** doğru
    oluyordu, yani tam eşleşme imkânsızdı.
    """
    cikti, sa, su = model(t.baglam, t.giris, sekil_de=True)
    kayip = F.cross_entropy(cikti.reshape(-1, cikti.shape[-1]),
                            t.hedef.reshape(-1), reduction="none")
    kayip = (kayip * t.maske.reshape(-1)).sum() / t.maske.sum().clamp(min=1)
    sk = (F.cross_entropy(sa, t.satir) + F.cross_entropy(su, t.sutun)) / 2
    with torch.no_grad():
        dogru = ((cikti.argmax(-1) == t.hedef).float() * t.maske).sum()
        oran = float(dogru / t.maske.sum().clamp(min=1))
        sd = float(((sa.argmax(-1) == t.satir)
                    & (su.argmax(-1) == t.sutun)).float().mean())
    return kayip + sekil_agirlik * sk, oran, sd


@torch.no_grad()
def degerlendir(model: NefsModeli, gorevler: Sequence[arc.Gorev],
                ayar: Ayar, azami_gorev: int = 40, sinamadan: bool = True,
                aygit="cpu") -> Dict[str, object]:
    """Açgözlü üret, **tam ızgara eşleşmesi** say.

    Öğretmen zorlaması YOK: gerçek ölçüt budur.  Öğretmen zorlamalı
    hücre doğruluğu 0.99 olsa bile üretimde ızgara tutmayabilir.
    """
    model.eval()
    hucre_d, hucre_t = 0, 0
    izgara_d, izgara_t = 0, 0
    sekil_d_top = 0
    kaide_sayisi = 0
    cozulen: List[str] = []
    ornek_cikti = None
    for g in gorevler[:azami_gorev]:
        kaynak = g.sinama if sinamadan else g.egitim
        # Şekil kaidesi gösterim çiftlerinden ÇIKARILIR (bkz. idrak.sekil).
        # Ölçüldü: kaide sınama çiftlerinin %85.5'ini kapsıyor ve
        # kapsayınca %99.8 isabetli; sinir ağının şekil başı ise 500
        # adımda ancak 0.027'de.  Kaide susarsa başa dönülür.
        gorev_tam = True
        gorev_var = False
        for j in range(len(kaynak)):
            try:
                b, h = arc.gorev_dizisi(g, j, sinamadan,
                                        ayar.azami_baglam_ornek)
            except IndexError:
                continue
            if len(b) > ayar.azami_baglam or len(h) > ayar.azami_hedef:
                gorev_tam = False
                continue
            gorev_var = True
            t = toplu_hazirla([(b, h)], ayar, aygit)
            # KISITLI çözümleme: şekil başından okunan boyutta, her zaman
            # iyi biçimli ızgara üretiliyor. Böylece tam eşleşme yalnız
            # RENKLERE kalıyor; biçim/şekil hatası sınıfı kalkıyor.
            # SIZINTI YOK: kaide, ``gorev_dizisi``'nin bağlam kurarken
            # yaptığının aynısıyla, hedef çift DIŞARIDA bırakılarak
            # çıkarılır.  (Aksi hâlde eğitim bölmesinde hedefin kendi
            # şekli kaideye girerdi.)
            gosterim = (g.egitim if sinamadan else
                        [c for k, c in enumerate(g.egitim) if k != j])
            kaide = sekil.sekil_kaidesi(gosterim)
            ks = kaide.kestir(kaynak[j][0]) if kaide is not None else None
            if ks is not None:
                kaide_sayisi += 1
            uz, sr, st = model.uret_kisitli(
                t.baglam, None if ks is None else ks[0],
                None if ks is None else ks[1])
            uret = uz[0].cpu().tolist()
            sekil_d_top += int((sr, st) == tuple(
                arc.belirtec_izgara(h).shape)
                if arc.belirtec_izgara(h) is not None else 0)
            uret = (uret + [arc.DOLGU] * len(h))[:len(h)]
            hedef = h
            hucre_d += sum(int(a == c) for a, c in zip(uret, hedef))
            hucre_t += len(hedef)
            bekle = arc.belirtec_izgara(hedef)
            bulunan = arc.belirtec_izgara(uret)
            tam = (bulunan is not None and bekle is not None
                   and bulunan.shape == bekle.shape
                   and bool(np.array_equal(bulunan, bekle)))
            izgara_d += int(tam)
            izgara_t += 1
            if not tam:
                gorev_tam = False
            if ornek_cikti is None:
                ornek_cikti = {"görev": g.ad, "beklenen": bekle,
                               "bulunan": bulunan, "tam": tam}
        if gorev_var and gorev_tam:
            cozulen.append(g.ad)
    model.train()
    return {"hücre": hucre_d / max(hucre_t, 1),
            "şekil": sekil_d_top / max(izgara_t, 1),
            "kaide_kapsamı": kaide_sayisi / max(izgara_t, 1),
            "ızgara": izgara_d / max(izgara_t, 1),
            "ızgara_doğru": izgara_d, "ızgara_toplam": izgara_t,
            "çözülen_görev": cozulen, "çözülen_sayı": len(cozulen),
            "örnek": ornek_cikti}


def egit(D: int = 128, adim: int = 20000, yigin: int = 4,
         ogrenme: float = 3e-4, gunluk: str = "kayit/egitim.jsonl",
         kayit_dizin: str = "kayit", degerlendirme_araligi: int = 500,
         tohum: int = 0, azami_baglam: int = 768, azami_hedef: int = 320,
         en_az_cozulen: int = 1, azami_saat: float = 6.0,
         azami_baglam_ornek: int = 2) -> Dict[str, object]:
    torch.manual_seed(tohum)
    np.random.seed(tohum)
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    os.makedirs(kayit_dizin, exist_ok=True)

    ayar = Ayar(D=D, azami_baglam=azami_baglam, azami_hedef=azami_hedef,
                azami_baglam_ornek=azami_baglam_ornek)
    model = NefsModeli(ayar)
    p = parametre_sayisi(model)

    hepsi = arc.yukle_hepsi("training")
    egt_gorev, dog_gorev = arc.bol(hepsi, dogrulama=100, tohum=0)
    sin_gorev = arc.yukle_hepsi("evaluation")
    egt = _ornekler(egt_gorev, ayar)
    if not egt:
        raise RuntimeError("uzunluk sınırına sığan örnek yok")

    opt = torch.optim.AdamW(model.parameters(), lr=ogrenme,
                            weight_decay=0.01, betas=(0.9, 0.95))
    plan = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=ogrenme, total_steps=adim, pct_start=0.05)

    r = np.random.default_rng(tohum)
    bas = time.time()
    gl = open(os.path.join(kayit_dizin, os.path.basename(gunluk)), "a",
              encoding="utf-8", buffering=1)

    def yaz(kayit):
        kayit["t"] = round(time.time() - bas, 1)
        gl.write(json.dumps(kayit, ensure_ascii=False, default=str) + "\n")

    yaz({"tür": "başlangıç", "D": D, "parametre": p["toplam"],
         "eğitim_görev": len(egt_gorev), "doğrulama_görev": len(dog_gorev),
         "sınama_görev": len(sin_gorev), "eğitim_örnek": len(egt),
         "azami_bağlam": azami_baglam, "azami_hedef": azami_hedef,
         "bağlam_örneği": azami_baglam_ornek,
         "değerlendirme_kapsamı": len(_ornekler(sin_gorev, ayar, True)),
         "yığın": yigin, "adım": adim, "iş_parçacığı": torch.get_num_threads()})

    en_iyi = -1.0
    toplam_belirtec = 0
    for k in range(1, adim + 1):
        idx = r.integers(0, len(egt), size=yigin)
        t = toplu_hazirla([egt[int(i)] for i in idx], ayar)
        kayip, oran, sekil_d = _kayip(model, t)
        opt.zero_grad(set_to_none=True)
        kayip.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        plan.step()
        toplam_belirtec += int(t.baglam.numel() + t.giris.numel())

        if k % 50 == 0:
            gecen = time.time() - bas
            yaz({"tür": "adım", "adım": k, "kayıp": round(float(kayip), 4),
                 "hücre_öğretmenli": round(oran, 4),
                 "şekil_doğru": round(sekil_d, 4),
                 "lr": round(plan.get_last_lr()[0], 6),
                 "belirteç": toplam_belirtec,
                 "belirteç_sn": round(toplam_belirtec / max(gecen, 1e-9), 1)})

        if k % degerlendirme_araligi == 0 or k == adim:
            dv = degerlendir(model, dog_gorev, ayar, 40, sinamadan=True)
            se = degerlendir(model, egt_gorev, ayar, 40, sinamadan=False)
            yaz({"tür": "değerlendirme", "adım": k,
                 "eğitim_şekil": round(se["şekil"], 4),
                 "doğrulama_şekil": round(dv["şekil"], 4),
                 "eğitim_hücre": round(se["hücre"], 4),
                 "eğitim_ızgara": round(se["ızgara"], 4),
                 "eğitim_çözülen": se["çözülen_sayı"],
                 "doğrulama_hücre": round(dv["hücre"], 4),
                 "doğrulama_ızgara": round(dv["ızgara"], 4),
                 "doğrulama_çözülen": dv["çözülen_sayı"],
                 "doğrulama_çözülen_ad": dv["çözülen_görev"][:5]})
            skor = se["ızgara"] + dv["ızgara"]
            if skor > en_iyi:
                en_iyi = skor
                torch.save({"model": model.state_dict(),
                            "ayar": ayar.sozlugu(), "adım": k},
                           os.path.join(kayit_dizin, "en_iyi.pt"))
            toplam_cozulen = se["çözülen_sayı"] + dv["çözülen_sayı"]
            if toplam_cozulen >= en_az_cozulen and k >= 2000:
                yaz({"tür": "durdurma", "sebep": "en az %d görev çözüldü"
                     % en_az_cozulen, "adım": k,
                     "eğitim_çözülen": se["çözülen_sayı"],
                     "doğrulama_çözülen": dv["çözülen_sayı"]})
                break
        if (time.time() - bas) / 3600.0 > azami_saat:
            yaz({"tür": "durdurma", "sebep": "süre sınırı", "adım": k})
            break

    son_d = degerlendir(model, dog_gorev, ayar, 100, sinamadan=True)
    son_s = degerlendir(model, sin_gorev, ayar, 120, sinamadan=True)
    son_e = degerlendir(model, egt_gorev, ayar, 100, sinamadan=False)
    netice = {"tür": "netice", "adım": k,
              "süre_dk": round((time.time() - bas) / 60, 2),
              "eğitim_ızgara": son_e["ızgara"],
              "eğitim_çözülen": son_e["çözülen_sayı"],
              "doğrulama_ızgara": son_d["ızgara"],
              "doğrulama_çözülen": son_d["çözülen_sayı"],
              "doğrulama_çözülen_ad": son_d["çözülen_görev"],
              "sınama_ızgara": son_s["ızgara"],
              "sınama_çözülen": son_s["çözülen_sayı"],
              "sınama_çözülen_ad": son_s["çözülen_görev"],
              "belirteç_sn": round(toplam_belirtec
                                   / max(time.time() - bas, 1e-9), 1)}
    yaz(netice)
    torch.save({"model": model.state_dict(), "ayar": ayar.sozlugu(),
                "adım": k}, os.path.join(kayit_dizin, "son.pt"))
    gl.close()
    return netice


def ana(argv: Optional[Sequence[str]] = None) -> int:
    a = argparse.ArgumentParser()
    a.add_argument("--D", type=int, default=128)
    a.add_argument("--adim", type=int, default=20000)
    a.add_argument("--yigin", type=int, default=4)
    a.add_argument("--lr", type=float, default=3e-4)
    a.add_argument("--gunluk", default="egitim.jsonl")
    a.add_argument("--dizin", default="kayit")
    a.add_argument("--aralik", type=int, default=500)
    a.add_argument("--saat", type=float, default=6.0)
    a.add_argument("--baglam", type=int, default=2048)
    a.add_argument("--hedef", type=int, default=640)
    a.add_argument("--ornek", type=int, default=2)
    # ÖLÇÜLDÜ: 4 çekirdekli bu makinede iki torch süreci aynı anda
    # koşarken iş parçacıkları birbirini eziyor.  Tek bir çözümleme
    # adımı yüklü hâlde 658.8 ms sürüyordu; aynı adım
    # ``set_num_threads(1)`` ile 16.6 ms -- yani 40× fark ALGORİTMADAN
    # DEĞİL, iş parçacığı aşırı-abonesinden geliyordu.  Bu yüzden
    # eşzamanlı koşarken --iplik 1 verilmelidir.
    a.add_argument("--iplik", type=int, default=0,
                   help="torch iş parçacığı sayısı (0 = dokunma)")
    n = a.parse_args(argv)
    if n.iplik > 0:
        torch.set_num_threads(n.iplik)
    r = egit(D=n.D, adim=n.adim, yigin=n.yigin, ogrenme=n.lr,
             gunluk=n.gunluk, kayit_dizin=n.dizin,
             degerlendirme_araligi=n.aralik, azami_saat=n.saat,
             azami_baglam=n.baglam, azami_hedef=n.hedef,
             azami_baglam_ornek=n.ornek)
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(ana())

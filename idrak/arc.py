"""ARC-AGI-2 veri katmanı: yükleme, belirteçleme, bölme.

**Kaynak verisi.**

* ``idrak/veri/arc_agi_2`` — resmî `arcprize/ARC-AGI-2
  <https://github.com/arcprize/ARC-AGI-2>`_: **1000** kamuya açık eğitim
  görevi, **120** değerlendirme görevi.  Hakikat kaynağı budur.
* ``idrak/veri/soyutlamalar`` — `cristianoc/arc-agi-2-abstraction-dataset
  <https://github.com/cristianoc/arc-agi-2-abstraction-dataset>`_: 120
  değerlendirme görevinin **hepsi** için tabii lisanla yazılmış
  soyutlama notları (``abstractions.md``), tipli DSL ve çalışan Python
  çözücüsü (``solution.py``).  Kullanıcının istediği "sözlü algoritma"
  verisi budur.

**Bölme oranı -- neden 50/50 değil.**  Sınama kümesinin tek işi
hatanın *tarafsız bir kestirimini* vermektir; kestirimin standart
hatası ``≈ √(p(1−p)/n)`` ile ``n``e bağlıdır, eğitim kümesinin
büyüklüğüne değil.  120 görevlik bir sınamada bu ``≈ 4.6`` yüzde
puandır ve yeter.  Eğitim kümesini yarıya indirmek ise öğrenmeyi
doğrudan zayıflatır.  Alışılmış oran bu yüzden 80/20 ya da 90/10'dur;
50/50 yalnız veri **çok bol** ve model **çok küçük** olduğunda
savunulur.

Burada üstelik bölmeyi kendimiz uydurmuyoruz -- ARC'ın **kendi**
bölmesi var ve ona uyuyoruz:

============  =======  ===================================
küme          görev    kullanım
============  =======  ===================================
eğitim        900      ağırlık güncellemesi
doğrulama     100      durdurma ve ayar (eğitimden ayrık)
sınama        120      resmî değerlendirme, **hiç dokunulmaz**
============  =======  ===================================

Yani ``900/100/120`` ≈ **%80 / %9 / %11**.  Doğrulama, resmî eğitim
kümesinden ayrılır; resmî değerlendirme kümesi eğitimde **hiç
kullanılmaz**.

**Belirteçleme.**  Bir ızgara ``0-9`` renk hücrelerinden oluşur.
Sözlük::

    0-9   renkler
    10    satır sonu
    11    ızgara sonu
    12    girdi→çıktı ayıracı
    13    dolgu (kayıp maskelenir)
    14    örnek ayıracı

Bir görev örneği ``[girdi ızgarası] 12 [çıktı ızgarası] 11`` dizisidir.
Çok örnekli görevlerde önceki (girdi, çıktı) çiftleri **bağlam** olarak
öne konur: model kaideyi örneklerden çıkarmak zorundadır -- ARC'ın
meselesi budur.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "KOK", "RENK", "SATIR_SONU", "IZGARA_SONU", "AYIRAC", "DOLGU",
    "ORNEK_AYIRAC", "SOZLUK",
    "Gorev", "yukle", "yukle_hepsi", "bol",
    "izgara_belirtecle", "belirtec_izgara", "gorev_dizisi",
    "toplu_uret", "istatistik", "soyutlama_oku",
]

KOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "veri")
ARC = os.path.join(KOK, "arc_agi_2")
SOYUT = os.path.join(KOK, "soyutlamalar")

RENK = 10
SATIR_SONU = 10
IZGARA_SONU = 11
AYIRAC = 12
DOLGU = 13
ORNEK_AYIRAC = 14
SOZLUK = 15


@dataclass
class Gorev:
    """Bir ARC görevi: ``train`` çiftleri ve ``test`` çiftleri."""
    ad: str
    egitim: List[Tuple[np.ndarray, np.ndarray]]
    sinama: List[Tuple[np.ndarray, np.ndarray]]
    kaynak: str = ""

    def azami_kenar(self) -> int:
        k = 0
        for a, b in self.egitim + self.sinama:
            k = max(k, a.shape[0], a.shape[1], b.shape[0], b.shape[1])
        return k

    def sekil_sabit_mi(self) -> bool:
        """Girdi ve çıktı aynı şekilde mi? — en kolay sınıf."""
        return all(a.shape == b.shape for a, b in self.egitim + self.sinama)


def _cift(d) -> Tuple[np.ndarray, np.ndarray]:
    return (np.array(d["input"], dtype=np.int64),
            np.array(d["output"], dtype=np.int64))


def yukle(yol: str) -> Gorev:
    with open(yol, encoding="utf-8") as f:
        d = json.load(f)
    ad = os.path.splitext(os.path.basename(yol))[0]
    return Gorev(ad, [_cift(x) for x in d["train"]],
                 [_cift(x) for x in d["test"]],
                 os.path.basename(os.path.dirname(yol)))


def yukle_hepsi(kume: str = "training") -> List[Gorev]:
    """``training`` (1000) veya ``evaluation`` (120)."""
    dizin = os.path.join(ARC, kume)
    if not os.path.isdir(dizin):
        raise FileNotFoundError(
            "ARC verisi yok: %s  (idrak/veri/arc_agi_2 bekleniyor)" % dizin)
    return [yukle(os.path.join(dizin, ad))
            for ad in sorted(os.listdir(dizin)) if ad.endswith(".json")]


def bol(gorevler: Sequence[Gorev], dogrulama: int = 100, tohum: int = 0
        ) -> Tuple[List[Gorev], List[Gorev]]:
    """Resmî eğitim kümesini eğitim/doğrulama diye ayır.

    Karıştırma **sabit tohumludur**: aynı bölme her koşuda tekrarlanır,
    yoksa "doğrulama iyileşti" hükmü ölçülemez olur.
    """
    idx = np.random.default_rng(tohum).permutation(len(gorevler))
    d = [gorevler[int(i)] for i in idx[:dogrulama]]
    e = [gorevler[int(i)] for i in idx[dogrulama:]]
    return e, d


# ══════════════════════════════════════════════════════════════════════
#  Belirteçleme
# ══════════════════════════════════════════════════════════════════════

def izgara_belirtecle(g: np.ndarray) -> List[int]:
    """Izgara → belirteç dizisi (satır sonlarıyla)."""
    t: List[int] = []
    for satir in g:
        t.extend(int(v) for v in satir)
        t.append(SATIR_SONU)
    return t


def belirtec_izgara(t: Sequence[int]) -> Optional[np.ndarray]:
    """Belirteç dizisi → ızgara.  Bozuksa ``None``.

    **Sessizce onarmıyoruz**: satırlar eşit uzunlukta değilse ya da hiç
    hücre yoksa ``None`` dönüyor.  Yanlış bir ızgarayı "düzelterek"
    doğru saymak, tam eşleşme ölçütünü sahte kılardı.
    """
    satirlar: List[List[int]] = []
    cari: List[int] = []
    for v in t:
        v = int(v)
        if v in (IZGARA_SONU, AYIRAC, DOLGU, ORNEK_AYIRAC):
            break
        if v == SATIR_SONU:
            satirlar.append(cari)
            cari = []
        elif 0 <= v < RENK:
            cari.append(v)
        else:
            return None
    if cari:
        satirlar.append(cari)
    if not satirlar or not satirlar[0]:
        return None
    w = len(satirlar[0])
    if any(len(s) != w for s in satirlar):
        return None
    return np.array(satirlar, dtype=np.int64)


def gorev_dizisi(gorev: Gorev, hedef_indis: int = 0,
                 sinamadan: bool = False, azami_baglam: int = 3
                 ) -> Tuple[List[int], List[int]]:
    """``(bağlam, hedef)`` — bağlamda örnekler, hedefte istenen çıktı.

    Bağlam: ``girdi₁ 12 çıktı₁ 14 girdi₂ 12 çıktı₂ 14 … girdi* 12``
    Hedef : ``çıktı* 11``

    Model kaideyi **örneklerden** çıkarmak zorundadır; hedef ızgara
    bağlamda hiç geçmez.
    """
    # Hedef örnek bağlamdan ÇIKARILIR. (İlk hâlde çıkarmamıştım ve
    # kendi denetimim yakaladı: hedef ızgara bağlamda birebir geçiyordu,
    # yani model kaideyi öğrenmeden kopyalayarak "çözebilirdi".)
    if sinamadan:
        ornekler = gorev.egitim[:azami_baglam]
    else:
        ornekler = [c for k, c in enumerate(gorev.egitim)
                    if k != hedef_indis][:azami_baglam]
    baglam: List[int] = []
    for a, b in ornekler:
        baglam.extend(izgara_belirtecle(a))
        baglam.append(AYIRAC)
        baglam.extend(izgara_belirtecle(b))
        baglam.append(ORNEK_AYIRAC)
    kaynak = gorev.sinama if sinamadan else gorev.egitim
    if hedef_indis >= len(kaynak):
        raise IndexError("hedef indisi yok")
    gi, co = kaynak[hedef_indis]
    baglam.extend(izgara_belirtecle(gi))
    baglam.append(AYIRAC)
    hedef = izgara_belirtecle(co) + [IZGARA_SONU]
    return baglam, hedef


def toplu_uret(gorevler: Sequence[Gorev], azami_uzunluk: int,
               tohum: int = 0, azami_baglam: int = 3
               ) -> Iterator[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """``(dizi, hedef, maske)`` üçlüleri — sonsuz karışık akış.

    ``maske`` yalnız hedef bölgesinde 1'dir: kayıp **bağlamdan
    hesaplanmaz**, yoksa model kaideyi öğrenmek yerine bağlamı
    kopyalamayı öğrenir.
    """
    r = np.random.default_rng(tohum)
    sira = list(range(len(gorevler)))
    while True:
        r.shuffle(sira)
        for i in sira:
            g = gorevler[i]
            for j in range(len(g.egitim)):
                try:
                    b, h = gorev_dizisi(g, j, False, azami_baglam)
                except IndexError:
                    continue
                dizi = b + h
                if len(dizi) > azami_uzunluk:
                    continue
                n = len(dizi)
                x = np.full(azami_uzunluk, DOLGU, dtype=np.int64)
                m = np.zeros(azami_uzunluk, dtype=np.float64)
                x[:n] = dizi
                m[len(b):n] = 1.0
                yield x, np.roll(x, -1), m


def istatistik(gorevler: Sequence[Gorev]) -> Dict[str, object]:
    kenar, uzunluk, sabit = [], [], 0
    for g in gorevler:
        kenar.append(g.azami_kenar())
        sabit += g.sekil_sabit_mi()
        try:
            b, h = gorev_dizisi(g, 0)
            uzunluk.append(len(b) + len(h))
        except IndexError:
            pass
    return {"görev": len(gorevler),
            "azamî_kenar_ortalama": float(np.mean(kenar)),
            "azamî_kenar_en_büyük": int(np.max(kenar)),
            "dizi_uzunluğu_ortanca": float(np.median(uzunluk)),
            "dizi_uzunluğu_p90": float(np.percentile(uzunluk, 90)),
            "dizi_uzunluğu_en_büyük": int(np.max(uzunluk)),
            "şekli_sabit_görev": sabit,
            "şekli_sabit_oran": sabit / max(len(gorevler), 1)}


def soyutlama_oku(ad: str) -> Optional[str]:
    """Bir değerlendirme görevinin **sözlü algoritmasını** oku."""
    yol = os.path.join(SOYUT, ad, "abstractions.md")
    if not os.path.exists(yol):
        return None
    with open(yol, encoding="utf-8") as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s = []
    egt = yukle_hepsi("training")
    dgr = yukle_hepsi("evaluation")
    s.append("=== ARC-AGI-2 verisi ===")
    s.append("  resmî eğitim: %d görev   resmî değerlendirme: %d görev"
             % (len(egt), len(dgr)))
    e, d = bol(egt)
    s.append("  bölme: eğitim %d / doğrulama %d / sınama %d  "
             "(%.0f%% / %.0f%% / %.0f%%)"
             % (len(e), len(d), len(dgr),
                100 * len(e) / (len(e) + len(d) + len(dgr)),
                100 * len(d) / (len(e) + len(d) + len(dgr)),
                100 * len(dgr) / (len(e) + len(d) + len(dgr))))
    s.append("  Sınama kümesi 120 görev → hata kestiriminin standart")
    s.append("  hatası ≈ √(p(1−p)/120) ≈ %.1f puan. 50/50 bölmek eğitimi"
             % (100 * math.sqrt(0.25 / 120)))
    s.append("  yarıya indirirdi, kestirimi ise ancak %.1f puana iyileştirirdi."
             % (100 * math.sqrt(0.25 / 560)))

    for ad, k in (("eğitim", e), ("doğrulama", d), ("sınama", dgr)):
        i = istatistik(k)
        s.append("  %-10s kenar ort=%.1f azm=%d   dizi ortanca=%.0f "
                 "p90=%.0f azm=%d   şekli sabit=%d (%.0f%%)"
                 % (ad, i["azamî_kenar_ortalama"], i["azamî_kenar_en_büyük"],
                    i["dizi_uzunluğu_ortanca"], i["dizi_uzunluğu_p90"],
                    i["dizi_uzunluğu_en_büyük"], i["şekli_sabit_görev"],
                    100 * i["şekli_sabit_oran"]))

    s.append("\n=== Belirteçleme gidiş-dönüşü kayıpsız mı? ===")
    hata = 0
    for g in egt[:200]:
        for a, b in g.egitim:
            if not np.array_equal(belirtec_izgara(izgara_belirtecle(a)), a):
                hata += 1
    s.append("  200 görevin bütün ızgaralarında gidiş-dönüş hatası: %d" % hata)

    s.append("\n=== Bozuk diziyi sessizce onarmıyoruz ===")
    for ad, t in (("eşit olmayan satır", [1, 2, SATIR_SONU, 3, SATIR_SONU]),
                  ("hiç hücre yok", [SATIR_SONU]),
                  ("geçersiz belirteç", [1, 99, SATIR_SONU])):
        s.append("  %-20s → %s" % (ad, belirtec_izgara(t)))

    s.append("\n=== Sözlü algoritma (soyutlama) verisi ===")
    var = sum(soyutlama_oku(g.ad) is not None for g in dgr)
    s.append("  120 değerlendirme görevinin %d'sinde sözlü algoritma var"
             % var)
    ornek = soyutlama_oku(dgr[0].ad)
    if ornek:
        s.append("  örnek (%s):" % dgr[0].ad)
        for satir in ornek.strip().splitlines()[:3]:
            s.append("    " + satir[:96])

    s.append("\n=== Bir görevin bağlam/hedef dizisi ===")
    g = egt[0]
    b, h = gorev_dizisi(g, 0)
    s.append("  görev %s: bağlam %d belirteç, hedef %d belirteç"
             % (g.ad, len(b), len(h)))
    sizinti = 0
    for gg in egt[:300]:
        for j in range(len(gg.egitim)):
            bb, hh = gorev_dizisi(gg, j)
            hedef = hh[:-1]
            if any(bb[i:i + len(hedef)] == hedef
                   for i in range(max(0, len(bb) - len(hedef) + 1))):
                sizinti += 1
    s.append("  300 görevin bütün hedeflerinde bağlam sızıntısı: %d"
             % sizinti)
    s.append("  (Hedef örnek bağlamdan çıkarılıyor; çıkarılmasaydı model")
    s.append("   kaideyi öğrenmeden KOPYALAYARAK çözerdi.)")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())

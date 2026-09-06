"""
RÜŞT KİLİDİ -- ÇİZELGE (TAKVİM) **VE** ÖLÇÜ (MUAYENE)

===================================================================
ESKİ USUL İMHA EDİLDİ: KÖR TAKVİM
===================================================================

Evvelce rüşt yalnız bir takvimdi (``nefs/kulli_mizan.py:rust``)::

    α(t) = σ((t/T − t₀)/τ)

Vakit gelince fıtrat kilitleniyor, hata hafızaya fatura edilmeye
başlıyordu. **Fakat vakit bir olgunluk delili değildir.** Topolojisi
yırtık -- yâni mantığında kapanmamış deliği olan -- bir dimağ da
takvime bakarak rüşte eriyordu. O usul bu turda imha edildi (ferman
1-E: yarım iş yasak; yeni usul geldiyse eskisi aynı turda kesilir).

===================================================================
KAT'Î HÜKÜM: ASENKRON EŞİK-KORUMALI HİBRİT RÜŞT FONKSİYONU
===================================================================

    α_rüşt(t) = σ((t − t₀)/τ) · exp( −(‖dF(t)‖²_DEC + ‖H¹(U;F)‖²)
                                     / σ²_kapanış )

İki çarpan, iki ayrı soru:

* **σ(·) -- TAKVİM.** "Vakti geldi mi?" Adyabatik faz geçişi; keskin
  bir aç-kapa anahtarı değil.
* **exp(·) -- MUAYENE.** "Yırtık kapandı mı?" ``dF`` ayrık dış türevin
  artığıdır (morfizm alanı kapalı mı), ``H¹`` birinci kohomolojinin
  boyudur (çevrimlerde kapanmamış delik sayısı). İkisi de sıfıra
  inmedikçe üs sıfıra inmez ve ``α`` **kilitli** kalır.

Yâni: vakit gelse de yırtık kapanmadıkça fıtrat serbest bırakılmaz.

===================================================================
FERMAN 7-D: HODGE/KOHOMOLOJİ AYRIK TAŞIYICIDA
===================================================================

Zabıtlar ``H¹``i sürekli de Rham kohomolojisiyle yazar. Yeni nesil
taşıyıcıda tam karşılığı ``GF(2)`` üstünde simplisyel kohomolojidir --
ve bu bir yaklaştırma değil, aynı sayıdır (Betti sayısı ``mod 2``):

    ∂₁ : kenarlar → köşeler        (n_kenar × n_köşe, GF(2))
    ∂₂ : üçgenler → kenarlar       (n_üçgen × n_kenar, GF(2))

    dim H¹ = dim ker ∂₁ − rank ∂₂
           = (n_kenar − rank ∂₁) − rank ∂₂

Rank ``GF(2)`` Gauss elemesiyle bulunur: **tamsayı XOR**, kayan nokta
yok, SVD yok (SVD zaten fermanla iptal).

``‖dF‖²_DEC`` ise morfizm alanının ayrık dış türevidir: her üçgen
``(a,b,c)`` için ``F(a→b) ⊕ F(b→c) ⊕ F(c→a)`` sıfır olmalıdır (kapalı
form). Olmayan üçgenlerin nispeti ``‖dF‖²``dir.

===================================================================
ÖLÇÜ KIRMIZI YANABİLİR (FERMAN 5)
===================================================================

``RustAyari.muayene = 0`` denince ikinci çarpan ``1`` olur ve eski kör
takvim geri gelir. Rapor bunu yazar: kapı KAPALI. Yâni yeni tedbirin
faydası -- yırtık varken rüştün kilitli kalması -- ölçülebilir bir
şeydir, iddia değil.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["RustAyari", "gf2_rank", "sinir_operatorleri",
           "topolojik_yirtik", "rust_kilidi"]


@dataclass
class RustAyari:
    """Rüşt kilidinin ölçüleri."""

    #: Takvimin ortası (tur nispetiyle).
    t0: float = 0.5
    #: Takvimin genişliği.
    tau: float = 0.15
    #: ``σ_kapanış`` -- muayene kapısının genişliği. Küçüldükçe sertleşir.
    kapanis: float = 0.5
    #: ``0`` = muayene KAPALI: yalnız takvim (eski kör hâl).
    muayene: int = 1
    #: Tâlimin toplam adım kestirimi -- takvimin paydası.
    toplam_adim: int = 200

    def __post_init__(self) -> None:
        assert float(self.tau) > 0.0, "takvim genişliği sıfır olamaz"
        assert float(self.kapanis) > 0.0, (
            "σ_kapanış sıfır olamaz: sıfıra bölme. Muayeneyi kapatmak "
            "için ``muayene=0`` denir")


def gf2_rank(M: np.ndarray) -> int:
    """``GF(2)`` üstünde rank -- **XOR ile Gauss elemesi**.

    Kayan nokta yoktur, SVD yoktur (ferman 7: SVD iptal). Satırlar
    ``uint8`` bit dizileridir; eleme tek ``^=`` ile yürür.
    """
    A = (np.asarray(M) & 1).astype(np.uint8).copy()
    if A.size == 0:
        return 0
    satir, sutun = A.shape
    r = 0
    for c in range(sutun):
        pivot = -1
        for i in range(r, satir):
            if A[i, c]:
                pivot = i
                break
        if pivot < 0:
            continue
        if pivot != r:
            A[[r, pivot]] = A[[pivot, r]]
        vur = A[:, c].astype(bool).copy()
        vur[r] = False
        A[vur] ^= A[r]
        r += 1
        if r == satir:
            break
    return int(r)


def sinir_operatorleri(baglamlar: Sequence[Sequence[int]], n: int
                       ) -> Tuple[np.ndarray, np.ndarray,
                                  List[Tuple[int, int]],
                                  List[Tuple[int, int, int]]]:
    """``(∂₁, ∂₂, kenarlar, üçgenler)`` -- veriden kurulan simplisyel kompleks.

    Köşeler belirteçlerdir (``n`` tane). Bir bağlamda beraber geçen her
    ikili bir **kenar**, her üçlü bir **üçgen**tir: yâni kompleks
    veriden okunur, elle kurulmaz (ferman 6).

    ``∂₁`` kenardan köşeye, ``∂₂`` üçgenden kenaradır; ikisi de
    ``GF(2)``de ``0/1``dir (karakteristik 2'de işaret yoktur).
    """
    n = int(n)
    kenar_no: Dict[Tuple[int, int], int] = {}
    ucgen: List[Tuple[int, int, int]] = []
    gorulen = set()
    # **BAĞLAMLAR EVVELA TEKİLLEŞTİRİLİR.** Kompleks yalnız *hangi
    # belirteçlerin beraber göründüğüne* bakar; aynı belirteç kümesini
    # taşıyan bin bağlam aynı kenarları ve aynı üçgenleri verir. Evvelce
    # her bağlam tek tek taranıyordu ve ``pencere=512``de bu, kayıp
    # çağrısının **%90'ını** yiyordu (ölçüldü: 10,17 sn / 11,3 sn).
    # Sözlük 16 olduğu için tekil küme sayısı en çok 2¹⁶'dır ve fiilen
    # bir avuçtur.
    kumeler = {tuple(sorted(set(int(x) % n for x in bag)))
               for bag in baglamlar}
    for t in kumeler:
        for i in range(len(t)):
            for j in range(i + 1, len(t)):
                kenar_no.setdefault((t[i], t[j]), len(kenar_no))
        for i in range(len(t)):
            for j in range(i + 1, len(t)):
                for k in range(j + 1, len(t)):
                    u = (t[i], t[j], t[k])
                    if u not in gorulen:
                        gorulen.add(u)
                        ucgen.append(u)
    kenarlar = [k for k, _ in sorted(kenar_no.items(), key=lambda x: x[1])]
    d1 = np.zeros((len(kenarlar), n), np.uint8)
    for e, (a, b) in enumerate(kenarlar):
        d1[e, a] = 1
        d1[e, b] = 1
    d2 = np.zeros((len(ucgen), len(kenarlar)), np.uint8)
    for f, (a, b, c) in enumerate(ucgen):
        for kenar in ((a, b), (b, c), (a, c)):
            d2[f, kenar_no[kenar]] = 1
    return d1, d2, kenarlar, ucgen


def topolojik_yirtik(baglamlar: Sequence[Sequence[int]], n: int,
                     morfizm: Optional[np.ndarray] = None
                     ) -> Dict[str, Any]:
    """``(‖dF‖²_DEC , ‖H¹‖²)`` -- muayenenin iki sayısı.

    ``morfizm`` verilirse ``(n, n)`` bir ``GF(2)`` alanıdır:
    ``F(a→b)``. Verilmezse morfizm **veriden** okunur: ``a`` ile ``b``
    beraber görüldüyse ``F(a→b) = 1``. İkinci hâlde ``dF``, kompleksin
    kendi kapalılığını ölçer.
    """
    n = int(n)
    d1, d2, kenarlar, ucgen = sinir_operatorleri(baglamlar, n)
    n_kenar = len(kenarlar)
    if n_kenar == 0:
        # Kenar yoksa çevrim de yoktur: yırtık sıfırdır ve bu bir
        # hüküm değil, boş bir kompleksin tabiî hâlidir.
        return {"h1": 0, "dF_dec": 0.0, "kenar": 0, "üçgen": 0,
                "rank_d1": 0, "rank_d2": 0, "kopuk": 0}
    r1 = gf2_rank(d1)
    r2 = gf2_rank(d2) if len(ucgen) else 0
    # dim H¹ = dim ker ∂₁ − rank ∂₂
    h1 = max(0, (n_kenar - r1) - r2)

    if morfizm is None:
        # **MORFİZM VERİDEN OKUNUR VE YÖNLÜDÜR.**
        #
        # Evvelce burada ``F[a,b] = F[b,a] = 1`` (kenar var mı) yazıyordu
        # ve o ölçü **hiçbir zaman yeşil yanamazdı**: her üçgende
        # ``1 ⊕ 1 ⊕ 1 = 1``, yâni ``‖dF‖²`` daima tam 1. Ölçüldü ve
        # düzeltildi (ferman 5: yanamayan ölçü bir şey ölçmüyordur).
        #
        # Doğrusu **yön**dür: ``F(a→b) = 1`` ancak ``a``, ``b``den önce
        # geliyorsa. O zaman üçgen çevrimi::
        #
        #     sıralı  a<b<c :  F(a→b)=1, F(b→c)=1, F(c→a)=0  → ⊕ = 0
        #     devirli a<b<c<a: F(a→b)=1, F(b→c)=1, F(c→a)=1  → ⊕ = 1
        #
        # Yâni ``dF``, morfizm alanının **geçişli (transitif)** olup
        # olmadığını ölçer: kapalı form, devirsiz sıralamadır.
        # **PYTHON DÖNGÜSÜ YOK (ferman 7).** "``a``, ``b``den kaç kere
        # önce geldi" sayımı ikili döngüyle ``O(Σ L²)``dir ve
        # ``pencere=512``de kayıp çağrısının tamamını yer. Aynı sayı,
        # birikimli toplamla ``O(L·n)``de çıkar ve tek çarpıma iner::
        #
        #     M      : (L, n) tek-sıcak
        #     onceki : cumsum(M) − M      (her mevkiden ÖNCEKİ sayımlar)
        #     onde   = onceki.T @ M
        onde = np.zeros((n, n), np.int64)
        for bag in baglamlar:
            t = np.asarray(list(bag), np.int64) % n
            if t.size < 2:
                continue
            M = np.zeros((t.size, n), np.int64)
            M[np.arange(t.size), t] = 1
            onceki = np.cumsum(M, axis=0) - M
            onde += onceki.T @ M
        np.fill_diagonal(onde, 0)
        F = (onde > onde.T).astype(np.uint8)
    else:
        F = (np.asarray(morfizm) & 1).astype(np.uint8)
        assert F.shape == (n, n), "morfizm alanı (n, n) olmalı"

    # ``dF`` -- her üçgende çevrimin kapanışı: F(a→b) ⊕ F(b→c) ⊕ F(c→a)
    acik = 0
    for (a, b, c) in ucgen:
        if (int(F[a, b]) ^ int(F[b, c]) ^ int(F[c, a])) & 1:
            acik += 1
    dF = float(acik) / float(max(1, len(ucgen)))
    return {"h1": int(h1), "dF_dec": float(dF * dF), "kenar": n_kenar,
            "üçgen": len(ucgen), "rank_d1": r1, "rank_d2": r2,
            "kopuk": int(n - r1)}


def rust_kilidi(adim: int, dF_dec: float, h1: int,
                ayar: Optional[RustAyari] = None) -> Dict[str, float]:
    """``α_rüşt(t) = σ((t−t₀)/τ) · exp(−(‖dF‖² + ‖H¹‖²)/σ²_kapanış)``.

    Dönen sözlükte üç sayı ayrı ayrı durur -- ``takvim``, ``muayene``,
    ``α`` -- çünkü ``α``nın niçin küçük kaldığı (vakit mi gelmedi,
    yırtık mı kapanmadı) rapordan okunabilmelidir.
    """
    a = ayar or RustAyari()
    T = max(1, int(a.toplam_adim))
    u = (float(adim) / T - float(a.t0)) / float(a.tau)
    u = float(np.clip(u, -60.0, 60.0))
    takvim = float(1.0 / (1.0 + math.exp(-u)))

    if not int(a.muayene):
        # **KAPI KAPALI:** eski kör takvim. Rapor bunu yazar.
        return {"takvim": takvim, "muayene": 1.0, "α": takvim,
                "dF_dec": float(dF_dec), "h1": float(int(h1))}

    # ``‖H¹‖²`` -- kohomoloji boyunun karesi. Tek bir kapanmamış delik
    # bile üssü küçültür; ikisi dörde katlar.
    yirtik = float(dF_dec) + float(int(h1)) ** 2
    us = -yirtik / (float(a.kapanis) ** 2)
    muayene = float(math.exp(max(us, -700.0)))
    return {"takvim": takvim, "muayene": muayene,
            "α": float(takvim * muayene),
            "dF_dec": float(dF_dec), "h1": float(int(h1))}

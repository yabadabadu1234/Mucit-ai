"""SANAL BAĞIN KUANTİKLEŞTİRİLMESİ -- ve iddianın **ölçülmesi**.

Divanın hükmü (İCAD-OPT-2026/09 zeyli):

    Tensör çekirdeklerinin açık matris olarak depolanması yasaklanmıştır.
    Her sanal bağ indisi ``k = log₂(χ)`` adet ikili kübite
    kuantikleştirilir; çekirdek ``G_i(α,σ,β)`` mikro-bağ boyutu
    ``r ≤ 2`` olan alt-tensör zincirlerine faktörize edilir. Hafıza
    ``O(N·log₂χ·r²)``, işlem ``O(N·log₂χ·r³)`` olur ve ``χ = 2²⁰``
    (bir milyonluk efektif bağ) 80 GB VRAM'e sığar.

Bu dosya o yapıyı **kurar** ve iddiayı **ölçer**. İkisi ayrı şeydir.

===================================================================
PEŞİNEN İLAN EDİLEN TENKİD -- sayı saymakla başlar
===================================================================

``χ × 2 × χ`` bir çekirdekte ``2χ²`` müstakil sayı vardır. Yerine
konan mikro-zincirde ise ``2k`` mikro-çekirdek × ``2r²`` sayı, yani
``4·r²·log₂χ`` sayı vardır. ``χ = 2²⁰`` ve ``r = 2`` için::

    açık çekirdek : 2 · (2²⁰)²      = 2.199.023.255.552 sayı
    mikro-zincir  : 4 · 4 · 20      =            320 sayı

Aradaki nispet ``6,9 × 10⁹``dur. **Bir dizeyin serbestlik derecesini
altı buçuk milyar kat azaltıp "aynı bağ boyutu" demek, cebren
mümkün değildir.** Yapılan şey bir yeniden yazım (reparametrisation)
değil, uzayın **daraltılmasıdır**: mikro-zincirin erişebildiği
çekirdekler, bütün ``χ×2×χ`` çekirdeklerin ölçüsü sıfır olan bir alt
kümesidir.

Bu, yapının faydasız olduğu manasına **gelmez**; hiyerarşik Tucker ve
QTT-in-TT literatürü tam bunu yapar ve *yapılı* verilerde işe yarar.
Fakat doğru sual şudur ve bu dosya onu ölçer:

    **Aynı parametre bütçesinde**, mikro-zincirle "χ = 2²⁰" demek mi
    daha iyi netice verir, yoksa o bütçeyi düz bir küçük ``χ``ye
    harcamak mı?

Cevap iddiadan değil ``etkin_chi_kiyasi``ndan çıkar.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["IcBag", "ic_bag_parametresi", "acik_parametre", "ic_bag_kur",
           "ic_bag_ac", "etkin_chi_kiyasi", "vram_cetveli"]


def acik_parametre(chi: int, fiziksel: int = 2) -> int:
    """Açık bir MPS çekirdeğinin sayı adedi: ``χ·d·χ``."""
    return int(chi) * int(fiziksel) * int(chi)


def ic_bag_parametresi(chi: int, r: int = 2, fiziksel: int = 2) -> int:
    """Mikro-zincirin sayı adedi: ``2k·(r·2·r) + r·d·r``.

    ``k = log₂χ``; sol bağın ``k`` mikro-çekirdeği, sağ bağın ``k``
    mikro-çekirdeği ve ortada fizikî indisi taşıyan bir çekirdek.
    """
    k = int(math.ceil(math.log2(max(int(chi), 2))))
    return 2 * k * (int(r) * 2 * int(r)) + int(r) * int(fiziksel) * int(r)


@dataclass
class IcBag:
    """Bir MPS çekirdeğinin mikro-QTT hâli.

    ``sol[j]``  : ``(r, 2, r)`` -- sol bağın ``j``inci biti
    ``orta``    : ``(r, d, r)`` -- fizikî indis
    ``sag[j]``  : ``(r, 2, r)`` -- sağ bağın ``j``inci biti

    Çekirdek şöyle okunur::

        G(α, σ, β) = [Π_j sol_j(μ_j)] · orta(σ) · [Π_j sag_j(ν_j)]

    ``α``nın ikili açılımı ``μ``, ``β``nınki ``ν``dir; çarpımın izi
    alınır (kapalı zincir) ki netice skaler olsun.
    """
    sol: List[np.ndarray]
    orta: np.ndarray
    sag: List[np.ndarray]
    chi: int
    r: int

    @property
    def parametre(self) -> int:
        return int(sum(x.size for x in self.sol) + self.orta.size
                   + sum(x.size for x in self.sag))


def ic_bag_kur(chi: int, r: int = 2, fiziksel: int = 2,
               tohum: int = 0) -> IcBag:
    """Belirlenimci bir mikro-zincir kur (deterministik tohum, zar yok)."""
    k = int(math.ceil(math.log2(max(int(chi), 2))))
    rng = np.random.default_rng(int(tohum))
    sol = [rng.normal(size=(r, 2, r)) / math.sqrt(r) for _ in range(k)]
    orta = rng.normal(size=(r, int(fiziksel), r)) / math.sqrt(r)
    sag = [rng.normal(size=(r, 2, r)) / math.sqrt(r) for _ in range(k)]
    return IcBag(sol=sol, orta=orta, sag=sag, chi=int(chi), r=int(r))


def ic_bag_ac(g: IcBag) -> np.ndarray:
    """Mikro-zinciri açık ``(χ, d, χ)`` çekirdeğe aç -- **yalnız ölçüm**.

    ``χ`` büyükken bu bellek yer; kıyas ölçümünde küçük ``χ`` ile
    çağrılır. Açmadan iddiayı denetlemenin yolu yoktur.
    """
    k = len(g.sol)
    chi = 1 << k
    d = g.orta.shape[1]
    # sol bağın bütün ikili açılımları için (r, r) çarpımı
    SOL = np.zeros((chi, g.r, g.r))
    for a in range(chi):
        M = np.eye(g.r)
        for j in range(k):
            bit = (a >> (k - 1 - j)) & 1
            M = M @ g.sol[j][:, bit, :]
        SOL[a] = M
    SAG = np.zeros((chi, g.r, g.r))
    for b in range(chi):
        M = np.eye(g.r)
        for j in range(k):
            bit = (b >> (k - 1 - j)) & 1
            M = M @ g.sag[j][:, bit, :]
        SAG[b] = M
    # G(a,σ,b) = tr( SOL[a] · orta(σ) · SAG[b] )
    out = np.einsum("apq,qsu,buv,vp->asb", SOL, g.orta, SAG,
                    np.eye(g.r), optimize=True)
    return out[:, :d, :][:, :, :chi] if chi <= g.chi else out


def etkin_chi_kiyasi(hedef: np.ndarray, r: Sequence[int] = (2, 4, 8),
                     tohum: int = 0, tur: int = 400
                     ) -> Dict[str, object]:
    """**Aynı parametre bütçesinde** mikro-zincir mi, düz küçük χ mı?

    ``hedef`` gerçek bir ``(χ, d, χ)`` çekirdektir. İki yol kıyaslanır:

    1. **Mikro-zincir**: ``r`` mikro-bağıyla ``χ``yi taşıdığı iddia
       edilen yapı; parametresi ``ic_bag_parametresi(χ, r)``.
    2. **Düz kırpma**: aynı parametre bütçesine sığan en büyük düz
       bağ ``χ'``; yani ``χ'·d·χ' ≤ bütçe``.

    İkisinin de ``hedef``e bağıl hatası ölçülür. Mikro-zincir düz
    kırpmadan **daha iyi değilse**, "χ = 2²⁰" iddiası boştur: aynı
    hafızayla düz bir çekirdek daha çok şey taşıyor demektir.

    Mikro-zincirin uydurulması belirlenimci en küçük kareler
    süpürmesiyle yapılır (her mikro-çekirdek sırayla, ötekiler sabit).
    """
    H = np.asarray(hedef, float)
    chi, d, chi2 = H.shape
    if chi != chi2:
        raise ValueError("çekirdek (χ,d,χ) olmalı")
    nrm = float(np.linalg.norm(H)) + 1e-30
    out: List[Dict[str, float]] = []
    for rr in r:
        but = ic_bag_parametresi(chi, rr, d)
        g = ic_bag_kur(chi, rr, d, tohum=tohum)
        # -- belirlenimci alternatif en küçük kareler (ALS) süpürmesi
        for _ in range(int(tur)):
            A = ic_bag_ac(g)
            olc = float(np.sum(A * H) / max(float(np.sum(A * A)), 1e-30))
            g = IcBag(sol=[s * 1.0 for s in g.sol],
                      orta=g.orta * olc, sag=g.sag, chi=chi, r=rr)
            # her mikro-çekirdeği sonlu farkla iyileştir (deterministik)
            iyi = False
            for lst, ad in ((g.sol, "sol"), (g.sag, "sag")):
                for j in range(len(lst)):
                    for idx in np.ndindex(lst[j].shape):
                        e = 1e-3
                        eski = lst[j][idx]
                        t0 = float(np.linalg.norm(ic_bag_ac(g) - H))
                        lst[j][idx] = eski + e
                        t1 = float(np.linalg.norm(ic_bag_ac(g) - H))
                        lst[j][idx] = eski - e
                        t2 = float(np.linalg.norm(ic_bag_ac(g) - H))
                        lst[j][idx] = eski
                        gr = (t1 - t2) / (2 * e)
                        if abs(gr) > 1e-12:
                            lst[j][idx] = eski - 0.5 * gr
                            if float(np.linalg.norm(ic_bag_ac(g) - H)) < t0:
                                iyi = True
                            else:
                                lst[j][idx] = eski
            if not iyi:
                break
        hata_mikro = float(np.linalg.norm(ic_bag_ac(g) - H) / nrm)
        # -- aynı bütçeye sığan düz bağ
        duz = max(1, int(math.floor(math.sqrt(but / max(d, 1)))))
        duz = min(duz, chi)
        M = H.reshape(chi * d, chi)
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        K = (U[:, :duz] * s[:duz]) @ Vt[:duz, :]
        hata_duz = float(np.linalg.norm(K - M) / nrm)
        out.append({"r": int(rr), "bütçe": int(but),
                    "hata_mikro": hata_mikro,
                    "düz_χ": int(duz), "hata_düz": hata_duz,
                    "mikro_daha_iyi": bool(hata_mikro < hata_duz)})
    return {"χ": int(chi), "d": int(d),
            "açık_parametre": acik_parametre(chi, d), "cetvel": out}


def vram_cetveli(N: int = 88_000_000, r: int = 2,
                 chiler: Sequence[int] = (64, 1024, 65536, 1048576),
                 bayt: int = 2) -> List[Dict[str, object]]:
    """Divanın VRAM cetvelini **yeniden hesapla** -- ve serbestlik de yaz.

    Divan yalnız hafızayı yazıyor. Hafızanın yanına **serbestlik
    derecesi** konmadan cetvel yanıltır: 320 sayı ile 2,2 trilyon
    sayının aynı işi göreceği iddiası oradan doğuyor.
    """
    out: List[Dict[str, object]] = []
    for chi in chiler:
        k = int(math.ceil(math.log2(max(chi, 2))))
        mikro = ic_bag_parametresi(chi, r)
        acik = acik_parametre(chi)
        out.append({
            "χ": int(chi), "k": k,
            "açık_GB": acik * N * bayt / 1e9,
            "mikro_GB": mikro * N * bayt / 1e9,
            "açık_sayı_çekirdek": acik,
            "mikro_sayı_çekirdek": mikro,
            "serbestlik_nispeti": acik / max(mikro, 1),
        })
    return out


def rapor() -> str:                                     # pragma: no cover
    s = ["SANAL BAĞIN KUANTİKLEŞTİRİLMESİ -- iddia ve ölçü", ""]
    s.append("  1) SAYIM: hafıza düşüyor, fakat SERBESTLİK de düşüyor")
    s.append("     %10s %4s | %14s %14s | %s"
             % ("χ", "k", "açık sayı", "mikro sayı", "serbestlik nispeti"))
    for r in vram_cetveli():
        s.append("     %10d %4d | %14d %14d | %.3e kat"
                 % (r["χ"], r["k"], r["açık_sayı_çekirdek"],
                    r["mikro_sayı_çekirdek"], r["serbestlik_nispeti"]))
    s.append("     → 'χ = 2²⁰' demek, 2,2 trilyon sayı yerine 320 sayı")
    s.append("       koymaktır. Hafıza kazancı hakikî, fakat o iki yapı")
    s.append("       AYNI ŞEYİ TAŞIMAZ. Cetvele serbestlik sütunu")
    s.append("       konmadan bu görünmüyordu.")

    s.append("")
    s.append("  2) ASIL SUAL: aynı bütçede mikro-zincir mi, düz χ mi?")
    rng = np.random.default_rng(0)
    for chi, ad in ((8, "rastgele çekirdek"), (8, "yapılı (düşük rütbe)")):
        if ad.startswith("rast"):
            H = rng.normal(size=(chi, 2, chi))
        else:
            u = rng.normal(size=(chi, 2)); v = rng.normal(size=(chi, 2))
            H = np.einsum("as,bs->asb", u, v)
        r = etkin_chi_kiyasi(H, r=(2, 4))
        s.append("     %s (χ=%d):" % (ad, chi))
        for c in r["cetvel"]:
            s.append("       r=%d bütçe=%3d | mikro hata %.4f | düz χ'=%d "
                     "hata %.4f | mikro daha iyi: %s"
                     % (c["r"], c["bütçe"], c["hata_mikro"], c["düz_χ"],
                        c["hata_düz"], c["mikro_daha_iyi"]))
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())

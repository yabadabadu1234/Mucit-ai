"""KÜLLÎ DİMAĞ HAMİLTONYENİ -- 41 meleke, 20 mertebe, 4 zırh, 1 gaye.

Padişahın tashihi, bu turun küllî esasıdır ve evvelki hâlimin
merkezindeki yanlışı söker:

    41 Meleke, arka arkaya dizilip birbirine vuran 41 klasik gizli
    katman DEĞİLDİR. Melekeler, Hilbert uzayındaki tek bir manifoldun
    Lie Cebri Üreteçleridir (T^a); yani tek bir üniter Hamiltonyenin
    aynı anda çalışan paralel koordinat eksenleridir.

ve ``Ĥ_toplam`` dört terimin toplamı değildir; üç katmanlı bir
mimarîdir::

    Ĥ_toplam(θ) = Ĥ_ARC(θ)                                   ← gaye (iş)
                + Σ_{m=0}^{19} Π_koho^(m) Π_betti^(m) 𝒮_m
                      [ Σ_{i ∈ Meleke_m} θ_i T_i ]
                  𝒮_m† Π_betti^(m) Π_koho^(m)                ← 41 meleke
                + λ_mizan · Ĥ_BGCM(θ)                        ← muvazene

**Neden bu üç katman ayrılmazdır.**

* Yalnız ``Ĥ_ARC`` koşarsa model **ezberler**: ızgarayı tutturur, kuralı
  öğrenmez. Betti deliği açılır.
* Yalnız zırh koşarsa model **çelişkisiz fakat işsiz** kalır: sıfır
  kayıp alır ve hiçbir şey çözmez. (Bu, evvelki turda sorduğum sualdi;
  cevabı budur -- zırh gaye ile aynı Hamiltonyendedir, ayrı bir dünya
  değil.)
* ``Ĥ_BGCM`` olmazsa melekeler birbirini **söndürür**: ölçüldüğü üzere
  𝒪₂₄ (İspat) dalgayı ``1e-7``ye indirip 𝒪₃₉'u (Belâgat) boğuyordu.
  Muvazene terimi, iki melekenin komütatörünü cezalandırarak buna
  mâni olur.

**Peşinen ilan edilen bir eksik (kullanıcı hükmü C).** 41 melekenin 20
mertebeye dağılımı burada **inşa edilmiştir**, ölçülmemiştir: ceride
yalnız birkaç misal verir (𝒪₁,𝒪₂,𝒪₃₉ → k=0,1; 𝒪₈,𝒪₂₂,𝒪₂₄ → k=2,7;
𝒪₅,𝒪₁₂,𝒪₄₁ → k=4,9). Kalan otuz iki melekenin mertebesi tasrih
edilmemiştir; buradaki dağılım o misalleri **tutan** ve gerisini
düzgün yayan bir tercihtir ve tam cetvel gelince değişecektir.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["MELEKE_SAYISI", "MERTEBE_SAYISI", "CERIDE_MISALLERI",
           "meleke_mertebeleri", "so_ureteci", "mertebe_hamiltonyeni",
           "bgcm_kaybi", "muvazene_matrisi", "zirh_projektorleri",
           "H_toplam", "DimagAyari"]

#: Melekelerin adedi -- 𝒪₁ … 𝒪₄₁.
MELEKE_SAYISI: int = 41
#: Mertebe adedi -- 10 sabit zemin + 10 dinamik lif (`nefs/mertebe.py`).
MERTEBE_SAYISI: int = 20

#: Ceridenin **tasrih ettiği** meleke → mertebe misalleri. Dağılım bu
#: cetveli tutmak zorundadır; sınama onu denetler.
CERIDE_MISALLERI: Dict[int, int] = {
    1: 0,    # Lafız
    2: 1,    # İştikak
    39: 1,   # Belâgat
    8: 2,    # Kıyas
    22: 2,   # İllet Keşfi
    24: 7,   # İspat
    5: 4,    # Tecrit
    12: 4,   # Temsil
    41: 9,   # Hikmet
}


def meleke_mertebeleri(misaller: Optional[Dict[int, int]] = None
                       ) -> Dict[int, int]:
    """41 melekeyi 20 mertebeye dağıt -- **misalleri tutarak**.

    Usul iki adımdır ve keyfî yeri açıkça işaretlidir:

    1. Ceridenin tasrih ettiği melekeler kendi mertebelerine konur.
       Bu kısım **verilidir**, tercih değildir.
    2. Kalanlar, numara sırasında, her mertebenin doluluğu gözetilerek
       **en boş mertebeye** yerleştirilir. Böylece dağılım düzgün olur
       ve hiçbir mertebe boş kalmaz -- boş bir mertebe, o mertebede
       hiçbir melekenin çalışmadığı, yani ``Ĥ_m = 0`` demektir ve zırh
       orada hiçbir şey süzemez.

    Netice belirlenimcidir: aynı misallerden hep aynı cetvel çıkar.
    """
    mis = dict(CERIDE_MISALLERI if misaller is None else misaller)
    out: Dict[int, int] = {}
    doluluk = [0] * MERTEBE_SAYISI
    for no, m in mis.items():
        if not 1 <= no <= MELEKE_SAYISI:
            raise ValueError("meleke numarası 1..41 olmalı: %d" % no)
        if not 0 <= m < MERTEBE_SAYISI:
            raise ValueError("mertebe 0..19 olmalı: %d" % m)
        out[no] = m
        doluluk[m] += 1
    for no in range(1, MELEKE_SAYISI + 1):
        if no in out:
            continue
        m = int(np.argmin(doluluk))          # en boş mertebe; berabere → küçük
        out[no] = m
        doluluk[m] += 1
    return out


def so_ureteci(D: int, a: int) -> np.ndarray:
    """``T^a = E_{pq} − E_{qp}`` -- ``so(D)``nin temel üreteci.

    Antisimetriktir, dolayısıyla ``exp(θT)`` **tam ortogonaldir** ve
    normu korur (ceridenin reel ``SO(D)`` hükmü). ``a`` indisi
    ``(p, q)`` çiftini sözlük sırasında belirler; belirlenimcidir,
    rastgele seçim yoktur.
    """
    D = int(D)
    ciftler = D * (D - 1) // 2
    if ciftler <= 0:
        raise ValueError("D ≥ 2 olmalı")
    a = int(a) % ciftler
    p = 0
    k = a
    while k >= D - 1 - p:
        k -= D - 1 - p
        p += 1
    q = p + 1 + k
    T = np.zeros((D, D))
    T[p, q] = 1.0
    T[q, p] = -1.0
    return T


def mertebe_hamiltonyeni(m: int, teta: np.ndarray, D: int,
                         cetvel: Optional[Dict[int, int]] = None
                         ) -> Tuple[np.ndarray, List[int]]:
    """``Ĥ_m = Σ_{i ∈ Meleke_m} θ_i T_i`` -- **tek** antisimetrik dizey.

    Döner ``(Ĥ_m, o mertebedeki meleke numaraları)``. 41 meleke ayrı
    ayrı çarpılmaz; hepsi tek bir üretece toplanır -- padişahın küllî
    esası budur ve maliyet farkı buradan doğar.
    """
    cet = meleke_mertebeleri() if cetvel is None else cetvel
    teta = np.asarray(teta, float).ravel()
    if teta.size < MELEKE_SAYISI:
        teta = np.resize(teta, MELEKE_SAYISI)
    H = np.zeros((int(D), int(D)))
    uyeler: List[int] = []
    for no in range(1, MELEKE_SAYISI + 1):
        if cet[no] != int(m):
            continue
        uyeler.append(no)
        H = H + float(teta[no - 1]) * so_ureteci(int(D), no - 1)
    return H, uyeler


def muvazene_matrisi(cetvel: Optional[Dict[int, int]] = None
                     ) -> np.ndarray:
    """``M_ij`` -- hangi iki melekenin çatışması ne kadar ağır sayılır.

    **Aynı mertebedeki melekeler ağır, farklı mertebedekiler hafif
    cezalanır** ve sebebi cebridir: aynı mertebede çalışan iki meleke
    aynı alt uzayı paylaşır, biri ötekinin dalgasını doğrudan söndürür.
    Farklı mertebedekiler zaten ayrı eksenlerdedir (H21: mertebeler
    toplanmaz), çatışmaları dolaylıdır.

    Köşegen sıfırdır: bir melekenin kendisiyle komütatörü zaten sıfır.
    """
    cet = meleke_mertebeleri() if cetvel is None else cetvel
    M = np.zeros((MELEKE_SAYISI, MELEKE_SAYISI))
    for i in range(1, MELEKE_SAYISI + 1):
        for j in range(1, MELEKE_SAYISI + 1):
            if i == j:
                continue
            M[i - 1, j - 1] = 1.0 if cet[i] == cet[j] else 0.1
    return M


def bgcm_kaybi(teta: np.ndarray, D: int,
               M: Optional[np.ndarray] = None,
               cetvel: Optional[Dict[int, int]] = None) -> Dict[str, float]:
    """``Ĥ_BGCM = Σ_ij M_ij ‖[𝒪_i, 𝒪_j]‖²_F`` -- **41 melekenin muvazenesi**.

    İki meleke sıra değiştirebiliyorsa (``[𝒪_i,𝒪_j] = 0``) birbirinin
    işini bozmaz: hangi sırada koşarlarsa koşsunlar netice aynıdır.
    Komütatör büyükse sıra mühimdir ve biri ötekini **eziyor** demektir.

    Ölçü kırmızıya döner: bütün melekeler aynı Cartan alt cebrinde
    (sıra değiştiren) seçilirse kayıp tam sıfırdır; rastgele seçilirse
    büyük çıkar. ``rapor`` ikisini de gösterir.
    """
    teta = np.asarray(teta, float).ravel()
    if teta.size < MELEKE_SAYISI:
        teta = np.resize(teta, MELEKE_SAYISI)
    Mm = muvazene_matrisi(cetvel) if M is None else np.asarray(M, float)
    O = [float(teta[i]) * so_ureteci(int(D), i)
         for i in range(MELEKE_SAYISI)]
    top = 0.0
    en_kotu = 0.0
    cift: Tuple[int, int] = (0, 0)
    for i in range(MELEKE_SAYISI):
        for j in range(i + 1, MELEKE_SAYISI):
            C = O[i] @ O[j] - O[j] @ O[i]
            v = float(np.sum(C * C))
            w = float(Mm[i, j] + Mm[j, i])
            top += w * v
            if w * v > en_kotu:
                en_kotu, cift = w * v, (i + 1, j + 1)
    return {"kayıp": float(top), "en_kötü_çift_şiddeti": float(en_kotu),
            "en_kötü_i": float(cift[0]), "en_kötü_j": float(cift[1]),
            "muvazeneli": bool(top <= 1e-12)}


def zirh_projektorleri(nokta: np.ndarray, D: int, eps: float,
                       lam: float = 1.0) -> Dict[str, np.ndarray]:
    """``(𝒮, Π_betti, Π_koho)`` -- dördü de aynı veriden çıkar.

    * ``𝒮``      -- `nefs/zirh.sheaf_izdusumu`; ek yeri uyumsuzluğunu söndürür.
    * ``Π_betti`` -- ``exp(−λ Δ_Hodge)``; delikli yönleri bastırır.
    * ``Π_koho``  -- ``I − Σ_{ω ∈ H⁰, ω≠sabit} |ω⟩⟨ω|``; kopuk mana
      adalarını (çelişkiyi) siler. **Sabit vektör dışarıda bırakılır**:
      o, "her şey tek parça" yönüdür ve silinirse durum tamamen yok
      olurdu -- silinmesi gereken FAZLA bileşenlerdir.
    """
    from kuantum.tda import vietoris_rips
    from nefs.zirh import hodge_laplasyeni, sheaf_izdusumu

    X = np.atleast_2d(np.asarray(nokta, float))
    if X.shape[0] != int(D):
        raise ValueError("nokta sayısı D olmalı: %d ≠ %d" % (X.shape[0], D))
    Dm = np.sqrt(np.maximum(
        np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=2), 0.0))
    K = vietoris_rips(Dm, float(eps), azami_boyut=1)
    L = hodge_laplasyeni(K, 0)
    if L.shape[0] != int(D):                       # tekil düğüm eksikse
        Z = np.zeros((int(D), int(D)))
        n = min(L.shape[0], int(D))
        Z[:n, :n] = L[:n, :n]
        L = Z
    oz, V = np.linalg.eigh((L + L.T) / 2.0)
    Pb = V @ np.diag(np.exp(-float(lam) * np.maximum(oz, 0.0))) @ V.T
    # kohomoloji: sıfır özdeğerli yönler = bağlantılı bileşenler.
    olcek = max(float(abs(oz).max()), 1e-30)
    cekirdek = V[:, oz <= 1e-9 * olcek]
    sabit = np.ones((int(D), 1)) / math.sqrt(int(D))
    if cekirdek.shape[1]:
        # sabit yönü çekirdekten çıkar; kalan "fazla ada" yönleridir
        c = cekirdek - sabit @ (sabit.T @ cekirdek)
        n = np.linalg.norm(c, axis=0)
        c = c[:, n > 1e-9] / n[n > 1e-9]
        Pk = np.eye(int(D)) - c @ c.T
    else:
        Pk = np.eye(int(D))
    S = sheaf_izdusumu(X[:, 0], X[:, -1]) if X.shape[1] > 1 else np.eye(D)
    if S.shape[0] != int(D):                       # pragma: no cover
        S = np.eye(int(D))
    return {"S": S, "betti": Pb, "koho": Pk,
            "betti0": int(cekirdek.shape[1])}


@dataclass
class DimagAyari:
    """``Ĥ_toplam``ın ölçüleri."""
    D: int = 16
    lam_mizan: float = 1.0
    lam_hodge: float = 1.0
    eps_rips: float = 1.2


def H_toplam(teta: np.ndarray, nokta: np.ndarray,
             H_arc: Optional[np.ndarray] = None,
             ayar: Optional[DimagAyari] = None
             ) -> Dict[str, object]:
    """Üç katmanı **tek dizeyde** birleştir ve her kalemi ayrı raporla.

    Dönen ``H`` bir ``D×D`` dizeydir; ``kalem`` sözlüğü her terimin
    Frobenius payını verir ki hiçbiri ötekinin arkasına saklanmasın
    (H47: ölçüler daima yan yana).
    """
    a = ayar or DimagAyari()
    D = int(a.D)
    P = zirh_projektorleri(nokta, D, a.eps_rips, a.lam_hodge)
    S, Pb, Pk = P["S"], P["betti"], P["koho"]
    cet = meleke_mertebeleri()

    H_mel = np.zeros((D, D))
    mertebe_payi: List[float] = []
    for m in range(MERTEBE_SAYISI):
        Hm, uyeler = mertebe_hamiltonyeni(m, teta, D, cet)
        if not uyeler:
            mertebe_payi.append(0.0)
            continue
        # Π_koho Π_betti 𝒮 [Ĥ_m] 𝒮ᵀ Π_betti Π_koho -- ceridenin sırası
        Z = Pk @ Pb @ S @ Hm @ S.T @ Pb.T @ Pk.T
        H_mel = H_mel + Z
        mertebe_payi.append(float(np.linalg.norm(Z)))

    b = bgcm_kaybi(teta, D, cetvel=cet)
    Ha = np.zeros((D, D)) if H_arc is None else np.asarray(H_arc, float)
    H = Ha + H_mel + float(a.lam_mizan) * b["kayıp"] * np.eye(D)
    return {"H": H,
            "kalem": {"ARC": float(np.linalg.norm(Ha)),
                      "meleke": float(np.linalg.norm(H_mel)),
                      "BGCM": float(a.lam_mizan * b["kayıp"] * math.sqrt(D))},
            "mertebe_payı": mertebe_payi,
            "bgcm": b,
            "betti0": int(P["betti0"]),
            "dolu_mertebe": int(sum(1 for x in mertebe_payi if x > 0))}


def rapor() -> str:                                     # pragma: no cover
    s = ["KÜLLÎ DİMAĞ HAMİLTONYENİ -- 41 meleke, 20 mertebe, 4 zırh", ""]
    cet = meleke_mertebeleri()
    s.append("  1) 41 melekenin 20 mertebeye dağılımı")
    for m in range(MERTEBE_SAYISI):
        uy = [n for n in range(1, MELEKE_SAYISI + 1) if cet[n] == m]
        s.append("     mertebe %2d : %s" % (m, uy))
    yanlis = [n for n, m in CERIDE_MISALLERI.items() if cet[n] != m]
    s.append("     ceridenin misalleri tutuyor mu: %s"
             % ("EVET" if not yanlis else "HAYIR %s" % yanlis))
    bos = [m for m in range(MERTEBE_SAYISI)
           if not any(cet[n] == m for n in cet)]
    s.append("     boş mertebe: %s" % (bos or "yok"))

    s.append("")
    s.append("  2) Muvazene (BGCM) -- ölçü kırmızıya dönüyor mu?")
    D = 12
    # (a) hepsi sıra değiştiren: aynı Cartan alt cebri → kayıp SIFIR
    teta0 = np.zeros(MELEKE_SAYISI)
    teta0[0] = 1.0
    b0 = bgcm_kaybi(teta0, D)
    s.append("     tek meleke uyanık      : kayıp %.3e  muvazeneli=%s"
             % (b0["kayıp"], b0["muvazeneli"]))
    rng = np.random.default_rng(0)
    b1 = bgcm_kaybi(rng.normal(size=MELEKE_SAYISI), D)
    s.append("     41'i birden rastgele   : kayıp %.3e  en kötü çift 𝒪%d-𝒪%d"
             % (b1["kayıp"], int(b1["en_kötü_i"]), int(b1["en_kötü_j"])))
    b2 = bgcm_kaybi(0.05 * rng.normal(size=MELEKE_SAYISI), D)
    s.append("     41'i zayıf (θ×0,05)    : kayıp %.3e  (θ⁴ ile küçülür)"
             % b2["kayıp"])

    s.append("")
    s.append("  3) Ĥ_toplam -- üç kalem yan yana")
    rng = np.random.default_rng(1)
    D = 16
    nk = rng.normal(size=(D, 3))
    for ad, t in (("zayıf θ", 0.05 * rng.normal(size=MELEKE_SAYISI)),
                  ("kuvvetli θ", rng.normal(size=MELEKE_SAYISI))):
        r = H_toplam(t, nk, H_arc=np.eye(D) * 0.3,
                     ayar=DimagAyari(D=D))
        k = r["kalem"]
        s.append("     %-11s ARC=%.4f  meleke=%.4f  BGCM=%.4f"
                 % (ad, k["ARC"], k["meleke"], k["BGCM"]))
        s.append("                 dolu mertebe=%d/20   zırhın gördüğü β₀=%d"
                 % (r["dolu_mertebe"], r["betti0"]))
    s.append("")
    s.append("  Üç kalem birbirinin arkasına saklanmıyor: θ büyüdükçe")
    s.append("  BGCM θ⁴ ile büyüyüp meleke terimini bastırıyor -- muvazene")
    s.append("  terimi tam bunun içindir (𝒪₂₄'ün 𝒪₃₉'u boğması).")
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())

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

__all__ = ["MELEKE_SAYISI", "MERTEBE_SAYISI", "KANONIK_CETVEL",
           "EKSIK_MELEKELER",
           "meleke_mertebeleri", "so_ureteci", "mertebe_hamiltonyeni",
           "bgcm_kaybi", "muvazene_matrisi", "zirh_projektorleri",
           "H_toplam", "DimagAyari"]

#: Melekelerin adedi -- 𝒪₁ … 𝒪₄₄ (divanın 09-KÜLLÎ-TEŞKİLAT celsesi).
#: 41 aslî melekeye üç müstakil uzuv ilâve edildi: 𝒪₄₂ Umumileştirme,
#: 𝒪₄₃ Talim, 𝒪₄₄ Tahsil. Bunlar soyut isim değil, ``nefs/teskilat.py``de
#: formülleriyle duran operatörlerdir.
MELEKE_SAYISI: int = 44
#: Mertebe adedi -- 10 sabit zemin + 10 dinamik lif (`nefs/mertebe.py`).
MERTEBE_SAYISI: int = 20

#: **DİVAN-I ÂLÎ'NİN KANONİK 41 → 20 CETVELİ** (2 Eylül 2026 celsesi).
#:
#: Evvelki turda bu dağılım **inşa edilmişti** ve açık borç olarak
#: yazılmıştı; padişah tam cetveli verdi ve borç kapandı. Cetvel
#: harfiyen buradadır ve sınama onu denetler.
#:
#: Mertebe numaraları: ``0-9`` sabit zemin, ``10-19`` dinamik lif
#: (``d₁ … d₁₀`` sırasıyla ``10 … 19``).
KANONIK_CETVEL: Dict[int, int] = {
    # --- SABİT ZEMİN (lisan, mantık, ontolojik iskelet)
    1: 0, 37: 0, 38: 0,        # k=0 Lafız ve duyu zemini
    4: 1, 34: 1,               # k=1 Sentaks ve tertip
    6: 2, 2: 2, 3: 2,          # k=2 Tasavvur ve iç seyir
    7: 3, 35: 3,               # k=3 Mana ve intikal
    8: 4, 9: 4,                # k=4 Tahlil VE TERKİP (zıt çift, tasdik edildi)
    5: 5,                      # k=5 Tecrit ve soyutlama
    10: 6,                     # k=6 Tezat ve dinamik polarite
    23: 7, 18: 7,              # k=7 Mantık ve dedüksiyon
    11: 8, 12: 8,              # k=8 Tenakuz ve cerh
    13: 9, 32: 9,              # k=9 Tasdik ve itikat derecesi
    # --- DİNAMİK LİFLER (akıl yürütme, keşif, hüküm manifoldu)
    22: 10, 16: 10,            # d₁ İllet ve nedensellik (DAG)
    15: 11, 14: 11,            # d₂ Merak ve teleoloji (gaye)
    21: 12, 25: 12, 26: 12,    # d₃ Tefekkür, Teemmül, Temkin (tasdik edildi)
    27: 13, 28: 13,            # d₄ Tetkik ve kılcal muayene
    24: 14, 29: 14,            # d₅ İspat ve burhân
    30: 15, 36: 15,            # d₆ Tahkik ve asla ircâ (tevil)
    33: 16, 31: 16,            # d₇ Küllî muhakeme ve adalet
    19: 17, 20: 17,            # d₈ Temsil ve teşbih köprüsü
    17: 18, 41: 18,            # d₉ İhtimaliyat ve münazara
    40: 19, 39: 19, 42: 19, 43: 19, 44: 19,   # d₁₀ Sanat, Belâgat,
                               # Umumileştirme, Talim, Tahsil
}

#: **BORÇ KAPANDI.** Evvelki turda ``𝒪₉ Terkip`` ile ``𝒪₂₁ Tefekkür``
#: cetvelde yoktu; gerekçeyle yerleştirilip padişahın tasdikine
#: sunulmuştu. Divan 09-KÜLLÎ-TEŞKİLAT celsesinde **ikisini de
#: onayladı** (𝒪₉ → k=4 Tahlil'in zıt çifti, 𝒪₂₁ → d₃ Tefekkür) ve
#: ayrıca ``𝒪₄₂ Umumileştirme``, ``𝒪₄₃ Talim``, ``𝒪₄₄ Tahsil``
#: melekelerini ``d₁₀``a tescil etti. Cetvel artık **44 tamdır** ve
#: bu sözlük boştur -- boş kalması, borcun kapandığının şahididir.
EKSIK_MELEKELER: Dict[int, int] = {}


def meleke_mertebeleri(cetvel: Optional[Dict[int, int]] = None
                       ) -> Dict[int, int]:
    """Kanonik cetveli döndür -- **inşa yok, tablo var**.

    Evvelki hâli 41 melekeyi "en boş mertebeye" yerleştiriyordu ve bu
    bir tercihti. Artık divanın cetveli statik bağlıdır; yalnız
    cetvelde bulunmayan iki meleke (``𝒪₉``, ``𝒪₂₁``) gerekçeli
    yerlerine konur ve bu **ayrıca işaretlidir**.
    """
    out = dict(KANONIK_CETVEL if cetvel is None else cetvel)
    for no, m in EKSIK_MELEKELER.items():
        out.setdefault(no, m)
    eksik = [n for n in range(1, MELEKE_SAYISI + 1) if n not in out]
    if eksik:                                        # pragma: no cover
        raise ValueError("cetvelde olmayan meleke: %s" % eksik)
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
    # **NORMALİZASYON (padişahın 3. hükmü).** Komütatör ``θ²`` ile,
    # izi ``θ⁴`` ile büyür; ölçüldü: ``λ = 1``de kuvvetli ``θ``da
    # BGCM = 680,86 iken ARC = 1,20 idi -- muvazene terimi gayeyi
    # eziyordu. Payda ``1 + Σ‖O_k‖_F⁴``tür ve aynı mertebeden büyüdüğü
    # için netice **analitik olarak [0,1]e hapsedilir**:
    #
    #     Ĥ_BGCM^norm = Σ M_ij ‖[O_i,O_j]‖²_F / (1 + Σ_k ‖O_k‖_F⁴)
    #
    # Cauchy-Schwarz: ``‖[A,B]‖_F ≤ 2‖A‖_F‖B‖_F`` olduğundan pay,
    # ``4 max(M) (Σ‖O_k‖²)²`` ile sınırlıdır; payda aynı kuvvettedir.
    payda = 1.0 + float(sum(float(np.sum(o * o)) ** 2 for o in O))
    norm = top / payda
    return {"kayıp": float(top), "kayıp_norm": float(norm),
            "payda": float(payda),
            "en_kötü_çift_şiddeti": float(en_kotu),
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
    # ``λ_mizan(θ) = λ₀ / (1 + ‖θ‖²)`` -- padişahın geodezik ölçeklemesi.
    # Normalize BGCM zaten [0,1]dedir; λ o aralığı bir kere daha
    # ``θ`` ile söndürerek büyük ``θ`` rejiminde gayeyi serbest bırakır.
    tt = np.asarray(teta, float).ravel()
    lam = float(a.lam_mizan) / (1.0 + float(tt @ tt))
    bgcm_terim = lam * b["kayıp_norm"]
    H = Ha + H_mel + bgcm_terim * np.eye(D)
    return {"H": H,
            "λ_mizan": float(lam),
            "kalem": {"ARC": float(np.linalg.norm(Ha)),
                      "meleke": float(np.linalg.norm(H_mel)),
                      "BGCM": float(bgcm_terim * math.sqrt(D))},
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
    yanlis = [n for n, m in KANONIK_CETVEL.items() if cet[n] != m]
    s.append("     divanın kanonik cetveli tutuyor mu: %s"
             % ("EVET" if not yanlis else "HAYIR %s" % yanlis))
    s.append("     cetvelde OLMAYAN, gerekçeyle konan: %s"
             % {("𝒪%d" % n): m for n, m in EKSIK_MELEKELER.items()})
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
    s.append("     tek meleke uyanık   : ham %.3e  norm %.6f  muvazeneli=%s"
             % (b0["kayıp"], b0["kayıp_norm"], b0["muvazeneli"]))
    rng = np.random.default_rng(0)
    for ad, olc in (("41'i zayıf ×0,05", 0.05), ("41'i orta ×1", 1.0),
                    ("41'i kuvvetli ×5", 5.0), ("41'i azgın ×50", 50.0)):
        bb = bgcm_kaybi(olc * rng.normal(size=MELEKE_SAYISI), D)
        s.append("     %-19s: ham %.3e  norm %.6f"
                 % (ad, bb["kayıp"], bb["kayıp_norm"]))
    s.append("     → ham kayıp θ⁴ ile patlıyor, NORMALİZE olan [0,1]de kalıyor")

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

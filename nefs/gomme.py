"""Tokenın kuantum yazmacına gömülmesi -- **genlik kodlaması**.

Kullanıcı hükmü (bu turun tashihi):

    Her token'ın 4096 boyutlu float vektörü v, 12-kübitlik durumun
    genliğidir: |token⟩ = Σ_k v_k |k⟩. Asla her sayıyı ayrı kübit yapma!

ve küllî veri kümesi üç yazmaca tensörlenir::

    |D⟩ = (1/√(BL)) Σ_j Σ_t Σ_k v_k^{(j,t)} |j⟩₁₁ ⊗ |t⟩₁₂ ⊗ |k⟩₁₂

    j : yığın indisi   (B = 2048 → 11 kübit)
    t : bağlam yeri    (L = 4096 → 12 kübit)
    k : mana lifi      (D = 4096 → 12 kübit)
                                     ───────
                                      35 kübit

**35 kübit ile 22 milyonun farkı budur ve karıştırılmamalıdır:** 35
kübit verinin **adresidir** (logaritmik indeksleme); 22 milyon kübit
parametre arama uzayı ve iş alanıdır. Adres yazmacı modeli eğitmez,
yalnız veriyi taşır.

**Bu dosyanın ölçtüğü asıl şey: χ ≤ 16 bu veriyi taşıyabiliyor mu?**
Ceride *"QTT, 35 kübit arasındaki bağ boyutunu χ ≤ 16'da tutarak 8,38
milyon tokenı 30-50 MB'da saklar"* der. Bu bir iddiadır ve burada
**sayılır**: ``qtt_bag_ihtiyaci`` gerçek bağ ihtiyacını, ``gomme_hatasi``
χ = 16'da atılan ağırlığı ölçer. Ölçü kırmızıya dönebilir ve dönmesi de
matluptur -- dönmüyorsa bir şey ölçmüyordur.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["genlige_gom", "veri_yazmaci",
           "YazmacOlcusu", "bellek_cetveli",
           "QTT_TABAN", "QTT_KADEME", "QTT_BAG", "qtt_parametre_sayisi",
           "qtt_gomme", "qtt_sadakat_cetveli"]


# ══════════════════════════════════════════════════════════════════════
#  MÜHÜRLENEN AYRIŞIM (padişahın 3. kat'î emri)
# ══════════════════════════════════════════════════════════════════════
#
#     "KESİNLİKLE n=2, d=12 (İkili Quantics) SEÇİLECEKTİR."
#
# Gerekçesi üç kalemdir ve keyfî değildir:
#   1. Kübit birebir eşlemesi -- ``n = 2`` tabanı 12 sanal kübitin
#      iki boyutlu durumlarıyla örtüşür; ara modülo dönüşümü yok.
#   2. QSP ve FCT ikili dyadic ızgarada çalışır.
#   3. Token başına 3,430 MFLOP ile en ucuz ayrışım budur (H180).
#
#: Quantics tabanı -- **değiştirilmez**.
QTT_TABAN: int = 2
#: Çekirdek sayısı: ``2^12 = 4096``.
QTT_KADEME: int = 12
#: Gömme çekirdeklerinin bağ boyutu (padişahın 2. emri: χ = 8).
QTT_BAG: int = 8


def qtt_parametre_sayisi(kademe: int = QTT_KADEME, chi: int = QTT_BAG,
                         taban: int = QTT_TABAN) -> int:
    """``kademe × (taban·χ·χ)`` -- gömmenin serbest sayı adedi.

    Padişahın hükmü: *"4096 sayıyı düz dizi olarak tutma; 12 adet
    2×8×8'lik tensör çekirdeği öğren."* Netice ``12 × 128 = 1536``tır.
    Uç çekirdeklerin bağı bir yanda 1 olduğu için hakikî adet biraz
    daha azdır; burada **üst sınır** verilir ve alt sınır
    ``qtt_gomme``nin kendi çekirdeklerinden sayılır -- iddia değil,
    sayım.
    """
    return int(kademe) * int(taban) * int(chi) * int(chi)


def qtt_gomme(v: np.ndarray, chi: int = QTT_BAG
              ) -> Tuple[List[np.ndarray], float, int]:
    """4096 boyutlu vektörü **12 QTT çekirdeğine** indir (χ bağıyla).

    Döner ``(çekirdekler, sadakat, parametre)``. ``sadakat``
    ``1 − bağıl hata``dır; ``parametre`` çekirdeklerdeki hakikî sayı
    adedidir (uç çekirdeklerin daralması dâhil).

    **Rank-1 DEĞİLDİR ve olmamalıdır** (padişahın 2. emri): ``χ = 1``
    12 kademede yalnız 24 parametre bırakır ve ölçüldüğüne göre dili
    temsil edemez. ``χ = 4`` ve ``χ = 8`` cetveli
    ``qtt_sadakat_cetveli``dedir.
    """
    psi, _ = genlige_gom(v)
    k = kubit_sayisi(np.asarray(v).size)
    cek, bag, hata = genlige_gom(psi=psi, kubit=k, chi=int(chi), ne="mps")
    par = int(sum(c.size for c in cek))
    return cek, float(1.0 - hata), par


def qtt_sadakat_cetveli(v: np.ndarray,
                        chiler: Sequence[int] = (1, 2, 4, 8, 16, 32)
                        ) -> List[Dict[str, float]]:
    """χ ile sadakat ve parametre adedi -- **yan yana** (H47).

    Ceridenin iddiası ``χ = 4`` → %99,2 ve ``χ = 8`` → %99,98'dir. Bu
    bir iddiadır; burada ölçülür ve verinin cinsine göre değişir.
    """
    out: List[Dict[str, float]] = []
    for c in chiler:
        _, sad, par = qtt_gomme(v, chi=int(c))
        out.append({"χ": int(c), "sadakat": float(sad),
                    "parametre": int(par),
                    "sıkıştırma": float(np.asarray(v).size) / max(par, 1)})
    return out


def genlige_gom(v=None, psi=None, kubit: int = 0, chi=None,
                norm: float = 1.0, D=None, ne: str = "gom"):
    """VEKTÖRÜ GENLİĞE GÖMMEK -- **tek terkip** (kütük H225).

    Küme: ``kubit_sayisi`` + ``genlik_gom`` + ``genlik_coz`` +
    ``mps_kur`` + ``qtt_bag_ihtiyaci`` + ``gomme_hatasi``. Altısı tek
    zincirin halkalarıydı ve son ikisi yalnız ``mps_kur``un iki ayrı
    çıktısını almak için vardı.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``kübit``       ``⌈log₂ D⌉`` -- ``D`` boyutu taşıyan kübit adedi
    ``gom``         ``(ψ, norm)`` -- birim normlu genlik vektörü
    ``çöz``         genlikten klasik vektöre dönüş
    ``mps``         ``(çekirdekler, bağlar, hata)``
    ``bağ``         kesmesiz **hakikî** bağ profili
    ``hata``        ``chi``de kesince atılan ağırlığın bağıl normu
    ==============  ==================================================

    ``D = 4096`` için kübit **12**'dir; ``4096 × 16`` bit (65.536 kübit)
    değil. Fark, genlik kodlamasının bütün kazancıdır.

    Genlik kodlaması normu **atar** (durum projektiftir); atılan norm
    ayrıca döndürülür ki kaybolmasın. **Kaba sıfırlama yasağı (H14)**
    burada da geçerlidir: ``v``nin uzunluğu ``2^k``ya tamamlanmaz,
    **sıfırla doldurulur** ve doldurulan yer raporlanır.

    MPS ayrışımı ardışık SVD'dir; ``chi`` verilirse her bağda kesilir ve
    **atılan ağırlık biriktirilerek** bağıl hata döndürülür.
    ``chi=None`` iken kesme yoktur ve dönen bağlar **hakikî** bağ
    ihtiyacıdır -- *"χ ≤ 16 yeter mi"* sualinin cevabı odur.
    """
    if ne == "kübit":
        d = int(D if D is not None else v)
        if d < 1:
            raise ValueError("D ≥ 1 olmalı")
        return int(math.ceil(math.log2(d)))

    if ne == "gom":
        vv = np.asarray(v, float).ravel()
        k = genlige_gom(D=vv.size, ne="kübit")
        tam = 1 << k
        if vv.size < tam:
            u = np.zeros(tam)
            u[:vv.size] = vv
            vv = u
        nrm = float(np.linalg.norm(vv))
        if nrm <= 1e-300:
            return np.full(tam, 1.0 / math.sqrt(tam)), 0.0
        return vv / nrm, nrm

    if ne == "çöz":
        pp = np.asarray(psi, float).ravel() * float(norm)
        return pp if D is None else pp[:int(D)]

    if ne not in ("mps", "bağ", "hata"):
        raise ValueError("gömme kipi bilinmiyor: %r" % (ne,))
    cc = None if ne == "bağ" else chi
    psi = np.asarray(psi, float).ravel()
    n = int(kubit)
    if psi.size != (1 << n):
        raise ValueError("genlik %d, 2^%d = %d değil" % (psi.size, n, 1 << n))
    cek: List[np.ndarray] = []
    bag: List[int] = []
    M = psi.reshape(1, -1)
    atilan = 0.0
    for k in range(n - 1):
        r0 = M.shape[0]
        M = M.reshape(r0 * 2, -1)
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        etkin = int(np.sum(s > 1e-12 * max(float(s[0]), 1e-30)))
        r1 = max(1, etkin if cc is None else min(int(cc), etkin))
        atilan += float(np.sum(s[r1:] ** 2))
        cek.append(U[:, :r1].reshape(r0, 2, r1))
        M = s[:r1, None] * Vt[:r1, :]
        bag.append(r1)
    cek.append(M.reshape(-1, 2, 1))
    top = float(np.sum(psi ** 2))
    hata = math.sqrt(max(atilan, 0.0) / max(top, 1e-300))
    if ne == "bağ":
        return bag
    if ne == "hata":
        return hata
    return cek, bag, hata


@dataclass
class YazmacOlcusu:
    """35 kübitlik veri yazmacının taksimatı -- ceridenin cetveli."""
    B: int = 2048
    L: int = 4096
    D: int = 4096

    @property
    def kubit_yigin(self) -> int:
        return genlige_gom(D=self.B, ne="kübit")

    @property
    def kubit_yer(self) -> int:
        return genlige_gom(D=self.L, ne="kübit")

    @property
    def kubit_mana(self) -> int:
        return genlige_gom(D=self.D, ne="kübit")

    @property
    def kubit(self) -> int:
        return self.kubit_yigin + self.kubit_yer + self.kubit_mana

    @property
    def token(self) -> int:
        return int(self.B) * int(self.L)

    def cetvel(self) -> str:
        return ("  yığın |j⟩  B=%-7d → %2d kübit\n"
                "  yer   |t⟩  L=%-7d → %2d kübit\n"
                "  mana  |k⟩  D=%-7d → %2d kübit\n"
                "  ───────────────────────────────\n"
                "  TOPLAM                 %2d kübit   (%d token)"
                % (self.B, self.kubit_yigin, self.L, self.kubit_yer,
                   self.D, self.kubit_mana, self.kubit, self.token))


def veri_yazmaci(V: np.ndarray) -> Tuple[np.ndarray, YazmacOlcusu]:
    """``(B, L, D)`` klasik veriyi tek genlik vektörüne gömer.

    Netice ``2^(kübit)`` uzunluktadır ve birim normludur. **Bu bir
    tanımdır, bir sıkıştırma değildir**: sıkıştırma MPS'e ayrılınca ve
    bağ kesilince olur (bkz. ``bellek_cetveli``).
    """
    V = np.asarray(V, float)
    if V.ndim != 3:
        raise ValueError("V (B, L, D) olmalı")
    B, L, D = V.shape
    o = YazmacOlcusu(B=B, L=L, D=D)
    T = np.zeros((1 << o.kubit_yigin, 1 << o.kubit_yer, 1 << o.kubit_mana))
    T[:B, :L, :D] = V
    psi = T.ravel()
    nrm = float(np.linalg.norm(psi))
    return (psi / nrm if nrm > 1e-300 else psi), o


def bellek_cetveli(V: np.ndarray, chi: Sequence[int] = (2, 4, 8, 16, 32)
                   ) -> Dict[str, object]:
    """χ cetveli: **bağ ihtiyacı, hata ve bellek** -- üçü yan yana.

    Ceridenin iddiası ``χ ≤ 16``dır. Burada üçü birden ölçülür ve
    hiçbiri tek başına okunmaz (kullanıcı hükmü H47: iki ölçü daima yan
    yana). Bellek, MPS çekirdeklerinin eleman sayısıdır (float32).
    """
    psi, o = veri_yazmaci(V)
    hakiki = genlige_gom(psi=psi, kubit=o.kubit, ne="bağ")
    out: List[Dict[str, float]] = []
    for c in chi:
        cek, bag, hata = genlige_gom(psi=psi, kubit=o.kubit, chi=int(c), ne="mps")
        eleman = int(sum(x.size for x in cek))
        out.append({"χ": int(c), "hata": float(hata),
                    "eleman": eleman, "MB": eleman * 4 / 1e6,
                    "azamî_bağ": int(max(bag)) if bag else 1})
    return {"ölçü": o, "hakikî_bağ": hakiki,
            "hakikî_âzamî_bağ": int(max(hakiki)) if hakiki else 1,
            "klasik_MB": float(np.asarray(V).size * 4 / 1e6),
            "cetvel": out}


def rapor() -> str:                                     # pragma: no cover
    s: List[str] = ["TOKENIN KUANTUM YAZMACINA GÖMÜLMESİ", ""]
    s.append("=== Ceridenin 35 kübitlik adres yazmacı ===")
    s.append(YazmacOlcusu().cetvel())
    s.append("  (klasik: %d token × %d boyut × 4 bayt = %.1f GB)"
             % (YazmacOlcusu().token, 4096,
                YazmacOlcusu().token * 4096 * 4 / 1e9))

    s.append("")
    s.append("=== Tek tokenın genlik gömmesi ===")
    rng = np.random.default_rng(0)
    for ad, v in (("rastgele", rng.normal(size=4096)),
                  ("düzgün", np.sin(np.linspace(0, 6, 4096))
                   * np.exp(-np.linspace(0, 3, 4096))),
                  ("tek-sıcak", np.eye(1, 4096, 1234).ravel())):
        psi, nrm = genlige_gom(v)
        bag = genlige_gom(psi=psi, kubit=12, ne="bağ")
        s.append("  %-10s hakikî âzamî bağ %3d   χ=16'da hata %.4f"
                 % (ad, max(bag), genlige_gom(psi=psi, kubit=12, chi=16, ne="hata")))

    s.append("")
    s.append("=== Küllî veri yazmacı: χ ≤ 16 yetiyor mu? ===")
    B, L, D = 8, 16, 64
    V = rng.normal(size=(B, L, D))
    r = bellek_cetveli(V)
    o = r["ölçü"]
    s.append("  numune: B=%d L=%d D=%d → %d kübit   (klasik %.4f MB)"
             % (B, L, D, o.kubit, r["klasik_MB"]))
    s.append("  kesmesiz hakikî âzamî bağ: %d" % r["hakikî_âzamî_bağ"])
    s.append("     χ      hata        MB     âzamî bağ")
    for c in r["cetvel"]:
        s.append("  %4d   %.4f   %8.5f    %4d"
                 % (c["χ"], c["hata"], c["MB"], c["azamî_bağ"]))
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())

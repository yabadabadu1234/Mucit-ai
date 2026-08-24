"""Yapıştır — token uzayı denkliklerinin Glue tipine köprüsü.

`morfizm` modülü, token uzayları arasındaki eşlemeleri **sayısal**
olarak tartar: izometri mi, konformal mı, ne kadar bilgi kaybediyor.
`omega_kategori_nbe` ise aynı fikrin **tip teorisi** tarafını taşır:
bir denklik ``e : A ≃ B``, Glue ile bir *yola* dönüşür

.. math::  \\mathrm{ua}(e) = \\langle i\\rangle\\;
   \\mathrm{Glue}\\;B\\;[\\,(i=0) \\mapsto (A, e),\\;
                          (i=1) \\mapsto (B, \\mathrm{id})\\,]

ve o yol boyunca taşıma **kayıpsızdır** — çünkü tipler arası eşitliktir,
bir yaklaşıklık değil.

Bu modül ikisini bir araya getirir ve **iki tarafın da aynı şeyi
söylediği yerleri ölçer**:

1. **Sınırda çöküş.** ``ua e @ 0`` normal formu ``A``, ``ua e @ 1``
   normal formu ``B`` olmalı — tanımsal olarak, ispat gerektirmeden.
   Makinede normalleştirilip karşılaştırılır.
2. **Taşıma denkliğin kendisidir.** ``ardil_denkligi`` boyunca taşıma
   ℤ üzerinde ``+1`` yapmalı.  Sarım sayısı hesabıyla ölçülür.
3. **Sayısal karşılık.** Bir token uzayı izometrisi de kayıpsızdır:
   gidip gelince aynı noktaya dönülür.  Aynı şeyin sayısal tarafı budur
   ve makine hassasiyetinde ölçülür.

**Neyin ispatlanmadığı açıkça söylenir:** buradaki köprü bir *analoji
kaydı*dır, iki formalizm arasında kurulmuş bir izomorfizm değil.
Sayısal izometri ile Glue denkliği aynı matematik nesnesi değildir;
ortak olan, ikisinin de "gidip gelince kayıp yok" şartını sağlaması ve
bu şartın iki tarafta da ölçülebilmesidir.  Modül bu ortaklığı ölçer,
daha fazlasını iddia etmez.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from omega_kategori_nbe import cekirdek as C
from omega_kategori_nbe import kutuphane as L
from omega_kategori_nbe import sozdizim as S
from omega_kategori_nbe.aralik import BIR, SIFIR, YANLIS, Aralik

from .manifold import Metrik, duz_metrik
from .morfizm import Morfizm, izometri_mi

__all__ = [
    "ua_sinirda_cokuyor_mu", "ardil_tasima_olc",
    "TokenDenkligi", "permutasyon_denkligi", "dogrusal_denklik",
    "kayipsizlik_karnesi",
]


# ══════════════════════════════════════════════════════════════════════
#  1. Tip teorisi tarafı
# ══════════════════════════════════════════════════════════════════════

def _yol_ucu(p: S.Terim, uc: int) -> S.Terim:
    """``p @ uc`` — yolun ucundaki tip (sözdizim terimi olarak)."""
    return S.YolUygula(p, BIR if uc else SIFIR)


def ua_sinirda_cokuyor_mu(A: S.Terim, B: S.Terim, e: S.Terim
                          ) -> Dict[str, object]:
    """``ua e @ 0 ≡ A`` ve ``ua e @ 1 ≡ B`` — normal formda karşılaştırılır.

    Bu, Glue'nun tanımının parçasıdır: yüz ``φ`` doğru olduğunda
    ``Glue B [φ ↦ (A,e)]`` **çöker** ve ``A`` olur.  Bir ispat terimi
    inşa edilmez; iki tarafın normal formu hesaplanıp eşitliği
    denetlenir.  Eşit değillerse Glue kuralı yanlış kurulmuş demektir.
    """
    yol = L.ua(A, B, e)
    sol_esit = C.esdeger_mi(_yol_ucu(yol, 0), A)
    sag_esit = C.esdeger_mi(_yol_ucu(yol, 1), B)
    return {
        "ua e @ 0": C.nf(_yol_ucu(yol, 0)),
        "A": C.nf(A), "sol_çöküyor": sol_esit,
        "ua e @ 1": C.nf(_yol_ucu(yol, 1)),
        "B": C.nf(B), "sağ_çöküyor": sag_esit,
        "her_ikisi": sol_esit and sag_esit,
    }


def ardil_tasima_olc(n: int = 3) -> Dict[str, object]:
    """``ua(ardil)`` boyunca taşıma ℤ'de ``+1`` mi yapıyor?

    Sarım sayısı hesabı bunu dolaylı olarak zaten ölçüyor
    (``sarim(dongu^n) = n``).  Burada doğrudan bakılır: ``ua`` ile
    kurulan yol boyunca ``0``ı taşıyınca ``1`` çıkmalı.
    """
    Z = S.Tamsayi()
    e = L.ardil_denkligi()
    yol = L.ua(Z, Z, e)
    i = C.taze("i")
    cizgi = S.YolUygula(yol, Aralik.degisken(i))
    terim = S.Transp(i, cizgi, YANLIS, S.Poz(S.Sfr()))
    beklenen = S.Poz(S.Ard(S.Sfr()))
    return {"taşınan": C.nf(terim), "beklenen": C.nf(beklenen),
            "eşit": C.esdeger_mi(terim, beklenen)}


# ══════════════════════════════════════════════════════════════════════
#  2. Sayısal taraf: token uzayı denklikleri
# ══════════════════════════════════════════════════════════════════════

@dataclass
class TokenDenkligi:
    """Token uzayları arasında **tersinir** bir eşleme.

    Kurulurken tersinirlik ölçülür: ``g∘f`` ve ``f∘g`` özdeşlikten ne
    kadar sapıyor.  "Denklik" adı, ölçüm eşiği geçtiğinde hak edilir;
    peşinen verilmez.
    """
    ileri: Morfizm
    geri: Morfizm
    ad: str = ""

    def __post_init__(self) -> None:
        if self.ileri.m != self.geri.n or self.geri.m != self.ileri.n:
            raise ValueError("ileri ile geri birbirinin tersi olacak şekilde "
                             "tiplenmeli")

    def gidis_donus(self, noktalar: Sequence[Sequence[float]]
                    ) -> Dict[str, object]:
        ileri_geri, geri_ileri = [], []
        for x in noktalar:
            x = np.asarray(x, float)
            ileri_geri.append(float(np.max(np.abs(self.geri(self.ileri(x)) - x))))
        for y in noktalar:
            y = np.asarray(y, float)
            if y.size != self.ileri.m:
                continue
            geri_ileri.append(float(np.max(np.abs(self.ileri(self.geri(y)) - y))))
        return {
            "ileri_sonra_geri": max(ileri_geri) if ileri_geri else float("nan"),
            "geri_sonra_ileri": (max(geri_ileri) if geri_ileri
                                 else float("nan")),
        }

    def denklik_mi(self, noktalar: Sequence[Sequence[float]],
                   tol: float = 1e-9) -> bool:
        r = self.gidis_donus(noktalar)
        degerler = [v for v in r.values() if not np.isnan(v)]
        return bool(degerler) and max(degerler) < tol


def permutasyon_denkligi(perm: Sequence[int]) -> TokenDenkligi:
    """Token koordinatlarını yeniden sıralayan denklik.

    Permütasyon, kayıpsızlığın en yalın hâlidir: hiçbir sayı
    değişmez, yalnız yerleri değişir.  Tersi de bir permütasyondur.
    """
    perm = list(perm)
    n = len(perm)
    if sorted(perm) != list(range(n)):
        raise ValueError("geçerli bir permütasyon değil")
    ters = [0] * n
    for i, p in enumerate(perm):
        ters[p] = i
    return TokenDenkligi(
        Morfizm(n, n, lambda x: np.asarray(x, float)[perm], "σ"),
        Morfizm(n, n, lambda y: np.asarray(y, float)[ters], "σ⁻¹"),
        ad=f"perm{tuple(perm)}")


def dogrusal_denklik(M: np.ndarray) -> TokenDenkligi:
    """Tersinir bir dizeyle verilen denklik.

    Tekil dizey verilirse ``LinAlgError`` doğar ve **yakalanmaz**:
    tersi olmayan bir eşlemeye "denklik" demek, modülün bütün
    iddialarını boşa çıkarırdı.
    """
    M = np.asarray(M, float)
    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError("kare dizey lazım")
    Mi = np.linalg.inv(M)
    n = M.shape[0]
    return TokenDenkligi(
        Morfizm(n, n, lambda x: M @ np.asarray(x, float), "M"),
        Morfizm(n, n, lambda y: Mi @ np.asarray(y, float), "M⁻¹"),
        ad="doğrusal")


# ══════════════════════════════════════════════════════════════════════
#  3. Karne
# ══════════════════════════════════════════════════════════════════════

def kayipsizlik_karnesi(d: TokenDenkligi,
                        noktalar: Sequence[Sequence[float]]
                        ) -> Dict[str, object]:
    """Bir token denkliğinin kayıpsızlık karnesi.

    Üç ayrı soru, üç ayrı ölçüm — biri diğerinin yerine geçmez:

    * **Tersinirlik**: gidip gelince aynı yere dönülüyor mu?
    * **İzometri**: mesafeler korunuyor mu?  (Tersinir olmak yetmez;
      ``2·x`` tersinirdir ama mesafeleri iki katına çıkarır.)
    * **Hacim**: ``|det|``.  ``1`` ise hacim korunur.
    """
    gd = d.gidis_donus(noktalar)
    duz = duz_metrik(d.ileri.n)
    izo = izometri_mi(d.ileri, duz, duz_metrik(d.ileri.m), noktalar)
    J = d.ileri.dphi(noktalar[0])
    detmi = (abs(float(np.linalg.det(J))) if J.shape[0] == J.shape[1]
             else float("nan"))
    return {
        "ad": d.ad,
        "tersinir": d.denklik_mi(noktalar),
        "gidiş_dönüş_sapması": max(v for v in gd.values()
                                   if not np.isnan(v)),
        "izometri": izo["izometri"],
        "izometri_sapması": izo["azamî_sapma"],
        "|det|": detmi,
    }


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s: List[str] = []

    s.append("=== Tip teorisi tarafı: Glue sınırda çöküyor mu? ===")
    Z = S.Tamsayi()
    for ad, e in (("özdeşlik denkliği", L.ozdeslik_denkligi(Z)),
                  ("ardıl denkliği", L.ardil_denkligi())):
        r = ua_sinirda_cokuyor_mu(Z, Z, e)
        s.append(f"  {ad:18s} ua e@0 ≡ A: {r['sol_çöküyor']}"
                 f"   ua e@1 ≡ B: {r['sağ_çöküyor']}")
    s.append("  Bu tanımsal bir eşitliktir: ispat terimi kurulmadı,")
    s.append("  iki tarafın normal formu hesaplanıp karşılaştırıldı.")

    s.append("\n=== ua(ardıl) boyunca taşıma +1 yapıyor mu? ===")
    t = ardil_tasima_olc()
    s.append(f"  transp(ua ardil, 0) = {t['taşınan']}")
    s.append(f"  beklenen            = {t['beklenen']}")
    s.append(f"  eşit mi? {t['eşit']}")

    s.append("\n=== Sayısal taraf: token denklikleri ===")
    noktalar = [[0.3, -0.5, 1.2, 0.8], [1.0, 0.0, -0.4, 2.1],
                [-1.1, 0.7, 0.2, -0.9]]
    donme = np.array([[np.cos(0.7), -np.sin(0.7), 0, 0],
                      [np.sin(0.7), np.cos(0.7), 0, 0],
                      [0, 0, np.cos(0.3), -np.sin(0.3)],
                      [0, 0, np.sin(0.3), np.cos(0.3)]])
    olcek = np.diag([2.0, 2.0, 2.0, 2.0])
    kesme = np.array([[1.0, 0.5, 0, 0], [0, 1.0, 0, 0],
                      [0, 0, 1.0, 0], [0, 0, 0, 1.0]])
    adaylar = [permutasyon_denkligi([2, 0, 3, 1]),
               dogrusal_denklik(donme),
               dogrusal_denklik(olcek),
               dogrusal_denklik(kesme)]
    adaylar[1].ad, adaylar[2].ad, adaylar[3].ad = "dönme", "×2", "kesme"
    s.append("  ad         tersinir  gidiş-dönüş   izometri  izo.sapma   |det|")
    for d in adaylar:
        k = kayipsizlik_karnesi(d, noktalar)
        s.append(f"  {k['ad']:10s} {str(k['tersinir']):8s}"
                 f"  {k['gidiş_dönüş_sapması']:.2e}"
                 f"    {str(k['izometri']):8s} {k['izometri_sapması']:.2e}"
                 f"  {k['|det|']:.4f}")
    s.append("  Dördü de TERSİNİR (yani kayıpsız), ama yalnız ikisi")
    s.append("  izometri. Tersinirlik ile mesafe korumak ayrı şeylerdir;")
    s.append("  '×2' hiçbir bilgi kaybetmez, sadece ölçeği değiştirir.")

    s.append("\n=== Tekil dizey denklik sayılmaz ===")
    try:
        dogrusal_denklik(np.array([[1.0, 2.0], [2.0, 4.0]]))
        s.append("  tekil dizey kabul edildi (BEKLENMEZ)")
    except np.linalg.LinAlgError as e:
        s.append(f"  tekil dizey reddedildi: {type(e).__name__}: {e}")

    s.append("\n=== Köprünün haddi ===")
    s.append("  Yukarıda İKİ AYRI şey ölçüldü ve ikisi de kayıpsızlık")
    s.append("  sağladı; ama bu, ikisinin aynı nesne olduğunu GÖSTERMEZ.")
    s.append("  Glue tarafında kayıpsızlık tanımsal bir eşitlik; sayısal")
    s.append("  tarafta ise 1e-16 mertebesinde bir ölçüm. Modül bu")
    s.append("  ortaklığı kaydeder, aralarında izomorfizm iddia etmez.")
    return "\n".join(s)


def rapor() -> str:
    return _gosterim()


if __name__ == "__main__":
    print(rapor())

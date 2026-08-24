"""
Küllî ittisâl: 41 melekenin akışı.

Kaynak metnin kapanış bölümü akışı şöyle tarif eder:

    Müşahede (𝒪₁) → Tecrit (𝒪₅) → Tasavvur (𝒪₆) → Mana (𝒪₇)
      → Tefekkür (𝒪₂₁), İllet (𝒪₂₂), Mantık (𝒪₂₃)
      → Teemmül (𝒪₂₅), Temkin (𝒪₂₆), Tetkik (𝒪₂₇), Tahkik (𝒪₃₀)
      → Muhakeme (𝒪₃₃) meclisinde Tasdik (𝒪₁₃) mührü
      → Belâgat (𝒪₃₉), Fesâhat (𝒪₃₇), Talâkat (𝒪₃₈) ile iblâğ

Bu tarif bir **kısmî sıra**dır: hangi melekenin hangisinden önce
geleceğini söyler, hepsinin yerini söylemez. Buradaki akış, o kısmî
sırayı bozmayan ve sözleşme çizgesini (``okur``/``yazar``) sağlayan tam
bir sıradır. İki şey ``test_nefs.py``de sınanır:

  1. Sıra, **sözleşme çizgesinin topolojik sıralamasıdır** (mecburî
     okumalar bakımından; ihtiyarî okumalar çizgeye girmez).
  2. Sıra, metnin kapanış bölümündeki kısmî sırayı **ihlâl etmez**.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import akil, beyan, idrak, murakabe  # noqa: F401  (sicili doldurur)
from .meleke import Meleke, melekeler, sicil
from .uzaylar import Durum, Parametreler

# Metnin kapanış bölümündeki kısmî sıra (önce → sonra)
KULLI_SIRA: Tuple[Tuple[int, int], ...] = (
    (1, 5), (5, 6), (6, 7),
    (7, 21), (21, 22), (22, 23),
    (23, 25), (25, 26), (26, 27), (27, 30),
    (30, 33), (33, 13),
    (13, 37), (37, 38), (38, 39),
)

# Akışın tam sırası. 𝒪₁₃ Tasdik İKİ kere koşar: bir kere kendi
# mertebesinde (ön tasdik), bir kere de 𝒪₃₃ Muhakeme meclisinden sonra
# **mühür** olarak. Metin bunu açıkça böyle söylüyor ("Muhakeme
# meclisinde Tasdik mührünü alarak").
AKIS: Tuple[int, ...] = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,          # idrak
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20, # hüküm ve gaye
    21, 22, 23, 24,                          # burhân
    25, 26, 27, 28, 29, 30, 31, 32,          # murâkabe
    33, 13,                                  # meclis + mühür
    34, 35, 36,                              # tafsil / tefsir / tevil
    37, 38, 39, 40, 41,                      # beyan
)


def ilk_yazanlar() -> Dict[str, int]:
    """Her alanı yazan melekelerin numaraları (akış sırasına bakmadan)."""
    yazan: Dict[str, List[int]] = {}
    for m in melekeler():
        for alan in m.yazar:
            yazan.setdefault(alan, []).append(m.no)
    return yazan


def sira_gecerli_mi(sira: Sequence[int] = AKIS) -> Tuple[bool, List[str]]:
    """Akış sırası hem sözleşmeyi hem küllî kısmî sırayı sağlıyor mu?

    Sözleşme şartı **sıralı** okunur: bir meleke koştuğunda, mecburî
    okuduğu her alan o ana kadar YA ``Durum``la birlikte gelmiş
    (``E``, ``d_*``) YA da daha önce koşan bir meleke tarafından
    yazılmış olmalıdır.

    Bunun "her okuyan, o alanı yazan HERKESTEN sonra gelmeli" biçiminde
    kurulması yanlış olurdu ve kurulup ölçüldü: yerinde güncelleyen
    melekeler (``okur=("S",)``, ``yazar=("S",)``) yüzünden 70'ten fazla
    sahte ihlâl üretti. Doğru şart, ilk yazımın ilk okumadan önce
    gelmesidir.
    """
    hatalar: List[str] = []
    baslangic = {"E", "d_in", "d_hayal", "d_sem"}
    yazilmis = set(baslangic)
    s = sicil()
    for yer, no in enumerate(sira):
        if no not in s:
            hatalar.append("𝒪%d sicilde yok" % no)
            continue
        m = s[no]
        for alan in m.okur:
            if alan not in yazilmis:
                hatalar.append("𝒪%d (%s) '%s' alanını okuyor; henüz yazılmadı"
                               % (no, m.ad, alan))
        yazilmis.update(m.yazar)

    eksik = set(x.no for x in melekeler()) - set(sira)
    if eksik:
        hatalar.append("akışta olmayan melekeler: %s" % sorted(eksik))

    # küllî kısmî sıra: 'a' EN GEÇ, 'b'nin EN ERKEN koştuğu yere kadar
    # koşmuş olmalı. Bir meleke akışta birden çok kere geçebildiği için
    # (𝒪₁₃ iki kere) uçlar ayrı ayrı alınır.
    ilk = {}
    son = {}
    for yer, no in enumerate(sira):
        ilk.setdefault(no, yer)
        son[no] = yer
    for a, b in KULLI_SIRA:
        if a not in ilk or b not in son:
            hatalar.append("küllî sırada geçen 𝒪%d/𝒪%d akışta yok" % (a, b))
        elif ilk[a] > son[b]:
            hatalar.append("küllî sıra ihlâli: 𝒪%d, 𝒪%d'den sonra" % (a, b))
    return (not hatalar), hatalar


class Nefs:
    """Bütün melekeleri sırayla koşturan işletici."""

    def __init__(self, tohum: int = 0, sira: Sequence[int] = AKIS) -> None:
        self.p = Parametreler(tohum)
        self.sira = tuple(sira)
        self.s = sicil()

    def idrak_et(self, E: np.ndarray, sual: Optional[np.ndarray] = None,
                 d_hayal: int = 24, d_sem: int = 16) -> Durum:
        d = Durum.kur(E, d_hayal=d_hayal, d_sem=d_sem)
        d.sual = sual
        for no in self.sira:
            self.s[no].kosu(d, self.p)
        return d


def rapor(tohum: int = 0, n: int = 20, d_in: int = 12) -> str:
    rng = np.random.default_rng(tohum)
    E = rng.normal(size=(n, d_in))
    nefs = Nefs(tohum)
    d = nefs.idrak_et(E)

    gecerli, hatalar = sira_gecerli_mi()
    satir = ["=== nefs: küllî akış ===",
             "meleke sayısı: %d   akış uzunluğu: %d   sıra geçerli: %s"
             % (len(melekeler()), len(AKIS), gecerli)]
    if hatalar:
        satir += ["  ! " + h for h in hatalar]
    satir.append("")
    satir += d.gunluk
    satir.append("")
    satir.append("makam=%s  P_idrak=%.4f  T=%.4f  tenakuz=%.4f"
                 % (d.makam, d.P_idrak, d.T, d.tenakuz))
    onemli = ["tecrit.β0", "tecrit.β1", "teemmül.τ_durma", "teemmül.yakınsadı",
              "illet.asiklik_ihlali", "muhakeme.mizan", "muhakeme.karar_geçti",
              "fesâhat.skor", "belâgat.skor", "sanat.harmoni",
              "münazara.netice_sentez"]
    satir.append("")
    for k in onemli:
        satir.append("  %-26s %.5g" % (k, d.olcum.al(k)))
    return "\n".join(satir)


if __name__ == "__main__":
    print(rapor())

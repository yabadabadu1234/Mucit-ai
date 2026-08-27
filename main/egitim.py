"""
Küllî Dimağ'ın eğitimi -- ARC metniyle, **gradyan inişi olmadan**.

Ölçüt (uygunluk) bir "kayıp fonksiyonu" değil, dalganın gördüğü
**potansiyeldir**: doğru belirtece verilen ihtimalin negatif logaritması,
artı topolojik cezalar. Aradaki fark lafzî değildir -- bu potansiyelin
gradyanı hiç alınmaz; Active Subspaces'in kurduğu ``r`` boyutlu yüzeyde
**dalga yayılır** ve küresel minimum spektral çöküşle bulunur (H28).

ARC metindir (kütük H5): ``idrak.arc`` bulmacayı belirteç akışına çevirir,
bu model o akışı olduğu gibi konuşur.
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from idrak import arc

from .dimag import Ayar, Dimag
from .optimize import as_gek_adimi, postnikov_adresi, tersine_tavlama

__all__ = ["ornekler", "uygunluk", "egit", "degerlendir"]


# =====================================================================
def ornekler(gorevler: Sequence, azami: int = 64, pencere: int = 48,
             tohum: int = 0) -> List[Tuple[List[int], int]]:
    """(bağlam, sonraki belirteç) çiftleri -- ARC akışından.

    Pencere kısa tutulur ki eğitim bir oturumda bitsin; **kapasite**
    iddiası ayrı ölçülür (``main.py kapasite``), eğitimle karıştırılmaz.
    """
    rng = np.random.default_rng(tohum)
    cikti: List[Tuple[List[int], int]] = []
    for g in gorevler:
        try:
            dizi, hedef = arc.gorev_dizisi(g, hedef_indis=0)
        except Exception:
            continue
        akis = list(dizi) + list(hedef)
        if len(akis) < 6:
            continue
        for _ in range(2):
            i = int(rng.integers(4, len(akis)))
            bas = max(0, i - pencere)
            cikti.append((akis[bas:i], int(akis[i])))
        if len(cikti) >= azami:
            break
    return cikti[:azami]


def uygunluk(model: Dimag, veri: Sequence[Tuple[List[int], int]],
             p: np.ndarray) -> float:
    """``V(p) = −(1/n)Σ log P(doğru) + topolojik ceza``.

    Topolojik ceza metnin kendi kaidesidir (H23): ``β₀ > 1`` ezber
    demektir, tıkanıklık ise mertebeler arası yırtık. İkisi de dalganın
    gördüğü potansiyele eklenir; ayrıca ``ayrık motor``a sinyal olur.
    """
    if not len(veri):
        return 0.0
    top = 0.0
    ceza = 0.0
    for baglam, hedef in veri:
        P, iz = model.ileri(baglam, p)
        top -= float(np.log(P[hedef % len(P)] + 1e-12))
        ceza += 0.02 * sum(max(b - 1, 0) for b in iz.betti.values())
        ceza += 0.05 * float(np.mean(list(iz.tikaniklik.values()) or [0.0]))
    return top / len(veri) + ceza / len(veri)


# =====================================================================
def egit(model: Dimag, veri: Sequence[Tuple[List[int], int]],
         cevrim: int = 6, r: int = 2, n_ornek: int = 20,
         ayrik: bool = True, tohum: int = 0,
         gunluk: Optional[List[str]] = None) -> Dict[str, object]:
    """Çift motorlu eğitim çevrimi."""
    p = model.demet.p.copy()
    V0 = uygunluk(model, veri, p)
    kayit: List[float] = [V0]
    t0 = time.perf_counter()
    D = tuple(model.ayar.dinamik)

    for c in range(cevrim):
        # --- sürekli motor: AS → GEK → dalga
        p_yeni, tani = as_gek_adimi(lambda q: uygunluk(model, veri, q), p,
                                    yaricap=0.5, r=r, izgara=20,
                                    n_ornek=n_ornek, tohum=tohum + c)
        V_yeni = uygunluk(model, veri, p_yeni)
        if V_yeni < kayit[-1]:
            p, V = p_yeni, V_yeni
        else:
            V = kayit[-1]                     # kabul edilmedi; dürüst kayıt
        kayit.append(V)

        # --- ayrık motor: tıkanıklık → Postnikov adresi → tersine tavlama
        if ayrik:
            _, iz = model.ileri(veri[0][0], p)
            adres = postnikov_adresi(iz.tikaniklik, D)
            aday = list(D)
            aday[int(np.argmax([iz.tikaniklik.get(m, 0.0) for m in aday]))] = adres

            def E_ayrik(vek: Tuple[int, ...]) -> float:
                model.ayar.dinamik = tuple(vek)
                return uygunluk(model, veri[:4], p)

            D_yeni, E_iyi = tersine_tavlama(E_ayrik, aday, adim=12,
                                            tohum=tohum + c)
            model.ayar.dinamik = tuple(D_yeni)
            D = tuple(D_yeni)

        if gunluk is not None:
            gunluk.append("çevrim %d: V=%.4f  aktif_özdeğer=%.3f  D=%s"
                          % (c, V, tani["özdeğer_oranı"], list(D)[:4]))

    model.demet.p = p
    return {"V_ilk": V0, "V_son": kayit[-1], "seyir": kayit,
            "süre_sn": time.perf_counter() - t0, "dinamik": D,
            "parametre": len(model.demet)}


# =====================================================================
def degerlendir(model: Dimag, gorevler: Sequence,
                azami: int = 20) -> Dict[str, object]:
    """Değerlendirme: bir bulmacanın hedef ızgarası **tam** çözüldü mü?

    Ölçü serttir ve öyle olmalıdır: ızgaranın her hücresi doğru olacak.
    Ayrıca ``ilk_belirteç_isabeti`` raporlanır -- model hiç doğru
    bilmiyorsa bu da sıfır çıkar ve iddia edilecek bir şey kalmaz.
    """
    cozulen = 0
    isabet_top = 0
    deneme = 0
    hucre_isabet: List[float] = []
    for g in gorevler[:azami]:
        try:
            dizi, hedef = arc.gorev_dizisi(g, hedef_indis=0)
        except Exception:
            continue
        deneme += 1
        baglam = list(dizi)
        uretilen: List[int] = []
        for _ in range(len(hedef)):
            P, _ = model.ileri(baglam[-64:])
            t = int(np.argmax(P))
            uretilen.append(t)
            baglam.append(t)
        h = list(hedef)
        n = min(len(h), len(uretilen))
        dogru = sum(1 for i in range(n) if h[i] == uretilen[i])
        hucre_isabet.append(dogru / max(len(h), 1))
        if uretilen[:len(h)] == h:
            cozulen += 1
        if n and uretilen[0] == h[0]:
            isabet_top += 1
    return {"deneme": deneme, "tam_çözülen": cozulen,
            "ilk_belirteç_isabeti": isabet_top,
            "ortalama_hücre_isabeti":
                float(np.mean(hucre_isabet)) if hucre_isabet else 0.0}

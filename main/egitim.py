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
from .kategori import uzaylari_kur
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
        # Topolojik ceza metnin kendi kaidesidir (H23): β₀ > 1 ezber,
        # tıkanıklık mertebeler arası yırtıktır. İkisi de dalganın
        # gördüğü potansiyele girer ve ayrık motora sinyal olur.
        ceza += 0.02 * sum(max(b - 1, 0) for b in iz.betti.values())
        ceza += 0.05 * float(np.mean(list(iz.tikaniklik.values()) or [0.0]))
        # Dolaşıklık ÖDÜLLENDİRİLİR: çarpım durumuna çöken bir yazmaç
        # süperpozisyonun zenginliğini kaybetmiş demektir.
        ceza -= 0.05 * float(iz.entropi_sonra)
    return top / len(veri) + ceza / len(veri)


# =====================================================================
def hedef_cezasi(model: Dimag, veri: Sequence[Tuple[List[int], int]],
                 p: np.ndarray) -> float:
    """``‖𝒢(u) − y_hedef‖²`` -- hedef bilgisinin potansiyele sızdırılması.

    Minimumun nerede olduğunu bilmiyoruz; fakat orada ne olacağını
    biliyoruz: doğru belirtecin ihtimali 1, ötekilerinki 0. Bu şart
    ``uygunluk``taki ``−log P``den farklıdır ve ondan daha keskindir --
    ``−log P`` yalnız doğru belirtece bakar, bu ise **bütün dağılımın**
    hedefe olan uzaklığını cezalandırır (yanlışların hepsi bastırılır).
    İkisi ayrı yüzeylerdir ve ``as_gek_adimi`` içinde ayrı ayrı vekile
    oturtulup öyle toplanır (kütük H28).
    """
    if not len(veri):
        return 0.0
    top = 0.0
    for baglam, hedef in veri:
        P, _ = model.ileri(baglam, p)
        y = np.zeros_like(P)
        y[hedef % len(P)] = 1.0
        top += float(np.sum((P - y) ** 2))
    return top / len(veri)


def egit(model: Dimag, veri: Sequence[Tuple[List[int], int]],
         cevrim: int = 6, r: int = 2, n_ornek: int = 20,
         ayrik: bool = True, tohum: int = 0, lam_hedef: float = 0.5,
         gama_azami: float = 0.25,
         gunluk: Optional[List[str]] = None) -> Dict[str, object]:
    """Çift motorlu eğitim çevrimi -- hedef güdümlü ve tünelleme vanalı."""
    p = model.p.copy()
    V0 = uygunluk(model, veri, p)
    kayit: List[float] = [V0]
    t0 = time.perf_counter()
    D = tuple(model.ayar.dinamik)
    gama = 0.0
    tunel_kaydi: List[float] = []

    for c in range(cevrim):
        # --- TÜNELLEME VANASI (kütük H29): başıboş değil, teşhise kilitli.
        # Metnin melekeleri burada yoktur; fakat vananın açılma şartı
        # aynen vardır: (i) TIKANMA teşhis edilecek (kohomolojik
        # tıkanıklık yüksek), (ii) ŞEK olacak (potansiyel bir evvelki
        # çevrimde inmemiş, yani sıkışılmış). İkisi birden olmadan Γ
        # açılmaz; açıldıktan sonra ilerleme olursa **mühürlenir**.
        _, iz_v = model.ileri(veri[0][0], p)
        tik_ort = float(np.mean(list(iz_v.tikaniklik.values()) or [0.0]))
        sikisti = c > 0 and kayit[-1] >= kayit[-2] - 1e-9
        if sikisti and tik_ort > 0.5:
            gama = min(gama_azami, gama + 0.1)      # Merak Γ'yı yükseltir
        elif not sikisti:
            gama = 0.0                              # Tahkik mühürler
        model.ayar.gama = gama
        tunel_kaydi.append(gama)

        # --- sürekli motor: AS → GEK → hedef sızdırma → dalga
        p_yeni, tani = as_gek_adimi(
            lambda q: uygunluk(model, veri, q), p,
            yaricap=0.5, r=r, izgara=20, n_ornek=n_ornek,
            hedef_ceza=lambda q: hedef_cezasi(model, veri[:4], q),
            lam_hedef=lam_hedef, tohum=tohum + c)
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
                # Mertebe değişince 20 uzay YENİDEN kurulur ve yeniden
                # makine denetiminden geçer -- ayrık motorun seçtiği
                # mertebe, tip denetiminden geçmeyen bir uzay olamaz.
                model.ayar.dinamik = tuple(vek)
                model.uzaylar = uzaylari_kur(vek)
                return uygunluk(model, veri[:4], p)

            D_yeni, E_iyi = tersine_tavlama(E_ayrik, aday, adim=12,
                                            tohum=tohum + c)
            model.ayar.dinamik = tuple(D_yeni)
            model.uzaylar = uzaylari_kur(D_yeni)
            D = tuple(D_yeni)

        if gunluk is not None:
            gunluk.append("çevrim %d: V=%.4f  aktif_özdeğer=%.3f  D=%s"
                          % (c, V, tani["özdeğer_oranı"], list(D)[:4]))

    model.p = p
    return {"V_ilk": V0, "V_son": kayit[-1], "seyir": kayit,
            "süre_sn": time.perf_counter() - t0, "dinamik": D,
            "parametre": len(model), "tünel": tunel_kaydi,
            "tünel_açıldı": float(sum(1 for g in tunel_kaydi if g > 0.0))}


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
            P, _ = model.ileri(baglam[-48:])
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

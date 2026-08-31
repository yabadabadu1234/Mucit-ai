"""
MANTIĞA SADAKAT ÖLÇÜMÜ -- kütük H102'nin açık borcunun kapatılması.

Kullanıcı hükmü (H102): *"Mantığa sadık kalmak, tüm melekelerin tüm
adımları boyunca asla sadakatten ayrılmaması gereken bir şeydir;
melekelerden başka sistemde ne varsa onun da sadık kalması gerekir.
Mantık yürütme ise arada sırada tercih edilecek bir stratejidir."*

Ben *"bu şu hâliyle koda geçmez, tarifi lâzım"* diye itiraz etmiştim.
Kullanıcının getirdiği vesika tarifi verdi ve tarif **doğrudur**:

> Mantığa sadakat, zihnin bir şeyi *hesaplaması* değil; hiçbir hesabın
> mantık dışı bir duruma taşmasına izin vermeyen bir **kod uzayı**
> (stabilizer / gauge alt-uzayı) olmasıdır.

===================================================================
TENKİT: vesikanın şartı FAZLA KUVVETLİ (H100 gereği)
===================================================================

Vesika şunu yazıyor::

    [𝒪_j , Ŝ_mantık] = 0        ∀ j ∈ {1..41}

Bu **merkezleyici** (centralizer) şartıdır ve modeli felç eder:
``n`` kübitte ``n`` bağımsız üreteçli bir stabilizer grubunun
merkezleyicisi (fazlar hariç) grubun kendisidir. O hâlde melekeler
stabilizer grubunun dışına hiç çıkamaz, yani **hiçbir şey öğrenemez**.

Doğrusu **normalleştirici** (normalizer) şartıdır::

    U† Ŝ U ∈ ⟨Ŝ⟩              (kod uzayını kendine götürmek)

Komütasyon bunun hususî ve kısır hâlidir. Normalleştirici şartı Clifford
tipi zenginliğe izin verir: meleke kod uzayının **içinde** serbestçe
dolaşır, dışına taşamaz. Aranan da budur.

===================================================================
ÖLÇÜLEN ŞART -- somut ve kırmızı yanabilir (H90)
===================================================================

Soyut stabilizer yerine, bu mimarinin kendi alanlarında tarif edilmiş
**üç mantık şartı** ölçülür. Üçü de küllî hüküm bloğundan, H88'de
düzeltilip tam dalgayla doğrulanmış ``blok_dagilimi`` ile okunur:

1. **Tenakuzsuzluk** -- ``P(tasdik=1 ∧ nakz=1)``.
   Bir hüküm hem mühürlenip hem nakzedilemez. Bu ihtimalin ağırlığı
   **tenakuz kütlesi**dir ve sıfıra yakın olmalıdır.

2. **Ayniyet** -- ``P(tasdik₀ ≠ tasdik₁)``.
   Aynı alanın kübitleri aynı hükmü taşır; ayrışmaları, hükmün kendi
   içinde bölünmesidir.

3. **Kâfi sebep** -- ``P(tasdik=1 ∧ mîzân=0)``.
   Delilsiz mühür. Tasdik uyanıkken mîzân bütünüyle uykudaysa hüküm
   dayanaksızdır.

**Sadakat ölçüsü** bir melekenin bu üç kütleyi **artırıp
artırmadığıdır**. Artırmayan meleke sadıktır; artıran değildir.

===================================================================
NİÇİN BU BİR OKUMA DEĞİL
===================================================================

Kütük H31 akış içinde okumayı yasaklar. Burada yasak çiğnenmiyor:
bu modül `tanilama/` altındadır ve **hâricî bir âlettir**, tıpkı
`tanilama/haraplama.py` gibi. Akışın kendisi hiçbir şey okumaz; ölçen,
dışarıdan bakan tabiptir. Sadakatin akış **içinde** icrası ayrı bir
iştir ve üniter olmak zorundadır (tenakuzlu kolun faz sönümlemesi);
o henüz kurulmamıştır ve kurulmuş gibi de yapılmamaktadır.
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from nefs.qakis import QNefs
from nefs.qegitim import belirtecleri_kodla
from nefs.qmeleke import QAKIS, qsicil
from nefs.qyazmac import QAyar, QYazmac
from nefs.sadakat import sadakat_intaci, sadakat_kapisi

__all__ = ["sadakat_olcusu", "haritala", "rapor"]


# =====================================================================
def _blok_bitleri(kac: int) -> np.ndarray:
    """``blok_dagilimi``nin indis düzenindeki bit dizeyi ``(2^kac, kac)``.

    Düzen **ölçülerek** tayin edilir, varsayılmaz: ``rho`` yeniden
    dizilirken ilk kübit en anlamlı bit olur. Yine de bu, sınamayla
    doğrulanır (``_duzeni_dogrula``).
    """
    n = 1 << kac
    x = np.arange(n)
    return np.stack([(x >> (kac - 1 - j)) & 1 for j in range(kac)], axis=1)


def _duzeni_dogrula() -> bool:
    """Bit düzeni hakikaten öyle mi? Bilinen bir durumla sınanır.

    ``bas`` kübiti ``|1⟩``, gerisi ``|0⟩`` olan bir durumda ağırlık,
    ilk kübitin en anlamlı bit olduğu indiste toplanmalıdır.
    """
    from nefs.qyazmac import donme

    ayar = QAyar(bag=4)
    q = QYazmac(1, ayar)
    bas = q.kulli("tasdik", 0)
    q.tek(bas, donme(0.5 * np.pi))          # |0> → |1>
    P = np.asarray(q.blok_dagilimi(bas, 3), float).ravel()
    return bool(np.argmax(P) == 4)          # 100 (ikilik) = 4


def _kutleler(q: QYazmac) -> Dict[str, float]:
    """Üç mantık şartının ihlâl kütlesi -- hepsi ``[0,1]``."""
    bas = q.kulli("tasdik", 0)
    kac = 5                                  # tasdik(2) + sukut(1) + nakz(2)
    P = np.asarray(q.blok_dagilimi(bas, kac), float).ravel()
    b = _blok_bitleri(kac)
    tas0, tas1, nak0 = b[:, 0], b[:, 1], b[:, 3]

    # 1) tenakuzsuzluk: hem mühürlenmiş hem nakzedilmiş olamaz
    tenakuz = float(P[(tas0 == 1) & (nak0 == 1)].sum())
    # 2) ayniyet: aynı alanın kübitleri ayrışmamalı
    ayniyet = float(P[tas0 != tas1].sum())

    # --- TESADÜF TABANI: ham sayı tek başına YANILTIR.
    # İki bağımsız ve yansız kübit zaten ``P(ikisi de 1) = 0,25`` ve
    # ``P(ayrışık) = 0,50`` verir. O hâlde ölçülmesi gereken şey ham
    # kütle değil, **bağımsızlık varsayımının üstündeki fazlalıktır**.
    # Fazlalık sıfıra yakınsa hüküm şudur: alanlar mantıkî şartı ne
    # çiğniyor ne gözetiyor -- yapısızlar. (H90: ölçüt kırmızı
    # yanabilmeli, ama yeşilin nerede olduğu da bilinmeli.)
    p_tas0 = float(P[tas0 == 1].sum())
    p_tas1 = float(P[tas1 == 1].sum())
    p_nak0 = float(P[nak0 == 1].sum())
    tenakuz_taban = p_tas0 * p_nak0
    ayniyet_taban = p_tas0 * (1.0 - p_tas1) + (1.0 - p_tas0) * p_tas1

    # 3) kâfi sebep: tasdik uyanıkken mîzân bütünüyle uykuda olamaz
    mb = q.kulli("mizan", 0)
    _, mk = q._alan["mizan"]
    Pm = np.asarray(q.blok_dagilimi(mb, mk), float).ravel()
    mizan_uyku = float(Pm[0])                # bütün mîzân kübitleri |0>
    tasdik_uyanik = float(P[tas0 == 1].sum())
    kafi_sebep = tasdik_uyanik * mizan_uyku  # bağımsızlık yaklaşığı

    return {"tenakuz": tenakuz, "ayniyet": ayniyet,
            "kâfi_sebep": kafi_sebep,
            "tenakuz_fazla": tenakuz - tenakuz_taban,
            "ayniyet_fazla": ayniyet - ayniyet_taban,
            "toplam": tenakuz + ayniyet + kafi_sebep,
            # Hüküm bu satıra bakar: bağımsızlık tabanının üstündeki
            # fazlalık. Sıfıra yakınsa alanlar YAPISIZDIR.
            "fazla": abs(tenakuz - tenakuz_taban)
                     + abs(ayniyet - ayniyet_taban)}


# =====================================================================
def sadakat_olcusu(tohum: int = 0, satir: int = 6, sozluk: int = 16,
                   ayar: Optional[QAyar] = None, kalp: bool = True
                   ) -> List[Dict[str, object]]:
    """Akışı meleke meleke koştur ve her adımda üç kütleyi ölç.

    Dönen listede her satır bir melekedir ve ``Δ`` sütunları o melekenin
    kütleleri **ne kadar artırdığını** söyler. Artı işaret sadakatsizliktir.
    """
    ayar = ayar or QAyar(tohum=tohum)
    rng = np.random.default_rng(tohum)
    belirtec = [int(x) for x in rng.integers(0, sozluk, size=satir)]
    E = belirtecleri_kodla(belirtec, ayar.satir_kubiti, sozluk)

    nefs = QNefs(tohum, ayar, sadakat=kalp)
    q = QYazmac(satir, ayar)
    q.kodla(E)
    q.superpozisyon()
    q.mera()

    sicil = qsicil()
    onceki = _kutleler(q)
    satirlar: List[Dict[str, object]] = []
    for adim, no in enumerate(QAKIS):
        t0 = time.perf_counter()
        sicil[no].kosu(q, nefs.p)
        if kalp:
            sadakat_kapisi(q, nefs.p)      # KALP: muafiyetsiz, her adımda
        simdi = _kutleler(q)
        satirlar.append({
            "adım": adim, "no": no, "ad": sicil[no].ad,
            "tenakuz": simdi["tenakuz"], "ayniyet": simdi["ayniyet"],
            "kâfi_sebep": simdi["kâfi_sebep"],
            "Δtenakuz": simdi["tenakuz"] - onceki["tenakuz"],
            "Δayniyet": simdi["ayniyet"] - onceki["ayniyet"],
            "Δkâfi": simdi["kâfi_sebep"] - onceki["kâfi_sebep"],
            "Δtoplam": simdi["toplam"] - onceki["toplam"],
            "fazla": simdi["fazla"],
            "tenakuz_fazla": simdi["tenakuz_fazla"],
            "ayniyet_fazla": simdi["ayniyet_fazla"],
            "süre_sn": time.perf_counter() - t0,
        })
        onceki = simdi
    if kalp:
        sadakat_intaci(q)                  # işaretler burada söner
        son = _kutleler(q)
        satirlar.append({"adım": len(satirlar), "no": 0, "ad": "«sadakat intâcı»",
                         "tenakuz": son["tenakuz"], "ayniyet": son["ayniyet"],
                         "kâfi_sebep": son["kâfi_sebep"],
                         "Δtenakuz": son["tenakuz"] - onceki["tenakuz"],
                         "Δayniyet": son["ayniyet"] - onceki["ayniyet"],
                         "Δkâfi": son["kâfi_sebep"] - onceki["kâfi_sebep"],
                         "Δtoplam": son["toplam"] - onceki["toplam"],
                         "fazla": son["fazla"],
                         "tenakuz_fazla": son["tenakuz_fazla"],
                         "ayniyet_fazla": son["ayniyet_fazla"],
                         "süre_sn": 0.0})
    return satirlar


def haritala(satirlar: Sequence[Dict[str, object]], esik: float = 1e-9
             ) -> Dict[str, object]:
    """Sadık / sadakatsiz melekelerin dökümü."""
    sadik = [r for r in satirlar if float(r["Δtoplam"]) <= esik]
    sadakatsiz = sorted((r for r in satirlar if float(r["Δtoplam"]) > esik),
                        key=lambda r: -float(r["Δtoplam"]))
    return {"sadık": sadik, "sadakatsiz": sadakatsiz,
            "sadık_sayısı": len(sadik), "toplam": len(satirlar)}


def rapor(tohum: int = 0, satir: int = 6) -> str:
    s = ["=== MANTIĞA SADAKAT: 41 meleke şartı bozuyor mu? ===", ""]
    s.append("bit düzeni sınaması: %s"
             % ("GEÇTİ" if _duzeni_dogrula() else "**KALDI -- ölçüm geçersiz**"))
    s += ["",
          "tenakuz   : P(tasdik=1 ∧ nakz=1)      -- hem mühür hem nakz",
          "ayniyet   : P(tasdik₀ ≠ tasdik₁)      -- hüküm kendi içinde bölük",
          "kâfi sebep: P(tasdik=1) · P(mîzân=0)  -- delilsiz mühür",
          "",
          "  %-3s %-22s %10s %10s %10s %11s"
          % ("𝒪", "ad", "tenakuz", "ayniyet", "kâfi", "Δtoplam")]
    r = sadakat_olcusu(tohum=tohum, satir=satir, kalp=True)
    for x in r:
        s.append("  %-3d %-22s %10.3e %10.3e %10.3e %+11.3e"
                 % (x["no"], x["ad"], x["tenakuz"], x["ayniyet"],
                    x["kâfi_sebep"], x["Δtoplam"]))

    h = haritala(r)
    s += ["", "--- SADAKAT HÜKMÜ ---",
          "şartı BOZMAYAN meleke : %d / %d"
          % (h["sadık_sayısı"], h["toplam"])]
    if h["sadakatsiz"]:
        s.append("en çok bozanlar:")
        for x in h["sadakatsiz"][:6]:
            s.append("   𝒪%-3d %-22s Δ=%+.3e (tenakuz %+.2e, ayniyet %+.2e,"
                     " kâfi %+.2e)"
                     % (x["no"], x["ad"], x["Δtoplam"], x["Δtenakuz"],
                        x["Δayniyet"], x["Δkâfi"]))
    son = r[-1] if r else None
    if son:
        s += ["",
              "akış sonunda ihlâl kütlesi: tenakuz=%.4f  ayniyet=%.4f  "
              "kâfi_sebep=%.4f"
              % (son["tenakuz"], son["ayniyet"], son["kâfi_sebep"]),
              "",
              "TESADÜF TABANININ ÜSTÜNDEKİ FAZLALIK (asıl hüküm budur):",
              "  tenakuz fazlası = %+.4f   ayniyet fazlası = %+.4f"
              % (son["tenakuz_fazla"], son["ayniyet_fazla"]),
              "",
              "Fazlalık sıfıra yakınsa mana şudur: küllî hüküm alanları",
              "mantıkî şartı ne çiğniyor ne gözetiyor -- YAPISIZLAR.",
              "Bu, H94'teki 'kalp yok' hükmünün ikinci bir delilidir."]
    # --- KALPLİ / KALPSİZ MUKAYESESİ: kalp söküldüğünde ne oluyor?
    ry = sadakat_olcusu(tohum=tohum, satir=satir, kalp=False)
    sy, sk = ry[-1], r[-1]
    s += ["", "=" * 62,
          "KALP SÖKÜLÜNCE NE OLUYOR? (haraplama, sadakat kapısı kapalı)",
          "",
          "  %-22s %12s %12s %10s" % ("ölçü", "KALPSİZ", "KALPLİ", "kazanç"),
          "  %-22s %12.4f %12.4f %9.1f×"
          % ("tenakuz kütlesi", sy["tenakuz"], sk["tenakuz"],
             sy["tenakuz"] / max(sk["tenakuz"], 1e-12)),
          "  %-22s %12.4f %12.4f %9.1f×"
          % ("ayniyet ihlâli", sy["ayniyet"], sk["ayniyet"],
             sy["ayniyet"] / max(sk["ayniyet"], 1e-12)),
          "  %-22s %+12.4f %+12.4f %10s"
          % ("tenakuz FAZLASI", sy["tenakuz_fazla"], sk["tenakuz_fazla"], "-"),
          "  %-22s %+12.4f %+12.4f %10s"
          % ("ayniyet FAZLASI", sy["ayniyet_fazla"], sk["ayniyet_fazla"], "-"),
          "",
          "Kalp bir uzuvsa: söküldüğünde vücut BOZULMALI. Kazanç 1'e",
          "yakınsa kapı bir şey yapmıyor demektir ve öyle yazılır."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())

"""
MANTIĞA SADAKAT KAPISI -- akış içinde, ÜNİTER, her melekeden sonra.

Kullanıcı hükmü (H102): *"Mantığa sadık kalmak, tüm melekelerin tüm
adımları boyunca asla sadakatten ayrılmaması gereken bir şeydir."*
Ve (H104'ün vesikası): *"Mantığa sadakat bir meleke değildir; sistemin
varlık şartıdır."*

===================================================================
NİÇİN BU BİR KALP
===================================================================

H94'te haraplama ölçümü *"kalp yok"* dedi: 41 melekenin tesir nispeti
1,4; hiçbirinin çıkarılması vücudu yıkmıyor. H105'te sadakat ölçümü
ikinci bir delil getirdi: ``tasdik`` ile ``nakz`` arasında **hiçbir
mantıkî bağ yok** -- tenakuz kütlesi tesadüf tabanının altında (fazlalık
−0,0017). Yani ikisi bir arada olamaz olduğu hâlde, bunu **hiçbir
meleke icra etmiyor**.

Hadis-i şerifteki ölçü şudur: *bozulunca bütün vücudu bozan şey*. Bir
uzuv değil, her uzvun **tâbi olduğu** şey. İşte bu kapı odur: her
melekeden sonra vurulur, hiçbir melekenin muaf tutulamayacağı şarttır,
ve kaldırılırsa bütün hükümler mantıksız kalır.

===================================================================
NİÇİN OKUMA DEĞİL -- H31 çiğnenmiyor
===================================================================

Kapı hiçbir şey **okumaz**. Mantık dışı kola bir ``π`` fazı vurur;
hangi kolun işaretlendiği hiçbir yerde sayıya dökülmez. Kolun kendi
genliği kendi cezasını taşır. Bu, kullanıcının *"kalp seçmez,
dolaştırır"* (H102) hükmünün fiilî karşılığıdır.

===================================================================
ÖLÇÜLEN VE DÜZELTİLEN TASARIM HATASI -- niçin bastırma değil işaret
===================================================================

Kapı evvelâ kontrollü **dönme** ile kuruldu: *"nakz uyanıksa tasdiki
sıfıra doğru çevir."* Ölçüldü ve **kötüleştirdi**: tenakuz kütlesi
0,2944'ten 0,3242'ye çıktı.

Sebep bir kodlama hatası değil, bir **imkânsızlıktır**:

> Dönme monoton değildir: ``R(−λ)``, ``|1⟩``e yakın bir kolu ``|0⟩``a
> çeker fakat ``|0⟩``a yakın kolu ``|1⟩``e iter. Daha umumîsi:
> **hiçbir sabit üniter kapı bir alt uzayı şartsız söndüremez.**
> Üniterlik normu korur; genliği ancak *taşır*. Şartsız söndürmek bir
> izdüşümdür, izdüşüm üniter değildir -- yani okumadır ve H31'i kırar.

O hâlde sadakat **iki adımdır**:

1. ``sadakat_kapisi`` -- her melekeden sonra, mantık dışı kola ``π``
   fazı vurur (``CZ``). Marjinalleri hiç değiştirmez; tek başına
   ölçümde görünmez ve görünmemesi doğrudur.
2. ``sadakat_intaci`` -- akışın sonunda, küllî hüküm bloğunda
   ``I − 2|0…0⟩⟨0…0|`` yansıtması. Faz farkını genlik farkına çevirir
   ve işaretli kollar **söner**.

Bu, `nefs/qkaide.py`de fiilen ölçülmüş usulün ta kendisidir (H98:
17–22 kat yükseltme).

===================================================================
İŞARETLENEN ÜÇ MANTIK DIŞI HÂL
===================================================================

    |tasdik=1, nakz=1⟩       hem mühürlü hem nakzedilmiş
    |tasdik₀=1, tasdik₁=0⟩   hüküm kendi içinde bölük
    |tasdik=1, mîzân₀=0⟩     delilsiz mühür (kâfi sebep yok)

===================================================================
ÖLÇÜLEN NETİCE -- kalp söküldüğünde vücut bozuluyor
===================================================================

======================  ==========  =========  ========
ölçü                    KALPSİZ     KALPLİ     kazanç
======================  ==========  =========  ========
tenakuz kütlesi         0,2944      **0,0977**  3,0×
ayniyet ihlâli          0,5542      **0,1586**  3,5×
ayniyet fazlası         +0,0571     **−0,0550** işaret döndü
======================  ==========  =========  ========

H94'te *aranan* fakat bulunamayan uzuv budur: kaldırıldığında bütün
hüküm alanları bozulan şey.

===================================================================
İDDİA EDİLMEYEN
===================================================================

* Tenakuz **fazlası** (tesadüf tabanının üstü) −0,0017'den +0,0042'ye
  çıktı. Ham kütle üç kat düştü fakat iki marjinal de düştüğü için
  taban da düştü; nispî hâl hâlâ tesadüf civarındadır. Yani şart
  **tatbik ediliyor**, fakat alanlar arasında hâlâ hakikî bir mantıkî
  bağ kurulmuş değil.
* Şart **yumuşaktır**: işaretli kolun genliğini düşürür, sıfırlamaz.
  Kesin yasak bir izdüşüm olurdu ve üniter değildir.
* Faz işaretinin ``π`` olması, ``2^k`` kollu bir Grover değil tek turluk
  bir yansıtmadır; tur sayısı ayarlanabilir fakat **ayarlanmadı**.
"""
from __future__ import annotations

import math
from typing import Optional, Tuple

import numpy as np

from .qyazmac import QYazmac, degil_x, donme, kontrollu_donme

__all__ = ["SADAKAT_SIDDETI", "sadakat_kapisi", "sadakat_intaci",
           "sadakat_acilari"]

#: Şartın tatbik şiddeti. Öğrenilebilir; işaretleri sabittir.
SADAKAT_SIDDETI: Tuple[float, float, float] = (0.35, 0.25, 0.20)


def sadakat_acilari(p=None) -> Tuple[float, float, float]:
    """Üç şartın şiddeti -- parametreden gelir, işareti kapıda sabitlenir."""
    if p is None:
        return SADAKAT_SIDDETI
    try:
        a = np.asarray(p.al("sadakat/3", 3), float)
    except Exception:
        return SADAKAT_SIDDETI
    # Şiddet daima müsbet ve mâkul hadde tutulur; işaret kapıda konur.
    return tuple(float(x) for x in (np.abs(a) * 0.5 + np.array(SADAKAT_SIDDETI)))


def _kontrollu_z() -> np.ndarray:
    """``CZ = diag(1,1,1,−1)`` -- yalnız ``|11⟩`` koluna ``π`` fazı.

    Reeldir (kütük H98: reel yazmaçta ``π`` fazı vardır, keyfî
    ``e^{iθ}`` yoktur) ve tam üniterdir.
    """
    G = np.eye(4, dtype=np.float64)
    G[3, 3] = -1.0
    return G


def sadakat_kapisi(q: QYazmac, p=None) -> None:
    """Mantık dışı kolları **işaretle** -- bastırma, işaretle.

    **ÖLÇÜLEN VE DÜZELTİLEN TASARIM HATASI.** Bu kapı evvelâ kontrollü
    DÖNME ile kuruldu: *"nakz uyanıksa tasdiki sıfıra doğru çevir."*
    Ölçüldü ve **kötüleştirdi**: tenakuz kütlesi 0,2944'ten 0,3242'ye
    çıktı. Sebep bir kodlama hatası değil, bir **imkânsızlıktır**:

    > Dönme monoton değildir. ``R(−λ)`` ``|1⟩``e yakın bir kolu
    > ``|0⟩``a çeker, fakat ``|0⟩``a yakın kolu ``|1⟩``e iter. Daha
    > umumîsi: **hiçbir sabit üniter kapı bir alt uzayı şartsız
    > söndüremez.** Üniterlik normu korur; genliği ancak *taşır*.
    > Şartsız söndürmek bir izdüşümdür ve izdüşüm üniter değildir --
    > yani okumadır, H31'i kırar.

    O hâlde sadakat, bastırmakla değil **işaretlemekle** icra edilir:
    yasaklı kola ``π`` fazı vurulur, sönmesi ise sondaki girişime
    (``sadakat_intaci``) bırakılır. Bu, `nefs/qkaide.py`de fiilen
    ölçülmüş usulün ta kendisidir (H98: 17–22 kat yükseltme).

    İşaretlenen üç mantık dışı hâl::

        |tasdik=1, nakz=1⟩     hem mühürlü hem nakzedilmiş
        |tasdik₀=1, tasdik₁=0⟩ hüküm kendi içinde bölük
        |tasdik=1, mîzân₀=0⟩   delilsiz mühür

    Faz vurmak marjinalleri **hiç değiştirmez**; onun için bu kapı tek
    başına ölçümde görünmez ve görünmemesi doğrudur. Hükmü doğuran,
    işaretle girişimin bileşkesidir.
    """
    CZ = _kontrollu_z()
    tas0 = q.kulli("tasdik", 0)
    tas1 = q.kulli("tasdik", 1)
    nak0 = q.kulli("nakz", 0)
    miz0 = q.kulli("mizan", 0)

    # 1) tenakuzsuzluk: |tasdik=1, nakz=1⟩ işaretlenir
    q.uzak_cift(tas0, nak0, CZ)

    # 2) ayniyet: |tasdik₀=1, tasdik₁=0⟩ işaretlenir.
    #    ``X`` ile sarmak, ikinci kübitin ``|0⟩`` hâlini kontrol yapar.
    q.tek(tas1, degil_x())
    q.cift(tas0, CZ)
    q.tek(tas1, degil_x())

    # 3) kâfi sebep: |tasdik=1, mîzân₀=0⟩ işaretlenir
    q.tek(miz0, degil_x())
    q.uzak_cift(tas0, miz0, CZ)
    q.tek(miz0, degil_x())

    # --- 4) KELÂM ŞARTI (kütük H108). **Kendi ölçümümle bulduğum boşluk.**
    # H107'de ölçüldü: kalbin ``beyan`` üzerindeki tesiri yalnız 0,6×,
    # çünkü ``beyan`` ``kelam`` alanından okunur ve kapı ``kelam``a hiç
    # dokunmuyordu. Yani kalp hükmü idare ediyor, KELÂMI etmiyordu.
    #
    # Mantıkî şart: **mühürlenmemiş hükümle konuşulmaz.**
    #     |kelam₀=1, tasdik₀=0⟩  →  işaretlenir
    kel0 = q.kulli("kelam", 0)
    q.tek(tas0, degil_x())
    q.uzak_cift(kel0, tas0, CZ)
    q.tek(tas0, degil_x())

    # --- 5) SÜKÛT ŞARTI. Susarken mühürlemek olmaz; ikisi bir arada
    # bulunamaz (kütük H10: sükût bir kusur değil fazilettir, fakat
    # hükümle beraber olamaz).
    #     |sukut=1, tasdik₀=1⟩  →  işaretlenir
    q.uzak_cift(q.kulli("sukut", 0), tas0, CZ)

    # --- 6) GAYE ŞARTI (Dosya 7). Gaye ile hüküm AYRIŞAMAZ: gaye
    # istemediğini mühürlemek de, istediğini mühürlememek de mantık
    # dışıdır. İki kol da işaretlenir (XOR).
    gay0 = q.kulli("gaye", 0)
    q.tek(gay0, degil_x())
    q.uzak_cift(tas0, gay0, CZ)          # |tasdik=1, gaye=0⟩
    q.tek(gay0, degil_x())
    q.tek(tas0, degil_x())
    q.uzak_cift(tas0, gay0, CZ)          # |tasdik=0, gaye=1⟩
    q.tek(tas0, degil_x())


def sadakat_intaci(q: QYazmac, tur: int = 1) -> float:
    """İşaretlenen kolları **söndür** -- küllî hüküm bloğunda girişim.

    Faz işareti tek başına marjinali değiştirmez; onu genlik farkına
    çeviren şey **yansıtmadır**. `nefs/qkaide.py`de ölçülen usulün
    aynısı: süperpozisyon tabanına dön, ``|0…0⟩`` etrafında yansıt,
    geri dön. Yansıtma köşegen olduğu için MPO bağ boyutu 2'dir ve
    ancilla gerekmez.

    **Niçin yalnız hüküm alanları.** Veri kübitlerine dokunulmaz;
    yansıtma yalnız ``tasdik``, ``nakz``, ``mizan`` üçlüsünü kapsar.
    Bütün zincire vurmak, dalganın taşıdığı bütün suretleri de
    karıştırırdı.
    """
    # **Yansıtma, işaretlenen bütün alanları kapsamalıdır.** Evvelce
    # yalnız mizan/tasdik/nakz'ı kapsıyordu; ``kelam``a işaret vurulup
    # yansıtmaya alınmazsa o işaret **hiçbir zaman genliğe dönmez**.
    yuv = [q.kulli("mizan", j) for j in range(q._alan["mizan"][1])]
    yuv += [q.kulli("tasdik", j) for j in range(q._alan["tasdik"][1])]
    yuv += [q.kulli("sukut", j) for j in range(q._alan["sukut"][1])]
    yuv += [q.kulli("nakz", j) for j in range(q._alan["nakz"][1])]
    yuv += [q.kulli("kelam", j) for j in range(q._alan["kelam"][1])]
    yuv += [q.kulli("gaye", j) for j in range(q._alan["gaye"][1])]
    yuv = sorted(set(yuv))
    bas, son = min(yuv), max(yuv) + 1
    kesme = 0.0
    for _ in range(max(1, int(tur))):
        q.tek_yigin(yuv, np.stack([donme(-0.25 * math.pi)] * len(yuv)))
        W = {}
        for j in range(bas, son):
            T = np.zeros((2, 2, 2, 2))
            T[0, 0, 0, 0] = T[0, 1, 1, 0] = 1.0
            T[1, 0, 0, 1] = 1.0
            W[j] = T
        kesme += q.y.mpo_uygula(W, 2, bas=bas, son=son,
                                sol_sinir=np.array([1.0, -2.0]),
                                sag_sinir=np.array([1.0, 1.0]))
        q.tek_yigin(yuv, np.stack([donme(0.25 * math.pi)] * len(yuv)))
    return kesme

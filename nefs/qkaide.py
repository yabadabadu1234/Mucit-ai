"""
KÂİDE ORAĞI -- H91'in icrası, **reel** yazmaçta.

Kullanıcı hükmü: *"Faz orağı olarak bağla ama 2^k şeklinde artmasın."*
Ve: *"qkaide diye bir dosya yazarsın olur biter, ana akışa onu koyarsın."*

===================================================================
1. NİÇİN ``2^k`` YOK
===================================================================

Ebat kâidesi bir **indis** değil bir **denklemdir**::

    r · h_çıktı  =  p · h_girdi + q          (p, q, r küçük tamsayı)

Sapma ``δ = p·h + q − r·h_çıktı``dır. Şimdi can alıcı nokta: ``p``, ``q``,
``r`` kübitlere bit bit yazıldığında ``δ`` **bitlerde doğrusaldır**::

    p = Σ_i 2^i p_i   ⇒   δ = Σ_m c_m b_m + d,   c_m klasik olarak bilinir

Doğrusal olduğu için ``δ``yı bütün kâide adayları için **aynı anda**
hesaplamak, kübit başına **bir** kontrollü kapı ister. ``2^k`` taban
durumunu tek tek dolaşmaya hiç gerek yoktur. Benim evvelki teklifim
(``mizan`` bütün taban durumlarını klasik denetleyip köşegen kursun)
tam da bu yüzden düşürüldü ve düşürülmesi doğrudur.

===================================================================
2. NİÇİN FAZ DEĞİL AÇI -- yazmaç REELDİR
===================================================================

Kullanıcının getirdiği teklif ``exp(−iγδ²)`` diyagonal faz işlemcisini
öneriyordu. Fikir doğrudur (ancilla ve çöp ihtiyacını kaldırır) fakat
**bu mimaride doğrudan tatbik edilemez**: bu projenin yazmacı reeldir --
``dik_iki_kubit`` ortogonaldir, ``A`` reel kayan noktadır, ``beyan``
``np.real`` alır. Reel bir yazmaçta ``exp(iθZ)`` yoktur; olan yalnız
``diag(1,−1)`` yani ``π`` fazıdır.

Reel karşılığı vardır ve daha ucuzdur: ``δ``yı bir **faza** değil bir
**açıya** yazmak. Tek bir ``orak`` kübiti ``|0⟩``dan başlar ve her kâide
kolunda o kolun ``δ``sı kadar döner::

    R(γδ)|0⟩ = cos(γδ)|0⟩ + sin(γδ)|1⟩

``δ = 0`` olan kolda orak **hiç kımıldamaz**; ``δ ≠ 0`` olan her kol
``|1⟩``e genlik **sızdırır**. Şahitler sırayla işlendiğinde (akışkan
usul), yalnız **bütün şahitlerde** ``δ=0`` olan kol ``orak=|0⟩``da tam
genliğiyle kalır. Yani:

    **İSPAT, HİÇ SIZDIRMAMIŞ OLAN KOLDUR.**

Bu, Grover'ın işaretleme adımının reel ve ancillasız karşılığıdır.
``2^k`` yoktur, çöp yazmacı yoktur, geri alma derdi yoktur -- çünkü
işaretleme zaten tek kübitte ve tersinirdir.

===================================================================
3. MALİYET
===================================================================

``K`` şahit, ``k`` kâide kübiti için ``K·k`` iki-kübit kapısı. ``k=12``,
``K=4`` için 48 kapı. Kâide adayı sayısı ``2^12 = 4096``tır ve hepsi
**aynı anda** denetlenir. Nispet ``4096 / 48 ≈ 85``tir ve ``k``
büyüdükçe üstel olarak açılır -- kullanıcının *"aynı anda 1 milyon
belirteç"* hükmünün bu rükündeki fiilî karşılığı budur.

===================================================================
4. İDDİA EDİLMEYEN
===================================================================

Bu modül **yalnız ebat rüknünü** (``H_D``) kurar. İskelet (``H_S``),
illet (``H_C``), nakz (``H_N``) ve muhakeme (``H_J``) rükünleri
kurulmamıştır ve kurulmuş gibi yapılmamaktadır.

Ayrıca ``χ``nın ne olacağı **ölçülmemiştir**; ölçüm H89 gereği nizam
kurulduktan sonradır. Kontrollü dönmeler dolaşıklık üretir ve bunun
sıfır olduğu iddia edilmiyor (kütük H95).

Hakikat kaynağı `nefs/kaide.py`dir (klasik mîzân); bu modülün verdiği
ağırlıklar orada hesaplanan yüklemle **yüzleştirilir** ve ayrı düştükleri
yerde kuantum taraf yanlıştır (kütük H88'in dersi, H90'ın şartı).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .qyazmac import QYazmac, donme, faz_z, kontrollu_donme

__all__ = ["EbatSarti", "sartlari_kur", "KaideOragi", "coz_kaide"]


# =====================================================================
@dataclass(frozen=True)
class EbatSarti:
    """Tek bir şahidin ebat şartı: ``δ = Σ c_m b_m + d``.

    ``c`` katsayıları **klasiktir** ve şahitten çıkar; kâidenin kendisi
    (``b`` bitleri) süperpozisyondadır. Doğrusallık bu ayrımı mümkün
    kılar ve ``2^k``yı kaldıran şey odur.
    """
    c: Tuple[float, ...]
    d: float

    def sapma(self, bitler: Sequence[int]) -> float:
        return float(sum(ci * bi for ci, bi in zip(self.c, bitler)) + self.d)


def sartlari_kur(sahitler: Sequence[Tuple[int, int]], bit: int = 4
                 ) -> List[EbatSarti]:
    """``(h_girdi, h_çıktı)`` çiftlerinden şartları çıkar.

    Kâide::  ``r · h_çıktı = p · h_girdi + q``
    Bit dizilişi:: ``[p_0..p_{bit-1}, q_0..q_{bit-1}, r_0..r_{bit-1}]``

    Katsayılar::
        p_i →  2^i · h_girdi
        q_j →  2^j
        r_l → −2^l · h_çıktı
    """
    sartlar: List[EbatSarti] = []
    for h_in, h_out in sahitler:
        c: List[float] = []
        c += [float(1 << i) * float(h_in) for i in range(bit)]
        c += [float(1 << j) for j in range(bit)]
        c += [-float(1 << l) * float(h_out) for l in range(bit)]
        sartlar.append(EbatSarti(tuple(c), 0.0))
    return sartlar


# =====================================================================
class KaideOragi:
    """Kâide yazmacını süperpozisyona sokar ve şartı **açıya** yazar."""

    def __init__(self, q: QYazmac, gama: float = 0.35) -> None:
        self.q = q
        self.gama = float(gama)
        _, self.k = q._alan["kaide"]
        self.orak = q.kulli("orak", 0)

    # -----------------------------------------------------------------
    def yuvalar(self) -> List[int]:
        return [self.q.kulli("kaide", j) for j in range(self.k)]

    def hazirla(self) -> None:
        """Bütün kâide adaylarını **aynı anda** aç: her kübite ``π/4``.

        ``2^k`` aday doğar ve hafızada hiçbir şey büyümez -- süperpozisyon
        bedavadır, pahalı olan dolaşıklıktır (bkz. `docs/ISTILAH.md`).
        """
        yuv = self.yuvalar()
        self.q.tek_yigin(yuv, np.stack([donme(0.25 * math.pi)] * len(yuv)))

    # -----------------------------------------------------------------
    def sart_yaz(self, sart: EbatSarti) -> None:
        """Tek bir şahidin şartını orak kübitine yaz -- **akışkan usul**.

        Her kâide kübiti, kendi katsayısı kadar orak kübitini çevirir::

            b_m = 1  →  orak ``γ·c_m`` kadar döner
            b_m = 0  →  hiç dönmez

        Dönmeler bileşke olduğu için (``R(α)R(β) = R(α+β)``) orak, o kolun
        ``γ·δ``sı kadar dönmüş olur. ``δ = 0`` ise orak yerinde durur.

        **Neden şahitler tek tek işlenir.** Hepsinin ``δ``sı tek açıda
        toplansaydı, ``δ₁ = +3`` ile ``δ₂ = −3`` birbirini götürür ve
        hiçbirini sağlamayan bir kâide sağlıyor görünürdü. Şahit başına
        ayrı yazıp ayrı işaretlemek bu iptali imkânsız kılar; kütük
        H95'teki *akışkan geri alma* kaidesinin buradaki karşılığı budur.
        """
        yuv = self.yuvalar()
        if abs(sart.d) > 1e-12:
            self.q.tek(self.orak, donme(self.gama * sart.d))
        for m, cm in enumerate(sart.c):
            teta = self.gama * float(cm)
            if abs(teta) < 1e-12:
                continue
            self.q.uzak_cift(yuv[m], self.orak, kontrollu_donme(teta))

    def sart_geri_al(self, sart: EbatSarti) -> None:
        """``sart_yaz``ın tam tersi -- ters sırada ve ters açıyla."""
        yuv = self.yuvalar()
        for m in range(len(sart.c) - 1, -1, -1):
            teta = -self.gama * float(sart.c[m])
            if abs(teta) < 1e-12:
                continue
            self.q.uzak_cift(yuv[m], self.orak, kontrollu_donme(teta))
        if abs(sart.d) > 1e-12:
            self.q.tek(self.orak, donme(-self.gama * sart.d))

    # -----------------------------------------------------------------
    def isaretle(self, sartlar: Sequence[EbatSarti]) -> None:
        """Bütün şahitleri sırayla işaretle.

        Her şahit için: şartı yaz → orak kübitine ``Z`` vur → şartı geri
        al. ``δ=0`` olan kolda orak hiç kımıldamadığı için ``Z`` ona
        dokunmaz ve genliği tam kalır; ``δ≠0`` olan kolda ise orak
        ``|1⟩``e sızmış olduğundan ``Z`` o kolu böler ve genliğini
        ``cos(2γδ)`` nispetinde düşürür.

        Bir kâide **bütün** şahitleri sağlamadıkça sızıntıdan kurtulamaz;
        yani işaretleme, şartların **mantıkî çarpımıdır** (``⋀``) ve
        bunun için ayrı bir çok-kontrollü kapıya ihtiyaç yoktur.
        """
        for s in sartlar:
            self.sart_yaz(s)
            self.q.tek(self.orak, faz_z())
            self.sart_geri_al(s)

    def difuzyon(self) -> None:
        """Grover difüzyonu -- ``|Ψ₀⟩`` etrafında yansıtma, kâide bloğunda.

        ``D = 2|Ψ₀⟩⟨Ψ₀| − I``. Reel yazmaçta aynen kurulur: süperpozisyon
        tabanına dön, ``|0…0⟩`` etrafında yansıt, geri dön.
        """
        yuv = self.yuvalar()
        H = np.stack([donme(-0.25 * math.pi)] * len(yuv))
        self.q.tek_yigin(yuv, H)
        for j in yuv:
            self.q.tek(j, faz_z())
        self.q.tek_yigin(yuv, np.stack([donme(0.25 * math.pi)] * len(yuv)))


# =====================================================================
def coz_kaide(sahitler: Sequence[Tuple[int, int]], bit: int = 4,
              tur: int = 1, gama: float = 0.35,
              ayar=None) -> Dict[str, object]:
    """Ebat kâidesini kübit hattında ara -- **tek geçişte, hepsi birden**.

    Dönen sözlükte kâide bloğunun dağılımı ve en yüksek genlikli aday
    vardır. Bu bir cevap değil bir **mîzândır**: hiçbir aday öne
    çıkmıyorsa o da bir hükümdür ve sükût edilir (H10).
    """
    from dataclasses import replace as _replace

    from .qyazmac import QAyar

    ayar = ayar or QAyar()
    if ayar.kaide_bit != bit:
        ayar = _replace(ayar, kaide_bit=bit)
    k = 3 * bit
    if dict(ayar.kulli_alanlar).get("kaide") != k:
        alanlar = tuple((ad, k if ad == "kaide" else n)
                        for ad, n in ayar.kulli_alanlar)
        ayar = _replace(ayar, kulli_alanlar=alanlar)

    q = QYazmac(1, ayar)
    orak = KaideOragi(q, gama=gama)
    orak.hazirla()
    sartlar = sartlari_kur(sahitler, bit)
    for _ in range(max(1, int(tur))):
        orak.isaretle(sartlar)
        orak.difuzyon()

    P = np.asarray(q.blok_dagilimi(q.kulli("kaide", 0), k), float).ravel()
    en = int(np.argmax(P))
    return {"dağılım": P, "en_yüksek": en, "olasılık": float(P[en]),
            "çözüm": _coz(en, bit), "kesme": float(q.iz.kesme),
            "χ": int(q.y.bag), "kapı": int(q.iz.kapi)}


def _coz(indis: int, bit: int) -> Tuple[int, int, int]:
    """Taban durumu indisini ``(p, q, r)``ye çevir."""
    b = [(indis >> i) & 1 for i in range(3 * bit)]
    p = sum(b[i] << i for i in range(bit))
    qq = sum(b[bit + j] << j for j in range(bit))
    r = sum(b[2 * bit + l] << l for l in range(bit))
    return p, qq, r

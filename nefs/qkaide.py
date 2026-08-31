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
2. NİÇİN AÇI DEĞİL İŞARET -- yazmaç REELDİR (ÖLÇÜLDÜ)
===================================================================

Kullanıcının getirdiği teklif ``exp(−iγδ²)`` **diyagonal faz**
işlemcisi öneriyordu. Bu mimaride tatbik **edilemez**: yazmaç reeldir
-- ``dik_iki_kubit`` ortogonaldir, ``A`` reel kayan noktadır, ``beyan``
``np.real`` alır. Reel yazmaçta ``exp(iθZ)`` yoktur; olan ``diag(1,−1)``,
yani ``π`` fazıdır.

Evvelâ ``δ`` bir **açıya** yazıldı (orak kübiti ``γδ`` kadar döner).
Kullanıcı hükmü *"ikisini de kur, ÖLÇÜM karar versin"* gereği iki usul
yan yana koşturuldu ve ölçüm hükmünü verdi::

    usul          tepe doğru mu     çözümlerin ağırlığı (düz: 0,047)
    açı × 1            ✗                    0,064   ← yükseltme YOK
    işaret × 1         ✓                    0,473
    işaret × 2         ✓                    0,787   ← 17 kat

Açı usulü niçin işlemedi: işaretleme kâide yazmacına **faz** değil,
oraka **genlik** yazıyor. Orak izlenip atılınca ``cos² + sin² = 1``
olduğu için kâide marjinali hiç değişmiyor. Reel yazmaçta faz geri
tepmesi ancak ``X`` ile olur (``|−⟩``, ``X``in −1 özdurumudur);
``R_y``nin özdurumları karmaşık olduğu için açı kodlamasıyla temiz bir
faz orağı **kurulamaz**. Açı usulü ölçümden sonra **silindi**.

Kalan usul şudur: ``δ``nın koşan toplamı MPO'nun **bağ indisinde**
taşınır ve sağ sınır, toplam sıfırsa ``−1`` verir::

    w_sağ = w_sol + c_m · b_m        (i'de köşegen)

Bağ boyutu ``δ``nın **menzili** kadardır -- ``2^k`` değil, katsayıların
büyüklüğünde polinom. Difüzyon da ``I − 2|0…0⟩⟨0…0|`` MPO'sudur
(bağ boyutu 2); evvelce her kübite ayrı ``Z`` vurulmuştu ve o işlemci
çarpanlarına ayrıldığı için **hiçbir şey yansıtmıyordu** (H97).

===================================================================
3. MALİYET ve ÖLÇÜLEN NETİCE
===================================================================

``k = 6`` kâide kübiti (64 aday) için tek MPO; ölçülen kesme
``~1e-16``, yani işlem fiilen **tam**. Beş hâlde klasik hakikatle
yüzleştirildi::

    çıktı = girdi     → (2,0,2) ✓    ağırlık 0,787  (düz 0,047)
    çıktı = 2·girdi   → (2,0,1) ✓    ağırlık 0,344  (düz 0,016)
    çıktı = girdi/2   → (1,0,2) ✓    ağırlık 0,344  (düz 0,016)
    çıktı = girdi+1   → (3,3,3) ✓    ağırlık 0,787  (düz 0,047)
    ÇELİŞKİLİ         → çözüm yok, ağırlık 0,000 ✓  (1 sahte kök bildirildi)

Bütün adaylar **aynı anda** denetlenir; kullanıcının *"aynı anda 1
milyon belirteç"* hükmünün bu rükündeki fiilî karşılığı budur.

**Kabul edilen hudut.** Şahitler tek bir doğrusal biçimde
(``Σ λ_s δ_s``) birleştirilir; bu, ``δ_s``lerin ayrı ayrı sıfır olmasını
garanti etmez. Doğuracağı **sahte kökler klasik olarak sayılır**
(``sahte_kokler``) ve gizlenmez -- çelişkili hâlde bir tane çıktı ve
bildirildi. Tam AND, bağ indisinde bütün ``δ_s``leri birden taşımayı
ister; bağ boyutu şahit sayısında üstel büyür ve o yüzden alınmadı.

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

from .qyazmac import QYazmac, donme

__all__ = ["EbatSarti", "sartlari_kur", "KaideOragi", "coz_kaide"]

#: Şahitleri tek doğrusal biçimde birleştiren ağırlıklar. Asal ve
#: birbirine yakın olmayan seçilir ki ``Σ λ_s δ_s = 0`` tesadüfen
#: sağlanmasın; sahte kök doğurup doğurmadığı ayrıca **sınanır**.
_LAMBDA: Tuple[int, ...] = (1, 3, 7, 13, 23, 41, 71, 113)


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
    """Kâide yazmacını süperpozisyona sokar ve şartı **işaretle** vurur."""

    def __init__(self, q: QYazmac) -> None:
        self.q = q
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
    def sifir_yansitmasi(self) -> float:
        """``R₀ = I − 2|0…0⟩⟨0…0|`` -- kâide bloğunda, **tam**, ancillasız.

        **ÖLÇÜLEN VE DÜZELTİLEN KUSUR (kütük H97).** Evvelce difüzyon,
        her kübite ayrı ayrı ``Z`` vurularak yazılmıştı. O işlemci
        ``Π_j (−1)^{b_j}``dir; **çarpanlarına ayrılır** ve ``|0…0⟩``
        etrafında hiçbir yansıtma yapmaz. Ölçüldü: dağılım düpedüz
        düzgün kalıyordu (1/64, beş halin hepsinde).

        Doğrusu ``k`` katlı **kontrollü** ``Z``dir ve tek kübitlik
        ``Z``lerin çarpımı ona eşit değildir. Ancilla ile kurmak
        gerekmez: işlemci köşegen olduğu için **MPO bağ boyutu 2**dir::

            w = 0 kanalı : birim (δ_ij)          katsayı  +1
            w = 1 kanalı : |0⟩⟨0| (δ_i0 δ_j0)    katsayı  −2

        Sol sınır ``(1, −2)``, sağ sınır ``(1, 1)``; bileşke tam olarak
        ``I − 2|0…0⟩⟨0…0|``dır.
        """
        yuv = self.yuvalar()
        bas, son = min(yuv), max(yuv) + 1
        W: Dict[int, np.ndarray] = {}
        for j in yuv:
            T = np.zeros((2, 2, 2, 2))
            T[0, 0, 0, 0] = T[0, 1, 1, 0] = 1.0      # birim kanalı
            T[1, 0, 0, 1] = 1.0                      # |0⟩⟨0| kanalı
            W[j] = T
        return self.q.y.mpo_uygula(
            W, 2, bas=bas, son=son,
            sol_sinir=np.array([1.0, -2.0]),
            sag_sinir=np.array([1.0, 1.0]))

    def difuzyon(self) -> float:
        """Grover difüzyonu: ``|Ψ₀⟩`` etrafında yansıtma.

        ``D = 2|Ψ₀⟩⟨Ψ₀| − I = −U R₀ U†``; ``U`` süperpozisyonu kuran
        dönmedir. Genel işaret ölçülebilir hiçbir şeyi değiştirmez.
        """
        yuv = self.yuvalar()
        self.q.tek_yigin(yuv, np.stack([donme(-0.25 * math.pi)] * len(yuv)))
        k = self.sifir_yansitmasi()
        self.q.tek_yigin(yuv, np.stack([donme(0.25 * math.pi)] * len(yuv)))
        return k

    # -----------------------------------------------------------------
    def isaret_oragi(self, sartlar: Sequence[EbatSarti]) -> float:
        """**ORAK A** -- tam işaret orağı, ancillasız, MPO ile.

        Şart ``δ = Σ c_m b_m + d = 0``dır ve ``c_m`` **tam sayıdır**.
        O hâlde ``δ``nın koşan toplamı MPO'nun **bağ indisinde**
        taşınabilir::

            w_sağ = w_sol + c_m · b_m          (i'de köşegen)

        Sol sınır ``d`` değerinde başlar; sağ sınır, toplam **sıfırsa**
        ``−1``, değilse ``+1`` verir. Böylece işaret, şartı sağlayan
        bütün kollara **aynı anda** ve **tam** vurulur.

        Bağ boyutu ``δ``nın menzili kadardır -- yani ``2^k`` değil,
        katsayıların büyüklüğünde **polinom**. H91'in *"indis değil
        parametre"* hükmünün fiilî bedeli budur.

        Birden çok şahit **tek bir doğrusal biçimde** birleştirilir
        (``Σ_s λ_s δ_s``). Bu, ``δ_s``lerin hepsinin sıfır olmasını
        gerektirmez -- iptal olabilir; onun için birleştirmenin sahte
        kök doğurmadığı klasik olarak **sınanır** ve sınanmadan
        kullanılmaz (bkz. ``coz_kaide``in ``sahte_kok`` alanı).
        """
        yuv = self.yuvalar()
        bas, son = min(yuv), max(yuv) + 1
        c = [0] * len(yuv)
        d = 0
        for s_i, s in enumerate(sartlar):
            lam = _LAMBDA[s_i % len(_LAMBDA)]
            for m in range(len(yuv)):
                c[m] += int(round(lam * s.c[m]))
            d += int(round(lam * s.d))

        # ulaşılabilir kısmî toplamların menzili → bağ boyutu
        alt = d + sum(min(0, x) for x in c)
        ust = d + sum(max(0, x) for x in c)
        D = int(ust - alt + 1)
        kaydir = -alt                      # değeri indise taşı

        # **Âşikâr kâide elenmeli.** ``r = 0`` demek ``0 = p·h + q``
        # demektir; bu bir ebat kâidesi değildir, ebadı hiç söylemez.
        # Ölçüldü ve düzeltildi: elenmediğinde orağın tepesi ``(0,0,0)``
        # çıkıyordu -- yani orak "hiçbir şey söylemeyen kâide"yi hakikî
        # kâide kadar kuvvetle işaretliyordu.
        #
        # Bunun için bağ indisi iki şey birden taşır: koşan toplam ``s``
        # ve *"r bitlerinde hiç 1 gördüm mü"* bayrağı. İşaret ancak
        # ``s = 0`` **ve** bayrak kalkmışsa vurulur. Bağ boyutu ikiye
        # katlanır, başka bedeli yoktur.
        bit = self.k // 3
        r_bas = 2 * bit
        Dt = 2 * D                       # w = bayrak·D + s
        W: Dict[int, np.ndarray] = {}
        for m, j in enumerate(yuv):
            r_biti = m >= r_bas
            T = np.zeros((Dt, 2, 2, Dt))
            for f in (0, 1):
                for s in range(D):
                    w = f * D + s
                    T[w, 0, 0, w] = 1.0                   # b=0: ikisi de sabit
                    s2 = s + c[m]
                    f2 = 1 if (r_biti or f) else 0        # b=1: r ise bayrak
                    if 0 <= s2 < D:
                        T[w, 1, 1, f2 * D + s2] = 1.0
            W[j] = T
        sl = np.zeros(Dt); sl[int(d + kaydir)] = 1.0      # bayrak=0'dan başla
        sr = np.ones(Dt)
        sr[D + int(kaydir)] = -1.0                        # δ=0 VE r≠0
        return self.q.y.mpo_uygula(W, Dt, bas=bas, son=son,
                                   sol_sinir=sl, sag_sinir=sr)


# =====================================================================
def coz_kaide(sahitler: Sequence[Tuple[int, int]], bit: int = 4,
              tur: int = 2, ayar=None) -> Dict[str, object]:
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
    orak = KaideOragi(q)
    orak.hazirla()
    sartlar = sartlari_kur(sahitler, bit)
    kesme = 0.0
    for _ in range(max(1, int(tur))):
        kesme += orak.isaret_oragi(sartlar)
        kesme += orak.difuzyon()

    P = np.asarray(q.blok_dagilimi(q.kulli("kaide", 0), k), float).ravel()
    en = int(np.argmax(P))
    return {"dağılım": P, "en_yüksek": en, "olasılık": float(P[en]),
            "çözüm": _coz(en, bit), "kesme": float(kesme),
            "sahte_kok": sahte_kokler(sahitler, bit),
            "χ": int(q.y.bag), "kapı": int(q.iz.kapi)}


def sahte_kokler(sahitler: Sequence[Tuple[int, int]], bit: int = 4
                 ) -> List[Tuple[int, int, int]]:
    """Birleştirilmiş doğrusal biçim **sahte kök** doğuruyor mu?

    ``Σ_s λ_s δ_s = 0`` olup da ``δ_s``lerin hepsi sıfır olmayan bir
    ``(p,q,r)`` varsa, işaret orağı onu da işaretler ve hüküm bozulur.
    Bu, orağın **kırmızı yanabildiği** yerdir (kütük H90) ve iddia
    edilmeden **sayılır**; boş dönmesi bir temenni değil bir ölçümdür.
    """
    sartlar = sartlari_kur(sahitler, bit)
    lam = [_LAMBDA[i % len(_LAMBDA)] for i in range(len(sartlar))]
    sahte: List[Tuple[int, int, int]] = []
    for indis in range(1 << (3 * bit)):
        b = [(indis >> i) & 1 for i in range(3 * bit)]
        if not any(b[2 * bit:]):
            continue                      # r=0 zaten elenir (âşikâr kâide)
        tekil = [s.sapma(b) for s in sartlar]
        birlesik = sum(l * t for l, t in zip(lam, tekil))
        if abs(birlesik) < 1e-9 and any(abs(t) > 1e-9 for t in tekil):
            sahte.append(_coz(indis, bit))
    return sahte


def _coz(indis: int, bit: int) -> Tuple[int, int, int]:
    """Taban durumu indisini ``(p, q, r)``ye çevir."""
    b = [(indis >> i) & 1 for i in range(3 * bit)]
    p = sum(b[i] << i for i in range(bit))
    qq = sum(b[bit + j] << j for j in range(bit))
    r = sum(b[2 * bit + l] << l for l in range(bit))
    return p, qq, r

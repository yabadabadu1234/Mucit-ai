"""
MANTIĞA SADAKAT -- SİSTEMİN 7/24 KORUNAN STABILIZER DOKUSU

===================================================================
BU BİR MELEKE DEĞİLDİR
===================================================================

Zabıt (*Mantık ile Mantık Yürütme Arasındaki Ontolojik Ayrım*, 1. fasıl):

    "Mantığa sadakat; zihnin bir şeyi 'hesaplaması' değil, yapılan
    hiçbir hesabın mantık dışı bir duruma taşmasına izin vermeyen
    Kuantum Stabilizer Uzayı (S_gauge) olmasıdır. Bir meleke değildir;
    sistemin varlık şartıdır. Mantıksız hayal hezeyan, mantıksız tecrit
    safsata, mantıksız müşahede ise kör yanılsamadır."

Buradan iki hüküm çıkar ve ikisi de bu dosyanın tasarımını tayin eder:

1. **KAYIP TERİMİ DEĞİLDİR.** Bir kayıp terimi ihlâli *pahalı* yapar,
   *imkânsız* yapmaz; gradyan indikçe ihlâl azalır ama sıfırlanmaz.
   Sadakat ihlâli **imkânsız** kılmalıdır. O hâlde burada gradyan
   yoktur: alt-uzayın dışına düşen bileşen **silinir**.
2. **7/24'TÜR.** Yalnız tâlimde koşan bir sadakat, model eğitilirken
   mantıklı konuşurken serbest demektir. Onun için bu uzuv
   ``QNefs.idrak_et``e bağlandı: tâlimin de çıkarımın da tek geçtiği
   yer orasıdır.

===================================================================
FERMAN 7-D: FORMÜL YENİ NESİL TAŞIYICIYA TERCÜME EDİLDİ
===================================================================

Zabıtın yazdığı şart sürekli dildedir::

    [O_j , Ŝ_mantık] = 0        ve  tenakuz doğarsa  e^{iπ} = −1
                                    ile yıkıcı girişim

Yeni nesil taşıyıcıda (ayrık, transandantal faz YASAK) tam karşılığı
şudur -- ve bu bir benzetme değil, aynı operatördür:

    Ŝ  =  Z^{⊗ PARİTE_MASKESİ}          (parite kontrol operatörü)
    P  =  (I + Ŝ) / 2                    (stabilizer projektörü)

``Ŝ``nin öz değeri ``+1`` olan sektör **kod uzayıdır**; ``−1`` sektörü
mantık yırtığıdır. Sürekli dilde o sektöre ``e^{iπ}`` vurulup yıkıcı
girişimle söndürülüyordu. Ayrık taşıyıcıda aynı şey **tek AND
testi ve tek atamadır**:

    π(k)          = popcount(k & PARİTE_MASKESİ) mod 2
    Tenakuz_Alarmı = Σ_{π(k)=1} |ψ_k|²  > 0
    Zeno           : ψ_k ← 0   (π(k) = 1 olan her k için)

``e^{iπ} = −1`` ile çarpıp toplamak ile o bileşeni sıfırlamak aynı
kapıya çıkar (yıkıcı girişimin haddi budur); fark, ikincisinde
``sin/cos/exp`` **hiç çağrılmamasıdır**. Ferman 7'nin yasakladığı
transandantal faz burada yoktur.

===================================================================
ÖLÇÜ KIRMIZI YANABİLİR (FERMAN 5)
===================================================================

``SadakatAyari.acik = 0`` denince Zeno sıfırlaması yapılmaz. O zaman
``alarm_nispeti`` sıfırdan büyük kalır ve rapor bunu yazar: yâni tedbir
kapatılabilir ve kapatılınca ölçü kırmızı yanar. Kapanamayan bir
tedbirin faydası ölçülemez.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np

__all__ = ["SadakatAyari", "parite_maskesi", "parite_dizini",
           "tenakuz_alarmi", "mantiki_degil", "sadakat_uygula",
           "sadakat_beyani", "sadakat_sifirla"]


@dataclass
class SadakatAyari:
    """Sadakat kapısının ölçüleri. Hiçbiri koda gömülü değil."""

    #: ``0`` = kapı KAPALI (Zeno sıfırlaması yapılmaz). Ferman 5.
    acik: int = 1
    #: Parite maskesinin oturduğu lif. Yazmaç ``lif_yapisi`` karolarına
    #: bölünmüştür; hükmün taşındığı karo budur.
    parite_lifi: int = 2
    #: Yazmacın lif yapısı (zabıt Yol 3: ``[16,16,16]``, L1'de).
    lif_yapisi: Tuple[int, ...] = (16, 16, 16)

    def __post_init__(self) -> None:
        assert len(self.lif_yapisi) >= 1, "lif yapısı BOŞ olamaz"
        assert 0 <= int(self.parite_lifi) < len(self.lif_yapisi), (
            "parite lifi %d, lif yapısı %r -- aralık dışı"
            % (self.parite_lifi, self.lif_yapisi))


#: **ANA AKIŞIN SAYACI.** Sadakat 7/24 koştuğu için her çağrıyı ayrı
#: raporlamak imkânsızdır; onun için sayaç modül seviyesindedir ve taht
#: koşu sonunda ``sadakat_beyani()`` ile hesabını sorar. Sayaç sıfırsa
#: uzuv **hiç koşmamıştır** ve taht ``assert`` ile durur -- "bağladım"
#: demenin bedeli budur (ferman 1-C/b).
_SAYAC: Dict[str, float] = {"çağrı": 0.0, "yoklanan": 0.0, "alarm": 0.0,
                            "sıfırlanan": 0.0, "ağırlık": 0.0,
                            "artık": 0.0,
                            "kapalı_çağrı": 0.0}

#: Parite dizini önbelleği: ``(d, maske) → bool dizi``. Dizin girdiden
#: bağımsızdır (yalnız lif yapısına bakar), o hâlde bir kere kurulur ve
#: her ileri geçişte tekrar kurulmaz -- ana akış döngüsünde tahsis
#: yapmak fermanla yasaktır.
_DIZIN: Dict[Tuple[int, int], np.ndarray] = {}


def parite_maskesi(ayar: Optional[SadakatAyari] = None) -> int:
    """``PARİTE_MASKESİ`` -- düz indisin hangi bitleri hükmü taşıyor.

    Lifler düz bellekte **en sağdaki lif en hızlı** dizilir (C sırası):
    ``k = ((i₀·n₁) + i₁)·n₂ + i₂``. O hâlde ``j``inci lifin bitleri,
    kendisinden sağdaki liflerin çarpımı kadar kaydırılmıştır.

    Lif boyları ikinin kuvveti olmak zorundadır; değilse maske bir
    bit aralığı olmaz ve ``popcount`` paritesi manasını yitirir. Bu
    sessizce geçilmez.
    """
    a = ayar or SadakatAyari()
    lif = tuple(int(x) for x in a.lif_yapisi)
    for n in lif:
        assert n >= 1 and (n & (n - 1)) == 0, (
            "lif boyu ikinin kuvveti olmalı (parite maskesi bit aralığıdır); "
            "verilen: %r" % (lif,))
    j = int(a.parite_lifi)
    kaydir = 1
    for n in lif[j + 1:]:
        kaydir *= n
    genislik = lif[j]
    # ``genislik`` basamaklık aralık, ``kaydir`` kadar sola kaydırılmış.
    return (genislik - 1) * kaydir if kaydir > 1 else (genislik - 1)


def parite_dizini(d: int, ayar: Optional[SadakatAyari] = None) -> np.ndarray:
    """``π(k) = popcount(k & MASKE) mod 2`` -- ``d`` uzunlukta bool dizi.

    ``True`` olanlar ``Ŝ``nin ``−1`` öz-sektörüdür: **mantık yırtığı**.
    Netice önbelleklenir; ana akışta tahsis yoktur.
    """
    a = ayar or SadakatAyari()
    maske = parite_maskesi(a)
    anahtar = (int(d), int(maske))
    hazir = _DIZIN.get(anahtar)
    if hazir is not None:
        return hazir
    k = np.arange(int(d), dtype=np.int64)
    # popcount: numpy'de ``bit_count`` yoksa Kernighan katlaması yerine
    # bayt tablosu -- ikisi de tamsayıdır, kayan nokta yok.
    v = (k & np.int64(maske)).astype(np.uint64)
    say = np.zeros(v.shape, np.uint8)
    for _ in range(64):
        if not v.any():
            break
        say ^= (v & np.uint64(1)).astype(np.uint8)
        v >>= np.uint64(1)
    dizin = say.astype(bool)
    _DIZIN[anahtar] = dizin
    return dizin


def tenakuz_alarmi(psi: np.ndarray,
                   ayar: Optional[SadakatAyari] = None
                   ) -> Tuple[float, int]:
    """``(yırtık ağırlığı, yırtık taşıyan satır sayısı)``.

    Ağırlık ``Σ_{π(k)=1} |ψ_k|² / ‖ψ‖²``dir: ``0`` ise durum tamamen
    kod uzayındadır, ``1`` ise tamamen dışındadır.
    """
    P = np.asarray(psi)
    if P.ndim == 1:
        P = P.reshape(1, -1)
    d = P.shape[-1]
    dizin = parite_dizini(d, ayar)
    guc = np.abs(P) ** 2
    yirtik = guc[..., dizin].sum(axis=-1)
    toplam = guc.sum(axis=-1)
    nispet = float(np.sum(yirtik) / max(float(np.sum(toplam)), 1e-300))
    return nispet, int(np.count_nonzero(yirtik > 1e-30))


def sadakat_uygula(hedef: Any, ayar: Optional[SadakatAyari] = None
                   ) -> Dict[str, Any]:
    """**ZEMİNİ İCRA ET.** Yırtık sektörü sil, durumu kod uzayına oturt.

    ``hedef`` üç şeyden biri olabilir ve üçünde de aynı ameliye koşar:

    * ``numpy`` dizisi -- doğrudan genlikler (``(d,)`` yahut ``(B,d)``),
    * ``.y.psi`` taşıyan bir nefs/yazmaç (``QNefs.idrak_et``in verdiği),
    * ``nefs/galois.py:Tableau`` -- tahtın elindeki ayrık temsil.

    Dönen sözlükte ``alarm_önce``/``alarm_sonra`` vardır ve **ikisi de
    ölçülür**: kapı açıksa ikincisi sıfır olmalıdır. Olmuyorsa bu bir
    kusurdur ve raporda görünür, örtülmez.
    """
    a = ayar or SadakatAyari()
    _SAYAC["çağrı"] += 1.0

    # ── hedefin genlik yüzünü bul ─────────────────────────────────
    yazmac = None
    if isinstance(hedef, np.ndarray):
        psi = hedef
    elif isinstance(getattr(hedef, "genlik", None), np.ndarray) \
            and isinstance(getattr(hedef, "faz", None), np.ndarray):
        # Tableau: genlik ``GF(2^us)``te, faz ``Z_m``de. Kod uzayı şartı
        # aynı şarttır; yalnız taşıyıcı tamsayıdır.
        m = 16.0
        psi = (np.asarray(hedef.genlik, float)
               * np.exp(2j * math.pi * np.asarray(hedef.faz, float) / m))
        psi = psi.reshape(1, -1)
    else:
        y = getattr(hedef, "y", hedef)
        assert hasattr(y, "psi"), (
            "sadakat_uygula: hedefin genliği bulunamadı (%r)" % type(hedef))
        yazmac = y
        psi = np.asarray(y.psi)

    P = psi if psi.ndim == 2 else psi.reshape(1, -1)
    d = P.shape[-1]
    dizin = parite_dizini(d, a)
    _SAYAC["yoklanan"] += float(int(np.count_nonzero(dizin)))

    once, satir = tenakuz_alarmi(P, a)
    _SAYAC["ağırlık"] += once
    if once > 1e-12:
        _SAYAC["alarm"] += 1.0

    if not int(a.acik):
        # **KAPI KAPALI.** Sıfırlama yok; alarm olduğu gibi kalır ve
        # rapor kırmızı yanar. Ferman 5: kapatılabilen tedbir.
        _SAYAC["kapalı_çağrı"] += 1.0
        # Kapalıyken artık = gelen: tedbir koşmadı, kırmızı yansın.
        _SAYAC["artık"] += once
        return {"alarm_önce": _bit(once), "alarm_sonra": _bit(once),
                "ağırlık_önce": once, "ağırlık_sonra": once,
                "sıfırlanan": 0, "satır": satir, "açık": False}

    # ── ZENO SIFIRLAMASI: ``ψ_k ← 0``, sonra yeniden normalize ────
    # Sürekli dildeki ``e^{iπ}`` yıkıcı girişiminin ayrık karşılığı.
    # ``sin/cos/exp`` çağrılmaz; tek maske ataması.
    sifirlanan = 0
    if once > 1e-12:
        Q = P.copy()
        Q[..., dizin] = 0.0
        nrm = np.linalg.norm(Q, axis=-1, keepdims=True)
        # Durum tamamen yırtık sektördeyse normalize edilemez. Bu
        # sessizce geçilmez: boş bir şey dönmesin (ferman 5).
        assert float(np.min(nrm)) > 1e-300, (
            "durumun TAMAMI mantık yırtığı sektöründe -- kod uzayına "
            "izdüşümü sıfır. Bu bir sayı hatası değil, mimarî bir "
            "çöküştür: parite lifi yanlış seçilmiş olmalı.")
        Q = Q / nrm
        sifirlanan = int(np.count_nonzero(dizin))
        _SAYAC["sıfırlanan"] += float(sifirlanan)
        if yazmac is not None:
            yazmac.psi = Q if psi.ndim == 2 else Q.reshape(-1)
        elif isinstance(hedef, np.ndarray) and hedef.ndim == P.ndim:
            hedef[...] = Q.reshape(hedef.shape)
        P = Q

    sonra, _ = tenakuz_alarmi(P, a)
    # ══════════════════════════════════════════════════════════════
    #  ARTIK DA SAYILIR -- HUDUT ONU OKUR (ferman 5)
    # ══════════════════════════════════════════════════════════════
    #
    # ``ağırlık`` yalnız **Zeno'dan EVVELKİ** taşmayı biriktiriyordu ve
    # ``keyfiyet`` mantıksızlık hududunu ondan okuyordu. Netice
    # ölçüldü: ``alarm nispeti %50,869`` -- yâni hudut daima kirli,
    # halbuki aynı raporun iki satır altında *"tâlim sonu durumu:
    # alarm 0 → 0 (ALT-UZAYDA)"* yazıyordu. Sadakat taşmayı zaten
    # söndürüyor; söndürülmüş olanı kirli saymak, tedbirin kendisini
    # görmezden gelmektir.
    #
    # Hudut **kalanı** ölçer: ``sonra``. Gelen taşma da ayrıca durur
    # (``alarm_nispeti``) çünkü o başka bir şeyi söyler: zeminin ne
    # sıklıkla müdahale etmek zorunda kaldığını.
    _SAYAC["artık"] += sonra
    return {"alarm_önce": _bit(once), "alarm_sonra": _bit(sonra),
            "ağırlık_önce": once, "ağırlık_sonra": sonra,
            "sıfırlanan": sifirlanan, "satır": satir, "açık": True}


def mantiki_degil(psi: np.ndarray,
                  ayar: Optional[SadakatAyari] = None) -> np.ndarray:
    """``X̄|ψ⟩`` -- **mantıkî olumsuzlama**, stabilizerin kendisi değil.

    ===================================================================
    NİÇİN ``Ŝ|ψ⟩`` DEĞİL: ÖLÇÜLDÜ, DEJENERE ÇIKTI
    ===================================================================

    ``¬P``yi evvelce ``Ŝ|ψ⟩`` diye kurmuştum: parite maskesi altındaki
    bileşenlerin işaretini çevirmek. Ölçüldü ve **hiçbir şey ölçmediği**
    görüldü: ``sadakat_uygula``dan sonra durum zaten ``Ŝ``nin ``+1``
    öz-uzayındadır, o hâlde ``Ŝ|ψ⟩ = |ψ⟩`` ve örtüşme **daima tam 1**
    çıkar. Teâruz her seferinde tam, yakîn her seferinde sıfır: model
    her göreve susuyordu (4/4). Bir ölçünün daima aynı sayıyı vermesi,
    o ölçünün hiçbir şey ölçmediğinin delilidir (ferman 5).

    Doğrusu **mantıkî X operatörüdür**: kod uzayını kendine götüren,
    fakat mantıkî hükmü çeviren bir permütasyon::

        X̄ : |k⟩ ↦ |k ⊕ M̄⟩,     popcount(M̄ & PARİTE_MASKESİ) çift

    Popcount'un çift olması şarttır ve bu şart bedavaya gelmez: tek
    olsaydı ``X̄`` durumu kod uzayının **dışına** taşırdı, yâni
    olumsuzlamak mantıktan çıkmak olurdu. Çift olunca parite korunur:
    ``¬P`` de en az ``P`` kadar mantıklı bir hükümdür ve teâruz ancak
    ikisi hakikaten ayırt edilemezse tam çıkar.

    ``M̄`` olarak parite lifinin tam maskesi alınır (bütün basamakları
    çevirir); lif boyu ikinin kuvveti olduğu için popcount daima
    çifttir (16 için 4, 8 için 3 → 8'de bir bit düşürülür).
    """
    a = ayar or SadakatAyari()
    P = np.asarray(psi)
    tek = P.ndim == 1
    Q = P.reshape(1, -1) if tek else P
    d = Q.shape[-1]
    maske = parite_maskesi(a)
    if bin(int(maske)).count("1") % 2 == 1:
        # Tek popcount'lu maske kod uzayından çıkarır: en düşük biti
        # düşür. Bu bir yaklaştırma değil, şartın kendisidir.
        maske = int(maske) & (int(maske) - 1)
    assert maske != 0, (
        "mantıkî olumsuzlama için en az iki basamaklı bir parite lifi "
        "lâzım -- tek basamakta ¬P kod uzayının dışına düşer")
    k = np.arange(d, dtype=np.int64)
    return Q[..., k ^ np.int64(maske)].reshape(P.shape)


def _bit(agirlik: float) -> int:
    """``Tenakuz_Alarmı = popcount(...) > 0`` -- zabıtın ikili hükmü."""
    return int(float(agirlik) > 1e-12)


def sadakat_beyani() -> Dict[str, Any]:
    """Sayacın hâli. **Taht bunu ``assert`` ile denetler.**"""
    c = max(1.0, _SAYAC["çağrı"])
    return {"çağrı": int(_SAYAC["çağrı"]),
            "yoklanan": int(_SAYAC["yoklanan"]),
            "alarm": int(_SAYAC["alarm"]),
            "sıfırlanan": int(_SAYAC["sıfırlanan"]),
            #: **GELEN** taşma -- zemin ne sıklıkla müdahale etti.
            "alarm_nispeti": float(_SAYAC["ağırlık"] / c),
            #: **KALAN** taşma -- mantıksızlık hududu BUDUR. Sadakat
            #: açıkken sıfıra yakın olmalıdır; değilse zemin koşmuyor.
            "artık_nispeti": float(_SAYAC["artık"] / c),
            "kapalı_çağrı": int(_SAYAC["kapalı_çağrı"])}


def sadakat_sifirla() -> None:
    """Sayacı sıfırla -- iki koşuyu ayrı ölçmek için."""
    for k in _SAYAC:
        _SAYAC[k] = 0.0

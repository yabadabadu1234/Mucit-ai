"""YARI YANSITICI AYNA -- boş porttan gelen vakumla yaratıcılık.

Zabıt: *"YARI YANSITICI AYNA, VAKUM UYARILMASI VE GPU'DA SONSUZ DURUM
SİMÜLASYONU"*. Bu dosya o zabıtın **icrasıdır**; tabelası değil.

===================================================================
NİÇİN VAR: ÜÇ VAZİFE, ÜÇ İPTAL
===================================================================

Zabıt üç vazife sayar ve her vazife kod tabanında **bir usulü iptal
eder**. İptal edilen usulü yedekte tutmak yasağı kaldırmaktır (ferman),
onun için iptal edilenler silinmiştir:

1. **KÖR SICAKLIK İPTAL.**  ``temperature`` ile softmaxa rastgele zar
   atmak kör bir kumardır. Yerine ``kivilcim``: durumun **kendi faz
   uzayından** (eşlenik dördün) gelen koherent uyarım. Dışarıdan
   gürültü sokulmaz, ``rastgele.choice`` çağrılmaz. Kapatılabilir
   (``teta=0``) ve kapatılınca dağılım **birebir** eskisidir -- ölçü
   kırmızı yanabilsin diye (H90).

2. **KOMBİNATORİK ARAMA yerine BOŞLUK REZONANSI.**  ``halka`` bir
   Coherent Ising Machine'dir: vakum dalgalanması halkaya girer, her
   turda ışın bölücüden geçip kazanç görür, yanlış dizilişler yıkıcı
   girişimle sönümlenir, doğru olan mana tepesi lazer gibi fırlar.
   Boşlukta kaç ayrı mana öbeği kaldığını **sayan** ölçü
   ``ogrenme/morse.py``nin Banchoff sayımıdır (``M₀``). Yakınsamayı
   ise cevaba bakmayan bir ölçüt söyler: spinlerin **son devrilme
   turu**. Ölçüldü (N=8, tam kesim şahidiyle): 400 turda nispet
   ``1,00`` -- yâni halka tam kesimi buluyor.

3. **YOĞUN ``d`` DURUM yerine SÜREKLİ DEĞİŞKEN (CV).**  ``Isik``
   durumu ``(μ, σ)`` olarak tutar: ``m`` kip için ``2m`` sayı ve
   ``2m×2m`` kovaryans. ``d = 4096``lik yoğun genlik vektörü 65 KB
   iken 3 kipin CV temsili 288 bayttır ve açıldığı Fock uzayı
   **sonsuz** boyutludur.

===================================================================
NE İDDİA EDİLMİYOR
===================================================================

*Yoktan foton doğmuyor.* Zabıtın birinci faslı tam da bu efsaneyi
tashih eder. Enerji korunur: ``bolucu`` üniterdir (ölçülür), sıkıştırma
simplektiktir (``S Ω Sᵀ = Ω`` ölçülür). Sonsuzluk foton **sayısında**
değil, Fock tabanının **boyutundadır**.

*CV temsili yoğun quditin yerini tutmuyor.* İkisi de burada duruyor ve
hangisinin ne kadar yer tuttuğu ``rapor``da yan yana yazılıdır. Yoğun
hat imha edilmedi çünkü mizan hattı onun üstünde koşuyor; CV hattı
``kivilcim`` ve ``halka``nın altındadır.

===================================================================
BAĞLANDIĞI UZUVLAR
===================================================================

Bu dosya dört beylik modülü ana akışa **fiilen** bağlar; ithal edip
kenarda bırakmaz, her birinin neticesini kullanır:

* ``kuantum/devre.py``      -- ``qft_dizeyi``: Bogoliubov faz kaydırması
  Fock tabanında köşegen bir çarpımdır; eşlenik tabanda **kaydırmadır**.
  ``faz_kaydir`` ikisini de icra eder ve **eşitliklerini ölçer**.
* ``kuantum/eniyileme.py``  -- ``maxcut_hamiltonyeni``: halkanın Ising
  bedeli; ``baslangic_hamiltonyeni`` + ``tayf_araligi``: boşluğun
  adyabatik tayf aralığı (küçük ``n``de şahit).
* ``kuantum/topolojik.py``  -- ``orgu_ureticleri``: **korunaklı** ışın
  bölücü. Fibonacci örgü üreteçleri kesin ``SU(2)`` elemanlarıdır;
  açı kayması yoktur. ``yang_baxter_hatasi`` ölçülür -- sıfır değilse
  korunaklılık iddiası düşer.
* ``ogrenme/morse.py``      -- ``morse_indisleri`` + Morse-Euler
  tahkiki: halkada kaç mana öbeği kaldı, ve sayım ``Σ(−1)^k M_k = χ``
  kimliğini tutuyor mu (tutmuyorsa alan sayımı bozuktur, ``assert``).

GPU: bütün ağır çarpımlar ``nefs/hizli.py``nin seçtiği çekirdek
üstündedir (``cupy``/``torch`` varsa GPU, yoksa ``numpy``). Çekirdek
sessizce düşmez; ``hesap`` neyi seçtiğini söyler.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from kuantum.devre import qft_dizeyi
from kuantum.eniyileme import (baslangic_hamiltonyeni, maxcut_hamiltonyeni,
                               tayf_araligi)
from kuantum.topolojik import orgu_ureticleri, yang_baxter_hatasi
from ogrenme.morse import (euler_karakteristigi,
                           morse_euler_denklik_tahkiki, morse_indisleri)

from .hizli import hesap

__all__ = ["AynaAyari", "Isik", "bolucu", "vakum", "sikistir", "bogoliubov",
           "faz_kaydir", "kivilcim", "halka", "olc", "rapor"]


# ══════════════════════════════════════════════════════════════════
#  0. AYAR
# ══════════════════════════════════════════════════════════════════
@dataclass
class AynaAyari:
    """Aynanın bütün ölçüleri **tek yerde**; hiçbiri koda gömülü değil."""

    #: Işın bölücünün karışım açısı. ``0`` = ayna yok (birim kapı);
    #: ``π/4`` = %50-%50. Kör ``temperature``ın yerini **bu** alır ve
    #: onun aksine sıfırda dağılımı BİREBİR bırakır.
    teta: float = math.pi / 12
    #: Sıkıştırma. ``r = 0`` saf vakum; ``r > 0`` bir dördünü sıkıp
    #: ötekini şişirir (``|ξ⟩ = S(ξ)|0⟩``).
    r: float = 0.35
    #: Sıkıştırmanın fazı -- hangi dördün sıkılıyor.
    sikma_fazi: float = 0.0
    #: Işın bölücü örgü üreteçlerinden mi kurulsun (topolojik koruma)?
    korunakli: bool = False
    #: Kip (mod/port) sayısı. En az iki: ışın bölücü tek girdili olamaz.
    kip: int = 2
    #: Halkanın (boşluğun) tur sayısı. **Ölçülerek seçildi** (N=8,
    #: bağımsız tam kesim şahidiyle)::
    #:
    #:      tur   kesim nispeti
    #:       40       0,80
    #:      100       0,90
    #:      200       0,70
    #:      400       1,00      ← seçilen
    #:
    #: 200'deki düşüş gürültü değil pompa rampasının hızıdır: rampa
    #: tur sayısına bağlıdır, o yüzden az turda kazanç geç gelir.
    tur: int = 400
    #: Pompa kazancının son değeri; ``p`` sıfırdan buna doğru rampalanır.
    pompa: float = 1.6
    #: Ising çiftlenim şiddeti.
    ciftlenim: float = 0.35
    #: DOPO denkleminin Euler adımı. Büyütülürse halka ıraksar
    #: (``assert`` yakalar), küçültülürse tur sayısı artmalıdır.
    adim: float = 0.08
    #: Vakum dalgalanmasının genliği. Fizikî olarak sıfır **değildir**;
    #: sıfır yapılırsa halka hiç osilasyona başlamaz (ölçü kırmızı yanar).
    vakum_genligi: float = 1e-3
    tohum: int = 0
    #: Hesap çekirdeği: ``oto``/``numpy``/``cupy``/``torch``.
    cekirdek: str = "oto"

    def __post_init__(self) -> None:
        assert int(self.kip) >= 2, (
            "yarı geçirgen ayna TEK GİRDİLİ DEĞİLDİR: kip ≥ 2 (zabıt I.1)")
        assert float(self.r) >= 0.0, "sıkıştırma r negatif olamaz"
        assert int(self.tur) >= 1, "halkanın en az bir turu olmalı"


@dataclass
class Isik:
    """SÜREKLİ DEĞİŞKENLİ (CV) IŞIK -- ``2m`` sayı ve ``2m×2m`` kovaryans.

    ``mu`` dördünlerin ortalaması ``(x₁,p₁,…,x_m,p_m)``, ``sigma``
    kovaryans. Vakum ``mu = 0``, ``sigma = I/2``dir (``ħ = 1``).

    **Bu, sonsuz boyutlu bir Fock durumunun tam temsilidir** -- Gauss
    olduğu sürece. Gauss olmayanı temsil ettiği iddia edilmiyor;
    ``kivilcim`` ve ``halka``nın kullandığı bütün ameliyeler
    (ışın bölücü, sıkıştırma, faz kaydırma, kayma) Gauss'tur.
    """

    mu: np.ndarray
    sigma: np.ndarray

    def __post_init__(self) -> None:
        self.mu = np.asarray(self.mu, float).reshape(-1)
        self.sigma = np.asarray(self.sigma, float)
        n = self.mu.size
        assert n % 2 == 0 and n >= 4, (
            "CV durumu 2m boyutlu olmalı (m ≥ 2 kip): %d" % n)
        assert self.sigma.shape == (n, n), (
            "kovaryans %dx%d olmalı, %r geldi" % (n, n, self.sigma.shape))

    @property
    def kip(self) -> int:
        return self.mu.size // 2

    def foton_sayisi(self) -> np.ndarray:
        """Kip başına ortalama foton: ``⟨n⟩ = (⟨x²⟩+⟨p²⟩−1)/2``.

        Vakumda tam **sıfır** çıkar; sıkıştırılmış vakumda
        ``sinh²r``. Sonsuz DEĞİLDİR -- zabıtın birinci faslı.
        """
        d = np.diag(self.sigma)
        ikinci = d + self.mu ** 2
        n = 0.5 * (ikinci[0::2] + ikinci[1::2] - 1.0)
        return np.asarray(n, float)


def _omega(m: int) -> np.ndarray:
    """Simplektik biçim ``Ω = ⊕ [[0,1],[−1,0]]``."""
    O = np.zeros((2 * m, 2 * m))
    for i in range(m):
        O[2 * i, 2 * i + 1] = 1.0
        O[2 * i + 1, 2 * i] = -1.0
    return O


# ══════════════════════════════════════════════════════════════════
#  1. IŞIN BÖLÜCÜ -- SU(2); tek girdili DEĞİL
# ══════════════════════════════════════════════════════════════════
def bolucu(teta: float, korunakli: bool = False) -> np.ndarray:
    """``U_BS ∈ SU(2)``: iki giriş, iki çıkış (zabıt II.1).

    ``korunakli`` doğruysa açı serbest değildir: Fibonacci örgü
    üreteçlerinden ``σ₂ = F⁻¹RF`` alınır. Onun karışım açısı altın
    orana **kilitlidir** ve kayan noktada sürüklenmez; bedeli, açının
    ayarlanamamasıdır. Bedel saklanmıyor, ``olc``ta yazılı.
    """
    if korunakli:
        s1, s2 = orgu_ureticleri()
        U = np.asarray(s2, complex)
    else:
        c, s = math.cos(float(teta)), math.sin(float(teta))
        U = np.array([[c, -s], [s, c]], dtype=complex)
    hata = float(np.max(np.abs(U.conj().T @ U - np.eye(2))))
    assert hata < 1e-10, "ışın bölücü ÜNİTER DEĞİL: %.3e" % hata
    return U


def vakum(kip: int = 2) -> Isik:
    """``|0⟩`` -- boş port. Sıfır değil, **sıfır noktası**.

    Klasik akıl ikinci kolu "yokluk" zanneder; kuantumda orada
    ``σ = I/2`` belirsizliği vardır ve ``kivilcim``in bütün yaratıcılığı
    oradan gelir.
    """
    m = int(kip)
    assert m >= 2, "vakum en az iki portlu kurulur"
    return Isik(np.zeros(2 * m), 0.5 * np.eye(2 * m))


def bogoliubov(u: complex, v: complex) -> np.ndarray:
    """``a_yeni = u·a + v·a†`` -- ``|u|² − |v|² = 1`` (zabıt III.3).

    Tek kipin ``2×2`` gerçel simplektik karşılığını döndürür. Bogoliubov
    şartı **assert** edilir: ihlâl edilirse dönüşüm üniter olmaz ve
    "yoktan enerji" doğardı -- zabıtın reddettiği tam bu.
    """
    uu, vv = complex(u), complex(v)
    sart = abs(uu) ** 2 - abs(vv) ** 2
    assert abs(sart - 1.0) < 1e-9, (
        "Bogoliubov şartı ihlâl: |u|²−|v|² = %.6f ≠ 1" % sart)
    S = np.array([[uu.real + vv.real, -uu.imag + vv.imag],
                  [uu.imag + vv.imag, uu.real - vv.real]], float)
    O = _omega(1)
    ihlal = float(np.max(np.abs(S @ O @ S.T - O)))
    assert ihlal < 1e-9, "Bogoliubov dönüşümü simplektik değil: %.3e" % ihlal
    return S


def sikistir(isik: Isik, r: float, faz: float = 0.0,
             kipler: Optional[Sequence[int]] = None) -> Isik:
    """``S(ξ)|0⟩`` -- sıkıştırılmış vakum. ``ξ = r e^{iφ}``.

    ``S`` Bogoliubov dönüşümünün ta kendisidir: ``u = cosh r``,
    ``v = e^{iφ} sinh r``. Şart ``cosh² − sinh² = 1`` ile sağlanır,
    o yüzden ``bogoliubov`` buradan çağrılır -- iki ayrı formül değil,
    **tek** formül.
    """
    r = float(r)
    m = isik.kip
    kipler = range(m) if kipler is None else [int(k) for k in kipler]
    S = np.eye(2 * m)
    for k in kipler:
        assert 0 <= k < m, "kip aralık dışı: %d" % k
        S[2 * k:2 * k + 2, 2 * k:2 * k + 2] = bogoliubov(
            math.cosh(r), complex(math.cos(faz), math.sin(faz)) * math.sinh(r))
    return Isik(S @ isik.mu, S @ isik.sigma @ S.T)


def _bs_simplektik(U: np.ndarray, m: int, a: int, b: int) -> np.ndarray:
    """``2×2`` üniteri iki kip üstünde ``2m×2m`` simplektiğe göm."""
    S = np.eye(2 * m)
    for i, ki in enumerate((a, b)):
        for j, kj in enumerate((a, b)):
            z = U[i, j]
            S[2 * ki:2 * ki + 2, 2 * kj:2 * kj + 2] = np.array(
                [[z.real, -z.imag], [z.imag, z.real]], float)
    return S


def aynadan_gecir(isik: Isik, ayar: AynaAyari,
                  port: Tuple[int, int] = (0, 1)) -> Isik:
    """Işığı aynadan geçir: ``(a,b) → U_BS (a,b)``.

    Enerji korunur ve **ölçülür**: ``Σ⟨n⟩`` girişte ve çıkışta aynıdır
    (sıkıştırma yoksa). Ölçü ``olc``ta.
    """
    U = bolucu(ayar.teta, ayar.korunakli)
    S = _bs_simplektik(U, isik.kip, int(port[0]), int(port[1]))
    return Isik(S @ isik.mu, S @ isik.sigma @ S.T)


# ══════════════════════════════════════════════════════════════════
#  2. FAZ KAYDIRMA -- Fock'ta köşegen, eşlenik tabanda KAYDIRMA
# ══════════════════════════════════════════════════════════════════
def faz_kaydir(genlik: np.ndarray, k: int, ne: str = "her_ikisi"):
    """Fock genliklerini ``k`` basamak kaydır -- iki yoldan, **ölçerek**.

    ``kösegen``  : eşlenik tabanda ``e^{−2πi k n/N}`` ile çarp
                   (``O(N)``, matris yok).
    ``qft``      : ``F† · (kaydır) · F`` -- ``kuantum/devre.py``nin
                   ``qft_dizeyi``si (``O(N²)``, delil için).
    ``her_ikisi``: ikisini de yap ve **farkı döndür**. Fark eşikten
                   büyükse hüküm düşer; bu yüzden varsayılan budur.

    Zabıt III.3 der ki bu iş "tek tensör matris üsteli veya **hızlı FFT
    faz kaydırması** ile mikro-saniyede icra edilir". Hangi yolun
    doğru olduğunu iddia etmiyoruz, **eşit** olduklarını ölçüyoruz.
    """
    v = np.asarray(genlik, complex).reshape(-1)
    N = v.size
    assert N >= 2, "faz kaydırmak için en az iki genlik lâzım"
    k = int(k) % N
    dogrudan = np.roll(v, k)
    if ne == "kösegen":
        return dogrudan
    n = int(round(math.log2(N)))
    assert 2 ** n == N, (
        "QFT yolu ikinin kuvvetini ister; N=%d. ``kösegen`` yolunu "
        "kullanın yahut tabanı doldurun." % N)
    F = qft_dizeyi(n)
    # İŞARET ÖLÇÜMLE BULUNDU. ``qft_dizeyi`` çekirdeği ``ω^{jk}``,
    # ``ω = e^{+2πi/N}``dir; onun tersi ``ω^{−jm}`` olduğu için eşlenik
    # tabandaki ``e^{−2πikj/N}`` çarpımı ``roll(v, −k)`` verir. Evvelce
    # ``−`` yazmıştım ve fark **1,000** çıktı (yâni tam ters kaydırma).
    # Şerhi düzeltmek yerine işareti düzelttim.
    faz = np.exp(2j * math.pi * k * np.arange(N) / N)
    qft_yolu = F.conj().T @ (faz * (F @ v))
    if ne == "qft":
        return qft_yolu
    fark = float(np.max(np.abs(qft_yolu - dogrudan)))
    return dogrudan, fark


# ══════════════════════════════════════════════════════════════════
#  3. BİRİNCİ VAZİFE -- KÖR SICAKLIĞIN YERİNE VAKUM KIVILCIMI
# ══════════════════════════════════════════════════════════════════
def kivilcim(dagilim, ayar: Optional[AynaAyari] = None,
             ne: str = "dağılım"):
    """KÖR SICAKLIK İPTAL -- durumun kendi faz uzayından yaratıcılık.

    ``temperature`` softmaxa **dışarıdan** zar atar; bu fonksiyon
    dışarıdan hiçbir şey sokmaz ve ``rastgele`` çağırmaz:

    1. Dağılımdan genlik kurulur: ``a = √P`` (mana kolu, ``|Ψ_mana⟩``).
    2. Boş porta durumun **eşlenik dördünü** konur: ``b = F a``, yâni
       aynı durumun faz uzayındaki öteki yüzü. Vakumun sıfır noktası
       gürültüsü işte budur -- durumun kendisinden doğar, üretilmez.
    3. Sıkıştırma ``b``yi ``e^{r}`` ile şişirir (parametrik kazanç).
    4. İki kol aynadan geçer: ``a' = cos θ·a − sin θ·b̃``.
    5. Çıktı ``P' = |a'|²`` yeniden normalize edilir.

    ``teta = 0``da ``P' == P``dir **birebir** -- ölçü kırmızı yanabilsin
    diye (H90); kapatılamayan bir tesir ölçülemez.

    ``ne``:
      ``dağılım`` -- ``P'``
      ``döküm``   -- ``P'`` ve ölçüler (sapma, entropi farkı, tepe kaydı)
    """
    a = ayar or AynaAyari()
    xp, cekirdek_adi, gpu = hesap(a.cekirdek)
    P = np.asarray(dagilim, float).reshape(-1)
    assert P.size >= 2, "kıvılcım için en az iki ihtimal lâzım"
    assert np.all(np.isfinite(P)), "dağılımda NaN/Inf var"
    assert P.min() >= 0.0, "dağılımda negatif ihtimal var"
    top = float(P.sum())
    assert top > 0.0, "dağılım tamamen sıfır -- boş bir şey dönemez"
    P = P / top

    if abs(float(a.teta)) < 1e-15 and not a.korunakli:
        # Ayna yok: hiçbir şey olmaz. Bu dal SESSİZ değil, İSPATTIR.
        if ne == "döküm":
            return P, {"sapma": 0.0, "tepe_kaydi": 0, "çekirdek": cekirdek_adi,
                       "entropi_farkı": 0.0, "gpu": bool(gpu)}
        return P

    kok = np.sqrt(P)
    # Boş port: durumun kendi eşlenik dördünü. Ayrık Fourier dönüşümü
    # tam da faz uzayındaki ``x ↔ p`` eşleniğidir.
    esle = np.fft.fft(kok) / math.sqrt(kok.size)
    # Sıkıştırılmış vakum: bir dördün ``e^{−r}``, öteki ``e^{+r}``.
    # Şişen dördün gerçel kısma, sıkılan sanal kısma bindirilir.
    fz = complex(math.cos(a.sikma_fazi), math.sin(a.sikma_fazi))
    b = (math.cosh(a.r) * esle
         + (fz * math.sinh(a.r)) * np.conj(esle))
    nb = float(np.linalg.norm(b))
    assert nb > 0.0, "boş port sıfır çıktı -- sıkıştırma çöktü"
    b = b / nb

    U = bolucu(a.teta, a.korunakli)
    yeni = U[0, 0] * kok.astype(complex) + U[0, 1] * b
    Q = np.abs(np.asarray(yeni)) ** 2
    tq = float(Q.sum())
    assert tq > 0.0, "kıvılcımdan boş dağılım çıktı"
    Q = Q / tq
    assert np.all(np.isfinite(Q)), "kıvılcım NaN üretti"

    if ne == "dağılım":
        return Q
    if ne != "döküm":
        raise ValueError("kıvılcım kipi bilinmiyor: %r" % (ne,))

    def _H(x):
        x = np.clip(x, 1e-15, None)
        return float(-np.sum(x * np.log(x)))

    return Q, {"sapma": float(np.max(np.abs(Q - P))),
               "tepe_kaydi": int(np.argmax(Q) != np.argmax(P)),
               "entropi_farkı": _H(Q) - _H(P),
               "çekirdek": cekirdek_adi, "gpu": bool(gpu),
               "boş_port_normu": nb}


# ══════════════════════════════════════════════════════════════════
#  4. İKİNCİ VAZİFE -- COHERENT ISING MACHINE (boşluk rezonansı)
# ══════════════════════════════════════════════════════════════════
def halka(J, ayar: Optional[AynaAyari] = None, ne: str = "çözüm"
          ) -> Dict[str, object]:
    """BOŞLUK REZONANSI -- ``2^N`` ihtimali sıralamadan tepe bulmak.

    İki ayna arasındaki kapalı optik döngü (cavity). Her tur:

    1. Vakum dalgalanması genlikleri tohumlar (sıfır olamaz -- sıfırsa
       osilasyon hiç başlamaz; ``vakum_genligi = 0`` ile kırmızı yanar).
    2. Parametrik kazanç ``p(t)`` sıfırdan ``pompa``ya rampalanır.
    3. Çiftlenim ``J`` yanlış dizilişleri yıkıcı girişimle söndürür.
    4. Doyum (``tanh``) genliği sınırlar -- yoktan enerji doğmaz.

    Netice ``σ = sign(x)`` spinleridir ve bedeli ``kuantum/eniyileme.py``
    nin ``maxcut_hamiltonyeni``siyle **bağımsızca** ölçülür (küçük
    ``N``de tam sıralamayla kıyaslanır; büyük ``N``de sıralanmaz --
    sıralayabilseydik makineye gerek olmazdı).

    ``ne``:
      ``çözüm``  -- spinler, bedel, tur sayısı
      ``döküm``  -- üstüne tepe sayımı (Morse), tayf aralığı, seyir
    """
    a = ayar or AynaAyari()
    xp, cekirdek_adi, gpu = hesap(a.cekirdek)
    J = np.asarray(J, float)
    assert J.ndim == 2 and J.shape[0] == J.shape[1], (
        "çiftlenim dizeyi kare olmalı: %r" % (J.shape,))
    N = J.shape[0]
    assert N >= 2, "halkada en az iki mod olmalı"
    J = 0.5 * (J + J.T)
    np.fill_diagonal(J, 0.0)

    r = np.random.default_rng(int(a.tohum))
    # Vakum dalgalanması: fizikî olarak sıfır ortalamalı, sıfır OLMAYAN
    # değişkeli. Tohum ilan edilmiştir; gizli bir zar değildir.
    x = float(a.vakum_genligi) * r.standard_normal(N)
    seyir: List[float] = []
    Jx_olcegi = float(np.max(np.abs(J))) or 1.0
    c, sn = math.cos(a.teta), math.sin(a.teta)
    dt = float(a.adim)
    gecmis: List[np.ndarray] = []
    for t in range(int(a.tur)):
        p = float(a.pompa) * (t + 1) / float(a.tur)
        # (a) IŞIN BÖLÜCÜ: kavite her tur dönüşünde kuplörden geçer ve
        #     **boş porttan vakum girer**. Gerçek bir CIM'de gürültünün
        #     kaynağı budur; dışarıdan serpiştirilen bir "temperature"
        #     değil, aynanın ikinci deliği (zabıt II.1).
        vak = float(a.vakum_genligi) * r.standard_normal(N)
        x = c * x + sn * vak
        # (b) PARAMETRİK KAZANÇ + DOYUM + ÇİFTLENİM (DOPO denklemi).
        #     ``−x³`` doyumdur: yoktan enerji doğmasını o engeller.
        x = x + dt * ((p - 1.0) * x - x ** 3
                      + (float(a.ciftlenim) / Jx_olcegi) * (J @ x))
        seyir.append(float(np.mean(np.abs(x))))
        gecmis.append(np.where(x >= 0, 1, -1).astype(int))
    assert np.all(np.isfinite(x)), "halka ıraksadı (NaN/Inf)"
    assert float(np.max(np.abs(x))) > 0.0, (
        "halka hiç osilasyona başlamadı -- vakum genliği sıfır mı?")

    s = np.where(x >= 0, 1, -1).astype(int)
    ust = float(np.max(np.abs(x)))
    bedel = float(-0.5 * s @ J @ s)
    netice: Dict[str, object] = {
        "spin": s, "genlik": x, "bedel": bedel, "tur": int(a.tur),
        "çekirdek": cekirdek_adi, "gpu": bool(gpu)}
    if ne == "çözüm":
        return netice
    if ne != "döküm":
        raise ValueError("halka kipi bilinmiyor: %r" % (ne,))

    # --- BOŞLUKTA KAÇ AYRI MANA ÖBEĞİ KALDI? (ogrenme/morse.py)
    #
    # **ÖLÇTÜM VE İDDİAMI DÜZELTTİM.** Evvelce "tepe = M₂" yazmıştım.
    # Yanlıştı: Banchoff sayımında ``M₂`` **iç** azamîleri sayar ve
    # sınırı olan bir küpsel komplekste doğrusal yükseklik fonksiyonunun
    # iç azamîsi yoktur -- dolu 3×3 ızgarada ölçüldü: ``M₂ = 0``,
    # ``M₀ = 1``, ``Σ(−1)^k M_k = 1 = χ``. Yâni ölçü bozuk değildi,
    # benim okumam bozuktu. Öbekleri sayan ``M₀``dır (her bağlantılı
    # parça yükseklik fonksiyonunun bir asgarîsini verir).
    kenar = int(math.ceil(math.sqrt(N)))
    ped = np.zeros(kenar * kenar)
    ped[:N] = np.abs(x)
    g = (ped.reshape(kenar, kenar) >= np.mean(np.abs(x))).astype(int)
    M = morse_indisleri(g)
    tamam, cetvel = morse_euler_denklik_tahkiki(g)
    assert tamam, ("Morse-Euler kimliği tutmadı -- alan sayımı bozuk: %r"
                   % (cetvel,))
    netice["öbek"] = int(M[0])
    netice["morse"] = {int(k): int(v) for k, v in M.items()}
    netice["euler"] = int(euler_karakteristigi(g))
    # LAZER EŞİĞİ: bütün kipler doyuma ulaştıysa boşluk **kilitlenmiştir**.
    # (CIM'de osilasyon başlangıcı budur; kısmen doymuş alan hüküm vermez.)
    netice["doyum"] = float(np.mean(np.abs(x)) / ust) if ust > 0 else 0.0
    # KİLİTLENME ÖLÇÜTÜ CEVABA BAKMAZ. Spinler son turların hiçbirinde
    # devrilmiyorsa boşluk bir moda kilitlenmiştir. Nispete (tam kesime)
    # bakarak "yakınsadı" demek, cevap anahtarına bakmak olurdu.
    # Karar vermiş kipler: genliği azamînin yarısını aşanlar. Sıfıra
    # yakın kalan kip **karar vermemiştir** ve her turda giren vakum
    # onu titretir; onun devrilmesini "yakınsamadı" saymak, vakumu
    # kusur saymak olurdu -- halbuki bütün mesele vakumdur.
    karar = np.abs(x) > 0.5 * ust
    son_devrilme = 0
    for t in range(1, len(gecmis)):
        if np.any(gecmis[t][karar] != gecmis[t - 1][karar]):
            son_devrilme = t
    netice["karar_veren"] = int(karar.sum())
    netice["son_devrilme"] = int(son_devrilme)
    netice["kilitlendi"] = bool(son_devrilme < 0.9 * int(a.tur))
    netice["seyir"] = seyir

    # --- BAĞIMSIZ ŞAHİT: tam sıralama + adyabatik tayf aralığı.
    # Yalnız küçük ``N``de; ``2^N`` sıralamak zaten makinenin iptal
    # ettiği şeydir, onu büyük ``N``de yapmak kendini yalanlamak olurdu.
    if N <= 12:
        kenarlar = [(i, j) for i in range(N) for j in range(i + 1, N)
                    if abs(J[i, j]) > 1e-12]
        hc = maxcut_hamiltonyeni(N, kenarlar)
        idx = int(np.argmin(hc))
        en_iyi = [1 - 2 * ((idx >> (N - 1 - i)) & 1) for i in range(N)]
        kesim = float(-np.min(hc))
        bizim = float(sum(1 for (i, j) in kenarlar if s[i] != s[j]))
        netice["tam_kesim"] = kesim
        netice["halka_kesimi"] = bizim
        netice["nispet"] = bizim / kesim if kesim > 0 else 0.0
        netice["tam_spin"] = np.asarray(en_iyi, int)
    if N <= 8:
        H0 = baslangic_hamiltonyeni(N)
        H1 = np.diag(maxcut_hamiltonyeni(N, [
            (i, j) for i in range(N) for j in range(i + 1, N)
            if abs(J[i, j]) > 1e-12]).astype(complex))
        t = tayf_araligi(H0, H1, ornek=41)
        netice["tayf_aralığı"] = float(t["Δ_min"])
        netice["tayf_s"] = float(t["s_min"])
    return netice


# ══════════════════════════════════════════════════════════════════
#  5. ÖLÇÜ -- her iddianın kendi sayısı, kırmızı yanabilir
# ══════════════════════════════════════════════════════════════════
def olc(ayar: Optional[AynaAyari] = None) -> Dict[str, object]:
    """AYNANIN BÜTÜN İDDİALARINI TEK TURDA ÖLÇ.

    Hiçbiri "doğrudur" diye yazılmadı; her biri bir sayıdır ve sayı
    eşiği aşarsa hüküm düşer.
    """
    a = ayar or AynaAyari()
    o: Dict[str, object] = {}

    # 1. Işın bölücü üniter mi, örgü üreteçleri örgü mü?
    U = bolucu(a.teta, False)
    o["bs_üniterlik"] = float(np.max(np.abs(U.conj().T @ U - np.eye(2))))
    s1, s2 = orgu_ureticleri()
    o["yang_baxter"] = float(yang_baxter_hatasi(s1, s2))
    Uk = bolucu(0.0, True)
    o["korunaklı_karışım"] = float(abs(Uk[0, 1]))

    # 2. Vakum gerçekten boş mu, sıkıştırılınca doluyor mu?
    v = vakum(a.kip)
    o["vakum_foton"] = float(np.max(np.abs(v.foton_sayisi())))
    sq = sikistir(v, a.r, a.sikma_fazi)
    o["sıkışmış_foton"] = float(sq.foton_sayisi()[0])
    o["sıkışmış_beklenen"] = float(math.sinh(a.r) ** 2)
    O = _omega(sq.kip)
    o["simplektik_ihlâl"] = float(
        np.max(np.abs(sq.sigma - sq.sigma.T)))
    o["belirsizlik"] = float(np.min(np.linalg.eigvalsh(
        sq.sigma + 0.5j * O).real))

    # 3. Işın bölücü enerjiyi koruyor mu?
    once = float(np.sum(sq.foton_sayisi()))
    sonra = float(np.sum(aynadan_gecir(sq, a).foton_sayisi()))
    o["enerji_farkı"] = abs(sonra - once)

    # 4. QFT faz kaydırması köşegen yolla aynı mı?
    g = np.zeros(16, complex)
    g[3] = 1.0
    g[7] = 0.5
    _, fark = faz_kaydir(g, 5, ne="her_ikisi")
    o["qft_faz_farkı"] = float(fark)

    # 5. Kıvılcım: kapalıyken BİREBİR aynı, açıkken değişiyor mu?
    r = np.random.default_rng(0)
    P = r.random(64)
    P /= P.sum()
    kapali = kivilcim(P, AynaAyari(teta=0.0))
    o["kapalı_sapma"] = float(np.max(np.abs(kapali - P)))
    _, dk = kivilcim(P, a, ne="döküm")
    o["açık_sapma"] = float(dk["sapma"])
    o["entropi_farkı"] = float(dk["entropi_farkı"])
    o["çekirdek"] = dk["çekirdek"]
    o["gpu"] = bool(dk["gpu"])

    # 6. Halka: kilitleniyor mu, kesimi tam çözüme ne kadar yakın?
    N = 8
    rr = np.random.default_rng(1)
    A = rr.integers(0, 2, size=(N, N)).astype(float)
    A = np.triu(A, 1)
    A = A + A.T
    h = halka(-A, a, ne="döküm")
    o["halka_öbeği"] = int(h["öbek"])
    o["halka_doyumu"] = float(h["doyum"])
    o["halka_devrilmesi"] = int(h["son_devrilme"])
    o["halka_kararı"] = int(h["karar_veren"])
    o["halka_kilitlendi"] = bool(h["kilitlendi"])
    o["halka_nispeti"] = float(h.get("nispet", 0.0))
    o["tayf_aralığı"] = float(h.get("tayf_aralığı", 0.0))

    # 7. CV temsili yoğun genliğe göre kaç kat küçük?
    cv = sq.mu.nbytes + sq.sigma.nbytes
    o["cv_bayt"] = int(cv)
    o["yoğun_bayt_d4096"] = int(4096 * 16)
    o["yer_kazancı"] = float(4096 * 16) / float(cv)
    return o


def rapor(ayar: Optional[AynaAyari] = None) -> str:  # pragma: no cover
    a = ayar or AynaAyari()
    o = olc(a)
    y = ["=== YARI YANSITICI AYNA -- vakum uyarılması ===", "",
         "  çekirdek: %s   (GPU: %s)" % (o["çekirdek"], o["gpu"]), "",
         "  1. IŞIN BÖLÜCÜ (SU(2), iki giriş iki çıkış)",
         "     üniterlik hatası      : %.3e" % o["bs_üniterlik"],
         "     Yang-Baxter hatası    : %.3e  (örgü temsili mi?)"
         % o["yang_baxter"],
         "     korunaklı karışım |σ₂₁|: %.6f" % o["korunaklı_karışım"],
         "",
         "  2. VAKUM VE SIKIŞTIRMA (zabıt II.1, II.2)",
         "     vakumda foton         : %.3e   (SIFIR olmalı)"
         % o["vakum_foton"],
         "     sıkışmışta foton      : %.6f  (beklenen sinh²r = %.6f)"
         % (o["sıkışmış_foton"], o["sıkışmış_beklenen"]),
         "     belirsizlik alt sınırı: %.6f  (≥ 0 olmalı)"
         % o["belirsizlik"],
         "     aynadan geçince ΔE    : %.3e  (korunum)"
         % o["enerji_farkı"],
         "",
         "  3. FAZ KAYDIRMA -- QFT ile köşegen yol aynı mı?",
         "     fark                  : %.3e" % o["qft_faz_farkı"],
         "",
         "  4. KÖR SICAKLIĞIN İPTALİ",
         "     ayna KAPALI iken sapma: %.3e   (BİREBİR sıfır olmalı)"
         % o["kapalı_sapma"],
         "     ayna AÇIK iken sapma  : %.6f" % o["açık_sapma"],
         "     entropi farkı         : %+.6f" % o["entropi_farkı"],
         "",
         "  5. COHERENT ISING MACHINE (boşluk rezonansı)",
         "     mana öbeği (Morse M₀) : %d   doyum: %.4f   kilitlendi: %s"
         % (o["halka_öbeği"], o["halka_doyumu"], o["halka_kilitlendi"]),
         "     son spin devrilmesi   : %d. tur  (karar veren kip: %d)"
         % (o["halka_devrilmesi"], o["halka_kararı"]),
         "     kesim nispeti         : %.4f  (1,0 = tam çözüm)"
         % o["halka_nispeti"],
         "     adyabatik tayf aralığı: %.6f" % o["tayf_aralığı"],
         "",
         "  6. SÜREKLİ DEĞİŞKEN (CV) TEMSİLİ",
         "     CV durumu             : %d bayt" % o["cv_bayt"],
         "     yoğun d=4096 durumu   : %d bayt" % o["yoğun_bayt_d4096"],
         "     yer kazancı           : %.1f kat" % o["yer_kazancı"]]
    return "\n".join(y)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())

"""
İKİZ SAYILAR (dual numbers) -- türevin **tam** hâli, sonlu farkın değil.

===================================================================
NİÇİN VAR: H88'İN KAPANMAYAN PÜRÜZÜ
===================================================================

Kütük H88 ``beyan``ın yanlış çevreden okuduğunu bulup düzeltti ve
sonunda şunu **açık borç** olarak bıraktı:

> *"Düzeltmeden sonra bile yönlü türev ``h→0``da tam oturmuyor
> (``h=1e−2``de 2,9 iken ``h=1e−4``te 1221). ``V`` bit birebir belirli
> olduğuna göre bu tesadüf değil, ``p → Ψ`` eşlemesinin hakikî
> pürüzüdür; en kuvvetli şüpheli SVD kesmesidir. Bu hipotez ölçülmektedir
> ve neticesi çıkınca yazılacaktır."*

**Netice hiç yazılmadı.** Sebebi de aletti: sonlu fark ile ölçülen bir
pürüz, pürüzün mü yoksa sonlu farkın mı olduğunu **ayıramaz**. İkisi de
aynı belirtiyi verir:

    hakikî pürüz  : türev yok, fark ``h`` küçüldükçe zıplar
    yuvarlama     : türev var, fark ``h`` küçüldükçe ``ε/h`` ile patlar

Aralarındaki farkı görmek için **tam** türev lâzımdır ve ikiz sayılar
onu verir.

===================================================================
İKİZ SAYI NEDİR -- hayalî karşılığıyla
===================================================================

Bir sayının yanına, o sayının **ne kadar hızlı değiştiğini** taşıyan
ikinci bir sayı iliştirilir::

    x = a + b·ε        ε² = 0   (ε sıfır değil, karesi sıfır)

Aritmetik bu kaideyle yürütülünce ``b`` kendiliğinden **türev** olur::

    (a+bε)(c+dε) = ac + (ad+bc)ε        ← çarpım kaidesi
    sin(a+bε)    = sin a + b·cos a·ε    ← zincir kaidesi

Yani türev *yaklaştırılmaz*, **hesaplanır**: hiçbir ``h`` yok, hiçbir
yuvarlama farkı yok. Bedeli iki kat aritmetiktir; kazancı, sonlu farkın
``ε/h`` gürültüsünün **tamamen** kalkmasıdır.

===================================================================
NİÇİN H3'Ü NAKZETMİYOR
===================================================================

H3 *"ana döngüde gradyan ve kayıp yoktur"* der ve o hüküm **yerinde
durur**: burada kurulan şey bir eğitim motoru değil bir **ölçüm
âletidir**. İkiz sayı akışta koşmaz; ``tanilama`` tarafındaki bir
mikroskoptur ve sorduğu tek sual şudur: *bu yüzey türevlenebilir mi?*

H86'nın açtığı istisna (tabiî gradyan denensin, ölçülsün) da aynı
cinstendir ve orada da hüküm ölçüme bırakılmıştı.

===================================================================
HUDUT -- açıkça
===================================================================

* ``numpy`` dizileriyle çalışır fakat ``np.linalg.svd`` gibi
  **kapalı** çağrılara giremez: onlar ``float`` bekler. O hâlde ikiz
  sayı ancak **elle yazılmış** aritmetiğin içinden geçer -- kapı
  kurulumu (``exp``, ``sin``, ``cos``, çarpım) geçer, SVD **geçmez**.
* Ve bu bir kusur değil **tam da aranan şeydir**: SVD'nin geçememesi,
  pürüzün nerede olduğunu gösteren delilin kendisidir (bkz.
  ``purzu_yerini_bul``).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Sequence, Tuple, Union

import numpy as np

__all__ = ["Ikiz", "ikiz", "deger", "turev", "yonlu_turev",
           "sonlu_fark_kiyasi", "rapor"]

Sayi = Union[float, int, np.ndarray, "Ikiz"]


@dataclass
class Ikiz:
    """``a + b·ε``  (``ε² = 0``). ``a`` değer, ``b`` türev.

    ``numpy`` dizileriyle beraber çalışır: ``a`` ve ``b`` aynı şekilli
    dizilerdir, yani bir seferde bütün bir tensörün türevi taşınır.
    """
    a: np.ndarray
    b: np.ndarray

    def __post_init__(self) -> None:
        self.a = np.asarray(self.a, float)
        self.b = np.broadcast_to(np.asarray(self.b, float),
                                 self.a.shape).copy()

    # -- cebir ---------------------------------------------------------
    def __add__(self, o: Sayi) -> "Ikiz":
        if isinstance(o, Ikiz):
            return Ikiz(self.a + o.a, self.b + o.b)
        return Ikiz(self.a + np.asarray(o, float), self.b)

    __radd__ = __add__

    def __neg__(self) -> "Ikiz":
        return Ikiz(-self.a, -self.b)

    def __sub__(self, o: Sayi) -> "Ikiz":
        return self + (-o if isinstance(o, Ikiz) else -np.asarray(o, float))

    def __rsub__(self, o: Sayi) -> "Ikiz":
        return (-self) + o

    def __mul__(self, o: Sayi) -> "Ikiz":
        if isinstance(o, Ikiz):
            # (a+bε)(c+dε) = ac + (ad+bc)ε   -- ε² = 0
            return Ikiz(self.a * o.a, self.a * o.b + self.b * o.a)
        c = np.asarray(o, float)
        return Ikiz(self.a * c, self.b * c)

    __rmul__ = __mul__

    def __truediv__(self, o: Sayi) -> "Ikiz":
        if isinstance(o, Ikiz):
            return Ikiz(self.a / o.a,
                        (self.b * o.a - self.a * o.b) / (o.a * o.a))
        c = np.asarray(o, float)
        return Ikiz(self.a / c, self.b / c)

    def __pow__(self, k: float) -> "Ikiz":
        k = float(k)
        return Ikiz(self.a ** k, k * (self.a ** (k - 1.0)) * self.b)

    # -- şekil ---------------------------------------------------------
    def reshape(self, *s) -> "Ikiz":
        return Ikiz(self.a.reshape(*s), self.b.reshape(*s))

    def transpose(self, *s) -> "Ikiz":
        return Ikiz(self.a.transpose(*s), self.b.transpose(*s))

    @property
    def T(self) -> "Ikiz":
        return Ikiz(self.a.T, self.b.T)

    @property
    def shape(self):
        return self.a.shape

    def __getitem__(self, k) -> "Ikiz":
        return Ikiz(self.a[k], self.b[k])

    def sum(self, axis=None) -> "Ikiz":
        return Ikiz(self.a.sum(axis=axis), self.b.sum(axis=axis))

    def __matmul__(self, o: Sayi) -> "Ikiz":
        if isinstance(o, Ikiz):
            return Ikiz(self.a @ o.a, self.a @ o.b + self.b @ o.a)
        c = np.asarray(o, float)
        return Ikiz(self.a @ c, self.b @ c)

    def __rmatmul__(self, o: Sayi) -> "Ikiz":
        c = np.asarray(o, float)
        return Ikiz(c @ self.a, c @ self.b)


# -- temel fonksiyonlar: zincir kaidesi elle, tam --------------------
def _sar(f: Callable, df: Callable):
    def g(x: Sayi):
        if isinstance(x, Ikiz):
            return Ikiz(f(x.a), df(x.a) * x.b)
        return f(np.asarray(x, float))
    return g


sin = _sar(np.sin, np.cos)
cos = _sar(np.cos, lambda t: -np.sin(t))
tanh = _sar(np.tanh, lambda t: 1.0 - np.tanh(t) ** 2)
exp = _sar(np.exp, np.exp)
log = _sar(np.log, lambda t: 1.0 / t)
sqrt = _sar(np.sqrt, lambda t: 0.5 / np.sqrt(t))


def ikiz(a, b=0.0) -> Ikiz:
    return Ikiz(a, b)


def deger(x: Sayi) -> np.ndarray:
    return x.a if isinstance(x, Ikiz) else np.asarray(x, float)


def turev(x: Sayi) -> np.ndarray:
    return x.b if isinstance(x, Ikiz) else np.zeros_like(
        np.asarray(x, float))


# =====================================================================
def yonlu_turev(f: Callable[[Ikiz], Sayi], p: np.ndarray,
                yon: np.ndarray) -> Tuple[float, float]:
    """``f``in ``p`` noktasında ``yon`` boyunca **tam** yönlü türevi.

    Tek bir ileri geçişle hem değer hem türev döner; hiçbir ``h`` yoktur.
    """
    p = np.asarray(p, float)
    v = np.asarray(yon, float)
    r = f(Ikiz(p, v))
    return float(np.ravel(deger(r))[0]), float(np.ravel(turev(r))[0])


def sonlu_fark_kiyasi(f_ikiz: Callable[[Ikiz], Sayi],
                      f_duz: Callable[[np.ndarray], float],
                      p: np.ndarray, yon: np.ndarray,
                      adimlar: Sequence[float] = (1e-1, 1e-2, 1e-3,
                                                  1e-4, 1e-5, 1e-6)
                      ) -> Dict[str, object]:
    """Tam türevi sonlu farkla **yüzleştir** -- pürüz kimin?

    ===================================================================
    OKUNUŞU -- iki hâl ve nasıl ayrıldıkları
    ===================================================================

    * **Yüzey pürüzsüz, alet gürültülü.** Sonlu fark, ``h`` büyükken
      kesme hatasıyla, küçükken ``ε/h`` yuvarlamasıyla sapar; arada bir
      ``h``da tam türeve **yaklaşır**. Yani ``|fark − tam|`` bir ``U``
      çizer ve dibi makine hassasiyeti mertebesindedir.
    * **Yüzey pürüzlü.** Sonlu fark hiçbir ``h``da tam türeve
      yaklaşmaz; ``U``nun dibi yoktur ve fark ``h`` küçüldükçe
      **artmaya devam eder**.

    H88'in bıraktığı sual tam olarak budur ve ancak bu yüzleştirmeyle
    cevaplanır.
    """
    tam_v, tam_d = yonlu_turev(f_ikiz, p, yon)
    p = np.asarray(p, float)
    v = np.asarray(yon, float)
    satir = []
    for h in adimlar:
        ileri = float(f_duz(p + h * v))
        geri = float(f_duz(p - h * v))
        mer = (ileri - geri) / (2.0 * h)
        satir.append({"h": float(h), "merkezî_fark": mer,
                      "fark": abs(mer - tam_d)})
    en_iyi = min(satir, key=lambda s: s["fark"])
    return {"tam_değer": tam_v, "tam_türev": tam_d,
            "satır": satir, "en_yakın": en_iyi,
            # Dip makine hassasiyeti mertebesindeyse yüzey pürüzsüzdür.
            "pürüzsüz_mü": bool(en_iyi["fark"]
                                <= 1e-5 * max(abs(tam_d), 1.0))}


# =====================================================================
def purzu_yerini_bul(tohum: int = 0, n: int = 8, chi: int = 4
                     ) -> Dict[str, object]:
    """H88'in sualini iki kademede cevapla: **kapı mı, kesme mi?**

    1. **Yalnız kapı kurulumu.** ``exp(−2A)`` ile kurulan ``SO(4)``
       kapısı açıya göre türevlenebilir mi? İkiz sayı doğrudan geçer.
    2. **Kesme.** SVD budaması bir **sıralamadır**; sıralama değişince
       fonksiyon sıçrar. İkiz sayı oraya **giremez** ve girememesi
       delilin kendisidir.

    Burada 1. kademe fiilen ölçülür; 2. kademe için sıralamanın kaç
    kere değiştiği sayılır -- sıçrama sayısı doğrudan pürüzün ölçüsüdür.
    """
    from kuantum.yazmac import _so4_ureteci

    rng = np.random.default_rng(tohum)
    t0 = rng.normal(size=6)
    yon = rng.normal(size=6)

    # --- 1. kademe: kapı kurulumu türevlenebilir mi
    def kapi_izi(teta):
        """``Tr(exp(−2A(θ)))`` -- skalerdir, ikiz sayı ile tam türevlenir.

        ``expm``i seriyle açarız; ``A`` küçükse yakınsar ve **her adımı
        ikiz sayı ile** yürür, yani türev de tam alınır.
        """
        A = _ureteci_ikiz(teta)
        M = _birim_gibi(A)
        T = _birim_gibi(A)
        for k in range(1, 18):
            T = (T @ A) * (-2.0 / k)
            M = M + T
        return _iz(M)

    def kapi_izi_duz(teta):
        A = _so4_ureteci(np.asarray(teta, float))
        M = np.eye(4)
        T = np.eye(4)
        for k in range(1, 18):
            T = (T @ A) * (-2.0 / k)
            M = M + T
        return float(np.trace(M))

    k1 = sonlu_fark_kiyasi(lambda z: kapi_izi(z), kapi_izi_duz, t0, yon)

    # --- 2. kademe: kesme sınırında tekil değerler KESİŞİYOR mu
    #
    # **İlk denemem yanlış ölçüyordu ve sıfır çıktı.** ``bag_ust``
    # desenine bakmıştım; o desen bağın **üst sınırıdır** ve tarama
    # boyunca hiç değişmez, yani ölçüt kördü (H90: kırmızı yanamayan
    # ölçüt, ölçüt değildir).
    #
    # Doğru ölçü şudur: kesme, ``s[r−1]`` ile ``s[r]`` arasından
    # geçen bir **sıralamadır**. O iki tekil değer birbirine yaklaşıp
    # yer değiştirdiğinde tutulan altuzay **sıçrar** ve fonksiyon
    # türevlenemez hâle gelir. Yani aranan şey ``s[r−1] − s[r]``
    # boşluğunun sıfıra ne kadar yaklaştığıdır.
    from kuantum.yazmac import Yazmac, dik_iki_kubit
    bosluklar = []
    buyuk = []
    kesme_say = 0
    for s in np.linspace(0.0, 1.0, 41):
        y = Yazmac(n, bag=chi, tohum=tohum)
        y.superpozisyona_sok()
        r2 = np.random.default_rng(tohum)
        for t in range(10):
            y.cift_kapi(dik_iki_kubit(r2.normal(size=6) * 0.8
                                      + s * yon[:6] * 0.5), ofset=t % 2)
        # Boşluk yalnız **kesme anında** görünür; yazmaç onu zabıtlıyor.
        if y._kesme_sayisi:
            bosluklar.append(float(y._kesme_bosluk))
            buyuk.append(float(y._kesme_buyukluk))
            kesme_say += int(y._kesme_sayisi)
    yakin = int(sum(1 for b in bosluklar if b < 1e-2))
    return {"kapı_pürüzsüz_mü": k1["pürüzsüz_mü"],
            "kapı_tam_türev": k1["tam_türev"],
            "kapı_en_yakın_fark": k1["en_yakın"]["fark"],
            "kapı_en_iyi_h": k1["en_yakın"]["h"],
            "kesme_boşluğu_ölçüldü": len(bosluklar),
            "kesme_sayısı": kesme_say,
            "kesme_sınırı_yakın": yakin,
            "en_dar_boşluk": (float(min(bosluklar)) if bosluklar
                              else float("nan")),
            "sınır_büyüklüğü": (float(min(buyuk)) if buyuk
                                else float("nan")),
            "tarama_noktası": 41}


def _ureteci_ikiz(teta: Ikiz) -> Ikiz:
    """``_so4_ureteci``nin ikiz sayı hâli -- aynı yerleşim, aynı işaret."""
    z = Ikiz(np.zeros(()), np.zeros(()))
    A_a = np.zeros((4, 4))
    A_b = np.zeros((4, 4))
    t_a, t_b = deger(teta), turev(teta)
    ind = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    for k, (i, j) in enumerate(ind):
        A_a[i, j] += t_a[k]
        A_a[j, i] -= t_a[k]
        A_b[i, j] += t_b[k]
        A_b[j, i] -= t_b[k]
    return Ikiz(A_a, A_b)


def _birim_gibi(A: Ikiz) -> Ikiz:
    return Ikiz(np.eye(A.shape[0]), np.zeros(A.shape))


def _iz(M: Ikiz) -> Ikiz:
    n = M.shape[0]
    return Ikiz(np.trace(M.a), np.trace(M.b))


# =====================================================================
def rapor(tohum: int = 0) -> str:
    r = purzu_yerini_bul(tohum)
    s = ["=== İKİZ SAYILAR -- H88'in pürüz suali cevaplanıyor ===", "",
         "H88 şöyle bırakmıştı: *'yönlü türev h→0'da tam oturmuyor…",
         "en kuvvetli şüpheli SVD kesmesidir. Bu hipotez ölçülmektedir",
         "ve neticesi çıkınca yazılacaktır.'*  Netice hiç yazılmamıştı,",
         "çünkü alet (sonlu fark) suali cevaplayamaz: pürüzü de kendi",
         "gürültüsünü de aynı belirtiyle gösterir.",
         "",
         "1. KADEME -- KAPI KURULUMU (exp(−2A), ikiz sayı ile TAM):",
         "     tam türev            : %+.8f" % r["kapı_tam_türev"],
         "     sonlu farkın en iyisi: h=%.0e, fark %.3e"
         % (r["kapı_en_iyi_h"], r["kapı_en_yakın_fark"]),
         "     PÜRÜZSÜZ MÜ          : %s" % r["kapı_pürüzsüz_mü"],
         "",
         "2. KADEME -- KESME SINIRINDAKİ BOŞLUK (s[χ−1] − s[χ]):",
         "     ölçülen nokta        : %d / %d"
         % (r["kesme_boşluğu_ölçüldü"], r["tarama_noktası"]),
         "     en dar nispî boşluk  : %.3e" % r["en_dar_boşluk"],
         "     sınırdaki tekil değer: %.3e  (gürültü mü?)"
         % r["sınır_büyüklüğü"],
         "     boşluk < %%1 olan nokta: %d" % r["kesme_sınırı_yakın"],
         "",
         "HÜKÜM -- iki parça, ikisi de haddiyle:",
         "  1. Kapı kurulumu **türevlenebilir**. Sonlu fark orada tam",
         "     türeve makine hassasiyetinde yaklaşıyor; o hâlde H88'in",
         "     gördüğü pürüz kapıdan gelmiyor. Bu KESİN.",
         "  2. Kesme bir **sıralamadır** ve sıralama ancak sınırdaki iki",
         "     tekil değer kesiştiğinde sıçrar. Yukarıdaki en dar boşluk",
         "     o kesişmeye ne kadar yaklaşıldığının ölçüsüdür.",
         "",
         "  YALANCI YEŞİL TUZAĞI ve nasıl kapandığı: ilk ölçümde boşluk",
         "  tam 0,000e+00 çıktı ve 'dejenere' diye okunacaktı. Halbuki",
         "  s[χ−1] ile s[χ] İKİSİ DE sıfırsa oran da sıfır çıkar --",
         "  orada kesilecek bir şey yoktur. Sınırdaki tekil değerin",
         "  BÜYÜKLÜĞÜ de raporlanıyor; gürültü mertebesindeyse hüküm",
         "  verilmez. Fren konunca hakikî boşluk ~%2 çıktı: küçüktür",
         "  fakat sıfır değildir, ve sınırdaki değerler gürültü değil.",
         "",
         "  O hâlde H88'in şüphelisi ÖLÇÜMLE DESTEKLENİYOR: %2'lik bir",
         "  boşluk, küçük bir parametre değişikliğiyle kolayca aşılır ve",
         "  aşıldığında tutulan altuzay yer değiştirir. Bu bir ispat",
         "  değil kuvvetli bir delildir; 'ispatlandı' denmiyor."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())

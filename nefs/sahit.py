"""
Şahit uzvu: bir bulmacanın gösterim çiftlerini **organla sezmek**.

Kütükteki H6'nın gövdesi burasıdır. Mesele şudur: bir ARC bulmacasının
bütün örnekleri aynı kurala tâbidir. Modele bunu bir **bayrakla**
bildirmek kolaydır ve yanlıştır -- bayrak, modelin sezmediği bir şeyi
dışarıdan dayatır; o bilgi organın kendisinde yaşamaz, sözleşmede yaşar.
Burada yapılan başkadır:

  1. **Bölütleme** (`bolutle`): ham duyu akışındaki kopma noktaları
     ölçülür. Ayıraç sembolü aranmaz; ardışık satırlar arasındaki
     mesafenin medyan+MAD eşiğini aştığı yerler bölüt sınırıdır. Yani
     "burada yeni bir örnek başlıyor" hükmü **duyudan** çıkar.
  2. **Şahit başına kaide** (`kaide_uydur`): her bölüt kendi içinde
     girdi/çıktı diye ikiye ayrılır (en büyük iç kopma) ve aradaki
     dönüşüm **dik Procrustes** ile kapalı formda çözülür. Gradyan yok,
     adım yok: ``R = UVᵀ``, ``UΣVᵀ = SVD(ÇᵀG)``.
  3. **Küllî kaide** (`kulli_kaide`): şahitlerin kaideleri kutupsal
     ortalama ile birleştirilir -- ``R̄ = polar(Σ Rₖ)``. Dik dizeylerin
     Öklit ortalaması dik değildir; kutupsal izdüşüm onu Stiefel'e geri
     indirir.
  4. **Nakz** (`nakz_bul`): dışarıda-bırak (leave-one-out) sınaması.
     ``j``'siz kurulan küllî kaide ``j``'de tutmuyorsa ``j`` bir karşı
     örnektir ve **tek karşı örnek küllî hükmü düşürür**. Bu, mîzânın
     ``nakz`` itirazının sayısal karşılığıdır.

**Dürüstlük şartı.** Bölütleme sezgisel bir kopma ölçüsüdür; doğru
bölütlemeyi garanti etmez. Şahit sayısı ikiden azsa tevafuk **tanımsızdır**
(sıfır değil) ve bu hâl `Bolutleme.yeterli` ile açıkça taşınır. Eşik de
raporlanır; gizli sabit yoktur.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Sahit", "Bolutleme", "bolutle", "kaide_uydur", "kulli_kaide",
           "artiklar", "nakz_bul", "delil_dizileri"]


# =====================================================================
#  1. Bölütleme
# =====================================================================
@dataclass(frozen=True)
class Sahit:
    """Bir gösterim çifti: ``[bas, son)`` satırları, içinde girdi/çıktı.

    ``kesim`` bölütün içindeki girdi→çıktı sınırıdır (mutlak satır
    indisi). ``bas < kesim < son`` daima sağlanır.
    """
    no: int
    bas: int
    kesim: int
    son: int

    @property
    def girdi(self) -> slice:
        return slice(self.bas, self.kesim)

    @property
    def cikti(self) -> slice:
        return slice(self.kesim, self.son)

    @property
    def dilim(self) -> slice:
        return slice(self.bas, self.son)

    def __len__(self) -> int:
        return self.son - self.bas


@dataclass
class Bolutleme:
    """Bölütlemenin kendisi ve onu **denetlenebilir** kılan ölçüler."""
    sahitler: List[Sahit] = field(default_factory=list)
    esik: float = 0.0
    kopmalar: Optional[np.ndarray] = None
    yeterli: bool = False          # tevafuk için en az iki şahit var mı?
    sebep: str = ""

    def __len__(self) -> int:
        return len(self.sahitler)


def _kopma_olcusu(Z: np.ndarray) -> np.ndarray:
    """Ardışık satırlar arasındaki normalize mesafe; uzunluk ``n-1``."""
    if len(Z) < 2:
        return np.zeros(0)
    fark = np.linalg.norm(np.diff(Z, axis=0), axis=1)
    olcek = float(np.median(fark)) if fark.size else 0.0
    return fark / (olcek + 1e-12)


def _mad_esigi(x: np.ndarray, kat: float = 3.0) -> float:
    """Medyan + kat·MAD. Ortalama+std yerine bu seçildi: sınırların
    kendisi uç değerdir, ortalamayı kendileri şişirir."""
    if x.size == 0:
        return float("inf")
    med = float(np.median(x))
    mad = float(np.median(np.abs(x - med)))
    return med + kat * (mad if mad > 1e-12 else float(np.std(x)) + 1e-12)


def bolutle(Z: np.ndarray, asgari_uzunluk: int = 4,
            kat: float = 3.0) -> Bolutleme:
    """Duyu akışını şahitlere böl -- ayıraç sembolü **aramadan**.

    ``asgari_uzunluk``: bir şahit hem girdi hem çıktı barındıracağı için
    en az 4 satır olmalıdır (2+2). Daha kısa bölütler komşusuna katılır.
    """
    n = len(Z)
    if n < 2 * asgari_uzunluk:
        return Bolutleme(sahitler=[], esik=float("nan"),
                         kopmalar=_kopma_olcusu(Z), yeterli=False,
                         sebep="akış iki şahide bölünemeyecek kadar kısa")

    kopma = _kopma_olcusu(Z)
    esik = _mad_esigi(kopma, kat)
    aday = [i + 1 for i, v in enumerate(kopma) if v > esik]

    # İKİ MERTEBELİ AYIRAÇ. Bir bulmaca akışında iki tür kopma vardır:
    # örnekleri ayıran (büyük) ve bir örneğin girdisiyle çıktısını ayıran
    # (küçük). İkisi de eşiği aşar. Hepsini şahit sınırı saymak akışı
    # ikiye katlayarak böler -- ölçüldü: 5 şahitlik akış 10 parçaya
    # bölünüyordu. Bu yüzden adaylar kendi aralarında medyanla ikiye
    # ayrılır: üst yarı şahit sınırı, alt yarı iç kesimdir.
    if len(aday) >= 3:
        buyukluk = np.array([kopma[a - 1] for a in aday])
        ic_esik = float(np.median(buyukluk))
        aday = [a for a, v in zip(aday, buyukluk) if v > ic_esik]

    # asgarî uzunluk şartıyla sınırları ayıkla
    sinirlar: List[int] = [0]
    for a in aday:
        if a - sinirlar[-1] >= asgari_uzunluk and n - a >= asgari_uzunluk:
            sinirlar.append(a)
    sinirlar.append(n)

    if len(sinirlar) <= 2:
        return Bolutleme(sahitler=[], esik=esik, kopmalar=kopma,
                         yeterli=False,
                         sebep="kopma eşiği aşan sınır yok; akış tek parça")

    sahitler: List[Sahit] = []
    for no, (b, s) in enumerate(zip(sinirlar[:-1], sinirlar[1:])):
        kesim = _ic_kesim(kopma, b, s)
        sahitler.append(Sahit(no=no, bas=b, kesim=kesim, son=s))
    return Bolutleme(sahitler=sahitler, esik=esik, kopmalar=kopma,
                     yeterli=len(sahitler) >= 2,
                     sebep="" if len(sahitler) >= 2 else "tek şahit")


def _ic_kesim(kopma: np.ndarray, bas: int, son: int) -> int:
    """Bölütün içindeki en büyük kopma = girdi/çıktı sınırı.

    Uçlara yapışmasın diye en az birer satır bırakılır; aksi hâlde
    girdi ya da çıktı boş kalır ve Procrustes tanımsızlaşır.
    """
    ic = range(bas + 1, son)
    aday = [(kopma[i - 1], i) for i in ic if 0 <= i - 1 < len(kopma)]
    if not aday:
        return bas + max(1, (son - bas) // 2)
    return max(aday)[1]


# =====================================================================
#  2. Şahit başına kaide -- kapalı form, gradyansız
# =====================================================================
def _cerceve(S: np.ndarray, sahit: Sahit
             ) -> Tuple[np.ndarray, np.ndarray]:
    """Şahidi **kendi çerçevesine** taşı: merkezle ve ölçekle.

    Bu, kaidenin ne olduğuna dair bir hükümdür. Kaide, ızgaranın nerede
    durduğu ya da ne kadar büyük olduğu değildir -- **şekil**tir. Yer ve
    ölçek şahide hastır (her örnek başka yerde, başka boyuttadır); kural
    hepsinde ortaktır. Bu yüzden Procrustes merkezlenmiş ve ölçeklenmiş
    çerçevede kurulur.

    Merkezlemesiz kurulup ölçüldü ve **kaldı**: aynı kurala tâbi beş
    şahitte dahi dışarıda-bırak artığı 0.27–1.00 arasına çıkıyor, nakz
    5/5 şahidi düşürüyordu. Sebep, akıştaki yer kaymasının (offset)
    dik dönmeyle taşınamamasıydı.
    """
    G = np.asarray(S[sahit.girdi], float)
    C = np.asarray(S[sahit.cikti], float)
    t = min(len(G), len(C))
    if t == 0:
        return np.zeros((0, S.shape[1])), np.zeros((0, S.shape[1]))
    G, C = G[:t], C[:t]
    G = G - G.mean(0, keepdims=True)
    C = C - C.mean(0, keepdims=True)
    ng = float(np.linalg.norm(G))
    nc = float(np.linalg.norm(C))
    G = G / (ng if ng > 1e-12 else 1.0)
    C = C / (nc if nc > 1e-12 else 1.0)
    return G, C


def capraz_kovaryans(S: np.ndarray, sahit: Sahit) -> np.ndarray:
    """``Aₖ = Çₖᵀ Gₖ`` -- şahidin kaide hakkındaki **ham şehadeti**.

    Bu, kaidenin kendisi değil ona dair delildir. Delillerin toplanabilir
    olması burada mühimdir: ``argmin_R Σₖ ‖R Gₖ − Çₖ‖²`` çözümü
    ``polar(Σₖ Aₖ)``dir. Yani şahitler **verilerini** birleştirir,
    hükümlerini ortalamaz.
    """
    G, C = _cerceve(S, sahit)
    if len(G) == 0:
        return np.zeros((S.shape[1], S.shape[1]))
    return C.T @ G


def _polar(A: np.ndarray) -> np.ndarray:
    """``polar(A) = UVᵀ`` -- Frobenius mânâsında en yakın dik dizey."""
    U, _, Vt = np.linalg.svd(A)
    return U @ Vt


def kaide_uydur(S: np.ndarray, sahit: Sahit) -> np.ndarray:
    """``R = argmin_{RᵀR=I} ‖R G − Ç‖_F`` -- dik Procrustes, kapalı form.

    ``G``/``Ç``, ``_cerceve`` ile merkezlenip ölçeklenmiş girdi/çıktı
    satırlarıdır. Satır sayıları eşit değilse kısası kadarı alınır; bu
    bir yaklaşımdır ve ``artiklar`` ile ölçülür, gizlenmez.

    Çözüm kapalı formdur: ``UΣVᵀ = SVD(ÇᵀG)`` ⟹ ``R = UVᵀ``. Ne adım
    boyu vardır, ne yakınsama şartı, ne de gradyan.
    """
    G, _ = _cerceve(S, sahit)
    if len(G) == 0:
        return np.eye(S.shape[1])
    return _polar(capraz_kovaryans(S, sahit))


def kulli_kaide(caprazlar: Sequence[np.ndarray]) -> np.ndarray:
    """``R̄ = polar(Σₖ Aₖ)`` -- şahitlerin **müşterek** kaidesi.

    Girdi, şahit başına kaide değil şahit başına **çapraz kovaryanstır**
    (`capraz_kovaryans`). Bunun sebebi ölçümle çıktı ve mühimdir:

    Tek bir şahitte eşleşen satır sayısı ``t``, mana boyutundan (``d_sem``)
    küçükse ``Aₖ``ın rütbesi eksiktir ve ``polar(Aₖ)``ın boş uzaydaki
    kısmı **keyfîdir**. Kaideleri (yani ``polar(Aₖ)``ları) ortalamak, o
    keyfî kısımları da ortalar; ölçüldü: aynı kurala tâbi beş şahitte
    dışarıda-bırak artığı 0.42–1.04 çıkıyor, nakz 5/5 düşürüyordu.
    Çapraz kovaryanslar toplanınca rütbe birikir ve kaide belirlenir --
    ki şahitliğin mânâsı zaten budur: bir şahit tek başına yetmez,
    beraberce yeter.
    """
    if not caprazlar:
        raise ValueError("şehadet yok")
    return _polar(np.sum(np.stack([np.asarray(a, float) for a in caprazlar]),
                         axis=0))


# =====================================================================
#  3. Artık, delil, nakz
# =====================================================================
def artiklar(S: np.ndarray, sahit: Sahit, R: np.ndarray) -> np.ndarray:
    """``‖R gₚ − çₚ‖ / (‖çₚ‖+ε)`` -- şahidin kendi çerçevesinde."""
    G, C = _cerceve(S, sahit)
    if len(G) == 0:
        return np.zeros(0)
    pay = np.linalg.norm(G @ R.T - C, axis=1)
    payda = np.linalg.norm(C, axis=1) + 1e-12
    return pay / payda


def _bos_kaide(ds: int, tohum: int) -> np.ndarray:
    """Hiçbir alâkası olmayan bir dik dizey -- **boş hipotez** ölçeği."""
    rng = np.random.default_rng(tohum)
    Q, _ = np.linalg.qr(rng.normal(size=(ds, ds)))
    return Q


def _tolerans(S: np.ndarray, sahitler: Sequence[Sahit],
              kaideler: Sequence[np.ndarray]) -> float:
    """Tolerans **iki uçtan** kalibre edilir; dışarıdan sabit konmaz.

    Tek uçtan kalibrasyon kurulup ölçüldü ve **kaldı**: yalnız kendi
    artıklarının medyan+MAD eşiği alınınca tolerans 0.045 çıktı, çünkü
    bir kaide kendi şahidinde tanımı gereği neredeyse hatasızdır. O
    eşikle bütün şahitler nakzedilmiş görünüyordu (5/5) -- ölçü, "tutar"
    ile "tutmaz"ı ayırmıyordu.

    Doğrusu iki ölçeği karşılaştırmaktır:

    * ``kendi``  : kaidenin kendi şahidindeki artığı -- **en iyi** hâl,
    * ``boş``    : alâkasız (rastgele dik) bir kaidenin artığı -- **tesadüf** hâli,

    ve eşik ikisinin geometrik ortasıdır. Böylece soru şu olur: dışarıda
    bırakılan şahit, küllî kaideyle *tam uyuma* mı yoksa *tesadüfe* mi
    daha yakın?
    """
    if not sahitler:
        return float("inf")
    R_hep = kulli_kaide([capraz_kovaryans(S, s) for s in sahitler])
    R_bos = _bos_kaide(S.shape[1], tohum=len(sahitler) * 1000 + S.shape[1])
    kendi = [float(np.mean(a)) for a in
             (artiklar(S, s, R_hep) for s in sahitler) if a.size]
    bos = [float(np.mean(a)) for a in
           (artiklar(S, s, R_bos) for s in sahitler) if a.size]
    if not kendi or not bos:
        return float("inf")
    b = max(float(np.median(bos)), 1e-9)
    # medyan alınır, ortalama değil: bozuk şahit azınlıksa ölçeği
    # bozmasın diye. Taban ``b·1e-4``: kusursuz uyumda (artık ≈ 0)
    # geometrik orta sıfıra çöker ve eşik anlamsızlaşırdı.
    k = max(float(np.median(kendi)), b * 1e-4)
    return float(np.sqrt(k * b))


def delil_dizileri(S: np.ndarray, sahitler: Sequence[Sahit],
                   kaideler: Sequence[np.ndarray],
                   tol: Optional[float] = None
                   ) -> Tuple[List[np.ndarray], float]:
    """Şahit başına ikili delil dizisi -- ``fitrat.tevafuk`` için.

    ``dₖ[i] = 𝕀( şahit k ile şahit i BERABER kurdukları kaide, i'yi
    açıklıyor mu )``, yani ``polar(Aₖ + Aᵢ)``ın ``i``deki artığı.

    Tek şahidin kendi kaidesi kullanılmadı ve sebebi ölçüldü: ``t <
    d_sem`` iken ``polar(Aₖ)``ın boş uzayı keyfîdir, dolayısıyla
    ``dₖ`` neredeyse köşegen çıkıyor (herkes yalnız kendini teyit
    ediyor) ve tevafuk sûnî olarak sıfıra iniyordu. İkişerli birleşim,
    şahitliğin tabiatına da uygundur: iki şahit bir şahitten fazlasını
    tayin eder.

    Bu diziler `fitrat.tevafuk.tevafuk_olcusu` ve `fazla_sayma`ya
    doğrudan verilir; "kaç müteber şahit var" hükmü oradan gelir.
    """
    if tol is None:
        tol = _tolerans(S, sahitler, kaideler)
    caprazlar = [capraz_kovaryans(S, s) for s in sahitler]
    deliller: List[np.ndarray] = []
    for k in range(len(sahitler)):
        satir = []
        for i in range(len(sahitler)):
            R = _polar(caprazlar[k] + caprazlar[i])
            a = artiklar(S, sahitler[i], R)
            satir.append(float(np.mean(a) <= tol) if a.size else 0.0)
        deliller.append(np.array(satir))
    return deliller, float(tol)


def nakz_bul(S: np.ndarray, sahitler: Sequence[Sahit],
             kaideler: Sequence[np.ndarray],
             tol: Optional[float] = None) -> Dict[str, object]:
    """Dışarıda-bırak sınaması: küllî kaideyi **düşüren** şahitler.

    ``j``'siz kurulan ``R̄₋ⱼ`` şahit ``j``'de tolerans dışında kalıyorsa
    ``j`` bir karşı örnektir. Mîzânda tek karşı örnek küllî önermeyi
    düşürür (`mizan.munazara.nakz_gecerli_mi` ile aynı hüküm); burada da
    öyle davranılır: ``nakz`` boş değilse "hepsi aynı kurala tâbi"
    iddiası **yakîn** olamaz.

    **Nakz kademelidir.** Tek turda kurulup ölçüldü ve **kaldı**: dört
    şahitten yalnız biri başka kurala tâbiyken dördü birden nakzedilmiş
    çıkıyordu. Sebep açıktır -- dışarıda bırakılan şahit ``j`` sağlam
    olsa bile, geri kalanların içinde bozuk olan durduğu için küllî
    kaide zaten bozuktur ve ``j``de tutmaz. Yani bir karşı örnek bütün
    şahitleri suçlu gösteriyordu.

    Doğrusu, mîzânda da olduğu gibi, **önce en ağır karşı örneği
    ayırmak**tır: artığı en büyük şahit nakzedilmiş sayılır, kaide
    onsuz yeniden kurulur ve kalanlar tekrar yoklanır. Hiçbiri toleransı
    aşmayana kadar sürer; en az iki şahit kalır (tek şahitle küllî
    kaideden söz edilemez).
    """
    m = len(sahitler)
    if m < 2:
        return {"nakz": [], "artık": [], "tolerans": float("nan"),
                "kalan": list(range(m)), "sebep": "en az iki şahit lazım"}
    if tol is None:
        tol = _tolerans(S, sahitler, kaideler)
    caprazlar = [capraz_kovaryans(S, s) for s in sahitler]
    kalan = list(range(m))
    nakz: List[int] = []
    artik = [float("nan")] * m
    while len(kalan) >= 2:
        tur: List[Tuple[float, int]] = []
        for j in kalan:
            digerleri = [caprazlar[k] for k in kalan if k != j]
            R_eksik = kulli_kaide(digerleri) if digerleri else caprazlar[j]
            a = artiklar(S, sahitler[j], R_eksik)
            ort = float(np.mean(a)) if a.size else float("inf")
            tur.append((ort, j))
            artik[j] = ort
        en_kotu, j = max(tur)
        if en_kotu <= tol:
            break
        nakz.append(j)
        kalan.remove(j)
    R_kulli = kulli_kaide([caprazlar[k] for k in kalan] or caprazlar)
    return {"nakz": sorted(nakz), "artık": artik, "tolerans": float(tol),
            "kaide": R_kulli, "kalan": kalan, "sebep": ""}


# =====================================================================
def _akis_kur(m: int, ds: int, t: int, bozuk: Optional[int] = None,
              tohum: int = 0) -> np.ndarray:
    """``m`` şahitlik yapay akış. ``bozuk`` verilirse o şahit BAŞKA bir
    kurala tâbidir -- nakzın yakalaması gereken şey odur."""
    rng = np.random.default_rng(tohum)
    R_hakiki = np.linalg.qr(rng.normal(size=(ds, ds)))[0]
    R_sapik = np.linalg.qr(rng.normal(size=(ds, ds)))[0]
    bloklar = []
    for k in range(m):
        G = rng.normal(size=(t, ds))
        R = R_sapik if k == bozuk else R_hakiki
        C = G @ R.T
        # iç kopma (girdi→çıktı) KÜÇÜK, dış kopma (örnek→örnek) BÜYÜK
        bloklar.append(np.vstack([G, C + 6.0]) + 60.0 * k)
    return np.vstack(bloklar)


def _bir_deneme(baslik: str, S: np.ndarray) -> List[str]:
    b = bolutle(S)
    s = ["%s" % baslik,
         "  bulunan şahit: %d   eşik=%.3f   yeterli=%s"
         % (len(b), b.esik, b.yeterli)]
    for x in b.sahitler:
        s.append("    şahit %d: [%2d,%2d) kesim=%2d" % (x.no, x.bas, x.son, x.kesim))
    if b.yeterli:
        K = [kaide_uydur(S, x) for x in b.sahitler]
        n = nakz_bul(S, b.sahitler, K)
        s.append("  tolerans=%.4f   nakz=%s" % (n["tolerans"], n["nakz"]))
        s.append("  dışarıda-bırak artıkları: %s"
                 % ["%.4f" % v for v in n["artık"]])
        d, tol = delil_dizileri(S, b.sahitler, K)
        s.append("  delil dizileri (kaide k → şahit i'de tutar mı):")
        for k, dk in enumerate(d):
            s.append("    k=%d  %s" % (k, "".join("%d" % int(v) for v in dk)))
    return s


def _gosterim() -> str:
    s = ["=== şahit bölütlemesi (ayıraç SEMBOLÜ aranmadan) ==="]
    s += _bir_deneme("\n--- hepsi aynı kurala tâbi ---",
                     _akis_kur(m=5, ds=8, t=6))
    s += _bir_deneme("\n--- 2 numaralı şahit BAŞKA kurala tâbi ---",
                     _akis_kur(m=5, ds=8, t=6, bozuk=2))
    s.append("\nHüküm: ikinci akışta nakz boş DEĞİLDİR; tek karşı örnek")
    s.append("küllî kaideyi düşürür ve makam yakîn olamaz.")
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(_gosterim())

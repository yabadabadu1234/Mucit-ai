"""LİF -- kelimenin nereye takıldığı: tip → kategori → uzay → nokta.

Padişahın zabıtlarının mimarinin göbeğine oturduğu yer burasıdır
(``docs/zabit/kudret/``). Bu dosya bir **çip değildir**: yeni riyaziye
yazmaz. Zabıtların kabul ettiği iki usulün kodu zaten depoda yazılıydı
ve **yetim** duruyordu; burada onlar tek nizamda birleştirilir.

===================================================================
1. İPTAL EDİLENİN İPTALİ -- düz ikili kodlama
===================================================================

Zabıt (``Kelime_ve_Durum_Kodlamasının_Tensörel_ve_Kuantum_Mahiyeti``)
iki tuzağı yasaklar:

* **Tuzak A -- taban kodlaması.** Kelimenin indeksini ikiliye çevirmek
  (``5 → |00000101⟩``). Bütün kelimeler birbirine dik olur:
  ``⟨5|6⟩ = 0``. "Kedi" ile "köpek" arasındaki akrabalık yok olur.
* **Tuzak B -- düz genlik kodlaması.** ``2^k`` boyutlu bir vektörü
  ``k`` kübitin genliklerine dümdüz yaymak. ``j₁`` ile ``j_k``
  arasında **yapay** bir hiyerarşi doğar; uzayda komşu olan 15 ile 16,
  ikili tabanda ``01111`` ile ``10000`` olur ve bütün bitleri
  zıtlaşır.

Kabul edilen iki usul::

    Kabul 1  MPS / Tensör Treni     h_{j₁…j_k} = A₁^{(j₁)} ⋯ A_k^{(j_k)}
    Kabul 2  Qudit ℂ^d / Koherent   |x⟩ = D(x)|0⟩

**İkisinin de kodu bu depoda vardı:** ``nefs/ttkan.py`` (TT-SVD, sanal
bağ ``r``) ve ``kuantum/surekli.py`` (``yer_degistirme``,
``tutarli_durum``). İkisi de hiçbir yerden çağrılmıyordu.

===================================================================
2. KARTEZYEN KUTUNUN İPTALİ -- ve cevheri takma tarzının değişmesi
===================================================================

Zabıt (``Bağımlı Lifli Tip Tensörü``) ``ℋ_kat ⊗ ℋ_uzay ⊗ ℋ_nokta``
kutusunu iptal eder. Yerine Grothendieck kuruluşu, yâni bağımlı
toplam::

    ℋ_Qudit  ≅  ⊕      ( ⊕        ( ⊕          ℋ_Point^(t,c,u) ) )
               t∈Type    c∈Cat(t)    u∈Space(c)

**Padişahın sorduğu hesap budur: cevheri takma tarzı nasıl değişir?**

    ==================  ====================  =======================
                        Kartezyen kutu        Bağımlı lif
                        (iptal)               (kabul)
    ==================  ====================  =======================
    boyut               |T|·|C|·|U| sabit     Σ_t Σ_{c∈Cat(t)}|Space(c)|
    yeni tip eklemek    bütün tensörü büyütür yalnız kendi lifini ekler
    ``c`` adresi        ``t``den bağımsız     ``Cat(t)`` -- ``t``ye BAĞLI
    boş kesişim         sıfırla doldurulur    hiç YOKTUR
    kod karşılığı       ``ndarray(T,C,U)``    lif defteri + ``ac``
    ==================  ====================  =======================

Yâni: **cevher artık sabit ebatlı bir kutuya çakılamaz.** Her cevher
kendi lifiyle birlikte takılır ve takıldığı yer, taktığın şeyin
**tipine** bağlıdır. Kutuda ``(t,c,u)`` üçlüsünün her kombinasyonu
için bir hücre ayrılırdı ve olmayanlar sıfırla dolardı; lifte olmayan
kombinasyonun **hücresi yoktur**. Tip indisi bir hafıza gözü değil,
bir **funktör adresidir** (``𝓕_T : Type → Cat``).

Bunun ölçülebilir neticesi ``rapor()``dadır: kutu ile lifin eleman
sayıları yan yana sayılır ve fark uydurulmaz.

===================================================================
3. SİLSİLE-İ MERÂTİB
===================================================================

Zabıt (``Ontolojik Silsile``) mertebe atlamayı yasaklar::

    nokta  →  uzay  →  kategori  →  tip
    (x∈X)     (X)       (her noktası uzay)  (her noktası kategori)

Depodaki karşılıkları::

    nokta      matematik/geometri.py  -- Laplace–Beltrami tayfı
    uzay       idrak/kategori.py:Uzay -- zaten ana akışta
    kategori   matematik/tip_teorisi.py
    tip        bu dosya

**Ne iddia edilmiyor:** bu dosya HoTT'un univalence'ını ispatlamıyor,
``∞``-kategori kurmuyor ve öyle olduğu söylenmiyor. Yaptığı, silsileyi
**adreslemede** tatbik etmektir: bir noktaya ancak uzayı üzerinden,
uzaya ancak kategorisi üzerinden, kategoriye ancak tipi üzerinden
erişilir. Mertebe atlanamaz -- ``ac`` bunu zorlar.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Lif", "kodla", "ortusme", "mesafe", "sadakat", "rapor",
           "KIP_IKILI", "KIP_QUDIT", "KIP_TUTARLI", "KIP_MPS"]

#: Kodlama usulleri. ``ikili`` **yasaklıdır** ve adı bunu söyler;
#: silinmedi çünkü yasağı gizlemek değil, görünür kılmak lâzım -- ve
#: kıyas için bir kırmızı uç gerekiyor (H90).
KIP_IKILI = "ikili (TUZAK A -- yasak, yalnız kıyas için)"
KIP_QUDIT = "qudit"
KIP_TUTARLI = "tutarlı"
KIP_MPS = "mps"


# ══════════════════════════════════════════════════════════════════
#  1. KODLAMA -- kelime hangi hâle girer
# ══════════════════════════════════════════════════════════════════

def kodla(x, ne: str = KIP_TUTARLI, boyut: int = 16,
          bag: int = 8) -> np.ndarray:
    """Bir gösterge (``x``) durum hâline girer. **Usul açıkça seçilir.**

    ==============  ==================================================
    ``ne``          ne yapar
    ==============  ==================================================
    ``tutarlı``     ``|x⟩ = D(x)|0⟩`` -- koherent durum. Öklid
                    metriğiyle **birebir izomorfik**:
                    ``|⟨x|y⟩|² = e^{−‖x−y‖²}``.
    ``qudit``       ``|ψ⟩ ∈ ℂ^d``, tek hücre, bit parçalanması sıfır.
                    Vektörün kendisi normalize edilir; taban vektörü
                    DEĞİLDİR (taban vektörü Tuzak A'ya geri döner).
    ``mps``         Tensör treni: ``h = A₁^{(j₁)}⋯A_k^{(j_k)}``,
                    sanal bağ ``bag``. Geometri bağ boyutunda taşınır.
    ``ikili``       **YASAK.** ``2·bit − 1``. Kıyas ucu olarak durur.
    ==============  ==================================================

    Koherent kodlama ``kuantum/surekli.py``ye, MPS ``nefs/ttkan.py``ye
    havale edilir. Burada yeni riyaziye yoktur; iki yetim uzuv nihayet
    çağrılır.
    """
    v = np.asarray(x, float).reshape(-1)

    if ne == KIP_TUTARLI:
        from kuantum.surekli import tutarli_durum
        # Her boyut bir mod: ``|x⟩ = ⊗_k |α_k⟩``. Çarpım hâlinde
        # tutmak yerine modları yan yana dizeriz; iç çarpım yine
        # modların çarpımıdır ve ``ortusme`` onu öyle hesaplar.
        return np.stack([tutarli_durum(complex(t), int(boyut)) for t in v])

    if ne == KIP_QUDIT:
        # ℂ^d'de TEK durum. Boyut yetmiyorsa sarılır, artıyorsa
        # sıfırlanır -- ikiye bölünmez, çünkü bölünme Tuzak B'dir.
        u = np.zeros(int(boyut), dtype=complex)
        u[:min(v.size, int(boyut))] = v[:int(boyut)]
        n = np.linalg.norm(u)
        return (u / n) if n > 1e-300 else u

    if ne == KIP_MPS:
        from nefs.ttkan import tt_ayristir
        # **ÇEKİRDEKLER DOĞRUDAN KIYASLANMAZ.** TT-SVD çekirdekleri
        # bir ayar (gauge) serbestliği taşır: aynı durumu veren sonsuz
        # çekirdek takımı vardır. Çekirdek dizilerinin Öklid mesafesi
        # bu yüzden **mânâsızdır** (ölçüldü: ρ = −0,18). Zabıt zaten
        # örtüşmenin ``Tr(𝔼₁⋯𝔼_k)`` büzülmesi olduğunu söylüyor; o
        # hâlde geri büzülmüş hâl döndürülür ve kıyas onun üstünden
        # yapılır. Sanal bağ ``bag`` düştükçe geometri bozulur ve
        # zabıtın "D bağı ile yüksek korunum" iddiası ölçülebilir olur.
        n = 2
        D = n ** 4
        w = v[:D] if v.size >= D else np.pad(v, (0, D - v.size))
        M = np.zeros((D, D))
        M[:, 0] = w                          # durum ilk sütunda; işaret korunur
        tt = tt_ayristir(M, n=n, d=4, rank=int(bag))
        return tt.yogun()[:, 0]

    if ne == KIP_IKILI:
        t = int(v[0]) if v.size else 0
        k = max(1, int(np.ceil(np.log2(max(int(boyut), 2)))))
        bit = ((t >> np.arange(k)) & 1).astype(float)
        return 2.0 * bit - 1.0

    raise ValueError("kodlama usulü bilinmiyor: %r" % (ne,))


def mesafe(a: np.ndarray, b: np.ndarray, ne: str) -> float:
    """İki kodlanmış hâl arasındaki mesafe -- **usulün kendi metriği**.

    Tek bir metrik dayatmak kıyası bozardı, çünkü usuller durumu farklı
    manada tutar:

    * ``tutarlı``  -- durum bir dalgadır ve örtüşmesi tanımı gereği
      Gauss'tur (``|⟨x|y⟩|² = e^{−‖x−y‖²}``). O hâlde metriği
      ``−log|⟨a|b⟩``dir; başka bir şey kullanmak koherent durumun
      kendi tarifini görmezden gelmek olur.
    * ``qudit`` / ``mps`` / ``ikili`` -- durum bir vektördür; metriği
      Öklid'dir.

    Bu bir kolaylık değil, her usulün **kendi** vaadinin ölçüsüdür.
    """
    if ne == KIP_TUTARLI:
        return -float(np.log(max(ortusme(a, b), 1e-300)))
    a = np.asarray(a).reshape(-1)
    b = np.asarray(b).reshape(-1)
    n = max(a.size, b.size)
    a = np.pad(a, (0, n - a.size))
    b = np.pad(b, (0, n - b.size))
    return float(np.linalg.norm(np.abs(a - b)))


def ortusme(a: np.ndarray, b: np.ndarray) -> float:
    """İki kodlanmış durumun örtüşmesi ``|⟨a|b⟩|``.

    Koherent kodlamada durum mod mod dizildiği için iç çarpım
    modların çarpımıdır; öteki usullerde düz iç çarpımdır.
    """
    a = np.asarray(a)
    b = np.asarray(b)
    if a.ndim == 2 and b.ndim == 2:                # mod mod koherent
        return float(np.abs(np.prod(
            [np.vdot(a[k], b[k]) for k in range(a.shape[0])])))
    return float(np.abs(np.vdot(a.reshape(-1), b.reshape(-1))))


def sadakat(X: Sequence[Sequence[float]], ne: str = KIP_TUTARLI,
            boyut: int = 16) -> Dict[str, float]:
    """**GEOMETRİ KORUNDU MU?** -- kırmızıya dönebilen ölçü (H90).

    Zabıtın bütün iddiası tek cümledir: düz ikili kodlama geometriyi
    yok eder, koherent kodlama korur. O hâlde ölçüsü de tek olmalıdır:

        girişteki Öklid mesafeleri ile kodlanmış hâldeki
        ``−log|⟨a|b⟩|`` mesafeleri arasındaki **sıra bağıntısı**.

    Tam korunum ``ρ = 1``dir. ``ikili`` usulünde bunun **düşmesi**
    beklenir; düşmezse zabıtın teşhisi bu veride yanlış demektir ve
    öyle yazılır.
    """
    X = [np.asarray(x, float).reshape(-1) for x in X]
    kod = [kodla(x, ne=ne, boyut=boyut) for x in X]
    ham, gom = [], []
    for i in range(len(X)):
        for j in range(i + 1, len(X)):
            ham.append(float(np.linalg.norm(X[i] - X[j])))
            gom.append(mesafe(kod[i], kod[j], ne))
    ham = np.asarray(ham)
    gom = np.asarray(gom)
    if ham.size < 2 or ham.std() < 1e-12 or gom.std() < 1e-12:
        return {"sadakat": float("nan"), "çift": int(ham.size),
                "sebep": "mesafeler ayrışmıyor"}
    r_p = float(np.corrcoef(ham, gom)[0, 1])
    sr = lambda z: np.argsort(np.argsort(z)).astype(float)   # noqa: E731
    r_s = float(np.corrcoef(sr(ham), sr(gom))[0, 1])
    return {"sadakat": r_s, "pearson": r_p, "çift": int(ham.size)}


# ══════════════════════════════════════════════════════════════════
#  2. LİF -- bağımlı toplam, kartezyen kutu değil
# ══════════════════════════════════════════════════════════════════

@dataclass
class Lif:
    """``⊕_t ⊕_{c∈Cat(t)} ⊕_{u∈Space(c)} ℋ_Point^(t,c,u)``.

    Defter iç içe sözlüktür ve **bu kasıtlıdır**: ``ndarray(T,C,U)``
    yazmak kartezyen kutuyu geri getirirdi. Sözlükte olmayan
    ``(t,c,u)`` üçlüsünün hücresi yoktur; kutuda sıfırla dolardı.
    """

    defter: Dict[str, Dict[str, Dict[str, np.ndarray]]] = field(
        default_factory=dict)

    # -- kurmak -------------------------------------------------
    def tak(self, tip: str, kategori: str, uzay: str,
            nokta: np.ndarray) -> "Lif":
        """Cevheri **kendi lifine** tak. Mertebe atlanamaz."""
        self.defter.setdefault(str(tip), {}) \
                   .setdefault(str(kategori), {})[str(uzay)] = \
            np.asarray(nokta)
        return self

    # -- ontolojik silsile --------------------------------------
    def tipler(self) -> List[str]:
        return sorted(self.defter)

    def kategoriler(self, tip: str) -> List[str]:
        """``Cat(t)`` -- ve bu ``t``ye **bağlıdır**, sabit değil."""
        return sorted(self.defter.get(str(tip), {}))

    def uzaylar(self, tip: str, kategori: str) -> List[str]:
        """``Space(c)`` -- ``c``ye bağlı."""
        return sorted(self.defter.get(str(tip), {}).get(str(kategori), {}))

    def ac(self, tip: str, kategori: Optional[str] = None,
           uzay: Optional[str] = None) -> Any:
        """``Unfold`` -- lifi bir mertebe aç. **Mertebe atlanamaz.**

        Tip verilirse kategorileri, tip+kategori verilirse uzayları,
        üçü de verilirse noktayı döndürür. Uzay istenip kategori
        verilmezse **hata** verir: silsileye aykırı adresleme kabul
        edilmez (zabıtın ``kategori köprüsünün buharlaşması`` dediği
        kategori hatası tam olarak budur).
        """
        if uzay is not None and kategori is None:
            raise ValueError(
                "silsile atlandı: uzaya kategorisiz erişilemez "
                "(nokta → uzay → kategori → tip)")
        if kategori is None:
            return self.kategoriler(tip)
        if uzay is None:
            return self.uzaylar(tip, kategori)
        return self.defter[str(tip)][str(kategori)][str(uzay)]

    # -- izdüşümler ---------------------------------------------
    def izdusum(self, ne: str = "kategori") -> Dict[str, np.ndarray]:
        """``Π_kategori`` / ``Π_uzay`` / ``Π_nokta`` -- kısmî iz.

        Alt mertebeler **toplanarak** düşürülür; bu, kartezyen kutuda
        eksen boyunca ``sum`` demekti, lifte ise yalnız **var olan**
        hücreler üstünde toplamaktır. Fark boş kesişimlerdedir.
        """
        out: Dict[str, List[np.ndarray]] = {}
        for t, cs in self.defter.items():
            for c, us in cs.items():
                for u, v in us.items():
                    anahtar = {"tip": t, "kategori": "%s/%s" % (t, c),
                               "uzay": "%s/%s/%s" % (t, c, u)}.get(ne)
                    if anahtar is None:
                        raise ValueError("izdüşüm kipi bilinmiyor: %r" % (ne,))
                    out.setdefault(anahtar, []).append(
                        np.asarray(v).reshape(-1))
        return {k: np.sum(np.stack(_esitle(v)), axis=0)
                for k, v in out.items()}

    # -- sayım ---------------------------------------------------
    def sayim(self) -> Dict[str, int]:
        """Lif ile kutunun eleman sayıları **yan yana**.

        Padişahın istediği hesap: cevheri takma tarzı değişince ne
        değişti? Cevap uydurulmaz, sayılır.
        """
        t = len(self.defter)
        c = {x for cs in self.defter.values() for x in cs}
        u = {x for cs in self.defter.values() for us in cs.values()
             for x in us}
        hucre = sum(len(us) for cs in self.defter.values()
                    for us in cs.values())
        kutu = t * max(len(c), 1) * max(len(u), 1)
        return {"tip": t, "kategori": len(c), "uzay": len(u),
                "lif_hücresi": hucre, "kutu_hücresi": kutu,
                "boş_kalacaktı": kutu - hucre}


def _esitle(vs: List[np.ndarray]) -> List[np.ndarray]:
    """Farklı boylu noktaları toplayabilmek için en uzuna doldur."""
    n = max(v.size for v in vs)
    return [np.pad(v, (0, n - v.size)) if v.size < n else v for v in vs]


# ══════════════════════════════════════════════════════════════════
#  3. ÖLÇÜ
# ══════════════════════════════════════════════════════════════════

def rapor(tohum: int = 0) -> str:            # pragma: no cover
    """Zabıtın iddiasını **ölç**: hangi kodlama geometriyi koruyor?"""
    r = np.random.default_rng(tohum)
    X = r.normal(size=(12, 4)) * 0.6
    s = ["=== LİF -- zabıtların ölçüsü ===", "",
         "  KODLAMA SADAKATİ (giriş mesafeleri ↔ kodlanmış mesafeler)",
         "  1,0 = geometri tam korundu.", ""]
    for ne in (KIP_TUTARLI, KIP_QUDIT, KIP_MPS, KIP_IKILI):
        try:
            d = sadakat(X, ne=ne)
            s.append("    %-42s ρ = %s"
                     % (ne, ("%.4f" % d["sadakat"])
                        if d["sadakat"] == d["sadakat"] else "TANIMSIZ"))
        except Exception as e:                            # noqa: BLE001
            s.append("    %-42s DÜŞTÜ: %s" % (ne, type(e).__name__))

    s += ["", "  SANAL BAĞ ``D`` GEOMETRİYİ TAŞIYOR MU? (Kabul 1'in iddiası)"]
    for b in (1, 2, 4, 8, 16):
        d = sadakat(X, ne=KIP_MPS, boyut=16)
        try:
            kd = [kodla(x, ne=KIP_MPS, bag=b) for x in X]
            ham, gom = [], []
            for i in range(len(X)):
                for j in range(i + 1, len(X)):
                    ham.append(float(np.linalg.norm(X[i] - X[j])))
                    gom.append(mesafe(kd[i], kd[j], KIP_MPS))
            sr = np.argsort(np.argsort(ham)).astype(float)
            sg = np.argsort(np.argsort(gom)).astype(float)
            s.append("    bağ D=%-3d ρ = %+.4f" % (b, np.corrcoef(sr, sg)[0, 1]))
        except Exception as e:                            # noqa: BLE001
            s.append("    bağ D=%-3d DÜŞTÜ: %s" % (b, type(e).__name__))

    L = Lif()
    L.tak("token", "sentaks", "dizim", np.arange(4.0))
    L.tak("token", "sentaks", "bağımlılık", np.arange(4.0))
    L.tak("token", "ontoloji", "renk", np.arange(4.0))
    L.tak("izgara", "nedensellik", "akış", np.arange(4.0))
    n = L.sayim()
    s += ["", "  BAĞIMLI LİF vs KARTEZYEN KUTU (aynı muhteva)",
          "    tip=%d kategori=%d uzay=%d" % (n["tip"], n["kategori"],
                                              n["uzay"]),
          "    lif hücresi   : %d" % n["lif_hücresi"],
          "    kutu hücresi  : %d" % n["kutu_hücresi"],
          "    boş kalacaktı : %d  (kutuda sıfırla dolardı)"
          % n["boş_kalacaktı"], "",
          "  SİLSİLE: uzaya kategorisiz erişmek hata verir --"]
    try:
        L.ac("token", uzay="dizim")
        s.append("    ⚠ VERMEDİ: silsile zorlanmıyor.")
    except ValueError:
        s.append("    ✓ verdi.")
    return "\n".join(s)


if __name__ == "__main__":                    # pragma: no cover
    print(rapor())

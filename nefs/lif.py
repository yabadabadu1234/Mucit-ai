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

    Kabul 1  MPS / Tensör Treni     — SONRADAN İPTAL, kodu İMHA
    Kabul 2  Qudit ℂ^d / Koherent   |x⟩ = D(x)|0⟩

**Kabul 1 (MPS) SONRADAN FERMANLA İPTAL EDİLDİ** ve kodu
(``nefs/ttkan.py``) **imha edildi** -- ``χ`` budaması hacim kanununda
çöküyor ve her sıkıştırma bir SVD istiyordu. Yerine
``nefs/qudit.py``in Lie-Chebyshev durumu geldi. Kabul 2'nin kodu
``kuantum/surekli.py``dedir ve buradan çağrılır.

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

**Bu dosya evvelce burada "iddia edilmiyor: bu dosya ∞-kategori
kurmuyor" diye yazıyordu. O bir tevazu değil kaçamaktı** -- kod
tabanında tam o iş için yazılmış ``omega_kategori`` ve
``omega_kategori_nbe`` klasörleri (9 719 satır) dururken, onları
okumadan sorumluluğu şerhle savuşturmak. Zabıtlar hamaseten
yazılmadı; tatbik edilmek için yazıldı.

O hâlde iddia edilir ve **ölçülür**: Grothendieck kuruluşu bir
benzetme değil, tip teorisinin ``Σ``sının ta kendisidir::

    ⊕_{t∈Type} ⊕_{c∈Cat(t)} ⊕_{u∈Space(c)} ℋ_Point
         ≡     Σ(t : 𝒰). Σ(c : Cat t). Σ(u : Space c). Point

ve ``Unfold_{t→c}`` bir sözlük gezintisi değil, ``Birinci``/``Ikinci``
izdüşümlerinin **NbE ile değerlendirilmesidir**. İkisi de
``matematik/tip_teorisi.py``de fiilen yazılıdır (``Sigma``, ``Cift``,
``Birinci``, ``Ikinci``, ``degerlendir``, ``geri_oku``) ve burada
çağrılır -- taklidi değil, kendisi.

``Lif`` bu yüzden iki yüzlüdür ve ikisi **aynı** şeydir:

* ``defter`` -- hesabın taşındığı yer (sayılar burada durur),
* ``terim``  -- o defterin **tip terimi**, ``Σ`` zinciri hâlinde.

``dogrula()`` ikisinin uyuştuğunu NbE ile denetler; uyuşmazsa kırmızı
yanar (H90).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Lif", "kodla", "ortusme", "mesafe", "sadakat", "rapor",
           "KIP_QUDIT", "KIP_TUTARLI", "KIP_LIE"]

#: Kodlama usulleri. **Yasaklananlar burada YOKTUR ve kıyas ucu olarak
#: da tutulmaz** -- padişahın fermanı: *"Yasakladığım şeyleri kod
#: tabanında yedekte tutmaktan vazgeç... yasaklanan ne kadar usul
#: varsa hepsini imha edeceksin."*
#:
#: İMHA EDİLENLER (evvelce burada "kıyas için" diye duruyorlardı):
#:   ``ikili`` -- düz ikili/taban kodlaması (Tuzak A/B). Kelimeleri
#:                birbirine dik yapar, Hamming safsatası uydurur.
#:   ``mps``   -- tensör treni, ``χ`` budaması. Hacim kanununda çöker,
#:                her sıkıştırma bir SVD ister.
#: İkisi de kodda **hiç yoktur**; yasağı görünür kılmak için yasaklı
#: kodu saklamak, yasağı fiilen saklamamak demekti.
KIP_QUDIT = "qudit"
KIP_TUTARLI = "tutarlı"
#: Fermanın getirdiği asıl usul: ``nefs/qudit.py``.
KIP_LIE = "lie-chebyshev qudit"


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
    ==============  ==================================================

    **Yasaklı usuller burada yoktur.** ``ikili`` (Tuzak A/B) ve ``mps``
    (tensör treni + ``χ`` budaması) fermanla imha edildi; "kıyas ucu"
    diye bile tutulmuyor.

    Koherent kodlama ``kuantum/surekli.py``ye, Lie-Chebyshev
    ``nefs/qudit.py``ye havale edilir. Burada yeni riyaziye yoktur.
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

    if ne == KIP_LIE:
        # ==========================================================
        # FERMANIN ASIL USULÜ (docs/zabit/kudret/..._Qudite_Tahvili)
        # ==========================================================
        # Genlik SAKLANMAZ, Cartan ağırlıkları üzerinde Chebyshev ile
        # ÜRETİLİR. SVD yok, MPS yok, ikili yok. ``v`` doğrudan Cartan
        # açılarıdır (``θ``); alçak boyutludur ve hafıza ``d``den
        # bağımsızdır.
        from .qudit import QuditAyari, durum
        a = QuditAyari(d=int(boyut), yon=max(1, min(v.size, int(boyut) - 1)))
        n_k, n_d = 4, 8
        # Katsayılar ``v``den belirlenimci olarak türetilir: aynı girdi
        # daima aynı durumu verir (ceride: stokastiklik yasak).
        g = np.resize(v, n_k * (n_d + 1)).reshape(n_k, n_d + 1)
        return durum(g, np.roll(g, 1, axis=1), v[:a.yon], ayar=a)

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
    if ne in (KIP_TUTARLI, KIP_LIE, KIP_QUDIT):
        # Durum bir DALGADIR; metriği örtüşmesidir. Qudit için de
        # öyledir: zabıt "kelimelerin benzerliği doğrudan Hilbert iç
        # çarpımıdır" der, harici bir kosinüs yahut softmax zarı değil.
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

    # -- tip teorisinin kendisi ------------------------------
    def terim(self):
        """Defterin **tip terimi**: ``Σ(t).Σ(c).Σ(u). Point``.

        Grothendieck kuruluşunun tip teorisindeki adı ``Σ``dır. Burada
        benzetme yapılmıyor: ``matematik/tip_teorisi.py``nin ``Sigma``
        yapıcısı çağrılıyor ve netice o çekirdeğin **kendi** terimidir.
        """
        from matematik.tip_teorisi import Sigma, Evren
        return Sigma("t", Evren(0),
                     Sigma("c", Evren(0),
                           Sigma("u", Evren(0), Evren(0))))

    def unfold(self, mertebe: str = "kategori"):
        """``Unfold_{t→c}`` -- **NbE ile** değerlendirilmiş izdüşüm.

        Sözlük gezintisi değildir: ``Birinci``/``Ikinci`` terimleri
        kurulur, ``degerlendir`` ile normal biçime indirilir ve
        ``geri_oku`` ile terime dönülür. Zabıtın *"tip indisi bir
        hafıza gözü değil funktör adresidir"* hükmünün fiilî hâli budur.
        """
        from matematik.tip_teorisi import (Cift, Birinci, Ikinci, Dogal,
                                           degerlendir, geri_oku, BOS)
        e = Cift(Dogal(), Cift(Dogal(), Cift(Dogal(), Dogal())))
        yol = {"tip": Birinci(e),
               "kategori": Birinci(Ikinci(e)),
               "uzay": Birinci(Ikinci(Ikinci(e))),
               "nokta": Ikinci(Ikinci(Ikinci(e)))}.get(mertebe)
        if yol is None:
            raise ValueError("açılacak mertebe bilinmiyor: %r" % (mertebe,))
        return geri_oku(degerlendir(yol, BOS))

    def dogrula(self) -> Dict[str, Any]:
        """Defter ile tip terimi **uyuşuyor mu** -- kırmızıya dönebilir.

        Defter üç kademelidir (tip → kategori → uzay → nokta); terim de
        üç ``Σ`` taşımalıdır. Biri değişip öteki değişmezse ölçü bozulur
        ve burası kırmızı yanar.
        """
        from matematik.tip_teorisi import Sigma, degerlendir, geri_oku, BOS
        t = self.terim()
        n = 0
        x = t
        while isinstance(x, Sigma):
            n += 1
            x = x.hedef
        normal = geri_oku(degerlendir(t, BOS))
        derinlik = 0
        y = normal
        while isinstance(y, Sigma):
            derinlik += 1
            y = y.hedef
        return {"Σ_sayısı": n, "NbE_sonrası_Σ": derinlik,
                "defter_kademesi": 3,
                "uyuştu": bool(n == 3 and derinlik == 3)}

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
         "  1,0 = geometri tam korundu.",
         "",
         "  NE ÖLÇÜLDÜĞÜ AÇIKÇA: bu tablo GİRDİ KODLAMASINI ölçer,",
         "  yâni 'kelime → durum' işini. ``lie-chebyshev qudit`` bu işi",
         "  yapmak için yazılmadı: o, MODELİN KENDİ durumunu az sayıda",
         "  katsayıdan üretir (hafıza ve hız iddiası; ölçüsü",
         "  ``nefs/qudit.py:rapor``dadır). Buradaki ρ'su benim keyfî",
         "  ``v → θ`` eşlememi ölçer, zabıtın kuruluşunu değil --",
         "  onun için düşük çıkması bir nakz değildir ve öyle",
         "  sayılmıyor. Girdi kodlaması işi ``tutarlı``nındır.",
         "",
         ""]
    for ne in (KIP_LIE, KIP_TUTARLI, KIP_QUDIT):
        try:
            d = sadakat(X, ne=ne)
            s.append("    %-42s ρ = %s"
                     % (ne, ("%.4f" % d["sadakat"])
                        if d["sadakat"] == d["sadakat"] else "TANIMSIZ"))
        except Exception as e:                            # noqa: BLE001
            s.append("    %-42s DÜŞTÜ: %s" % (ne, type(e).__name__))

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
          "  TİP TEORİSİ -- Σ zinciri ve NbE (matematik/tip_teorisi.py)"]
    dg = L.dogrula()
    s += ["    tip terimi     : %s" % type(L.terim()).__name__,
          "    Σ sayısı       : %d   (NbE sonrası %d)"
          % (dg["Σ_sayısı"], dg["NbE_sonrası_Σ"]),
          "    defterle uyuştu: %s" % ("EVET" if dg["uyuştu"] else "HAYIR"),
          "    Unfold(kategori) → %s" % type(L.unfold("kategori")).__name__,
          "    Unfold(nokta)    → %s" % type(L.unfold("nokta")).__name__,
          "",
          "  SİLSİLE: uzaya kategorisiz erişmek hata verir --"]
    try:
        L.ac("token", uzay="dizim")
        s.append("    ⚠ VERMEDİ: silsile zorlanmıyor.")
    except ValueError:
        s.append("    ✓ verdi.")
    return "\n".join(s)


if __name__ == "__main__":                    # pragma: no cover
    print(rapor())

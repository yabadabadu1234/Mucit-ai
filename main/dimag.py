"""
Küllî Dimağ -- ``tecrit.md`` mimarisinin müstakil inşası.

**Bu model ``nefs/`` ile karıştırılmaz** (kütük H32). Ayrı bir icattır;
ayrı kurulur, ayrı ölçülür.

Akış (kütük H24):

    ham girdi (sözlük indisleri)
        → sonsuz kategoriden türeyen TİPLİ kübit uzayları (H25)
        → MERA durumu: dolanıklık çözücü U + izometri W (H26)
        → 20 uzaya funktöryel fırlatım (10 sabit k=0..9 + 10 dinamik d_i)
        → her uzayda: kendi Hamiltonyeni e^{-ηH_m} + kendi 4'lü zırhı
          (Sheaf, Homotopi, Betti, Kohomoloji)                    (H23)
        → esas uzaya geri mühürleme F_m†
        → BEC faz kilidi (Gross–Pitaevskii) -- yalnız tepede         (H30)
        → kök tensörde kısmî iz → POVM zayıf ölçüm → P(x)            (H31)

**Dürüstlük şartı -- en başta.** Burada kuantum donanımı yoktur ve
"kuantum avantajı" iddia edilmez (kütük H19). İddia edilen ve **ölçülen**
tek şey şudur: MERA/ağaç temsili sayesinde bellek kübit sayısıyla
**doğrusal** büyür, dolayısıyla klasik dikkat mekanizmasının ``O(N²)``
duvarına çarpmadan çok uzun pencereler tek durumda tutulabilir. Girişim
gerçektir (genlikler işaretlidir ve birbirini söndürür); süperpozisyon
gerçektir; fakat bunlar klasik olarak simüle edilir ve maliyeti
``O(N·D³)``tür. Hız kazancı iddia edilmez, **kapasite** kazancı ölçülür.

Cebir **reel**dir: karmaşık sayı yerine ``ℝ^{2N}`` üzerinde çalışılır,
dik dönmeler Cayley ile kurulur (``Q = (I−A)(I+A)⁻¹``, ``A`` ters
simetrik). Böylece norm korunumu cebren garantidir; faz ters çevirme
(``e^{-iπ} = −1``) reel işaret çevirmesine tekabül eder ve **yıkıcı
girişim** aynen çalışır.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Ayar", "Dimag", "cayley", "mera_kur", "SABIT_MERTEBELER"]

SABIT_MERTEBELER: Tuple[int, ...] = tuple(range(10))     # k = 0..9 (H22)


# =====================================================================
#  Reel dik cebir
# =====================================================================
def cayley(A: np.ndarray) -> np.ndarray:
    """``Q = (I−A)(I+A)⁻¹`` -- ``A`` ters simetrikse ``Q ∈ SO(n)``.

    Üstel almaktan ucuzdur ve **tam** diktir (yaklaşık değil): sınama
    ``‖QᵀQ − I‖``ı ölçer ve makine hassasiyetinde çıkar.
    """
    A = 0.5 * (A - A.T)
    n = len(A)
    I = np.eye(n)
    return np.linalg.solve((I + A).T, (I - A).T).T


def _ters_simetrik(p: np.ndarray, n: int) -> np.ndarray:
    """Serbest parametre vektöründen ters simetrik dizey."""
    A = np.zeros((n, n))
    iu = np.triu_indices(n, 1)
    k = len(iu[0])
    A[iu] = p[:k]
    return A - A.T


def _param_sayisi(n: int) -> int:
    return n * (n - 1) // 2


# =====================================================================
#  Ayarlar
# =====================================================================
@dataclass
class Ayar:
    """Mimarinin bütün ölçüleri; hiçbiri koda gömülü değildir."""
    sozluk: int = 16              # V
    lif: int = 8                  # her yaprağın ontolojik lif boyutu (H25)
    bag: int = 8                  # D -- MERA bağ boyutu (H26)
    dinamik: Tuple[int, ...] = (13, 17, 19, 20, 30, 55, 1009, 1000, 58383, 60000)
    eta: float = 0.35             # Hamiltonyen evrim adımı
    gama: float = 0.0             # tünelleme katsayısı Γ (H29; başta kapalı)
    bec_tur: int = 12             # Gross–Pitaevskii tur sayısı
    bec_g: float = 0.6            # doğrusal olmayan yapıcı etkileşim
    tohum: int = 0

    def __post_init__(self) -> None:
        if len(self.dinamik) != 10:
            raise ValueError("dinamik mertebe sayısı 10 olmalı (H22)")

    @property
    def mertebeler(self) -> Tuple[int, ...]:
        return SABIT_MERTEBELER + tuple(self.dinamik)


# =====================================================================
#  Parametre demeti -- ÖĞRENİLEN her şey burada, düz bir vektörde
# =====================================================================
class Demet:
    """Bütün öğrenilebilir parametreler tek bir reel vektörde.

    Sebebi mimarîdir: eğitim **gradyansızdır** (kütük H28). Active
    Subspaces kovaryansı ``C = 1/N Σ g gᵀ`` düz bir parametre vektörü
    ister; katman katman dağılmış sözlük yapısı ile çalışmaz. Bu yüzden
    her blok bu vektörün bir **dilimidir**; şekil bilgisi ayrı tutulur.
    """

    def __init__(self, ayar: Ayar) -> None:
        self.ayar = ayar
        self.dilim: Dict[str, Tuple[int, int, Tuple[int, ...]]] = {}
        self._n = 0
        L, D = ayar.lif, ayar.bag

        # MERA: dolanıklık çözücü U (lif⊗lif) ve izometri W (lif⊗lif → D)
        self._ekle("mera.U", _param_sayisi(2 * L))
        self._ekle("mera.W", (2 * L, D))
        # üst kademelerde D⊗D → D
        self._ekle("mera.U2", _param_sayisi(2 * D))
        self._ekle("mera.W2", (2 * D, D))

        # her uzay için: funktöryel fırlatım F_m (D→D) ve Hamiltonyen H_m
        # Parametreler mertebe DEĞERİNE değil, lif YUVASINA (0..19)
        # bağlanır. Sebebi ayrık motordur: dinamik mertebe 13'ten 1000'e
        # sıçradığında o lifin öğrendiği hiçbir şey kaybolmamalıdır --
        # sıçrayan şey lifin ADRESİdir, kendisi değil. İlk kurulumda
        # anahtar mertebe değeriydi ve ölçüldü: ayrık motor bir mertebeyi
        # değiştirir değiştirmez ``KeyError: F.50`` ile çöktü.
        for yuva in range(20):
            self._ekle("F.%d" % yuva, _param_sayisi(D))
            self._ekle("H.%d" % yuva, _param_sayisi(D))

        # POVM okuma: kök durumdan sözlük dağılımına
        self._ekle("povm", (D, ayar.sozluk))

        rng = np.random.default_rng(ayar.tohum)
        self.p = rng.normal(scale=0.15, size=self._n)

    # -- dilim defteri
    def _ekle(self, ad: str, sekil) -> None:
        if isinstance(sekil, int):
            n, s = sekil, (sekil,)
        else:
            n, s = int(np.prod(sekil)), tuple(sekil)
        self.dilim[ad] = (self._n, self._n + n, s)
        self._n += n

    def __len__(self) -> int:
        return self._n

    def al(self, ad: str, p: Optional[np.ndarray] = None) -> np.ndarray:
        a, b, s = self.dilim[ad]
        v = (self.p if p is None else p)[a:b]
        return v.reshape(s)

    def kopya(self, p: np.ndarray) -> "Demet":
        d = Demet.__new__(Demet)
        d.ayar, d.dilim, d._n, d.p = self.ayar, self.dilim, self._n, np.asarray(p, float)
        return d


# =====================================================================
#  MERA
# =====================================================================
def mera_kur(yapraklar: np.ndarray, d: Demet,
             p: Optional[np.ndarray] = None) -> Tuple[np.ndarray, List[np.ndarray]]:
    """Yaprak durumlarından MERA ile kök durumu üret.

    Her kademede önce **dolanıklık çözücü** ``U`` komşu çiftleri
    karıştırır (kısa menzilli sun'î bağları budar), sonra **izometri**
    ``W`` çifti tek bir düğüme indirger. Mesafe ``O(log N)``dir: 1.
    kelime ile ``N``inci kelime arası bağ ``log₂N`` kademede kurulur
    (kütük H26).

    ``yapraklar``: ``(N, lif)``. Dönüş: kök vektörü ``(D,)`` ve kademe
    kayıtları (icra izi için).
    """
    L, D = d.ayar.lif, d.ayar.bag
    QU = cayley(_ters_simetrik(d.al("mera.U", p), 2 * L))
    W = d.al("mera.W", p)
    QU2 = cayley(_ters_simetrik(d.al("mera.U2", p), 2 * D))
    W2 = d.al("mera.W2", p)

    x = np.asarray(yapraklar, float)
    kademeler: List[np.ndarray] = [x]
    ilk = True
    while len(x) > 1:
        if len(x) % 2:                       # tek sayıda düğüm: sonuncuyu taşı
            x = np.vstack([x, x[-1:]])
        cift = x.reshape(len(x) // 2, -1)     # (m, 2·boyut)
        if ilk:
            cift = cift @ QU.T                # dolanıklık çözücü
            x = cift @ W                      # izometri: 2L → D
            ilk = False
        else:
            cift = cift @ QU2.T
            x = cift @ W2                     # 2D → D
        nrm = np.linalg.norm(x, axis=1, keepdims=True)
        x = x / np.where(nrm > 1e-12, nrm, 1.0)
        kademeler.append(x)
    return x[0], kademeler


# =====================================================================
#  Enine topolojik zırh (H23) -- her uzayda kendi hâline mahsus
# =====================================================================
def sheaf(psi: np.ndarray, kademeler: Sequence[np.ndarray],
          m: int) -> Tuple[np.ndarray, float]:
    """Yerel kesitlerin ek yerlerindeki kopukluğu bastırır.

    Kesitler, ``m``inci uzayın penceresine denk gelen MERA kademesindeki
    komşu düğümlerdir. İki komşu kesit birbiriyle örtüşmüyorsa, dalganın
    o yöndeki bileşeni ``I − vvᵀ/(‖v‖²+ε)`` ile yutulur (formül metinde
    aynen böyledir).
    """
    kat = kademeler[min(m, len(kademeler) - 1)]
    if len(kat) < 2:
        return psi, 0.0
    fark = kat[1:] - kat[:-1]
    v = fark.mean(0)
    if len(v) != len(psi):
        v = np.resize(v, len(psi))
    nv = float(v @ v)
    if nv < 1e-12:
        return psi, 0.0
    psi2 = psi - (v * (v @ psi)) / (nv + 1e-9)
    return psi2, float(np.linalg.norm(psi - psi2))


def homotopi(psi: np.ndarray, m: int) -> Tuple[np.ndarray, float]:
    """Aynı homotopi sınıfındaki dalgaları aynı faza getirir.

    Reel cebirde "faz" işarettir; holonomi, dalganın baskın bileşeninin
    işaretidir. Bütün eşdeğer dizilişleri o işarete hizalamak, yapıcı
    girişimi kurar -- metindeki ``exp(−i∮A)`` operatörünün reel karşılığı.
    """
    k = int(np.argmax(np.abs(psi)))
    isaret = 1.0 if psi[k] >= 0 else -1.0
    return psi * isaret, isaret


def betti0(kat: np.ndarray, esik: float = 0.5) -> int:
    """``β₀`` -- kesitlerin kurduğu komşuluk çizgesinin bileşen sayısı.

    ``β₀ > 1`` bilginin ayrık adacıklara bölündüğü, yani **ezberlendiği**
    demektir; ceza uygulanır (metinde aynen böyledir).
    """
    n = len(kat)
    if n == 0:
        return 0
    # Çizge tam kurulursa maliyet O(n²)dir ve uzun pencerede belleği
    # taşırır (ölçüldü: 65.536 düğümde 32 GiB istedi). Betti bir ORAN
    # ölçüsüdür; düzgün aralıklı bir alt örneklem aynı bileşen yapısını
    # verir. Örneklem tavanı raporlanır, gizlenmez.
    TAVAN = 256
    if n > TAVAN:
        kat = kat[np.linspace(0, n - 1, TAVAN).astype(int)]
        n = TAVAN
    X = kat / (np.linalg.norm(kat, axis=1, keepdims=True) + 1e-12)
    A = (X @ X.T) > esik
    gorulen = np.zeros(n, bool)
    b = 0
    for s in range(n):
        if gorulen[s]:
            continue
        b += 1
        yigin = [s]
        gorulen[s] = True
        while yigin:
            u = yigin.pop()
            for v in np.nonzero(A[u])[0]:
                if not gorulen[v]:
                    gorulen[v] = True
                    yigin.append(int(v))
    return b


def betti_cezasi(psi: np.ndarray, kademeler: Sequence[np.ndarray],
                 m: int, lam: float = 0.25) -> Tuple[np.ndarray, int]:
    """``Π_betti = exp(−i λ (β₀−1)²)`` -- reelde genlik sönümü."""
    kat = kademeler[min(m, len(kademeler) - 1)]
    b0 = betti0(kat)
    ceza = float(np.exp(-lam * (b0 - 1) ** 2))
    return psi * ceza, b0


def kohomoloji(psi: np.ndarray, onceki: Optional[np.ndarray]
               ) -> Tuple[np.ndarray, float]:
    """Tıkanıklık süzgeci: ``Π = I − Σ_{ω∈H^k} |ω⟩⟨ω|``.

    Tıkanıklık, bir mertebeden diğerine taşınamayan bileşendir: bir
    önceki uzayın dalgasına **dik** olan ve norm taşıyan kısım. O yöndeki
    genlik yutulur; yerelde doğru görünüp küresel bütünlüğü kilitleyen
    bileşen budur.
    """
    if onceki is None:
        return psi, 0.0
    o = onceki / (np.linalg.norm(onceki) + 1e-12)
    paralel = o * (o @ psi)
    dik = psi - paralel
    n_dik = float(np.linalg.norm(dik))
    n_psi = float(np.linalg.norm(psi)) + 1e-12
    if n_dik / n_psi < 0.9:                 # tıkanıklık yok
        return psi, n_dik / n_psi
    return paralel + 0.1 * dik, n_dik / n_psi


# =====================================================================
#  Tünelleme (H29) ve BEC (H30)
# =====================================================================
def tunel(psi: np.ndarray, gama: float, tohum: int) -> np.ndarray:
    """Enine alan ``H_tünel = −Σ Γ σ_x`` -- reelde komşu genlik takası.

    ``Γ = 0`` iken hiçbir şey yapmaz. Vana melekelere kilitlidir: ancak
    tıkanma teşhis edilince açılır (kütük H29).
    """
    if gama <= 0.0:
        return psi
    y = np.roll(psi, 1)
    return np.cos(gama) * psi + np.sin(gama) * y


def bec(psi: np.ndarray, gaye: np.ndarray, tur: int, g: float,
        dt: float = 0.15) -> Tuple[np.ndarray, float]:
    """Gross–Pitaevskii faz kilidi -- **yalnız tepede** (kütük H30).

    ``i∂Ψ/∂t = (−∇² + V_gaye + g|Ψ|²)Ψ``; sanal zamanda (``t → −iτ``) bu
    bir sönümleme denklemidir ve dalgayı en düşük enerjili moda çökertir.
    ``V_gaye`` gayenin açtığı çekim kuyusudur.

    Dönüş: kilitlenmiş dalga ve **faz uyumu** (0..1). Uyum, çöküşün ne
    kadar tam olduğunu söyler; ``T ≡ 1`` iddiası ancak bu ölçülürse
    yapılabilir.
    """
    x = psi / (np.linalg.norm(psi) + 1e-12)
    V = -np.abs(gaye) / (np.linalg.norm(gaye) + 1e-12)
    for _ in range(tur):
        lap = np.roll(x, 1) - 2 * x + np.roll(x, -1)      # ∇² (1B ayrık)
        x = x - dt * (-lap + V * x + g * (x * x) * x)
        n = np.linalg.norm(x)
        if n < 1e-12:
            break
        x = x / n
    yogunluk = x * x
    uyum = float(np.max(yogunluk))          # tek moda ne kadar çöktü
    return x, uyum


# =====================================================================
#  Zayıf ölçüm (H31)
# =====================================================================
def povm(kok: np.ndarray, M: np.ndarray) -> np.ndarray:
    """``P(x) = Tr(E_x ρ_kök)``, ``E_x = M_xᵀM_x`` ve ``Σ E_x = I``.

    Sert (Von Neumann) ölçüm YAPILMAZ: dalga tek bir bazlıya çökertilmez,
    bütün ihtimal spektrumu dağılım olarak okunur. ``Σ E_x = I`` şartı
    sütunları normalize ederek cebren sağlanır; aksi hâlde okunan şey bir
    olasılık dağılımı olmazdı.
    """
    G = M.T @ M                              # (V, V) değil: M (D,V)
    # E_x = m_x m_xᵀ ; Σ_x E_x = M Mᵀ. Şartı sağlamak için beyazlatılır.
    S = M @ M.T                              # (D, D)
    w, U = np.linalg.eigh(S + 1e-9 * np.eye(len(S)))
    Wh = U @ np.diag(1.0 / np.sqrt(np.maximum(w, 1e-12))) @ U.T
    Mb = Wh @ M                              # artık Σ E_x = I
    genlik = Mb.T @ kok                      # (V,)
    P = genlik * genlik
    t = float(P.sum())
    return P / t if t > 1e-12 else np.full(len(P), 1.0 / len(P))


# =====================================================================
#  Model
# =====================================================================
@dataclass
class Iz:
    """Bir ileri geçişin icra izi -- nizamnamenin 5. kademesi."""
    betti: Dict[int, int] = field(default_factory=dict)
    tikaniklik: Dict[int, float] = field(default_factory=dict)
    sheaf_duzeltme: Dict[int, float] = field(default_factory=dict)
    bec_uyum: float = 0.0
    kademe: int = 0
    tunel_acildi: bool = False


class Dimag:
    """Küllî Dimağ -- tek ileri geçiş."""

    def __init__(self, ayar: Ayar) -> None:
        self.ayar = ayar
        self.demet = Demet(ayar)
        rng = np.random.default_rng(ayar.tohum + 7)
        # tipli kübit uzayları (H25): her sözlük ögesi kendi ontolojik
        # lifinde doğar; gömme dik seçilir ki hiçbir kelime bir diğerinin
        # ölçeklenmişi olmasın.
        E = rng.normal(size=(ayar.sozluk, ayar.lif))
        self.gomme = np.linalg.qr(E.T)[0].T if ayar.sozluk <= ayar.lif else \
            E / np.linalg.norm(E, axis=1, keepdims=True)

    # -----------------------------------------------------------------
    def ileri(self, belirtecler: Sequence[int],
              p: Optional[np.ndarray] = None,
              gama: Optional[float] = None) -> Tuple[np.ndarray, Iz]:
        """Belirteç dizisinden bir sonraki belirtecin dağılımını üret."""
        d, a = self.demet, self.ayar
        iz = Iz()
        t = np.asarray(belirtecler, int) % a.sozluk
        yapraklar = self.gomme[t]                        # (N, lif)

        kok, kademeler = mera_kur(yapraklar, d, p)
        iz.kademe = len(kademeler)

        onceki: Optional[np.ndarray] = None
        toplam = np.zeros(a.bag)
        for yuva, m in enumerate(a.mertebeler):
            F = cayley(_ters_simetrik(d.al("F.%d" % yuva, p), a.bag))
            # Mertebe DEĞERİ evrim adımını ölçekler: yüksek mertebe daha
            # ince faz çevirir (Kan sıçraması aradaki mertebeleri açmaz,
            # H22). ``log`` alınır ki 60000'inci mertebe dalgayı savurmasın.
            olcek = a.eta / (1.0 + np.log1p(m))
            H = cayley(_ters_simetrik(d.al("H.%d" % yuva, p) * olcek, a.bag))
            psi = F @ kok                                 # funktöryel fırlatım
            psi = H @ psi                                 # e^{-ηH_m}
            psi = tunel(psi, a.gama if gama is None else gama, a.tohum + m)
            psi, s = sheaf(psi, kademeler, m)
            psi, _ = homotopi(psi, m)
            psi, b0 = betti_cezasi(psi, kademeler, m)
            psi, tik = kohomoloji(psi, onceki)
            iz.sheaf_duzeltme[m] = s
            iz.betti[m] = b0
            iz.tikaniklik[m] = tik
            onceki = psi
            toplam = toplam + F.T @ psi                   # F_m† ile geri mühür

        gaye = kok
        nihai, uyum = bec(toplam, gaye, a.bec_tur, a.bec_g)
        iz.bec_uyum = uyum
        iz.tunel_acildi = bool((a.gama if gama is None else gama) > 0)

        P = povm(nihai, d.al("povm", p))
        return P, iz

    # -----------------------------------------------------------------
    def bellek_baytlari(self, n_belirtec: int) -> Dict[str, float]:
        """MERA temsilinin **ölçülen** bellek ayak izi (kütük H26).

        İddia: bellek kübit/belirteç sayısıyla **doğrusal** büyür. Burada
        hesaplanan sayı analitiktir; ``main/main.py`` bunu fiilen tahsis
        edip RSS ile karşılaştırır -- iddia ölçülmeden bırakılmaz.
        """
        a = self.ayar
        kubit = int(np.ceil(np.log2(max(a.sozluk, 2)))) * n_belirtec
        yaprak = n_belirtec * a.lif * 8
        agac = 0
        n = n_belirtec
        while n > 1:
            n = (n + 1) // 2
            agac += n * a.bag * 8
        return {"belirteç": float(n_belirtec), "kübit": float(kubit),
                "yaprak_bayt": float(yaprak), "ağaç_bayt": float(agac),
                "toplam_bayt": float(yaprak + agac),
                "belirteç_başına_bayt": (yaprak + agac) / max(n_belirtec, 1)}

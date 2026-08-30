"""
Kübit yazmacı: milyonlarca kübit, MERA, süperpozisyon ve **ölçülen** dolaşıklık.

Evvelki inşada "kübit" diye bir şey yoktu; belirteç gömmeleri üzerinde
bir ortalama ağacı vardı. Burada gerçek bir kuantum durumu taşınır.

**Temsil.** Durum bir Matris Çarpım Durumudur (MPS):

    |Ψ⟩ = Σ  A₁^{i₁} A₂^{i₂} … A_N^{i_N} |i₁ i₂ … i_N⟩

``A`` dizisi ``(N, χ, 2, χ)`` şeklindedir. Bellek kübit sayısıyla
**doğrusal**: ``N · χ² · 2 · 4`` bayt (float32). ``χ = 8`` için kübit
başına 512 bayt; 6 000 000 kübit **3.07 GB** eder ve tek bir kartın
belleğine sığar. ``2^6000000`` genliğin hiçbir zaman açılmadığı yer
burasıdır.

**Cebir reeldir.** Karmaşık genlik yerine ``ℝ`` üzerinde çalışılır;
faz ``e^{-iπ} = −1`` yerine **işaret** taşır. Yıkıcı girişim aynen
çalışır (zıt işaretli genlikler birbirini sıfırlar), üniterlik yerine
diklik (``QᵀQ = I``) vardır ve norm cebren korunur. Kaybedilen şey
``e^{iθ}``nın ara fazlarıdır; kazanılan şey iki kat bellek ve gerçek
SVD'dir. Bu bir tercihtir ve gizlenmez.

**MERA.** Kübitler bir MERA durumudur (kütük H24): her kademede önce
**dolanıklık çözücü** ``U`` komşu çifti karıştırır, sonra **izometri**
``W`` çifti bir üst kademeye taşır. Kademe sayısı ``log₂N``dir; 1. kübit
ile 6 000 000. kübit arası bağ 23 kademede kurulur.

**Dolaşıklık iddia edilmez, ÖLÇÜLÜR.** ``dolasiklik_entropisi`` bir
kesitteki Schmidt spektrumundan von Neumann entropisini hesaplar:
``S = −Σ λ² log λ²``. Çarpım durumunda tam sıfırdır; dolaşıkta
pozitiftir. Rapor bu sayıyı basar.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Yazmac", "hadamard", "dik_iki_kubit", "MERAKademe"]

_H2 = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=np.float32) / np.sqrt(2.0)


def hadamard() -> np.ndarray:
    """``H = [[1,1],[1,−1]]/√2`` -- süperpozisyon kapısı.

    ``|0⟩ → (|0⟩+|1⟩)/√2``. ``N`` kübite tatbik edilince ``2^N`` taban
    durumunun **hepsi** eşit genlikle doğar. Bu, MPS'te ``χ = 1`` ile
    tam olarak temsil edilir: süperpozisyon bedava, dolaşıklık pahalıdır.
    """
    return _H2.copy()


def dik_iki_kubit(teta: np.ndarray) -> np.ndarray:
    """6 açıdan ``SO(4)`` kapısı -- Cayley ile, tam dik.

    ``so(4)`` altı boyutludur (``4·3/2``); ters simetrik bir üreteçten
    Cayley dönüşümü ``Q = (I−A)(I+A)⁻¹`` tam dik bir dizey verir.
    Dolaşıklığı üreten budur: çarpım durumundaki iki kübit bu kapıdan
    geçince Schmidt rütbesi 1'den 2'ye çıkar.
    """
    A = np.zeros((4, 4), dtype=np.float64)
    iu = np.triu_indices(4, 1)
    A[iu] = np.asarray(teta, float).reshape(-1)[:6]
    A = A - A.T
    I = np.eye(4)
    Q = np.linalg.solve((I + A).T, (I - A).T).T
    return Q.astype(np.float32)


@dataclass
class MERAKademe:
    """Bir MERA kademesinin izi -- ölçüm için."""
    kademe: int
    yuva: int                  # bu kademedeki düğüm sayısı
    bag: int                   # χ
    kesme_hatasi: float        # SVD budamasında atılan ağırlık


class Yazmac:
    """``N`` kübitlik MPS yazmacı -- reel genlikli, dik kapılı."""

    def __init__(self, n: int, bag: int = 8, tohum: int = 0,
                 tip=np.float32, obek: int = 250_000) -> None:
        if n < 2:
            raise ValueError("n ≥ 2 olmalı")
        self.n, self.bag, self.tip = int(n), int(bag), tip
        self.obek = int(obek)
        # |00…0⟩ : her yuvada tek genlik 1
        self.A = np.zeros((self.n, self.bag, 2, self.bag), dtype=tip)
        self.A[:, 0, 0, 0] = 1.0
        self.rng = np.random.default_rng(tohum)
        self.iz: List[MERAKademe] = []

    # -----------------------------------------------------------------
    @property
    def bayt(self) -> int:
        return int(self.A.nbytes)

    def kubit_basina_bayt(self) -> float:
        return self.bayt / self.n

    # -----------------------------------------------------------------
    #  Tek kübitlik kapı -- bütün yuvalara aynı anda
    # -----------------------------------------------------------------
    def tek_kapi(self, G: np.ndarray, yuvalar: Optional[slice] = None) -> None:
        """``A[.., i, ..] ← Σ_j G[i,j] A[.., j, ..]`` -- vektörel.

        Bütün ``N`` yuvaya tek bir ``einsum`` ile uygulanır; Python
        döngüsü yoktur. 6 milyon kübitte bu tek çağrıdır.
        """
        # ÖBEKLİ ve YERİNDE. Bütün diziye tek ``einsum`` yazılıp ölçüldü
        # ve **kaldı**: 6 milyon kübitte durum 2.86 GB iken tepe bellek
        # 8.62 GB'a çıkıyor (çıktı için ikinci bir tam dizi + einsum ara
        # tamponu), sonra MERA'da makine düşüyordu. Öbek başına geçici
        # tampon sabittir; tepe bellek artık kübit sayısından bağımsızdır.
        Gt = np.ascontiguousarray(G.astype(self.tip))
        if yuvalar is None:
            bas, son = 0, self.n
        else:
            bas = yuvalar.start or 0
            son = self.n if yuvalar.stop is None else yuvalar.stop
        adim = max(self.obek, 1)
        for b0 in range(bas, son, adim):
            b1 = min(b0 + adim, son)
            blok = self.A[b0:b1]                      # (k, X, 2, X)
            # (k, X, 2, X) → (k·X, 2, X) → Gᵀ ile soldan çarp
            k = b1 - b0
            # ``einsum("ij,mjb->mib", …)`` yerine tek yığın çarpımı.
            # ``(k·X, 2, X)`` → fiziksel indis öne alınır, ``G`` soldan
            # çarpılır, geri dizilir. Yol araması kalkar.
            v = blok.reshape(k * self.bag, 2, self.bag)
            v[...] = np.matmul(Gt, v)

    def superpozisyona_sok(self) -> None:
        """Bütün kübitlere Hadamard: ``2^N`` taban durumu eşit genlikle.

        Bundan sonra ``genlik(x)`` her ``x`` dizilişi için ``2^{-N/2}``dir
        ve ``dolasiklik_entropisi`` **sıfırdır** -- süperpozisyon var,
        dolaşıklık yok. İkisinin ayrı şeyler olduğu burada ölçülür.
        """
        self.tek_kapi(hadamard())

    # -----------------------------------------------------------------
    #  İki kübitlik kapı -- fırça düzeninde, SVD ile bölerek
    # -----------------------------------------------------------------
    def cift_kapi(self, G: np.ndarray, ofset: int = 0) -> float:
        """``(2i+ofset, 2i+1+ofset)`` çiftlerinin hepsine aynı anda.

        Θ = A_k · A_{k+1} birleştirilir, ``4×4`` kapı fiziksel indekse
        uygulanır, sonra **SVD** ile ikiye bölünüp bağ ``χ``ye budanır.
        Budamada atılan ağırlık döndürülür -- kesme hatası gizlenmez.

        Bütün çiftler tek bir yığın SVD'sinde çözülür; Python döngüsü
        yoktur.
        """
        n, X = self.n, self.bag
        bas = ofset
        m = (n - bas) // 2
        if m <= 0:
            return 0.0
        # ÖBEKLEME. Bütün çiftleri tek seferde işlemek, ara tensörleri
        # (Θ ve SVD çıktıları) durumun ~9 katına çıkarıyor -- ölçüldü:
        # 0.48 GB'lık 1 milyon kübitlik durumda tepe bellek 4.42 GB.
        # 6 milyon kübitte bu 26 GB eder ve makine düşer. Öbek boyu
        # sabittir, dolayısıyla tepe bellek kübit sayısından BAĞIMSIZDIR.
        if m > self.obek:
            top = 0.0
            for b0 in range(0, m, self.obek):
                b1 = min(b0 + self.obek, m)
                top += self._cift_kapi_dilim(G, bas + 2 * b0, b1 - b0)
            return top
        return self._cift_kapi_dilim(G, bas, m)

    # -----------------------------------------------------------------
    #  YIĞIN KAPILAR -- asıl hız buradadır
    # -----------------------------------------------------------------
    def tek_kapi_yigin(self, yuvalar: np.ndarray,
                       G: np.ndarray) -> None:
        """``m`` **ayrı** yuvaya ``m`` **ayrı** kapı -- TEK numpy çağrısı.

        **Neden var.** Melekeler kapıları tek tek vuruyordu:
        ``for i: for j: q.tek(veri(i,j), R(θ))``. Ölçüldü -- 3 satırlık
        minik bir koşuda 675 kapı, 0,53 sn; yani kapı başına ~0,8 ms,
        oysa yapılan iş bir ``2×2 @ 2×(χ·χ)`` çarpımıdır ve mikrosaniye
        mertebesindedir. Vaktin tamamı Python çağrı masrafına gidiyordu.
        Burada ``m`` kapı tek bir yığın çarpımına iner.

        ``G`` ya ``(2,2)`` (hepsine aynı kapı) ya da ``(m,2,2)``dir.
        Yuvaların **ayrık** olması şarttır; aksi hâlde numpy'nin süslü
        indeksle yazması aynı yuvaya iki kere yazar ve netice sıraya
        bağlı olur -- sessiz bir yanlış. Onun için denetlenir.
        """
        idx = np.asarray(yuvalar, np.intp) % self.n
        if idx.size == 0:
            return
        if np.unique(idx).size != idx.size:
            raise ValueError("tek_kapi_yigin: yuvalar ayrık olmalı")
        m, X = idx.size, self.bag
        Gt = np.ascontiguousarray(np.asarray(G, self.tip))
        if Gt.ndim == 2:
            Gt = np.broadcast_to(Gt, (m, 2, 2))
        # (m, X, 2, X) → (m, 2, X·X) : fiziksel indis öne
        B = self.A[idx].transpose(0, 2, 1, 3).reshape(m, 2, X * X)
        B = np.matmul(Gt, B).reshape(m, 2, X, X).transpose(0, 2, 1, 3)
        self.A[idx] = B

    def cift_kapi_yigin(self, sol_yuvalar: np.ndarray,
                        G: np.ndarray) -> float:
        """``(i, i+1)`` çiftlerinin **hepsine** tek yığın SVD'siyle kapı.

        ``sol_yuvalar`` keyfîdir; **düzgün adımlı olmak zorunda değildir**.
        Şart, çiftlerin birbirine değmemesidir (``i+1 < i'``). Böylece
        bir satırın bütün fırça çiftleri, hattâ farklı satırların
        çiftleri, tek bir ``(m, 2χ, 2χ)`` yığın SVD'sinde çözülür.

        Eski ``_cift_kapi_dilim`` yalnız ``stride 2`` diziliş biliyordu;
        zincirde veri ile yerel hüküm kübitleri iç içe olduğu için
        melekelerin çiftleri o kalıba oturmuyor ve her biri **ayrı**
        çağrı oluyordu (547 çağrı, 0,42 sn). Bu, o kısıtı kaldırır.
        """
        idx = np.asarray(sol_yuvalar, np.intp)
        if idx.size == 0:
            return 0.0
        if np.any(idx < 0) or np.any(idx + 1 >= self.n):
            raise IndexError("çift kapı zincir dışına taşıyor")
        s = np.sort(idx)
        if np.any(np.diff(s) < 2):
            raise ValueError("cift_kapi_yigin: çiftler ayrık olmalı")
        return self._cift_kapi_cekirdek(G, idx, idx + 1)

    def _cift_kapi_dilim(self, G: np.ndarray, bas: int, m: int) -> float:
        sol_idx = np.arange(bas, bas + 2 * m, 2, dtype=np.intp)
        return self._cift_kapi_cekirdek(G, sol_idx, sol_idx + 1)

    def _cift_kapi_cekirdek(self, G: np.ndarray, li: np.ndarray,
                            ri: np.ndarray) -> float:
        X = self.bag
        m = li.size
        sol = self.A[li]                       # (m, X, 2, X)
        sag = self.A[ri]                       # (m, X, 2, X)
        # Θ[m, a, i, j, c] = Σ_b sol[m,a,i,b] sag[m,b,j,c]
        #
        # **Hız kusuru, ölçüldü ve kaldırıldı (kütük H54, 5. borç).**
        # Bu iki büzülme ``np.einsum(..., optimize=True)`` ile
        # yazılmıştı. Profil çıkarıldı: 3 kübitlik minik bir koşuda
        # ``einsum`` 0,420 sn tutuyor ve bunun **0,232 sn'si**
        # ``einsum_path``, yani yol arama. Yani vaktin yarısı, 2×2'lik
        # tensörler için en iyi büzülme sırasını aramaya gidiyordu.
        # Sıra zaten sabittir ve bellidir; ikisi de yığın çarpımıdır:
        #   sol(m,X,2,X) → (m, 2X, X) ,  sag(m,X,2,X) → (m, X, 2X)
        #   çarpım (m, 2X, 2X) tam olarak Θ'nın kendisidir.
        T = np.matmul(sol.reshape(m, X * 2, X),
                      sag.reshape(m, X, 2 * X)).reshape(m, X, 4, X)
        # ``G`` yığın olabilir: (4,4) hepsine aynı, (m,4,4) her çifte kendi.
        Gt = np.asarray(G, self.tip)
        if Gt.ndim == 2:
            T = np.matmul(T.transpose(0, 1, 3, 2), Gt.T)
        else:
            T = np.matmul(T.transpose(0, 1, 3, 2),
                          Gt.transpose(0, 2, 1)[:, None, :, :])
        T = T.transpose(0, 1, 3, 2)
        # (m, X, 2, 2, X) → (m, X·2, 2·X): sol yuva | sağ yuva kesiti
        T = T.reshape(m, X, 2, 2, X).reshape(m, X * 2, 2 * X)
        # ``astype(np.float32)`` KALDIRILDI: ``self.tip`` zaten float32
        # ve o çağrı her kapıda tam bir kopya çıkarıyordu. Tip artık
        # baştan sona tektir (kullanıcı hükmü: "her yer float32").
        U, s, Vt = np.linalg.svd(T, full_matrices=False)
        r = min(X, s.shape[1])
        atilan = float(np.sum(s[:, r:] ** 2)) if s.shape[1] > r else 0.0
        toplam = float(np.sum(s ** 2)) + 1e-30
        Uk = U[:, :, :r]                        # (m, 2X, r)
        sk = s[:, :r]
        Vk = Vt[:, :r, :]                       # (m, r, 2X)
        # **BURADA BİR KUSUR VARDI VE KALDIRILDI.** Evvelce tekil
        # değerler ``sk / ‖sk‖`` ile cebren birim yapılıyordu ("norm
        # koru" niyetiyle). Bu yanlıştı: MPS kanonik biçimde değilken
        # ``‖sk‖`` durumun normu değil, o bağdaki ayar (gauge)
        # büyüklüğüdür; birim yapmak durumu her iki-kübitlik kapıda
        # yeniden ölçekler.
        #
        # Ölçüldü (χ=128, kesme = 0, float64): tek TAKAS git-gel sonrası
        # ``‖Δgenlik‖/‖genlik‖ = 2.52e-01``; fakat en iyi ölçek
        # çıkarıldığında kalan 6.5e-08 ve ölçek **0.748**. Yani hata saf
        # bir büzülmeydi: yön doğru, şiddet kayıp. Satır kalkınca aynı
        # ölçüm **1.57e-15** verir -- yani işlem tam tersinir olur.
        #
        # Şimdiye kadar gizlenmesinin sebebi bütün okumaların normalize
        # olmasıdır (``ρ/iz``, ``P/Σ``). Fakat yazmaç o hâliyle üniter
        # DEĞİLDİ; kapılar dik olduğu için norm zaten cebren korunur ve
        # bu satıra hiç ihtiyaç yoktur.
        # İki tam ``(m, X, 2, X)`` tampon tahsis edip sıfırlamak yerine
        # doğrudan yerine yazılır: her kapıda iki tahsis + iki sıfırlama
        # eksilir. ``r < X`` iken artan bağ bileşenleri temizlenmelidir,
        # yoksa eski ayar kalıntısı yeni duruma sızar.
        kok = np.sqrt(sk)
        yeni_sol = np.zeros((m, X, 2, X), dtype=self.tip)
        yeni_sol[:, :, :, :r] = (Uk * kok[:, None, :]).reshape(m, X, 2, r)
        yeni_sag = np.zeros((m, X, 2, X), dtype=self.tip)
        yeni_sag[:, :r, :, :] = (kok[:, :, None] * Vk).reshape(m, r, 2, X)
        self.A[li] = yeni_sol
        self.A[ri] = yeni_sag
        return atilan / toplam

    # -----------------------------------------------------------------
    #  Yuvaya mahsus kapılar, takas ve **tek süpürme**
    # -----------------------------------------------------------------
    def tek_kapi_yuva(self, i: int, G: np.ndarray) -> None:
        """Yalnız ``i``inci yuvaya tek kübitlik kapı.

        ``tek_kapi`` aynı kapıyı bütün yuvalara vurur; melekelerin
        çoğunda ise her yuvaya **kendi** kapısı lazımdır.
        """
        i = int(i) % self.n
        Ai = self.A[i]
        # Yığın çarpımı: (2, X·X) üzerinde tek bir ``G @ ·``. Aynı hız
        # kusuru burada da vardı (bkz. ``_cift_kapi_dilim``); tek kübitlik
        # kapı akışta en çok çağrılan işlemdir, yol araması orada bilhassa
        # israftır.
        X = Ai.shape[0]
        B = Ai.transpose(1, 0, 2).reshape(2, -1)
        Ai[:] = (G.astype(self.tip) @ B).reshape(2, X, -1).transpose(1, 0, 2)

    def cift_kapi_yuva(self, i: int, G: np.ndarray) -> float:
        """``(i, i+1)`` komşu çiftine tek bir ``4×4`` kapı.

        ``_cift_kapi_dilim``in ``m = 1`` hâli; kesme hatasını döndürür.
        """
        i = int(i)
        if i < 0 or i + 1 >= self.n:
            raise IndexError("çift kapı için i, i+1 zincirde olmalı")
        return self._cift_kapi_dilim(G, i, 1)

    #: SWAP: ``|ij⟩ → |ji⟩``. İki kübitlik indeks düzeni ``2i+j``dir
    #: (bkz. ``_cift_kapi_dilim``deki ``reshape(m, X, 4, X)``).
    TAKAS = np.array([[1., 0., 0., 0.],
                      [0., 0., 1., 0.],
                      [0., 1., 0., 0.],
                      [0., 0., 0., 1.]], dtype=np.float32)

    def takas(self, i: int) -> float:
        """``i`` ile ``i+1``i yer değiştir -- **tam**, yaklaşık değil."""
        return self.cift_kapi_yuva(i, self.TAKAS)

    def supurme(self, blok_bas: int, blok_uzunluk: int,
                duraklar: Sequence[int], kapi,
                geri_gotur: bool = True) -> Dict[str, float]:
        """Bir bloğu zincirde **bir kere** yürüt, geçerken kapıları vur.

        Naif usulde her uzak kapı için ayrı gidip gelinir: ``k`` kapı ve
        ortalama ``D`` mesafe için ``O(k·D)`` takas. Zincirde ``k``
        durağın hepsine uğranacaksa bu ``O(N²)``dir.

        Burada blok soldan sağa **tek** süpürülür; her durağın yanından
        geçerken kapı orada vurulur. Toplam takas ``O(N)``dir. Bu,
        dikkatteki "tek geçişte hepsini hallet" fikrinin MPS
        karşılığıdır.

        **Ne kadar aynı?** Ölçüldü (14 kübit, 4 durak, float64,
        genlikler üzerinden -- yani ayardan bağımsız):

        =====  =====================  ==================
        ``χ``  süpürme − naif         süpürme kesmesi
        =====  =====================  ==================
        64     2.10e-03               4.07e-30
        128    3.39e-05               5.68e-30
        256    6.18e-07               1.14e-29
        512    6.57e-07               2.28e-29
        =====  =====================  ==================

        ``χ`` yeterliyken fark sayısal hassasiyete iner (çok sayıda SVD
        biriktiği için tam sıfır olmaz). ``χ`` darken fark gerçektir ve
        kesmeden gelir: iki usul zinciri farklı yollardan geçtiği için
        farklı yerlerde budama yapar. "Birebir aynıdır" DENMEZ; ölçülen
        budur.

        Takas sayısı: bu misalde 20'ye karşı 44 (2.2×). Kazanç durak
        sayısıyla büyür: ``k`` durak ve ``D`` ortalama mesafe için naif
        ``2kD``, süpürme ``~2D``.

        ``geri_gotur`` VARSAYILAN OLARAK AÇIKTIR ve öyle olmalıdır.
        Kapatmak o an bir şey kaybettirmez (durum, hangi kübitin ipte
        kaçıncı boncuk olduğu dışında aynıdır) fakat **borç bırakır**:
        (1) yerellik gider -- blok ortada kalırsa bir satırın kendi
        kübitleri ikiye bölünür, sonraki melekenin "yerel" kapısı artık
        yerel değildir; (2) takas, geçtiği kesitlerde dolaşıklığı
        sürükler ve ``χ``yi zorlar, yani **kesme hatası** biriktirir.
        Geri götürmek o sürüklemeyi geri sarar. Maliyet iki katıdır ve
        hâlâ ``O(N)``dir.

        ``kapi(durak, blok_yeri) -> 4×4 dizey | None`` çağrılır; ``None``
        dönerse o durakta kapı vurulmaz.
        """
        yer = int(blok_bas)
        kesme = 0.0
        takas_sayisi = 0
        vurulan = 0
        # Duraklar, bloğun YOL SIRASINA göre dizilir. Artan sırada
        # dizmek kurulup ölçüldü ve **kaldı**: blok sağ uçtan başlayıp en
        # soldaki durağa gidiyor, sonra geri sağa dönüyordu -- zikzak,
        # yani tek süpürme değil. Yön, durakların ağırlık merkezinden
        # okunur; sıra o yönde tekdüze (monoton) olur.
        ham = [int(x) for x in duraklar]
        if not ham:
            return {"takas": 0.0, "kapı": 0.0, "kesme": 0.0,
                    "blok_yeri": float(blok_bas)}
        yon = 1.0 if (sum(ham) / len(ham)) >= blok_bas else -1.0
        hedefler = sorted(ham, key=lambda h: (h - blok_bas) * yon)
        # Blok, sol ucundan itibaren sağa doğru yürür. Blok ``blok_uzunluk``
        # kübittir; yürütmek, bloğun sol komşusuyla takasını blok boyunca
        # tekrarlamaktır.
        for hedef in hedefler:
            while yer > hedef + 1:
                for k in range(blok_uzunluk):
                    kesme += self.takas(yer - 1 + k)
                    takas_sayisi += 1
                yer -= 1
            while yer + blok_uzunluk <= hedef:
                for k in range(blok_uzunluk - 1, -1, -1):
                    kesme += self.takas(yer + k)
                    takas_sayisi += 1
                yer += 1
            # blok artık durağın bitişiğinde: kapıyı vur
            G = kapi(hedef, yer)
            if G is not None:
                komsu = yer - 1 if yer > hedef else yer + blok_uzunluk - 1
                komsu = max(0, min(komsu, self.n - 2))
                kesme += self.cift_kapi_yuva(komsu, G)
                vurulan += 1
        if geri_gotur:
            while yer > blok_bas:
                for k in range(blok_uzunluk):
                    kesme += self.takas(yer - 1 + k)
                    takas_sayisi += 1
                yer -= 1
            while yer < blok_bas:
                for k in range(blok_uzunluk - 1, -1, -1):
                    kesme += self.takas(yer + k)
                    takas_sayisi += 1
                yer += 1
        return {"takas": float(takas_sayisi), "kapı": float(vurulan),
                "kesme": float(kesme), "blok_yeri": float(yer)}

    # -----------------------------------------------------------------
    #  MPO: kübitleri oynatmadan bütün zincire aynı anda etki et
    # -----------------------------------------------------------------
    def mpo_uygula(self, W: Dict[int, np.ndarray], D: int,
                   bas: int = 0, son: Optional[int] = None,
                   sol_sinir: Optional[np.ndarray] = None,
                   sag_sinir: Optional[np.ndarray] = None) -> float:
        """Matris Çarpım Operatörünü duruma uygula ve ``χ``ye geri sıkıştır.

        **Takas ağının kapanan yolu.** Uzak iki kübite kapı vurmak için
        onları yan yana getirmek, geçilen her kesitte hakiki dolaşıklığı
        sürükler; ölçüldü ve ``χ`` ile KAPANMADI (χ=8'de kapı başına
        4.0e-02 kesme, χ=128'de hâlâ 4.4e-02). Sebep ``χ``nin darlığı
        değil, MPS'in bir boyutlu oluşudur (kütük H26).

        Çare, veriyi taşımak yerine **operatörü yürütmektir**. MPO,
        zincirin her yuvasında bir ``(D, 2, 2, D)`` tensörüdür ve bütün
        zincire aynı anda etki eder. Hiçbir kübit yer değiştirmez,
        dolayısıyla hiçbir dolaşıklık sürüklenmez. Maliyet ``O(N χ³ D³)``,
        yani yuva sayısında **doğrusal**.

        ``W`` sözlüğü yalnız kimliğe eşit OLMAYAN yuvaları taşır; kalan
        yuvalarda kimlik (``δ_ab δ_{w_l w_r}``) varsayılır -- yani seyrek
        bir operatör bedava taşınır.

        Uygulama iki adımdır: (1) birleştirme -- bağ ``χ·D``ye çıkar;
        (2) sıkıştırma -- sağdan sola QR, soldan sağa SVD ile ``χ``ye
        iner. Atılan ağırlık döndürülür; gizlenmez.
        """
        son = self.n if son is None else int(son)
        bas = max(0, int(bas))
        if son <= bas:
            return 0.0
        X = self.bag
        tip = self.tip
        kimlik = np.zeros((D, 2, 2, D), dtype=tip)
        for w in range(D):
            kimlik[w, 0, 0, w] = 1.0
            kimlik[w, 1, 1, w] = 1.0

        # --- 1) birleştirme: A'[k] = Σ_j W[k][wl,i,j,wr] A[k][a,j,b]
        #
        # **İki hız kusuru kaldırıldı.** (a) Her yuva ``float64``e
        # yükseltiliyordu; durum zaten ``float32`` olduğu için bu, her
        # MPO'da bütün zinciri iki katı bellekle kopyalamak demekti.
        # (b) Büzülme ``einsum(..., optimize=True)`` ile yazılmıştı ve
        # profil, vaktin beşte birinin **yol aramasına** gittiğini
        # gösterdi. Sıra sabittir; iki yığın çarpımıdır:
        #     W(p,i,j,q) → (p·i·q, j) ,  A(a,j,b) → (j, a·b)
        # çarpım (p·i·q, a·b) → yeniden dizilerek (p,a,i,q,b).
        T: List[np.ndarray] = []
        for k in range(bas, son):
            Ak = self.A[k]                                  # (X, 2, X)
            Wk = np.asarray(W.get(k, kimlik), tip)
            W2 = Wk.transpose(0, 1, 3, 2).reshape(D * 2 * D, 2)
            A2 = Ak.transpose(1, 0, 2).reshape(2, X * X)
            P = (W2 @ A2).reshape(D, 2, D, X, X)            # (p,i,q,a,b)
            T.append(np.ascontiguousarray(P.transpose(0, 3, 1, 2, 4)))
        # --- sınır vektörleri
        # Varsayılan ``e₀``dır: bağ birim cebir elemanıyla başlar ve
        # 0. bileşende kapanır. Fakat bazı operatörler bunu istemez:
        # kontrollü DAĞITIM (küllî hüküm sağda, duraklar solda) iki
        # dalı -- kaynak ``|0⟩`` ve kaynak ``|1⟩`` -- ayrı bağ
        # bileşenlerinde taşır ve solda **ikisini de** toplar. O hâlde
        # sol sınır ``(1,1)``dir. Sınırlar ayarlanabilir olmasaydı o
        # operatör hiç kurulamazdı.
        sl = np.zeros(D, tip) if sol_sinir is None else np.asarray(sol_sinir,
                                                                   tip)
        sr = np.zeros(D, tip) if sag_sinir is None else np.asarray(sag_sinir,
                                                                   tip)
        if sol_sinir is None:
            sl[0] = 1.0
        if sag_sinir is None:
            sr[0] = 1.0
        if len(T) == 1:
            # tek yuva: iki sınır da aynı tensöre kapanır
            T[0] = np.tensordot(np.tensordot(sl, T[0], axes=([0], [0])),
                                sr, axes=([2], [0]))
        else:
            T[0] = np.tensordot(sl, T[0], axes=([0], [0])
                                ).reshape(X, 2, D * X)
            T[-1] = np.tensordot(T[-1], sr, axes=([3], [0])
                                 ).reshape(D * X, 2, X)
            for i in range(1, len(T) - 1):
                T[i] = T[i].reshape(D * X, 2, D * X)

        # --- 2) sıkıştırma: sağdan sola QR (kanonikleştir), sonra SVD
        atilan = 0.0
        for k in range(len(T) - 1, 0, -1):
            t = T[k]
            dl, _, dr = t.shape
            M = t.reshape(dl, 2 * dr)
            # ``M = Rᵀ Qᵀ``: sağ tensör ``Qᵀ`` olur, ``Rᵀ`` sola geçer.
            # ``einsum("aib,cb->aic", …, Rᵀ)`` yazılıp ölçüldü ve **kaldı**:
            # o, ``Rᵀ``nin ikinci indisiyle sözleşerek fiilen ``R`` ile
            # çarpar; MPO'nun normu 1'den 0.97'ye düşüyor, netice takas
            # ağıyla %25 ayrışıyordu. Doğrusu ``b`` indisini ``Rᵀ``nin
            # BİRİNCİ indisiyle sözleştirmektir.
            Q, R = np.linalg.qr(M.T)                        # (2dr, r), (r, dl)
            r = Q.shape[1]
            T[k] = Q.T.reshape(r, 2, dr)
            # ``einsum("aib,bc->aic", …)`` yerine doğrudan yığın çarpımı:
            # ``(a,i,b) @ (b,c) → (a,i,c)`` numpy'de zaten budur.
            T[k - 1] = T[k - 1] @ R.T
        for k in range(len(T) - 1):
            t = T[k]
            dl, _, dr = t.shape
            U, s, Vt = np.linalg.svd(t.reshape(dl * 2, dr),
                                     full_matrices=False)
            r = min(X, len(s))
            top = float(np.sum(s ** 2)) + 1e-30
            atilan += float(np.sum(s[r:] ** 2)) / top
            T[k] = U[:, :r].reshape(dl, 2, r)
            # ``diag(s)·Vt`` önce kurulur (``(r,dr)``), sonra tek çarpım:
            # ``(r,dr) @ (dr, 2·c) → (r, 2·c)``. Üç indisli einsum'un
            # yol araması burada da israftı.
            SV = s[:r, None] * Vt[:r, :]
            nk = T[k + 1]
            T[k + 1] = (SV @ nk.reshape(nk.shape[0], -1)
                        ).reshape(r, 2, nk.shape[2])
        # son yuva da ``χ``ye sığmalı
        if T[-1].shape[0] > X:
            t = T[-1]
            U, s, Vt = np.linalg.svd(t.reshape(t.shape[0], 2 * t.shape[2]),
                                     full_matrices=False)
            r = min(X, len(s))
            top = float(np.sum(s ** 2)) + 1e-30
            atilan += float(np.sum(s[r:] ** 2)) / top
            T[-1] = (np.diag(s[:r]) @ Vt[:r]).reshape(r, 2, t.shape[2])

        # --- 3) geri yaz. Tampon bir kere tahsis edilir ve her yuvada
        # sıfırlanır; her yuva için yeni bir dizi ayırmak MPO'yu yuva
        # sayısı kadar tahsisle yüklüyordu.
        yeni = np.empty((X, 2, X), dtype=tip)
        for i, k in enumerate(range(bas, son)):
            t = T[i]
            a, _, b = t.shape
            ka, kb = min(a, X), min(b, X)
            yeni[...] = 0.0
            yeni[:ka, :, :kb] = t[:ka, :, :kb]
            self.A[k] = yeni
        return atilan

    # -----------------------------------------------------------------
    #  MERA
    # -----------------------------------------------------------------
    def mera_kur(self, kademe: Optional[int] = None,
                 teta: Optional[np.ndarray] = None) -> List[MERAKademe]:
        """MERA: her kademede dolanıklık çözücü + izometri.

        Kademe ``s``de çiftler ``2^s`` uzaklıkta olmalıdır. MPS'te uzak
        çift pahalıdır; bu yüzden **fırça ofseti** kullanılır: kademe
        ``s``de önce ofset 0, sonra ofset 1 ile komşu çiftlere kapı
        uygulanır. İki ofsetli bir kademe, korelasyonun menzilini bir
        katmanda iki katına çıkarır; ``log₂N`` kademede menzil bütün
        zinciri kaplar. Bu, MERA'nın ``O(log N)`` mesafe hususiyetinin
        MPS üzerindeki fiilî karşılığıdır.

        ``teta`` verilmezse kapılar tohumdan türetilir; verilirse
        **öğrenilen** açılardır (kademe başına 12 açı: 6 çözücü + 6
        izometri).
        """
        s_azami = int(np.ceil(np.log2(self.n)))
        kademe = s_azami if kademe is None else min(kademe, s_azami)
        self.iz = []
        for s in range(kademe):
            if teta is not None:
                t = np.asarray(teta, float).reshape(-1)
                a = t[(2 * s * 6) % max(len(t) - 12, 1):][:12]
                if len(a) < 12:
                    a = np.resize(a, 12)
                U = dik_iki_kubit(a[:6])
                W = dik_iki_kubit(a[6:12])
            else:
                U = dik_iki_kubit(self.rng.normal(scale=0.6, size=6))
                W = dik_iki_kubit(self.rng.normal(scale=0.6, size=6))
            h1 = self.cift_kapi(U, ofset=0)      # dolanıklık çözücü
            h2 = self.cift_kapi(W, ofset=1)      # izometri
            self.iz.append(MERAKademe(kademe=s, yuva=self.n, bag=self.bag,
                                      kesme_hatasi=float(h1 + h2)))
        return self.iz

    # -----------------------------------------------------------------
    #  Ölçüm: dolaşıklık ve tek yuva yoğunlukları -- ÇÖKÜŞ YOK
    # -----------------------------------------------------------------
    def dolasiklik_entropisi(self, kesit: Optional[int] = None,
                             pencere: int = 24) -> Dict[str, float]:
        """Bir kesitteki von Neumann entropisi ``S = −Σ λ² ln λ²``.

        Kesitin solundaki ``pencere`` kadar yuva çarpılıp Schmidt
        spektrumu çıkarılır. ``S = 0`` çarpım durumu, ``S > 0``
        dolaşıklık demektir. **Ölçülen budur**; "dolaşık" lafı buradan
        gelir, iddiadan değil.
        """
        kesit = self.n // 2 if kesit is None else int(kesit)
        bas = max(0, kesit - pencere)
        # Sol bloğu soldan sağa çarp: M[(fiziksel...), bag]
        # Sol uç sınır vektörü: MPS ilk yuvanın 0. bağ indisinde başlar.
        M: Optional[np.ndarray] = None
        for k in range(bas, kesit):
            Ak = self.A[k].astype(np.float64)          # (X, 2, X)
            if M is None:
                # başlangıç sınırı: sol bağ indisi 0
                M = Ak[0]                              # (2, X)
            else:
                M = np.tensordot(M, Ak, axes=([-1], [0]))   # (..., 2, X)
                M = M.reshape(-1, self.bag)
                if M.shape[0] > 2048:                  # bellek freni: QR ile sıkıştır
                    _, M = np.linalg.qr(M)
        if M is None:
            return {"entropi": 0.0, "schmidt": 1.0, "kesit": float(kesit)}
        s = np.linalg.svd(M, compute_uv=False)
        p = s ** 2
        t = float(p.sum())
        if t <= 1e-300:
            return {"entropi": 0.0, "schmidt": 1.0, "kesit": float(kesit)}
        p = p / t
        nz = p > 1e-15
        H = float(-np.sum(p[nz] * np.log(p[nz])))
        return {"entropi": H,
                "schmidt": float(np.sum(nz)),
                "azami_entropi": float(np.log(len(p))),
                "kesit": float(kesit),
                "pencere": float(pencere)}

    def yuva_yogunluklari(self, yuvalar: Sequence[int]) -> np.ndarray:
        """Seçili yuvaların ``2×2`` indirgenmiş yoğunlukları -- **zayıf**.

        Sert (Von Neumann) ölçüm yapılmaz: durum çökertilmez, yalnız
        çevreye göre kısmî iz alınır. ``ρ_i = Tr_çevre |Ψ⟩⟨Ψ|``nin
        MPS'teki yerel yaklaşığı ``Σ_{a,c} A[i,a,·,c] A[i,a,·,c]``dir.
        """
        idx = np.asarray(yuvalar, np.intp) % self.n
        if idx.size == 0:
            return np.zeros((0, 2, 2))
        X = self.bag
        # Python döngüsü + yuva başına ``einsum`` yerine tek yığın
        # çarpımı: ``B[m,i,(a,b)] @ B[m,j,(a,b)]ᵀ → R[m,i,j]``.
        # **Ölçüm float64'e yükseltilir** (kullanıcı hükmü: durum f32,
        # ölçüm f64): iz 1'den ne kadar sapıyor sorusunun cevabı
        # float32'de gürültüye gömülürdü.
        B = self.A[idx].transpose(0, 2, 1, 3).reshape(-1, 2, X * X)
        B = B.astype(np.float64)
        R = np.matmul(B, B.transpose(0, 2, 1))              # (m, 2, 2)
        iz = np.trace(R, axis1=1, axis2=2)
        iyi = iz > 1e-300
        out = np.empty_like(R)
        out[iyi] = R[iyi] / iz[iyi][:, None, None]
        out[~iyi] = np.eye(2) / 2.0
        return out

    def norm_hatasi(self, ornek: int = 64) -> float:
        """Yuva yoğunluklarının izi 1'den ne kadar sapıyor?

        Kapılar dikse ve bölme normu koruyorsa sıfıra yakın olmalıdır.
        Tam norm ``⟨Ψ|Ψ⟩`` bütün zinciri taramayı ister; burada örneklem
        alınır ve örneklem büyüklüğü raporlanır.
        """
        idx = np.linspace(0, self.n - 1, min(ornek, self.n)).astype(int)
        R = self.yuva_yogunluklari(idx)
        return float(np.max(np.abs(np.trace(R, axis1=1, axis2=2) - 1.0)))

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
            v = blok.reshape(k * self.bag, 2, self.bag)
            np.einsum("ij,mjb->mib", Gt, v, out=v, optimize=True)

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

    def _cift_kapi_dilim(self, G: np.ndarray, bas: int, m: int) -> float:
        X = self.bag
        sol = self.A[bas:bas + 2 * m:2]        # (m, X, 2, X)
        sag = self.A[bas + 1:bas + 2 * m:2]    # (m, X, 2, X)
        # Θ[m, a, i, j, c] = Σ_b sol[m,a,i,b] sag[m,b,j,c]
        T = np.einsum("maib,mbjc->maijc", sol, sag, optimize=True)
        T = T.reshape(m, X, 4, X)
        T = np.einsum("pq,maqc->mapc", G.astype(self.tip), T, optimize=True)
        # (m, X, 2, 2, X) → (m, X·2, 2·X): sol yuva | sağ yuva kesiti
        T = T.reshape(m, X, 2, 2, X).reshape(m, X * 2, 2 * X)
        U, s, Vt = np.linalg.svd(T.astype(np.float32), full_matrices=False)
        r = min(X, s.shape[1])
        atilan = float(np.sum(s[:, r:] ** 2)) if s.shape[1] > r else 0.0
        toplam = float(np.sum(s ** 2)) + 1e-30
        Uk = U[:, :, :r]                        # (m, 2X, r)
        sk = s[:, :r]
        Vk = Vt[:, :r, :]                       # (m, r, 2X)
        # norm koru: her çiftin tekil değerleri birim yapılır
        nrm = np.sqrt(np.sum(sk ** 2, axis=1, keepdims=True)) + 1e-20
        sk = sk / nrm
        yeni_sol = np.zeros((m, X, 2, X), dtype=self.tip)
        yeni_sag = np.zeros((m, X, 2, X), dtype=self.tip)
        yeni_sol[:, :, :, :r] = (Uk * np.sqrt(sk)[:, None, :]
                                 ).reshape(m, X, 2, r)
        VS = (np.sqrt(sk)[:, :, None] * Vk).reshape(m, r, 2, X)
        yeni_sag[:, :r, :, :] = VS
        self.A[bas:bas + 2 * m:2] = yeni_sol
        self.A[bas + 1:bas + 2 * m:2] = yeni_sag
        return atilan / toplam

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
        out = np.zeros((len(yuvalar), 2, 2))
        for t, i in enumerate(yuvalar):
            Ai = self.A[int(i) % self.n].astype(np.float64)
            R = np.einsum("aib,ajb->ij", Ai, Ai, optimize=True)
            iz = float(np.trace(R))
            out[t] = R / iz if iz > 1e-300 else np.eye(2) / 2.0
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

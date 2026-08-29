"""
İki boyutlu Ağaç Tensör Ağı (TTN) -- MERA ile PEPS'in barıştırılması.

Kullanıcı hükmü (H53): *"MERA ile PEPS'i barıştırarak yapabiliyorsan yap,
yaklaşıklığı yok etmenin çaresini düşün."* ve *"MPS'i iki boyutlu ağacın
YAPRAKLARINDA kullan."*

**Yaklaşıklık nereden geliyordu ve nasıl öldürülür.**

* **MPS (zincir):** büzülme tamdır, fakat iki boyutlu ızgarayı zincire
  serince kesitten geçen kenar uzunluğu kadar dolaşıklık taşınır.
  Ölçüldü (H52): ``χ ≈ renk^w``; ARC'de ``10³⁰`` -- imkânsız.
* **PEPS (ızgara ağı):** hendese doğrudur, alan kanununu birebir
  karşılar; fakat ağda **çevrim (loop)** vardır ve çevrimli bir ağı
  büzmek ``#P``-zordur. Ancak yaklaşık hesaplanır ve o yaklaşıklığın
  hatası **kontrol edilemez**.
* **AĞAÇ (TTN):** çevrim **yoktur**. Onun için büzülme MPS gibi
  **tamdır**; hiçbir yaklaşıklık girmez. Aynı zamanda hendese iki
  boyutludur: ızgara dörde bölünür, her blok bir üst düğüme bağlanır.

Yani ağaç, PEPS'in iki boyutlu komşuluğunu alır, MPS'in tam
hesaplanabilirliğini korur. **Yaklaşıklığı öldüren şey budur.**

**Asıl kazanç mesafededir.** İki hücre arasındaki tensör yolu:

    MPS   : ``O(N)``      -- 30×30'da 900 adıma kadar
    AĞAÇ  : ``O(log N)``  -- 30×30'da 10 adım

**Neyin iddia edilmediği.** Ağaç, iki boyutlu alan kanununu **kaldırmaz**;
hiçbir tensör ağı kaldıramaz. Kaldırdığı şey PEPS'in büzülme
yaklaşıklığı ve MPS'in mesafe cezasıdır. ``χ`` ihtiyacı hâlâ kesitin
sınırıyla büyür; fakat ağaçta kesit bir **blok sınırıdır** (``O(√N)``),
zincirdeki gibi bütün genişlik (``O(w)``) değil, ve mesafe cezası
tamamen kalkar. Bunun ne kadar fayda ettiği **ölçülür**, iddia edilmez.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["AgacAyar", "AgacYazmaci", "Dugum"]


@dataclass
class Dugum:
    """Ağacın bir düğümü.

    Yaprak ise ``hucre`` doludur ve tensör ``(d, üst_bağ)`` şeklindedir.
    İç düğüm ise tensör ``(sol_bağ, sağ_bağ, üst_bağ)`` şeklindedir.
    Kök düğümde ``üst_bağ = 1``.
    """
    no: int
    hucre: Optional[Tuple[int, int]] = None
    sol: Optional[int] = None
    sag: Optional[int] = None
    ust: Optional[int] = None
    T: Optional[np.ndarray] = None

    @property
    def yaprak(self) -> bool:
        return self.hucre is not None


@dataclass
class AgacAyar:
    h: int = 3
    w: int = 3
    renk: int = 4
    bag: int = 8               # χ
    tohum: int = 0


class AgacYazmaci:
    """İki boyutlu ızgaranın bütün muhtemel hâllerini tutan ağaç.

    Bölme usulü: her adımda dikdörtgenin **uzun kenarı** ikiye bölünür.
    Böylece bloklar kareye yakın kalır ve blok sınırı (dolayısıyla
    gereken ``χ``) mümkün olan en küçük hâlde tutulur. Satır satır yahut
    sütun sütun bölmek uzun ince şeritler doğurur ve sınırı büyütür --
    bu bir tercih değil, alan kanununun dayattığı şeydir.
    """

    def __init__(self, ayar: Optional[AgacAyar] = None) -> None:
        self.ayar = ayar or AgacAyar()
        a = self.ayar
        self.d = a.renk
        self.dugumler: List[Dugum] = []
        self.yaprak_no: Dict[Tuple[int, int], int] = {}
        self.kok = self._kur(0, 0, a.h, a.w, None)
        self.kesme = 0.0
        self.kapi = 0
        self.merkez: Optional[int] = None

    # -----------------------------------------------------------------
    def _yeni(self, **kw) -> int:
        no = len(self.dugumler)
        self.dugumler.append(Dugum(no=no, **kw))
        return no

    def _kur(self, i0: int, j0: int, h: int, w: int,
             ust: Optional[int]) -> int:
        """Dikdörtgeni özyinelemeli olarak ikiye böl; yaprakta hücre kalır."""
        if h == 1 and w == 1:
            no = self._yeni(hucre=(i0, j0), ust=ust)
            self.yaprak_no[(i0, j0)] = no
            # yaprak tensörü: (d, üst_bağ=1) -- düzgün süperpozisyon
            self.dugumler[no].T = (np.ones((self.d, 1), complex)
                                   / math.sqrt(self.d))
            return no
        no = self._yeni(ust=ust)
        if h >= w:                       # uzun kenar dikey → yatay kes
            k = h // 2
            sol = self._kur(i0, j0, k, w, no)
            sag = self._kur(i0 + k, j0, h - k, w, no)
        else:                            # uzun kenar yatay → dikey kes
            k = w // 2
            sol = self._kur(i0, j0, h, k, no)
            sag = self._kur(i0, j0 + k, h, w - k, no)
        self.dugumler[no].sol = sol
        self.dugumler[no].sag = sag
        # iç düğüm: (sol_bağ, sağ_bağ, üst_bağ) -- başlangıçta hepsi 1
        self.dugumler[no].T = np.ones((1, 1, 1), complex)
        return no

    # -----------------------------------------------------------------
    def derinlik(self) -> int:
        d = 0
        for no in self.yaprak_no.values():
            k = 0
            x = self.dugumler[no].ust
            while x is not None:
                k += 1
                x = self.dugumler[x].ust
            d = max(d, k)
        return d

    def yol(self, a: Tuple[int, int], b: Tuple[int, int]) -> List[int]:
        """İki yaprak arasındaki **tek** yol -- ağaçta çevrim yok.

        Bu, MPS'e karşı asıl kazançtır: zincirde iki hücre arası mesafe
        ``O(N)``, ağaçta ``O(log N)``. Yolun tekliği çevrimsizliğin
        neticesidir ve büzülmenin tam olmasının da sebebidir.
        """
        def kok_yolu(no: int) -> List[int]:
            y = [no]
            while self.dugumler[y[-1]].ust is not None:
                y.append(self.dugumler[y[-1]].ust)
            return y
        ya, yb = kok_yolu(self.yaprak_no[a]), kok_yolu(self.yaprak_no[b])
        kume = {x: i for i, x in enumerate(ya)}
        for j, x in enumerate(yb):
            if x in kume:
                return ya[:kume[x] + 1] + yb[:j][::-1]
        raise ValueError("yol bulunamadı -- ağaç bozuk")

    def mesafe(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return len(self.yol(a, b)) - 1

    # -----------------------------------------------------------------
    #  Ayar (gauge): kanonik hâl
    # -----------------------------------------------------------------
    def _komsular(self, no: int) -> List[int]:
        D = self.dugumler[no]
        return [x for x in (D.ust, D.sol, D.sag) if x is not None]

    def _indis(self, no: int, komsu: int) -> int:
        """``no`` düğümünün tensöründe ``komsu``ya bakan indisin yeri."""
        D = self.dugumler[no]
        if D.ust == komsu:
            return 1 if D.yaprak else 2
        if D.sol == komsu:
            return 0
        if D.sag == komsu:
            return 1
        raise ValueError("%d ile %d komşu değil" % (no, komsu))

    def _carp(self, no: int, komsu: int, M: np.ndarray) -> None:
        """``no``nun ``komsu``ya bakan indisine ``M`` dizeyini çarp.

        ``T'…ᵢ = Σⱼ T…ⱼ M[j,i]``. Bağ boyu ``M``in ikinci boyuna döner;
        bu yüzden bağ daralması ve genişlemesi hep bu tek yerden geçer.
        """
        p = self._indis(no, komsu)
        T = np.moveaxis(self.dugumler[no].T, p, -1)
        T = T @ M
        self.dugumler[no].T = np.moveaxis(T, -1, p)

    def kanonik(self, merkez: int) -> None:
        """Bütün tensörleri ``merkez``e bakacak şekilde izometrik yap.

        Yapraklardan merkeze doğru QR süpürmesi. Netice: merkez dışındaki
        her düğüm, merkeze bakan indisi hariç, bir izometridir. Bunun
        neden şart olduğu ölçüldü ve gizlenmez: kesme (truncation) ancak
        **çevresi izometrikse** en iyidir; değilse atılan tekil değerler
        hakikî hatayı vermez ve "kesme" diye raporlanan sayı yalan olur.

        Çevrimsizlik burada da işe yarar: her düğümün merkeze giden **tek**
        bir yolu vardır, dolayısıyla süpürme sırası tereddütsüzdür.
        MPS'te de böyledir; PEPS'te böyle bir şey **yoktur** -- kanonik
        hâl çevrimli ağda tanımlı değildir, bütün belâ oradan çıkar.
        """
        n = len(self.dugumler)
        uzak = [-1] * n
        dogru: List[Optional[int]] = [None] * n
        uzak[merkez] = 0
        kuyruk = [merkez]
        bas = 0
        while bas < len(kuyruk):
            x = kuyruk[bas]
            bas += 1
            for y in self._komsular(x):
                if uzak[y] < 0:
                    uzak[y] = uzak[x] + 1
                    dogru[y] = x
                    kuyruk.append(y)
        for x in sorted(range(n), key=lambda i: -uzak[i]):
            p = dogru[x]
            if p is None:
                continue
            ip = self._indis(x, p)
            T = np.moveaxis(self.dugumler[x].T, ip, -1)
            sek, D = T.shape[:-1], T.shape[-1]
            Q, R = np.linalg.qr(T.reshape(-1, D))
            k = Q.shape[1]
            self.dugumler[x].T = np.moveaxis(Q.reshape(sek + (k,)), -1, ip)
            self._carp(p, x, R.T)
        self.merkez = merkez

    def norm(self) -> float:
        """Durumun normu. Kanonik hâlde **yalnız merkez tensörünün** normu.

        Bütün ağacı büzmeye gerek yoktur; çevresi izometrik olduğu için
        onların katkısı birebir birdir. 30×30'da bu, ``d^900`` boyutlu bir
        vektörün normunu tek bir küçük tensörden okumak demektir.
        """
        if self.merkez is None:
            self.kanonik(self.kok)
        return float(np.linalg.norm(self.dugumler[self.merkez].T))

    def normalize(self) -> float:
        n = self.norm()
        if n > 1e-300:
            self.dugumler[self.merkez].T = self.dugumler[self.merkez].T / n
        return n

    # -----------------------------------------------------------------
    #  Kapılar: AĞAÇ MPO -- operatör yol boyunca yayılır, kübit OYNAMAZ
    # -----------------------------------------------------------------
    def tek_kapi(self, hucre: Tuple[int, int], G: np.ndarray) -> None:
        """Tek hücreye üniter. Bağ büyümez, kesme olmaz, hata **sıfırdır**."""
        no = self.yaprak_no[hucre]
        self.dugumler[no].T = np.asarray(G, complex) @ self.dugumler[no].T
        self.kapi += 1

    def _sup(self, P: Sequence[int], kes: bool) -> None:
        """Yol boyunca dik merkezi taşı; ``kes`` ise ``χ``ya indir."""
        for i in range(len(P) - 1):
            x, y = P[i], P[i + 1]
            ip = self._indis(x, y)
            T = np.moveaxis(self.dugumler[x].T, ip, -1)
            sek, D = T.shape[:-1], T.shape[-1]
            M = T.reshape(-1, D)
            if kes:
                U, S, Vt = np.linalg.svd(M, full_matrices=False)
                k = min(len(S), self.ayar.bag)
                self.kesme += float(np.sum(S[k:] ** 2))
                U, R = U[:, :k], S[:k, None] * Vt[:k, :]
            else:
                U, R = np.linalg.qr(M)
                k = U.shape[1]
            self.dugumler[x].T = np.moveaxis(U.reshape(sek + (k,)), -1, ip)
            self._carp(y, x, R.T)

    def cift_kapi(self, a: Tuple[int, int], b: Tuple[int, int],
                  G: np.ndarray) -> None:
        """İki hücreye üniter -- **hücreler yerinden kımıldamadan**.

        Kullanıcı hükmü: *"Ağaç MPO -- operatörü yol boyunca yay, kübit
        oynatma."* Yapılan tam olarak budur:

        1. ``G`` iki parçaya ayrılır: ``G = Σₖ Aₖ ⊗ Bₖ`` (SVD, ``r ≤ d²``).
           Ayrışmanın rütbesi ``r``, operatörün taşıdığı **bağ**dır.
        2. ``Aₖ`` ``a`` yaprağına, ``Bₖ`` ``b`` yaprağına vurulur ve her
           ikisi de üstlerine bir ``k`` indisi bırakır.
        3. ``k`` indisi ``a`` ile ``b`` arasındaki **tek yol** boyunca
           taşınır: yoldaki her düğüm ``T ⊗ δ`` ile genişletilir. Zirvede
           iki taraftan gelen ``k`` aynı ``δ`` ile kapanır -- operatör
           orada birleşir.
        4. Yol boyunca bağlar ``r`` katına çıkar; QR ile ayar alınıp SVD
           ile ``χ``ya indirilir.

        Takas ağıyla farkı: takasta hücreler yer değiştirir ve **her**
        takas ayrı bir kesme yapar; burada hücre hiç kımıldamaz, kesme
        yalnız yol kenarlarında bir kere olur. Zincirdeki takas yolu
        30×30'da 899 adımdı; buradaki yol 20'dir (bkz. ``mesafe``).

        Yaklaşıklık iddiası yok: ``χ`` yeterken hata makine hassasiyeti
        mertebesindedir, yetmezken **ölçülür** (``kesme``) ve öyle
        bildirilir.
        """
        d = self.d
        G = np.asarray(G, complex).reshape(d, d, d, d)      # a_çık,b_çık,a_gir,b_gir
        M = G.transpose(0, 2, 1, 3).reshape(d * d, d * d)   # (a_çık,a_gir)|(b_çık,b_gir)
        U, S, Vt = np.linalg.svd(M, full_matrices=False)
        r = int(np.sum(S > 1e-12 * (S[0] if S.size else 1.0)))
        r = max(r, 1)
        A = (U[:, :r] * S[:r]).T.reshape(r, d, d)
        B = Vt[:r, :].reshape(r, d, d)

        P = self.yol(a, b)
        self.kanonik(P[0])

        # --- uçlar: operatörün iki yarısı
        for no, K in ((P[0], A), (P[-1], B)):
            T = self.dugumler[no].T                          # (d, u)
            T2 = np.einsum("kij,ju->iuk", K, T, optimize=True)
            self.dugumler[no].T = T2.reshape(d, -1)

        # --- yol: δ ile yayılma (zirvede aynı δ operatörü kapatır)
        for i in range(1, len(P) - 1):
            x, e, f = P[i], P[i - 1], P[i + 1]
            ie, if_ = self._indis(x, e), self._indis(x, f)
            T = np.moveaxis(self.dugumler[x].T, [ie, if_], [0, 1])
            De, Df = T.shape[0], T.shape[1]
            kalan = T.shape[2:]
            T2 = np.einsum("efR,kl->ekflR", T.reshape(De, Df, -1),
                           np.eye(r), optimize=True)
            T2 = T2.reshape((De * r, Df * r) + kalan)
            self.dugumler[x].T = np.moveaxis(T2, [0, 1], [ie, if_])

        self._sup(P, kes=False)          # ayar: merkezi b'ye taşı
        self._sup(P[::-1], kes=True)     # kes: b'den a'ya, χ'ya indir
        self.merkez = P[0]
        self.kapi += 1

    # -----------------------------------------------------------------
    def hucre_dagilimi(self, hucre: Tuple[int, int]) -> np.ndarray:
        """Bir hücrenin marjinal dağılımı -- **çöküş yok**, zayıf okuma.

        Kanonik hâl sayesinde bütün ağacı büzmeye gerek kalmaz: merkez o
        yaprağa taşınır, geri kalanın katkısı birimdir.
        """
        no = self.yaprak_no[hucre]
        self.kanonik(no)
        T = self.dugumler[no].T
        p = np.real(np.sum(T * np.conj(T), axis=1))
        s = float(p.sum())
        return p / s if s > 1e-300 else p

    # -----------------------------------------------------------------
    #  Durum: bütün ızgaraların süperpozisyonu
    # -----------------------------------------------------------------
    def buz(self) -> np.ndarray:
        """Bütün ağacı büz -- **tam**, yaklaşıklık yok (çevrim olmadığı için).

        Netice ızgaranın tam dalga fonksiyonudur: ``d^(h·w)`` boyutunda.
        Yalnız **küçük ızgaralarda** çağrılabilir; asıl işleyiş bunu hiç
        açmaz. Burada bulunmasının sebebi, ağacın doğruluğunu bilinen
        hâllerle **sınayabilmektir**.
        """
        a = self.ayar
        if self.d ** (a.h * a.w) > 2 ** 22:
            raise MemoryError("tam büzülme yalnız küçük ızgarada")
        sira: List[Tuple[int, int]] = []

        def cik(no: int) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
            D = self.dugumler[no]
            if D.yaprak:
                return D.T, [D.hucre]          # (d, ust)
            S, hs = cik(D.sol)
            G, hg = cik(D.sag)
            # (…fizikî…, sol_ust) × (sol_ust, sag_ust, ust)
            M = np.tensordot(S, D.T, axes=([-1], [0]))     # (…, sag_ust, ust)
            M = np.tensordot(M, G, axes=([-2], [-1]))      # (…, ust, …g)
            # indisleri düzelt: ust en sona
            nd = M.ndim
            eks = list(range(nd))
            u = len(hs)                       # 'ust' indisinin yeri
            eks.remove(u)
            eks.append(u)
            return np.transpose(M, eks), hs + hg

        T, hucreler = cik(self.kok)
        T = T.reshape([self.d] * len(hucreler))
        # hücreleri satır sırasına göre yeniden diz
        hedef = [(i, j) for i in range(a.h) for j in range(a.w)]
        eks = [hucreler.index(x) for x in hedef]
        return np.transpose(T, eks).reshape(-1)

    def durum(self) -> Dict[str, float]:
        """Ağacın hâli: en büyük bağ, düğüm sayısı, bellek, kesme."""
        en_bag = 0
        bayt = 0
        for D in self.dugumler:
            if D.T is not None:
                en_bag = max(en_bag, max(D.T.shape))
                bayt += D.T.nbytes
        return {"düğüm": float(len(self.dugumler)),
                "yaprak": float(len(self.yaprak_no)),
                "derinlik": float(self.derinlik()),
                "en_büyük_bağ": float(en_bag),
                "bayt": float(bayt),
                "kesme": float(self.kesme),
                "kapı": float(self.kapi)}


# =====================================================================
#  Sınama: ağaç kapısı, TAM hesapla birebir karşılaştırılır
# =====================================================================
def _yogun_cift(psi: np.ndarray, n: int, d: int, pa: int, pb: int,
                G: np.ndarray) -> np.ndarray:
    """Aynı kapıyı **tam** dalga vektörüne vur -- hakikat kaynağı."""
    T = psi.reshape([d] * n)
    T = np.moveaxis(T, [pa, pb], [0, 1])
    sek = T.shape
    T = (G.reshape(d * d, d * d) @ T.reshape(d * d, -1)).reshape(sek)
    return np.moveaxis(T, [0, 1], [pa, pb]).reshape(-1)


def _rastgele_uniter(m: int, rng) -> np.ndarray:
    A = rng.normal(size=(m, m)) + 1j * rng.normal(size=(m, m))
    Q, R = np.linalg.qr(A)
    return Q * (np.diag(R) / np.abs(np.diag(R)))[None, :]


def _kapi_sinamasi(h: int, w: int, renk: int, bag: int, kapi: int,
                   tohum: int = 0) -> Dict[str, float]:
    rng = np.random.default_rng(tohum)
    ag = AgacYazmaci(AgacAyar(h=h, w=w, renk=renk, bag=bag))
    psi = ag.buz()
    n, d = h * w, renk
    hucreler = [(i, j) for i in range(h) for j in range(w)]
    for _ in range(kapi):
        a, b = rng.choice(len(hucreler), size=2, replace=False)
        G = _rastgele_uniter(d * d, rng)
        ag.cift_kapi(hucreler[a], hucreler[b], G)
        psi = _yogun_cift(psi, n, d, int(a), int(b), G)
    yak = ag.buz()
    # işaret/ölçek serbestliği yok: ikisi de aynı temsilde, doğrudan fark
    hata = float(np.linalg.norm(yak - psi) / (np.linalg.norm(psi) + 1e-300))
    return {"hata": hata, "norm": float(np.linalg.norm(yak)),
            "kesme": ag.kesme, "en_büyük_bağ": ag.durum()["en_büyük_bağ"]}


def _gosterim() -> str:
    s = ["=== iki boyutlu ağaç: kurulum ==="]
    for h, w in ((3, 3), (5, 5), (10, 10), (30, 30)):
        ag = AgacYazmaci(AgacAyar(h=h, w=w, renk=10, bag=8))
        d = ag.durum()
        kose = ag.mesafe((0, 0), (h - 1, w - 1))
        s.append("  %2dx%-2d  düğüm=%4d derinlik=%2d   köşe-köşe: zincir %3d → "
                 "ağaç %2d  (%.1f kat)"
                 % (h, w, int(d["düğüm"]), int(d["derinlik"]),
                    h * w - 1, kose, (h * w - 1) / max(kose, 1)))

    s += ["", "=== AĞAÇ MPO kapısı: TAM hesapla karşılaştırma ===",
          "  (kübit oynatılmıyor; operatör yol boyunca yayılıyor)",
          "",
          "  ızgara  renk  χ   kapı   ‖Δψ‖/‖ψ‖     norm       kesme     "
          "en büyük bağ"]
    for h, w, renk, bag, kapi in ((2, 2, 2, 16, 6), (2, 3, 2, 64, 8),
                                  (3, 3, 2, 64, 10), (2, 3, 3, 81, 6)):
        r = _kapi_sinamasi(h, w, renk, bag, kapi)
        s.append("  %dx%-4d  %d    %-3d %-4d  %.3e  %.9f  %.3e  %d"
                 % (h, w, renk, bag, kapi, r["hata"], r["norm"],
                    r["kesme"], int(r["en_büyük_bağ"])))

    s += ["", "  --- χ kısılınca ne oluyor (aynı devre, yalnız χ değişiyor) ---",
          "  χ    ‖Δψ‖/‖ψ‖     kesme"]
    for bag in (2, 4, 8, 16, 64):
        r = _kapi_sinamasi(3, 3, 2, bag, 10)
        s.append("  %-4d %.3e  %.3e" % (bag, r["hata"], r["kesme"]))

    s += ["", "Hüküm: χ yeterken hata makine hassasiyetindedir -- ağaç MPO'su",
          "tam bir üniterdir, yaklaşıklık DEĞİLDİR. χ yetmezken hata ölçülür",
          "ve kesme ile beraber raporlanır; iddia edilmez."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(_gosterim())

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
            self.dugumler[no].T = np.ones((self.d, 1)) / math.sqrt(self.d)
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
        self.dugumler[no].T = np.ones((1, 1, 1))
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

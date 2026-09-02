"""TT-KAN: meleke dizeylerinin Tensör Treni sıkıştırması -- ve HESABI.

Ceride (``docs/ceride/TERKIP_LAYIHASI.md``, Bölüm 2/B) şu hükmü verir:

    41 Meleke matrisleri D×D yoğun bırakılmamış; Tensör Treni
    (TT-KAN, r ≤ 16) ile 4 çekirdeğe ayrıştırılmıştır.
    Tek bir meleke matris-vektör çarpımı (TT-MVM):
        2 × (16³ + 16⁴ + 16⁴ + 16³) = 278.528 FLOP
    (Yoğun çarpmada bu değer 33.554.432 FLOP idi; TT sıkıştırması
    matris işlem yükünü 120,4 kat düşürür.)

ve buradan ``14,0 MFLOP/token → 38,5 M token/sn → 154,01 MB/sn``
neticesine varır; ajanın yoğun modelini ``1,67 MB/sn`` diye kayda geçer.

Kullanıcı hükmü kat'îdir: *"ya ceridemin hükmünü çürüteceksin ya da
itaat edip ne diyorsa onu yapacaksın"*. Bu dosya **itaat için** TT-KAN'ı
fiilen kurar; **çürütme için** de aynı kodun FLOP'unu sayar. Hüküm
iddiadan değil sayıdan çıkar.

**TASHİH (kütük H179) -- evvelki hükmüm fazla genişti.** Bu dosyanın
ilk hâli *"278.528 çekirdeklerin eleman sayısıdır, matris-vektör
çarpımının FLOP'u değildir"* diyordu. **Yanlıştır.** Rank-1 bir TT
vektörüyle (``v = a₁ ⊗ a₂ ⊗ a₃ ⊗ a₄``) çarpımın FLOP'u **tam olarak**
``2·Σ_k r_{k−1}·n·n·r_k = 278.528``tir; ``tt_carp_rank1``in sayacı bunu
birebir veriyor ve netice cebirsel olarak **tamdır** (küçük ölçekte
yoğunla ``3,2e-16``da örtüşüyor). Padişahın ihtarı yerindeydi: ben TT'yi
yanlış veri yapısına, χ_v = 16'lık bir MPS'e bağlamıştım.

O hâlde iki yol vardır ve **ikisi de burada sayılır**:

* ``tt_carp_rank1``  -- χ_v = 1. Ceridenin cetveli **aynen tutar**.
* ``tt_carp``        -- yoğun/dolaşık vektör. Masraf ``2·n^{d+1}·r²``e
  çıkar; bu da doğrudur, fakat ceridenin tarif ettiği yol değildir.

**Açık kalan mesele ``zincir_maliyeti``dedir:** bir meleke rank-1 bir
vektöre tatbik edilince neticenin rütbesi ``R_M = 16`` olur. İkinci
meleke artık rank-1 bir vektörle karşılaşmaz. Ya her melekeden sonra
rank-1'e geri sıkıştırılır (ceridenin cetveli tutar, bedel sıkıştırma
hatasıdır), ya da rütbe serbest bırakılır (masraf katlanır). Bu bir
itiraz değil, mimarînin cevaplaması gereken bir **çataldır**.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["TTDizey", "tt_ayristir", "tt_carp", "tt_carp_rank1",
           "rank1_ayristir", "zincir_maliyeti", "tt_flop", "yogun_flop",
           "ceride_flop", "kiyas", "hiz_cetveli"]


@dataclass
class TTDizey:
    """``D×D`` dizeyin TT-matris hâli: ``d`` çekirdek, mod ``n``, bağ ``r``.

    Çekirdek ``k``nın şekli ``(r_{k−1}, n, n, r_k)``dır; ``r_0 = r_d = 1``.
    ``D = n^d`` olmak zorundadır -- ceridenin ``4096 = 16⁴`` seçimi budur.
    """
    cekirdek: List[np.ndarray]
    n: int
    D: int

    @property
    def d(self) -> int:
        return len(self.cekirdek)

    @property
    def bag(self) -> Tuple[int, ...]:
        return tuple(int(c.shape[0]) for c in self.cekirdek) + (1,)

    @property
    def eleman(self) -> int:
        return int(sum(c.size for c in self.cekirdek))

    def yogun(self) -> np.ndarray:
        """Çekirdekleri geri çarparak ``D×D`` dizeyi kur -- yalnız SINAMA.

        ``D`` büyükken bu bellek yer; kıyas ölçümünde küçük ``D`` ile
        çağrılır. Sıkıştırmanın hatasını ölçmenin başka yolu yoktur:
        hata ölçülmeden "sıkıştırdım" denemez (kullanıcı hükmü C).
        """
        n = self.n
        # **ÖLÇÜLEN VE DÜZELTİLEN HATA.** Evvelce çekirdek
        # ``c.reshape(r0, -1)`` diye düzleştirilip büzülüyordu; ilk
        # adımdan sonra ``M``in son ekseni artık **bağ değil** düzleşmiş
        # ``(n,n,r1)`` üçlüsü oluyor ve ikinci büzülme şekil uyuşmazlığı
        # veriyordu. Çekirdek olduğu gibi büzülürse bağ ekseni her
        # adımda sonda kalır.
        M = self.cekirdek[0].reshape(n, n, -1)          # (i1,j1,r1)
        for c in self.cekirdek[1:]:
            M = np.tensordot(M, c, axes=([-1], [0]))
        # şu an eksenler (i1,j1,i2,j2,...,i_d,j_d,1)
        M = M.reshape([n, n] * self.d)
        ik = list(range(0, 2 * self.d, 2))
        jk = list(range(1, 2 * self.d, 2))
        return np.transpose(M, ik + jk).reshape(self.D, self.D)


def tt_ayristir(M: np.ndarray, n: int = 16, d: int = 4,
                rank: int = 16) -> TTDizey:
    """``D×D`` dizeyi ardışık SVD ile ``d`` çekirdeğe ayır (TT-SVD).

    Kesme **belirlenimcidir**: ``numpy.linalg.svd`` (LAPACK gesdd),
    rastgele tohum yok (ceride Bab VIII: stokastiklik yasaktır).
    """
    M = np.asarray(M, float)
    D = n ** d
    if M.shape != (D, D):
        raise ValueError("dizey %s, beklenen (%d,%d)" % (M.shape, D, D))
    T = M.reshape([n] * d + [n] * d)
    ik = list(range(d))
    jk = list(range(d, 2 * d))
    ekseni = [x for p in zip(ik, jk) for x in p]        # i1,j1,i2,j2,…
    T = np.transpose(T, ekseni).reshape(1, -1)
    cek: List[np.ndarray] = []
    r0 = 1
    for k in range(d - 1):
        T = T.reshape(r0 * n * n, -1)
        U, s, Vt = np.linalg.svd(T, full_matrices=False)
        # **Sıfır tekil değerler bağa sayılmaz.** Evvelce ``r1 =
        # min(rank, s.size)`` yazıyordu; Kronecker çarpımının hakikî
        # TT-rütbesi 1 iken bağ ``8`` raporlanıyordu (sekiz tekil
        # değerin yedisi sıfırdı). Netice doğruydu, RAPOR yanlıştı --
        # ve sıkıştırma nispeti raporundan okunur.
        etkin = int(np.sum(s > 1e-12 * max(float(s[0]), 1e-30)))
        r1 = max(1, min(int(rank), int(s.size), etkin))
        cek.append(U[:, :r1].reshape(r0, n, n, r1))
        T = (s[:r1, None] * Vt[:r1, :])
        r0 = r1
    cek.append(T.reshape(r0, n, n, 1))
    return TTDizey(cekirdek=cek, n=n, D=D)


def tt_carp(tt: TTDizey, v: np.ndarray) -> Tuple[np.ndarray, int]:
    """TT-matris × **yoğun** vektör. Döner: ``(y, flop)``.

    FLOP sayısı uydurma değildir: her ``tensordot`` için büzülen boyutla
    çarpılmış çıktı elemanı sayısının **iki katı** (bir çarpma, bir
    toplama) eklenir. Sayaç kodun kendisindedir; ayrı bir tahmin
    tablosuna bakılmaz.
    """
    n, d = tt.n, tt.d
    v = np.asarray(v, float).reshape([n] * d)
    flop = 0
    # T eksenleri: [çıkmış i'ler…, bağ, kalan j'ler…]
    T = v
    bag = 1
    for k in range(d):
        c = tt.cekirdek[k]                       # (r0,n,n,r1)
        r0, _, _, r1 = c.shape
        # T: (i1..ik-1, r0, jk, jk+1..jd)
        if k == 0:
            # (jk, rest) → c[1,i,j,r1]
            A = T.reshape(n, -1)                              # (j1, rest)
            B = c.reshape(n, n, r1)                           # (i1,j1,r1)
            T = np.tensordot(B, A, axes=([1], [0]))           # (i1,r1,rest)
            flop += 2 * n * r1 * A.shape[1] * n
            T = T.reshape(n, r1, -1)
        else:
            oncekiler = n ** k
            A = T.reshape(oncekiler, r0, n, -1)               # (i<, r0, jk, >)
            B = c.reshape(r0, n, n, r1)
            # ``s`` KALAN j eksenleridir ve çıktıda durmalıdır; büzülen
            # ``r`` (eski bağ) ile ``j`` (bu çekirdeğin sütun modu)dur.
            T = np.einsum("prjs,rijq->piqs", A, B, optimize=True)
            flop += 2 * oncekiler * r0 * n * A.shape[3] * n * r1
            T = T.reshape(oncekiler * n, r1, -1)
        bag = r1
    return T.reshape(-1), int(flop)


def tt_carp_rank1(tt: TTDizey, a: Sequence[np.ndarray]
                  ) -> Tuple[List[np.ndarray], int]:
    """TT-matris × **rank-1 TT vektörü** -- ceridenin hakikî yolu.

    Vektör ``v = a₁ ⊗ a₂ ⊗ … ⊗ a_d`` (χ_v = 1) ise, ``k``ıncı çekirdek
    yalnız kendi ``a_k``sıyla büzülür::

        H_k[r₀, i, r₁] = Σ_j G_k[r₀, i, j, r₁] · a_k[j]
        masraf          = 2 · r₀ · n · n · r₁

    Toplam ``2·(16³ + 16⁴ + 16⁴ + 16³) = 278.528`` -- ceridenin sayısı
    **tam olarak budur** ve sayaç bunu teyit eder.

    Dönen, neticenin TT çekirdekleridir (``(r₀, n, r₁)`` şeklinde);
    yoğun vektöre açılmaz, zira açmak ``n^d`` yer tutar ve kazancı
    yakar. **Neticenin rütbesi artık 1 değil ``R_M``dir**; bu, bu
    dosyanın açtığı asıl meseledir (bkz. ``zincir_maliyeti``).
    """
    a = [np.asarray(x, float).ravel() for x in a]
    if len(a) != tt.d:
        raise ValueError("rank-1 vektör %d çarpandan olmalı" % tt.d)
    out: List[np.ndarray] = []
    flop = 0
    for k, c in enumerate(tt.cekirdek):
        r0, n, m, r1 = c.shape
        if a[k].size != m:
            raise ValueError("çarpan %d: %d ≠ %d" % (k, a[k].size, m))
        out.append(np.tensordot(c, a[k], axes=([2], [0])))   # (r0,n,r1)
        flop += 2 * r0 * n * m * r1
    return out, int(flop)


def rank1_ayristir(v: np.ndarray, n: int = 16, d: Optional[int] = None
                   ) -> Tuple[List[np.ndarray], float]:
    """``v``yi ``a₁ ⊗ … ⊗ a_d``ye en iyi rank-1 yaklaşımıyla ayır.

    Ardışık SVD'nin baş tekil vektörleriyle (TT-SVD'nin rütbe-1 hâli).
    Döner: ``(çarpanlar, bağıl hata)``. **Hata sıfır değilse** o
    vektörün χ_v = 1 olduğu iddiası o kadar yanlıştır; sayı budur,
    iddia değil.
    """
    v = np.asarray(v, float).ravel()
    if d is None:
        d = int(round(math.log(max(v.size, 2), n)))
    if v.size != n ** d:
        raise ValueError("vektör %d, %d^%d = %d değil"
                         % (v.size, n, d, n ** d))
    T = v.reshape([n] * d)
    carpan: List[np.ndarray] = []
    kalan = T
    olcek = 1.0
    for k in range(d - 1):
        M = kalan.reshape(n, -1)
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        carpan.append(U[:, 0].copy())
        olcek *= float(s[0])
        kalan = Vt[0].reshape([n] * (d - k - 1))
    carpan.append(kalan.ravel() * olcek)
    geri = carpan[0]
    for c in carpan[1:]:
        geri = np.multiply.outer(geri, c)
    hata = float(np.linalg.norm(geri.ravel() - v)
                 / max(np.linalg.norm(v), 1e-30))
    return carpan, hata


def zincir_maliyeti(meleke: int = 41, n: int = 16, d: int = 4,
                    r: int = 16, sikistir: bool = True) -> Dict[str, object]:
    """41 melekeyi **ard arda** koşturmanın maliyeti -- rütbe büyür mü?

    Ceridenin ``278.528 FLOP`` hesabı ``χ_v = 1`` içindir. Fakat bir
    meleke tatbik edilince neticenin rütbesi ``R_M = 16`` olur; ikinci
    meleke artık rank-1 bir vektörle değil rütbe-16 bir vektörle
    karşılaşır. İki ihtimal vardır ve ikisi de burada sayılır:

    * ``sikistir=True``  -- her melekeden sonra netice **rank-1'e geri
      sıkıştırılır**. O zaman her meleke 278.528 FLOP'tur ve ceridenin
      cetveli aynen tutar; bedeli sıkıştırma hatasıdır.
    * ``sikistir=False`` -- rütbe serbest bırakılır. O zaman ``k``ıncı
      melekede vektör rütbesi ``min(r^k, n^{d/2})``e kadar büyür ve
      masraf katlanır.

    Bu bir itiraz değil, bir **çatal**dır: hangi kolun seçildiği
    mimarînin hükmüdür ve sayısı burada durur.
    """
    tek = 0
    r0 = 1
    for k in range(d):
        r1 = 1 if k == d - 1 else r
        tek += 2 * r0 * n * n * r1
        r0 = r1
    if sikistir:
        return {"kol": "her melekeden sonra rank-1'e sıkıştır",
                "meleke_başına_FLOP": int(tek),
                "toplam_FLOP": int(meleke * tek),
                "vektör_rütbesi": 1,
                "not": "ceridenin cetveli aynen tutar; bedel sıkıştırma hatası"}
    # rütbe serbest: χ_k = min(r^k, n^{d/2}) -- MPS'in fizikî tavanı
    tavan = n ** (d // 2)
    top = 0
    khi = 1
    for _ in range(meleke):
        # MPO(r) × MPS(khi): orta çekirdeklerde 2·n²·r²·khi²
        top += 2 * (n * n) * (r * r) * (khi * khi) * (d - 2) + 2 * tek
        khi = min(khi * r, tavan)
    return {"kol": "rütbe serbest (sıkıştırma yok)",
            "meleke_başına_FLOP": None,
            "toplam_FLOP": int(top),
            "vektör_rütbesi": int(khi),
            "not": "rütbe r^k ile büyür, %d'de doyar" % tavan}


def yogun_flop(D: int) -> int:
    """Yoğun ``D×D`` matris-vektör çarpımı: ``2D²``."""
    return 2 * int(D) * int(D)


def ceride_flop(n: int = 16, d: int = 4, r: int = 16) -> int:
    """Ceridenin TT-MVM hesabı: çekirdek elemanlarının iki katı.

    ``2 × (16³ + 16⁴ + 16⁴ + 16³) = 278.528``. Bu, çekirdeklerin
    **eleman sayısıdır**; çarpılan vektörün bağı 1 kabul edilmiştir.
    """
    top = 0
    r0 = 1
    for k in range(d):
        r1 = 1 if k == d - 1 else r
        top += r0 * n * n * r1
        r0 = r1
    return 2 * top


def kiyas(n: int = 8, d: int = 3, rank: int = 8,
          tohum: int = 0) -> Dict[str, object]:
    """TT ile yoğunu **fiilen** koştur: FLOP, hata ve nispet.

    ``D = n^d`` küçük tutulur (16⁴ = 4096'lık yoğun dizey 134 MB'dır ve
    yalnız kıyas için kurulup atılmak üzere pahalıdır); nispetler
    ``D``den bağımsız cebirsel olduğu için netice ölçekten bağımsızdır
    ve ``n=16, d=4`` için ``tt_flop`` ile ayrıca teyit edilir.
    """
    D = n ** d
    rng = np.random.default_rng(tohum)
    M = rng.normal(size=(D, D)) / np.sqrt(D)
    # Yapısız (tam rütbeli) dizey: sıkıştırmanın EN KÖTÜ hâli.
    tt = tt_ayristir(M, n=n, d=d, rank=rank)
    v = rng.normal(size=D)
    y_tt, flop_tt = tt_carp(tt, v)
    y_yg = M @ v
    hata = float(np.linalg.norm(y_tt - y_yg) / max(np.linalg.norm(y_yg), 1e-30))
    # Yapılı (düşük rütbeli) dizey: sıkıştırmanın işe yaradığı hâl.
    k = max(rank // 2, 1)
    L = rng.normal(size=(D, k)) / np.sqrt(D)
    M2 = L @ L.T
    tt2 = tt_ayristir(M2, n=n, d=d, rank=rank)
    y2, _ = tt_carp(tt2, v)
    hata2 = float(np.linalg.norm(y2 - M2 @ v)
                  / max(np.linalg.norm(M2 @ v), 1e-30))
    # **TT'nin hakkını vermek için üçüncü hâl.** Yukarıdaki iki dizey de
    # TT yapısında DEĞİLDİR; onlarla ölçmek TT'yi kendi sahasında değil
    # yabancı sahada denemektir ve haksızlıktır (kullanıcı hükmü D:
    # kendini de tenkit et). Kronecker çarpımı ``M3 = A₁⊗A₂⊗…⊗A_d`` tam
    # TT-rütbe 1'dir; TT onu **makine hassasiyetinde** taşımalıdır.
    # Taşımazsa kusur ceridede değil bu kodda demektir.
    Aк = [rng.normal(size=(n, n)) / np.sqrt(n) for _ in range(d)]
    M3 = Aк[0]
    for A in Aк[1:]:
        M3 = np.kron(M3, A)
    tt3 = tt_ayristir(M3, n=n, d=d, rank=rank)
    y3, _ = tt_carp(tt3, v)
    hata3 = float(np.linalg.norm(y3 - M3 @ v)
                  / max(np.linalg.norm(M3 @ v), 1e-30))
    return {"D": D, "n": n, "d": d, "rank": rank,
            "hata_kronecker": hata3,
            "bag_kronecker": tt3.bag,
            "flop_tt": int(flop_tt),
            "flop_yogun": yogun_flop(D),
            "flop_ceride": ceride_flop(n, d, rank),
            "nispet_tt_yogun": flop_tt / float(yogun_flop(D)),
            "nispet_ceride_yogun": ceride_flop(n, d, rank)
            / float(yogun_flop(D)),
            "eleman_tt": tt.eleman,
            "eleman_yogun": D * D,
            "hata_yapisiz": hata,
            "hata_yapili": hata2}


def tt_flop(n: int = 16, d: int = 4, r: int = 16) -> int:
    """Yoğun vektöre TT-MVM'in **cebrî** FLOP'u -- ``tt_carp`` ile aynı.

    İlk çekirdek ``2·n²·r``, ara çekirdek ``k`` ``2·n^{k}·r·n·n^{d−k−1}·r
    = 2·n^{d+1}·r²``, son çekirdek ``2·n^{d+1}·r``. Baskın terim
    ``2·n^{d+1}·r²``dir ve ``r``de **karesel** büyür; ceridenin
    ``2·n^d·r²`` sandığı yerde bir ``n`` çarpanı eksiktir.
    """
    top = 2 * n * n * r * (n ** (d - 1))
    for k in range(1, d):
        r0 = r
        r1 = 1 if k == d - 1 else r
        top += 2 * (n ** k) * r0 * n * (n ** (d - k - 1)) * n * r1
    return int(top)


def hiz_cetveli(tflops: float = 629.2e12, bayt_token: int = 4,
                meleke: int = 41, ek_flop_token: float = 2.58e6,
                n: int = 16, d: int = 4, r: int = 16) -> Dict[str, Dict]:
    """Ceridenin VIII. bölüm cetvelini **aynı formülle** yeniden kur.

    Ceride ``629,2 TFLOPS``, ``4 bayt/token`` ve 41 meleke kabul eder;
    RHT + KAN + Hodge için ``0,10 + 2,00 + 0,48 = 2,58 MFLOP/token`` ek
    yük yazar. Buradaki tek fark meleke başına FLOP'tur: ceride
    ``ceride_flop``u kullanır, biz ``tt_flop``u -- ikisi de burada,
    yan yana, kullanıcının H47 hükmü gereğince.
    """
    D = n ** d
    satir: Dict[str, Dict] = {}

    def kayit(ad: str, flop_meleke: float) -> None:
        ct = meleke * flop_meleke + ek_flop_token
        tok = tflops / ct
        satir[ad] = {"MFLOP/token": ct / 1e6,
                     "token/sn": tok,
                     "MB/sn": tok * bayt_token / 1e6}

    kayit("ceride TT-KAN (χ_v=1)", ceride_flop(n, d, r))
    kayit("hakikî TT-MVM (yoğun vektör)", tt_flop(n, d, r))
    kayit("yoğun D×D", yogun_flop(D))
    return satir


def _rapor() -> str:                                    # pragma: no cover
    """Kendi kendini gösterme (H126): ceridenin hız hükmü, sayıyla."""
    sat = ["TT-KAN: CERİDENİN HIZ HÜKMÜNÜN FİİLÎ HESABI", ""]
    k = kiyas(n=8, d=3, rank=8)
    sat.append("  ÖLÇÜLEN KIYAS (D=%d, n=%d, d=%d, r=%d)"
               % (k["D"], k["n"], k["d"], k["rank"]))
    for ad in ("flop_ceride", "flop_tt", "flop_yogun", "eleman_tt",
               "eleman_yogun", "hata_kronecker", "hata_yapili",
               "hata_yapisiz"):
        sat.append("    %-18s %s" % (ad, k[ad]))
    sat += ["",
            "  16⁴ ÖLÇEĞİNDE MELEKE BAŞINA FLOP",
            "    ceride (çekirdek eleman sayısı, χ_v=1) : %12d"
            % ceride_flop(16, 4, 16),
            "    hakikî TT-MVM (yoğun/dolaşık vektör)   : %12d"
            % tt_flop(16, 4, 16),
            "    yoğun D×D                              : %12d"
            % yogun_flop(4096),
            "",
            "  %-34s %12s %14s %10s" % ("REJİM", "MFLOP/tok", "token/sn",
                                        "MB/sn")]
    for ad, v in hiz_cetveli().items():
        sat.append("  %-34s %12.3f %14.0f %10.2f"
                   % (ad, v["MFLOP/token"], v["token/sn"], v["MB/sn"]))
    return "\n".join(sat)


if __name__ == "__main__":   # pragma: no cover
    print(_rapor())

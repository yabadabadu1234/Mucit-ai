"""
Stabilizer rank ayrışımı (Bravyi–Gosset–Smith) -- Clifford çerçevesi + T.

Vesikadaki hüküm:

    |Ψ⟩ = Σ_{j=1}^{χ_stab} c_j |φ_j^{Stab}⟩ ,  χ_stab ∈ 𝒪(2^{αt}), α ≈ 0,228

**Fikir.** Dolaşıklık arttıkça MPS'in bağ boyutu ``χ`` patlar; çünkü
``χ`` **dolaşıklığa** bağlıdır. Stabilizer ayrışımında ise rank
dolaşıklığa değil **Clifford-dışılığa** (magic) bağlıdır: bir Clifford
devresi ne kadar dolaşık durum üretirse üretsin rank **1** kalır. Rank
ancak T kapısı (yahut başka Clifford-dışı kapı) girince büyür.

**Burada temsil edilen sınıf ve neyin temsil EDİLMEDİĞİ.** Bu dosya
**köşegen (diyagonal) Clifford yörüngesini** tutar:

    |φ_{D,J}⟩ = 2^{−n/2} Σ_{y∈F₂ⁿ} i^{q(y)} |y⟩ ,
    q(y) = Σ_i D_i y_i + 2 Σ_{i<j} J_ij y_i y_j   (mod 4)

Yani ``|+⟩^n``e ``Z``, ``S`` ve ``CZ`` vurularak varılan bütün
durumlar. Genlik ``O(1)``de okunur, küllî faz **takip edilir** (Aaronson–
Gottesman tablosu küllî fazı taşımaz; girişim için faz şarttır, onun
için tablo değil bu form seçildi).

Temsil edilmeyen: ``H`` (Hadamard) kapısı bu formu bozar ve umumî
Clifford için CH-formu lazımdır. **Yazılmadı ve yazıldığı iddia
edilmiyor.** Sebebi şudur: bizim ihtiyacımız olan devre zaten bu
sınıftadır -- referans durum ``|+⟩^n`` (bir kat H, başlangıçta),
kayıp orağı ``U_L`` **köşegendir**, difüzyon ``D`` ise devre olarak
değil rütbe-bir cebir olarak işlenir (``kuantum/dalga.py``). Umumî
Clifford lazım olursa borç olarak yazılır, uydurulmaz.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["StabilizerDurum", "StabilizerRank", "bgs_haddi"]

#: Bravyi–Gosset–Smith üssü: ``χ_stab ≲ 2^{αt}``.
ALFA = 0.228


def bgs_haddi(t: int) -> float:
    """``2^{0,228 t}`` -- t kapısı sayısına bağlı rank haddi (nazarî)."""
    return float(2.0 ** (ALFA * t))


@dataclass
class StabilizerDurum:
    """``2^{−n/2} Σ_y i^{q(y)}|y⟩`` -- tek bir Clifford çerçevesi."""
    n: int
    D: np.ndarray                                   # (n,) ∈ Z₄
    J: np.ndarray                                   # (n,n) üst üçgen, 0/1

    @staticmethod
    def arti(n: int) -> "StabilizerDurum":
        """``|+⟩^n`` -- düzgün süperpozisyon, faz yok."""
        return StabilizerDurum(n, np.zeros(n, np.int64),
                               np.zeros((n, n), np.int64))

    def kopya(self) -> "StabilizerDurum":
        return StabilizerDurum(self.n, self.D.copy(), self.J.copy())

    # -- köşegen Clifford kapıları: form KAPALI kalır ------------------
    def z(self, a: int) -> None:
        self.D[a] = (self.D[a] + 2) % 4

    def s(self, a: int) -> None:
        self.D[a] = (self.D[a] + 1) % 4

    def cz(self, a: int, b: int) -> None:
        i, j = (a, b) if a < b else (b, a)
        self.J[i, j] ^= 1

    # -----------------------------------------------------------------
    def faz(self, Y: np.ndarray) -> np.ndarray:
        """``q(y) mod 4`` -- yığın hâlinde, ``(B,)``."""
        Y = np.atleast_2d(np.asarray(Y, np.int64))
        dogrusal = Y @ self.D
        ikili = np.einsum("bi,ij,bj->b", Y, self.J, Y, optimize=True)
        return (dogrusal + 2 * ikili) % 4

    def genlik(self, Y: np.ndarray) -> np.ndarray:
        """``⟨y|φ⟩`` -- normalize, ``O(1)`` (yığında ``O(Bn²)``)."""
        q = self.faz(Y)
        return (1j ** q) * (2.0 ** (-0.5 * self.n))


# =====================================================================
class StabilizerRank:
    """``Σ_j c_j |φ_j⟩`` -- rank, **dolaşıklığa değil magic'e** bağlıdır."""

    def __init__(self, n: int) -> None:
        self.n = int(n)
        self.terimler: List[Tuple[complex, StabilizerDurum]] = [
            (1.0 + 0j, StabilizerDurum.arti(n))]
        self.t_sayisi = 0
        self.budama_hatasi = 0.0

    # -----------------------------------------------------------------
    def __len__(self) -> int:
        return len(self.terimler)

    def genlik(self, Y: np.ndarray) -> np.ndarray:
        Y = np.atleast_2d(np.asarray(Y, np.int64))
        top = np.zeros(len(Y), complex)
        for c, f in self.terimler:
            top = top + c * f.genlik(Y)
        return top

    # -- Clifford: rank BÜYÜMEZ ---------------------------------------
    def z(self, a: int) -> None:
        for _, f in self.terimler:
            f.z(a)

    def s(self, a: int) -> None:
        for _, f in self.terimler:
            f.s(a)

    def cz(self, a: int, b: int) -> None:
        for _, f in self.terimler:
            f.cz(a, b)

    # -- T: rank İKİYE katlanır ---------------------------------------
    def t(self, a: int) -> None:
        """``T = diag(1, e^{iπ/4})``. Köşegen Clifford grubunda değildir.

        Tam ayrışım: ``T = α·I + β·S`` (``S = diag(1,i)``). İki şart::

            α + β   = 1               (|0⟩ üzerinde)
            α + iβ  = e^{iπ/4}        (|1⟩ üzerinde)

        Buradan ``β = (e^{iπ/4} − 1)/(i − 1)``, ``α = 1 − β``. Ayrışım
        **tam**tır; yaklaşıklık yoktur. Rank her T ile ikiye katlanır;
        ``budama`` ile geri indirilir ve hatası ölçülür.
        """
        e = np.exp(1j * math.pi / 4)
        beta = (e - 1.0) / (1j - 1.0)
        alfa = 1.0 - beta
        yeni: List[Tuple[complex, StabilizerDurum]] = []
        for c, f in self.terimler:
            g = f.kopya()
            g.s(a)
            yeni.append((c * alfa, f))
            yeni.append((c * beta, g))
        self.terimler = yeni
        self.t_sayisi += 1

    # -----------------------------------------------------------------
    def budama(self, chi: int, Y_olcum: Optional[np.ndarray] = None
               ) -> float:
        """En büyük ``chi`` terimi tut; **atılan ağırlığı ölç ve dön**.

        Bravyi–Gosset–Smith'in seyrekleştirmesi rastgele izdüşümle daha
        iyi bir sabit verir; burada yapılan ondan basit ve **daha
        kötüdür** -- katsayı büyüklüğüne göre kesme. Öyle olduğu için de
        öyle raporlanır: aşağıdaki ölçüm bir alt sınır değil, bu basit
        kesmenin fiilî hatasıdır.
        """
        if len(self.terimler) <= chi:
            return 0.0
        sira = sorted(range(len(self.terimler)),
                      key=lambda i: -abs(self.terimler[i][0]))
        tut = sira[:chi]
        at = sira[chi:]
        atilan = float(sum(abs(self.terimler[i][0]) ** 2 for i in at))
        self.terimler = [self.terimler[i] for i in tut]
        self.budama_hatasi += atilan
        return atilan

    def seyreklestir(self, k: int, tohum: int = 0) -> Dict[str, float]:
        """Bravyi–Gosset **rastgele seyrekleştirmesi** -- asıl usul budur.

        ``|Ψ⟩ = Σ_j c_j|φ_j⟩`` iken ``p_j = |c_j| / ‖c‖₁`` ile ``k`` terim
        **iadeli** çekilir ve

            |Ω⟩ = (‖c‖₁ / k) Σ_{s=1}^{k} (c_{j_s}/|c_{j_s}|) |φ_{j_s}⟩

        kurulur. Teoremin verdiği had ``𝔼‖Ψ − Ω‖² ≤ ‖c‖₁²/k``dır. Dikkat:
        had ``‖c‖₂``ye değil **``‖c‖₁``e** bağlıdır -- terimler dik
        olmadığı için ``ℓ₂`` ağırlığı hatanın ölçüsü değildir.

        Bu, katsayı büyüklüğüne göre kesmenin (``budama``) neden çöktüğünü
        de açıklar ve o çöküş aşağıda ölçülmüştür: ``χ`` 4096'dan 64'e
        inince atılan ``ℓ₂`` ağırlığı 1,6e-03 iken genlik hatası 9,87e-01
        çıkmıştı. Küçük katsayı, küçük hata demek değildir.
        """
        rng = np.random.default_rng(tohum)
        c = np.array([t[0] for t in self.terimler], complex)
        l1 = float(np.abs(c).sum())
        if l1 <= 0.0 or k <= 0:
            return {"k": float(k), "l1": l1, "had": float("inf")}
        p = np.abs(c) / l1
        sec = rng.choice(len(c), size=int(k), replace=True, p=p)
        yeni: Dict[int, complex] = {}
        for j in sec:
            faz = c[j] / abs(c[j])
            yeni[int(j)] = yeni.get(int(j), 0j) + (l1 / k) * faz
        self.terimler = [(v, self.terimler[j][1]) for j, v in yeni.items()]
        return {"k": float(k), "l1": l1, "had": float(l1 * l1 / k),
                "ayrık_terim": float(len(self.terimler))}

    def durum(self) -> Dict[str, float]:
        return {"kübit": float(self.n), "rank": float(len(self.terimler)),
                "t_kapısı": float(self.t_sayisi),
                "bgs_haddi": bgs_haddi(self.t_sayisi),
                "budama_hatası": self.budama_hatasi,
                "bellek_bayt": float(sum(f.D.nbytes + f.J.nbytes
                                         for _, f in self.terimler)),
                "açık_dizi_bayt_log2": float(self.n + 4)}


# =====================================================================
def _gosterim() -> str:
    rng = np.random.default_rng(0)
    n = 14
    Y = rng.integers(0, 2, size=(400, n))
    s = ["=== Stabilizer rank: dolaşıklık BEDAVA, magic PAHALI ==="]

    # --- 1. Clifford devresi: rank 1 kalır, durum dolaşık olur
    S = StabilizerRank(n)
    for _ in range(60):
        a, b = rng.choice(n, 2, replace=False)
        S.cz(int(a), int(b))
        S.s(int(rng.integers(n)))
    g = S.genlik(Y)
    s += ["",
          "1) 60 Clifford kapısı (CZ + S) sonrası:",
          "   rank = %d   bellek = %d bayt   açık dizi olsaydı = 2^%d karmaşık"
          % (len(S), int(S.durum()["bellek_bayt"]), n),
          "   |genlik| hepsi eşit mi (Clifford yörüngesi şartı): sapma %.2e"
          % float(np.abs(np.abs(g) - 2.0 ** (-n / 2)).max()),
          "   norm² (400 örnekten kestirim × 2^n): %.6f"
          % float((np.abs(g) ** 2).mean() * 2 ** n)]

    # --- 2. T kapıları: rank ikiye katlanır, HAT ile mukayese
    s += ["", "2) T kapısı eklendikçe rank (tam ayrışım, budama yok):",
          "   t   rank      BGS haddi 2^0,228t   tam devre 2^t"]
    S2 = StabilizerRank(n)
    for t in range(1, 13):
        S2.t(int(rng.integers(n)))
        if t in (1, 2, 4, 6, 8, 10, 12):
            s.append("   %-3d %-9d %-19.2f %d"
                     % (t, len(S2), bgs_haddi(t), 2 ** t))

    # --- 3. Budama: rank'ı kısınca hata ne oluyor (ÖLÇÜM)
    s += ["", "3) Budama: rank χ'ya inince genlik hatası",
          "   χ    tutulan   atılan ağırlık   ‖Δgenlik‖/‖genlik‖"]
    tam = None
    for chi in (4096, 64, 16, 8, 4, 2, 1):
        S3 = StabilizerRank(n)
        rng2 = np.random.default_rng(5)
        for _ in range(12):
            S3.t(int(rng2.integers(n)))
        at = S3.budama(chi)
        gg = S3.genlik(Y)
        if tam is None:
            tam = gg
            s.append("   %-4d %-9d %-16.3e %s" % (chi, len(S3), at, "(esas)"))
        else:
            s.append("   %-4d %-9d %-16.3e %.3e"
                     % (chi, len(S3), at,
                        float(np.linalg.norm(gg - tam)
                              / (np.linalg.norm(tam) + 1e-300))))

    # --- 4. BGS rastgele seyrekleştirmesi: ASIL usul
    s += ["", "4) Bravyi–Gosset rastgele seyrekleştirmesi (aynı devre):",
          "   k     ayrık terim   ‖Δgenlik‖²/‖genlik‖²   nazarî had ‖c‖₁²/k"]
    r: Dict[str, float] = {"l1": float("nan")}
    for k in (16, 64, 256, 1024, 4096, 16384):
        S4 = StabilizerRank(n)
        rng3 = np.random.default_rng(5)
        for _ in range(12):
            S4.t(int(rng3.integers(n)))
        r = S4.seyreklestir(k, tohum=1)
        gg = S4.genlik(Y)
        hata = float(np.linalg.norm(gg - tam) ** 2
                     / (np.linalg.norm(tam) ** 2 + 1e-300))
        s.append("   %-5d %-13d %-22.3e %.3e"
                 % (k, int(r["ayrık_terim"]), hata, r["had"]))
    s.append("   (‖c‖₁ = %.3f; had ℓ₂'ye değil ℓ₁'e bağlıdır)" % r["l1"])

    s += ["",
          "Hüküm: Clifford kapıları rankı HİÇ büyütmüyor (60 kapı → rank 1);",
          "rank yalnız T ile büyüyor. Bu, MPS'in tam tersidir: orada 60",
          "dolaştırıcı kapı χ'yı patlatırdı. Bedel, temsil edilen sınıfın",
          "dar olmasıdır -- H yoktur ve olduğu iddia edilmiyor."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(_gosterim())

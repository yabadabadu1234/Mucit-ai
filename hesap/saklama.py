"""Kuantum durumunu saklamanın gerçek maliyeti: keyfî vs YAPILI.

Kaynak: ``docs/kaynak/kuantum_hudutsuzluk.tex`` §Atom Sayısı
Kısıtlamasının Reddi.

**M27 tashihi.**  Kaynak, "``2^300`` parametre ``10^80`` atomdan
fazladır, dolayısıyla imkânsızdır" itirazını "ontolojik hata" diye
reddediyor.  İtirazın **kapsamı** yanlış anlaşılmış:

* İtiraz doğrudur ve **keyfî** bir durum içindir.  Genel bir ``N``-kubit
  durumu ``2^N`` karmaşık sayı ister; ``N = 300``de bu ``2×10^90``
  sayıdır ve hiçbir fizikî bellekle yazılamaz.  Bu, uzayın *boyutuna*
  değil, o boyutta *keyfî bir noktayı adreslemeye* dair bir sayımdır.
* İtiraz **yapılı** sınıfları kapsamaz.  Kararlayıcı (stabilizer)
  durumlar ``O(N²)`` bit, düşük bağlı MPS durumları ``O(Nχ²)`` sayı ile
  **tam olarak** saklanır.  ``N = 400``, ``N = 4000`` bu sınıflarda
  sıradan bir hesaptır ve bu modülde **gerçekten koşuluyor**.

Yani doğru cevap "sınır yoktur" değil, **"hangi yapılı sınıftayız"**dır.
İkisi de burada kurulu ve maliyetleri ölçülüyor:

* :class:`Kararlayici` — CHP tablosu; Clifford devreleri ``O(N²)``
  bellek, kapı başına ``O(N)`` iş.  ``N = 1024`` kubit koşuluyor.
* :class:`MPS` — çarpım/düşük dolaşıklı durumlar; ``O(Nχ²)`` bellek.
* :func:`keyfi_durum_maliyeti` — keyfî durumun maliyeti; ölçekleme
  sayıyla gösteriliyor.

**Dürüstlük şartı.**  Kararlayıcı durumlar üniversal değildir
(Gottesman--Knill: klasik olarak verimli benzetilirler, yani tek
başlarına kuantum üstünlüğü vermezler).  MPS'in maliyeti ``χ`` ile,
``χ`` de dolaşıklıkla büyür.  İki sınıf da "bedava sonsuzluk" değildir
ve bu, modülün kendi ölçümleriyle gösteriliyor.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "keyfi_durum_maliyeti", "Kararlayici", "MPS",
    "kararlayici_maliyeti", "mps_maliyeti", "sinif_kiyasi",
]

EVREN_ATOM = 1e80


def keyfi_durum_maliyeti(N: int) -> Dict[str, object]:
    """Keyfî ``N``-kubit durumu: ``2^N`` karmaşık sayı.

    ``log10`` ile hesaplanıyor; ``2**300`` float'a sığmaz ama
    logaritması sığar (aynı sınıf hata daha önce ``0.9^400``da
    yakalanmıştı).
    """
    log10_sayi = N * math.log10(2.0)
    log10_bayt = log10_sayi + math.log10(16.0)      # complex128
    return {"N": N, "log10_katsayı_sayısı": log10_sayi,
            "log10_bayt": log10_bayt,
            "evren_atomundan_fazla_mı": log10_sayi > 80.0,
            "atomla_oran_log10": log10_sayi - 80.0}


# ══════════════════════════════════════════════════════════════════════
#  1. Kararlayıcı (stabilizer) durumlar — CHP tablosu
# ══════════════════════════════════════════════════════════════════════

class Kararlayici:
    """``N`` kubitlik kararlayıcı durum — ``O(N²)`` bit.

    Tablo: ``2N × (2N+1)`` GF(2) dizeyi.  Satır ``i``, bir Pauli
    çarpımının ``(x | z | faz)`` gösterimidir; ilk ``N`` satır
    yıkıcılar (destabilizer), son ``N`` satır kararlayıcılardır.
    Aaronson--Gottesman usulü.

    Kapılar: ``H``, ``S``, ``CNOT`` — hepsi ``O(N)``.  Ölçüm ``O(N²)``.
    """

    def __init__(self, n: int):
        self.n = n
        self.x = np.zeros((2 * n, n), dtype=np.uint8)
        self.z = np.zeros((2 * n, n), dtype=np.uint8)
        self.r = np.zeros(2 * n, dtype=np.uint8)
        for i in range(n):
            self.x[i, i] = 1          # yıkıcılar: X_i
            self.z[n + i, i] = 1      # kararlayıcılar: Z_i

    # --- kapılar ---
    def H(self, a: int) -> "Kararlayici":
        self.r ^= self.x[:, a] & self.z[:, a]
        self.x[:, a], self.z[:, a] = self.z[:, a].copy(), self.x[:, a].copy()
        return self

    def S(self, a: int) -> "Kararlayici":
        self.r ^= self.x[:, a] & self.z[:, a]
        self.z[:, a] ^= self.x[:, a]
        return self

    def CNOT(self, a: int, b: int) -> "Kararlayici":
        self.r ^= (self.x[:, a] & self.z[:, b]
                   & (self.x[:, b] ^ self.z[:, a] ^ 1))
        self.x[:, b] ^= self.x[:, a]
        self.z[:, a] ^= self.z[:, b]
        return self

    def X(self, a: int) -> "Kararlayici":
        return self.H(a).S(a).S(a).H(a)

    def Z(self, a: int) -> "Kararlayici":
        return self.S(a).S(a)

    # --- ölçüm ---
    def olc(self, a: int, tohum: Optional[int] = None) -> Dict[str, object]:
        """``Z_a`` ölçümü.  Belirli mi rastgele mi olduğu **söylenir**."""
        n = self.n
        p = None
        for i in range(n, 2 * n):
            if self.x[i, a]:
                p = i
                break
        if p is not None:                       # rastgele netice
            rng = np.random.default_rng(tohum)
            for i in range(2 * n):
                if i != p and self.x[i, a]:
                    self._satir_carp(i, p)
            self.x[p - n] = self.x[p].copy()
            self.z[p - n] = self.z[p].copy()
            self.r[p - n] = self.r[p]
            self.x[p] = 0
            self.z[p] = 0
            self.z[p, a] = 1
            netice = int(rng.integers(0, 2))
            self.r[p] = netice
            return {"netice": netice, "belirli_mi": False}
        # belirli netice
        xs = np.zeros(n, dtype=np.uint8)
        zs = np.zeros(n, dtype=np.uint8)
        rs = 0
        for i in range(n):
            if self.x[i, a]:
                rs, xs, zs = self._birlestir(rs, xs, zs, self.r[i + n],
                                             self.x[i + n], self.z[i + n])
        return {"netice": int(rs), "belirli_mi": True}

    # --- iç yardımcılar ---
    @staticmethod
    def _g(x1, z1, x2, z2) -> int:
        if x1 == 0 and z1 == 0:
            return 0
        if x1 == 1 and z1 == 1:
            return int(z2) - int(x2)
        if x1 == 1 and z1 == 0:
            return int(z2) * (2 * int(x2) - 1)
        return int(x2) * (1 - 2 * int(z2))

    def _satir_carp(self, i: int, j: int) -> None:
        t = 2 * int(self.r[i]) + 2 * int(self.r[j])
        for k in range(self.n):
            t += self._g(self.x[j, k], self.z[j, k],
                         self.x[i, k], self.z[i, k])
        self.r[i] = np.uint8((t % 4) // 2)
        self.x[i] ^= self.x[j]
        self.z[i] ^= self.z[j]

    def _birlestir(self, rs, xs, zs, ri, xi, zi):
        t = 2 * int(rs) + 2 * int(ri)
        for k in range(self.n):
            t += self._g(xi[k], zi[k], xs[k], zs[k])
        return (t % 4) // 2, xs ^ xi, zs ^ zi

    def bellek_bayt(self) -> int:
        return int(self.x.nbytes + self.z.nbytes + self.r.nbytes)


def kararlayici_maliyeti(N: int) -> Dict[str, object]:
    """``O(N²)`` bit — keyfî durumun ``2^N``'i ile kıyas."""
    bit = 2 * N * (2 * N + 1)
    return {"N": N, "bit": bit, "bayt": bit / 8.0,
            "log10_bayt": math.log10(max(bit / 8.0, 1e-300)),
            "keyfî_log10_bayt": keyfi_durum_maliyeti(N)["log10_bayt"]}


# ══════════════════════════════════════════════════════════════════════
#  2. MPS (matris çarpım durumu)
# ══════════════════════════════════════════════════════════════════════

class MPS:
    """``N`` kubit, bağ boyutu ``χ`` — ``O(Nχ²)`` sayı.

    ``A[k]`` şekli ``(χ_sol, 2, χ_sağ)``.  Burada yalnız *saklama* ve
    *çakışma* gerekiyor; tam bir MPS motoru değil, maliyetin gerçekten
    ``O(Nχ²)`` olduğunu ve normun doğru hesaplandığını göstermek için.
    """

    def __init__(self, tensorler: Sequence[np.ndarray]):
        self.A = [np.asarray(a, complex) for a in tensorler]
        self.N = len(self.A)

    @staticmethod
    def carpim_durumu(acilar: Sequence[float]) -> "MPS":
        """Dolaşıksız çarpım durumu — ``χ = 1``."""
        return MPS([np.array([[[math.cos(t / 2)], [math.sin(t / 2)]]],
                             dtype=complex) for t in acilar])

    @staticmethod
    def rastgele(N: int, chi: int, tohum: int = 0) -> "MPS":
        r = np.random.default_rng(tohum)
        A = []
        for k in range(N):
            sol = 1 if k == 0 else chi
            sag = 1 if k == N - 1 else chi
            A.append(r.normal(size=(sol, 2, sag))
                     + 1j * r.normal(size=(sol, 2, sag)))
        return MPS(A)

    def norm_kare(self) -> float:
        """``⟨ψ|ψ⟩`` — soldan sağa daraltma, ``O(Nχ³)``."""
        E = np.eye(self.A[0].shape[0], dtype=complex)
        for a in self.A:
            E = np.einsum("ij,isk,jsl->kl", E, a, a.conj())
        return float(np.real(E.reshape(-1)[0]))

    def normalize(self) -> "MPS":
        n = self.norm_kare()
        self.A[0] = self.A[0] / math.sqrt(n)
        return self

    def tam_vektor(self) -> np.ndarray:
        """Tam ``2^N`` vektörü — yalnız küçük ``N``de kıyas için."""
        if self.N > 20:
            raise ValueError("N > 20: tam vektör kurulmaz (mesele bu)")
        v = self.A[0]
        for a in self.A[1:]:
            v = np.einsum("i...j,jsk->i...sk", v, a)
        return v.reshape(-1)

    def bellek_sayi(self) -> int:
        return int(sum(a.size for a in self.A))


def mps_maliyeti(N: int, chi: int) -> Dict[str, object]:
    sayi = 2 * chi * chi * (N - 2) + 4 * chi if N > 2 else 4 * chi
    return {"N": N, "chi": chi, "karmaşık_sayı": sayi,
            "bayt": sayi * 16,
            "log10_bayt": math.log10(max(sayi * 16.0, 1e-300)),
            "keyfî_log10_bayt": keyfi_durum_maliyeti(N)["log10_bayt"]}


def sinif_kiyasi(N: int, chi: int = 32) -> Dict[str, object]:
    return {"keyfî": keyfi_durum_maliyeti(N),
            "kararlayıcı": kararlayici_maliyeti(N),
            "mps": mps_maliyeti(N, chi)}


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    import time
    s = []
    s.append("=== İtiraz KEYFÎ durum için doğrudur ===")
    s.append("       N    log10(katsayı)   log10(bayt)   evren atomundan "
             "fazla mı?")
    for N in (50, 100, 300, 400, 1024):
        k = keyfi_durum_maliyeti(N)
        s.append("  %6d   %12.1f   %12.1f   %s (10^%.0f kat)"
                 % (N, k["log10_katsayı_sayısı"], k["log10_bayt"],
                    k["evren_atomundan_fazla_mı"], k["atomla_oran_log10"]))
    s.append("  N=300'de katsayı sayısı evrendeki atomdan 10^10 kat fazla.")
    s.append("  Bu itiraz DOĞRUDUR ve reddedilemez.")

    s.append("\n=== Ama YAPILI durumlar bambaşka: kararlayıcı ===")
    s.append("       N   kararlayıcı bayt   keyfî log10(bayt)")
    for N in (100, 400, 1024, 4096):
        m = kararlayici_maliyeti(N)
        s.append("  %6d   %14.0f   %16.1f"
                 % (N, m["bayt"], m["keyfî_log10_bayt"]))

    s.append("\n=== 1024 kubitlik kararlayıcı durum GERÇEKTEN koşuluyor ===")
    for N in (64, 256, 1024):
        t0 = time.perf_counter()
        st = Kararlayici(N)
        for i in range(N):
            st.H(i)
        for i in range(N - 1):
            st.CNOT(i, i + 1)
        t1 = time.perf_counter()
        o = st.olc(0, tohum=0)
        t2 = time.perf_counter()
        s.append("  N=%5d  %d kapı %7.1f ms   ölçüm %6.1f ms   bellek "
                 "%7.1f KB   netice=%d (belirli mi: %s)"
                 % (N, 2 * N - 1, (t1 - t0) * 1e3, (t2 - t1) * 1e3,
                    st.bellek_bayt() / 1024, o["netice"], o["belirli_mi"]))
    s.append("  Aynı devre keyfî durum vektörüyle 2^1024 katsayı isterdi.")

    s.append("\n=== Kararlayıcı doğru mu? Bell durumu sağlaması ===")
    st = Kararlayici(2).H(0).CNOT(0, 1)
    o0 = st.olc(0, tohum=1)
    o1 = st.olc(1, tohum=1)
    s.append("  H(0), CNOT(0,1) → |Φ⁺⟩;  ölç(0)=%d (belirli mi %s), "
             "ölç(1)=%d (belirli mi %s)"
             % (o0["netice"], o0["belirli_mi"], o1["netice"],
                o1["belirli_mi"]))
    s.append("  İlk ölçüm RASTGELE, ikincisi BELİRLİ ve ilkine eşit:")
    s.append("  bu tam olarak Bell bağlılığıdır. Eşit mi? %s"
             % (o0["netice"] == o1["netice"]))
    esit = 0
    for t in range(200):
        st = Kararlayici(2).H(0).CNOT(0, 1)
        a = st.olc(0, tohum=t)["netice"]
        b = st.olc(1, tohum=t)["netice"]
        esit += (a == b)
    s.append("  200 bağımsız koşuda iki ölçüm hep eşit mi? %d/200" % esit)

    s.append("\n=== MPS: O(Nχ²) ===")
    s.append("       N   χ    karmaşık sayı        bayt   keyfî log10(bayt)")
    for N, chi in ((100, 8), (400, 32), (4096, 32)):
        m = mps_maliyeti(N, chi)
        s.append("  %6d  %3d   %12d   %9d   %14.1f"
                 % (N, chi, m["karmaşık_sayı"], m["bayt"],
                    m["keyfî_log10_bayt"]))
    s.append("  MPS normu doğru mu? (küçük N'de tam vektörle kıyas)")
    for N, chi in ((6, 1), (8, 3), (10, 4)):
        m = MPS.rastgele(N, chi, tohum=2).normalize()
        v = m.tam_vektor()
        s.append("    N=%2d χ=%d  MPS ⟨ψ|ψ⟩=%.12f   tam vektör ‖v‖²=%.12f"
                 % (N, chi, m.norm_kare(), float(np.vdot(v, v).real)))

    s.append("\n=== Dürüstlük şartı: bedava sonsuzluk yok ===")
    s.append("  (i) Kararlayıcı durumlar Gottesman–Knill gereği KLASİK")
    s.append("      olarak verimli benzetilir; tek başlarına kuantum")
    s.append("      üstünlüğü vermezler. Ucuz olmalarının sebebi budur.")
    s.append("  (ii) MPS maliyeti χ ile büyür; χ da dolaşıklıkla.")
    s.append("       Hacim yasası dolaşıklığında χ ~ 2^{N/2} olur ve")
    s.append("       maliyet keyfî duruma geri döner:")
    for N in (20, 40, 80):
        chi = 2 ** (N // 2)
        m = mps_maliyeti(N, chi)
        s.append("       N=%2d, χ=2^%d: log10(bayt)=%.1f   keyfî=%.1f"
                 % (N, N // 2, m["log10_bayt"], m["keyfî_log10_bayt"]))
    s.append("  Doğru cevap 'sınır yoktur' değil, HANGİ YAPILI SINIFTA")
    s.append("  olunduğunu yazmaktır.")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())

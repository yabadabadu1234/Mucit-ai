"""
matematik/temel.py - Hilbert Uzayı, Kuantum Cebir, Metrik ve Holonomi Temel Fonksiyonları
Mucit-AI / Nefs-i Müdrike Küllî Matematik Motoru
"""

import math
import cmath
from typing import List, Tuple, Union, Optional, Any

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class KuantumDurum:
    """d-boyutlu normalize karmaşık kuantum durum vektörü |psi>"""
    def __init__(self, vektor: Union[List[complex], Any], etiket: str = ""):
        self.etiket = etiket
        if HAS_NUMPY:
            if isinstance(vektor, np.ndarray):
                self.v = vektor.astype(np.complex128).flatten()
            else:
                self.v = np.array(vektor, dtype=np.complex128).flatten()
            norm = np.linalg.norm(self.v)
            if norm > 1e-15:
                self.v = self.v / norm
            self.d = len(self.v)
        else:
            # Saf Python fallback
            norm_kare = sum(abs(x)**2 for x in vektor)
            norm = math.sqrt(norm_kare)
            if norm > 1e-15:
                self.v = [complex(x) / norm for x in vektor]
            else:
                self.v = [complex(x) for x in vektor]
            self.d = len(self.v)

    def ic_carpim(self, diger: 'KuantumDurum') -> complex:
        """<self | diger> = sum_k self[k]^* * diger[k]"""
        if HAS_NUMPY:
            return complex(np.vdot(self.v, diger.v))
        else:
            return sum(x.conjugate() * y for x, y in zip(self.v, diger.v))

    def fubini_study_mesafesi(self, diger: 'KuantumDurum') -> float:
        """ds_FS^2 = 1 - |<self | diger>|^2"""
        c = self.ic_carpim(diger)
        sadakat = abs(c)**2
        return max(0.0, 1.0 - sadakat)

    def yogunluk_matrisi(self) -> Any:
        """rho = |psi><psi|"""
        if HAS_NUMPY:
            return np.outer(self.v, np.conj(self.v))
        else:
            n = self.d
            mat = [[complex(0) for _ in range(n)] for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    mat[i][j] = self.v[i] * self.v[j].conjugate()
            return mat

    def to_list(self) -> List[complex]:
        if HAS_NUMPY:
            return [complex(x) for x in self.v]
        return list(self.v)

    def __repr__(self) -> str:
        tag = f" '{self.etiket}'" if self.etiket else ""
        return f"<KuantumDurum{tag} d={self.d}>"


def bargmann_3_nokta(p1: KuantumDurum, p2: KuantumDurum, p3: KuantumDurum) -> Tuple[float, float, complex]:
    """
    Delta_3(p1, p2, p3) = <p1|p2><p2|p3><p3|p1> = r_3 * exp(i * Phi_3)
    Döndürür: (r_3, Phi_3, Delta_3)
    """
    c12 = p1.ic_carpim(p2)
    c23 = p2.ic_carpim(p3)
    c31 = p3.ic_carpim(p1)
    delta3 = c12 * c23 * c31
    r3 = abs(delta3)
    phi3 = cmath.phase(delta3)
    return r3, phi3, delta3


def bargmann_n_nokta(durumlar: List[KuantumDurum]) -> Tuple[float, float, complex, List[float]]:
    """
    Delta_n = <p1|p2><p2|p3>...<pn|p1> = r_n * exp(i * Phi_n)
    Simplicial Cecycle Decomposition ile ara üçgen fazlarını da döner.
    """
    n = len(durumlar)
    if n < 2:
        return 1.0, 0.0, complex(1.0, 0.0), []
    if n == 2:
        c12 = durumlar[0].ic_carpim(durumlar[1])
        c21 = durumlar[1].ic_carpim(durumlar[0])
        delta2 = c12 * c21
        return abs(delta2), cmath.phase(delta2), delta2, []

    # Zincir çarpımı
    delta_n = complex(1.0, 0.0)
    for k in range(n):
        sonraki = (k + 1) % n
        ic = durumlar[k].ic_carpim(durumlar[sonraki])
        delta_n *= ic

    r_n = abs(delta_n)
    phi_n = cmath.phase(delta_n)

    # Simplicial üçgenleme: Phi_n = sum_{k=2}^{n-1} Phi_3(p1, pk, pk+1)
    ucgen_fazlari = []
    p1 = durumlar[0]
    for k in range(1, n - 1):
        pk = durumlar[k]
        pk1 = durumlar[k + 1]
        _, phi_3, _ = bargmann_3_nokta(p1, pk, pk1)
        ucgen_fazlari.append(phi_3)

    return r_n, phi_n, delta_n, ucgen_fazlari


def hilbert_schmidt_ic_carpim(rho1: Any, rho2: Any) -> float:
    """Tr(rho1 * rho2)"""
    if HAS_NUMPY:
        prod = np.matmul(rho1, rho2)
        return float(np.real(np.trace(prod)))
    else:
        n = len(rho1)
        toplam = 0.0
        for i in range(n):
            for j in range(n):
                toplam += (rho1[i][j] * rho2[j][i]).real
        return toplam


def lie_komutator(A: Any, B: Any) -> Any:
    """[A, B] = A*B - B*A"""
    if HAS_NUMPY:
        return np.matmul(A, B) - np.matmul(B, A)
    else:
        n = len(A)
        AB = [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        BA = [[sum(B[i][k] * A[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        return [[AB[i][j] - BA[i][j] for j in range(n)] for i in range(n)]


def rastgele_kuantum_durum(d: int, etiket: str = "", tohum: Optional[int] = None) -> KuantumDurum:
    """Haar ölçümüne yakın normalize rastgele qudit durumu üretir"""
    import random
    if tohum is not None:
        rng = random.Random(tohum)
    else:
        rng = random.Random()

    ham = []
    for _ in range(d):
        re = rng.gauss(0.0, 1.0)
        im = rng.gauss(0.0, 1.0)
        ham.append(complex(re, im))
    return KuantumDurum(ham, etiket=etiket)

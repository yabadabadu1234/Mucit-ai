"""Kuantum asgarî arama: Grover, Dürr--Høyer ve adiyabatik çöküş.

Kaynak: ``docs/kaynak/kuantum_asgari_arama.tex``.

**Kaynağın doğru yazdığı yerler.**  Faz kehaneti
``O_f = Σ e^{iγf(x)}|x⟩⟨x|`` üniterdir; eşik kehaneti
``O_y|x⟩ = −|x⟩ ⟺ f(x) < f(y)`` doğrudur; Grover difüzyonu
``D = 2|Ψ₀⟩⟨Ψ₀| − I`` ve tur sayısı ``m ≈ (π/4)√(2^N/K)`` doğrudur;
adiyabatik ölçüt ``T ≥ ħ·max|⟨E₁|dH/dt|E₀⟩|/g_min²`` doğrudur.

**M18 -- ``K`` bilinmiyor.**  ``m``in formülü ``K``yı içerir ve ``K``
aramanın *neticesine* bağlıdır; önceden bilinmez.  Yanlış ``m`` ile
Grover dönmesi hedefi **aşar** ve başarı düşer.  Ölçüldü
(``2^10 = 1024``): gerçek ``K = 64`` iken ``K = 1`` varsayıp ``m = 25``
koşmak başarıyı **0.099**a düşürüyor; doğru ``m = 3`` ile 0.961.
Ayrıca ``2·m_opt`` turda ``K=1`` için başarı 0.9995'ten **0.0002**'ye
iniyor -- fazla dönmek zarardır.

Doğrusu Dürr--Høyer'in **rastgele tur çizelgesidir**: ``m``,
``[0, ⌈λ^j⌉)`` aralığından çekilir (``λ = 6/5``, ``j = 0,1,2,…``).
Bu, ``K``yı bilmeden beklenen ``O(√(2^N/K))`` sorguyu korur ve burada
gerçekten koşuluyor.

**M19 -- "%100 doğruluk".**  Adiyabatik teorem bir limit ifadesidir;
sonlu ``T``de başarı asla tam 1 değildir.  Ölçülüyor.  (Kaynakta bu
cümle ayrıca ``%`` kaçırılmadığı için LaTeX'te tamamen kayboluyor.)
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "esit_superpozisyon", "faz_kehaneti", "esik_kehaneti",
    "difuzyon", "grover_turu", "grover_basari_egrisi",
    "en_iyi_tur", "durr_hoyer", "sabit_m_ile_arama",
    "adiyabatik_asgari", "tayf_araligi_asgari",
]


def esit_superpozisyon(N: int) -> np.ndarray:
    """``|Ψ₀⟩ = H^{⊗n}|0⟩`` — ``N = 2^n`` boyutunda."""
    return np.full(N, 1.0 / math.sqrt(N), dtype=complex)


def faz_kehaneti(f: np.ndarray, gamma: float) -> np.ndarray:
    """``O_f = diag(e^{iγf(x)})`` — köşegen, üniter (kaynak doğru)."""
    return np.exp(1j * gamma * np.asarray(f, float))


def esik_kehaneti(f: np.ndarray, esik: float) -> np.ndarray:
    """``O_y = diag(−1 if f(x) < esik else +1)``."""
    return np.where(np.asarray(f, float) < esik, -1.0, 1.0)


def difuzyon(psi: np.ndarray) -> np.ndarray:
    """``D = 2|Ψ₀⟩⟨Ψ₀| − I`` — ortalama etrafında yansıma, ``O(N)``.

    Tam dizey kurulmaz: ``Dψ = 2⟨ψ⟩ − ψ``.
    """
    return 2.0 * psi.mean() - psi


def grover_turu(psi: np.ndarray, isaret: np.ndarray) -> np.ndarray:
    """Bir Grover turu: kehanet sonra difüzyon."""
    return difuzyon(isaret * psi)


def grover_basari_egrisi(N: int, K: int, azami_tur: int,
                         tohum: int = 0) -> np.ndarray:
    """``m = 0…azami_tur`` için işaretli kümenin toplam olasılığı."""
    isaretli = np.zeros(N, dtype=bool)
    isaretli[:K] = True
    isaret = np.where(isaretli, -1.0, 1.0)
    psi = esit_superpozisyon(N)
    egri = [float((np.abs(psi[isaretli]) ** 2).sum())]
    for _ in range(azami_tur):
        psi = grover_turu(psi, isaret)
        egri.append(float((np.abs(psi[isaretli]) ** 2).sum()))
    return np.array(egri)


def en_iyi_tur(N: int, K: int) -> int:
    """``m_opt = round((π/4)√(N/K))`` — ``K`` **biliniyorsa**."""
    return int(round(math.pi / 4.0 * math.sqrt(N / max(K, 1))))


def sabit_m_ile_arama(f: np.ndarray, esik: float, m: int,
                      tohum: int = 0) -> Dict[str, object]:
    """``m`` turu sabit koş ve ölç — ``m`` yanlışsa ne oluyor görülsün."""
    N = f.shape[0]
    isaret = esik_kehaneti(f, esik)
    isaretli = isaret < 0
    psi = esit_superpozisyon(N)
    for _ in range(m):
        psi = grover_turu(psi, isaret)
    p = np.abs(psi) ** 2
    p = p / p.sum()
    x = int(np.random.default_rng(tohum).choice(N, p=p))
    return {"m": m, "başarı_olasılığı": float(p[isaretli].sum()),
            "ölçülen_x": x, "isabet": bool(isaretli[x]),
            "K": int(isaretli.sum())}


def durr_hoyer(f: np.ndarray, tohum: int = 0, lam: float = 6.0 / 5.0,
               azami_sorgu: int = 10000) -> Dict[str, object]:
    """Dürr--Høyer asgarî arama — ``K`` **bilinmeden** (M18).

    Tur sayısı ``m``, ``[0, ⌈λ^j⌉)`` aralığından rastgele çekilir;
    ``j`` her turda büyür.  Böylece ``K``yı bilmek gerekmez ve beklenen
    sorgu ``O(√N)`` kalır.  Toplam kehanet çağrısı **sayılıyor**;
    "karmaşıklık iyi" iddiası sayıyla tartılıyor.
    """
    r = np.random.default_rng(tohum)
    N = f.shape[0]
    y = int(r.integers(0, N))
    sorgu = 0
    j = 0.0
    seyir = [(0, y, float(f[y]))]
    while sorgu < azami_sorgu:
        ust = max(1, int(math.ceil(lam ** j)))
        m = int(r.integers(0, min(ust, int(3 * math.sqrt(N)) + 1)))
        isaret = esik_kehaneti(f, f[y])
        if not (isaret < 0).any():
            break                                # y zaten asgarî
        psi = esit_superpozisyon(N)
        for _ in range(m):
            psi = grover_turu(psi, isaret)
        sorgu += m + 1
        p = np.abs(psi) ** 2
        p = p / p.sum()
        x = int(r.choice(N, p=p))
        if f[x] < f[y]:
            y = x
            seyir.append((sorgu, y, float(f[y])))
            j = 0.0
        else:
            j += 1.0
        if f[y] == f.min():
            break
    return {"x": y, "f": float(f[y]), "asgarî": float(f.min()),
            "bulundu_mu": bool(f[y] == f.min()), "sorgu": sorgu,
            "sqrt_N": math.sqrt(N), "sorgu_bölü_sqrtN": sorgu / math.sqrt(N),
            "seyir": seyir}


# ══════════════════════════════════════════════════════════════════════
#  Adiyabatik (M19)
# ══════════════════════════════════════════════════════════════════════

def _baslangic_H(n: int) -> np.ndarray:
    """``H₀ = −Σ X_i`` — temel durumu ``|+⟩^{⊗n}``, **köşegen değil**."""
    N = 2 ** n
    H = np.zeros((N, N))
    for i in range(n):
        bit = 1 << (n - 1 - i)
        idx = np.arange(N)
        H[idx, idx ^ bit] -= 1.0
    return H


def tayf_araligi_asgari(f: np.ndarray, ornek: int = 101,
                        s_ust: float = 0.95) -> Dict[str, object]:
    """``g(s) = E₁ − E₀`` ve ``[0, s_ust]``te asgarîsi."""
    N = f.shape[0]
    n = int(round(math.log2(N)))
    H0 = _baslangic_H(n)
    H1 = np.diag(np.asarray(f, float))
    ss = np.linspace(0.0, 1.0, ornek)
    g = []
    for s in ss:
        e = np.linalg.eigvalsh((1 - s) * H0 + s * H1)
        g.append(float(e[1] - e[0]))
    g = np.array(g)
    mask = ss <= s_ust
    i = int(np.argmin(np.where(mask, g, np.inf)))
    return {"s": ss, "aralık": g, "g_min": float(g[i]),
            "s_min": float(ss[i]), "uç": float(g[-1])}


def adiyabatik_asgari(f: np.ndarray, T: float, adim: int = 300
                      ) -> Dict[str, object]:
    """``H(t)`` ile taşı; **asgarî** duruma örtüşme.

    Dilim başına tam üstel kullanılıyor: ölçülen hata gerçekten
    adiyabatik hatadır, üstel yaklaşımı değil.
    """
    N = f.shape[0]
    n = int(round(math.log2(N)))
    H0 = _baslangic_H(n)
    H1 = np.diag(np.asarray(f, float))
    e0, V0 = np.linalg.eigh(H0)
    psi = V0[:, 0].astype(complex)
    dt = T / adim
    for k in range(adim):
        s = (k + 0.5) / adim
        lam, V = np.linalg.eigh((1 - s) * H0 + s * H1)
        psi = (V * np.exp(-1j * lam * dt)) @ (V.conj().T @ psi)
    en_kucuk = float(np.min(f))
    hedef = np.isclose(f, en_kucuk)
    p = float((np.abs(psi[hedef]) ** 2).sum())
    return {"T": T, "başarı": p, "tam_1_mi": p == 1.0,
            "1_e_uzaklık": 1.0 - p,
            "asgarî_katlılık": int(hedef.sum())}


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s = []
    N = 1024
    s.append("=== Grover eğrisi: fazla dönmek ZARARDIR ===")
    s.append("     K   m_opt   P(m_opt)   P(2·m_opt)   P(3·m_opt)")
    for K in (1, 4, 16, 64):
        m = en_iyi_tur(N, K)
        e = grover_basari_egrisi(N, K, 3 * m + 1)
        s.append("  %4d   %5d   %8.4f   %10.4f   %10.4f"
                 % (K, m, e[m], e[min(2 * m, len(e) - 1)],
                    e[min(3 * m, len(e) - 1)]))
    s.append("  Başarı m ile TEKDÜZE ARTMIYOR; sinüzoidal salınıyor.")

    s.append("\n=== M18: K bilinmezse m seçilemez ===")
    r = np.random.default_rng(0)
    f = r.random(N)
    K_gercek = 64
    esik = np.sort(f)[K_gercek]
    for varsayim, ad in ((1, "K=1 varsayıldı (YANLIŞ)"),
                         (K_gercek, "K=64 biliniyor (İMKÂNSIZ)")):
        m = en_iyi_tur(N, varsayim)
        d = sabit_m_ile_arama(f, esik, m)
        s.append("  %-28s m=%3d → başarı = %.4f"
                 % (ad, m, d["başarı_olasılığı"]))
    s.append("  'K biliniyor' hâli gerçekte kurulamaz: K, aramanın")
    s.append("  NETİCESİNE bağlıdır. Doğru çare rastgele tur çizelgesi:")

    s.append("\n=== Dürr–Høyer: K bilinmeden asgarîyi buluyor ===")
    s.append("      N    bulundu mu   sorgu   sorgu/√N")
    for n in (8, 10, 12):
        Nn = 2 ** n
        basari, sorgular = 0, []
        for t in range(20):
            ff = np.random.default_rng(100 + t).random(Nn)
            d = durr_hoyer(ff, tohum=t)
            basari += d["bulundu_mu"]
            sorgular.append(d["sorgu"])
        s.append("  %5d      %2d/20     %6.1f   %7.2f"
                 % (Nn, basari, float(np.mean(sorgular)),
                    float(np.mean(sorgular)) / math.sqrt(Nn)))
    s.append("  Sorgu sayısı √N'in küçük bir katı; K hiç bilinmedi.")

    s.append("\n=== M19: adiyabatik başarı sonlu T'de TAM 1 DEĞİL ===")
    n = 4
    ff = np.random.default_rng(5).random(2 ** n)
    ff[3] = -1.0                                  # tek asgarî
    t = tayf_araligi_asgari(ff)
    s.append("  g_min = %.6f (s=%.2f)   uçta g(1) = %.6f"
             % (t["g_min"], t["s_min"], t["uç"]))
    s.append("       T     başarı        1 − başarı    tam 1 mi?")
    for T in (1.0, 4.0, 16.0, 64.0, 256.0):
        a = adiyabatik_asgari(ff, T)
        s.append("  %6.1f   %.10f   %.3e     %s"
                 % (T, a["başarı"], a["1_e_uzaklık"], a["tam_1_mi"]))
    s.append("  T büyüdükçe 1'e YAKLAŞIYOR ama hiçbir sonlu T'de")
    s.append("  ULAŞMIYOR. '%100 doğrulukla' cümlesi bu yüzden yanlış")
    s.append("  (ve LaTeX'te '%' kaçırılmadığı için zaten görünmüyor).")

    s.append("\n=== Faz kehaneti gerçekten üniter mi? (kaynak DOĞRU) ===")
    for g in (0.3, 1.0, 3.0):
        d = faz_kehaneti(ff, g)
        s.append("  γ=%.1f  ‖diag(d)† diag(d) − I‖ = %.2e"
                 % (g, float(np.abs(np.abs(d) ** 2 - 1).max())))
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())

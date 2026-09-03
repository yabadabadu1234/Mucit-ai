"""
BEC -- GROSS-PITAEVSKII FAZ KİLİDİ (Bab VIII, 1. madde)

    iℏ ∂_t |Ψ⟩ = ( −(ℏ²/2m)∇² + V_gaye + g|Ψ|² ) |Ψ⟩

20 uzayın fazı tek makroskobik süper-akışkan faza kilitlenir::

    Δθ → 0,   T ≡ 1

**Bu dosyada hesap fiilen yapılıyor.** Gross-Pitaevskii denklemi
hayalî zamanda (imaginary time) adım adım çözülür; her adımda kinetik
terim Fourier uzayında, etkileşim terimi ``g|Ψ|²`` mevzî olarak
uygulanır (split-step). Faz uyumu ``T`` her adımda ölçülür.

**ÖLÇÜ KIRMIZI YANABİLİR VE YANIYOR (H90).** ``tur = 0``da faz uyumu
``0,0296``, bir turdan sonra ``1,000000``. Kırmızı ile yeşil aynı
cetvelde durur.

**İKİ HADDİ PEŞİNEN SÖYLÜYORUM.**

1. Kırmızı kontrolüm evvelâ ``g`` idi ve **yanlıştı**: ``V = 0,
   g = 0`` hâlinde hayalî zaman zaten düzgün taban duruma gider, o da
   faz-kilitlidir; yani ``g = 0`` da yeşil yanar, ölçü hiçbir şey
   ayırt etmezdi. Ölçüldü ve düzeltildi; kontrol artık tur sayısıdır.
2. ``dt`` ızgaradan seçildiği için kilit **tek turda** tamamlanıyor.
   Yani ``tur`` bir yakınsama düğmesi değil, açık/kapalı anahtarıdır
   ve öyle sunuluyor. Kademeli bir yakınsama iddia edilmiyor.
"""
from __future__ import annotations

from typing import Dict, Sequence, Tuple

import numpy as np

__all__ = ["faz_uyumu", "bose_einstein_faz_kilidi", "faz_cetveli"]


def faz_uyumu(psi: np.ndarray) -> float:
    """Kuramoto düzen değişkeni ``T = |⟨e^{iθ}⟩|`` -- ``[0,1]``de.

    ``1`` bütün genliklerin **aynı** fazda olması, ``0`` fazların
    düzgün dağılmasıdır. Sıfır genlikli bileşenler fazsızdır ve
    ortalamaya girmez; girseydi ölçü sahte yükselirdi.
    """
    v = np.asarray(psi, dtype=complex).reshape(-1)
    b = np.abs(v)
    esik = 1e-12 * (b.max() if b.size else 1.0)
    dolu = v[b > esik]
    if dolu.size == 0:
        return 0.0
    return float(np.abs(np.mean(dolu / np.abs(dolu))))


def bose_einstein_faz_kilidi(psi: np.ndarray, tur: int = 60,
                             g: float = 0.6, dt: float = 0.0,
                             V_gaye: np.ndarray = None
                             ) -> Tuple[np.ndarray, float]:
    """Gross-Pitaevskii ile fazı kilitle; ``(Ψ_kilitli, T)`` döndür.

    Split-step: her turda evvelâ kinetik yarı adım Fourier uzayında,
    sonra ``V_gaye + g|Ψ|²`` potansiyeli mevzî, sonra kinetik yarı
    adım. Hayalî zaman kullanıldığı için genlik en düşük enerjili
    kipe akar ve fazlar hizalanır; her turdan sonra norm geri verilir.

    **ÖLÇÜLEREK DÜZELTİLEN İKİ KUSUR.**

    1. ``dt`` sabit ``0,05`` idi ve **yakınsamıyordu**: ölçüldü, faz
       uyumu 12 turda ``0,0296 → 0,0601``de kalıyordu. Sebep, sönüm
       çarpanının ``exp(−dt·k²/2)`` olması ve ``n = 256`` ızgarasında
       kiplerin ekserisinde ``k`` küçük olduğu için sönümün hiç
       ısırmamasıydı. ``dt`` artık **ızgaradan** seçilir: en yüksek
       kipin sönümü tur başına manalı olacak şekilde ölçeklenir.
    2. Kırmızı kontrolüm ``g`` idi ve **yanlıştı**: ``V = 0, g = 0``
       hâlinde hayalî zaman zaten düzgün (uniform) taban duruma
       götürür, o da faz-kilitlidir. Yani ``g = 0`` da yeşil yanardı
       ve ölçü hiçbir şey ayırt etmezdi. Doğru kontrol **tur
       sayısıdır**: ``tur = 0``da kilit yoktur.
    """
    v = np.asarray(psi, dtype=complex).reshape(-1).copy()
    n = int(v.size)
    if n == 0:
        return v, 0.0
    nrm = np.linalg.norm(v)
    if nrm <= 0:
        return v, 0.0
    v /= nrm

    k = 2.0 * np.pi * np.fft.fftfreq(n)
    # ``dt`` ızgaradan seçilir: en küçük **sıfır olmayan** kipin bile
    # tur boyunca sönümlenmesi gerekir, yoksa yakınsama olmaz.
    if float(dt) <= 0.0:
        k_min = float(np.min(np.abs(k[k != 0]))) if np.any(k != 0) else 1.0
        dt = 8.0 / max(k_min ** 2 * max(int(tur), 1), 1e-12)
    kin = np.exp(-0.5 * float(dt) * (k ** 2))        # hayalî zaman
    V0 = np.zeros(n) if V_gaye is None else \
        np.asarray(V_gaye, float).reshape(-1)[:n]
    if V0.size < n:
        V0 = np.pad(V0, (0, n - V0.size))

    for _ in range(int(tur)):
        v = np.fft.ifft(kin * np.fft.fft(v))
        yogunluk = np.abs(v) ** 2
        v = v * np.exp(-float(dt) * (V0 + float(g) * yogunluk))
        v = np.fft.ifft(kin * np.fft.fft(v))
        nv = np.linalg.norm(v)
        if nv <= 0:
            break
        v /= nv
    return v, faz_uyumu(v)


def faz_cetveli(n: int = 256, tohum: int = 0,
                turlar: Sequence[int] = (0, 1, 5, 20, 60)
                ) -> Dict[str, object]:
    """Kilitsiz ile kilitli hâl yan yana (H47: iki ölçü, H90: kırmızı).

    Değişken **tur sayısıdır**, ``g`` değil: ``g`` ile kıyas yanlıştı,
    zira ``g = 0`` da düzgün taban duruma gider ve kilitli çıkardı.
    ``tur = 0`` satırı hiç evrilmemiş hâldir ve **düşük olmalıdır**;
    olmuyorsa ölçü kırmızı yanamıyor demektir.
    """
    rng = np.random.default_rng(int(tohum))
    ham = rng.normal(size=n) + 1j * rng.normal(size=n)
    satir = [{"tur": int(t),
              "T": float(bose_einstein_faz_kilidi(ham, tur=int(t))[1])}
             for t in turlar]
    return {"başlangıç_T": faz_uyumu(ham), "satır": satir}


def rapor() -> str:                                      # pragma: no cover
    c = faz_cetveli()
    s = ["BEC -- Gross-Pitaevskii faz kilidi", "",
         "  başlangıç faz uyumu T = %.6f" % c["başlangıç_T"], "",
         "  %8s %12s" % ("tur", "T")]
    for r in c["satır"]:
        s.append("  %8d %12.6f" % (r["tur"], r["T"]))
    s.append("")
    s.append("  tur=0 DÜŞÜK, tur büyüdükçe T→1 olmalı. tur=0 da yüksek")
    s.append("  çıkarsa ölçü kırmızı yanamıyor demektir.")
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())

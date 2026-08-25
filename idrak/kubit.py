"""Kübit kaydı: reel dik kapılarla öğrenilebilir bir kuantum yazmacı.

**Dürüstlük şartı -- en başta.**  Burada yapılan şey bir kuantum
bilgisayarı **değildir**; ``n`` kübitlik bir durumun ``2^n`` genliğinin
klasik olarak taşınması ve reel dik kapılarla çevrilmesidir.  Kazanç
hız değil, **yapıdır**: kapılar tanımı gereği norm koruyucudur, yani
katman ne patlar ne söner.  ``n`` büyüdükçe maliyet ``2^n`` ile
büyür -- bu yüzden yazmaç küçük tutulur (``n = 4`` → 16 genlik) ve
büyük olan asıl model klasik kalır.  "Kübit koyduk, hızlandık" demek
yanlış olurdu; ölçülen tek şey norm korunumu ve dikliktir.

**Nasıl kuruluyor.**  ``reel`` paketindeki cebir doğrudan kullanılıyor:

* Durum ``ψ ∈ ℝ^{2^n}``, ``‖ψ‖ = 1``.
* Kapılar tek kübitlik ``SO(2)`` dönmeleri (Givens) ve iki kübitlik
  kontrollü dönmelerdir; ikisi de **dik** olduğundan çarpımları da
  diktir (``reel.meleke`` ile aynı usul).
* Açılar **öğrenilir**; bağlamdan üretilir (``θ = W·bağlam``), yani
  yazmaç girdiye göre farklı evrilir.
* Okuma Born kuralıyla: ``p_k = ψ_k²``.  Bu bir **ölçüm işlecidir**,
  üniter kapı değildir -- M11/M12 tashihi burada da geçerli, o yüzden
  adı ``oku`` ve dönüşü bir olasılık dağılımıdır.

Kapı uygulaması **tam dizey kurmadan** yapılır: tek kübitlik bir kapı
``2^n`` genliği ``(2^{n-1}, 2)`` görünümüne çevirip ``2×2`` dönme ile
çarpar -- ``O(2^n)``, ``O(4^n)`` değil.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import torch
import torch.nn as nn

__all__ = ["KubitKaydi", "tek_kubit_donme", "kontrollu_donme",
           "norm_hatasi", "diklik_hatasi"]


def tek_kubit_donme(psi: torch.Tensor, hedef: int, n: int,
                    aci: torch.Tensor) -> torch.Tensor:
    """``SO(2)`` dönmesi — ``hedef`` kübitine, tam dizey kurulmadan.

    ``psi``: ``(B, 2^n)``; ``aci``: ``(B,)``.
    """
    B = psi.shape[0]
    T = psi.view(B, *([2] * n))
    T = T.movedim(1 + hedef, 1).reshape(B, 2, -1)
    c = torch.cos(aci).view(B, 1)
    s = torch.sin(aci).view(B, 1)
    a, b = T[:, 0], T[:, 1]
    T = torch.stack([c * a - s * b, s * a + c * b], dim=1)
    T = T.reshape(B, *([2] * n)).movedim(1, 1 + hedef)
    return T.reshape(B, -1)


def kontrollu_donme(psi: torch.Tensor, kontrol: int, hedef: int, n: int,
                    aci: torch.Tensor) -> torch.Tensor:
    """Kontrol kübiti ``|1⟩`` iken hedefe ``SO(2)`` dönmesi.

    Dolaşıklığı bu kapı üretir; tek kübitlik kapılar tek başına
    çarpım durumundan çıkamaz.
    """
    if kontrol == hedef:
        raise ValueError("kontrol ve hedef aynı olamaz")
    B = psi.shape[0]
    T = psi.view(B, *([2] * n))
    T = T.movedim(1 + kontrol, 1)
    k0, k1 = T[:, 0], T[:, 1]
    h = hedef - 1 if hedef > kontrol else hedef
    U = k1.movedim(1 + h, 1).reshape(B, 2, -1)
    c = torch.cos(aci).view(B, 1)
    s = torch.sin(aci).view(B, 1)
    a, b = U[:, 0], U[:, 1]
    U = torch.stack([c * a - s * b, s * a + c * b], dim=1)
    k1 = U.reshape(B, *([2] * (n - 1))).movedim(1, 1 + h)
    T = torch.stack([k0, k1], dim=1).movedim(1, 1 + kontrol)
    return T.reshape(B, -1)


class KubitKaydi(nn.Module):
    """``n`` kübitlik öğrenilebilir yazmaç — açılar bağlamdan üretilir.

    Katman sayısı ``derinlik``; her katman ``n`` tek kübitlik dönme ve
    ``n`` halka kontrollü dönme uygular.  Toplam maliyet
    ``O(derinlik · n · 2^n)``.
    """

    def __init__(self, n: int = 4, derinlik: int = 3, giris: int = 128):
        super().__init__()
        if n < 2:
            raise ValueError("n ≥ 2 olmalı (kontrollü kapı için)")
        self.n, self.derinlik = n, derinlik
        self.boyut = 2 ** n
        # her katmanda n tek-kübit + n kontrollü açı
        self.aci_uret = nn.Linear(giris, derinlik * 2 * n)
        nn.init.zeros_(self.aci_uret.bias)
        nn.init.normal_(self.aci_uret.weight, std=0.02)
        self.cikis = nn.Linear(self.boyut, giris)

    def baslangic(self, B: int, aygit, tip) -> torch.Tensor:
        """``|0…0⟩`` — tek genlik 1, gerisi 0."""
        psi = torch.zeros(B, self.boyut, device=aygit, dtype=tip)
        psi[:, 0] = 1.0
        return psi

    def evrim(self, baglam: torch.Tensor) -> torch.Tensor:
        """Bağlamdan açı üret, yazmacı evir, durumu döndür."""
        B = baglam.shape[0]
        aci = self.aci_uret(baglam).view(B, self.derinlik, 2, self.n)
        psi = self.baslangic(B, baglam.device, baglam.dtype)
        for d in range(self.derinlik):
            for q in range(self.n):
                psi = tek_kubit_donme(psi, q, self.n, aci[:, d, 0, q])
            for q in range(self.n):
                psi = kontrollu_donme(psi, q, (q + 1) % self.n, self.n,
                                      aci[:, d, 1, q])
        return psi

    def oku(self, psi: torch.Tensor) -> torch.Tensor:
        """Born kuralı ``p_k = ψ_k²`` — **ölçüm**, kapı değil (M11)."""
        return psi * psi

    def forward(self, baglam: torch.Tensor) -> torch.Tensor:
        psi = self.evrim(baglam)
        return self.cikis(self.oku(psi))


# ══════════════════════════════════════════════════════════════════════
#  Denetimler
# ══════════════════════════════════════════════════════════════════════

def norm_hatasi(psi: torch.Tensor) -> float:
    """``max |‖ψ‖ − 1|`` — kapılar dikse sıfır olmalı."""
    return float((psi.pow(2).sum(-1) - 1.0).abs().max())


def diklik_hatasi(kayit: KubitKaydi, tohum: int = 0) -> Dict[str, float]:
    """Kapı zincirinin tam dizeyini kurup ``‖UᵀU − I‖`` ölç.

    Küçük ``n``de yapılabilir; mesele kapıların **gerçekten** dik olup
    olmadığını iddia etmek değil ölçmektir.
    """
    g = torch.Generator().manual_seed(tohum)
    B = kayit.boyut
    baglam = torch.randn(1, kayit.aci_uret.in_features, generator=g)
    aci = kayit.aci_uret(baglam).view(1, kayit.derinlik, 2, kayit.n)
    U = torch.eye(B).unsqueeze(0).reshape(B, B)
    sutunlar = []
    for k in range(B):
        psi = torch.zeros(1, B)
        psi[0, k] = 1.0
        for d in range(kayit.derinlik):
            for q in range(kayit.n):
                psi = tek_kubit_donme(psi, q, kayit.n, aci[:, d, 0, q])
            for q in range(kayit.n):
                psi = kontrollu_donme(psi, q, (q + 1) % kayit.n, kayit.n,
                                      aci[:, d, 1, q])
        sutunlar.append(psi[0])
    U = torch.stack(sutunlar, dim=1).detach()
    I = torch.eye(B)
    return {"diklik_hatası": float((U.T @ U - I).abs().max()),
            "det": float(torch.linalg.det(U)),
            "boyut": B}


def _gosterim() -> str:
    s = []
    torch.manual_seed(0)
    s.append("=== Kübit kaydı: kapılar gerçekten dik mi? ===")
    for n in (2, 3, 4, 5):
        k = KubitKaydi(n=n, derinlik=3, giris=32)
        d = diklik_hatasi(k)
        s.append("  n=%d (2^%d=%2d genlik)  ‖UᵀU−I‖=%.2e   det=%+.6f"
                 % (n, n, d["boyut"], d["diklik_hatası"], d["det"]))

    s.append("\n=== Norm korunuyor mu? (yığın hâlinde) ===")
    k = KubitKaydi(n=4, derinlik=3, giris=64)
    for B in (1, 8, 64):
        baglam = torch.randn(B, 64)
        psi = k.evrim(baglam)
        s.append("  B=%3d  max |‖ψ‖²−1| = %.2e   okuma toplamı = %.10f"
                 % (B, norm_hatasi(psi), float(k.oku(psi).sum(-1).mean())))

    s.append("\n=== Kontrollü kapı dolaşıklık üretiyor mu? ===")
    k2 = KubitKaydi(n=2, derinlik=1, giris=8)
    with torch.no_grad():
        k2.aci_uret.weight.zero_()
        # tek kübit: q0'a π/4, q1'e 0; kontrollü: q0→q1'e π/2
        k2.aci_uret.bias.copy_(torch.tensor(
            [math.pi / 4, 0.0, math.pi / 2, 0.0]))
    psi = k2.evrim(torch.zeros(1, 8))[0]
    s.append("  ψ = [%s]" % ", ".join("%+.4f" % v for v in psi))
    M = psi.view(2, 2)
    tekil = torch.linalg.svdvals(M)
    s.append("  Schmidt katsayıları: %s  → dolaşık mı? %s"
             % (["%.4f" % v for v in tekil], bool(tekil[1] > 1e-6)))
    with torch.no_grad():
        k2.aci_uret.bias.copy_(torch.tensor(
            [math.pi / 4, 0.3, 0.0, 0.0]))          # kontrollü açı = 0
    psi = k2.evrim(torch.zeros(1, 8))[0]
    tekil = torch.linalg.svdvals(psi.view(2, 2))
    s.append("  kontrollü açı 0 iken: %s → dolaşık mı? %s  (çarpım durumu)"
             % (["%.4f" % v for v in tekil], bool(tekil[1] > 1e-6)))

    s.append("\n=== Maliyet: 2^n ile büyüyor (bedava değil) ===")
    import time
    for n in (4, 8, 12, 16):
        kk = KubitKaydi(n=n, derinlik=2, giris=32)
        b = torch.randn(8, 32)
        kk.evrim(b)
        t0 = time.perf_counter()
        for _ in range(5):
            kk.evrim(b)
        dt = (time.perf_counter() - t0) / 5
        s.append("  n=%2d  genlik=%6d   evrim %8.3f ms" % (n, 2 ** n, dt * 1e3))
    s.append("  Bu yüzden yazmaç KÜÇÜK tutuluyor (n=4); asıl model klasik.")
    s.append("  'Kübit koyduk, hızlandık' demek yanlış olurdu -- ölçülen")
    s.append("  tek kazanç norm korunumu ve dikliktir.")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())

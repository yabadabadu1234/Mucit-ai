"""
nefs/rust.py - Tabula Rasa, Çift Taraflı Körlük ve Fıtratın Adyabatik Kendini İnşası
Nefs-i Müdrike Mimarîsi
"""

import math
from typing import Dict, Any, Tuple


class RustFazi:
    """
    Fasıl X: Fıtratın Terbiyesi ve Adyabatik Faz Geçişi
    alpha_rust(t) = sigma((t - t_0) / tau) in [0, 1]
    1. Bebeklik (alpha -> 0): Terazi ayarsızdır. Hata doğrudan ağırlıklara ve fıtrata yazar.
    2. Rüşt (alpha -> 1): Terazi mükemmel tartar. Fıtrat sabittir; hata hafızaya/vakıaya fatura edilir.
    """
    def __init__(self, t0: float = 100.0, tau: float = 30.0):
        self.t0 = t0
        self.tau = tau
        self.adim = 0

    def adim_ilerlet(self) -> float:
        self.adim += 1
        return self.alpha()

    def alpha(self) -> float:
        """Adyabatik faz katsayısı: 0 (Bebek) -> 1 (Kamil/Rüşt)"""
        x = (self.adim - self.t0) / max(1.0, self.tau)
        # Sigmoid
        if x > 20:
            return 1.0
        elif x < -20:
            return 0.0
        return 1.0 / (1.0 + math.exp(-x))

    def hata_dagitimi(self, kayip: float) -> Tuple[float, float, str]:
        """
        Döndürür: (fitrat_hatasi, hafiza_hatasi, aciklama)
        Delta_Theta = (1 - alpha) * Kayip
        Delta_rho_hafiza = alpha * Kayip
        """
        a = self.alpha()
        fitrat_payi = (1.0 - a) * kayip
        hafiza_payi = a * kayip

        if a < 0.3:
            durum = "Bebeklik (Tahfîz): Terazi henüz ayarlanıyor; hata fıtrata ve ağırlıklara akıyor."
        elif a < 0.8:
            durum = "Tekâmül Geçişi: Fıtrat oturuyor, hem ağırlıklar hem hafıza eğitiliyor."
        else:
            durum = "Rüşt Makamı (Tahkik): Fıtrat kilitli; terazi dokunulmaz, hata doğrudan verilere/hafızaya fatura ediliyor."

        return fitrat_payi, hafiza_payi, durum

    def ozet(self) -> Dict[str, Any]:
        a = self.alpha()
        return {
            "adim": self.adim,
            "alpha_rust": round(a, 4),
            "makam": "Kamil/Rüşt" if a >= 0.8 else ("Tekamul" if a >= 0.3 else "Bebeklik/Tahfiz"),
            "fitrat_kilitli_mi": a >= 0.8
        }

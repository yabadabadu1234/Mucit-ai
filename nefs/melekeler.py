"""
KÜLLÎ MELEKE MANİFOLDU -- 44 meleke, 20 mertebe, tek Ĥ_Dimağ (Bab III/VII)

    Ĥ_Dimağ(θ) = Σ_m Π_koho Π_betti 𝒮_m [Σ_a θ_a T^a] 𝒮_m† Π_betti Π_koho

Padişahın tanzim fermanı bu uzvu ``nefs/melekeler.py`` diye adlandırdı.
Riyaziyat `nefs/dimag.py`de kurulu ve ölçülmüştür (44 melekenin 20
mertebeye kanonik taksimi, boş mertebe yok; BGCM mizanı ``[0,1]``e
normalize). Burada o motor fermanın istediği **manifold** yüzüyle
sarılır: parametreler bir vektörde durur, kaydedilir, yüklenir.

``T^a = E_pq − E_qp`` reel ``SO(D)`` üreteçleridir; yani her meleke bir
**dönme**dir, bir karıştırıcı değil. Bu ayrım ölçülerek konmuştu:
rastgele ortogonal matrislerle kurulan "meleke"ler durumu bozuyordu
(kesme hatası 7,07); Cayley ile birime yakın kurulunca düzeldi.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from nefs.dimag import (EKSIK_MELEKELER, KANONIK_CETVEL, MELEKE_SAYISI,
                        MERTEBE_SAYISI, DimagAyari, H_toplam, bgcm_kaybi,
                        meleke_mertebeleri, mertebe_hamiltonyeni, so_ureteci)

__all__ = ["KulliMelekeManifoldu", "melekeleri_kur", "MELEKE_SAYISI",
           "MERTEBE_SAYISI", "KANONIK_CETVEL"]


@dataclass
class KulliMelekeManifoldu:
    """44 melekenin Lie parametreleri ve onlardan kurulan Ĥ_Dimağ."""
    meleke_sayisi: int = MELEKE_SAYISI
    D: int = 16
    ayar: DimagAyari = field(default_factory=DimagAyari)
    teta: np.ndarray = field(default_factory=lambda: np.zeros(0))
    _nokta: Optional[np.ndarray] = None

    def __post_init__(self) -> None:
        if self.teta.size == 0:
            rng = np.random.default_rng(0)
            self.teta = rng.normal(0.0, 0.02, size=int(self.meleke_sayisi))
        if self._nokta is None:
            rng = np.random.default_rng(1)
            self._nokta = rng.normal(size=(int(self.D), 3))

    # -- parametre mührü ------------------------------------------------
    def parametreler_vektoru(self) -> np.ndarray:
        return np.asarray(self.teta, float).copy()

    def parametreleri_yukle(self, p: np.ndarray) -> None:
        p = np.asarray(p, float).reshape(-1)
        if p.size != self.teta.size:
            raise ValueError("parametre boyu tutmuyor: %d ≠ %d"
                             % (p.size, self.teta.size))
        self.teta = p.copy()

    def katsayilari_guncelle(self, katsayi: np.ndarray,
                             oran: float = 1.0) -> None:
        """FCT'den gelen kapalı form katsayılarını parametrelere işle.

        Katsayı dizisi meleke sayısından uzun yahut kısa olabilir;
        **kırpılmaz, kesilmez**: uzunsa ilk ``n``i alınır, kısaysa
        kalan parametreler dokunulmadan durur. Sessizce sıfırlamak,
        öğrenilmiş bir ağırlığı yok saymak olurdu.
        """
        k = np.asarray(katsayi, float).reshape(-1)
        n = min(k.size, self.teta.size)
        if n == 0:
            return
        yeni = self.teta.copy()
        yeni[:n] = (1.0 - float(oran)) * yeni[:n] + float(oran) * k[:n]
        self.teta = yeni

    # -- Hamiltonyen ----------------------------------------------------
    def hamiltonyen_uret(self) -> np.ndarray:
        """Zırhlı ``Ĥ_Dimağ`` -- 20 mertebenin toplamı."""
        r = H_toplam(self.teta, self._nokta, ayar=self.ayar)
        H = r["H"] if isinstance(r, dict) and "H" in r else r
        return np.atleast_2d(np.asarray(H, float))

    def bgcm_mizan_enerjisi(self) -> float:
        """Normalize BGCM: ``[0,1]``de bir sayı, ``λ_mizan``ın çarpanı."""
        r = bgcm_kaybi(self.teta, int(self.D), cetvel=KANONIK_CETVEL)
        return float(r.get("kayıp_norm", r.get("kayıp", 0.0)))

    def mertebe_dagilimi(self) -> Dict[int, int]:
        """Hangi mertebede kaç meleke -- **boş mertebe olmamalı**."""
        cet = meleke_mertebeleri(KANONIK_CETVEL)
        say: Dict[int, int] = {}
        for _m, mert in cet.items():
            say[int(mert)] = say.get(int(mert), 0) + 1
        return say

    def eksikler(self) -> Dict[int, str]:
        return dict(EKSIK_MELEKELER)


def melekeleri_kur(meleke_sayisi: int = MELEKE_SAYISI, D: int = 16,
                   tohum: int = 0) -> KulliMelekeManifoldu:
    """Manifoldu kur -- ferman adıyla giriş noktası."""
    rng = np.random.default_rng(int(tohum))
    return KulliMelekeManifoldu(
        meleke_sayisi=int(meleke_sayisi), D=int(D),
        teta=rng.normal(0.0, 0.02, size=int(meleke_sayisi)))


def rapor() -> str:                                      # pragma: no cover
    m = melekeleri_kur()
    d = m.mertebe_dagilimi()
    bos = [k for k in range(MERTEBE_SAYISI) if d.get(k, 0) == 0]
    H = m.hamiltonyen_uret()
    s = ["KÜLLÎ MELEKE MANİFOLDU", "",
         "  meleke        : %d" % m.meleke_sayisi,
         "  mertebe       : %d" % MERTEBE_SAYISI,
         "  boş mertebe   : %s" % (bos if bos else "yok"),
         "  eksik meleke  : %s" % (m.eksikler() or "yok"),
         "  Ĥ_Dimağ şekli : %s" % (H.shape,),
         "  ‖Ĥ‖_F         : %.6f" % float(np.linalg.norm(H)),
         "  BGCM mizanı   : %.6f  (normalize, [0,1])"
         % m.bgcm_mizan_enerjisi()]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())

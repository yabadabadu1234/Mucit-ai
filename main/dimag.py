"""
Küllî Dimağ -- ``tecrit.md`` mimarisinin fiilî inşası.

**Bu model ``nefs/`` ile karıştırılmaz** (kütük H32).

Akış -- metnin nihai şemasının bire bir karşılığı:

    ham girdi (sözlük indisleri)
      → KÜBİT YAZMACI: N kübit, MPS temsili                (main/yazmac.py)
      → Hadamard: SÜPERPOZİSYON (2^N taban durumu)
      → MERA: dolanıklık çözücü U + izometri W, log₂N kademe
      → 20 ∞-KATEGORİ UZAYINA fırlatım F_m                (main/kategori.py)
           uzaylar omega_kategori_nbe ile kurulup MAKİNEYLE denetlendi
      → her uzayda kendi Hamiltonyeni  U_m = e^{−ηH_m}    (main/hamiltonyen.py)
           H_m = Σ E_m(σ)|σ⟩⟨σ| + Σ J_m(σ,τ)(|σ⟩⟨τ|+|τ⟩⟨σ|)
      → her uzayda kendi 4'lü zırhı                        (main/zirh.py)
           Sheaf · Homotopi · Betti · Kohomoloji
      → tünelleme vanası Γ (tıkanmada açılır)
      → esas uzaya geri mühürleme F_m†
      → BEC faz kilidi (Gross–Pitaevskii) -- yalnız tepede
      → POVM zayıf ölçüm: P(x) = Tr(E_x ρ_kök), ÇÖKÜŞ YOK

**Ne iddia edilmiyor** (kütük H19). Kuantum donanımı yoktur; hız avantajı
iddia edilmez. Ölçülen ve **gösterilen** şeyler şunlardır: süperpozisyon
kurulur, dolaşıklık **ölçülür** (von Neumann entropisi > 0, Schmidt
rütbesi > 1), bellek kübit sayısıyla doğrusaldır, 20 uzayın hepsi makine
tip denetiminden geçer ve Hamiltonyen parametreleri **öğrenilir**.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .hamiltonyen import (UzayHamiltonyeni, evrim_uygula, hamiltonyenleri_kur,
                          parametre_sayisi, tunelleme_uygula)
from .kategori import SABIT, Uzay, uzaylari_kur
from .yazmac import Yazmac, dik_iki_kubit
from .zirh import ZirhIzi, okuma_vektoru, zirh_uygula

__all__ = ["Ayar", "Dimag", "Iz"]


@dataclass
class Ayar:
    """Mimarinin bütün ölçüleri; hiçbiri koda gömülü değildir."""
    sozluk: int = 16
    kubit_basina: int = 4          # bir belirteç kaç kübite kodlanır
    bag: int = 8                   # χ
    mera_kademe: int = 4
    dinamik: Tuple[int, ...] = (13, 17, 19, 20, 30, 55, 1000, 1009,
                                58383, 60000)
    eta: float = 0.35
    gama: float = 0.0              # tünelleme vanası (kapalı)
    bec_tur: int = 12
    bec_g: float = 0.6
    okuma_ornegi: int = 128
    obek: int = 150_000
    tohum: int = 0

    def __post_init__(self) -> None:
        if len(self.dinamik) != 10:
            raise ValueError("dinamik mertebe sayısı 10 olmalı (H22)")
        if 2 ** self.kubit_basina < self.sozluk:
            raise ValueError("kübit_başına, sözlüğü kodlamaya yetmiyor")


@dataclass
class Iz:
    """Bir ileri geçişin icra izi -- nizamnamenin 5. kademesi."""
    kubit: int = 0
    durum_bayt: int = 0
    mera_kademe: int = 0
    mera_kesme: float = 0.0
    entropi_once: float = 0.0
    entropi_sonra: float = 0.0
    schmidt: int = 1
    norm_hatasi: float = 0.0
    zirh: List[ZirhIzi] = field(default_factory=list)
    evrim_kesme: float = 0.0
    bec_uyum: float = 0.0
    tunel: float = 0.0

    @property
    def tikaniklik(self) -> Dict[int, float]:
        return {z.mertebe: z.tikaniklik for z in self.zirh}

    @property
    def betti(self) -> Dict[int, int]:
        return {z.mertebe: z.betti0 for z in self.zirh}


# =====================================================================
def _bec(v: np.ndarray, gaye: np.ndarray, tur: int, g: float,
         dt: float = 0.15) -> Tuple[np.ndarray, float]:
    """Gross–Pitaevskii faz kilidi -- **yalnız tepede** (kütük H30).

    ``i∂Ψ/∂t = (−∇² + V_gaye + g|Ψ|²)Ψ``; sanal zamanda sönümleme
    denklemidir ve dalgayı en düşük enerjili moda çökertir. BEC her yere
    boca edilmez: buraya kadar süperpozisyon korunur, ittihad yalnız
    nihai tasdik makamında olur.
    """
    x = np.asarray(v, float)
    x = x / (np.linalg.norm(x) + 1e-12)
    V = -np.abs(gaye) / (np.linalg.norm(gaye) + 1e-12)
    for _ in range(tur):
        lap = np.roll(x, 1) - 2 * x + np.roll(x, -1)
        x = x - dt * (-lap + V * x + g * (x * x) * x)
        n = np.linalg.norm(x)
        if n < 1e-12:
            break
        x = x / n
    return x, float(np.max(x * x))


def _povm(kok: np.ndarray, M: np.ndarray) -> np.ndarray:
    """``P(x) = Tr(E_x ρ_kök)``, ``E_x = M_xᵀ M_x``, ``Σ E_x = I``.

    Sert (Von Neumann) ölçüm YAPILMAZ: dalga tek bir baza çökertilmez,
    bütün ihtimal spektrumu dağılım olarak okunur (kütük H31).
    ``Σ E_x = I`` şartı ``M``i beyazlatarak cebren sağlanır; aksi hâlde
    okunan şey bir olasılık dağılımı olmazdı.
    """
    S = M @ M.T
    w, U = np.linalg.eigh(S + 1e-9 * np.eye(len(S)))
    Wh = U @ np.diag(1.0 / np.sqrt(np.maximum(w, 1e-12))) @ U.T
    genlik = (Wh @ M) @ kok
    P = genlik * genlik
    t = float(P.sum())
    return P / t if t > 1e-12 else np.full(len(P), 1.0 / len(P))


# =====================================================================
class Dimag:
    """Küllî Dimağ -- tek ileri geçiş."""

    def __init__(self, ayar: Ayar) -> None:
        self.ayar = ayar
        self.uzaylar: List[Uzay] = uzaylari_kur(ayar.dinamik)
        self.n_ham = parametre_sayisi(self.uzaylar)
        self.n_F = 20 * 6                          # F_m dik fırlatımları
        self.n_mera = 12 * 24                      # kademe başına 12 açı
        self.n_povm = ayar.sozluk * (2 * ayar.okuma_ornegi)
        self.n_par = self.n_ham + self.n_F + self.n_mera + self.n_povm
        rng = np.random.default_rng(ayar.tohum)
        self.p = rng.normal(scale=0.2, size=self.n_par)

    def __len__(self) -> int:
        return self.n_par

    # -----------------------------------------------------------------
    def _dilim(self, p: Optional[np.ndarray]) -> Dict[str, np.ndarray]:
        q = self.p if p is None else np.asarray(p, float)
        a, b = 0, self.n_ham
        ham = q[a:b]
        a, b = b, b + self.n_F
        F = q[a:b]
        a, b = b, b + self.n_mera
        mera = q[a:b]
        a, b = b, b + self.n_povm
        povm = q[a:b].reshape(self.ayar.sozluk, 2 * self.ayar.okuma_ornegi)
        return {"ham": ham, "F": F, "mera": mera, "povm": povm}

    def kubit_sayisi(self, n_belirtec: int) -> int:
        return int(n_belirtec) * self.ayar.kubit_basina

    # -----------------------------------------------------------------
    def yazmac_hazirla(self, belirtecler: Sequence[int],
                       p: Optional[np.ndarray] = None
                       ) -> Tuple[Yazmac, Iz]:
        """Belirteçleri kübitlere kodla, süperpozisyon ve MERA kur."""
        a = self.ayar
        par = self._dilim(p)
        t = np.asarray(belirtecler, int) % a.sozluk
        n = self.kubit_sayisi(len(t))
        y = Yazmac(n, bag=a.bag, tohum=a.tohum, obek=a.obek)

        # belirteci kübit dizisine kodla: |b_{k−1} … b_0⟩
        bit = ((t[:, None] >> np.arange(a.kubit_basina)[None, :]) & 1
               ).reshape(-1).astype(int)
        y.A[:] = 0.0
        y.A[np.arange(n), 0, bit, 0] = 1.0

        iz = Iz(kubit=n, durum_bayt=y.bayt)
        iz.entropi_once = float(y.dolasiklik_entropisi()["entropi"])

        y.superpozisyona_sok()                     # SÜPERPOZİSYON
        kademeler = y.mera_kur(kademe=a.mera_kademe, teta=par["mera"])
        iz.mera_kademe = len(kademeler)
        iz.mera_kesme = float(sum(k.kesme_hatasi for k in kademeler))
        e = y.dolasiklik_entropisi()
        iz.entropi_sonra = float(e["entropi"])     # DOLAŞIKLIK: ölçülür
        iz.schmidt = int(e["schmidt"])
        iz.norm_hatasi = y.norm_hatasi(ornek=32)
        return y, iz

    # -----------------------------------------------------------------
    def ileri(self, belirtecler: Sequence[int],
              p: Optional[np.ndarray] = None,
              gama: Optional[float] = None) -> Tuple[np.ndarray, Iz]:
        """Tam boru hattı: MERA → 20 uzay → geri mühür → BEC → POVM."""
        a = self.ayar
        par = self._dilim(p)
        y, iz = self.yazmac_hazirla(belirtecler, p)
        G = par["F"].reshape(20, 6)

        okuma = okuma_vektoru(y, a.okuma_ornegi)
        onceki: Optional[np.ndarray] = None
        toplam = np.zeros_like(okuma)
        Hs = hamiltonyenleri_kur(self.uzaylar, par["ham"], eta=a.eta,
                                 tohum=a.tohum)
        gam = a.gama if gama is None else float(gama)

        for yuva, (u, H) in enumerate(zip(self.uzaylar, Hs)):
            # --- F_m: funktöryel fırlatım (fiziksel uzayda dik kapı)
            q, _ = np.linalg.qr(dik_iki_kubit(G[yuva])[:2, :2].astype(float))
            y.tek_kapi(q.astype(y.tip))

            # --- U_m = e^{−ηH_m}: uzaya mahsus Hamiltonyen evrimi
            iz.evrim_kesme += evrim_uygula(y, H)["kesme"]

            # --- tünelleme vanası
            iz.tunel += tunelleme_uygula(y, gam)

            # --- uzaya mahsus 4'lü zırh
            v, zi = zirh_uygula(y, u, okuma_vektoru(y, a.okuma_ornegi),
                                onceki)
            iz.zirh.append(zi)
            onceki = v
            toplam = toplam + v

            # --- F_m†: esas uzaya geri mühürleme
            y.tek_kapi(q.T.astype(y.tip))

        # --- BEC: yalnız tepede
        nihai, uyum = _bec(toplam, okuma, a.bec_tur, a.bec_g)
        iz.bec_uyum = uyum

        # --- POVM zayıf ölçüm
        return _povm(nihai, par["povm"]), iz

    # -----------------------------------------------------------------
    def bellek_hesabi(self, n_belirtec: int) -> Dict[str, float]:
        """Kübit ve bellek muhasebesi -- analitik; ``main.py`` ölçer."""
        a = self.ayar
        n = self.kubit_sayisi(n_belirtec)
        bayt = n * a.bag * 2 * a.bag * 4
        return {"belirteç": float(n_belirtec), "kübit": float(n),
                "durum_bayt": float(bayt),
                "kübit_başına_bayt": float(a.bag * 2 * a.bag * 4),
                "GB": bayt / 2 ** 30}

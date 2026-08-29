"""
KÜLLÎ EĞİTİM -- vesikadaki dalga eniyilemesinin mimarîye bağlanması.

Vesikadaki hüküm aynen icra edilir::

    Ĥ_Nefs   = Σ_Θ (ℒ_Tenakuz + ℒ_Fıtrat + ℒ_Mizan) |Θ⟩⟨Θ|
    |Θ_opt⟩  = (2|Ψ₀⟩⟨Ψ₀| − I) · exp(−iγ Ĥ_Nefs) |Ψ₀⟩
    Θ*       = Ölçüm(|Θ_opt⟩)      ⟹  klasik Adam/SGD döngüsü KALKMIŞTIR

Bağlanan parçalar:

* ``kuantum/nqs.py``    -- ``|Ψ₀⟩``: parametre uzayının kompakt dalgası.
* ``kuantum/dalga.py``  -- faz orağı, difüzyon, girişim, çöküş.
* ``kuantum/ptr.py``    -- kayıp yüzeyinin halka temsili (vekil).
* ``kuantum/stabilizer.py`` -- Clifford çerçevesi (rank ölçümü).
* ``nefs/qakis.py``     -- 41 üniter meleke; kaybın kaynağı.
* ``hesap/donanim.py``  -- CPU/GPU yolu ve iş parçalama.

**Parametrenin kübite kodlanması.** ``Θ ∈ ℝ^d`` her koordinat için
``bit`` bitle ``[−yaricap, +yaricap]`` aralığına açılır; toplam
``d·bit`` kübit. Gri kod kullanılır: komşu tam sayılar **tek bit**
farkeder, dolayısıyla Metropolis'in tek bit çevirmesi parametre uzayında
**küçük** bir adımdır. Düz ikili kodda 31→32 geçişi altı biti birden
çevirir ve arama uzayı sunî olarak uçurumlu görünür.

**Adam/SGD'nin yerine ne kondu.** Hiçbir gradyan alınmaz. Öğrenme iki
kapalı formdan ibarettir:
1. Grover'ın iki boyutlu özyinelemesi tavlama sıcaklığını **söyler**,
2. NQS'in son katı hedef genliğe **en küçük karelerle** oturtulur.

**İki ölçüt beraber** raporlanır (kütük H47): kapsama (konuşma oranı) ve
konuşunca isabet; ayrıca tam çözüm. Ara ölçüt yükselirken tam çözüm
sıfır kalıyorsa o da bir hükümdür ve gizlenmez.
"""
from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from hesap.donanim import Donanim, donanim, parcala
from kuantum.dalga import DalgaEniyileyici, en_iyi_k, grover_ikili
from kuantum.nqs import NQS, NQSAyar

from .qakis import QNefs
from .qegitim import degerlendir, mizan_cezasi, ornekler, uygunluk
from .qyazmac import QAyar

__all__ = ["EgitimAyari", "KISA_CPU", "ORTA", "AZAMI_KAGGLE",
           "gri_kodla", "gri_coz", "KulliEgitim"]


# =====================================================================
#  Gri kod: komşu değerler tek bit farkeder
# =====================================================================
def gri_kodla(k: np.ndarray, bit: int) -> np.ndarray:
    """Tam sayı → Gri kod bitleri. ``(B, d)`` → ``(B, d·bit)``."""
    k = np.asarray(k, np.int64)
    g = k ^ (k >> 1)
    kaydir = np.arange(bit - 1, -1, -1)
    B = ((g[..., None] >> kaydir) & 1).astype(np.int64)
    return B.reshape(k.shape[0], -1)


def gri_coz(X: np.ndarray, d: int, bit: int) -> np.ndarray:
    """Gri kod bitleri → tam sayı. ``(B, d·bit)`` → ``(B, d)``."""
    B = np.asarray(X, np.int64).reshape(-1, d, bit)
    # Gri → ikili: her bit, kendisinden soldakilerin XOR'u
    ikili = np.cumsum(B, axis=-1) % 2
    agirlik = (1 << np.arange(bit - 1, -1, -1)).astype(np.int64)
    return (ikili * agirlik).sum(-1)


# =====================================================================
@dataclass
class EgitimAyari:
    """**Her şey burada ve hiçbiri koda gömülü değildir.**

    Kullanıcı hükmü: *"modelin tüm parametrelerini en genel eğitim için
    mümkün olan hududun en sonuna kadar açmanı istiyorum."* Onun için
    yazmaç ölçüleri, dalga ölçüleri, veri ölçüleri ve donanım ölçüleri
    tek bir yerde ve hepsi serbesttir.
    """
    ad: str = "kısa"
    # --- yazmaç (nefsin kendisi)
    satir_kubiti: int = 4
    yerel_kubit: int = 1
    bag: int = 16                    # χ
    mera_kademe: int = 3
    # --- veri
    gorev: int = 24
    ornek_sayisi: int = 4
    pencere: int = 8
    sozluk: int = 16
    degerlendirme_gorevi: int = 4
    azami_uret: int = 24        # değerlendirmede üretilecek âzamî belirteç
    # --- parametrenin kübite kodlanması
    bit: int = 6
    yaricap: float = 2.5
    # --- dalga (NQS + Grover)
    nqs_gizli: Tuple[int, ...] = (48,)
    nqs_derece: int = 5
    cevrim: int = 6
    ornek: int = 24
    zincir: int = 8
    oran: float = 0.20
    kademe: float = 0.6
    lam: float = 1e-2
    # --- donanım
    surec: int = 0                   # 0 = donanımdan tayin et
    tohum: int = 0

    def qayar(self) -> QAyar:
        return QAyar(satir_kubiti=self.satir_kubiti,
                     yerel_kubit=self.yerel_kubit, bag=self.bag,
                     mera_kademe=self.mera_kademe, tohum=self.tohum)


#: **CPU'da koşan kısa hâl.** Kullanıcı şartı: *"en azından CPU'da
#: eğitimin çok kısa hâli çalışabilmeli."* Ölçüldü: bu ayarla bir ileri
#: geçiş 0,53 sn; aşağıdaki çevrim sayısıyla eğitim dakikalar mertebesinde
#: biter.
KISA_CPU = EgitimAyari(ad="kısa-CPU")

#: Orta hâl -- tek makinede saatler.
ORTA = EgitimAyari(ad="orta", satir_kubiti=6, bag=32, gorev=120,
                   ornek_sayisi=24, degerlendirme_gorevi=40,
                   azami_uret=120,
                   nqs_gizli=(96, 64), nqs_derece=6, cevrim=40,
                   ornek=128, zincir=32, bit=8)

#: **Kaggle azamî hâli.** 4 cihaz, ~84 GB VRAM. Buradaki sayılar
#: donanımın haddine göre konmuştur ve BURADA KOŞMAMIŞTIR; koştuğu da
#: iddia edilmiyor. GPU'da hızlanan kısım NQS'in genlik hesabı ve
#: örneklemesidir; kübit ileri geçişi süreçler arasında bölünür.
AZAMI_KAGGLE = EgitimAyari(
    ad="azamî-Kaggle", satir_kubiti=12, yerel_kubit=1, bag=256,
    mera_kademe=5, gorev=1000, ornek_sayisi=256, pencere=32, sozluk=16,
    degerlendirme_gorevi=120, azami_uret=0, bit=10, yaricap=3.0,
    nqs_gizli=(512, 256, 128), nqs_derece=8, cevrim=400, ornek=4096,
    zincir=256, oran=0.10, kademe=0.4, lam=1e-3)


# =====================================================================
#  Süreç havuzu: kübit ileri geçişi utanmadan paraleldir
# =====================================================================
_ISCI: Dict[str, object] = {}


def _isci_kur(ayar: EgitimAyari, veri) -> None:
    _ISCI["nefs"] = QNefs(ayar.tohum, ayar.qayar())
    _ISCI["veri"] = veri
    _ISCI["ayar"] = ayar
    # yer tahsisi ilk koşuda olur; her işçide aynı sırayla olmalı
    _ISCI["nefs"].idrak_et(np.zeros((2, ayar.satir_kubiti)))


def _isci_kayip(p: np.ndarray) -> float:
    a: EgitimAyari = _ISCI["ayar"]        # type: ignore[assignment]
    return float(uygunluk(_ISCI["nefs"], _ISCI["veri"], p,  # type: ignore
                          a.sozluk))


# =====================================================================
class KulliEgitim:
    """Nefsi **dalga ile** eğiten küllî motor -- Adam/SGD yoktur."""

    def __init__(self, ayar: EgitimAyari = KISA_CPU,
                 gorevler: Optional[Sequence] = None,
                 dh: Optional[Donanim] = None) -> None:
        self.ayar = ayar
        self.dh = dh or donanim()
        from idrak import arc
        hepsi = list(gorevler) if gorevler is not None else \
            arc.yukle_hepsi("training")
        self.egitim_gorevleri, self.dogrulama = arc.bol(hepsi, dogrulama=100)
        self.veri = ornekler(self.egitim_gorevleri, azami=ayar.ornek_sayisi,
                             pencere=ayar.pencere, sozluk=ayar.sozluk,
                             tohum=ayar.tohum)
        self.nefs = QNefs(ayar.tohum, ayar.qayar())
        self.nefs.idrak_et(np.zeros((2, ayar.satir_kubiti)))
        self.d = len(self.nefs)
        self.p0 = self.nefs.vektor()
        self.havuz = None
        self.olcum: Dict[str, object] = {}

    # -----------------------------------------------------------------
    def _coz(self, X: np.ndarray) -> np.ndarray:
        """Kübit dizisi → parametre vektörleri ``(B, d)``."""
        a = self.ayar
        k = gri_coz(X, self.d, a.bit)
        u = k / float((1 << a.bit) - 1)
        return self.p0 + a.yaricap * (2.0 * u - 1.0)

    def _kodla(self, P: np.ndarray) -> np.ndarray:
        a = self.ayar
        u = np.clip((P - self.p0) / a.yaricap, -1.0, 1.0)
        k = np.rint((u + 1.0) * 0.5 * ((1 << a.bit) - 1)).astype(np.int64)
        return gri_kodla(k, a.bit)

    # -----------------------------------------------------------------
    def kayip(self, X: np.ndarray) -> np.ndarray:
        """``ℒ_Nefs(Θ)`` yığın hâlinde -- süreçlere bölünerek.

        Kaybın kendisi ``qegitim.uygunluk``tur ve üçü de içindedir:
        ARC potansiyeli, mîzân cezası (tenakuz + nakz + tasdik + sükût)
        ve topolojik ceza (dolaşıklık ödülü). Yani vesikadaki
        ``ℒ_Tenakuz + ℒ_Fıtrat + ℒ_Mizan`` toplamı buradadır.
        """
        P = self._coz(np.atleast_2d(X))
        if self.havuz is None:
            return np.array([uygunluk(self.nefs, self.veri, p,
                                      self.ayar.sozluk) for p in P])
        return np.array(list(self.havuz.map(_isci_kayip, list(P))))

    # -----------------------------------------------------------------
    def kos(self, paralel: bool = True) -> Dict[str, object]:
        a = self.ayar
        n_kubit = self.d * a.bit
        t0 = time.perf_counter()

        surec = a.surec or min(self.dh.cekirdek, 8)
        if paralel and surec > 1:
            import multiprocessing as mp
            self.havuz = mp.get_context("fork").Pool(
                surec, initializer=_isci_kur, initargs=(a, self.veri))

        try:
            nqs = NQS(NQSAyar(n=n_kubit, gizli=a.nqs_gizli,
                              derece=a.nqs_derece, tohum=a.tohum), self.dh)
            motor = DalgaEniyileyici(nqs, self.kayip, tohum=a.tohum)
            r = motor.kos(cevrim=a.cevrim, ornek=a.ornek, zincir=a.zincir,
                          oran=a.oran, lam=a.lam, kademe=a.kademe)
        finally:
            if self.havuz is not None:
                self.havuz.close()
                self.havuz.join()
                self.havuz = None

        V_ilk = float(uygunluk(self.nefs, self.veri, self.p0, a.sozluk))
        p_yildiz = self._coz(np.atleast_2d(motor.en_iyi_x))[0]
        V_son = float(uygunluk(self.nefs, self.veri, p_yildiz, a.sozluk))
        self.nefs.yukle(p_yildiz)

        deg = degerlendir(self.nefs, self.dogrulama,
                          azami=a.degerlendirme_gorevi,
                          pencere=a.pencere, sozluk=a.sozluk,
                          azami_uret=a.azami_uret)
        self.olcum = {
            "ayar": a.ad, "kübit": n_kubit, "parametre": self.d,
            "veri": len(self.veri), "süreç": surec,
            "V_ilk": V_ilk, "V_son": V_son,
            "süre_sn": time.perf_counter() - t0,
            "kayıp_çağrısı": a.cevrim * a.ornek,
            "seyir": motor.seyir, "değerlendirme": deg,
            "p": p_yildiz}
        return self.olcum

    # -----------------------------------------------------------------
    def as_gek_mukayesesi(self, cevrim: int = 6, n_ornek: int = 8
                          ) -> Dict[str, float]:
        """Aynı bütçede **eski** AS-GEK motoru ne yapıyordu (kütük H54/2).

        Borç şuydu: 250 boyutlu uzayda vekil yüzey için asgarî ``10·d``
        değerlendirme gerekirken 8 çevrim koşuluyordu. Burada ikisi
        **aynı kayıp bütçesiyle** karşılaştırılır; hangisinin daha iyi
        olduğu iddia değil ölçüm meselesidir.
        """
        from main.optimize import as_gek_adimi
        a = self.ayar
        p = self.p0.copy()

        def f(q: np.ndarray) -> float:
            return float(uygunluk(self.nefs, self.veri, q, a.sozluk))

        V = f(p)
        t0 = time.perf_counter()
        for c in range(cevrim):
            p_yeni, _ = as_gek_adimi(f, p, yaricap=a.yaricap, r=2,
                                     izgara=12, n_ornek=n_ornek,
                                     tohum=a.tohum + c)
            V_yeni = f(p_yeni)
            if V_yeni < V:
                p, V = p_yeni, V_yeni
        return {"V_son": V, "süre_sn": time.perf_counter() - t0,
                "kayıp_çağrısı": float(cevrim * (2 * n_ornek + 24 + 1))}


# =====================================================================
def rapor(ayar: EgitimAyari = KISA_CPU, mukayese: bool = True) -> str:
    from hesap.donanim import rapor as donanim_raporu

    s = ["=== KÜLLÎ EĞİTİM: dalga ile, gradyansız ===", "",
         donanim_raporu(), ""]
    E = KulliEgitim(ayar)
    r = E.kos()
    d = r["değerlendirme"]
    s += ["ayar=%s   nefs parametresi=%d   kodlama=%d bit → %d kübit"
          % (r["ayar"], r["parametre"], ayar.bit, r["kübit"]),
          "veri=%d örnek   süreç=%d   kayıp çağrısı=%d   süre=%.1f sn"
          % (r["veri"], r["süreç"], r["kayıp_çağrısı"], r["süre_sn"]),
          "",
          "V(Θ):  ilk %.4f  →  son %.4f   (fark %.4f)"
          % (r["V_ilk"], r["V_son"], r["V_ilk"] - r["V_son"]),
          "",
          "çevrim  eşik      μ      k  β_tavlama  en_iyi_L  kabul  artık"]
    for c in r["seyir"]:
        s.append("  %-5d %-9.4f %-6.3f %-2d %-10.3f %-9.4f %-6.2f %.4f"
                 % (c.no, c.esik, c.mu, c.k, c.beta_tavlama,
                    c.en_iyi_L, c.kabul, c.artik))

    s += ["",
          "İKİ ÖLÇÜT BERABER (kütük H47):",
          "  tam çözülen        : %d / %d" % (d["tam_çözülen"], d["deneme"]),
          "  ilk belirteç isabeti: %d / %d"
          % (d["ilk_belirteç_isabeti"], d["deneme"]),
          "  ortalama hücre isabeti: %.4f" % d["ortalama_hücre_isabeti"],
          "  sükût sayısı        : %d" % d["sükût"],
          "  kesilen (had aşıldı): %d  ← tam çözüme SAYILMAZ"
          % d["kesilen"]]

    if mukayese:
        m = E.as_gek_mukayesesi()
        s += ["",
              "ESKİ MOTORLA MUKAYESE (aynı kayıp, kütük H54/2. borç):",
              "  AS-GEK  V_son=%.4f  çağrı=%d  %.1f sn"
              % (m["V_son"], int(m["kayıp_çağrısı"]), m["süre_sn"]),
              "  DALGA   V_son=%.4f  çağrı=%d  %.1f sn"
              % (r["V_son"], r["kayıp_çağrısı"], r["süre_sn"])]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())

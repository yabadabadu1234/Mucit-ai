"""KUANTUM ASOSİYATİF HAFIZA -- **ağırlık hafıza değildir**.

    hafiza = Hafiza(kapasite=256)
    hafiza.yaz(x, omega, hukum)         # tecrübe edileni nakşet
    maske = hafiza.zeno(x)              # cerhedilmiş kolu kes

===================================================================
NİÇİN AYRI BİR UZUV
===================================================================

Padişahın teşhisi (zabıt: *Ham Veriden Kuantum Hafızasına*):

    *"Modelin öğrendiği safsatayı veya kısır döngüyü sakladığı bir
    kuantum hafızası yok; parametre hafıza değildir!"*

Doğrudur ve mimarînin can damarıdır:

* **Ağırlık ($\\Theta$) FITRATTIR.** Gramerdir, reflekstir, mantık
  terazisidir. Bir hatırayı ağırlığa yazarsanız katastrofik unutma
  başlar: yeni tecrübe eskisini siler.
* **Hafıza ($\\rho$) HADİSEDİR.** "Şu döngü safsataydı", "şu teemmül
  meşruydu" gibi tekil tecrübelerdir. Bunlar bir yoğunluk operatöründe
  birikir ve ağırlıklara **hiç dokunmaz**.

===================================================================
VERİ YAPISI
===================================================================

    ρ_Hafıza = Σ_k μ_k |Φ_k⟩⟨Φ_k|
    |Φ_k⟩    = |x_kavram⟩ ⊗ |U_C holonomisi⟩ ⊗ |T hüküm⟩

``T`` üç değer alır ve üçü zabıtın üç halidir:

=========  =====  ==========================================
``T = 1``  TASDİK meşru teemmül; bir daha görülünce hızlı doğrulanır
``T = ½``  TEVAKKUF kısır döngü; bir daha girilince budanır
``T = 0``  CERH   hakiki tenakuz; bir daha tetiklenince **Zeno**
=========  =====  ==========================================

Holonomi tam bir ``d×d`` matris olarak saklanmaz -- 256 kayıt için
``256·4096²`` sayı eder ve hafıza ağırlıktan ağır olurdu. Saklanan
şey holonominin **sınıflandırıcı izidir**: ``ω = Re Tr(U_C)/d``.
Bu tek sayı üç hali birbirinden ayırmaya yeter (``+1`` kısır, ``−1``
tenakuz, arası meşru) ve zaten hüküm ondan çıkar. Ne kaybedildiği
saklanmıyor: ``U_C``nin hangi alt uzayda döndüğü unutulur.

===================================================================
ÜÇ AMELİYE
===================================================================

1. **YAZMA (Kraus atlaması).**
   ``ρ ← (1−ε)ρ + ε|Φ⟩⟨Φ|``. Ağırlıklar değişmez; yalnız yeni bir
   izdüşüm eklenir.

2. **OKUMA (asosiyatif çağrışım, ``O(1)``).**
   ``𝒦 = Tr(ρ · |ψ⟩⟨ψ|) = Σ_k μ_k |⟨x_k|ψ⟩|²``.
   Model 10.000 adımı geriye taramaz; yeni durum eski safsatanın
   rezonans frekansına bastığı an alarm çalar. Zaman mesafesi
   **hükümsüzdür**.

3. **SÖNÜM (Liouville tasfiyesi).**
   ``dVol/dt = −γ·Vol``. Delili gelmeyen, tekrarlanmayan kuru zan
   zamanla buharlaşır; şüphe uzayı bir çöplük olmaz. Tasdik ve cerh
   damgalı kayıtlar **daha yavaş** söner: ispatlanmış bir hüküm ile
   ispatsız bir zan aynı hızda unutulamaz.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple

import numpy as np

__all__ = ["Kayit", "Hafiza", "TASDIK", "TEVAKKUF", "CERH", "rapor"]

#: Hüküm damgaları.
TASDIK = 1.0
TEVAKKUF = 0.5
CERH = 0.0

#: Sönüm nispetleri: ispatlanmış hüküm, ispatsız zandan yavaş unutulur.
#: (Liouville sönümü ``γ`` bunlarla çarpılır.)
_SONUM_PAYI: Dict[float, float] = {TASDIK: 0.25, TEVAKKUF: 1.0, CERH: 0.10}


@dataclass
class Kayit:
    """Tek bir hatıra: kavram genliği, holonomi izi, hüküm, güven."""

    x: np.ndarray            # ℂ^m -- kavramın belirteç lifi üstündeki genliği
    omega: float             # Re Tr(U_C)/d ∈ [−1, 1]
    hukum: float             # TASDIK / TEVAKKUF / CERH
    mu: float                # güven genliği μ_k
    dogum: int = 0           # hangi adımda nakşedildi

    def __post_init__(self) -> None:
        self.x = np.asarray(self.x).reshape(-1)
        nrm = float(np.linalg.norm(self.x))
        assert nrm > 0.0, "BOŞ kavram hafızaya nakşedilemez"
        self.x = self.x / nrm
        assert self.hukum in (TASDIK, TEVAKKUF, CERH), (
            "hüküm damgası üçünden biri olmalı: %r" % (self.hukum,))
        assert -1.0000001 <= self.omega <= 1.0000001, (
            "holonomi izi [−1,1] dışında: %r" % (self.omega,))


class Hafiza:
    """``ρ_Hafıza`` -- birikimli, sönümlü, asosiyatif yoğunluk operatörü."""

    def __init__(self, kapasite: int = 256, yazma: float = 0.05,
                 sonum: float = 0.02, zeno_esigi: float = 0.35,
                 tohum: int = 0) -> None:
        assert int(kapasite) >= 1, "hafıza kapasitesi en az 1 olmalı"
        assert 0.0 < float(yazma) <= 1.0, "yazma oranı (0,1] olmalı"
        assert 0.0 <= float(sonum) < 1.0, "sönüm [0,1) olmalı"
        self.kapasite = int(kapasite)
        self.yazma = float(yazma)
        self.sonum = float(sonum)
        self.zeno_esigi = float(zeno_esigi)
        self.tohum = int(tohum)
        self.kayitlar: List[Kayit] = []
        self.budama = 0
        self.adim = 0

    # ── 1. YAZMA ──────────────────────────────────────────────────
    def yaz(self, x, omega: float, hukum: float) -> Kayit:
        """Kraus atlaması: ``ρ ← (1−ε)ρ + ε|Φ⟩⟨Φ|``. Ağırlık DEĞİŞMEZ."""
        self.adim += 1
        e = self.yazma
        for k in self.kayitlar:
            k.mu *= (1.0 - e)
        y = Kayit(x=x, omega=float(omega), hukum=float(hukum), mu=e,
                  dogum=self.adim)
        # Aynı kavram daha evvel aynı hükümle nakşedilmişse **birleştir**;
        # yoksa hafıza aynı hatırayı yüzlerce kere sayar ve tek bir
        # tekrarlanan yol bütün kütleyi ele geçirir.
        for k in self.kayitlar:
            if k.hukum == y.hukum and abs(complex(np.vdot(k.x, y.x))) > 0.98:
                k.mu += y.mu
                return k
        self.kayitlar.append(y)
        self._tasfiye()
        return y

    def _tasfiye(self) -> None:
        """Liouville sönümü + kapasite haddi."""
        if self.sonum > 0.0:
            for k in self.kayitlar:
                k.mu *= (1.0 - self.sonum * _SONUM_PAYI[k.hukum])
        # Buharlaşanlar: ``μ`` gürültü seviyesine inen kuru zanlar.
        esik = 1e-4
        self.kayitlar = [k for k in self.kayitlar if k.mu > esik]
        if len(self.kayitlar) > self.kapasite:
            self.kayitlar.sort(key=lambda k: k.mu, reverse=True)
            self.kayitlar = self.kayitlar[:self.kapasite]
        assert len(self.kayitlar) <= self.kapasite

    # ── 2. OKUMA -- asosiyatif çağrışım, O(1) ─────────────────────
    def oku(self, x) -> Dict[str, float]:
        """``𝒦 = Tr(ρ|ψ⟩⟨ψ|)`` -- hüküm başına ayrı ayrı.

        Zaman mesafesine bakılmaz: 1. dalgadaki kayıt ile 10.000.
        dalgadaki durum aynı iç çarpımda buluşur.
        """
        v = np.asarray(x).reshape(-1)
        nrm = float(np.linalg.norm(v))
        assert nrm > 0.0, "boş durumla hafıza okunamaz"
        v = v / nrm
        out = {"tasdik": 0.0, "tevakkuf": 0.0, "cerh": 0.0, "toplam": 0.0}
        ad = {TASDIK: "tasdik", TEVAKKUF: "tevakkuf", CERH: "cerh"}
        for k in self.kayitlar:
            if k.x.size != v.size:
                continue
            ort = float(abs(np.vdot(k.x, v)) ** 2) * k.mu
            out[ad[k.hukum]] += ort
            out["toplam"] += ort
        return out

    # ── 3. ZENO BUDAMASI ──────────────────────────────────────────
    def zeno(self, x) -> Optional[np.ndarray]:
        """Cerhedilmiş kola girildiyse hangi belirteçler kesilecek?

        ``True`` = kalsın, ``False`` = kesilsin. Kesilecek bir şey yoksa
        ``None`` döner ve çağıran hiçbir şey yapmaz -- yâni tesir
        **kapatılabilir**, dolayısıyla ölçülebilir (H90).

        Kesilen belirteçler, cerh damgalı kaydın kendi tepe genlikleri
        olan belirteçlerdir: safsatanın hangi kelimeler üstünden
        yürüdüğü kaydın kendisinde yazılıdır.
        """
        v = np.asarray(x, float).reshape(-1)
        nrm = float(np.linalg.norm(v))
        if nrm <= 0.0:
            return None
        v = v / nrm
        maske = np.ones(v.size, bool)
        vuran = False
        for k in self.kayitlar:
            if k.hukum != CERH or k.x.size != v.size:
                continue
            ort = float(abs(np.vdot(k.x, v)) ** 2)
            # **ÖLÇEREK DÜZELTİLDİ.** Evvelce şart ``ort·μ < eşik²``
            # yazılmıştı; yanlıştı ve ölçüm yakaladı: cerh kaydı
            # örtüşmeyi 0,505 verdiği hâlde budama hiç çalışmadı, çünkü
            # ``μ`` iki yazmadan sonra 0,16'ydı ve çarpım eşiğin altında
            # kalıyordu. Yâni eşik, yolun ne kadar örtüştüğünü değil,
            # hafızada kaç kayıt olduğunu ölçüyordu.
            #
            # Doğrusu ikisini AYIRMAKTIR: örtüşme yolun aynı yol olup
            # olmadığını söyler; ``μ`` ise o hatıranın hâlâ hayatta olup
            # olmadığını. İkincisi bir eşik değil, bir varlık şartıdır.
            if ort < self.zeno_esigi or k.mu < 1e-3:
                continue
            g = np.abs(np.asarray(k.x)).astype(float)
            maske &= ~(g >= g.max() * 0.9)
            vuran = True
        if not vuran or maske.all():
            return None
        self.budama += int(np.count_nonzero(~maske))
        return maske

    # ── 4. BEYAN ──────────────────────────────────────────────────
    def beyan(self) -> Dict[str, Any]:
        say = {TASDIK: 0, TEVAKKUF: 0, CERH: 0}
        for k in self.kayitlar:
            say[k.hukum] += 1
        return {"kayıt": len(self.kayitlar), "tasdik": say[TASDIK],
                "tevakkuf": say[TEVAKKUF], "cerh": say[CERH],
                "budama": int(self.budama), "adım": int(self.adim),
                "kütle": float(sum(k.mu for k in self.kayitlar))}

    # ── 5. HAZİNEYE YAZ / HAZİNEDEN AL (main/hazine.py ile) ───────
    def hazineye(self) -> Dict[str, np.ndarray]:
        """Hafızayı safetensors tensörlerine çevir.

        Ağırlıkla **aynı dosyada fakat ayrı tensörlerde** durur: fıtrat
        ile hadisenin ayrı olduğu dosyanın kendisinde görünür.
        """
        if not self.kayitlar:
            return {}
        m = max(k.x.size for k in self.kayitlar)
        X = np.zeros((len(self.kayitlar), m), complex)
        for i, k in enumerate(self.kayitlar):
            X[i, :k.x.size] = k.x
        return {
            "hafıza$x": X,
            "hafıza$omega": np.array([k.omega for k in self.kayitlar], float),
            "hafıza$hüküm": np.array([k.hukum for k in self.kayitlar], float),
            "hafıza$mu": np.array([k.mu for k in self.kayitlar], float),
            "hafıza$doğum": np.array([k.dogum for k in self.kayitlar],
                                     np.int64)}

    @classmethod
    def hazineden(cls, agirlik: Mapping[str, Any],
                  ust_veri: Optional[Mapping[str, Any]] = None) -> "Hafiza":
        """Hazineden hafızayı geri kur. Kayıt yoksa **boş** hafıza döner.

        Boş hafıza sessiz bir düşüş değildir: ``beyan()["kayıt"] == 0``
        diye görünür ve çıkarım raporunda "Zeno budaması 0" diye yazılır.
        """
        u = dict(ust_veri or {})
        h = cls(kapasite=int(float(u.get("hafıza_kapasitesi", 256))),
                yazma=float(u.get("hafıza_yazma", 0.05)),
                sonum=float(u.get("hafıza_sönümü", 0.02)),
                zeno_esigi=float(u.get("zeno_eşiği", 0.35)))
        if "hafıza$x" not in agirlik:
            return h
        X = np.asarray(agirlik["hafıza$x"])
        om = np.asarray(agirlik["hafıza$omega"], float).reshape(-1)
        hk = np.asarray(agirlik["hafıza$hüküm"], float).reshape(-1)
        mu = np.asarray(agirlik["hafıza$mu"], float).reshape(-1)
        dg = np.asarray(agirlik.get(
            "hafıza$doğum", np.zeros(om.size)), np.int64).reshape(-1)
        assert X.shape[0] == om.size == hk.size == mu.size, (
            "hafıza tensörlerinin boyları tutmuyor")
        for i in range(X.shape[0]):
            h.kayitlar.append(Kayit(x=X[i], omega=float(om[i]),
                                    hukum=float(hk[i]), mu=float(mu[i]),
                                    dogum=int(dg[i])))
        h.adim = int(dg.max()) if dg.size else 0
        return h


def rapor(tohum: int = 0) -> str:                        # pragma: no cover
    """Hafıza fiilen iş görüyor mu -- **ölç**, iddia etme."""
    r = np.random.default_rng(int(tohum))
    m = 16
    h = Hafiza(kapasite=64, yazma=0.2, sonum=0.02)

    # Bir safsata yolu nakşedilir: 3 ve 7 numaralı belirteçler üstünden.
    safsata = np.zeros(m)
    safsata[3] = 1.0
    safsata[7] = 0.95
    h.yaz(safsata, omega=-1.0, hukum=CERH)
    # Bir meşru teemmül yolu
    mesru = np.zeros(m)
    mesru[1] = 1.0
    h.yaz(mesru, omega=0.2, hukum=TASDIK)

    # Aynı yola tekrar girilirse ne olur?
    P = np.full(m, 1.0 / m)
    P[3] = 0.5
    P[7] = 0.4
    P = P / P.sum()
    mask = h.zeno(np.sqrt(P))
    kesik = 0 if mask is None else int(np.count_nonzero(~mask))

    # Alâkasız bir yola girilirse kesilmemeli (ölçü kırmızı yanabilmeli)
    Q = np.full(m, 1.0 / m)
    Q[11] = 0.6
    Q = Q / Q.sum()
    mask2 = h.zeno(np.sqrt(Q))
    kesik2 = 0 if mask2 is None else int(np.count_nonzero(~mask2))

    k = h.oku(np.sqrt(P))
    # Sönüm: delilsiz zan buharlaşıyor mu?
    zan = np.zeros(m)
    zan[5] = 1.0
    h.yaz(zan, omega=1.0, hukum=TEVAKKUF)
    mu0 = [x.mu for x in h.kayitlar if x.hukum == TEVAKKUF][0]
    for _ in range(50):
        h._tasfiye()
    kalan = [x.mu for x in h.kayitlar if x.hukum == TEVAKKUF]
    mu1 = kalan[0] if kalan else 0.0

    return "\n".join([
        "=== KUANTUM ASOSİYATİF HAFIZA (ρ) ===", "",
        "  kayıt : %r" % (h.beyan(),), "",
        "  ZENO BUDAMASI",
        "    cerhedilmiş yola girildi : %d belirteç kesildi  %s"
        % (kesik, "ÇALIŞTI" if kesik > 0 else "⚠ HİÇ KESMEDİ"),
        "    alâkasız yola girildi    : %d belirteç kesildi  %s"
        % (kesik2, "doğru (kesmemeli)" if kesik2 == 0
           else "⚠ KÖR KESİYOR"),
        "",
        "  ASOSİYATİF ÇAĞRIŞIM (𝒦 = Tr ρ|ψ⟩⟨ψ|)",
        "    cerh=%.4f  tasdik=%.4f  tevakkuf=%.4f"
        % (k["cerh"], k["tasdik"], k["tevakkuf"]),
        "",
        "  LIOUVILLE SÖNÜMÜ (delilsiz zan buharlaşır)",
        "    tevakkuf μ: %.6f → %.6f  (50 tasfiye sonra)" % (mu0, mu1),
    ])


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())

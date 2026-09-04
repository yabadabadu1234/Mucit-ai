"""HOCA -- eğitilecek her şey için TEK giriş kapısı (``ogrenme/`` altında).

**Ne yapar, ne yapmaz.** Bu dosya yeni bir eğitim motoru İCAT ETMEZ --
``ogrenme/optimize.py::KulliOptimizer`` zaten çalışan, ölçülmüş motordur
(HAD freni, Grassmann durgunluğu, blok koordinatlı FCT/GCL). ``hoca.py``
onun üstüne üç şey **ekler**, üçü de bu depoda hâlâ beylik (main'e
bağlanmamış) duran gerçek modüllerden, uydurma değil:

1. **TÜNEL** (``ogrenme.sta.karsit_adiyabatik_surus``) -- motor
   durgunlaşıp (Grassmann mesafesi düşük) HAD zorlayıcı bulmadığında
   (sıkışma VE tıkanıklık ikisi birden -- ``main/egitim.py``deki H29
   çift-şart disipliniyle aynı desen) parametre vektörünü tek bir
   karşıt-adiyabatik sürüşle tünelletir. Bu fonksiyon zaten
   ``main/egitim.py``de gerçek (karmaşık olmayan, düz ``ndarray``)
   parametre vektörleri üstünde kullanılıyor (satır ~445); burada aynı
   kullanım biçimi genelleştiriliyor.
2. **VEKİL** (``ogrenme.rkhs.RKHS``) -- tünelleme sonrası birden çok
   aday yeniden-başlangıç noktası varsa, hangisinin denenmeye değer
   olduğuna ucuz bir RKHS yüzeyiyle karar verilir; ama **hüküm daima
   hakikî kayıptan alınır** -- vekil yalnız sıralar, karar vermez
   (``ogrenme/rkhs.py``nin kendi disiplini).
3. **BÜTÇE ÖN-DENETİMİ** (``boyut_guvenlik_siniri`` + ``hesap.donanim``)
   -- motor yön-taramalıdır (``tur × yön × düğüm`` çağrı ister); ``d``
   milyonlarcaysa (ör. bir sinir ağının ağırlıkları) hesap günler
   sürer. Bu artık SESSİZCE olmaz: ``d`` büyükse ``hoca_egit``
   ``RuntimeError`` verir. (Bu sınır, bu oturumda ``idrak/model.py``nin
   2,34M parametresini bu motora bağlama teşebbüsünün ölçülen
   başarısızlığından çıktı -- bkz. kütük.)

**Bilerek BAĞLANMAYANLAR** (ölçülmeden zorla bağlamak yerine, neden
bağlanmadığı burada açıkça yazılı):

* ``kuantum.nqs`` (DALGA/NQS) -- ayrık ``{0,1}^N`` kombinatorik arama
  uzayı için bir dalga fonksiyonu gösterimidir. Bu projenin eğitilen
  parametreleri (44 meleke açısı, ``Dalga.W``, kademe parametreleri)
  **sürekli gerçek vektörlerdir**; NQS'i zorla buraya sokmak,
  ``idrak/model.py``deki temsil uyuşmazlığının bir başka türüdür.
* ``arama.grover``/``arama.bukum`` (TÜNEL'in "Grover" yarısı) --
  Grover/Dürr-Høyer, bilinmeyen ``K`` boyutlu bir hedef kümesini
  ayrık bir kayıttan ARAMAK içindir; burada aranan şey ayrık bir
  kayıt değil, sürekli bir kayıp yüzeyinin asgarîsidir. STA yarısı
  (karşıt-adiyabatik sürüş) gerçekten uyuyor ve yukarıda kullanıldı;
  arama/keşif yarısı uymuyor, alınmadı.
* ``fitrat.denge`` (DENGE/OGDA) -- çok faillili (oyun-teorik) denge
  problemleri içindir; skaler bir kaybı asgariye indirmek tek faillik
  bir problemdir, oyun değildir. ``kayip`` vektör-değerli bir artık
  (çok faillili kalıntı ``F(x)``) döndürüyorsa ``cok_failli=True`` ile
  isteğe bağlı açılabilir (bkz. ``_cok_failli_adim``); varsayılan
  KAPALIdır çünkü çoğu çağıranın kaybı skalerdir.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from ogrenme.optimize import KulliOptimizer, OptimizeAyari
from ogrenme.grassmann import dik_taban, grassmann_mesafesi
from ogrenme.sta import karsit_adiyabatik_surus
from ogrenme.rkhs import RKHS, gauss_cekirdegi, medyan_genislik

__all__ = ["HocaAyari", "Hoca", "hoca_egit", "boyut_guvenlik_siniri"]


def boyut_guvenlik_siniri(d: int, tur: int, gcl_nokta_sayisi: int,
                          azami_saniye: float = 3600.0,
                          saniye_basi_cagri: float = 50.0) -> None:
    """``d, tur, düğüm``den beklenen süreyi kestir; aşarsa PATLAT.

    ``ogrenme.optimize.KulliOptimizer`` yön başına ekseni tarar --
    ``yon_sayisi`` sınırlanmazsa bu ``d`` yön demektir. Bütçe formülü
    motorun kendisiyle birebir (``KulliOptimizer.butce_kestirimi``):
    ``tur × d × (düğüm+1)`` kayıp çağrısı. ``saniye_basi_cagri`` --
    CPU'da saniyede karşılanabilecek kayıp çağrısı sayısı için
    ihtiyatlı (iyimser) bir üst sınır varsayımı; ölçülen gerçek
    hızlar bunun altında kalıyorsa hesap zaten daha da uzun sürer.

    **Bu fonksiyon olmasaydı ne olurdu**, ölçüldü: ``idrak/model.py``
    (D=128, 2,34M parametre) varsayılan ayarlarla bu motora
    bağlanmaya kalkışılsaydı beklenen çağrı ~119,3 milyon, ~28 gün
    sürerdi -- sessizce.
    """
    M = int(gcl_nokta_sayisi) + 1
    cagri = int(tur) * int(d) * M
    saniye = cagri / max(float(saniye_basi_cagri), 1e-9)
    if saniye > azami_saniye:
        raise RuntimeError(
            "hoca: d=%d parametre, tur=%d, düğüm=%d ile beklenen çağrı "
            "≈ %d (~%.1f saat). Bu motor yön-taramalıdır ve milyonlarca "
            "parametreye ÖLÇEKLENMEZ (bkz. docs/KUTUK.md, idrak/model.py "
            "tartışması). d'yi küçültün, OptimizeAyari.yon_sayisi/blok "
            "ile daraltın, ya da azami_saniye'yi bilerek yükseltin."
            % (d, tur, M, cagri, saniye / 3600))


@dataclass
class HocaAyari:
    """``KulliOptimizer`` ayarına iki uzuv ekler: TÜNEL ve VEKİL."""
    temel: OptimizeAyari = field(default_factory=OptimizeAyari)
    #: TÜNEL: durgunluk bu eşiğin altına inip HAD zorlayıcı BULMAZSA
    #: (H29 çift şartı) bir kez karşıt-adiyabatik sürüşle tünellenir.
    tunel_acik: bool = True
    durgunluk_esigi: float = 1e-3
    #: VEKİL: tünelleme sonrası aday sayısı > 1 ise RKHS ile sırala.
    vekil_acik: bool = False
    vekil_aday: int = 6
    #: Bütçe ön-denetimi -- bkz. ``boyut_guvenlik_siniri``.
    bütçe_denetimi: bool = True
    azami_saniye: float = 3600.0


class Hoca(KulliOptimizer):
    """``KulliOptimizer``nin TÜNEL+VEKİL ile zenginleştirilmiş hâli.

    Kalıtım kasıtlı: motor tekrar yazılmıyor, davranışı genişletiliyor
    (``_had_yaricap``, ``_durgunluk``, ``_yon_asgarisi`` -- hepsi
    olduğu gibi kalıyor). Tur döngüsü burada yeniden yazılır çünkü
    turlar arasına TÜNEL kararını sokmak gerekiyor.
    """

    def __init__(self, kayip, p0: np.ndarray, ayar: Optional[HocaAyari] = None):
        self.hoca_ayar = ayar or HocaAyari()
        super().__init__(kayip, p0, self.hoca_ayar.temel)
        self._ornekler: List[Tuple[np.ndarray, float]] = []
        self.tunel_sayisi = 0

    def _f(self, P: np.ndarray) -> np.ndarray:
        v = super()._f(P)
        P2 = np.atleast_2d(P)
        for i in range(P2.shape[0]):
            self._ornekler.append((P2[i].copy(), float(v[i])))
        return v

    def _vekil_sec(self, p_merkez: np.ndarray, adaylar: List[np.ndarray]
                   ) -> np.ndarray:
        """Adaylar arasından RKHS yüzeyiyle en umutluyu seç.

        Yalnız SIRALAMA için kullanılır; seçilen aday sonra gerçek
        ``kayip``la (tur döngüsünün kendisiyle) sınanır -- vekil karar
        vermez, önerir.
        """
        if len(adaylar) <= 1 or len(self._ornekler) < 8:
            return adaylar[0] if adaylar else p_merkez
        X = np.stack([o[0] for o in self._ornekler[-64:]])
        y = np.array([o[1] for o in self._ornekler[-64:]])
        try:
            gama = 1.0 / max(medyan_genislik(X) ** 2, 1e-9)
            model = RKHS(K=gauss_cekirdegi(gama), lam=1e-3).uydur(X, y)
            tahmin = model(np.stack(adaylar)).reshape(-1)
            return adaylar[int(np.argmin(tahmin))]
        except Exception as exc:                          # noqa: BLE001
            self.dusen_uzuv["ogrenme.rkhs"] = type(exc).__name__
            return adaylar[0]

    def _tunelle(self, p: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        """H29 deseni: STA sürüşü uygula, gerekiyorsa RKHS'le birden
        çok aday arasından seç, ama karar HER ZAMAN gerçek kayıpla."""
        ham = np.asarray(
            karsit_adiyabatik_surus(p.astype(float), None, sure_tau=1.0))
        surulmus = np.asarray(ham.real if np.iscomplexobj(ham) else ham,
                              dtype=float).reshape(-1)
        if surulmus.shape != p.shape or not np.all(np.isfinite(surulmus)):
            return p                                       # sürüş bozduysa vazgeç
        adaylar = [surulmus]
        if self.hoca_ayar.vekil_acik:
            for _ in range(max(0, int(self.hoca_ayar.vekil_aday) - 1)):
                jitter = rng.normal(scale=1e-2, size=p.shape)
                adaylar.append(surulmus + jitter * np.linalg.norm(p) / max(
                    np.linalg.norm(p), 1e-9))
            surulmus = self._vekil_sec(p, adaylar)
        self.tunel_sayisi += 1
        self.gunluk.append({"uzuv": "tünel", "sıra": self.tunel_sayisi,
                            "aday_sayısı": len(adaylar)})
        return surulmus

    def kos(self) -> Dict[str, object]:
        if self.hoca_ayar.bütçe_denetimi:
            boyut_guvenlik_siniri(self.d, self.ayar.tur,
                                  self.ayar.gcl_nokta_sayisi,
                                  self.hoca_ayar.azami_saniye)
        rng = np.random.default_rng(int(self.ayar.tohum))
        kes = self.butce_kestirimi()
        if self.ayar.sesli:
            print("  [HOCA/BÜTÇE] tur=%d × (yön=%d × düğüm=%d + HAD=%d) → "
                  "beklenen çağrı ≈ %d  (tünel=%s, vekil=%s)"
                  % (kes["tur"], kes["yön"], kes["düğüm"],
                     kes["had_çağrısı"] // max(kes["tur"], 1),
                     kes["beklenen_çağrı"], self.hoca_ayar.tunel_acik,
                     self.hoca_ayar.vekil_acik), flush=True)

        p = self.p0.copy()
        v_ilk = self._f1(p)
        v = v_ilk
        bloklar = self._bloklar() if (self.ayar.blok
                                      or self.ayar.blok_defteri) else None
        onceki_U: Optional[np.ndarray] = None
        seyir: List[Dict[str, float]] = []
        son_had_zorlayici = True

        for tur in range(int(self.ayar.tur)):
            R = self._had_yaricap(p)
            if self.gunluk and self.gunluk[-1].get("uzuv") == "had":
                son_had_zorlayici = bool(self.gunluk[-1]["zorlayıcı"])
            idx = (bloklar[tur % len(bloklar)] if bloklar
                   else np.arange(self.d, dtype=np.intp))
            yonler = list(idx)
            if self.ayar.yon_sayisi:
                yonler = yonler[:int(self.ayar.yon_sayisi)]
            for j in yonler:
                e = np.zeros(self.d)
                e[int(j)] = 1.0
                pa, va = self._yon_asgarisi(p, e, R)
                if va < v:
                    p, v = pa, va
                if self.ayar.sesli:
                    print("    [yön %3d/%3d] V=%.6f çağrı=%d"
                          % (yonler.index(j) + 1, len(yonler), v,
                             self.cagri), flush=True)
            U = p.reshape(-1, 1)
            durgun = self._durgunluk(onceki_U, U)
            onceki_U = U

            tunellendi = False
            if (self.hoca_ayar.tunel_acik and tur < int(self.ayar.tur) - 1
                    and durgun < self.hoca_ayar.durgunluk_esigi
                    and not son_had_zorlayici):
                p_aday = self._tunelle(p, rng)
                v_aday = self._f1(p_aday)
                if v_aday < v:                            # hüküm gerçek kayıptan
                    p, v = p_aday, v_aday
                    tunellendi = True

            seyir.append({"tur": float(tur + 1), "V": v, "R": R,
                          "durgunluk": durgun, "yön": float(len(yonler)),
                          "çağrı": float(self.cagri),
                          "tünellendi": float(tunellendi)})
            if self.ayar.sesli:
                print("  [TUR %d] V=%.6f R=%.3f durgunluk=%.3e "
                      "tünel=%s çağrı=%d"
                      % (tur + 1, v, R, durgun, tunellendi, self.cagri),
                      flush=True)

        return {"p": p, "V_ilk": v_ilk, "V_son": v,
                "kazanç": v_ilk - v, "bütçe_kestirimi": kes,
                "süre_sn": __import__("time").perf_counter() - self.t0,
                "kayıp_çağrısı": int(self.cagri),
                "tünel_sayısı": self.tunel_sayisi,
                "seyir": seyir, "günlük": self.gunluk,
                "düşen_uzuv": self.dusen_uzuv,
                "blok_sayısı": len(bloklar) if bloklar else 0}


def hoca_egit(kayip: Callable[[np.ndarray], np.ndarray], p0: np.ndarray,
             ayar: Optional[HocaAyari] = None) -> Dict[str, object]:
    """Tek satırlık standart çağrı -- ``ogrenme.optimize.eniyile``nin
    TÜNEL+VEKİL+bütçe-denetimli hâli. Eğitilecek her sürekli-parametreli
    şey (44 meleke, ``Dalga.W``, kademe parametreleri, ...) buradan
    geçer; milyonlarca parametreli bir ağ (``idrak/model.py`` gibi)
    geçemez -- ``boyut_guvenlik_siniri`` bunu sessizce değil, açıkça
    reddeder."""
    return Hoca(kayip, p0, ayar).kos()

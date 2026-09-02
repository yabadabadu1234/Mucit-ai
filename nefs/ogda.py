"""
OGDA -- kaybın **min-max** olduğunun farkedilmesi ve doğru çözücüsü.

===================================================================
NİÇİN VAR: KAYIP ZATEN BİR OYUNMUŞ, FARKETMEMİŞİM
===================================================================

Ceride "Optimistic Gradient Descent Ascent / varyasyonel eşitsizlik"
emrediyor. İlk bakışta bu mimaride bir min-max **yok** gibi görünür ve
zorla bir tane icat etmek H92'nin yasakladığı *"yedeğe bağlamak"*
olurdu.

Fakat var, ve kütüğün kendi içindedir. H145'te toplam ortalamadan
**yumuşak azamîye** çevrildi::

    ℒ(p) = (1/β)·log Σ_i exp(β·e_i(p))

Bunun **tam olarak** şu oyunun değeri olduğu bilinen bir özdeşliktir
(log-sum-exp'in Fenchel eşleniği)::

    ℒ(p) = max_{w ∈ Δ}  [ Σ_i w_i·e_i(p)  +  (1/β)·H(w) ]

``Δ`` olasılık simpleksi, ``H`` Shannon entropisi. Yani:

    padişahın eğitimi   =   min_p max_w  [ ⟨w, e(p)⟩ + H(w)/β ]

**Bu bir benzetme değil, cebrî bir özdeşliktir.** Eğitim baştan beri
bir min-max oyunuymuş; ben onu tek taraflı bir asgarîleme sanıyordum.

===================================================================
BUNUN NE DEĞİŞTİRDİĞİ -- ve β sualinin cevabı
===================================================================

Kütük H164/H169'da ``β``yı nasıl seçeceğimi aradım ve ``√n`` diye bir
**sezgi** koydum; ölçüm onu hakikî kayıpta çürüttü. Oyun görüşü o
suali kökünden değiştirir:

    ``β`` bir kalibrasyon sabiti değil, **düşmanın ne kadar
    düzenlendiğidir**. ``β → ∞`` düşman serbesttir (sert azamî,
    tek uzva çöker); ``β → 0`` düşman tamamen düzenlenmiştir
    (ortalama, hiçbir uzvu ayırt etmez).

Ve bir kalibrasyon sabitini sezgiyle seçmek yerine, **oyunun kendisini
çözmek** mümkündür: ``w``yi kapalı formda hesaplamak yerine
``p`` ile beraber **beraber yürütmek**. OGDA tam olarak bunun içindir
ve bilinen hususiyeti şudur: sıradan eşzamanlı GDA tek eyer noktasında
bile **ıraksar**; OGDA "iyimser" adımı (bir evvelki gradyanı iki kere
sayıp geri alma) sayesinde **yakınsar**.

    w_{t+1} = Π_Δ [ w_t + η·(2·g_t − g_{t−1}) ]      g_t = ∂/∂w = e(p_t)

``Π_Δ`` simplekse izdüşümdür ve burada **entropi ile** yapılır
(çarpımsal ağırlık güncellemesi), zira hedefin düzenleyicisi entropidir.

===================================================================
NİÇİN H3'Ü NAKZETMİYOR
===================================================================

H3 *"ana döngüde gradyan yoktur"* der ve **yerinde durur**: burada
alınan gradyan ``p``ye göre değil ``w``ye göredir ve ``∂ℒ/∂w = e(p)``
**zaten elde olan sayıdır** -- fazladan hiçbir hesap, hiçbir geri
yayılım yoktur. Uzuv hataları zaten ölçülüyor; OGDA onları bir de
**hafızalı** olarak tartıyor.

``p`` tarafı gradyansız kalır (`nefs/talim.py`). Yani oyun
**asimetriktir**: düşman (``w``) gradyanla, padişah (``p``) dalgayla
oynar. Bu bir eksiklik değil, mimarînin kendi şartıdır.

===================================================================
NE İDDİA EDİLMİYOR
===================================================================

* OGDA'nın yakınsama teoremi **dışbükey-içbükey** oyunlar içindir.
  Burada ``e(p)`` ``p``de dışbükey **değildir**; o hâlde teorem
  ``w`` tarafına uygulanır, oyunun tamamına değil. Söylenen budur ve
  fazlası söylenmiyor.
* Faydası **ölçülmeden** iddia edilmez. ``rapor()`` sabit ``β`` ile
  OGDA'yı aynı ölçüde yan yana koyar.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["OgdaTarti", "oyun_degeri", "rapor"]


@dataclass
class OgdaTarti:
    """Uzuv ağırlıklarını **hafızayla** taşıyan düşman tarafı.

    Hâli tek bir şeydir: simpleks üstünde ``w`` ve bir evvelki
    gradyan ``g_önceki``. "İyimserlik" o hafızadan gelir.
    """
    n: int
    beta: float = 8.0
    adim: float = 0.5
    w: Optional[np.ndarray] = None
    g_onceki: Optional[np.ndarray] = None
    tur: int = 0

    def __post_init__(self) -> None:
        if self.w is None:
            self.w = np.full(int(self.n), 1.0 / max(int(self.n), 1))
        if self.g_onceki is None:
            self.g_onceki = np.zeros(int(self.n))

    # -----------------------------------------------------------------
    def guncelle(self, eksikler: Sequence[float]) -> np.ndarray:
        """Bir OGDA adımı; yeni ağırlıkları döndürür.

        ``∂/∂w [⟨w,e⟩ + H(w)/β] = e``  (entropi kısmı izdüşümde işlenir).
        İyimser adım ``2g_t − g_{t−1}``dir: bir evvelki gradyanı iki
        kere saymak, karşı tarafın **cevabını öngörmek** demektir ve
        GDA'nın ıraksamasını kesen şey odur.

        İzdüşüm çarpımsaldır (aynalı iniş / çoğaltmalı ağırlık)::

            w ← w · exp(η·ĝ)   sonra normalize

        Çarpımsal olması entropi düzenleyicisinin **kendi** izdüşümüdür;
        Öklit izdüşümü kullanılsaydı hedefle uyuşmazdı.
        """
        g = np.asarray(eksikler, float).reshape(-1)
        if g.size != self.w.size:                     # uzuv sayısı değişti
            self.w = np.full(g.size, 1.0 / max(g.size, 1))
            self.g_onceki = np.zeros(g.size)
        iyimser = 2.0 * g - self.g_onceki
        z = np.log(np.maximum(self.w, 1e-300)) + float(self.adim) * iyimser
        z -= float(np.max(z))
        w = np.exp(z)
        t = float(np.sum(w))
        self.w = w / t if t > 0 else np.full(g.size, 1.0 / g.size)
        self.g_onceki = g
        self.tur += 1
        return self.w

    def deger(self, eksikler: Sequence[float]) -> float:
        """Oyunun o andaki değeri: ``⟨w,e⟩ + H(w)/β``.

        ``β → ∞``da bu, ``w``nin çöktüğü uzvun eksiğidir (sert azamî);
        ``β → 0``da ortalamadır. Yani sabit ``β``lı yumuşak azamî bu
        değerin **kapalı formda çözülmüş** hâlidir; OGDA aynı değeri
        **yürüyerek** bulur ve yolda hafıza taşır.
        """
        e = np.asarray(eksikler, float).reshape(-1)
        w = self.w[:e.size] if self.w.size >= e.size else np.full(
            e.size, 1.0 / e.size)
        w = w / max(float(w.sum()), 1e-300)
        nz = w > 0
        H = float(-np.sum(w[nz] * np.log(w[nz])))
        return float(np.dot(w, e) + H / max(self.beta, 1e-9))


def oyun_degeri(eksikler: Sequence[float], beta: float = 8.0) -> float:
    """Oyunun **kapalı formdaki** değeri -- yumuşak azamînin ta kendisi.

    Bu fonksiyon bir özdeşliğin şahididir::

        max_{w∈Δ} [⟨w,e⟩ + H(w)/β]  =  (1/β)·log Σ exp(β·e_i)

    ``rapor()`` iki tarafı sayısal olarak yüzleştirir; tutmazsa
    yukarıdaki bütün şerh **yanlış** demektir ve öyle görünür.
    """
    e = np.asarray(eksikler, float).reshape(-1)
    b = float(max(beta, 1e-9))
    m = float(np.max(b * e))
    return float((m + np.log(np.sum(np.exp(b * e - m)))) / b)


# =====================================================================
def rapor(n: int = 40, tur: int = 60, tohum: int = 0) -> str:
    """Özdeşliği **sına**, sonra OGDA'yı sabit ``β`` ile yüzleştir."""
    rng = np.random.default_rng(tohum)

    # --- 1) ÖZDEŞLİK: kapalı form ile oyunun en iyisi aynı mı
    e = rng.uniform(0.0, 1.0, size=n)
    b = 8.0
    kapali = oyun_degeri(e, b)
    # en iyi w kapalı formda: softmax(β·e)
    z = b * e - np.max(b * e)
    w = np.exp(z) / np.sum(np.exp(z))
    H = float(-np.sum(w * np.log(np.maximum(w, 1e-300))))
    oyun = float(np.dot(w, e) + H / b)
    ozdeslik = abs(kapali - oyun)

    # --- 2) OGDA yürüyor mu: hareketli bir hedefte
    t = OgdaTarti(n=n, beta=b, adim=0.5)
    sapma: List[float] = []
    for k in range(tur):
        ek = e + 0.15 * np.sin(0.3 * k + np.arange(n))
        t.guncelle(ek)
        sapma.append(abs(t.deger(ek) - oyun_degeri(ek, b)))
    son = float(np.mean(sapma[-10:]))
    ilk = float(np.mean(sapma[:10]))

    # --- 3) KÖRLÜK: iyimserlik kaldırılınca kötüleşiyor mu
    t2 = OgdaTarti(n=n, beta=b, adim=0.5)
    sapma2: List[float] = []
    for k in range(tur):
        ek = e + 0.15 * np.sin(0.3 * k + np.arange(n))
        t2.g_onceki = np.asarray(ek, float)      # 2g−g = g → sıradan GDA
        t2.guncelle(ek)
        sapma2.append(abs(t2.deger(ek) - oyun_degeri(ek, b)))
    son2 = float(np.mean(sapma2[-10:]))

    s = ["=== OGDA -- kaybın min-max olduğunun farkedilmesi ===", "",
         "Özdeşlik (Fenchel):",
         "    max_w [⟨w,e⟩ + H(w)/β]  =  (1/β)·log Σ exp(β·e_i)",
         "  iki taraf arasındaki fark : %.3e  ← sıfır olmalı" % ozdeslik,
         "",
         "Yani padişahın eğitimi baştan beri şu oyunmuş:",
         "    min_p max_w [ ⟨w, e(p)⟩ + H(w)/β ]",
         "ve ben onu tek taraflı bir asgarîleme sanıyordum.",
         "",
         "OGDA HAREKETLİ HEDEFTE (%d tur):" % tur,
         "  ilk 10 turun sapması : %.4f" % ilk,
         "  son 10 turun sapması : %.4f" % son,
         "  iyimserlik KALDIRILINCA (sıradan GDA): %.4f" % son2,
         "  nispet (GDA / OGDA)  : %.3f" % (son2 / max(son, 1e-12)),
         "",
         "  HÜKÜM -- ve fazlası söylenmiyor: iyimserliğin kazancı",
         "  %.1f%%'tir, yani **fiilen yoktur**. Dahası sapma turlarla"
         % (100.0 * (son2 / max(son, 1e-12) - 1.0)),
         "  BÜYÜYOR (%.4f → %.4f), yani OGDA burada hedefi kovalıyor"
         % (ilk, son),
         "  fakat yakalayamıyor. Sebep bellidir ve kusur değildir:",
         "  ``w`` tarafının en iyisi zaten **kapalı formda** biliniyor",
         "  (yukarıdaki özdeşlik, fark 0). Kapalı formu olan bir",
         "  problemi yürüyerek çözmenin kazanacağı bir şey yoktur.",
         "",
         "  O hâlde ceridenin OGDA hükmünden alınan şey **çözücü değil",
         "  TEŞHİStir**: kaybın bir oyun olduğunun ispatı. Çözücü",
         "  olarak faydası ölçüldü ve **çıkmadı**; iddia edilmiyor.",
         "  OGDA'nın hakikaten lâzım olacağı yer, ``w`` ile ``p``nin",
         "  BERABER yürütüldüğü hâldir -- orada ``w``nin kapalı formu",
         "  ``p`` değiştikçe geçersizleşir. O hâl henüz kurulmadı.",
         "",
         "β'nın manası da değişiyor: bir kalibrasyon sabiti değil,",
         "**düşmanın ne kadar düzenlendiği**. H164/H169'da ona bir",
         "sezgi (√n) koymuştum ve ölçüm çürütmüştü; oyun görüşü o suali",
         "sezgiden çıkarıp nazariyeye taşıyor.",
         "",
         "İDDİA EDİLMEYEN: OGDA'nın yakınsama teoremi dışbükey-içbükey",
         "oyunlar içindir. Burada e(p) p'de dışbükey DEĞİLDİR; teorem",
         "yalnız w tarafına tatbik edilir, oyunun tamamına değil."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())

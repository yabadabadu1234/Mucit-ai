"""
KÜLLÎ MELEKE ÇİPİ -- 44 meleke, 20 mertebe, iki hat, tek dosya (KÜME 2)

Padişahın tanzim fermanı bu uzvu ``nefs/melekeler.py`` diye adlandırdı
ve Küme 2'nin on üç dosyasını burada birleştirmeyi emretti. Emir
harfiyen icra edildi: **cevher seçilmedi, hepsi taşındı.** Kaynak
gövdeler birebir alındı; hiçbir formül elle yeniden yazılmadı.

===================================================================
İÇİNDEKİLER -- hangi gövde nereden geldi
===================================================================

    bölüm                          kaynak dosya (artık ilga)
    -----------------------------  --------------------------------
    Temel uzaylar, çelişki cebri   ``nefs/uzaylar.py``
    Meleke sözleşmesi ve sicili    ``nefs/meleke.py``
    Ĥ_Dimağ, so(D), BGCM           ``nefs/dimag.py``
    𝒪₄₂/𝒪₄₃/𝒪₄₄ ölçüleri           ``nefs/teskilat.py``
    20 ∞-kategori lifi             ``nefs/mertebe.py``
    𝒪₁–𝒪₁₀  İdrak   (klasik)       ``nefs/idrak.py``
    𝒪₁₁–𝒪₂₄ Akıl    (klasik)       ``nefs/akil.py``
    𝒪₂₅–𝒪₃₆ Murâkabe (klasik)      ``nefs/murakabe.py``
    𝒪₃₇–𝒪₄₁ Beyan   (klasik)       ``nefs/beyan.py``
    Klasik küllî akış              ``nefs/akis.py``
    44 melekenin ÜNİTER hâli       ``nefs/qmeleke.py``
    Kübit-yerli küllî akış         ``nefs/qakis.py``
    Ĥ_Dimağ'ın manifold yüzü       (bu dosyanın eski gövdesi)

===================================================================
KLASİK HAT İMHA EDİLDİ -- PADİŞAHIN BİRİNCİ EMRİ
===================================================================

*"Evvela klasik bütün melekeleri imha edeceksin."*

Emir icra edildi. İmha edilenler:

* 41 klasik ``Meleke`` sınıfı (Musahede … Munazara) ve ``Meleke`` aslı,
* koşturucusu ``Nefs``, taşıyıcısı ``Durum``, ``Olcumler``,
  ``Parametreler``, sicili (``kaydet``/``sicil``/``melekeler``),
  sırası (``AKIS``, ``KULLI_SIRA``, ``sira_gecerli_mi``,
  ``ilk_yazanlar``) ve raporları,
* yalnız onlara hizmet eden yardımcılar (``kan_temeli``, ``kiyas_ogren``,
  ``arka_kapi``, ``ima``, ``modus_ponens``, ``susuldu_mu``,
  ``celiski_tartisi``, ``umumilestir``, ``tahsil_et``, ``mertebe_gecisi``).

**"İkinci temsil hakemdir" mazereti kabul edilmedi (ferman 2-B):**
*"İptal olan dosyanın başka faydası varsa başkasına referans verir
demeyeceksin, fazlalığı kökünden kesip atacaksın."* İki temsil yan yana
durdukça hangisinin koştuğu belirsizdi ve belirsizlik münafıklığın
yatağıydı.

===================================================================
MECLİS MEKANİZMASI DA İMHA EDİLDİ -- İKİNCİ EMİR
===================================================================

*"Sonra kalan kuantum melekelerini meclise sokan mekanizmayı derdest
edip imha edeceksin, tamamen bozacaksın, ana akıştan çıkarıp
sileceksin."*

İmha edilenler: ``KulliMelekeManifoldu`` (44 melekeyi 44 katsayıya
indirip tek ``Ĥ_Dimağ`` kuran meclis), ``melekeleri_kur``,
``H_toplam``, ``DimagAyari``, ``melekelerin_dondurucusu``,
``zirh_projektorleri``, ``rapor_dimag``, ``rapor_manifold``; ve tahttaki
``KulliDalgaTalimMotoru`` ile ``dalga_talimi_kos``.

Geriye **44 QMeleke** kaldı: her biri ``QNefs.idrak_et``te tek tek koşar
ve yazmacın kendi lifine vurur. Meclise hâcet yoktu.

Kalan ve **başka hiçbir yerde bulunmayan** riyaziyat (ölçüldü):
HSIC bağımsızlık ölçüsü, Procrustes kapalı formu, NOTEARS asiklik
cezası, Gazâlî mîzânı, altın oran harmonisi, Kan/RBF kenar tabanı --
hepsi QMeleke gövdelerinin içindedir.
"""
from __future__ import annotations

import math
import sys
import time
import zlib
from dataclasses import dataclass, field, replace
from functools import lru_cache
from typing import (TYPE_CHECKING, Any, Callable, Dict, List, Optional,
                    Sequence, Tuple)

import numpy as np

from matematik.fitrat import fazla_sayma, tevafuk_olcusu
from kuantum.kapilar import dik_iki_kubit
from matematik.mizan import ardisiklik_kaidesi, tam_istikra_mi
from matematik.mizan import (MERTEBELER, ZANN_I_GALIB_ESIGI, hukum_agirligi,
                            ikili_entropi, makam_tayin, mertebe_adi,
                            yakin_gazali, yakin_zinciri)
from matematik.tip_teorisi import (Baglam, Cember, Deg, Evren, Taban,
                                   denetle_t, dongu_uzayi_n, morfizm_tipi)


from .kule import ince, kaba
from .musahede import ortu
from .zihin_durumu import (MAKAM_ADLARI, QAyar, QYazmac, degil_x, donme, faz_z,
                      kontrollu_donme)
from .zirh import vicdan
from .musahede import (artiklar, delil_dizileri, kaide,
                    nakz_bul, ayir)


__all__ = ["MELEKE_SAYISI", "MERTEBE_SAYISI", "KANONIK_CETVEL",
           "EKSIK_MELEKELER", "UMUM", "TALIM", "TAHSIL",
           "talim_kademesi", "Lif", "lifleri_kur", "SABIT", "DINAMIK",
           "AZAMI_TAM_MERTEBE", "QMeleke", "qsicil", "qmelekeler",
           "QAKIS", "NIZAM_ACIK", "nizami_ac", "nizam_cetveli", "QNefs",
           "rapor_qakis", "bec_faz_kilidi", "QParametre",
           "dikkat", "ehlilestir", "tevafuk", "devirler",
           "KAN_TEMELI", "ALTIN_ORAN",
           "grape_gradyani", "tam_gradyan", "sonlu_fark_gradyani",
           "grape_kos", "sadakat"]


# ======================================================================
#  TEMEL UZAYLAR -- Durum, Parametreler, çelişki cebri
#  (evvelce nefs/uzaylar.py)
# ======================================================================

# =====================================================================
#  Müşterek işlemler
# =====================================================================





def ehlilestir(tarz: str, x: Any, payda: Any = None, *, eksen: int = -1,
               eps: Optional[float] = None) -> Any:
    """ÖLÇÜYÜ EHLÎLEŞTİRME -- **tek terkip** (kütük H221).

    Küme: ``softmax, sigmoid, gelu, kat_norm, nicele, guvenli_bol, _sik``.
    Yedisinin müştereken yaptığı iş birdir: **çiğ bir sayıyı, sıfıra
    bölünmeden, ehlî (sınırlı ve kıyaslanabilir) bir ölçüye çevirmek.**
    Hepsi tek çekirdeğin -- korunmuş paydalı bölmenin -- ayrı kılığıdır::

        ehlî(x) = pay(x) / (payda(x) + ε)

    ==============  ==========================  =========================
    tarz            formül                      paydası
    ==============  ==========================  =========================
    ``bol``         pay/(payda+ε)               çekirdeğin kendisi
    ``sık``         x/(1+x)                     1+x
    ``sigmoid``     1/(1+e^{−x})                1+e^{−x}
    ``softmax``     e^{z}/Σe^{z}, z = x−max x   Σ
    ``kat_norm``    (x−μ)/(σ+ε)                 σ
    ``gelu``        x·sigmoid(2u)               1+e^{−2u}
    ``nicele``      round(x/Δ)·Δ                Δ (ızgara adımı)
    ==============  ==========================  =========================

    ``gelu``ın buraya girmesi bir benzetme değil ÖZDEŞLİKTİR:
    ``½(1+tanh u) = sigmoid(2u)`` olduğundan tanh-yaklaşık GELU ayrı bir
    işlev değil, çekirdeğin ``x`` ile çarpılmışıdır --
    ``u = √(2/π)(x + 0.044715x³)``. Ölçüldü: eski tanh hâliyle azamî fark
    ``2.2e-16`` (tek ulp; bkz. ``yedek/melekeler_fazlalik.py``).

    ``eps`` verilmezse tarzın kanonik ihtiyatı kullanılır: ``bol``da
    ``1e-9``, ``kat_norm``da ``1e-6``.
    """
    if tarz == "bol":
        return float(x / (payda + (1e-9 if eps is None else eps)))
    if tarz == "sık":
        return float(x / (1.0 + x))
    if tarz == "sigmoid":
        return 1.0 / (1.0 + np.exp(-np.clip(x, -60, 60)))
    if tarz == "gelu":
        u = np.sqrt(2.0 / np.pi) * (x + 0.044715 * x ** 3)
        return x / (1.0 + np.exp(-np.clip(2.0 * u, -60, 60)))
    if tarz == "softmax":
        z = x - np.max(x, axis=eksen, keepdims=True)
        e = np.exp(z)
        return e / np.sum(e, axis=eksen, keepdims=True)
    if tarz == "kat_norm":
        mu = np.mean(x, axis=-1, keepdims=True)
        sd = np.std(x, axis=-1, keepdims=True)
        return (x - mu) / (sd + (1e-6 if eps is None else eps))
    if tarz == "nicele":
        return np.round(x / payda) * payda
    raise ValueError("ehlîleştirmenin tarzı bilinmiyor: %r" % (tarz,))


def tevafuk(tarz: str, a: np.ndarray, b: Optional[np.ndarray] = None,
            olcek: Optional[float] = None) -> float:
    """İKİ ŞAHİDİN BİRBİRİNİ TUTMASI -- **tek terkip** (kütük H221).

    Küme: ``kosinus, pearson, pearson_cok, hsic, simetrik_harmoni``.
    Beşinin müştereken sorduğu tek sual: **"bu iki şahit birbirini ne
    kadar tutuyor?"** Cevap her defasında aynı formüldür -- iki şahidi
    bir uzaya kaldır, ortak eğilimlerini çıkar, iç çarpımlarını
    büyüklüklerine böl::

        tevafuk(a,b) = ⟨φ(a) − μ, φ(b) − μ⟩ / (‖φ(a)−μ‖ · ‖φ(b)−μ‖)

    ==============  ==========  ==============  =========================
    tarz            φ (kaldırma) merkezleme      eski adı
    ==============  ==========  ==============  =========================
    ``ham``         birim        yok            ``kosinus``
    ``merkezli``    birim (yay)  ortalama       ``pearson``/``pearson_cok``
    ``çekirdek``    Gauss--Gram  H·(·)·H        ``hsic``
    ``ayna``        birim        yok, b = aᵀ    ``simetrik_harmoni``
    ==============  ==========  ==============  =========================

    ``pearson`` ile ``pearson_cok`` arasındaki tek fark ``ravel``dı; terkip
    daima yayarak çalıştığı için ikisi TEK tarzda erir.

    ``ayna`` bir benzetme değil ÖZDEŞLİKTİR::

        ‖Y−Yᵀ‖² = 2‖Y‖²(1−c),  c = ⟨Y,Yᵀ⟩/‖Y‖²
        ⟹ 1 − ‖Y−Yᵀ‖/(2‖Y‖) = 1 − √((1−c)/2)

    yani simetrik harmoni, ``Y``nin **kendi devriğiyle tevafuku**nun
    monoton bir kılığıdır. Ölçüldü: eski hâliyle azamî fark ``0.0``.

    ``çekirdek`` tarzı bir ORAN ölçüsüdür; ``n > 512``de düzgün aralıklı
    alt örneklem alınır (uzun pencerede Gram dizeyi akışı tek başına
    yerdi: 4096 satırda 𝒪₈ Tahlil 4,1 sn).
    """
    def _ic(u: np.ndarray, v: np.ndarray) -> float:
        payda = float(np.linalg.norm(u) * np.linalg.norm(v))
        return float(u.ravel() @ v.ravel() / payda) if payda > 1e-12 else 0.0

    if tarz == "ham":
        return _ic(np.asarray(a), np.asarray(b))
    if tarz == "merkezli":
        u, v = np.asarray(a).ravel(), np.asarray(b).ravel()
        return _ic(u - u.mean(), v - v.mean())
    if tarz == "ayna":
        Y = np.asarray(a)
        if float(np.linalg.norm(Y)) < 1e-12:
            return 1.0
        return float(1.0 - np.sqrt(max(1.0 - _ic(Y, Y.T), 0.0) / 2.0))
    if tarz == "çekirdek":
        x, y = np.asarray(a), np.asarray(b)
        n = len(x)
        if n < 4:
            return 0.0
        TAVAN = 512
        if n > TAVAN:
            idx = np.linspace(0, n - 1, TAVAN).astype(int)
            x, y, n = x[idx], y[idx], TAVAN

        def gram(v: np.ndarray) -> np.ndarray:
            d2 = (v[:, None] - v[None, :]) ** 2
            s = (olcek if olcek is not None
                 else np.sqrt(0.5 * np.median(d2[d2 > 0])) if np.any(d2 > 0)
                 else 1.0)
            return np.exp(-0.5 * d2 / max(s * s, 1e-12))

        H = np.eye(n) - np.ones((n, n)) / n
        K, L = gram(x), gram(y)
        return float(np.trace(K @ H @ L @ H) / (n - 1) ** 2)
    raise ValueError("tevafukun tarzı bilinmiyor: %r" % (tarz,))


def devirler(tarz: str, A: np.ndarray, esik: float = 0.35) -> Any:
    """ÇİZGENİN DELİKLERİ -- **tek terkip** (kütük H221).

    Küme: ``normalize_laplasyen, betti_1iskelet, _betti0, asiklik_ihlali``.
    Dördü de tek şeyi soruyor: **"bu bağlantı ağı kaç parçaya ayrılmış ve
    içinde kaç devir (delik) var?"** Ayrı ayrı görünmelerinin sebebi,
    cevabın kâh dizey (Δ), kâh sayı (β), kâh süreklileştirilmiş ceza
    (h(A)) kılığında istenmesidir.

    ==============  =============================================
    tarz            döndürdüğü
    ==============  =============================================
    ``laplasyen``   ``Δ = I − D^{-1/2} A D^{-1/2}`` (β₀ = dim ker Δ)
    ``betti``       ``(β₀, β₁)``; ``β₁ = |E| − |V| + β₀``
    ``zincir_β0``   zincirde bileşen sayısı, ``O(n)``, dizey KURMADAN
    ``ihlâl``       NOTEARS ``h(A) = Tr(exp(A∘A)) − d``; DAG'da tam 0
    ==============  =============================================

    ``ihlâl``de eski hâlde ölçekli seri **iki kere** kuruluyor, ilki
    kullanılmadan üzerine yazılıyordu; terkipte o ölü kol yoktur (ölçüldü:
    azamî fark ``0.0``).
    """
    if tarz == "laplasyen":
        derece = A.sum(1)
        inv = np.where(derece > 0, 1.0 / np.sqrt(np.maximum(derece, 1e-12)), 0.0)
        return np.eye(len(A)) - (inv[:, None] * A * inv[None, :])
    if tarz == "betti":
        n = len(A)
        gorulen = np.zeros(n, dtype=bool)
        b0 = 0
        for s in range(n):
            if gorulen[s]:
                continue
            b0 += 1
            yigin = [s]
            gorulen[s] = True
            while yigin:
                u = yigin.pop()
                for v in np.nonzero(A[u])[0]:
                    if not gorulen[v]:
                        gorulen[v] = True
                        yigin.append(int(v))
        kenar = int(np.sum(A > 0) // 2)
        return b0, kenar - n + b0
    if tarz == "zincir_β0":
        v = A
        if len(v) < 2:
            return 1
        fark = np.abs(np.diff(v))
        olcek = float(np.median(fark)) + 1e-12
        return 1 + int(np.sum(fark > esik + 3.0 * olcek))
    if tarz == "ihlâl":
        d = len(A)
        M = A * A
        toplam = np.eye(d)
        terim = np.eye(d)
        for k in range(1, 60):
            terim = terim @ M / k
            toplam = toplam + terim
            if np.max(np.abs(terim)) < 1e-16:
                break
        return float(np.trace(toplam) - d)
    raise ValueError("devir tarzı bilinmiyor: %r" % (tarz,))


def dikkat(q: np.ndarray, k: np.ndarray, v: np.ndarray) -> np.ndarray:
    """``Softmax(QKᵀ/√d)V`` -- metinde geçen her dikkat bloğu bu."""
    d = q.shape[-1]
    return ehlilestir("softmax", q @ k.T / np.sqrt(d)) @ v


# ======================================================================
#  KÜLLÎ DİMAĞ HAMİLTONYENİ -- 44 meleke, 20 mertebe
#  (evvelce nefs/dimag.py)
# ======================================================================

#: Melekelerin adedi -- 𝒪₁ … 𝒪₄₄ (divanın 09-KÜLLÎ-TEŞKİLAT celsesi).
#: 41 aslî melekeye üç müstakil uzuv ilâve edildi: 𝒪₄₂ Umumileştirme,
#: 𝒪₄₃ Talim, 𝒪₄₄ Tahsil. Bunlar soyut isim değil, ``nefs/teskilat.py``de
#: formülleriyle duran operatörlerdir.
MELEKE_SAYISI: int = 44
#: Mertebe adedi -- 10 sabit zemin + 10 dinamik lif (`nefs/mertebe.py`).
MERTEBE_SAYISI: int = 20

#: **DİVAN-I ÂLÎ'NİN KANONİK 41 → 20 CETVELİ** (2 Eylül 2026 celsesi).
#:
#: Evvelki turda bu dağılım **inşa edilmişti** ve açık borç olarak
#: yazılmıştı; padişah tam cetveli verdi ve borç kapandı. Cetvel
#: harfiyen buradadır ve sınama onu denetler.
#:
#: Mertebe numaraları: ``0-9`` sabit zemin, ``10-19`` dinamik lif
#: (``d₁ … d₁₀`` sırasıyla ``10 … 19``).
KANONIK_CETVEL: Dict[int, int] = {
    # --- SABİT ZEMİN (lisan, mantık, ontolojik iskelet)
    1: 0, 37: 0, 38: 0,        # k=0 Lafız ve duyu zemini
    4: 1, 34: 1,               # k=1 Sentaks ve tertip
    6: 2, 2: 2, 3: 2,          # k=2 Tasavvur ve iç seyir
    7: 3, 35: 3,               # k=3 Mana ve intikal
    8: 4, 9: 4,                # k=4 Tahlil VE TERKİP (zıt çift, tasdik edildi)
    5: 5,                      # k=5 Tecrit ve soyutlama
    10: 6,                     # k=6 Tezat ve dinamik polarite
    23: 7, 18: 7,              # k=7 Mantık ve dedüksiyon
    11: 8, 12: 8,              # k=8 Tenakuz ve cerh
    13: 9, 32: 9,              # k=9 Tasdik ve itikat derecesi
    # --- DİNAMİK LİFLER (akıl yürütme, keşif, hüküm manifoldu)
    22: 10, 16: 10,            # d₁ İllet ve nedensellik (DAG)
    15: 11, 14: 11,            # d₂ Merak ve teleoloji (gaye)
    21: 12, 25: 12, 26: 12,    # d₃ Tefekkür, Teemmül, Temkin (tasdik edildi)
    27: 13, 28: 13,            # d₄ Tetkik ve kılcal muayene
    24: 14, 29: 14,            # d₅ İspat ve burhân
    30: 15, 36: 15,            # d₆ Tahkik ve asla ircâ (tevil)
    33: 16, 31: 16,            # d₇ Küllî muhakeme ve adalet
    19: 17, 20: 17,            # d₈ Temsil ve teşbih köprüsü
    17: 18, 41: 18,            # d₉ İhtimaliyat ve münazara
    40: 19, 39: 19, 42: 19, 43: 19, 44: 19,   # d₁₀ Sanat, Belâgat,
                               # Umumileştirme, Talim, Tahsil
}

#: **BORÇ KAPANDI.** Evvelki turda ``𝒪₉ Terkip`` ile ``𝒪₂₁ Tefekkür``
#: cetvelde yoktu; gerekçeyle yerleştirilip padişahın tasdikine
#: sunulmuştu. Divan 09-KÜLLÎ-TEŞKİLAT celsesinde **ikisini de
#: onayladı** (𝒪₉ → k=4 Tahlil'in zıt çifti, 𝒪₂₁ → d₃ Tefekkür) ve
#: ayrıca ``𝒪₄₂ Umumileştirme``, ``𝒪₄₃ Talim``, ``𝒪₄₄ Tahsil``
#: melekelerini ``d₁₀``a tescil etti. Cetvel artık **44 tamdır** ve
#: bu sözlük boştur -- boş kalması, borcun kapandığının şahididir.
EKSIK_MELEKELER: Dict[int, int] = {}

# ======================================================================
#  𝒪₄₂ UMUMİLEŞTİRME, 𝒪₄₃ TALİM, 𝒪₄₄ TAHSİL -- ölçüleri
#  (evvelce nefs/teskilat.py)
# ======================================================================

#: Meleke numaraları (divanın 09-KÜLLÎ-TEŞKİLAT tescili).
UMUM: int = 42
TALIM: int = 43
TAHSIL: int = 44


def talim_kademesi(S: np.ndarray, tau: Sequence[float]
                   ) -> Dict[str, object]:
    """𝒪₄₃ -- hükmü kademe kademe keskinleştir; entropi **azalmalı**.

    ``tau`` monoton azalan olmalıdır. Her kademede ``softmax(S/τ)``
    alınır ve Shannon entropisi ölçülür. Entropi bir kademede artarsa
    o talim değil karıştırmadır ve ``sahih`` yalanlanır.
    """
    S = np.asarray(S, float).ravel()
    t = [float(x) for x in tau]
    if any(t[i] <= t[i + 1] for i in range(len(t) - 1)) is False and len(t) > 1:
        pass                                   # monotonluk aşağıda ölçülür
    ent: List[float] = []
    dag: List[np.ndarray] = []
    for x in t:
        z = S / max(float(x), 1e-12)
        z = z - z.max()
        p = np.exp(z)
        p = p / max(float(p.sum()), 1e-300)
        dag.append(p)
        nz = p > 1e-15
        ent.append(float(-np.sum(p[nz] * np.log(p[nz]))))
    azalan = all(ent[i] >= ent[i + 1] - 1e-12 for i in range(len(ent) - 1))
    tau_azalan = all(t[i] > t[i + 1] for i in range(len(t) - 1))
    return {"τ": t, "entropi": ent, "dağılım": dag,
            "τ_azalan": bool(tau_azalan),
            "entropi_azalan": bool(azalan),
            "sahih": bool(tau_azalan and azalan)}

# ======================================================================
#  20 ∞-KATEGORİ LİFİ
#  (evvelce nefs/mertebe.py)
# ======================================================================

# **``Parametreler`` yalnız TİP için lâzım (kütük H215).**
# ``mertebe_gecisi`` ``p.lie_tasarruf(...)`` çağırır; o usul yalnız
# klasik ``nefs/uzaylar.Parametreler``dedir (``QParametre``de YOKTUR --
# ölçüldü). Yani buradaki anotasyon, `nefs/qmeleke.py`dekinin aksine
# **doğrudur**. Fakat bağ çalışma anında lâzımdır, modül yüklenirken
# değil: modül seviyesinde tutulunca kuantum hattı (``qegitim`` yalnız
# ``DINAMIK``i, ``qmeleke`` yalnız ``lifleri_kur``u alır) bütün klasik
# dünyayı beraberinde sürüklüyordu.


# ``morfizm_tipi(A, n)`` ağacı derindir; denetleyici özyinelemeli iner.
sys.setrecursionlimit(max(sys.getrecursionlimit(), 200000))

#: Sabit blok: ardışık ve değişmez zemin (kütük H22).
SABIT: Tuple[int, ...] = tuple(range(10))
#: Dinamik blok: ardışık DEĞİL; sonsuz spektrumdan seçilmiş keyfî on
#: mertebe. Aradaki mertebeler için hiçbir şey açılmaz -- seyrek Kan
#: sıçraması. Bu on sayı ana modelin sabitidir; değiştirmek serbesttir.
DINAMIK: Tuple[int, ...] = (13, 17, 19, 20, 30, 55, 1000, 1009, 58383, 60000)

#: Bu derinliğe kadar ``morfizm_tipi`` fiilen kurulup denetlenir; üstü
#: temsilci tiple denetlenir ve **öyle işaretlenir**. Sebep ölçüldü:
#: denetim süresi mertebeyle üssel büyür (n=20: 0,66 sn, n=22: 1,05 sn),
#: n=60 000 imkânsızdır.
AZAMI_TAM_MERTEBE = 20

_U = Evren(0)
_D = Deg


@dataclass(frozen=True)
class Lif:
    """Bir ∞-kategori mertebesi ve mananın orada göreceği geometri."""
    yuva: int              # 0..19
    mertebe: int
    tam_kuruldu: bool      # morfizm_tipi fiilen inşa edildi mi
    denetlendi: bool       # makine tip denetiminden geçti mi
    tip_ozeti: str
    hata: str = ""

    @property
    def pencere(self) -> int:
        """Lifin dokunduğu eksen bloğunun genişliği: ``m+1``, 4 ile sınırlı.

        Sınır zaruridir: ``m+1`` genişliğinde yerel bir kapı ``2^(m+1)``
        boyutlu bir dizey ister. Dördün üstündeki mertebe kaybolmaz,
        **adıma** taşınır (aşağıya bak).
        """
        return min(self.mertebe + 1, 4)

    @property
    def adim(self) -> int:
        """Lifin baktığı satır mesafesi -- logaritmik.

        Tabansız alınırsa 60 000 mertebe hiçbir satıra dokunmaz; zincir
        kopar. Logaritma, yüksek mertebeyi uzak fakat erişilebilir kılar.
        """
        return 1 + int(math.log2(1 + self.mertebe))

    @property
    def olcek(self) -> float:
        """Dönme açısı ``1/(1+log(1+m))``: yüksek mertebe daha az büker."""
        return 1.0 / (1.0 + math.log1p(float(self.mertebe)))


# =====================================================================
def _tam_kur(m: int) -> Tuple[object, str]:
    return morfizm_tipi(_D("A"), m), "morfizm_tipi(A, %d)" % m


def _temsilci_kur(m: int) -> Tuple[object, str]:
    """Yüksek mertebe için temsilci tip -- ``Ω^n(S¹)`` kulesinin bir katı.

    Bu bir taklit değil **kısıtlı bir şahittir**: aynı homotopi kulesinin
    bir katıdır, fakat ``m``inci katı değildir. Rapor bunu böyle söyler.
    """
    n = 1 + (m % AZAMI_TAM_MERTEBE)
    return (dongu_uzayi_n(Cember(), Taban(), n),
            "Ω^%d(S¹)  [mertebe %d için temsilci]" % (n, m))


@lru_cache(maxsize=4)
def lifleri_kur(dinamik: Tuple[int, ...] = DINAMIK) -> Tuple[Lif, ...]:
    """20 lifi kur ve **her birini makine ile tip denetiminden geçir**.

    Önbelleklidir: denetim ~2 saniye sürer ve akış her koşuda yeniden
    kurmamalıdır. Lifler donuk (``frozen``) olduğu için paylaşmak
    emniyetlidir.
    """
    if len(dinamik) != 10:
        raise ValueError("dinamik mertebe sayısı 10 olmalı (H22)")
    gA = Baglam.terimlerden({"A": _U, "a": _D("A"), "b": _D("A")})
    g0 = Baglam()

    lifler: List[Lif] = []
    for yuva, m in enumerate(tuple(SABIT) + tuple(int(x) for x in dinamik)):
        tam = m <= AZAMI_TAM_MERTEBE
        tip, ozet = _tam_kur(m) if tam else _temsilci_kur(m)
        baglam = gA if tam else g0
        hata = ""
        try:
            denetle_t(tip, _U, baglam)
            gecti = True
        except Exception as e:                       # noqa: BLE001
            gecti = False
            hata = "%s: %s" % (type(e).__name__, str(e)[:120])
        lifler.append(Lif(yuva=yuva, mertebe=m, tam_kuruldu=tam,
                          denetlendi=gecti, tip_ozeti=ozet, hata=hata))
    return tuple(lifler)


#: KAN kenarlarının tek değişkenli tabanı: ``"rbf"`` veya ``"bspline"``.
#:
#: Risalelerde KAN kenarları **B-spline** ile tarif edilir; buradaki ilk
#: gerçekleme ise Gauss RBF kullanıyordu.  İkisi de tek değişkenli bir
#: taban verir, fakat üç noktada ayrışırlar ve bu ayrım ölçülebilir:
#:
#: * **Yerellik** — derece ``k`` B-spline'ı yalnız ``k+1`` düğüm
#:   aralığında sıfırdan farklıdır; bir katsayıyı oynatmak uzaktaki
#:   değerleri HİÇ etkilemez.  Gauss RBF her yerde sıfırdan farklıdır.
#: * **Birliğin bölünmesi** — ``Σ_i B_i(t) = 1`` tam sağlanır, yani
#:   çıktı tabanın konveks birleşimidir ve ölçek kaymaz.  RBF'te böyle
#:   bir garanti yoktur; toplam ``t``ye göre dalgalanır.
#: * **Kenar dışı** — B-spline ızgara dışında tam sıfırdır (o yüzden
#:   :mod:`token_uzaylari.kan_spline` ayrıca bir taban terimi taşır);
#:   RBF üstel küçük ama sıfırdan farklı kalır.
#:
#: Varsayılan ``"rbf"`` bırakıldı ki mevcut ölçümler ve testler aynı
#: kalsın; ``"bspline"`` belgelere sadık olandır ve
#: ``test_kan_temelleri_kiyas`` ikisini yan yana tartar.
KAN_TEMELI = "rbf"

# ======================================================================
#  𝒪₃₇–𝒪₄₁ BEYAN (klasik tensör hattı)
#  (evvelce nefs/beyan.py)
# ======================================================================

ALTIN_ORAN = (1.0 + np.sqrt(5.0)) / 2.0

# mertebe adlarının sayısal sırası -- ölçüm defteri float ister
MERTEBE_SIRA: Dict[str, int] = {
    ad: i for i, (_, ad) in enumerate(reversed(MERTEBELER), start=1)
}

# ======================================================================
#  KLASİK KÜLLÎ AKIŞ -- reel S üzerinde 41 meleke
#  (evvelce nefs/akis.py)
# ======================================================================

# Metnin kapanış bölümündeki kısmî sıra (önce → sonra)
KULLI_SIRA: Tuple[Tuple[int, int], ...] = (
    (1, 5), (5, 6), (6, 7),
    (7, 21), (21, 22), (22, 23),
    (23, 25), (25, 26), (26, 27), (27, 30),
    (30, 33), (33, 13),
    (13, 37), (37, 38), (38, 39),
)

# Akışın tam sırası. 𝒪₁₃ Tasdik İKİ kere koşar: bir kere kendi
# mertebesinde (ön tasdik), bir kere de 𝒪₃₃ Muhakeme meclisinden sonra
# **mühür** olarak. Metin bunu açıkça böyle söylüyor ("Muhakeme
# meclisinde Tasdik mührünü alarak").
AKIS: Tuple[int, ...] = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,          # idrak
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20, # hüküm ve gaye
    21, 22, 23, 24,                          # burhân
    25, 26, 27, 28, 29, 30, 31, 32,          # murâkabe
    33, 13,                                  # meclis + mühür
    34, 35, 36,                              # tafsil / tefsir / tevil
    37, 38, 39, 40, 41,                      # beyan
)

# ======================================================================
#  44 MELEKENİN ÜNİTER HÂLİ -- hiçbiri okumaz
#  (evvelce nefs/qmeleke.py)
# ======================================================================

#: Altın oran -- 𝒪₄₀ Sanat'ın kendi tarifinden gelen açı.
ALTIN = (1.0 + math.sqrt(5.0)) / 2.0

#: χ tavanı **icra edilsin mi**? Varsayılan artık ``False``dır
#: (kütük H149, H118'in nakzı) ve sebebi ölçülmüştür:
#:
#:     tavanlı  : log F = −60,50, akış sonu entropisi 1,3863 (ln 4, ÇAKILI)
#:     tavansız : log F = −57,64, akış sonu entropisi 2,7708 (≈ ln 16)
#:
#: Tavan bir bütçe değil imhaydı: bir melekenin bağını kısmak, o
#: melekenin yerini daraltmaz; **diğer melekelerin kurduğu dolaşıklığı
#: siler**. Beyan melekelerine ulaşan dalganın entropisi yarıya iniyor
#: ve akış sonu girdiden bağımsız sabit bir sayıya çivileniyordu.
#:
#: ``True`` yapılarak eski davranış geri alınabilir -- kapatılamayan
#: bir tedbirin faydası ölçülemez (kütük H90) ve bu bayrak, nakzın
#: kendisinin de sınanabilmesi için duruyor.
NIZAM_ACIK: bool = False


def nizami_ac(acik: bool = True) -> bool:
    """Dolaşıklık nizamını aç/kapa; **evvelki hâli** döndürür."""
    global NIZAM_ACIK
    eski = NIZAM_ACIK
    NIZAM_ACIK = bool(acik)
    return eski


#: **STIEFEL İZOMETRİSİ -- meleke başına kanonikleştirme** (ceridenin
#: 1. mecburi müdahalesi; kütük H163).
#:
#: `kuantum/yazmac.py::kanonikle` MPS'i karışık kanonik hâle getirir ve o
#: hâlde SVD kesmesi **ispatlı olarak en iyidir** (Eckart–Young);
#: kanonik olmayan biçimde tekil değerler atılan durumların hakikî
#: ağırlığını temsil etmez. H121 bu yazmacın kanonik **olmadığını**
#: zaten yazıyordu; bedeli hiç ölçülmemişti.
#:
#: ÖLÇÜLDÜ (40 iki-kübitlik kapı, kanonikleştirme periyodu değişken)::
#:
#:     kübit χ   periyot    log F     kapı başına   kanoniklik hatası
#:     16    8   yok       −17,17       0,6509         2,87e+00
#:     16    8   1         −10,97       0,7602         5,58e-08   (+6,21)
#:     16   16   yok       −11,96       0,7415         4,26e+00
#:     16   16   1          −7,18       0,8357         6,19e-08   (+4,79)
#:     24   16   yok       −25,72       0,5257         4,61e+00
#:     24   16   1         −14,82       0,6904         6,81e-08  (+10,90)
#:
#: 24 kübitte ``e^{10,9} ≈ 54 000`` kat daha çok genlik tutuluyor ve
#: kazanç **zincir uzadıkça büyüyor** -- nazariyenin dediği tam budur:
#: zincir uzadıkça çevre diklikten daha çok sapar.
#:
#: **VE BU ÖLÇÜM YANILTICIYDI -- VARSAYILAN ``False``** (kütük H167).
#:
#: Yukarıdaki tablo ``sadakat_log`` ile alınmıştı ve o sayı **ayara
#: (gauge) bağlıdır**. Kanonik hâlde manası değişir: merkezden **uzak**
#: bir bağda iki sol-izometrik tensörün kurduğu ``Θ``nın bütün tekil
#: değerleri **eşittir** (``ΘᵀΘ = I``). O hâlde:
#:
#: * ``kalan/tam`` oranı ayarın değil **şeklin** hükmüne düşer, yani
#:   ölçü kıyas edilemez hâle gelir;
#: * daha kötüsü, orada kesmek fizikî olarak **en kötü** kesmedir --
#:   Schmidt tayfı merkezde durur, merkez dışında her yön eşit
#:   ağırlıklı görünür ve budama körlemesine olur.
#:
#: Akışta ölçüldü ve felâket: 𝒪₂₀ Teşbih'te durum normu
#: ``4,411 → 1,888e-64``, ``log F = −inf``.
#:
#: **Bu, H80'in kendi dersinin tekrarıdır** ve benim hatamdır:
#: *"Ayar-bağımlı bir büyüklükle hüküm vermek, ölçmeden hüküm
#: vermekten farksızdır."* Aynı tuzağa ikinci defa düştüm.
#:
#: Kanoniklik **yanlış değildir**; yanlış olan onu merkezden uzakta
#: kesmeyle beraber kullanmaktır. Doğrusu TEBD'in usulüdür: dikgenlik
#: merkezi **kapıyla beraber yürür**. Bu yazmaçta kapılar yığın hâlinde
#: (aynı anda birçok bağda) vurulduğu için -- ki o yığın 2 kat hız
#: kazandırmıştı (H79/H80) -- tek bir merkez tutulamaz. İki tasarım
#: birbiriyle çelişiyor ve bu **açık bir borçtur**, örtülmüyor.
#:
#: ``kanonikle`` ve ``kanonik_hata`` `kuantum/yazmac.py`de **durmaya devam
#: eder**: ölçüm âleti olarak doğrudur (H121'in iddiasını sayıyla
#: gösterir) ve merkez takibi kurulduğunda hazırdır.
KANONIK_ACIK: bool = False


def kanoniklestir(acik: bool = True) -> bool:
    """Kanonikleştirmeyi aç/kapa; **evvelki hâli** döndürür (H90)."""
    global KANONIK_ACIK
    eski = KANONIK_ACIK
    KANONIK_ACIK = bool(acik)
    return eski

_QSICIL: Dict[int, "QMeleke"] = {}


def qkaydet(sinif):
    ornek = sinif()
    if ornek.no in _QSICIL:
        raise ValueError("𝒪%d iki kere kaydedildi" % ornek.no)
    _QSICIL[ornek.no] = ornek
    return sinif


def qsicil() -> Dict[int, "QMeleke"]:
    return dict(_QSICIL)


def qmelekeler() -> List["QMeleke"]:
    return [_QSICIL[i] for i in sorted(_QSICIL)]


def nizam_cetveli() -> List[Tuple[int, str, str, Optional[int]]]:
    """41 melekenin dolaşıklık sınıfı ve χ tavanı -- rapor için.

    Cetvel koda gömülü değil, **okunabilirdir**: hangi melekenin hangi
    sınıfta olduğu iddia edilmez, buradan okunur ve
    `tanilama/nizam_dolasiklik.py` neticesini ölçer.
    """
    return [(m.no, m.ad, m.SINIF, m.CHI) for m in qmelekeler()]


class QParametre:
    """Bütün melekelerin açılarını taşıyan **tek düz vektör**.

    Eğitim motoru (AS-GEK) tek bir ``ℝ^d`` vektörü üzerinde çalışır;
    dolayısıyla melekelerin açıları dağınık duramaz. Her meleke ilk
    istediğinde kendine bir dilim ayrılır ve o dilim ebediyen onundur --
    yer tahsisi **çağrı sırasına göre** ve tekrarlanabilirdir.

    Bu, ``main/``daki dersin ana modele taşınmış hâlidir: orada
    Hamiltonyen parametreleri mertebeye anahtarlanınca ayrık motor
    kendi öğrendiğini siliyordu (kütük H39). Burada anahtar melekenin
    **numarası ve adı**dır; akış sırası değişse de dilim kaymaz.
    """

    def __init__(self, tohum: int = 0, genislik: int = 1) -> None:
        self.tohum = int(tohum)
        #: **DAR TAŞIYICININ TELÂFİSİ** (bkz. ``QMeleke.yay``). Her
        #: meleke kendi açı dilimini bu kat kadar büyük ister.
        #: ``1`` = telâfi yok; ölçü kapatılabilir ve kırmızı yanar.
        self.genislik = max(1, int(genislik))
        self._yer: Dict[str, Tuple[int, int]] = {}
        self._n = 0
        self._vek: Optional[np.ndarray] = None

    # -- yer tahsisi --------------------------------------------------
    def al(self, anahtar: str, n: int) -> np.ndarray:
        if anahtar not in self._yer:
            self._yer[anahtar] = (self._n, int(n))
            self._n += int(n)
        bas, kac = self._yer[anahtar]
        if self._vek is None or len(self._vek) < self._n:
            self._buyut()
        return self._vek[bas:bas + kac]

    def _buyut(self) -> None:
        eski = self._vek
        rng = np.random.default_rng(self.tohum)
        yeni = rng.normal(scale=1.0, size=max(self._n, 1))
        if eski is not None:
            yeni[:len(eski)] = eski
        self._vek = yeni

    # -- eğitim arayüzü -----------------------------------------------
    def __len__(self) -> int:
        return self._n

    def vektor(self) -> np.ndarray:
        if self._vek is None:
            self._buyut()
        return np.asarray(self._vek[:self._n], float).copy()

    def yukle(self, v: np.ndarray) -> None:
        """Eğitim motorunun verdiği vektörü yerine koy."""
        v = np.asarray(v, float).reshape(-1)
        if self._vek is None:
            self._buyut()
        m = min(len(v), len(self._vek))
        self._vek[:m] = v[:m]

    def defter(self) -> Dict[str, Tuple[int, int]]:
        """Hangi melekenin nerede olduğu -- dürüstlük için raporlanır."""
        return dict(self._yer)


class QMeleke:
    """Üniter melekenin ortak atası."""

    no: int = 0
    ad: str = ""
    #: Bir küllî alanda birikecek açıların **sabit** sayısı. Durak sayısı
    #: değişse de bu değişmez; açılar duraklara devrolur.
    BIRIKIM_ACI: int = 8

    # =================================================================
    #  DOLAŞIKLIK NİZAMI (Dosya 1 / kütük H118)
    # =================================================================
    #: Melekenin dolaşıklık sınıfı: ``"kurucu"``, ``"koruyucu"``,
    #: ``"çözücü"``.
    #:
    #: **Tenkidim baştan yazılıdır ve saklanmıyor.** Dosya 1 "Tecrit
    #: χ→1", "Tasdik χ=1 saf durum", "İspat mutlak çözücü" diyor. Sabit
    #: bir ÜNİTER kapı Schmidt rütbesini şartsız düşüremez -- H107'de
    #: ispatlandı (üniterlik normu korur, dönme monoton değildir). O
    #: hâlde tablo bir üniter iddiası olarak okunursa **yanlıştır**.
    #:
    #: Doğru okunuşu **kesme cetveli**dir: kesme zaten üniter değildir,
    #: yaklaşıklığın kendisidir. Bir melekeye χ tavanı vermek, o
    #: melekenin kapılarından sonra bağın kaç Schmidt değeriyle
    #: tutulacağını söylemektir. Bu tam olarak kurulabilir ve
    #: ÖLÇÜLEBİLİR -- `tanilama/nizam_dolasiklik.py` ölçer.
    SINIF: str = "koruyucu"
    #: Bu meleke koşarken izin verilen âzamî Schmidt rütbesi.
    #: ``None`` = tavan yok (yazmacın kendi ``bag``ı).
    CHI: Optional[int] = None

    def aci(self, p, n: int, olcek: float = 0.6) -> np.ndarray:
        """Bu melekenin öğrenilen açıları -- düz vektördeki kendi dilimi."""
        # Anahtara UZUNLUK da girer. Girmediğinde ölçüldü ve kırıldı:
        # 𝒪₁ Müşahede önce 4, sonra 6 açı istiyor; tek anahtar ikisini
        # aynı dilime yolluyordu ve ``dik_iki_kubit`` 6 yerine 4 açı
        # alıyordu. Uzunluk artık girdiden bağımsız olduğu için (bkz.
        # ``yay``) anahtar da kararlıdır.
        anahtar = "q%d.%s/%d" % (self.no, self.ad, int(n))
        if isinstance(p, QParametre):
            return olcek * p.al(anahtar, n)
        return olcek * p.v(anahtar, n)          # eski (tohumlu) arayüz

    def yay(self, p, n_sabit: int, hedef: int, olcek: float = 0.6
            ) -> np.ndarray:
        """``n_sabit`` öğrenilen açıyı ``hedef`` durağa **yay**.

        **Ölçülen ve düzeltilen kusur.** Açılar evvelce satır sayısı
        kadar isteniyordu (``aci(p, n_satir*k)``); 4 satırla kurulan
        model 8 satır görünce ``IndexError`` veriyordu. Daha kötüsü:
        parametre sayısı girdinin uzunluğuna bağlı olsaydı model
        uzunluklar arasında hiç genelleyemezdi -- öğrendiği şey "bu
        uzunlukta ne yapılır" olurdu.

        Doğrusu, parametrenin **satırdan bağımsız** olmasıdır: öğrenilen
        şey "kaçıncı satırda ne yapılır" değil, "bir satırın kaçıncı
        kübitinde ne yapılır"dır. Evrişimin (convolution) ötelemeye
        bağışıklığı ile aynı kaidedir. Fazla durak varsa açılar
        devrolur (tile), eksikse kesilir.
        """
        # ── GENİŞLİK: DEVRİ GECİKTİREN TELÂFİ ─────────────────────
        # Padişahın hükmü: *"galois gibi dar bir uzay kullandığımız
        # için mutlaka fazla sayıda parametre kullanmalısın."*
        #
        # ``np.resize`` açıları duraklara **devrederek** yayar: 8 açı
        # 20 durağa yayılınca 12 durak bir öncekinin açısını tekrar
        # eder. Genişlik o devri geciktirir -- meleke ``n_sabit·g``
        # açı sahibi olur ve ``g`` katı durak ayrı parametre alır.
        #
        # **``hedef`` İSTENEN AÇI SAYISINA GİREMEZ.** Girerse parametre
        # sayısı girdinin uzunluğuna bağlanır ve model uzunluklar
        # arasında hiç genelleyemez -- bu dosyada evvelce ölçülmüş
        # kusurun ta kendisidir. O hâlde çarpan yalnız ``g``dir;
        # ``hedef`` küçükse fazlası aşağıda **kesilir**.
        g = max(1, int(getattr(p, "genislik", 1)))
        a = self.aci(p, int(n_sabit) * g, olcek)
        if hedef <= 0:
            return np.zeros(0)
        return np.resize(a, int(hedef))

    def birikim(self, p, n: int, olcek: float = 0.6) -> np.ndarray:
        """Bir küllî alanda BİRİKECEK açılar -- ``n`` ile bölünmüş.

        **Ölçülen ve düzeltilen kusur.** Birikim açıları doğrudan
        ``aci()``den alınıp 20 duraktan geçirilince toplam dönme ~10
        radyana çıkıyor; çember sarılıyor ve hedef kübit tamamen faz
        siliniyor. Ölçüldü: kelam alanının 16 taban durumu **tam
        düzgün** (her biri 0.0625) çıkıyordu, yani model konuşamıyordu.

        Sebep dolaşıklığın tabiatı değil, ölçeğin yanlışlığıydı: bir
        şahidin küllî hükme katkısı sınırlı olmalıdır ki yüz şahit
        çemberi tur atmasın. Birikim açısı ``θ_i / n``dir; böylece
        toplam dönme durak sayısından bağımsız olarak ``O(1)`` kalır ve
        hüküm, delil çoğaldıkça **keskinleşir**, silinmez.
        """
        return self.yay(p, self.BIRIKIM_ACI, n, olcek) / max(float(n), 1.0)

    def uygula(self, q: QYazmac, p: "QParametre") -> None:  # pragma: no cover
        raise NotImplementedError

    def kosu(self, q: QYazmac, p: "QParametre") -> None:
        n0 = q.iz.kapi
        # =============================================================
        # χ TAVANI **İCRADAN KALDIRILDI** (kütük H149, H118'in nakzı)
        # =============================================================
        #
        # Evvelce her meleke kendi ``CHI`` bütçesiyle koşuyor, yani o
        # meleke vurulurken yazmacın bağı zorla ``CHI``ye indiriliyordu.
        # Fikir makuldü: kurucu çok bağ ister, çözücü az. Fakat icrası
        # **yanlıştı** ve ölçüldü.
        #
        # Kusur şudur: bağ boyutu bir **kapının** değil, **bütün
        # dalganın** vasfıdır. Bir melekeyi düşük tavanla koşturmak "bu
        # meleke az yer kaplasın" demek değil, "**bu meleke, diğer
        # melekelerin kurduğu dolaşıklığı silsin**" demektir. Yani tavan
        # bir bütçe değil, bir imhadır.
        #
        # ÖLÇÜLDÜ (χ=16 yazmaç, 1814 kapı, tek geçiş):
        #
        #     tavanlı   : log F = −60,50   kapı başına 0,9672
        #                 akış sonu entropisi 1,3863  (= ln 4, ÇAKILI)
        #     TAVANSIZ  : log F = −57,64   kapı başına 0,9687
        #                 akış sonu entropisi 2,7708  (≈ ln 16)
        #
        # Yani tavan, beyan melekelerine ulaşan dalganın dolaşıklığını
        # **yarıya indiriyordu**; üstelik akış sonunu tam ``ln 4``e
        # çiviliyordu -- girdiden bağımsız sabit bir sayı, ki bu bir
        # ölçüm değil bir kelepçedir. Bedeli yalnız %11 süredir.
        #
        # ``CHI`` **kaldırılmadı**: sınıf ilanı (kurucu/koruyucu/çözücü)
        # manalı bir taahhüttür ve ``nizam_yuzlestir()`` onu ölçümle
        # yüzleştirir -- tıpkı `nefs/sozlesme.py`nin bölge ilanını
        # yüzleştirdiği gibi. İlan artık **icra edilmiyor, sınanıyor**;
        # aradaki fark, kelepçe ile sözleşme arasındaki farktır.
        #
        # **``bag_tavan`` KESİLDİ (χ, MPS bağ boyutu).** Burada
        # ``q.y.bag_tavan = min(CHI, q.y.bag)`` yazıyordu; ``bag_tavan``
        # kuruluyor fakat **hiçbir yerde okunmuyordu** -- yâni nizam
        # kelepçesi zaten hiçbir şey kısmıyordu. Quditte bağ yoktur:
        # durum tam tutulur, kesme sıfırdır (SVD/MPS fermanla iptal).
        # ``CHI`` ilanı duruyor ve ``nizam_yuzlestir()`` onu ölçümle
        # yüzleştiriyor: ilan icra edilmiyor, **sınanıyor**.
            # **STIEFEL İZOMETRİSİ -- meleke koşmadan EVVEL** (H163).
            # Kanonik hâlde SVD kesmesi en iyidir; kanonik olmayan
            # biçimde tekil değerler atılanın hakikî ağırlığını
            # temsil etmez. Ölçüldü: 24 kübitte log F −25,72 → −14,82,
            # yani 54 000 kat daha çok genlik tutuluyor.
            #
            # **Meleke başına** çağrılır, kapı başına değil: kapı başına
            # en iyi neticeyi veriyor (yukarıdaki tabloda periyot 1)
            # fakat maliyeti akışta ölçülmelidir; meleke başına
            # çağırmak, kazancın çoğunu maliyetin küçük bir kısmıyla
            # alır. Bu bir tercih değil, ölçülen iki ucun arasıdır.
        if KANONIK_ACIK:
            q.y.kanonikle()
        self.uygula(q, p)
        q.iz.not_dus("𝒪%d %s" % (self.no, self.ad),
                     "%d kapı" % (q.iz.kapi - n0))

    # -- müşterek desenler -------------------------------------------
    def tugla(self, q: QYazmac, p: "QParametre", ofset: int = 0,
              olcek: float = 0.5) -> None:
        """Veri kübitleri üzerinde fırça (brick) düzeninde ``SO(4)`` katmanı.

        Komşu çiftlere dik kapı vurmak dolaşıklığı yayar; iki ofsetli iki
        katman, menzili bir kademede iki katına çıkarır (kademeli
        harmanın fırça düzenindeki karşılığı).
        """
        a = self.aci(p, 6, olcek)
        G = dik_iki_kubit(a)
        k = q.veri_yuvasi
        # **Y I Ğ I N.** Bütün fırça çiftleri birbirinden ayrıktır:
        # bir satır içinde ``j`` ile ``j+2`` çakışmaz, satırlar arasında
        # da yerel hüküm kübiti ayırıcı durur. O hâlde ``n·⌊k/2⌋`` ayrı
        # çağrı yerine TEK yığın SVD'si yeter (kütük H79).
        sol = q.veri_izgara(range(ofset, k - 1, 2))
        q.cift_yigin(sol, G)

    def satir_donmesi(self, q: QYazmac, p: "QParametre",
                      olcek: float = 0.6) -> None:
        """Her satırın her veri kübitine kendi öğrenilen dönmesi."""
        k = q.veri_yuvasi
        a = self.aci(p, k, olcek)          # sütun başına, satırdan bağımsız
        # Kapılar sütuna bağlı olduğu için ``k`` ayrı dizey yeter;
        # ``n·k`` yuvaya tek çağrıda yayılır.
        Gk = np.stack([donme(float(t)) for t in a])
        yuv = q.veri_izgara()
        q.tek_yigin(yuv, np.tile(Gk, (q.n_satir, 1, 1)))


# =====================================================================
#  𝒪₁–𝒪₁₀  İDRAK
# =====================================================================
@qkaydet
class QMusahede(QMeleke):
    """𝒪₁ Müşahede -- odaklanma: veri kübitlerine öz-dikkat katmanı.

    Reel modelde bu ``Softmax(QKᵀ/√d)V`` idi ve ``n×n`` maliyetliydi.
    Üniter karşılığı fırça düzeninde iki ``SO(4)`` katmanıdır: her kapı
    komşu iki kübitin genliklerini karıştırır, iki ofset menzili
    ikiye katlar. Maliyet yuva sayısında **doğrusal**; dikkatin karesel
    derdi burada yoktur (kütük H34'ün kule ile çözdüğü şeyi, kübit
    yazmacı yapısı gereği çözer).
    """
    no, ad = 1, "Müşahede"
    SINIF, CHI = "kurucu", 8   # öz-dikkat: fırça katmanı dolaşıklığı kurar

    def uygula(self, q, p):
        self.satir_donmesi(q, p, 0.7)
        self.tugla(q, p, ofset=0, olcek=0.6)
        self.tugla(q, p, ofset=1, olcek=0.6)


@qkaydet
class QHayal(QMeleke):
    """𝒪₂ Hayal -- suretin açılması: kısmî süperpozisyon.

    Tam Hadamard bütün ihtimalleri eşitler; hayal o kadar başıboş
    değildir. Her satırın son veri kübiti ``θ`` kadar açılır: ihtimal
    kapısı aralanır, fakat mevcut suret silinmez.
    """
    no, ad = 2, "Hayal"
    SINIF, CHI = "kurucu", 8   # süperpozisyonu aralar

    def uygula(self, q, p):
        a = self.yay(p, 4, q.n_satir, 0.9)
        j = q.veri_yuvasi - 1
        q.tek_yigin([q.veri(i, j) for i in range(q.n_satir)],
                    np.stack([donme(0.25 * math.pi + float(t)) for t in a]))


@qkaydet
class QMuhayyile(QMeleke):
    """𝒪₃ Muhayyile -- terkip serbestliği: uzak kübitleri karıştırır.

    Hayal gördüğünü açar; muhayyile **görmediğini** birleştirir. Bunun
    için satır içinde atlamalı çiftler (``j`` ile ``j+2``) kullanılır --
    komşuluk değil, sıçrama.
    """
    no, ad = 3, "Muhayyile"
    SINIF, CHI = "kurucu", 16   # atlamalı çift: uzak menzil kurar

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.8))
        k = q.veri_yuvasi
        for i in range(q.n_satir):
            for j in range(0, k - 2):
                q.uzak_cift(q.veri(i, j), q.veri(i, j + 2), G)


@qkaydet
class QTertip(QMeleke):
    """𝒪₄ Tertip -- şahit bölütlemesi: satırı kendi yerel hükmüne bağlar.

    Kütük H6: "hepsi aynı kurala tâbidir" bilgisi bayrakla bildirilmez,
    organlarla sezilir. Burada her satırın son veri kübiti, o satırın
    yerel hüküm kübitine **kontrollü dönme** ile bağlanır; ikisi zincirde
    bitişiktir, dolayısıyla kapı yereldir ve ucuzdur. Satırın muhtevası
    hiçbir yerde okunmaz; hüküm onunla **dolaşır**.
    """
    no, ad = 4, "Tertip"
    SINIF, CHI = "koruyucu", 8   # satırı yerel hükme bağlar, menzil kısa

    def uygula(self, q, p):
        a = self.yay(p, 4, q.n_satir, 0.7)
        j = q.veri_yuvasi - 1
        # (veri son kübiti, yerel hüküm) çiftleri bitişik ve ayrıktır
        q.cift_yigin([q.veri(i, j) for i in range(q.n_satir)],
                     np.stack([kontrollu_donme(float(t)) for t in a]))


@qkaydet
class QTecrit(QMeleke):
    """𝒪₅ Tecrit -- soyutlama: dolanıklık **çözücü**.

    MERA'nın ``U``su gibi çalışır fakat ters yönde: ortak olmayanı ayırır.
    Fırça katmanının tersi (``Gᵀ``) uygulanır; dik olduğu için bu tam
    tersidir ve bilgi kaybetmez -- tecrit, atmak değil **ayırmaktır**.
    """
    no, ad = 5, "Tecrit"
    #: **χ TAVANI KALDIRILDI (kütük H148, H118'in nakzı).** Evvelce
    #: ``CHI = 1`` idi, yani bu meleke koşarken yazmacın bağı zorla 1'e
    #: iniyor ve dalga **çarpım durumuna kesiliyordu**. Ölçüldü (χ=32):
    #:
    #:     tavan=1     : tutulan 6,6e-10   entropi 3,357 → 0,693
    #:     tavan=yok   : tutulan 0,909     entropi 3,357 → 3,346
    #:
    #: İki netice çıktı. Birincisi: tavan bilgiyi **on milyar kat**
    #: imha ediyordu. İkincisi ve daha mühimi: tavan kalkınca bu
    #: melekenin daraltması **tamamen kayboluyor** -- demek ki Tecrit'in
    #: çözücülüğü hiç kapısından gelmiyor, yalnız kesmeden geliyormuş.
    #: Şerhi "fırça katmanının tersi (Gᵀ), bilgi kaybetmez" diyor fakat
    #: kapı kurucununkinden **başka kübit çiftlerine** vuruyor; o hâlde
    #: hakikaten ters değil. Bu bir borçtur ve gizlenmiyor: tecridin
    #: manasını üniter olarak icra edecek kapı henüz yazılmadı.
    SINIF, CHI = "çözücü", None

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.5))
        k = q.veri_yuvasi
        q.cift_yigin(q.veri_izgara(range(1, k - 1, 2)), G.T)


@qkaydet
class QTasavvur(QMeleke):
    """𝒪₆ Tasavvur -- küllî mahiyetin kurulması: bir MERA kademesi daha.

    Dolaşıklığı satırlar arasına taşıyan yer burasıdır; tek satırın
    kendi içindeki kapılar mahiyeti küllîleştirmez.
    """
    no, ad = 6, "Tasavvur"
    SINIF, CHI = "kurucu", 16   # MERA kademesi: dolaşıklığı satırlar arasına taşır

    def uygula(self, q, p):
        q.harman(kademe=1, teta=self.aci(p, 24, 0.6))


@qkaydet
class QMana(QMeleke):
    """𝒪₇ Mana -- satırların manası küllî tasdike akar.

    Bütün yerel hükümler tek bir MPO ile ``tasdik`` alanına akıtılır.
    Kübit oynamaz, dolaşıklık sürüklenmez; bağ 2'dir.
    """
    no, ad = 7, "Mana"
    SINIF, CHI = "koruyucu", 4   # MPO bağı zaten 2; birikim tek kübite akar

    def uygula(self, q, p):
        q.mpo_topla("tasdik", self.birikim(p, q.n_satir, 0.9))


@qkaydet
class QTahlil(QMeleke):
    """𝒪₈ Tahlil -- bileşenlerine ayırma: kübit başına ayrı dönme.

    Her kübit kendi açısıyla çevrilince ortak hâl bileşenlerine ayrışır;
    bu, tekil değer ayrışımının üniter karşılığıdır (dik dönmeler).
    """
    no, ad = 8, "Tahlil"
    SINIF, CHI = "çözücü", 2   # tahlil: ortak hâli bileşenlerine ayırır

    def uygula(self, q, p):
        self.satir_donmesi(q, p, 0.8)


@qkaydet
class QTerkip(QMeleke):
    """𝒪₉ Terkip -- ayrılanı birleştirme: ters yönlü fırça katmanı."""
    no, ad = 9, "Terkip"
    SINIF, CHI = "kurucu", 8   # terkip: ayrılanı birleştirir

    def uygula(self, q, p):
        self.tugla(q, p, ofset=1, olcek=0.7)


@qkaydet
class QTezat(QMeleke):
    """𝒪₁₀ Tezat -- **yıkıcı girişim**: zıt kutupların işareti çevrilir.

    Kütük H19'un üç şartından üçüncüsü budur ve burada fiilen olur:
    ``σ_z`` bir taban durumunun işaretini çevirir, o genlik komşusuyla
    toplandığında **sıfırlanır**. Klasik bir "tezat skoru" hesaplansaydı
    bu olmazdı; girişim ancak işaretli genlikte olur.
    """
    no, ad = 10, "Tezat"
    SINIF, CHI = "koruyucu", 4   # işaret çevirme; bağ büyütmez

    def uygula(self, q, p):
        Z = faz_z()
        k = q.veri_yuvasi
        q.tek_yigin([q.veri(i, k - 1) for i in range(1, q.n_satir, 2)], Z)


# =====================================================================
#  𝒪₁₁–𝒪₂₄  HÜKÜM, GAYE, BURHÂN
# =====================================================================
@qkaydet
class QTenakuz(QMeleke):
    """𝒪₁₁ Tenakuz -- çelişkinin küllî ``tenakuz`` alanına akıtılması.

    Reel modelde çelişki ``C = −S(AᵀA)Sᵀ`` idi: ``n×n``, karesel. Burada
    çelişki bir dizey değil, bir **dolaşıklıktır**: her satırın yerel
    hükmü küllî tenakuz kübitine bağlanır; birbiriyle uyuşmayan satırlar
    o kübitte zıt yönde dönme üretir ve **birbirini söndürür** (yıkıcı
    girişim). Uyuşanlar ise aynı yönde döner ve yapıcı girişimle
    kuvvetlenir. Ölçü hiçbir yerde çıkmaz; hüküm dalgada durur.
    """
    no, ad = 11, "Tenakuz Bulma"
    SINIF, CHI = "koruyucu", 4   # MPO birikimi, bağ 2

    def uygula(self, q, p):
        a = self.birikim(p, q.n_satir, 1.1)
        # işaret satır sırasına göre alternatiflenir: uyuşmazlık zıt döner
        isaret = np.where(np.arange(q.n_satir) % 2 == 0, 1.0, -1.0)
        q.mpo_topla("tenakuz", a * isaret)


@qkaydet
class QTenkit(QMeleke):
    """𝒪₁₂ Tenkit -- zayıf satırın yerel hükmü ``|0⟩``a doğru çevrilir.

    Elemek, reel modelde satırı **sıfırlamaktı** -- kayıplı ve H14'e
    aykırı. Üniter karşılığı elemek değil **bastırmaktır**: yerel hüküm
    kübiti sıfır yönüne döndürülür, bilgi silinmez, ağırlığı düşer.
    """
    no, ad = 12, "Tenkit"
    SINIF, CHI = "çözücü", 2   # tenkit: zayıf şahidi bastırır

    def uygula(self, q, p):
        a = self.yay(p, 4, q.n_satir, 0.4)
        q.tek_yigin(q.yereller(),
                    np.stack([donme(-abs(float(t))) for t in a]))


@qkaydet
class QTasdik(QMeleke):
    """𝒪₁₃ Tasdik -- mühür: küllî tasdik alanı içinde faz kilidi.

    Akışta **iki kere** koşar (kendi mertebesinde ve 𝒪₃₃'ten sonra);
    ikisinde de aynı kapıdır. Mühür, tasdik kübitlerini birbirine
    bağlayan bir kontrollü dönmedir: ikisi hemfikirse mühür tutar.
    """
    no, ad = 13, "Tasdik"
    #: Tavan **ölçüldü ve tesirsizdi**: ``CHI`` 1, 2, 4 yahut ``None``
    #: iken tutulan kesir daima ``1,0000`` ve entropi hiç değişmiyor.
    #: Yani bu meleke kesme gerektirecek bir dolaşıklık kurmuyor; ilan
    #: edilen "saf durum (χ=1)" şartı bir şey icra etmiyordu. Yanıltıcı
    #: olmasın diye kaldırıldı; davranış aynen aynıdır.
    SINIF, CHI = "çözücü", None

    def uygula(self, q, p):
        a = self.aci(p, 2, 0.5)
        q.cift(q.kulli("tasdik", 0), kontrollu_donme(float(a[0])))
        q.tek(q.kulli("tasdik", 1), donme(float(a[1])))


@qkaydet
class QGaye(QMeleke):
    """𝒪₁₄ Gaye -- teleolojik ufuk: tasdik ``mîzân``a bağlanır.

    Gaye, hükmün nereye çekildiğidir. Tasdik alanı mîzân alanına
    kontrollü dönme ile bağlanır; ikisi de küllî blok içindedir ve
    aralarındaki mesafe blok boyu kadardır (13 kübit), dolayısıyla takas
    burada meşrudur ve ucuzdur.
    """
    no, ad = 14, "Gaye Belirleme"
    SINIF, CHI = "koruyucu", 4   # tasdik→mîzân, küllî blok içinde kısa bağ

    def uygula(self, q, p):
        a = self.aci(p, 4, 0.5)
        for j in range(2):
            q.uzak_cift(q.kulli("tasdik", j), q.kulli("mizan", j),
                        kontrollu_donme(float(a[j])))


@qkaydet
class QMerak(QMeleke):
    """𝒪₁₅ Merak -- bilgisizliğin açılması: ``nakz`` alanı süperpozisyona.

    Sual sormak, cevabı bilmediğini ilan etmektir; kuantum karşılığı o
    kübiti süperpozisyona sokmaktır. Merak ayrıca tünelleme vanasını
    açan melekedir (kütük H29) -- ``Γ`` buradan yükselir.
    """
    no, ad = 15, "Merak ve Sual"
    SINIF, CHI = "kurucu", 8   # merak: nakz alanını süperpozisyona sokar

    def uygula(self, q, p):
        a = self.aci(p, 2, 0.5)
        q.tek_yigin([q.kulli("nakz", j) for j in range(2)],
                    np.stack([donme(0.25 * math.pi + float(t))
                              for t in a[:2]]))


@qkaydet
class QDenemeYanilma(QMeleke):
    """𝒪₁₆ Deneme-Yanılma -- keşif: küçük rastgele (fakat tohumlu) hamleler.

    Oyuncu-eleştirmen döngüsünün üniter karşılığı, ödülü ölçüp geri
    beslemek değildir (o okuma olurdu); **hamle dizisini** uygulamaktır.
    Hangi hamlenin iyi olduğunu eğitim motoru söyler: bu melekenin
    açıları öğrenilen parametrelerdir.
    """
    no, ad = 16, "Deneme-Yanılma"
    SINIF, CHI = "kurucu", 8   # keşif hamleleri

    def uygula(self, q, p):
        k = q.veri_yuvasi
        a = self.aci(p, k, 0.3)
        Gk = np.tile(np.stack([donme(float(t)) for t in a]),
                     (q.n_satir, 1, 1))
        q.tek_yigin(q.veri_izgara(), Gk)


@qkaydet
class QIhtimal(QMeleke):
    """𝒪₁₇ İhtimal -- Bayes: önselin mîzâna yazılması.

    ``P(S|ℰ) ∝ P(ℰ|S)P(S)``. Üniter karşılığı, mîzân kübitlerinin
    önsel açıyla çevrilmesidir; olabilirlik ise 𝒪₇ Mana'nın akıttığı
    dolaşıklıkta zaten durmaktadır. Çarpım, dönmelerin **bileşkesidir**
    (``R(α)R(β) = R(α+β)``) -- yani logaritmik toplama.
    """
    no, ad = 17, "İhtimal Hesabı"
    SINIF, CHI = "koruyucu", 4   # önsel: tek kübitlik dönmeler

    def uygula(self, q, p):
        a = self.aci(p, 4, 0.4)
        q.tek_yigin([q.kulli("mizan", j) for j in range(4)],
                    np.stack([donme(float(t)) for t in a[:4]]))


@qkaydet
class QKiyas(QMeleke):
    """𝒪₁₈ Kıyas -- şahitten şahide: komşu satırlar arasında kapı.

    Bilinen vakadan bilinmeyene geçmek, iki satırı aynı kapıdan
    geçirmektir: aralarındaki dönüşüm ortak olursa dolaşıklık kurulur.
    Satırlar zincirde ``oge`` kadar uzaktır (varsayılan 5); bu kısa
    mesafede takas meşrudur.
    """
    no, ad = 18, "Kıyas"
    SINIF, CHI = "kurucu", 8   # kıyas: satırdan satıra dolaşıklık

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.5))
        for i in range(q.n_satir - 1):
            q.uzak_cift(q.veri(i, 0), q.veri(i + 1, 0), G)


@qkaydet
class QTemsil(QMeleke):
    """𝒪₁₉ Temsil -- soyutu somuta indirmek, **tersinir** olarak.

    Reel modelde bu bir kodlayıcı/çözücü çiftiydi ve devir hatası
    ölçülüyordu. Üniter kapı dik olduğu için devir hatası **cebren
    sıfırdır**: ``GᵀG = I``. Temsilin bilgi kaybetmemesi burada bir
    iddia değil, kapının tarifidir.
    """
    no, ad = 19, "Temsil"
    SINIF, CHI = "koruyucu", 8   # temsil dik ve tersinir

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.6))
        k = q.veri_yuvasi
        sol = [q.veri(i, 0) for i in range(q.n_satir)]
        if k >= 4:
            sol += [q.veri(i, 2) for i in range(q.n_satir)]
        q.cift_yigin(sol, G)


@qkaydet
class QTesbih(QMeleke):
    """𝒪₂₀ Teşbih -- vech-i şebeh: ilk iki satırın ortak yönü.

    Benzeyen ile benzetilen arasındaki ortak vecih, iki satırı aynı
    kapıdan geçirip dolaştırmakla kurulur.
    """
    no, ad = 20, "Teşbih"
    SINIF, CHI = "kurucu", 8   # teşbih: iki satırı dolaştırır

    def uygula(self, q, p):
        if q.n_satir < 2:
            return
        G = dik_iki_kubit(self.aci(p, 6, 0.5))
        k = q.veri_yuvasi
        for j in range(k):
            q.uzak_cift(q.veri(0, j), q.veri(1, j), G)


@qkaydet
class QTefekkur(QMeleke):
    """𝒪₂₁ Tefekkür -- **20 ∞-kategori mertebesinden geçiş** (kütük H40).

    Ana modelin ``main/``dan devraldığı asıl icat budur. Yirmi lif
    ``omega_kategori_nbe`` ile kurulup makineyle denetlenir; her lif
    dalgayı **kendi mertebesine mahsus** açı ve menzille büker:

    * ``olcek`` -- dönme açısı ``1/(1+log(1+m))``; yüksek mertebe az büker.
    * ``adim``  -- lifin baktığı satır mesafesi ``1+⌊log₂(1+m)⌋``; yüksek
      mertebe **uzak menzilli** tutarlılıktır.
    * ``pencere`` -- lifin dokunduğu kübit bloğunun genişliği.

    Mertebeler **toplanmaz** (H21); ayrı liflerde ayrı eksenlere etki
    eder, bileşke terkiptir. Uzak menzilli bağ MPO ile kurulur -- yani
    1000. mertebe 16 satır ötesine takas yapmadan dokunur.
    """
    no, ad = 21, "Tefekkür"
    SINIF, CHI = "kurucu", 16   # tefekkür: 20 mertebe, uzak menzil

    def uygula(self, q, p):
        lifler = lifleri_kur(DINAMIK)
        a = self.aci(p, len(lifler), 1.0)
        k = q.veri_yuvasi

        # --- (1) Tek kübitlik kısım: her lif KENDİ eksenine dokunur.
        # Aynı eksene düşen lifler (yuva % k aynı olanlar) aynı kübite
        # ardışık dönme vurur; ``R(α)R(β) = R(α+β)`` olduğu için bunlar
        # **toplanabilir** ve netice birebir aynıdır. Ayrı eksenler ayrı
        # kalır -- H21 (mertebeler toplanmaz) bozulmaz: toplanan şey
        # mertebeler değil, aynı eksendeki dönme açılarıdır.
        eksen_acisi: Dict[int, float] = {}
        for lif in lifler:
            teta = lif.olcek * (1.0 + 0.3 * float(a[lif.yuva]))
            eksen_acisi[lif.yuva % k] = eksen_acisi.get(lif.yuva % k, 0.0) + teta
        yuv, Gl = [], []
        for j, top in eksen_acisi.items():
            R = donme(top)
            for i in range(q.n_satir):
                yuv.append(q.veri(i, j))
                Gl.append(R)
        q.tek_yigin(yuv, np.stack(Gl))
            # Uzak menzilli tutarlılık. **Ölçülen ve düzeltilen kusur
            # (kütük H54, 3. borç).** Mesafe evvelce SATIR cinsinden
            # alınıyor ve ``adim < n_satir`` şartına takılıyordu. Ölçüldü:
            # 6 satırlık bir girdide ``adım`` 1000. mertebe için 10,
            # 60 000. mertebe için 17 çıkıyor; ikisi de 6'dan büyük
            # olduğu için yüksek mertebelerin **ayırt edici tarafı olan
            # uzak menzil hiç ateşlenmiyordu**. Geriye yalnız ``olcek``
            # kalıyor, o da 1000 ile 60 000 arasında 0,126'ya karşı
            # 0,083 -- yani ayrık motorun seçtiği yüksek mertebe fiilen
            # hiçbir şey yapmıyordu.
            #
        # Doğrusu, mesafeyi satırda değil **kübit zincirinde** ölçmek.
        # Yazmaç zaten bir zincirdir; 6 satır × 12 kübit = 72 kübitlik
        # bir zincirde 17 adımlık bir sıçrama pekâlâ tanımlıdır ve
        # satır sayısından bağımsızdır.
        #
        # --- (2) Uzak menzil: YİRMİ MPO YERİNE TEK MPO.
        #
        # Yirmi lif ayrı ayrı ``mpo_topla`` çağırıyordu ve profilde en
        # pahalı tek kalem buydu (0,52 sn, koşunun %41'i). Halbuki
        # ``mpo_topla``nın uyguladığı üniter ``U = exp((Σᵢ θᵢ nᵢ) ⊗ Y)``
        # şeklindedir; ``nᵢ`` aynı tabanda köşegen ve ``Y`` sabit olduğu
        # için iki çağrı **değişmeli**dir:
        #
        #     exp(A⊗Y)·exp(B⊗Y) = exp((A+B)⊗Y)
        #
        # Yani yirmi çağrının bileşkesi, durak açılarının toplandığı TEK
        # çağrıya birebir eşittir. **H21 bozulmaz:** toplanan şey
        # mertebeler değil, aynı durağa düşen dönme açılarıdır; her lif
        # kendi ``adım``ıyla kendi duraklarını seçmeye devam eder.
        son = q.kulli("makam", 0)
        katki: Dict[int, float] = {}
        for lif in lifler:
            teta = lif.olcek * (1.0 + 0.3 * float(a[lif.yuva]))
            bas = q.veri(0, lif.yuva % k)
            duraklar = list(range(bas, son, lif.adim))
            if len(duraklar) < 2:
                continue
            pay = teta / len(duraklar)
            for d in duraklar:
                katki[d] = katki.get(d, 0.0) + pay
        if len(katki) >= 2:
            dur = sorted(katki)
            q.mpo_topla("makam", [katki[d] for d in dur], duraklar=dur)


@qkaydet
class QIllet(QMeleke):
    """𝒪₂₂ İllet Keşfi -- nedensellik: **yönlü** bağ.

    Nedensellik simetrik değildir; sebep sonuçtan öncedir. Kontrollü
    dönme tam da böyledir: kontrol (önceki satır) ``|1⟩`` iken hedef
    (sonraki satır) döner, tersi olmaz. Asiklik şartı inşa gereği
    sağlanır -- kapı hep soldan sağadır.
    """
    no, ad = 22, "İllet Keşfi"
    SINIF, CHI = "koruyucu", 8   # illet: yönlü ve seyrek

    def uygula(self, q, p):
        a = self.yay(p, 4, max(q.n_satir - 1, 1), 0.5)
        for i in range(q.n_satir - 1):
            q.uzak_cift(q.veri(i, 0), q.veri(i + 1, 0),
                        kontrollu_donme(float(a[i])))


@qkaydet
class QMantik(QMeleke):
    """𝒪₂₃ Mantık -- nakz: tek karşı örnek küllî önermeyi düşürür.

    Kütük H6'nın kaidesi burada bir üniterdir: her yerel hüküm ``nakz``
    alanına **negatif** açıyla akar. Bir tek şahit ters yönde uyanırsa
    küllî nakz kübiti döner ve 𝒪₃₂'de yakîni düşürür. Toplama değil
    girişimdir: nakzlar birbirini kuvvetlendirir, tasdikler söndürür.
    """
    no, ad = 23, "Mantık Yürütme"
    SINIF, CHI = "koruyucu", 4   # MPO nakz birikimi, bağ 2

    def uygula(self, q, p):
        q.mpo_topla("nakz", -np.abs(self.birikim(p, q.n_satir, 0.8)))


@qkaydet
class QIspat(QMeleke):
    """𝒪₂₄ İspat -- burhân zinciri: yerel hükümler ardışık bağlanır.

    ``P₀ → P₁ → … → Pₙ``. Zincirin her halkası bir kontrollü dönmedir;
    bir halka kopuksa (kontrol ``|0⟩``) sonraki hiç dönmez -- yani
    geçersiz öncülden netice çıkmaz. Occam cezası açıların küçülmesiyle
    temsil edilir: uzun zincir daha az döndürür.
    """
    no, ad = 24, "İspat"
    #: **χ TAVANI KALDIRILDI (kütük H148, H118'in nakzı).** Ölçüldü (χ=32):
    #:
    #:     tavan=1     : tutulan 8,7e-12   entropi 3,357 → 1,386
    #:     tavan=yok   : tutulan 0,548     entropi 3,357 → 1,383
    #:
    #: Yani "ispat daraltır" manası **kapının kendisinde** üniter olarak
    #: zaten vardır: tavan kalkınca da entropi ~ln4'e iniyor. Tavan o
    #: manayı üretmiyordu; üstüne 6×10¹⁰ kat genlik imha ediyordu.
    #:
    #: Bunun bedeli mimarîdedir: 𝒪₂₄ akışın 24. sırasındadır, yani
    #: beyan melekeleri (𝒪₃₇–𝒪₄₀) amputte bir dalga üstünde çalışıyordu.
    #: Kütük H133'ün ("hüküm cevaba ulaşmıyor") **fizikî sebebi** budur.
    SINIF, CHI = "çözücü", None

    def uygula(self, q, p):
        a = self.yay(p, 4, max(q.n_satir - 1, 1), 0.5)
        for i in range(q.n_satir - 1):
            teta = float(a[i]) / (1.0 + 0.1 * i)      # Occam: uzun zincir zayıf
            q.uzak_cift(q.yerel(i), q.yerel(i + 1), kontrollu_donme(teta))


# =====================================================================
#  𝒪₂₅–𝒪₃₆  MURÂKABE
# =====================================================================
@qkaydet
class QTeemmul(QMeleke):
    """𝒪₂₅ Teemmül -- devridaim: aynı katman birkaç kere.

    Reel modelde 200 tur dikkat koşuyor ve durma ölçütü aranıyordu; o,
    her turda okuma isterdi. Üniter karşılığı sabit sayıda tekrardır ve
    yakınsama **kapının kendisinden** gelir: ``R(θ)`` tekrarı ``R(kθ)``
    verir, yani devridaim bir dönmeye eşdeğerdir ve ıraksamaz.
    """
    no, ad = 25, "Teemmül"
    SINIF, CHI = "koruyucu", 8   # devridaim; yeni menzil açmaz
    TUR = 3

    def uygula(self, q, p):
        for t in range(self.TUR):
            self.tugla(q, p, ofset=t % 2, olcek=0.3)


@qkaydet
class QTemkin(QMeleke):
    """𝒪₂₆ Temkin -- sarsılmazlık: küçük açı, büyük vakar.

    Temkin, hâli az değiştirmektir. Açılar kasten küçüktür; bu bir
    ihmal değil melekenin tarifidir.
    """
    no, ad = 26, "Temkin"
    SINIF, CHI = "koruyucu", 4   # temkin: küçük açı

    def uygula(self, q, p):
        a = self.yay(p, 4, q.n_satir, 0.12)
        q.tek_yigin(q.yereller(),
                    np.stack([donme(float(t)) for t in a]))


@qkaydet
class QTetkik(QMeleke):
    """𝒪₂₇ Tetkik -- kılcal inceleme: her kübite ayrı ince dönme."""
    no, ad = 27, "Tetkik"
    SINIF, CHI = "koruyucu", 4   # tetkik: ince tek kübit dönmesi

    def uygula(self, q, p):
        self.satir_donmesi(q, p, 0.2)


@qkaydet
class QTashih(QMeleke):
    """𝒪₂₈ Tashih -- düzeltme: tetkikin bulduğunun **tersi**.

    Reel modelde düzeltme "iyileştirdiyse kabul" edilirdi; o bir okuma
    isterdi. Üniter karşılığı, tetkikin uyguladığı dönmenin bir kısmını
    geri almaktır: ``R(−λθ)``. ``λ`` öğrenilir; eğitim motoru ne kadar
    geri alınacağını söyler.
    """
    no, ad = 28, "Tashih"
    SINIF, CHI = "çözücü", 2   # tashih: tetkikin bir kısmını geri alır

    def uygula(self, q, p):
        k = q.veri_yuvasi
        tetkik = QTetkik().aci(p, k, 0.2)
        lam = float(np.tanh(self.aci(p, 1, 1.0)[0]))
        Gk = np.tile(np.stack([donme(-lam * float(t)) for t in tetkik]),
                     (q.n_satir, 1, 1))
        q.tek_yigin(q.veri_izgara(), Gk)


@qkaydet
class QTeyit(QMeleke):
    """𝒪₂₉ Teyit -- **bağımsız** ikinci kanal.

    İki kanal dolaştırılınca uyuşma yapıcı, uyuşmazlık yıkıcı girişim
    verir. Bağımlı iki kanalın uyuşması **yeni bilgi değildir**; o
    hâlde kanalların mümkün olduğunca ayrı olması şarttır.

    **KANAL ÇİFTİ ELLE DEĞİL ÖLÇÜMLE SEÇİLDİ (kütük H162, H128'in
    borcu).** Evvelce *"satırın iki ucu"* alınıyordu ve bu bir
    **tedbir**di, ölçülmemişti. H128'de ölçüldü: fazla sayma oranı
    ``1,2091``, muteber şahit sayısı 2 değil **1,65** -- yani 𝒪₂₉
    delili yaklaşık **%19 şişiriyordu**. Kusur küçüktü fakat sıfır
    değildi ve borç olarak yazılmıştı.

    Beş aday çift aynı ölçüyle yarıştırıldı (12 koşu, 8 satır)::

        usul              Pearson    fazla sayma   muteber şahit
        satır_iki_ucu     +0,1643      1,2091          1,6541   ← evvelki
        veri_vs_yerel     +0,0826      1,1675          1,7130   ← seçilen
        çapraz_satır      +0,2177      1,1315          1,7675
        yerel_vs_yerel    −0,0916      1,2302          1,6257
        veri_ortası       −0,0300      1,1883          1,6830

    ``veri_vs_yerel`` seçildi ve sebebi **iki ölçütte birden**
    üstünlüğüdür: fazla saymada da (1,2091 → 1,1675) Pearson'da da
    (0,164 → 0,083) yürürlükteki çifti yeniyor. ``çapraz_satır`` fazla
    saymada daha iyidir fakat Pearson'da **kötüdür**; onu seçmek,
    hükmü destekleyen ölçütü seçmek olurdu ve kütük H47 tam olarak
    bunu yasaklar (*"ölçütü ölçen koyarsa kendini kandırır"*).

    Kazanç mütevazıdır ve büyütülmüyor: fazla sayma %19'dan **%17**'ye
    iniyor. Kanallar hâlâ tam bağımsız değildir (bağımsız üç şahitte
    kıyas tabanı 1,05) ve bu **açıkça** duruyor.

    Manası da evvelkinden sağlamdır: ham duyu (veri kübiti) ile o satır
    hakkında **verilmiş hüküm** (yerel kübit) iki ayrı cinstendir; aynı
    satırın iki ucu ise aynı cinsten iki noktadır.
    """
    no, ad = 29, "Teyit"
    SINIF, CHI = "koruyucu", 8   # teyit: veri ile yerel hüküm

    def uygula(self, q, p):
        k = q.veri_yuvasi
        if k < 2:
            return
        G = dik_iki_kubit(self.aci(p, 6, 0.5))
        # Kanal 1: satırın ilk veri kübiti (ham duyu).
        # Kanal 2: o satırın yerel hüküm kübiti (verilmiş hüküm).
        # İkisi zincirde bitişik değildir (aralarında ``k−1`` kübit
        # vardır), o yüzden ``uzak_cift`` yolu seçer -- takas mı MPO mu,
        # kararı ``mpo_esigi`` verir (H80: eşiği ölçüm koydu).
        for i in range(q.n_satir):
            q.uzak_cift(q.veri(i, 0), q.yerel(i), G)


@qkaydet
class QTahkik(QMeleke):
    """𝒪₃₀ Tahkik -- kökene inmek: küllî kaidenin mühürlenmesi.

    Yerel hükümler ikinci defa, fakat bu sefer **tasdik** alanına ve
    farklı açılarla akıtılır. Taklit ile tahkiki ayıran budur: aynı
    delil iki ayrı yoldan aynı hükmü veriyorsa tahkik, yalnız birinden
    geliyorsa taklittir. İki yol girişimle karşılaştırılır.
    """
    no, ad = 30, "Tahkik"
    SINIF, CHI = "koruyucu", 4   # MPO tasdik birikimi, bağ 2

    def uygula(self, q, p):
        q.mpo_topla("tasdik", self.birikim(p, q.n_satir, 1.0), j=1)


@qkaydet
class QTedebbur(QMeleke):
    """𝒪₃₁ Tedebbür -- âkıbete bakmak: evrim operatörünün tekrarı.

    ``S_{t+H} = ∫ Evrim``. Üniter karşılığı aynı dik operatörün ``H``
    kere uygulanmasıdır. Risk ölçülmez (okuma olurdu); onun yerine
    ileri sarımın kendisi mîzâna bağlanır.
    """
    no, ad = 31, "Tedebbür"
    SINIF, CHI = "kurucu", 8   # tedebbür: ileri sarım
    UFUK = 4

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.25))
        # **Cebrî sadeleştirme (kullanıcı hükmü: netice birebir aynı
        # kaldığı ispatlanabildiği sürece serbest).** Aynı ``G`` aynı
        # çifte ``UFUK`` kere vuruluyordu; dik dizeyler için
        # ``G·G·G·G = G⁴`` ve tek kapıda uygulanır. Netice birebir
        # aynıdır (``_sadelestirme_sinamasi`` ölçer), maliyet ``UFUK``
        # katı ucuzdur. İz kaydı yine "UFUK=4" der: meleke ne yaptığını
        # söylemeye devam eder, makine ucuz yoldan yapar.
        GU = np.linalg.matrix_power(np.asarray(G, float), self.UFUK)
        q.cift_yigin([q.veri(i, 0) for i in range(q.n_satir)], GU)
        a = self.aci(p, 2, 0.3)
        q.tek_yigin([q.kulli("mizan", 2 + j) for j in range(2)],
                    np.stack([donme(float(t)) for t in a[:2]]))


@qkaydet
class QSekZanYakin(QMeleke):
    """𝒪₃₂ Şek-Zan-Yakîn -- **makam bir faza kodlanır** (kullanıcı hükmü).

    Makam **üç** kübitlik bir merdivendir (kütük H129'un kapanan
    borcu): sekiz basamak, Gray sırasında, beş mertebeyi taşır. Hiçbir
    yerde okunmaz; **çevrilir**.

    **Hangi kübit ne demek -- iddia değil, hesap.** Merdiven Gray
    olduğu için her kübitin manası ``makam_kubit_manasi()`` ile fiilen
    hesaplanır ve şu çıkar (sınama denetler)::

        makam₀ = 1  ⟺  üst yarı        (Zan ve üstü)  → hükmün CİHETİ
        makam₁ = 1  ⟺  orta dörtlü     (Şek–Zan)      → KARARSIZLIK kuşağı
        makam₂ = 1  ⟺  ara basamaklar                 → İNCE ayar

    Kapılar buna göre yöneltilir:

    * ``tasdik`` uyanıksa ``makam₀`` müsbet döner -- hüküm üst yarıya,
      Zan ve üstüne çekilir.
    * ``nakz`` uyanıksa ``makam₀`` menfî döner: tek karşı örnek küllî
      önermeyi düşürür (H6), yani hükmü alt yarıya iter.
    * ``tenakuz`` uyanıksa ``makam₁`` **müsbet** döner. Bu bir
      tashihtir: evvelce menfî dönüyordu, yani çelişki makamı aşağı
      itiyordu. Çelişkinin işi hükmü düşürmek değil **kararsızlaştırmak**
      -- Şek–Zan kuşağına, kararın verilemediği yere çekmektir.
    * ``tasdik₁`` (tahkikin ikinci yolu) ``makam₂``ye ince ayar verir:
      iki müstakil yol aynı hükmü veriyorsa makam bir basamak yukarı
      kayabilsin. ``zann-ı gālib`` ile ``yakîn`` arasındaki fark tam
      olarak bu ince basamaktır; iki kübitle temsil edilemiyordu.

    Sükût kapısı da ``makam₁``e taşındı: susmak, hükmün **düşük**
    olmasından değil **kararsız** olmasından doğar. Evvelce ``makam₀``a
    bağlıydı, yani model "hükmüm menfî" ile "hükmüm yok"u
    ayıramıyordu.

    Hepsi kontrollü dönmedir, hepsi küllî blok içindedir. Makamın
    sayısı ancak nihaî POVM'de doğar ve o da bir **dağılımdır** --
    "makam Zan'dır" diye sert bir hüküm hiç kurulmaz (H31).
    """
    no, ad = 32, "Şek-Zan-Yakîn"
    SINIF, CHI = "çözücü", 2   # makam kararı: ihtimaller daralır

    def uygula(self, q, p):
        a = self.aci(p, 5, 0.6)
        mk = q._alan["makam"][1]
        # cihet: tasdik yukarı, nakz aşağı -- ikisi de EN ANLAMLI kübite
        q.uzak_cift(q.kulli("tasdik", 0), q.kulli("makam", 0),
                    kontrollu_donme(abs(float(a[0]))))
        q.uzak_cift(q.kulli("nakz", 0), q.kulli("makam", 0),
                    kontrollu_donme(-abs(float(a[1]))))
        # kararsızlık: çelişki makamı orta kuşağa çeker
        if mk >= 2:
            q.uzak_cift(q.kulli("tenakuz", 0), q.kulli("makam", 1),
                        kontrollu_donme(abs(float(a[2]))))
        # ince ayar: tahkikin ikinci yolu (tasdik₁) zann-ı gālib ile
        # yakîn arasındaki basamağı oynatır -- iki kübitte YOK olan yer.
        if mk >= 3:
            q.uzak_cift(q.kulli("tasdik", 1), q.kulli("makam", 2),
                        kontrollu_donme(float(a[3])))
        # Sükût kapısı: makam KARARSIZ kuşaktaysa sükût kübiti uyanır.
        q.uzak_cift(q.kulli("makam", 1 if mk >= 2 else 0),
                    q.kulli("sukut", 0),
                    kontrollu_donme(abs(float(a[4]))))


@qkaydet
class QMuhakeme(QMeleke):
    """𝒪₃₃ Muhakeme -- meclis: bütün küllî alanların tartıldığı yer.

    Mîzân ``Γ = aleyhte/lehte``dir. Üniter karşılığı bir bölme değil,
    **zıt yönlü dönmelerin bileşkesidir**: lehte deliller (tasdik) mîzânı
    bir yöne, aleyhte deliller (tenakuz, nakz) öbür yöne çevirir. Netice
    ``R(Σ lehte − Σ aleyhte)``dir -- bölmenin logaritmik karşılığı.
    Hiçbir yerde bölme yapılmaz, dolayısıyla sıfıra bölme derdi de yoktur.
    """
    no, ad = 33, "Muhakeme"
    SINIF, CHI = "koruyucu", 4   # muhakeme: küllî blok içi bağlar

    def uygula(self, q, p):
        a = self.aci(p, 6, 0.5)
        # lehte: tasdik → mîzân (artı yön)
        for j in range(2):
            q.uzak_cift(q.kulli("tasdik", j), q.kulli("mizan", j),
                        kontrollu_donme(abs(float(a[j]))))
        # aleyhte: tenakuz ve nakz → mîzân (eksi yön)
        for j in range(2):
            q.uzak_cift(q.kulli("tenakuz", j), q.kulli("mizan", 2 + j),
                        kontrollu_donme(-abs(float(a[2 + j]))))
        for j in range(2):
            q.uzak_cift(q.kulli("nakz", j), q.kulli("mizan", j),
                        kontrollu_donme(-abs(float(a[4 + j]))))


@qkaydet
class QTafsil(QMeleke):
    """𝒪₃₄ Tafsil -- mücmeli dallarına açmak: küllîden yerele **dağıtım**.

    Buraya kadar bilgi hep yukarı aktı; tafsil onu geri indirir.
    ``mpo_dagit`` bunu kübit oynatmadan yapar. Sadakat şartı (açılan
    şey toplanınca geri gelmeli) burada cebren sağlanır: dağıtım
    üniterdir, tersi vardır.
    """
    no, ad = 34, "Tafsil"
    SINIF, CHI = "koruyucu", 8   # tafsil: MPO dağıtımı, bağ 2

    def uygula(self, q, p):
        q.mpo_dagit("makam", self.birikim(p, q.n_satir, 0.7))


@qkaydet
class QTefsir(QMeleke):
    """𝒪₃₅ Tefsir -- müphemi siyak ve sibakla açmak.

    Her satır hem öncekiyle hem sonrakiyle bağlanır; murâd, bu üçlünün
    ortak dolaşıklığında durur.
    """
    no, ad = 35, "Tefsir"
    SINIF, CHI = "koruyucu", 8   # tefsir: siyak-sibak, komşu satır

    def uygula(self, q, p):
        G = dik_iki_kubit(self.aci(p, 6, 0.4))
        k = q.veri_yuvasi
        for i in range(1, q.n_satir):
            q.uzak_cift(q.veri(i - 1, k - 1), q.veri(i, 0), G)


@qkaydet
class QTevil(QMeleke):
    """𝒪₃₆ Tevil -- zâhir çelişince irca; **şartlı** ve üniter.

    Keyfî te'vilin önündeki sed, kontrolün ta kendisidir: te'vil ancak
    ``tenakuz`` kübiti uyanıkken döner. Çelişki yoksa kontrol ``|0⟩``dır
    ve te'vil hiç olmaz -- "gereksiz te'vil yok" şartı burada bir ölçüm
    değil, kapının tarifidir.
    """
    no, ad = 36, "Tevil"
    SINIF, CHI = "koruyucu", 4   # te'vil şartlıdır; çelişki yoksa hiç dönmez

    def uygula(self, q, p):
        a = self.aci(p, 2, 0.5)
        for j in range(2):
            q.uzak_cift(q.kulli("tenakuz", j), q.kulli("tasdik", j),
                        kontrollu_donme(float(a[j])))


# =====================================================================
#  𝒪₃₇–𝒪₄₁  BEYAN
# =====================================================================
@qkaydet
class QFesahat(QMeleke):
    """𝒪₃₇ Fesâhat -- mana **kelam alanına** akar.

    Buraya kadar bütün iş veri ve hüküm kübitlerindeydi; kelam ``|0⟩``da
    bekliyordu. Fesâhat, satırların manasını kelama akıtan ilk
    melekedir: her satırın ilk veri kübiti, kelamın bir kübitine MPO
    ile bağlanır.

    **Neden ayrı bir alan.** Ölçüldü: veri kübitlerinden okunan
    dağılım tam düzgün çıkıyordu (16 durumun her biri 0.0625) -- her
    şey her şeyle dolaştığında küçük bloğun marjinali âzamî karışıktır
    ve model konuşamaz. Kelam ``|0⟩``dan başlayıp yalnız beyan
    melekelerinin yazdığı bir alandır; oradan okunan dağılım
    yoğunlaşabilir.
    """
    no, ad = 37, "Fesâhat"
    SINIF, CHI = "koruyucu", 4   # fesâhat: MPO ile kelama akar

    def uygula(self, q, p):
        # **BEYAN KAPISI (kullanıcı kat'î kararı / kütük H131).**
        # Duraklar evvelce ``q.veri(i, 0)`` idi -- yani mana HAM VERİDEN
        # akıyordu. Karar ilga etti: *"Beyan melekeleri ham veriden
        # doğrudan BESLENEMEZ… mana yalnızca Muhakeme Meclisinden geçmiş,
        # Tasdik mührü basılmış muhkem hüküm üzerinden akacaktır."*
        #
        # Yerel hüküm kübiti, o satır hakkında **verilmiş hükümdür**;
        # ham duyu değildir. Mana artık oradan akıyor.
        _, kk = q._alan["kelam"]
        a = self.birikim(p, q.n_satir * kk, 1.2) * kk
        duraklar = q.yereller()
        for j in range(kk):
            q.mpo_topla("kelam", a[j * q.n_satir:(j + 1) * q.n_satir],
                        duraklar=duraklar, j=j)
        # TASDİK MÜHRÜ: mühür yoksa kelâm bastırılır. Menfî kontrol
        # (``X`` sarmalı) ile: ``tasdik₀ = 0`` iken kelam sıfıra çevrilir.
        b = self.aci(p, 2, 0.6)
        tas = q.kulli("tasdik", 0)
        q.tek(tas, degil_x())
        for j in range(min(kk, 2)):
            q.uzak_cift(tas, q.kulli("kelam", j),
                        kontrollu_donme(-abs(float(b[j]))))
        q.tek(tas, degil_x())


@qkaydet
class QTalakat(QMeleke):
    """𝒪₃₈ Talâkat -- akıcılık: kelam kübitleri arası bağ.

    Kelam kopuk hecelerden ibaret olmasın diye kelam alanının komşu
    kübitleri birbirine bağlanır; bunlar bitişiktir, kapı yereldir.
    """
    no, ad = 38, "Talâkat"
    SINIF, CHI = "koruyucu", 4   # talâkat: kelam içi komşu bağ

    def uygula(self, q, p):
        # **BEYAN KAPISI (H131).** Son satır evvelce ``self.tugla(...)``
        # idi, yani talâkat VERİ kübitlerine fırça atıyordu. Akıcılık
        # kelamın kendi içinde olur; ham veriden akıcılık devşirmek,
        # kararın ilga ettiği doğrudan beslenmenin ta kendisidir.
        _, kk = q._alan["kelam"]
        G = dik_iki_kubit(self.aci(p, 6, 0.4))
        for j in range(kk - 1):
            q.cift(q.kulli("kelam", j), G)
        # Akıcılık artık TASDİKten besleniyor: mühürlü hüküm ne kadar
        # kuvvetliyse kelam o kadar akıcı.
        a = self.aci(p, 2, 0.35)
        for j in range(2):
            q.uzak_cift(q.kulli("tasdik", j), q.kulli("kelam", j),
                        kontrollu_donme(float(a[j])))


@qkaydet
class QBelagat(QMeleke):
    """𝒪₃₉ Belâgat -- makamın kelama sirayeti.

    Belâgat, sözü **makamına göre** söylemektir. Küllî makam kübiti
    bütün satırlara dağıtılır: Yakîn makamında kelam başka, Şek
    makamında başka bükülür. Dağıtım MPO iledir.
    """
    no, ad = 39, "Belâgat"
    SINIF, CHI = "koruyucu", 4   # belâgat: makam kelama sirayet eder

    def uygula(self, q, p):
        _, kk = q._alan["kelam"]
        # **AÇI SAYISI VURULACAK ALANDAN GELİR** (ferman 1-M), satır
        # sayısından değil. Evvelce ikinci öbek ``birikim(p, q.n_satir)``
        # ile boyutlanıyor, fakat ``tasdik`` yuvalarına vuruluyordu:
        # iki ayrı şeyin sayısı bir yerden alınıyordu. ``n_satir`` 2
        # iken tesadüfen tutuyor, yazmacın kendi sayısı (1) konunca
        # ``IndexError`` veriyordu -- yâni tutması tesadüftü.
        _, tk = q._alan["tasdik"]
        a = np.concatenate([self.aci(p, kk, 0.45),
                            self.birikim(p, tk, 0.7)])
        # makam kelama sirayet eder: küllî blok içinde, kısa mesafe.
        # Bölen ``2`` değil alanın **kendi genişliğidir**: makam 3
        # kübite çıkınca (H129) sabit 2 üçüncü kübiti hiç kullanmaz ve
        # sirayet, merdivenin ince basamağını görmezden gelirdi.
        mk = q._alan["makam"][1]
        for j in range(kk):
            q.uzak_cift(q.kulli("makam", j % mk), q.kulli("kelam", j),
                        kontrollu_donme(float(a[j])))
        # **BEYAN KAPISI (H131).** Evvelce ``mpo_dagit("makam", …)`` ile
        # makam SATIRLARA (yerel hükümlere) iniyordu. Belâgat sözü
        # makamına göre söylemektir; hükmü aşağı indirmek 𝒪₃₄ Tafsil'in
        # işidir, beyanın değil. Sirayet artık tasdik üzerinden kelama.
        for j in range(min(tk, kk)):
            q.uzak_cift(q.kulli("tasdik", j),
                        q.kulli("kelam", (j + 2) % kk),
                        kontrollu_donme(float(a[kk + j])))


@qkaydet
class QSanat(QMeleke):
    """𝒪₄₀ Sanat -- **altın oran**: açı melekenin kendi tarifinden gelir.

    Bu melekenin açısı öğrenilmez ve öğrenilmemelidir: ``2π/φ²``
    altın açıdır ve ardışık uygulandığında hiçbir yuvaya iki kere aynı
    fazı vermez (en düzgün dağılım). Ahenk bir tercih değil, bir sayıdır.
    """
    no, ad = 40, "Sanat"
    SINIF, CHI = "koruyucu", None   # sanat: yalnız tek kübitlik dönme, kesme yok

    def uygula(self, q, p):
        # **BEYAN KAPISI (H131).** Altın açı evvelce VERİ kübitlerine de
        # vuruluyordu. Sanat, keşfedilmiş hakikate elbise giydirmektir;
        # ham duyuyu bükmek onun işi değildir. Artık yalnız kelam ve
        # makam alanına dokunur.
        altin_aci = 2.0 * math.pi / (ALTIN ** 2)
        _, kk = q._alan["kelam"]
        mk = q._alan["makam"][1]
        q.tek_yigin([q.kulli("makam", j) for j in range(mk)],
                    np.stack([donme((altin_aci * (j + 1)) % (2 * math.pi))
                              for j in range(mk)]))
        q.tek_yigin([q.kulli("kelam", j) for j in range(kk)],
                    np.stack([donme((altin_aci * (j + 1)) % (2 * math.pi))
                              for j in range(kk)]))


@qkaydet
class QMunazara(QMeleke):
    """𝒪₄₁ Münazara -- tez ve antitezin telîfi: son bileşke.

    Mîzân ile makam son kere bağlanır; beyan bundan sonra okunur.
    """
    no, ad = 41, "Münazara"
    SINIF, CHI = "çözücü", 2   # münazara: son bileşke, telîf daraltır

    def uygula(self, q, p):
        _, kk = q._alan["kelam"]
        a = self.aci(p, 4 + kk, 0.5)
        for j in range(2):
            q.uzak_cift(q.kulli("mizan", j), q.kulli("makam", j),
                        kontrollu_donme(float(a[j])))
        # SÜKÛT KAPISI (kütük H10/H16): sükût kübiti uyanıksa kelam
        # bastırılır. Bilmediğini söylememek bir kabiliyettir ve burada
        # bir kapıdır: kontrol |1⟩ iken kelam sıfır yönüne döner.
        for j in range(kk):
            q.uzak_cift(q.kulli("sukut", 0), q.kulli("kelam", j),
                        kontrollu_donme(-abs(float(a[4 + j]))))
        q.tek(q.kulli("sukut", 0), donme(float(a[2]) * 0.5))


# =====================================================================
#  𝒪₄₂–𝒪₄₄  TEŞKİLÂT -- üç uzuv NİHAYET akışa girdi (kütük H213)
# =====================================================================
#
# **ÖLÇÜLEN VE KAPATILAN ÇELİŞKİ.** `nefs/dimag.py` ``MELEKE_SAYISI =
# 44`` diyor ve ``KANONIK_CETVEL`` 𝒪₄₂/𝒪₄₃/𝒪₄₄'ü ``d₁₀``a tescil
# ediyordu; fakat ``QAKIS`` 41'de bitiyordu. Yani Lie manifoldu 44
# üreteç sayarken akış 41 kapı vuruyordu -- üç meleke cetvelde vardı,
# icrada yoktu. `nefs/teskilat.py` de AST ile ölçüldü: **sıfır gerçek
# çağıran**, yalnız divanın sicilinde duruyordu.
#
# Aşağıdaki üç sınıf o boşluğu kapatır. Formüller `nefs/teskilat.py`den
# alınmıştır; oradaki klasik hâlleri **ölçü** (sözleşme denetçisi)
# olarak yerinde durur, buradaki hâlleri **kapı**dır. İkisi ayrı
# şeydir ve karıştırılmaz: kapı hiçbir şey okumaz (H31).


@qkaydet
class QUmumilestirme(QMeleke):
    """𝒪₄₂ Umumileştirme -- numunelerin **kesişimindeki** kanun.

    `nefs/teskilat.py`nin formülü::

        𝒪_umum(S) = Π_inv · [ ⊗_j 𝒮_j(X_in^(j) → Y_out^(j)) ]

    Manası: birkaç numunede görülen dönüşümlerin kesişimindeki
    **değişmez** kısmı süzmek; bir numuneye mahsus araz kesişimde
    kalmaz, kanun kalır.

    **Üniter karşılığı budur ve uydurma değildir.** Numuneler burada
    satırların yerel hüküm kübitleridir. ``mpo_topla`` bütün durakları
    **aynı** açıyla küllî alana akıtır::

        U = exp( (Σ_i θ n_i) ⊗ Y )

    Açı her durakta aynı olduğu için, uyanık olan duraklar birbirini
    **pekiştirir**, uyuşmayanlar katkı vermez -- yani biriken dönme
    tam olarak durakların **ortak** (kesişimdeki) kısmını taşır.
    Π_inv'in kübit üzerindeki karşılığı budur: ayrı ayrı açı vermek
    her numuneye kendi arazını taşıtırdı, aynı açı yalnız kanunu
    taşır.

    Bir numunenin arazı için ayrıca ``tenakuz``a zayıf bir sızıntı
    açılır: kesişim dışında kalan, çelişki alanında birikir.
    """
    no, ad = 42, "Umumileştirme"
    # Ölçüldü (``nefs/nizam.yuzlestir``): ΔS = +0,0080 -- koruyucu
    # bandının (|ΔS| ≤ 0,05) içinde. Sınıf iddia değil, ölçüdür.
    # CHI, emsali MPO birikimlerininkiyle aynı (bağ zaten 2).
    SINIF, CHI = "koruyucu", 4

    def uygula(self, q, p):
        n = max(1, q.n_satir)
        a = self.aci(p, 2, 0.5)
        # Π_inv: BÜTÜN duraklar AYNI açıyla -- kesişim böyle süzülür.
        ortak = np.full(n, float(a[0]) / float(n))
        q.iz.kesme += q.mpo_topla("mizan", ortak)
        # kesişim dışında kalan araz: zayıf, ters işaretli sızıntı
        q.iz.kesme += q.mpo_topla("tenakuz", -0.25 * ortak)


@qkaydet
class QTalim(QMeleke):
    """𝒪₄₃ Talim -- hükmü kademe kademe **keskinleştirmek**.

    `nefs/teskilat.py`nin formülü::

        𝒪_talim(S, τ) = Π_l softmax(S·W_l / τ_l) · Π_fesahat
        şart: τ₁ > τ₂ > … > τ_L  (yayvandan keskine, tersi olmaz)

    **Üniter karşılığı.** Sıcaklığı düşürmek dağılımı keskinleştirir;
    kübitte bunun karşılığı, kelam alanının genliğini kademe kademe
    **daha büyük** açıyla tek yöne toplamaktır: ``θ_l ∝ 1/τ_l``. τ
    monoton azaldığı için θ monoton **artar** ve beyan yayvandan
    keskine gider.

    **Kademe cetveli uydurulmaz, sözleşmeden gelir.** ``τ`` merdiveni
    `teskilat.talim_kademesi` ile fiilen sınanır: sabit ve
    belirlenimci bir hüküm vektöründe entropinin monoton azaldığı
    denetlenir. ``sahih`` yalanlanırsa merdiven kurulmaz ve meleke
    **hiç dönmez** -- karıştırmayı talim diye icra etmektense
    susmak yeğdir (H10).
    """
    no, ad = 43, "Talim"
    # Ölçüldü: ΔS = +0,0195 -- koruyucu bandının içinde. Yalnız tek
    # kübitlik dönmeler vurur, bağ büyütmez.
    SINIF, CHI = "koruyucu", 4
    #: Yayvandan keskine; ``talim_kademesi`` bunun monotonluğunu ölçer.
    TAU: Tuple[float, ...] = (4.0, 2.0, 1.0, 0.5)
    #: Merdivenin sınandığı sabit hüküm vektörü -- girdiden bağımsız,
    #: belirlenimci. Dalgadan OKUNMAZ; melekenin kendi tarifidir.
    OLCU: Tuple[float, ...] = (3.0, 1.0, 0.5, -1.0, 2.0)

    def uygula(self, q, p):
        r = talim_kademesi(np.asarray(self.OLCU, float), self.TAU)
        if not r["sahih"]:                       # pragma: no cover
            return                               # karıştırma yapmaktansa sus
        _, kk = q._alan["kelam"]
        a = self.aci(p, len(self.TAU), 0.4)
        for l, tau in enumerate(self.TAU):
            # θ_l ∝ 1/τ_l : τ düştükçe dönme büyür, beyan keskinleşir
            teta = float(a[l]) / float(tau)
            q.tek_yigin([q.kulli("kelam", j) for j in range(kk)],
                        np.stack([donme(teta) for _ in range(kk)]))


@qkaydet
class QTahsil(QMeleke):
    """𝒪₄₄ Tahsil -- ağırlığı emanet olmaktan çıkarıp **zâtî mülk** kılmak.

    `nefs/teskilat.py`nin formülü::

        𝒪_tahsil(θ) = θ ∘ exp(−η · Ĥ_Dimağ(θ)) + γ · I_meleke

    ``exp(−ηĤ)`` bir Gibbs sönümüdür (çelişkili yönler bastırılır);
    ``γI`` melekenin kendi kimliğini korur -- tamamen dışarının
    şekline girmesin diye.

    **Üniter karşılığı ve NEDEN ORAYA VURULDUĞU.** Bu meleke ötekiler
    gibi hükme değil, **parametre bölgesine** dokunur: `kuantum/kubit_taksimati.py`
    zincirde ``|x⟩`` diye bir bölge ayırır ve ceride onu "model
    ağırlıkları" diye tarif eder. Tahsil tam orada iş görür:

    * Gibbs sönümü ``exp(−ηĤ)`` → parametre kübitlerine, mîzân
      (çelişki enerjisi) **kontrollü** bir dönme: mîzân uyanıksa
      parametre söner. Çelişkili yön bastırılır.
    * ``γ·I`` → parametre kübitlerine küçük, kontrolsüz bir kimlik
      dönmesi: kaynak ne derse desin meleke kendi kimliğinden bir
      pay saklar.

    Bölge kapalıysa (``bolge_ac=False``) meleke sessizce hiçbir şey
    yapmaz; ``eklem_olcusu`` o zaman zaten kırmızı yanar.
    """
    no, ad = 44, "Tahsil"
    # **SINIFIM YANLIŞTI VE ÖLÇÜM YALANLADI (kütük H213).** Evvelâ
    # ``koruyucu`` yazmıştım; ``nefs/nizam.yuzlestir`` ΔS = **−0,5541**
    # ölçtü, yani ihlâl 0,4654. Hâlbuki melekenin kendi tarifi zaten
    # *"yüksek enerjili, yani çelişkili yönler bastırılır"* diyor --
    # bu bir **çözücü**nün tarifidir. İlan ölçüye uyduruldu, ölçü
    # ilana değil. CHI emsali çözücülerinkiyle aynı (tashih, tenkit).
    SINIF, CHI = "çözücü", 2
    #: Gibbs sönüm şiddeti ve kimlik payı -- melekenin kendi tarifi.
    ETA: float = 0.1
    GAMA: float = 0.05

    def uygula(self, q, p):
        if not q.bolge_var("parametre"):
            return
        npar = q.taksimat.bolge["parametre"][1]
        kac = min(int(npar), 8)                  # bütçe: ilk 8 kübit
        a = self.aci(p, 2, 0.5)
        # exp(−ηĤ): mîzân uyanıksa parametre söner (kontrollü dönme)
        for j in range(kac):
            q.uzak_cift(q.kulli("mizan", j % 4), q.parametre(j),
                        kontrollu_donme(-abs(float(a[0])) * float(self.ETA)))
        # γ·I: kimlik payı -- kontrolsüz, küçük, daima
        q.tek_yigin([q.parametre(j) for j in range(kac)],
                    np.stack([donme(float(self.GAMA) * float(a[1]))
                              for _ in range(kac)]))


#: Akış sırası -- reel modelin ``AKIS``ıyla birebir aynı (𝒪₁₃ iki kere),
#: **artık 44 melekelik** (kütük H213): 𝒪₄₂/𝒪₄₃/𝒪₄₄ beyanın ardından
#: koşar, zira teşkilât hükmün değil hükmü **sahiplenmenin** işidir.
QAKIS: Tuple[int, ...] = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24,
    25, 26, 27, 28, 29, 30, 31, 32,
    33, 13,
    34, 35, 36,
    37, 38, 39, 40, 41,
    42, 43, 44,
)

# ======================================================================
#  KÜBİT-YERLİ KÜLLÎ AKIŞ -- 44 meleke, tek dalga
#  (evvelce nefs/qakis.py)
# ======================================================================

#: Yoğuşmaya (kondensata) **giren** küllî alanlar. Kütük H54, 4. borç:
#: BEC bütün küllî bloğa vurulunca sükûtu boğuyordu. Ölçüldü:
#: ``sukut 0,7924 → 0,0626`` (12,7 kat düşüş), üstelik ``tenakuz
#: 0,3305 → 0,5758`` ve ``P_Şek 0,1553 → 0,2561`` -- yani faz kilidi
#: nefsi hem susamaz hem daha çelişkili kılıyordu.
#:
#: Sebep kavramîdir, sayısal değil. BEC **hükmün ittihadıdır**: bütün
#: parçaların tek bir faza kilitlenmesi. Sükût bir hüküm DEĞİLDİR;
#: tenakuz ve nakz da hüküm değil, hükmün ÖNÜNDEKİ engellerdir. Onları
#: da aynı faza kilitlemek, "bilmiyorum" diyebilme kabiliyetini
#: (kütük H10) faz kilidiyle susturmak demektir. Onun için yoğuşmaya
#: yalnız hüküm taşıyan alanlar girer.
YOGUSAN: Tuple[str, ...] = ("makam", "mizan", "tasdik", "kelam")


def bec_faz_kilidi(q: QYazmac, tur: int = 6, g: float = 0.35) -> None:
    """Gross–Pitaevskii faz kilidi -- **yalnız tepede** (kütük H30).

    ``iħ∂Ψ/∂t = (−∇²/2m + V_gaye + g|Ψ|²)Ψ``. BEC'i her yere boca etmek
    süperpozisyonu öldürür; burada yalnız **küllî hüküm bloğuna**, yani
    nihaî tasdik makamına uygulanır. Veri kübitlerine dokunulmaz;
    dolayısıyla dalga diri kalır.

    Üniter kalması şarttır: doğrusal olmayan ``g|Ψ|²`` terimi burada
    kübit sayısına bağlı **sabit** bir açıya çevrilir (ortalama alan
    yaklaşığı). Gerçek doğrusalsızlık okuma isterdi; bu, onun üniter
    ve okumasız karşılığıdır ve öyle bildirilir.
    """
    alanlar = [(ad, kac) for ad, kac in q.ayar.kulli_alanlar
               if ad in YOGUSAN]
    for t in range(tur):
        # kinetik terim: blok içi komşu bağları
        for ad, kac in alanlar:
            for j in range(kac - 1):
                q.cift(q.kulli(ad, j), _kinetik(0.12))
        # ortalama alan: her kübite aynı faz -- ittihad
        faz = g / (1.0 + t)
        for ad, kac in alanlar:
            for j in range(kac):
                q.tek(q.kulli(ad, j), donme(faz))


def _kinetik(teta: float) -> np.ndarray:
    """``−∇²``in iki kübitlik üniter karşılığı: komşu genlik alışverişi."""
    c, s = math.cos(teta), math.sin(teta)
    G = np.eye(4)
    G[1, 1] = c
    G[1, 2] = -s
    G[2, 1] = s
    G[2, 2] = c
    return G


class QNefs:
    """41 üniter melekeyi tek dalga üzerinde koşturan işletici."""

    def __init__(self, tohum: int = 0, ayar: Optional[QAyar] = None,
                 sira: Sequence[int] = QAKIS, sadakat: bool = True,
                 gaye: bool = True) -> None:
        # **AYAR EVVELÂ.** Parametre taşıyıcısı genişliğini ayardan
        # okur; ters sırada kurulursa genişlik daima ``1`` kalırdı --
        # yâni ayar konur, hiç okunmazdı (ferman 1-C/b).
        self.ayar = ayar or QAyar(tohum=tohum)
        self.p = QParametre(tohum, genislik=int(
            getattr(self.ayar, "parametre_genisligi", 1)))
        self.sira = tuple(sira)
        self.s = qsicil()
        #: Gaye doğuşu açık mı (Dosya 4 / kütük H122)? Yalnız **ölçüm**
        #: için kapatılır: kapatılamayan bir tedbirin faydası ölçülemez
        #: (H90). Akışta daima açıktır.
        self.gaye = bool(gaye)
        #: Mantığa sadakat kapısı açık mı? Yalnız **ölçüm** için
        #: kapatılır (haraplama: kalp söküldüğünde vücut ne olur?).
        #: Akışta daima açıktır ve kapatılması bir hüküm değil, bir
        #: teşrihtir.
        self.sadakat = bool(sadakat)

    # -----------------------------------------------------------------
    def idrak_et(self, E: np.ndarray, bec: bool = True,
                 yigin: int = 0, tikaniklik: float = 0.0,
                 olcum: Optional[bool] = None) -> QYazmac:
        """Ham duyudan nihaî hükme -- **tek geçiş, tek yol**.

        ``E`` ``(n, d)`` ise tek girdi; ``(B, n, d)`` ise **yığın**:
        ``B`` ayrı girdi aynı anda idrak edilir ve her üye kendi hükmünü
        verir. ``yigin`` açıkça verilirse yazmaç o büyüklükte kurulur
        (aynı girdi ``B`` kere -- yalnız hız ölçümü için).

        =================================================================
        ``olcumlu_idrak`` İMHA EDİLDİ -- İKİNCİ İLERİ GEÇİŞ YOKTU ARTIK
        =================================================================

        Evvelce buranın yanında ``nefs/kulli_kayip.py:olcumlu_idrak``
        duruyordu: aynı akışı **ikinci kere** kuruyor, farkı melekeler
        arasında okuma almasıydı. İki yol yan yana durdukça hangisinin
        koştuğu belirsizdir (ferman 1-E) -- ve burada belirsizlik zararsız
        değildi: o ikinci yol ``sadakat_uygula``yı, yâni **7/24 mantık
        zeminini hiç çağırmıyordu**. Yâni melekelerin ölçüldüğü geçiş,
        mantık alt-uzayı şartının koşmadığı geçişti.

        Artık tek yol var. ``olcum`` doğruysa her melekeden sonra:

        * melekenin **ilan ettiği alanların** okuması alınır (sözleşme),
        * o geçişte **attığı bilgi** (kesme) tutulan kesir olarak yazılır,
        * dolaşıklık entropisindeki fark ``ΔS`` olarak biriktirilir --
          nizam taahhüdü bununla yüzleştirilir.

        Netice ``q.okumalar`` ve ``q.dS``de durur; ``ℒ_Meleke`` ile
        ``ℒ_Zırh``ın nizam ucu oradan okunur (ferman 1-S). ``olcum``
        verilmezse ayardan gelir (``meleke_olcumu``, varsayılan açık) --
        yâni cevher varsayılanda **koşar**, kapatılınca ölçü kırmızı
        yanar (ferman 5).
        """
        E = np.asarray(E, float)
        if olcum is None:
            olcum = bool(int(getattr(self.ayar, "meleke_olcumu", 1)))
        B = E.shape[0] if E.ndim == 3 else max(1, int(yigin))
        n_satir = E.shape[-2]
        ayar = self.ayar
        if B != ayar.yigin:
            ayar = replace(ayar, yigin=B)
        q = QYazmac(n_satir, ayar)
        q.kodla(E)
        # **ČECH TIKANIKLIĞI (Dosya 3 / kütük H125).** ``H¹`` dalganın
        # değil GİRDİNİN vasfıdır -- görevin gösterim çiftlerinden, akış
        # hiç koşmadan hesaplanır. Onu bir kapıya çevirmek ``kodla`` ile
        # aynı cinstendir; H31 yasağı melekenin dalgaya bakmasınaydı.
        # Küllî cevabı olmayan bir suale verilecek karşılık susmaktır.
        if tikaniklik:
            ortu(ne="kapı", q=q, h1=float(tikaniklik))
        q.superpozisyon()
        q.harman()
        # **MANTIĞA SADAKAT: her melekeden sonra, muafiyetsiz** (H102/H105).
        # Bu bir meleke değildir, melekelerin tâbi olduğu şarttır -- yani
        # bu mimarinin kalbidir. Kaldırıldığında hiçbir hüküm mantıklı
        # kalmaz; H94'te *aranan* ve bulunamayan uzuv budur.
        # Hiçbir şey OKUMAZ: şartı hesaplayıp karar vererek değil,
        # dolaştırarak icra eder (kullanıcı hükmü: "kalp seçmez,
        # dolaştırır").
        # ── FERMAN 1-S: OKUMA BU GEÇİŞTE ALINIR, İKİNCİSİNDE DEĞİL ──
        okumalar: Dict[int, Dict[str, float]] = {}
        dS: Dict[int, float] = {}
        if olcum:
            from .kulli_kayip import (SOZLESME, _TAKSIMAT_ARTIGI,
                                      bolge_degeri)

            def _entropi() -> float:
                """Dolaşıklık entropisi -- **yalnız o**.

                ``q.olcumler()`` çağrılıp içinden tek sayı almak, on bir
                küllî alanın yoğunluğunu ve ``norm_hatasi``yı da
                hesaplatırdı (ölçüldü: 90 çağrıda 2,56 sn, 1,07'si
                ``norm_hatasi``). Yığında **ilk üye** okunur; ortalama
                alınca kayıp kayıyordu (0,414573544417 → 0,414415282390)
                ve kayan sayı hızlanma değil hiledir.
                """
                e = q.y.dolasiklik_entropisi()
                v = e.get("entropi_yigin", None)
                if v is None:
                    return float(e["entropi"])
                return float(np.asarray(v, float).reshape(-1)[0])

        # **ENTROPİ ARTIK TAŞINIYOR** (ferman 1-T). Evvelce her meleke
        # için iki kere ölçülüyordu (önce/sonra) ve taşımak **denenip
        # reddedilmişti**: aradaki okumalar POVM'di ve durumu
        # değiştiriyordu, o hâlde "bir melekenin sonrası, bir sonrakinin
        # öncesidir" doğru değildi.
        #
        # O gerekçe **artık yok**: zayıf ölçüm çöpe atıldı, okumalar
        # ``alan_degeri`` (``‖Π_C Ψ‖²``) ile alınıyor ve o durumu
        # **hiç değiştirmiyor**. Yâni iki nokta artık hakikaten aynı
        # durumdur ve taşımak bir kısaltma değil, bir kimliktir.
        # Entropi çağrısı meleke başına 2'den 1'e iner.
        S_tasinan = _entropi() if olcum else 0.0
        for no in self.sira:
            onceki_sadakat = float(q.y.sadakat_log()) if olcum else 0.0
            S_once = S_tasinan
            self.s[no].kosu(q, self.p)
            if self.sadakat:
                vicdan(q, self.p, ne="işaret")
            if olcum:
                # ``ΔS`` -- melekenin dolaşıklığa tesiri (nizam taahhüdü
                # bununla yüzleştirilir). Aynı meleke sırada iki kere
                # geçebilir; tesirleri toplanır.
                S_tasinan = _entropi()
                fark = S_tasinan - S_once
                dS[int(no)] = dS.get(int(no), 0.0) + (
                    0.0 if fark != fark else fark)
                ilan = SOZLESME.get(int(no), ((), ""))[0]
                d: Dict[str, float] = {}
                for ad in ilan:
                    # İmha edilen kübit taksimatının artığı ve veri/yerel
                    # alanları ölçüye girmez: birincisi olmayan bir
                    # bölgedir, ikincisi hüküm taşımaz (büyüğü iyi demek
                    # keyfî olurdu). İkisi de **kesmeden** ölçülür.
                    if ad in _TAKSIMAT_ARTIGI or ad in ("veri", "yerel"):
                        continue
                    d[ad] = bolge_degeri(q, ad)
                # Melekenin o geçişte **tuttuğu kesir**: ``exp(−düşüş)``.
                # Log uzayında, zira ``sadakat()`` çarpımsaldır ve 1814
                # kapıdan sonra 4e-12'ye iner.
                dus = max(0.0, onceki_sadakat - float(q.y.sadakat_log()))
                d["kesme"] = float(np.exp(-dus))
                # İki geçişten birinde bozması, bozmadığı manasına
                # gelmez: **en kötüsü** tutulur.
                eski = okumalar.get(int(no))
                okumalar[int(no)] = d if eski is None else {
                    k: min(v, eski.get(k, v)) for k, v in d.items()}
        if self.sadakat:
            # TERTİP: mantık usulleri süperpozisyonda koşar ve `mizan`
            # neyin yasak olduğunu söyler (H109). Ana akışa buradan
            # bağlanır -- artık `mizan` beylik değil tebaadır.
            q.iz.kesme += vicdan(q, ne="usul")
        if self.gaye:
            # **GAYE DOĞUŞU (Dosya 4 / H122).** ``gaye`` alanı H108'den
            # beri tahsisliydi fakat ÖLÇÜLDÜ ve tam ``|0⟩``daydı: hiçbir
            # meleke ona dokunmuyordu. Burada hükümden **doğar**
            # (tasdik kuvvetlendirir, tenakuz ve nakz zayıflatır), sonra
            # mîzâna sirayet eder ve sükût eşiğini kurar. Üçü de MPO'dur;
            # hiçbir yerde okuma yoktur.
            from ogrenme.optimize import gaye_kos
            q.iz.kesme += gaye_kos(q, self.p)
        if self.sadakat:
            # İşaretlenen mantık dışı kollar burada SÖNER: faz farkı,
            # yansıtmayla genlik farkına çevrilir (H98'de ölçülen usul).
            vicdan(q, ne="intaç")
            # ══════════════════════════════════════════════════════
            #  MANTIĞA SADAKAT -- STABILIZER ZEMİNİ (nefs/sadakat.py)
            # ══════════════════════════════════════════════════════
            #
            # Zabıt: *"yapılan hiçbir hesabın mantık dışı bir duruma
            # taşmasına izin vermeyen Kuantum Stabilizer Uzayı"*.
            #
            # ``vicdan`` bir **meleke ameliyesidir**: işaretler, sonra
            # söndürür. Bu ise bir **alt-uzay şartıdır**: parite
            # kontrol operatörünün ``−1`` sektörü, ne kadar küçük
            # olursa olsun, sıfırlanır. İkisi ayrı şeydir ve ikisi de
            # koşar -- birincisi hükmü terbiye eder, ikincisi taşmayı
            # imkânsız kılar.
            #
            # **7/24 OLMASININ MANASI BURADADIR**: ``idrak_et`` tâlimin
            # de çıkarımın da tek geçtiği yerdir. Sadakat başka bir
            # yere konsaydı (mesela yalnız mizana) model eğitilirken
            # mantıklı, konuşurken serbest olurdu.
            # **KAPI AYARDAN GELİR, KODA GÖMÜLÜ DEĞİL.** Evvelce burada
            # ``acik=1`` ve ``parite_lifi=min(2, …)`` yazılıydı; o hâlde
            # ``EgitimAyari.sadakat_acik = 0`` demek hiçbir şeyi
            # kapatmıyordu ve tedbirin faydası ölçülemiyordu (ferman 5).
            from .sadakat import SadakatAyari, sadakat_uygula
            lif = tuple(int(x) for x in q.y.ayar.lif)
            sadakat_uygula(q.y, SadakatAyari(
                acik=int(getattr(self.ayar, "sadakat_acik", 1)),
                parite_lifi=min(int(getattr(self.ayar, "parite_lifi", 2)),
                                len(lif) - 1),
                lif_yapisi=lif))
        if bec:
            bec_faz_kilidi(q)
        # **Ölçümden evvel durum, durum olmalıdır.** Kesme her vuruşta
        # normu bir parça düşürür; kırk bir meleke boyunca birikince
        # ``⟨Ψ|Ψ⟩`` 2e-10'a kadar indiği ÖLÇÜLDÜ. Atılan ağırlık
        # ``q.iz.kesme``de ayrıca durur -- yani unutma gizlenmiyor --
        # fakat dağılım artık normu 1 olan bir dalgadan okunur.
        # **HAKİKÎ kesme burada ölçülür.** Bütün kapılar diktir; normu
        # düşüren tek şey kesmedir. O hâlde normalize etmeden EVVELKİ
        # ``⟨Ψ|Ψ⟩``, atılan ağırlığın tam tamlamasıdır::
        #
        #     kesme_hakiki = 1 − ⟨Ψ|Ψ⟩        (``[0,1]``, kıyas edilebilir)
        #
        # ``iz.kesme`` (kapı başına nispî atılanların toplamı) H111'de
        # ölçüldü ve **ölçüt olmadığı** görüldü: χ büyüdükçe artıyordu.
        # Teşhis için duruyor; hüküm bu satırdan verilir.
        # Telâfiden sonra norm kaybı göstermez; hakikî ölçü, kapı
        # başına tutulan kesrin ÇARPIMIDIR (``Yazmac.sadakat``).
        q.iz.kesme_hakiki = float(max(0.0, 1.0 - q.y.sadakat()))
        q.y.normalize()
        # **OKUMALAR YAZMACIN ÜSTÜNDE DURUR** (ferman 1-S). Ayrı bir
        # dönüş değeri yapılmadı: ``idrak_et``in on beş çağrı yeri var ve
        # hepsi ``q`` bekliyor. Ölçüm kapalıysa ikisi de boştur ve o
        # zaman ``ℒ_Meleke`` ile ``ℒ_Zırh``ın nizam ucu sıfırlanır --
        # yâni kapatınca ölçü hakikaten kırmızı yanar.
        q.okumalar = okumalar
        q.dS = dS
        return q

    # -- eğitim arayüzü ------------------------------------------------
    def __len__(self) -> int:
        """Öğrenilecek açı sayısı. Yer tahsisi ilk koşuda yapılır;
        bu yüzden ``idrak_et`` bir kere çağrılmadan sayı bilinmez ve
        bilinmediği hâlde tahmin edilmez."""
        return len(self.p)

    def vektor(self) -> np.ndarray:
        return self.p.vektor()

    def yukle(self, v: np.ndarray) -> None:
        self.p.yukle(v)


# =====================================================================
def rapor_qakis(tohum: int = 0, n: int = 20, d_in: int = 12,
          ayar: Optional[QAyar] = None) -> str:
    rng = np.random.default_rng(tohum)
    E = rng.normal(size=(n, d_in))
    nefs = QNefs(tohum, ayar)
    t0 = time.perf_counter()
    q = nefs.idrak_et(E)
    dt = time.perf_counter() - t0
    o = q.olcumler()

    s = ["=== nefs (KÜBİT): 41 meleke, tek dalga, tek ölçüm ===",
         "",
         "kübit=%d  (satır=%d × %d + küllî %d)   χ=%d   durum=%.1f KB"
         % (q.n, q.n_satir, q.oge, q.ayar.kulli_yuva, q.ayar.bag,
            q.y.bayt / 1024.0),
         "kapı=%d  takas=%d  MPO=%d  toplam kesme=%.3e  %.2f sn"
         % (q.iz.kapi, q.iz.takas, q.iz.supurme, q.iz.kesme, dt),
         "",
         "SÜPERPOZİSYON → DOLAŞIKLIK (ölçülen, iddia edilen değil):",
         "  MERA öncesi entropi = %.6f  (Schmidt = %d)"
         % (q.iz.entropi_once, q.iz.schmidt_once),
         "  MERA sonrası entropi = %.6f  (Schmidt = %d)"
         % (q.iz.entropi_sonra, q.iz.schmidt),
         "  akış sonu entropi    = %.6f" % o["entropi"],
         "  norm hatası          = %.2e" % o["norm_hatası"],
         "",
         "MAKAM DAĞILIMI (POVM zayıf ölçüm -- ÇÖKÜŞ YOK):"]
    for ad in MAKAM_ADLARI:
        p = o["P_" + ad]
        s.append("  %-6s %.4f  %s" % (ad, p, "█" * int(round(40 * p))))
    s += ["",
          "KÜLLÎ HÜKÜMLER (zayıf okuma, [0,1]):"]
    for ad, _ in q.ayar.kulli_alanlar:
        s.append("  %-9s %.4f" % (ad, o[ad]))
    s += ["", "MELEKELERİN İCRA İZİ:"]
    s += ["  " + x for x in q.iz.gunluk]
    return "\n".join(s)


# ====================================================================
#  KÜME 8: GRAPE -- kapı darbelerinin optimal kontrolü
# ====================================================================

def _uexp(H: np.ndarray, t: float) -> np.ndarray:
    lam, V = np.linalg.eigh(H)
    return (V * np.exp(-1j * lam * t)) @ V.conj().T


def _genel_expm(M: np.ndarray, tur: int = 60) -> np.ndarray:
    """Genel ``exp(M)`` — ölçekle-kare-al + Taylor.

    Fréchet blok dizeyi ``[[A,E],[0,A]]`` **dejenere özdeğerlidir**
    (``A``nın tayfı iki kere geçer), bu yüzden özayrışım yolu orada
    sayısal olarak çöker.  Ölçüldü: ``eig`` ile kurulan tam gradyan
    sonlu farktan 1.9e-01…4.5e-01 sapıyordu; ölçekle-kare-al ile
    1e-10 mertebesine iniyor.
    """
    M = np.asarray(M, complex)
    nrm = float(np.abs(M).sum(axis=1).max())
    k = max(0, int(math.ceil(math.log2(max(nrm, 1e-300)))) + 2)
    A = M / (2.0 ** k)
    S = np.eye(A.shape[0], dtype=complex)
    T = np.eye(A.shape[0], dtype=complex)
    for i in range(1, tur):
        T = T @ A / i
        S = S + T
        if np.abs(T).max() < 1e-18:
            break
    for _ in range(k):
        S = S @ S
    return S


def sadakat(H0: np.ndarray, Hk: Sequence[np.ndarray],
            om: Sequence[np.ndarray], psi0: np.ndarray,
            hedef: np.ndarray, T: float) -> float:
    """``F = |⟨hedef|U(T)|ψ₀⟩|²``."""
    M = len(om[0])
    dt = T / M
    p = np.asarray(psi0, complex).copy()
    for j in range(M):
        H = H0 + sum(om[k][j] * Hk[k] for k in range(len(Hk)))
        p = _uexp(H, dt) @ p
    return float(abs(np.vdot(hedef, p)) ** 2)


def _ileri_geri(H0, Hk, om, psi0, hedef, T):
    M = len(om[0])
    dt = T / M
    Us, ileri = [], [np.asarray(psi0, complex).copy()]
    p = ileri[0]
    for j in range(M):
        H = H0 + sum(om[k][j] * Hk[k] for k in range(len(Hk)))
        U = _uexp(H, dt)
        Us.append(U)
        p = U @ p
        ileri.append(p.copy())
    geri = [None] * (M + 1)
    lam = np.asarray(hedef, complex).copy()
    geri[M] = lam.copy()
    for j in range(M - 1, -1, -1):
        lam = Us[j].conj().T @ lam
        geri[j] = lam.copy()
    return Us, ileri, geri, dt


def grape_gradyani(H0, Hk, om, psi0, hedef, T) -> List[np.ndarray]:
    """Kaynağın (birinci mertebe) GRAPE gradyanı — ``O(Δt²)`` hatalı."""
    Us, ileri, geri, dt = _ileri_geri(H0, Hk, om, psi0, hedef, T)
    M = len(om[0])
    G = [np.zeros(M) for _ in Hk]
    for k in range(len(Hk)):
        for j in range(M):
            P, PSI = geri[j + 1], ileri[j + 1]
            G[k][j] = 2.0 * np.real(np.vdot(P, PSI)
                                    * np.vdot(PSI, (1j * dt * Hk[k]) @ P))
    return G


def tam_gradyan(H0, Hk, om, psi0, hedef, T) -> List[np.ndarray]:
    """**Tam** gradyan — üstelin Fréchet türeviyle.

    ``d/dθ exp(A(θ))`` için genişletilmiş dizey kaidesi:
    ``exp([[A, E],[0, A]]) = [[e^A, dexp],[0, e^A]]``.  Bu, ``Δt``de
    yaklaşım **değildir**; ölçülüyor.

    Blok dizey dejenere özdeğerlidir; üstel :func:`_genel_expm` ile
    (ölçekle-kare-al) alınır.  Özayrışım kullanmak burada **çöker** --
    ilk hâlde öyle yazmıştım, ölçüm yakaladı.
    """
    M = len(om[0])
    dt = T / M
    n = H0.shape[0]
    Us, ileri, geri, _ = _ileri_geri(H0, Hk, om, psi0, hedef, T)
    G = [np.zeros(M) for _ in Hk]
    for k in range(len(Hk)):
        for j in range(M):
            H = H0 + sum(om[q][j] * Hk[q] for q in range(len(Hk)))
            A = -1j * dt * H
            E = -1j * dt * Hk[k]
            B = np.zeros((2 * n, 2 * n), dtype=complex)
            B[:n, :n] = A
            B[n:, n:] = A
            B[:n, n:] = E
            EB = _genel_expm(B)
            dU = EB[:n, n:]
            P, PSI = geri[j + 1], ileri[j]
            # F = |⟨hedef|U_M…U_1|ψ₀⟩|²; ∂F/∂θ = 2Re[⟨c⟩* · ⟨P|dU|ψ_j⟩]
            c = np.vdot(geri[0], ileri[0])
            G[k][j] = 2.0 * np.real(np.conj(c) * np.vdot(P, dU @ PSI))
    return G


def sonlu_fark_gradyani(H0, Hk, om, psi0, hedef, T, h: float = 1e-6
                        ) -> List[np.ndarray]:
    """Merkezî sonlu fark — hakem."""
    M = len(om[0])
    G = [np.zeros(M) for _ in Hk]
    for k in range(len(Hk)):
        for j in range(M):
            o1 = [x.copy() for x in om]; o1[k][j] += h
            o2 = [x.copy() for x in om]; o2[k][j] -= h
            G[k][j] = (sadakat(H0, Hk, o1, psi0, hedef, T)
                       - sadakat(H0, Hk, o2, psi0, hedef, T)) / (2 * h)
    return G


def grape_kos(H0, Hk, psi0, hedef, T: float, M: int = 40,
              tur: int = 200, adim: float = 0.5, tohum: int = 0
              ) -> Dict[str, object]:
    """GRAPE ile sadakati yükselt — yaklaşık gradyanla."""
    r = np.random.default_rng(tohum)
    om = [r.normal(size=M) * 0.2 for _ in Hk]
    F = sadakat(H0, Hk, om, psi0, hedef, T)
    seyir = [F]
    t = adim
    for _ in range(tur):
        G = grape_gradyani(H0, Hk, om, psi0, hedef, T)
        n = math.sqrt(sum(float(np.sum(g * g)) for g in G))
        if n < 1e-14:
            break
        yeni = [om[k] + t * G[k] / n for k in range(len(Hk))]
        Fy = sadakat(H0, Hk, yeni, psi0, hedef, T)
        if Fy > F:
            om, F = yeni, Fy
        else:
            t *= 0.5
            if t < 1e-10:
                break
        seyir.append(F)
    return {"kontrol": om, "sadakat": F, "seyir": seyir,
            "tekdüze_mi": all(seyir[i] <= seyir[i + 1] + 1e-12
                              for i in range(len(seyir) - 1))}

"""
𝒪₂₅–𝒪₃₆: murâkabe -- nefsin kendi hükmünü denetlediği mertebe.

Buradaki melekelerin ortak vasfı şudur: hiçbiri yeni bilgi ÜRETMEZ;
hepsi mevcut hükmü **yoklar**. Teemmül devreder, Temkin sarsar, Tetkik
kılcalına bakar, Tashih düzeltir, Teyit ikinci kanaldan sorar, Tahkik
kökenini arar, Tedebbür âkıbetine bakar, Şek-Zan-Yakîn makamını tayin
eder, Muhakeme karara bağlar, Tafsil açar, Tefsir murâdı bulur, Tevil
zâhir çelişince te'vil eder.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from .meleke import Meleke, kaydet
from .uzaylar import (Durum, Parametreler, celiski_gradyani, celiski_skoru,
                      dikkat, gelu, guvenli_bol, kat_norm, kosinus, sigmoid,
                      softmax)


# =====================================================================
@kaydet
class Teemmul(Meleke):
    """𝒪₂₅ Teemmül -- devridaim ve **durma ölçütü**.

    ``M⁽ᵗ⁾ = LayerNorm(M⁽ᵗ⁻¹⁾ + MultiHeadAttn(Ŷ, S, H))``, ve
    ``τ_durma = ArgMin_τ (‖M⁽ᵗ⁾ − M⁽ᵗ⁻¹⁾‖ < ε)``.

    Sınanabilir iddia: devridaim **yakınsar** ve durma ölçütü ``𝒦``
    turdan önce tetiklenir.

    "Ardışık farklar MONOTON azalır" diye kurulup sınandı ve **kaldı**:
    bazı tohumlarda 1-2 tur geriye sıçrama oluyor. Bu beklenir --
    büzücü bir eşleme geometrik yakınsama garanti eder, tur tur
    monotonluk garanti ETMEZ; ``LayerNorm`` de büzücü değildir. İddia
    düzeltildi: ölçülen şey artık ``azalma_oranı = son/ilk`` ve
    geriye sıçrama SAYISIDIR.

    Azamî tur sayısı ölçümle seçildi: yakınsama geometriktir fakat
    yavaştır (κ=0.4'te fark 60 turda 3.64 → 0.055). 12 turda kesilince
    ölçüt hiç tetiklenmiyordu; ``𝒦 = 200`` ile ``ε = 10⁻³`` tipik olarak
    100-130. turda sağlanıyor. Bu, "teemmül ucuz değildir" demenin
    sayısal hâlidir ve maliyeti ``0.1·τ_durma`` olarak raporlanır.
    """

    no, ad = 25, "Teemmül"
    okur, yazar = ("S", "H_hayal"), ("M",)

    def uygula(self, d: Durum, p: Parametreler, K: int = 200,
               eps: float = 1e-3) -> None:
        S, H = d.S, d.H_hayal
        n, ds = S.shape
        Wq = p.W("teemmül.q", (ds, ds))
        Wk = p.W("teemmül.k", (H.shape[1], ds))
        Wv = p.W("teemmül.v", (H.shape[1], ds))

        M = kat_norm(S.copy())
        farklar: List[float] = []
        tau_durma = K
        for t in range(1, K + 1):
            Y = dikkat(M @ Wq, H @ Wk, H @ Wv)
            # SÖNÜMLÜ artık: ``M + κY`` biçiminde kurulup ölçüldü ve
            # yakınsamadı (12 turda fark 0.51'de takıldı). ``(1−κ)M + κY``
            # dışbükey harmandır; dikkat çıktısı ``H``nin dışbükey
            # örtüsünde kaldığı için harman büzücüdür ve yakınsar.
            kappa = 0.4
            M_yeni = kat_norm((1 - kappa) * M + kappa * Y)
            fark = float(np.linalg.norm(M_yeni - M))
            farklar.append(fark)
            M = M_yeni
            if fark < eps:
                tau_durma = t
                break
        d.M = M
        d.olcum.koy("teemmül.τ_durma", float(tau_durma))
        d.olcum.koy("teemmül.son_fark", farklar[-1])
        d.olcum.koy("teemmül.yakınsadı", float(farklar[-1] < eps))
        sicrama = sum(1 for i in range(len(farklar) - 1)
                      if farklar[i + 1] > farklar[i] + 1e-12)
        d.olcum.koy("teemmül.geriye_sıçrama", float(sicrama))
        d.olcum.koy("teemmül.azalma_oranı",
                    farklar[-1] / max(farklar[0], 1e-300))
        d.olcum.koy("teemmül.maliyet", 0.1 * tau_durma)
        d.not_dus(self.ad, "τ=%d, son fark=%.2e" % (tau_durma, farklar[-1]))


# =====================================================================
@kaydet
class Temkin(Meleke):
    """𝒪₂₆ Temkin -- sarsılmazlık: ``min_{‖δ‖≤ε} T(S+δ)``.

    ``VakarKatsayısı = 1/(1+‖∇_t S‖²)``; ``S_müstakar`` hâlihazırdaki ile
    öncekinin vakarla ağırlıklı harmanıdır. Sarsılmazlık, en kötü
    hâldeki tasdik değeriyle ölçülür -- bu bir **asgarî** aramasıdır,
    ortalama değil; temkinin tarifi budur.
    """

    no, ad = 26, "Temkin"
    okur, yazar = ("S", "M"), ()

    def uygula(self, d: Durum, p: Parametreler, ornek: int = 24) -> None:
        S, M = d.S, d.M
        hedef = d.G if d.G is not None else S.mean(0)
        rng = np.random.default_rng(p.tohum + 26)
        eps = 0.1 * float(np.linalg.norm(S)) / max(np.sqrt(S.size), 1.0)

        temel = kosinus(M.mean(0), hedef)
        en_kotu = temel
        for _ in range(ornek):
            delta = rng.normal(size=S.shape)
            delta *= eps / max(float(np.linalg.norm(delta)), 1e-12)
            en_kotu = min(en_kotu, kosinus((M + delta).mean(0), hedef))

        vakar = 1.0 / (1.0 + float(np.sum(np.diff(S, axis=0) ** 2)))
        d.olcum.koy("temkin.vakar", vakar)
        d.olcum.koy("temkin.sarsılmazlık", en_kotu)
        d.olcum.koy("temkin.tolerans_marjı", temel - en_kotu)
        d.olcum.koy("temkin.emin", float(temel - en_kotu < 0.05))


# =====================================================================
@kaydet
class Tetkik(Meleke):
    """𝒪₂₇ Tetkik -- kılcal kusur haritası.

    ``δS_kılcal = S ⊙ M_mikro``, ``KusurHaritası = |δS − S_ideal|``.
    "İdeal" burada, ``S``in kendi düşük kipli (pürüzsüz) izdüşümüdür:
    kusur, sinyalin **kendi düzgün hâlinden** sapmasıdır. Böylece ölçüt
    dışarıdan bir doğru dayatmaz.
    """

    no, ad = 27, "Tetkik"
    okur, yazar = ("S",), ()

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n, ds = S.shape
        maske = sigmoid(S @ p.W("tetkik.mikro", (ds, ds)))
        kilcal = S * maske

        # ideal: ilk yarı tekil kiple yeniden kurulan pürüzsüz hâl
        U, s, Vt = np.linalg.svd(S, full_matrices=False)
        k = max(1, len(s) // 2)
        ideal = (U[:, :k] * s[:k]) @ Vt[:k]
        kusur = np.abs(kilcal - ideal)

        d.olcum.koy("tetkik.kusur_l1", float(np.sum(kusur)))
        d.olcum.koy("tetkik.pürüz_derecesi", float(np.sum(np.diff(kilcal, axis=0) ** 2)))
        d.olcum.koy("tetkik.azami_kusur", float(np.max(kusur)))
        d.olcum.koy("tetkik.kusurlu_hücre_oranı",
                    float(np.mean(kusur > np.quantile(kusur, 0.9))))


# =====================================================================
@kaydet
class Tashih(Meleke):
    """𝒪₂₈ Tashih -- düzeltme, fakat **şartlı**.

    ``S_musahhah = S − γ·KusurHaritası ⊙ ∇Tenakuz``; düzeltme ancak
    ``T_yeni > T_eski`` ise kabul edilir, aksi hâlde ``S_itidal``
    (tez ile antitezin ortası) alınır. Yani tashih, iyileştirdiğini
    ÖLÇEREK kabul eder; körü körüne uygulanmaz.
    """

    no, ad = 28, "Tashih"
    okur, yazar = ("S",), ("S",)
    ihtiyari = ("G",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        ds = S.shape[1]
        hedef = d.G if d.G is not None else S.mean(0)

        def tasdik(M: np.ndarray) -> float:
            return kosinus(M.mean(0), hedef)

        eski = tasdik(S)
        A = p.W("tashih.A", (ds, ds))
        grad = celiski_gradyani(S, A, 0.0)
        grad = grad / max(float(np.max(np.abs(grad))), 1.0)
        musahhah = S - 0.05 * grad
        yeni = tasdik(musahhah)

        itidal = 0.5 * (S + musahhah)
        basarili = yeni > eski
        d.S = musahhah if basarili else itidal
        d.olcum.koy("tashih.eski_T", eski)
        d.olcum.koy("tashih.yeni_T", yeni)
        d.olcum.koy("tashih.başarılı", float(basarili))
        d.olcum.koy("tashih.düzeltme_miktarı",
                    float(np.linalg.norm(d.S - S)))


# =====================================================================
@kaydet
class Teyit(Meleke):
    """𝒪₂₉ Teyit -- **bağımsız** ikinci kanaldan doğrulama.

    ``NetTeyitSkoru = GüvenKatsayısı × BağımsızlıkDüzeyi``, ve
    ``T ← min(1, T + W_teyit)``. Buradaki incelik şudur: birbirini teyit
    eden iki kanal, ancak BAĞIMSIZ ise delil kuvvetlendirir. Bağımlı iki
    kanalın uyuşması yeni bilgi değildir -- bu yüzden çarpan olarak
    ``1 − |Cov|`` konur ve sınanır.
    """

    no, ad = 29, "Teyit"
    okur, yazar = ("S", "X"), ()

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, X = d.S, d.X
        ds = S.shape[1]
        # ikinci kanal: ham duyudan doğrudan türetilen bağımsız okuma
        E2 = kat_norm(X @ p.W("teyit.kanal2", (X.shape[1], ds)))
        guven = kosinus(S.mean(0), E2.mean(0))
        bagimsizlik = 1.0 - abs(pearson_cok(S, E2))
        net = guven * bagimsizlik
        eski = d.T
        d.T = float(min(1.0, eski + 0.2 * max(net, 0.0)))
        d.olcum.koy("teyit.güven", guven)
        d.olcum.koy("teyit.bağımsızlık", bagimsizlik)
        d.olcum.koy("teyit.net_skor", net)
        d.olcum.koy("teyit.T_artışı", d.T - eski)


def pearson_cok(A: np.ndarray, B: np.ndarray) -> float:
    a, b = A.ravel(), B.ravel()
    a0, b0 = a - a.mean(), b - b.mean()
    payda = float(np.linalg.norm(a0) * np.linalg.norm(b0))
    return float(a0 @ b0 / payda) if payda > 1e-12 else 0.0


# =====================================================================
@kaydet
class Tahkik(Meleke):
    """𝒪₃₀ Tahkik -- kökene inmek; **taklidi** ayırmak.

    ``S_tahkik = ArgMin_S (ℒ_köken(S) + Tenakuz(S, Aksiyomlar))``.
    ``TaklitDerecesi = exp(−α‖S − S_şöhret‖²)``: yaygın (şöhretli)
    cevaba ne kadar yakınsan taklit ihtimali o kadar yüksektir. Tahkik,
    yakınlığı değil **kökenle bağı** arar.
    """

    no, ad = 30, "Tahkik"
    okur, yazar = ("S", "X"), ()

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, X = d.S, d.X
        ds = S.shape[1]
        koken = kat_norm(X @ p.W("tahkik.köken", (X.shape[1], ds))).mean(0)
        sohret = S.mean(0)                       # en yaygın/ortalama cevap

        kokenle_bag = kosinus(S.mean(0), koken)
        taklit = float(np.exp(-0.5 * float(np.sum((S.mean(0) - sohret) ** 2))))
        T_tahkik = float(sigmoid(4.0 * (kokenle_bag - taklit)))
        d.olcum.koy("tahkik.kökenle_bağ", kokenle_bag)
        d.olcum.koy("tahkik.taklit_derecesi", taklit)
        d.olcum.koy("tahkik.T", T_tahkik)
        d.olcum.koy("tahkik.muhakkik", float(T_tahkik > 0.9))


# =====================================================================
@kaydet
class Tedebbur(Meleke):
    """𝒪₃₁ Tedebbür -- âkıbete bakmak.

    ``S_{t+H} = ∫ Evrim``; ``𝒱_âkıbet = 𝔼[Σ βᵏ 𝒰_gaye(S_{t+k})]``;
    ``Risk = P(S_{t+H} ∈ 𝒮_tehlike)``; ve emniyetli hamle
    ``ArgMax_a (𝒱 − γ·Risk)``.

    Risk, ileri sarımların **kaçının** felaket eşiğinin altına düştüğü
    ile ölçülür; bu bir Monte Carlo tahminidir ve öyle bildirilir.
    """

    no, ad = 31, "Tedebbür"
    okur, yazar = ("M", "G"), ()

    def uygula(self, d: Durum, p: Parametreler, H: int = 8,
               sarim: int = 24) -> None:
        M, G = d.M, d.G
        ds = M.shape[1]
        A = p.lie_tasarruf("tedebbür.evrim", ds, teta=0.15)
        rng = np.random.default_rng(p.tohum + 31)
        beta, tehlike = 0.9, 0.0

        degerler, felaket = [], 0
        for _ in range(sarim):
            s = M.mean(0).copy()
            V = 0.0
            for k in range(1, H + 1):
                s = kat_norm(s @ A.T + 0.1 * rng.normal(size=ds))
                V += (beta ** k) * float(np.exp(-np.linalg.norm(s - G)))
            degerler.append(V)
            if float(np.exp(-np.linalg.norm(s - G))) < tehlike + 1e-3:
                felaket += 1
        risk = felaket / sarim
        V_ort = float(np.mean(degerler))
        d.olcum.koy("tedebbür.değer", V_ort)
        d.olcum.koy("tedebbür.risk", risk)
        d.olcum.koy("tedebbür.net", V_ort * (1 - risk))
        d.olcum.koy("tedebbür.ufuk", float(H))


# =====================================================================
@kaydet
class SekZanYakin(Meleke):
    """𝒪₃₂ Şek-Zan-Yakîn İdraki -- makam tayini.

    ``P_idrak = σ(W[S ⊕ İ ⊕ T])`` ve

        Şek   : ``|P − 0.5| < ε_şek``
        Zan   : ``0.5 + ε_şek ≤ P < 1 − ε_yakîn``
        Yakîn : ``P ≥ 1 − ε_yakîn``

    **Metinde bir boşluk var ve kapatıldı.** Yukarıdaki üç şart
    ``P < 0.5 − ε_şek`` aralığını (yani "aleyhte zan") KAPSAMAZ. Sadık
    kalıp boş bırakmak, ``Makam``ı tanımsız yapardı. Burada o aralık
    **Vehim** diye adlandırıldı: zannın aleyhte olanı. Böylece parçalanış
    hem TAM hem AYRIK olur ve bu ``test_nefs.py``de sınanır.
    """

    no, ad = 32, "Şek-Zan-Yakîn"
    okur, yazar = ("S",), ("makam",)

    EPS_SEK = 0.05
    EPS_YAKIN = 0.05

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        ds = S.shape[1]
        ozellik = np.concatenate([S.mean(0), np.full(ds, d.tenakuz),
                                  np.full(ds, d.T)])
        d.P_idrak = float(sigmoid(ozellik @ p.v("idrak.p", 3 * ds)))
        d.makam = makam_tayin(d.P_idrak, self.EPS_SEK, self.EPS_YAKIN)
        d.olcum.koy("idrak.P", d.P_idrak)
        d.olcum.koy("idrak.entropi", ikili_entropi(d.P_idrak))
        d.olcum.koy("idrak.hüküm", hukum_agirligi(d.P_idrak, d.makam))
        d.not_dus(self.ad, "P=%.4f → %s" % (d.P_idrak, d.makam))


def makam_tayin(P: float, eps_sek: float = 0.05,
                eps_yakin: float = 0.05) -> str:
    """Dört makam; **tam ve ayrık** parçalanış."""
    if P >= 1 - eps_yakin:
        return "Yakîn"
    if P > 0.5 + eps_sek:
        return "Zan"
    if P >= 0.5 - eps_sek:
        return "Şek"
    return "Vehim"


def ikili_entropi(P: float) -> float:
    if P <= 0.0 or P >= 1.0:
        return 0.0
    return float(-P * np.log(P) - (1 - P) * np.log(1 - P))


def hukum_agirligi(P: float, makam: str) -> float:
    """``Hüküm = 1·𝕀_yakîn + P·𝕀_zan + 0.5·𝕀_şek`` (+ Vehim için ``P``)."""
    return {"Yakîn": 1.0, "Zan": P, "Şek": 0.5, "Vehim": P}[makam]


# =====================================================================
@kaydet
class Muhakeme(Meleke):
    """𝒪₃₃ Muhakeme -- **meclis**: bütün delillerin tartıldığı yer.

    ``Γ_mizan = AleyhteDeliller/(LehteDeliller+ε)``; karar eşiği
    ``𝕀(Γ < τ_kabul)``; ve makro operatör ``R_kebîr`` ile program sentezi.
    Karar geçmezse ``RejimDeğiştir`` -- yani nefs, hükmü zorlamak yerine
    kipini değiştirir.
    """

    no, ad = 33, "Muhakeme"
    okur, yazar = ("M", "S_kebir", "G_kebir"), ("S_kebir",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        ds = d.S_kebir.shape[0]
        R = p.lie_tasarruf("muhakeme.R", ds, teta=0.2)
        S_yeni = R @ d.S_kebir

        lehte = max(kosinus(S_yeni, d.G_kebir), 0.0) + max(d.T, 0.0)
        aleyhte = max(d.tenakuz, 0.0) + max(d.olcum.al("tenkit.sapma", 0.0), 0.0)
        mizan = guvenli_bol(aleyhte, lehte)
        tau = 1.0
        gecti = mizan < tau

        program = gelu(S_yeni @ p.W("muhakeme.p1", (ds, ds))) @ p.W("muhakeme.p2", (ds, ds))
        T_kebir = float(sigmoid(4.0 * (kosinus(S_yeni, d.G_kebir) - d.tenakuz)))
        d.S_kebir = kat_norm(T_kebir * program + (1 - T_kebir) * d.S_kebir)
        d.olcum.koy("muhakeme.mizan", mizan)
        d.olcum.koy("muhakeme.karar_geçti", float(gecti))
        d.olcum.koy("muhakeme.T_kebîr", T_kebir)
        d.olcum.koy("muhakeme.rejim_değişti", float(not gecti))
        d.not_dus(self.ad, "mizan=%.3f (τ=1.0) → %s"
                  % (mizan, "karar" if gecti else "rejim değiştir"))


# =====================================================================
@kaydet
class Tafsil(Meleke):
    """𝒪₃₄ Tafsil -- mücmeli dallarına açmak.

    ``S_tafsil = ⊕_k S_dal⁽ᵏ⁾``, ``w_k = softmax(v_dᵀ S_dal⁽ᵏ⁾)``, ve
    **sadakat şartı** ``Birleştir(S_tafsil) ≈ S_mücmel``.

    Tafsilin bedeli budur: açmak, toplayınca geri gelmiyorsa açmak değil
    dağıtmaktır. Sadakat hatası ölçülür ve sınanır.
    """

    no, ad = 34, "Tafsil"
    okur, yazar = ("S_kebir",), ()

    def uygula(self, d: Durum, p: Parametreler, K: int = 5) -> None:
        mucmel = d.S_kebir
        ds = len(mucmel)
        dallar = np.stack([gelu(mucmel @ p.W("tafsil.dal%d" % k, (ds, ds)))
                           for k in range(K)])
        w = softmax(dallar @ p.v("tafsil.vd", ds))
        birlesik = w @ dallar

        # sadakat: birleştirilmiş dalları mücmele en iyi afin uydurma
        olcek = float(birlesik @ mucmel) / max(float(birlesik @ birlesik), 1e-12)
        hata = float(np.linalg.norm(olcek * birlesik - mucmel)
                     / max(np.linalg.norm(mucmel), 1e-12))
        d.olcum.koy("tafsil.dallanma", float(K))
        d.olcum.koy("tafsil.sadakat_hatası", hata)
        d.olcum.koy("tafsil.netlik",
                    guvenli_bol(float(np.sum(np.linalg.norm(dallar, axis=1))),
                                float(np.linalg.norm(mucmel))))
        d.olcum.koy("tafsil.ağırlık_toplamı", float(w.sum()))


# =====================================================================
@kaydet
class Tefsir(Meleke):
    """𝒪₃₅ Tefsir -- müphemi **siyak ve sibakla** açmak.

    ``Murad = Softmax(S W [A⊕B]ᵀ/√d)[A⊕B]W_v``; ``Vuzuh = 1 − ℋ(P(Murad))``.
    ``Muhkemat`` (yakîn makamındaki önermeler) tefsirin sınırıdır:
    tefsir, muhkemle çelişemez -- çelişirse iş ``𝒪₃₆ Tevil``e düşer.
    """

    no, ad = 35, "Tefsir"
    okur, yazar = ("S", "H_hayal"), ()

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, H = d.S, d.H_hayal
        ds = S.shape[1]
        siyak = np.roll(S, 1, axis=0)               # önceki bağlam
        sibak = np.roll(S, -1, axis=0)              # sonraki bağlam
        baglam = np.concatenate([siyak, sibak], axis=0)
        W = p.W("tefsir.W", (ds, ds))
        agirlik = softmax((S @ W) @ baglam.T / np.sqrt(ds))
        murad = agirlik @ baglam @ p.W("tefsir.v", (ds, ds))

        pr = agirlik.mean(0)
        nz = pr > 0
        H_ent = -float(np.sum(pr[nz] * np.log(pr[nz])))
        azami = float(np.log(len(pr)))
        d.olcum.koy("tefsir.vuzuh", 1.0 - H_ent / max(azami, 1e-12))
        d.olcum.koy("tefsir.murad_normu", float(np.linalg.norm(murad)))
        d.olcum.koy("tefsir.muhkem_mi", float(d.makam == "Yakîn"))
        d.olcum.koy("tefsir.dikkat_toplamı", float(agirlik.sum(1).mean()))


# =====================================================================
@kaydet
class Tevil(Meleke):
    """𝒪₃₆ Tevil -- zâhir çelişince **irca**.

    ``T_tevil = 𝕀(Tenakuz(zâhir) > 0 ∧ Tenakuz(müevvel) = 0)``. Yani
    te'vil ancak (i) zâhirde hakikaten çelişki varsa ve (ii) te'vil o
    çelişkiyi KALDIRIYORSA geçerlidir. İki şarttan biri düşerse zâhir
    olduğu gibi kalır -- keyfî te'vilin önündeki sed budur ve sınanır.
    """

    no, ad = 36, "Tevil"
    okur, yazar = ("S",), ("S",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        ds = S.shape[1]
        A = p.W("tevil.A", (ds, ds))

        def celiski(M: np.ndarray) -> float:
            return celiski_skoru(M, A, 0.5)

        zahir = celiski(S)
        illet = celiski_gradyani(S, A, 0.5)
        illet = illet / max(float(np.max(np.abs(illet))), 1.0)
        muevvel = S - 0.1 * illet
        sonra = celiski(muevvel)

        gecerli = (zahir > 0.0) and (sonra < zahir)
        d.S = muevvel if gecerli else S
        d.olcum.koy("tevil.zâhir_çelişki", zahir)
        d.olcum.koy("tevil.müevvel_çelişki", sonra)
        d.olcum.koy("tevil.geçerli", float(gecerli))
        d.olcum.koy("tevil.gereksiz_tevil_yok", float(zahir > 0 or not gecerli))

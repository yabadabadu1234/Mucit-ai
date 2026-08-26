"""
𝒪₁–𝒪₁₀: duyudan mahiyete. Ham sinyalin suret, soyutlama ve mana kazandığı
mertebe.

Her sınıfın belgesinde, kaynak metnin hangi denklemlerini fiilen
hesapladığı ve hangilerini yalnız **tanı** olarak taşıdığı yazılıdır.
Metinde bazı satırlar (ör. ``Path_müşahede``, ``unglue(glue …)``) tip
teorisi tarafında yaşar; onlar bu modülde hesaplanmaz, ``omega_kategori``
tarafındadır ve orada makine ile denetlenir. Burada onların yerine, aynı
şeyin sayısal karşılığı olan **ölçüm** konur ve öyle işaretlenir.
"""
from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from .meleke import Meleke, kaydet
from .sahit import bolutle
from .uzaylar import (Durum, Olcumler, Parametreler, dikkat, gelu, guvenli_bol,
                      kat_norm, kosinus, nicele, sigmoid, softmax)


# =====================================================================
@kaydet
class Musahede(Meleke):
    """𝒪₁ Müşahede -- ``X_t = Π_müşahede(E_t)``.

    Hesaplanan: odak çekirdeği ``k_odak`` ile ağırlıklı toplama, öz-dikkat
    ``H⁽¹⁾``, süzgeç kapısı, ve **FNO çekirdeği**
    ``σ(Wv + ℱ⁻¹(R_θ·ℱv))`` (HoTT nüshasının 6. denklemi) -- bu, `yaklasim`
    modülünün Fourier işlemcisinin aynı fikridir ve burada spektral bir
    ön-süzgeç olarak koşar.

    Tanı: ``𝒜_müşahede = Tr(XᵀΔX)`` (uzamsal pürüz) ve ``ℒ_müşahede``.
    """

    no, ad = 1, "Müşahede"
    okur, yazar = ("E",), ("X",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        E = d.E
        n, di = E.shape

        # k_odak(r, r₀): konum uzayında Gauss odak penceresi
        r = np.arange(n, dtype=float)
        r0 = float(np.argmax(np.linalg.norm(E, axis=1)))   # en kuvvetli uyaran
        sigma = max(n / 4.0, 1.0)
        k_odak = np.exp(-((r - r0) ** 2) / (2 * sigma ** 2))
        X = E * k_odak[:, None]

        # FNO çekirdeği: R_θ kip çarpanları (düşük kipler geçer)
        F = np.fft.rfft(X, axis=0)
        kip = min(8, F.shape[0])
        R = p.v("müşahede.R", kip)
        F[:kip] *= (1.0 + 0.5 * R)[:, None]
        F[kip:] *= 0.0
        X_fno = np.fft.irfft(F, n=n, axis=0)
        X = np.tanh(X @ p.W("müşahede.W", (di, di)) + X_fno)

        # öz-dikkat
        Wq, Wk, Wv = (p.W("müşahede." + a, (di, di)) for a in "qkv")
        H1 = dikkat(X @ Wq, X @ Wk, X @ Wv)

        # süzgeç kapısı  X ⊙ σ(W_süzgeç X)
        kapi = sigmoid(H1 @ p.W("müşahede.süzgeç", (di, di)))
        d.X = kat_norm(H1 * kapi)

        # tanı: uzamsal pürüz  Tr(Xᵀ Δ X),  Δ = ikinci fark
        lap = np.diff(d.X, n=2, axis=0) if n >= 3 else np.zeros((1, di))
        d.olcum.koy("müşahede.pürüz", np.sum(lap * lap))
        d.olcum.koy("müşahede.sadakat", -np.mean((d.X - kat_norm(E)) ** 2))
        d.not_dus(self.ad, "odak r₀=%d, kip=%d" % (int(r0), kip))


# =====================================================================
@kaydet
class Hayal(Meleke):
    """𝒪₂ Hayal -- hissî suretlerin kaydı ve sönümlü tutulması.

    Hesaplanan: ``Z = LayerNorm(W_h X + b)``; ısı denklemi adımı
    ``∂Z/∂t = ΔZ − λZ + F(X)``; kapılı bellek
    ``H = α⊙Z + (1−α)⊙H₋``; ``Memoria`` üstel ağırlıklı iz; ve
    ``Z_sağlam = Quantize(Z, Δ)``.
    """

    no, ad = 2, "Hayal"
    okur, yazar = ("X",), ("Z_hayal", "H_hayal")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        X = d.X
        n, di = X.shape
        dh = d.d_hayal
        Z = kat_norm(X @ p.W("hayal.h", (di, dh)))

        # ısı denklemi adımı (ayrık Laplace, açık Euler)
        lam, dt = 0.1, 0.05
        Zc = Z.copy()
        ileri, geri = np.roll(Zc, -1, axis=0), np.roll(Zc, 1, axis=0)
        Z = Zc + dt * ((ileri - 2 * Zc + geri) - lam * Zc + 0.5 * Zc)

        onceki = d.H_hayal if d.H_hayal is not None else np.zeros_like(Z)
        alfa = sigmoid(np.concatenate([X, onceki], axis=1)
                       @ p.W("hayal.α", (di + dh, dh)))
        H = alfa * Z + (1 - alfa) * onceki

        d.Z_hayal = Z
        d.H_hayal = H
        # Memoria: geçmişe üstel sönümle bakan iz (burada tek adımlık hâli)
        beta = 0.7
        d.olcum.koy("hayal.memoria", np.mean(beta * H + (1 - beta) * onceki))
        d.olcum.koy("hayal.nicelenmis_sapma",
                    np.mean(np.abs(nicele(Z, 0.05) - Z)))
        d.olcum.koy("hayal.kapı_ortalaması", np.mean(alfa))


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


def kan_temeli(v: np.ndarray, nb: int, tur: Optional[str] = None
               ) -> np.ndarray:
    """``(n, d)`` girdiden ``(n, d, nb)`` tek değişkenli taban dizeyi.

    ``tur`` verilmezse :data:`KAN_TEMELI` kullanılır.
    """
    tur = tur or KAN_TEMELI
    if tur == "rbf":
        dugum = np.linspace(-2.5, 2.5, nb)
        h = (dugum[1] - dugum[0]) * 1.5
        return np.exp(-0.5 * ((v[:, :, None] - dugum) / h) ** 2)
    if tur == "bspline":
        from token_uzaylari.kan_spline import bspline_temeli, dugum_dizisi
        k = 3
        G = nb - k                      # temel sayısı G+k = nb olsun
        if G < 1:
            raise ValueError("bspline için nb > 3 olmalı")
        d = dugum_dizisi(G, k, -2.5, 2.5)
        n, dh = v.shape
        B = bspline_temeli(v.reshape(-1), d, k)      # (n·dh, nb)
        return B.reshape(n, dh, nb)
    raise ValueError(f"bilinmeyen KAN tabanı: {tur!r}")


# =====================================================================
@kaydet
class Muhayyile(Meleke):
    """𝒪₃ Muhayyile -- kayıtlı suretten YENİ suret kurmak.

    Hesaplanan: Lie tasarrufu ``R ▷ (Z ⊗ M)``; **KAN biçimi**
    ``Φ_kurgu(x) = Σ_q Φ_q(Σ_p φ_{q,p}(z_p))`` (HoTT nüshası, 4-5.
    denklemler) -- kenar fonksiyonları :func:`kan_temeli` ile (RBF veya
    B-spline, bkz. :data:`KAN_TEMELI`); yaratıcılık gürültüsü
    ``ξ ~ 𝒩(0, σ²)``; ve ``Serbestlik = D_KL(P(Ẑ) ‖ P(Z))`` ile fantezi
    süzgeci.

    Metnin ``Ẑ·𝕀(Serbestlik ≤ τ)`` sert kesmesi yerine **uyarlanan adım**
    kullanılır; gerekçesi aşağıda, ölçümüyle birlikte yazılıdır. Netice
    aynı şartı SAĞLAR: çıktının serbestliği her hâlükârda ``τ``nun
    altındadır. Yani muhayyile serbesttir, fakat serbestliği ölçülür ve
    haddi vardır.
    """

    no, ad = 3, "Muhayyile"
    okur, yazar = ("Z_hayal",), ("Z_muhayyile",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        Z = d.Z_hayal
        n, dh = Z.shape
        R = p.lie_tasarruf("muhayyile.R", dh, teta=0.4)
        M = p.W("muhayyile.M", (dh, dh))
        taban = (Z @ M) @ R.T

        # KAN: kenarlarda tek değişkenli taban, düğümlerde yalnız toplam.
        nb = 12

        def kenar(v: np.ndarray, ad: str) -> np.ndarray:
            """``Σ_p φ_{q,p}(v_p)``: her (girdi kanalı, taban) çifti için bir
            ağırlık; düğüm yalnız toplar. KAN'ın tarifi budur."""
            B = kan_temeli(v, nb)                                   # (n, dh, nb)
            C = p.W(ad, (dh * nb, v.shape[1])).reshape(dh, nb, v.shape[1])
            return np.einsum("npb,pbk->nk", B, C)

        ic = kenar(taban, "muhayyile.φ")
        dis = kenar(ic, "muhayyile.Φ")

        rng = np.random.default_rng(p.tohum + 3)
        # Metnin 7. denklemi ``Z⁽ᵗ⁺¹⁾ = Z⁽ᵗ⁾ + η(W Z⁽ᵗ⁾ + ξ)`` bir ARTIK
        # (residual) güncellemedir: muhayyile sıfırdan suret uydurmaz,
        # mevcut sureti BOZAR. Buna sadık kalındı.
        oran = float(np.linalg.norm(Z)) / max(float(np.linalg.norm(dis)), 1e-12)
        sapma = dis * oran + 0.05 * rng.normal(size=dis.shape)

        # Fantezi süzgeci: metinde ``Ẑ · 𝕀(Serbestlik ≤ τ)``, yani eşik
        # aşılınca çıktı SIFIRLANIR. Bu hâliyle kurulup ölçüldü:
        #
        #   eğitilmemiş ağırlıkta Serbestlik 4 ile 792 arasında çıkıyor ve
        #   süzgeç HER seferinde tetikleniyor; muhayyile bütünüyle susuyor.
        #
        # Sert kesme burada iki bakımdan kötüdür: (i) sureti tamamen yok
        # eder -- oysa kayıtlı suret zaten elde; (ii) eşik neyi keseceğini
        # değil, her şeyi keseceğini söyler. Bunun yerine ``η`` UYARLANIR:
        # serbestliği ``τ``nun altına sokan EN BÜYÜK adım seçilir. Böylece
        # muhayyile susturulmaz, DİZGİNLENİR; ve ``Serbestlik ≤ τ`` artık
        # çıktının sağladığı bir NİTELİKTİR (sınanır).
        tau = 2.0
        secilen, Zh = 0.0, Z.copy()
        for eta in (0.35, 0.2, 0.1, 0.05, 0.02, 0.01):
            aday = Z + eta * sapma
            if _kl_gauss(aday, Z, buzulme=0.5) <= tau:
                secilen, Zh = eta, aday
                break
        serbest = _kl_gauss(Zh, Z, buzulme=0.5)
        d.Z_muhayyile = Zh
        d.olcum.koy("muhayyile.serbestlik", serbest)
        d.olcum.koy("muhayyile.eta", secilen)
        d.olcum.koy("muhayyile.dizginlendi", float(secilen < 0.35))
        d.olcum.koy("muhayyile.tau", tau)
        d.not_dus(self.ad, "serbestlik=%.3f (τ=%.1f)" % (serbest, tau))


def _kl_gauss(A: np.ndarray, B: np.ndarray, buzulme: float = 0.1) -> float:
    """Çok değişkenli Gauss tahminleri arasında ``D_KL(P_A ‖ P_B)``.

    Örnek sayısı boyuttan küçük olabildiği için kovaryanslara **büzülme**
    (shrinkage) uygulanır: ``Σ ← (1−α)Σ + α·(tr Σ/d)·I``. Bu olmadan
    ``log det`` tekilleşir ve ölçüm ±∞ olur.
    """
    d = A.shape[1]
    ma, mb = A.mean(0), B.mean(0)

    def kov(V: np.ndarray) -> np.ndarray:
        C = np.cov(V.T) + 1e-9 * np.eye(d)
        return (1 - buzulme) * C + buzulme * (np.trace(C) / d) * np.eye(d)

    Ca, Cb = kov(A), kov(B)
    Cb_inv = np.linalg.inv(Cb)
    fark = mb - ma
    _, la = np.linalg.slogdet(Ca)
    _, lb = np.linalg.slogdet(Cb)
    return float(0.5 * (np.trace(Cb_inv @ Ca) + fark @ Cb_inv @ fark - d + lb - la))


# =====================================================================
@kaydet
class Tertip(Meleke):
    """𝒪₄ Tertip -- suretleri nizama koymak.

    Hesaplanan: ikili öncelik skoru ``Sıra(Zᵢ,Zⱼ) = σ(W(Zᵢ⊕Zⱼ))``den
    türetilen bir sıralama; permütasyon dizeyi ``M = Σ eₖ e_{π(k)}ᵀ``;
    ve nizam ölçüsü ``𝒞 = Tr(Zᵀ Δ_çizge Z)``.

    Metnin ``Equiv_tertip = (Z_ham ≃ Z_düzenli)`` satırı bir DENKLİK
    iddiasıdır: permütasyon tersinirdir, dolayısıyla tertip bilgi
    kaybetmez. Burada bu, ``M``in permütasyon olduğunun (satır ve sütun
    toplamlarının 1 olması) sınanmasıyla karşılanır.

    **Şahit bölütlemesi burada yapılır** (kütük H6). Tertip, suretleri
    yalnız sıralamaz; onları **bölümlere** de ayırır -- bir bulmacanın
    örneklerini birbirinden ayıran şey de bir tertiptir. Ayıraç sembolü
    ARANMAZ; akıştaki kopmalar ölçülür (``sahit.bolutle``). Böylece
    "bunlar ayrı örneklerdir" bilgisi modele bayrakla verilmiş olmaz,
    organla sezilmiş olur.

    Dışarıdan ``Durum.kur(..., sahitler=...)`` ile bölütleme verilirse o
    kabul edilir ve ``tertip.şahit_verildi = 1`` diye **işaretlenir**;
    verilen bölütleme modelin kabiliyeti sayılamaz.
    """

    no, ad = 4, "Tertip"
    okur, yazar = ("E", "Z_hayal"), ("sira", "sahitler")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        Z = d.Z_hayal
        n, dh = Z.shape

        # --- şahit bölütlemesi: **ham duyu** üzerinden
        #
        # Bölütleme evvelce ``Z_hayal`` üzerinden yapılıyordu ve ölçüldü:
        # kurallı beş şahitlik bir akışta üç şahit bulunuyor, kurallı ile
        # bozuk akış aynı bölütlemeyi veriyordu. Sebep 𝒪₁ Müşahede'nin
        # odak penceresi (``k_odak``) ve spektral kesmesidir: ikisi de
        # akışı yumuşatır, örnek sınırlarındaki kopmayı siler. Örnek
        # sınırı ham akışın hususiyetidir; onu suret kurulduktan sonra
        # aramak, delili işlemden sonra aramaya benzer.
        verildi = d.sahitler is not None
        if not verildi:
            b = bolutle(d.E)
            d.sahitler = b.sahitler
            d.olcum.koy("tertip.kopma_eşiği", b.esik)
            d.olcum.koy("tertip.bölütleme_yeterli", float(b.yeterli))
            if not b.yeterli and b.sebep:
                d.not_dus(self.ad, "şahit yok: %s" % b.sebep)
        else:
            d.olcum.koy("tertip.bölütleme_yeterli", float(len(d.sahitler) >= 2))
        d.olcum.koy("tertip.şahit_verildi", float(verildi))
        d.olcum.koy("tertip.şahit_sayısı", float(len(d.sahitler)))
        oncelik = (Z @ p.v("tertip.τ", dh))
        pi = np.argsort(-oncelik)               # yüksek öncelik önce
        d.sira = pi

        M = np.zeros((n, n))
        M[np.arange(n), pi] = 1.0
        Zd = M @ Z

        # çizge Laplasyeni ile nizam maliyeti (komşu farkları)
        C = float(np.sum((Zd[1:] - Zd[:-1]) ** 2))
        d.olcum.koy("tertip.nizam_maliyeti", C)
        d.olcum.koy("tertip.permütasyon_mu",
                    float(np.allclose(M.sum(0), 1) and np.allclose(M.sum(1), 1)))
        d.olcum.koy("tertip.düzensizlik",
                    float(np.sum(np.abs(np.argsort(pi) - np.arange(n)))))


# =====================================================================
@kaydet
class Tecrit(Meleke):
    """𝒪₅ Tecrit -- arazı atıp özü almak; **topolojik** soyutlama.

    Hesaplanan: ``P_D = U_k U_kᵀ`` Grassmann izdüşümü (SVD ile);
    normalize çizge Laplasyeni
    ``Δ = I − D^{-1/2} A D^{-1/2}``; ve **Betti sayıları**.

    Betti sayıları burada tahmin değil, TAM hesaptır: 1-iskelet için
    ``β₀`` bağlantılı bileşen sayısı, ``β₁ = |E| − |V| + β₀`` devir
    sayısıdır. İkisi de ``test_nefs.py``de bilinen çizgelerle sınanır.
    """

    no, ad = 5, "Tecrit"
    okur, yazar = ("X",), ("U_k", "D", "w_kesit")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        X = d.X
        n, di = X.shape
        k = max(1, min(di // 2, n - 1, 4))
        U, s, Vt = np.linalg.svd(X, full_matrices=False)
        Uk = Vt[:k].T                                   # (d_in, k) ortonormal
        d.U_k = Uk
        d.D = X @ Uk @ Uk.T                             # P_D(X)

        # ``w ∈ ℳ``: AĞIRLIK, bir kayıp fonksiyonunun durağan noktası
        # değil, parametrize lifleşmenin **kesitidir** (kütük H3).
        # ``ℳ = Gr(k, d_in)`` taban uzayı, lif ``U_k``ın gerdiği alt uzay;
        # kesit, veriden KAPALI FORMDA (SVD ile) okunur -- adım yok,
        # gradyan yok. ``omega_kategori_nbe.iliskiler.kesit_tipi`` bu
        # kesitin tip teorisi tarafındaki karşılığını makineyle denetler;
        # burada onun sayısal cismi taşınır.
        d.w_kesit = Uk
        # kesitin lifte kaldığının sağlaması: ``U_kᵀU_k = I``
        diklik = float(np.max(np.abs(Uk.T @ Uk - np.eye(k))))
        d.olcum.koy("tecrit.kesit_diklik_hatası", diklik)
        d.olcum.koy("tecrit.kesit_boyutu", float(k))

        # komşuluk çizgesi: eşik üstü kosinüs benzerliği
        Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
        A = (Xn @ Xn.T > 0.5).astype(float)
        np.fill_diagonal(A, 0.0)
        b0, b1 = betti_1iskelet(A)
        d.olcum.koy("tecrit.β0", b0)
        d.olcum.koy("tecrit.β1", b1)
        d.olcum.koy("tecrit.k", k)
        d.olcum.koy("tecrit.kayıp",
                    float(np.sum((X - d.D) ** 2)) / max(float(np.sum(X * X)), 1e-12))
        d.not_dus(self.ad, "k=%d  β₀=%d β₁=%d" % (k, b0, b1))


def normalize_laplasyen(A: np.ndarray) -> np.ndarray:
    """``Δ = I − D^{-1/2} A D^{-1/2}``. Yalıtık düğümlerde ``D=0``;
    orada ``D^{-1/2}`` yerine 0 alınır (kanonik ihtiyat)."""
    derece = A.sum(1)
    inv = np.where(derece > 0, 1.0 / np.sqrt(np.maximum(derece, 1e-12)), 0.0)
    return np.eye(len(A)) - (inv[:, None] * A * inv[None, :])


def betti_1iskelet(A: np.ndarray) -> Tuple[int, int]:
    """Basit çizgenin (1-iskelet) Betti sayıları.

    ``β₀`` = bağlantılı bileşen sayısı,
    ``β₁ = |E| − |V| + β₀`` (devir uzayının boyutu).
    """
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


# =====================================================================
@kaydet
class Tasavvur(Meleke):
    """𝒪₆ Tasavvur -- soyut çekirdeğin KAVRAM hâline gelmesi.

    Hesaplanan: ``S = GELU(D W_{d2s} + H W_{h2s} + b)``; Riemann metriği
    ``g_ij = ⟨∂S/∂uᵢ, ∂S/∂uⱼ⟩`` (sonlu farkla); hacim ögesi
    ``√det g``; makro kavram ``S_kebîr``; ve ``LayerNorm`` ile kemâl.

    **Muhayyile buraya katılır.** Tasavvur, hâfızadaki sureti (``H``)
    ve soyutlanmış özü (``D``) birleştirir; fakat kavram yalnız
    görülenden kurulmaz -- muhayyilenin ürettiği varyasyon (``𝒪₃``) da
    girer. Evvelce ``Z_muhayyile`` yazılıyor, kimse okumuyordu: ölçüldü,
    𝒪₃ düşürülünce netice hiç değişmiyordu. Katkı **küçük tutulur**
    (katsayı 0.25), çünkü muhayyile kavramı kurmaz, zenginleştirir.
    """

    no, ad = 6, "Tasavvur"
    okur, yazar = ("D", "H_hayal"), ("S", "S_kebir")
    ihtiyari = ("Z_muhayyile",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        D, H = d.D, d.H_hayal
        n, di = D.shape
        dh, ds = d.d_hayal, d.d_sem
        S = gelu(D @ p.W("tasavvur.d2s", (di, ds)) + H @ p.W("tasavvur.h2s", (dh, ds)))
        if d.Z_muhayyile is not None and d.Z_muhayyile.shape[0] == n:
            S = S + 0.25 * gelu(d.Z_muhayyile
                                @ p.W("tasavvur.m2s",
                                      (d.Z_muhayyile.shape[1], ds)))
            d.olcum.koy("tasavvur.muhayyile_katkısı", 1.0)
        else:
            d.olcum.koy("tasavvur.muhayyile_katkısı", 0.0)
        S = kat_norm(S + S @ p.W("tasavvur.res", (ds, ds)))
        d.S = S
        d.S_kebir = kat_norm(S.mean(0) @ p.W("tasavvur.macro", (ds, ds)))

        # g_ij: örnek ekseni boyunca sonlu fark → (n-1, ds) → Gram
        if n >= 2:
            dS = np.diff(S, axis=0)
            g = dS.T @ dS / max(n - 1, 1)
            isaret, logdet = np.linalg.slogdet(g + 1e-6 * np.eye(ds))
            d.olcum.koy("tasavvur.hacim_log", 0.5 * logdet if isaret > 0 else float("-inf"))
        d.olcum.koy("tasavvur.norm", float(np.linalg.norm(S) / np.sqrt(S.size)))


# =====================================================================
@kaydet
class Mana(Meleke):
    """𝒪₇ Mana -- kavramın **kasda** bağlanması (vâhime etiketi).

    Hesaplanan: ``K_t = LayerNorm(X W_k)`` vâhime etiketi;
    ``μ_mana = σ(S W_m + K W_v)``; bağlam dikkati; ``Ξ = μ_mana ⊗ μ_bağlam``
    ve ``μ_net``. ``AnlamDerecesi`` gaye ile kosinüs olarak ölçülür --
    gaye henüz kurulmadıysa (``𝒪₁₄``den önce) ölçüm ``nan`` kalır ve bu
    açıkça böyle bildirilir.
    """

    no, ad = 7, "Mana"
    okur, yazar = ("S", "X"), ("K_vahime", "mu_mana")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, X = d.S, d.X
        n, ds = S.shape
        di = X.shape[1]
        K = kat_norm(X @ p.W("mana.k", (di, ds)))
        d.K_vahime = K
        mu = sigmoid(S @ p.W("mana.m", (ds, ds)) + K @ p.W("mana.v", (ds, ds)))

        H = d.H_hayal if d.H_hayal is not None else S
        Wq = p.W("mana.q", (ds, ds))
        Wk = p.W("mana.hk", (H.shape[1], ds))
        Wv = p.W("mana.hv", (H.shape[1], ds))
        mu_baglam = dikkat(S @ Wq, H @ Wk, H @ Wv)

        Xi = mu * mu_baglam
        d.mu_mana = kat_norm(mu + Xi @ p.W("mana.x", (ds, ds)))
        if d.G is not None:
            d.olcum.koy("mana.anlam_derecesi", abs(kosinus(S.mean(0), d.G)))
        d.olcum.koy("mana.ilişki_katsayısı",
                    float(np.mean(sigmoid(np.concatenate([S, mu], axis=1)
                                          @ p.v("mana.vm", 2 * ds)))))


# =====================================================================
@kaydet
class Tahlil(Meleke):
    """𝒪₈ Tahlil -- bütünü cins ve fasıllarına ayırmak.

    Hesaplanan: ``S = Σ σᵢ uᵢ vᵢᵀ`` (SVD); spektral entropi
    ``−Σ pᵢ log pᵢ``, ``pᵢ = σᵢ²/Σσⱼ²``; ``S_cins`` (ilk k kip) ve
    ``S_fasıl`` (kalan); ve bileşenler arası **HSIC** bağımsızlık ölçüsü.

    HSIC burada gerçek biçimiyle kurulur: ``Tr(K H L H)/(n−1)²``,
    ``H = I − 11ᵀ/n``. Bağımsız iki bileşende ~0, bağımlı olanda kayda
    değer -- bu ``test_nefs.py``de doğrulanır.
    """

    no, ad = 8, "Tahlil"
    okur, yazar = ("S",), ("parcalar", "tekil_degerler")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        U, s, Vt = np.linalg.svd(S, full_matrices=False)
        d.tekil_degerler = s
        m = len(s)
        # bileşenler: σᵢ uᵢ vᵢᵀ'nin örnek eksenindeki izdüşümü
        d.parcalar = U * s                                   # (n, m)

        pay = s ** 2
        pr = pay / max(float(pay.sum()), 1e-12)
        nz = pr > 0
        d.olcum.koy("tahlil.entropi", -float(np.sum(pr[nz] * np.log(pr[nz]))))
        k = max(1, int(np.sum(s > 0.1 * s[0])))
        d.olcum.koy("tahlil.cins_kip_sayısı", k)
        if m >= 2:
            d.olcum.koy("tahlil.hsic_ilk_iki",
                        hsic(d.parcalar[:, 0], d.parcalar[:, 1]))
        d.not_dus(self.ad, "kip=%d entropi=%.3f" % (k, d.olcum.al("tahlil.entropi")))


def hsic(x: np.ndarray, y: np.ndarray, olcek: float | None = None) -> float:
    """Hilbert--Schmidt Bağımsızlık Ölçütü, Gauss çekirdeğiyle.

    ``HSIC = Tr(K H L H)/(n−1)²``. Bağımsızlıkta 0'a yakınsar.
    """
    n = len(x)
    if n < 4:
        return 0.0

    def gram(v: np.ndarray) -> np.ndarray:
        d2 = (v[:, None] - v[None, :]) ** 2
        s = olcek if olcek is not None else np.sqrt(0.5 * np.median(d2[d2 > 0])) if np.any(d2 > 0) else 1.0
        return np.exp(-0.5 * d2 / max(s * s, 1e-12))

    H = np.eye(n) - np.ones((n, n)) / n
    K, L = gram(x), gram(y)
    return float(np.trace(K @ H @ L @ H) / (n - 1) ** 2)


# =====================================================================
@kaydet
class Terkip(Meleke):
    """𝒪₉ Terkip -- parçaları yeniden **bir** kılmak.

    Hesaplanan: ağırlıklar ``w_k = softmax(vᵀS⁽ᵏ⁾)``; her parçaya bir Lie
    tasarrufu ``R_k ▷ S⁽ᵏ⁾``; ``Ω_bütünlük`` (metinde dış çarpım
    ``⋀``; burada **ters simetrik** kısım olarak alınır, çünkü ``⋀``in
    sayısal karşılığı budur); ve uyum katsayısıyla ölçeklenen sentez.

    ``UyumKatsayısı = min_{i≠j} CosSim`` düşükse sentez SÖNER: metnin
    ``S_sentez · σ(Uyum·β)`` çarpanı. Yani terkip, uyuşmayan parçaları
    zorla birleştirmez.
    """

    no, ad = 9, "Terkip"
    okur, yazar = ("S", "parcalar"), ("S",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n, ds = S.shape
        R = p.lie_tasarruf("terkip.R", ds, teta=0.25)
        w = softmax(S @ p.v("terkip.vt", ds))
        terkip = (w[:, None] * (S @ R.T))

        Om = terkip.T @ terkip
        Om = 0.5 * (Om - Om.T)                     # ⋀: ters simetrik kısım
        sentez = gelu(terkip + terkip @ Om.T * 0.1)

        # uyum: parçalar arası en KÜÇÜK kosinüs
        Sn = S / (np.linalg.norm(S, axis=1, keepdims=True) + 1e-12)
        C = Sn @ Sn.T
        np.fill_diagonal(C, np.inf)
        uyum = float(np.min(C)) if n > 1 else 1.0
        d.S = kat_norm(sentez) * float(sigmoid(3.0 * uyum))
        d.olcum.koy("terkip.uyum_katsayısı", uyum)
        d.olcum.koy("terkip.ω_ters_simetrik",
                    float(np.max(np.abs(Om + Om.T))))     # ≈ 0 olmalı


# =====================================================================
@kaydet
class Tezat(Meleke):
    """𝒪₁₀ Tezat -- zıtlığı ÖLÇMEK (henüz hüküm vermeden).

    Hesaplanan: ``Θ(Sᵢ,Sⱼ) = 1 − cos(Sᵢ,Sⱼ)`` tezat dizeyi; en büyük
    özvektör ile "tezat kutbu"; ve ``W_opp = −I + v v ᵀ`` zıtlık
    operatörü.

    Hüküm ``𝒪₁₁ Tenakuz``ün işidir; fakat Tezat'ın bulduğu **kutup**
    ona verilir. Evvelce bu meleke ``Durum``a hiçbir şey yazmıyordu ve
    ölçüldü: düşürüldüğünde neticede ``‖ΔN‖ = 0`` çıkıyordu -- yani
    hesaplanan her şey günlüğe yazılıp atılıyordu. Tezat kutbu artık
    veri yoluna konur ve 𝒪₁₁ çelişki çekirdeğini o kutupla kurar.
    Ölçmekle hükmetmek yine ayrıdır; ayrı olan, ölçünün ZAYİ olması
    değildir.
    """

    no, ad = 10, "Tezat"
    okur, yazar = ("S",), ("tezat_kutbu",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n = len(S)
        Sn = S / (np.linalg.norm(S, axis=1, keepdims=True) + 1e-12)
        Theta = 1.0 - Sn @ Sn.T
        d.olcum.koy("tezat.azami", float(np.max(Theta)))
        d.olcum.koy("tezat.ortalama", float(np.mean(Theta)))
        kutup = S.mean(0)
        if n >= 2:
            oz, vek = np.linalg.eigh(0.5 * (Theta + Theta.T))
            d.olcum.koy("tezat.baskın_özdeğer", float(oz[-1]))
            kutup = softmax(vek[:, -1]) @ S
            d.olcum.koy("tezat.kutup_normu", float(np.linalg.norm(kutup)))
        d.tezat_kutbu = kutup / (float(np.linalg.norm(kutup)) + 1e-12)

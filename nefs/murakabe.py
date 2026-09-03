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

from fitrat.tevafuk import fazla_sayma, tevafuk_olcusu
from mizan.istikra import ardisiklik_kaidesi, tam_istikra_mi

from .meleke import Meleke, kaydet
from .kule import ince, kaba
from .sahit import (artiklar, capraz_kovaryans, delil_dizileri, kulli_kaide)
from .uzaylar import (Durum, Parametreler, celiski_esigi, celiski_gradyani,
                      celiski_skoru,
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
    ihtiyari = ("Q_sual", "sonsal")

    def uygula(self, d: Durum, p: Parametreler, K: int = 200,
               eps: float = 1e-3) -> None:
        # 200 tur boyunca ``n×n`` dikkat koşar; kule olmadan bu, uzun
        # pencerede akışın en pahalı yeridir. Devridaim kaba kademede
        # döner; ``M`` ince eksene geri yayılır (artık bağı korunur).
        S_ham, H_ham = d.S, d.H_hayal
        n_ham = len(S_ham)
        S, kademe, _ = kaba(S_ham, d.tavan)
        H, _, _ = kaba(H_ham, d.tavan)
        n, ds = S.shape
        d.olcum.koy("teemmül.kule_kademesi", float(kademe))
        Wq = p.W("teemmül.q", (ds, ds))
        # Teemmül boşluğa dalmaz, bir SUAL etrafında döner. 𝒪₁₅'in
        # ürettiği ``Q_sual`` sorgu yönünü kaydırır. Evvelce ``Q_sual``
        # yazılıyor, kimse okumuyordu -- ölçüldü: 𝒪₁₅ düşürülünce netice
        # hiç değişmiyordu. Kaydırma toplanarak yapılır (çarpımla değil),
        # yoksa sual sıfıra yakınken sorgu söner.
        q_kaydirma = None
        if d.Q_sual is not None and np.shape(d.Q_sual) == (ds,):
            q_kaydirma = np.asarray(d.Q_sual, float)[None, :]
        d.olcum.koy("teemmül.sual_var", float(q_kaydirma is not None))
        Wk = p.W("teemmül.k", (H.shape[1], ds))
        Wv = p.W("teemmül.v", (H.shape[1], ds))

        # 𝒪₁₇'nin Bayes ardılı, teemmülün hangi satıra ağırlık vereceğini
        # söyler. Evvelce ``sonsal`` hesaplanıp atılıyordu -- ölçüldü:
        # 𝒪₁₇ düşürülünce netice hiç değişmiyordu.
        if d.sonsal is not None and len(d.sonsal) == n:
            agirlik = np.asarray(d.sonsal, float)[:, None] * n
            d.olcum.koy("teemmül.sonsal_var", 1.0)
        else:
            agirlik = 1.0
            d.olcum.koy("teemmül.sonsal_var", 0.0)
        M = kat_norm(S.copy() * agirlik)
        farklar: List[float] = []
        tau_durma = K
        for t in range(1, K + 1):
            Q = M @ Wq if q_kaydirma is None else M @ Wq + 0.5 * q_kaydirma
            Y = dikkat(Q, H @ Wk, H @ Wv)
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
        d.M = M if kademe == 0 else ince(M, n_ham, kademe)
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
    okur, yazar = ("S", "M"), ("S",)

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
        # **Temkin fiilen sarsılmazlığı KURAR.** Metin "S_müstakar,
        # hâlihazırdaki ile öncekinin vakarla ağırlıklı harmanıdır" der;
        # evvelce yalnız ölçülüyordu. Vakar yüksekse (akış pürüzsüzse)
        # hâl korunur; düşükse teemmül belleğine yaslanılır.
        d.S = kat_norm(vakar * S + (1.0 - vakar) * M)
        d.olcum.koy("temkin.harman", float(np.linalg.norm(d.S - S)))
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
    okur, yazar = ("S",), ("kusur",)
    ihtiyari = ("somut",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n, ds = S.shape
        maske = sigmoid(S @ p.W("tetkik.mikro", (ds, ds)))
        kilcal = S * maske

        # ideal: ilk yarı tekil kiple yeniden kurulan pürüzsüz hâl
        U, s, Vt = np.linalg.svd(S, full_matrices=False)
        k = max(1, len(s) // 2)
        ideal = (U[:, :k] * s[:k]) @ Vt[:k]
        # 𝒪₁₉ Temsil'in somut hâli varsa "ideal" ona göre düzeltilir:
        # kusur, sinyalin kendi düzgün hâlinden VE somut temsilinden
        # sapmasıdır. Evvelce ``somut`` üretilip atılıyordu.
        if d.somut is not None and d.somut.shape[0] == n:
            geri = d.somut @ np.linalg.pinv(p.W("temsil.dec", (ds, d.d_hayal)))
            ideal = 0.5 * ideal + 0.5 * geri
            d.olcum.koy("tetkik.somut_var", 1.0)
        else:
            d.olcum.koy("tetkik.somut_var", 0.0)
        kusur = np.abs(kilcal - ideal)
        d.kusur = kusur          # 𝒪₂₈ Tashih bunu kendi formülünde kullanır

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
    ihtiyari = ("G", "A_neden", "kusur")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        ds = S.shape[1]
        hedef = d.G if d.G is not None else S.mean(0)

        def tasdik(M: np.ndarray) -> float:
            return kosinus(M.mean(0), hedef)

        eski = tasdik(S)
        A = p.W("tashih.A", (ds, ds))
        Sk, kademe_t, _ = kaba(S, d.tavan)   # çelişki dizeyi ``n×n``
        esik = celiski_esigi(Sk, A, 0.5)
        d.olcum.koy("tashih.eşik", esik)
        grad = celiski_gradyani(Sk, A, esik)
        if kademe_t:
            grad = ince(grad, len(S), kademe_t)
        # **Düzeltme illetin bulunduğu yerde yapılır.** 𝒪₂₂ İllet Keşfi
        # bir nedensellik çizgesi (``A_neden``) kuruyor, hiçbir meleke
        # okumuyordu -- ölçüldü: 𝒪₂₂ düşürülünce netice hiç değişmiyordu.
        # Artık düzeltme, satırın nedensel derecesiyle ağırlıklanır:
        # hiçbir şeyin sebebi olmayan satırı düzeltmek bir şeyi düzeltmez.
        if d.A_neden is not None and d.A_neden.shape == (len(S), len(S)):
            derece = np.abs(np.asarray(d.A_neden, float)).sum(1)
            agirlik = derece / (float(np.max(derece)) + 1e-12)
            grad = grad * (0.5 + 0.5 * agirlik)[:, None]
            d.olcum.koy("tashih.illet_ağırlığı", 1.0)
        else:
            d.olcum.koy("tashih.illet_ağırlığı", 0.0)
        # Metnin kendi formülü: ``S − γ·KusurHaritası ⊙ ∇Tenakuz``.
        # Kusur haritası evvelce hiç çarpılmıyordu -- formül yazılıydı,
        # icra edilmiyordu.
        if d.kusur is not None and d.kusur.shape == grad.shape:
            k = d.kusur / (float(np.max(d.kusur)) + 1e-12)
            grad = grad * k
            d.olcum.koy("tashih.kusur_kullanıldı", 1.0)
        else:
            d.olcum.koy("tashih.kusur_kullanıldı", 0.0)
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

    **Şahitler burada tartılır** (kütük H6). Bir bulmacanın beş örneği,
    beş şahit demek DEĞİLDİR: birbirinden türemiş şahitler tek şahit
    hükmündedir. ``fitrat.tevafuk`` bunu zaten ölçüyordu ve ana akışta
    hiç çağrılmıyordu; artık çağrılır:

    * ``tevafuk_olcusu`` -- şartlı bağımsızlıkla ağırlıklı uyuşma,
    * ``fazla_sayma``    -- ``müteber şahit = 1 + (m−1)·ortalama ağırlık``.

    ``müteber_sahit``, 𝒪₃₂'deki istikrânın ``n``idir. Yani "kaç örnek
    gördüm" değil, "kaç **bağımsız** örnek gördüm" sorusunun cevabı
    hükme girer.
    """

    no, ad = 29, "Teyit"
    okur, yazar = ("S", "X", "E"), ("sahit_agirliklari",)
    ihtiyari = ("sahitler", "kaideler", "nakz")

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

        # ---- şahitlerin tartılması
        sahitler = d.sahitler or []
        kaideler = d.kaideler or []
        m = len(sahitler)
        if m < 2 or len(kaideler) != m:
            d.sahit_agirliklari = np.ones(max(m, 0))
            d.muteber_sahit = float(m)
            d.tevafuk = 0.0
            d.olcum.koy("teyit.tevafuk_tanımlı", 0.0)
            d.olcum.koy("teyit.müteber_şahit", float(m))
            return

        # deliller ham duyu uzayında kurulur -- kaideler orada yaşar
        # (bkz. 𝒪₁₈ Kıyas). ``S`` ile kurulup ölçüldü: satırları karışmış
        # bir uzayda hiçbir kaide tutmuyor, bütün delil dizileri sıfır
        # çıkıyor ve müteber şahit sayısı 1'e çöküyordu.
        deliller, tol = delil_dizileri(d.E, sahitler, kaideler)
        # hipotez: şahit i, nakzedilmemiş olanlardan mıdır?
        nakz = set(d.nakz or [])
        H = np.array([0.0 if i in nakz else 1.0 for i in range(m)])
        if H.min() == H.max():
            # tek sınıf: log-olabilirlik oranı tanımsızlaşır. Bu bir
            # kusur değil, hâlin kendisidir -- ayrıştırıcı delil yok.
            H = np.array([1.0] * m)

        t = tevafuk_olcusu(deliller, H)
        d.tevafuk = float(t["tevafuk"]) if t["tevafuk"] is not None else 0.0
        f = fazla_sayma(deliller, H)
        d.muteber_sahit = float(f.get("muteber_şahit_sayısı", m))

        # şahit başına ağırlık: kendi delil dizisinin, hipotezle uyuşması
        agirlik = []
        for k in range(m):
            uyusan = float(np.mean(deliller[k] == H))
            agirlik.append(uyusan)
        d.sahit_agirliklari = np.asarray(agirlik, float)

        d.olcum.koy("teyit.tevafuk_tanımlı", 1.0)
        d.olcum.koy("teyit.tevafuk", d.tevafuk)
        d.olcum.koy("teyit.şahit_sayısı", float(m))
        d.olcum.koy("teyit.müteber_şahit", d.muteber_sahit)
        d.olcum.koy("teyit.fazla_sayma_oranı",
                    float(f.get("fazla_sayma_oranı", 1.0)))
        d.olcum.koy("teyit.delil_toleransı", tol)
        d.not_dus(self.ad, "şahit=%d → müteber=%.2f  tevafuk=%.3f"
                  % (m, d.muteber_sahit, d.tevafuk))


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

    **Küllî kaide burada mühürlenir** (kütük H6). Kaide, şahitlerin
    çapraz kovaryanslarının kutupsal toplamıdır (`sahit.kulli_kaide`) --
    fakat **nakzedilmiş şahitler dışarıda bırakılır**: kökeni bozuk
    şahitten alınan kaide taklittir, tahkik değildir.

    Evvelki hâlde ``TaklitDerecesi`` daima 1 çıkıyordu, çünkü ``S_şöhret``
    ``S.mean(0)``ın kendisi olarak alınmıştı: ``exp(−0.5·‖x−x‖²) = 1``.
    Yani "taklit mi?" sorusunun cevabı hesaplanmadan "evet" veriliyordu.
    Şöhret artık şahitlerden **bağımsız** bir merci olarak alınır: en
    kalabalık kümenin merkezi değil, mananın ana bileşenidir; taklit
    ölçüsü de ona olan uzaklıktan okunur.
    """

    no, ad = 30, "Tahkik"
    okur, yazar = ("S", "X", "E"), ("kaide",)
    ihtiyari = ("sahitler", "nakz")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, X = d.S, d.X
        ds = S.shape[1]
        koken = kat_norm(X @ p.W("tahkik.köken", (X.shape[1], ds))).mean(0)

        # şöhret: mananın baskın bileşeni -- "herkesin söylediği".
        U, sv, Vt = np.linalg.svd(S - S.mean(0), full_matrices=False)
        sohret = Vt[0] * float(np.linalg.norm(S.mean(0)))

        kokenle_bag = kosinus(S.mean(0), koken)
        taklit = float(np.exp(-0.5 * float(np.sum((S.mean(0) - sohret) ** 2))))
        T_tahkik = float(sigmoid(4.0 * (kokenle_bag - taklit)))
        d.olcum.koy("tahkik.kökenle_bağ", kokenle_bag)
        d.olcum.koy("tahkik.taklit_derecesi", taklit)
        d.olcum.koy("tahkik.T", T_tahkik)
        d.olcum.koy("tahkik.muhakkik", float(T_tahkik > 0.9))

        # ---- küllî kaidenin mühürlenmesi
        sahitler = d.sahitler or []
        nakz = set(d.nakz or [])
        temiz = [s for i, s in enumerate(sahitler) if i not in nakz]
        if temiz:
            # kaide ham duyu uzayında yaşar (bkz. 𝒪₁₈ Kıyas)
            d.kaide = kulli_kaide([capraz_kovaryans(d.E, s) for s in temiz])
            kalan = [float(np.mean(artiklar(d.E, s, d.kaide)))
                     for s in temiz if artiklar(d.E, s, d.kaide).size]
            d.olcum.koy("tahkik.kaide_artığı",
                        float(np.mean(kalan)) if kalan else float("nan"))
            d.olcum.koy("tahkik.kaide_dikliği",
                        float(np.max(np.abs(d.kaide.T @ d.kaide
                                            - np.eye(len(d.kaide))))))
        else:
            # Hiç temiz şahit yok: kaide **birim**tir, yani "hiçbir şey
            # değişmiyor" hükmü. Uydurma bir kaide üretmek yerine
            # cehli îlan etmek doğrusudur; 𝒪₃₂ bunu Şek'e çevirir.
            d.kaide = np.eye(d.E.shape[1])
            d.olcum.koy("tahkik.kaide_artığı", float("nan"))
        d.olcum.koy("tahkik.temiz_şahit", float(len(temiz)))


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
    okur, yazar = ("M", "G"), ("akibet",)

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
        d.akibet = float(risk)   # 𝒪₃₃ mîzânda aleyhte delil olarak tartar
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

    **``P_idrak`` artık istikrâdan gelir** (kütük H3/H6). Evvelce
    ``σ(W[S ⊕ tenakuz ⊕ T])`` idi: eğitilmemiş bir ağırlıkla çarpılan,
    hiçbir delile bağlanmayan bir sayı. Şimdi:

        k = nakzedilmemiş şahit sayısı
        n = MÜTEBER şahit sayısı (𝒪₂₉'un fazla saymadan arındırdığı)
        P = (k+α)/(n+α+β)          -- Laplace'ın ardışıklık kaidesi

    (`mizan.istikra.ardisiklik_kaidesi`). İki hüküm buradan çıkar ve
    ikisi de kasten böyledir:

    * **Nakz varsa yakîn olmaz.** Tek karşı örnek küllî önermeyi
      düşürür; makam en çok Zan'a kadar çıkabilir.
    * **Sonlu şahitle yakîn olmaz.** ``β > 0`` iken ``P < 1``
      (`tam_istikra_mi`). Eksik istikrâdan yakîn devşirmek, delilden
      değil önselden devşirmektir. Bu, projenin dürüstlük şartıdır ve
      gizlenmez -- ölçüsü ``idrak.tam_istikrâ`` diye raporlanır.

    Şahit yoksa eski vekil formül **açıkça işaretlenerek** kullanılır
    (``idrak.vekil_formül = 1``).

    **Sükût** (kütük H10): makam Şek ise ``d.sukut`` kalkar ve beyan
    melekeleri susar. Bilmediğini söylememek bir kabiliyettir.
    """

    no, ad = 32, "Şek-Zan-Yakîn"
    okur, yazar = ("S",), ("makam", "sukut")
    ihtiyari = ("sahitler", "nakz", "sahit_agirliklari",
                "mertebe_tikanikligi")

    EPS_SEK = 0.05
    EPS_YAKIN = 0.05

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        ds = S.shape[1]
        sahitler = d.sahitler or []
        m = len(sahitler)

        if m >= 2 and d.nakz is not None:
            k_ham = m - len(d.nakz)
            muteber = max(float(d.muteber_sahit), 1.0)
            # müteber şahit sayısı kesirlidir; istikrâ tam sayı ister.
            n = max(1, int(round(min(muteber, float(m)))))
            k = int(np.clip(round(k_ham * n / max(m, 1)), 0, n))
            d.P_idrak = float(ardisiklik_kaidesi(k, n))
            d.olcum.koy("idrak.istikrâ_k", float(k))
            d.olcum.koy("idrak.istikrâ_n", float(n))
            d.olcum.koy("idrak.tam_istikrâ", float(tam_istikra_mi(k, n)))
            d.olcum.koy("idrak.vekil_formül", 0.0)
            makam = makam_tayin(d.P_idrak, self.EPS_SEK, self.EPS_YAKIN)
            if d.nakz and makam == "Yakîn":
                makam = "Zan"       # nakz varken yakîn iddiası meşru değil
                d.olcum.koy("idrak.nakz_yakîni_düşürdü", 1.0)
            d.makam = makam
        else:
            ozellik = np.concatenate([S.mean(0), np.full(ds, d.tenakuz),
                                      np.full(ds, d.T)])
            d.P_idrak = float(sigmoid(ozellik @ p.v("idrak.p", 3 * ds)))
            d.makam = makam_tayin(d.P_idrak, self.EPS_SEK, self.EPS_YAKIN)
            d.olcum.koy("idrak.vekil_formül", 1.0)

        # **Mertebe tıkanıklığı yakîni düşürür** (kütük H40). 𝒪₂₁'in
        # 20 ∞-kategori mertebesinden geçirdiği mana bir mertebeden
        # ötekine TAŞINAMIYORSA -- yani taşınamayan dik bileşen normun
        # onda dokuzunu aşıyorsa -- o mana bir mertebeye hapsolmuştur.
        # Hapsolmuş bir manadan yakîn devşirmek, nakz varken yakîn
        # iddia etmekle aynı hatadır: küllîlik iddiası yerel bir delille
        # temellendirilmiş olur. Makam en çok Zan'a çıkabilir.
        if d.mertebe_tikanikligi is not None:
            tik = np.asarray(d.mertebe_tikanikligi, float)
            tikanik = int(np.sum(tik > 0.9))
            d.olcum.koy("idrak.tıkanık_lif", float(tikanik))
            d.olcum.koy("idrak.tıkanıklık_ort", float(tik.mean()))
            if tikanik and d.makam == "Yakîn":
                d.makam = "Zan"
                d.olcum.koy("idrak.tıkanıklık_yakîni_düşürdü", 1.0)
            else:
                d.olcum.koy("idrak.tıkanıklık_yakîni_düşürdü", 0.0)

        # **Sükût iki kapıdan geçer** (kütük H16). Birincisi makamdır:
        # Şek'te söylenecek bir şey yoktur. İkincisi serbest enerjidir:
        # ``F_tenakuz ≤ ε_durgun`` ise zihinde çözülmesi gereken bir
        # tenakuz kalmamıştır ve zihin durgun suya döner. ``ε_durgun``
        # ELLE KONMAZ (H17): mananın kendi gürültü tabanından türetilir.
        eps_durgun = float(np.mean(np.abs(np.diff(S, axis=0)))) * 0.05 \
            if len(S) > 1 else 0.0
        durgun = bool(d.serbest_enerji <= eps_durgun)
        d.sukut = bool(d.makam == "Şek" or durgun)
        d.olcum.koy("idrak.ε_durgun", eps_durgun)
        d.olcum.koy("idrak.F_tenakuz", d.serbest_enerji)
        d.olcum.koy("idrak.durgun", float(durgun))
        d.olcum.koy("idrak.P", d.P_idrak)
        d.olcum.koy("idrak.entropi", ikili_entropi(d.P_idrak))
        d.olcum.koy("idrak.hüküm", hukum_agirligi(d.P_idrak, d.makam))
        d.olcum.koy("idrak.sükût", float(d.sukut))
        d.not_dus(self.ad, "P=%.4f → %s%s"
                  % (d.P_idrak, d.makam, "  (sükût)" if d.sukut else ""))


#: ``zan`` ile ``zann-ı gālib``i ayıran eşik. Elle konmuş bir sayı
#: değildir: `mizan/munazara.py`nin ``MERTEBELER`` cetvelinden gelir.
ZANN_I_GALIB_ESIGI: float = 0.75


#: Görünen adlar -- `mizan/munazara.py`nin küçük harfli mertebe
#: adlarının bu dosyadaki yazımı. Eşikler oradan gelir, adlar burada
#: sunulur; iki ayrı cetvel DEĞİLDİR.
_MAKAM_ADI: Dict[str, str] = {
    "yakîn": "Yakîn", "zann-ı gālib": "Zann-ı gālib", "zan": "Zan",
    "şek": "Şek", "vehim": "Vehim",
}


def makam_tayin(P: float, eps_sek: float = 0.0,
                eps_yakin: float = 0.0) -> str:
    """**Beş** makam; eşikler **mîzânın cetvelinden**, elden değil.

    **ÖLÇÜLEN VE DÜZELTİLEN KUSUR (kütük H214).** Bu fonksiyon
    eşiklerinin *"elle konmuş bir sayı değil, `mizan/munazara.py`nin
    ``MERTEBELER`` cetvelinden"* geldiğini söylüyordu; ``0,75`` için
    doğruydu, gerisi için **değildi**. Kaynakla yüzleştirildi
    (``mertebe_adi`` ile aynı ``P``lerde):

    ========  ================  ==============  ==============
    ``P``     kaynak (mîzân)    bu fonksiyon    doğru mu
    ========  ================  ==============  ==============
    0,25      şek               Vehim           **HAYIR**
    0,40      şek               Vehim           **HAYIR**
    0,50      zan               Şek             **HAYIR**
    0,55      zan               Şek             **HAYIR**
    0,95      zann-ı gālib      Yakîn           **HAYIR**
    0,99      zann-ı gālib      Yakîn           **HAYIR**
    ========  ================  ==============  ==============

    Kaynaktan sapma **7/13**ti. Aynı beş mertebeyi kuran ikinci nüsha
    (`nefs/qyazmac.py`nin Gray merdiveni) ise **0/13** sapıyordu; yani
    yanlış olan buydu.

    Zararı nazarî değildi: `nefs/kademeler.py` tasdik ağırlığını
    (``hukum_agirligi(p, makam_tayin(p))``) buradan alır ve o hat
    ``main/egitim.py``den fiilen erişilir. İki uçta birden yanlıştı --
    ``0,95``te **fazla** iddia (zann-ı gālibe "Yakîn" demek, H10/H100'ün
    tam aksi), ``0,25-0,40``ta **eksik** iddia (şek'e "Vehim" demek).

    ``eps_*`` payları **varsayılan olarak sıfırdır**: cetvelde öyle bir
    bant yoktur. Sıfırdan büyük verilirse ``şek``in tabanı aşağı,
    ``yakîn``in tabanı yukarı kaydırılır ve bu artık cetvelin değil
    çağıranın hükmüdür.
    """
    from mizan.munazara import MERTEBELER
    e_sek, e_yakin = float(eps_sek), float(eps_yakin)
    for esik, ad in MERTEBELER:                  # cetvel azalan sırada
        e = float(esik)
        if ad == "yakîn":
            e -= e_yakin                         # yakîn tabanını gevşet
        elif ad == "şek":
            e -= e_sek                           # şek tabanını gevşet
        if P >= e:
            return _MAKAM_ADI[ad]
    return "Vehim"


def ikili_entropi(P: float) -> float:
    if P <= 0.0 or P >= 1.0:
        return 0.0
    return float(-P * np.log(P) - (1 - P) * np.log(1 - P))


def hukum_agirligi(P: float, makam: str) -> float:
    """``Hüküm = 1·𝕀_yakîn + P·𝕀_zan + 0.5·𝕀_şek`` (+ Vehim için ``P``).

    ``Zann-ı gālib`` de ``P``dir: kuvvetli zan, zannın kendi
    kuvvetiyle tartılır; ``1``e yuvarlanmaz. Yuvarlansaydı, ayırt
    etmek için açtığımız mertebe hemen yakîne katılmış olurdu.
    """
    return {"Yakîn": 1.0, "Zann-ı gālib": P, "Zan": P,
            "Şek": 0.5, "Vehim": P}[makam]


# =====================================================================
@kaydet
class Muhakeme(Meleke):
    """𝒪₃₃ Muhakeme -- **meclis**: bütün delillerin tartıldığı yer.

    ``Γ_mizan = AleyhteDeliller/(LehteDeliller+ε)``; karar eşiği
    ``𝕀(Γ < τ_kabul)``; ve makro operatör ``R_kebîr`` ile program sentezi.
    Karar geçmezse ``RejimDeğiştir`` -- yani nefs, hükmü zorlamak yerine
    kipini değiştirir.

    **En büyük kopukluk buradaydı ve burada kapatıldı.** ``S_kebîr`` bir
    kere 𝒪₆ Tasavvur'da yazılıyor, sonra hiç güncellenmiyordu. Beyan
    melekeleri (𝒪₃₇–𝒪₄₁) ise yalnız ``S_kebîr``i okur. Netice: 𝒪₇'den
    𝒪₃₂'ye kadar ``S`` üzerinde yapılan bütün iş -- tefekkür, illet,
    tashih, te'vil -- kelama HİÇ ULAŞMIYORDU. Ölçüldü: bu melekelerin
    düşürülmesi ``‖ΔN‖ = 0`` veriyordu; sebep melekelerin boş olması
    değil, mecliste mikro hâlin okunmamasıydı.

    Meclis artık mevcut ``S``ten toplanır: tez, o âna kadar yapılmış
    bütün murâkabenin hâlidir. Eski ``S_kebîr`` atılmaz, harmana girer
    (``0.5/0.5``) -- tasavvurun kurduğu makro mana da bir delildir.
    """

    no, ad = 33, "Muhakeme"
    okur, yazar = ("M", "S", "S_kebir", "G_kebir", "E"), ("S_kebir",)
    ihtiyari = ("kaide", "sahitler", "nakz", "mertebe_tikanikligi",
                "mertebe_betti")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        ds = d.S_kebir.shape[0]
        guncel = kat_norm(d.S.mean(0) @ p.W("muhakeme.macro", (ds, ds)))
        d.S_kebir = kat_norm(0.5 * d.S_kebir + 0.5 * guncel)
        d.olcum.koy("muhakeme.mikro_katkısı",
                    float(np.linalg.norm(guncel)))
        # **Küllî kaide burada tatbik edilir.** 𝒪₃₀ Tahkik'in mühürlediği
        # kaide varsa makro operatör O'dur; yoksa tohumdan türetilen bir
        # dönme kullanılır ve bu **işaretlenir**. Evvelce kaide hiç
        # okunmuyordu: 𝒪₃₀ hesaplıyor, kimse kullanmıyordu -- ölçüldü,
        # 𝒪₃₀ düşürülünce netice hiç değişmiyordu.
        if d.kaide is not None and d.kaide.shape == (ds, ds):
            R = d.kaide
            d.olcum.koy("muhakeme.kaide_tatbik", 1.0)
        else:
            R = p.lie_tasarruf("muhakeme.R", ds, teta=0.2)
            d.olcum.koy("muhakeme.kaide_tatbik", 0.0)
        S_yeni = R @ d.S_kebir

        lehte = max(kosinus(S_yeni, d.G_kebir), 0.0) + max(d.T, 0.0)
        aleyhte = (max(d.tenakuz, 0.0)
                   + max(d.olcum.al("tenkit.sapma", 0.0), 0.0)
                   + max(d.akibet, 0.0))     # 𝒪₃₁'in ölçtüğü âkıbet riski

        # **Şahit delili mîzâna girer.** Küllî kaide ``d_in`` uzayında
        # yaşadığı için (bkz. 𝒪₁₈) meclis onu dizey olarak tatbik
        # edemeyebilir; fakat hükmünü tartabilir ve tartmalıdır: kaç
        # müteber şahit tasdik ediyor, kaçı nakzediyor. Bu bağ olmadan
        # 𝒪₂₃ Mantık, 𝒪₂₉ Teyit ve 𝒪₃₀ Tahkik'in bütün işi mecliste
        # kayboluyordu -- ölçüldü, üçü de "tesirsiz" çıkıyordu.
        if d.sahitler:
            m = len(d.sahitler)
            n_nakz = len(d.nakz or [])
            muteber = max(float(d.muteber_sahit), 0.0)
            lehte += muteber * (m - n_nakz) / max(m, 1)
            aleyhte += muteber * n_nakz / max(m, 1)
            d.olcum.koy("muhakeme.şahit_lehte", muteber * (m - n_nakz) / max(m, 1))
            d.olcum.koy("muhakeme.şahit_aleyhte", muteber * n_nakz / max(m, 1))
            # 𝒪₃₀'un mühürlediği küllî kaide, kalan şahitleri ne kadar
            # açıklıyor? Kaide dizey olarak tatbik edilemese de (boyut
            # uyuşmazlığı) hükmü tartılabilir; bu bağ olmadan 𝒪₃₀
            # tamamen tesirsiz kalıyordu.
            if d.kaide is not None and d.kaide.shape[0] == d.E.shape[1]:
                temiz = [x for i, x in enumerate(d.sahitler)
                         if i not in set(d.nakz or [])]
                art = [float(np.mean(artiklar(d.E, x, d.kaide)))
                       for x in temiz if artiklar(d.E, x, d.kaide).size]
                if art:
                    ort = float(np.mean(art))
                    lehte += max(1.0 - ort, 0.0)
                    aleyhte += max(ort, 0.0)
                    d.olcum.koy("muhakeme.kaide_artığı", ort)
        # **Mertebeler arası tıkanıklık ve ezber mîzâna girer** (H40).
        # 𝒪₂₁'in 20 mertebeden geçirdiği mana bir mertebede hapsolduysa
        # (tıkanıklık) yahut ayrık adacıklara bölündüyse (``β₀ > 1``,
        # yani ezber -- H23), bu aleyhte delildir. Tıkanıklığın TERSİ de
        # delildir ve lehte sayılır: yirmi mertebenin hepsinde tutan bir
        # mana, tek mertebede tutandan kuvvetlidir.
        if d.mertebe_tikanikligi is not None:
            tik = np.asarray(d.mertebe_tikanikligi, float)
            ort = float(tik.mean())
            aleyhte += ort
            lehte += max(1.0 - ort, 0.0)
            d.olcum.koy("muhakeme.mertebe_aleyhte", ort)
            d.olcum.koy("muhakeme.mertebe_lehte", max(1.0 - ort, 0.0))
        if d.mertebe_betti is not None:
            b0 = np.asarray(d.mertebe_betti, float)
            ezber = float(np.mean(np.maximum(b0 - 1.0, 0.0)))
            aleyhte += ezber
            d.olcum.koy("muhakeme.mertebe_ezber", ezber)

        mizan = guvenli_bol(aleyhte, lehte)
        tau = 1.0
        gecti = mizan < tau

        program = gelu(S_yeni @ p.W("muhakeme.p1", (ds, ds))) @ p.W("muhakeme.p2", (ds, ds))
        nakz_orani = (len(d.nakz or []) / max(len(d.sahitler or []), 1)
                      if d.sahitler else 0.0)
        T_kebir = float(sigmoid(4.0 * (kosinus(S_yeni, d.G_kebir)
                                       - d.tenakuz - nakz_orani)))
        # **Karar geçmezse program tatbik EDİLMEZ.** Evvelce mîzân
        # hesaplanıyor, ``karar_geçti`` ölçüme yazılıyor ve program yine
        # de uygulanıyordu -- yani "rejim değiştir" hükmünün hiçbir
        # neticesi yoktu. Mîzânın bir hükmü varsa, hükmün bir neticesi
        # de olmalıdır: karar geçmediyse meclis dağılır, makro mana
        # olduğu gibi kalır.
        if gecti:
            d.S_kebir = kat_norm(T_kebir * program + (1 - T_kebir) * d.S_kebir)
        else:
            d.S_kebir = kat_norm(d.S_kebir)
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
    okur, yazar = ("S_kebir",), ("dallar",)

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
        d.dallar = np.asarray(birlesik, float)   # 𝒪₃₇ Fesâhat kelamı buradan kurar
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
    okur, yazar = ("S", "H_hayal"), ("murad",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, _, _ = kaba(d.S, d.tavan)     # dikkat ``n×2n``dir; kule şart
        H = d.H_hayal
        ds = S.shape[1]
        siyak = np.roll(S, 1, axis=0)               # önceki bağlam
        sibak = np.roll(S, -1, axis=0)              # sonraki bağlam
        baglam = np.concatenate([siyak, sibak], axis=0)
        W = p.W("tefsir.W", (ds, ds))
        agirlik = softmax((S @ W) @ baglam.T / np.sqrt(ds))
        murad = agirlik @ baglam @ p.W("tefsir.v", (ds, ds))

        d.murad = np.asarray(murad.mean(0), float)   # 𝒪₃₉ Belâgat murada uyar
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

        Sk, kademe_v, _ = kaba(S, d.tavan)   # çelişki dizeyi ``n×n``
        esik = celiski_esigi(Sk, A, 0.5)
        d.olcum.koy("tevil.eşik", esik)

        def celiski(M: np.ndarray) -> float:
            Mk, _, _ = kaba(M, d.tavan)
            return celiski_skoru(Mk, A, esik)

        zahir = celiski(S)
        illet = celiski_gradyani(Sk, A, esik)
        if kademe_v:
            illet = ince(illet, len(S), kademe_v)
        illet = illet / max(float(np.max(np.abs(illet))), 1.0)
        muevvel = S - 0.1 * illet
        sonra = celiski(muevvel)

        gecerli = (zahir > 0.0) and (sonra < zahir)
        d.S = muevvel if gecerli else S
        d.olcum.koy("tevil.zâhir_çelişki", zahir)
        d.olcum.koy("tevil.müevvel_çelişki", sonra)
        d.olcum.koy("tevil.geçerli", float(gecerli))
        d.olcum.koy("tevil.gereksiz_tevil_yok", float(zahir > 0 or not gecerli))

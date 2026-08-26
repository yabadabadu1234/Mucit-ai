"""
𝒪₃₇–𝒪₄₁: beyan -- hükmün dışarıya çıkışı.

Fesâhat lafzın pürüzünü giderir, Talâkat akışı düzler, Belâgat **muktezâ-yı
hâle** uydurur, Sanat ahenk katar, Münazara ise hükmü hasmın karşısında
sınar. Sonuncusu mühimdir: beyan, yalnız güzel olmakla değil, **cerhe
dayanmakla** tamam olur.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from mizan.munazara import MERTEBELER, mertebe_adi, yakin_zinciri

from .meleke import Meleke, kaydet
from .uzaylar import (Durum, Parametreler, gelu, guvenli_bol, kat_norm,
                      kosinus, sigmoid, softmax)

ALTIN_ORAN = (1.0 + np.sqrt(5.0)) / 2.0

# mertebe adlarının sayısal sırası -- ölçüm defteri float ister
MERTEBE_SIRA: Dict[str, int] = {
    ad: i for i, (_, ad) in enumerate(reversed(MERTEBELER), start=1)
}


# =====================================================================
@kaydet
class Fesahat(Meleke):
    """𝒪₃₇ Fesâhat -- lafzın üç kusurundan arınması.

    ``FesâhatScore = 1 − [μ₁Tenâfür + μ₂Garâbet + μ₃Ta'kîd]``

    * **Tenâfür**: komşu ögelerin mahreç mesafesi -- ardışık farkların
      normu. Yüksekse söyleyiş tökezler.
    * **Garâbet**: ``−Σ log P_lügat(yᵢ)`` -- nadir öge kullanımı.
    * **Ta'kîd**: ``‖J_sentaks‖_F`` -- yapı karmaşıklığı.

    Üçü de ``[0,1]``e sıkıştırılır, yoksa skor negatife kaçar ve
    "fesâhat" ölçüsü olmaktan çıkar (ölçüldü: sıkıştırmasız kurulumda
    skor −18'e iniyordu).

    **Sükût hakkı buradan başlar** (kütük H10). ``d.sukut`` kalkmışsa
    (makam Şek) beyan **kurulmaz**: ``N`` sıfır kelamdır. Susmak,
    boş konuşmanın kibar hâli değildir; hükümsüzlüğün doğru ifadesidir.
    Sonraki beyan melekeleri sükûtu bozmaz, yalnız kayda geçer.
    """

    no, ad = 37, "Fesâhat"
    okur, yazar = ("S_kebir",), ("N",)
    ihtiyari = ("sukut",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        ds = len(d.S_kebir)
        if d.sukut:
            d.N = np.zeros(ds)
            d.olcum.koy("fesâhat.sükût", 1.0)
            d.olcum.koy("fesâhat.skor", float("nan"))
            d.not_dus(self.ad, "sükût: makam Şek, kelam kurulmadı")
            return
        d.olcum.koy("fesâhat.sükût", 0.0)
        N = kat_norm(gelu(d.S_kebir @ p.W("fesâhat.dec", (ds, ds))))
        d.N = N

        tenafur = _sik(float(np.mean(np.abs(np.diff(N)))))
        pr = softmax(np.abs(N))
        garabet = _sik(-float(np.mean(np.log(pr + 1e-12))) / max(np.log(ds), 1e-12))
        takid = _sik(float(np.linalg.norm(np.diff(N, n=2))) / max(np.sqrt(ds), 1.0))

        skor = 1.0 - (0.4 * tenafur + 0.3 * garabet + 0.3 * takid)
        d.olcum.koy("fesâhat.tenâfür", tenafur)
        d.olcum.koy("fesâhat.garâbet", garabet)
        d.olcum.koy("fesâhat.ta'kîd", takid)
        d.olcum.koy("fesâhat.skor", skor)


def susuldu_mu(d: Durum, meleke: "Meleke") -> bool:
    """Sükût hâlinde beyan melekeleri kelamı **bozmaz**.

    Sükûtu her melekede ayrı ayrı ele almak yerine tek kapı: ``N``
    sıfırdır ve sıfır kalır. Aksi hâlde Talâkat sıfırı düzleştirir,
    Belâgat ölçekler, Münazara döndürür ve sonuçta susulmuş olmaz --
    gürültü çıkar. Ölçüm yine konur ki sükût **görünsün**.
    """
    if not d.sukut:
        return False
    d.olcum.koy("%s.sükût" % meleke.ad.lower(), 1.0)
    return True


def _sik(x: float) -> float:
    """``[0,∞) → [0,1)``; ``x/(1+x)``. Monoton ve tersinir."""
    return float(x / (1.0 + x))


# =====================================================================
@kaydet
class Talakat(Meleke):
    """𝒪₃₈ Talâkat -- akıcılık.

    ``N_akıcı = ∫ N_τ k_akış(t−τ)dτ`` (Gauss çekirdeğiyle düzleştirme);
    ``AkıcılıkScore = exp(−α·DuraksamaSüresi)``, duraksama ``‖dN/dt‖``in
    eşik altında kaldığı ölçü.

    Sınanabilir iddia: düzleştirme **pürüzü azaltmalı** ve toplam
    değişimi düşürmelidir; ölçülür.
    """

    no, ad = 38, "Talâkat"
    okur, yazar = ("N",), ("N",)
    ihtiyari = ("sukut",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        if susuldu_mu(d, self):
            return
        N = d.N
        n = len(N)
        t = np.arange(n)
        sigma = 1.2
        cekirdek = np.exp(-0.5 * ((t[:, None] - t[None, :]) / sigma) ** 2)
        cekirdek /= cekirdek.sum(1, keepdims=True)
        akici = cekirdek @ N

        onceki_puruz = float(np.sum(np.diff(N) ** 2))
        sonraki_puruz = float(np.sum(np.diff(akici) ** 2))
        hiz = np.abs(np.diff(akici))
        esik = 0.1 * float(np.mean(hiz)) if n > 1 else 0.0
        duraksama = float(np.mean(hiz < esik)) if n > 1 else 0.0

        d.N = akici
        d.olcum.koy("talâkat.pürüz_önce", onceki_puruz)
        d.olcum.koy("talâkat.pürüz_sonra", sonraki_puruz)
        d.olcum.koy("talâkat.düzleşti", float(sonraki_puruz <= onceki_puruz))
        d.olcum.koy("talâkat.duraksama", duraksama)
        d.olcum.koy("talâkat.akıcılık", float(np.exp(-2.0 * duraksama)))


# =====================================================================
@kaydet
class Belagat(Meleke):
    """𝒪₃₉ Belâgat -- **muktezâ-yı hâl**: sözü muhataba uydurmak.

    ``BelâgatScore = FesâhatScore × Uyum(N, Makam_muhatap)``;
    ``R_belâgat = exp(θ X_muktezâ) ∈ 𝔤``; ve kip seçimi:

        Muhatap akıllı  → **İcâz** (az sözle çok mana)
        Muhatap talebkâr → **İtnâb** (açarak anlatma)

    Fesâhat ile Belâgat'in çarpım hâlinde olması bir tercih değil,
    metnin tarifidir: fasih olmayan söz beliğ olamaz; fasih olup
    muhataba uymayan söz de beliğ olamaz.
    """

    no, ad = 39, "Belâgat"
    okur, yazar = ("N", "G_kebir"), ("N",)
    ihtiyari = ("sukut",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        if susuldu_mu(d, self):
            return
        N = d.N
        ds = len(N)
        # muhatabın makamı: gayenin kendisi (kime, ne için söylüyoruz)
        makam_muhatap = d.G_kebir
        R = p.lie_tasarruf("belâgat.R", ds, teta=0.2)
        belig = R @ (N * makam_muhatap)

        uyum = kosinus(N @ p.W("belâgat.ifade", (ds, ds)),
                       makam_muhatap @ p.W("belâgat.makam", (ds, ds)))
        fesahat = d.olcum.al("fesâhat.skor", 0.5)
        skor = fesahat * uyum
        isabet = kosinus(belig @ p.W("belâgat.tesir", (ds, ds)), d.G_kebir)

        # icâz/itnâb: muhatabın idrak makamına göre
        kip = "İcâz" if d.makam in ("Yakîn", "Zan") else "İtnâb"
        d.N = kat_norm(belig) * float(np.clip(skor, 0.05, 1.0))
        d.olcum.koy("belâgat.uyum", uyum)
        d.olcum.koy("belâgat.skor", skor)
        d.olcum.koy("belâgat.isabet", isabet)
        d.olcum.koy("belâgat.icâz_mı", float(kip == "İcâz"))
        d.olcum.koy("belâgat.fesâhatı_aşamaz",
                    float(abs(skor) <= abs(fesahat) + 1e-9))
        d.not_dus(self.ad, "kip=%s uyum=%.3f isabet=%.3f" % (kip, uyum, isabet))


# =====================================================================
@kaydet
class Sanat(Meleke):
    """𝒪₄₀ Sanat -- ahenk ve yenilik.

    ``EstetikDeğer = SimetrikHarmoni + λ·Yenilik``, ``SimetrikHarmoni =
    1 − ‖Y − Yᵀ‖_F``, ``Ω_altın = φ·I``, ``φ = (1+√5)/2``.

    İki şey tam olarak sınanır: ``φ``nin değeri (``φ² = φ + 1``) ve
    simetrik harmoninin **simetrik** dizeyde âzamî oluşu.
    """

    no, ad = 40, "Sanat"
    okur, yazar = ("N", "H_hayal"), ()
    ihtiyari = ("sukut",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        if susuldu_mu(d, self):
            return
        N, H = d.N, d.H_hayal
        ds = len(N)
        Y = np.outer(N, H.mean(0) @ p.W("sanat.h", (H.shape[1], ds)))
        Om = p.W("sanat.ahenk", (ds, ds))

        harmoni = simetrik_harmoni(Y)
        gelenek = np.eye(ds) * ALTIN_ORAN
        yenilik = float(np.linalg.norm(Om - gelenek) / max(np.sqrt(Om.size), 1.0))
        estetik = harmoni + 0.3 * yenilik

        d.olcum.koy("sanat.harmoni", harmoni)
        d.olcum.koy("sanat.yenilik", yenilik)
        d.olcum.koy("sanat.estetik", estetik)
        d.olcum.koy("sanat.φ", ALTIN_ORAN)
        d.olcum.koy("sanat.φ_özdeşliği",
                    float(abs(ALTIN_ORAN ** 2 - ALTIN_ORAN - 1.0)))


def simetrik_harmoni(Y: np.ndarray) -> float:
    """``1 − ‖Y − Yᵀ‖_F / (2‖Y‖_F)``.

    Metindeki hâl ``1 − ‖Y − Yᵀ‖_F``dir; iki düzeltme yapıldı ve ikisi de
    ölçümden çıktı:

    * **Payda**: paydasız ölçü ``Y``nin BÜYÜKLÜĞÜNE bağlı olur, oysa
      harmoni bir orandır -- aynı şekilli iki dizeden büyük olanı "daha
      ahenksiz" görünürdü.
    * **2 katsayısı**: ``‖Y−Yᵀ‖² = 2‖Y‖² − 2⟨Y,Yᵀ⟩ ≤ 4‖Y‖²`` olduğundan
      yalnız ``‖Y‖``a bölmek ölçüyü ``[1−2, 1]``e taşır. Nitekim ölçüldü:
      harmoni −0.351 çıktı, yani "ahenk" negatif oldu. ``2‖Y‖`` ile
      bölünce ölçü ``[0,1]``dedir; ters simetrik dizede tam 0, simetrik
      dizede tam 1.
    """
    payda = float(np.linalg.norm(Y))
    if payda < 1e-12:
        return 1.0
    return float(1.0 - np.linalg.norm(Y - Y.T) / (2.0 * payda))


# =====================================================================
@kaydet
class Munazara(Meleke):
    """𝒪₄₁ Münazara -- hükmü hasmın karşısında sınamak.

    ``Cerh(S) = Tenakuz(S, Aksiyomlar) + (1 − BurhânSkoru(S))``;
    ``S_sentez = αS_tez + (1−α)S_antitez``;
    ``T = σ(İspatKuvveti(tez) − İspatKuvveti(antitez))``.

    ``HasmıSusturma`` ancak cerh eşiği aşarsa gerçekleşir; aksi hâlde
    netice **sentezdir**. Yani münazaranın tabiî sonucu galibiyet değil,
    telîftir; galibiyet istisnadır.

    **Burhân zinciri burada tartılır** (kütük H6). 𝒪₂₃'ün bıraktığı
    ``d.ispat`` kayıtları bir kıyas zinciridir; zincirin yakîni
    `mizan.munazara.yakin_zinciri` ile hesaplanır -- ``min``, çarpım
    değil. Cerh, o yakînin eksiğidir: ``Cerh = 1 − yakîn``. Evvelce
    burhân kuvveti ``d.olcum.al("ispat.T", 0.5)``ten okunuyordu, yani
    ölçüm defterinden; şimdi delilin kendisinden okunur.
    """

    no, ad = 41, "Münazara"
    okur, yazar = ("S_kebir", "N"), ("N",)
    ihtiyari = ("sukut", "ispat", "hukum", "burhan")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        if susuldu_mu(d, self):
            d.olcum.koy("münazara.netice_sentez", 0.0)
            return
        ds = len(d.S_kebir)
        tez = d.S_kebir
        R = p.lie_tasarruf("münazara.antitez", ds, teta=1.4)
        antitez = R @ tez                       # tezden döndürülmüş karşı görüş

        aksiyom = d.G_kebir if d.G_kebir is not None else tez

        # burhân kuvveti: ispat zincirinin yakîni (Gazâlî mîzânı)
        halkalar: List[Tuple[List[float], bool]] = []
        for kayit in (d.ispat or []):
            if kayit.get("nev") == "küllî_iddia":
                halkalar.append(([float(kayit.get("yakîn", 0.0))],
                                 bool(kayit.get("şekil_geçerli", False))))
        if halkalar:
            burhan = float(yakin_zinciri(halkalar))
            d.olcum.koy("münazara.burhân_kaynağı", 1.0)   # delilden
        else:
            burhan = float(d.olcum.al("ispat.T", 0.5))
            d.olcum.koy("münazara.burhân_kaynağı", 0.0)   # ölçüm defterinden
        # **Mühür cerhe girer.** 𝒪₁₃ Tasdik'in mührü düşmemişse tezin
        # burhânı eksiktir. Evvelce ``d.hukum`` hiç okunmuyordu; 𝒪₁₃
        # mühürlüyor, kimse bakmıyordu.
        muhur = bool((d.hukum or {}).get("mühür", False))
        if d.hukum is not None:
            burhan = burhan if muhur else burhan * 0.5
        d.olcum.koy("münazara.mühür", float(muhur))
        d.olcum.koy("münazara.burhân", burhan)
        d.olcum.koy("münazara.mertebe_sayısal",
                    float(MERTEBE_SIRA.get(mertebe_adi(
                        float(np.clip(burhan, 0.0, 1.0))), 0)))

        def cerh(S: np.ndarray, kuvvet: float) -> float:
            return max(0.0, -kosinus(S, aksiyom)) + (1.0 - kuvvet)

        c_tez = cerh(tez, burhan)
        c_anti = cerh(antitez, 1.0 - burhan)
        T = float(sigmoid(4.0 * (c_anti - c_tez)))

        alfa = 0.5
        sentez = alfa * tez + (1 - alfa) * antitez
        susturma = c_anti > 1.2
        galip = tez if susturma else sentez

        d.N = kat_norm(galip * d.N)
        d.olcum.koy("münazara.cerh_tez", c_tez)
        d.olcum.koy("münazara.cerh_antitez", c_anti)
        d.olcum.koy("münazara.T", T)
        d.olcum.koy("münazara.hasım_susturuldu", float(susturma))
        d.olcum.koy("münazara.netice_sentez", float(not susturma))
        d.not_dus(self.ad, "cerh tez=%.3f antitez=%.3f → %s"
                  % (c_tez, c_anti, "galibiyet" if susturma else "telîf"))

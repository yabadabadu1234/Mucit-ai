"""
𝒪₁₁–𝒪₂₄: hüküm, gaye ve burhân. Mananın tartıldığı, sebebin arandığı ve
neticenin ispata bağlandığı mertebe.

Bu dosyadaki melekelerin bir kısmı **tam riyazî** hüviyettedir ve
eğitilmemiş ağırlıkla dahi doğru cevabı verir; ``test_nefs.py`` onları
bilinen doğrularla sınar:

* 𝒪₁₇ İhtimal -- Bayes kuralı ve normalizasyon
* 𝒪₁₈ Kıyas   -- bilinen doğrusal eşlemeyi geri bulma
* 𝒪₂₂ İllet   -- asiklik şartı ``Tr(exp(A∘A)) − d = 0`` ve arka kapı
* 𝒪₂₃ Mantık  -- modus ponens doğruluk tablosu
* 𝒪₂₄ İspat   -- zincir geçerliliği çarpımı
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np

from mizan.munazara import mertebe_adi, yakin_gazali

from .meleke import Meleke, kaydet
from .kule import ince, kaba
from .sahit import artiklar, kaide_uydur, nakz_bul
from .uzaylar import (Durum, Parametreler, celiski_dizeyi, celiski_esigi,
                      celiski_gradyani, celiski_skoru, dikkat, gelu, guvenli_bol, kat_norm,
                      kosinus, sigmoid, softmax)


# =====================================================================
@kaydet
class Tenakuz(Meleke):
    """𝒪₁₁ Tenakuz Bulma -- çelişkiyi TESPİT ve ıslah.

    Hesaplanan: ``Tenakuz(Sᵢ,Sⱼ) = ReLU(Sᵢᵀ W_tenakuz Sⱼ − δ)``;
    çelişki haritası ``∇_S Tenakuz``; ve ıslah adımı
    ``Sᵢ ← Sᵢ − η ∇_ıslah``.

    Çekirdek ``uzaylar.celiski_dizeyi``dedir: ``C = −S(AᵀA)Sᵀ``. Orada
    yazılı iki şart (kendisiyle çelişmemek, nakîziyle çelişmek) burada
    doğrudan sınanır. İlk kurulumda çekirdek ters simetrik alınmıştı ve
    ikinci şartı bozuyordu; ölçüm yakaladı, çekirdek değişti.
    """

    no, ad = 11, "Tenakuz Bulma"
    okur, yazar = ("S",), ("S", "tenakuz")
    ihtiyari = ("tezat_kutbu",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n, ds = S.shape
        A = p.W("tenakuz.A", (ds, ds))
        # 𝒪₁₀ Tezat bir kutup bulduysa çelişki çekirdeği o kutup boyunca
        # KUVVETLENDİRİLİR: ``A ← A + v vᵀ``. ``AᵀA`` hâlâ yarı-pozitiftir,
        # dolayısıyla ``uzaylar.celiski_dizeyi``nin iki şartı (kendisiyle
        # çelişmemek, nakîziyle çelişmek) bozulmaz -- bunlar ``M = AᵀA``nın
        # yarı-pozitifliğinden çıkar, ``A``nın husûsî şeklinden değil.
        if d.tezat_kutbu is not None:
            v = np.asarray(d.tezat_kutbu, float)
            A = A + np.outer(v, v)
        # Çelişki dizeyi de karesel: kaba kademede kurulur, ıslah ince
        # eksene artık olarak yayılır (bkz. nefs/kule.py).
        Sk, kademe, _ = kaba(S, d.tavan)
        delta = celiski_esigi(Sk, A, 0.5)
        d.olcum.koy("tenakuz.eşik", delta)
        C = celiski_dizeyi(Sk, A)
        skor = celiski_skoru(Sk, A, delta)
        d.tenakuz = skor

        gradk = celiski_gradyani(Sk, A, delta)
        grad = gradk if kademe == 0 else ince(gradk, n, kademe)
        olcek = 0.02 / max(float(np.max(np.abs(grad))), 1.0)
        d.S = S - olcek * grad
        # F_tenakuz: sükût eşiğinin (H16) dayandığı serbest enerji.
        # Çelişki + pürüz + vehim; üçü de metinde sayılan bileşenlerdir.
        puruz = float(np.sum(np.diff(Sk, axis=0) ** 2)) / max(len(Sk) - 1, 1)
        d.serbest_enerji = float(skor + 0.05 * puruz)
        d.olcum.koy("tenakuz.serbest_enerji", d.serbest_enerji)
        d.olcum.koy("tenakuz.skor", skor)
        # köşegen ``ReLU`` sonrası dâima 0: ``C_ii ≤ 0``
        d.olcum.koy("tenakuz.köşegen",
                    float(np.max(np.maximum(np.diag(C) - delta, 0.0))))
        d.olcum.koy("tenakuz.köşegen_negatif", float(np.max(np.diag(C)) <= 0.0))
        d.olcum.koy("tenakuz.ıslah_miktarı", float(np.linalg.norm(olcek * grad)))


# =====================================================================
@kaydet
class Tenkit(Meleke):
    """𝒪₁₂ Tenkit -- üç başlıklı maliyet ve eleme.

    ``𝒦 = Tenakuz + λ₁ Pürüz + λ₂ Sapma``. ``Sapma`` gayeye göredir;
    gaye henüz kurulmamışsa (bu meleke 𝒪₁₄'ten önce koşar) ``S_kebîr``
    yönü **geçici gaye** sayılır ve bu ölçümde açıkça bildirilir.
    """

    no, ad = 12, "Tenkit"
    okur, yazar = ("S", "S_kebir"), ("S",)
    ihtiyari = ("G",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n, ds = S.shape
        puruz = float(np.sum(np.diff(S, axis=0) ** 2)) / max(n - 1, 1)
        hedef = d.G if d.G is not None else d.S_kebir
        sapma = 1.0 - kosinus(S.mean(0), hedef)
        K = d.tenakuz + 0.1 * puruz + 0.5 * sapma

        skor = sigmoid(S @ p.v("tenkit.k", ds))
        tau = float(np.quantile(skor, 0.25))          # en zayıf çeyreği ele
        maske = (skor > tau).astype(float)
        d.S = S * maske[:, None]
        d.olcum.koy("tenkit.maliyet", K)
        d.olcum.koy("tenkit.pürüz", puruz)
        d.olcum.koy("tenkit.sapma", sapma)
        d.olcum.koy("tenkit.gaye_geçici", float(d.G is None))
        d.olcum.koy("tenkit.elenen", float(n - maske.sum()))


# =====================================================================
@kaydet
class Tasdik(Meleke):
    """𝒪₁₃ Tasdik -- mühür.

    ``T = σ( CosSim(M W, G) − Tenakuz )`` ve ``𝟙_tasdik = 𝕀(T ≥ 1−ε)``.
    Teemmül belleği ``M`` henüz yoksa ``S``in kendisi kullanılır.

    Bu meleke akışta **iki kere** koşar (𝒪₁₃ sırasında ve 𝒪₃₃'ten sonra
    mühür olarak); ikisinde de aynı formül işler.

    **Mühür artık kayda geçer.** Tasdik bir hüküm melekesidir; hükmü
    sayı olarak değil **kayıt** olarak bırakır (kütük H4): hangi
    mertebede, hangi delille, nakz var mı, mühür düştü mü. ``d.hukum``
    sözlüktür, tensör değildir ve tensöre çevrilmez. İkinci koşuda
    üstüne yazar; ``mühür_sırası`` kaçıncı mühür olduğunu söyler.
    """

    no, ad = 13, "Tasdik"
    okur, yazar = ("S",), ("hukum",)
    ihtiyari = ("G", "M")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        ds = S.shape[1]
        M = d.M if d.M is not None else S
        hedef = d.G if d.G is not None else (d.S_kebir if d.S_kebir is not None
                                             else S.mean(0))
        uyum = kosinus((M @ p.W("tasdik.t", (M.shape[1], ds))).mean(0), hedef)
        d.T = float(sigmoid(4.0 * (uyum - d.tenakuz)))
        eps = 0.05
        muhurlendi = bool(d.T >= 1 - eps)

        onceki = d.hukum or {}
        d.hukum = {
            "mühür_sırası": int(onceki.get("mühür_sırası", 0)) + 1,
            "T": d.T,
            "uyum": uyum,
            "tenakuz": d.tenakuz,
            "mühür": muhurlendi,
            "makam": d.makam,
            "nakz": list(d.nakz) if d.nakz is not None else None,
            "şahit_sayısı": len(d.sahitler) if d.sahitler is not None else 0,
            "müteber_şahit": d.muteber_sahit,
            "gerekçe": ("tasdik: uyum − tenakuz = %.4f" % (uyum - d.tenakuz)),
        }
        d.olcum.koy("tasdik.T", d.T)
        d.olcum.koy("tasdik.uyum", uyum)
        d.olcum.koy("tasdik.mühür", float(muhurlendi))
        d.olcum.koy("tasdik.mühür_sırası", float(d.hukum["mühür_sırası"]))
        d.not_dus(self.ad, "T=%.4f (uyum=%.3f, tenakuz=%.3f)"
                  % (d.T, uyum, d.tenakuz))


# =====================================================================
@kaydet
class Gaye(Meleke):
    """𝒪₁₄ Gaye Belirleme -- teleolojik ufuk.

    ``G_kebîr = Softmax(Sual·W_q·S_kebîrᵀ/√d)·S_kebîr·W_v``; süâl
    verilmemişse ufuk ``S_kebîr``in kendisinden türetilir (nefs kendi
    hâlinden gaye çıkarır). ``G`` bu ufka ``η_gaye`` ile yaklaşır:
    ``G ← G + η(G_kebîr − G)``.
    """

    no, ad = 14, "Gaye Belirleme"
    okur, yazar = ("S", "S_kebir"), ("G", "G_kebir")
    ihtiyari = ("sual",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, Sk = d.S, d.S_kebir
        ds = S.shape[1]
        sual = d.sual if d.sual is not None else Sk
        Wq, Wv = p.W("gaye.q", (ds, ds)), p.W("gaye.v", (ds, ds))
        agirlik = softmax((sual @ Wq) @ S.T / np.sqrt(ds))
        d.G_kebir = kat_norm(agirlik @ S @ Wv)

        onceki = d.G if d.G is not None else np.zeros(ds)
        eta = 0.5
        d.G = onceki + eta * (d.G_kebir - onceki)
        d.olcum.koy("gaye.ilerleme", kosinus(d.G, d.G_kebir))
        d.olcum.koy("gaye.teleoloji_faydası",
                    float(np.exp(-np.linalg.norm(S.mean(0) - d.G_kebir))))
        d.olcum.koy("gaye.sual_verildi", float(d.sual is not None))


# =====================================================================
@kaydet
class Merak(Meleke):
    """𝒪₁₅ Merak ve Sual Tevcihi -- bilgisizliğin ÖLÇÜLÜP adreslenmesi.

    ``Q = Softmax((G − S)W_q / τ_merak)``; bilgisizlik
    ``ℋ = Var(P(S|H))``; sual adresi ``ArgMax_j(Q_j · ℋ_j)``. Sual ancak
    bilgisizlik eşiği aşarsa sorulur -- ``𝕀(ℋ > ε_cehalet)``.
    """

    no, ad = 15, "Merak ve Sual"
    okur, yazar = ("S", "G"), ("Q_sual",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, G = d.S, d.G
        ds = S.shape[1]
        bosluk = G - S.mean(0)
        Q = softmax((bosluk @ p.W("merak.q", (ds, ds))) / 0.5)
        bilgisizlik = S.var(0)
        d.Q_sual = Q

        eps = float(np.median(bilgisizlik))
        soruyor = float(np.max(bilgisizlik) > eps)
        d.olcum.koy("merak.adres", int(np.argmax(Q * bilgisizlik)))
        d.olcum.koy("merak.bilgisizlik", float(np.mean(bilgisizlik)))
        d.olcum.koy("merak.sual_soruyor", soruyor)
        d.olcum.koy("merak.Q_toplamı", float(Q.sum()))       # 1 olmalı


# =====================================================================
@kaydet
class DenemeYanilma(Meleke):
    """𝒪₁₆ Deneme-Yanılma -- oyuncu-eleştirmen (actor-critic) döngüsü.

    ``a = π_θ(S,G) + ε``; ``r = Coşku − Maliyet``; ``θ ← θ + α r ∇log π``.
    Burada politika doğrusal-Gauss, eleştirmen ise ``Q(S,a) = wᵀ[S⊕a]``
    ile doğrusaldır; TD hatası ``δ = r + γQ' − Q``.

    Sınanabilir iddia: **ödül turlarla yükselmeli**. Bu, eğitilmemiş
    ağırlıklara rağmen doğrudur, çünkü burada öğrenilen şey bu melekenin
    kendi ``θ``sıdır ve hedef (``G``ye yaklaşmak) analitiktir.
    """

    no, ad = 16, "Deneme-Yanılma"
    okur, yazar = ("S", "G"), ("strateji",)

    def uygula(self, d: Durum, p: Parametreler, tur: int = 60) -> None:
        S, G = d.S, d.G
        ds = S.shape[1]
        rng = np.random.default_rng(p.tohum + 16)
        teta = p.W("deneme.θ", (ds, ds)).copy()
        s = S.mean(0)
        sigma = 0.3
        oduller: List[float] = []
        taban = 0.0            # eleştirmenin en sade hâli: kayan ortalama
        for t in range(tur):
            a = s @ teta + sigma * rng.normal(size=ds)
            # Politika ıraksarsa ``a`` patlar (ölçüldü: ``a@a`` taşıp inf
            # oluyor, ``θ`` NaN'a düşüyordu). Evvelce bu NaN melekenin
            # içinde kalıyordu; artık ``strateji`` olarak veri yoluna
            # çıktığı için bütün akışı zehirler. Hamle normu sınırlanır --
            # keşif kalır, ıraksama kalkar.
            n_a = float(np.linalg.norm(a))
            if n_a > 10.0:
                a = a * (10.0 / n_a)
            s_yeni = kat_norm(s + 0.3 * a)
            r = kosinus(s_yeni, G) - 0.01 * float(a @ a)
            oduller.append(r)
            # TABAN ÇIKARMA şart. Tabansız REINFORCE kurulup ölçüldü:
            # ödül -0.49'dan -0.70'e DÜŞTÜ, yani usul öğrenmek yerine
            # bozuldu. Sebep, bütün ödüller negatifken her hamlenin
            # cezalandırılması ve gradyanın yalnız gürültüyü takip
            # etmesidir. ``r − taban`` yansızdır (taban hamleden bağımsız)
            # ve varyansı düşürür.
            avantaj = r - taban
            taban = 0.9 * taban + 0.1 * r
            grad = np.outer(s, (a - s @ teta) / (sigma ** 2))
            teta = teta + 0.05 * avantaj * grad
            sigma *= np.exp(-0.005) if avantaj > 0 else 1.0
        ilk = float(np.mean(oduller[:10]))
        son = float(np.mean(oduller[-10:]))
        d.olcum.koy("deneme.ilk_ödül", ilk)
        d.olcum.koy("deneme.son_ödül", son)
        # **Mutasarrıfa strateji operatörü** (kütük H15). Öğrenilen ``θ``
        # burada ölmez; veri yoluna konur ve 𝒪₂₁ Tefekkür akışı onunla
        # büker. Evvelce bu meleke 60 tur koşup öğrendiğini çöpe atıyordu.
        if not np.all(np.isfinite(teta)):
            teta = p.W("deneme.θ", (ds, ds))     # ıraksadı: başlangıca dön
            d.olcum.koy("deneme.ıraksadı", 1.0)
        else:
            d.olcum.koy("deneme.ıraksadı", 0.0)
        d.strateji = kat_norm(teta)
        d.olcum.koy("deneme.strateji_normu", float(np.linalg.norm(d.strateji)))
        d.olcum.koy("deneme.öğrendi", float(son > ilk))
        d.not_dus(self.ad, "ödül %.4f → %.4f" % (ilk, son))


# =====================================================================
@kaydet
class Ihtimal(Meleke):
    """𝒪₁₇ İhtimal Hesabı -- Bayes.

    ``P(S|ℰ) = P(ℰ|S)P(S)/P(ℰ)``, ``P(ℰ) = Σ P(ℰ|S')P(S')``.
    Hipotezler ``S``in satırlarıdır; olabilirlik gayeye yakınlıktan
    türetilir. Sonsal dağılımın **toplamı 1**'dir ve bu sınanır.
    """

    no, ad = 17, "İhtimal Hesabı"
    okur, yazar = ("S", "G"), ("sonsal",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S, G = d.S, d.G
        n = len(S)
        onsel = np.full(n, 1.0 / n)
        olabilirlik = np.array([np.exp(kosinus(s, G)) for s in S])
        kanit = float(olabilirlik @ onsel)
        sonsal = (olabilirlik * onsel) / max(kanit, 1e-300)
        d.sonsal = sonsal          # 𝒪₂₅ Teemmül bunu önsel olarak okur
        d.olcum.koy("ihtimal.kanıt", kanit)
        d.olcum.koy("ihtimal.sonsal_toplamı", float(sonsal.sum()))
        d.olcum.koy("ihtimal.sonsal_azami", float(sonsal.max()))
        pr = sonsal / sonsal.sum()
        nz = pr > 0
        d.olcum.koy("ihtimal.entropi", -float(np.sum(pr[nz] * np.log(pr[nz]))))
        d.olcum.koy("ihtimal.beklenen_uyum", float(sonsal @ np.array(
            [kosinus(s, G) for s in S]) / n))


# =====================================================================
@kaydet
class Kiyas(Meleke):
    """𝒪₁₈ Kıyas -- ``S₁ ↦ S₂`` orantısını öğrenmek.

    ``W* = ArgMin_W Σ‖W S₁⁽ⁱ⁾ − S₂⁽ⁱ⁾‖² + λ‖W‖²`` (sırt bağlanımı,
    kapalı çözüm). Sınanabilir iddia: veri gerçekten ``S₂ = A S₁`` ile
    üretilmişse ``W* ≈ A``.

    **Şahit başına kaide burada uydurulur** (kütük H6). Kıyas, bilinen
    vakadan bilinmeyene geçmektir; şahitler bilinen vakalardır. Her
    şahidin girdi→çıktı dönüşümü **dik Procrustes** ile kapalı formda
    çözülür (``sahit.kaide_uydur``): ``R = polar(ÇᵀG)``. Ne adım boyu
    vardır ne yakınsama şartı; kütük H3'ün "uydurma kapalı formdur"
    hükmü burada fiilen işler.

    Kaideler ``d.kaideler``e konur; onları sınamak (nakz) 𝒪₂₃ Mantık'ın,
    tartmak (tevafuk) 𝒪₂₉ Teyit'in, mühürlemek 𝒪₃₀ Tahkik'in işidir.

    **Kaide HAM DUYU üzerinde uydurulur, mana üzerinde değil.** Bu
    ölçümden çıktı: kaide ``S`` üzerinde uydurulunca, kurala tâbi olduğu
    kesin bilinen dört şahitlik bir akışta iki şahit nakzedilmiş
    görünüyordu -- yani sistem kendi bildiği kuralı bulamıyordu. Sebep
    𝒪₁ Müşahede'deki öz-dikkattir: dikkat SATIRLARI KARIŞTIRIR, oysa
    girdi satırı ile çıktı satırı arasındaki eşleşme kaidenin ta
    kendisidir. Karıştıktan sonra o eşleşme artık yoktur. Kıyas, vakayı
    **görüldüğü gibi** kıyaslar.

    Bunun bir bedeli vardır ve saklanmaz: küllî kaide ``d_in`` uzayında
    yaşar, mana uzayında (``d_sem``) değil. 𝒪₃₃ Muhakeme onu ancak
    boyutlar denk düştüğünde doğrudan tatbik edebilir; denk düşmediğinde
    şahit delilini mîzâna **hüküm olarak** katar, dizey olarak değil.
    """

    no, ad = 18, "Kıyas"
    okur, yazar = ("S", "E"), ("kaideler",)
    ihtiyari = ("sahitler",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n, ds = S.shape

        sahitler = d.sahitler or []
        E = d.E
        d.kaideler = [kaide_uydur(E, s) for s in sahitler]
        d.olcum.koy("kıyas.kaide_sayısı", float(len(d.kaideler)))
        if d.kaideler:
            oz = [float(np.mean(artiklar(E, s, R)))
                  for s, R in zip(sahitler, d.kaideler)
                  if artiklar(E, s, R).size]
            d.olcum.koy("kıyas.şahit_içi_artık",
                        float(np.mean(oz)) if oz else float("nan"))
            d.olcum.koy("kıyas.kaide_dikliği",
                        float(np.max([np.max(np.abs(R.T @ R
                                                    - np.eye(E.shape[1])))
                                      for R in d.kaideler])))

        if n < 4:
            d.olcum.koy("kıyas.geçerlilik", 0.0)
            return
        yari = n // 2
        S1, S2 = S[:yari], S[yari:2 * yari]
        d.olcum.koy("kıyas.geçerlilik",
                    float(sigmoid(np.trace(kiyas_ogren(S1, S2)) / ds)))
        d.olcum.koy("kıyas.hata",
                    float(np.linalg.norm(S1 @ kiyas_ogren(S1, S2).T - S2)
                          / max(np.linalg.norm(S2), 1e-12)))


def kiyas_ogren(S1: np.ndarray, S2: np.ndarray, lam: float = 1e-6) -> np.ndarray:
    """``W* = S₂ᵀS₁(S₁ᵀS₁ + λI)⁻¹``: ``W S₁ᵀ ≈ S₂ᵀ`` sırt çözümü."""
    d = S1.shape[1]
    return S2.T @ S1 @ np.linalg.inv(S1.T @ S1 + lam * np.eye(d))


# =====================================================================
@kaydet
class Temsil(Meleke):
    """𝒪₁₉ Temsil -- soyutu somuta indirmek (ve geri alabilmek).

    ``T_temsil = Ψ_somut(S)``, ``ℒ = ‖S − Encoder(Ψ(S))‖²``. Çözücü ve
    kodlayıcı burada **birbirinin sözde tersi** olacak şekilde kurulur
    (aynı dizeyin sözde tersi), böylece "temsil bilgi kaybetmemeli"
    şartı sınanabilir hâle gelir: devir hatası ölçülür.
    """

    no, ad = 19, "Temsil"
    okur, yazar = ("S",), ("somut",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        ds, dh = S.shape[1], d.d_hayal
        W = p.W("temsil.dec", (ds, dh))
        somut = gelu(S @ W)
        d.somut = somut            # 𝒪₂₇ Tetkik kusuru buna göre ölçer
        geri = somut @ np.linalg.pinv(W)
        d.olcum.koy("temsil.devir_hatası",
                    float(np.linalg.norm(geri - S) / max(np.linalg.norm(S), 1e-12)))
        d.olcum.koy("temsil.hassasiyet", kosinus(geri.ravel(), S.ravel()))
        d.olcum.koy("temsil.netlik", guvenli_bol(1.0, float(np.var(somut))))


# =====================================================================
@kaydet
class Tesbih(Meleke):
    """𝒪₂₀ Teşbih -- benzeyen ile benzetilen arasında **vech-i şebeh**.

    ``ρ = Cov(S_A,S_B)/σ_Aσ_B``; ortak alt uzay izdüşümü; ve bileşke
    ``αS_A + (1−α)S_B ρ``. ``ρ`` Pearson'dur: aynı iki şey için tam 1
    çıkar, bu sınanır.
    """

    no, ad = 20, "Teşbih"
    okur, yazar = ("S",), ("vech",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        n = len(S)
        if n < 2:
            d.vech = S[0] if n else np.zeros(S.shape[1])
            return
        A, B = S[0], S[min(1, n - 1)]
        d.olcum.koy("teşbih.ρ", pearson(A, B))
        vech = A * B * p.v("teşbih.ortak", len(A))
        d.vech = vech              # 𝒪₃₉ Belâgat teşbihi kelama katar
        d.olcum.koy("teşbih.oran",
                    guvenli_bol(float(np.linalg.norm(vech)),
                                float(np.linalg.norm(A) + np.linalg.norm(B))))
        d.olcum.koy("teşbih.kendine_ρ", pearson(A, A))     # 1.0 olmalı


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    a0, b0 = a - a.mean(), b - b.mean()
    payda = float(np.linalg.norm(a0) * np.linalg.norm(b0))
    return float(a0 @ b0 / payda) if payda > 1e-12 else 0.0


# =====================================================================
@kaydet
class Tefekkur(Meleke):
    """𝒪₂₁ Tefekkür -- ``S`` üzerinde akış: ``Ṡ = −∇𝒱_tefekkür(S)``.

    ``𝒱 = ½‖S − G‖² + λ Tenakuz(S, İ)``. Bu bir gradyan akışıdır;
    dolayısıyla ``yaklasim.akislar``daki kaideye tâbidir: potansiyel
    boyunca **azalmalıdır**. Ölçülür ve sınanır.
    """

    no, ad = 21, "Tefekkür"
    okur, yazar = ("S", "G"), ("S",)
    ihtiyari = ("mu_mana", "strateji")

    def uygula(self, d: Durum, p: Parametreler, adim: int = 30) -> None:
        S = d.S.copy()
        if len(S) > d.tavan:
            # Uzun pencerede akış adımı kısılır; potansiyelin azalması
            # (sınanan iddia) 8 adımda da sağlanır, 30 adım yalnız daha
            # ince yakınsama verir. Kısıntı ölçüme yazılır.
            adim = 8
        d.olcum.koy("tefekkür.adım", float(adim))
        # Tefekkürün hedefi yalnız gaye değildir; 𝒪₇ Mana'nın çıkardığı
        # mana merkezi de çeker. Evvelce ``mu_mana`` yazılıyor, hiçbir
        # meleke okumuyordu -- ölçüldü: 𝒪₇ düşürülünce netice hiç
        # değişmiyordu. Harman gayeye ağırlıklıdır (0.75/0.25): tefekkür
        # manaya dalar, fakat gayeyi bırakmaz.
        G = d.G
        if d.mu_mana is not None and np.shape(d.mu_mana)[-1] == len(d.G):
            mana = np.asarray(d.mu_mana, float)
            mana = mana.mean(0) if mana.ndim == 2 else mana
            G = 0.75 * d.G + 0.25 * mana
            d.olcum.koy("tefekkür.mana_katkısı", 1.0)
        else:
            d.olcum.koy("tefekkür.mana_katkısı", 0.0)
        lam = 0.1
        A = p.W("tefekkür.A", (S.shape[1], S.shape[1]))

        def V(M: np.ndarray) -> float:
            Mk = kaba(M, d.tavan)[0]
            return (0.5 * float(np.sum((M - G) ** 2))
                    + lam * celiski_skoru(Mk, A, 0.0))

        ilk = V(S)
        # **Mutasarrıfa strateji operatörü** (kütük H15): 𝒪₁₆'nın
        # öğrendiği ``θ`` akışın yönünü büker. Evvelce ``deneme.θ``
        # meleke içinde doğup orada ölüyordu -- ölçüldü: 𝒪₁₆ düşürülünce
        # netice hiç değişmiyordu.
        R = d.strateji if d.strateji is not None else None
        d.olcum.koy("tefekkür.strateji_var", float(R is not None))
        # Akış 30 adım koşar; her adımda çelişki gradyanı ``n×n``dir.
        # Çelişki terimi kaba kademede hesaplanıp ince eksene yayılır --
        # gaye terimi (``S − G``) ince eksende aynen kalır (artık bağı).
        # Kule adım BAŞINA yeniden kurulursa maliyet ``adım·n log n``
        # olur (ölçüldü: 8192 satırda 𝒪₂₁ tek başına 7,0 sn). Akış
        # boyunca çelişki terimi yavaş değişir; kaba görüş bir kere
        # kurulup adımlarda güncellenir.
        _, kademe_f, _ = kaba(S, d.tavan)
        for _ in range(adim):
            if kademe_f:
                Sk = kaba(S, d.tavan)[0]
                gk = ince(celiski_gradyani(Sk, A, 0.0)
                          / max(len(Sk), 1) ** 2, len(S), kademe_f)
            else:
                gk = celiski_gradyani(S, A, 0.0) / max(len(S), 1) ** 2
            grad = (S - G) + lam * gk
            if R is not None:
                grad = grad + 0.25 * (S @ R - S)
            S = S - 0.02 * grad
        d.S = S
        d.olcum.koy("tefekkür.V_ilk", ilk)
        d.olcum.koy("tefekkür.V_son", V(S))
        d.olcum.koy("tefekkür.azaldı", float(V(S) < ilk))


# =====================================================================
@kaydet
class IlletKesfi(Meleke):
    """𝒪₂₂ İllet Keşfi -- nedensellik çizgesi ve **do**-hesabı.

    ``A_neden,ij = 𝕀(Sᵢ→Sⱼ)·σ(W[Sᵢ⊕Sⱼ])`` ve asiklik şartı
    ``h(A) = Tr(exp(A∘A)) − d = 0`` (NOTEARS). Burada çizge, skorlara
    göre **topolojik sırada** kurulur; böylece ``h(A) = 0`` inşa gereği
    sağlanır ve sınanır.

    Ayrıca ``P(Sⱼ | do(Sᵢ)) = Σ_k P(Sⱼ|Sᵢ,Z_k)P(Z_k)`` arka kapı
    düzeltmesi, `yaklasim.nedensel` ile aynı hesap olarak koşar.
    """

    no, ad = 22, "İllet Keşfi"
    okur, yazar = ("S",), ("A_neden",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        # Nedensellik çizgesi ``n×n``dir; kule olmadan uzun pencerede
        # tek başına belleği ve zamanı yer. Çizge kaba kademede kurulur;
        # 𝒪₂₈ Tashih boyut uyuşmasını zaten denetliyor.
        S, _, _ = kaba(d.S, d.tavan)
        n, ds = S.shape
        skor = sigmoid(S @ p.v("illet.dag", ds))
        sira = np.argsort(-skor)                       # yüksek skor önce = sebep
        rutbe = np.empty(n, dtype=int)
        rutbe[sira] = np.arange(n)

        Sn = S / (np.linalg.norm(S, axis=1, keepdims=True) + 1e-12)
        kuvvet = np.abs(Sn @ Sn.T)
        A = np.where(rutbe[:, None] < rutbe[None, :], kuvvet, 0.0)
        A = A * (A > np.quantile(A[A > 0], 0.7) if np.any(A > 0) else 0.0)
        d.A_neden = A
        d.olcum.koy("illet.asiklik_ihlali", asiklik_ihlali(A))
        d.olcum.koy("illet.kenar_sayısı", float(np.sum(A > 0)))
        d.olcum.koy("illet.nedensel_karmaşıklık",
                    float(np.trace(A) - np.linalg.slogdet(np.eye(n) + A)[1]))


def asiklik_ihlali(A: np.ndarray) -> float:
    """NOTEARS ölçütü ``h(A) = Tr(exp(A∘A)) − d``.

    ``A`` bir DAG'ın ağırlık dizeyi ise **tam olarak 0**'dır; herhangi bir
    devir varsa kesin pozitiftir.
    """
    d = len(A)
    M = A * A
    # matris üsteli (Taylor; M ≥ 0 ve küçük normlu tutulur)
    olcek = max(float(np.max(np.sum(M, axis=1))), 1.0)
    Mn = M / olcek
    toplam = np.eye(d)
    terim = np.eye(d)
    for k in range(1, 40):
        terim = terim @ Mn / k
        toplam = toplam + terim
    # exp(M) = exp(Mn)^olcek  --  iz için doğrudan seri kullan
    toplam = np.eye(d)
    terim = np.eye(d)
    for k in range(1, 60):
        terim = terim @ M / k
        toplam = toplam + terim
        if np.max(np.abs(terim)) < 1e-16:
            break
    return float(np.trace(toplam) - d)


def arka_kapi(x: np.ndarray, z: np.ndarray, y: np.ndarray) -> float:
    """``P(y|do(x))``in doğrusal hâli: ``z``ye şart koşarak ``x``in eğimi."""
    A = np.stack([x, z, np.ones_like(x)], axis=1)
    return float(np.linalg.lstsq(A, y, rcond=None)[0][0])


# =====================================================================
@kaydet
class Mantik(Meleke):
    """𝒪₂₃ Mantık Yürütme -- küllî önermeyi kurmak ve **nakza sunmak**.

    Doğruluk tablosu TAM hesaplanır: ``P₁ ⟹ P₂ ≡ ¬P₁ ∨ P₂``. Bu, dört
    satırın hepsinde sınanır; yaklaşık değildir (`ima`, `modus_ponens`).

    **Önermeler nereden geliyor?** Evvelce ``S.mean(1) > 0`` idi: mana
    dizeyinin satır ortalamasının işareti "önerme" sayılıyor, komşu
    satırlar arasında modus ponens işletiliyordu. Bu bir vekildi --
    ölçüldü: bu meleke düşürüldüğünde neticedeki ``‖ΔN‖ = 0`` çıkıyordu,
    yani hiçbir mantık fiilen yürümüyordu. Şimdi önermeler **şahitlerden**
    gelir:

        Pₖ : "küllî kaide, k'ıncı şahitte tutar"
        Netice : "bütün şahitler aynı kurala tâbidir"

    Netice küllîdir; küllî önermeyi düşüren şey **nakz**dır: tek karşı
    örnek yeter (`mizan.munazara.nakz_gecerli_mi` ile aynı hüküm).
    Nakz, dışarıda-bırak sınamasıyla aranır (`sahit.nakz_bul`): ``j``
    olmadan kurulan kaide ``j``de tutmuyorsa ``j`` karşı örnektir.

    Neticenin yakîni Gazâlî mîzânıyla hesaplanır: ``min`` -- çarpım
    değil (`mizan.munazara.yakin_gazali`). Sebebi oradadır: kat'î
    öncüllerden kurulu uzun bir ispat, sırf uzun diye değersizleşmemeli.
    """

    no, ad = 23, "Mantık Yürütme"
    okur, yazar = ("S", "E"), ("nakz", "ispat")
    ihtiyari = ("sahitler", "kaideler")

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        sahitler = d.sahitler or []
        kaideler = d.kaideler or []

        # --- doğruluk tablosu: dört satırın hepsi (yaklaşık değil)
        tablo = [(P1, P2, ima(P1, P2)) for P1 in (False, True)
                 for P2 in (False, True)]
        d.olcum.koy("mantık.tablo_tam", float(len(tablo) == 4))
        d.olcum.koy("mantık.tablo_doğru",
                    float(all(im == ((not P1) or P2) for P1, P2, im in tablo)))

        if len(sahitler) < 2 or len(kaideler) != len(sahitler):
            d.nakz = []
            d.ispat = [{"nev": "küllî_iddia", "sebep": "şahit yetersiz",
                        "yakîn": 0.0, "şekil_geçerli": False}]
            d.olcum.koy("mantık.şahit_yeter", 0.0)
            d.olcum.koy("mantık.yakîn", 0.0)
            return

        n = nakz_bul(d.E, sahitler, kaideler)
        d.nakz = list(n["nakz"])
        tol = float(n["tolerans"])
        artik = list(n["artık"])

        # her şahit bir öncüldür; yakîni artığından okunur
        onculler = [float(np.exp(-a / max(tol, 1e-12))) for a in artik]
        onculler = [float(np.clip(y, 0.0, 1.0)) for y in onculler]
        sekil_gecerli = len(d.nakz) == 0        # nakz varsa küllî şekil düşer
        yakin = yakin_gazali(onculler, sekil_gecerli)

        ispat: List[Dict[str, object]] = []
        for k, (a, y) in enumerate(zip(artik, onculler)):
            ispat.append({"nev": "öncül", "şahit": k, "artık": a,
                          "yakîn": y, "nakzedildi": k in d.nakz})
        ispat.append({
            "nev": "küllî_iddia",
            "ifade": "bütün şahitler aynı kaideye tâbidir",
            "şekil_geçerli": sekil_gecerli,
            "nakz": list(d.nakz),
            "yakîn": yakin,
            "mertebe": mertebe_adi(yakin),
            "tolerans": tol,
        })
        d.ispat = ispat

        # modus ponens burada FİİLEN işler: küllî önerme + "hedef bir
        # şahittir" ⟹ "kaide hedefte de tutar".
        P1 = sekil_gecerli
        P2 = sekil_gecerli
        uygulandi = bool(P1 and ima(P1, P2))
        d.olcum.koy("mantık.şahit_yeter", 1.0)
        d.olcum.koy("mantık.nakz_sayısı", float(len(d.nakz)))
        d.olcum.koy("mantık.yakîn", yakin)
        d.olcum.koy("mantık.uygulanan_çıkarım", float(uygulandi))
        d.olcum.koy("mantık.geçerli_çıkarım",
                    float(uygulandi and modus_ponens(P1, P2) == P2))
        d.not_dus(self.ad, "şahit=%d nakz=%s yakîn=%.4f (%s)"
                  % (len(sahitler), d.nakz, yakin, mertebe_adi(yakin)))


def ima(P1: bool, P2: bool) -> bool:
    """``P₁ ⟹ P₂ ≡ ¬P₁ ∨ P₂``."""
    return (not P1) or P2


def modus_ponens(P1: bool, P2: bool) -> bool:
    """``P₁`` ve ``P₁⟹P₂`` doğruysa ``P₂``. Öncüller sağlanmıyorsa
    çıkarım YAPILMAZ -- ``None`` yerine ``P₂``nin kendisi değil, kuralın
    tanımı gereği yalnız sağlandığı hâlde kullanılır."""
    if not (P1 and ima(P1, P2)):
        raise ValueError("modus ponens öncülleri sağlanmıyor")
    return P2


# =====================================================================
@kaydet
class Ispat(Meleke):
    """𝒪₂₄ İspat -- burhân zinciri ``P₀ → P₁ → … → Pₙ ≡ Q``.

    ``T_ispat = Π_k Geçerlilik(P_{k−1} ⟹ P_k)``; ``𝟙_QED = 𝕀(T = 1)``;
    ``Sarsılmazlık = T/(1+λn)`` -- yani uzun zincir, aynı geçerlilikte
    daha zayıf sayılır (Occam'ın ispata tatbiki).
    """

    no, ad = 24, "İspat"
    okur, yazar = ("S",), ("burhan",)

    def uygula(self, d: Durum, p: Parametreler) -> None:
        S = d.S
        zincir = [S[i] for i in range(len(S))]
        d.burhan = zincir
        gecerlilikler = [
            float(sigmoid(4.0 * kosinus(zincir[k - 1], zincir[k])))
            for k in range(1, len(zincir))
        ]
        T = float(np.prod(gecerlilikler)) if gecerlilikler else 1.0
        n = len(gecerlilikler)
        d.olcum.koy("ispat.T", T)
        d.olcum.koy("ispat.zincir_uzunluğu", float(n))
        d.olcum.koy("ispat.QED", float(T >= 1 - 1e-9))
        d.olcum.koy("ispat.sarsılmazlık", guvenli_bol(T, 1.0 + 0.1 * n))
        d.olcum.koy("ispat.boşluk",
                    float(np.sum([np.sum((zincir[k] - zincir[k - 1]) ** 2)
                                  for k in range(1, len(zincir))])))

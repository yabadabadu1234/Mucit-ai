"""ZIRH ÇİPİ -- dörtlü topolojik zırh, mantık sadakati ve MPO işareti.

KÜME 3'ün tevhidi (kütük H222). Dokuz dosya -- ``nefs/zirh.py``,
``ogrenme/zirh.py``, ``ogrenme/zirh_mizan.py``, ``kuantum/tda.py``,
``nefs/sadakat.py``, ``nefs/tertip.py``, ``nefs/isaret.py``,
``nefs/nizam.py``, ``nefs/kod_uzayi.py`` -- burada birleşti. Terkip üç
adımda yapıldı, padişahın usulü gereği: (a) evvelâ her dosya **kendi
içinde** terkip edildi, (b) sonra dosyalar birleştirildi, (c) sonra
birleşik gövdede **bir daha** terkip edildi. Hiçbir cevher seçilip
imha edilmedi; asılları ``yedek/kume3_asillari/`` altında şahittir.

**Gaye.** Bu mimaride asla bir sonraki token tahmini (Cross-Entropy)
yapılmaz. Minimize edilecek şey::

    L_toplam = L_Kohomoloji (Çelişki)
             + L_Betti      (Ezber boşluğu / delik)
             + L_Sheaf      (Ek yeri uyumsuzluğu)
             + L_Homotopi   (Yola bağımlılık)
             + L_Nizam      (Melekenin tutmadığı taahhüt)

Öğrenilen şey bir kelime dağılımı değil, **çelişkisiz bir mana
manifoldudur**. Hedef: ``L_toplam == 0`` olan 44 Meleke SO(D)
Lie-ağırlıklarını bulmak.

**Dört süzgeç, dört ayrı sual.**

===========  ==============================  ==========================
süzgeç       neyi sorar                      sıfır olması ne demek
===========  ==============================  ==========================
Sheaf 𝒮      iki mefhum ek yerinde uyuşuyor  yerel hükümler küllî bir
             mu? ``‖ΔRes‖²``                 hükme yapışıyor
Betti/Hodge  muhakemede delik var mı?        ezber adacığı yok; her
             ``dim ker Δ_Hodge``             çevrim doldurulmuş
Kohomoloji   kapanan fakat dolmayan çevrim   çelişki (safsata) yok
             var mı? ``dim H^m``
Homotopi     çevrim boyunca faz dönüyor mu?  ``W(γ) = 1``, yol bağımsız
             ``|W(γ) − 1|``                  -- hüküm yola bağlı değil
===========  ==============================  ==========================

**Betti ile Kohomoloji niçin ayrı kalem değil.** Sonlu boyutta
``dim H_k = dim H^k = dim ker Δ_k`` (Hodge teoremi); ikisini ayrı yazmak
**çift saymaktır**. Ayrı olan derecedir: ``k = 1`` çevrim delikleri,
``k = 0`` kopuk mana adaları. Farklı dereceler, farklı manalar.

**Çipin dört odası.**

1. **Analitik topolojik süzgeçler** -- ``yama``,
   ``delik``, ``iz``; Ĥ matrisine projektör olarak.
2. **Yazmaç enine süzgeçleri** -- ``zirhla`` MPS dalgasına O(N)
   yerel kapılarla vurur; aynı dört süzgeç, başka veçhe.
3. **Birleşik mantık sadakati** -- ``vicdan``:
   ``mizan.onerme``den türeyen yasaklar, epistemik sadakat şartları ve
   ``R₀`` intacı **tek** süpürmede.
4. **Nizam, stabilizer ve zırh kaybı** -- ``taahhude_yuzlestir``,
   ``muhru_stabilizerle_yuzlestir``, ``kulli_zirh_kaybi``.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import (Callable, Dict, Iterable, List, Mapping, Optional,
                    Sequence, Tuple)

import numpy as np

from idrak.kategori import Uzay
from kuantum.stabilizer import StabilizerDurum
# MPS ``Yazmac`` fermanla imha edildi; zırh artık qudit
# yazmacını kullanır (aynı ölçüler, SVD yok).
from nefs.qyazmac import QuditYazmac as Yazmac
from matematik.mizan import Onerme, Tablo, deg, degil, ise, ve
from nefs.zihin_durumu import QYazmac, degil_x, donme

__all__ = [
    # 1. analitik süzgeçler
    "yama", "delik", "iz",
    "vietoris_rips", "dogum_olum_cetveli", "cetveller_arasi_mesafe",
    "kahan_toplam",
    # 2. zırh giydirme (matris ve dalga)
    "ZirhAyari", "ZirhIzi", "zirhla", "dalgayi_yokla",
    # 3. mantık sadakati
    "Usul", "USULLER", "ALANLAR", "isaret_vur",
    "vicdan",
    # 4. nizam, mühür, kayıp
    "SINIF_CIHETI", "NIZAM_BANDI", "SADAKAT_SIDDETI",
    "taahhude_yuzlestir", "muhru_stabilizerle_yuzlestir",
    "zirh_kaybi", "rapor",
]



# ════════════════════════════════════════════════════════════════════
#  nefs/zirh.py
# ════════════════════════════════════════════════════════════════════

def yama(res_a: np.ndarray, res_b: np.ndarray,
                       eps: float = 1e-9) -> Dict[str, object]:
    """EK YERİ TUTUYOR MU -- **tek terkip** (kütük H222).

    Küme: ``sheaf_uyumsuzlugu`` + ``sheaf_izdusumu``. İkisi de tek bir
    farktan doğar -- iki örtünün ek yerindeki kısıtlama farkı
    ``Δ = Res_α − Res_β``. Biri o farkın **büyüklüğünü** sorar, öteki
    o farkın **yönünü söndüren** izdüşümü kurar; ayrı ayrı çağrılınca
    ``Δ`` iki kere hesaplanıyordu::

        uyumsuzluk = ‖Δ‖²
        𝒮 = I − ΔΔᵀ / (‖Δ‖² + ε)

    Bir demet (sheaf) kesitinin var olabilmesi için örtüşen iki açık
    kümenin kısıtlamaları ek yerinde **eşit** olmalıdır. Eşit değilse
    yerel hükümler küllî bir hükme yapışmaz: model bir yerde "A", başka
    yerde "değil-A" der ve ikisini bağdaştıramaz.

    Uyumsuzluk sıfıra giderken ``𝒮 → I`` olur (hiçbir şey söndürülmez);
    büyükken uyumsuz yön tamamen atılır. ``ε`` sıfıra bölmeyi değil,
    **sıfır uyumsuzlukta kimliğe düzgün yaklaşmayı** temin eder.
    """
    a = np.asarray(res_a, float)
    b = np.asarray(res_b, float)
    if a.shape != b.shape:
        raise ValueError("iki kısıtlama aynı şekilde olmalı")
    d = (a - b).ravel()
    kare = float(d @ d)
    return {"uyumsuzluk": kare,
            "izdüşüm": np.eye(d.size) - np.outer(d, d) / (kare + float(eps)),
            "fark": d}


def delik(K: Dict[int, List[Tuple[int, ...]]], k: int = 1,
                  ne: str = "delik", esik: Optional[float] = None):
    """ŞEKİLDE KAÇ DELİK VAR -- **tek terkip** (kütük H222, birleşik tur).

    Küme: ``sinir_operatoru`` + ``kombinatoryal_laplasyen`` + ``betti`` +
    ``euler_karakteristigi`` (``kuantum/tda.py``) + ``hodge_laplasyeni``
    + ``hodge_bettisi`` + ``betti_kaybi`` + ``koho_kaybi``
    (``nefs/zirh.py``). Sekizi ayrı dosyalarda, ayrı isimlerle duruyordu;
    hepsi **tek bir dizeyin** -- ``Δ_k`` Hodge Laplasyeninin -- ayrı
    okunuşudur. Zırh tarafı her çağrıda ``kuantum.tda``ya inip ``∂``yı
    yeniden kurduruyor, sonra kendi özdeğer ayrışımını bir kere daha
    yapıyordu::

        ∂_k[v₀…v_k] = Σ_j (−1)^j [v₀…v̂_j…v_k]
        Δ_k = ∂_{k+1}∂_{k+1}ᵀ + ∂_kᵀ∂_k
        β_k = dim ker Δ_k               (eşikli özdeğer sayımı)
        boşluk = min{λ : λ > eşik}      (spektral boşluk)
        χ = Σ_k (−1)^k |C_k|

    ==============  =============================================
    ``ne``          döndürdüğü
    ==============  =============================================
    ``sınır``       ``∂_k`` dizeyi
    ``laplasyen``   ``Δ_k`` dizeyi
    ``betti``       ``β_k`` (tam sayı)
    ``euler``       ``χ`` (tam sayı)
    ``delik``       sözlük: betti, boşluk, delik_cezası, ada_cezası
    ==============  =============================================

    İşaretler kanonik sıralamadan gelir; sıra bozulursa ``∂∘∂ = 0``
    bozulur.

    **Betti ile kohomoloji niçin ayrı fonksiyon değil.** Sonlu boyutta
    ``dim H_k = dim H^k = dim ker Δ_k`` (Hodge teoremi); ikisini ayrı
    kalem yazmak **çift saymaktır**. Ayrı olan derecedir, isim değil:

    * ``k = 1`` -- muhakemedeki **delikler**; ceza ``b₁``dir.
    * ``k = 0`` -- birbirine bağlanmamış **mana adaları**; ``b₀ = 1``
      sağlıklıdır (tek parça), ceza fazlalık kadardır: ``max(b₀−1, 0)``.

    Spektral boşluk ayrıca döner ve bir ölçüdür (H47): Betti sayısı tam
    sayıdır, gradyan taşımaz; boşluk süreklidir ve eğitim ona yol bulur.

    Eşik verilmezse dizeyin ölçeğine göre seçilir:
    ``tol = n · ε_mach · max(1, ‖Δ‖₂)`` -- LAPACK'in rütbe hesabında
    kullandığı ölçüt. Mutlak eşik, büyük dereceli çizgelerde hakiki
    sıfır olmayan özdeğerleri de sıfır sayardı. Tikhonov düzenlemesi
    (``Δ + εI``) burada **kullanılmaz**: o, ölçülmek istenen çekirdeği
    tam olarak yok eder (K25 tashihi).
    """
    if ne == "euler":
        return int(sum((-1) ** kk * len(v) for kk, v in K.items()))

    def sinir(kk: int) -> np.ndarray:
        if kk <= 0:
            return np.zeros((0, len(K.get(0, []))))
        ust = K.get(kk, [])
        alt = K.get(kk - 1, [])
        yer = {x: i for i, x in enumerate(alt)}
        B = np.zeros((len(alt), len(ust)))
        for j, x in enumerate(ust):
            for i in range(len(x)):
                yuz = x[:i] + x[i + 1:]
                if yuz in yer:
                    B[yer[yuz], j] = (-1.0) ** i
        return B

    if ne == "sınır":
        return sinir(int(k))

    Bk = sinir(int(k))                      # (|C_{k-1}|, |C_k|)
    Bk1 = sinir(int(k) + 1)                 # (|C_k|, |C_{k+1}|)
    n = len(K.get(int(k), []))
    D = np.zeros((n, n))
    if Bk1.size:
        D = D + Bk1 @ Bk1.T
    if Bk.size:
        D = D + Bk.T @ Bk
    if ne == "laplasyen":
        return D

    if D.size == 0:
        if ne == "betti":
            return 0
        return {"betti": 0.0, "betti0": 0.0, "boşluk": 0.0, "kayıp": 0.0,
                "delik_cezası": 0.0, "ada_cezası": 0.0}
    oz = np.linalg.eigvalsh((D + D.T) / 2.0)
    olcek = max(float(abs(oz).max()), 1e-30)
    e = esik
    if ne == "betti":
        if e is None:
            e = D.shape[0] * np.finfo(float).eps * max(1.0, olcek)
        return int(np.sum(oz <= e))
    if ne != "delik":
        raise ValueError("delik sayımının kipi bilinmiyor: %r" % (ne,))

    sifir = oz <= (1e-9 if e is None else e) * olcek
    kalan = oz[~sifir]
    b = int(sifir.sum())
    bosluk = float(kalan.min()) if kalan.size else 0.0
    delik_sayisi = float(b)                # k = 1 okuması
    ada = float(max(b - 1, 0))              # k = 0 okuması
    return {"betti": float(b), "betti0": float(b), "boşluk": bosluk,
            "delik_cezası": delik_sayisi, "ada_cezası": ada,
            "kayıp": ada if int(k) == 0 else delik_sayisi}


def iz(baglanti: Sequence[np.ndarray]) -> Dict[str, object]:
    """AYNI YERE İKİ YOLDAN GİDİNCE FARK EDER Mİ -- **tek terkip** (H222).

    Küme: ``wilson_cevrimi`` + ``homotopi_kaybi``. İkincisi birincisini
    çağırıp normunu alıyor, üstelik aynı sayıyı ``W_sapması`` ve
    ``kayıp`` diye **iki ayrı anahtarda** döndürüyordu::

        W(γ) = U_n ⋯ U_2 U_1,     sapma = ‖W − I‖_F / √n

    Bağlantılar ortogonal (reel) dizeylerdir; çarpımları da öyledir.
    ``W = I`` ise hüküm **yola bağlı değildir**: aynı neticeye hangi
    yoldan gidilirse gidilsin aynı şey çıkar. ``W ≠ I`` ise mana yola
    bağlıdır ve model aynı meseleye iki farklı sırada bakınca iki farklı
    hüküm verir.
    """
    W = None
    for U in baglanti:
        A = np.asarray(U, float)
        W = A if W is None else A @ W
    if W is None:
        W = np.eye(1)
    n = W.shape[0]
    sapma = float(np.linalg.norm(W - np.eye(n)) / math.sqrt(max(n, 1)))
    return {"W": W, "sapma": sapma, "kayıp": sapma}


def zirhla(hedef, ayar: Optional[ZirhAyari] = None,
                esik: float = 1e-9, S: Optional[np.ndarray] = None,
                Pi_betti: Optional[np.ndarray] = None,
                Pi_koho: Optional[np.ndarray] = None,
                u: Optional[Uzay] = None, okuma: Optional[np.ndarray] = None,
                onceki: Optional[np.ndarray] = None):
    """ZIRH GİYDİRMEK -- **tek terkip** (kütük H222, birleşik tur).

    Küme: ``zirh_uygula`` (``nefs/zirh.py``) + ``operatore_zirh_giydir``
    (``ogrenme/zirh.py``) + ``dalgaya_zirh_giydir``
    (``ogrenme/zirh_mizan.py``). Üçü de **aynı dört süzgeci** giydiriyor,
    fakat üç ayrı dosyada, üç ayrı kod yolundan. Zabıttaki birinci
    çelişki buydu: analitik süzgeçler soyut ``Ĥ`` matrisine projektör
    olarak vurulurken, aynı süzgeçler MPS dalgası üzerinde ``O(N)``
    yerel kapılarla ayrıca yazılmıştı; ikisi birbirinden habersizdi.
    Artık tek kapıdan geçerler ve hangi veçhenin çalıştığını ``hedef``
    tayin eder:

    * ``hedef`` bir **dizey** ise -- ``Ĥ`` üzerine dördü geçirilir,
      ``(Ĥ_zırhlı, rapor)`` döner. ``S/Pi_betti/Pi_koho`` verilirse
      hazır projektörlerle **yalnız** ``Π_koho Π_betti 𝒮 H 𝒮ᵀ Π_betti
      Π_koho`` sırası uygulanır ve dizey döner.
    * ``hedef`` bir **yazmaç** ise -- ``okuma`` vektörü üzerinde dört
      süzgeç koşar ve **yazmaca geri yansır**; ``(düzeltilmiş_okuma,
      ZirhIzi)`` döner.

    **Projektör sırası keyfî değildir ve tersine çevrilemez:** 𝒮 en
    içtedir (yerel ek yeri), sonra Betti (delik), en dışta kohomoloji
    (çelişki). İçten dışa doğru **daha küllî** bir şarttır; dıştaki,
    içtekinin düzeltmesini görmelidir.

    Rapor **her zırh için ayrı sayı** taşır. Tek bir toplam sayı
    dönseydi hangi zırhın çalıştığı bilinemez, biri ölse fark edilmezdi
    (H90).

    Dizey veçhesinde dört süzgecin ``Ĥ``den okunuşu:

    * **Sheaf** -- operatörün üst ve alt üçgeni iki yamadır; ek
      yerindeki uyumsuzluk sheaf artığıdır.
    * **Betti/Kohomoloji** -- kompleksin **gölgesinden**: köşeler
      satırlar, kenarlar ``|H_ij| > eşik`` çiftleridir. Bu bir gölgedir,
      tam nerv değildir ve öyle söyleniyor: Betti sayıları buradan
      okununca ``H``nin bağlantı yapısını ölçer, manifoldun kendisini
      değil.
    * **Homotopi** -- kapalı yolda ``W(γ) = 1`` mi. Çevrimin halkaları
      **aynı ebatta** olmak zorundadır; yoksa ``W(γ)`` çarpımı hiç
      kurulamaz. Kare bir pencere kaydırılır ve son halka başa döner.

    Dalga veçhesinde süzgeçler okuma vektörü üzerinde çalışır ve
    **yazmaca geri yansır**: Betti cezası bir genlik tartısı, homotopi
    bir işaret kapısı olarak kübitlere uygulanır. Yani zırh yalnız
    ölçmez, dalgayı da büker.
    """
    if isinstance(hedef, np.ndarray) or not hasattr(hedef, "n"):
        H = np.atleast_2d(np.asarray(hedef, float))
        if S is not None or Pi_betti is not None or Pi_koho is not None:
            A = H
            for P in (S, Pi_betti, Pi_koho):
                if P is not None:
                    P = np.asarray(P, float)
                    A = P @ A @ P.T
            return A
        a = ayar or ZirhAyari()
        H = np.atleast_2d(np.asarray(H, float))
        n = int(H.shape[0])

        # (1) Sheaf: üst/alt üçgen iki yama
        ust = np.triu(H)
        alt = np.tril(H).T
        ek = yama(ust, alt)
        s_hata = float(ek["uyumsuzluk"])
        S = ek["izdüşüm"]

        # (2)(3) Betti ve kohomoloji: kompleksin gölgesi
        #
        # ÖLÇÜLEN VE DÜZELTİLEN KUSUR (kütük H229). Eşik MUTLAK
        # (``1e-9``) alınıyordu; ``H``in kendi medyanı ``2,8e-4``
        # olduğu için bu, ölçeğin dört milyonda biriydi ve graf
        # **dâima tam graf** çıkıyordu. Netice: ``β₁ = C(n,2) − n + 1``
        # -- ``n = 16`` için sabit **105**, ve ``H``in DEĞERLERİNE hiç
        # bakmıyordu. Eşik artık ``H``in kendi ölçeğinden okunur:
        # medyan-üstü bağlantılar kenar sayılır, altındakiler sayılmaz.
        # Böylece kompleks nihayet dalganın şeklini görür.
        A = np.abs(H)
        # Ölçek **âzamîden** okunur, medyandan değil: medyan eşiği
        # tanım gereği kenarların yarısını tutar ve β₁ yine sabit
        # kalır (ölçüldü: 105 yerine 45, ama hâlâ kıpırdamıyor).
        # Âzamîye göre eşik, kütlesi birkaç bağa toplanmış bir dalgada
        # SEYREK, yayılmış bir dalgada YOĞUN graf verir -- yâni artık
        # dalganın şeklini görür.
        dis = A[~np.eye(n, dtype=bool)]
        olcek = float(dis.max()) if dis.size else 0.0
        e_kompleks = max(float(esik), a.betti_kat * olcek)
        K = {0: [(i,) for i in range(n)],
             1: [(i, j) for i in range(n) for j in range(i + 1, n)
                 if A[i, j] > e_kompleks or A[j, i] > e_kompleks]}
        b1 = delik(K, k=1)
        b0 = delik(K, k=0)
        # Ve ceza NORMALİZE edilir. Ham sayım ``[0, C(n,2)−n+1]``de
        # yaşıyordu; öteki dört ihlâl ``[0,1]``de. Yumuşak âzamîde bir
        # SAYIM ile bir KESİR yarışınca sayım dâima kazanır ve ötekiler
        # görünmez olur -- kayıp 104,597641'de çakılıp kalmasının
        # sebebi buydu. (Aynı ders BGCM'de ``kayıp_norm`` ile zaten
        # öğrenilmişti; zırha uygulanmamıştı.)
        azami_b1 = max(1, n * (n - 1) // 2 - n + 1)

        # (4) Homotopi: kapalı yolda Wilson çevrimi
        adim = max(2, min(8, n))
        m = max(1, n // adim)
        baglanti = []
        for i in range(adim):
            b = i * m
            blok = H[b:b + m, b:b + m]
            if blok.shape != (m, m):
                blok = np.zeros((m, m))
            baglanti.append(np.eye(m) + 1e-3 * blok)
        h = iz(baglanti)

        toplam = zirh_kaybi(sheaf=s_hata,
                            betti=float(b1["delik_cezası"]) / azami_b1,
                            koho=float(b0["ada_cezası"]) / max(n, 1),
                            homotopi=float(h["sapma"]), ayar=a)

        # Projektör ancak ``H`` ile aynı ebatta ise vurulur; sheaf
        # izdüşümü ``Δ``nın **yayılmış** boyunda olduğu için ekseriya
        # değildir ve o hâlde dizey olduğu gibi kalır.
        H_zirhli = (S @ H @ S.T
                    if getattr(S, "shape", None) == H.shape else H)
        return H_zirhli, {
            "sheaf_uyumsuzluk": s_hata,
            "betti_delik_sayisi": float(b1["betti"]),
            "kohomoloji_tikaniklik": float(b0["ada_cezası"]),
            "homotopi_burulma": float(h["sapma"]),
            "toplam_kayip": float(toplam["kayıp"]),
            "mizan_dengesi": float(np.abs(np.mean(H_zirhli))),
        }
    y = hedef
    v = np.asarray(okuma, float).copy()
    k = len(v) // 2
    z = v[:k]

    # --- 1. Sheaf: ek yerlerindeki kopukluğu bastır
    if k >= 2:
        fark = np.diff(z)
        d = np.zeros_like(z)
        d[:-1] += 0.5 * fark
        d[1:] -= 0.5 * fark
        agirlik = 1.0 / (1.0 + float(np.mean(np.abs(fark))))
        z_yeni = z + (1.0 - agirlik) * d
        sheaf_d = float(np.linalg.norm(z_yeni - z))
        z = z_yeni
    else:
        sheaf_d = 0.0

    # --- 2. Homotopi: baskın bileşenin işaretine hizala (yapıcı girişim)
    i = int(np.argmax(np.abs(z))) if k else 0
    isaret = 1.0 if (k == 0 or z[i] >= 0) else -1.0
    z = z * isaret

    # --- 3. Betti: ayrık adacık = ezber → genlik cezası
    from nefs.melekeler import devirler
    b0 = devirler("zincir_β0", z)
    ceza = float(np.exp(-0.25 * (b0 - 1) ** 2))
    z = z * ceza

    # --- 4. Kohomoloji: taşınamayan (dik) bileşeni yut
    tik = 0.0
    if onceki is not None and len(onceki) == len(v):
        o = np.asarray(onceki, float)
        no = np.linalg.norm(o) + 1e-12
        oh = o / no
        tam = np.concatenate([z, v[k:]])
        paralel = oh * float(oh @ tam)
        dik = tam - paralel
        nd, nt = float(np.linalg.norm(dik)), float(np.linalg.norm(tam)) + 1e-12
        tik = nd / nt
        if tik > 0.9:                       # tıkanıklık: yalnız %10'u geçsin
            tam = paralel + 0.1 * dik
        z, v = tam[:k], tam
    v = np.concatenate([z, v[k:]])

    # --- zırhın yazmaca geri yansıması
    if abs(isaret + 1.0) < 1e-9:            # işaret çevrildi → σ_z kapısı
        y.tek_kapi(np.array([[1.0, 0.0], [0.0, -1.0]], dtype=y.tip))
    if ceza < 0.999:                        # Betti cezası → genlik tartısı
        g = np.array([[1.0, 0.0], [0.0, ceza]], dtype=np.float64)
        g = g / (np.linalg.norm(g, axis=0, keepdims=True) + 1e-30)
        y.tek_kapi(g.astype(y.tip))

    return v, ZirhIzi(mertebe=u.mertebe, sheaf_duzeltme=sheaf_d,
                      homotopi_isaret=isaret, betti0=b0,
                      betti_ceza=ceza, tikaniklik=tik)



@dataclass
class ZirhAyari:
    """Zırhın ağırlıkları ve yumuşak-asgarî sertliği."""
    w_sheaf: float = 1.0
    w_betti: float = 1.0
    w_koho: float = 1.0
    w_homotopi: float = 1.0
    #: Nizam (meleke taahhüdü) ihlâlinin ağırlığı -- H222'de zırhın
    #: içine alındı; evvelce tâlim kaybına harici bir ek olarak
    #: veriliyordu ve zırh onu hiç görmüyordu.
    w_nizam: float = 1.0
    #: ``τ``: yumuşak **âzamî** sertliği. Kullanıcı hükmü 4 gereğince
    #: düz aritmetik ortalama alınmaz. Fakat burada ``max``a yumuşak
    #: yaklaşılır, ``min``e değil -- ve sebebi şudur: bunlar **ihlâl**
    #: ölçüleridir; hepsi sıfır olmalıdır, dolayısıyla hükmü **en kötü
    #: ihlâl** verir. Kaybın yumuşak-asgarîsi (`nefs/olcu.py`) uzuvların
    #: *kabiliyeti* içindir; burada ölçülen kabiliyet değil ihlâldir.
    tau: float = 4.0
    #: Betti kompleksinin eşiği, ``|H|``in **medyanının katı** olarak.
    #: Mutlak eşik (evvelce ``1e-9``) ölçekten bağımsızdır ve dizeyin
    #: medyanı ondan büyükse graf dâima tam çıkar; β₁ o zaman ``H``in
    #: değerlerine değil yalnız EBADINA bakan bir sabit olur (H229).
    #: ``0.3`` = ``|H|``in âzamîsinin onda üçü; büyütmek kompleksi
    #: seyreltir. Medyan denendi ve reddedildi: medyan eşiği kenarların
    #: hep yarısını tutar, β₁ yine sabit kalır.
    betti_kat: float = 0.3


def zirh_kaybi(sheaf: float = 0.0, betti: float = 0.0, koho: float = 0.0,
               homotopi: float = 0.0, nizam: float = 0.0,
               ayar: Optional[ZirhAyari] = None,
               q=None) -> Dict[str, object]:
    """KÜLLÎ ZIRH KAYBI -- **tek terkip** (kütük H222, birleşik tur).

    Küme: ``zirh_kaybi`` + ``sinif_ihlali``/``yuzlestir``in kayba giden
    ucu (``nefs/nizam.py``) + ``kod_uzayi.yuzlestir``in mühür ucu.
    Zabıttaki üçüncü çelişki buydu: melekelerin ``ΔS`` taahhüdü ve
    Clifford kod uzayı doğrulaması ana akışın **dışında** ayrı teftişler
    olarak duruyordu; zırh onları görmüyordu. Artık nizam ihlâli
    doğrudan zırh kaybına girer, stabilizer sapması ise zırhın
    **delinmezlik mührü** olarak aynı sözlükte raporlanır.

    Beş ihlâl **yumuşak âzamî** ile birleşir:

    .. math::  L = \\tfrac{1}{\\tau}\\ln \\sum_i w_i e^{\\tau \\ell_i}

    Düz toplam, dört süzgeç temiz bir beşincisi berbat iken cezayı
    seyreltirdi; düz ``max`` ise türevsizdir ve eğitim ona yol bulamaz.
    Yumuşak âzamî ikisinin arasıdır ve ``τ → ∞``da ``max``a gider.

    ``L = 0`` ancak **beşi birden** sıfır iken olur -- ve bu, ceza
    fonksiyonunun ``ln Σ w_i`` kadar kaydırılmasıyla temin edilir;
    kaydırılmasaydı bütün ihlâller sıfırken bile ``ln 5`` kalırdı.

    ``q`` verilirse mühür de yoklanır: MPS'in hüküm dağılımı ile tam
    Clifford stabilizer dağılımı arasındaki TVD. **Bu bir sınamadır,
    bir iddia değil** -- kayba katılmaz, zira yapısal bir ölçüdür
    (H154: mimarî kesme bir optimizasyon parametresi değildir); yalnız
    ``mühür_tvd`` anahtarında raporlanır.
    """
    a = ayar or ZirhAyari()
    l = np.array([float(sheaf), float(betti), float(koho),
                  float(homotopi), float(nizam)])
    w = np.array([a.w_sheaf, a.w_betti, a.w_koho, a.w_homotopi,
                  a.w_nizam])
    t = float(a.tau)
    m = float(np.max(t * l))
    ls = m + math.log(float(np.sum(w * np.exp(t * l - m))))
    L = (ls - math.log(float(np.sum(w)))) / t
    out: Dict[str, object] = {
        "sheaf": float(l[0]), "betti": float(l[1]), "koho": float(l[2]),
        "homotopi": float(l[3]), "nizam": float(l[4]),
        "kayıp": float(L), "çelişkisiz": bool(L <= 1e-12)}
    if q is not None:
        try:
            out["mühür_tvd"] = float(
                muhru_stabilizerle_yuzlestir(q)["tvd"])
        except Exception as e:                       # pragma: no cover
            out["mühür_tvd"] = float("nan")
            out["mühür_hatası"] = str(e)
    return out






# ════════════════════════════════════════════════════════════════════
#  ogrenme/zirh.py
# ════════════════════════════════════════════════════════════════════





# ════════════════════════════════════════════════════════════════════
#  ogrenme/zirh_mizan.py
# ════════════════════════════════════════════════════════════════════

@dataclass
class ZirhIzi:
    """Bir uzaydaki zırh teftişinin izi."""
    mertebe: int
    sheaf_duzeltme: float
    homotopi_isaret: float
    betti0: int
    betti_ceza: float
    tikaniklik: float


def dalgayi_yokla(y: Yazmac, ornek: int = 256) -> np.ndarray:
    """DALGAYI BOZMADAN YOKLAMAK (eski ``okuma_vektoru``).

    Dalganın ``ornek`` yuvadaki **zayıf** okuması -- çöküş yok.

    Her yuvanın ``2×2`` indirgenmiş yoğunluğundan Bloch benzeri iki reel
    sayı alınır: ``z = ρ₀₀ − ρ₁₁`` (nüfus farkı) ve ``x = 2ρ₀₁`` (uyum).
    Bu, süperpozisyonu bozmadan alınan bir POVM okumasıdır.
    """
    n = y.n
    idx = np.linspace(0, n - 1, min(ornek, n)).astype(int)
    R = y.tekil_yogunluklar(idx)                 # (k, 2, 2)
    z = R[:, 0, 0] - R[:, 1, 1]
    x = 2.0 * R[:, 0, 1]
    return np.concatenate([z, x])






# ════════════════════════════════════════════════════════════════════
#  kuantum/tda.py
# ════════════════════════════════════════════════════════════════════

def vietoris_rips(D: np.ndarray, eps: float, azami_boyut: int = 2
                  ) -> Dict[int, List[Tuple[int, ...]]]:
    """``VR(X, ε)`` — çapı ``ε``yi aşmayan bütün simpleksler.

    ``D``: ``(N, N)`` mesafe dizeyi.  Dönen: boyuttan simpleks
    listesine sözlük; her simpleks **sıralı** bir demettir (kanonik
    yönelim), ki sınır operatöründeki işaretler tutarlı olsun.

    Sıralama şart: aynı simpleksi iki farklı sırayla eklemek, sınır
    operatöründe iki kere sayılmasına ve ``∂∘∂ = 0``ın bozulmasına
    yol açar.
    """
    D = np.asarray(D, float)
    N = D.shape[0]
    if D.shape != (N, N):
        raise ValueError("D kare olmalı")
    K: Dict[int, List[Tuple[int, ...]]] = {0: [(i,) for i in range(N)]}
    onceki = K[0]
    for k in range(1, azami_boyut + 1):
        simpleksler = []
        for s in itertools.combinations(range(N), k + 1):
            if all(D[a, b] <= eps for a, b in itertools.combinations(s, 2)):
                simpleksler.append(s)
        K[k] = simpleksler
        if not simpleksler:
            for kk in range(k + 1, azami_boyut + 1):
                K[kk] = []
            break
        onceki = simpleksler
    return K




def dogum_olum_cetveli(D: np.ndarray, esikler: Sequence[float],
                       k: int = 0, azami_boyut: int = 2,
                       tau: float = 0.0):
    """DELİKLER NE ZAMAN DOĞUP NE ZAMAN ÖLÜYOR -- **tek terkip** (H222).

    Küme: ``betti_egrisi`` + ``barkod`` + ``kalicilik_suzgeci``. Üçü
    zincirleme birbirini çağırıyordu; tek işleri, eşik dizisi boyunca
    ``β_k(ε)``yi okuyup değişimlerinden doğum/ölüm çubukları çıkarmak
    ve kısa ömürlüleri elemekti.

    ``tau > 0`` verilirse yaşam süresi ``τ``dan kısa çubuklar elenir
    (gürültü süzgeci). ``tau = 0`` bütün çubukları bırakır.

    Bu, tam kalıcılık algoritması **değildir** (sınıfları tek tek
    izlemez); ``β_k``nın arttığı yerde doğum, azaldığı yerde ölüm sayar.
    **Hangi** sınıfın öldüğünü bilmez -- fakat barkodun *çoklu kümesi*
    doğrudur ve bottleneck mesafesi zaten çoklu küme üzerinden
    tanımlıdır. Bu sınırlama açıkça yazıldı: daha fazlası iddia
    edilmiyor.
    """
    egri = [delik(vietoris_rips(D, e, azami_boyut), k, "betti")
            for e in esikler]
    dogumlar: List[float] = []
    cubuklar: List[Tuple[float, float]] = []
    onceki = 0
    for e, b in zip(esikler, egri):
        if b > onceki:
            dogumlar.extend([e] * (b - onceki))
        elif b < onceki:
            for _ in range(onceki - b):
                if dogumlar:
                    cubuklar.append((dogumlar.pop(), e))
        onceki = b
    sonsuz = float(esikler[-1])
    for d in dogumlar:
        cubuklar.append((d, sonsuz))
    if tau > 0.0:
        cubuklar = [(b, d) for b, d in cubuklar if d - b >= tau]
    return {"eğri": egri, "çubuklar": cubuklar}


def cetveller_arasi_mesafe(B1: Sequence[Tuple[float, float]],
                           B2: Sequence[Tuple[float, float]],
                           kip: str = "bottleneck", p: float = 2.0) -> float:
    """İKİ DOĞUM-ÖLÜM CETVELİ BİRBİRİNE NE KADAR UZAK -- tek terkip (H222).

    Küme: ``_kupsuz_mesafe`` + ``_kosegene`` + ``bottleneck`` +
    ``_eslesme_var_mi`` + ``wasserstein_p``. Beşi de tek bir ölçüyü --
    iki çoklu küme arasındaki eşleme maliyetini -- kurar; ilk ikisi
    maliyet çekirdeği, sonraki ikisi tam ``W_∞``, sonuncusu ``W_p`` üst
    sınırıdır.

    ==============  ==================================================
    ``kip``         ne verir
    ==============  ==================================================
    ``bottleneck``  ``W_∞(B₁,B₂) = inf_γ sup_x ‖x − γ(x)‖_∞`` -- **TAM**
    ``wasserstein`` ``W_p`` -- **açgözlü ÜST SINIR**, tam değil
    ==============  ==================================================

    İkisi karıştırılmamalıdır ve karıştırılmasın diye tek kapıda,
    ``kip`` adıyla ayrılmıştır.

    Eşleme köşegene gitmeye de izin verir; yoksa farklı uzunluktaki
    cetveller karşılaştırılamazdı. Küçük problemlerde tam çözüm macar
    algoritmasına gerek kalmadan **ikili arama + eşleşme denetimi** ile
    bulunur: aday mesafeler sonlu bir kümedir (bütün nokta-nokta ve
    nokta-köşegen mesafeleri), o yüzden en küçük uygulanabilir aday
    aranır.

    **Simetri şartı.** Köşegene eşleme serbestliğini yalnız bir tarafa
    vekil koyarak modellemek ``W_∞(A,B)`` ile ``W_∞(B,A)``yı farklı
    çıkarır -- ki mesafe simetrik olmalıdır. Bu ilk hâlde öyle olmuş ve
    rastgele cetvellerde simetri testinde yakalanmıştı (0,354 v 0,371).
    Doğru inşa: **her iki tarafa** birer köşegen vekili konur.

    * sol düğümler: ``B₁`` noktaları + ``B₂`` için köşegen vekilleri
    * sağ düğümler: ``B₂`` noktaları + ``B₁`` için köşegen vekilleri

    Kenarlar: nokta-nokta (``ℓ_∞ ≤ d``), nokta-kendi vekili
    (``(ölüm−doğum)/2 ≤ d``) ve vekil-vekil (her zaman serbest;
    köşegenden köşegene mesafe sıfırdır). ``|B₁|+|B₂|`` boyunda tam
    eşleşme varsa ``W_∞ ≤ d``dir.
    """
    def kupsuz(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def kosegene(a):
        """Bir noktanın köşegene ``ℓ_∞`` mesafesi: ``(d−b)/2``."""
        return abs(a[1] - a[0]) / 2.0

    B1, B2 = list(B1), list(B2)

    if kip == "wasserstein":
        kalan = list(B2)
        toplam = 0.0
        for x in B1:
            if kalan:
                i = int(np.argmin([kupsuz(x, y) for y in kalan]))
                d = kupsuz(x, kalan[i])
                if d <= kosegene(x):
                    kalan.pop(i)
                else:
                    d = kosegene(x)
            else:
                d = kosegene(x)
            toplam += d ** p
        for y in kalan:
            toplam += kosegene(y) ** p
        return toplam ** (1.0 / p)

    if kip != "bottleneck":
        raise ValueError("cetvel mesafesinin kipi bilinmiyor: %r" % (kip,))

    if not B1 and not B2:
        return 0.0

    def eslesme_var_mi(d: float) -> bool:
        tol = 1e-12
        n1, n2 = len(B1), len(B2)
        if n1 == 0 and n2 == 0:
            return True
        sol_n = n1 + n2
        komsu: List[List[int]] = [[] for _ in range(sol_n)]
        for i, a in enumerate(B1):
            for j, b in enumerate(B2):
                if kupsuz(a, b) <= d + tol:
                    komsu[i].append(j)
            if kosegene(a) <= d + tol:
                komsu[i].append(n2 + i)          # a → kendi köşegen vekili
        for j, b in enumerate(B2):
            if kosegene(b) <= d + tol:
                komsu[n1 + j].append(j)          # b'nin vekili → b
            for i in range(n1):                  # vekil-vekil: serbest
                komsu[n1 + j].append(n2 + i)

        esles_sag: Dict[int, int] = {}

        def artir(u: int, gorulen: set) -> bool:
            for v in komsu[u]:
                if v in gorulen:
                    continue
                gorulen.add(v)
                if v not in esles_sag or artir(esles_sag[v], gorulen):
                    esles_sag[v] = u
                    return True
            return False

        return sum(1 for u in range(sol_n) if artir(u, set())) == sol_n

    adaylar = sorted({kupsuz(a, b) for a in B1 for b in B2}
                     | {kosegene(a) for a in B1}
                     | {kosegene(b) for b in B2} | {0.0})
    alt, ust = 0, len(adaylar) - 1
    if not eslesme_var_mi(adaylar[ust]):
        return float("inf")
    while alt < ust:
        orta = (alt + ust) // 2
        if eslesme_var_mi(adaylar[orta]):
            ust = orta
        else:
            alt = orta + 1
    return adaylar[alt]


def kahan_toplam(xs: Iterable[float]) -> float:
    """Kahan (dengelemeli) toplama.

    ``y = x − c``; ``t = s + y``; ``c = (t − s) − y``; ``s = t``.
    ``c``, o adımda **kaybedilen** kısmı taşır ve bir sonraki terime
    geri verilir.

    Hata sınırı ``(2ε + O(Nε²))Σ|x_i|`` — baş terim ``N``den
    **bağımsızdır**.  ``Nε`` sınırı naif toplamanınkidir; Kahan'ın
    bütün faydası tam olarak o ``N``i düşürmesindedir (K32 tashihi).
    """
    s = 0.0
    c = 0.0
    for x in xs:
        y = float(x) - c
        t = s + y
        c = (t - s) - y
        s = t
    return s


def _mesafe(P: np.ndarray) -> np.ndarray:
    d = P[:, None, :] - P[None, :, :]
    return np.sqrt(np.sum(d * d, axis=2))


def _cember(n: int, r: float = 1.0) -> np.ndarray:
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.stack([r * np.cos(t), r * np.sin(t)], axis=1)


def _iki_cember(n: int) -> np.ndarray:
    a = _cember(n)
    b = _cember(n) + np.array([10.0, 0.0])
    return np.vstack([a, b])






# ════════════════════════════════════════════════════════════════════
#  nefs/sadakat.py
# ════════════════════════════════════════════════════════════════════

SADAKAT_SIDDETI: Tuple[float, float, float] = (0.35, 0.25, 0.20)




# ════════════════════════════════════════════════════════════════════
#  nefs/tertip.py
# ════════════════════════════════════════════════════════════════════

#: İşaretin de yansıtmanın da üzerinde durduğu hüküm alanları -- **TEK**
#: liste. Ayrışırlarsa vurulan işaret hiçbir zaman genliğe dönmez; H222'de
#: terkibin kapattığı boşluk tam olarak buydu.
HUKUM_ALANLARI: Tuple[str, ...] = ("mizan", "tasdik", "sukut", "nakz",
                                   "kelam", "gaye")

#: Usullerin üzerinde konuştuğu hüküm alanları -- **sıra mühimdir**,
#: ``mizan`` değişkeni ile kübit yuvası bu sırayla eşlenir.
ALANLAR: Tuple[Tuple[str, int], ...] = (
    ("tasdik", 0), ("nakz", 0), ("mizan", 0), ("kelam", 0), ("sukut", 0),
)


class Usul:
    """Bir mantık usulü: ``mizan`` formülü + kübit yuvalarına eşlemesi.

    Formül **doğru** olduğu değerlemeler meşrudur; **yanlış** olduğu her
    değerleme mantık dışıdır ve işaretlenir. Yani usul bir yasak
    listesidir ve o listeyi ``mizan`` çıkarır, ben çıkarmam.

    Yasak listesi artık burada değil, ``yasaklari_isaretle`` terkibinde
    çıkarılır (kütük H222): formülden yasağa, yasaktan MPO'ya giden yol
    tek bir yoldur ve tek yerde durur.
    """

    def __init__(self, ad: str, kur: Callable[[Dict[str, Onerme]], Onerme],
                 izah: str = "") -> None:
        self.ad = ad
        self.izah = izah
        self.formul = kur({a: deg(a) for a, _ in ALANLAR})


USULLER: Tuple[Usul, ...] = (
    Usul("tenakuzsuzluk",
         lambda v: degil(ve(v["tasdik"], v["nakz"])),
         "Bir hüküm hem mühürlenip hem nakzedilemez."),
    Usul("kâfi_sebep",
         lambda v: ise(v["tasdik"], v["mizan"]),
         "Mühür ancak delille olur: tasdik varsa mîzân da uyanık olmalı."),
    Usul("kelâm_şartı",
         lambda v: ise(v["kelam"], v["tasdik"]),
         "Mühürlenmemiş hükümle konuşulmaz."),
    Usul("sükût_şartı",
         lambda v: degil(ve(v["sukut"], v["tasdik"])),
         "Susarken mühürlemek olmaz (kütük H10)."),
)




# ════════════════════════════════════════════════════════════════════
#  nefs/isaret.py
# ════════════════════════════════════════════════════════════════════



# ════════════════════════════════════════════════════════════════════
#  nefs/nizam.py
# ════════════════════════════════════════════════════════════════════

SINIF_CIHETI: Dict[str, int] = {
    "kurucu": +1,
    "çözücü": -1,
    "koruyucu": 0,
}


NIZAM_BANDI: float = 0.05


KORUYUCU_BANDI: float = NIZAM_BANDI


#: Usullerin yasak cetveli **bir kere** kurulur. Evvelce her koşuda
#: ``Tablo`` yeniden inşa ediliyordu; doğruluk tablosu ``θ``ya bağlı
#: değildir, dolayısıyla her turda yeniden sayılması saf israftı.
_YASAK_CETVELI: Optional[Dict[str, List[Dict[str, int]]]] = None


def _yasak_cetveli() -> Dict[str, List[Dict[str, int]]]:
    """Her usulün **yanlış** çıktığı değerlemeler -- mizan'ın hükmü."""
    global _YASAK_CETVELI
    if _YASAK_CETVELI is None:
        c: Dict[str, List[Dict[str, int]]] = {}
        for u in USULLER:
            adlar = sorted(u.formul.degiskenler())
            if not adlar:
                c[u.ad] = []
                continue
            t = Tablo(adlar)
            sutun = t.sutun(u.formul)
            c[u.ad] = [{ad: (i >> t.yer[ad]) & 1 for ad in adlar}
                       for i in range(1 << t.n) if not ((sutun >> i) & 1)]
        _YASAK_CETVELI = c
    return _YASAK_CETVELI


def vicdan(q=None, p=None, usuller=None, tur: int = 1,
                                   ne: str = "hepsi", orutu=None):
    """MANTIK DIŞI KOLU İŞARETLEYİP SÖNDÜRMEK -- tek terkip (H222, birleşik).

    Küme: ``cok_kontrollu_isaret`` + ``sifir_yansitmasi``
    (``nefs/isaret.py``) + ``_degiskenler`` + ``Usul.yasaklar`` +
    ``usul_yasaklari`` + ``tertip_kos`` (``nefs/tertip.py``) +
    ``sadakat_acilari`` + ``_kontrollu_z`` + ``sadakat_kapisi`` +
    ``sadakat_intaci`` (``nefs/sadakat.py``). **Dokuz isim, tek amel.**

    Zabıttaki ikinci çelişki buydu: ``sadakat`` altı yasak için ayrı
    ``CZ`` vuruyor, ``tertip`` dört usul için ayrı MPO çalıştırıyor,
    ``isaret`` ise ikisinin de kullandığı ``D=2`` çekirdeği üçüncü bir
    dosyada tutuyordu -- ve intaç (yansıtma) hangi alanları kapsayacağını
    çağıran taraftan öğreniyordu. Yanlış kurulunca -- meselâ ``kelam``a
    işaret vurulup yansıtmaya alınmazsa -- o işaret **hiçbir zaman
    genliğe dönmezdi**. Terkipte işaretlenen alanlar ile yansıtılan
    alanlar **aynı listeden** (``HUKUM_ALANLARI``) çıkar; ayrışamazlar.

    ==============  =================================================
    ``ne``          ne yapar
    ==============  =================================================
    ``örüntü``      ``orutu={yuva: bit}`` kolunu işaretler (float döner)
    ``işaret``      altı epistemik sadakat şartını işaretler
    ``usul``        ``mizan``dan türeyen yasakları işaretler (float)
    ``intaç``       ``R₀`` yansıtmasıyla işaretlileri söndürür (float)
    ``hepsi``       işaret → usul → intaç
    ``yasaklar``    yalnız yasak cetvelini döndürür (``q`` gereksiz)
    ==============  =================================================

    **İŞARET ÇEKİRDEĞİ (D=2 MPO).** ``orutu``daki bütün şartlar sağlanan
    kola ``π`` fazı vurulur; kesme dönerse köşegen ve bağ boyutu 2 olduğu
    için ``~1e-16`` beklenir, büyükse **bildirilir**.
    ``R₀ = I − 2|0…0⟩⟨0…0|`` yansıtması bunun hususî hâlidir (bütün
    yuvalarda aranan bit ``0``) ve Grover difüzyonunun orta adımıdır.

    **ÖLÇÜLEN VE DÜZELTİLEN TASARIM HATASI (sadakat).** Bu kapı evvelâ
    kontrollü DÖNME ile kuruldu: *"nakz uyanıksa tasdiki sıfıra doğru
    çevir."* Ölçüldü ve **kötüleştirdi**: tenakuz kütlesi 0,2944'ten
    0,3242'ye çıktı. Sebep kodlama hatası değil, bir **imkânsızlıktır**:

    > Dönme monoton değildir. ``R(−λ)`` ``|1⟩``e yakın bir kolu ``|0⟩``a
    > çeker, fakat ``|0⟩``a yakın kolu ``|1⟩``e iter. Daha umumîsi:
    > **hiçbir sabit üniter kapı bir alt uzayı şartsız söndüremez.**
    > Üniterlik normu korur; genliği ancak *taşır*. Şartsız söndürmek
    > bir izdüşümdür ve izdüşüm üniter değildir -- yani okumadır, H31'i
    > kırar.

    O hâlde sadakat, bastırmakla değil **işaretlemekle** icra edilir:
    yasaklı kola ``π`` fazı vurulur (``CZ = diag(1,1,1,−1)``; reeldir,
    H98: reel yazmaçta ``π`` fazı vardır, keyfî ``e^{iθ}`` yoktur),
    sönmesi sondaki girişime bırakılır. Bu, `nefs/qkaide.py`de fiilen
    ölçülmüş usulün ta kendisidir (H98: 17--22 kat yükseltme).

    İşaretlenen altı mantık dışı hâl::

        |tasdik=1, nakz=1⟩       hem mühürlü hem nakzedilmiş
        |tasdik₀=1, tasdik₁=0⟩   hüküm kendi içinde bölük
        |tasdik=1, mîzân₀=0⟩     delilsiz mühür
        |kelam₀=1, tasdik₀=0⟩    mühürlenmemiş hükümle konuşmak (H108)
        |sukut=1, tasdik₀=1⟩     susarken mühürlemek (H10)
        |tasdik ⊕ gaye⟩          gaye ile hüküm ayrışması (Dosya 7)

    Faz vurmak marjinalleri **hiç değiştirmez**; onun için işaret tek
    başına ölçümde görünmez ve görünmemesi doğrudur. Hükmü doğuran,
    işaretle girişimin bileşkesidir.

    **ÖLÇÜLEN VE DÜZELTİLEN KUSUR (tertip).** Evvelce doğruluk tablosu
    BÜTÜN alanlar üzerinden kuruluyordu; halbuki her formül ancak
    birkaçına bağlıdır. ``¬(tasdik ∧ nakz)`` tek bir örüntüdür, fakat
    beş değişken üzerinden sayılınca serbest üç değişkenin ``2³ = 8``
    bileşimi ayrı ayrı yazılıyordu. Netice: usul başına 8 MPO, toplam
    32; ve **kesme 1,8e+01**e fırlıyordu (χ patlaması). Doğrusu,
    formülün fiilen bağlı olduğu değişkenleri ``Onerme.degiskenler()``den
    almak ve tabloyu yalnız onlar üzerinde kurmaktır. O zaman her usul
    **tek** örüntü verir ve işaret ``≤3`` kontrollü kalır.

    ``tertip`` yazmacı evvelâ süperpozisyona sokulur; sonra her usulün
    yasakları, o usule ait tertip kübiti ``|1⟩`` iken işaretlenir. Yani
    bir usul "açık" da "kapalı" da değildir -- **ikisi birden**dir ve
    hangisinin işe yaradığını girişim tayin eder.

    **Niçin yalnız hüküm alanları.** Veri kübitlerine dokunulmaz;
    yansıtma yalnız hüküm bloğunu kapsar. Bütün zincire vurmak, dalganın
    taşıdığı bütün suretleri de karıştırırdı. Yansıtma köşegen olduğu
    için MPO bağ boyutu 2'dir ve ancilla gerekmez.
    """
    if ne == "yasaklar":
        return _yasak_cetveli()

    def isaret(orutu_: Mapping[int, int]) -> float:
        """D=2 MPO işaret çekirdeği -- bütün işaretlemelerin aslı."""
        if not orutu_:
            return 0.0
        yuv = sorted(int(k) for k in orutu_)
        bas, son = yuv[0], yuv[-1] + 1
        # ── ARADAKİ **BİRİM** YUVALAR HİÇ KURULMAZ ────────────────
        # Evvelce ``bas``tan ``son``a bütün yuvalar için bir
        # ``(2,2,2,2)`` tensör kuruluyordu; ``mpo_uygula`` ise onların
        # ``W[0,:,:,0]`` kesitini alıp **kimlik olduğu için atıyordu**.
        # Yâni işaret başına yüzlerce tensör kuruluyor, hepsi
        # kuruldukları yerde çöpe gidiyordu. Ölçüldü: tek küllî mizan
        # çağrısında ``numpy.zeros`` 15 678 kere çağrılıyor ve ezici
        # çoğunluğu buradan geliyor.
        #
        # **NETİCE BİREBİR AYNIDIR** ve bu bir yaklaşıklık değildir:
        # kimlik kapısı duruma vurulunca durumu hiç değiştirmez; onu
        # kurmamak ile kurup atmak arasında **hesap farkı yoktur**,
        # yalnız masraf farkı vardır.
        W: Dict[int, np.ndarray] = {}
        for j in yuv:
            T = np.zeros((2, 2, 2, 2))
            T[0, 0, 0, 0] = T[0, 1, 1, 0] = 1.0          # birim kanalı
            b = int(orutu_[j]) & 1
            T[1, b, b, 1] = 1.0                          # yalnız aranan bit
            W[j] = T
        return q.y.mpo_uygula(W, 2, bas=bas, son=son,
                              sol_sinir=np.array([1.0, -2.0]),
                              sag_sinir=np.array([1.0, 1.0]))

    if orutu is not None or ne == "örüntü":
        return isaret(orutu or {})

    kesme = 0.0

    if ne in ("işaret", "hepsi"):
        CZ = np.eye(4, dtype=np.float64)
        CZ[3, 3] = -1.0
        tas0 = q.kulli("tasdik", 0)
        tas1 = q.kulli("tasdik", 1)
        nak0 = q.kulli("nakz", 0)
        miz0 = q.kulli("mizan", 0)
        kel0 = q.kulli("kelam", 0)
        gay0 = q.kulli("gaye", 0)
        # 1) tenakuzsuzluk: |tasdik=1, nakz=1⟩
        q.uzak_cift(tas0, nak0, CZ)
        # 2) ayniyet: |tasdik₀=1, tasdik₁=0⟩. ``X`` ile sarmak, ikinci
        #    kübitin ``|0⟩`` hâlini kontrol yapar.
        q.tek(tas1, degil_x())
        q.cift(tas0, CZ)
        q.tek(tas1, degil_x())
        # 3) kâfi sebep: |tasdik=1, mîzân₀=0⟩
        q.tek(miz0, degil_x())
        q.uzak_cift(tas0, miz0, CZ)
        q.tek(miz0, degil_x())
        # 4) KELÂM ŞARTI (H108). H107'de ölçüldü: kalbin ``beyan``
        #    üzerindeki tesiri yalnız 0,6x idi, çünkü ``beyan``
        #    ``kelam``dan okunur ve kapı ``kelam``a hiç dokunmuyordu --
        #    kalp hükmü idare ediyor, KELÂMI etmiyordu.
        q.tek(tas0, degil_x())
        q.uzak_cift(kel0, tas0, CZ)
        q.tek(tas0, degil_x())
        # 5) SÜKÛT ŞARTI (H10): sükût kusur değil fazilettir, fakat
        #    hükümle beraber olamaz.
        q.uzak_cift(q.kulli("sukut", 0), tas0, CZ)
        # 6) GAYE ŞARTI: gaye ile hüküm AYRIŞAMAZ; iki kol da (XOR).
        q.tek(gay0, degil_x())
        q.uzak_cift(tas0, gay0, CZ)          # |tasdik=1, gaye=0⟩
        q.tek(gay0, degil_x())
        q.tek(tas0, degil_x())
        q.uzak_cift(tas0, gay0, CZ)          # |tasdik=0, gaye=1⟩
        q.tek(tas0, degil_x())

    if ne in ("usul", "hepsi"):
        us = USULLER if usuller is None else usuller
        _, kac = q._alan["tertip"]
        yuv = [q.kulli("tertip", j) for j in range(kac)]
        # süperpozisyon: her usul hem denenir hem denenmez
        q.tek_yigin(yuv, np.stack([donme(0.25 * math.pi)] * len(yuv)))
        cetvel = _yasak_cetveli()
        yer = dict(ALANLAR)
        for i, u in enumerate(us[:kac]):
            for yasak in cetvel.get(u.ad, []):
                # Yalnız formülün bağlı olduğu alanlar kısıtlanır;
                # ötekiler serbest bırakılır.
                o = {q.kulli(ad, yer[ad]): b for ad, b in yasak.items()}
                o[yuv[i]] = 1                 # o usul AÇIK olan kolda
                kesme += isaret(o)

    if ne in ("intaç", "hepsi"):
        yuv = sorted({q.kulli(ad, j) for ad in HUKUM_ALANLARI
                      for j in range(q._alan[ad][1])})
        for _ in range(max(1, int(tur))):
            q.tek_yigin(yuv, np.stack([donme(-0.25 * math.pi)] * len(yuv)))
            kesme += isaret({int(j): 0 for j in
                             range(min(yuv), max(yuv) + 1)})
            q.tek_yigin(yuv, np.stack([donme(0.25 * math.pi)] * len(yuv)))

    return float(kesme)


def taahhude_yuzlestir(sinif=None, dS=None, nefs=None,
                       E=None, ayar=None):
    """MELEKE SÖZÜNÜ TUTTU MU -- **tek terkip** (kütük H222).

    Küme: ``sinif_ihlali`` + ``yuzlestir``. İkincisi birincisini satır
    satır çağırıyordu; ikisi tek bir sualin iki ölçeğidir -- "bu meleke
    taahhüt ettiği işi yaptı mı?" Tek kapıda birleşti:

    * ``sinif`` ve ``dS`` verilirse **tek satırlık** ihlâl döner (float).
    * verilmezse 44 melekenin hepsi koşturulup **cetvel** döner:
      ``no, ad, sınıf, ΔS, ihlâl, uydu_mu``.

    Her sınıf ``ΔS`` için bir **bölge** taahhüt eder; ihlâl, o bölgeye
    olan **eksikliktir**::

        kurucu    : ΔS ≥ +B      ihlâl = tanh(max(0, B − ΔS))
        çözücü    : ΔS ≤ −B      ihlâl = tanh(max(0, B + ΔS))
        koruyucu  : |ΔS| ≤ B     ihlâl = tanh(max(0, |ΔS| − B))

    **Niçin bölge, yalnız işaret değil (H157).** İlk hâli "cihet
    tutuyorsa ihlâl yok" diyordu. Ölçünce görüldü ki melekelerin çoğu
    ``±0,0000`` okuyor -- ve sıfır, hiçbir cihete ters düşmediği için
    **her taahhüde uyuyor** sayılıyordu. Yani hiç çözmeyen 𝒪₅ Tecrit
    "tam uydu" notu alıyordu: tam da H148'in kapatmaya çalıştığı borç,
    ölçünün körlüğünde saklanıyordu. Taahhüt bir **iş** taahhüdüdür;
    işi yapmamak da ihlâldir.

    ``tanh`` ile sıkıştırılır ki tek bir uçuk ölçüm bütün kaybı ele
    geçirmesin -- H145'te ölçülen "doymuş uzuv" kusuru tekrarlanmasın.
    Eksiklik ölçüsü bölge dışında her yerde **eğimlidir**; işaret ölçüsü
    ise sıfırda düz olduğu için eğitime yol göstermiyordu.
    """
    def ihlal(sn: str, d: float) -> float:
        c = SINIF_CIHETI.get(str(sn), 0)
        d = float(d)
        # ``c*d`` cihet doğruysa müsbet; bölgeye girmek için ≥ bant.
        eksik = (abs(d) - NIZAM_BANDI) if c == 0 else (NIZAM_BANDI - c * d)
        return float(np.tanh(max(0.0, eksik)))

    if sinif is not None and dS is not None:
        return ihlal(sinif, dS)

    from .kulli_kayip import olcumlu_idrak
    from .melekeler import qsicil

    if nefs is None:
        from .musahede import gorevleri_getir

        from main.egitim import KISA_CPU
        from .melekeler import QNefs
        from .qegitim import belirtecleri_kodla, ornekler
        a = ayar or KISA_CPU
        nefs = QNefs(a.tohum, a.qayar())
        nefs.idrak_et(np.zeros((2, a.veri_lifi)))
        veri = ornekler(gorevleri_getir("training")[:6], azami=2,
                        pencere=a.pencere, sozluk=a.sozluk)
        # Genişlik TABANDIR, sözlük değil (ferman 1-N).
        E = np.stack([belirtecleri_kodla(b, a.veri_lifi, a.veri_lifi)
                      for b, _ in veri])
    _q, _ok, dSler = olcumlu_idrak(nefs, E, meleke_olcumu=False,
                                   sinif_olcumu=True)
    sic = qsicil()
    out: List[Dict[str, object]] = []
    for no in sorted(dSler):
        m = sic[no]
        d = float(dSler[no])
        ih = ihlal(m.SINIF, d)
        out.append({"no": no, "ad": m.ad, "sınıf": m.SINIF,
                    "ΔS": d, "ihlâl": ih, "uydu_mu": ih <= 1e-9})
    return out




# ════════════════════════════════════════════════════════════════════
#  nefs/kod_uzayi.py
# ════════════════════════════════════════════════════════════════════

def muhru_stabilizerle_yuzlestir(q, alanlar: Sequence[str] = ("tasdik", "nakz"),
                                 n: int = 0,
                                 cz_ciftleri: Sequence[Tuple[int, int]] = (),
                                 z_yuvalari: Sequence[int] = ()
                                 ) -> Dict[str, object]:
    """MÜHÜR SAĞLAM MI -- **tek terkip** (kütük H222).

    Küme: ``hukum_kod_uzayi`` + ``kod_uzayi_dagilimi`` + ``yuzlestir``.
    Üçü zincirleme birbirini çağırıyordu ve ortadaki ikisi tek başına
    hiçbir yerde kullanılmıyordu; tek işleri, MPS'in hüküm dağılımını
    **tam** Clifford temsiliyle yüzleştirmekti.

    ``q`` verilmezse (``n > 0`` ile) yalnız kod uzayı kurulup dağılımı
    döner; verilirse MPS ile yüzleştirilir.

    Kod uzayı: ``|+⟩^n`` + ``CZ`` işaretleri. Her ``CZ(a,b)`` bir mantık
    şartının ``|11⟩`` yasağıdır. Netice **tamdır**: kesme yok, bağ boyutu
    yok, ``2^n`` açılmıyor -- durum ``(D, J)`` çiftinde ``O(n²)`` yer
    tutuyor. Dağılım ``P(y) = |⟨y|φ⟩|²`` yalnız **yüzleştirme** için
    açılır ve ``n`` küçük tutulur; maksat MPS'i denetlemektir, onun
    yerine geçmek değil.

    **Bu bir sınamadır, bir iddia değil.** Mesafe (TVD) büyükse MPS
    tarafında kesme ısırıyor demektir ve sayı onu söyler.
    """
    def kur(nn: int, cz, zy) -> StabilizerDurum:
        # ``StabilizerDurum.z`` ve ``.cz`` **yerinde** değiştirir ve
        # ``None`` döndürür; dönüşü yeniden atamak sessizce ``None``
        # verirdi.
        d = StabilizerDurum.arti(int(nn))
        for a in zy:
            d.z(int(a))
        for a, b in cz:
            d.cz(int(a), int(b))
        return d

    def dagilim(d: StabilizerDurum) -> np.ndarray:
        m = d.n
        if m > 14:
            raise ValueError("yüzleştirme için n ≤ 14 (2^n açılıyor)")
        Y = np.array([[(i >> j) & 1 for j in range(m)] for i in range(1 << m)],
                     dtype=np.int64)
        P = np.abs(np.asarray(d.genlik(Y))) ** 2
        t = float(P.sum())
        return P / t if t > 1e-30 else np.full(1 << m, 1.0 / (1 << m))

    if q is None:
        d = kur(n, cz_ciftleri, z_yuvalari)
        return {"kübit": int(n), "kod": d, "P_stab": dagilim(d)}

    yuv: List[int] = []
    for ad in alanlar:
        _, kac = q._alan[ad]
        yuv += [q.kulli(ad, j) for j in range(kac)]
    yuv = sorted(set(yuv))
    m = len(yuv)
    bas = min(yuv)
    if max(yuv) - bas + 1 != m:
        raise ValueError("yüzleştirme için alanlar bitişik olmalı")

    P_mps = np.asarray(q.blok_dagilimi(bas, m), float).ravel()

    # Aynı şartı taşıyan kod uzayı: ``|tasdik₀=1, nakz₀=1⟩`` yasağı.
    yerel = {j: i for i, j in enumerate(yuv)}
    ilk, son = alanlar[0], alanlar[-1]
    cz = [(yerel[q.kulli(ilk, 0)], yerel[q.kulli(son, 0)])]
    P_stab = dagilim(kur(m, cz, ()))

    # ``blok_dagilimi`` ilk kübiti EN ANLAMLI bit sayar; stabilizer ise
    # ``Y[:, j]`` ile ``j``. inci kübiti en anlamsız sayar. Düzen
    # varsayılmaz, **çevrilir**.
    idx = np.array([int("".join(str((i >> j) & 1)
                               for j in range(m - 1, -1, -1)), 2)
                    for i in range(1 << m)])
    P_stab = P_stab[idx]

    return {"kübit": m, "P_mps": P_mps, "P_stab": P_stab,
            "tvd": 0.5 * float(np.sum(np.abs(P_mps - P_stab))),
            "kapsanan_şart": len(cz),
            "kapsanmayan": "menfî kontrollü ve üç kontrollü şartlar"}



# ====================================================================
#  KÜME 8: Wilson holonomisi -- homotopi zırhının bağımsız şahidi
# ====================================================================

def holonomi(kenar_fazlari: Sequence[float]) -> complex:
    """``W(γ) = exp(i Σ a_e)`` — kapalı çevrim boyunca ``U(1)`` holonomisi."""
    return complex(np.exp(1j * float(np.sum(kenar_fazlari))))


def cevrim_egriligi(kenar_fazlari: Sequence[float],
                    yuz_var_mi: bool = False) -> Dict[str, object]:
    """Yerel eğrilik ve holonomi yan yana.

    Halkada (``yuz_var_mi=False``) çevrimin sınırladığı bir yüz yoktur;
    ``F`` her yerde sıfır olsa bile Stokes uygulanamaz.
    """
    W = holonomi(kenar_fazlari)
    return {"F_yerel_sıfır_mı": True, "yüz_var_mı": yuz_var_mi,
            "holonomi": W, "holonomi_trivial_mi": bool(abs(W - 1) < 1e-12),
            "faz": float(np.angle(W)),
            "toplam_akı_bölü_2pi": float(np.sum(kenar_fazlari)
                                         / (2 * math.pi))}


def duz_mu(kenar_fazlari: Sequence[float]) -> bool:
    """Bağlantı **yerel olarak** düz mü? — her yüzde eğrilik sıfır mı.

    Halkada hiç yüz yoktur, dolayısıyla cevap her zaman ``True``dur;
    mesele tam da budur.
    """
    return True


def aharonov_bohm(N: int = 8, aki_bolu_2pi: float = 0.37
                  ) -> Dict[str, object]:
    """Halka üzerinde düz bağlantı, trivial olmayan holonomi.

    Toplam akı ``N`` kenara eşit dağıtılır; her kenarın kendi
    komşuluğunda bağlantı düzdür (yüz yok), fakat çevrim holonomisi
    ``e^{2πi·akı}``dır.
    """
    a = np.full(N, 2 * math.pi * aki_bolu_2pi / N)
    d = cevrim_egriligi(a, yuz_var_mi=False)
    # kıyas: aynı akı bir DİSKTE olsaydı, Stokes uygulanır ve F ≠ 0 olurdu
    d["disk_olsaydı_F"] = 2 * math.pi * aki_bolu_2pi
    d["|W−1|"] = float(abs(d["holonomi"] - 1))
    return d


def _rapor_bukum() -> str:
    s = []
    s.append("=== M20: tünelleme O(1) DEĞİL, üstel pahalı ===")
    s.append("  genişlik      γ          T = e^{−γ}     beklenen deneme")
    for d in tunel_maliyet_cetveli((1, 2, 4, 8, 16)):
        s.append("  %8.0f   %8.4f      %.3e      %.3e"
                 % (d["genişlik"], d["γ"], d["T"], d["beklenen_deneme"]))
    s.append("  Risalenin kendi formülü T = e^{−γ} diyor; aynı sayfada")
    s.append("  'O(1) mertebesinde geçilir' demek onunla çelişiyor.")
    s.append("  Doğru kazanç: klasikte SIFIR olan olasılık POZİTİF oluyor.")

    s.append("\n=== M21: düz bağlantı, trivial OLMAYAN holonomi ===")
    for aki in (0.0, 0.25, 0.37, 0.5, 1.0):
        d = aharonov_bohm(8, aki)
        s.append("  akı/2π=%.2f   yerel F=0 mı? %s   yüz var mı? %s   "
                 "W=%+.4f%+.4fi   |W−1|=%.4f   trivial mi? %s"
                 % (aki, d["F_yerel_sıfır_mı"], d["yüz_var_mı"],
                    d["holonomi"].real, d["holonomi"].imag, d["|W−1|"],
                    d["holonomi_trivial_mi"]))
    s.append("  akı tam sayı olduğunda holonomi trivial oluyor; arada")
    s.append("  DEĞİL. F her hâlde sıfır. Yani 'F=0 ⟹ ΔΦ=0' yanlış;")
    s.append("  doğru ölçüt W(γ)=1'dir. (Aharonov–Bohm.)")

    s.append("\n=== M22: GRAPE gradyanı O(Δt²) yaklaşımı ===")
    r = np.random.default_rng(1)
    n = 4

    def herm(sd):
        A = (np.random.default_rng(sd).normal(size=(n, n))
             + 1j * np.random.default_rng(sd + 99).normal(size=(n, n)))
        return A + A.conj().T

    H0, Hk = herm(1), [herm(2), herm(3)]
    psi0 = np.zeros(n, complex); psi0[0] = 1
    hedef = np.zeros(n, complex); hedef[n - 1] = 1
    s.append("     M      Δt      sonlu fark      GRAPE        fark      "
             "fark/Δt²")
    for M in (10, 20, 40, 80, 160):
        om = [np.full(M, 0.3), np.full(M, -0.2)]
        dt = 1.0 / M
        j, k = M // 3, 0
        sf = sonlu_fark_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        g = grape_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        s.append("  %5d  %.5f  %+.8f  %+.8f  %.2e  %.4f"
                 % (M, dt, sf, g, abs(g - sf), abs(g - sf) / dt ** 2))
    s.append("  'fark/Δt²' sütunu sabitleniyor: hata tam olarak O(Δt²).")
    s.append("  Kaynak bunu EŞİTLİK olarak yazıyor; yaklaşımdır.")

    s.append("\n=== Tam (Fréchet) gradyan sonlu farkla uyuşuyor mu? ===")
    for M in (10, 20, 40):
        om = [np.full(M, 0.3), np.full(M, -0.2)]
        j, k = M // 3, 0
        sf = sonlu_fark_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        tam = tam_gradyan(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        yak = grape_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        s.append("  M=%3d  sonlu fark=%+.10f   tam=%+.10f (fark %.2e)   "
                 "GRAPE=%+.10f (fark %.2e)"
                 % (M, sf, tam, abs(tam - sf), yak, abs(yak - sf)))

    s.append("\n=== GRAPE gerçekten çalışıyor mu? ===")
    d = grape_kos(H0, Hk, psi0, hedef, 1.0, M=40, tur=300)
    s.append("  başlangıç sadakat = %.6f   son sadakat = %.6f"
             % (d["seyir"][0], d["sadakat"]))
    s.append("  tekdüze artıyor mu? %s   (tur sayısı %d)"
             % (d["tekdüze_mi"], len(d["seyir"])))
    s.append("  Yaklaşık gradyan eniyilemeyi bozmuyor: adım kabul ölçütü")
    s.append("  sadakati doğrudan sınadığı için yanlış yöne gidilmiyor.")
    return "\n".join(s)

def rapor() -> str:                                     # pragma: no cover
    """KENDİNİ GÖSTERME -- **tek terkip** (kütük H222, birleşik tur).

    Küme: yedi ayrı ``rapor()`` (dokuz dosyadan altısında) + ``_gosterim``.
    Her biri kendi ``s`` listesini kurup ayrı ayrı ``"\\n".join`` ediyordu;
    çipin bütün veçheleri artık **tek** gösterimde, sırayla akar.

    Bir zırhın raporu, süzgeçlerin adını saymakla olmaz; her birinin
    fiilen ısırdığı, kasten bozuk bir girdide **kırmızıya döndüğü**
    görülmelidir (H126, H90).
    """
    s: List[str] = ["ZIRH ÇİPİ -- Küme 3 tevhidi"]
    s.append("")
    s.append("=" * 70)
    s.append("  DÖRTLÜ TOPOLOJİK SÜZGEÇ -- gayenin kendisi")
    s.append("=" * 70)
    s += ["DÖRTLÜ TOPOLOJİK ZIRH -- gayenin kendisi", ""]

    s.append("=== Betti: delik VAR mı? (kırmızı/yeşil) ===")
    # Bir çember: 8 nokta, tek delik → b₁ = 1 (KIRMIZI)
    aci = np.linspace(0, 2 * math.pi, 8, endpoint=False)
    cember = np.stack([np.cos(aci), np.sin(aci)], axis=1)
    Dc = np.sqrt(((cember[:, None] - cember[None]) ** 2).sum(2))
    Kc = vietoris_rips(Dc, 0.9, azami_boyut=2)
    r1 = delik(Kc, 1)
    s.append("  çember (delik)  : b₁=%.0f  boşluk=%.4f  kayıp=%.1f"
             % (r1["betti"], r1["boşluk"], r1["kayıp"]))
    # Dolu disk: delik yok → b₁ = 0 (YEŞİL)
    rng = np.random.default_rng(0)
    disk = rng.normal(size=(14, 2))
    disk = disk / np.maximum(np.linalg.norm(disk, axis=1, keepdims=True), 1)
    disk = disk * rng.uniform(0, 1, (14, 1)) ** 0.5
    Dd = np.sqrt(((disk[:, None] - disk[None]) ** 2).sum(2))
    Kd = vietoris_rips(Dd, 1.2, azami_boyut=2)
    r2 = delik(Kd, 1)
    s.append("  dolu disk       : b₁=%.0f  boşluk=%.4f  kayıp=%.1f"
             % (r2["betti"], r2["boşluk"], r2["kayıp"]))

    s.append("")
    s.append("=== Kohomoloji: mana adaları (b₀ − 1) ===")
    iki = np.vstack([rng.normal(size=(6, 2)) * 0.2,
                     rng.normal(size=(6, 2)) * 0.2 + 10.0])
    Di = np.sqrt(((iki[:, None] - iki[None]) ** 2).sum(2))
    Ki = vietoris_rips(Di, 0.8, azami_boyut=1)
    k1 = delik(Ki, 0)
    s.append("  iki kopuk ada   : b₀=%.0f  kayıp=%.1f   ← KIRMIZI"
             % (k1["betti0"], k1["kayıp"]))
    Kb = vietoris_rips(Di, 16.0, azami_boyut=1)
    k2 = delik(Kb, 0)
    s.append("  bağlanmış       : b₀=%.0f  kayıp=%.1f"
             % (k2["betti0"], k2["kayıp"]))

    s.append("")
    s.append("=== Sheaf ve Homotopi ===")
    a = np.array([1.0, 2.0, 3.0])
    s.append("  uyumlu ek yeri  : ‖ΔRes‖² = %.3e"
             % yama(a, a)["uyumsuzluk"])
    s.append("  uyumsuz ek yeri : ‖ΔRes‖² = %.3f   ← KIRMIZI"
             % yama(a, a + np.array([0.0, 0.5, -0.3]))["uyumsuzluk"])
    from nefs.zihin_durumu import donme
    kapali = [donme(0.4), donme(-0.4)]
    acik = [donme(0.4), donme(0.1)]
    s.append("  kapanan çevrim  : |W−I| = %.3e"
             % iz(kapali)["sapma"])
    s.append("  kapanmayan      : |W−I| = %.4f   ← KIRMIZI"
             % iz(acik)["sapma"])

    s.append("")
    s.append("=== Küllî zırh kaybı (yumuşak âzamî) ===")
    s.append("  dördü de sıfır      : L = %.3e"
             % zirh_kaybi()["kayıp"])
    s.append("  yalnız biri bozuk   : L = %.4f   (düz ortalama %.4f olurdu)"
             % (zirh_kaybi(betti=1.0)["kayıp"], 1.0 / 4.0))
    s.append("  dördü de bozuk      : L = %.4f"
             % zirh_kaybi(1.0, 1.0, 1.0, 1.0)["kayıp"])
    s.append("")
    s.append("=" * 70)
    s.append("  OPERATÖRE ZIRH GİYDİRME")
    s.append("=" * 70)
    rng = np.random.default_rng(0)
    s += ["OPERATÖRE ZIRH GİYDİRME", ""]
    for ad, H in (("rastgele", rng.normal(size=(12, 12))),
                  ("birim (temiz)", np.eye(12)),
                  ("tam bağlı", np.ones((12, 12)))):
        _Hz, r = zirhla(H)
        s.append("  %-14s sheaf=%.4f betti=%.0f koho=%.4f homotopi=%.4f "
                 "toplam=%.4f"
                 % (ad, r["sheaf_uyumsuzluk"], r["betti_delik_sayisi"],
                    r["kohomoloji_tikaniklik"], r["homotopi_burulma"],
                    r["toplam_kayip"]))
    s.append("")
    s.append("  Satırlar birbirinden AYRI çıkmalı; hepsi aynı çıkarsa")
    s.append("  zırh ölçmüyor demektir.")
    s.append("")
    s.append("=" * 70)
    s.append("  DALGAYA ZIRH GİYDİRME")
    s.append("=" * 70)
    from idrak.kategori import Uzay

    s += ["ENİNE TOPOLOJİK ZIRH -- dört süzgeç, dördü de ısırıyor mu?", ""]
    n = 24
    k = n

    def kos(z: np.ndarray, onceki=None) -> ZirhIzi:
        y = Yazmac(8, bag=4, tohum=0)
        v = np.concatenate([z, np.zeros_like(z)])
        u = Uzay(yuva=0, mertebe=1, tam_kuruldu=True, denetlendi=True,
                 baglayici=0, tip_ozeti="sınama")
        return zirhla(y, u=u, okuma=v, onceki=onceki)[1]

    duz = np.linspace(-0.2, 0.2, k)
    kopuk = duz.copy()
    kopuk[k // 2:] += 3.0                     # tek büyük sıçrama → β₀ = 2
    dalgali = np.sin(np.linspace(0, 12, k))
    menfi = -np.abs(duz) - 0.5                # baskın bileşen menfî

    s.append("  %-14s %-12s %-8s %-10s %s"
             % ("okuma", "sheaf", "işaret", "β₀", "betti cezası"))
    for ad, z in (("düz", duz), ("kopuk", kopuk),
                  ("dalgalı", dalgali), ("menfî", menfi)):
        zi = kos(z)
        s.append("  %-14s %-12.4f %-8.0f %-10d %.4f"
                 % (ad, zi.sheaf_duzeltme, zi.homotopi_isaret,
                    zi.betti0, zi.betti_ceza))

    s.append("")
    s.append("  Kohomoloji: **önceki okumaya dik** bileşen yutuluyor mu?")
    onc = np.concatenate([duz, np.zeros_like(duz)])
    for ad, z in (("aynı yön", duz), ("dik yön", dalgali)):
        zi = kos(z, onceki=onc)
        s.append("    %-10s tıkanıklık = %.4f" % (ad, zi.tikaniklik))
    s.append("    (dik yönde tıkanıklık 1'e yaklaşmalı; yaklaşmıyorsa")
    s.append("     dördüncü süzgeç ölüdür.)")
    s.append("")
    s.append("=" * 70)
    s.append("  TOPOLOJİ: kompleks, Betti, barkod, mesafe")
    s.append("=" * 70)
    from fractions import Fraction
    s += []

    s.append("=== ∂∘∂ = 0 ölçülüyor ===")
    rng = np.random.default_rng(0)
    P = rng.normal(size=(9, 3))
    K = vietoris_rips(_mesafe(P), 2.2, azami_boyut=3)
    s.append("  simpleks sayıları: "
             + ", ".join(f"|C_{k}|={len(v)}" for k, v in sorted(K.items())))
    for k in (1, 2, 3):
        B1 = delik(K, k, "sınır")
        B2 = delik(K, k + 1, "sınır")
        if B1.size and B2.size:
            s.append(f"  ‖∂_{k}∘∂_{k+1}‖∞ = "
                     f"{np.max(np.abs(B1 @ B2)):.2e}")

    s.append("\n=== Bilinen şekillerde Betti sayıları ===")
    ornekler = [
        ("3 ayrık nokta", np.array([[0., 0.], [10., 0.], [0., 10.]]),
         0.5, (3, 0)),
        ("çember (16 nokta)", _cember(16), 0.5, (1, 1)),
        ("iki çember", _iki_cember(12), 0.6, (2, 2)),
        ("dolu üçgen", np.array([[0., 0.], [1., 0.], [0.5, 0.87]]),
         1.5, (1, 0)),
    ]
    for ad, P_, eps, (b0, b1) in ornekler:
        Kx = vietoris_rips(_mesafe(P_), eps, azami_boyut=2)
        o0, o1 = delik(Kx, 0, "betti"), delik(Kx, 1, "betti")
        s.append(f"  {ad:20s} ε={eps:.2f}  β₀={o0} (bekl. {b0})"
                 f"   β₁={o1} (bekl. {b1})"
                 f"   χ={delik(Kx, 0, chr(101)+chr(117)+chr(108)+chr(101)+chr(114))}")

    s.append("\n=== K25: Tikhonov çekirdeği yok ediyor ===")
    Kc = vietoris_rips(_mesafe(_cember(16)), 0.5, azami_boyut=2)
    D0 = delik(Kc, 0, "laplasyen")
    oz = np.linalg.eigvalsh(D0)
    s.append(f"  ker Δ₀ boyutu = {int(np.sum(np.abs(oz) < 1e-9))}  (β₀)")
    for eps in (1e-6, 1e-3):
        oz_e = np.linalg.eigvalsh(D0 + eps * np.eye(D0.shape[0]))
        s.append(f"  ε={eps:.0e}: ker(Δ₀+εI) boyutu = "
                 f"{int(np.sum(np.abs(oz_e) < 1e-9))}"
                 f"   ε-eşikli sayım = {int(np.sum(oz_e <= eps + 1e-9))}")
    s.append("  Düzenleme çekirdeği siliyor; Betti eşikli SAYIMLA okunmalı.")

    s.append("\n=== Kalıcılık: gürültü ile hakiki delik ===")
    r = np.random.default_rng(3)
    P2 = _cember(24) + 0.03 * r.normal(size=(24, 2))
    esikler = np.linspace(0.05, 2.2, 40)
    cub0 = dogum_olum_cetveli(_mesafe(P2), esikler, k=0)["çubuklar"]
    cub1 = dogum_olum_cetveli(_mesafe(P2), esikler, k=1)["çubuklar"]
    s.append(f"  β₀ barkodu: {len(cub0)} çubuk, "
             f"en uzun {max(d - b for b, d in cub0):.3f}")
    s.append(f"  β₁ barkodu: {len(cub1)} çubuk, "
             f"en uzun {max((d - b for b, d in cub1), default=0):.3f}")
    for tau in (0.0, 0.1, 0.5, 1.0):
        s.append(f"    τ={tau:.1f} süzgecinden geçen: "
                 f"β₀ {len([c for c in cub0 if c[1] - c[0] >= tau])}, "
                 f"β₁ {len([c for c in cub1 if c[1] - c[0] >= tau])}")

    s.append("\n=== Bottleneck mesafesi ===")
    A = [(0.0, 1.0), (0.2, 0.9)]
    B = [(0.0, 1.0), (0.2, 0.9)]
    s.append(f"  aynı barkod: {cetveller_arasi_mesafe(A, B):.6f}  (0 olmalı)")
    C = [(0.0, 1.0), (0.2, 0.9), (0.5, 0.52)]
    s.append(f"  kısa bir çubuk eklendi: {cetveller_arasi_mesafe(A, C):.6f}"
             f"   (o çubuğun köşegene mesafesi = {(0.52-0.5)/2:.3f})")
    Dd = [(0.0, 1.3), (0.2, 0.9)]
    s.append(f"  bir çubuk 0.3 uzadı: {cetveller_arasi_mesafe(A, Dd):.6f}")
    s.append(f"  boş barkodla: {cetveller_arasi_mesafe(A, []):.6f}"
             f"   (en uzun çubuğun yarısı = {1.0/2:.3f})")

    s.append("\n=== Kahan toplaması: hata N'den bağımsız (K32) ===")
    s.append("        N     naif hata     Kahan hata    naif/Kahan")
    for N in (1_000, 10_000, 100_000):
        rr = np.random.default_rng(N)
        xs = rr.normal(0, 1, N) * 10.0 ** rr.integers(-8, 8, N)
        tam = float(sum(Fraction(float(x)) for x in xs))
        olcek = float(np.sum(np.abs(xs)))
        naif = 0.0
        for x in xs:
            naif += float(x)
        h_naif = abs(naif - tam) / olcek
        h_kahan = abs(kahan_toplam(xs) - tam) / olcek
        oran = h_naif / h_kahan if h_kahan > 0 else float("inf")
        s.append(f"  {N:9d}   {h_naif:.3e}    {h_kahan:.3e}"
                 f"    {oran:>8.1f}×")
    eps = np.finfo(float).eps
    s.append(f"  makine epsilon = {eps:.3e}; Kahan hatası birkaç eps")
    s.append("  mertebesinde ve N ile BÜYÜMÜYOR — kaidenin söylediği bu.")
    s.append("")
    s.append("=" * 70)
    s.append("  DOLAŞIKLIK NİZAMI -- ilan ile ölçümün yüzleşmesi")
    s.append("=" * 70)
    s += ["=== DOLAŞIKLIK NİZAMI -- ilan ile ölçümün yüzleştirilmesi ===",
         "",
         "Her meleke bir SINIF ilan eder; taahhüdü ΔS'in bölgesidir:",
         "  kurucu ΔS≥+%.2f   çözücü ΔS≤−%.2f   koruyucu |ΔS|≤%.2f"
         % (NIZAM_BANDI, NIZAM_BANDI, NIZAM_BANDI),
         "",
         "  𝒪   meleke               sınıf      ΔS       ihlâl"]
    satir = taahhude_yuzlestir()
    uyan = 0
    for r in satir:
        uyan += bool(r["uydu_mu"])
        s.append("  %-3d %-20s %-10s %+8.4f  %.4f%s"
                 % (r["no"], r["ad"], r["sınıf"], r["ΔS"], r["ihlâl"],
                    "" if r["uydu_mu"] else "   ← İHLÂL"))
    s += ["",
          "%d/%d meleke ilanına uyuyor." % (uyan, len(satir)),
          "",
          "İhlâl bir kusur değil bir **eğitim işareti**dir: ölçü",
          "`nefs/kulli_kayip.py`nin öğrenilebilir kaybına girer, yani",
          "meleke 'çözücüyüm' dediği için değil FİİLEN çözdüğü için",
          "çözücü olur. 𝒪₅ Tecrit'in H148'de açık kalan borcu budur:",
          "sabit bir üniter keyfî bir durumu çözemez; çözücülük ancak",
          "eğitilerek kazanılır, iddia edilerek değil."]
    s.append("")
    s.append("=" * 70)
    s.append("  STABILIZER MÜHRÜ")
    s.append("=" * 70)
    s += ["MANTIK KOD UZAYI -- stabilizer ile MPS'in yüzleştirilmesi", ""]

    s.append("  1) Clifford devresinde dağılım TAM mı?")
    for n, cz in ((4, [(0, 1)]), (6, [(0, 1), (2, 3), (4, 5)]),
                  (8, [(i, i + 1) for i in range(7)])):
        r = muhru_stabilizerle_yuzlestir(None, n=n, cz_ciftleri=cz)
        d, P = r["kod"], r["P_stab"]
        s.append("    n=%d, %d CZ → Σ P = %.15f, sıfır olmayan hâl %d/%d"
                 % (n, len(cz), float(P.sum()),
                    int(np.sum(P > 1e-15)), 1 << n))
    s.append("    (Σ P tam 1; hiçbir bağ boyutu, hiçbir kesme yok.)")

    s.append("")
    s.append("  2) MPS ile yüzleştirme (tasdik ⊗ nakz bloğu)")
    from nefs.zihin_durumu import QAyar, QYazmac
    rng = np.random.default_rng(0)
    for bag in (4, 8, 16):
        q = QYazmac(4, QAyar())
        q.kodla(rng.normal(size=(4, 8)))
        q.superpozisyon()
        q.harman()
        # ``tasdik`` ile ``nakz`` arasında ``sukut`` var; bitişik
        # olan çift ``tenakuz`` ile ``tasdik``tır. Bitişiklik şartı
        # gevşetilmiyor, ona uyan alanlar seçiliyor.
        r = muhru_stabilizerle_yuzlestir(q, alanlar=("tenakuz", "tasdik"))
        s.append("    χ=%-3d kübit=%d  TVD(MPS, stabilizer) = %.4f"
                 % (bag, r["kübit"], r["tvd"]))
    s.append("    Kapsanmayan: %s" % r["kapsanmayan"])
    s.append("    (TVD büyük çıkması bir kusur DEĞİL bir teşhistir: iki")
    s.append("     temsil aynı devreyi taşımıyor -- MPS akışın tamamını,")
    s.append("     stabilizer yalnız iki-kontrollü müsbet şartı görüyor.)")
    return "\n".join(s)


if __name__ == "__main__":                              # pragma: no cover
    print(rapor())

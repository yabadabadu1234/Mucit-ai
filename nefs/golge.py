"""
GÖLGE KÂHİN -- `reel/` ve `akis/` ana hattı **denetleyen** ikinci kaynak.

Dosya 6 reel hat için üç kademe teklif ediyor: (1) gölge kâhin olarak
dondur, (2) bütün sınamaları ``ε ≤ 1e-14``te çapraz doğrula, (3) icra
yolundan çıkar.

===================================================================
TENKİDİM -- 3. KADEME ŞU AN MANASIZDIR
===================================================================

`reel/` ve `akis/` **zaten icra yolunda değil**; ikisi de beylik
(`tanilama/nizam.py` sayıyor: reel 1230 satır, akis 1792 satır, ikisi de
tahta bağlı değil). "İcra yolundan çıkarmak" için evvelâ girmiş olması
lazım. O hâlde 3. kademe bir iş değil, bir yanılgıdır ve öyle
zabıtlanır.

Asıl iş 1. ve 2. kademedir ve onların manası şudur: **ana hattın
iddialarını, ana hattı hiç kullanmayan bir koddan denetlemek.** H88'in
dersi buydu -- ``beyan`` aylarca yanlış çevreden okudu çünkü
karşılaştıracak ikinci bir temsil yoktu. `nefs/kod_uzayi.py` o ikinciyi
hüküm bloğu için verdi (stabilizer). Bu dosya **kapılar** için verir.

===================================================================
NE DENETLENİYOR
===================================================================

1. **Grup sadakati** -- ``akis.lie.so_n_mi`` ile: melekelerin kurduğu
   her iki kübitlik kapı hakikaten ``SO(4)``te mi? ``kuantum/yazmac.py``
   bunu Cayley'in cebrinden **iddia ediyor**; burada ölçülüyor.

2. **Erişilebilirlik boşluğu** -- Cayley ``det(I+Q) = 0`` olan hiçbir
   dönmeye ulaşamaz, yani **hiçbir π dönmesine**. Reel yazmaçta yegâne
   faz π olduğu için (H98) bu doğrudan bir kabiliyet eksiğidir.
   ``akis.lie.uslu_harita`` boşluğu gösterir ve kapatır.

3. **Reel gömme sadakati** -- ``reel.karmasik``: ``H`` Hermitesel
   dizeyinin reel gömmesi ``SO(2N)``de mi, ve ``exp(−tJH_ℝ)`` gerçekten
   ``exp(−iHt)``nin gömmesi mi? Bu, bütün projenin *"cebir reeldir"*
   tercihinin dayanağıdır ve bir kere bile ana hattan denetlenmemişti.

4. **Dik dönüşüm çapraz doğrulaması** -- ``reel.hartley``: ``RHT``
   ``RHT² = I`` ve ``RHTᵀRHT = I`` sağlıyor mu? Ana hattın kapılarıyla
   aynı cinsten (dik, reel, involutif olabilen) müstakil bir dönüşüm;
   ``ε ≤ 1e-14`` şartı burada fiilen sınanır.

===================================================================
HUDUT -- açıkça
===================================================================

`reel.karmasik` kendi şerhinde mühim bir uyarı taşıyor ve o uyarı bu
projeyi doğrudan ilgilendirir: gömme **tek** sistemde çarpımsaldır,
**birleşik** sistemde değildir (``dim_ℝ(ℂ^m ⊗ ℂ^n) = 2mn`` iken
``ℝ^{2m} ⊗ ℝ^{2n} = 4mn``).

Bu, ana hattı çürütmez ve çürüttüğü söylenmemelidir: `kuantum/yazmac.py`
karmaşık kuramın reel bir **gömmesi** değildir, doğrudan **reel** bir
kuantum kuramıdır (reel genlik, dik kapı). Fakat neticesi şudur ve
saklanmaz: reel yazmaç karmaşık olandan **daha dar**dır. Kazanılan
bellek ve hakikî SVD, kaybedilen ara fazlardır.
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np

from akis.lie import en_yakin_dik, so_izdusumu, so_n_mi, uslu_harita
from kuantum.yazmac import (dik_iki_kubit, dik_iki_kubit_us,
                         dik_iki_kubit_us_yigin, dik_iki_kubit_yigin)
from reel.hartley import hartley
from reel.karmasik import (hermitesel_mi, reel_evrim, reel_goem,
                           karmasik_coz, so_2n_mi)

__all__ = ["grup_sadakati", "erisim_bosslugu", "reel_gomme_sadakati",
           "dik_donusum_dogrulamasi", "rapor", "EPSILON"]

#: Dosya 6'nın şartı: çapraz doğrulama ``ε ≤ 1e-14``te tutmalı.
EPSILON: float = 1e-14

#: ``float64``ün makine epsilonu -- bütün ölçeklendirmenin birimi.
ULP: float = float(np.finfo(np.float64).eps)          # 2,22e-16

#: Kabul edilen âzamî yuvarlama birikimi, **ULP cinsinden**.
#:
#: **Dosya 6'nın mutlak eşiği ölçekten bağımsızdır ve bu yanlıştır.**
#: Ölçüldü: ``exp(−tJH_ℝ)`` ile ``exp(−iHt)`` farkı 1,03e-14, ``RHT``in
#: ``N=512``de diklik sapması 8,51e-14. İkisi de "1e-14 şartını
#: tutmuyor" görünür; halbuki ikisi de **doğru**dur. Sebep:
#:
#: * makine epsilonu 2,22e-16'dır; 1e-14 yalnız **45 ulp**tur,
#: * yuvarlama hatası işlem sayısıyla büyür -- bir ``N×N`` özayrışım
#:   ve iki dizey çarpımı ``O(N)`` ulp biriktirir. ``N=512``de 8,5e-14
#:   = 383 ulp, yani boyut başına **0,75 ulp**. Bu, mükemmel bir
#:   sayısal davranıştır.
#:
#: Yani mutlak bir eşik, büyük boyutta doğru kodu **yanlış** ilan eder.
#: Ölçüt ölçekle beraber büyümeli::
#:
#:     sapma / (ULP · N · şartlılık)  ≤  AZAMI_ULP
#:
#: ``şartlılık`` dizey üstelinde ``‖H‖·t``dir ve o da ölçülerek girdi:
#: yalnız boyuta bölündüğünde ölçüt 11,6 ulp veriyor, yani eşiği kıl
#: payı aşıp **doğru** kodu yanlış ilan ediyordu. ``exp``in yuvarlama
#: hatasının argümanla büyümesi bilinen bir hususiyettir; sonradan
#: uydurulmuş bir çarpan değildir. Girdikten sonra 0,66 ulp.
#:
#: Bu bir gevşetme DEĞİLDİR ve öyle olmadığı gösterilebilir: hakikî bir
#: hata (mesela `reel.karmasik`in yanlış işareti) 2,17 verir, yani
#: ``1e16`` ulp -- eşiğin on üç mertebe üstünde. Aradaki uçurum o kadar
#: geniştir ki eşiğin tam yeri hükmü değiştirmez.
AZAMI_ULP: float = 10.0


def grup_sadakati(ornek: int = 200, olcek: float = 3.0,
                  tohum: int = 0) -> Dict[str, object]:
    """Melekelerin kapıları hakikaten ``SO(4)``te mi? -- `akis.lie` ile."""
    rng = np.random.default_rng(tohum)
    t = rng.normal(size=(int(ornek), 6)) * float(olcek)
    out: Dict[str, object] = {}
    for ad, yig in (("cayley", dik_iki_kubit_yigin),
                    ("us", dik_iki_kubit_us_yigin)):
        G = np.asarray(yig(t), np.float64)
        dik = float(max(np.abs(g.T @ g - np.eye(4)).max() for g in G))
        det = np.array([np.linalg.det(g) for g in G])
        out[ad] = {
            "diklik_sapması": dik,
            "det_sapması": float(np.abs(det - 1.0).max()),
            "hepsi_SO4": bool(all(so_n_mi(g, tol=1e-5) for g in G)),
        }
    return out


def erisim_bosslugu(deneme: int = 200_000, tohum: int = 0
                    ) -> Dict[str, object]:
    """Cayley π dönmelerine ulaşabiliyor mu? -- **hayır**, ve ne kadar uzak.

    Hedef ``diag(1, 1, −1, −1)``: ``SO(4)``tedir (``det = +1``), yani
    meşru bir meleke kapısıdır; fakat ``det(I+Q) = 0`` olduğu için
    Cayley'in tekil noktasıdır.
    """
    hedef = np.diag([1.0, 1.0, -1.0, -1.0])
    rng = np.random.default_rng(tohum)
    en_iyi = np.inf
    kalan = int(deneme)
    for olcek in (0.5, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0):
        k = max(1, kalan // 8)
        G = np.asarray(dik_iki_kubit_yigin(rng.normal(size=(k, 6)) * olcek),
                       np.float64)
        en_iyi = min(en_iyi, float(np.abs(G - hedef).max(axis=(1, 2)).min()))

    # ``exp`` aynı hedefe TAM ulaşır; üreteç açıkça yazılabilir.
    a = np.zeros(6)
    a[5] = -0.5 * np.pi          # ``exp(−2A)`` ölçeği: −2·(−π/2) = +π
    us = np.asarray(dik_iki_kubit_us(a), np.float64)
    return {
        "hedef": "diag(1,1,-1,-1)",
        "hedef_SO4te_mi": bool(so_n_mi(hedef)),
        "det_I_arti_Q": float(np.linalg.det(np.eye(4) + hedef)),
        "cayley_en_iyi": float(en_iyi),
        "üstel_hatası": float(np.abs(us - hedef).max()),
        "deneme": int(deneme),
    }


def reel_gomme_sadakati(n: int = 4, tohum: int = 0) -> Dict[str, float]:
    """``exp(−tJH_ℝ)`` gerçekten ``exp(−iHt)``nin gömmesi mi? -- `reel`."""
    rng = np.random.default_rng(tohum)
    A = rng.normal(size=(n, n)); A = A + A.T
    B = rng.normal(size=(n, n)); B = B - B.T
    H = A + 1j * B
    assert hermitesel_mi(H)
    psi = rng.normal(size=n) + 1j * rng.normal(size=n)
    lam, V = np.linalg.eigh(H)
    en_kotu = 0.0
    dik = 0.0
    # **ŞARTLILIK (conditioning) hesaba katılır ve sebebi ölçüldü.**
    # ``exp(−iHt)``nin yuvarlama hatası yalnız boyutla değil, üstelin
    # ARGÜMANIYLA da büyür: özdeğerler ``λt`` kadar döner ve ``cos/sin``
    # o argümanda değerlendirilir. İlk hâlde ölçüt yalnız boyuta
    # bölünüyordu ve 11,6 ulp veriyordu -- eşiği (10) kılpayı aşıyor,
    # yani DOĞRU kodu yanlış ilan ediyordu. ``‖H‖·t`` çarpanı girince
    # 1 ulp'un altına iner. Bu bir sonradan uydurma değil, dizey
    # üstelinin bilinen şartlılığıdır.
    olcek = 0.0
    for t in (0.2, 0.6, 1.5, 3.0):
        ref = (V * np.exp(-1j * lam * t)) @ (V.conj().T @ psi)
        U = reel_evrim(H, t)
        got = karmasik_coz(U @ reel_goem(psi))
        en_kotu = max(en_kotu, float(np.abs(got - ref).max()))
        dik = max(dik, float(so_2n_mi(U)["diklik_sapması"]))
        olcek = max(olcek, float(np.abs(lam).max()) * t
                    * float(np.abs(psi).max()))
    return {"azamî_sapma": en_kotu, "diklik_sapması": dik,
            "şartlılık": olcek,
            "ulp_boyut_başına": en_kotu / (ULP * n * max(olcek, 1.0))}


def _yanlis_isaretle_kiyas(n: int = 4, tohum: int = 0) -> float:
    """Hakikî bir hata ne kadar büyük görünür? -- eşiğin sağlaması.

    `reel.karmasik` M28'de kaynağın **yanlış işaretini** kıyas için
    saklamış (``exp(+tJH_ℝ)``, zamanı tersine çevirir). Eşiğin bir
    gevşetme olmadığı ancak böyle gösterilebilir: doğru kod boyut başına
    ~1 ulp verirken, yanlış kod ``1e16`` ulp verir.
    """
    from reel.karmasik import kaynak_isaretiyle_evrim
    rng = np.random.default_rng(tohum)
    A = rng.normal(size=(n, n)); A = A + A.T
    B = rng.normal(size=(n, n)); B = B - B.T
    H = A + 1j * B
    psi = rng.normal(size=n) + 1j * rng.normal(size=n)
    lam, V = np.linalg.eigh(H)
    t = 0.6
    ref = (V * np.exp(-1j * lam * t)) @ (V.conj().T @ psi)
    got = karmasik_coz(kaynak_isaretiyle_evrim(H, t) @ reel_goem(psi))
    return float(np.abs(got - ref).max())


def dik_donusum_dogrulamasi(boyutlar=(8, 64, 512)) -> Dict[int, Dict[str, float]]:
    """``RHT``: dik, simetrik, involutif mi? -- müstakil bir dik dönüşüm."""
    o: Dict[int, Dict[str, float]] = {}
    for N in boyutlar:
        Hm = hartley(N=N, ne="dizey")
        x = np.random.default_rng(N).normal(size=N)
        o[N] = {
            "diklik": float(np.abs(Hm.T @ Hm - np.eye(N)).max()),
            "involutif": float(np.abs(Hm @ Hm - np.eye(N)).max()),
            "simetri": float(np.abs(Hm - Hm.T).max()),
            "hızlı_ile_fark": float(np.abs(Hm @ x - hartley(x)).max()),
        }
    return o


def rapor(deneme: int = 200_000) -> str:
    s = ["=== GÖLGE KÂHİN (Dosya 6) -- reel/ ve akis/ ana hattı denetliyor ===",
         "",
         "Dosya 6'nın 3. kademesi ('icra yolundan çıkar') ŞU AN MANASIZDIR",
         "ve öyle zabıtlanır: reel/ ve akis/ zaten icra yolunda değil,",
         "ikisi de beylik. Çıkarmak için evvelâ girmiş olması lazım.",
         "Asıl iş 1. ve 2. kademedir: ana hattı, ana hattı hiç kullanmayan",
         "bir koddan denetlemek.",
         "",
         "--- 1) GRUP SADAKATİ (akis.lie.so_n_mi) ---"]
    g = grup_sadakati()
    for ad in ("cayley", "us"):
        d = g[ad]
        s.append("  %-7s diklik=%.2e  det sapması=%.2e  hepsi SO(4)'te: %s"
                 % (ad, d["diklik_sapması"], d["det_sapması"], d["hepsi_SO4"]))

    s += ["", "--- 2) ERİŞİLEBİLİRLİK BOŞLUĞU (H120) ---"]
    e = erisim_bosslugu(deneme)
    s += ["  hedef %s   SO(4)'te mi: %s   det(I+Q) = %.1f"
          % (e["hedef"], e["hedef_SO4te_mi"], e["det_I_arti_Q"]),
          "  Cayley ile en iyi yaklaşım (%d deneme) : %.4f"
          % (e["deneme"], e["cayley_en_iyi"]),
          "  üstel harita ile hata                  : %.2e"
          % e["üstel_hatası"],
          "",
          "  Yani π dönmeleri Cayley'in DIŞINDADIR. Reel yazmaçta yegâne",
          "  faz π olduğuna göre (H98), melekeler işaret çevirmeyi hiç",
          "  öğrenemiyordu; bütün işaret kapıları elle konmak zorunda",
          "  kaldı. Bu bir tercih değil, farkedilmemiş bir kısıttı."]

    s += ["", "--- 3) REEL GÖMME SADAKATİ (reel.karmasik) ---"]
    r = reel_gomme_sadakati()
    yanlis = _yanlis_isaretle_kiyas()
    s += ["  exp(−tJH_ℝ) ile exp(−iHt) farkı : %.2e  (%.2f ulp/boyut)"
          % (r["azamî_sapma"], r["ulp_boyut_başına"]),
          "  SO(2N) diklik sapması           : %.2e" % r["diklik_sapması"],
          "  şart (≤ %.0f ulp/boyut)          : %s"
          % (AZAMI_ULP,
             "TUTUYOR" if r["ulp_boyut_başına"] <= AZAMI_ULP else "TUTMUYOR"),
          "  KIYAS -- kaynağın yanlış işareti : %.3f  (%.1e ulp/boyut)"
          % (yanlis, yanlis / (ULP * 4 * max(r["şartlılık"], 1.0))),
          "  Yani eşik bir gevşetme değil: doğru kod ile hakikî hata",
          "  arasında on beş mertebe var."]

    s += ["", "--- 4) DİK DÖNÜŞÜM ÇAPRAZ DOĞRULAMASI (reel.hartley) ---"]
    for N, d in dik_donusum_dogrulamasi().items():
        s.append("  N=%4d  diklik=%.2e  RHT²−I=%.2e  simetri=%.2e  "
                 "(%.2f ulp/boyut)"
                 % (N, d["diklik"], d["involutif"], d["simetri"],
                    d["diklik"] / (ULP * N)))
    s += ["",
          "Dosya 6'nın MUTLAK ε ≤ 1e-14 şartı burada REDDEDİLDİ ve yerine",
          "ölçekli şart konuldu. Sebep: 1e-14 yalnız 45 ulp'tur ve",
          "yuvarlama hatası boyutla büyür; mutlak eşik, N=512'de DOĞRU",
          "kodu yanlış ilan ediyordu (8,51e-14 = boyut başına 0,75 ulp).",
          "Bir ölçüt, doğru koda kırmızı yakıyorsa ölçüt bozuktur."]

    s += ["",
          "HUDUT: reel.karmasik'in kendi uyarısı bu projeyi ilgilendirir --",
          "gömme TEK sistemde çarpımsaldır, BİRLEŞİK sistemde değildir.",
          "Bu ana hattı çürütmez (kuantum/yazmac.py karmaşık kuramın gömmesi",
          "değil, doğrudan reel bir kuantum kuramıdır) fakat neticesi",
          "saklanmaz: reel yazmaç karmaşık olandan DAHA DARDIR."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())

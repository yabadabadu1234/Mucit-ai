"""KANONİK DENETÇİ -- iki durum aynı mı? ``O(1)`` adres eşitliğiyle.

    a = kanonik_adres(psi, cekirdek=16)
    b = kanonik_adres(phi, cekirdek=16)
    ayni = (a["adres"] == b["adres"])        # tek CPU çevrimi

===================================================================
BU DOSYA BİR HESAP MOTORU DEĞİLDİR -- ÖYLE OLMASI YASAKLANDI
===================================================================

Evvelce burada tam bir TDD hesap motoru vardı: kapı, çift kapı,
toplama, noktasal faz, iç çarpım, çöp toplama. **Zabıt (TDD
Darboğazının Riyazî İspatı) onu kökünden iptal etti** ve gerekçesi
ispatlıdır:

    *"Elemanları sürekli bir olasılık dağılımından çekilmiş bir durum
    tensörü, 1 olasılıkla hiçbir izomorfik alt-bloğa veya skaler kat
    ilişkisine sahip olamaz... İki rastgele karmaşık vektörün doğrusal
    bağımlı olma olasılığı SIFIRDIR (Lebesgue ölçüsü). Yani rastgele
    sayılarda hiçbir düğüm birleşemez; graf tam ağaç olarak açılır."*

    *"Ölçtüğünüz 35 163× yavaşlama, tamı tamına donanımın fizikî
    gecikme katsayısıdır: SIMD paralel işlem (100 GFLOPS) / işaretçi
    kovalama (3 MFLOPS) ≈ 33 000×."*

Ve hükmü:

    *"İleri ve geri yayılımda TDD'nin işaretçi (pointer/hash)
    hamallığını derhal iptal ediyoruz. TDD'yi bir hesaplama motoru
    olarak değil; sadece ve sadece mantık kilitlendiğinde kanonik
    adres eşitliğini (O(1)) kontrol eden haricî bir denetçi olarak
    tutuyoruz."*

**Kronecker başlangıçla kurtarma teklifi de reddedildi** ve sebebi
yazılıdır: ``t=0``da Schmidt rankı ``χ=1``dir ve TDD 48 düğüme iner;
fakat ilk gradyan adımında lifler arası çapraz bağ doğar, ``χ``
fırlar ve motor 322 saniyelik cehenneme geri döner. Zabıtın tabiriyle:
*"Sırf başlangıç durumunu Kronecker yapmak bir göz boyamadır."*

===================================================================
GERİYE NE KALDI: TEK VAZİFE
===================================================================

Denetçinin tek işi şudur: bir durumun **çekirdeğini** (ilk ``cekirdek``
elemanı, ışına göre kanonikleştirilmiş) tek bir adrese indirmek.
İki durumun eşitliği artık matris normu değil, **adres kıyasıdır**.

Çekirdek niçin tamamı değil: zabıt *"durumun sadece 16 elemanlık
çekirdeği hashlenerek TDD kanonik adresine bakılır; süre maliyeti
322 saniye değil, 0,0001 saniyedir"* der. Tamamını hashlemek, kesilen
kökü geri sürdürmek olurdu.

**Ne iddia edilmiyor:** çekirdek eşitliği durumların **tam** eşitliği
değildir; ilk ``cekirdek`` elemanı aynı olup gerisi farklı olabilir.
Denetçi bir **elektir**, ispat değil: adres farklıysa durumlar KESİN
farklıdır; aynıysa "aynı olabilir" denir ve gerekirse tam kıyas
(``ic_carpim``) yapılır. Bu, hash tablolarının klasik kaidesidir.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np

__all__ = ["TddAyari", "kanonik_adres", "esit_mi", "rapor"]


@dataclass
class TddAyari:
    """Denetçinin ölçüleri."""

    #: İki bileşenin aynı sayılması için tolerans (anahtara girer).
    tolerans: float = 1e-9
    #: Hashlenecek çekirdek boyu.
    cekirdek: int = 16


def kanonik_adres(psi, cekirdek: int = 16,
                  ayar: Optional[TddAyari] = None) -> Dict[str, Any]:
    """Durumun çekirdeğinden **kanonik adres** çıkar -- ``O(çekirdek)``.

    Işına göre kanoniklik: ilk sıfır olmayan bileşen ``1`` yapılır, o
    hâlde ``ψ`` ile ``λψ`` **aynı adrestir**. Faz ve ölçek farkı
    durumların ayrı olduğu manasına gelmez.
    """
    a = ayar or TddAyari()
    v = np.asarray(psi, complex).reshape(-1)
    assert v.size >= 1, "adres için en az bir genlik lâzım"
    k = max(1, min(int(cekirdek), v.size))
    c = v[:k]
    tol = float(a.tolerans)
    j = int(np.argmax(np.abs(c) > tol)) if np.any(np.abs(c) > tol) else -1
    if j < 0:
        anahtar: Tuple = ("0", k)
    else:
        w = c / c[j]
        basamak = max(1, int(round(-math.log10(max(tol, 1e-15)))))
        anahtar = (k, j) + tuple(np.round(w, basamak).tolist())
    return {"adres": hash(anahtar), "anahtar": anahtar,
            "çekirdek": k, "boy": int(v.size),
            "bayt": int(c.nbytes)}


def esit_mi(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    """İki kanonik adres aynı mı -- **tek kıyas**, matris normu yok.

    ``False`` KESİNDİR: adresler farklıysa durumlar farklıdır.
    ``True`` bir **eleme**dir: çekirdekler aynı, gerisi bakılmadı.
    """
    return a["adres"] == b["adres"] and a["anahtar"] == b["anahtar"]


def rapor(d: int = 4096, tohum: int = 0) -> str:         # pragma: no cover
    """Denetçi ne kadar hızlı ve ne kadar ayırt ediyor -- **ölç**."""
    import time
    r = np.random.default_rng(int(tohum))
    v = r.normal(size=d) + 1j * r.normal(size=d)
    v /= np.linalg.norm(v)
    w = v * np.exp(1j * 0.7)                 # yalnız faz farkı
    u = r.normal(size=d) + 1j * r.normal(size=d)
    u /= np.linalg.norm(u)

    t0 = time.perf_counter()
    for _ in range(1000):
        av = kanonik_adres(v)
    sure = (time.perf_counter() - t0) / 1000
    aw, au = kanonik_adres(w), kanonik_adres(u)

    t0 = time.perf_counter()
    for _ in range(1000):
        _ = abs(complex(np.vdot(v, u)))
    tam = (time.perf_counter() - t0) / 1000

    return "\n".join([
        "=== KANONİK DENETÇİ (TDD hesap motoru İPTAL) ===", "",
        "  d = %d   çekirdek = 16 eleman" % d,
        "  adres alma  : %.7f sn" % sure,
        "  tam iç çarpım: %.7f sn   → denetçi %.1f× hızlı"
        % (tam, tam / max(sure, 1e-12)),
        "",
        "  ψ ile λψ (yalnız faz farkı) : aynı adres mi → %s  (doğru)"
        % esit_mi(av, aw),
        "  ψ ile bağımsız φ            : aynı adres mi → %s  (doğru)"
        % esit_mi(av, au),
        "",
        "  Hesap motoru KÖKÜNDEN KESİLDİ: kapı, toplama, iç çarpım,",
        "  çöp toplama -- hiçbiri yok. Zabıtın hükmü: TDD ileri/geri",
        "  akışta REDDEDİLİR, yalnız kanonik denetçidir.",
    ])


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())

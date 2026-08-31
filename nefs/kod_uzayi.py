"""
MANTIK KOD UZAYI -- hüküm bloğunun **stabilizer** temsili.

`kuantum/stabilizer.py` bir hakikat söylüyordu ve **beylikti**:

> Rank dolaşıklığa değil **Clifford-dışılığa** bağlıdır. Bir Clifford
> devresi ne kadar dolaşık durum üretirse üretsin rank **1** kalır.

Bu, bu projede az evvel ölçülen derde birebir cevaptır. Ölçüldü
(kütük H115): akış âzamî dolaşıklık üretiyor, Schmidt rütbesi **her
χ'de doyuyor** (8→8, 16→16, 32→32, 64→64) ve entropi ``log₂χ``ye
yapışık. Yani MPS hiçbir bütçede yetmiyor.

Fakat **mantık katmanı Clifford'dur**: `nefs/sadakat.py` ve
`nefs/tertip.py` yalnız ``CZ``, ``Z`` ve ``X`` kullanır. O hâlde hüküm
bloğu, MPS'in kesmesine hiç uğramadan **tam** olarak temsil edilebilir.

===================================================================
NE İÇİN KULLANILIYOR -- yedek bir motor DEĞİL
===================================================================

Bu modül MPS'in yerine geçmez (H92: paralel hat yasak). Vazifesi
**hakikat kaynağı** olmaktır:

    MPS'in hüküm bloğunda okuduğu dağılım, aynı kapıların stabilizer
    temsilindeki tam dağılımıyla **yüzleştirilir**.

İkisi ayrı düşerse MPS tarafı yanlıştır. H88'in dersi tam buydu:
``beyan`` aylarca yanlış çevreden okudu ve **karşılaştıracak ikinci
bir temsil olmadığı için** farkedilmedi. Artık var.

===================================================================
HUDUT -- açıkça
===================================================================

``StabilizerDurum`` **köşegen** Clifford yörüngesini tutar
(``|+⟩^n``e ``Z``, ``S``, ``CZ``). Bizim işaretlerimizden:

* iki kontrollü olanlar (``|11⟩`` işareti) doğrudan ``cz``dir -- **tam**;
* menfî kontrollüler (``|10⟩``, ``|01⟩``, ``|00⟩``) ``X`` sarmalı ister
  ve ``X`` köşegen ailenin dışına çıkarır;
* üç kontrollü olanlar (tertip) hiç köşegen-Clifford değildir.

Onun için burada **yalnız iki-kontrollü, müsbet işaretli** şartlar
yüzleştirilir ve hangilerinin dışarıda kaldığı **sayılır**. Kapsamadığı
yeri kapsıyormuş gibi yapmaz.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np

from kuantum.stabilizer import StabilizerDurum

__all__ = ["hukum_kod_uzayi", "kod_uzayi_dagilimi", "yuzlestir"]


def hukum_kod_uzayi(n: int, cz_ciftleri: Sequence[Tuple[int, int]],
                    z_yuvalari: Sequence[int] = ()) -> StabilizerDurum:
    """Hüküm bloğunun kod uzayı: ``|+⟩^n`` + ``CZ`` işaretleri.

    Her ``CZ(a,b)`` bir mantık şartının ``|11⟩`` yasağıdır. Netice
    **tam**tır: kesme yok, bağ boyutu yok, ``2^n`` açılmıyor -- durum
    ``(D, J)`` çiftinde ``O(n²)`` yer tutuyor.
    """
    # ``StabilizerDurum.z`` ve ``.cz`` **yerinde** değiştirir ve ``None``
    # döndürür; dönüşü yeniden atamak sessizce ``None`` verirdi.
    d = StabilizerDurum.arti(int(n))
    for a in z_yuvalari:
        d.z(int(a))
    for a, b in cz_ciftleri:
        d.cz(int(a), int(b))
    return d


def kod_uzayi_dagilimi(d: StabilizerDurum) -> np.ndarray:
    """``P(y) = |⟨y|φ⟩|²`` -- bütün ``2^n`` taban durumu için.

    Yalnız **yüzleştirme** için kullanılır ve ``n`` küçük tutulur
    (``n ≤ 12``); maksat MPS'i denetlemektir, onun yerine geçmek değil.
    """
    n = d.n
    if n > 14:
        raise ValueError("yüzleştirme için n ≤ 14 (2^n açılıyor)")
    Y = np.array([[(i >> j) & 1 for j in range(n)] for i in range(1 << n)],
                 dtype=np.int64)
    g = np.asarray(d.genlik(Y))
    P = np.abs(g) ** 2
    t = float(P.sum())
    return P / t if t > 1e-30 else np.full(1 << n, 1.0 / (1 << n))


def yuzlestir(q, alanlar: Sequence[str] = ("tasdik", "nakz")) -> Dict[str, object]:
    """MPS'in hüküm dağılımını stabilizer temsiliyle **yüzleştir**.

    Kurulan kod uzayı, `nefs/sadakat.py`nin iki-kontrollü müsbet
    şartlarını taşır (``|tasdik=1, nakz=1⟩`` gibi). Dönen sözlükte iki
    dağılım ve aralarındaki toplam değişinti mesafesi vardır.

    **Bu bir sınamadır, bir iddia değil.** Mesafe büyükse MPS tarafında
    kesme ısırıyor demektir ve sayı onu söyler.
    """
    yuv: List[int] = []
    for ad in alanlar:
        _, kac = q._alan[ad]
        yuv += [q.kulli(ad, j) for j in range(kac)]
    yuv = sorted(set(yuv))
    n = len(yuv)
    bas = min(yuv)
    if max(yuv) - bas + 1 != n:
        raise ValueError("yüzleştirme için alanlar bitişik olmalı")

    P_mps = np.asarray(q.blok_dagilimi(bas, n), float).ravel()

    # Aynı şartı taşıyan kod uzayı: ``|tasdik₀=1, nakz₀=1⟩`` yasağı.
    yerel = {j: i for i, j in enumerate(yuv)}
    cz = [(yerel[q.kulli("tasdik", 0)], yerel[q.kulli("nakz", 0)])]
    d = hukum_kod_uzayi(n, cz)
    P_stab = kod_uzayi_dagilimi(d)

    # ``blok_dagilimi`` ilk kübiti EN ANLAMLI bit sayar; stabilizer ise
    # ``Y[:, j]`` ile ``j``. inci kübiti en anlamsız sayar. Düzen
    # varsayılmaz, **çevrilir**.
    idx = np.array([int("".join(str((i >> j) & 1)
                               for j in range(n - 1, -1, -1)), 2)
                    for i in range(1 << n)])
    P_stab = P_stab[idx]

    tvd = 0.5 * float(np.sum(np.abs(P_mps - P_stab)))
    return {"kübit": n, "P_mps": P_mps, "P_stab": P_stab, "tvd": tvd,
            "kapsanan_şart": len(cz),
            "kapsanmayan": "menfî kontrollü ve üç kontrollü şartlar"}

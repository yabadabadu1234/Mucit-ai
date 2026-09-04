"""
do-hesabı: bağlanım ile müdahalenin ayrımı.

Bir fonksiyon yaklaşımı ``E[Y | X = x]`` öğrenir. Bu, "X'i x YAPARSAM Y ne
olur" sorusunun cevabı DEĞİLDİR; "X'i x GÖRÜRSEM Y ne olur" sorusunun
cevabıdır. İkisi ancak X'in dışarıdan atandığı hâlde çakışır.

Fark, ortak bir sebep (confounder) varken açılır:

    Z → X,   Z → Y,   X → Y

Burada ``E[Y|X=x]`` hem X'in doğrudan etkisini hem Z üzerinden gelen sahte
ilişkiyi taşır. Müdahale dağılımı ``P(Y | do(X=x))`` ise arka kapı
düzeltmesiyle bulunur:

    P(y | do(x)) = Σ_z P(y | x, z) P(z)

Bu dosya, ÜRETİCİ modeli bilerek kurar (yani doğru cevap bilinir), sonra
üç tahmini kıyaslar:

  * ham bağlanım (yalnız X ile)              -- yanlı
  * arka kapı düzeltmesi (X ve Z ile)        -- doğru
  * fiilî müdahale benzetimi (X rastgele atanır) -- altın ölçü

Zaafı: arka kapı, karıştırıcının ÖLÇÜLDÜĞÜNÜ varsayar. Ölçülmemiş
karıştırıcıda düzeltme de yanlıdır -- bu da aşağıda gösterilir.
"""
from __future__ import annotations

from typing import Dict, Tuple

import numpy as np


# Üretici model (doğrusal yapısal denklemler):
#   Z ~ N(0,1)
#   X = a·Z + εx
#   Y = b·X + c·Z + εy          →   do(X) etkisi tam olarak b'dir
A_ZX, B_XY, C_ZY = 1.5, 0.8, -2.0


def uret(n: int, tohum: int = 0, mudahale: float | None = None) -> Tuple[np.ndarray, ...]:
    rng = np.random.default_rng(tohum)
    z = rng.normal(size=n)
    if mudahale is None:
        x = A_ZX * z + rng.normal(size=n) * 0.5
    else:
        # do(X): X artık Z'den gelmiyor, dışarıdan atanıyor
        x = rng.normal(size=n) * mudahale
    y = B_XY * x + C_ZY * z + rng.normal(size=n) * 0.5
    return z, x, y


def _egim(x: np.ndarray, y: np.ndarray) -> float:
    A = np.stack([x, np.ones_like(x)], axis=1)
    return float(np.linalg.lstsq(A, y, rcond=None)[0][0])


def _kismi_egim(x: np.ndarray, z: np.ndarray, y: np.ndarray) -> float:
    A = np.stack([x, z, np.ones_like(x)], axis=1)
    return float(np.linalg.lstsq(A, y, rcond=None)[0][0])


def baglanim_mudahale_ayrimi(n: int = 200000, tohum: int = 0) -> Dict[str, object]:
    """Üç tahmin, bilinen doğru cevap ``b = 0.8`` ile kıyaslanır."""
    z, x, y = uret(n, tohum)
    ham = _egim(x, y)                              # E[Y|X]: yanlı
    duzeltilmis = _kismi_egim(x, z, y)             # arka kapı: doğru

    _, xi, yi = uret(n, tohum + 1, mudahale=1.0)   # fiilî do(X)
    deneysel = _egim(xi, yi)

    return {
        "dogru_etki_b": B_XY,
        "ham_baglanim": ham,
        "arka_kapi": duzeltilmis,
        "deneysel_mudahale": deneysel,
        "ham_yanli": bool(abs(ham - B_XY) > 0.1),
        "arka_kapi_dogru": bool(abs(duzeltilmis - B_XY) < 0.02),
        "deneysel_dogru": bool(abs(deneysel - B_XY) < 0.02),
        "arka_kapi_deneyselle_uyusuyor": bool(abs(duzeltilmis - deneysel) < 0.02),
    }


def olculmemis_karistirici(n: int = 200000, tohum: int = 0) -> Dict[str, object]:
    """**Zaaf.** Z gözlenmiyorsa arka kapı düzeltmesi kurulamaz.

    Burada ikinci, GİZLİ bir karıştırıcı U eklenir; Z ölçülür, U ölçülmez.
    Z ile düzeltmek yetmez: tahmin hâlâ yanlıdır. do-hesabı bir hesap
    usulüdür, karıştırıcı üretmez -- neyin ölçüldüğü bir VERİ meselesidir.
    """
    rng = np.random.default_rng(tohum)
    z = rng.normal(size=n)
    u = rng.normal(size=n)                       # gizli
    x = A_ZX * z + 1.2 * u + 0.5 * rng.normal(size=n)
    y = B_XY * x + C_ZY * z + 1.7 * u + 0.5 * rng.normal(size=n)

    z_ile = _kismi_egim(x, z, y)
    A = np.stack([x, z, u, np.ones_like(x)], axis=1)
    hepsi_ile = float(np.linalg.lstsq(A, y, rcond=None)[0][0])
    return {
        "dogru_etki_b": B_XY,
        "yalniz_z_ile_duzeltme": z_ile,
        "z_ve_u_ile_duzeltme": hepsi_ile,
        "z_ile_hala_yanli": bool(abs(z_ile - B_XY) > 0.1),
        "u_gorulunce_duzeliyor": bool(abs(hepsi_ile - B_XY) < 0.02),
    }


def catal_ve_carpisma(n: int = 200000, tohum: int = 0) -> Dict[str, object]:
    """Hangi değişkene şart koşulacağı, grafiğin YÖNÜNE bağlıdır.

    * **Çatal** ``X ← Z → Y``: Z'ye şart koşmak sahte ilişkiyi KALDIRIR.
    * **Çarpışma** ``X → C ← Y``: C'ye şart koşmak, bağımsız X ve Y
      arasında sahte ilişki YARATIR (Berkson yanlılığı).

    Yani "ne kadar çok değişken katarsan o kadar iyi" YANLIŞTIR.
    """
    rng = np.random.default_rng(tohum)
    # çatal
    z = rng.normal(size=n)
    x1 = z + 0.5 * rng.normal(size=n)
    y1 = z + 0.5 * rng.normal(size=n)          # X'in Y'ye doğrudan etkisi YOK
    catal_ham = _egim(x1, y1)
    catal_z_ile = _kismi_egim(x1, z, y1)

    # çarpışma
    x2 = rng.normal(size=n)
    y2 = rng.normal(size=n)                    # gerçekten bağımsız
    c = x2 + y2 + 0.5 * rng.normal(size=n)
    carp_ham = _egim(x2, y2)
    carp_c_ile = _kismi_egim(x2, c, y2)
    return {
        "catal_ham": catal_ham,
        "catal_z_ile": catal_z_ile,
        "catal_sart_kosmak_duzeltti": bool(abs(catal_ham) > 0.5 and abs(catal_z_ile) < 0.02),
        "carpisma_ham": carp_ham,
        "carpisma_c_ile": carp_c_ile,
        "carpisma_sart_kosmak_bozdu": bool(abs(carp_ham) < 0.02 and abs(carp_c_ile) > 0.2),
    }


def rapor() -> str:
    s = ["=== nedensel ==="]
    a = baglanim_mudahale_ayrimi()
    s.append("do-ayrımı  doğru b=%.2f | ham bağlanım=%.4f (yanlı=%s) | arka kapı=%.4f | deneysel=%.4f"
             % (a["dogru_etki_b"], a["ham_baglanim"], a["ham_yanli"],
                a["arka_kapi"], a["deneysel_mudahale"]))
    s.append("           arka kapı deneyselle uyuşuyor=%s" % a["arka_kapi_deneyselle_uyusuyor"])
    b = olculmemis_karistirici()
    s.append("zaaf       gizli U varken: yalnız Z ile=%.4f (hâlâ yanlı=%s) | Z+U ile=%.4f (düzeliyor=%s)"
             % (b["yalniz_z_ile_duzeltme"], b["z_ile_hala_yanli"],
                b["z_ve_u_ile_duzeltme"], b["u_gorulunce_duzeliyor"]))
    c = catal_ve_carpisma()
    s.append("çatal      ham=%.4f → Z ile=%.4f  (şart koşmak düzeltti=%s)"
             % (c["catal_ham"], c["catal_z_ile"], c["catal_sart_kosmak_duzeltti"]))
    s.append("çarpışma   ham=%.4f → C ile=%.4f  (şart koşmak BOZDU=%s)"
             % (c["carpisma_ham"], c["carpisma_c_ile"], c["carpisma_sart_kosmak_bozdu"]))
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())

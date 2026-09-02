"""ÜÇ YENİ UZUV: 𝒪₄₂ Umumileştirme, 𝒪₄₃ Talim, 𝒪₄₄ Tahsil.

Padişahın hükmü: *"Umumileştirme isminden de belli olduğu üzere bir
melekedir. Talim beyanla alakalı, bir usul düzenleyicidir. Tahsil ise
bizzat bizim eğitimimizle alakalıdır. Ben bunların bizzat belli
formüllerle uzuv olarak vazife alması taraftarıyım."*

Üçü de burada **formülleriyle** durur ve üçünün de ölçüsü kırmızıya
döner. Soyut isim değildirler.

===================================================================
𝒪₄₂ UMUMİLEŞTİRME (el-Ta'mîm) -- Kan uzantısı / kolimit
===================================================================

    𝒪_umum(S) = Π_inv · [ ⊗_j 𝒮_j(X_in^(j) → Y_out^(j)) ]

Manası şudur: birkaç numunede görülen dönüşümlerin **kesişimindeki
değişmez** kısmı süzmek. Bir numuneye mahsus araz (tesadüf) kesişimde
kalmaz; kanun kalır. İcrası, numunelerin ortak sıfır uzayına
izdüşümdür ve ``Π_inv`` tam odur.

**Ölçüsü kırmızıya döner:** bütün numuneler aynı kanunu taşıyorsa
umumîleşen alt uzayın boyutu > 0 çıkar; her numune başka bir şey
söylüyorsa **0** çıkar ve o zaman umumileştirilecek bir şey yoktur.

===================================================================
𝒪₄₃ TALİM (el-Ta'lîm) -- usul düzenleyici, beyana ait
===================================================================

    𝒪_talim(S, τ) = Π_l softmax(S·W_l / τ_l) · Π_fesahat

Manası: bir hükmü muhatabın seviyesine göre **kademelendirmek**.
Sıcaklık ``τ`` yüksekken beyan yayvandır (çok ihtimal, az kesinlik);
düşükken keskindir. Kademe dizisi ``τ₁ > τ₂ > … > τ_L`` monoton
olmalıdır: talim, yayvandan keskine gider, tersi olmaz.

**Ölçüsü kırmızıya döner:** kademeler arası entropi monoton
azalmıyorsa talim değil karıştırma yapılıyordur.

===================================================================
𝒪₄₄ TAHSİL (el-Tahsîl) -- ağırlığı zâtî mülk kılmak
===================================================================

    𝒪_tahsil(θ) = θ ∘ exp(−η · Ĥ_Dimağ(θ)) + γ · I_meleke

Manası: dışarıdan gelen bilgiyi **emanet** olmaktan çıkarıp ağırlığa
işlemek. ``exp(−ηĤ)`` bir Gibbs sönümüdür (yüksek enerjili, yani
çelişkili yönler bastırılır); ``γI`` ise melekenin kendi kimliğini
korur -- tamamen dışarının şekline girmesin diye.

**Ölçüsü kırmızıya döner:** ``η`` büyükse θ tamamen söner (öğrenme
değil silinme); ``γ`` büyükse hiç değişmez (öğrenmeme). İkisi de
raporlanır.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["UMUM", "TALIM", "TAHSIL", "umumilestir", "talim_kademesi",
           "tahsil_et"]

#: Meleke numaraları (divanın 09-KÜLLÎ-TEŞKİLAT tescili).
UMUM: int = 42
TALIM: int = 43
TAHSIL: int = 44


def umumilestir(ciftler: Sequence[Tuple[np.ndarray, np.ndarray]],
                esik: float = 1e-8) -> Dict[str, object]:
    """𝒪₄₂ -- numunelerin **kesişimindeki** değişmez dönüşümü süz.

    Her ``(X, Y)`` çifti bir ``A`` arar: ``A X ≈ Y``. Tek bir çift
    sonsuz çok ``A``ya uyar; **kanun**, hepsine birden uyanların
    kesişimidir. Kesişim, yığılmış kısıt dizeyinin sıfır uzayının
    ötelenmesidir ve boyutu ``serbestlik``tir.

    * ``serbestlik = 0`` → hiçbir ``A`` hepsine uymuyor: **çelişki**.
    * ``serbestlik > 0`` → bir kanun ailesi var; ``A`` en küçük
      normlusudur (Occam: en sade kanun).
    """
    if not ciftler:
        raise ValueError("en az bir numune lâzım")
    X0 = np.atleast_2d(np.asarray(ciftler[0][0], float))
    d = X0.shape[0]
    # vec(Y) = (Xᵀ ⊗ I) vec(A)
    satirlar: List[np.ndarray] = []
    sag: List[np.ndarray] = []
    for X, Y in ciftler:
        X = np.atleast_2d(np.asarray(X, float))
        Y = np.atleast_2d(np.asarray(Y, float))
        if X.shape[0] != d or Y.shape[0] != d:
            raise ValueError("bütün numuneler aynı boyutta olmalı")
        satirlar.append(np.kron(X.T, np.eye(d)))
        sag.append(Y.T.reshape(-1))
    M = np.vstack(satirlar)
    b = np.concatenate(sag)
    U, s, Vt = np.linalg.svd(M, full_matrices=False)
    olcek = max(float(s[0]) if s.size else 0.0, 1e-30)
    tut = s > float(esik) * olcek
    a = Vt[tut].T @ ((U[:, tut].T @ b) / s[tut])
    A = a.reshape(d, d).T
    artik = float(np.linalg.norm(M @ a - b) / max(np.linalg.norm(b), 1e-30))
    return {"A": A, "serbestlik": int(np.sum(~tut)),
            "artık": artik,
            "umumîleşti": bool(artik < 1e-6),
            "numune": len(ciftler)}


def talim_kademesi(S: np.ndarray, tau: Sequence[float]
                   ) -> Dict[str, object]:
    """𝒪₄₃ -- hükmü kademe kademe keskinleştir; entropi **azalmalı**.

    ``tau`` monoton azalan olmalıdır. Her kademede ``softmax(S/τ)``
    alınır ve Shannon entropisi ölçülür. Entropi bir kademede artarsa
    o talim değil karıştırmadır ve ``sahih`` yalanlanır.
    """
    S = np.asarray(S, float).ravel()
    t = [float(x) for x in tau]
    if any(t[i] <= t[i + 1] for i in range(len(t) - 1)) is False and len(t) > 1:
        pass                                   # monotonluk aşağıda ölçülür
    ent: List[float] = []
    dag: List[np.ndarray] = []
    for x in t:
        z = S / max(float(x), 1e-12)
        z = z - z.max()
        p = np.exp(z)
        p = p / max(float(p.sum()), 1e-300)
        dag.append(p)
        nz = p > 1e-15
        ent.append(float(-np.sum(p[nz] * np.log(p[nz]))))
    azalan = all(ent[i] >= ent[i + 1] - 1e-12 for i in range(len(ent) - 1))
    tau_azalan = all(t[i] > t[i + 1] for i in range(len(t) - 1))
    return {"τ": t, "entropi": ent, "dağılım": dag,
            "τ_azalan": bool(tau_azalan),
            "entropi_azalan": bool(azalan),
            "sahih": bool(tau_azalan and azalan)}


def tahsil_et(teta: np.ndarray, H: np.ndarray, eta: float = 0.1,
              gama: float = 0.05) -> Dict[str, object]:
    """𝒪₄₄ -- ``θ ∘ exp(−η·H) + γ·I`` ile ağırlığı zâtî mülk kıl.

    ``H`` Ĥ_Dimağ'ın o parametreye düşen enerjisidir (burada köşegeni
    alınır: her ağırlığın kendi enerjisi). Yüksek enerji = çelişkili
    yön; ``exp(−ηH)`` onu söndürür.

    Dönen ``değişim`` ve ``sönüm`` ikisi birden okunur (H47): sönüm
    1'e yakınsa hiç öğrenilmemiş, 0'a yakınsa silinmiştir.
    """
    th = np.asarray(teta, float).ravel()
    Hd = np.asarray(H, float)
    e = np.diag(Hd) if Hd.ndim == 2 else Hd.ravel()
    if e.size != th.size:
        e = np.resize(e, th.size)
    sonum = np.exp(-float(eta) * np.abs(e))
    yeni = th * sonum + float(gama)
    return {"θ": yeni,
            "sönüm": float(np.mean(sonum)),
            "değişim": float(np.linalg.norm(yeni - th)
                             / max(np.linalg.norm(th), 1e-30)),
            "silindi": bool(np.mean(sonum) < 0.05),
            "öğrenmedi": bool(np.mean(sonum) > 0.999
                              and abs(float(gama)) < 1e-12)}


def rapor() -> str:                                     # pragma: no cover
    s = ["ÜÇ YENİ UZUV -- 𝒪₄₂ Umumileştirme, 𝒪₄₃ Talim, 𝒪₄₄ Tahsil", ""]
    rng = np.random.default_rng(0)

    s.append("  𝒪₄₂ UMUMİLEŞTİRME -- kanun var mı, yoksa çelişki mi?")
    d = 4
    A = rng.normal(size=(d, d))
    cift = [(X, A @ X) for X in (rng.normal(size=(d, 3)) for _ in range(4))]
    r = umumilestir(cift)
    s.append("     tutarlı 4 numune : artık %.2e  serbestlik %d  umumîleşti %s"
             % (r["artık"], r["serbestlik"], r["umumîleşti"]))
    s.append("     bulunan A, hakikî A'ya uzaklığı: %.2e"
             % float(np.linalg.norm(r["A"] - A) / np.linalg.norm(A)))
    bozuk = list(cift[:3]) + [(cift[3][0], rng.normal(size=(d, 3)))]
    r2 = umumilestir(bozuk)
    s.append("     biri çelişkili   : artık %.4f  umumîleşti %s   ← KIRMIZI"
             % (r2["artık"], r2["umumîleşti"]))

    s.append("")
    s.append("  𝒪₄₃ TALİM -- kademeler keskinleşiyor mu?")
    S = np.array([3.0, 1.0, 0.5, -1.0, 2.0])
    t1 = talim_kademesi(S, (4.0, 2.0, 1.0, 0.5))
    s.append("     τ azalan  : entropi %s  sahih %s"
             % ([round(x, 4) for x in t1["entropi"]], t1["sahih"]))
    t2 = talim_kademesi(S, (0.5, 1.0, 2.0, 4.0))
    s.append("     τ ARTAN   : entropi %s  sahih %s   ← KIRMIZI"
             % ([round(x, 4) for x in t2["entropi"]], t2["sahih"]))

    s.append("")
    s.append("  𝒪₄₄ TAHSİL -- öğrenme mi, silme mi, hiç mi?")
    th = rng.normal(size=8)
    H = np.diag(np.abs(rng.normal(size=8)))
    for eta, gama, ad in ((0.1, 0.05, "mutedil"), (50.0, 0.0, "η çok büyük"),
                          (0.0, 0.0, "η sıfır")):
        r3 = tahsil_et(th, H, eta=eta, gama=gama)
        s.append("     %-12s sönüm %.4f  değişim %.4f  silindi=%s "
                 "öğrenmedi=%s"
                 % (ad, r3["sönüm"], r3["değişim"], r3["silindi"],
                    r3["öğrenmedi"]))
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())

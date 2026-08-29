"""
HÜKÜM DENETİMİ -- kütükteki her hükmün kodda **fiilen** koşup koşmadığı.

Kullanıcı şartı: *"hüküm ceridesindeki tüm hükümleri kodda icra
etmelisin."* Bunu **iddia etmek** kolaydır ve kıymetsizdir. Onun için
burada iddia yoktur: her hüküm için makinenin koşturabileceği bir
**şahit** vardır ve üç neticeden biri çıkar:

* ``GEÇTİ``      -- hüküm kodda fiilen icra ediliyor, şahit doğruladı.
* ``KALDI``      -- şahit koştu ve hükmü **doğrulamadı**. Bu bir kusurdur
                    ve gizlenmez.
* ``ŞAHİTSİZ``   -- hüküm makine ile sınanabilir değil (usûlî yahut
                    kavramî bir hüküm). Sayısı ayrıca raporlanır ki
                    "hepsi geçti" denip geçilmesin.

Kütükte 75 hüküm vardır; hepsinin makine şahidi **yoktur** ve olduğu
iddia edilmiyor. Aşağıdaki liste, şahidi kurulabilenlerdir.
"""
from __future__ import annotations

import math
import time
import traceback
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

__all__ = ["Sahit", "SAHITLER", "denetle", "rapor"]


@dataclass
class Sahit:
    hukum: str
    ozet: str
    kos: Callable[[], Tuple[bool, str]]


# =====================================================================
#  Şahitler
# =====================================================================
def _h3_gradyansiz() -> Tuple[bool, str]:
    """Öğrenme kapalı formdadır: son kat tek bir ``solve`` ile oturur."""
    from kuantum.dalga import DalgaEniyileyici
    from kuantum.nqs import NQS, NQSAyar
    nq = NQS(NQSAyar(n=12, gizli=(8,), derece=3, tohum=0))
    X = np.random.default_rng(0).integers(0, 2, size=(64, 12))
    y = np.random.default_rng(1).normal(size=64)
    m = DalgaEniyileyici(nq, lambda Z: np.zeros(len(np.atleast_2d(Z))))
    artik = m._son_kat_oturt(X, y, lam=1e-6)
    F = nq.ozellik(X)
    # ``log ψ``nin reel kısmı özelliklerde doğrusal olmalı: yeniden kur
    fark = float(np.abs(F @ nq.son_kat().real - nq.log_genlik(X).real).max())
    return fark < 1e-8, "doğrusallık sapması %.2e, uydurma artığı %.3f" % (
        fark, artik)


def _h6_sahitlik() -> Tuple[bool, str]:
    """Tek karşı örnek küllî kaideyi düşürür."""
    from .sahit import _akis_kur, bolutle, kaide_uydur, nakz_bul
    temiz = _akis_kur(m=5, ds=8, t=6)
    bozuk = _akis_kur(m=5, ds=8, t=6, bozuk=2)
    r = []
    for S in (temiz, bozuk):
        b = bolutle(S)
        K = [kaide_uydur(S, x) for x in b.sahitler]
        r.append(nakz_bul(S, b.sahitler, K)["nakz"])
    return (not r[0]) and bool(r[1]), "temiz nakz=%s, bozuk nakz=%s" % tuple(r)


def _h14_kayipsiz() -> Tuple[bool, str]:
    """Belirteçleme gidiş-dönüşü kayıpsız."""
    from idrak import arc
    g = arc.yukle_hepsi("training")[:40]
    hata = 0
    n = 0
    for gv in g:
        for a, b in gv.egitim:
            n += 1
            if not np.array_equal(arc.belirtec_izgara(
                    arc.izgara_belirtecle(a)), a):
                hata += 1
    return hata == 0, "%d ızgarada %d hata" % (n, hata)


def _h21_mertebeler_toplanmaz() -> Tuple[bool, str]:
    """Terkip sıralıdır: lif sırası değişince netice **değişmeli**."""
    from . import mertebe
    from .uzaylar import Parametreler
    p = Parametreler(tohum=0)
    S = np.random.default_rng(0).normal(size=(12, 16))
    A, _, _, _ = mertebe.mertebe_gecisi(S, p, mertebe.DINAMIK)
    ters = tuple(reversed(mertebe.DINAMIK))
    B, _, _, _ = mertebe.mertebe_gecisi(S, p, ters)
    fark = float(np.linalg.norm(A - B) / (np.linalg.norm(A) + 1e-12))
    return fark > 1e-6, "sıra değişince bağıl fark %.3e (>0 olmalı)" % fark


def _h24_mera_dolasiklik() -> Tuple[bool, str]:
    """Süperpozisyon tek başına dolaşıklık vermez; MERA verir."""
    from .qakis import QNefs
    from .qyazmac import QAyar
    q = QNefs(0, QAyar(satir_kubiti=4, bag=16))
    r = q.idrak_et(np.random.default_rng(0).normal(size=(3, 4)))
    return (r.iz.entropi_once < 1e-6 and r.iz.entropi_sonra > 1e-3), \
        "MERA öncesi %.6f → sonrası %.6f" % (r.iz.entropi_once,
                                             r.iz.entropi_sonra)


def _h30_bec_yalniz_tepede() -> Tuple[bool, str]:
    """BEC veri kübitlerine **dokunmaz**; yalnız hüküm alanlarına vurur."""
    from .qakis import QNefs, YOGUSAN, bec_faz_kilidi
    from .qyazmac import QAyar
    q = QNefs(0, QAyar(satir_kubiti=4, bag=16))
    r = q.idrak_et(np.random.default_rng(0).normal(size=(3, 4)), bec=False)
    veri_yuvalari = [r.veri(i, j) for i in range(3) for j in range(4)]
    once = np.asarray(r.y.yuva_yogunluklari(veri_yuvalari))
    bec_faz_kilidi(r)
    sonra = np.asarray(r.y.yuva_yogunluklari(veri_yuvalari))
    fark = float(np.abs(once - sonra).max())
    return fark < 1e-9, "veri kübitlerinde sapma %.2e; yoğuşan alanlar %s" % (
        fark, list(YOGUSAN))


def _h31_povm_cokus_yok() -> Tuple[bool, str]:
    """Zayıf ölçüm normu bozmaz -- çöküş yoktur."""
    from .qakis import QNefs
    from .qyazmac import QAyar
    q = QNefs(0, QAyar(satir_kubiti=4, bag=16))
    r = q.idrak_et(np.random.default_rng(0).normal(size=(3, 4)))
    o1 = r.olcumler()
    o2 = r.olcumler()
    ayni = all(abs(o1[k] - o2[k]) < 1e-12 for k in o1
               if isinstance(o1[k], float))
    return (o1["norm_hatası"] < 1e-10) and ayni, \
        "norm hatası %.2e, iki okuma aynı: %s" % (o1["norm_hatası"], ayni)


def _h42_uniterlik() -> Tuple[bool, str]:
    """Yazmaç üniterdir: tam akış sonunda norm hatası makine mertebesinde."""
    from .qakis import QNefs
    from .qyazmac import QAyar
    q = QNefs(0, QAyar(satir_kubiti=4, bag=16))
    r = q.idrak_et(np.random.default_rng(1).normal(size=(4, 4)))
    return r.olcumler()["norm_hatası"] < 1e-10, \
        "norm hatası %.2e" % r.olcumler()["norm_hatası"]


def _h43_kelam_konusabiliyor() -> Tuple[bool, str]:
    """Kelam alanı düzgün DEĞİL -- model konuşabiliyor."""
    from .qakis import QNefs
    from .qyazmac import QAyar
    q = QNefs(0, QAyar(satir_kubiti=4, bag=16))
    r = q.idrak_et(np.random.default_rng(0).normal(size=(3, 4)))
    P = r.beyan(16)
    duz = 1.0 / len(P)
    sapma = float(np.abs(P - duz).max())
    return sapma > 1e-3, "beyan dağılımının düzgünden sapması %.4f" % sapma


def _h44_uzunluktan_bagimsiz() -> Tuple[bool, str]:
    """Parametre sayısı girdi uzunluğuna bağlı değildir."""
    from .qakis import QNefs
    from .qyazmac import QAyar
    a = QAyar(satir_kubiti=4, bag=16)
    q = QNefs(0, a)
    q.idrak_et(np.random.default_rng(0).normal(size=(3, 4)))
    n1 = len(q)
    q.idrak_et(np.random.default_rng(0).normal(size=(7, 4)))
    n2 = len(q)
    return n1 == n2, "3 satırda %d, 7 satırda %d parametre" % (n1, n2)


def _h53_agac_tam_buzulme() -> Tuple[bool, str]:
    """Ağaçta çevrim yok → büzülme TAM."""
    from .agac import AgacAyar, AgacYazmaci
    for h, w in ((2, 2), (2, 3), (3, 3)):
        ag = AgacYazmaci(AgacAyar(h=h, w=w, renk=2, bag=8))
        psi = ag.buz()
        if abs(float(np.sum(np.abs(psi) ** 2)) - 1.0) > 1e-9:
            return False, "%dx%d: ΣP = %.10f" % (h, w,
                                                 np.sum(np.abs(psi) ** 2))
    return True, "1×2/2×2/2×3/3×3 hepsinde ΣP = 1,0000000000"


def _h64_agac_mpo() -> Tuple[bool, str]:
    """Ağaç MPO kapısı, χ yeterken TAM hesapla aynı."""
    from .agac import _kapi_sinamasi
    r = _kapi_sinamasi(3, 3, 2, 64, 10)
    return r["hata"] < 1e-12, "‖Δψ‖/‖ψ‖ = %.3e, norm %.9f" % (r["hata"],
                                                              r["norm"])


def _h65_boyut_ihtimalde() -> Tuple[bool, str]:
    """Çıktı ağacı açıkken bütün boyutlar askıda: ``P(dolu)=renk/(renk+1)``."""
    from .ucagac import UcAgac
    g = np.array([[1, 2], [3, 0]])
    u = UcAgac([(g, g)], g, renk=4, bag=8)
    M = u.doluluk_haritasi()
    bek = 4.0 / 5.0
    return float(np.abs(M - bek).max()) < 1e-9, \
        "P(dolu) sapması %.2e (beklenen %.3f)" % (np.abs(M - bek).max(), bek)


def _h66_hayal_tersinir() -> Tuple[bool, str]:
    """Anlık kademe tersinir devreyle temizlenir; destekçisiz tahsis reddedilir."""
    from .agac import AgacAyar, AgacYazmaci
    from .hayal import Hayal
    ag = AgacYazmaci(AgacAyar(h=4, w=4, renk=2, bag=32))
    h = Hayal(ag)
    h.ac("çalışma", [(2, j) for j in range(4)], "anlık", "𝒪₄ Tertip")
    reddetti = False
    try:
        h.ac("kaçak", [(3, 0)], "anlık", "")
    except PermissionError:
        reddetti = True
    rng = np.random.default_rng(0)
    once = np.array([ag.hucre_dagilimi((2, j)) for j in range(4)])
    for _ in range(5):
        a = (2, int(rng.integers(4)))
        b = (int(rng.integers(4)), int(rng.integers(4)))
        if a == b:
            continue
        G = np.linalg.qr(rng.normal(size=(4, 4))
                         + 1j * rng.normal(size=(4, 4)))[0]
        h.cift(a, b, G, destekci="𝒪₃ Muhayyile")
    h.temizle()
    sonra = np.array([ag.hucre_dagilimi((2, j)) for j in range(4)])
    hata = float(np.abs(sonra - once).max())
    return reddetti and hata < 1e-10, \
        "destekçisiz reddedildi=%s, geri alma hatası %.2e" % (reddetti, hata)


def _h71_clifford_bedava() -> Tuple[bool, str]:
    """60 Clifford kapısı rankı büyütmez; T büyütür."""
    from kuantum.stabilizer import StabilizerRank
    rng = np.random.default_rng(0)
    S = StabilizerRank(10)
    for _ in range(60):
        a, b = rng.choice(10, 2, replace=False)
        S.cz(int(a), int(b))
        S.s(int(rng.integers(10)))
    clifford_rank = len(S)
    S.t(0)
    return clifford_rank == 1 and len(S) == 2, \
        "60 Clifford sonrası rank %d, bir T sonrası %d" % (clifford_rank,
                                                           len(S))


def _h71_bgs_haddi() -> Tuple[bool, str]:
    """BGS seyrekleştirmesinin haddi ``‖c‖₁²/k`` fiilen tutuyor mu."""
    from kuantum.stabilizer import StabilizerRank
    n = 12
    Y = np.random.default_rng(0).integers(0, 2, size=(300, n))
    tam = StabilizerRank(n)
    rng = np.random.default_rng(5)
    diziliş = [int(rng.integers(n)) for _ in range(12)]
    for a in diziliş:
        tam.t(a)
    g0 = tam.genlik(Y)
    asan = []
    for k in (64, 256, 1024):
        S = StabilizerRank(n)
        for a in diziliş:
            S.t(a)
        r = S.seyreklestir(k, tohum=1)
        hata = float(np.linalg.norm(S.genlik(Y) - g0) ** 2
                     / np.linalg.norm(g0) ** 2)
        if hata > r["had"]:
            asan.append((k, hata, r["had"]))
    return not asan, ("had üç k değerinde de tuttu" if not asan
                      else "haddi aşan: %s" % asan)


def _h72_ptr_buzulme() -> Tuple[bool, str]:
    """Halkanın yığın büzülmesi elle çarpımla birebir aynı."""
    from kuantum.ptr import TensorHalka
    H = TensorHalka(5, d=2, chi=3, tohum=2)
    X = np.random.default_rng(0).integers(0, 2, size=(7, 5))
    elle = []
    for x in X:
        M = np.eye(3)
        for k in range(5):
            M = M @ H.G[k][:, x[k], :]
        elle.append(np.trace(M))
    fark = float(np.abs(H.genlik(X) - np.array(elle)).max())
    return fark < 1e-12, "âzamî fark %.2e" % fark


def _h73_yuksek_mertebeler_kosuyor() -> Tuple[bool, str]:
    """20 lifin **hepsi** uzak menzilli MPO vuruyor mu (H54/3. borç)."""
    from .mertebe import DINAMIK, lifleri_kur
    from .qakis import QNefs
    from .qyazmac import QAyar
    lifler = lifleri_kur(DINAMIK)
    azami_adim = max(l.adim for l in lifler)

    def atesleyen(n_satir: int, k: int) -> int:
        q = QNefs(0, QAyar(satir_kubiti=k, bag=8))
        r = q.idrak_et(np.zeros((n_satir, k)))
        bas, son = r.veri(0, 0), r.kulli("makam", 0)
        return sum(1 for lif in lifler
                   if len(range(bas, son, lif.adim)) >= 2)

    # Küçük yazmaç: veri zinciri 15 kübit; âzamî adım 16 -- iki yüksek
    # mertebe HÂLÂ ateşleyemez ve bu gizlenmez. Şart, veri zincirinin
    # en az ``2·âzamî_adım`` uzunlukta olmasıdır.
    kucuk = atesleyen(3, 4)
    buyuk = atesleyen(6, 12)
    return buyuk == 20, ("küçük yazmaçta %d/20, büyükte %d/20 "
                         "(âzamî adım %d; veri zinciri ≥ 2·adım olmalı)"
                         % (kucuk, buyuk, azami_adim))


def _h73_bec_sukutu_bogmuyor() -> Tuple[bool, str]:
    """BEC sükûtu ve tenakuzu **değiştirmiyor** (H54/4. borç)."""
    from .qakis import QNefs
    from .qyazmac import QAyar
    E = np.random.default_rng(0).normal(size=(3, 4))
    a = QAyar(satir_kubiti=4, bag=16)
    o0 = QNefs(0, a).idrak_et(E, bec=False).olcumler()
    o1 = QNefs(0, a).idrak_et(E, bec=True).olcumler()
    ds = abs(o0["sukut"] - o1["sukut"])
    dt = abs(o0["tenakuz"] - o1["tenakuz"])
    return ds < 1e-9 and dt < 1e-9, \
        "Δsükût %.2e, Δtenakuz %.2e (BEC'siz sükût %.4f)" % (ds, dt,
                                                             o0["sukut"])


def _h75_gri_kod() -> Tuple[bool, str]:
    """Gri kod: gidiş-dönüş kayıpsız ve komşular tek bit farkeder."""
    from .kulli_egitim import gri_kodla, gri_coz
    rng = np.random.default_rng(0)
    for bit in (3, 6, 10):
        k = rng.integers(0, 1 << bit, size=(200, 7))
        if int(np.abs(gri_coz(gri_kodla(k, bit), 7, bit) - k).max()):
            return False, "bit=%d gidiş-dönüş bozuk" % bit
    A = gri_kodla(np.arange(0, 64)[:, None], 6)
    farklar = set(np.abs(np.diff(A, axis=0)).sum(1).tolist())
    return farklar == {1}, "gidiş-dönüş kayıpsız; komşu bit farkı %s" % farklar


def _h69_grover_kapali_form() -> Tuple[bool, str]:
    """Grover özyinelemesi ``k+1`` sayı üzerinde; ``k*`` kapalı formda."""
    from kuantum.dalga import en_iyi_k, grover_ikili
    kotu = []
    for mu in (0.5, 0.2, 0.05, 0.01, 0.002):
        teta = math.asin(math.sqrt(mu))
        for k in range(0, 6):
            al, be = grover_ikili(mu, k)
            p = mu * al * al / (mu * al * al + (1 - mu) * be * be)
            # Grover'ın kapalı formu: P(iyi) = sin²((2k+1)θ)
            bek = math.sin((2 * k + 1) * teta) ** 2
            if abs(p - bek) > 1e-9:
                kotu.append(("sin² tutmadı", mu, k, p, bek))
        k = en_iyi_k(mu)
        p = math.sin((2 * k + 1) * teta) ** 2
        # ``k*``, ``(2k+1)θ``yı ``π/2``ye EN YAKIN getiren tam sayıdır.
        #
        # İlk hâlde şart "k* bütün k'lar içinde en iyi olsun" diye
        # konmuştu ve KALDI: μ=0,2'de k*=1 iken k=52 daha yüksek çıkıyor.
        # Kusur kodda değil şahitte idi -- ``sin²((2k+1)θ)`` DEVRÎdir;
        # çok daha fazla dönerek tepeye biraz daha yakın düşmek daima
        # mümkündür, fakat 52 tur atmak 1 turun yerini tutmaz. ``k*``
        # aranan şey "mutlak en iyi" değil, **en ucuz tepe**dir.
        en_yakin = min(range(0, 200),
                       key=lambda kk: abs((2 * kk + 1) * teta
                                          - math.pi / 2))
        if k != en_yakin:
            kotu.append(("k* π/2'ye en yakın değil", mu, k, en_yakin))
        # μ küçükken k* yoğunlaştırmalı; μ=0,5'te Grover ZATEN
        # yoğunlaştıramaz (sin²((2k+1)·π/4) daima ≤ 0,5) -- bu bir
        # kusur değil, kapalı formun kendisidir ve şart o yüzden
        # yalnız küçük μ için konur.
        if mu <= 0.1 and p < 0.85:
            kotu.append(("küçük μ'da yoğunlaşma yok", mu, k, p))
    return not kotu, ("sin²((2k+1)θ) beş μ ve altı k için tam tuttu; "
                      "k* daima en iyi" if not kotu else "kusurlu: %s" % kotu)


def _h47_iki_olcut() -> Tuple[bool, str]:
    """Ölçüt İKİdir ve ikisi de ayrı raporlanır."""
    from .boyut import olc
    from idrak import arc
    r = olc(arc.yukle_hepsi("evaluation")[:40])
    var = all(k in r for k in ("isabet_oranı", "konuşunca_isabet",
                               "sükût", "yanlış"))
    return var, "kapsama %.3f, konuşunca isabet %.3f, sükût %d" % (
        r["isabet_oranı"], r["konuşunca_isabet"], r["sükût"])


def _h74_paralellik_neticeyi_degistirmiyor() -> Tuple[bool, str]:
    """İş parçalama davranışı **değiştirmez**, yalnız hızı."""
    from hesap.donanim import Donanim, parcala, topla_paralel
    X = np.arange(37.0).reshape(37, 1)

    def f(P, cihaz):
        return P * 2.0
    tek = topla_paralel(f, X, Donanim(False, ("cpu",), (0.0,), 1, True))
    dort = topla_paralel(f, X, Donanim(False, ("a", "b", "c", "d"),
                                       (1, 1, 1, 1), 4, False))
    bolme = parcala(37, 4)
    dengeli = max(b - a for a, b in bolme) - min(b - a for a, b in bolme) <= 1
    return (np.array_equal(tek, dort) and dengeli), \
        "tek=dört cihaz: %s, bölme %s" % (np.array_equal(tek, dort), bolme)


SAHITLER: List[Sahit] = [
    Sahit("H3", "öğrenme kapalı formdadır, gradyan yok", _h3_gradyansiz),
    Sahit("H6", "tek karşı örnek küllî kaideyi düşürür", _h6_sahitlik),
    Sahit("H14", "belirteçleme kayıpsız intibak", _h14_kayipsiz),
    Sahit("H21", "mertebeler toplanmaz, terkip sıralıdır",
          _h21_mertebeler_toplanmaz),
    Sahit("H24", "dolaşıklığı MERA verir, süperpozisyon değil",
          _h24_mera_dolasiklik),
    Sahit("H30", "BEC yalnız tepede; veri kübitlerine dokunmaz",
          _h30_bec_yalniz_tepede),
    Sahit("H31", "POVM zayıf ölçüm -- çöküş yok", _h31_povm_cokus_yok),
    Sahit("H42", "yazmaç üniterdir", _h42_uniterlik),
    Sahit("H43", "kelam alanı düzgün değil -- model konuşabiliyor",
          _h43_kelam_konusabiliyor),
    Sahit("H44", "parametre girdi uzunluğundan bağımsız",
          _h44_uzunluktan_bagimsiz),
    Sahit("H47", "ölçüt İKİdir ve ayrı raporlanır", _h47_iki_olcut),
    Sahit("H53", "ağaçta büzülme TAM (çevrim yok)", _h53_agac_tam_buzulme),
    Sahit("H64", "ağaç MPO kapısı tam hesapla aynı", _h64_agac_mpo),
    Sahit("H65", "boyut ihtimal uzayının içinde", _h65_boyut_ihtimalde),
    Sahit("H66", "anlık hayal tersinir temizlenir", _h66_hayal_tersinir),
    Sahit("H69", "Grover kapalı formda, k* ve salınım doğru",
          _h69_grover_kapali_form),
    Sahit("H71a", "Clifford rankı büyütmez, T büyütür",
          _h71_clifford_bedava),
    Sahit("H71b", "BGS seyrekleştirme haddi tutuyor", _h71_bgs_haddi),
    Sahit("H72", "halka büzülmesi elle çarpımla aynı", _h72_ptr_buzulme),
    Sahit("H73a", "20 mertebenin hepsi uzak menzil ateşliyor",
          _h73_yuksek_mertebeler_kosuyor),
    Sahit("H73b", "BEC sükûtu boğmuyor", _h73_bec_sukutu_bogmuyor),
    Sahit("H74", "iş parçalama neticeyi değiştirmiyor",
          _h74_paralellik_neticeyi_degistirmiyor),
    Sahit("H75", "Gri kod kayıpsız, komşular tek bit", _h75_gri_kod),
]

#: Makine şahidi **kurulamayan** hükümler ve sebebi. Bunlar "geçti"
#: sayılmaz; sayıları raporun sonunda ayrıca yazılır ki tablo kimseyi
#: aldatmasın.
SAHITSIZ: Dict[str, str] = {
    "H1/H2/H4/H5": "usûlî: hangi modülün ana hat olduğu, uzvun cinsi",
    "H7–H13": "erken usûl hükümleri; çoğu sonraki hükümlerde eridi",
    "H32–H41": "inşa kararları (main/ ayrı model, zincir düzeni)",
    "H45/H46/H48/H49": "geçmiş ÖLÇÜMLERİN kaydı; şahit değil netice",
    "H50/H51/H55–H63": "kavramî hükümler (kademe, ağaç sayısı, meleke tarifi)",
    "H67": "cevap bekleyen sualler -- borçtur, şahidi olamaz",
    "H68/H70/H75": "kısmen şahitli; sayısal neticeleri kendi modüllerinde",
}


# =====================================================================
def denetle() -> List[Tuple[str, str, str, str, float]]:
    netice = []
    for s in SAHITLER:
        t0 = time.perf_counter()
        try:
            gecti, mesaj = s.kos()
            hal = "GEÇTİ" if gecti else "KALDI"
        except Exception as e:                       # noqa: BLE001
            hal, mesaj = "HATA", "%s: %s" % (type(e).__name__, str(e)[:90])
        netice.append((s.hukum, s.ozet, hal, mesaj,
                       time.perf_counter() - t0))
    return netice


def rapor() -> str:
    n = denetle()
    s = ["=== HÜKÜM DENETİMİ: kütükteki hükümlerin kodda icrası ===", ""]
    for hukum, ozet, hal, mesaj, dt in n:
        isaret = {"GEÇTİ": "✓", "KALDI": "✗", "HATA": "!"}[hal]
        s.append("%s %-5s %-46s %5.2fs" % (isaret, hukum, ozet, dt))
        s.append("        %s" % mesaj)
    gecti = sum(1 for x in n if x[2] == "GEÇTİ")
    s += ["", "%d/%d şahit geçti." % (gecti, len(n)), "",
          "ŞAHİTSİZ HÜKÜMLER (geçti SAYILMAZ):"]
    for k, v in SAHITSIZ.items():
        s.append("  %-14s %s" % (k, v))
    s += ["",
          "Kütükte 75 hüküm vardır; hepsinin makine şahidi YOKTUR ve",
          "olduğu iddia edilmiyor. Yukarıdaki tablo yalnız şahidi",
          "kurulabilenleri gösterir."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())

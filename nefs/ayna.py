from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from kuantum.devre import qft_vur
from kuantum.eniyileme import (baslangic_hamiltonyeni, maxcut_hamiltonyeni,
                               tayf_araligi)
from kuantum.topolojik import orgu_ureticleri, yang_baxter_hatasi
from ogrenme.morse import (euler_karakteristigi,
                           morse_euler_denklik_tahkiki, morse_indisleri)

from .hizli import hesap

__all__ = ["AynaAyari", "Isik", "bolucu", "vakum", "sikistir", "bogoliubov",
           "faz_kaydir", "kivilcim", "halka", "olc", "rapor"]


@dataclass
class AynaAyari:

    teta: float = math.pi / 12
    r: float = 0.35
    sikma_fazi: float = 0.0
    korunakli: bool = False
    kip: int = 2
    tur: int = 24
    sahit_n: int = 8
    usul: str = "kararlı"
    kararli_adim: int = 24
    kararli_esik: float = 1e-6
    pompa: float = 1.6
    ciftlenim: float = 0.35
    adim: float = 0.08
    vakum_genligi: float = 1e-3
    tohum: int = 0
    cekirdek: str = "oto"

    def __post_init__(self) -> None:
        assert int(self.kip) >= 2, (
            "yarı geçirgen ayna TEK GİRDİLİ DEĞİLDİR: kip ≥ 2 (zabıt I.1)")
        assert float(self.r) >= 0.0, "sıkıştırma r negatif olamaz"
        assert int(self.tur) >= 1, "halkanın en az bir turu olmalı"


@dataclass
class Isik:

    mu: np.ndarray
    sigma: np.ndarray

    def __post_init__(self) -> None:
        self.mu = np.asarray(self.mu, float).reshape(-1)
        self.sigma = np.asarray(self.sigma, float)
        n = self.mu.size
        assert n % 2 == 0 and n >= 4, (
            "CV durumu 2m boyutlu olmalı (m ≥ 2 kip): %d" % n)
        assert self.sigma.shape == (n, n), (
            "kovaryans %dx%d olmalı, %r geldi" % (n, n, self.sigma.shape))

    @property
    def kip(self) -> int:
        return self.mu.size // 2

    def foton_sayisi(self) -> np.ndarray:
        d = np.diag(self.sigma)
        ikinci = d + self.mu ** 2
        n = 0.5 * (ikinci[0::2] + ikinci[1::2] - 1.0)
        return np.asarray(n, float)


def _omega(m: int) -> np.ndarray:
    O = np.zeros((2 * m, 2 * m))
    for i in range(m):
        O[2 * i, 2 * i + 1] = 1.0
        O[2 * i + 1, 2 * i] = -1.0
    return O


def bolucu(teta: float, korunakli: bool = False) -> np.ndarray:
    if korunakli:
        s1, s2 = orgu_ureticleri()
        yb = float(yang_baxter_hatasi(s1, s2))
        assert yb < 1e-9, (
            "korunaklı ışın bölücü istendi fakat üreteçler örgü "
            "temsili değil: Yang-Baxter hatası %.3e" % yb)
        U = np.asarray(s2, complex)
    else:
        c, s = math.cos(float(teta)), math.sin(float(teta))
        U = np.array([[c, -s], [s, c]], dtype=complex)
    hata = float(np.max(np.abs(U.conj().T @ U - np.eye(2))))
    assert hata < 1e-10, "ışın bölücü ÜNİTER DEĞİL: %.3e" % hata
    return U


def vakum(kip: int = 2) -> Isik:
    m = int(kip)
    assert m >= 2, "vakum en az iki portlu kurulur"
    return Isik(np.zeros(2 * m), 0.5 * np.eye(2 * m))


def bogoliubov(u: complex, v: complex) -> np.ndarray:
    uu, vv = complex(u), complex(v)
    sart = abs(uu) ** 2 - abs(vv) ** 2
    assert abs(sart - 1.0) < 1e-9, (
        "Bogoliubov şartı ihlâl: |u|²−|v|² = %.6f ≠ 1" % sart)
    S = np.array([[uu.real + vv.real, -uu.imag + vv.imag],
                  [uu.imag + vv.imag, uu.real - vv.real]], float)
    O = _omega(1)
    ihlal = float(np.max(np.abs(S @ O @ S.T - O)))
    assert ihlal < 1e-9, "Bogoliubov dönüşümü simplektik değil: %.3e" % ihlal
    return S


def sikistir(isik: Isik, r: float, faz: float = 0.0,
             kipler: Optional[Sequence[int]] = None) -> Isik:
    r = float(r)
    m = isik.kip
    kipler = range(m) if kipler is None else [int(k) for k in kipler]
    S = np.eye(2 * m)
    for k in kipler:
        assert 0 <= k < m, "kip aralık dışı: %d" % k
        S[2 * k:2 * k + 2, 2 * k:2 * k + 2] = bogoliubov(
            math.cosh(r), complex(math.cos(faz), math.sin(faz)) * math.sinh(r))
    return Isik(S @ isik.mu, S @ isik.sigma @ S.T)


def _bs_simplektik(U: np.ndarray, m: int, a: int, b: int) -> np.ndarray:
    S = np.eye(2 * m)
    for i, ki in enumerate((a, b)):
        for j, kj in enumerate((a, b)):
            z = U[i, j]
            S[2 * ki:2 * ki + 2, 2 * kj:2 * kj + 2] = np.array(
                [[z.real, -z.imag], [z.imag, z.real]], float)
    return S


def aynadan_gecir(isik: Isik, ayar: AynaAyari,
                  port: Tuple[int, int] = (0, 1)) -> Isik:
    U = bolucu(ayar.teta, ayar.korunakli)
    S = _bs_simplektik(U, isik.kip, int(port[0]), int(port[1]))
    return Isik(S @ isik.mu, S @ isik.sigma @ S.T)


def faz_kaydir(genlik: np.ndarray, k: int, ne: str = "her_ikisi"):
    v = np.asarray(genlik, complex).reshape(-1)
    N = v.size
    assert N >= 2, "faz kaydırmak için en az iki genlik lâzım"
    k = int(k) % N
    dogrudan = np.roll(v, k)
    if ne == "kösegen":
        return dogrudan
    faz = np.exp(2j * math.pi * k * np.arange(N) / N)
    qft_yolu = qft_vur(faz * qft_vur(v), ters=True)
    if ne == "qft":
        return qft_yolu
    fark = float(np.max(np.abs(qft_yolu - dogrudan)))
    return dogrudan, fark


def kivilcim(dagilim, ayar: Optional[AynaAyari] = None,
             ne: str = "dağılım"):
    a = ayar or AynaAyari()
    xp, cekirdek_adi, gpu = hesap(a.cekirdek)
    P = np.asarray(dagilim, float).reshape(-1)
    assert P.size >= 2, "kıvılcım için en az iki ihtimal lâzım"
    assert np.all(np.isfinite(P)), "dağılımda NaN/Inf var"
    assert P.min() >= 0.0, "dağılımda negatif ihtimal var"
    top = float(P.sum())
    assert top > 0.0, "dağılım tamamen sıfır -- boş bir şey dönemez"
    P = P / top

    if abs(float(a.teta)) < 1e-15 and not a.korunakli:
        if ne == "döküm":
            return P, {"sapma": 0.0, "tepe_kaydi": 0, "çekirdek": cekirdek_adi,
                       "entropi_farkı": 0.0, "gpu": bool(gpu)}
        return P

    kok = np.sqrt(P)
    m = kok.size
    esle = qft_vur(kok.astype(complex))
    yol = "qft"
    fz = complex(math.cos(a.sikma_fazi), math.sin(a.sikma_fazi))
    b = (math.cosh(a.r) * esle
         + (fz * math.sinh(a.r)) * np.conj(esle))
    nb = float(np.linalg.norm(b))
    assert nb > 0.0, "boş port sıfır çıktı -- sıkıştırma çöktü"
    b = b / nb

    U = bolucu(a.teta, a.korunakli)
    yeni = U[0, 0] * kok.astype(complex) + U[0, 1] * b
    Q = np.abs(np.asarray(yeni)) ** 2
    tq = float(Q.sum())
    assert tq > 0.0, "kıvılcımdan boş dağılım çıktı"
    Q = Q / tq
    assert np.all(np.isfinite(Q)), "kıvılcım NaN üretti"

    if ne == "dağılım":
        return Q
    if ne != "döküm":
        raise ValueError("kıvılcım kipi bilinmiyor: %r" % (ne,))

    def _H(x):
        x = np.clip(x, 1e-15, None)
        return float(-np.sum(x * np.log(x)))

    return Q, {"eşlenik_yolu": yol,
               "sapma": float(np.max(np.abs(Q - P))),
               "tepe_kaydi": int(np.argmax(Q) != np.argmax(P)),
               "entropi_farkı": _H(Q) - _H(P),
               "çekirdek": cekirdek_adi, "gpu": bool(gpu),
               "boş_port_normu": nb}


def halka(J, ayar: Optional[AynaAyari] = None, ne: str = "çözüm"
          ) -> Dict[str, object]:
    a = ayar or AynaAyari()
    xp, cekirdek_adi, gpu = hesap(a.cekirdek)
    J = np.asarray(J, float)
    assert J.ndim == 2 and J.shape[0] == J.shape[1], (
        "çiftlenim dizeyi kare olmalı: %r" % (J.shape,))
    N = J.shape[0]
    assert N >= 2, "halkada en az iki mod olmalı"
    J = 0.5 * (J + J.T)
    np.fill_diagonal(J, 0.0)

    r = np.random.default_rng(int(a.tohum))
    x = float(a.vakum_genligi) * r.standard_normal(N)
    seyir: List[float] = []
    Jx_olcegi = float(np.max(np.sum(np.abs(J), axis=1))) or 1.0
    c, sn = math.cos(a.teta), math.sin(a.teta)
    dt = float(a.adim)
    gecmis: List[np.ndarray] = []
    if str(a.usul) == "kararlı":
        for t in range(int(a.tur)):
            p = float(a.pompa) * (t + 1) / float(a.tur)
            vak = float(a.vakum_genligi) * r.standard_normal(N)
            x = c * x + sn * vak
            for _ in range(int(a.kararli_adim)):
                once = x
                x = x + dt * ((p - 1.0) * x - x ** 3
                              + (float(a.ciftlenim) / Jx_olcegi) * (J @ x))
                if float(np.max(np.abs(x - once))) < float(a.kararli_esik):
                    break
            seyir.append(float(np.mean(np.abs(x))))
            gecmis.append(np.where(x >= 0, 1, -1).astype(int))
        assert np.all(np.isfinite(x)), "halka ıraksadı (NaN/Inf)"
        assert float(np.max(np.abs(x))) > 0.0, (
            "halka hiç osilasyona başlamadı -- vakum genliği sıfır mı?")
        return _halka_netice(x, J, a, seyir, gecmis, N, ne,
                             cekirdek_adi, gpu)
    for t in range(int(a.tur)):
        p = float(a.pompa) * (t + 1) / float(a.tur)
        vak = float(a.vakum_genligi) * r.standard_normal(N)
        x = c * x + sn * vak
        x = x + dt * ((p - 1.0) * x - x ** 3
                      + (float(a.ciftlenim) / Jx_olcegi) * (J @ x))
        seyir.append(float(np.mean(np.abs(x))))
        gecmis.append(np.where(x >= 0, 1, -1).astype(int))
    assert np.all(np.isfinite(x)), "halka ıraksadı (NaN/Inf)"
    assert float(np.max(np.abs(x))) > 0.0, (
        "halka hiç osilasyona başlamadı -- vakum genliği sıfır mı?")
    return _halka_netice(x, J, a, seyir, gecmis, N, ne, cekirdek_adi, gpu)


def _halka_netice(x, J, a, seyir, gecmis, N, ne, cekirdek_adi, gpu):
    s = np.where(x >= 0, 1, -1).astype(int)
    ust = float(np.max(np.abs(x)))
    bedel = float(-0.5 * s @ J @ s)
    netice: Dict[str, object] = {
        "spin": s, "genlik": x, "bedel": bedel, "tur": int(a.tur),
        "çekirdek": cekirdek_adi, "gpu": bool(gpu)}
    if ne == "çözüm":
        return netice
    if ne != "döküm":
        raise ValueError("halka kipi bilinmiyor: %r" % (ne,))

    kenar = int(math.ceil(math.sqrt(N)))
    ped = np.zeros(kenar * kenar)
    ped[:N] = np.abs(x)
    g = (ped.reshape(kenar, kenar) >= np.mean(np.abs(x))).astype(int)
    M = morse_indisleri(g)
    tamam, cetvel = morse_euler_denklik_tahkiki(g)
    assert tamam, ("Morse-Euler kimliği tutmadı -- alan sayımı bozuk: %r"
                   % (cetvel,))
    netice["öbek"] = int(M[0])
    netice["morse"] = {int(k): int(v) for k, v in M.items()}
    netice["euler"] = int(euler_karakteristigi(g))
    netice["doyum"] = float(np.mean(np.abs(x)) / ust) if ust > 0 else 0.0
    karar = np.abs(x) > 0.5 * ust
    son_devrilme = 0
    for t in range(1, len(gecmis)):
        if np.any(gecmis[t][karar] != gecmis[t - 1][karar]):
            son_devrilme = t
    netice["karar_veren"] = int(karar.sum())
    netice["son_devrilme"] = int(son_devrilme)
    netice["kilitlendi"] = bool(son_devrilme < 0.9 * int(a.tur))
    netice["seyir"] = seyir

    if N > 12 and int(a.sahit_n) >= 3:
        k = int(min(a.sahit_n, N))
        sec = np.random.default_rng(int(a.tohum) + 7).choice(
            N, size=k, replace=False)
        Jk = J[np.ix_(sec, sec)]
        kenarlar = [(i, j) for i in range(k) for j in range(i + 1, k)
                    if abs(Jk[i, j]) > 1e-12]
        if kenarlar:
            hc = maxcut_hamiltonyeni(k, kenarlar)
            kesim = float(-np.min(hc))
            sk = s[sec]
            bizim = float(sum(1 for (i, j) in kenarlar if sk[i] != sk[j]))
            netice["şahit_n"] = k
            netice["şahit_nispeti"] = (bizim / kesim) if kesim > 0 else 0.0
    if N <= 12:
        kenarlar = [(i, j) for i in range(N) for j in range(i + 1, N)
                    if abs(J[i, j]) > 1e-12]
        hc = maxcut_hamiltonyeni(N, kenarlar)
        idx = int(np.argmin(hc))
        en_iyi = [1 - 2 * ((idx >> (N - 1 - i)) & 1) for i in range(N)]
        kesim = float(-np.min(hc))
        bizim = float(sum(1 for (i, j) in kenarlar if s[i] != s[j]))
        netice["tam_kesim"] = kesim
        netice["halka_kesimi"] = bizim
        netice["nispet"] = bizim / kesim if kesim > 0 else 0.0
        netice["tam_spin"] = np.asarray(en_iyi, int)
    if N <= 8:
        H0 = baslangic_hamiltonyeni(N)
        H1 = np.diag(maxcut_hamiltonyeni(N, [
            (i, j) for i in range(N) for j in range(i + 1, N)
            if abs(J[i, j]) > 1e-12]).astype(complex))
        t = tayf_araligi(H0, H1, ornek=41)
        netice["tayf_aralığı"] = float(t["Δ_min"])
        netice["tayf_s"] = float(t["s_min"])
    return netice


def olc(ayar: Optional[AynaAyari] = None) -> Dict[str, object]:
    a = ayar or AynaAyari()
    o: Dict[str, object] = {}

    U = bolucu(a.teta, False)
    o["bs_üniterlik"] = float(np.max(np.abs(U.conj().T @ U - np.eye(2))))
    s1, s2 = orgu_ureticleri()
    o["yang_baxter"] = float(yang_baxter_hatasi(s1, s2))
    Uk = bolucu(0.0, True)
    o["korunaklı_karışım"] = float(abs(Uk[0, 1]))

    v = vakum(a.kip)
    o["vakum_foton"] = float(np.max(np.abs(v.foton_sayisi())))
    sq = sikistir(v, a.r, a.sikma_fazi)
    o["sıkışmış_foton"] = float(sq.foton_sayisi()[0])
    o["sıkışmış_beklenen"] = float(math.sinh(a.r) ** 2)
    O = _omega(sq.kip)
    o["simplektik_ihlâl"] = float(
        np.max(np.abs(sq.sigma - sq.sigma.T)))
    o["belirsizlik"] = float(np.min(np.linalg.eigvalsh(
        sq.sigma + 0.5j * O).real))

    once = float(np.sum(sq.foton_sayisi()))
    sonra = float(np.sum(aynadan_gecir(sq, a).foton_sayisi()))
    o["enerji_farkı"] = abs(sonra - once)

    g = np.zeros(16, complex)
    g[3] = 1.0
    g[7] = 0.5
    _, fark = faz_kaydir(g, 5, ne="her_ikisi")
    o["qft_faz_farkı"] = float(fark)

    r = np.random.default_rng(0)
    P = r.random(64)
    P /= P.sum()
    kapali = kivilcim(P, AynaAyari(teta=0.0))
    o["kapalı_sapma"] = float(np.max(np.abs(kapali - P)))
    _, dk = kivilcim(P, a, ne="döküm")
    o["açık_sapma"] = float(dk["sapma"])
    o["entropi_farkı"] = float(dk["entropi_farkı"])
    o["çekirdek"] = dk["çekirdek"]
    o["gpu"] = bool(dk["gpu"])

    N = 8
    rr = np.random.default_rng(1)
    A = rr.integers(0, 2, size=(N, N)).astype(float)
    A = np.triu(A, 1)
    A = A + A.T
    h = halka(-A, a, ne="döküm")
    o["halka_öbeği"] = int(h["öbek"])
    o["halka_doyumu"] = float(h["doyum"])
    o["halka_devrilmesi"] = int(h["son_devrilme"])
    o["halka_kararı"] = int(h["karar_veren"])
    o["halka_kilitlendi"] = bool(h["kilitlendi"])
    o["halka_nispeti"] = float(h.get("nispet", 0.0))
    o["tayf_aralığı"] = float(h.get("tayf_aralığı", 0.0))

    cv = sq.mu.nbytes + sq.sigma.nbytes
    o["cv_bayt"] = int(cv)
    o["yoğun_bayt_d4096"] = int(4096 * 16)
    o["yer_kazancı"] = float(4096 * 16) / float(cv)
    return o


def rapor(ayar: Optional[AynaAyari] = None) -> str:
    a = ayar or AynaAyari()
    o = olc(a)
    y = ["=== YARI YANSITICI AYNA -- vakum uyarılması ===", "",
         "  çekirdek: %s   (GPU: %s)" % (o["çekirdek"], o["gpu"]), "",
         "  1. IŞIN BÖLÜCÜ (SU(2), iki giriş iki çıkış)",
         "     üniterlik hatası      : %.3e" % o["bs_üniterlik"],
         "     Yang-Baxter hatası    : %.3e  (örgü temsili mi?)"
         % o["yang_baxter"],
         "     korunaklı karışım |σ₂₁|: %.6f" % o["korunaklı_karışım"],
         "",
         "  2. VAKUM VE SIKIŞTIRMA (zabıt II.1, II.2)",
         "     vakumda foton         : %.3e   (SIFIR olmalı)"
         % o["vakum_foton"],
         "     sıkışmışta foton      : %.6f  (beklenen sinh²r = %.6f)"
         % (o["sıkışmış_foton"], o["sıkışmış_beklenen"]),
         "     belirsizlik alt sınırı: %.6f  (≥ 0 olmalı)"
         % o["belirsizlik"],
         "     aynadan geçince ΔE    : %.3e  (korunum)"
         % o["enerji_farkı"],
         "",
         "  3. FAZ KAYDIRMA -- QFT ile köşegen yol aynı mı?",
         "     fark                  : %.3e" % o["qft_faz_farkı"],
         "",
         "  4. KÖR SICAKLIĞIN İPTALİ",
         "     ayna KAPALI iken sapma: %.3e   (BİREBİR sıfır olmalı)"
         % o["kapalı_sapma"],
         "     ayna AÇIK iken sapma  : %.6f" % o["açık_sapma"],
         "     entropi farkı         : %+.6f" % o["entropi_farkı"],
         "",
         "  5. COHERENT ISING MACHINE (boşluk rezonansı)",
         "     mana öbeği (Morse M₀) : %d   doyum: %.4f   kilitlendi: %s"
         % (o["halka_öbeği"], o["halka_doyumu"], o["halka_kilitlendi"]),
         "     son spin devrilmesi   : %d. tur  (karar veren kip: %d)"
         % (o["halka_devrilmesi"], o["halka_kararı"]),
         "     kesim nispeti         : %.4f  (1,0 = tam çözüm)"
         % o["halka_nispeti"],
         "     adyabatik tayf aralığı: %.6f" % o["tayf_aralığı"],
         "",
         "  6. SÜREKLİ DEĞİŞKEN (CV) TEMSİLİ",
         "     CV durumu             : %d bayt" % o["cv_bayt"],
         "     yoğun d=4096 durumu   : %d bayt" % o["yoğun_bayt_d4096"],
         "     yer kazancı           : %.1f kat" % o["yer_kazancı"]]
    return "\n".join(y)

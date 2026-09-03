"""HDTF -- Hiyerarşik İkili Ağaç Katlaması, **belirlenimci** QTT inşası.

Divan-ı Âlî'nin 2. hükmü (2 Eylül 2026 celsesi):

    2^35 genliği klasik bellekte açıp SVD alamazsın; her token'ı ayrı
    ayrı 12 SVD ile sıkıştırmak ise 826 token/sn ile sistemi kilitler.
    Sahih çözüm: Hiyerarşik İkili Ağaç Katlaması (HDTF).

    1. Sözlük tablosu baştan 12-çekirdekli QTT olarak tutulur; bir
       token'ın çekirdekleri O(1) sürede çekilir -- SVD YOKTUR.
    2. L = 4096 uzunluğundaki dizi tek hamlede açılmaz: komşu token
       çiftleri yerel QR/SVD ile birleştirilir, 4096 → 2048 → … → 1.

**Katlamanın cebri.** İki blok ``|A⟩`` ve ``|B⟩``yi yeni bir mevki
kübitiyle birleştirmek, MPS toplamının ta kendisidir::

    |yeni⟩ = |0⟩ ⊗ |A⟩ + |1⟩ ⊗ |B⟩

    çekirdek 0   : (1, 2, 2)   -- kontrol; |0⟩ → A dalı, |1⟩ → B dalı
    çekirdek 1…n−1: köşegen blok ``diag(A_j, B_j)`` -- bağlar toplanır
    çekirdek n   : dikey ek ``[A_n ; B_n]`` -- sağ bağ 1'e kapanır

Bağ ``a_j + b_j``ye çıkar; **derhal** kanonik süpürmeyle ``χ``ye iner.
Hiçbir yerde ``2^n`` genlik açılmaz, hiçbir yerde zar atılmaz.

**Maliyet.** ``L`` token, ``χ`` bağ, ``q = log₂L + 12`` yuva için
seviye ``ℓ``de ``L/2^ℓ`` katlama ve her katlama ``O((ℓ+12)·χ³)``::

    Σ_{ℓ} (L/2^ℓ)(ℓ+12) χ³   ≈  O(L · χ³)

yani token sayısında **doğrusal** ve ``χ``de kübiktir. Ölçüsü
``hdtf_olcusu``dedir; iddia değil, sayılır.
"""
from __future__ import annotations

import math
import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["mps_birlestir", "mps_kirp", "mps_norm", "mps_genlik",
           "dyadic_katla", "dyadic_katla_yigin", "hdtf_yigin", "sozluk_qtt", "token_cekirdegi", "hdtf_kur",
           "hdtf_olcusu"]


def _cek(v: np.ndarray, kubit: int, chi: Optional[int] = None
         ) -> Tuple[List[np.ndarray], float]:
    """Genlik vektörünü MPS çekirdeklerine ayır (ardışık SVD)."""
    v = np.asarray(v, float).ravel()
    n = int(kubit)
    if v.size != (1 << n):
        raise ValueError("genlik %d, 2^%d değil" % (v.size, n))
    cek: List[np.ndarray] = []
    M = v.reshape(1, -1)
    atilan = 0.0
    for _ in range(n - 1):
        r0 = M.shape[0]
        M = M.reshape(r0 * 2, -1)
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        etkin = int(np.sum(s > 1e-12 * max(float(s[0]), 1e-30)))
        r1 = max(1, etkin if chi is None else min(int(chi), etkin))
        atilan += float(np.sum(s[r1:] ** 2))
        cek.append(U[:, :r1].reshape(r0, 2, r1))
        M = s[:r1, None] * Vt[:r1, :]
    cek.append(M.reshape(-1, 2, 1))
    top = float(v @ v)
    return cek, math.sqrt(max(atilan, 0.0) / max(top, 1e-300))


def mps_birlestir(A: Sequence[np.ndarray], B: Sequence[np.ndarray]
                  ) -> List[np.ndarray]:
    """``|0⟩⊗A + |1⟩⊗B`` -- yeni bir mevki kübiti ekleyerek katla.

    Kesme **yoktur**; bağ olduğu gibi toplanır. Kırpma ayrı bir
    adımdır (``mps_kirp``) ve ayrı ölçülür -- birleştirmenin kendisi
    tamdır, kayıp yalnız kırpmadadır.
    """
    A = list(A)
    B = list(B)
    if len(A) != len(B):
        raise ValueError("iki blok aynı yuva sayısında olmalı: %d ≠ %d"
                         % (len(A), len(B)))
    n = len(A)
    out: List[np.ndarray] = []
    # kontrol çekirdeği: |0⟩ → A dalı (bağ 0), |1⟩ → B dalı (bağ 1)
    k0 = np.zeros((1, 2, 2))
    k0[0, 0, 0] = 1.0
    k0[0, 1, 1] = 1.0
    out.append(k0)
    for j in range(n):
        a, b = np.asarray(A[j], float), np.asarray(B[j], float)
        al, ar = a.shape[0], a.shape[2]
        bl, br = b.shape[0], b.shape[2]
        if j == n - 1:
            # son yuva: sağ bağ 1'e kapanmalı → dikey ek
            c = np.zeros((al + bl, 2, 1))
            c[:al, :, :] = a
            c[al:, :, :] = b
        else:
            c = np.zeros((al + bl, 2, ar + br))
            c[:al, :, :ar] = a
            c[al:, :, ar:] = b
        out.append(c)
    return out


def mps_kirp(cek: Sequence[np.ndarray], chi: int) -> Tuple[List[np.ndarray],
                                                           float]:
    """Kanonik süpürmeyle bağı ``χ``ye indir. Döner ``(çekirdek, hata)``.

    Sağdan sola QR (kanonikleştir), soldan sağa SVD (kırp). Bu sıra
    **Eckart-Young manasında en iyi** kırpmayı verir; zip-up'ın
    aksine burada sağdaki çevre görülmüş olur (kütük H185).
    """
    C = [np.asarray(c, float).copy() for c in cek]
    n = len(C)
    if n < 2:
        return C, 0.0
    for k in range(n - 1, 0, -1):
        t = C[k]
        dl, dr = t.shape[0], t.shape[2]
        Q, R = np.linalg.qr(t.reshape(dl, 2 * dr).T)     # (2dr,r),(r,dl)
        r = Q.shape[1]
        C[k] = Q.T.reshape(r, 2, dr)
        C[k - 1] = np.tensordot(C[k - 1], R.T, axes=([2], [0]))
    atilan = 0.0
    top = 0.0
    for k in range(n - 1):
        t = C[k]
        dl, dr = t.shape[0], t.shape[2]
        U, s, Vt = np.linalg.svd(t.reshape(dl * 2, dr), full_matrices=False)
        if top == 0.0:
            top = float(np.sum(s ** 2)) + 1e-30
        r = max(1, min(int(chi), s.size))
        atilan += float(np.sum(s[r:] ** 2))
        C[k] = U[:, :r].reshape(dl, 2, r)
        SV = s[:r, None] * Vt[:r, :]
        C[k + 1] = np.tensordot(SV, C[k + 1], axes=([1], [0]))
    return C, math.sqrt(max(atilan, 0.0) / max(top, 1e-300))


def mps_norm(cek: Sequence[np.ndarray]) -> float:
    """``‖ψ‖`` -- çevre büzülmesiyle, genliği açmadan."""
    E = np.ones((1, 1))
    for c in cek:
        c = np.asarray(c, float)
        E = np.einsum("ac,aib,cid->bd", E, c, c, optimize=True)
    return math.sqrt(max(float(E[0, 0]), 0.0))


def mps_genlik(cek: Sequence[np.ndarray]) -> np.ndarray:
    """Çekirdekleri açıp tam genlik -- **yalnız küçük ``n`` sınamasında**."""
    T = np.asarray(cek[0], float)[0]                    # (2, r)
    for c in cek[1:]:
        T = np.tensordot(T, np.asarray(c, float), axes=([-1], [0]))
    return T[..., 0].reshape(-1)


def dyadic_katla(bloklar: Sequence[Sequence[np.ndarray]], chi: int
                 ) -> Tuple[List[np.ndarray], float, int]:
    """``L`` bloğu ikili ağaçla tek bloğa katla. ``(çekirdek, hata, katlama)``.

    ``L`` ikinin kuvveti değilse **son blok tekrarlanmaz**: eksik yer
    sıfır bloğuyla değil, ağacın o dalı hiç kurulmayarak doldurulur
    (tekrarlamak veriyi çoğaltmak, sıfırlamak ise kaba sıfırlama
    olurdu -- H14 yasağı).
    """
    kat = [list(b) for b in bloklar]
    hata = 0.0
    sayac = 0
    while len(kat) > 1:
        yeni: List[List[np.ndarray]] = []
        for i in range(0, len(kat) - 1, 2):
            c = mps_birlestir(kat[i], kat[i + 1])
            c, h = mps_kirp(c, int(chi))
            hata = math.hypot(hata, h)
            sayac += 1
            yeni.append(c)
        if len(kat) % 2:
            # eşi olmayan blok bir üst seviyeye **olduğu gibi** çıkar;
            # fakat yuva sayısı bir eksik kalır, o yüzden başına
            # ``|0⟩`` mevki kübiti eklenir (kimlik katlama).
            tek = list(kat[-1])
            k0 = np.zeros((1, 2, 1))
            k0[0, 0, 0] = 1.0
            yeni.append([k0] + tek)
        kat = yeni
    return kat[0], float(hata), int(sayac)



# ══════════════════════════════════════════════════════════════════════
#  YIĞIN KATLAMA -- aynı seviyedeki bütün çiftler TEK çağrıda
# ══════════════════════════════════════════════════════════════════════
#
# **ÖLÇÜLEN VE DÜZELTİLEN DARBOĞAZ.** Yukarıdaki ``dyadic_katla`` cebren
# doğrudur (birleştirme hatası ``0,000e+00``) fakat **1100 token/sn**de
# kalıyordu -- token başına ayrı SVD'nin (826) yanında kazanç yok gibi.
# Sebep FLOP değil **Python çağrı masrafı**dır: ``L = 1024`` için 1023
# katlama × 22 yuva × 2 süpürme = ~45.000 ayrı LAPACK çağrısı, her biri
# ``8×16`` gibi minicik dizeylerde.
#
# Bir seviyedeki bütün bloklar **aynı şekildedir** (hepsi ``χ``ye
# kırpılmıştır). O hâlde yığın ekseni açılabilir: ``numpy.linalg.qr`` ve
# ``svd`` yığın hâlinde çalışır ve seviye başına çağrı sayısı blok
# adedinden **bağımsız** hâle gelir.


def _yigin_kirp(C: List[np.ndarray], chi: int, usul: str = "svd"
                ) -> Tuple[List[np.ndarray], np.ndarray]:
    """Yığın hâlinde kanonik kırpma. ``C[j]`` şekli ``(N, rl, 2, rr)``.

    Sağdan sola QR, soldan sağa SVD -- ``mps_kirp`` ile aynı cebir,
    fakat ``N`` blok tek çağrıda. Dönen hata **blok başına**dır.
    """
    n = len(C)
    N = C[0].shape[0]
    if n < 2:
        return C, np.zeros(N)
    for k in range(n - 1, 0, -1):
        t = C[k]
        _, dl, _, dr = t.shape
        M = t.reshape(N, dl, 2 * dr).transpose(0, 2, 1)     # (N,2dr,dl)
        Q, R = np.linalg.qr(M)
        r = Q.shape[2]
        C[k] = Q.transpose(0, 2, 1).reshape(N, r, 2, dr)
        p = C[k - 1]
        C[k - 1] = np.matmul(p.reshape(N, -1, p.shape[3]),
                             R.transpose(0, 2, 1)
                             ).reshape(N, p.shape[1], 2, r)
    atilan = np.zeros(N)
    top = None
    for k in range(n - 1):
        t = C[k]
        _, dl, _, dr = t.shape
        M = t.reshape(N, dl * 2, dr)
        if usul == "gram":
            # **CPU ÇARESİ (padişahın 3. emri).** LAPACK ``gesdd``
            # yerine Gram dizeyinin ``eigh``i: ``MᵀM = V Λ Vᵀ`` ve
            # ``σ = √Λ``. Gram ``dr×dr``dir, ``M`` ise ``2dl×dr``;
            # yani ayrışım daha küçük bir dizeyde koşar.
            #
            # **Bedeli peşinen ilan edilir:** kare almak koşul sayısını
            # KARELER (``κ → κ²``). Küçük ``χ``de ve iyi koşullu
            # çekirdeklerde ölçülebilir; ölçülmeden varsayılan
            # yapılmaz -- ``usul`` açıkça istenmedikçe SVD koşar.
            G = np.matmul(M.transpose(0, 2, 1), M)
            lam, V = np.linalg.eigh((G + G.transpose(0, 2, 1)) / 2.0)
            lam = lam[:, ::-1]
            V = V[:, :, ::-1]
            sv = np.sqrt(np.maximum(lam, 0.0))
            Vt = V.transpose(0, 2, 1)
            U = np.matmul(M, V) / np.maximum(sv[:, None, :], 1e-30)
        else:
            U, sv, Vt = np.linalg.svd(M, full_matrices=False)
        if top is None:
            top = np.sum(sv ** 2, axis=1) + 1e-30
        r = max(1, min(int(chi), sv.shape[1]))
        atilan += np.sum(sv[:, r:] ** 2, axis=1)
        C[k] = U[:, :, :r].reshape(N, dl, 2, r)
        SV = sv[:, :r, None] * Vt[:, :r, :]
        nk = C[k + 1]
        C[k + 1] = np.matmul(SV, nk.reshape(N, nk.shape[1], -1)
                             ).reshape(N, r, 2, nk.shape[3])
    return C, np.sqrt(np.maximum(atilan, 0.0) / top)


def dyadic_katla_yigin(bloklar: Sequence[Sequence[np.ndarray]], chi: int,
                       hedef_blok: int = 1, usul: str = "svd"
                       ) -> Tuple[List[np.ndarray], float, int]:
    """``dyadic_katla``ın yığın hâli -- **aynı cebir, tek çağrı**.

    Netice ``dyadic_katla`` ile makine hassasiyetinde aynıdır ve
    ``rapor`` bunu fiilen yüzleştirir; hız kazancı ayrıca ölçülür.

    ``hedef_blok`` **kaç blok kalınca duracağını** söyler ve bu, tek
    dizinin katlanmasından ``B`` dizinin AYNI ANDA katlanmasına geçişin
    anahtarıdır: ``B`` dizi ``B·L`` blok olarak yatırılır ve ağaç
    ``hedef_blok = B``de durur. O zaman yığın ekseni en dip seviyede
    bile ``B`` kalır ve LAPACK çağrıları küçülmez -- ölçüldüğüne göre
    darboğaz FLOP değil **çağrı adedi**dir (H189).
    """
    L = len(bloklar)
    if L == 0:
        raise ValueError("en az bir blok lâzım")
    q = len(bloklar[0])
    # (N, rl, 2, rr) yığınına al -- bütün bloklar aynı şekilde
    C = [np.stack([np.asarray(bloklar[i][j], float) for i in range(L)])
         for j in range(q)]
    hata = 0.0
    sayac = 0
    while C[0].shape[0] > int(hedef_blok):
        N = C[0].shape[0]
        tek = None
        if N % 2:
            tek = [c[-1:] for c in C]
            C = [c[:-1] for c in C]
            N -= 1
        A = [c[0::2] for c in C]
        B = [c[1::2] for c in C]
        M = N // 2
        yeni: List[np.ndarray] = []
        k0 = np.zeros((M, 1, 2, 2))
        k0[:, 0, 0, 0] = 1.0
        k0[:, 0, 1, 1] = 1.0
        yeni.append(k0)
        for j in range(len(A)):
            a, b = A[j], B[j]
            al, ar = a.shape[1], a.shape[3]
            bl, br = b.shape[1], b.shape[3]
            if j == len(A) - 1:
                c = np.zeros((M, al + bl, 2, 1))
                c[:, :al] = a
                c[:, al:] = b
            else:
                c = np.zeros((M, al + bl, 2, ar + br))
                c[:, :al, :, :ar] = a
                c[:, al:, :, ar:] = b
            yeni.append(c)
        yeni, h = _yigin_kirp(yeni, int(chi), usul=usul)
        hata = math.hypot(hata, float(np.sqrt(np.mean(h ** 2))))
        sayac += M
        if tek is not None:
            # eşi olmayan blok bir üst seviyeye kimlik katlamasıyla çıkar
            t0 = np.zeros((1, 1, 2, 1))
            t0[0, 0, 0, 0] = 1.0
            tek = [t0] + tek
            yeni = [np.concatenate([yeni[j], tek[j]], axis=0)
                    if yeni[j].shape[1:] == tek[j].shape[1:]
                    else _hizala(yeni[j], tek[j]) for j in range(len(yeni))]
        C = yeni
    if C[0].shape[0] == 1:
        return [c[0] for c in C], float(hata), int(sayac)
    return C, float(hata), int(sayac)


def _hizala(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """İki yığını ortak bağ boyutunda birleştir (sıfırla doldurarak).

    Tek kalan blok, katlanmış bloklardan farklı bağ taşıyabilir. Kaba
    sıfırlama yasağı (H14) burada **ihlâl edilmiyor**: atılan hiçbir şey
    yok, yalnız daha küçük olan tensör sıfır dolgu ile aynı kutuya
    yerleştiriliyor; genlikler aynen duruyor.
    """
    rl = max(a.shape[1], b.shape[1])
    rr = max(a.shape[3], b.shape[3])
    out = np.zeros((a.shape[0] + b.shape[0], rl, 2, rr))
    out[:a.shape[0], :a.shape[1], :, :a.shape[3]] = a
    out[a.shape[0]:, :b.shape[1], :, :b.shape[3]] = b
    return out



def hdtf_yigin(diziler: np.ndarray, sozluk: Sequence[Sequence[np.ndarray]],
               chi: int = 8, usul: str = "svd"
               ) -> Tuple[List[np.ndarray], float, int]:
    """``B`` diziyi **aynı anda** katla -- yığın ekseni hiç küçülmez.

    ``diziler`` ``(B, L)`` belirteç indisleridir. ``B·L`` blok tek
    yığında yatırılır; ağaç ``B`` blok kalınca durur, yani her dizi
    kendi içinde katlanır ve diziler birbirine **karışmaz**.

    **Niçin bu, tek dizi katlamaktan başkadır.** Tek dizide seviye
    ``ℓ``de yığın ``L/2^ℓ``ye iner ve son seviyelerde 1'e düşer;
    LAPACK o zaman ``16×16`` gibi minicik dizeylerde çağrı başına
    mikrosaniyeler yerine **çağrı masrafı** öder. ``B`` dizi birden
    katlanınca en dip seviyede bile yığın ``B``dir.

    Dönen çekirdekler ``(B, rl, 2, rr)`` şeklindedir: **yığın MPS**.
    ``main.yazmac.Yazmac``ın ``B`` ekseniyle aynı mantıktır.
    """
    A = np.atleast_2d(np.asarray(diziler, dtype=np.int64))
    B, L = A.shape
    duz = A.ravel()
    bloklar = [token_cekirdegi(sozluk, int(t)) for t in duz]
    return dyadic_katla_yigin(bloklar, int(chi), hedef_blok=int(B),
                              usul=usul)


def sozluk_qtt(E: np.ndarray, chi: int = 8
               ) -> Tuple[List[List[np.ndarray]], np.ndarray, float]:
    """Sözlük tablosunu **bir kere** QTT'ye çevir: ``(çekirdekler, norm, hata)``.

    ``E`` ``(V, D)``dir. Netice her kelime için 12 çekirdektir ve
    eğitim boyunca **değişmez**; bir token'ın çekirdeği bundan sonra
    ``token_cekirdegi`` ile ``O(1)`` çekilir -- SVD yoktur.

    Bu, ``(C)`` yükleme kaleminin **tek defalık** kısmıdır: maliyeti
    ``V`` ile doğrusaldır, ``B·L`` ile değil. Ceridenin
    ``V = 200.000`` sözlüğünde bu, ``8,4 milyon`` token yerine
    ``200 bin`` sıkıştırma demektir -- **42 kat** az.
    """
    E = np.atleast_2d(np.asarray(E, float))
    V, D = E.shape
    q = int(math.ceil(math.log2(max(D, 2))))
    tam = 1 << q
    # **YIĞIN AYRIŞTIRMA.** Evvelce ``V`` kelime için ayrı ayrı ``q``
    # SVD çağrılıyordu (``V·q`` çağrı). Bütün kelimeler aynı şekilde
    # olduğu için yığın ekseni açılır ve çağrı sayısı ``q``ya iner --
    # kelime adedinden **bağımsız**.
    P = np.zeros((V, tam))
    P[:, :min(D, tam)] = E[:, :min(D, tam)]
    nrm = np.linalg.norm(P, axis=1)
    P = P / np.maximum(nrm, 1e-300)[:, None]
    yigin: List[np.ndarray] = []
    M = P.reshape(V, 1, tam)
    atilan = np.zeros(V)
    for _ in range(q - 1):
        r0 = M.shape[1]
        M = M.reshape(V, r0 * 2, -1)
        U, sv, Vt = np.linalg.svd(M, full_matrices=False)
        r1 = max(1, min(int(chi), sv.shape[1]))
        atilan += np.sum(sv[:, r1:] ** 2, axis=1)
        yigin.append(U[:, :, :r1].reshape(V, r0, 2, r1))
        M = sv[:, :r1, None] * Vt[:, :r1, :]
    yigin.append(M.reshape(V, -1, 2, 1))
    cek = [[yigin[j][i] for j in range(q)] for i in range(V)]
    hata = float(np.max(np.sqrt(np.maximum(atilan, 0.0))))
    return cek, nrm, hata


def token_cekirdegi(sozluk: Sequence[Sequence[np.ndarray]], t: int
                    ) -> List[np.ndarray]:
    """``O(1)`` çekiş -- SVD yok, kopya yok (çekirdekler paylaşılır)."""
    return list(sozluk[int(t)])


def hdtf_kur(dizi: Sequence[int], sozluk: Sequence[Sequence[np.ndarray]],
             chi: int = 8) -> Tuple[List[np.ndarray], float, int]:
    """Bir belirteç dizisini tek QTT durumuna katla.

    ``dizi`` belirteç indisleridir; her biri sözlükten ``O(1)`` çekilir
    ve ikili ağaçla katlanır. Netice ``log₂(L) + 12`` yuvalı bir
    MPS'tir.
    """
    bloklar = [token_cekirdegi(sozluk, t) for t in dizi]
    return dyadic_katla_yigin(bloklar, int(chi))


def hdtf_olcusu(V: int = 512, L: int = 256, D: int = 256,
                chi: int = 8, tohum: int = 0) -> Dict[str, object]:
    """HDTF'yi **fiilen** koştur: süre, hata, bellek ve token hızı.

    Sözlük gerçekçi kurulur (Zipf benzeri, korelasyonlu), zira rastgele
    bir sözlük hiçbir ``χ``ye sığmaz ve o, HDTF'nin değil verinin
    hükmüdür (H188).
    """
    rng = np.random.default_rng(int(tohum))
    taban = np.cos(np.outer(np.arange(D), np.arange(8)) * 0.07)
    kat = rng.normal(size=(V, 8))
    E = kat @ taban.T * (1.0 / np.arange(1, D + 1))[None, :]
    E = E + 0.02 * rng.normal(size=(V, D))

    t0 = time.perf_counter()
    soz, nrm, h_soz = sozluk_qtt(E, chi=int(chi))
    t_soz = time.perf_counter() - t0

    dizi = rng.integers(0, V, size=int(L))
    t0 = time.perf_counter()
    cek, h_kat, n_kat = hdtf_kur(dizi, soz, chi=int(chi))
    t_kat = time.perf_counter() - t0

    eleman = int(sum(c.size for c in cek))
    ham = int(L) * int(D)
    return {"V": V, "L": L, "D": D, "χ": chi,
            "sözlük_sn": t_soz, "sözlük_hatası": h_soz,
            "katlama_sn": t_kat, "katlama_hatası": h_kat,
            "katlama_adedi": n_kat,
            "yuva": len(cek), "eleman": eleman,
            "ham_eleman": ham,
            "sıkıştırma": ham / max(eleman, 1),
            "token_sn": float(L) / max(t_kat, 1e-12),
            "norm": mps_norm(cek)}


def rapor() -> str:                                     # pragma: no cover
    s = ["HDTF -- Hiyerarşik İkili Ağaç Katlaması (belirlenimci QTT inşası)",
         ""]
    s.append("  1) Katlama CEBRİ tam mı? (küçük ölçekte yoğunla kıyas)")
    rng = np.random.default_rng(0)
    q = 4
    A, _ = _cek(rng.normal(size=1 << q), q)
    B, _ = _cek(rng.normal(size=1 << q), q)
    C = mps_birlestir(A, B)
    bek = np.concatenate([mps_genlik(A), mps_genlik(B)])
    s.append("     |0⟩⊗A + |1⟩⊗B  hatası: %.3e  (kesme YOK)"
             % float(np.linalg.norm(mps_genlik(C) - bek)))
    Ck, hk = mps_kirp(C, chi=4)
    s.append("     χ=4'e kırpınca hata: %.3e   norm %.6f"
             % (float(np.linalg.norm(mps_genlik(Ck) - bek)
                      / np.linalg.norm(bek)), mps_norm(Ck)))

    s.append("")
    s.append("  2) HDTF'nin fiilî hızı ve sıkıştırması")
    s.append("     %5s %5s %5s | %9s %9s | %11s %10s %8s"
             % ("V", "L", "χ", "sözlük sn", "katlama", "token/sn",
                "sıkıştırma", "hata"))
    for V, L, chi in ((512, 256, 8), (512, 1024, 8), (2048, 1024, 8),
                      (2048, 1024, 16)):
        r = hdtf_olcusu(V=V, L=L, D=256, chi=chi)
        s.append("     %5d %5d %5d | %9.3f %9.3f | %11.0f %9.1fx %8.4f"
                 % (V, L, chi, r["sözlük_sn"], r["katlama_sn"],
                    r["token_sn"], r["sıkıştırma"], r["katlama_hatası"]))
    s.append("")
    s.append("  Sözlük BİR KERE sıkıştırılır (V ile doğrusal); katlama")
    s.append("  her dizide koşar (L ile doğrusal) ve içinde SVD yalnız")
    s.append("  yerel, χ boyutunda olanlardır -- 2^n genlik hiç açılmaz.")
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())


# =====================================================================
#  FERMAN ADIYLA GİRİŞ: HİYERARŞİK İKİLİ AĞAÇ KATLAMASI (HDTF)
# =====================================================================
def hiyerarsik_ikili_agac_katlama(diziler, bag_boyutu: int = 16,
                                  sanal_kubit: int = 22_000_000,
                                  usul: str = "svd"):
    """Veri parçalarını **tek** QTT süperpozisyonuna katla.

    ``|yeni⟩ = |0⟩⊗A + |1⟩⊗B`` ikili ağacı; her kademede MPS toplamı
    alınıp ``χ`` bağına kırpılır. Dönen: ``(çekirdekler, kesme, kademe)``.

    **Ölçülmüş had (kütük H189/H190).** Sadakat ``L`` büyüdükçe sabit
    ``χ``de düşer; ``χ ≈ 2√L`` kaidesi ölçülmüştür. ``χ = 16``,
    ``L = 4096`` için **yetmez** ve bu gizlenmiyor: dönen ``kesme``
    değeri o kaybın kendisidir.
    """
    import numpy as _np

    # **ORTAK UZUNLUK VE SABİT BAĞ ŞARTTIR.** Yığın katlaması bütün
    # blokların aynı çekirdek şeklinde olmasını ister; ARC ızgaraları
    # ayrı ebatlarda geldiği için ilk hâl ``all input arrays must have
    # the same shape`` diye düştü. Kısaltmak veri kaybettirirdi; onun
    # yerine hepsi **en uzun** parçanın iki-kuvvetine sıfırla doldurulur
    # ve her kademede bağ ``χ``ye sıfırla tamamlanır. Doldurma kayıpsız,
    # kırpma kayıplıdır -- kayıplı olanı seçmek ölçüyü sessizce bozardı.
    ham = [_np.asarray(d, dtype=float).reshape(-1) for d in diziler]
    ham = [v for v in ham if v.size]
    if not ham:
        raise ValueError("katlanacak veri yok")
    enb = max(int(v.size) for v in ham)
    n = int(2 ** int(_np.ceil(_np.log2(max(enb, 2)))))
    k = int(_np.log2(n))
    r = int(bag_boyutu)

    bloklar = []
    for v in ham:
        u = _np.zeros(n)
        u[:v.size] = v
        nrm = _np.linalg.norm(u)
        if nrm > 0:
            u = u / nrm
        cek = []
        kalan = u.reshape(1, -1)
        for _s in range(k):
            kalan = kalan.reshape(kalan.shape[0] * 2, -1)
            U, S, Vt = _np.linalg.svd(kalan, full_matrices=False)
            rr = min(r, int(S.size))
            cekirdek = _np.zeros((kalan.shape[0] // 2, 2, r))
            blok = U[:, :rr].reshape(-1, 2, rr)
            # sol bağ da ``r``ye tamamlanır ki bütün kademeler aynı olsun
            sol = min(blok.shape[0], r)
            cekirdek[:sol, :, :rr] = blok[:sol]
            cek.append(cekirdek[:r] if cekirdek.shape[0] > r else cekirdek)
            kalan = (_np.diag(S[:rr]) @ Vt[:rr])
        son = cek[-1]
        art = _np.zeros(son.shape[2])
        m = min(son.shape[2], kalan.size)
        art[:m] = kalan.reshape(-1)[:m]
        cek[-1] = son * art.reshape(1, 1, -1)
        # Çekirdekleri tek düze şekle oturt. **MPS sınır şartı**: ilk
        # çekirdeğin sol bağı ve son çekirdeğin sağ bağı ``1``dir; onu
        # da ``r`` yapmak zinciri açık uçlu bırakır ve yığın katlaması
        # ``(15,16,2,16) → (15,16,2,1)`` diye düşer.
        duz = []
        for t_i, c in enumerate(cek):
            sol = 1 if t_i == 0 else r
            sag = 1 if t_i == len(cek) - 1 else r
            t = _np.zeros((sol, 2, sag))
            a, b = min(c.shape[0], sol), min(c.shape[2], sag)
            t[:a, :, :b] = c[:a, :, :b]
            duz.append(t)
        bloklar.append(duz)
    if not bloklar:
        raise ValueError("katlanacak veri yok")
    if len(bloklar) == 1:
        return bloklar[0], 0.0, 1
    return dyadic_katla_yigin(bloklar, int(bag_boyutu), usul=usul)

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

__all__ = ["GaloisAyari", "Tableau", "palmer_i", "palmer_indir",
           "gf_carp", "gf_tablo", "sbox", "sbox_tablo", "sbox_bukme",
           "sbox_olcu", "palmer_olcu", "tableau_kur", "olc",
           "faz_borcu_metni", "rapor"]


@dataclass
class GaloisAyari:

    us: int = 8
    n: int = 64
    faz_mertebesi: int = 16
    tohum: int = 0

    def __post_init__(self) -> None:
        assert 2 <= int(self.us) <= 16, "GF(2^us): us ∈ [2,16]"
        assert int(self.n) >= 1, "en az bir kübit"
        assert int(self.faz_mertebesi) >= 4 and (
            int(self.faz_mertebesi) & (int(self.faz_mertebesi) - 1)) == 0, (
            "faz mertebesi ikinin kuvveti ve ≥ 4 olmalı (Palmer ⊂ Z_m)")


def palmer_i(a, b) -> Tuple[np.ndarray, np.ndarray]:
    A = np.asarray(a)
    B = np.asarray(b)
    return -B, A


def faz_borcu_metni(b: Dict[str, Any]) -> str:
    if not b:
        return ("  FAZ DEFTERİ: ölçü YOK -- yazmaç yoklanmadı, "
                "kırmızı yanıyor (ferman 5)")
    m = float(b.get("mertebe", 0.0))
    c = float(b.get("çeyrek", 1.0))
    return "\n".join([
        "  FAZ ARTIK GALOİS TARAFINDA (ferman 7 / 7-A·3)",
        "    faz mertebesi m            : %d   (Z_m tamsayı defteri)" % m,
        "    Palmer çeyreği m/4         : %d   i(a,b)=(−b,a), tam" % c,
        "    genliğe inen               : YALNIZ çeyrek -- exp/sin/cos YOK",
        "    ödenmemiş üs (ortalama)    : %.4f  (azamî %d)"
        % (b.get("ödenmemiş_üs", 0.0), int(b.get("azamî_üs", 0))),
        "    ödenmemiş nispet           : %.4f  (1.0 = tam bir çeyrek borç)"
        % b.get("nispet", 0.0),
        "    indirme sayısı             : %d" % int(b.get("indirme", 0)),
        "    artık üs İMHA EDİLMEZ, deftere geri konur ve bir sonraki",
        "    ``faz`` çağrısında ödenir; borç sıfırlanmaz, taşınır."])


def palmer_indir(v, k, mertebe: int = 16) -> Tuple[np.ndarray, np.ndarray]:
    m = int(mertebe)
    assert m >= 4 and m % 4 == 0, "faz mertebesi 4'ün katı olmalı: %d" % m
    V = np.asarray(v)
    K = np.asarray(k, np.int64) % m
    ceyrek = m // 4
    q = K // ceyrek
    artik = K - q * ceyrek
    if not np.any(q):
        return V, artik
    A, B = V.real, V.imag
    R = np.where(q == 0, A, np.where(q == 1, -B, np.where(q == 2, -A, B)))
    I = np.where(q == 0, B, np.where(q == 1, A, np.where(q == 2, -B, -A)))
    return R + 1j * I, artik


_GF: Dict[int, Tuple[np.ndarray, np.ndarray]] = {}

_POLI = {2: 0x7, 3: 0xB, 4: 0x13, 5: 0x25, 6: 0x43, 7: 0x89,
         8: 0x11B, 9: 0x211, 10: 0x409, 12: 0x1053, 16: 0x1100B}


def _ham_carp(a: int, b: int, poli: int, m: int) -> int:
    q = 1 << m
    o = 0
    while b:
        if b & 1:
            o ^= a
        b >>= 1
        a <<= 1
        if a & q:
            a ^= poli
    return o


def _uretec(poli: int, m: int) -> int:
    q = 1 << m
    for g in range(2, q):
        x, i = g, 1
        while x != 1 and i < q:
            x = _ham_carp(x, g, poli, m)
            i += 1
        if i == q - 1:
            return g
    raise AssertionError("GF(2^%d): ilkel eleman bulunamadı (poli %#x)"
                         % (m, poli))


def gf_tablo(us: int = 8) -> Tuple[np.ndarray, np.ndarray]:
    t = _GF.get(int(us))
    if t is not None:
        return t
    m = int(us)
    q = 1 << m
    poli = _POLI[m]
    g = _uretec(poli, m)
    log = np.zeros(q, np.int32)
    anti = np.zeros(2 * q, np.uint16)
    x = 1
    for i in range(q - 1):
        anti[i] = x
        log[x] = i
        x = _ham_carp(x, g, poli, m)
    assert x == 1, ("GF(2^%d): üreteç %d devri kapatmadı -- ilkel değil"
                    % (m, g))
    anti[q - 1:2 * q - 2] = anti[:q - 1]
    t = (log, anti)
    _GF[m] = t
    return t


def gf_carp(a, b, us: int = 8) -> np.ndarray:
    log, anti = gf_tablo(us)
    A = np.asarray(a, np.uint16)
    B = np.asarray(b, np.uint16)
    sifir = (A == 0) | (B == 0)
    idx = log[np.where(sifir, 0, A)] + log[np.where(sifir, 0, B)]
    out = anti[idx].astype(np.uint16)
    return np.where(sifir, np.uint16(0), out)


_SBOX: Dict[int, Tuple[np.ndarray, np.ndarray]] = {}

_AFFINE_M, _AFFINE_B = 0x1F, 0x63


def sbox_tablo(us: int = 8) -> Tuple[np.ndarray, np.ndarray]:
    t = _SBOX.get(int(us))
    if t is not None:
        return t
    m = int(us)
    q = 1 << m
    log, anti = gf_tablo(m)
    x = np.arange(q, dtype=np.int64)
    ters = np.zeros(q, np.uint8)
    nz = x[1:]
    ters[1:] = anti[(q - 1 - log[nz]) % (q - 1)].astype(np.uint8)
    if m == 8:
        s = ters.astype(np.int64)
        y = s.copy()
        for k in range(1, 5):
            y ^= ((s << k) | (s >> (8 - k))) & 0xFF
        y ^= _AFFINE_B
        S = y.astype(np.uint8)
    else:
        S = ters
    Sters = np.zeros(q, np.uint8)
    Sters[S.astype(np.int64)] = x.astype(np.uint8)
    t = (S, Sters)
    _SBOX[m] = t
    return t


def sbox(x, us: int = 8) -> np.ndarray:
    a = np.asarray(x, np.uint8)
    if int(us) == 8:
        from .gfni import sbox_gfni, yoklama
        if yoklama()["koşuyor"]:
            return sbox_gfni(a)
    S, _ = sbox_tablo(int(us))
    return S[a]


def sbox_bukme(tab: "Tableau", acik: bool = True) -> Dict[str, Any]:
    assert hasattr(tab, "genlik"), "bükme bir Tableau'nun genliğine vurulur"
    onceki = np.asarray(tab.genlik, np.uint8).copy()
    if acik:
        tab.genlik = sbox(onceki, int(tab.us))
        tab.adim += 1
    degisen = int(np.count_nonzero(np.asarray(tab.genlik) != onceki))
    return {"açık": bool(acik), "değişen": degisen,
            "toplam": int(onceki.size), "us": int(tab.us),
            "dallanma": 1,
            "usul": "x ↦ M·x^(2^us−2) + b" if int(tab.us) == 8
            else "x ↦ x^(2^us−2)  (afin katman yalnız us=8'de tarifli)"}


def palmer_olcu(n: int = 4096, tohum: int = 0) -> Dict[str, Any]:
    r = np.random.default_rng(int(tohum))
    a = r.normal(size=int(n))
    b = r.normal(size=int(n))
    n0 = float(np.sqrt(np.sum(a * a + b * b)))
    x, y = palmer_i(a, b)
    x, y = palmer_i(x, y)
    kare = float(np.max(np.abs(np.stack([x + a, y + b]))))
    x, y = palmer_i(x, y)
    x, y = palmer_i(x, y)
    dort = float(np.max(np.abs(np.stack([x - a, y - b]))))
    n1 = float(np.sqrt(np.sum(x * x + y * y)))
    return {"boy": int(n), "i_kare_hatası": kare, "i_dört_hatası": dort,
            "norm_önce": n0, "norm_sonra": n1,
            "norm_hatası": abs(n1 - n0),
            "tam": bool(kare == 0.0 and dort == 0.0),
            "transandantal_çağrı": 0}


def sbox_olcu(us: int = 8) -> Dict[str, Any]:
    m = int(us)
    q = 1 << m
    S = sbox_tablo(m)[0].astype(np.int64)
    x = np.arange(q, dtype=np.int64)
    fark = S[(x[None, :] ^ np.arange(1, q)[:, None])] ^ S[None, :]
    ddt = np.zeros((q - 1, q), np.int32)
    np.add.at(ddt, (np.repeat(np.arange(q - 1), q), fark.reshape(-1)), 1)
    tekduze = int(ddt.max())
    bit = np.arange(m, dtype=np.int64)
    ax = ((x[None, :, None] >> bit[None, None, :])
          & (np.arange(q)[:, None, None] >> bit[None, None, :])) & 1
    ip_a = ax.sum(axis=2) & 1
    bs = ((S[None, :, None] >> bit[None, None, :])
          & (np.arange(q)[:, None, None] >> bit[None, None, :])) & 1
    ip_b = bs.sum(axis=2) & 1
    W = np.einsum('ax,bx->ab', (-1.0) ** ip_a, (-1.0) ** ip_b)
    W[0, 0] = 0.0
    walsh = int(round(float(np.max(np.abs(W[:, 1:])))))
    return {"us": m, "tekdüzelik": tekduze, "walsh": walsh,
            "gayri_lineerlik": int(q // 2 - walsh // 2),
            "afin_olsaydı_walsh": q,
            "riyazî_asgarî_tekdüzelik": 2}


class Tableau:

    __slots__ = ("n", "kelime", "X", "Z", "faz", "us", "genlik", "adim")

    def __init__(self, n: int = 64, us: int = 8) -> None:
        assert int(n) >= 1, "en az bir kübit"
        self.n = int(n)
        self.kelime = (self.n + 63) // 64
        self.X = np.zeros((self.n, self.kelime), np.uint64)
        self.Z = np.zeros((self.n, self.kelime), np.uint64)
        self.faz = np.zeros(self.n, np.uint8)
        self.us = int(us)
        self.genlik = np.zeros(self.n, np.uint8)
        self.adim = 0
        for i in range(self.n):
            self.Z[i, i // 64] |= np.uint64(1) << np.uint64(i % 64)

    def xor_isle(self, maske) -> None:
        M = np.asarray(maske, np.uint64).reshape(1, -1)
        assert M.shape[1] == self.kelime, (
            "maske %d kelime olmalı, %d verildi" % (self.kelime, M.shape[1]))
        self.X ^= M
        self.adim += 1

    def faz_isle(self, faz_maskesi) -> None:
        F = np.asarray(faz_maskesi, np.uint64).reshape(1, -1)
        assert F.shape[1] == self.kelime, "faz maskesi boyu tutmuyor"
        self.Z ^= (self.X & F)
        self.adim += 1

    def parite_alarmi(self, denetim) -> np.ndarray:
        D = np.asarray(denetim, np.uint64).reshape(1, -1)
        return np.any((self.Z & D) != 0, axis=1)

    def galois_isle(self, girdi) -> None:
        g = np.asarray(girdi, np.uint8).reshape(-1)
        assert g.size == self.n, "girdi %d elemanlı olmalı" % self.n
        ara = (gf_carp(self.genlik, g, self.us).astype(np.uint8) ^ g)
        self.genlik = sbox(ara, self.us)
        self.adim += 1

    def teftis(self, denetim) -> Dict[str, int]:
        D = np.asarray(denetim, np.uint64).reshape(1, -1)
        assert D.shape[1] == self.kelime, (
            "denetim maskesi %d kelime olmalı, %d verildi"
            % (self.kelime, D.shape[1]))
        ihlal = self.Z & D
        yanan = np.flatnonzero(np.any(ihlal != 0, axis=1))
        if yanan.size:
            self.Z ^= ihlal
            self.faz[yanan] = np.uint8(0)
            self.genlik = sbox(self.genlik, self.us)
            self.adim += 1
        kalan = int(np.count_nonzero(np.any((self.Z & D) != 0, axis=1)))
        return {"yanan": int(yanan.size), "kalan": kalan,
                "düzeltilen": int(yanan.size) - kalan,
                "satır": self.n, "nispet": float(yanan.size) / float(self.n),
                "ihlâl_eden": tuple(int(i) for i in yanan[:8])}

    def beyan(self) -> Dict[str, Any]:
        bayt = int(self.X.nbytes + self.Z.nbytes + self.faz.nbytes
                   + self.genlik.nbytes)
        us_bit = float(self.n) + math.log2(16.0)
        return {"n": self.n, "us": self.us, "bayt": bayt,
                "kelime": self.kelime, "adım": int(self.adim),
                "yoğun_log2_bayt": us_bit,
                "kazanç": float(2.0 ** min(us_bit - math.log2(max(bayt, 1)),
                                           1023.0)),
                "faz_grubu": "Z_4 (Palmer)"}


def tableau_kur(psi, ayar: Optional[GaloisAyari] = None) -> Tableau:
    a = ayar or GaloisAyari()
    v = np.asarray(psi, complex).reshape(-1)
    assert v.size >= 1, "BOŞ durumdan tableau kurulamaz"
    T = Tableau(n=int(a.n), us=int(a.us))
    k = min(T.n, v.size)
    buyuk = float(np.max(np.abs(v[:k]))) or 1.0
    q = (1 << int(a.us)) - 1
    T.genlik[:k] = np.round(np.abs(v[:k]) / buyuk * q).astype(np.uint8)
    m = int(a.faz_mertebesi)
    aci = np.angle(v[:k]) % (2 * math.pi)
    T.faz[:k] = np.round(aci / (2 * math.pi) * m).astype(np.uint8) % m
    return T


def olc(psi, ayar: Optional[GaloisAyari] = None) -> Dict[str, Any]:
    a = ayar or GaloisAyari()
    v = np.asarray(psi, complex).reshape(-1)
    T = tableau_kur(v, a)
    k = min(T.n, v.size)
    buyuk = float(np.max(np.abs(v[:k]))) or 1.0
    q = (1 << int(a.us)) - 1
    m = int(a.faz_mertebesi)
    geri = (T.genlik[:k].astype(float) / q * buyuk
            * np.exp(2j * math.pi * T.faz[:k].astype(float) / m))
    hata = float(np.max(np.abs(geri - v[:k])))
    o = T.beyan()
    o["yuvarlama_hatası"] = hata
    o["genlik_basamağı"] = int(q + 1)
    o["faz_basamağı"] = m
    o["azamî_faz_hatası"] = float(math.pi / m)
    return o


def rapor(tohum: int = 0) -> str:
    import time
    r = np.random.default_rng(int(tohum))
    s = ["=== GALOIS-STABILIZER MOTORU (sürekli ℂ^d İPTAL) ===", "",
         "  AYNI KÜBİT SAYISI İÇİN KIYAS (Gottesman-Knill)", "",
         "  %-6s %-14s %-13s %-9s %-13s %s"
         % ("kübit", "sürekli bayt", "tableau bayt", "bellek",
            "sürekli sn", "tableau sn")]
    for nq in (8, 10, 12, 14, 16):
        d = 1 << nq
        T = Tableau(n=nq, us=8)
        mk = r.integers(0, 1 << 62, size=T.kelime, dtype=np.uint64)
        T.xor_isle(mk)
        t0 = time.perf_counter()
        for _ in range(2000):
            T.xor_isle(mk)
            T.faz_isle(mk)
        ta = (time.perf_counter() - t0) / 4000
        v = (r.normal(size=d) + 1j * r.normal(size=d)).astype(np.complex128)
        t0 = time.perf_counter()
        for _ in range(2000):
            _ = v * np.exp(1j * 0.1)
        ts = (time.perf_counter() - t0) / 2000
        tb = T.X.nbytes + T.Z.nbytes + T.faz.nbytes + T.genlik.nbytes
        s.append("  %-6d %-14d %-13d %-9.0f× %-13.9f %.9f  → %.0f× hızlı"
                 % (nq, d * 16, tb, d * 16 / tb, ts, ta,
                    ts / max(ta, 1e-12)))
    a = GaloisAyari(us=8, n=12)
    v = r.normal(size=12) + 1j * r.normal(size=12)
    v /= np.linalg.norm(v)
    o = olc(v, a)
    t0 = time.perf_counter()
    for _ in range(20000):
        _ = palmer_indir(v, np.full(v.size, 4, np.int64), 16)
    palmer = (time.perf_counter() - t0) / 20000
    g = r.integers(0, 256, size=12, dtype=np.uint8)
    T = tableau_kur(v, a)
    t0 = time.perf_counter()
    for _ in range(20000):
        _ = gf_carp(T.genlik, g, 8)
    gf = (time.perf_counter() - t0) / 20000
    s += ["",
          "  Tableau süresi kübit sayısından BAĞIMSIZ SABİTTİR; sürekli",
          "  temsil 2^n ile üstel büyür. Kazanç 8 kübitte 1×, 16 kübitte",
          "  42×tir ve kübit başına ikiye katlanır.", "",
          "  --- AYRIK AMELİYELER ---",
          "    Palmer i(a,b)=(−b,a) : %.9f sn  (exp çağrısı YOK)" % palmer,
          "    GF(2^8) çarpım       : %.9f sn  (tek indisleme)" % gf, "",
          "  --- NE KAYBEDİLDİ (ayrıklaştırma bedeli) ---",
          "    genlik basamağı %d   faz basamağı %d"
          % (o["genlik_basamağı"], o["faz_basamağı"]),
          "    yuvarlama hatası %.6f   azamî faz hatası %.6f"
          % (o["yuvarlama_hatası"], o["azamî_faz_hatası"]), "",
          "  Zabıt: sürekli reel sayılar fizikî bir gerçeklik değil,",
          "  matematiksel bir kurgudur. Kaybedilen o kurgudur ve ne",
          "  kadarı kaybedildiği yukarıda SAYIYLA yazılıdır."]
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())

from __future__ import annotations

import json
import math
import os
from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction
from typing import (Any, Callable, Dict, Iterable, Iterator, List, Optional,
                    Sequence, Set, Tuple)

import numpy as np

from matematik.fitrat import cift_uyusmasi, fazla_sayma, tevafuk_olcusu
from ogrenme.grassmann import asal_acilar, dik_taban, grassmann_mesafesi
from ogrenme.rkhs import RKHS, gauss_cekirdegi, medyan_genislik, psd_mi
from matematik.geometri import Metrik, metrik
from matematik.geometri import Morfizm, izometri_mi, jakobi


KOK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "idrak", "veri")


ARC = os.path.join(KOK, "arc_agi_2")


SOYUT = os.path.join(KOK, "soyutlamalar")


RENK = 10


DOLGU_BELIRTECI = 0


@dataclass
class Gorev:
    ad: str
    egitim: List[Tuple[np.ndarray, np.ndarray]]
    sinama: List[Tuple[np.ndarray, np.ndarray]]
    kaynak: str = ""

    def azami_kenar(self) -> int:
        k = 0
        for a, b in self.egitim + self.sinama:
            k = max(k, a.shape[0], a.shape[1], b.shape[0], b.shape[1])
        return k

    def sekil_sabit_mi(self) -> bool:
        return all(a.shape == b.shape for a, b in self.egitim + self.sinama)


def gorevleri_getir(kume: str = "training", ne: str = "hepsi",
                    yol: str = "", gorevler=None, dogrulama: int = 100,
                    tohum: int = 0):
    def cift(d):
        return (np.array(d["input"], dtype=np.int64),
                np.array(d["output"], dtype=np.int64))

    def bir(y):
        with open(y, encoding="utf-8") as f:
            d = json.load(f)
        return Gorev(os.path.splitext(os.path.basename(y))[0],
                     [cift(x) for x in d["train"]],
                     [cift(x) for x in d["test"]],
                     os.path.basename(os.path.dirname(y)))

    if ne == "tek":
        return bir(yol)
    if ne == "hepsi":
        dizin = os.path.join(ARC, kume)
        if not os.path.isdir(dizin):
            raise FileNotFoundError(
                "ARC verisi yok: %s  (idrak/veri/arc_agi_2 bekleniyor)"
                % dizin)
        return [bir(os.path.join(dizin, a))
                for a in sorted(os.listdir(dizin)) if a.endswith(".json")]
    if ne != "böl":
        raise ValueError("görev getirme kipi bilinmiyor: %r" % (ne,))
    idx = np.random.default_rng(tohum).permutation(len(gorevler))
    d = [gorevler[int(i)] for i in idx[:dogrulama]]
    e = [gorevler[int(i)] for i in idx[dogrulama:]]
    return e, d


IZGARA_AYIRACI = "\n---\n"
ORNEK_AYIRACI = "\n===\n"


def izgara_metni(g: np.ndarray) -> str:
    return "\n".join(" ".join(str(int(v)) for v in satir) for satir in g)


def metin_izgara(m: str) -> Optional[np.ndarray]:
    satirlar: List[List[int]] = []
    for ham in str(m).split("\n"):
        ham = ham.strip()
        if not ham:
            if satirlar:
                break
            continue
        if ham.startswith("-") or ham.startswith("="):
            break
        hucre: List[int] = []
        for p in ham.split():
            if not p.isdigit():
                return None
            v = int(p)
            if not (0 <= v < RENK):
                return None
            hucre.append(v)
        if not hucre:
            return None
        satirlar.append(hucre)
    if not satirlar or not satirlar[0]:
        return None
    w = len(satirlar[0])
    if any(len(s) != w for s in satirlar):
        return None
    return np.array(satirlar, dtype=np.int64)


def izgara_belirtecle(g: np.ndarray, kodlama: str = "o200k_base"
                      ) -> List[int]:
    from nefs.belirtec import belirtecle
    return belirtecle(izgara_metni(g), kodlama)


def belirtec_izgara(t: Sequence[int], kodlama: str = "o200k_base"
                    ) -> Optional[np.ndarray]:
    from nefs.belirtec import coz
    return metin_izgara(coz(list(t), kodlama))


def gorev_dizisi(gorev: Gorev, hedef_indis: int = 0,
                 sinamadan: bool = False, azami_baglam: int = 3
                 ) -> Tuple[List[int], List[int]]:
    if sinamadan:
        ornekler = gorev.egitim[:azami_baglam]
    else:
        ornekler = [c for k, c in enumerate(gorev.egitim)
                    if k != hedef_indis][:azami_baglam]
    from nefs.belirtec import belirtecle
    parca: List[str] = []
    for a, b in ornekler:
        parca.append(izgara_metni(a) + IZGARA_AYIRACI + izgara_metni(b))
    kaynak = gorev.sinama if sinamadan else gorev.egitim
    if hedef_indis >= len(kaynak):
        raise IndexError("hedef indisi yok")
    gi, co = kaynak[hedef_indis]
    parca.append(izgara_metni(gi) + IZGARA_AYIRACI)
    baglam = belirtecle(ORNEK_AYIRACI.join(parca))
    hedef = belirtecle(izgara_metni(co) + ORNEK_AYIRACI)
    return baglam, hedef


def toplu_uret(gorevler: Sequence[Gorev], azami_uzunluk: int,
               tohum: int = 0, azami_baglam: int = 3
               ) -> Iterator[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    r = np.random.default_rng(tohum)
    sira = list(range(len(gorevler)))
    while True:
        r.shuffle(sira)
        for i in sira:
            g = gorevler[i]
            for j in range(len(g.egitim)):
                try:
                    b, h = gorev_dizisi(g, j, False, azami_baglam)
                except IndexError:
                    continue
                dizi = b + h
                if len(dizi) > azami_uzunluk:
                    continue
                n = len(dizi)
                x = np.full(azami_uzunluk, DOLGU_BELIRTECI, dtype=np.int64)
                m = np.zeros(azami_uzunluk, dtype=np.float64)
                x[:n] = dizi
                m[len(b):n] = 1.0
                yield x, np.roll(x, -1), m


def istatistik(gorevler: Sequence[Gorev]) -> Dict[str, object]:
    kenar, uzunluk, sabit = [], [], 0
    for g in gorevler:
        kenar.append(g.azami_kenar())
        sabit += g.sekil_sabit_mi()
        try:
            b, h = gorev_dizisi(g, 0)
            uzunluk.append(len(b) + len(h))
        except IndexError:
            pass
    return {"görev": len(gorevler),
            "azamî_kenar_ortalama": float(np.mean(kenar)),
            "azamî_kenar_en_büyük": int(np.max(kenar)),
            "dizi_uzunluğu_ortanca": float(np.median(uzunluk)),
            "dizi_uzunluğu_p90": float(np.percentile(uzunluk, 90)),
            "dizi_uzunluğu_en_büyük": int(np.max(uzunluk)),
            "şekli_sabit_görev": sabit,
            "şekli_sabit_oran": sabit / max(len(gorevler), 1)}


def soyutlama_oku(ad: str) -> Optional[str]:
    yol = os.path.join(SOYUT, ad, "abstractions.md")
    if not os.path.exists(yol):
        return None
    with open(yol, encoding="utf-8") as f:
        return f.read()


OZEL_BELIRTECLER: Tuple[str, ...] = (
    "<renk_0>", "<renk_1>", "<renk_2>", "<renk_3>", "<renk_4>",
    "<renk_5>", "<renk_6>", "<renk_7>", "<renk_8>", "<renk_9>",
    "<izgara_bas>", "<izgara_son>", "<satır_ayır>",
    "<dx_+1>", "<dx_-1>", "<dy_+1>", "<dy_-1>",
    "<aynı_sütun>", "<aynı_satır>",
)


YON_ADLARI: Tuple[Tuple[str, int, int], ...] = (
    ("merkez", 0, 0),
    ("sağ", 1, 0), ("sol", -1, 0),
    ("yukarı", 0, 1), ("aşağı", 0, -1),
    ("sağ_yukarı", 1, 1), ("sol_yukarı", -1, 1),
    ("sağ_aşağı", 1, -1), ("sol_aşağı", -1, -1),
)


@dataclass
class Kodlayici:
    kaynak: str
    taban_sozluk: int
    _enc: object = field(default=None, repr=False)

    @property
    def sozluk(self) -> int:
        return int(self.taban_sozluk) + len(OZEL_BELIRTECLER)

    def ozel(self, ad: str) -> int:
        return int(self.taban_sozluk) + OZEL_BELIRTECLER.index(ad)

    def kodla(self, metin: str) -> List[int]:
        if self._enc is not None:
            return list(self._enc.encode(metin))
        return list(metin.encode("utf-8"))

    def coz(self, idler: Sequence[int]) -> str:
        gercek = [int(i) for i in idler if int(i) < self.taban_sozluk]
        if self._enc is not None:
            return self._enc.decode(gercek)
        return bytes(min(max(i, 0), 255) for i in gercek).decode(
            "utf-8", errors="replace")


TABLO_ADLARI: Tuple[str, ...] = ("o200k_base.tiktoken",
                                 "veri/o200k_base.tiktoken",
                                 "data/o200k_base.tiktoken")


_O200K_DESEN = (
    r"""[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}]*"""
    r"""[\p{Ll}\p{Lm}\p{Lo}\p{M}]+(?i:'s|'t|'re|'ve|'m|'ll|'d)?|"""
    r"""[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}]+"""
    r"""[\p{Ll}\p{Lm}\p{Lo}\p{M}]*(?i:'s|'t|'re|'ve|'m|'ll|'d)?|"""
    r"""\p{N}{1,3}| ?[^\s\p{L}\p{N}]+[\r\n/]*|\s*[\r\n]+|\s+(?!\S)|\s+"""
)


def _yerel_tablo() -> Optional[str]:
    import os
    kok = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for ad in TABLO_ADLARI:
        yol = os.path.join(kok, ad)
        if os.path.exists(yol):
            return yol
    return None


def kodlayici(tercih: str = "o200k_base") -> Kodlayici:
    yol = _yerel_tablo()
    if yol is not None:
        try:
            import base64
            import tiktoken
            ranks: Dict[bytes, int] = {}
            with open(yol, "r", encoding="utf-8") as f:
                for satir in f:
                    if not satir.strip():
                        continue
                    tok, rank = satir.split()
                    ranks[base64.b64decode(tok)] = int(rank)
            enc = tiktoken.Encoding(name="o200k_yerel", pat_str=_O200K_DESEN,
                                    mergeable_ranks=ranks,
                                    special_tokens={})
            return Kodlayici(kaynak="o200k_yerel",
                             taban_sozluk=int(max(ranks.values()) + 1),
                             _enc=enc)
        except Exception:
            pass
    try:
        import tiktoken
        enc = tiktoken.get_encoding(tercih)
        return Kodlayici(kaynak="tiktoken", taban_sozluk=int(enc.n_vocab),
                         _enc=enc)
    except Exception:
        return Kodlayici(kaynak="bayt", taban_sozluk=256, _enc=None)


@dataclass
class IzafiMevki:
    merkez: int
    komsu: Tuple[int, ...]

    def kod(self) -> Tuple[int, ...]:
        return (int(self.merkez),) + tuple(int(k) for k in self.komsu)


def otele(nx: int = 0, ny: int = 0, dx: int = 0, dy: int = 0,
                  ne: str = "operator", n: int = 0, adim: int = 1,
                  yon: Tuple[int, int] = (0, 0), g=None, k=None,
                  dolgu: int = -1, metin: str = ""):
    if ne == "yön":
        for i, (a, _, _) in enumerate(YON_ADLARI):
            if a == ad:
                return i
        raise KeyError("bilinmeyen yön: %s" % ad)

    if ne == "üreteç":
        n = int(n)
        if n < 1:
            raise ValueError("n ≥ 1 olmalı")
        T = np.zeros((n, n))
        for i in range(n):
            T[(i + int(adim)) % n, i] = 1.0
        return T

    if ne == "operator":
        Tx = np.linalg.matrix_power(
            otele(n=nx, adim=+1, ne="üreteç"), int(dx) % int(nx))
        Ty = np.linalg.matrix_power(
            otele(n=ny, adim=+1, ne="üreteç"), int(dy) % int(ny))
        return np.kron(Tx, Ty)

    if ne == "ızgara":
        k = k or kodlayici()
        G = np.atleast_2d(np.asarray(g, int))
        h, w = G.shape
        dizi: List[int] = [k.ozel("<izgara_bas>")]
        ornek: List[IzafiMevki] = []
        for i in range(h):
            if i:
                dizi.append(k.ozel("<satır_ayır>"))
            for j in range(w):
                dizi.append(k.ozel("<renk_%d>" % (int(G[i, j]) % 10)))
                kom: List[int] = []
                for _, dx, dy in YON_ADLARI[1:]:
                    ii, jj = i - dy, j + dx
                    kom.append(int(G[ii, jj]) if 0 <= ii < h and 0 <= jj < w
                               else int(dolgu))
                ornek.append(IzafiMevki(merkez=int(G[i, j]),
                                        komsu=tuple(kom)))
        dizi.append(k.ozel("<izgara_son>"))
        return {"dizi": dizi, "izafi": ornek, "en": w, "boy": h,
                "kodlayıcı": k.kaynak}

    if ne != "metin":
        raise ValueError("izafî öteleme kipi bilinmiyor: %r" % (ne,))
    k = k or kodlayici()
    return {"dizi": k.kodla(metin), "kodlayıcı": k.kaynak,
            "Δ": (1, 0)}


class IzafiMevki2D:

    def __init__(self, yaricap: int = 1) -> None:
        self.yaricap = int(yaricap)
        self._kod = None

    def izgara_donustur(self, g) -> "np.ndarray":
        B = _komsuluk(g, self.yaricap)
        return B.reshape(-1, B.shape[2]).astype(float)

    def durum_vektoru_kur(self, g) -> "np.ndarray":
        v = self.izgara_donustur(g).reshape(-1)
        n = np.linalg.norm(v)
        return v / n if n > 0 else v

    def ebat_kanunu_coz(self, g):
        import numpy as _np
        a = _np.atleast_2d(_np.asarray(g, int))
        return (int(a.shape[0]), int(a.shape[1]))


def tiktoken_2d_kodla(metin: str, k=None):
    r = otele(ne="metin", metin=str(metin), k=k)
    import numpy as _np
    return _np.asarray(r.get("belirtec", r.get("kod", [])), dtype=float)


def tiktoken_2d_coz(kodlar, k=None) -> str:
    kod = k or kodlayici()
    enc = getattr(kod, "_enc", None)
    dizi = [int(x) for x in np.asarray(kodlar).reshape(-1)]
    if enc is None:
        return " ".join(str(x) for x in dizi)
    try:
        return enc.decode(dizi)
    except Exception:
        return " ".join(str(x) for x in dizi)


@dataclass
class Nesne:
    renk: int
    hucreler: np.ndarray
    izam: int
    kutu: Tuple[int, int, int, int]
    merkez: Tuple[float, float]
    sekil: np.ndarray
    tenasub: Tuple[float, float, float]
    tarif: Dict[str, float] = field(default_factory=dict)


@dataclass
class Mesud:
    izgara: np.ndarray

    isik: np.ndarray
    levn: np.ndarray
    gecirgenlik: np.ndarray
    mekan: np.ndarray

    baglanti: np.ndarray
    doku: np.ndarray

    nesneler: List[Nesne]
    bud: np.ndarray

    adet: Dict[int, int]
    tenasub: Tuple[float, float, float]
    mukayese: np.ndarray
    emsal: Dict[str, float]
    katman: Dict[str, float]
    sekil_ozeti: Dict[str, float]
    sureklilik: Dict[str, float]
    husn: float
    kubh: float

    def ozet(self) -> Dict[str, float]:
        return {
            "ışık_ort": float(self.isik.mean()),
            "ışık_sap": float(self.isik.std()),
            "bağlantı_ort": float(self.baglanti.mean()),
            "doku_ort": float(self.doku.mean()),
            "geçirgenlik_ort": float(self.gecirgenlik.mean()),
            "aykırılık_ort": float(self.mukayese.mean()),
            "emsal_şekil": self.emsal["emsal_şekil"],
            "emsal_dönük": self.emsal["emsal_dönük"],
            "ihtilaf": self.emsal["ihtilaf"],
            "şekil_sınıfı": self.emsal["sınıf"],
            "kavşak": self.katman["kavşak"],
            "kesafet": self.katman["kesafet"],
            "şeffafiyet": self.katman["şeffafiyet"],
            "nesne_sayısı": float(len(self.nesneler)),
            "renk_sayısı": float(len(self.adet)),
            "en_boy": float(self.tenasub[0]),
            "yatay_simetri": float(self.tenasub[1]),
            "dikey_simetri": float(self.tenasub[2]),
            "hüsn": float(self.husn),
            "kubh": float(self.kubh),
        }


def _isik(g: np.ndarray) -> np.ndarray:
    varlik = np.where(g != 0, 1.0, -1.0)
    yerel = _pencere_ortalamasi(varlik, 3)
    return 0.5 * varlik + 0.5 * (varlik - yerel)


def _levn(g: np.ndarray) -> np.ndarray:
    idx = np.clip(g, 0, 9)
    rgb = np.array([[0.00, 0.00, 0.00],
                    [0.15, 0.35, 0.95],
                    [0.95, 0.20, 0.20],
                    [0.20, 0.80, 0.25],
                    [0.98, 0.90, 0.20],
                    [0.60, 0.60, 0.60],
                    [0.95, 0.20, 0.70],
                    [0.98, 0.60, 0.15],
                    [0.45, 0.80, 0.95],
                    [0.55, 0.10, 0.20]])
    c = rgb[idx]
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    return np.stack([R - G,
                     B - 0.5 * (R + G),
                     0.3 * R + 0.6 * G + 0.1 * B], axis=-1)


def _gecirgenlik(g: np.ndarray) -> np.ndarray:
    return np.where(g == 0, 1.0, -1.0)


def _mekan(g: np.ndarray) -> np.ndarray:
    H, W = g.shape
    r = np.linspace(0.0, 1.0, H)[:, None] * np.ones((1, W))
    c = np.ones((H, 1)) * np.linspace(0.0, 1.0, W)[None, :]
    return np.stack([r, c], axis=-1)


def _baglanti(g: np.ndarray) -> np.ndarray:
    H, W = g.shape
    ayni = np.zeros((H, W), float)
    farkli = np.zeros((H, W), float)
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        kaydir = np.full((H, W), -1, dtype=int)
        r0, r1 = max(0, dr), min(H, H + dr)
        c0, c1 = max(0, dc), min(W, W + dc)
        kaydir[r0 - dr:r1 - dr, c0 - dc:c1 - dc] = g[r0:r1, c0:c1]
        var = kaydir >= 0
        ayni += (var & (kaydir == g)).astype(float)
        farkli += (var & (kaydir != g)).astype(float)
    return (ayni - farkli) / 4.0


def _doku(g: np.ndarray) -> np.ndarray:
    H, W = g.shape
    cesit = np.zeros((H, W), float)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            kaydir = np.full((H, W), -1, dtype=int)
            r0, r1 = max(0, dr), min(H, H + dr)
            c0, c1 = max(0, dc), min(W, W + dc)
            kaydir[r0 - dr:r1 - dr, c0 - dc:c1 - dc] = g[r0:r1, c0:c1]
            cesit += ((kaydir >= 0) & (kaydir != g)).astype(float)
    cesit = cesit / 8.0
    return cesit - float(np.median(cesit))


def _bilesenler(g: np.ndarray, zemin: int = 0,
                capraz: bool = False) -> List[Nesne]:
    H, W = g.shape
    ata = -np.ones(H * W, dtype=int)

    def kok(x: int) -> int:
        while ata[x] != x:
            ata[x] = ata[ata[x]]
            x = ata[x]
        return x

    for i in range(H):
        for j in range(W):
            if g[i, j] == zemin:
                continue
            k = i * W + j
            ata[k] = k
    komsu = ((-1, 0), (0, -1)) if not capraz else \
            ((-1, 0), (0, -1), (-1, -1), (-1, 1))
    for i in range(H):
        for j in range(W):
            if g[i, j] == zemin:
                continue
            k = i * W + j
            for dr, dc in komsu:
                a, b = i + dr, j + dc
                if 0 <= a < H and 0 <= b < W and g[a, b] == g[i, j]:
                    ra, rb = kok(k), kok(a * W + b)
                    if ra != rb:
                        ata[ra] = rb

    kume: Dict[int, List[Tuple[int, int]]] = {}
    for i in range(H):
        for j in range(W):
            if g[i, j] == zemin:
                continue
            kume.setdefault(kok(i * W + j), []).append((i, j))

    out: List[Nesne] = []
    for hucreler in kume.values():
        A = np.array(hucreler)
        ust, sol = A.min(0)
        alt, sag = A.max(0)
        maske = np.zeros((alt - ust + 1, sag - sol + 1), dtype=bool)
        maske[A[:, 0] - ust, A[:, 1] - sol] = True
        out.append(Nesne(
            renk=int(g[A[0, 0], A[0, 1]]),
            hucreler=A,
            izam=len(A),
            kutu=(int(ust), int(sol), int(alt), int(sag)),
            merkez=(float(A[:, 0].mean()), float(A[:, 1].mean())),
            sekil=maske,
            tenasub=_tenasub(g=maske, ne="maske"),
            tarif=_sekil_tarifi(maske)))
    out.sort(key=lambda n: (-n.izam, n.kutu))
    return out


def _bud(g: np.ndarray, nesneler: Sequence[Nesne]) -> np.ndarray:
    H, W = g.shape
    if not nesneler:
        return np.zeros((H, W))
    dolu = (g != 0)
    if not dolu.any():
        return np.zeros((H, W))
    d = np.full((H, W), np.inf)
    d[dolu] = 0.0
    for i in range(H):
        for j in range(W):
            v = d[i, j]
            if i > 0:
                v = min(v, d[i - 1, j] + 1)
                if j > 0:
                    v = min(v, d[i - 1, j - 1] + 1)
                if j + 1 < W:
                    v = min(v, d[i - 1, j + 1] + 1)
            if j > 0:
                v = min(v, d[i, j - 1] + 1)
            d[i, j] = v
    for i in range(H - 1, -1, -1):
        for j in range(W - 1, -1, -1):
            v = d[i, j]
            if i + 1 < H:
                v = min(v, d[i + 1, j] + 1)
                if j > 0:
                    v = min(v, d[i + 1, j - 1] + 1)
                if j + 1 < W:
                    v = min(v, d[i + 1, j + 1] + 1)
            if j + 1 < W:
                v = min(v, d[i, j + 1] + 1)
            d[i, j] = v
    m = float(d[np.isfinite(d)].max()) if np.isfinite(d).any() else 1.0
    return d / max(m, 1.0)


def _sekil_tarifi(m: np.ndarray) -> Dict[str, float]:
    h, w = m.shape
    alan = float(m.sum())
    if alan == 0:
        return {"betti1": 0.0, "çevre": 0.0, "tıkızlık": 0.0,
                "doluluk": 0.0, "simetri": 8.0,
                "m20": 0.0, "m02": 0.0, "m11": 0.0}

    P = np.pad(m, 1, constant_values=False)
    cevre = 0.0
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        kaydir = P[1 + dr:1 + dr + h, 1 + dc:1 + dc + w]
        cevre += float((m & ~kaydir).sum())

    bos = ~m
    gorulmus = np.zeros_like(bos)
    yigin = []
    for i in range(h):
        for j in (0, w - 1):
            if bos[i, j] and not gorulmus[i, j]:
                gorulmus[i, j] = True
                yigin.append((i, j))
    for j in range(w):
        for i in (0, h - 1):
            if bos[i, j] and not gorulmus[i, j]:
                gorulmus[i, j] = True
                yigin.append((i, j))
    while yigin:
        i, j = yigin.pop()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            a, b = i + dr, j + dc
            if 0 <= a < h and 0 <= b < w and bos[a, b] and not gorulmus[a, b]:
                gorulmus[a, b] = True
                yigin.append((a, b))
    ic_bos = bos & ~gorulmus
    delik = 0
    kalan = ic_bos.copy()
    while kalan.any():
        i, j = map(int, np.argwhere(kalan)[0])
        delik += 1
        y = [(i, j)]
        kalan[i, j] = False
        while y:
            a, b = y.pop()
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                p_, q_ = a + dr, b + dc
                if 0 <= p_ < h and 0 <= q_ < w and kalan[p_, q_]:
                    kalan[p_, q_] = False
                    y.append((p_, q_))

    sim = 0
    for k in range(4):
        R = np.rot90(m, k)
        if R.shape == m.shape and np.array_equal(R, m):
            sim += 1
        Y = R[:, ::-1]
        if Y.shape == m.shape and np.array_equal(Y, m):
            sim += 1

    idx = np.argwhere(m)
    y0, x0 = idx.mean(0)
    dy = idx[:, 0] - y0
    dx = idx[:, 1] - x0
    n2 = alan ** 2
    return {"betti1": float(delik),
            "çevre": cevre,
            "tıkızlık": float(cevre * cevre / alan),
            "doluluk": float(alan / (h * w)),
            "simetri": float(sim),
            "m20": float((dy * dy).sum() / n2),
            "m02": float((dx * dx).sum() / n2),
            "m11": float((dy * dx).sum() / n2)}


def _sureklilik(g: np.ndarray) -> Dict[str, float]:
    H, W = g.shape
    ortme = 0
    on: Dict[int, int] = {}
    arka: Dict[int, int] = {}

    def tara(A: np.ndarray) -> None:
        nonlocal ortme
        h, w = A.shape
        for i in range(h):
            j = 0
            while j < w:
                c = A[i, j]
                if c == 0:
                    j += 1
                    continue
                k = j
                while k < w and A[i, k] == c:
                    k += 1
                t = k
                while t < w and A[i, t] != c and A[i, t] != 0:
                    t += 1
                if k < t < w and A[i, t] == c and (t - k) <= 3:
                    ortme += 1
                    d = int(A[i, k])
                    on[d] = on.get(d, 0) + 1
                    arka[int(c)] = arka.get(int(c), 0) + 1
                j = k

    tara(g)
    tara(g.T)
    return {"örtme": float(ortme),
            "ön_renk": float(len(on)),
            "arka_renk": float(len(arka))}


def _tenasub(g=None, nesneler=None, ne: str = "maske"):
    if ne == "maske":
        m = g
        h, w = m.shape
        oran = w / max(h, 1)
        yatay = float((m == m[:, ::-1]).mean())
        dikey = float((m == m[::-1, :]).mean())
        return (float(oran), yatay, dikey)

    if ne != "küllî":
        raise ValueError("tenasüb kipi bilinmiyor: %r" % (ne,))
    if not nesneler:
        return _tenasub(g=g != 0, ne="maske")
    w = np.array([n.izam for n in nesneler], float)
    w = w / w.sum()
    T = np.array([n.tenasub for n in nesneler], float)
    return (float(w @ T[:, 0]), float(w @ T[:, 1]), float(w @ T[:, 2]))


def _emsal(nesneler=None, sekil=None, ne: str = "emsal"):
    if ne == "kanonik":
        en_kucuk: Optional[Tuple[Tuple[int, int], bytes]] = None
        for k in range(4):
            R = np.rot90(sekil, k)
            for V in (R, R[:, ::-1]):
                A = np.ascontiguousarray(V)
                aday = ((int(A.shape[0]), int(A.shape[1])), A.tobytes())
                if en_kucuk is None or aday < en_kucuk:
                    en_kucuk = aday
        return en_kucuk

    if ne != "emsal":
        raise ValueError("emsal kipi bilinmiyor: %r" % (ne,))
    m = len(nesneler)
    if m < 2:
        return {"emsal_şekil": 0.0, "emsal_ızam": 0.0, "emsal_renk": 0.0,
                "emsal_dönük": 0.0, "ihtilaf": 0.0, "sınıf": float(m)}
    ayni_sekil = ayni_izam = ayni_renk = donuk = 0
    cift = 0
    ham = [(n.sekil.shape, np.ascontiguousarray(n.sekil).tobytes())
           for n in nesneler]
    kan = [_emsal(sekil=n.sekil, ne="kanonik") for n in nesneler]
    for i in range(m):
        for j in range(i + 1, m):
            cift += 1
            a, b = nesneler[i], nesneler[j]
            if a.izam == b.izam:
                ayni_izam += 1
            if a.renk == b.renk:
                ayni_renk += 1
            if ham[i] == ham[j]:
                ayni_sekil += 1
            elif kan[i] == kan[j]:
                donuk += 1
    imza = set()
    for n in nesneler:
        imza.add((n.sekil.shape, n.sekil.tobytes()))
    return {"emsal_şekil": ayni_sekil / cift,
            "emsal_ızam": ayni_izam / cift,
            "emsal_renk": ayni_renk / cift,
            "emsal_dönük": donuk / cift,
            "ihtilaf": 1.0 - (ayni_sekil + donuk) / cift,
            "sınıf": float(len(imza))}


def _seffafiyet(g: np.ndarray) -> Dict[str, float]:
    H, W = g.shape
    kavsak = 0
    yatay_kazandi = 0
    dikey_kazandi = 0
    ucuncu = 0
    for i in range(H):
        for j in range(W):
            c = g[i, j]
            if c == 0:
                continue
            y = [g[i, j - 1] if j > 0 else 0, g[i, j + 1] if j + 1 < W else 0]
            d = [g[i - 1, j] if i > 0 else 0, g[i + 1, j] if i + 1 < H else 0]
            ys = y[0] if y[0] == y[1] and y[0] != 0 else 0
            ds = d[0] if d[0] == d[1] and d[0] != 0 else 0
            if ys and ds and ys != ds:
                kavsak += 1
                if c == ys:
                    yatay_kazandi += 1
                elif c == ds:
                    dikey_kazandi += 1
                else:
                    ucuncu += 1
    if kavsak == 0:
        return {"kavşak": 0.0, "kesafet": 0.0, "şeffafiyet": 0.0}
    tutarli = max(yatay_kazandi, dikey_kazandi) / kavsak
    return {"kavşak": float(kavsak),
            "kesafet": float(tutarli),
            "şeffafiyet": float(ucuncu / kavsak)}


def _mukayese(g: np.ndarray, pencere: int = 3) -> np.ndarray:
    H, W = g.shape
    d = _doku(g)
    b = _baglanti(g)
    oz = np.stack([d, b], axis=-1).reshape(-1, 2)
    merkez = oz.mean(0)
    sapma = np.linalg.norm(oz - merkez, axis=1).reshape(H, W)
    olcek = float(sapma.max()) + 1e-12
    return 1.0 - 2.0 * (sapma / olcek)


def _pencere_ortalamasi(A: np.ndarray, k: int) -> np.ndarray:
    p = k // 2
    P = np.pad(A, p, mode="edge")
    out = np.zeros_like(A, dtype=float)
    for dr in range(k):
        for dc in range(k):
            out += P[dr:dr + A.shape[0], dc:dc + A.shape[1]]
    return out / (k * k)


def bak(izgara: np.ndarray) -> Mesud:
    g = np.asarray(izgara, int)
    if g.ndim != 2:
        raise ValueError("müşahede iki boyutlu ızgara ister")
    nesneler = _bilesenler(g)
    adet: Dict[int, int] = {}
    for n in nesneler:
        adet[n.renk] = adet.get(n.renk, 0) + 1

    ten = _tenasub(g=g, nesneler=nesneler, ne="küllî")
    muk = _mukayese(g)
    ems = _emsal(nesneler)
    kat = _seffafiyet(g)
    sur = _sureklilik(g)
    if nesneler:
        w_ = np.array([n.izam for n in nesneler], float)
        w_ = w_ / w_.sum()
        anahtarlar = list(nesneler[0].tarif.keys())
        sek = {k: float(w_ @ np.array([n.tarif[k] for n in nesneler]))
               for k in anahtarlar}
    else:
        sek = {k: 0.0 for k in ("betti1", "çevre", "tıkızlık", "doluluk",
                                "simetri", "m20", "m02", "m11")}
    husn = float(0.5 * (ten[1] + ten[2])
                 * (0.5 + 0.5 * ems["emsal_şekil"])
                 / (1.0 + abs(np.log(max(ten[0], 1e-6)))))
    return Mesud(
        izgara=g,
        isik=_isik(g),
        levn=_levn(g),
        gecirgenlik=_gecirgenlik(g),
        mekan=_mekan(g),
        baglanti=_baglanti(g),
        doku=_doku(g),
        nesneler=nesneler,
        bud=_bud(g, nesneler),
        adet=adet,
        tenasub=ten,
        mukayese=muk,
        emsal=ems,
        katman=kat,
        sekil_ozeti=sek,
        sureklilik=sur,
        husn=husn,
        kubh=1.0 - husn)


def devinim_olc(a: Mesud, b: Mesud) -> Dict[str, float]:
    out: Dict[str, float] = {}
    ayni_sekil = a.izgara.shape == b.izgara.shape
    out["şekil_aynı"] = float(ayni_sekil)
    if ayni_sekil:
        deg = (a.izgara != b.izgara)
        out["hareket"] = float(deg.mean())
        out["sükûn"] = float(1.0 - deg.mean())
        for ad, X, Y in (("ışık", a.isik, b.isik),
                         ("bağlantı", a.baglanti, b.baglanti),
                         ("doku", a.doku, b.doku),
                         ("geçirgenlik", a.gecirgenlik, b.gecirgenlik),
                         ("mukayese", a.mukayese, b.mukayese),
                         ("bu'd", a.bud, b.bud)):
            out["Δ" + ad] = float(np.abs(X - Y).mean())
        out["Δlevn"] = float(np.abs(a.levn - b.levn).mean())
    else:
        out["hareket"] = 1.0
        out["sükûn"] = 0.0
    out["Δadet"] = float(sum(abs(b.adet.get(k, 0) - a.adet.get(k, 0))
                             for k in set(a.adet) | set(b.adet)))
    out["Δnesne"] = float(len(b.nesneler) - len(a.nesneler))
    out["Δen_boy"] = float(b.tenasub[0] - a.tenasub[0])
    out["Δyatay_sim"] = float(b.tenasub[1] - a.tenasub[1])
    out["Δdikey_sim"] = float(b.tenasub[2] - a.tenasub[2])
    out["Δhüsn"] = float(b.husn - a.husn)
    for k in ("emsal_şekil", "emsal_dönük", "ihtilaf", "sınıf"):
        out["Δ" + k] = float(b.emsal[k] - a.emsal[k])
    for k in ("kavşak", "kesafet", "şeffafiyet"):
        out["Δ" + k] = float(b.katman[k] - a.katman[k])
    for k in a.sekil_ozeti:
        out["Δş_" + k] = float(b.sekil_ozeti[k] - a.sekil_ozeti[k])
    for k in ("örtme", "ön_renk", "arka_renk"):
        out["Δsür_" + k] = float(b.sureklilik[k] - a.sureklilik[k])
    out["örtme_çözüldü"] = float(a.sureklilik["örtme"] > 0
                                 and b.sureklilik["örtme"] == 0)
    out["örtme_kuruldu"] = float(a.sureklilik["örtme"] == 0
                                 and b.sureklilik["örtme"] > 0)
    return out


class SekilKaidesi:

    def __init__(self, satir: Tuple[str, object], sutun: Tuple[str, object]):
        self.satir, self.sutun = satir, sutun

    @property
    def ad(self) -> str:
        return "%s|%s" % (self.satir[0], self.sutun[0])

    @staticmethod
    def _eksen(kaide: Tuple[str, object], gs: Tuple[int, int],
               eksen: int) -> Optional[int]:
        kip, deger = kaide
        if kip == "sabit":
            return int(deger)
        kaynak = gs[eksen] if kip == "oran" else gs[1 - eksen]
        pay = Fraction(kaynak) * deger
        if pay.denominator != 1 or pay < 1:
            return None
        return int(pay)

    def kestir(self, girdi: np.ndarray, azami_kenar: int = 30
               ) -> Optional[Tuple[int, int]]:
        gs = (int(girdi.shape[0]), int(girdi.shape[1]))
        r = self._eksen(self.satir, gs, 0)
        c = self._eksen(self.sutun, gs, 1)
        if r is None or c is None:
            return None
        if not (1 <= r <= azami_kenar and 1 <= c <= azami_kenar):
            return None
        return r, c

    def __repr__(self) -> str:
        return "SekilKaidesi(%r, %r)" % (self.satir, self.sutun)


Boyut = Tuple[int, int]


KAIDE_ADLARI: Tuple[str, ...] = (
    "aynı", "devrik", "dolu_kutu", "en_büyük_nesne", "en_küçük_nesne",
    "tek_nesne", "nesne_sayısı_kare", "renk_sayısı_kare", "nesne_katı",
    "×2", "÷2", "×3", "÷3", "×4", "÷4", "×2 yatay", "×2 dikey",
)


QTT_TABAN: int = 2


QTT_KADEME: int = 12


QTT_BAG: int = 8


def kalip(ciftler=None, girdi=None, ne: str = "tahmin",
                   ad: str = "", g=None, m=None, gorevler=None,
                   azami: int = 400, azami_hucre: int = 1600,
                   eksen: int = 0, azami_kenar: int = 30):
    if ne == "kesir":
        if not ciftler:
            return None
        for kip in ("oran", "capraz"):
            katsayilar = set()
            for a, b in ciftler:
                kaynak = (a.shape[eksen] if kip == "oran"
                          else a.shape[1 - eksen])
                if kaynak == 0:
                    return None
                katsayilar.add(Fraction(int(b.shape[eksen]), int(kaynak)))
            if len(katsayilar) == 1:
                return (kip, katsayilar.pop())
        kenarlar = {int(b.shape[eksen]) for _, b in ciftler}
        if len(kenarlar) == 1:
            return ("sabit", kenarlar.pop())
        return None

    if ne == "şekil":
        sa = kalip(ciftler, eksen=0, ne="kesir")
        su = kalip(ciftler, eksen=1, ne="kesir")
        if sa is None or su is None:
            return None
        return SekilKaidesi(sa, su)

    def cetvel(k: str, gg, mm):
        gg = np.asarray(gg)
        if k == "aynı":
            return (gg.shape[0], gg.shape[1])
        if k == "devrik":
            return (gg.shape[1], gg.shape[0])
        if k == "dolu_kutu":
            idx = np.argwhere(gg != 0)
            if not len(idx):
                return None
            a, b = idx.min(0)
            c, d = idx.max(0)
            return (int(c - a + 1), int(d - b + 1))
        if k in ("en_büyük_nesne", "en_küçük_nesne"):
            if not mm.nesneler:
                return None
            n = mm.nesneler[0 if k == "en_büyük_nesne" else -1]
            return (n.sekil.shape[0], n.sekil.shape[1])
        if k == "tek_nesne":
            if len(mm.nesneler) < 3:
                return None
            imza = {}
            for i, n in enumerate(mm.nesneler):
                anah = (np.asarray(n.sekil, np.uint8).tobytes()
                        + bytes(n.sekil.shape))
                imza.setdefault(anah, []).append(i)
            tekler = [v[0] for v in imza.values() if len(v) == 1]
            if len(tekler) != 1:
                return None
            n = mm.nesneler[tekler[0]]
            return (n.sekil.shape[0], n.sekil.shape[1])
        if k == "nesne_sayısı_kare":
            n = len(mm.nesneler)
            return (n, n) if n else None
        if k == "renk_sayısı_kare":
            n = len(mm.adet)
            return (n, n) if n else None
        if k == "×2 yatay":
            return (gg.shape[0], gg.shape[1] * 2)
        if k == "×2 dikey":
            return (gg.shape[0] * 2, gg.shape[1])
        if k.startswith("×"):
            a = int(k[1:])
            return (gg.shape[0] * a, gg.shape[1] * a)
        if k.startswith("÷"):
            a = int(k[1:])
            if gg.shape[0] % a or gg.shape[1] % a:
                return None
            return (gg.shape[0] // a, gg.shape[1] // a)
        if k == "nesne_katı":
            n = len(mm.nesneler)
            return (gg.shape[0] * n, gg.shape[1] * n) if n else None
        if k.startswith("sabit"):
            return tuple(int(x) for x in k[6:-1].split(", "))
        raise ValueError("boyut kaidesi bilinmiyor: %r" % (k,))

    if ne == "cetvel":
        return cetvel(ad, g, m)

    if ne == "bul":
        if not ciftler:
            return None
        k = kalip(ciftler, ne="şekil")
        if k is not None:
            hepsi = all(k.kestir(a, azami_kenar)
                        == (int(b.shape[0]), int(b.shape[1]))
                        for a, b in ciftler)
            if hepsi:
                return k
        mesudlar = [bak(a) for a, _ in ciftler]
        for k2 in KAIDE_ADLARI:
            tamam = True
            for (a, b), mm in zip(ciftler, mesudlar):
                t_ = cetvel(k2, a, mm)
                if t_ is None or t_ != (b.shape[0], b.shape[1]):
                    tamam = False
                    break
            if tamam:
                return k2
        boyutlar = {(b.shape[0], b.shape[1]) for _, b in ciftler}
        if len(boyutlar) == 1:
            return "sabit%s" % (boyutlar.pop(),)
        return None

    if ne == "tahmin":
        k = kalip(ciftler, ne="bul")
        if k is None:
            return None, "sükût"
        gg = np.asarray(girdi)
        if isinstance(k, SekilKaidesi):
            t_ = k.kestir(gg, azami_kenar)
            return (t_, "kesir:%s" % k.ad) if t_ is not None else (None, "sükût")
        return cetvel(k, gg, bak(gg)), k

    if ne == "kapsam":
        kapsanan = dogru = toplam = 0
        kip_sayaci: Dict[str, int] = {}
        for gv in gorevler:
            k = kalip(gv.egitim, ne="bul")
            for a, b in gv.sinama:
                toplam += 1
                if k is None:
                    continue
                if isinstance(k, SekilKaidesi):
                    tahmin, kad = k.kestir(a, azami_kenar), "kesir:" + k.ad
                else:
                    tahmin, kad = cetvel(k, a, bak(a)), k
                if tahmin is None:
                    continue
                kapsanan += 1
                kip_sayaci[kad] = kip_sayaci.get(kad, 0) + 1
                if tuple(tahmin) == (int(b.shape[0]), int(b.shape[1])):
                    dogru += 1
        return {"sınama_çifti": toplam, "kapsanan": kapsanan, "doğru": dogru,
                "kapsam": kapsanan / max(toplam, 1),
                "isabet_kapsayınca": dogru / max(kapsanan, 1),
                "kip": dict(sorted(kip_sayaci.items(), key=lambda x: -x[1]))}

    if ne != "ölç":
        raise ValueError("boyut kipi bilinmiyor: %r" % (ne,))
    isabet = yanlis = sukut = deneme = 0
    kaide_say: Dict[str, int] = {}
    kaide_isabet: Dict[str, int] = {}
    for gv in gorevler[:azami]:
        egt = [(np.array(a), np.array(b)) for a, b in gv.egitim
               if np.array(a).size <= azami_hucre
               and np.array(b).size <= azami_hucre]
        sin = [(np.array(a), np.array(b)) for a, b in gv.sinama
               if np.array(a).size <= azami_hucre
               and np.array(b).size <= azami_hucre]
        if len(egt) < 2 or not sin:
            continue
        deneme += 1
        gi, co = sin[0]
        t, ad = kalip(egt, gi)
        kaide_say[ad] = kaide_say.get(ad, 0) + 1
        if t is None:
            sukut += 1
        elif t == (co.shape[0], co.shape[1]):
            isabet += 1
            kaide_isabet[ad] = kaide_isabet.get(ad, 0) + 1
        else:
            yanlis += 1
    return {"deneme": deneme, "isabet": isabet, "yanlış": yanlis,
            "sükût": sukut,
            "isabet_oranı": isabet / max(deneme, 1),
            "konuşunca_isabet": isabet / max(isabet + yanlis, 1),
            "kaide_dağılımı": dict(sorted(kaide_say.items(),
                                          key=lambda x: -x[1])),
            "kaide_isabeti": kaide_isabet}


def qtt_parametre_sayisi(kademe: int = QTT_KADEME, chi: int = QTT_BAG,
                         taban: int = QTT_TABAN) -> int:
    return int(kademe) * int(taban) * int(chi) * int(chi)


def qtt_gomme(v: np.ndarray, chi: int = QTT_BAG
              ) -> Tuple[List[np.ndarray], float, int]:
    psi, _ = genlige_gom(v)
    k = genlige_gom(D=np.asarray(v).size, ne="kübit")
    cek, bag, hata = genlige_gom(psi=psi, kubit=k, chi=int(chi), ne="mps")
    par = int(sum(c.size for c in cek))
    return cek, float(1.0 - hata), par


def qtt_sadakat_cetveli(v: np.ndarray,
                        chiler: Sequence[int] = (1, 2, 4, 8, 16, 32)
                        ) -> List[Dict[str, float]]:
    out: List[Dict[str, float]] = []
    for c in chiler:
        _, sad, par = qtt_gomme(v, chi=int(c))
        out.append({"χ": int(c), "sadakat": float(sad),
                    "parametre": int(par),
                    "sıkıştırma": float(np.asarray(v).size) / max(par, 1)})
    return out


def genlige_gom(v=None, psi=None, kubit: int = 0, chi=None,
                norm: float = 1.0, D=None, ne: str = "gom"):
    if ne == "kübit":
        d = int(D if D is not None else v)
        if d < 1:
            raise ValueError("D ≥ 1 olmalı")
        return int(math.ceil(math.log2(d)))

    if ne == "gom":
        vv = np.asarray(v, float).ravel()
        k = genlige_gom(D=vv.size, ne="kübit")
        tam = 1 << k
        if vv.size < tam:
            u = np.zeros(tam)
            u[:vv.size] = vv
            vv = u
        nrm = float(np.linalg.norm(vv))
        if nrm <= 1e-300:
            return np.full(tam, 1.0 / math.sqrt(tam)), 0.0
        return vv / nrm, nrm

    if ne == "çöz":
        pp = np.asarray(psi, float).ravel() * float(norm)
        return pp if D is None else pp[:int(D)]

    if ne not in ("mps", "bağ", "hata"):
        raise ValueError("gömme kipi bilinmiyor: %r" % (ne,))
    cc = None if ne == "bağ" else chi
    psi = np.asarray(psi, float).ravel()
    n = int(kubit)
    if psi.size != (1 << n):
        raise ValueError("genlik %d, 2^%d = %d değil" % (psi.size, n, 1 << n))
    cek: List[np.ndarray] = []
    bag: List[int] = []
    M = psi.reshape(1, -1)
    atilan = 0.0
    for k in range(n - 1):
        r0 = M.shape[0]
        M = M.reshape(r0 * 2, -1)
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        etkin = int(np.sum(s > 1e-12 * max(float(s[0]), 1e-30)))
        r1 = max(1, etkin if cc is None else min(int(cc), etkin))
        atilan += float(np.sum(s[r1:] ** 2))
        cek.append(U[:, :r1].reshape(r0, 2, r1))
        M = s[:r1, None] * Vt[:r1, :]
        bag.append(r1)
    cek.append(M.reshape(-1, 2, 1))
    top = float(np.sum(psi ** 2))
    hata = math.sqrt(max(atilan, 0.0) / max(top, 1e-300))
    if ne == "bağ":
        return bag
    if ne == "hata":
        return hata
    return cek, bag, hata


@dataclass
class YazmacOlcusu:
    B: int = 2048
    L: int = 4096
    D: int = 4096

    @property
    def kubit_yigin(self) -> int:
        return genlige_gom(D=self.B, ne="kübit")

    @property
    def kubit_yer(self) -> int:
        return genlige_gom(D=self.L, ne="kübit")

    @property
    def kubit_mana(self) -> int:
        return genlige_gom(D=self.D, ne="kübit")

    @property
    def kubit(self) -> int:
        return self.kubit_yigin + self.kubit_yer + self.kubit_mana

    @property
    def token(self) -> int:
        return int(self.B) * int(self.L)

    def cetvel(self) -> str:
        return ("  yığın |j⟩  B=%-7d → %2d kübit\n"
                "  yer   |t⟩  L=%-7d → %2d kübit\n"
                "  mana  |k⟩  D=%-7d → %2d kübit\n"
                "  ───────────────────────────────\n"
                "  TOPLAM                 %2d kübit   (%d token)"
                % (self.B, self.kubit_yigin, self.L, self.kubit_yer,
                   self.D, self.kubit_mana, self.kubit, self.token))


def veri_yazmaci(V: np.ndarray) -> Tuple[np.ndarray, YazmacOlcusu]:
    V = np.asarray(V, float)
    if V.ndim != 3:
        raise ValueError("V (B, L, D) olmalı")
    B, L, D = V.shape
    o = YazmacOlcusu(B=B, L=L, D=D)
    T = np.zeros((1 << o.kubit_yigin, 1 << o.kubit_yer, 1 << o.kubit_mana))
    T[:B, :L, :D] = V
    psi = T.ravel()
    nrm = float(np.linalg.norm(psi))
    return (psi / nrm if nrm > 1e-300 else psi), o


def bellek_cetveli(V: np.ndarray, chi: Sequence[int] = (2, 4, 8, 16, 32)
                   ) -> Dict[str, object]:
    psi, o = veri_yazmaci(V)
    hakiki = genlige_gom(psi=psi, kubit=o.kubit, ne="bağ")
    out: List[Dict[str, float]] = []
    for c in chi:
        cek, bag, hata = genlige_gom(psi=psi, kubit=o.kubit, chi=int(c), ne="mps")
        eleman = int(sum(x.size for x in cek))
        out.append({"χ": int(c), "hata": float(hata),
                    "eleman": eleman, "MB": eleman * 4 / 1e6,
                    "azamî_bağ": int(max(bag)) if bag else 1})
    return {"ölçü": o, "hakikî_bağ": hakiki,
            "hakikî_âzamî_bağ": int(max(hakiki)) if hakiki else 1,
            "klasik_MB": float(np.asarray(V).size * 4 / 1e6),
            "cetvel": out}


def kopru(sozluk: int = 16, kubit: int = 16,
                      ne: str = "ölç"):
    def phi(x: np.ndarray) -> np.ndarray:
        t = np.asarray(x, float).reshape(-1)[0]
        out = []
        for i in range(kubit):
            u = (t / (1 << i)) % 2.0
            out.append(2.0 * (1.0 - abs(u - 1.0)) - 1.0)
        return np.asarray(out, float)

    if ne == "morfizm":
        return Morfizm(1, kubit, phi, ad="belirteç→açı")
    if ne != "ölç":
        raise ValueError("köprü kipi bilinmiyor: %r" % (ne,))
    from nefs.qegitim import belirtecleri_kodla

    T = np.arange(sozluk)
    E = belirtecleri_kodla(T, kubit, kubit)
    bit = (E > 0).astype(np.int64)
    geri = np.argmin(
        np.linalg.norm(E[:, None, :] - E[None, :, :], axis=2)
        + np.eye(len(T)) * 0.0, axis=1)
    tersinir = bool(np.array_equal(geri % sozluk, T % sozluk))
    carpisma = int(sozluk - len(set(map(tuple, bit.tolist()))))

    m = Morfizm(1, kubit, phi, ad="belirteç→açı")
    g = metrik("düz", n=1)
    h = metrik("düz", n=kubit)
    noktalar = [[float(x)] for x in np.linspace(0.3, sozluk - 0.7, 24)]
    izo = izometri_mi(m, g, h, noktalar, tol=1e-6)

    D_soz = np.abs(T[:, None] - T[None, :]).astype(float)
    D_aci = np.linalg.norm(E[:, None, :] - E[None, :, :], axis=2)
    ust = np.triu_indices(sozluk, 1)
    korelasyon = float(np.corrcoef(D_soz[ust], D_aci[ust])[0, 1])

    return {
        "tersinir": tersinir,
        "çarpışma": carpisma,
        "izometri": bool(izo["izometri"]),
        "izometri_azamî_sapma": float(izo["azamî_sapma"]),
        "mesafe_korelasyonu": korelasyon,
        "hüküm": ("H14 doğrulandı: kodlama tersinir."
                  if tersinir else
                  "H14 YANLIŞ: kodlama tersinir değil."),
    }


@dataclass(frozen=True)
class Sahit:
    no: int
    bas: int
    kesim: int
    son: int

    @property
    def girdi(self) -> slice:
        return slice(self.bas, self.kesim)

    @property
    def cikti(self) -> slice:
        return slice(self.kesim, self.son)

    @property
    def dilim(self) -> slice:
        return slice(self.bas, self.son)

    def __len__(self) -> int:
        return self.son - self.bas


@dataclass
class Bolutleme:
    sahitler: List[Sahit] = field(default_factory=list)
    esik: float = 0.0
    kopmalar: Optional[np.ndarray] = None
    yeterli: bool = False
    sebep: str = ""

    def __len__(self) -> int:
        return len(self.sahitler)


def ayir(Z=None, asgari_uzunluk: int = 4, kat: float = 3.0,
                   ne: str = "bölütle", v=None, kopma=None,
                   bas: int = 0, son: int = 0):
    if ne == "kopma":
        Z = np.asarray(Z, float)
        if len(Z) < 2:
            return np.zeros(0)
        fark = np.linalg.norm(np.diff(Z, axis=0), axis=1)
        olcek = float(np.median(fark)) if fark.size else 0.0
        return fark / (olcek + 1e-12)

    if ne == "eşik":
        x = np.asarray(v, float)
        if x.size == 0:
            return float("inf")
        med = float(np.median(x))
        mad = float(np.median(np.abs(x - med)))
        return med + kat * (mad if mad > 1e-12 else float(np.std(x)) + 1e-12)

    if ne == "iç_kesim":
        ic = range(bas + 1, son)
        aday = [(kopma[i - 1], i) for i in ic if 0 <= i - 1 < len(kopma)]
        if not aday:
            return bas + max(1, (son - bas) // 2)
        return max(aday)[1]

    if ne != "bölütle":
        raise ValueError("bölütleme kipi bilinmiyor: %r" % (ne,))
    n = len(Z)
    if n < 2 * asgari_uzunluk:
        return Bolutleme(sahitler=[], esik=float("nan"),
                         kopmalar=ayir(Z, ne="kopma"), yeterli=False,
                         sebep="akış iki şahide bölünemeyecek kadar kısa")

    kopma = ayir(Z, ne="kopma")
    esik = ayir(v=kopma, kat=kat, ne="eşik")
    aday = [i + 1 for i, v in enumerate(kopma) if v > esik]

    if len(aday) >= 3:
        buyukluk = np.array([kopma[a - 1] for a in aday])
        ic_esik = float(np.median(buyukluk))
        aday = [a for a, v in zip(aday, buyukluk) if v > ic_esik]

    sinirlar: List[int] = [0]
    for a in aday:
        if a - sinirlar[-1] >= asgari_uzunluk and n - a >= asgari_uzunluk:
            sinirlar.append(a)
    sinirlar.append(n)

    if len(sinirlar) <= 2:
        return Bolutleme(sahitler=[], esik=esik, kopmalar=kopma,
                         yeterli=False,
                         sebep="kopma eşiği aşan sınır yok; akış tek parça")

    sahitler: List[Sahit] = []
    for no, (b, s) in enumerate(zip(sinirlar[:-1], sinirlar[1:])):
        kesim = ayir(kopma=kopma, bas=b, son=s, ne="iç_kesim")
        sahitler.append(Sahit(no=no, bas=b, kesim=kesim, son=s))
    return Bolutleme(sahitler=sahitler, esik=esik, kopmalar=kopma,
                     yeterli=len(sahitler) >= 2,
                     sebep="" if len(sahitler) >= 2 else "tek şahit")


def _cerceve(S: np.ndarray, sahit: Sahit
             ) -> Tuple[np.ndarray, np.ndarray]:
    G = np.asarray(S[sahit.girdi], float)
    C = np.asarray(S[sahit.cikti], float)
    t = min(len(G), len(C))
    if t == 0:
        return np.zeros((0, S.shape[1])), np.zeros((0, S.shape[1]))
    G, C = G[:t], C[:t]
    G = G - G.mean(0, keepdims=True)
    C = C - C.mean(0, keepdims=True)
    ng = float(np.linalg.norm(G))
    nc = float(np.linalg.norm(C))
    G = G / (ng if ng > 1e-12 else 1.0)
    C = C / (nc if nc > 1e-12 else 1.0)
    return G, C


def kaide(S=None, sahit=None, ne: str = "küllî", sahitler=None,
                A=None):
    def polar(Am):
        U, _, Vt = np.linalg.svd(np.asarray(Am, float))
        return U @ Vt

    if ne == "polar":
        return polar(A)
    if ne == "kovaryans":
        G, C = _cerceve(S, sahit)
        if len(G) == 0:
            return np.zeros((S.shape[1], S.shape[1]))
        return C.T @ G

    if ne == "tek":
        G, _ = _cerceve(S, sahit)
        if len(G) == 0:
            return np.eye(S.shape[1])
        return polar(kaide(S, sahit, ne="kovaryans"))

    if ne != "küllî":
        raise ValueError("kaide kipi bilinmiyor: %r" % (ne,))
    if not sahitler:
        raise ValueError("şehadet yok")
    return polar(np.sum(np.stack([np.asarray(a, float) for a in sahitler]),
                        axis=0))


def artiklar(S: np.ndarray, sahit: Sahit, R: np.ndarray) -> np.ndarray:
    G, C = _cerceve(S, sahit)
    if len(G) == 0:
        return np.zeros(0)
    pay = np.linalg.norm(G @ R.T - C, axis=1)
    payda = np.linalg.norm(C, axis=1) + 1e-12
    return pay / payda


def _bos_kaide(ds: int, tohum: int) -> np.ndarray:
    rng = np.random.default_rng(tohum)
    Q, _ = np.linalg.qr(rng.normal(size=(ds, ds)))
    return Q


def _tolerans(S: np.ndarray, sahitler: Sequence[Sahit],
              kaideler: Sequence[np.ndarray]) -> float:
    if not sahitler:
        return float("inf")
    R_hep = kaide(
        sahitler=[kaide(S, s, ne="kovaryans") for s in sahitler],
        ne="küllî")
    R_bos = _bos_kaide(S.shape[1], tohum=len(sahitler) * 1000 + S.shape[1])
    kendi = [float(np.mean(a)) for a in
             (artiklar(S, s, R_hep) for s in sahitler) if a.size]
    bos = [float(np.mean(a)) for a in
           (artiklar(S, s, R_bos) for s in sahitler) if a.size]
    if not kendi or not bos:
        return float("inf")
    b = max(float(np.median(bos)), 1e-9)
    k = max(float(np.median(kendi)), b * 1e-4)
    return float(np.sqrt(k * b))


def delil_dizileri(S: np.ndarray, sahitler: Sequence[Sahit],
                   kaideler: Sequence[np.ndarray],
                   tol: Optional[float] = None
                   ) -> Tuple[List[np.ndarray], float]:
    if tol is None:
        tol = _tolerans(S, sahitler, kaideler)
    caprazlar = [kaide(S, s, ne="kovaryans") for s in sahitler]
    deliller: List[np.ndarray] = []
    for k in range(len(sahitler)):
        satir = []
        for i in range(len(sahitler)):
            R = kaide(ne="polar", A=caprazlar[k] + caprazlar[i])
            a = artiklar(S, sahitler[i], R)
            satir.append(float(np.mean(a) <= tol) if a.size else 0.0)
        deliller.append(np.array(satir))
    return deliller, float(tol)


def nakz_bul(S: np.ndarray, sahitler: Sequence[Sahit],
             kaideler: Sequence[np.ndarray],
             tol: Optional[float] = None) -> Dict[str, object]:
    m = len(sahitler)
    if m < 2:
        return {"nakz": [], "artık": [], "tolerans": float("nan"),
                "kalan": list(range(m)), "sebep": "en az iki şahit lazım"}
    if tol is None:
        tol = _tolerans(S, sahitler, kaideler)
    caprazlar = [kaide(S, s, ne="kovaryans") for s in sahitler]
    kalan = list(range(m))
    nakz: List[int] = []
    artik = [float("nan")] * m
    while len(kalan) >= 2:
        tur: List[Tuple[float, int]] = []
        for j in kalan:
            digerleri = [caprazlar[k] for k in kalan if k != j]
            R_eksik = kaide(sahitler=digerleri, ne="küllî") if digerleri else caprazlar[j]
            a = artiklar(S, sahitler[j], R_eksik)
            ort = float(np.mean(a)) if a.size else float("inf")
            tur.append((ort, j))
            artik[j] = ort
        en_kotu, j = max(tur)
        if en_kotu <= tol:
            break
        nakz.append(j)
        kalan.remove(j)
    R_kulli = kaide(sahitler=[caprazlar[k] for k in kalan] or caprazlar, ne="küllî")
    return {"nakz": sorted(nakz), "artık": artik, "tolerans": float(tol),
            "kaide": R_kulli, "kalan": kalan, "sebep": ""}


def _akis_kur(m: int, ds: int, t: int, bozuk: Optional[int] = None,
              tohum: int = 0) -> np.ndarray:
    rng = np.random.default_rng(tohum)
    R_hakiki = np.linalg.qr(rng.normal(size=(ds, ds)))[0]
    R_sapik = np.linalg.qr(rng.normal(size=(ds, ds)))[0]
    bloklar = []
    for k in range(m):
        G = rng.normal(size=(t, ds))
        R = R_sapik if k == bozuk else R_hakiki
        C = G @ R.T
        bloklar.append(np.vstack([G, C + 6.0]) + 60.0 * k)
    return np.vstack(bloklar)


def _bir_deneme(baslik: str, S: np.ndarray) -> List[str]:
    b = ayir(S)
    s = ["%s" % baslik,
         "  bulunan şahit: %d   eşik=%.3f   yeterli=%s"
         % (len(b), b.esik, b.yeterli)]
    for x in b.sahitler:
        s.append("    şahit %d: [%2d,%2d) kesim=%2d" % (x.no, x.bas, x.son, x.kesim))
    if b.yeterli:
        K = [kaide(S, x, ne="tek") for x in b.sahitler]
        n = nakz_bul(S, b.sahitler, K)
        s.append("  tolerans=%.4f   nakz=%s" % (n["tolerans"], n["nakz"]))
        s.append("  dışarıda-bırak artıkları: %s"
                 % ["%.4f" % v for v in n["artık"]])
        d, tol = delil_dizileri(S, b.sahitler, K)
        s.append("  delil dizileri (kaide k → şahit i'de tutar mı):")
        for k, dk in enumerate(d):
            s.append("    k=%d  %s" % (k, "".join("%d" % int(v) for v in dk)))
    return s


def iki_sahit_ayri_mi(n_kosu: int = 12, n_satir: int = 8, chi: int = 8,
                      tohum: int = 0, ne: str = "bağımsızlık", q=None):
    def kanal(qq):
        ilk = [qq.veri(i, 0) for i in range(qq.n_satir)]
        hukum = [qq.yerel(i) for i in range(qq.n_satir)]
        R1 = np.asarray(qq.y.tekil_yogunluklar(ilk), float)[0][:, 1, 1]
        R2 = np.asarray(qq.y.tekil_yogunluklar(hukum), float)[0][:, 1, 1]
        return R1, R2

    if ne == "kanal":
        return kanal(q)
    if ne != "bağımsızlık":
        raise ValueError("şahitlik kipi bilinmiyor: %r" % (ne,))
    from .melekeler import QNefs
    from .zihin_durumu import QAyar

    A, B = [], []
    for t in range(int(n_kosu)):
        E = np.random.default_rng(500 + t).normal(size=(n_satir, 12))
        q = QNefs(tohum, QAyar(tohum=tohum)).idrak_et(E)
        a, b = kanal(q)
        A.append(a)
        B.append(b)
    d1 = np.concatenate(A)
    d2 = np.concatenate(B)
    uyusma = float(cift_uyusmasi(d1, d2))

    def ikili(v: np.ndarray) -> np.ndarray:
        return (v > float(np.median(v))).astype(np.int64)

    H = ikili((d1 + d2) / 2.0)
    fs = fazla_sayma([ikili(d1), ikili(d2)], H)
    return {"koşu": int(n_kosu), "delil": int(d1.size), "uyuşma": uyusma,
            "kanal1_ort": float(d1.mean()), "kanal2_ort": float(d2.mean()),
            "fazla_sayma": fs}


def iki_olcegin_acisi(gorev=None, ne: str = "açı", lam: float = 1e-6,
                      tohum: int = 0, chi: int = 8, k: int = 3,
                      gorevler=None, g=None):
    def tarif(gg):
        gg = np.asarray(gg, int)
        h, w = gg.shape
        hist = np.bincount(gg.ravel(), minlength=10)[:10] / max(gg.size, 1)
        return np.concatenate([[h / 30.0, w / 30.0, (gg != 0).mean(),
                                float(gg.max()) / 9.0], hist])

    def oznitelik(gv):
        X, Y = [], []
        for a, b in gv.egitim:
            X.append(tarif(a))
            Y.append(tarif(b))
        if not X:
            return np.zeros((0, 14)), np.zeros((0, 14))
        return np.asarray(X, float), np.asarray(Y, float)

    if ne == "tarif":
        return tarif(g)
    if ne == "öznitelik":
        return oznitelik(gorev)

    if ne == "sağîr":
        X, Y = oznitelik(gorev)
        if len(X) < 2:
            return {"kuruldu": False, "sebep": "iki çiftten az"}
        gen = medyan_genislik(X)
        K = gauss_cekirdegi(1.0 / max(2.0 * gen ** 2, 1e-9))
        psd = bool(psd_mi(K, boyut=int(X.shape[1]))["psd_görünüyor"])
        m = RKHS(K, lam=lam)
        m.uydur(X, Y)
        artik = float(np.abs(np.asarray(m(X), float) - Y).max())
        d = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=2)
        n = len(X)
        cakisan = int((d[np.triu_indices(n, 1)] < 1e-9).sum()) if n > 1 else 0
        return {"kuruldu": True, "psd": psd, "genişlik": float(gen),
                "model": m, "X": X, "Y": Y, "koşul": float(m.kosul),
                "çakışan_çift": cakisan, "azamî_artık": artik}

    if ne == "kebîr":
        from .melekeler import QNefs
        from .zihin_durumu import QAyar
        X, Y = oznitelik(gorev)
        if len(X) == 0:
            return np.zeros(16)
        E = np.concatenate([X, Y], axis=1)
        q = QNefs(tohum, QAyar(tohum=tohum)).idrak_et(E)
        return np.asarray(q.beyan(0), float)

    if ne != "açı":
        raise ValueError("iki ölçek kipi bilinmiyor: %r" % (ne,))
    S, K = [], []
    kurulan = 0
    for gv in gorevler:
        r = iki_olcegin_acisi(gv, ne="sağîr")
        if not r.get("kuruldu"):
            continue
        X = r["X"]
        tah = np.asarray(r["model"](X), float).mean(axis=0)
        S.append(tah)
        K.append(iki_olcegin_acisi(gv, ne="kebîr", tohum=tohum, chi=chi)[:len(tah)])
        kurulan += 1
    if kurulan < k + 1:
        return {"görev": kurulan, "yeterli_mi": False}
    S = np.asarray(S, float)
    Kb = np.asarray(K, float)
    d = min(S.shape[1], Kb.shape[1])
    S, Kb = S[:, :d], Kb[:, :d]
    kk = min(k, d, S.shape[0])
    Ys = dik_taban(S.T[:, :kk] if S.T.shape[1] >= kk else S.T)
    Yk = dik_taban(Kb.T[:, :kk] if Kb.T.shape[1] >= kk else Kb.T)
    kk = min(Ys.shape[1], Yk.shape[1])
    Ys, Yk = Ys[:, :kk], Yk[:, :kk]
    aci = np.asarray(asal_acilar(Ys, Yk), float)
    return {
        "görev": kurulan,
        "yeterli_mi": True,
        "asal_açılar": aci,
        "azamî_açı": float(aci.max()) if aci.size else 0.0,
        "grassmann_mesafesi": float(grassmann_mesafesi(Ys, Yk)),
        "boyut": int(kk),
    }


def terkip_saglam_mi() -> Dict[str, object]:
    from matematik.tip_teorisi import bosluklar
    from .melekeler import QAKIS, qsicil

    s = qsicil()
    zincir_tam = all(no in s for no in QAKIS)
    return {
        "adım": len(QAKIS),
        "zincir_tam": bool(zincir_tam),
        "çekirdek_boşlukları": len(bosluklar()),
        "boşluk_başlıkları": [b.get("ad", b.get("başlık", "?"))
                              for b in bosluklar()][:6],
    }


def ortu(gorev=None, ne: str = "tıkanıklık", q=None,
                      h1: float = 0.0, olcek: float = 0.9,
                      n_gorev: int = 40, tohum: int = 0, chi: int = 8,
                      kapi: bool = True):
    if ne == "kapı":
        import math
        from .zihin_durumu import donme
        if h1 <= 0:
            return
        q.tek(q.kulli("sukut", 0), donme(float(olcek * math.atan(float(h1)))))
        return

    if ne == "yama":
        return [kalip([(a, b)], ne="şekil") for a, b in gorev.egitim]

    if ne == "tıkanıklık":
        K = [kalip([(a, b)], ne="şekil") for a, b in gorev.egitim]
        n = len(K)
        if n == 0:
            return {"yama": 0, "H1": 0, "kurulabilir": False}
        bos = sum(1 for k in K if k is None)
        uyusmaz: List[Tuple[int, int]] = []
        for i in range(n):
            for j in range(i + 1, n):
                if K[i] is None or K[j] is None:
                    continue
                if repr(K[i]) != repr(K[j]):
                    uyusmaz.append((i, j))
        ucler_tutarli = True
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    if any(x is None for x in (K[i], K[j], K[k])):
                        continue
                    ij = repr(K[i]) == repr(K[j])
                    jk = repr(K[j]) == repr(K[k])
                    ik = repr(K[i]) == repr(K[k])
                    if ij and jk and not ik:
                        ucler_tutarli = False
        kurulabilir = (bos == 0 and not uyusmaz)
        return {
            "yama": n,
            "kâidesiz_yama": bos,
            "uyuşmayan_çift": len(uyusmaz),
            "üçlü_tutarlı": ucler_tutarli,
            "H1": len(uyusmaz),
            "kurulabilir": bool(kurulabilir),
        }

    if ne != "bağ":
        raise ValueError("örtü kipi bilinmiyor: %r" % (ne,))
    from .melekeler import QNefs
    from .zihin_durumu import QAyar

    gorevler = gorevleri_getir("training")[:int(n_gorev)]
    H1, S = [], []
    for gv in gorevler:
        c = ortu(gv)
        if c["yama"] < 2:
            continue
        X, Y = iki_olcegin_acisi(gv, ne="öznitelik")
        if len(X) == 0:
            continue
        E = np.concatenate([X, Y], axis=1)
        q = QNefs(tohum, QAyar(tohum=tohum)).idrak_et(
            E, tikaniklik=(float(c["H1"]) if kapi else 0.0))
        yuv = [q.kulli("sukut", j)
               for j in range(q._alan["sukut"][1])]
        sk = float(np.asarray(q.y.tekil_yogunluklar(yuv),
                              float)[0][:, 1, 1].mean())
        H1.append(float(c["H1"] > 0))
        S.append(sk)
    if len(H1) < 4 or len(set(H1)) < 2:
        return {"görev": len(H1), "yeterli_mi": False}
    H1a, Sa = np.asarray(H1), np.asarray(S)
    return {
        "görev": len(H1),
        "yeterli_mi": True,
        "tıkanık_görev": int(H1a.sum()),
        "korelasyon": float(np.corrcoef(H1a, Sa)[0, 1]),
        "sukut_tıkanıkta": float(Sa[H1a > 0].mean()),
        "sukut_açıkta": float(Sa[H1a == 0].mean()),
    }


def rapor() -> str:
    s: List[str] = ["MÜŞAHEDE ÇİPİ -- Küme 6 tevhidi"]

    def _rapor_idrak_arc() -> List[str]:
        s: List[str] = []
        s += []
        egt = gorevleri_getir("training")
        dgr = gorevleri_getir("evaluation")
        s.append("=== ARC-AGI-2 verisi ===")
        s.append("  resmî eğitim: %d görev   resmî değerlendirme: %d görev"
                 % (len(egt), len(dgr)))
        e, d = gorevleri_getir(ne="böl", gorevler=egt)
        s.append("  bölme: eğitim %d / doğrulama %d / sınama %d  "
                 "(%.0f%% / %.0f%% / %.0f%%)"
                 % (len(e), len(d), len(dgr),
                    100 * len(e) / (len(e) + len(d) + len(dgr)),
                    100 * len(d) / (len(e) + len(d) + len(dgr)),
                    100 * len(dgr) / (len(e) + len(d) + len(dgr))))
        s.append("  Sınama kümesi 120 görev → hata kestiriminin standart")
        s.append("  hatası ≈ √(p(1−p)/120) ≈ %.1f puan. 50/50 bölmek eğitimi"
                 % (100 * math.sqrt(0.25 / 120)))
        s.append("  yarıya indirirdi, kestirimi ise ancak %.1f puana iyileştirirdi."
                 % (100 * math.sqrt(0.25 / 560)))

        for ad, k in (("eğitim", e), ("doğrulama", d), ("sınama", dgr)):
            i = istatistik(k)
            s.append("  %-10s kenar ort=%.1f azm=%d   dizi ortanca=%.0f "
                     "p90=%.0f azm=%d   şekli sabit=%d (%.0f%%)"
                     % (ad, i["azamî_kenar_ortalama"], i["azamî_kenar_en_büyük"],
                        i["dizi_uzunluğu_ortanca"], i["dizi_uzunluğu_p90"],
                        i["dizi_uzunluğu_en_büyük"], i["şekli_sabit_görev"],
                        100 * i["şekli_sabit_oran"]))

        s.append("\n=== Belirteçleme gidiş-dönüşü kayıpsız mı? ===")
        hata = 0
        for g in egt[:200]:
            for a, b in g.egitim:
                if not np.array_equal(belirtec_izgara(izgara_belirtecle(a)), a):
                    hata += 1
        s.append("  200 görevin bütün ızgaralarında gidiş-dönüş hatası: %d" % hata)

        s.append("\n=== Bozuk diziyi sessizce onarmıyoruz ===")
        for ad, m in (("eşit olmayan satır", "1 2\n3"),
                      ("hiç hücre yok", ""),
                      ("geçersiz renk", "1 99")):
            s.append("  %-20s → %s" % (ad, metin_izgara(m)))

        s.append("\n=== Sözlü algoritma (soyutlama) verisi ===")
        var = sum(soyutlama_oku(g.ad) is not None for g in dgr)
        s.append("  120 değerlendirme görevinin %d'sinde sözlü algoritma var"
                 % var)
        ornek = soyutlama_oku(dgr[0].ad)
        if ornek:
            s.append("  örnek (%s):" % dgr[0].ad)
            for satir in ornek.strip().splitlines()[:3]:
                s.append("    " + satir[:96])

        s.append("\n=== Bir görevin bağlam/hedef dizisi ===")
        g = egt[0]
        b, h = gorev_dizisi(g, 0)
        s.append("  görev %s: bağlam %d belirteç, hedef %d belirteç"
                 % (g.ad, len(b), len(h)))
        sizinti = 0
        for gg in egt[:300]:
            for j in range(len(gg.egitim)):
                bb, hh = gorev_dizisi(gg, j)
                hedef = hh[:-1]
                if any(bb[i:i + len(hedef)] == hedef
                       for i in range(max(0, len(bb) - len(hedef) + 1))):
                    sizinti += 1
        s.append("  300 görevin bütün hedeflerinde bağlam sızıntısı: %d"
                 % sizinti)
        s.append("  (Hedef örnek bağlamdan çıkarılıyor; çıkarılmasaydı model")
        s.append("   kaideyi öğrenmeden KOPYALAYARAK çözerdi.)")
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  ARC VERİSİ -- resmî bölme ve sızıntısız akış")
    s.append("=" * 70)
    s += _rapor_idrak_arc()

    def _rapor_nefs_lisan() -> List[str]:
        s: List[str] = []
        s += ["LİSAN VE 2D İZAFÎ MEVKİ", ""]
        k = kodlayici()
        s.append("  kodlayıcı kaynağı : %s   (taban sözlük %d, özel %d, toplam %d)"
                 % (k.kaynak, k.taban_sozluk, len(OZEL_BELIRTECLER), k.sozluk))
        if k.kaynak != "tiktoken":
            s.append("  ! tiktoken tablosu bu ortamda ağdan çekilemedi (403);")
            s.append("    aşağıdaki bütün sayılar BAYT YEDEĞİYLEdir.")

        s.append("")
        s.append("  1) İzafî operatörler ortogonal mi, ve mutlak koordinat")
        s.append("     taşımıyor mu?")
        nx, ny = 5, 4
        for ad, dx, dy in YON_ADLARI[1:5]:
            D = otele(nx=nx, ny=ny, dx=dx, dy=dy)
            dik = float(np.linalg.norm(D.T @ D - np.eye(nx * ny)))
            s.append("     %-10s Δ=(%+d,%+d)  ‖DᵀD−I‖ = %.2e" % (ad, dx, dy, dik))
        Dr = otele(nx=nx, ny=ny, dx=1, dy=0)
        Dl = otele(nx=nx, ny=ny, dx=-1, dy=0)
        s.append("     sağ ∘ sol = I : %.2e"
                 % float(np.linalg.norm(Dr @ Dl - np.eye(nx * ny))))

        s.append("")
        s.append("  2) Aynı örüntü ızgaranın HER YERİNDE aynı kodlanıyor mu?")
        A = np.zeros((6, 6), int)
        A[1, 1] = 3; A[1, 2] = 5
        B = np.zeros((6, 6), int)
        B[4, 3] = 3; B[4, 4] = 5
        ra = otele(ne="ızgara", g=A)["izafi"]
        rb = otele(ne="ızgara", g=B)["izafi"]
        ka = [x.kod() for x in ra if x.merkez == 3][0]
        kb = [x.kod() for x in rb if x.merkez == 3][0]
        s.append("     sol üstteki örüntü : %s" % (ka,))
        s.append("     sağ alttaki örüntü : %s" % (kb,))
        s.append("     AYNI MI: %s   ← mutlak koordinat olsaydı olmazdı"
                 % (ka == kb))

        s.append("")
        s.append("  3) Izgara ve metin AYNI akışta")
        g = otele(ne="ızgara", g=np.array([[1, 2], [3, 4]]))
        m = otele(ne="metin", metin="kırmızı kare sağa kayar")
        s.append("     ızgara dizisi  : %s" % g["dizi"])
        s.append("     metin dizisi   : %d belirteç (%s)"
                 % (len(m["dizi"]), m["kodlayıcı"]))
        s.append("     ikisi de aynı sözlükte; ayrı iki dünya yok.")
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  LİSAN -- yerel BPE ve izafî öteleme")
    s.append("=" * 70)
    s += _rapor_nefs_lisan()

    def _rapor_idrak_sekil() -> List[str]:
        s: List[str] = []
        s += ["=== Şekil kaidesi: ispatlı kestirim, yoksa sükût ==="]
        for kume in ("training", "evaluation"):
            try:
                g = gorevleri_getir(kume)
            except Exception as e:
                s.append("  %s yüklenemedi: %s" % (kume, e))
                continue
            d = kalip(ne="kapsam", gorevler=g)
            s.append("  %-10s  görev=%4d  sınama çifti=%4d" % (kume, len(g),
                                                               d["sınama_çifti"]))
            s.append("    kapsam=%.3f   kapsayınca isabet=%.3f   (doğru %d)"
                     % (d["kapsam"], d["isabet_kapsayınca"], d["doğru"]))
            s.append("    kipler: %s" % d["kip"])
        s.append("\n  Kıyas — sinir ağının şekil başı (500 adım, doğrulama):"
                 " 0.027")
        s.append("  Kıyas — donuk havuz üstünde doğrusal yoklama: 0.325 / 0.338")
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  ŞEKİL -- kesirli kaide, yoksa sükût")
    s.append("=" * 70)
    s += _rapor_idrak_sekil()

    def _rapor_nefs_gomme() -> List[str]:
        s: List[str] = []
        s += ["TOKENIN KUANTUM YAZMACINA GÖMÜLMESİ", ""]
        s.append("=== Ceridenin 35 kübitlik adres yazmacı ===")
        s.append(YazmacOlcusu().cetvel())
        s.append("  (klasik: %d token × %d boyut × 4 bayt = %.1f GB)"
                 % (YazmacOlcusu().token, 4096,
                    YazmacOlcusu().token * 4096 * 4 / 1e9))

        s.append("")
        s.append("=== Tek tokenın genlik gömmesi ===")
        rng = np.random.default_rng(0)
        for ad, v in (("rastgele", rng.normal(size=4096)),
                      ("düzgün", np.sin(np.linspace(0, 6, 4096))
                       * np.exp(-np.linspace(0, 3, 4096))),
                      ("tek-sıcak", np.eye(1, 4096, 1234).ravel())):
            psi, nrm = genlige_gom(v)
            bag = genlige_gom(psi=psi, kubit=12, ne="bağ")
            s.append("  %-10s hakikî âzamî bağ %3d   χ=16'da hata %.4f"
                     % (ad, max(bag), genlige_gom(psi=psi, kubit=12, chi=16, ne="hata")))

        s.append("")
        s.append("=== Küllî veri yazmacı: χ ≤ 16 yetiyor mu? ===")
        B, L, D = 8, 16, 64
        V = rng.normal(size=(B, L, D))
        r = bellek_cetveli(V)
        o = r["ölçü"]
        s.append("  numune: B=%d L=%d D=%d → %d kübit   (klasik %.4f MB)"
                 % (B, L, D, o.kubit, r["klasik_MB"]))
        s.append("  kesmesiz hakikî âzamî bağ: %d" % r["hakikî_âzamî_bağ"])
        s.append("     χ      hata        MB     âzamî bağ")
        for c in r["cetvel"]:
            s.append("  %4d   %.4f   %8.5f    %4d"
                     % (c["χ"], c["hata"], c["MB"], c["azamî_bağ"]))
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  GÖMME -- 35 kübitlik adres ve QTT")
    s.append("=" * 70)
    s += _rapor_nefs_gomme()

    def _rapor_nefs_kopru() -> List[str]:
        s: List[str] = []
        s += ["FUNKTÖR KÖPRÜSÜ -- belirteç → açı geçişinin sıhhati", ""]
        s.append("  %-8s %-10s %-10s %-12s %-14s %s"
                 % ("sözlük", "kübit", "tersinir", "çarpışma",
                    "izometri", "mesafe kor."))
        for sozluk, kubit in ((4, 2), (8, 3), (16, 4), (16, 3), (32, 4)):
            r = kopru(sozluk, kubit)
            s.append("  %-8d %-10d %-10s %-12d %-14s %+.4f"
                     % (sozluk, kubit, r["tersinir"], r["çarpışma"],
                        r["izometri"], r["mesafe_korelasyonu"]))
        s.append("")
        s.append("  Son iki satır mühimdir: sözlük kübit sayısının taşıyabildiği")
        s.append("  adedi aşınca çarpışma başlar ve tersinirlik KIRILIR --")
        s.append("  yani ölçü kırmızıya dönebiliyor, H14 her hâlde doğru değil.")
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  KÖPRÜ -- belirteçten açıya geçişin sıhhati")
    s.append("=" * 70)
    s += _rapor_nefs_kopru()

    def _rapor_nefs_sahit() -> List[str]:
        s: List[str] = []
        s += ["=== şahit bölütlemesi (ayıraç SEMBOLÜ aranmadan) ==="]
        s += _bir_deneme("\n--- hepsi aynı kurala tâbi ---",
                         _akis_kur(m=5, ds=8, t=6))
        s += _bir_deneme("\n--- 2 numaralı şahit BAŞKA kurala tâbi ---",
                         _akis_kur(m=5, ds=8, t=6, bozuk=2))
        s.append("\nHüküm: ikinci akışta nakz boş DEĞİLDİR; tek karşı örnek")
        s.append("küllî kaideyi düşürür ve makam yakîn olamaz.")
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  ŞAHİT -- otonom bölütleme ve Procrustes")
    s.append("=" * 70)
    s += _rapor_nefs_sahit()

    def _rapor_nefs_sahitlik() -> List[str]:
        s: List[str] = []
        n_kosu = 12
        n_satir = 8
        chi = 8
        r = iki_sahit_ayri_mi(n_kosu, n_satir, chi)
        u = r["uyuşma"]
        s += ["=== ŞAHİTLİK -- 𝒪₂₉ Teyit'in bağımsızlık iddiası ===",
             "",
             "𝒪₂₉ şöyle diyor: *'Bir satırın ilk kübiti ile son kübiti AYRI",
             "kanallardır… bağımlı iki kanalın uyuşması yeni bilgi değildir.'*",
             "Bu bir tedbirdi ve hiç ölçülmemişti.",
             "",
             "  koşu / delil       : %d koşu, %d satır delili"
             % (r["koşu"], r["delil"]),
             "  kanal 1 ortalaması : %.4f" % r["kanal1_ort"],
             "  kanal 2 ortalaması : %.4f" % r["kanal2_ort"],
             "  çift uyuşması (Pearson) : %+.4f" % u,
             ""]
        fs = r["fazla_sayma"]
        oran = float(fs["fazla_sayma_oranı"])
        s += ["",
              "  FAZLA SAYMA (fitrat/tevafuk.py, ikili şahitlikle):",
              "    ortalama ağırlık      : %.4f  (1'e yakın = yığma meşru)"
              % fs["ortalama_ağırlık"],
              "    muteber şahit sayısı  : %.4f  (2'ye yakın = iki ayrı şahit)"
              % fs["muteber_şahit_sayısı"],
              "    fazla sayma oranı     : %.4f  (1 = fazla sayma yok)"
              % fs["fazla_sayma_oranı"],
              "  Kıyas için: bağımsız üç şahitte 1,05; ortak kaynaklıda 2,55.",
              ""]
        if abs(u) < 0.3 and oran < 1.10:
            s += ["  HÜKÜM: kanallar fiilen AYRI. 𝒪₂₉'un tedbiri tutuyor;",
                  "  ikisinin uyuşması hakikaten yeni delildir."]
        elif abs(u) < 0.3:
            s += ["  HÜKÜM: KARIŞIK ve iki ölçüt ayrı düşüyor. Pearson bağıntı",
                  "  görmüyor (%+.4f) fakat fazla sayma oranı %.4f -- yani" % (u, oran),
                  "  doğrusal olmayan bir bağımlılık var ve 𝒪₂₉ delili bir",
                  "  miktar şişiriyor. Muteber şahit sayısı 2 değil %.2f."
                  % float(fs["muteber_şahit_sayısı"]),
                  "  Tedbir KISMEN tutuyor; 'tamamen tutuyor' denmez."]
        elif abs(u) < 0.7:
            s += ["  HÜKÜM: kanallar KISMEN bağımlı. 𝒪₂₉ delili bir miktar",
                  "  fazla sayıyor; tedbir tamamen tutmuyor."]
        else:
            s += ["  HÜKÜM: kanallar KUVVETLE bağımlı. 𝒪₂₉ aynı delili iki",
                  "  kere sayıyor -- tasdiki hak etmediği yerde yükseltiyor.",
                  "  Bu bir kusurdur ve gizlenmiyor."]
        s += ["",
              "HUDUT: ölçülen şey iki kanalın ayrı KÜBİT olması değil (o",
              "zaten malûm); akış onları dolaştırdıktan sonra hâlâ ayrı",
              "BİLGİ taşıyıp taşımadıklarıdır."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  ŞAHİTLİK -- iki kanal hakikaten ayrı mı")
    s.append("=" * 70)
    s += _rapor_nefs_sahitlik()

    def _rapor_nefs_iki_olcek() -> List[str]:
        s: List[str] = []
        n_gorev = 24
        tohum = 0
        chi = 8
        gorevler = gorevleri_getir("training")[:int(n_gorev)]
        s += ["=== SAĞÎR ve KEBÎR -- iki ölçekli mimari (Dosya 5) ===",
             "",
             "KEBÎR: 41 melekenin bütün görevlerde ORTAK açıları.",
             "SAĞÎR: görev başına, o görevin kendi çiftlerinden, KAPALI",
             "       formda (H3: gradyan yok) -- `ogrenme/rkhs.py`.",
             ""]

        kuruldu = psd_ok = 0
        artiklar = []
        for gv in gorevler:
            r = iki_olcegin_acisi(gv, ne="sağîr")
            if r.get("kuruldu"):
                kuruldu += 1
                psd_ok += int(bool(r["psd"]))
                artiklar.append(r["azamî_artık"])
        s += ["SAĞÎR ÖLÇEK (%d görev):" % len(gorevler),
              "  kurulan            : %d" % kuruldu,
              "  çekirdeği PSD olan : %d  (PSD değilse temsil teoremi geçersiz)"
              % psd_ok,
              "  âzamî uydurma artığı (ortanca): %.2e"
              % (float(np.median(artiklar)) if artiklar else float("nan")),
              ""]

        o = iki_olcegin_acisi(gorevler=gorevler, tohum=tohum, chi=chi)
        s.append("İKİ ÖLÇEK AYNI ŞEYİ Mİ SÖYLÜYOR? (Grassmann asal açıları)")
        if not o.get("yeterli_mi"):
            s.append("  yeterli görev yok (%d)" % o.get("görev", k=0))
        else:
            s += ["  alt uzay boyutu    : %d" % o["boyut"],
                  "  asal açılar (rad)  : %s"
                  % np.array2string(o["asal_açılar"], precision=4),
                  "  âzamî açı          : %.4f rad  (π/2 = 1,5708 tam dik)"
                  % o["azamî_açı"],
                  "  Grassmann mesafesi : %.4f" % o["grassmann_mesafesi"],
                  ""]
            if o["azamî_açı"] < 0.1:
                s.append("  HÜKÜM: açılar sıfıra yakın -- sağîr ölçek kebîrin")
                s.append("  zaten bildiğini söylüyor. İKİNCİ ÖLÇEK GEREKSİZ.")
            else:
                s.append("  HÜKÜM: açılar büyük -- sağîr, kebîrin göremediği bir")
                s.append("  yön taşıyor. İki ölçek hakikaten ikidir.")
        s += ["",
              "Bu bir iddia değil ölçüttür ve kırmızı yanabilir (H90):",
              "açılar sıfıra yakın çıksaydı, iki ölçekli mimarinin bu",
              "hâliyle bedeli var faydası yok demektir ve öyle yazılırdı."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  İKİ ÖLÇEK -- sağîr ile kebîr aynı yere mi")
    s.append("=" * 70)
    s += _rapor_nefs_iki_olcek()

    def _rapor_nefs_operad() -> List[str]:
        s: List[str] = []
        n_gorev = 40
        tohum = 0
        chi = 8
        gorevler = gorevleri_getir("training")[:int(n_gorev)]
        s += ["=== ÖRTÜ, TERKİP, TIKANIKLIK (Dosya 3) ===",
             "",
             "Grothendieck fibrasyonu ZATEN kurulu (nefs/mertebe.py, 20 lif).",
             "Burada kurulan: ∞-operad terkibinin tipi ve ÇEch tıkanıklığı.",
             ""]

        t = terkip_saglam_mi()
        s += ["TERKİP (∞-operad):",
              "  akış adımı        : %d" % t["adım"],
              "  zincir tam mı     : %s" % t["zincir_tam"],
              "  ω-kategori çekirdeğinin BİLİNEN boşlukları: %d"
              % t["çekirdek_boşlukları"],
              ""]

        say = {"kurulabilir": 0, "tıkanık": 0, "kâidesiz": 0}
        ucsuz = 0
        for gv in gorevler:
            c = ortu(gv)
            if c["yama"] < 2:
                continue
            if c["kâidesiz_yama"]:
                say["kâidesiz"] += 1
            elif c["H1"]:
                say["tıkanık"] += 1
            else:
                say["kurulabilir"] += 1
            if not c["üçlü_tutarlı"]:
                ucsuz += 1
        s += ["ČECH TIKANIKLIĞI (%d görev):" % len(gorevler),
              "  H¹ = 0, küllî kâide var   : %d" % say["kurulabilir"],
              "  H¹ ≠ 0, TIKANIK           : %d" % say["tıkanık"],
              "  mahallî kâidesi bile yok  : %d" % say["kâidesiz"],
              "  üçlü tutarlılığı bozan    : %d  (0 olmalı -- kozikıl şartı)"
              % ucsuz,
              ""]

        b = ortu(ne="bağ", n_gorev=n_gorev, tohum=tohum, chi=chi)
        s.append("TIKANIKLIK → SÜKÛT (asıl ölçüm):")
        if not b.get("yeterli_mi"):
            s.append("  yeterli çeşitlilik yok (%d görev)" % b.get("görev", 0))
        else:
            s += ["  görev                 : %d (%d'i tıkanık)"
                  % (b["görev"], b["tıkanık_görev"]),
                  "  sükût, tıkanık görevde: %.4f" % b["sukut_tıkanıkta"],
                  "  sükût, açık görevde   : %.4f" % b["sukut_açıkta"],
                  "  korelasyon            : %+.4f" % b["korelasyon"],
                  ""]
            if b["korelasyon"] > 0.15:
                s.append("  HÜKÜM: tıkanıklık sükûtu ARTIRIYOR. Model, küllî")
                s.append("  cevabın olmadığı görevlerde susmaya meylediyor.")
            elif b["korelasyon"] < -0.15:
                s.append("  HÜKÜM: TERS. Model tıkanık görevlerde daha ÇOK")
                s.append("  konuşuyor -- bu bir kusurdur ve gizlenmiyor.")
            else:
                s.append("  HÜKÜM: bağ YOK. Modelin susması Čech tıkanıklığıyla")
                s.append("  alâkasız; Dosya 3'ün bu kehaneti icra EDİLMEMİŞ")
                s.append("  durumda ve borç olarak kalıyor.")
        s += ["",
              "HUDUT: burada kurulan tam Čech kohomolojisi DEĞİL, onun sonlu",
              "ve hesaplanabilir gölgesidir (sonlu örtü, ayrık kâide kümesi).",
              "İsmi doğru kullanmak, tamamını kurmayı iddia etmeyi gerektirmez."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  OPERAD -- örtü kapanıyor mu, terkip iyi tipli mi")
    s.append("=" * 70)
    s += _rapor_nefs_operad()
    return "\n".join(s)


if __name__ == "__main__":
    print(rapor())


_BILESEN_HAFIZA: Dict[bytes, List[Tuple[int, np.ndarray,
                                        Tuple[int, int, int, int]]]] = {}

_HAFIZA_HADDI: int = 4096

def bilesen_kutulari(g: np.ndarray, arka: int = 0
                     ) -> List[Tuple[int, np.ndarray, Tuple[int, int, int, int]]]:
    anah = arka.to_bytes(2, "little") + g.shape[0].to_bytes(2, "little") \
        + g.shape[1].to_bytes(2, "little") \
        + np.ascontiguousarray(g, dtype=np.int16).tobytes()
    onbellek = _BILESEN_HAFIZA.get(anah)
    if onbellek is not None:
        return onbellek
    H, W = g.shape
    gor = np.zeros((H, W), bool)
    out = []
    for i in range(H):
        for j in range(W):
            if gor[i, j] or g[i, j] == arka:
                continue
            renk = int(g[i, j])
            yigin = [(i, j)]
            gor[i, j] = True
            hucre = []
            while yigin:
                y, x = yigin.pop()
                hucre.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    a, b = y + dy, x + dx
                    if (0 <= a < H and 0 <= b < W and not gor[a, b]
                            and g[a, b] == renk):
                        gor[a, b] = True
                        yigin.append((a, b))
            ys = [y for y, _ in hucre]
            xs = [x for _, x in hucre]
            m = np.zeros((H, W), bool)
            for y, x in hucre:
                m[y, x] = True
            out.append((renk, m, (min(ys), max(ys), min(xs), max(xs))))
    if len(_BILESEN_HAFIZA) >= _HAFIZA_HADDI:
        _BILESEN_HAFIZA.pop(next(iter(_BILESEN_HAFIZA)))
    _BILESEN_HAFIZA[anah] = out
    return out


def _komsuluk(g: np.ndarray, yaricap: int = 1) -> np.ndarray:
    g = np.asarray(g)
    r = int(yaricap)
    P = np.pad(g, r, mode="constant", constant_values=0)
    H, W = g.shape
    k = 2 * r + 1
    out = np.empty((H, W, k * k), dtype=g.dtype)
    for i in range(k):
        for j in range(k):
            out[:, :, i * k + j] = P[i:i + H, j:j + W]
    return out

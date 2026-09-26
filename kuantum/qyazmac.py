from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import math

import numpy as np

from nefs.matchgate import matchgate_mi

__all__ = ["QuditAyar", "QuditYazmac", "Iz", "KULLI_SEKTOR_TABANI",
           "sektor_beyani", "sektor_metni", "senet_beyani"]

KULLI_SEKTOR_TABANI: int = 64

_SEKTOR_SAYAC: Dict[str, float] = {
    "dönme": 0.0, "faz_vuruşu": 0.0, "kenet": 0.0, "örüntü": 0.0,
    "küllî_faz_yazması": 0.0, "kapı_dizeyi": 0.0,
    "küllî_iç_çarpım": 0.0, "açık": 1.0}


def sektor_beyani() -> Dict[str, float]:
    return dict(_SEKTOR_SAYAC)


def sektor_metni(b=None) -> str:
    d = dict(b or sektor_beyani())
    top = (d["dönme"] + d["faz_vuruşu"] + d["kenet"] + d["örüntü"])
    if not top:
        return ("  SEKTÖR AMELİYELERİ: HİÇ KOŞMADI -- kırmızı "
                "(ferman 2-Ö)")
    return "\n".join([
        "  SEKTÖR AMELİYELERİ -- YUVA YOK, CARTAN KÖKÜ VAR (ferman 2-Ö)",
        "    Meleke tamsayı yuva aramaz; sektörün zâtî Cartan",
        "    jeneratörüne kilitlenir. Düşen kapı riyazî olarak",
        "    imkânsızdır: arada bekçi yoktur.",
        "    dönme %d   faz vuruşu %d   kenet %d   örüntü %d"
        % (int(d["dönme"]), int(d["faz_vuruşu"]), int(d["kenet"]),
           int(d["örüntü"])),
        "    BEDEL SAYILIR (ferman 5): küllî faz yazması %d ·"
        " küllî iç çarpım %d · sektör kapı dizeyi %d"
        % (int(d["küllî_faz_yazması"]), int(d.get("küllî_iç_çarpım", 0)),
           int(d["kapı_dizeyi"])),
        "    İkisi de yazmacın TAMAMINI tarar. Kenet defterinde altı",
        "    kenet aynı hâli okur ve defter uygulanmadığı için norm",
        "    değişmez: ağırlık BİR KEZ ölçülüp altısına verilir, yâni",
        "    iç çarpım kenet başına değil DEFTER başınadır (ferman 3).",
        "    Sayı büyükse yavaşlamanın yeri burasıdır.   (ölçü %s)"
        % ("açık" if d.get("açık") else "KAPALI"),
    ])

_SENET_SAYAC: Dict[str, float] = {"yazma": 0.0, "bayt": 0.0,
                                  "mahallî": 0.0, "mahallî_bayt": 0.0}


def senet_beyani() -> Dict[str, float]:
    b = dict(_SENET_SAYAC)
    b["bayt_başına"] = (b["bayt"] / b["yazma"]) if b["yazma"] else 0.0
    return b


_CEYREK = np.array([1.0 + 0.0j, 0.0 + 1.0j, -1.0 + 0.0j, 0.0 - 1.0j])

SENET_ACIK: List[bool] = [False]


class Iz:

    def __init__(self) -> None:
        self.kapi = 0
        self.kesme = 0.0
        self.defter: List[Tuple[str, str]] = []
        self.senet_acik = bool(SENET_ACIK[0])
        self.senet: List[Tuple[str, Tuple[int, ...], np.ndarray]] = []
        self.baglanti: List[Tuple[int, int, float, Any]] = []
        self.mahalli_senet: List[np.ndarray] = []
        self.mahalli_bag: List[Tuple[int, float, int, np.ndarray]] = []
        self.derinlik = 0
        self.uretecsiz = 0
        self.bag_reddi = 0
        self.son_senet = -1

    def not_dus(self, meleke: str, mesaj: str = "") -> None:
        self.defter.append((str(meleke), str(mesaj)))

    def senedi_ac(self) -> None:
        self.senet_acik = True
        self.senet = []
        self.baglanti = []
        self.uretecsiz = 0
        self.mahalli_senet: List[np.ndarray] = []
        self.mahalli_bag = []

    def mahalli_bag_yaz(self, par: int, olcek: float, seviye: int,
                        aci: np.ndarray) -> int:
        if not self.senet_acik:
            return -1
        self.mahalli_bag.append((int(par), float(olcek), int(seviye),
                                 np.asarray(aci, float).copy()))
        _SENET_SAYAC["mahallî_bağ"] = _SENET_SAYAC.get(
            "mahallî_bağ", 0.0) + 1.0
        return len(self.mahalli_bag) - 1

    def mahalli_yaz(self, mahalli) -> int:
        if not self.senet_acik or mahalli is None:
            return -1
        dilim = mahalli.senet_dilimi()
        if dilim.size == 0:
            return -1
        self.mahalli_senet.append(dilim)
        _SENET_SAYAC["mahallî"] += 1.0
        _SENET_SAYAC["mahallî_bayt"] += float(dilim.nbytes)
        return len(self.mahalli_senet) - 1

    def senedi_kapat(self) -> None:
        self.senet_acik = False
        self.senet = []
        self.baglanti = []
        self.mahalli_senet = []
        self.mahalli_bag = []

    def kapi_yaz(self, tur: str, yuvalar, G) -> int:
        if not self.senet_acik:
            return -1
        _SENET_SAYAC["yazma"] += 1.0
        A = np.asarray(G)
        _SENET_SAYAC["bayt"] += float(A.nbytes)
        self.senet.append((str(tur),
                           tuple(int(y) for y in np.atleast_1d(yuvalar)),
                           A.copy()))
        self.son_senet = len(self.senet) - 1
        return self.son_senet

    def bag_yaz(self, senet_no: int, parametre: int, olcek: float,
                turev=None) -> None:
        if not self.senet_acik or int(senet_no) < 0:
            if self.senet_acik:
                self.bag_reddi += 1
            return
        if turev is None:
            self.uretecsiz += 1
            return
        self.baglanti.append((int(senet_no), int(parametre), float(olcek),
                              turev))


@dataclass
class QuditAyar:

    d: int = 4096
    lif: Tuple[int, ...] = (16, 16, 16)
    yigin: int = 1
    kulli_alanlar: Tuple[Tuple[str, int], ...] = (
        ("makam", 3), ("mizan", 4), ("tenakuz", 2), ("tasdik", 2),
        ("sukut", 1), ("nakz", 2), ("kelam", 4), ("kaide", 12),
        ("orak", 1), ("gaye", 2), ("tertip", 4),
    )
    yerel_yuva: int = 1
    tip: object = np.complex128
    tohum: int = 0
    motor: str = "sürekli"
    faz_mertebesi: int = 16
    hat: str = "c"
    hat_bandi: int = 0

    def __post_init__(self):
        if int(np.prod(self.lif)) != int(self.d):
            raise ValueError("lifler çarpımı d'ye eşit olmalı: %s ≠ %d"
                             % (self.lif, self.d))


class QuditYazmac:

    def __init__(self, ayar: Optional[QuditAyar] = None,
                 veri_lifi: int = 4,
                 n: Optional[int] = None, bag: Optional[int] = None,
                 tohum: int = 0, tip=None, obek: Optional[int] = None,
                 yigin: Optional[int] = None) -> None:
        if ayar is None and n is not None:
            k = int(np.ceil(np.log2(max(int(n), 2))))
            k = int(min(max(k, 1), 20))
            ayar = QuditAyar(d=1 << k, lif=(1 << k,), tohum=int(tohum),
                             yigin=int(yigin or 1))
            veri_lifi = k
        self.ayar = ayar or QuditAyar()
        a = self.ayar
        self._veri_lifi = int(veri_lifi)
        ns, carp = 0, 1
        for _x in tuple(a.lif):
            if carp >= int(veri_lifi):
                break
            carp *= int(_x)
            ns += 1
        self._n_satir = max(1, ns)
        self._yuva_onbellek: Dict[int, Tuple[int, int]] = {}
        self._ikinin_kuvveti = all(
            (int(x) & (int(x) - 1)) == 0 for x in tuple(self.ayar.lif))
        self._bolum_onbellek: Dict[int, Tuple[int, int]] = {}
        self._gecerli_onbellek: Dict[int, bool] = {}
        self._adres_np: Optional[Tuple[np.ndarray, np.ndarray,
                                       np.ndarray]] = None
        self._veri_yuvasi = max(1, int(a.lif[0]).bit_length() - 1)
        self._satir_yuva = self._veri_yuvasi + int(self.ayar.yerel_yuva)
        self._dusen_kapi = 0
        self._kontrollu_kapi = 0
        self._matchgate_kapi = 0
        r = np.random.default_rng(int(a.tohum))
        self.B = int(a.yigin)
        self.d = int(a.d)
        self._seviye = int(round(math.log2(self.d)))
        assert 2 ** self._seviye == self.d, (
            "bit düzlemi ikinin kuvvetini ister: d=%d" % self.d)
        self._bekleyen: Dict[int, np.ndarray] = {}
        from .qcekirdek import Bant
        self._bant = Bant(int(a.yigin), int(a.d), tuple(a.lif),
                          hat=str(a.hat), bant=int(a.hat_bandi))
        self._faz_bekleyen: Optional[np.ndarray] = None
        self._faz_toplam = np.zeros((int(a.yigin), int(a.d)), float)
        self._faz_indirilen = 0
        self.cephe = 0
        self._psi = np.full((self.B, self.d), 1.0 / np.sqrt(self.d),
                            dtype=a.tip)
        self._kapi = 0
        self.iz = Iz()
        self.bag = 0
        self._sektor: Dict[str, Tuple[int, int]] = {}
        self._sektor_vurusu = 0
        bas = 0
        for ad, _pay in a.kulli_alanlar:
            gen = int(KULLI_SEKTOR_TABANI)
            assert int(_pay) <= gen, (
                "'%s' sektörü %d yuva ister, sabit taban %d'ten büyük "
                "olamaz (ferman 90)" % (ad, int(_pay), gen))
            assert bas + gen <= self.d, (
                "yazmaç küllî sektörlere yetmiyor: '%s' sektörü [%d,%d) "
                "ister, d=%d -- ölçülen bir sayıdır, sessizce küçültülemez "
                "(ferman 5)" % (ad, bas, bas + gen, self.d))
            self._sektor[ad] = (bas, bas + gen)
            bas += gen

    @property
    def n(self) -> int:
        return self._n_satir * (self._veri_lifi
                                + int(self.ayar.yerel_yuva)) + self.d

    @property
    def A(self) -> np.ndarray:
        return self.lifli

    def tekil_yogunluklar(self, yuvalar: Sequence[int]) -> np.ndarray:
        idx = [int(y) for y in np.asarray(yuvalar, np.intp).reshape(-1)]
        if not idx:
            return np.zeros((self.B, 0, 2, 2))
        lif = tuple(self.ayar.lif)
        T = self.lifli
        out = np.zeros((self.B, len(idx), 2, 2), complex)
        for m, y in enumerate(idx):
            k, alt = self._lif_no(y)
            if not (0 <= k < len(lif)):
                out[:, m] = np.eye(2) * 0.5
                continue
            n = lif[k]
            b = 1 << int(alt)
            if b >= n:
                out[:, m] = np.eye(2) * 0.5
                continue
            X = np.moveaxis(T, k + 1, -1).reshape(self.B, -1, n)
            m0 = np.array([x for x in range(n) if not (x & b)])
            m1 = m0 | b
            a0, a1 = X[:, :, m0], X[:, :, m1]
            out[:, m, 0, 0] = np.sum(np.abs(a0) ** 2, axis=(1, 2))
            out[:, m, 1, 1] = np.sum(np.abs(a1) ** 2, axis=(1, 2))
            c = np.sum(a0 * a1.conj(), axis=(1, 2))
            out[:, m, 0, 1] = c
            out[:, m, 1, 0] = c.conj()
        iz = out[:, :, 0, 0] + out[:, :, 1, 1]
        return out / np.maximum(iz[:, :, None, None].real, 1e-300)

    def yuva_yogunluklari(self, yuvalar=None) -> np.ndarray:
        if yuvalar is None:
            yuvalar = list(range(min(8, self.d)))
        return self.tekil_yogunluklar(yuvalar)

    def blok_dagilimi(self, bas: int, kac: int) -> np.ndarray:
        k, alt = self._lif_no(int(bas))
        k = min(int(k), len(self.ayar.lif) - 1)
        n = self.ayar.lif[k]
        X = np.moveaxis(self.lifli, k + 1, -1).reshape(self.B, -1, n)
        p = np.sum(np.abs(X) ** 2, axis=1)
        m = min(1 << int(kac), n)
        parca = np.array_split(np.arange(n), m)
        P = np.stack([p[:, i].sum(axis=1) for i in parca], axis=1)
        return P / np.maximum(P.sum(axis=1, keepdims=True), 1e-300)

    def olcumler_yigin(self) -> Dict[str, np.ndarray]:
        o = self.olcumler()
        return {k: np.atleast_1d(np.asarray(v, float))
                for k, v in o.items()}

    def makam_derece_vektoru(self) -> np.ndarray:
        n = int(self._mahalli_zorunlu().pencere)
        return np.linspace(0.0, 1.0, max(2, n))

    def makam_dagilimi(self) -> np.ndarray:
        return self._mahalli_zorunlu().kok_dagilimi("makam")

    @property
    def lifli(self) -> np.ndarray:
        return self.psi.reshape((self.B,) + tuple(self.ayar.lif))

    def norm(self) -> np.ndarray:
        return np.sum(np.abs(self.psi) ** 2, axis=1)

    def normalize(self) -> np.ndarray:
        n = np.sqrt(np.maximum(self.norm(), 1e-300))
        self.iz.kapi_yaz("ölçek", (), n.reshape(-1, 1).copy())
        self.psi = self.psi / n[:, None]
        return n

    def norm_hatasi(self) -> float:
        return float(np.max(np.abs(self.norm() - 1.0)))

    def sadakat(self) -> float:
        toplam = self._kapi + self._dusen_kapi
        if toplam <= 0:
            return 1.0
        return float(self._kapi) / float(toplam)

    def sadakat_kapi_basina(self, kapi: int = 1) -> float:
        kapi = max(1, int(kapi), int(self._kapi))
        return max(0.0, 1.0 - float(self._dusen_kapi) / float(kapi))

    def ic_carpim(self, other=None) -> np.ndarray:
        o = self.psi if other is None else np.asarray(other)
        return np.sum(np.conj(self.psi) * o, axis=1)

    def supurme(self, *a, **k) -> None:
        self.iz.not_dus("süpürme", "quditte süpürme yok -- işlem yok")

    def takas(self, *a, **k) -> None:
        self.iz.not_dus("takas", "quditte takas yok -- işlem yok")

    def genlik(self, idx) -> np.ndarray:
        return self.psi[:, int(idx)]

    def deger(self, idx) -> np.ndarray:
        return self.genlik(idx)

    def parametre(self) -> int:
        return int(self.d * 2)

    def bayt(self) -> int:
        return int(self.psi.nbytes)

    def superpozisyona_sok(self) -> None:
        self.superpozisyon()

    def harman_kur(self, *a, **k) -> None:
        self.iz.not_dus("harman_kur", "qudit lif üniterleri kullanılır")

    def tek_kapi(self, G, yuvalar) -> None:
        for y in np.atleast_1d(np.asarray(yuvalar)).reshape(-1):
            self.tek(int(y), G)

    def tek_kapi_yuva(self, yuva: int, G) -> None:
        self.tek(int(yuva), G)

    def cift_kapi(self, G, ofset: int = 0, alt=None, ust=None) -> None:
        self.cift(int(ofset), G)

    def cift_kapi_yuva(self, i: int, j: int, G) -> None:
        self.uzak_cift(int(i), int(j), G)

    def tek_kapi_yigin(self, yuvalar, G) -> None:
        self.tek_yigin(yuvalar, G)

    def cift_kapi_yigin(self, sol_yuvalar, G) -> None:
        G = np.asarray(G)
        m = len(list(sol_yuvalar))
        if G.ndim == 2:
            G = np.broadcast_to(G, (m,) + G.shape)
        for y, g in zip(sol_yuvalar, G):
            self.cift(int(y), g)

    def sadakat_log(self) -> float:
        return float(math.log(max(self.sadakat(), 1e-300)))

    def lif_kapisi(self, k: int, G: np.ndarray) -> None:
        raise NotImplementedError(
            "``lif_kapisi`` imha edildi: n×n kapı graf motoruna geçmez. "
            "Bit düzlemi kapılarını kullanın (``tek``, ``cift``, "
            "``bit_kapisi``). Lif %d, kapı %r." % (k, np.shape(G)))

    def _bit(self, k: int, alt: int) -> int:
        _on, ard = self._bolum(int(k))
        return int(math.log2(ard)) + int(alt)

    def _mahalli_zorunlu(self):
        m = getattr(self, "mahalli", None)
        assert m is not None, (
            "SEKTÖR MAHALLÎ YAZMAÇTAN OKUNUR -- bu yazmaca mahallî zırh "
            "bağlanmamış. Sektör bir bellek dilimi değil, Lie cebrinin "
            "zâtî süperseçim (DHR) yüküdür (ferman 2-Ö, 2-İ, 3-D #90).")
        assert int(getattr(m, "pencere", 0)) > 0, (
            "SEKTÖR OKUNDU FAKAT AKTİF PENCERE SIFIR -- `kodla` mahallî "
            "zırha tohum ekmeden sektör tartılamaz (ferman 2-A)")
        return m

    def sektor_agirligi(self, ad: str) -> np.ndarray:
        w = self._mahalli_zorunlu().sektor_yigini(str(ad))
        _SEKTOR_SAYAC["mahallî_okuma"] = _SEKTOR_SAYAC.get(
            "mahallî_okuma", 0.0) + 1.0
        return np.resize(np.asarray(w, float), self.B)


    def _eksen(self, k: int, alt: int) -> int:
        lif = tuple(self.ayar.lif)
        if not (0 <= int(k) < len(lif)):
            return 0
        n = int(lif[int(k)])
        if (1 << int(alt)) >= n:
            return 0
        return self._seviye - self._bit(int(k), int(alt))

    def _duzlem(self, T: np.ndarray, eksen: int, bit: int) -> np.ndarray:
        return T[(slice(None),) * eksen + (int(bit),)]

    def _bit_gorunumu(self) -> np.ndarray:
        T = self.psi.reshape((self.B,) + (2,) * self._seviye)
        assert np.shares_memory(T, self.psi), (
            "bit görünümü kopya çıktı -- kapı duruma vurmazdı")
        return T


    @property
    def psi(self) -> np.ndarray:
        if (self._bekleyen or self._faz_bekleyen is not None
                or not self._bant.bos_mu()):
            self._bosalt()
        return self._psi

    @psi.setter
    def psi(self, v) -> None:
        self._bekleyen.clear()
        self._faz_bekleyen = None
        self._psi = np.asarray(v)
        if self.iz.senet_acik:
            self.iz.kapi_yaz("durum", (),
                             np.asarray(self._psi, complex).copy())

    @property
    def psi_tensor(self) -> np.ndarray:
        return self.psi.reshape((self.B,) + tuple(self.ayar.lif))

    @psi_tensor.setter
    def psi_tensor(self, v) -> None:
        self.psi = np.asarray(v).reshape(self.B, self.d)

    def _karolari_banda(self) -> None:
        if not self._bekleyen:
            return
        bekleyen, self._bekleyen = self._bekleyen, {}
        for k in sorted(bekleyen):
            self._bant.karo(int(k), bekleyen[k])

    def _bosalt(self) -> None:
        self._karolari_banda()
        if not self._bant.bos_mu():
            self._psi = np.ascontiguousarray(self._psi)
            self._bant.bosalt(self._psi)
        self._faz_indir()

    def _faz_indir(self) -> None:
        t = self._faz_bekleyen
        if t is None:
            return
        self._faz_bekleyen = None
        if not np.any(t):
            return
        if self.iz.senet_acik:
            self.iz.kapi_yaz("faz", (),
                             np.broadcast_to(t, (self.B, self.d)).copy())
        self._psi = (self._psi * np.exp(-1j * t)).astype(self._psi.dtype)
        self._faz_toplam = self._faz_toplam + t
        self._faz_indirilen += 1

    def faz_birikimi(self) -> np.ndarray:
        return self._faz_toplam.copy()

    def faz_borcu(self) -> Dict[str, float]:
        a = np.abs(np.asarray(self._faz_toplam, float).reshape(-1))
        return {"toplam_faz_ortalama": float(np.mean(a)) if a.size else 0.0,
                "toplam_faz_azamî": float(a.max()) if a.size else 0.0,
                "indirme": float(self._faz_indirilen)}

    def _karo_indir(self, k: int, M: np.ndarray) -> None:
        n = int(self.ayar.lif[int(k)])
        on, ard = self._bolum(int(k))
        M = np.asarray(M, complex)
        if M.ndim == 3:
            X = self._psi.reshape(self.B, on, n, ard)
            Y = np.einsum("bij,bojd->boid", M, X, optimize=True)
            self._psi = np.ascontiguousarray(
                Y.reshape(self.B, self.d), dtype=self._psi.dtype)
            return
        X = self._psi.reshape(self.B * on, n, ard)
        if ard == 1:
            Y = X.reshape(-1, n) @ M.T
        else:
            Y = np.matmul(M, X)
        self._psi = np.ascontiguousarray(
            Y.reshape(self.B, self.d), dtype=self._psi.dtype)

    def _karo_vur(self, k: int, M: np.ndarray) -> None:
        self._faz_indir()
        M = np.asarray(M, complex)
        self.iz.kapi_yaz("karo", (int(k),), M)
        self._kapi += 1
        self.iz.kapi += 1
        if M.ndim == 3:
            self._bosalt()
            self._karo_indir(int(k), M)
            return
        eski = self._bekleyen.get(int(k))
        self._bekleyen[int(k)] = M if eski is None else M @ eski

    def _bit_kapisi_lifli(self, k: int, alt: int, G: np.ndarray,
                          bag=None) -> None:
        if self._eksen(k, alt) <= 0:
            self._dusen_kapi += 1
            if bag:
                self.iz.uretecsiz += len(bag)
            return
        n = int(self.ayar.lif[int(k)])
        self._karo_vur(k, self._gomulu(n, int(alt), G))
        if not bag or not self.iz.senet_acik:
            return
        for (par, olcek, dG) in bag:
            self.iz.bag_yaz(self.iz.son_senet, int(par), float(olcek),
                            ("bit", int(k), int(alt),
                             np.asarray(dG, complex).reshape(2, 2)))

    def _cift_kapisi_lifli(self, ki: int, ai: int, kj: int, aj: int,
                           G: np.ndarray, baglar=None) -> None:
        ei = self._eksen(ki, ai)
        ej = self._eksen(kj, aj)
        if ei <= 0 or ej <= 0 or ei == ej:
            self._dusen_kapi += 1
            if baglar:
                self.iz.uretecsiz += len(baglar)
            return
        G = np.asarray(G, complex).reshape(4, 4)
        if int(ki) == int(kj):
            n = int(self.ayar.lif[int(ki)])
            bi, bj = 1 << int(ai), 1 << int(aj)
            M = np.eye(n, dtype=complex)
            for x in range(n):
                if (x & bi) or (x & bj):
                    continue
                idx = [x, x | bj, x | bi, x | bi | bj]
                for a in range(4):
                    for b in range(4):
                        M[idx[a], idx[b]] = G[a, b]
            self._karo_vur(int(ki), M)
            if baglar:
                no = self.iz.son_senet
                n2 = int(self.ayar.lif[int(ki)])
                for (par, olcek, dG) in baglar:
                    dM = np.zeros((n2, n2), complex)
                    dG4 = np.asarray(dG, complex).reshape(4, 4)
                    for x in range(n2):
                        if (x & bi) or (x & bj):
                            continue
                        ix = [x, x | bj, x | bi, x | bi | bj]
                        for a in range(4):
                            for b in range(4):
                                dM[ix[a], ix[b]] = dG4[a, b]
                    self.iz.bag_yaz(no, int(par), float(olcek),
                                    ("karo4", int(ki), dM))
            return
        self._faz_indir()
        self._karolari_banda()
        bi = 1 << int(self._seviye - ei)
        bj = 1 << int(self._seviye - ej)
        if matchgate_mi(G)[0]:
            self._matchgate_kapi += 1
        _no = self.iz.kapi_yaz("bant", (int(bi), int(bj)), G)
        if baglar:
            for (par, olcek, dG) in baglar:
                self.iz.bag_yaz(_no, int(par), float(olcek),
                                ("bant4", int(bi), int(bj),
                                 np.asarray(dG, complex).reshape(4, 4)))
        self._bant.cift(bi, bj, G)
        self._kapi += 1
        self.iz.kapi += 1

    def bit_kapisi(self, k: int, alt: int, G: np.ndarray, bag=None) -> None:
        self._bit_kapisi(k, alt, G, bag)

    def _bit_kapisi(self, k: int, alt: int, G: np.ndarray,
                    bag=None) -> None:
        self._bit_kapisi_lifli(k, alt, G, bag)

    def faz(self, teta) -> None:
        t = np.asarray(teta, float)
        if t.ndim == 1 and t.size != self.d:
            from .qudit import agirlik
            t = np.asarray(agirlik(self.d, t.reshape(-1)), float)
        t = np.atleast_2d(t)
        assert t.shape[-1] == self.d, (
            "faz açısı yazmaç ebadında olmalı: %s ≠ %d"
            % (t.shape, self.d))
        t = np.broadcast_to(t, (self.B, self.d)).copy()
        if self._bekleyen:
            self._bosalt()
        self._faz_bekleyen = (t if self._faz_bekleyen is None
                              else self._faz_bekleyen + t)
        self._kapi += 1

    def sektor_kapisi(self, ad: str, M: np.ndarray) -> None:
        m = self._mahalli_zorunlu()
        M = np.asarray(M)
        assert M.ndim == 2 and M.shape[0] == M.shape[1], (
            "sektör kapısı kare olmalı, %s verildi" % (M.shape,))
        self.iz.mahalli_yaz(m)
        vuran = int(m.kok_kapisi(str(ad), M))
        if vuran <= 0:
            self._dusen_kapi += 1
            _SEKTOR_SAYAC["düşen"] = _SEKTOR_SAYAC.get("düşen", 0.0) + 1.0
            return
        _SEKTOR_SAYAC["kapı_dizeyi"] += 1.0
        self._kapi += 1

    def sektor_faz_vur(self, ad: str, aci, bag=None) -> int:
        m = getattr(self, "mahalli", None)
        if m is not None:
            m.cartan_ekle(str(ad), float(np.mean(
                np.asarray(aci, float).reshape(-1))))
        i, j = self.sektor(ad)
        a = np.asarray(aci, float).reshape(-1)
        gen = int(j - i)
        if a.size != gen:
            a = np.resize(a, gen) if a.size else np.zeros(gen, float)
        t = np.zeros(self.d, float)
        t[i:j] = a
        self.faz(t)
        self._sektor_vurusu += 1
        _SEKTOR_SAYAC["faz_vuruşu"] += 1.0
        _SEKTOR_SAYAC["küllî_faz_yazması"] += 1.0
        if bag:
            self._faz_bagla(np.arange(i, j, dtype=np.int64), bag)
        return gen

    def _genlik_agirligi(self) -> float:
        _SEKTOR_SAYAC["küllî_iç_çarpım"] = _SEKTOR_SAYAC.get(
            "küllî_iç_çarpım", 0.0) + 1.0
        return float(self._mahalli_zorunlu().kulli_agirlik())

    def sektor_donmesi(self, ad: str, teta, bag=None) -> int:
        m = self._mahalli_zorunlu()
        a = np.asarray(teta, float).reshape(-1)
        if a.size == 0:
            a = np.zeros(1, float)
        vuran = int(m.kok_donmesi(str(ad), a))
        if vuran <= 0:
            self._dusen_kapi += 1
            _SEKTOR_SAYAC["düşen"] = _SEKTOR_SAYAC.get("düşen", 0.0) + 1.0
            return 0
        self.iz.mahalli_yaz(m)
        self._kapi += 1
        self._sektor_vurusu += 1
        _SEKTOR_SAYAC["dönme"] += 1.0
        m.cartan_ekle(str(ad), float(np.mean(a)))
        if bag and self.iz.senet_acik:
            sev = int(m.kok_seviyesi(ad))
            for (par, olcek, pay) in ([bag] if isinstance(bag, tuple)
                                      else list(bag)):
                p = np.asarray(pay, float).reshape(-1)
                agir = (a * np.resize(p, a.size)) if p.size else a
                self.iz.mahalli_bag_yaz(int(par), float(olcek), sev, agir)
            _SEKTOR_SAYAC["mahallî_bağ"] = _SEKTOR_SAYAC.get(
                "mahallî_bağ", 0.0) + 1.0
        return vuran

    def satir_donmesi(self, i: int, teta, bag=None) -> int:
        m = self._mahalli_zorunlu()
        a = np.asarray(teta, float).reshape(-1)
        if a.size == 0:
            a = np.zeros(1, float)
        vuran = int(m.satir_donmesi(int(i), float(np.mean(a))))
        if vuran <= 0:
            self._dusen_kapi += 1
            _SEKTOR_SAYAC["düşen"] = _SEKTOR_SAYAC.get("düşen", 0.0) + 1.0
            return 0
        self.iz.mahalli_yaz(m)
        self._kapi += 1
        self._sektor_vurusu += 1
        _SEKTOR_SAYAC["dönme"] += 1.0
        if bag and self.iz.senet_acik:
            for (par, olcek, pay) in ([bag] if isinstance(bag, tuple)
                                      else list(bag)):
                p = np.asarray(pay, float).reshape(-1)
                agir = (a * np.resize(p, a.size)) if p.size else a
                self.iz.mahalli_bag_yaz(int(par), float(olcek), int(i), agir)
            _SEKTOR_SAYAC["mahallî_bağ"] = _SEKTOR_SAYAC.get(
                "mahallî_bağ", 0.0) + 1.0
        return vuran

    def satir_cifti(self, i: int, j: int, teta: float, bag=None) -> int:
        m = self._mahalli_zorunlu()
        t = float(teta)
        vuran = int(m.satir_cifti(int(i), int(j), t))
        if vuran <= 0:
            self._dusen_kapi += 1
            _SEKTOR_SAYAC["düşen"] = _SEKTOR_SAYAC.get("düşen", 0.0) + 1.0
            return 0
        self.iz.mahalli_yaz(m)
        self._kapi += 1
        self._sektor_vurusu += 1
        _SEKTOR_SAYAC["kenet"] += 1.0
        if bag and self.iz.senet_acik:
            for (par, olcek, pay) in ([bag] if isinstance(bag, tuple)
                                      else list(bag)):
                agir = float(np.mean(np.asarray(pay, float))) if np.size(
                    pay) else 1.0
                self.iz.mahalli_bag_yaz(int(par), float(olcek), int(i),
                                        np.array([t * agir]))
            _SEKTOR_SAYAC["mahallî_bağ"] = _SEKTOR_SAYAC.get(
                "mahallî_bağ", 0.0) + 1.0
        return vuran

    def sektor_cifti(self, kontrol: str, hedef: str,
                     bag: float = 1.0, degil: bool = False,
                     aci=None, senet=None, defter=None,
                     agirlik=None) -> float:
        i0, j0 = self.sektor(kontrol)
        i1, j1 = self.sektor(hedef)
        top = (float(agirlik) if agirlik is not None
               else self._genlik_agirligi())
        assert top > 0.0, (
            "yazmaç tamamen söndü -- kenetlenecek genlik yok (ferman 5)")
        m = self._mahalli_zorunlu()
        w_kontrol = float(m.sektor_yigini(str(kontrol)).sum() / top)
        w_kontrol = min(1.0, max(0.0, w_kontrol))
        if degil:
            w_kontrol = 1.0 - w_kontrol
        w_hedef = np.asarray(m.kok_dagilimi(str(hedef)),
                             float).mean(axis=0)
        pay = float(w_hedef.sum())
        teta = float(m.cartan_oku(str(kontrol)))
        gen = int(w_hedef.size)
        if aci is None:
            a = np.full(gen, teta, float)
        else:
            a = np.asarray(aci, float).reshape(-1)
            a = np.resize(a, gen) if a.size else np.zeros(gen, float)
        etki = float(bag) * float(np.mean(a)) * w_kontrol
        t = np.zeros(self.d, float)
        if pay > 0.0:
            dal = -float(bag) * w_kontrol * a * (w_hedef / pay) * gen
            u = int(min(self.d, i1 + dal.size))
            t[i1:u] = dal[:u - i1]
        if defter is None:
            self.faz(t)
        else:
            defter += t
        if defter is None:
            _SEKTOR_SAYAC["küllî_faz_yazması"] += 1.0
        self._sektor_vurusu += 1
        _SEKTOR_SAYAC["kenet"] += 1.0
        self._kenet_vurusu = getattr(self, "_kenet_vurusu", 0) + 1
        if senet and defter is None:
            self._faz_bagla(np.arange(i1, j1, dtype=np.int64), senet)
        elif senet:
            self._bekleyen_bag = getattr(self, "_bekleyen_bag", [])
            self._bekleyen_bag.append(
                (np.arange(i1, j1, dtype=np.int64), list(senet)))
        if m is not None:
            m.cartan_ekle("kenet.%s%s×%s"
                          % ("¬" if degil else "", kontrol, hedef), etki)
            m.cartan_ekle(str(hedef), etki)
        return etki

    def sektor_kenetleri(self, kenetler) -> float:
        k = list(kenetler)
        if not k:
            return 0.0
        defter = np.zeros(self.d, float)
        self._bekleyen_bag = []
        agirlik = self._genlik_agirligi()
        etki = 0.0
        for z in k:
            etki += self.sektor_cifti(
                str(z[0]), str(z[1]),
                bag=float(z[2]) if len(z) > 2 and z[2] is not None else 1.0,
                degil=bool(z[3]) if len(z) > 3 else False,
                aci=z[4] if len(z) > 4 else None,
                senet=z[5] if len(z) > 5 else None,
                defter=defter, agirlik=agirlik)
        self.faz(defter)
        _SEKTOR_SAYAC["küllî_faz_yazması"] += 1.0
        for dizin, senet in self._bekleyen_bag:
            self._faz_bagla(dizin, senet)
        self._bekleyen_bag = []
        return float(etki)

    def sektor_oruntusu(self, oruntu, kok: str = "") -> float:
        d = dict(oruntu or {})
        if not d:
            return 0.0
        top = self._genlik_agirligi()
        assert top > 0.0, (
            "yazmaç tamamen söndü -- örüntü tartılamaz (ferman 5)")
        carpim = 1.0
        parca: List[str] = []
        mh = self._mahalli_zorunlu()
        for sek in sorted(d):
            w = float(mh.sektor_yigini(str(sek)).sum() / top)
            w = min(1.0, max(0.0, w))
            bit = int(d[sek]) & 1
            carpim *= (w if bit else (1.0 - w))
            parca.append(("" if bit else "¬") + str(sek))
        ad = kok or ("yasak." + "∧".join(parca))
        mh.cartan_ekle(ad, float(carpim) * math.pi)
        self._oruntu_vurusu = getattr(self, "_oruntu_vurusu", 0) + 1
        self._sektor_vurusu += 1
        _SEKTOR_SAYAC["örüntü"] += 1.0
        return float(carpim)

    def sektor_faz_bagi(self, ad: str, par, olcek: float,
                        pay=None) -> List[Tuple[int, float, np.ndarray]]:
        i, j = self.sektor(ad)
        gen = int(j - i)
        pid = np.asarray(par, np.int64).reshape(-1)
        p = (np.ones(gen) if pay is None
             else np.resize(np.asarray(pay, float).reshape(-1), gen))
        bag = []
        for k in range(min(gen, pid.size)):
            v = np.zeros(gen, float)
            v[k] = float(p[k])
            bag.append((int(pid[k]), float(olcek), v))
        return bag

    def sektor(self, ad: str) -> Tuple[int, int]:
        if ad not in self._sektor:
            raise ValueError("küllî alan bilinmiyor: %r" % (ad,))
        return self._sektor[ad]

    def alan_degeri(self, ad: str):
        v = self.sektor_agirligi(ad)
        return float(v[0]) if self.B == 1 else v

    def olcumler(self) -> Dict[str, float]:
        mh = self._mahalli_zorunlu()
        out: Dict[str, float] = {}
        for ad in self._sektor:
            v = np.resize(np.asarray(mh.sektor_yigini(ad), float), self.B)
            out[ad] = float(v[0]) if self.B == 1 else v
        e = self.dolasiklik_entropisi()
        out["entropi"] = float(e["entropi"])
        out["norm_hatası"] = self.norm_hatasi()
        return out

    def dolasiklik_entropisi(self, kesit: int = 1) -> Dict[str, float]:
        lif = tuple(self.ayar.lif)
        kesit = int(np.clip(kesit, 1, len(lif) - 1))
        sol = int(np.prod(lif[:kesit]))
        sag = int(np.prod(lif[kesit:]))
        M = self.psi.reshape(self.B, sol, sag)
        rho = np.einsum("bij,bkj->bik", M, M.conj())
        iz = np.einsum("bii->b", rho).real
        rho = rho / np.maximum(iz, 1e-300)[:, None, None]
        w = np.linalg.eigvalsh(rho)
        w = np.clip(w.real, 1e-300, None)
        S = -np.sum(w * np.log(w), axis=1)
        return {"entropi": float(np.mean(S)),
                "entropi_yigin": S,
                "schmidt": float(min(sol, sag)),
                "kesit": kesit}

    def cephe_hali(self) -> np.ndarray:
        mh = self._mahalli_zorunlu()
        c = int(np.clip(int(self.cephe), 0, int(mh.pencere) - 1))
        n_v = int(self.ayar.lif[0])
        q = int(min(n_v, int(mh.taban)))
        H = np.zeros((self.B, n_v), complex)
        dilim = np.asarray(mh.hal[:, c, :q], complex)
        H[:dilim.shape[0], :q] = dilim[:self.B]
        G = getattr(self, "_cephe_genligi", None)
        assert G is not None, (
            "CEPHE HÂLİ SIRF MAHALLÎ OKUNAMAZ -- hibrit yazmaç ikisi "
            "beraberdir: donanım kanadı mahallî zırh, idrak kanadı KAN "
            "genliği (ferman 2-Ş, 2-Ê). İntâc koşmadan hâl istenmiş.")
        A = np.asarray(G, complex)
        k = int(min(n_v, A.shape[-1]))
        carpan = np.ones((self.B, n_v), complex)
        carpan[:A.shape[0], :k] = A[:self.B, :k]
        H = H * carpan
        _SEKTOR_SAYAC["hibrit_hal"] = _SEKTOR_SAYAC.get(
            "hibrit_hal", 0.0) + 1.0
        nrm = np.linalg.norm(H, axis=-1, keepdims=True)
        canli = nrm > 0.0
        assert bool(canli.any()), (
            "NEDENSEL CEPHE TAMAMEN SÖNDÜ -- hedef qudit %d, pencere %d; "
            "hâl okunamaz (ferman 2-Ê, 2-Ï, 5)" % (c, int(mh.pencere)))
        _SEKTOR_SAYAC["cephe_hali"] = _SEKTOR_SAYAC.get(
            "cephe_hali", 0.0) + 1.0
        return np.where(canli, H / np.where(canli, nrm, 1.0), H)

    def beyan(self, sozluk: int = 0) -> np.ndarray:
        taban = int(sozluk) if int(sozluk) >= 2 else int(self.ayar.lif[0])
        assert taban == int(self.ayar.lif[0]), (
            "beyan basamak eksenini okur: taban %d, lif[0] %d -- ikisi "
            "aynı eksen olmalı (ferman 1-M)" % (taban, int(self.ayar.lif[0])))
        mh = self._mahalli_zorunlu()
        c = int(np.clip(int(self.cephe), 0, int(mh.pencere) - 1))
        q = int(min(taban, int(mh.taban)))
        p = np.abs(np.asarray(mh.hal[:, c, :q], complex)) ** 2
        top = p.sum(axis=1, keepdims=True)
        canli = top > 0.0
        p = np.where(canli, p / np.where(canli, top, 1.0),
                     1.0 / float(max(1, q)))
        _SEKTOR_SAYAC["cephe_okuma"] = _SEKTOR_SAYAC.get(
            "cephe_okuma", 0.0) + 1.0
        if q == taban:
            return np.resize(p, (self.B, taban))
        cik = np.zeros((p.shape[0], taban), float)
        cik[:, :q] = p
        return np.resize(cik, (self.B, taban))

    def beyan_vecihle(self, sozluk: int, vecihler) -> np.ndarray:
        duz = self.beyan(int(sozluk))
        vs = list(vecihler or ())
        if not vs:
            return duz
        taban = int(sozluk) if int(sozluk) >= 2 else int(self.ayar.lif[0])
        top = np.zeros(taban, float)
        agir = 0.0
        for v in vs:
            u = np.asarray(v.gor(self.psi[0]), complex).reshape(-1)
            if u.size != self.d or not np.all(np.isfinite(u)):
                continue
            p = (np.abs(u[:taban]) ** 2)
            s = float(p.sum())
            if s <= 0.0:
                continue
            top += (p / s) * float(v.agirlik)
            agir += float(v.agirlik)
        if agir <= 0.0:
            return duz
        return (top / agir).reshape(1, taban)

    def povm(self, ad: str) -> Tuple[float, float]:
        mh = self._mahalli_zorunlu()
        s0 = mh.kok_seviyesi(ad)
        n = int(mh.pencere)
        v = np.asarray(mh.hal[:, :n, s0], complex)
        yari = int(n) // 2 or 1
        z = float(np.mean(np.sum(np.abs(v[:, :yari]) ** 2, axis=1)
                          - np.sum(np.abs(v[:, yari:]) ** 2, axis=1)))
        x = float(np.mean(2.0 * np.real(
            np.sum(v[:, :yari] * v[:, yari:yari * 2].conj(), axis=1))))
        return z, x


    def superpozisyon(self) -> None:
        self.psi = np.full((self.B, self.d), 1.0 / np.sqrt(self.d),
                           dtype=self.ayar.tip)


    def _lif_no(self, yuva: int) -> Tuple[int, int]:
        y = int(yuva)
        c = self._yuva_onbellek.get(y)
        if c is not None:
            return c
        ns = self._n_satir
        satir_yuva = self._satir_yuva
        if y < ns * satir_yuva:
            c = (y // satir_yuva, y % satir_yuva)
        else:
            o = y - ns * satir_yuva
            c = (len(self.ayar.lif), o)
            for k in range(ns, len(self.ayar.lif)):
                w = int(self.ayar.lif[k]).bit_length() - 1
                if o < w:
                    c = (k, o)
                    break
                o -= w
        self._yuva_onbellek[y] = c
        return c

    def gecerli(self, yuva: int) -> bool:
        y = int(yuva)
        c = self._gecerli_onbellek.get(y)
        if c is not None:
            return c
        k, alt = self._lif_no(y)
        lif = tuple(self.ayar.lif)
        c = bool(0 <= k < len(lif) and (1 << int(alt)) < int(lif[k]))
        self._gecerli_onbellek[y] = c
        return c

    def _adres_dizileri(self):
        if self._adres_np is None:
            ns = self._n_satir
            satir_yuva = self._veri_lifi + int(self.ayar.yerel_yuva)
            lif = tuple(self.ayar.lif)
            n = ns * satir_yuva + sum(
                int(x).bit_length() - 1 for x in lif[ns:])
            k = np.empty(n, np.int64)
            alt = np.empty(n, np.int64)
            gec = np.empty(n, bool)
            for y in range(n):
                kk, aa = self._lif_no(y)
                k[y] = kk
                alt[y] = aa
                gec[y] = self.gecerli(y)
            self._adres_np = (gec, k, alt)
        return self._adres_np

    def gecerli_toplu(self, yuvalar) -> np.ndarray:
        y = np.asarray(yuvalar, np.int64).reshape(-1)
        gec, _k, _a = self._adres_dizileri()
        icinde = (y >= 0) & (y < gec.size)
        out = np.zeros(y.size, bool)
        out[icinde] = gec[y[icinde]]
        return out

    def lif_no_toplu(self, yuvalar) -> Tuple[np.ndarray, np.ndarray]:
        y = np.asarray(yuvalar, np.int64).reshape(-1)
        gec, k, a = self._adres_dizileri()
        icinde = (y >= 0) & (y < gec.size)
        kk = np.full(y.size, -1, np.int64)
        aa = np.full(y.size, -1, np.int64)
        kk[icinde] = k[y[icinde]]
        aa[icinde] = a[y[icinde]]
        return kk, aa

    def veri(self, i: int, j: int) -> int:
        return int(i) * self._satir_yuva + int(j)

    def adres_beyani(self) -> Dict[str, int]:
        yuva = int(self._seviye)
        sigan = yuva // max(1, int(self._satir_yuva))
        kulli_bas = self._n_satir * self._satir_yuva
        gecersiz = sum(1 for y in range(kulli_bas,
                                        kulli_bas + int(self.d))
                       if not self.gecerli(y))
        return {"yuva_bütçesi": yuva,
                "satır_yuvası": int(self._satir_yuva),
                "yazmacın_saydığı_satır": int(self._n_satir),
                "yuvaya_sığan_satır": int(sigan),
                "küllî_taban": int(kulli_bas),
                "küllî_geçersiz_yuva": int(gecersiz),
                "küllî_yuva_adedi": int(self.d)}

    @property
    def n_satir(self) -> int:
        return int(self._n_satir)

    @property
    def veri_yuvasi(self) -> int:
        return int(self._veri_yuvasi)

    def veri_izgara(self, sutun=None, satir=None) -> np.ndarray:
        i = (np.arange(self._n_satir) if satir is None
             else np.asarray(satir, np.int64).reshape(-1))
        j = (np.arange(self._veri_yuvasi) if sutun is None
             else np.asarray(sutun, np.int64).reshape(-1))
        return (i[:, None] * self._satir_yuva + j[None, :]).reshape(-1)

    def yerel(self, i: int) -> int:
        return self.veri(i, self._veri_yuvasi)

    def kulli(self, ad: str, j: int = 0) -> int:
        i, _ = self.sektor(ad)
        return self._n_satir * self._satir_yuva + i + int(j)

    def yereller(self) -> List[int]:
        return [self.yerel(i) for i in range(self._n_satir)]

    def bolge_var(self, ad: str) -> bool:
        return ad in self._sektor

    def not_dus(self, meleke: str, mesaj: str = "") -> None:
        self.iz.not_dus(meleke, mesaj)

    def kanonikle(self) -> None:
        self.iz.not_dus("kanonikle", "quditte kanoniklik yok -- işlem yok")

    def _gomulu(self, n: int, alt: int, G: np.ndarray) -> np.ndarray:
        G = np.asarray(G, complex)
        dilimli = G.ndim == 3
        if dilimli:
            assert G.shape == (self.B, 2, 2), (
                "dilimli kapı yığın ebadında olmalı: %s ≠ (%d, 2, 2) -- "
                "parametre seviyeleri yığın ekseninde durur (ferman 2-R)"
                % (G.shape, self.B))
            M = np.broadcast_to(np.eye(n, dtype=complex),
                                (self.B, n, n)).copy()
        else:
            G = G.reshape(2, 2)
            M = np.eye(n, dtype=complex)
        b = 1 << int(alt)
        if b >= n:
            return M
        for x in range(n):
            if x & b:
                continue
            y = x | b
            if dilimli:
                M[:, x, x] = G[:, 0, 0]; M[:, x, y] = G[:, 0, 1]
                M[:, y, x] = G[:, 1, 0]; M[:, y, y] = G[:, 1, 1]
            else:
                M[x, x] = G[0, 0]; M[x, y] = G[0, 1]
                M[y, x] = G[1, 0]; M[y, y] = G[1, 1]
        return M

    def kontrollu_tek(self, yuva: int, G_dilim: np.ndarray) -> None:
        if not self.gecerli(yuva):
            self._dusen_kapi += 1
            return
        k, alt = self._lif_no(yuva)
        if self._eksen(k, alt) <= 0:
            self._dusen_kapi += 1
            return
        n = int(self.ayar.lif[int(k)])
        self._karo_vur(int(k), self._gomulu(n, int(alt), G_dilim))
        self._kontrollu_kapi += 1

    def tek(self, yuva: int, G: np.ndarray, bag=None) -> None:
        if not self.gecerli(yuva):
            self._dusen_kapi += 1
            if bag is not None:
                self.iz.uretecsiz += 1
            return
        k, alt = self._lif_no(yuva)
        self.bit_kapisi(k, alt, G)
        if bag is None or not self.iz.senet_acik:
            return
        for (par, olcek, dG) in ([bag] if isinstance(bag, tuple)
                                 else list(bag)):
            self.iz.bag_yaz(self.iz.son_senet, int(par), float(olcek),
                            ("bit", int(k), int(alt),
                             np.asarray(dG, complex).reshape(2, 2)))

    def tek_yigin(self, yuvalar: Sequence[int], G, baglar=None) -> None:
        G = np.asarray(G)
        if G.ndim == 2:
            G = np.broadcast_to(G, (len(yuvalar), 2, 2))
        yv = np.asarray([int(y) for y in yuvalar], np.int64)
        if self.iz.senet_acik:
            gec0 = self.gecerli_toplu(yv)
            kk0, aa0 = self.lif_no_toplu(yv)
            self._dusen_kapi += int((~gec0).sum())
            B = list(baglar) if baglar is not None else None
            if B is not None:
                assert len(B) == yv.size, (
                    "her yuvanın kendi bağı olmalı: %d yuva, %d bağ "
                    "(ferman 1-C/b)" % (yv.size, len(B)))
            for idx in np.flatnonzero(gec0):
                self.bit_kapisi(int(kk0[idx]), int(aa0[idx]),
                                np.asarray(G[int(idx)], complex).reshape(2, 2))
                if B is None or B[int(idx)] is None:
                    continue
                par, olcek, dG = B[int(idx)]
                self.iz.bag_yaz(
                    self.iz.son_senet, int(par), float(olcek),
                    ("bit", int(kk0[idx]), int(aa0[idx]),
                     np.asarray(dG, complex).reshape(2, 2)))
            return
        sira: List[Tuple[int, int]] = []
        birik: Dict[Tuple[int, int], np.ndarray] = {}
        gec = self.gecerli_toplu(yv)
        kk, aa = self.lif_no_toplu(yv)
        self._dusen_kapi += int((~gec).sum())
        for idx in np.flatnonzero(gec):
            g = G[int(idx)]
            anahtar = (int(kk[idx]), int(aa[idx]))
            g2 = np.asarray(g, complex).reshape(2, 2)
            if anahtar in birik:
                birik[anahtar] = g2 @ birik[anahtar]
            else:
                birik[anahtar] = g2
                sira.append(anahtar)
        for anahtar in sira:
            self.bit_kapisi(anahtar[0], anahtar[1], birik[anahtar])

    def cift(self, yuva: int, G: np.ndarray, baglar=None) -> None:
        self.uzak_cift(int(yuva), int(yuva) + 1, G, baglar=baglar)

    def _bolum(self, k: int) -> Tuple[int, int]:
        c = self._bolum_onbellek.get(int(k))
        if c is not None:
            return c
        lif = tuple(self.ayar.lif)
        on = 1
        for x in lif[:k]:
            on *= int(x)
        ard = 1
        for x in lif[k + 1:]:
            ard *= int(x)
        c = (on, ard)
        self._bolum_onbellek[int(k)] = c
        return c

    def cift_bit_kapisi(self, ki: int, ai: int, kj: int, aj: int,
                        G: np.ndarray, baglar=None) -> None:
        self._cift_kapisi_lifli(ki, ai, kj, aj, G, baglar=baglar)

    def uzak_cift(self, i: int, j: int, G: np.ndarray,
                  baglar=None) -> None:
        if not (self.gecerli(i) and self.gecerli(j)):
            self._dusen_kapi += 1
            if baglar:
                self.iz.uretecsiz += len(baglar)
            return
        G = np.asarray(G, complex).reshape(4, 4)
        ki, ai = self._lif_no(int(i))
        kj, aj = self._lif_no(int(j))
        lif = tuple(self.ayar.lif)
        if self._ikinin_kuvveti:
            self.cift_bit_kapisi(ki, ai, kj, aj, G, baglar=baglar)
            return
        if ki == kj:
            n = lif[ki]
            bi, bj = 1 << ai, 1 << aj
            if bi >= n or bj >= n or bi == bj:
                if baglar:
                    self.iz.uretecsiz += len(baglar)
                return
            M = np.eye(n, dtype=complex)
            for x in range(n):
                if (x & bi) or (x & bj):
                    continue
                idx = [x, x | bj, x | bi, x | bi | bj]
                for a in range(4):
                    for b in range(4):
                        M[idx[a], idx[b]] = G[a, b]
            self.lif_kapisi(ki, M)
            return
        ni, nj = lif[ki], lif[kj]
        bi, bj = 1 << ai, 1 << aj
        if bi >= ni or bj >= nj:
            if baglar:
                self.iz.uretecsiz += len(baglar)
            return
        T = self.lifli
        T = np.moveaxis(T, (ki + 1, kj + 1), (-2, -1))
        sekil = T.shape
        F = T.reshape(-1, ni, nj)
        Mi = np.eye(ni, dtype=complex)
        Mj = np.eye(nj, dtype=complex)
        for x in range(ni):
            if x & bi:
                continue
            for y in range(nj):
                if y & bj:
                    continue
                idx = [(x, y), (x, y | bj), (x | bi, y), (x | bi, y | bj)]
                v = np.stack([F[:, a, b] for a, b in idx], axis=1)
                v = v @ G.T
                for m, (a, b) in enumerate(idx):
                    F[:, a, b] = v[:, m]
        T = F.reshape(sekil)
        self.iz.kapi_yaz("çift_lif", (int(ki), int(kj), int(bi), int(bj)), G)
        self.psi = np.moveaxis(T, (-2, -1), (ki + 1, kj + 1)).reshape(
            self.B, self.d)
        self._kapi += 1
        self.iz.kapi += 1

    def mpo_uygula(self, W, D: int = 2, bas: int = 0, son=None,
                   sol_sinir=None, sag_sinir=None) -> float:
        if not isinstance(W, dict) or not W:
            return 0.0
        lif = tuple(self.ayar.lif)
        sira: List[Tuple[int, int]] = []
        birik: Dict[Tuple[int, int], np.ndarray] = {}
        for yuva, Wk in W.items():
            Wk = np.asarray(Wk)
            k, alt = self._lif_no(int(yuva))
            if Wk.ndim == 4:
                G = Wk[0, :, :, 0]
            elif Wk.ndim == 2 and Wk.shape == (2, 2):
                G = Wk
            else:
                continue
            if not self.gecerli(int(yuva)):
                self._dusen_kapi += 1
                continue
            G = np.asarray(G, complex).reshape(2, 2)
            if not np.any(G):
                continue
            if (abs(G[0, 0] - 1.0) < 1e-12 and abs(G[1, 1] - 1.0) < 1e-12
                    and abs(G[0, 1]) < 1e-12 and abs(G[1, 0]) < 1e-12):
                continue
            anahtar = (int(k), int(alt))
            g2 = np.asarray(G, complex).reshape(2, 2)
            if anahtar in birik:
                birik[anahtar] = g2 @ birik[anahtar]
            else:
                birik[anahtar] = g2
                sira.append(anahtar)
        for anahtar in sira:
            self.bit_kapisi(anahtar[0], anahtar[1], birik[anahtar])
        self.normalize()
        return 0.0

    def mpo_uygula_hizli(self, *a, **k) -> float:
        return self.mpo_uygula(*a, **k)

    def _mpo_adresleri(self, alan: str, kac: int, duraklar, j: int
                       ) -> np.ndarray:
        if duraklar is not None:
            d = np.asarray(list(duraklar), np.int64).reshape(-1)
            assert d.size, "durak listesi boş verilemez -- adres yoksa faz "\
                           "kime vurulacak (ferman 5)"
            assert int(d.min()) >= 0 and int(d.max()) < self.d, (
                "durak adresi yazmacın dışında: [%d, %d] ⊄ [0, %d)"
                % (int(d.min()), int(d.max()), self.d))
            return d
        i, jj = self.sektor(alan)
        kat = int(dict(self.ayar.kulli_alanlar).get(alan, 1))
        boy = max(1, (jj - i) // max(1, kat))
        bas = i + (int(j) % max(1, kat)) * boy
        son = min(jj, bas + boy)
        d = np.arange(bas, son, dtype=np.int64)
        return d if d.size else np.arange(i, jj, dtype=np.int64)

    def _faz_bagla(self, dizin: np.ndarray, baglar) -> None:
        if not self.iz.senet_acik or not baglar:
            return
        self._faz_indir()
        no = self.iz.son_senet
        if no < 0 or str(self.iz.senet[no][0]) != "faz":
            self.iz.uretecsiz += len(baglar)
            return
        q = np.asarray(self.iz.senet[no][2], np.int64)
        q = q[0] if q.ndim == 2 else q
        vur = np.power(1j, q[dizin])
        for (par, olcek, pay) in baglar:
            deger = 1j * np.asarray(pay, float) * vur
            self.iz.bag_yaz(no, int(par), float(olcek),
                            ("köşegen", dizin.copy(), deger))

    def _mpo(self, alan: str, acilar, duraklar, j: int, par, olcek: float,
             bol: bool, egim=None, bag=None) -> float:
        if alan not in self._sektor:
            return 0.0
        a = np.asarray(acilar if acilar is not None else [0.0],
                       float).reshape(-1)
        dizin = self._mpo_adresleri(alan, a.size, duraklar, int(j))
        sira = np.arange(dizin.size) % a.size
        bolen = float(dizin.size) if bol else 1.0
        t = np.zeros(self.d, float)
        np.add.at(t, dizin, -a[sira] / bolen)
        self.faz(t)
        if bag is not None:
            self._faz_bagla(dizin, list(bag))
            return 0.0
        if par is None:
            return 0.0
        pid = np.asarray(par, np.int64).reshape(-1)
        assert pid.size == a.size, (
            "her açının kendi parametresi olmalı: %d açı, %d parametre "
            "(ferman 1-C/b: isim yazmak bağlamak değildir)"
            % (a.size, pid.size))
        e = (np.ones(a.size, float) if egim is None
             else np.asarray(egim, float).reshape(-1))
        assert e.size == a.size, (
            "eğim tarifi açı sayısınca olmalı: %d ≠ %d" % (e.size, a.size))
        self._faz_bagla(
            dizin, [(int(pid[k]), float(olcek),
                     np.where(sira == k, e[sira] / bolen, 0.0))
                    for k in range(a.size)])
        return 0.0

    def mpo_topla(self, alan: str, acilar=None, duraklar=None, j: int = 0,
                  par=None, olcek: float = 1.0, egim=None, bag=None
                  ) -> float:
        return self._mpo(alan, acilar, duraklar, j, par, olcek, False,
                         egim, bag)

    def mpo_dagit(self, alan: str, acilar=None, duraklar=None, j: int = 0,
                  par=None, olcek: float = 1.0, egim=None, bag=None
                  ) -> float:
        return self._mpo(alan, acilar, duraklar, j, par, olcek, True,
                         egim, bag)

    def rapor(self) -> str:
        o = self.olcumler()
        s = ["=== QUDİT YAZMACI (MPS'in yerine) ===", "",
             "  d              : %d  (%.1f KB, TAM tutulur)"
             % (self.d, self.d * 16 / 1024),
             "  lifler         : %s" % (self.ayar.lif,),
             "  yığın          : %d" % self.B,
             "  norm hatası    : %.3e" % self.norm_hatasi(),
             "  entropi (kesit): %.6f" % o["entropi"],
             "  vurulan kapı   : %d" % self._kapi,
             "  sadakat log    : %.1f  (kesme yok → tam sıfır)"
             % self.sadakat_log(),
             "", "  SEKTÖRLER (eski küllî alanların yerine):"]
        for ad, (i, j) in self._sektor.items():
            s.append("    %-9s [%4d–%4d]  ağırlık %.6f"
                     % (ad, i, j, float(np.ravel(o[ad])[0])))
        return "\n".join(s)

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .qyazmac import QuditAyar, QuditYazmac

__all__ = ["QAyar", "QIz", "QYazmac", "MAKAM_ADLARI", "donme",
           "donme_turevi", "donme_dilim", "donme_dilim_turevi",
           "kontrollu_donme", "kontrollu_donme_turevi",
           "faz_z", "degil_x",
           "makam_derecesi", "makam_merdiveni",
           "makam_kubit_manasi", "makam_mertebeleri", "makam_mertebesi"]


@dataclass
class QAyar:

    veri_lifi: int = 16
    yerel_yuva: int = 1
    kartan_acisi: float = 0.2617993877991494
    harman_kademesi: int = 3
    tohum: int = 0
    obek: int = 150000
    yigin: int = 1
    kulli_alanlar: Tuple[Tuple[str, int], ...] = (
        ("makam", 3), ("mizan", 4), ("tenakuz", 2), ("tasdik", 2),
        ("sukut", 1), ("nakz", 2), ("kelam", 4), ("kaide", 12),
        ("orak", 1), ("gaye", 2), ("tertip", 4),
    )
    parametre_genisligi: int = 1
    meleke_olcumu: int = 1
    kaide_basamak: int = 4
    bolge_ac: bool = True
    bolge_asgari: int = 1
    hukum_lifi: int = 256
    lif_yapisi: Optional[Tuple[int, ...]] = (16, 16, 16)
    motor: str = "galois"
    faz_mertebesi: int = 16
    hat: str = "c"
    hat_bandi: int = 0
    sadakat_acik: int = 1
    parite_lifi: int = 2
    tip: object = np.complex128

    @property
    def kulli_yuva(self) -> int:
        return sum(n for _, n in self.kulli_alanlar)


class QIz:

    def __init__(self) -> None:
        self.kapi = 0
        self.kesme = 0.0
        self.defter: List[Tuple[str, str]] = []

    def not_dus(self, meleke: str, mesaj: str = "") -> None:
        self.defter.append((str(meleke), str(mesaj)))


class QYazmac:

    def __init__(self, n_satir: int, ayar: Optional[QAyar] = None) -> None:
        self.ayar = ayar or QAyar()
        a = self.ayar
        assert int(n_satir) >= 1, (
            "bağlam uzunluğu en az bir belirteç olmalı: %r" % (n_satir,))
        sozluk = int(a.veri_lifi)
        assert sozluk >= 2, (
            "veri lifi en az iki seviyeli olmalı: veri_lifi=%d" % sozluk)
        azami = tuple(int(x) for x in (a.lif_yapisi
                                       or (sozluk, a.hukum_lifi)))
        assert int(azami[0]) == sozluk, (
            "ilk lif veri lifidir, sözlükle bir olmalı: %d ≠ %d"
            % (azami[0], sozluk))
        yer_azami = int(np.prod(azami[1:]))
        assert int(n_satir) <= yer_azami, (
            "bağlam azamî hududu aşıyor: %d basamak, basamak başına hadd "
            "%d yer (ferman 2-O)" % (int(n_satir), yer_azami))
        yuva = int(a.kulli_yuva)
        K = 2
        while K * K < int(n_satir) or K * K < yuva:
            K *= 2
        K = min(K, int(math.isqrt(yer_azami)))
        lif = (sozluk, K, K)
        d = int(np.prod(lif))
        assert K * K >= int(n_satir), (
            "yazmaç bağlamı taşımıyor: basamak başına %d yer < bağlam=%d "
            "-- her basamak kendi seviyesini ister (ferman 2-M)"
            % (K * K, int(n_satir)))
        self.y = QuditYazmac(
            QuditAyar(d=d, lif=lif, yigin=int(a.yigin),
                      kulli_alanlar=a.kulli_alanlar,
                      yerel_yuva=int(a.yerel_yuva), tohum=int(a.tohum),
                      tip=a.tip, motor=str(a.motor),
                      faz_mertebesi=int(a.faz_mertebesi),
                      hat=str(a.hat), hat_bandi=int(a.hat_bandi)),
            veri_lifi=int(a.veri_lifi))
        self.iz = self.y.iz
        self.veri = self.y.veri
        self.yerel = self.y.yerel
        self.kulli = self.y.kulli
        self.tek = self.y.tek
        self.cift = self.y.cift
        self.uzak_cift = self.y.uzak_cift
        self.sektor_faz_vur = self.y.sektor_faz_vur
        self.sektor_faz_bagi = self.y.sektor_faz_bagi
        self._alan: Dict[str, Tuple[int, int]] = {
            ad: (self.y.kulli(ad, 0), int(kac))
            for ad, kac in a.kulli_alanlar}

    @property
    def n_satir(self) -> int:
        return int(self.y.n_satir)

    @property
    def veri_yuvasi(self) -> int:
        return int(self.y.veri_yuvasi)

    def yereller(self) -> List[int]:
        return self.y.yereller()

    def not_dus(self, meleke: str, mesaj: str = "") -> None:
        self.y.not_dus(meleke, mesaj)

    @property
    def n(self) -> int:
        return self.y.n

    @property
    def kubit_sayisi(self) -> int:
        return self.y.n

    def taksimat(self) -> Dict[str, Tuple[int, int]]:
        t = {"veri": (0, self.veri_kubiti),
             "yerel": (self.veri_kubiti, self.n_satir)}
        t.update(self._alan)
        return t

    def kulli_bas(self) -> int:
        return self.y.kulli(self.ayar.kulli_alanlar[0][0], 0)

    def bolge_var(self, ad: str) -> bool:
        return ad in self._alan or ad in ("meleke", "veri", "yerel")

    @property
    def veri_kubiti(self) -> int:
        return self.n_satir * self.veri_yuvasi

    @property
    def kulli_yuva(self) -> int:
        return self.ayar.kulli_yuva

    @property
    def meleke_kubiti(self) -> int:
        return self.kulli_yuva

    @property
    def ancilla(self) -> int:
        return 0

    def mpo_esigi(self) -> int:
        return 0

    def bolge_olculeri(self) -> Dict[str, int]:
        return {ad: (j - i) for ad, (i, j) in self.y._sektor.items()}

    def tek_yigin(self, yuvalar, G, baglar=None) -> None:
        self.y.tek_yigin(yuvalar, G, baglar=baglar)

    def kontrollu_tek(self, yuva: int, G_dilim) -> None:
        self.y.kontrollu_tek(yuva, G_dilim)

    def veri_izgara(self, sutun=None, satir=None):
        return self.y.veri_izgara(sutun, satir)

    def cift_yigin(self, sol_yuvalar, G, baglar=None) -> None:
        G = np.asarray(G)
        yuvalar = [int(y) for y in sol_yuvalar]
        m = len(yuvalar)
        if G.ndim == 2:
            G = np.broadcast_to(G, (m,) + G.shape)
        yv = np.asarray(yuvalar, np.int64)
        gec = self.y.gecerli_toplu(yv) & self.y.gecerli_toplu(yv + 1)
        self.y._dusen_kapi += int((~gec).sum())
        cift = self.y.cift
        tekil = (baglar is not None and len(baglar) == m
                 and not isinstance(baglar[0], tuple))
        for idx in np.flatnonzero(gec):
            cift(int(yv[idx]), G[int(idx)],
                 baglar=(baglar[int(idx)] if tekil else baglar))

    def mpo_topla(self, alan: str, acilar=None, duraklar=None, j: int = 0,
                  par=None, olcek: float = 1.0, egim=None, bag=None):
        return self.y.mpo_topla(alan, acilar, duraklar, j, par, olcek,
                                egim, bag)

    def mpo_dagit(self, alan: str, acilar=None, duraklar=None, j: int = 0,
                  par=None, olcek: float = 1.0, egim=None, bag=None):
        return self.y.mpo_dagit(alan, acilar, duraklar, j, par, olcek,
                                egim, bag)

    def kodla(self, E) -> None:
        E = np.asarray(E, float)
        if E.ndim == 2:
            E = E[None]
        sozluk = int(self.ayar.veri_lifi)
        B = self.y.B
        d = int(self.y.d)
        n_sat = int(E.shape[1])
        if E.shape[0] != B:
            E = E[np.arange(B) % E.shape[0]]
        assert sozluk == int(self.y.ayar.lif[0]), (
            "bağlam basamak eksenine yazılır: veri_lifi %d, lif[0] %d -- "
            "ikisi aynı eksen olmalı (ferman 1-M)"
            % (sozluk, int(self.y.ayar.lif[0])))
        Ez = E.reshape(B, n_sat, -1)
        bas = np.argmax(Ez, axis=-1) % sozluk
        dolu = Ez.max(axis=-1) > 0.0
        yer = d // sozluk
        assert n_sat <= yer, (
            "bağlam yazmaca sığmıyor: %d basamak, basamak başına %d yer -- "
            "yazmaç bağlam kadar olmalı (ferman 2-M)" % (n_sat, yer))
        seviye = bas * yer + np.arange(n_sat)[None, :]
        genlik = np.zeros((B, d), float)
        faz = np.zeros((B, d), float)
        yigin = np.repeat(np.arange(B), n_sat)
        sec = dolu.reshape(-1)
        genlik[yigin[sec], seviye.reshape(-1)[sec]] = 1.0
        faz[yigin[sec], seviye.reshape(-1)[sec]] = (
            (-2.0 * math.pi / float(sozluk))
            * (bas.reshape(-1)[sec].astype(float) + 1.0))
        assert bool(dolu.any()), (
            "bağlamın hiçbir basamağı dolu değil -- yazmaca yazacak şey "
            "yok, norm sıfır çıkardı (ferman 5)")
        pq = getattr(self, "pq", None)
        if True:
            if pq is not None:
                self.mahalli.hazirla(n_sat, B)
                self.mahalli.yerlestir(bas, dolu)
                kontrol, bag = pq.temas_kapilari()
                self.mahalli.kapilari_vur(
                    kontrol,
                    pq.rezonans(self.mahalli.koordinat(),
                                int(kontrol.size)),
                    bag)
                self._tohum = (bas, sec, yigin, seviye, B, n_sat, d)
        self.y.psi = genlik.astype(self.y.ayar.tip)
        self.y.normalize()
        self.y.faz(faz)
        self.y.iz.not_dus("kodla", "dolu %d / %d seviye"
                          % (int(dolu.sum() // max(B, 1)), d))

    def intac(self) -> float:
        kan = getattr(self, "kan", None)
        pq = getattr(self, "pq", None)
        tohum = getattr(self, "_tohum", None)
        if kan is None or tohum is None:
            return 0.0
        bas, sec, yigin, seviye, B, n_sat, d = tohum
        m = self.mahalli
        kuresel = m.kuresel_faz()
        yerel = m.faz[:B, :n_sat].mean(axis=-1) + kuresel
        taban = int(self.ayar.veri_lifi)
        yer = d // taban
        cephe = min(int(n_sat), yer - 1)
        aday = np.concatenate(
            [np.repeat(bas, taban, axis=0),
             np.tile(np.arange(taban, dtype=bas.dtype), B)[:, None]],
            axis=1)
        kulli_aday = kan.genlik(
            aday, parametre=pq,
            yerel_faz=np.repeat(yerel, taban)).reshape(B, taban)
        kulli = kulli_aday.sum(axis=1)
        agirlik = (m.genlik[:B, :n_sat] * kulli[:, None]).reshape(-1)
        G = np.zeros((B, d), complex)
        G[yigin[sec], seviye.reshape(-1)[sec]] = agirlik[sec]
        G[:, np.arange(taban) * yer + cephe] = kulli_aday
        self.y.psi = G.astype(self.y.ayar.tip)
        self.y.normalize()
        if self.y.iz.senet_acik:
            no = self.y.iz.kapi_yaz(
                "durum", (), np.asarray(self.y.psi, complex).copy())
            if pq is not None:
                self._kan_bagla(no, pq, bas, taban, yer, cephe, seviye,
                                sec, d)
        return float(kuresel)

    def _kan_bagla(self, no, pq, bas, taban, yer, cephe, seviye,
                   sec, d) -> int:
        kontrol, bag = pq.temas_kapilari()
        if kontrol.size == 0:
            return 0
        n = int(bas.shape[-1])
        w = 2.0 * (bas.astype(float) / float(max(1, pq.taban - 1))) - 1.0
        hedef = pq.rezonans(w.reshape(-1, n), int(kontrol.size))
        w_t = np.take_along_axis(w.reshape(-1, n), hedef,
                                 axis=-1).mean(axis=0)
        dizin = np.unique(np.concatenate(
            [seviye.reshape(-1)[sec],
             np.arange(taban) * yer + cephe]))
        for c in range(int(kontrol.size)):
            katsayi = complex(float(w_t[c]) * (float(bag[c]) + 1j))
            self.y.iz.bag_yaz(
                no, int(pq.d + int(kontrol[c])), 1.0,
                ("köşegen", dizin,
                 np.full(dizin.size, katsayi, complex)))
        return int(kontrol.size)

    def superpozisyon(self, yalniz_veri: bool = False) -> None:
        h = int(np.prod(self.y.ayar.lif[1:]))
        T = self.y.psi.reshape(self.y.B, -1, h).copy()
        T[...] = T.sum(axis=-1, keepdims=True) / np.sqrt(h)
        self.y.psi = T.reshape(self.y.B, self.y.d)
        self.y.normalize()

    def harman(self, kademe: Optional[int] = None, teta=None,
             kulli_dahil: bool = True, par_bas: int = -1,
             olcek: float = 1.0) -> None:
        k = int(kademe if kademe is not None else self.ayar.harman_kademesi)
        acilar = (None if teta is None
                  else np.asarray(teta, float).reshape(-1))
        r = (np.random.default_rng(int(self.ayar.tohum) + 17)
             if acilar is None else None)
        s = 0
        for _ in range(max(1, k)):
            for f, n in enumerate(self.y.ayar.lif):
                if not kulli_dahil and f == len(self.y.ayar.lif) - 1:
                    continue
                for alt in range(max(1, int(n).bit_length() - 1)):
                    if acilar is None:
                        a = float(r.normal(scale=0.1))
                    else:
                        a = float(acilar[s % acilar.size])
                        s += 1
                    c, sn = np.cos(a), np.sin(a)
                    bag = None
                    if acilar is not None and int(par_bas) >= 0:
                        bag = [(int(par_bas) + ((s - 1) % acilar.size),
                                float(olcek),
                                np.array([[-sn, -c], [c, -sn]], complex))]
                    self.y.bit_kapisi(
                        f, alt, np.array([[c, -sn], [sn, c]], complex),
                        bag=bag)

    def alan_degeri(self, ad: str):
        return self.y.alan_degeri(ad)

    def olcumler(self) -> Dict[str, float]:
        return self.y.olcumler()

    def olcumler_yigin(self) -> Dict[str, np.ndarray]:
        return self.y.olcumler_yigin()

    def makam_dagilimi(self) -> np.ndarray:
        return self.y.makam_dagilimi()

    def makam_derece_vektoru(self) -> np.ndarray:
        return self.y.makam_derece_vektoru()

    def makam_mertebe_dagilimi(self, P=None) -> Dict[str, np.ndarray]:
        P = self.makam_dagilimi() if P is None else np.atleast_2d(P)
        n = P.shape[1]
        k = max(1, n // 5)
        return {"m%d" % i: P[:, i * k:(i + 1) * k].sum(axis=1)
                for i in range(min(5, n // max(k, 1)))}

    def blok_dagilimi(self, bas: int, kac: int) -> np.ndarray:
        return self.y.blok_dagilimi(bas, kac)

    def povm(self, yuvalar) -> np.ndarray:
        R = self.y.tekil_yogunluklar(yuvalar)
        return np.stack([np.real(R[..., 1, 1]), np.real(R[..., 0, 1])],
                        axis=-1)

    def beyan(self, sozluk: int = 0, satir: int = 0) -> np.ndarray:
        return self.y.beyan(sozluk)

    def dizi_beyani(self, n: int, sozluk: int = 0) -> np.ndarray:
        return self.y.dizi_beyani(n, sozluk)


MAKAM_ADLARI: Tuple[str, ...] = ("Vehim", "Şek", "Zan", "Zann-ı gālib",
                                 "Yakîn")

def makam_merdiveni(kac: int) -> Tuple[int, ...]:
    n = 1 << int(kac)
    return tuple(k ^ (k >> 1) for k in range(n))

def makam_derecesi(kac: int) -> np.ndarray:
    n = 1 << int(kac)
    return np.arange(n, dtype=float) / max(n - 1, 1)

def makam_mertebesi(derece: float) -> str:
    L = len(MAKAM_ADLARI)
    x = float(min(max(float(derece), 0.0), 1.0))
    return MAKAM_ADLARI[min(int(x * L), L - 1)]


def makam_mertebeleri(kac: int) -> Tuple[str, ...]:
    return tuple(makam_mertebesi(x) for x in makam_derecesi(kac))

def makam_kubit_manasi(kac: int) -> Dict[int, Tuple[int, ...]]:
    merd = makam_merdiveni(kac)
    out: Dict[int, Tuple[int, ...]] = {}
    for b in range(int(kac)):
        vurgu = 1 << (int(kac) - 1 - b)
        out[b] = tuple(k for k, idx in enumerate(merd) if idx & vurgu)
    return out

def donme(teta: float) -> np.ndarray:
    c, s = math.cos(float(teta)), math.sin(float(teta))
    return np.array([[c, -s], [s, c]], dtype=np.float64)

def faz_z() -> np.ndarray:
    return np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.float64)

def degil_x() -> np.ndarray:
    return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.float64)

def donme_dilim(teta) -> np.ndarray:
    t = np.asarray(teta, float).reshape(-1)
    c, s = np.cos(t), np.sin(t)
    G = np.empty((t.size, 2, 2), dtype=np.float64)
    G[:, 0, 0] = c; G[:, 0, 1] = -s
    G[:, 1, 0] = s; G[:, 1, 1] = c
    return G


def donme_dilim_turevi(teta) -> np.ndarray:
    t = np.asarray(teta, float).reshape(-1)
    c, s = np.cos(t), np.sin(t)
    G = np.empty((t.size, 2, 2), dtype=np.float64)
    G[:, 0, 0] = -s; G[:, 0, 1] = -c
    G[:, 1, 0] = c; G[:, 1, 1] = -s
    return G


def donme_turevi(teta: float) -> np.ndarray:
    c, s = math.cos(float(teta)), math.sin(float(teta))
    return np.array([[-s, -c], [c, -s]], dtype=np.float64)


def kontrollu_donme(teta: float) -> np.ndarray:
    R = donme(teta)
    G = np.eye(4, dtype=np.float64)
    G[2:, 2:] = R
    return G


def kontrollu_donme_turevi(teta: float) -> np.ndarray:
    G = np.zeros((4, 4), dtype=np.float64)
    G[2:, 2:] = donme_turevi(teta)
    return G

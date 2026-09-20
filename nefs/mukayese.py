from __future__ import annotations

from enum import IntEnum

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Alem", "alem_kur", "Durum", "GECIS", "Makine",
           "ana_superpozisyon", "cozum_uzayi_ac", "cozum_uzayi_kapat",
           "mantik_filtresi", "mukayese_filtresi", "norm_maskesi",
           "cozum_beyani", "cozum_metni",
           "mukayese_melekesi", "mukayese_melekesi_beyani",
           "mukayese_melekesi_metni",
           "yirtiklari_tertiple",
           "Vecih", "vecihleri_istihrac", "vecih_beyani",
           "vecih_metni", "uyanik_vecihler", "alem_cinsleri",
           "ayniyet_ihtilaf", "tip_tayfi", "kanun_tayfi",
           "vecih_ac", "vecih_kapat", "merakla_coz",
           "omur_beyani", "omur_metni",
           "bargmann", "hipotez_halkasi", "swap_testi", "simplisiyal", "istisna_yeri",
           "choi", "nesnelestir", "spektrum", "hata_payi",
           "zorunlu", "mumkun", "kiplik",
           "mukayese_beyani", "mukayese_metni", "sayac"]

_MELEKE: Dict[str, float] = {
    "çağrı": 0.0, "halka": 0.0, "tenakuz": 0.0, "kısır": 0.0,
    "kopuk": 0.0, "yırtık": 0.0, "istisna": -1.0, "sapma": 0.0,
    "Φ_toplam": 0.0, "Δ_K": 0.0, "hafızaya": 0.0,
    "biriken_yırtık": 0.0, "tertiplenen_yırtık": 0.0,
    "ayniyet": 0.0, "ihtilaf_nispeti": 0.0, "ayrışan_vecih": 0.0,
    "açık": 1.0}


_YIRTIK_DEFTERI: List[Tuple[np.ndarray, np.ndarray]] = []


def yirtiklari_tertiple(hafiza, mahalli=None) -> Dict[str, Any]:
    if hafiza is None or not _YIRTIK_DEFTERI:
        return {"tertip": 0, "biriken": len(_YIRTIK_DEFTERI)}
    say = 0
    while _YIRTIK_DEFTERI:
        a, b = _YIRTIK_DEFTERI.pop()
        hafiza.yeniden_tertiple((a, b), sahit=None, mahalli=mahalli,
                                kapi="yırtık")
        say += 1
    _MELEKE["tertiplenen_yırtık"] += float(say)
    _MELEKE["biriken_yırtık"] = 0.0
    return {"tertip": int(say), "biriken": 0}


def mukayese_melekesi_beyani() -> Dict[str, float]:
    return dict(_MELEKE)


def mukayese_melekesi_metni(b: Optional[Dict[str, float]] = None) -> str:
    d = dict(b or mukayese_melekesi_beyani())
    if not d.get("çağrı"):
        return ("  MUKAYESE MELEKESİ: HİÇ KOŞMADI -- kırmızı "
                "(ferman 2-Ú)")
    return "\n".join([
        "  MUKAYESE MELEKESİ -- NETİCE ÇIKARAN CİNS (ferman 2-Ú)",
        "    Bu meleke durumu EVİRMEZ; içindeki veriden hüküm çıkarır.",
        "    çağrı %d   Bargmann halkası %d   ortalama Δ_K %.6f"
        % (int(d["çağrı"]), int(d["halka"]), d["Δ_K"]),
        "    dağıtık tenakuz (Φ→π) %d · kısırdöngü (Φ→0) %d · kopuk"
        " halka (r=0) %d"
        % (int(d["tenakuz"]), int(d["kısır"]), int(d["kopuk"])),
        "    SORİTES YIRTIĞI: %s   istisna köşe %d   sapma %.6f rad"
        % ("VAR" if d["yırtık"] else "yok", int(d["istisna"]),
           d["sapma"]),
        "    simplisiyal Φ toplamı %.6f rad   (n'li = (n−2) üçgenin"
        " bileşkesi)" % d["Φ_toplam"],
        "    netice hafızaya %d defa yazıldı; biriken yırtık %d,"
        " küme kapanışında tertiplenen %d"
        % (int(d["hafızaya"]), int(d.get("biriken_yırtık", 0)),
           int(d.get("tertiplenen_yırtık", 0))),
        "    Tertip her mizan çağrısında değil, KÜME KAPANINCA koşar.",
        "    -- netice bir sayı değil,",
        "    hafızaya kaydolan bir HÜKÜMDÜR.   (ölçü %s)"
        % ("açık" if d.get("açık") else "KAPALI"),
    ])


_VECIH: Dict[str, float] = {
    "istihraç": 0.0, "mertebe": 0.0, "münasebet": 0.0, "vecih": 0.0,
    "taşıyan_ağırlık": 0.0, "âlem": 0.0, "halka": 0.0, "cins": 0.0,
    "tip": 0.0, "kanun": 0.0, "açık": 1.0}


_TIP_TAYFI: Dict[str, float] = {}


def tip_tayfi() -> Dict[str, float]:
    return dict(_TIP_TAYFI)


_SAYAC: Dict[str, int] = {"bargmann": 0, "swap": 0, "spektrum": 0,
                          "hata_payı": 0, "nesne": 0, "choi": 0}


def sayac() -> Dict[str, int]:
    return dict(_SAYAC)


_ZAT_ADI = "zât"


@dataclass(frozen=True)
class Vecih:

    ad: str
    izdusum: Optional[Callable[[np.ndarray], np.ndarray]] = None
    agirlik: float = 1.0
    alem: str = ""
    mertebe: int = 0
    tasiyici: str = ""
    kaide: Tuple[Tuple[str, float], ...] = ()
    tayf: Tuple[Tuple[int, str, float], ...] = ()

    def kaidesi(self, ad: str) -> float:
        for k, v in self.kaide:
            if k == ad:
                return float(v)
        raise AssertionError(
            "%r âleminde %r kaidesi yok -- âlemler arasında mahiyet "
            "farkı vardır, bir âlemin kaidesi ötekine tatbik edilemez "
            "(ferman 1-Ğ)" % (self.alem, ad))

    def gor(self, x: np.ndarray) -> np.ndarray:
        v = np.asarray(x, complex).reshape(-1)
        if self.izdusum is None:
            return v
        u = np.asarray(self.izdusum(v), complex).reshape(-1)
        return u


def _izdusum(temel: np.ndarray) -> Callable[[np.ndarray], np.ndarray]:
    t = np.asarray(temel, complex).reshape(-1)
    def _f(v: np.ndarray) -> np.ndarray:
        return t * complex(np.vdot(t, v))
    return _f


def _mertebe_nispetleri(M: np.ndarray) -> List[Tuple[int, str, float]]:
    G = M @ M.conj().T
    ortusme = np.abs(G) ** 2
    disi = ortusme[~np.eye(ortusme.shape[0], dtype=bool)]
    fs_varyans = float(np.var(disi)) if disi.size else 0.0
    fark = float(np.mean(np.abs(np.diff(M, axis=0)) ** 2)) if M.shape[0] > 1 else 0.0
    m = M.shape[0]
    ucgen = 0.0
    if m >= 3:
        ucgen = float(np.mean([
            abs(complex(np.vdot(M[a], M[b])) * complex(np.vdot(M[b], M[c]))
                * complex(np.vdot(M[c], M[a])))
            for a in range(min(m, 6)) for b in range(a + 1, min(m, 6))
            for c in range(b + 1, min(m, 6))])) if m >= 3 else 0.0
    simetrisizlik = float(np.mean(np.abs(G - G.conj().T)))
    P = G / max(float(np.abs(np.trace(G)).real), 1e-300)
    Q = P
    evvel = float(np.linalg.norm(Q @ Q - Q))
    out: List[Tuple[int, str, float]] = [
        (0, "nokta", float(1.0 / (1.0 + fs_varyans))),
        (1, "uzay", float(fark / (1.0 + fark))),
        (2, "tip", float(1.0 / (1.0 + evvel))),
        (3, "kategori", float(ucgen * (1.0 + simetrisizlik))),
    ]
    k = 4
    while k < 3 + max(2, M.shape[0]):
        Q = Q @ P
        artik = float(np.linalg.norm(Q @ Q - Q))
        if not (artik < evvel - float(np.finfo(float).eps)):
            break
        out.append((k, "postnikov", float(1.0 / (1.0 + artik))))
        evvel = artik
        k += 1
    return out


def _tayf(M: np.ndarray) -> Tuple[Tuple[int, str, float], ...]:
    n = _mertebe_nispetleri(M)
    top = float(sum(max(0.0, x[2]) for x in n))
    if top <= 0.0:
        return tuple((int(l), str(a), 0.0) for l, a, _ in n)
    return tuple((int(l), str(a), float(max(0.0, v) / top))
                 for l, a, v in n)


def _tayf_adi(tayf: Tuple[Tuple[int, str, float], ...]) -> str:
    return str(max(tayf, key=lambda x: x[2])[1])


_KAIDE_ADLARI = ("tip.hudut", "tip.temas",
                 "kategori.korunum", "kategori.çekirdek",
                 "uzay.dönüşüm", "uzay.casimir")

_MERTEBE_KANUNLARI = (
    ("tip", ("tip.hudut", "tip.temas")),
    ("kategori", ("kategori.korunum", "kategori.çekirdek")),
    ("uzay", ("uzay.dönüşüm", "uzay.casimir")))

_KANUN_TAYFI: Dict[str, float] = {}


def kanun_tayfi() -> Dict[str, float]:
    return dict(_KANUN_TAYFI)


def _alem_adi(kaide: Tuple[Tuple[str, float], ...], tur: str,
              olcek: Dict[str, float]) -> str:
    d = dict(kaide)
    tutan = [mert for mert, adlar in _MERTEBE_KANUNLARI
             if any(float(d[ad]) > float(olcek.get(ad, 0.0))
                    for ad in adlar)]
    return "%s.%s" % (tur, "-".join(tutan) if tutan else "serbest")


def _yoneda(M: np.ndarray, a: int, b: int) -> Tuple[float, float,
                                                    List[int]]:
    ya = M.conj() @ M[a]
    yb = M.conj() @ M[b]
    na = float(np.linalg.norm(ya))
    nb = float(np.linalg.norm(yb))
    if na <= 1e-300 or nb <= 1e-300:
        return 0.0, 0.0, []
    hudut = float(np.clip(
        1.0 - abs(complex(np.vdot(ya, yb)) / (na * nb)) ** 2, 0.0, 1.0))
    ag = np.abs(ya) * np.abs(yb)
    temas = float(np.clip(float(ag.sum()) / (na * nb), 0.0, 1.0))
    olcu = float(np.median(ag)) if ag.size else 0.0
    dokunan = [int(k) for k in range(M.shape[0])
               if k != a and k != b and float(ag[k]) > olcu]
    return hudut, temas, dokunan


def _kohomoloji(M: np.ndarray, a: int, b: int, sahit: Sequence[int]
                ) -> Tuple[float, float, List[int]]:
    s = [int(k) for k in sahit]
    if not s:
        return 0.0, 0.0, []
    c = complex(np.vdot(M[a], M[b]))
    hol = np.asarray([
        c * complex(np.vdot(M[b], M[k])) * complex(np.vdot(M[k], M[a]))
        for k in s], complex)
    faz = np.asarray([float(np.angle(z)) if abs(z) > 0.0 else 0.0
                      for z in hol], float)
    korunum = float(abs(complex(np.mean(np.exp(1j * faz)))))
    sap = np.abs(faz)
    olcu = float(np.median(sap))
    cekirdek = [int(s[i]) for i in range(len(s))
                if float(sap[i]) <= olcu]
    nispet = float(len(cekirdek)) / float(len(s))
    return korunum, nispet, (cekirdek or s)


_SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], complex)
_SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], complex)

_EVRIM_DEFTERI: Dict[int, np.ndarray] = {}


def _tasiyici_evrim(aci: float) -> np.ndarray:
    cozunurluk = math.sqrt(float(np.finfo(float).eps))
    k = int(round(float(aci) / cozunurluk))
    U = _EVRIM_DEFTERI.get(k)
    if U is None:
        from kuantum.devre import evrim
        U = evrim(_SIGMA_Y, _SIGMA_X, k * cozunurluk)
        _EVRIM_DEFTERI[k] = U
    return U


def evrim_defteri() -> Dict[str, float]:
    return {"ayrı_açı": float(len(_EVRIM_DEFTERI))}


def _lie_casimir(M: np.ndarray, a: int, b: int, cekirdek: Sequence[int]
                 ) -> Tuple[float, float]:
    c = [int(k) for k in cekirdek] or [a, b]
    e1 = M[a]
    t = M[b] - complex(np.vdot(e1, M[b])) * e1
    n = float(np.linalg.norm(t))
    if n <= 1e-300:
        return 0.0, 0.0
    e2 = t / n
    aci = float(math.acos(float(np.clip(
        abs(complex(np.vdot(M[a], M[b]))), 0.0, 1.0))))
    U = _tasiyici_evrim(aci)
    tasinma: List[float] = []
    bloch = np.zeros(3, float)
    say = 0
    for k in c:
        al = complex(np.vdot(e1, M[k]))
        be = complex(np.vdot(e2, M[k]))
        agir = float(abs(al) ** 2 + abs(be) ** 2)
        if agir <= 1e-300:
            continue
        z = np.asarray([al, be], complex) / math.sqrt(agir)
        w = U @ z
        tasinma.append(float(np.clip(
            1.0 - abs(complex(np.vdot(z, w))) ** 2, 0.0, 1.0)))
        bloch += np.asarray([
            2.0 * float(np.real(np.conj(al) * be)),
            2.0 * float(np.imag(np.conj(al) * be)),
            float(abs(al) ** 2 - abs(be) ** 2)], float) / agir
        say += 1
    if not say:
        return 0.0, 0.0
    donusum = float(np.mean(tasinma))
    casimir = float(np.clip(
        float(np.linalg.norm(bloch)) / float(say), 0.0, 1.0))
    return donusum, casimir


def _kanunlar(M: np.ndarray, a: int, b: int
              ) -> Tuple[Tuple[str, float], ...]:
    hudut, temas, dokunan = _yoneda(M, a, b)
    korunum, cekirdek_nispeti, cekirdek = _kohomoloji(M, a, b, dokunan)
    donusum, casimir = _lie_casimir(M, a, b, cekirdek)
    return (("tip.hudut", hudut), ("tip.temas", temas),
            ("kategori.korunum", korunum),
            ("kategori.çekirdek", cekirdek_nispeti),
            ("uzay.dönüşüm", donusum), ("uzay.casimir", casimir))


def _munasebetler(M: np.ndarray) -> List[Dict[str, Any]]:
    m = int(M.shape[0])
    out: List[Dict[str, Any]] = []
    for a in range(m):
        for b in range(a + 1, m):
            t = M[a] - complex(np.vdot(M[b], M[a])) * M[b]
            n = float(np.linalg.norm(t))
            if n <= 1e-300:
                continue
            out.append({
                "çift": (int(a), int(b)),
                "yön": t / n,
                "kaide": _kanunlar(M, a, b)})
    return out


def _imza_olcegi(V: np.ndarray) -> np.ndarray:
    orta = np.median(V, axis=0)
    sap = np.median(np.abs(V - orta), axis=0)
    genlik = np.max(np.abs(V), axis=0)
    olcek = np.where(sap > 0.0, sap, genlik)
    return np.where(olcek > 0.0, olcek, 1.0)


def vecihleri_istihrac(durumlar: Sequence[np.ndarray]
                       ) -> Tuple[Vecih, ...]:
    D = [np.asarray(x, complex).reshape(-1) for x in durumlar]
    assert D, "vecih istihracı için en az bir durum lâzım"
    boy = min(x.size for x in D)
    M = _normalize(np.stack([x[:boy] for x in D]))
    mun = _munasebetler(M)
    assert mun, (
        "diziden tek münasebet dahi çıkmadı -- bütün kutuplar aynı "
        "noktada, mukayese edilecek bir şey yok (ferman 1-Ğ)")
    V = np.asarray([[v for _, v in r["kaide"]] for r in mun], float)
    olcek = _imza_olcegi(V)
    olcek_adli = {ad: float(olcek[i])
                  for i, ad in enumerate(_KAIDE_ADLARI)}
    obek: Dict[Tuple[int, ...], List[int]] = {}
    for i in range(V.shape[0]):
        imza = tuple(int(round(float(V[i, j] / olcek[j])))
                     for j in range(V.shape[1]))
        obek.setdefault(imza, []).append(i)
    out: List[Vecih] = []
    top_agir = 0.0
    for imza, idx in obek.items():
        kutup = sorted({k for i in idx for k in mun[i]["çift"]})
        Mo = M[kutup] if len(kutup) >= 2 else M
        tayf = _tayf(Mo)
        tur = _tayf_adi(tayf)
        mertebe = int(max(tayf, key=lambda x: x[2])[0])
        yon = np.zeros(boy, complex)
        for i in idx:
            yon = yon + np.asarray(mun[i]["yön"], complex)
        nrm = float(np.linalg.norm(yon))
        if nrm <= 1e-300:
            continue
        yon = yon / nrm
        orta = np.median(V[idx, :], axis=0)
        kaide = tuple((ad, float(orta[j]))
                      for j, ad in enumerate(_KAIDE_ADLARI))
        alem = _alem_adi(kaide, tur, olcek_adli)
        agir = float(np.sum(V[idx, 0]))
        top_agir += agir
        out.append(Vecih(
            "ℓ%d.%s.%s" % (mertebe, alem,
                           ".".join(str(x) for x in imza)),
            _izdusum(yon), agir, alem=alem, mertebe=int(mertebe),
            tasiyici=("∞-kategori" if mertebe >= 3 else
                      "∞-tip" if mertebe == 2 else
                      "uzay" if mertebe == 1 else "nokta"),
            kaide=kaide, tayf=tayf))
    assert out, (
        "münasebetler tartıldı fakat tek vecih neşet etmedi -- her "
        "münasebetin ayırt edici yönü söndü (ferman 1-Ğ)")
    out.sort(key=lambda v: -v.agirlik)
    esit = bool(top_agir <= 0.0)
    pay = (float(len(out)) if esit else top_agir)
    out = [Vecih(v.ad, v.izdusum,
                 float((1.0 if esit else v.agirlik) / pay),
                 alem=v.alem, mertebe=v.mertebe,
                 tasiyici=v.tasiyici, kaide=v.kaide, tayf=v.tayf)
           for v in out]
    _TIP_TAYFI.clear()
    _KANUN_TAYFI.clear()
    for v in out:
        for l, ad, nis in v.tayf:
            k = "ℓ%d.%s" % (int(l), str(ad))
            _TIP_TAYFI[k] = _TIP_TAYFI.get(k, 0.0) + float(
                nis * v.agirlik)
        for ad, nis in v.kaide:
            _KANUN_TAYFI[str(ad)] = _KANUN_TAYFI.get(str(ad), 0.0) + (
                float(nis) * float(v.agirlik))
    _VECIH["kanun"] = float(len(_KANUN_TAYFI))
    _VECIH["tip"] = float(sum(
        1 for x in _TIP_TAYFI.values()
        if x > 0.0))
    _VECIH["istihraç"] += 1.0
    _VECIH["münasebet"] = float(len(mun))
    _VECIH["mertebe"] = float(max(v.mertebe for v in out))
    _VECIH["vecih"] = float(len(out))
    _VECIH["taşıyan_ağırlık"] = float(sum(v.agirlik for v in out))
    _VECIH["âlem"] = float(len({v.alem for v in out}))
    return tuple(out)


_ZAT = Vecih(_ZAT_ADI, None)


def vecih_beyani() -> Dict[str, float]:
    return dict(_VECIH)


def vecih_metni(b: Optional[Dict[str, float]] = None) -> str:
    d = dict(b or vecih_beyani())
    if not d.get("istihraç"):
        return "  VECİH İSTİHRACI: HİÇ KOŞMADI -- kırmızı (ferman 1-Ğ)"
    return "\n".join([
        "  VECİH -- ∞-KATEGORİDEN NEŞET (ferman 1-Ğ, 2-Ú)",
        "    Elle yazılmış vecih listesi KESİLDİ; küllî matris ameliyesi",
        "    (eigh/svd) de KESİLDİ: vecih MÜNASEBETİN KAİDESİNDEN neşet",
        "    eder -- ikili bağ, faz ve üçgenin Φ'si bir imza verir,",
        "    aynı imzalı münasebetler bir ÂLEM teşkil eder.",
        "    istihraç %d   tartılan münasebet %d   neşet eden vecih %d"
        % (int(d["istihraç"]), int(d.get("münasebet", 0)),
           int(d["vecih"])),
        "    taşınan ağırlık %.6f   en üst h-mertebe ℓ=%d"
        % (d["taşıyan_ağırlık"], int(d["mertebe"])),
        "    Her vecih BİR ÂLEM taşır; ayrı âlem %d, taşıyıcı yapı"
        " ölçülerek seçilir" % int(d.get("âlem", 0)),
        "    (nokta · uzay · ∞-tip · ∞-KATEGORİ -- en umumî sonuncusudur,",
        "    ferman 2-Ā: kategori tipten daha umumîdir).",
        "    SORGU KANONİKTİR (ferman 2-Ú-E): öğrenilmez, dışarıdan da",
        "    gelmez. Kaide bir KANUNLAR MANZUMESİDİR ve üç usul, sırayla,",
        "    üçü birden koşar -- her biri bir evvelkinin neticesini alır:",
        "      1 YONEDA      Hom(−,Y) dış münasebet → hudut kanunları",
        "      2 KOHOMOLOJİ  δ∘δ=0 iç doku      → korunum kanunları",
        "      3 LIE/CASIMIR dinamik            → dönüşüm kanunları",
        "    doğan kanun %d -- ağırlıkla tartılmış nispetleri:"
        % int(d.get("kanun", 0)),
        "      " + ("  ".join(
            "%s %.4f" % (k, v) for k, v in
            sorted(kanun_tayfi().items(), key=lambda x: -x[1]))
            or "yok"),
        "    Tutmayan kanun gizlenmez: nispetiyle kırmızı yanar.",
        "    Bargmann halkası: BÜTÜN BOYLAR BERABER, tartılan halka %d"
        % int(d.get("halka", 0)),
        "    Mukayese halkası ÂLEME göre kapanır: ayrı cins %d"
        % int(d.get("cins", 0)),
        "    TİP ÇORBASI ÇÖKERTİLMEDİ (ferman 2-Ú-B): argmax ile tek",
        "    mertebe seçilmiyor, bütün tipler süperpozisyonda tartılıyor.",
        "    çözümlenen tip %d -- nispetleriyle:" % int(d.get("tip", 0)),
        "      " + ("  ".join(
            "%s %.4f" % (k, v) for k, v in
            sorted(tip_tayfi().items(), key=lambda x: -x[1]))
            or "yok"),
        "    Mertebede TAVAN YOKTUR: Postnikov kulesi artık sönmedikçe",
        "    ℓ+1 açılır.   (ölçü %s)"
        % ("açık" if d.get("açık") else "KAPALI"),
    ])


def _normalize(V: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(V, axis=-1, keepdims=True)
    return V / np.maximum(n, 1e-300)


def uyanik_vecihler(durumlar: Sequence[np.ndarray],
                    vecihler: Optional[Sequence[Vecih]] = None,
                    taban: float = 0.0) -> List[Vecih]:
    D = [np.asarray(x, complex).reshape(-1) for x in durumlar]
    assert D, "mukayese için en az bir durum lâzım"
    vs = list(vecihler if vecihler is not None
              else vecihleri_istihrac(D))
    eps = float(np.finfo(np.asarray(D[0]).dtype).eps
                if np.iscomplexobj(D[0]) else np.finfo(float).eps)
    had = float(taban) if float(taban) > 0.0 else math.sqrt(eps)
    canli: List[Vecih] = []
    for v in vs:
        M = _normalize(np.stack([v.gor(x) for x in D]))
        if not np.all(np.isfinite(M)):
            continue
        ayirt = 0.0
        for a in range(M.shape[0]):
            for b in range(a + 1, M.shape[0]):
                ayirt = max(ayirt, 1.0 - float(
                    abs(complex(np.vdot(M[a], M[b])))) ** 2)
        if ayirt > had:
            canli.append(v)
    return canli


_OMUR: Dict[str, float] = {
    "ateşleme": 0.0, "doğan": 0.0, "kapanan": 0.0, "netice": 0.0,
    "sönük_ateşleme": 0.0, "açık": 1.0}

_ACIK_VECIH: List[Vecih] = []


def omur_beyani() -> Dict[str, float]:
    b = dict(_OMUR)
    b["açık_kalan"] = float(b["doğan"] - b["kapanan"])
    return b


def omur_metni(b: Optional[Dict[str, float]] = None) -> str:
    d = dict(b or omur_beyani())
    if not d.get("ateşleme"):
        return ("  VECİH ÖMRÜ: MERAK HİÇ ATEŞLENMEDİ -- kırmızı "
                "(ferman 2-Ú-D)")
    return "\n".join([
        "  VECİH ÖMRÜ -- MOTORUN ANA MEKANİZMASI (ferman 2-Ú-D)",
        "    Vecih bir rapor kalemi değildir: model suale cevabı",
        "    AÇTIĞI VECİHLERİN İÇİNDE arar, netice alınınca kapatır.",
        "    merak ateşlemesi %d   (sönük %d)   doğan vecih %d"
        % (int(d["ateşleme"]), int(d.get("sönük_ateşleme", 0)),
           int(d["doğan"])),
        "    alınan netice %d   kapanan vecih %d   AÇIK KALAN %d"
        % (int(d["netice"]), int(d["kapanan"]),
           int(d.get("açık_kalan", 0))),
        "    Açık kalan SIFIR olmalıdır: kapanmayan vecih, saftirikçe",
        "    bekleyen vecihtir.   (ölçü %s)"
        % ("açık" if d.get("açık") else "KAPALI"),
    ])


def vecih_ac(durumlar: Sequence[np.ndarray],
             merak: Sequence[int]) -> Tuple[Vecih, ...]:
    _OMUR["ateşleme"] += 1.0
    D = [np.asarray(x, complex).reshape(-1) for x in durumlar]
    if not list(merak) or len(D) < 2 or not _OMUR.get("açık"):
        _OMUR["sönük_ateşleme"] += 1.0
        return ()
    vs = vecihleri_istihrac(D)
    _ACIK_VECIH.extend(vs)
    _OMUR["doğan"] += float(len(vs))
    return vs


def vecih_kapat(vecihler: Sequence[Vecih]) -> int:
    say = 0
    for v in list(vecihler):
        if v in _ACIK_VECIH:
            _ACIK_VECIH.remove(v)
        say += 1
    _OMUR["kapanan"] += float(say)
    return int(say)


def merakla_coz(durumlar: Sequence[np.ndarray], merak: Sequence[int],
                amel: Callable[[Tuple[Vecih, ...]], Any]) -> Any:
    vs = vecih_ac(durumlar, merak)
    try:
        netice = amel(vs)
    finally:
        vecih_kapat(vs)
    _OMUR["netice"] += 1.0
    assert not _ACIK_VECIH, (
        "%d vecih açık kaldı -- doğan vecih netice alınınca KAPANIR "
        "(ferman 2-Ú-D)" % len(_ACIK_VECIH))
    return netice


def ayniyet_ihtilaf(a: np.ndarray, b: np.ndarray,
                    vecihler: Sequence[Vecih],
                    hafiza=None) -> Dict[str, Any]:
    from .hafiza import CERH, TASDIK, TEVAKKUF
    vs = list(vecihler)
    assert vs, (
        "ayniyet/ihtilaf tayini için vecih lâzım -- şahit yoktur, "
        "hüküm VECİHLERDEN okunur (ferman 2-Ú)")
    ortusme: Dict[str, float] = {}
    for v in vs:
        ortusme[v.ad] = float(swap_testi(a, b, v)["örtüşme"])
    d = np.asarray(list(ortusme.values()), float)
    ihtilaf = float(d.max() - d.min())
    ittifak = float(1.0 - ihtilaf)
    asgari = float(d.min())
    tenakuz = bool(ihtilaf > ittifak)
    kisir = bool(not tenakuz and asgari >= ittifak)
    _MELEKE["ayniyet"] += 1.0
    _MELEKE["ihtilaf_nispeti"] = ihtilaf
    if tenakuz:
        _MELEKE["ayrışan_vecih"] = float(len(
            [x for x in d if x < d.max() - 0.5 * ihtilaf]))
    hukum = (TEVAKKUF if (tenakuz or kisir) else TASDIK)
    if hafiza is not None:
        hafiza.yaz(np.asarray(a, complex).reshape(-1),
                   omega=float(1.0 - ihtilaf),
                   hukum=(CERH if tenakuz else hukum))
        _MELEKE["hafızaya"] += 1.0
    return {"örtüşme": ortusme, "ihtilaf": ihtilaf, "ittifak": ittifak,
            "asgarî_örtüşme": asgari, "tenakuz": tenakuz,
            "kısır": kisir, "kayıt": float(hukum),
            "en_ayrık": (max(ortusme, key=lambda k: ortusme[k])
                         if ortusme else ""),
            "en_yakın": (min(ortusme, key=lambda k: ortusme[k])
                         if ortusme else "")}


def alem_cinsleri(durumlar: Sequence[np.ndarray],
                  vecihler: Optional[Sequence[Vecih]] = None
                  ) -> List[str]:
    D = [np.asarray(x, complex).reshape(-1) for x in durumlar]
    assert D, "âlem tayini için en az bir hâl lâzım"
    vs = list(vecihler if vecihler is not None
              else vecihleri_istihrac(D))
    assert vs, "hiç vecih neşet etmedi -- âlem tayin edilemez"
    out: List[str] = []
    for h in D:
        agir = [float(np.linalg.norm(v.gor(h))) for v in vs]
        out.append(str(vs[int(np.argmax(agir))].alem))
    _VECIH["cins"] = float(len(set(out)))
    return out


def bargmann(durumlar: Sequence[np.ndarray],
             vecih: Optional[Vecih] = None) -> Dict[str, Any]:
    _SAYAC["bargmann"] += 1
    v = vecih or _ZAT
    D = [v.gor(x) for x in durumlar]
    n = len(D)
    assert n >= 2, "mukayese en az iki kutup ister"
    M = _normalize(np.stack(D))
    carpim = complex(1.0)
    baglar: List[float] = []
    for k in range(n):
        c = complex(np.vdot(M[k], M[(k + 1) % n]))
        baglar.append(float(abs(c)))
        carpim *= c
    r = float(abs(carpim))
    fi = float(np.angle(carpim)) if r > 0.0 else 0.0
    kopuk = bool(min(baglar) <= float(np.finfo(float).eps))
    takla = float(abs(fi) / math.pi)
    kapanis = float(1.0 - takla)
    return {"vecih": v.ad, "n": int(n), "Δ": carpim, "r": r, "Φ": fi,
            "bağ": baglar, "kopuk": kopuk,
            "takla_nispeti": takla, "kapanış_nispeti": kapanis,
            "tenakuz": bool(not kopuk and takla > kapanis),
            "kısır": bool(not kopuk and kapanis > takla
                          and r >= float(np.mean(baglar)))}


def hipotez_halkasi(haller: Sequence[np.ndarray],
                    cinsler: Optional[Sequence[str]] = None,
                    vecih: Optional[Vecih] = None) -> Dict[str, Any]:
    H = [np.asarray(h, complex).reshape(-1) for h in haller]
    ad = ([str(c) for c in cinsler] if cinsler is not None
          else ["hepsi"] * len(H))
    assert len(ad) == len(H), (
        "hipotez sayısı %d, cins sayısı %d -- hâl ile cins ayrışmış"
        % (len(H), len(ad)))
    grup: Dict[str, List[int]] = {}
    for i, c in enumerate(ad):
        grup.setdefault(c, []).append(i)
    dokum: Dict[str, Any] = {}
    toplam = 0.0
    halka = ten = kis = kop = 0
    for c, idx in sorted(grup.items()):
        if len(idx) < 3:
            continue
        b = bargmann([H[i] for i in idx], vecih)
        d = (float(1.0 - float(b["r"])) + float(bool(b["tenakuz"]))
             + float(bool(b["kısır"])) + float(bool(b["kopuk"])))
        dokum[c] = {"hipotez": len(idx), "r": float(b["r"]),
                    "Φ": float(b["Φ"]), "tenakuz": bool(b["tenakuz"]),
                    "kısır": bool(b["kısır"]), "kopuk": bool(b["kopuk"]),
                    "Δ_K": float(d)}
        toplam += d
        halka += 1
        ten += int(bool(b["tenakuz"]))
        kis += int(bool(b["kısır"]))
        kop += int(bool(b["kopuk"]))
    return {"Δ_K": (toplam / halka) if halka else 0.0, "halka": int(halka),
            "tenakuz": int(ten), "kısır": int(kis), "kopuk": int(kop),
            "grup": dokum}


def mukayese_melekesi(haller: Sequence[np.ndarray],
                      cinsler: Optional[Sequence[str]] = None,
                      hafiza=None, mahalli=None,
                      vecih: Optional[Vecih] = None) -> Dict[str, Any]:
    from .hafiza import CERH, TEVAKKUF
    H = [np.asarray(h, complex).reshape(-1) for h in haller]
    assert H, "mukayese melekesine BOŞ hâl yığını geldi"
    _MELEKE["çağrı"] += 1.0
    if not _MELEKE.get("açık") or len(H) < 3:
        return {"kayıp": 0.0, "halka": 0, "yırtık": False,
                "istisna": None, "sapma": 0.0, "Φ_toplam": 0.0,
                "grup": {}}
    cins = (list(cinsler) if cinsler is not None
            else alem_cinsleri(H))
    hlk = hipotez_halkasi(H, cins, vecih)
    ist = istisna_yeri(H, vecih)
    sim = simplisiyal(H, vecih)
    _MELEKE["halka"] = float(hlk["halka"])
    _MELEKE["tenakuz"] = float(hlk["tenakuz"])
    _MELEKE["kısır"] = float(hlk["kısır"])
    _MELEKE["kopuk"] = float(hlk["kopuk"])
    _MELEKE["Δ_K"] = float(hlk["Δ_K"])
    _MELEKE["Φ_toplam"] = float(sim["Φ_toplam"])
    _MELEKE["yırtık"] = float(bool(ist["yırtık"]))
    _MELEKE["istisna"] = float(
        -1 if ist["istisna"] is None else int(ist["istisna"]))
    _MELEKE["sapma"] = float(ist["sapma"])
    if hafiza is not None and ist["istisna"] is not None:
        j = int(ist["istisna"]) % len(H)
        hafiza.yaz(H[j], omega=float(np.cos(float(ist["sapma"]))),
                   hukum=(CERH if ist["yırtık"] else TEVAKKUF))
        _MELEKE["hafızaya"] += 1.0
    if ist["yırtık"] and ist["istisna"] is not None:
        j = int(ist["istisna"]) % len(H)
        _YIRTIK_DEFTERI.append((H[j], H[(j + 1) % len(H)]))
        _MELEKE["biriken_yırtık"] = float(len(_YIRTIK_DEFTERI))
    return {"kayıp": float(hlk["Δ_K"]), "halka": int(hlk["halka"]),
            "yırtık": bool(ist["yırtık"]), "istisna": ist["istisna"],
            "sapma": float(ist["sapma"]),
            "Φ_toplam": float(sim["Φ_toplam"]),
            "tenakuz": int(hlk["tenakuz"]), "kısır": int(hlk["kısır"]),
            "kopuk": int(hlk["kopuk"]), "grup": hlk["grup"]}


def swap_testi(a: np.ndarray, b: np.ndarray,
               vecih: Optional[Vecih] = None) -> Dict[str, Any]:
    _SAYAC["swap"] += 1
    v = vecih or _ZAT
    M = _normalize(np.stack([v.gor(a), v.gor(b)]))
    c = complex(np.vdot(M[0], M[1]))
    ortusme = float(abs(c) ** 2)
    return {"vecih": v.ad, "örtüşme": ortusme,
            "fark": float(0.5 * (1.0 - ortusme)),
            "faz": float(np.angle(c)) if abs(c) > 0.0 else 0.0,
            "ayniyet": bool(ortusme >= 1.0 - 1e-9),
            "dik": bool(ortusme <= 1e-12)}


def simplisiyal(durumlar: Sequence[np.ndarray],
                vecih: Optional[Vecih] = None) -> Dict[str, Any]:
    v = vecih or _ZAT
    D = [v.gor(x) for x in durumlar]
    n = len(D)
    assert n >= 3, "simplisiyal ayrışım en az üç kutup ister"
    M = _normalize(np.stack(D))
    ucgen: List[Dict[str, Any]] = []
    toplam = 0.0
    for k in range(1, n - 1):
        c = (complex(np.vdot(M[0], M[k]))
             * complex(np.vdot(M[k], M[k + 1]))
             * complex(np.vdot(M[k + 1], M[0])))
        f = float(np.angle(c)) if abs(c) > 0.0 else 0.0
        toplam += f
        ucgen.append({"köşe": (0, k, k + 1), "r": float(abs(c)), "Φ": f})
    kalan = float((toplam + math.pi) % (2.0 * math.pi) - math.pi)
    return {"vecih": v.ad, "üçgen": ucgen, "Φ_toplam": kalan,
            "üçgen_sayısı": len(ucgen)}


def istisna_yeri(durumlar: Sequence[np.ndarray],
                 vecih: Optional[Vecih] = None) -> Dict[str, Any]:
    s = simplisiyal(durumlar, vecih)
    ucgen = s["üçgen"]
    if not ucgen:
        return {"vecih": s["vecih"], "istisna": None, "sapma": 0.0}
    sapma = [abs(float(u["Φ"])) for u in ucgen]
    i = int(np.argmax(sapma))
    ort = float(np.median(sapma))
    return {"vecih": s["vecih"], "üçgen": ucgen,
            "istisna": int(ucgen[i]["köşe"][1]),
            "sapma": float(sapma[i]), "ortanca_sapma": ort,
            "yırtık": bool(sapma[i] > 3.0 * max(ort, 1e-12))}


def choi(kanal: np.ndarray) -> Dict[str, Any]:
    _SAYAC["choi"] += 1
    E = np.asarray(kanal, complex)
    assert E.ndim == 2 and E.shape[0] == E.shape[1], (
        "Choi için kare bir kanal dizeyi lâzım")
    d = int(E.shape[0])
    v = E.reshape(-1) / math.sqrt(d)
    rho = np.outer(v, v.conj())
    iz = float(np.real(np.trace(rho)))
    return {"ρ": rho, "d": d, "iz": iz,
            "saflık": float(np.real(np.trace(rho @ rho)))}


def nesnelestir(netice: Dict[str, Any], boy: int) -> np.ndarray:
    _SAYAC["nesne"] += 1
    boy = max(2, int(boy))
    v = np.zeros(boy, complex)
    r = float(netice.get("r", 0.0))
    fi = float(netice.get("Φ", 0.0))
    baglar = [float(x) for x in (netice.get("bağ") or [r])]
    for i, b in enumerate(baglar[:boy]):
        v[i] = b * np.exp(1j * fi * (i + 1) / max(1, len(baglar)))
    if not np.any(np.abs(v) > 0.0):
        v[0] = 1.0
    return v / np.linalg.norm(v)


def spektrum(Y: Sequence[np.ndarray],
             vecihler: Optional[Sequence[Vecih]] = None,
             tohum: int = 0) -> Dict[str, Any]:
    _SAYAC["spektrum"] += 1
    D = [np.asarray(x, complex).reshape(-1) for x in Y]
    m = len(D)
    assert m >= 2, "spektrum en az iki kutup ister"
    canli = uyanik_vecihler(D, vecihler)
    halkalar: List[Dict[str, Any]] = []
    _VECIH["halka"] = 0.0
    for v in canli:
        for n in range(2, m + 1):
            _VECIH["halka"] += 1.0
            idx = [(int(tohum) + k) % m for k in range(n)]
            o = bargmann([D[i] for i in idx], v)
            o["indis"] = idx
            if o["kopuk"]:
                continue
            halkalar.append(o)
    return {"vecih": [v.ad for v in canli],
            "uyanık_vecih": len(canli), "aday_vecih": len(
                list(vecihler if vecihler is not None
                     else vecihleri_istihrac(Y))),
            "halka": halkalar, "halka_sayısı": len(halkalar),
            "tenakuz": sum(1 for h in halkalar if h["tenakuz"]),
            "kısır": sum(1 for h in halkalar if h["kısır"]),
            "en_kuvvetli": (max(halkalar, key=lambda h: h["r"])
                            if halkalar else None)}


def hata_payi(adlar: Sequence[str], artik: Sequence[float]
              ) -> Dict[str, Any]:
    _SAYAC["hata_payı"] += 1
    a = np.asarray(list(artik), float).reshape(-1)
    assert a.size == len(adlar), (
        "hata vektörü %d, ad %d -- bileşen kayboldu" % (a.size, len(adlar)))
    top = float(np.abs(a).sum())
    if top <= 0.0:
        return {"pay": {}, "açı": {}, "toplam": 0.0, "hâkim": None,
                "hâkim_payı": 0.0}
    birim = a / top
    kutup = np.zeros_like(a)
    kutup[int(np.argmax(np.abs(a)))] = 1.0
    aci: Dict[str, float] = {}
    pay: Dict[str, float] = {}
    for i, ad in enumerate(adlar):
        pay[str(ad)] = float(birim[i])
        e = np.zeros_like(a)
        e[i] = 1.0
        s = swap_testi(a.astype(complex), e.astype(complex))
        aci[str(ad)] = float(math.acos(
            float(np.clip(math.sqrt(max(s["örtüşme"], 0.0)), -1.0, 1.0))))
    h = int(np.argmax(np.abs(a)))
    return {"pay": pay, "açı": aci, "toplam": top,
            "hâkim": str(adlar[h]), "hâkim_payı": float(abs(birim[h])),
            "dağılım": float(-np.sum(
                np.abs(birim)[np.abs(birim) > 0]
                * np.log(np.abs(birim)[np.abs(birim) > 0])))}


def zorunlu(onerme: np.ndarray, sahitler: Sequence[np.ndarray],
            vecihler: Optional[Sequence[Vecih]] = None) -> Dict[str, Any]:
    return kiplik(onerme, sahitler, vecihler)["zorunlu"]


def mumkun(onerme: np.ndarray, sahitler: Sequence[np.ndarray],
           vecihler: Optional[Sequence[Vecih]] = None) -> Dict[str, Any]:
    return kiplik(onerme, sahitler, vecihler)["mümkün"]


def kiplik(onerme: np.ndarray, sahitler: Sequence[np.ndarray],
           vecihler: Optional[Sequence[Vecih]] = None) -> Dict[str, Any]:
    _SAYAC["kiplik"] = _SAYAC.get("kiplik", 0) + 1
    S = [np.asarray(x, complex).reshape(-1) for x in sahitler]
    assert S, "kiplik için en az bir şahit dünya lâzım"
    canli = uyanik_vecihler(S + [np.asarray(onerme, complex).reshape(-1)],
                            vecihler)
    dunya: Dict[str, float] = {}
    for v in canli:
        en = 0.0
        for w in S:
            en = max(en, float(swap_testi(onerme, w, v)["örtüşme"]))
        dunya[v.ad] = en
    if not dunya:
        return {"dünya": {}, "zorunlu": {"doğru": False, "nispet": 0.0},
                "mümkün": {"doğru": False, "nispet": 0.0},
                "erişilen": 0}
    d = np.asarray(list(dunya.values()), float)
    eps = math.sqrt(float(np.finfo(float).eps))
    tutan = d > eps
    return {"dünya": dunya, "erişilen": int(len(dunya)),
            "zorunlu": {"doğru": bool(np.all(tutan)),
                        "nispet": float(d.min())},
            "mümkün": {"doğru": bool(np.any(tutan)),
                       "nispet": float(d.max())}}


def mukayese_beyani(spek: Optional[Dict[str, Any]] = None,
                    hata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"sayaç": sayac(), "spektrum": spek, "hata": hata}


def mukayese_metni(o: Dict[str, Any]) -> str:
    s = ["  MUKAYESE MOTORU (nefs/mukayese.py) -- çok vazifeli uzuv"]
    c = o.get("sayaç") or {}
    s.append("    çağrı: " + "  ".join("%s %d" % (k, v)
                                       for k, v in sorted(c.items())))
    sp = o.get("spektrum")
    if sp:
        s += ["    VECİH SPEKTRUMU (mertebe = hangi vecihten bakıldığı):",
              "      uyanık vecih : %d / %d   (%s)"
              % (sp["uyanık_vecih"], sp["aday_vecih"],
                 ", ".join(sp["vecih"]) or "yok"),
              "      halka        : %d   tenakuz %d   kısır %d"
              % (sp["halka_sayısı"], sp["tenakuz"], sp["kısır"])]
        e = sp.get("en_kuvvetli")
        if e:
            s.append("      en kuvvetli  : %s  n=%d  r=%.4f  Φ=%+.4f"
                     % (e["vecih"], e["n"], e["r"], e["Φ"]))
    h = o.get("hata")
    if h and h.get("pay"):
        ust = sorted(h["pay"].items(), key=lambda x: -abs(x[1]))[:5]
        s += ["    HATA PAYI VE AÇISI (ferman 1-V'nin vektörü üstünde):",
              "      hâkim bileşen: %s  (%%%.2f)"
              % (h["hâkim"], 100.0 * h["hâkim_payı"]),
              "      dağılım (entropi): %.4f  -- 0'a yakın = tek kefe "
              "her şeyi yiyor" % h.get("dağılım", 0.0),
              "      " + "  ".join("%s %%%.1f∠%.2f"
                                   % (k, 100.0 * v, h["açı"].get(k, 0.0))
                                   for k, v in ust)]
    return "\n".join(s)


def _kategori_evreni() -> int:
    _FOCK_SAYAC["kategori_denetimi"] += 1.0
    return int(denetle_tip(kategori_tipi(), _BAGLAM))


def _mertebe_tutuyor_mu(r: int, n: int) -> bool:
    _FOCK_SAYAC["mertebe_denetimi"] += 1.0
    try:
        denetle_t(rn_sarti(Deg("A"), int(r), int(n)), Evren(0), _BAGLAM)
        return True
    except Exception:
        return False


def _esbiçim(V: np.ndarray) -> np.ndarray:
    L = np.log(np.abs(V) + float(np.finfo(float).tiny))
    return (L - L.mean(axis=1, keepdims=True)
            - L.mean(axis=0, keepdims=True) + L.mean())


def _bileske_artigi(V: np.ndarray) -> float:
    L = np.log(np.abs(V) + float(np.finfo(float).tiny))
    pay = float(np.linalg.norm(_esbiçim(V)))
    payda = float(np.linalg.norm(L - L.mean()))
    return float(pay / payda) if payda > 0.0 else 0.0


def _morfizm_mertebesi(V: np.ndarray) -> Tuple[int, Tuple[float, ...]]:
    kule: List[float] = []
    W = np.asarray(V, float)
    evvel = float("inf")
    n = -1
    for _ in range(int(max(2, min(W.shape[0], 16)))):
        if W.shape[0] < 2 or not np.isfinite(W).all():
            break
        art = _bileske_artigi(W)
        kule.append(art)
        if not (art < evvel - float(np.finfo(float).eps)):
            break
        evvel = art
        n += 1
        R = _esbiçim(W)
        W = np.abs(R @ R.T)
        np.fill_diagonal(W, 0.0)
    return int(max(-1, n)), tuple(kule)


def _nesne_mertebesi(V: np.ndarray) -> Tuple[int, int]:
    W = np.asarray(V, float)
    if W.shape[0] < 2:
        return 0, 0
    nrm = np.linalg.norm(W, axis=1, keepdims=True)
    nrm[nrm == 0.0] = 1.0
    B = W / nrm
    G = np.abs(B @ B.T)
    np.fill_diagonal(G, 0.0)
    ayni = int(np.count_nonzero(G >= 1.0 - float(np.sqrt(
        np.finfo(float).eps)))) // 2
    r = 0
    kalan = ayni
    while kalan > 0 and r < len(MERTEBE_ADI) - 1:
        r += 1
        kalan //= 2
    return int(r), int(ayni)


@dataclass(frozen=True)
class Alem:

    ad: str
    r: int
    n: int
    evren: int
    tutuyor: bool
    bileske_artigi: float
    ozdes_cift: int
    kule: Tuple[float, ...]

    def beyan(self) -> Dict[str, Any]:
        return {"âlem": self.ad, "r": int(self.r), "n": int(self.n),
                "evren": int(self.evren), "tutuyor": bool(self.tutuyor),
                "bileşke_artığı": float(self.bileske_artigi),
                "özdeş_çift": int(self.ozdes_cift),
                "kule": [float(x) for x in self.kule],
                "kule_boyu": len(self.kule)}


def alem_kur(V: np.ndarray) -> Alem:
    W = np.abs(np.asarray(V, float))
    n, kule = _morfizm_mertebesi(W)
    r, ayni = _nesne_mertebesi(W)
    while n >= 0 and not _mertebe_tutuyor_mu(r, n):
        n -= 1
    a = Alem(ad=rn_adi(r, n), r=int(r), n=int(n),
             evren=_kategori_evreni(),
             tutuyor=bool(n >= 0 and _mertebe_tutuyor_mu(r, n)),
             bileske_artigi=(float(kule[0]) if kule else 0.0),
             ozdes_cift=int(ayni), kule=kule)
    _SON_ALEM.clear()
    _SON_ALEM.update(a.beyan())
    return a


class Durum(IntEnum):

    VAKUM = 0
    SINIR = 1
    MESELE = 2
    UZAY = 3
    SUZULMUS = 4
    HUKUM = 5
    INTAC = 6


GECIS: Dict[Durum, Tuple[Durum, ...]] = {
    Durum.VAKUM: (Durum.SINIR,),
    Durum.SINIR: (Durum.MESELE,),
    Durum.MESELE: (Durum.UZAY, Durum.INTAC),
    Durum.UZAY: (Durum.SUZULMUS,),
    Durum.SUZULMUS: (Durum.HUKUM,),
    Durum.HUKUM: (Durum.UZAY, Durum.INTAC),
    Durum.INTAC: (),
}

_MAKINE_SAYACI: Dict[str, float] = {
    "geçiş": 0.0, "açılan": 0.0, "kapanan": 0.0, "maske": 0.0,
    "geri_yol": 0.0, "mesele_var": 0.0, "mesele_yok": 0.0,
    "tersi_yok": 0.0, "faz_çevirme": 0.0, "mercek": 0.0,
    "pergel": 0.0, "kök": 0.0}

_SON: Dict[str, Any] = {}


class Makine:

    __slots__ = ("durum", "izlek", "maskeli", "acik")

    def __init__(self) -> None:
        self.durum = Durum.VAKUM
        self.izlek: List[Durum] = [Durum.VAKUM]
        self.maskeli: set = set()
        self.acik = 0

    def gec(self, hedef: Durum) -> "Makine":
        assert hedef in GECIS[self.durum], (
            "YASAK DURUM GEÇİŞİ: %s → %s. Müsaade edilen: %s. Durum "
            "makinesinin geçiş tablosu delinemez (ferman 2-Æ)."
            % (self.durum.name, hedef.name,
               ", ".join(d.name for d in GECIS[self.durum]) or "yok"))
        self.durum = hedef
        self.izlek.append(hedef)
        _MAKINE_SAYACI["geçiş"] += 1.0
        return self

    def beyan(self) -> Dict[str, Any]:
        return {"durum": self.durum.name,
                "izlek": [d.name for d in self.izlek],
                "adım": len(self.izlek) - 1,
                "maskeli_jeton": len(self.maskeli),
                "açık_uzay": int(self.acik)}


def _entropi_gradyani(hal: np.ndarray) -> Tuple[np.ndarray, float]:
    P = np.abs(np.asarray(hal, complex).reshape(-1)) ** 2
    top = float(P.sum())
    assert top > 0.0, (
        "hâlin normu sıfır -- sınır şartı boş bir dalgaya vidalanamaz")
    P = P / top
    H = -P * np.log(P + float(np.finfo(float).tiny))
    return H, float(H.sum())


def _kanun_nispetleri() -> Dict[str, float]:
    from .mukayese import kanun_tayfi
    k = kanun_tayfi()
    assert k, (
        "kanun tayfı BOŞ -- yeni uzayın kaideleri okunamaz. Kaide "
        "elle yazılamaz (ferman 2-Ú-E, 6).")
    return {str(a): float(v) for a, v in k.items()}


def _hal_kur(baglam: Sequence[Sequence[int]], nefs, taban: int
             ) -> np.ndarray:
    from .qegitim import belirtecleri_kodla
    diz = [int(x) for o in baglam for x in list(o)]
    assert diz, "bağlam BOŞ -- sınır şartı yok demektir"
    from .nqs import turun_genligi
    E = belirtecleri_kodla(diz, int(taban), int(taban))
    q = nefs.idrak_et(E)
    return np.asarray(turun_genligi(nefs, q).hal, complex).reshape(-1)


def ana_superpozisyon(baglam: Sequence[Sequence[int]], nefs=None,
                      hafiza=None, sozluk: int = 0, pencere: int = 0,
                      taban: int = 0, basamak: int = 0,
                      makine: Optional[Makine] = None) -> Dict[str, Any]:
    assert nefs is not None, (
        "ana süperpozisyon motorsuz kurulamaz -- kâide cebriyle sual "
        "üretmek yasaktır (ferman 6)")
    m = makine or Makine()
    m.gec(Durum.SINIR)
    hal = _hal_kur(baglam, nefs, int(taban))
    H, toplam = _entropi_gradyani(hal)
    kanun = _kanun_nispetleri()
    en_zayif = min(kanun.items(), key=lambda x: x[1])
    mesele = float(1.0 - float(en_zayif[1]))
    boy = int(sum(len(list(o)) for o in baglam))
    aranan = int(np.argmax(H))
    ters_var = bool(np.isfinite(hal).all()
                    and float(np.linalg.norm(hal)) > 0.0)
    if not ters_var:
        _MAKINE_SAYACI["tersi_yok"] += 1.0
    m.gec(Durum.MESELE)
    if mesele > float(np.mean(list(kanun.values()))):
        _MAKINE_SAYACI["mesele_var"] += 1.0
        var = True
    else:
        _MAKINE_SAYACI["mesele_yok"] += 1.0
        var = False
    return {"makine": m, "hal": hal, "mesele": var,
            "mesele_nispeti": float(mesele),
            "en_zayıf_kanun": str(en_zayif[0]),
            "kaideler": kanun,
            "entropi": float(toplam),
            "aranan_basamak": aranan,
            "geri_yol_var": ters_var,
            "pencere": int(min(int(pencere), max(1, boy))),
            "boy": boy, "sözlük": int(sozluk), "taban": int(taban),
            "basamak": int(basamak)}


def cozum_uzayi_ac(sual: Dict[str, Any], nefs=None, hafiza=None,
                   fock=None) -> Dict[str, Any]:
    m: Makine = sual["makine"]
    if not sual["mesele"]:
        m.gec(Durum.INTAC)
        return {"makine": m, "açık": False, "hal": sual["hal"],
                "F": None, "sual": sual, "kayıt": []}
    assert sual["geri_yol_var"], (
        "FUNKTÖRÜN TERSİ YOK -- uzay AÇILMAZ. Açılırsa ana hâle "
        "dönülemez ve orada biriken idrak kaybolur (ferman 1-Ç).")
    m.gec(Durum.UZAY)
    m.acik += 1
    _MAKINE_SAYACI["açılan"] += 1.0
    klon = np.array(sual["hal"], complex, copy=True)
    kaide = sual["kaideler"]
    aci = math.pi * float(sual["mesele_nispeti"])
    kok = np.exp(1j * aci * np.linspace(0.0, 1.0, klon.size))
    F = kok
    klon = klon * F
    if fock is not None:
        for ad, v in kaide.items():
            fock.yarat("kaide.%s" % ad, entropi=float(v),
                       butce=float(sual["boy"]),
                       celiski=float(sual["mesele_nispeti"]))
    return {"makine": m, "açık": True, "hal": klon, "F": F,
            "sual": sual, "kayıt": []}


def mantik_filtresi(uzay: Dict[str, Any]) -> Dict[str, Any]:
    from .mukayese import bargmann
    m: Makine = uzay["makine"]
    if not uzay["açık"]:
        return uzay
    psi = np.asarray(uzay["hal"], complex).reshape(-1)
    n = psi.size
    E = np.zeros(n, complex)
    E[int(np.argmax(np.abs(psi)))] = 1.0
    o = bargmann([psi, E, psi - complex(np.vdot(E, psi)) * E])
    takla = float(o["takla_nispeti"])
    kapanis = float(o["kapanış_nispeti"])
    ihlal = ("tenakuz" if takla > kapanis else
             "kısırdöngü" if kapanis >= 1.0 - float(np.finfo(float).eps)
             else "")
    if ihlal:
        psi = psi - 2.0 * complex(np.vdot(E, psi)) * E
        _MAKINE_SAYACI["faz_çevirme"] += 1.0
    uzay["hal"] = psi
    uzay["kayıt"].append({"süzgeç": "mantık", "ihlâl": ihlal or "yok",
                          "takla": takla, "kapanış": kapanis,
                          "Φ": float(o["Φ"]), "r": float(o["r"])})
    m.gec(Durum.SUZULMUS)
    return uzay


def mukayese_filtresi(uzay: Dict[str, Any], hafiza=None,
                      mahalli=None) -> Dict[str, Any]:
    from .mukayese import bargmann
    if not uzay["açık"]:
        return uzay
    psi = np.asarray(uzay["hal"], complex).reshape(-1)
    kutup: List[np.ndarray] = [psi]
    if hafiza is not None:
        for k in sorted(getattr(hafiza, "kayitlar", []) or [],
                        key=lambda k: -float(getattr(k, "mu", 0.0)))[:2]:
            v = np.zeros(psi.size, complex)
            x = np.asarray(k.x, complex).reshape(-1)[:psi.size]
            v[:x.size] = x
            if float(np.linalg.norm(v)) > 0.0:
                kutup.append(v)
    if len(kutup) < 2:
        uzay["kayıt"].append({"süzgeç": "mukayese", "kutup": len(kutup),
                              "sebep": "kıyas kutbu yok", "r": 1.0,
                              "Φ": 0.0})
        return uzay
    o = bargmann(kutup)
    r = float(o["r"])
    fi = float(o["Φ"])
    beta = float(1.0 - r)
    psi = psi * math.exp(-beta)
    nrm = float(np.linalg.norm(psi))
    assert nrm > 0.0, "mukayese merceği dalgayı tamamen söndürdü"
    psi = psi / nrm
    _MAKINE_SAYACI["mercek"] += 1.0
    kok_adi = "mukayese.Φ%+.3f" % fi
    if mahalli is not None:
        mahalli.cartan_ekle(kok_adi, fi)
        _MAKINE_SAYACI["kök"] += 1.0
    d = psi.size
    psi = psi * np.exp(1j * fi * np.arange(d) / max(1, d - 1))
    _MAKINE_SAYACI["pergel"] += 1.0
    uzay["hal"] = psi
    uzay["kayıt"].append({"süzgeç": "mukayese", "kutup": len(kutup),
                          "r": r, "Φ": fi, "mercek_β": beta,
                          "kök": kok_adi})
    return uzay


def norm_maskesi(uzay: Dict[str, Any], jeton: int) -> Dict[str, Any]:
    m: Makine = uzay["makine"]
    psi = np.asarray(uzay["hal"], complex).reshape(-1)
    norm = float(np.vdot(psi, psi).real)
    kapali = bool(norm <= float(np.finfo(float).eps))
    if kapali:
        assert int(jeton) not in m.maskeli, (
            "JETON %d İKİNCİ DEFA MASKELENİYOR -- geri yol kısırdöngüye "
            "girdi (ferman 1-I: kısırdöngü kat'î huduttur)" % int(jeton))
        m.maskeli.add(int(jeton))
        _MAKINE_SAYACI["maske"] += 1.0
        _MAKINE_SAYACI["geri_yol"] += 1.0
    return {"norm": norm, "kapalı": kapali,
            "ceza": (-math.inf if kapali else 0.0),
            "maskeli": sorted(m.maskeli)}


def cozum_uzayi_kapat(uzay: Dict[str, Any], sual: Dict[str, Any],
                      hamiltonyen=None) -> Dict[str, Any]:
    m: Makine = uzay["makine"]
    psi = np.asarray(uzay["hal"], complex).reshape(-1)
    if uzay["açık"]:
        F = uzay["F"]
        assert F is not None, (
            "uzay açık fakat funktör kaydedilmemiş -- geri çevrim "
            "imkânsız (ferman 1-Ç)")
        psi = psi * np.conj(F)
        m.acik -= 1
        _MAKINE_SAYACI["kapanan"] += 1.0
        m.gec(Durum.HUKUM)
        m.gec(Durum.INTAC)
    assert m.acik == 0, (
        "AÇIK KALAN UZAY VAR (%d) -- saftirikçe bekleyen vecih "
        "kusurdur (ferman 2-Ú-D)" % m.acik)
    pencere = int(sual["pencere"])
    hafiza_kapasitesi = int(max(1, round(float(sual["entropi"])
                                         * float(len(sual["kaideler"])))))
    if hamiltonyen is not None:
        hamiltonyen.kefelerden({
            "artık_adı": ("uzay", "tip", "kategori"),
            "artık": np.array([float(sual["mesele_nispeti"]),
                               float(sual["entropi"]),
                               float(pencere)], float),
            "ham_artık": np.array([1.0, 1.0, 1.0], float)})
    o = {"pencere": pencere,
         "hafıza_kapasitesi": hafiza_kapasitesi,
         "hal": psi,
         "mesele": bool(sual["mesele"]),
         "mesele_nispeti": float(sual["mesele_nispeti"]),
         "en_zayıf_kanun": sual["en_zayıf_kanun"],
         "aranan_basamak": int(sual["aranan_basamak"]),
         "süzgeç": list(uzay["kayıt"]),
         "beyan": m.beyan()}
    _SON.clear()
    _SON.update({k: v for k, v in o.items() if k != "hal"})
    _SON["sayaç"] = dict(_MAKINE_SAYACI)
    return o


def cozum_beyani() -> Dict[str, Any]:
    if _SON:
        return dict(_SON)
    return {"pencere": 0, "hafıza_kapasitesi": 0, "mesele": False,
            "mesele_nispeti": 0.0, "en_zayıf_kanun": "KOŞMADI",
            "aranan_basamak": 0, "süzgeç": [],
            "beyan": {"durum": "KOŞMADI", "izlek": [], "adım": 0,
                      "maskeli_jeton": 0, "açık_uzay": 0},
            "sayaç": dict(_MAKINE_SAYACI)}


def cozum_metni(b: Optional[Dict[str, Any]] = None) -> str:
    d = b if b is not None else cozum_beyani()
    m = dict(d.get("beyan") or {})
    s = dict(d.get("sayaç") or {})
    sz = list(d.get("süzgeç") or [])
    mn = next((x for x in sz if x.get("süzgeç") == "mantık"), {})
    mk = next((x for x in sz if x.get("süzgeç") == "mukayese"), {})
    return "\n".join([
        "  ÇÖZÜM UZAYI -- DURUM MAKİNESİ (ferman 2-Æ, 2-Ý)",
        "    izlek: %s" % (" → ".join(m.get("izlek") or []) or "koşmadı"),
        "    mesele %s (nispet %.6f)   en zayıf kanun: %s"
        % ("VAR" if d.get("mesele") else "yok",
           float(d.get("mesele_nispeti", 0.0)), d.get("en_zayıf_kanun")),
        "    aranan basamak (entropi tepesi) %d   pencere %d   "
        "hafıza kapasitesi %d"
        % (int(d.get("aranan_basamak", 0)), int(d.get("pencere", 0)),
           int(d.get("hafıza_kapasitesi", 0))),
        "",
        "    MANTIK SÜZGECİ -- Z₂, faz çevirme (tek imkân)",
        "      ihlâl: %s   takla %.6f   kapanış %.6f   Φ %+.6f"
        % (mn.get("ihlâl", "koşmadı"), float(mn.get("takla", 0.0)),
           float(mn.get("kapanış", 0.0)), float(mn.get("Φ", 0.0))),
        "      faz çevirme %d kere koştu" % int(s.get("faz_çevirme", 0)),
        "",
        "    MUKAYESE SÜZGECİ -- MAHİYETİ FARKLI (ℝ⁺ × U(1))",
        "      r %.6f → mercek β %.6f   ·   Φ %+.6f → pergel, kök %s"
        % (float(mk.get("r", 0.0)), float(mk.get("mercek_β", 0.0)),
           float(mk.get("Φ", 0.0)), mk.get("kök", "yok")),
        "      mercek %d · pergel %d · açılan Cartan kökü %d"
        % (int(s.get("mercek", 0)), int(s.get("pergel", 0)),
           int(s.get("kök", 0))),
        "",
        "    GERİ YOL -- NORM MASKESİ (ferman 2-Æ/3)",
        "      maskelenen jeton %d   geri dönüş %d   maskeli şu an %d"
        % (int(s.get("maske", 0)), int(s.get("geri_yol", 0)),
           int(m.get("maskeli_jeton", 0))),
        "",
        "    açılan %d / kapanan %d   AÇIK KALAN %d  (sıfır olmalı)"
        % (int(s.get("açılan", 0)), int(s.get("kapanan", 0)),
           int(m.get("açık_uzay", 0))),
        "    geçiş %d   tersi olmadığı için açılmayan uzay %d"
        % (int(s.get("geçiş", 0)), int(s.get("tersi_yok", 0)))])

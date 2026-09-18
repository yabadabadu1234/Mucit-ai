from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["mukayese_melekesi", "mukayese_melekesi_beyani",
           "mukayese_melekesi_metni",
           "yirtiklari_tertiple",
           "Vecih", "vecihleri_istihrac", "vecih_beyani",
           "vecih_metni", "uyanik_vecihler", "alem_cinsleri",
           "ayniyet_ihtilaf", "tip_tayfi", "kanun_tayfi",
           "vecih_ac", "vecih_kapat", "merakla_coz",
           "omur_beyani", "omur_metni",
           "bargmann", "hipotez_halkasi", "swap_testi", "simplisiyal", "istisna_yeri",
           "choi", "nesnelestir", "spektrum", "hata_payi",
           "zorunlu", "mumkun", "kiplik", "paylar_olc",
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
    out: List[Tuple[int, str, float]] = [
        (0, "nokta", float(1.0 / (1.0 + fs_varyans))),
        (1, "uzay", float(fark / (1.0 + fark))),
        (2, "kategori", float(ucgen * (1.0 + simetrisizlik))),
    ]
    P = G / max(float(np.abs(np.trace(G)).real), 1e-300)
    Q = P
    evvel = float(np.linalg.norm(Q @ Q - Q))
    out.append((3, "tip", float(1.0 / (1.0 + evvel))))
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


def _lie_casimir(M: np.ndarray, a: int, b: int, cekirdek: Sequence[int]
                 ) -> Tuple[float, float]:
    c = [int(k) for k in cekirdek] or [a, b]
    e1 = M[a]
    t = M[b] - complex(np.vdot(e1, M[b])) * e1
    n = float(np.linalg.norm(t))
    if n <= 1e-300:
        return 0.0, 0.0
    e2 = t / n
    hiz: List[float] = []
    bloch = np.zeros(3, float)
    say = 0
    for k in c:
        al = complex(np.vdot(e1, M[k]))
        be = complex(np.vdot(e2, M[k]))
        agir = float(abs(al) ** 2 + abs(be) ** 2)
        if agir <= 1e-300:
            continue
        im = float(np.imag(np.conj(be) * al))
        hiz.append(float(np.clip(
            (agir - 4.0 * im * im) / agir, 0.0, 1.0)))
        bloch += np.asarray([
            2.0 * float(np.real(np.conj(al) * be)),
            2.0 * float(np.imag(np.conj(al) * be)),
            float(abs(al) ** 2 - abs(be) ** 2)], float) / agir
        say += 1
    if not say:
        return 0.0, 0.0
    donusum = float(np.mean(hiz))
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
            tasiyici=("∞-tip" if mertebe >= 3 else
                      "∞-kategori" if mertebe == 2 else
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
        "    (uzay · ∞-kategori · ∞-tip).",
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


def paylar_olc(adlar: Sequence[str], artik: Sequence[float]
               ) -> Dict[str, float]:
    _SAYAC["pay"] = _SAYAC.get("pay", 0) + 1
    a = np.asarray(list(artik), float).reshape(-1)
    n = a.size
    assert n == len(adlar), "pay ölçüsü: ad ile artık sayısı tutmuyor"
    if n < 3 or not np.any(np.abs(a) > 0.0):
        return {str(ad): 1.0 / max(n, 1) for ad in adlar}
    E = np.eye(n, dtype=complex)
    v = a.astype(complex)
    rez = np.zeros(n, float)
    for i in range(n):
        halka = [v, E[i], v - complex(np.vdot(E[i], v)) * E[i]]
        if float(np.linalg.norm(halka[2])) <= 1e-300:
            continue
        o = bargmann(halka)
        rez[i] = float(o["r"])
    top = float(rez.sum())
    if top <= 0.0:
        return {str(ad): 1.0 / n for ad in adlar}
    return {str(adlar[i]): float(rez[i] / top) for i in range(n)}


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

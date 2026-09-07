from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Kok", "olcek", "denge", "olcek_beyani", "hiz_yoklamasi"]


@dataclass(frozen=True)
class Kok:

    sozluk: int = 16
    comert: float = 0.5
    tohum: int = 0

    def __post_init__(self) -> None:
        assert int(self.sozluk) >= 2, "sözlük en az iki belirteç olmalı"
        assert 0.0 <= float(self.comert) <= 1.0, (
            "cömertlik [0,1] aralığında olmalı; verilen %r" % (self.comert,))


_HIZ: Dict[Tuple[int, int], float] = {}


def _ikinin_kuvveti(x: float, en_az: int = 1) -> int:
    v = max(float(x), 1.0)
    return int(max(en_az, 1 << int(math.floor(math.log2(v)))))


def _yukari_kuvvet(x: int) -> int:
    v = max(int(x), 1)
    return int(1 << int(math.ceil(math.log2(v))))


def hiz_yoklamasi(d: int, bayt: int = 8, tohum: int = 0) -> float:
    anahtar = (int(d), int(bayt))
    hazir = _HIZ.get(anahtar)
    if hazir is not None:
        return hazir
    import json as _json
    import os as _os
    from .donanim import onbellekler as _ob
    _o = _ob()
    _iz = "%s.%s.%s" % (_o.get("L1d"), _o.get("L2"), _o.get("L3"))
    kutuk = _os.path.join("depo", "olcek_hiz.json")
    if _os.path.exists(kutuk):
        with open(kutuk, encoding="utf-8") as f:
            kayit = _json.load(f)
        v = kayit.get("%d.%d.%s" % (int(d), int(bayt), _iz))
        if v:
            _HIZ[anahtar] = float(v)
            return float(v)
    tip = np.complex64 if int(bayt) == 8 else np.complex128
    B = 8
    r = np.random.default_rng(int(tohum))
    psi = (r.normal(size=(B, int(d))) + 1j * r.normal(size=(B, int(d))))
    psi = np.asarray(psi, tip)
    K = _ikinin_kuvveti(math.sqrt(max(int(d) // 2, 4)), 4)
    G = np.asarray(r.normal(size=(K, K)) + 1j * r.normal(size=(K, K)), tip)
    T = psi.reshape(B, -1, K)
    for _ in range(3):
        T = (T @ G.T).reshape(B, -1, K)
    n = 24
    t0 = time.perf_counter()
    for _ in range(n):
        T = (T @ G.T).reshape(B, -1, K)
    sure = max(time.perf_counter() - t0, 1e-9)
    kapi_sn = float(n * B) / sure
    kapi_yogunlugu = 0.404
    hiz = kapi_sn / kapi_yogunlugu
    assert hiz > 0.0, "hız yoklaması sıfır verdi -- ölçü bir şey ölçmüyor"
    hiz = float(_ikinin_kuvveti(hiz, 1024))
    _HIZ[anahtar] = hiz
    try:
        _os.makedirs("depo", exist_ok=True)
        kayit = {}
        if _os.path.exists(kutuk):
            with open(kutuk, encoding="utf-8") as f:
                kayit = _json.load(f)
        kayit["%d.%d.%s" % (int(d), int(bayt), _iz)] = hiz
        with open(kutuk, "w", encoding="utf-8") as f:
            _json.dump(kayit, f, indent=1)
    except OSError:
        pass
    return hiz


def olcek(kok: Optional[Kok] = None) -> Dict[str, Any]:
    k = kok or Kok()
    from .donanim import cekirdek_sayisi, onbellekler
    from .zihin_durumu import QAyar

    c = float(k.comert)
    bayt = 8
    ob = onbellekler()
    L1 = int(ob.get("L1d") or 32768)
    L2 = int(ob.get("L2") or (1 << 20))
    L3 = int(ob.get("L3") or (32 << 20))

    doluluk = 0.25 + 0.65 * c
    K = _ikinin_kuvveti(math.sqrt(L1 * doluluk / (3.0 * bayt)), 4)
    V = K
    yuva = sum(n for _, n in QAyar.kulli_alanlar)
    while K * K < yuva:
        K *= 2
    hukum = K * K
    d = V * K * K
    from .onbellek import yigin_sec
    tip = np.complex64 if bayt == 8 else np.complex128
    B_tavan = int(yigin_sec(d, tip)["B"])
    B = int(max(1, B_tavan))

    from tanilama.hiz_teftisi import AZAMI_SANIYE
    hiz = hiz_yoklamasi(d, bayt, int(k.tohum))
    butce = float(hiz) * float(AZAMI_SANIYE) * max(c, 1e-3)
    tur = 1 + int(round(8.0 * c))
    yon = 8 + int(round(56.0 * c))
    cagri = max(1, tur * yon)
    kalan = max(butce / float(cagri), 4.0)
    kenar = _ikinin_kuvveti(math.sqrt(kalan), 2)
    from .belirtec import basamak_sayisi as _bs
    _basamak = _bs(int(k.sozluk), V)
    from .musahede import gorev_boyu, sigan_nispet
    _gb = gorev_boyu()
    gereken = int(_gb["azamî"]) * int(_basamak)
    pencere = int(max(V, _ikinin_kuvveti(float(gereken), int(V))))
    sigan = float(sigan_nispet(pencere // max(1, int(_basamak))))
    ornek = int(max(1, min(int(max(kenar, B)),
                           int(butce // (float(cagri) * pencere)))))

    keyf = int(max(2, round(2 + 10 * c)))
    cev = int(max(2, (V // 2) * max(1, int(round(2 * c)))))
    obek = int(max(1, min(B, ornek,
                          max(cev, (ornek * keyf) // max(1, cagri)))))
    kume_sayisi = max(1, cagri // max(1, keyf))
    ornek = int(max(obek, min(ornek, obek * kume_sayisi)))
    genislik = int(max(1, round(1.0 + (K - 1) * c)))
    basamak = _basamak
    return {
        "belirtec_basamak": basamak,
        "parametre_genisligi": genislik,
        "veri_lifi": V, "karo": K, "hukum_lifi": hukum,
        "yigin_dilimi": obek, "keyfiyet_turu": keyf, "obek": obek,
        "ornek_sayisi": ornek, "pencere": pencere,
        "görev_belirteç_azamî": int(_gb["azamî"]),
        "görev_belirteç_ortanca": int(_gb["ortanca"]),
        "görev_sayısı": int(_gb["görev"]),
        "bağlama_sığan_nispet": sigan,
        "talim_tur": tur, "altuzay_ornek": yon,
        "cevrim_sayisi": int(max(2, (V // 2) * max(1, int(round(2 * c))))),
        "degerlendirme_gorevi": int(max(2, round(8 + 112 * c))),
        "dogrulama_sayisi": int(max(4, round(20 + 180 * c))),
        "kademe_gorevi": int(max(1, round(1 + 7 * c))),
        "azami_uret": int(max(8, basamak * int(_gb["hedef_azamî"]))),
        "yaricap": float(1.5 + 2.5 * c),
        "azami_talim_saati": float(AZAMI_SANIYE / 3600.0),
        "galois_us": 8,
        "tableau_n": 64,
        "faz_mertebesi": V,
        "siklotomik_us": 8,
        "flo_modu": int(max(4, 3 * max(2, V // 2))),
        "flo_kapisi": int(max(8, B)),
        "tdd_cekirdek": int(K),
        "stab_mertebe": int(max(2, K // 2)),
        "usul_seferi": int(max(1, max(2, V // 2) // 2)),
        "hafiza_kapasitesi": int(max(16, B)),
        "ayna_tur": int(max(4, K + K // 2)),
        "qudit_qsvt": int(K),
        "qudit_derece": int(max(2, K // 2)),
        "qudit_yon": int(max(2, K // 2)),
        "harman_kademesi": 3,
        "d": d, "L1d": L1, "L2": L2, "L3": L3, "yigin_tavani": B_tavan,
        "doluluk": doluluk, "ölçülen_hız": hiz, "bütçe": butce,
        "çağrı": cagri, "çekirdek": int(cekirdek_sayisi()),
        "belirteç": float(cagri) * ornek * pencere,
    }


PAYLAR: Dict[str, float] = {
    "uzay": 0.22,
    "tip": 0.13,
    "meleke": 0.12,
    "kategori": 0.10,
    "nokta": 0.10,
    "cevrim": 0.09,
    "tenakuz": 0.09,
    "zirh": 0.07,
    "monogami": 0.05,
    "engel": 0.03,
}


def denge(kefeler: Dict[str, float], taban: float = 0.05,
          tavan: float = 8.0,
          artik: Optional[Sequence[float]] = None,
          adlar: Optional[Sequence[str]] = None) -> Dict[str, float]:
    paylar = dict(PAYLAR)
    olculen = False
    if artik is not None and adlar is not None and len(adlar) >= 3:
        from .mukayese import paylar_olc
        ham = paylar_olc(list(adlar), list(artik))
        esle_ad = {"uzay": "uzay", "tip": "tip", "kategori": "kategori",
                   "nokta": "nokta", "cevrim": "çevrim",
                   "tenakuz": "tenakuz", "monogami": "monogami",
                   "engel": "engel"}
        toplu: Dict[str, float] = {}
        for ad, anahtar in esle_ad.items():
            toplu[ad] = float(ham.get(anahtar, 0.0))
        toplu["meleke"] = float(sum(v for k, v in ham.items()
                                    if k.startswith("𝒪")
                                    or k.startswith("alan.")
                                    or k.startswith("kademe.")))
        toplu["zirh"] = float(sum(v for k, v in ham.items()
                                  if k.startswith("zırh.")))
        top = float(sum(toplu.values()))
        if top > 0.0:
            paylar = {k: v / top for k, v in toplu.items()}
            olculen = True
    cipa = float(kefeler.get("rezonans", 0.0))
    pay_u = float(paylar.get("uzay", PAYLAR["uzay"])) or PAYLAR["uzay"]
    o: Dict[str, float] = {}
    frenlenen = []
    esle = {"cevrim": "çevrim", "tenakuz": "tenakuz_bariyer",
            "monogami": "monogami", "engel": "engel", "tip": "hodge",
            "kategori": "kategori", "nokta": "nokta",
            "meleke": "meleke", "zirh": "zırh"}
    esik = max(float(taban) * cipa, 1e-9)
    for ad, anahtar in esle.items():
        v = abs(float(kefeler.get(anahtar, 0.0)))
        nispet = float(paylar.get(ad, PAYLAR[ad])) / pay_u
        if v < esik:
            lam = nispet
            frenlenen.append(ad + "(taban)")
        else:
            lam = nispet * cipa / v
        if lam > nispet * float(tavan):
            lam = nispet * float(tavan)
            frenlenen.append(ad + "(tavan)")
        o["lam_" + ad] = float(lam)
    o["frenlenen"] = frenlenen
    return o


def olcek_beyani(kok: Kok, o: Optional[Dict[str, Any]] = None) -> str:
    d = o or olcek(kok)
    return "\n".join([
        "=== ÖLÇEK -- ÜÇ KÖK, ÜÇ FORMÜL (nefs/olcek.py) ===", "",
        "  KÖK 1  kodlama : tiktoken, sözlük = %d  (ÖLÇÜLDÜ, "
        "elle yazılmadı -- ferman 1-N)" % kok.sozluk,
        "  KÖK 2  cömert  = %.2f    (padişahın tek kabzası)" % kok.comert,
        "  KÖK 3  donanım : L1d %d B | L2 %d B | L3 %d B | %d çekirdek"
        % (d["L1d"], d["L2"], d["L3"], d["çekirdek"]),
        "",
        "  FORMÜL 1 -- YAPI (önbellekten)",
        "    V = K (veri lifi = karo)                 = %d" % d["veri_lifi"],
        "    sözlük (tiktoken'den ÖLÇÜLDÜ)            = %d" % kok.sozluk,
        "    basamak = ⌈log_V(sözlük)⌉                = %d"
        % d["belirtec_basamak"],
        "    3·K²·bayt ≤ L1d·%.2f  →  K              = %d"
        % (d["doluluk"], d["karo"]),
        "    lif = (V, K, K)   hüküm lifi = K²        = %d"
        % d["hukum_lifi"],
        "    d = V·K²                                 = %d" % d["d"],
        "    obek = yığın = min(B_tavan, örnek·keyf/çağrı) = %d  [tavan %d]"
        % (d["yigin_dilimi"], d["yigin_tavani"]),
        "",
        "  FORMÜL 2 -- BÜTÇE (ölçülen hız × süre haddi)",
        "    ölçülen hız (mikro yoklama)              = %.0f belirteç/sn"
        % d["ölçülen_hız"],
        "    bütçe = hız × AZAMİ_SANİYE × cömert      = %.3e belirteç"
        % d["bütçe"],
        "    çağrı = tur × yön = %d × %d              = %d"
        % (d["talim_tur"], d["altuzay_ornek"], d["çağrı"]),
        "    BAĞLAM SUALİ TAŞIR (ferman 1-Ö) -- bütçe artığı DEĞİL:",
        "      ölçülen görev boyu: ortanca %d, azamî %d belirteç "
        "(%d görev)"
        % (d["görev_belirteç_ortanca"], d["görev_belirteç_azamî"],
           d["görev_sayısı"]),
        "      pencere = azamî × basamak, ikinin kuvvetine    = %d"
        % d["pencere"],
        "      bağlama TAM sığan görev nispeti               = %%%.2f"
        % (100.0 * float(d["bağlama_sığan_nispet"])),
        "    örnek (bütçe pencereyi DEĞİL örneği kısar)      = %d"
        % d["ornek_sayisi"],
        "    fiilî yük = çağrı × örnek × pencere      = %.3e belirteç"
        % d["belirteç"],
        "    bütçeye sığdı mı                         : %s"
        % ("evet" if d["belirteç"] <= d["bütçe"] else "HAYIR ⚠"),
        "",
        "  FORMÜL 3 -- DENGE (λ'lar mizanın ilk çağrısından ölçülür)",
        "    söz hakları: %s"
        % "  ".join("%s %.2f" % (a, p) for a, p in sorted(
            PAYLAR.items(), key=lambda x: -x[1])),
        "    toplam pay = %.2f  (1 olmalı)" % sum(PAYLAR.values()),
    ])

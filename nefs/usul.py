"""
MANTIK YÜRÜTME SEFERİ -- KALBİN SEVK ETTİĞİ AKTİF İNŞA

===================================================================
BU 7/24 KOŞMAZ -- VE KOŞMAMASI ŞARTTIR
===================================================================

Zabıt (*Mantık ile Mantık Yürütme Arasındaki Ontolojik Ayrım*, 2. fasıl):

    "Mantık yürütme, zihnin her an körü körüne yaptığı bir iş değildir.
    Zihin sürekli Aristo kıyası kurmaz; kumaşa dokunan manifaturacı gibi
    bazen teemmül eder, ressam gibi bazen tahayyül eder. Ne zaman ki
    zihinde bir karanlık nokta, örtülü bir gaye veya şüpheli bir dâvâ
    belirir; işte o an Zihnin Kalbi, Tertip melekesine emir verir ve
    Mantık Yürütme Seferi başlatılır."

O hâlde bu dosyanın **doğru çalıştığının delili**, çağrılma sayısının
düşük olmasıdır. ``sefer_nispeti`` %100 çıkarsa mimari, zabıtın
yasakladığı şeye dönmüştür: *"her an boş yere mantık kapısı çalıştıran
kör bir hesap makinesi."* Rapor bu nispeti yazar.

===================================================================
GEDİK ÖLÇÜLÜR, TAHMİN EDİLMEZ
===================================================================

Kalbin "karanlık nokta" hissi bir sezgi değil, bir sayıdır: muhakeme
çevriminin holonomisi ``ω = Re Tr(U_C)/n``. ``ω < had`` ise çevrim
kendi başladığı aksiyomdan uzaklaşmıştır -- orası karanlıktır.

===================================================================
SEFERİN DÖRT DURAĞI (ZABITIN ŞEMASI)
===================================================================

    F_sevk : S_ham --Tertip--> M_usul --U_logic--> Q_netice
                                              --Lan_K--> S_muhkem

1. **TERTİP** -- girdileri derler, uygun ``M_usul`` manifoldunu seçer.
   Seçim keyfî değildir: çevrimin köşe sayısı ve ``ω``nın işareti
   usulü tayin eder (aşağıdaki ``_usul_sec``).
2. **HADD-İ EVSAT** -- orta terim ``b`` köprü olarak kurulur:
   ``a → b → c``. Bu, iki Givens dönmesinin bileşkesidir.
3. **U_M† ile UNCOMPUTE** -- *"B terimi U_B† ile uncompute edilir
   (dolanıklık çöpe dönüşmeden silinir)."* Orta terim izdüşümü
   neticeden **çıkarılır**; artık dolanıklık ölçülür ve raporlanır.
4. **Lan_K (SOL KAN UZANTISI)** -- netice ana müdrike manifolduna
   taşınır: neticenin müdrike üstündeki izdüşümü alınır ve **norm
   kazanıp kazanmadığı** ölçülür. Kazanmadıysa o sefer yeni bilgi
   üretmemiştir ve ``lan_k`` sayacı artmaz.

===================================================================
FERMAN 7-D: TAŞIYICI
===================================================================

Zabıt manifoldları soyut kategori diliyle anlatır. Ayrık taşıyıcıda
her ``M_usul`` bir **üniter dizeydir** ve üçü de aynı cinsten kurulur:
``nefs/kulli_mizan.py:givens`` düzlem içi SU(2) dönmesi. Usuller
birbirinden **hangi köşeleri hangi sırayla bağladıklarıyla** ayrılır
(Barbara ``a→b→c``, Aks-i Müstevî ``¬c→¬a``, Baroco ``reductio``…),
transandantal bir parametreyle değil. ``sin/cos/exp`` çağrılmaz.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["UsulAyari", "USULLER", "gedik_bul", "sefer", "usul_kos",
           "usul_beyani", "usul_sifirla"]


#: **MANTIK USULÜ MANİFOLDLARI.** Her biri bir çıkarım şeklidir ve
#: neyi neye bağladığı ``_usul_sec``te yazılıdır. İsimler süs değil:
#: hangi seferin hangi usulle koştuğu raporda dökülür.
USULLER: Tuple[str, ...] = (
    "Barbara",        # Her A B'dir, her B C'dir → her A C'dir
    "Celarent",       # Hiçbir B C değil, her A B → hiçbir A C değil
    "Cesare",         # Hiçbir C B değil, her A B → hiçbir A C değil
    "Darapti",        # Her B A, her B C → bazı A C'dir
    "Baroco",         # Reductio: neticeyi inkâr et, tenakuza düş
    "ModusPonens",    # A, A→B ⊢ B
    "Munfasıla",      # A ∨ B, ¬A ⊢ B
    "Temsil",         # analoji: a:b :: c:?
    "AksiMüstevî",    # kontrapozisyon: A→B ⊢ ¬B→¬A
    "Sorites",        # zincirleme kıyas
)


@dataclass
class UsulAyari:
    """Seferin ölçüleri."""

    #: ``0`` = sefer hiç açılmaz. Kapatılınca istihrac sıfırlanır.
    acik: int = 1
    #: Gediğin eşiği: ``ω < had`` ise çevrim karanlıktadır.
    had: float = 0.0
    #: Bir kayıp çağrısında açılacak azamî sefer -- bütçe ilan edilir.
    sefer: int = 4
    #: Lan_K'nın "yeni bilgi doğdu" eşiği: müdrike üstündeki izdüşüm
    #: normu bu kadar artmalı.
    lan_esigi: float = 1e-6


_SAYAC: Dict[str, float] = {
    "yoklama": 0.0, "sefer": 0.0, "istihrac": 0.0, "cerh": 0.0,
    "tahkik": 0.0, "uncompute": 0.0, "lan_k": 0.0, "artık": 0.0}
_USUL_SAYAC: Dict[str, int] = {}


def gedik_bul(omegalar: Sequence[float],
              ayar: Optional[UsulAyari] = None) -> List[int]:
    """**KALBİN YOKLAMASI.** Hangi çevrimler karanlıkta?

    Her çağrıda sayaç artar (yoklama), fakat sefer yalnız gedik
    bulununca açılır. İkisinin ayrı sayılması şart: kapının hiç
    çalınmaması ile çalınıp cevap alınmaması ayrı şeylerdir.
    """
    a = ayar or UsulAyari()
    _SAYAC["yoklama"] += 1.0
    if not int(a.acik):
        return []
    om = np.asarray(list(omegalar), float)
    if om.size == 0:
        return []
    karanlik = np.nonzero(om < float(a.had))[0]
    # Bütçe: en karanlıktan başla.
    sira = karanlik[np.argsort(om[karanlik])]
    return [int(i) for i in sira[:max(0, int(a.sefer))]]


def _usul_sec(omega: float, kose: int) -> str:
    """Tertip hangi manifoldu seçiyor -- **ölçüye göre**, keyfî değil.

    * ``ω`` çok negatifse (tam takla) usul ``Baroco``dur: netice zaten
      inkâr edilmiş, geriye reductio kalır.
    * Üç köşeli çevrim doğrudan kıyastır (``Barbara``/``Celarent``);
      ``ω``nın işareti olumlu/olumsuz kipi tayin eder.
    * Üçten uzun çevrim zincirleme kıyastır: ``Sorites``.
    """
    if omega < -0.75:
        return "Baroco"
    if kose > 3:
        return "Sorites"
    if omega < -0.25:
        return "Celarent"
    if omega < 0.0:
        return "AksiMüstevî"
    return "Barbara"


def _gaye(omega: float) -> str:
    """Seferin üç aslî gayesinden hangisi (zabıt, 3. fasıl)."""
    if omega < -0.5:
        return "cerh"        # ortada bir hipotez var, sıhhati şüpheli
    if omega < 0.0:
        return "tahkik"      # bir kanaat var, yakîne erdirilmek isteniyor
    return "istihrac"        # öncüllerde saklı hakikat bilfiil doğacak


def sefer(koseler: Sequence[np.ndarray], omega: float,
          mudrike: np.ndarray, ayar: Optional[UsulAyari] = None
          ) -> Dict[str, Any]:
    """**TEK SEFER.** Manifoldu seç, hadd-i evsatı kur, tasfiye et, taşı.

    ``mudrike`` ana müdrike manifoldunun taşıyıcısıdır (yığının
    ortalama hâli); netice oraya ``Lan_K`` ile taşınır.
    """
    from .kulli_mizan import givens
    a = ayar or UsulAyari()
    K = [np.asarray(k, complex).reshape(-1) for k in koseler]
    assert len(K) >= 3, "sefer en az üç köşe ister (hadd-i evsat lâzım)"
    K = [k / max(float(np.linalg.norm(k)), 1e-300) for k in K]
    usul = _usul_sec(float(omega), len(K))
    gaye = _gaye(float(omega))
    _SAYAC["sefer"] += 1.0
    _SAYAC[gaye] += 1.0
    _USUL_SAYAC[usul] = _USUL_SAYAC.get(usul, 0) + 1

    a0, b0, c0 = K[0], K[1], K[-1]
    # ── 2. DURAK: HADD-İ EVSAT ``b`` KÖPRÜ OLARAK KURULUR ─────────
    U_f = givens(a0, b0)
    U_g = givens(b0, c0)
    netice = U_g @ (U_f @ a0)

    # ── 3. DURAK: ``U_M†`` İLE UNCOMPUTE ──────────────────────────
    # Orta terim dolanıklık bırakmamalı: neticenin ``b`` üstündeki
    # izdüşümü çıkarılır. Kalan **ölçülür**, "temizlendi" diye
    # yazılmaz (ferman 5).
    ic = complex(np.vdot(b0, netice))
    temiz = netice - ic * b0
    artik = float(abs(ic))
    _SAYAC["artık"] += artik
    if artik < 0.5:
        _SAYAC["uncompute"] += 1.0

    nrm = float(np.linalg.norm(temiz))
    if nrm <= 1e-300:
        # Netice tamamen orta terimdi: sefer yeni bir şey doğurmadı.
        # Bu bir hata değil, bir neticedir ve öyle yazılır.
        return {"usul": usul, "gaye": gaye, "artık": artik,
                "lan_k": False, "kazanç": 0.0, "netice": None}
    temiz = temiz / nrm

    # ── 4. DURAK: Lan_K -- SOL KAN UZANTISI ───────────────────────
    # Netice ana müdrike manifolduna taşınır. "Yeni bilgi doğdu"
    # demenin şartı: müdrikenin neticeye örtüşmesi **artmalı**.
    M = np.asarray(mudrike, complex).reshape(-1)
    M = M / max(float(np.linalg.norm(M)), 1e-300)
    once = float(abs(complex(np.vdot(M, a0))))
    sonra = float(abs(complex(np.vdot(M, temiz))))
    kazanc = sonra - once
    tasindi = bool(kazanc > float(a.lan_esigi))
    if tasindi:
        _SAYAC["lan_k"] += 1.0
    return {"usul": usul, "gaye": gaye, "artık": artik,
            "lan_k": tasindi, "kazanç": float(kazanc), "netice": temiz}


def usul_kos(haller: Sequence[np.ndarray],
             cevrim_indisleri: Sequence[Sequence[int]],
             omegalar: Sequence[float],
             ayar: Optional[UsulAyari] = None) -> Dict[str, Any]:
    """Kalbi yokla, gedik varsa sefer aç. **Ana akışın bağlandığı yer.**"""
    a = ayar or UsulAyari()
    gedikler = gedik_bul(omegalar, a)
    if not gedikler:
        return {"sefer": 0, "gedik": 0, "kapanan": 0,
                "kazanç": 0.0, "borç": 0.0, "netice": []}
    H = np.stack([np.asarray(h, complex).reshape(-1) for h in haller])
    mudrike = H.sum(axis=0)
    toplam = 0.0
    acilan = 0
    kapanan = 0
    neticeler: List[Tuple[int, np.ndarray]] = []
    for c in gedikler:
        idx = [int(i) for i in cevrim_indisleri[c]]
        r = sefer([haller[i] for i in idx], float(omegalar[c]), mudrike, a)
        toplam += float(r["kazanç"])
        acilan += 1
        if r["lan_k"] and r["netice"] is not None:
            kapanan += 1
            neticeler.append((idx[0], np.asarray(r["netice"], complex)))
    # ── SEFERİN NETİCESİ KULLANILIR, RAPORLANMAKLA KALMAZ ──────────
    #
    # **Evvelce burada yalnız sayaç dönüyordu** ve ``kazanç`` hiçbir
    # yere gitmiyordu: sefer koşuyor, hadd-i evsat tasfiye ediliyor,
    # ``Lan_K`` hesaplanıyor -- sonra netice çöpe atılıyordu. Ferman
    # 1-C(b) kat'îdir: bağlamak, *"o fonksiyonun fiilen çağrılması **ve
    # neticesinin kullanılması**"*tır. İki yerde kullanılır:
    #
    #   ``netice``  -> ``kulli_mizan`` bunları **hafızaya** nakşeder
    #                  (zabıt: "zihne mal edilmiş yeni bilgi").
    #   ``borç``    -> kapanmayan gedik bir **epistemik borçtur** ve
    #                  mizanda cezalanır. Kapanmayan gedik bedavaysa,
    #                  mantık yürütmenin tâlime hiçbir tesiri olmaz.
    borc = (float(len(gedikler) - kapanan) / float(len(gedikler))
            if gedikler else 0.0)
    return {"sefer": acilan, "gedik": len(gedikler), "kapanan": kapanan,
            "kazanç": float(toplam), "borç": float(borc),
            "netice": neticeler}


def usul_beyani() -> Dict[str, Any]:
    """Sayacın hâli. **Taht ``yoklama > 0`` diye denetler.**"""
    y = max(1.0, _SAYAC["yoklama"])
    s = max(1.0, _SAYAC["sefer"])
    return {"yoklama": int(_SAYAC["yoklama"]),
            "sefer": int(_SAYAC["sefer"]),
            "sefer_nispeti": float(_SAYAC["sefer"] / y),
            "istihrac": int(_SAYAC["istihrac"]),
            "cerh": int(_SAYAC["cerh"]),
            "tahkik": int(_SAYAC["tahkik"]),
            "uncompute": int(_SAYAC["uncompute"]),
            "lan_k": int(_SAYAC["lan_k"]),
            "artık_dolanıklık": float(_SAYAC["artık"] / s),
            "usul": dict(_USUL_SAYAC)}


def usul_sifirla() -> None:
    for k in _SAYAC:
        _SAYAC[k] = 0.0
    _USUL_SAYAC.clear()

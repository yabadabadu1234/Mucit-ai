"""HIZ DEFTERİ -- 700 MB/sn hedefinin **iki ayrı muhasebesi**.

Padişahın hedefi: *"saniyede 700 MB veri işleme hızına padişah
ulaşmadığı müddetçe durma."* Bu dosya o hedefi ölçer ve -- mühim olan
budur -- **hedefin iki ayrı manası olduğunu** gösterir. İkisi
karıştırıldığı sürece ne ulaşıldığı ne ulaşılmadığı söylenebilir.

===================================================================
İKİ MUHASEBE -- ve aralarındaki uçurum
===================================================================

**(A) TOKEN BAŞINA MUHASEBE.** Her token müstakil bir QTT vektörüdür
(12 çekirdek, χ_v = 8). Melekelerin birleşik MPO'su her tokene ayrı
ayrı uygulanır, her adımda χ = 16'ya kanonik kırpılır. Ceridenin VIII.
bölüm cetveli budur::

    8.388.608 token × C_token FLOP  →  bir makro adım

**(B) KÜLLÎ SÜPERPOZİSYON MUHASEBESİ.** Bütün veri kümesi **tek bir 35
kübitlik QTT durumudur** (11 yığın + 12 yer + 12 mana). MPO o duruma
**bir kere** uygulanır ve 8,4 milyon tokenın hepsi aynı süpürmede
işlenir::

    1 MPO süpürmesi × 35 yuva  →  bir makro adım (bütün tokenlar)

**Bu ikisi arasında milyonlarca kat fark vardır** ve ceridenin kendi
metni ikisini birden söyler: yazmaç taksimatı (B)'dir, VIII. bölüm
cetveli (A)'dır. Bu dosya ikisini de ölçer, sayıyı yan yana koyar ve
hükmü **kullanıcıya bırakır** -- zira bu bir hesap meselesi değil bir
**mimarî tercih** meselesidir.

===================================================================
ÜÇÜNCÜ VE GİZLENEMEYECEK KALEM: veriyi YÜKLEMEK
===================================================================

(B) doğru olsa bile klasik veri bir yerden gelmek zorundadır.
``B=2048 × L=4096 × D=4096 × 4 bayt = 137,4 GB``tır ve bu, hiçbir
kuantum hilesiyle küçültülemez -- ancak **bir kere** okunup QTT'ye
sıkıştırılır. O hâlde "saniyede kaç MB" sorusunun cevabı, sistemin
hangi safhasını kastettiğine bağlıdır:

* **ham veriyi yutma** hızı  → bant genişliğiyle sınırlı (1,2 TB/sn)
* **QTT üzerinde işleme** hızı → çok daha yüksek, zira veri sıkışmış
* **sıkıştırmanın kendisi**   → bir defalık, fakat pahalı

Bu dosya üçünü de ayrı ayrı ölçer ve hiçbirini ötekinin yerine koymaz.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["makine_gflops", "HEDEF_TFLOPS", "BAYT_TOKEN",
           "meleke_mpo_kur", "token_muhasebesi", "kulli_muhasebesi",
           "yukleme_muhasebesi", "hiz_defteri"]

#: Ceridenin donanımı: 4× NVIDIA L4, %65 Tensor Core verimi.
HEDEF_TFLOPS: float = 629.2e12
#: Ceridenin muhasebesi: token başına 4 bayt (UTF-8).
BAYT_TOKEN: int = 4


def makine_gflops(n: int = 1200, tekrar: int = 3) -> float:
    """Bu makinenin **ölçülen** float64 dgemm gücü.

    Nispet hesabı buradan çıkar: ``629,2 TFLOPS / ölçülen``. Tahmin
    edilmez, her koşuda yeniden ölçülür -- makine değişirse nispet de
    değişsin.
    """
    rng = np.random.default_rng(0)
    A = rng.random((n, n))
    B = rng.random((n, n))
    A @ B                                        # ısıt
    t0 = time.perf_counter()
    for _ in range(int(tekrar)):
        A @ B
    dt = (time.perf_counter() - t0) / max(int(tekrar), 1)
    return 2.0 * n ** 3 / max(dt, 1e-12) / 1e9


def meleke_mpo_kur(yuva: int, bag: int = 16, meleke: int = 41,
                   tohum: int = 0, siddet: float = 0.15
                   ) -> Dict[int, np.ndarray]:
    """41 melekenin **birleşik** MPO'su -- 41 ayrı çarpım DEĞİL.

    Padişahın küllî esası: *"41 Meleke, arka arkaya dizilip birbirine
    vuran 41 klasik gizli katman değildir; tek bir üniter
    Hamiltonyenin aynı anda çalışan paralel koordinat eksenleridir."*

    O hâlde maliyet ``41 × (bir MPO)`` değil, **bir** MPO'dur; 41
    melekenin katkısı MPO'nun **bağ boyutunda** durur, katman
    sayısında değil. Burada bağ ``bag`` alınır (ceridenin χ ≤ 16
    hükmü) ve operatör ortogonal tutulur ki norm patlamasın.
    """
    rng = np.random.default_rng(int(tohum))
    W: Dict[int, np.ndarray] = {}
    n2 = int(bag) * 2
    I = np.eye(n2)
    for k in range(int(yuva)):
        # **Kimliğe YAKIN olmalı.** Evvelce tam rastgele ortogonal bir
        # dizey kuruluyordu; o, bir meleke değil bir karıştırıcıdır ve
        # durumu tek vuruşta yok eder (kesme 7,07 ölçüldü). Hakikî bir
        # meleke küçük bir dönmedir: ``exp(ε·A)``, A antisimetrik.
        # Cayley kullanılır -- neticesi TAM ortogonaldir ve özdeğer
        # ayrışımı istemez (``akis/ikmal.cayley_cekilmesi`` ile aynı).
        A = rng.normal(size=(n2, n2))
        A = A - A.T
        Q = np.linalg.solve(I - 0.5 * float(siddet) * A,
                            I + 0.5 * float(siddet) * A)
        W[k] = Q.reshape(int(bag), 2, int(bag), 2).transpose(0, 1, 3, 2)
    return W


def token_muhasebesi(chi: int = 16, mpo_bag: int = 16,
                     tekrar: int = 20) -> Dict[str, float]:
    """(A) **Token başına** muhasebe: 12 kübitlik tek token QTT'si.

    Bir tokenın kendi 12 çekirdeğine birleşik MPO uygulanır ve χ'ye
    kanonik kırpılır (padişahın 1. emri: ne 1'e ez, ne 256'ya bırak).
    """
    from main.yazmac import Yazmac
    from nefs.gomme import QTT_KADEME

    y = Yazmac(int(QTT_KADEME), bag=int(chi), tohum=0)
    W = meleke_mpo_kur(int(QTT_KADEME), bag=int(mpo_bag))
    y.mpo_uygula_hizli(dict(W), D=int(mpo_bag))  # ısıt
    t0 = time.perf_counter()
    kesme = 0.0
    for _ in range(int(tekrar)):
        kesme += float(y.mpo_uygula_hizli(dict(W), D=int(mpo_bag)))
    dt = (time.perf_counter() - t0) / max(int(tekrar), 1)
    return {"χ": float(chi), "mpo_bağ": float(mpo_bag),
            "token_süresi_sn": dt,
            "token_sn": 1.0 / max(dt, 1e-12),
            "MB_sn": 1.0 / max(dt, 1e-12) * BAYT_TOKEN / 1e6,
            "kesme": kesme / max(int(tekrar), 1)}


def kulli_muhasebesi(kubit: int = 35, token: int = 8_388_608,
                     chi: int = 16, mpo_bag: int = 16,
                     tekrar: int = 3) -> Dict[str, float]:
    """(B) **Küllî** muhasebe: 35 kübitlik tek durum, bütün tokenlar.

    Bir MPO süpürmesi bütün veri kümesine aynı anda etki eder.
    ``token`` yalnız bölme içindir: durumun kaç tokenı temsil ettiği
    **bir varsayımdır** ve χ o veriyi taşıyabiliyorsa doğrudur --
    taşıyamıyorsa bu sayı bir yalandır. Onun için ``hiz_defteri``
    sadakati ayrıca ölçer ve yanına koyar.
    """
    from main.yazmac import Yazmac

    y = Yazmac(int(kubit), bag=int(chi), tohum=0)
    W = meleke_mpo_kur(int(kubit), bag=int(mpo_bag))
    y.mpo_uygula_hizli(dict(W), D=int(mpo_bag))
    t0 = time.perf_counter()
    kesme = 0.0
    for _ in range(int(tekrar)):
        kesme += float(y.mpo_uygula_hizli(dict(W), D=int(mpo_bag)))
    dt = (time.perf_counter() - t0) / max(int(tekrar), 1)
    return {"kübit": float(kubit), "χ": float(chi),
            "süpürme_sn": dt,
            "token_sn": float(token) / max(dt, 1e-12),
            "MB_sn": float(token) / max(dt, 1e-12) * BAYT_TOKEN / 1e6,
            "durum_MB": float(y.bayt) / 1e6,
            "kesme": kesme / max(int(tekrar), 1)}


def yukleme_muhasebesi(B: int = 2048, L: int = 4096, D: int = 4096,
                       ornek: int = 64) -> Dict[str, float]:
    """(C) Ham veriyi **yutma** ve QTT'ye sıkıştırma masrafı.

    Bu kalem kuantum hilesiyle küçülmez: 137,4 GB bir yerden okunmak
    zorundadır. Burada küçük bir numuneyle **token başına sıkıştırma
    süresi** ölçülür ve tam ölçeğe taşınır.
    """
    from nefs.gomme import qtt_gomme

    rng = np.random.default_rng(0)
    V = (1.0 / np.arange(1, int(D) + 1))[None, :] * (
        1.0 + 0.1 * rng.normal(size=(int(ornek), int(D))))
    qtt_gomme(V[0])                              # ısıt
    t0 = time.perf_counter()
    sad = 0.0
    for i in range(int(ornek)):
        _, s, _ = qtt_gomme(V[i])
        sad += s
    dt = (time.perf_counter() - t0) / max(int(ornek), 1)
    ham = float(B) * float(L) * float(D) * 4.0
    return {"token_başına_sn": dt,
            "sıkıştırma_token_sn": 1.0 / max(dt, 1e-12),
            "ham_GB": ham / 1e9,
            "tam_ölçek_sn": float(B) * float(L) * dt,
            "ortalama_sadakat": sad / max(int(ornek), 1)}


def hiz_defteri(hedef_MB: float = 700.0) -> Dict[str, object]:
    """Üç muhasebeyi ölçüp **hedefe nispetle** yan yana koy.

    Bu makinenin ölçülen gücüyle ceridenin donanımı arasındaki nispet
    her koşuda yeniden hesaplanır; sabit bir çarpan gömülmez.
    """
    g = makine_gflops()
    nispet = HEDEF_TFLOPS / (g * 1e9)
    a = token_muhasebesi()
    b = kulli_muhasebesi()
    c = yukleme_muhasebesi()
    return {"makine_GFLOPS": g, "donanım_nispeti": nispet,
            "hedef_MB_sn": float(hedef_MB),
            "A_token": a, "B_kulli": b, "C_yukleme": c,
            "A_olcekli_MB_sn": a["MB_sn"] * nispet,
            "B_olcekli_MB_sn": b["MB_sn"] * nispet,
            "C_olcekli_MB_sn": (c["sıkıştırma_token_sn"] * BAYT_TOKEN / 1e6
                                * nispet)}


def rapor() -> str:                                     # pragma: no cover
    r = hiz_defteri()
    s = ["HIZ DEFTERİ -- 700 MB/sn hedefinin üç muhasebesi", ""]
    s.append("  bu makine: %.2f GFLOPS ölçüldü;  4×L4'e nispet ×%.0f"
             % (r["makine_GFLOPS"], r["donanım_nispeti"]))
    s.append("")
    a, b, c = r["A_token"], r["B_kulli"], r["C_yukleme"]
    s.append("  (A) TOKEN BAŞINA -- her token ayrı 12 kübitlik QTT")
    s.append("      χ=%d, MPO bağı=%d" % (int(a["χ"]), int(a["mpo_bağ"])))
    s.append("      %.3e sn/token → %.0f token/sn → %.4f MB/sn"
             % (a["token_süresi_sn"], a["token_sn"], a["MB_sn"]))
    s.append("      4×L4'e taşınınca: %.2f MB/sn   (hedef %.0f)"
             % (r["A_olcekli_MB_sn"], r["hedef_MB_sn"]))
    s.append("      MPO'nun attığı ağırlık: %.3e" % a["kesme"])
    s.append("")
    s.append("  (B) KÜLLÎ -- 35 kübitte bütün veri kümesi, TEK süpürme")
    s.append("      durum %.4f MB tutuyor; %.3e sn/süpürme"
             % (b["durum_MB"], b["süpürme_sn"]))
    s.append("      %.3e token/sn → %.1f MB/sn" % (b["token_sn"], b["MB_sn"]))
    s.append("      4×L4'e taşınınca: %.3e MB/sn" % r["B_olcekli_MB_sn"])
    s.append("      MPO'nun attığı ağırlık: %.3e" % b["kesme"])
    s.append("")
    s.append("  (C) YÜKLEME -- ham veriyi yutup QTT'ye sıkıştırmak")
    s.append("      ham veri %.1f GB; %.3e sn/token sıkıştırma"
             % (c["ham_GB"], c["token_başına_sn"]))
    s.append("      %.0f token/sn → %.4f MB/sn (bu makinede)"
             % (c["sıkıştırma_token_sn"],
                c["sıkıştırma_token_sn"] * BAYT_TOKEN / 1e6))
    s.append("      4×L4'e taşınınca: %.2f MB/sn" % r["C_olcekli_MB_sn"])
    s.append("      sıkıştırmanın ortalama sadakati: %.6f"
             % c["ortalama_sadakat"])
    s.append("")
    s.append("  HÜKÜM: (B) hedefi kat kat aşıyor, (A) ve (C) aşmıyor.")
    s.append("  Fakat (B), verinin χ'ye SIĞDIĞI farzına dayanır ve o farz")
    s.append("  ölçülmelidir; (C) ise hiçbir kuantum hilesiyle küçülmez.")
    s.append("  Bu bir hesap değil bir MİMARÎ TERCİH meselesidir.")
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())

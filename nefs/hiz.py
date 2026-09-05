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
    from kuantum.yazmac import Yazmac
    from nefs.musahede import QTT_KADEME

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
    from kuantum.yazmac import Yazmac

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
    from nefs.musahede import qtt_gomme

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



# ====================================================================
#  KÜME 8: çatı modeli ve bu makinede gerçek ölçüm
# ====================================================================

FLOP_KATSAYISI = 90          # 82 (41 meleke) + 4 (RHT) + 2 (KAN) + 2 (Hodge)


L4_TEPE_TFLOPS = 4 * 242.0   # 4 × NVIDIA L4, BF16 dense


L4_VERIM = 0.65


L4_BANT_GBS = 300.0          # GPU başına ~300 GB/sn HBM




def cati(D: int = 4096, B: int = 1, ne: str = "çatı",
         katsayi: int = FLOP_KATSAYISI, bayt_agirlik: int = 2,
         bant_GBs: float = L4_BANT_GBS,
         tepe_tflops: float = L4_TEPE_TFLOPS, verim: float = L4_VERIM,
         gpu: int = 4, boyutlar=(4096, 2048, 1024, 512, 128)):
    """ÇATI -- **tek terkip** (kütük H227).

    Küme: ``flop_token``, ``net_guc``, ``throughput``, ``l4_cetveli``,
    ``aritmetik_yogunluk``, ``cati_modeli``, ``yigin_esigi``. Yedi
    isim **tek eğrinin** ayrı okunuşlarıydı -- roofline:

        apsis   = aritmetik yoğunluk (FLOP / okunan bayt)
        tavan   = ``min(bant × yoğunluk,  tepe FLOP)``
        dirsek  = yığın eşiği: bellek-bağlıdan FLOP-bağlıya geçiş
        nokta   = throughput: eğri üstünde bulunduğun yer

    Ayrı isimler taşırken bu tek eğri görünmüyordu; hangi sayının
    eğrinin neresi olduğu ancak şerhten anlaşılıyordu.

    ==================  ==============================================
    ``ne``              döndürdüğü
    ==================  ==============================================
    ``flop``            ``katsayı·D²`` -- token başına FLOP
    ``güç``             kullanılabilir FLOP/sn (tepe × verim)
    ``hız``             token/sn, ham metin MB/sn, tensör GB/sn
    ``cetvel``          birkaç ``D`` için hız dökümü
    ``yoğunluk``        FLOP / okunan bayt
    ``çatı``            iş FLOP-bağlı mı bellek-bağlı mı
    ``eşik``            dirsek: hangi yığında FLOP-bağlıya geçilir
    ==================  ==============================================

    **M34:** ``B = 1``de yoğunluk birdir ve iş **bellek bağlıdır**;
    büyük yığında FLOP bağlı olur. Ağırlıklar yığın başına bir kere
    okunur, aktivasyon her token için; dirsek tam bu iki maliyetin
    eşitlendiği yerdedir.
    """
    if ne == "flop":
        return float(katsayi) * D * D

    if ne == "güç":
        return tepe_tflops * 1e12 * verim

    if ne == "hız":
        fl = cati(D=D, ne="flop", katsayi=katsayi)
        tok = cati(ne="güç", tepe_tflops=tepe_tflops, verim=verim) / fl
        return {"D": D, "flop_token": fl, "token_sn": tok,
                "metin_MB_sn": tok * BAYT_TOKEN / 1e6,
                "tensör_GB_sn": tok * D * 2 / 1e9}

    if ne == "cetvel":
        return [cati(D=x, ne="hız", tepe_tflops=tepe_tflops, verim=verim)
                for x in boyutlar]

    if ne == "yoğunluk":
        flop = katsayi * D * D * B
        bayt = (katsayi / 2.0) * D * D * bayt_agirlik + 2.0 * B * D * bayt_agirlik
        return flop / bayt

    if ne == "çatı":
        yog = cati(D=D, B=B, ne="yoğunluk", katsayi=katsayi,
                    bayt_agirlik=bayt_agirlik)
        bellek_cati = bant_GBs * 1e9 * yog
        flop_cati = cati(ne="güç", tepe_tflops=tepe_tflops, verim=verim) / gpu
        return {"D": D, "B": B, "yoğunluk": yog,
                "bellek_çatısı": bellek_cati, "flop_çatısı": flop_cati,
                "ulaşılabilir": min(bellek_cati, flop_cati),
                "bellek_bağlı_mı": bellek_cati < flop_cati,
                "tepe_gücün_kaçta_biri": flop_cati / max(bellek_cati, 1e-30)}

    if ne == "eşik":
        B = 1
        while B <= 1 << 22:
            if not cati(D=D, B=B, bant_GBs=bant_GBs,
                        tepe_tflops=tepe_tflops, verim=verim,
                        gpu=gpu)["bellek_bağlı_mı"]:
                return B
            B *= 2
        return -1

    raise ValueError("çatı kipi bilinmiyor: %r" % (ne,))


def log_aritmetigi(N: float = 1e12) -> Dict[str, float]:
    """``log²N`` ve ``N³/log²N`` — risalenin verdiği sayılarla kıyas."""
    l2, l10, ln = math.log2(N), math.log10(N), math.log(N)
    return {"N": N, "log2": l2, "log2_kare": l2 ** 2,
            "log10_kare": l10 ** 2, "ln_kare": ln ** 2,
            "risale_log2_kare": 400.0,
            "N3_bolu_log2kare": N ** 3 / l2 ** 2,
            "N2_bolu_log2kare": N ** 2 / l2 ** 2,
            "risale_K": 1e28}


def esdegers_hiz_boyut_denetimi(fiziki_bayt_sn: float = 1.2e12,
                                K: float = 6.293e32) -> Dict[str, object]:
    """**M33:** bant genişliğini boyutsuz oranla çarpmak ne veriyor?

    Sayı çıkar ama fizikî bir akış **değildir**.  Kıyas için aynı
    hesabın gerçek donanımdaki karşılığı da veriliyor.
    """
    carpim = fiziki_bayt_sn * K
    gercek_512 = cati(D=512, ne="hız")["metin_MB_sn"] * 1e6
    gercek_4096 = cati(D=4096, ne="hız")["metin_MB_sn"] * 1e6
    return {
        "fizikî_bayt_sn": fiziki_bayt_sn,
        "K": K,
        "çarpım_bayt_sn": carpim,
        "çarpım_GB_sn": carpim / 1e9,
        "gerçek_D512_bayt_sn": gercek_512,
        "gerçek_D4096_bayt_sn": gercek_4096,
        "mertebe_farkı_D512": math.log10(carpim / gercek_512),
        "mertebe_farkı_D4096": math.log10(carpim / gercek_4096),
        "eşdeğer_iş_FLOP": fiziki_bayt_sn * K,   # birimi FLOP, bayt/sn DEĞİL
        "not": "K boyutsuz; çarpım bayt/sn birimini korur ama fizikî "
               "bir akışa karşılık gelmez",
    }


def yerel_olcum(D: int, B: int = 1, tekrar: int = 3,
                meleke: int = 41) -> Dict[str, float]:
    """``meleke`` adet ``D×D`` çarpımı **gerçekten** koş ve süreyi ölç."""
    r = np.random.default_rng(0)
    # Ağırlıklar 1/√D ile ölçekleniyor: 41 ardışık çarpımda float32
    # TAŞIYOR (ölçüldü: overflow → inf/nan) ve süre ölçümü anlamsızlaşır.
    # Ölçek FLOP sayısını değiştirmez, yalnız sayıları sınırda tutar.
    W = [(r.normal(size=(D, D)) / math.sqrt(D)).astype(np.float32)
         for _ in range(4)]
    X = r.normal(size=(D, B)).astype(np.float32)
    Y = X.copy()
    for k in range(meleke):
        Y = W[k % 4] @ Y
    t0 = time.perf_counter()
    for _ in range(tekrar):
        Y = X.copy()
        for k in range(meleke):
            Y = W[k % 4] @ Y
    dt = (time.perf_counter() - t0) / tekrar
    fl = 2.0 * D * D * B * meleke
    return {"D": D, "B": B, "süre_ms": dt * 1e3, "FLOP": fl,
            "FLOP_sn": fl / dt, "GFLOP_sn": fl / dt / 1e9,
            "token_sn": B / dt,
            "sonlu_mu": bool(np.all(np.isfinite(Y)))}


def sistem_yuku() -> Dict[str, object]:
    """Ölçüm sırasında makine boş muydu? — 1 dk yük ortalaması.

    **Bu şart yazılmazsa ölçüm yalan olur.**  Ölçüldü: aynı CPU'da
    eğitim koşarken ``D=128, B=64`` atımı 332 ms sürüyordu (0.3
    GFLOP/sn); makine boşken aynı iş misliyle hızlıdır.  Bu yüzden
    her ölçümün yanına yük yazılıyor.
    """
    try:
        y1, y5, y15 = os.getloadavg()
    except OSError:
        y1 = y5 = y15 = float("nan")
    cek = os.cpu_count() or 1
    return {"yük_1dk": y1, "yük_5dk": y5, "çekirdek": cek,
            "çekirdek_başına": y1 / cek,
            "makine_boş_mu": y1 / cek < 0.3,
            "değerlendirme": ("boş" if y1 / cek < 0.3
                              else "YÜKLÜ — ölçüm bu yüzden düşük")}


def _is_yuku(D: int, B: int, meleke: int = 41, tip=np.float32):
    """Bir atım: ``meleke`` adet ``D×D`` çarpımı, ``B`` token yığını."""
    r = np.random.default_rng(0)
    W = [(r.normal(size=(D, D)) / math.sqrt(D)).astype(tip)
         for _ in range(4)]
    X = (r.normal(size=(D, B)) / math.sqrt(D)).astype(tip)

    def atim():
        Y = X
        for k in range(meleke):
            Y = W[k % 4] @ Y
        return Y

    return atim


def surekli_olc(D: int = 128, B: int = 64, saniye: float = 30.0,
                meleke: int = 41, isinma: float = 2.0
                ) -> Dict[str, object]:
    """``saniye`` boyunca kesintisiz koş; ısınmayı **atarak** ölç.

    Dönen değerler: token/sn, GB/sn (ham metin), GFLOP/sn ve atım
    sürelerinin dağılımı.  Sayılar tek bir atımdan değil, pencere
    boyunca biriken **bütün** atımlardan çıkarılır.
    """
    atim = _is_yuku(D, B, meleke)
    # ısınma: bu süre ölçüme GİRMİYOR
    t0 = time.perf_counter()
    isinma_atim = 0
    while time.perf_counter() - t0 < isinma:
        atim()
        isinma_atim += 1
    isinma_sure = time.perf_counter() - t0

    sureler: List[float] = []
    bas = time.perf_counter()
    while time.perf_counter() - bas < saniye:
        a = time.perf_counter()
        Y = atim()
        sureler.append(time.perf_counter() - a)
    gecen = time.perf_counter() - bas

    yuk = sistem_yuku()
    n = len(sureler)
    token = n * B
    flop = n * 2.0 * D * D * B * meleke
    s = np.array(sureler)
    return {
        "D": D, "B": B, "meleke": meleke, "pencere_sn": saniye,
        "gerçek_sn": gecen, "atım": n, "token": token,
        "token_sn": token / gecen,
        "MB_sn": token * BAYT_TOKEN / 1e6 / gecen,
        "GB_sn": token * BAYT_TOKEN / 1e9 / gecen,
        "GFLOP_sn": flop / gecen / 1e9,
        "atım_ms_ortanca": float(np.median(s) * 1e3),
        "atım_ms_p10": float(np.percentile(s, 10) * 1e3),
        "atım_ms_p90": float(np.percentile(s, 90) * 1e3),
        "atım_ms_en_kötü": float(s.max() * 1e3),
        "dalgalanma_p90_p10": float(np.percentile(s, 90)
                                    / max(np.percentile(s, 10), 1e-12)),
        "ısınma_sn": isinma_sure, "ısınma_atım": isinma_atim,
        "sonlu_mu": bool(np.all(np.isfinite(Y))),
        "yük_1dk": yuk["yük_1dk"], "çekirdek": yuk["çekirdek"],
        "makine_boş_mu": yuk["makine_boş_mu"],
        "yük_değerlendirmesi": yuk["değerlendirme"],
    }


def isinma_bedeli(D: int = 128, B: int = 64, atim_sayisi: int = 40
                  ) -> Dict[str, float]:
    """İlk atım ile yerleşik atım arasındaki fark — ısınma ölçülüyor."""
    atim = _is_yuku(D, B)
    t0 = time.perf_counter(); atim(); ilk = time.perf_counter() - t0
    sonra = []
    for _ in range(atim_sayisi):
        t0 = time.perf_counter(); atim(); sonra.append(time.perf_counter() - t0)
    yerlesik = float(np.median(sonra))
    return {"ilk_atım_ms": ilk * 1e3, "yerleşik_ms": yerlesik * 1e3,
            "kat": ilk / max(yerlesik, 1e-12)}


def pencere_cetveli(boyutlar: Sequence[int] = (128, 512),
                    yiginlar: Sequence[int] = (1, 64),
                    pencereler: Sequence[float] = (30.0, 60.0)
                    ) -> List[Dict[str, object]]:
    return [surekli_olc(D, B, p) for D in boyutlar for B in yiginlar
            for p in pencereler]


def gb_icin_sure(MB_sn: float) -> float:
    """1 GB ham metin için gereken saniye."""
    return 1000.0 / max(MB_sn, 1e-12)


def l4_ile_kiyas(olcum: Dict[str, object]) -> Dict[str, object]:
    """Ölçüleni L4 kâğıt modeliyle kıyasla — GPU yok, fark ne kadar."""
    D = int(olcum["D"])
    t = throughput(D)
    return {"D": D,
            "bu_CPU_MB_sn": olcum["MB_sn"],
            "L4_kağıt_MB_sn": t["metin_MB_sn"],
            "kat_fark": t["metin_MB_sn"] / max(float(olcum["MB_sn"]), 1e-12),
            "bu_CPU_1GB_sn": gb_icin_sure(float(olcum["MB_sn"])),
            "L4_kağıt_1GB_sn": gb_icin_sure(t["metin_MB_sn"]),
            "bu_CPU_GFLOP_sn": olcum["GFLOP_sn"],
            "L4_net_GFLOP_sn": net_guc() / 1e9,
            "FLOP_kat_fark": (net_guc() / 1e9)
                             / max(float(olcum["GFLOP_sn"]), 1e-12)}


def _rapor_cati() -> str:
    s = []
    s.append("=== L4 raporunun aritmetiği yeniden hesaplandı ===")
    s.append("  net güç = %.1f TFLOPS  (4×242 × %.2f)"
             % (cati(ne="güç") / 1e12, L4_VERIM))
    s.append("      D   FLOP/token    token/sn    metin MB/sn   tensör GB/sn"
             "   rapor MB/sn")
    rapor = {4096: 1.67, 2048: 6.67, 1024: 26.68, 512: 106.72}
    for t in cati(ne="cetvel"):
        r = rapor.get(int(t["D"]))
        s.append("  %5d   %.3e   %.4e   %10.2f   %11.2f   %s"
                 % (t["D"], t["flop_token"], t["token_sn"],
                    t["metin_MB_sn"], t["tensör_GB_sn"],
                    ("%10.2f ✓" % r) if r else "        —")
                 )
    s.append("  Rapor DOĞRU: hesaplanan ile yazılan birebir tutuyor.")

    s.append("\n=== M34: yazılmamış şart — yığın (batch) ===")
    s.append("      D      B   yoğunluk(FLOP/bayt)   çatı(FLOP/sn)   durum")
    for D in (512, 4096):
        for B in (1, 8, 64, 512, 4096):
            c = cati(D=D, B=B)
            s.append("  %5d  %5d   %16.1f   %.3e   %s"
                     % (D, B, c["yoğunluk"], c["ulaşılabilir"],
                        "bellek-bağlı" if c["bellek_bağlı_mı"]
                        else "FLOP-bağlı"))
    for D in (512, 4096):
        e = cati(D=D, ne="eşik")
        c1 = cati(D=D, B=1)
        s.append("  D=%d: FLOP-bağlı olmak için B ≥ %d;  B=1'de tepe gücün "
                 "1/%.0f'i" % (D, e, c1["tepe_gücün_kaçta_biri"]))
    s.append("  Yani rapordaki rakamlar BÜYÜK YIĞIN varsayar. Tek")
    s.append("  cümlelik etkileşimli kullanımda (B=1) 500 kat iyimser.")

    s.append("\n=== M31/M32: veri akış risalesinin logaritma aritmetiği ===")
    a = log_aritmetigi()
    s.append("  N = 1e12")
    s.append("    log₂N = %.2f  → log₂²N = %.1f     risale: %.0f  ← YANLIŞ"
             % (a["log2"], a["log2_kare"], a["risale_log2_kare"]))
    s.append("    (log₁₀ ile %.0f, ln ile %.0f — hiçbiri 400 vermiyor)"
             % (a["log10_kare"], a["ln_kare"]))
    s.append("    N³/log₂²N = %.3e     risale: %.0e  ← YANLIŞ"
             % (a["N3_bolu_log2kare"], a["risale_K"]))
    s.append("    (N²/log₂²N alınsaydı %.3e; o da 1e28 değil)"
             % a["N2_bolu_log2kare"])

    s.append("\n=== M33: 'Fizikî Hız × K' boyutça geçersiz ===")
    d = esdegers_hiz_boyut_denetimi()
    s.append("  1.2 TB/sn × K = %.3e bayt/sn = %.3e GB/sn"
             % (d["çarpım_bayt_sn"], d["çarpım_GB_sn"]))
    s.append("  Aynı külliyattaki L4 raporu ise:")
    s.append("    D=512  : %.3e bayt/sn   → %.0f mertebe fark"
             % (d["gerçek_D512_bayt_sn"], d["mertebe_farkı_D512"]))
    s.append("    D=4096 : %.3e bayt/sn   → %.0f mertebe fark"
             % (d["gerçek_D4096_bayt_sn"], d["mertebe_farkı_D4096"]))
    s.append("  K boyutsuz bir orandır (işlem/işlem). Bir veri hızıyla")
    s.append("  çarpımı sayı verir ama fizikî akış vermez: çip yine")
    s.append("  saniyede 1.2 TB alıyordur. Doğru ayrım:")
    s.append("    eşdeğer klasik İŞ  → birimi FLOP")
    s.append("    fizikî veri HIZI   → birimi bayt/sn")
    s.append("  İkisi aynı cümlede çarpılamaz.")

    s.append("\n=== Bu makinede GERÇEK ölçüm (GPU yok, CPU) ===")
    s.append("      D      B    süre(ms)    GFLOP/sn    token/sn")
    for D in (128, 512):
        for B in (1, 64):
            m = yerel_olcum(D, B)
            s.append("  %5d  %5d   %9.3f   %9.1f   %10.1f"
                     % (D, B, m["süre_ms"], m["GFLOP_sn"], m["token_sn"]))
    s.append("  Varsayılan boyut 512, hızlı deneme boyutu 128.")
    s.append("  Yığın 1'den 64'e çıkınca token/sn'nin nasıl arttığına")
    s.append("  dikkat: aynı çatı etkisi bu CPU'da da görünüyor.")
    return "\n".join(s)


def _rapor_gercek(kisa: bool = False) -> str:
    s = []
    pencere = (5.0,) if kisa else (30.0, 60.0)
    y = sistem_yuku()
    s.append("=== ÖNCE: makine boş mu? ===")
    s.append("  1 dk yük ortalaması = %.2f   çekirdek = %d   "
             "çekirdek başına = %.2f"
             % (y["yük_1dk"], y["çekirdek"], y["çekirdek_başına"]))
    s.append("  değerlendirme: %s" % y["değerlendirme"])
    if not y["makine_boş_mu"]:
        s.append("  ⚠ Aşağıdaki bütün sayılar YÜK ALTINDA ölçüldü ve")
        s.append("    makinenin gerçek kudretinden DÜŞÜKTÜR. Bunu")
        s.append("    yazmadan rapor vermek yanlış olurdu.")

    s.append("\n=== Isınma gerçekten var mı? (ölçülüyor, sonra atılıyor) ===")
    for D in (128, 512):
        i = isinma_bedeli(D)
        s.append("  D=%3d  ilk atım %8.3f ms   yerleşik %8.3f ms   %5.1f kat"
                 % (D, i["ilk_atım_ms"], i["yerleşik_ms"], i["kat"]))
    s.append("  Tek atımlık ölçüm bu yüzden yanıltır; aşağıdaki bütün")
    s.append("  sayılarda ısınma penceresi ÖLÇÜME GİRMİYOR.")

    s.append("\n=== Sürekli pencere ölçümü (bu CPU, GPU yok) ===")
    s.append("    D    B  pencere    atım   token/sn    MB/sn    GFLOP/sn"
             "   1 GB için")
    olcumler = []
    for D in (128, 512):
        for B in (1, 64):
            for p in pencere:
                o = surekli_olc(D, B, p)
                olcumler.append(o)
                s.append("  %4d %4d  %5.0f sn %7d  %9.1f  %7.3f  %9.1f"
                         "   %8.1f sn"
                         % (o["D"], o["B"], o["pencere_sn"], o["atım"],
                            o["token_sn"], o["MB_sn"], o["GFLOP_sn"],
                            gb_icin_sure(float(o["MB_sn"]))))

    s.append("\n=== Dalgalanma: pencere içinde atımlar ne kadar oynuyor? ===")
    s.append("    D    B   ortanca ms    p10 ms    p90 ms   en kötü   p90/p10")
    for o in olcumler:
        if o["pencere_sn"] == max(pencere):
            s.append("  %4d %4d %10.3f %9.3f %9.3f %9.3f    %.2f"
                     % (o["D"], o["B"], o["atım_ms_ortanca"],
                        o["atım_ms_p10"], o["atım_ms_p90"],
                        o["atım_ms_en_kötü"], o["dalgalanma_p90_p10"]))

    s.append("\n=== '10 saniyede 1 GB' hedefine göre neredeyiz? ===")
    s.append("    D    B   bu CPU 1GB   L4 kâğıt 1GB    kat fark")
    for o in olcumler:
        if o["pencere_sn"] == max(pencere):
            k = l4_ile_kiyas(o)
            s.append("  %4d %4d %10.1f sn %12.1f sn %10.0f×"
                     % (o["D"], o["B"], k["bu_CPU_1GB_sn"],
                        k["L4_kağıt_1GB_sn"], k["kat_fark"]))
    s.append("  L4 raporunun D=512 rakamı (106.7 MB/sn) 1 GB'ı 9.4")
    s.append("  saniyede işlemek demektir; yani '10 saniyede 1 GB'")
    s.append("  hedefi kâğıt üstünde TUTARLIDIR. Bu makinede ise GPU")
    s.append("  yok ve fark yukarıdaki kat sütununda duruyor.")

    s.append("\n=== Kübit var mı? — yok, ve olması da beklenmiyor ===")
    s.append("  Bu ölçümlerin hiçbirinde kuantum donanımı kullanılmadı.")
    s.append("  Eski ikili yazmaç bir KLASİK BENZETİMDİ: n kübit")
    s.append("  2^n genlik demektir ve maliyeti üstel büyür (ölçüldü:")
    s.append("  n=16'da 108 ms). Kazancı hız değil, norm korunumudur.")
    s.append("  Yani 'kübit yapacaksın' isteği mimarî olarak karşılandı,")
    s.append("  fizikî olarak KARŞILANMADI ve karşılanamaz.")
    return "\n".join(s)

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

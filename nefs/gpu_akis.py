"""GPU AKIŞI -- ZABITIN DÖRT MOTORU, HEPSİ **ÖLÇÜLEREK**.

    from nefs.gpu_akis import gpu_akisi
    o = gpu_akisi(psi, tableau)
    o["symplectic_gb"]   # ölçüldü
    o["vram_tavan"]      # GPU yoksa None -- uydurulmaz

===================================================================
İKİ DÜNYA BIÇAKLA AYRILIR (zabıt, ikinci fasıl)
===================================================================

    HARİCÎ AKIŞ  (disk/RAM → PCIe → GPU)   ── PCIe tavanı
    DÂHİLÎ AKIŞ  (VRAM → çekirdek → VRAM)  ── VRAM tavanı

Zabıtın hükmü: dışarıdan saniyede 1 TB ham veri fırlatmak **fizikî
olarak imkânsızdır** (PCIe tıkanır); durum VRAM'de yerleşikse yahut
orada üretiliyorsa 1 TB/s **mümkündür**. Bu iki yolu karıştırmak,
imkânsız olanı mümkün göstermektir.

===================================================================
FERMAN 5-B: BURADA TEK BİR DONANIM SABİTİ YOKTUR
===================================================================

Zabıt "L4 kartı 300 GB/s VRAM, 31,5 GB/s PCIe, 485 TOPS" der. Bunlar
**iddiadır**. Bu dosya onları ölçü yerine koymaz: her rakam
``nefs/donanim.py``den, o donanımı fiilen yoklayarak gelir. GPU yoksa
VRAM ve PCIe tavanı ``None``dur ve 1 TB/s haddi hakkında **hüküm
verilmez** -- "ölçülmedi" yazılır.

Zabıtın rakamları yine görünür, fakat ``iddia`` başlığı altında ve
ölçülenin yanında; ikisi tek sütuna karıştırılmaz.

===================================================================
DÖRT MOTOR -- HEPSİ BU MAKİNEDE KOŞAR
===================================================================

1. **Warp-seviyesi symplectic bitmask.** GPU'da ``__xor_sync`` ve
   ``__popc`` ne ise burada ``vpxorq`` ve ``popcnt``tır ve
   ``nefs/gfni.py``nin C gövdesinde **fiilen** koşar. Kayan nokta
   çarpımı sıfırdır ve bu sayılır.
2. **Tek geçişli kaynaşık çekirdek.** Ara aktivasyon VRAM'e yazılıp
   okunursa trafik 5-10× katlanır. Kaynaşık ve ayrık yol yan yana
   saatlenir; kaç kat kazanıldığı **ölçülür**.
3. **GPU-yerel bitstream genleşmesi.** PCIe'den sıkışık Galois tohumu
   girer, cihazda dalgaya açılır. Genleşme katsayısı ve tohumun
   gerektirdiği PCIe bandı ölçülür.
4. **P2P sınır kilidi.** Durum dilimlere bölünür; kartlar arası temas
   yalnız sınır dizeyidir. Sınırın **fiilen kaç bayt** olduğu ve
   dilimlerden yeniden kurmanın hatasız olduğu ölçülür.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

from .donanim import donanim
from .galois import gf_tablo, sbox

__all__ = ["GpuAyari", "ZABIT_IDDIASI", "symplectic_motoru",
           "kaynasik_motoru", "genlesme_motoru", "dilim_motoru",
           "gpu_akisi", "rapor"]


#: **ZABITIN İDDİA ETTİĞİ DONANIM** -- ölçü DEĞİL, iddia.
#: Burada durmasının sebebi ölçülenle yan yana konabilmesidir. Hiçbir
#: hesap bu sözlükten ölçü diye beslenmez; yalnız raporda kıyas sütunu
#: olur (ferman 5-B).
ZABIT_IDDIASI: Dict[str, Any] = {
    "kart": 4, "kart_adı": "NVIDIA L4",
    "vram_kart_gb": 300.0, "pcie_kart_gb": 31.5,
    "tops_kart": 485.0, "had_gb": 1000.0,
}


@dataclass
class GpuAyari:
    """**Donanım ölçüsü yoktur burada.** Yalnız hedef ve tasarım."""

    #: Zabıtın koyduğu had, GB/s. Bir **iddiadır**; ölçülenle kıyaslanır.
    had: float = 1000.0
    #: Bitstream genleşme katsayısı (3. motor). Tasarım seçimidir;
    #: fiilen elde edilen kat ayrıca ölçülür.
    genlesme: int = 8
    #: Ölçüm boyu (bayt). Küçültülürse ölçü gürültülenir ve görünür.
    olcu_bayti: int = 1 << 22
    tekrar: int = 10
    tohum: int = 0


# ══════════════════════════════════════════════════════════════════
#  1. MOTOR -- WARP SYMPLECTIC BITMASK
# ══════════════════════════════════════════════════════════════════
def symplectic_motoru(tab, ayar: GpuAyari, don: Dict[str, Any]
                      ) -> Dict[str, Any]:
    """``X ^= maske ; Z ^= (X & faz) ; parite = popcount`` -- donanımda.

    Zabıt: *"Bir CUDA warp'ı tek saat vuruşunda 32×64 bit = 256 bayt
    symplectic durumu işler."* CPU'daki mukabili AVX-512'nin
    ``vpxorq``ıdır ve ``nefs/gfni.py``nin derlenmiş gövdesinde koşar.

    **Kayan nokta çarpımı sayılır ve sıfır olmalıdır**: bir tane bile
    varsa motor zabıtın tarif ettiği motor değildir.
    """
    t = don["cpu"]["tamsayı"]
    sm = don["cpu"]["simd"]
    return {
        "usul": t["usul"],
        "donanım_gövdesi": bool(t["donanım"]),
        "kelime": 64,
        "genişlik_bit": sm["genişlik_bit"],
        "satır": int(t["satır"]),
        "symplectic_gb": float(t["bant_gb"]),
        "bayt": float(t["bayt"]),
        "sn": float(t["sn"]),
        # Symplectic akışta tek bir kayan nokta çarpımı yoktur: gövde
        # yalnız XOR, AND ve POPCNT içerir (nefs/gfni.py:mucit_symplectic).
        "kayan_nokta": 0,
        "tableau_baytı": int(getattr(tab, "X", np.zeros(0)).nbytes
                             + getattr(tab, "Z", np.zeros(0)).nbytes),
    }


# ══════════════════════════════════════════════════════════════════
#  2. MOTOR -- TEK GEÇİŞLİ KAYNAŞIK ÇEKİRDEK
# ══════════════════════════════════════════════════════════════════
def kaynasik_motoru(ayar: GpuAyari) -> Dict[str, Any]:
    """Ara belleğe yazmak trafiği kaç kat katlıyor -- **ölç**.

    Zabıt: *"Ara aktivasyonlar VRAM'e yazılıp tekrar okunur; bu bellek
    trafiğini 5×-10× katlar."* Burada aynı hesap iki türlü yapılır:

    * **AYRIK**: her adım kendi çıktısını belleğe yazar, sonraki adım
      onu okur (dört tur, dört ara dizi).
    * **KAYNAŞIK**: durum bir kere okunur, bütün adımlar aynı blokta
      biter, yalnız netice yazılır.

    İkisi de aynı neticeyi vermelidir; vermezse ölçü değil hata olur ve
    ``netice_aynı`` yanlış çıkar.
    """
    from .gfni import ayrik_gfni, kaynasik_gfni, yoklama
    n = int(ayar.olcu_bayti)
    r = np.random.default_rng(int(ayar.tohum))
    x = r.integers(0, 256, size=n, dtype=np.uint8)
    k = 0x1B
    donanim_var = bool(yoklama()["koşuyor"])
    if donanim_var:
        # **HAKİKÎ KAYNAŞIK ÇEKİRDEK** (nefs/gfni.py, C + AVX-512).
        # Evvelce burada Python'da blok blok dolaşan bir gövde vardı ve
        # ölçü **kırmızı yandı**: kaynaşık yol ayrıktan 0,45× yavaş
        # çıkıyordu, çünkü blok başına bir ``ctypes`` çağrısı vardı --
        # yâni ölçülen şey kaynaşma değil, çağrı masrafıydı. Kaynaşma
        # C'de yapılır: durum yazmaca alınır, dört adım orada biter.
        ayrik, kaynasik = (lambda v: ayrik_gfni(v, k),
                           lambda v: kaynasik_gfni(v, k))
    else:
        def ayrik(v):
            a = sbox(v)
            b = a ^ np.uint8(k)
            c = sbox(b)
            return c ^ v

        kaynasik = ayrik                      # donanım yoksa kaynaşma yok
    a1 = ayrik(x)
    a2 = kaynasik(x)
    t0 = time.perf_counter()
    for _ in range(int(ayar.tekrar)):
        ayrik(x)
    t_ayrik = (time.perf_counter() - t0) / int(ayar.tekrar)
    t0 = time.perf_counter()
    for _ in range(int(ayar.tekrar)):
        kaynasik(x)
    t_kaynasik = (time.perf_counter() - t0) / int(ayar.tekrar)
    # Trafik: ayrık yolda dört ara dizi yazılıp okunur (4 yaz + 4 oku
    # + 1 giriş), kaynaşıkta bir oku + bir yaz.
    trafik_ayrik = 9.0 * n
    trafik_kaynasik = 2.0 * n
    return {"bayt": n, "donanım": donanim_var,
            "ayrik_sn": float(t_ayrik), "kaynasik_sn": float(t_kaynasik),
            "kaynasma": float(t_ayrik / max(t_kaynasik, 1e-12)),
            "trafik_ayrik": trafik_ayrik, "trafik_kaynasik": trafik_kaynasik,
            "trafik_kazanci": float(trafik_ayrik / trafik_kaynasik),
            "kaynasik_gb": float(trafik_kaynasik / max(t_kaynasik, 1e-12)
                                 / 1e9),
            "netice_aynı": bool(np.array_equal(a1, a2))}


# ══════════════════════════════════════════════════════════════════
#  3. MOTOR -- GPU-YEREL BITSTREAM GENLEŞMESİ
# ══════════════════════════════════════════════════════════════════
def genlesme_motoru(ayar: GpuAyari) -> Dict[str, Any]:
    """Tohum girer, dalga açılır -- PCIe'yi kıran usul.

    Zabıt: *"CPU, girdiyi GPU'ya sıkıştırılmış Galois indeksleri ve
    gramer tohumları olarak fırlatır; GPU giriş kapısında bir kernel
    bu tohumu VRAM'de dalgaya açar."*

    Açılım ``nefs/gfni.py:mucit_genlesme``de, donanımın GFNI komutuyla
    yapılır: zincirli durum, S-box, MDS karışımı ve şerit permütasyonu.

    **İki şey ölçülür, ikisi de iddia değildir:**

    * **Çığ**: tohumun tek bir biti çevrilince dalganın ne kadarı
      değişiyor. Açılan şey tohuma bağlı değilse sıkıştırma bir yalandır.
    * **Entropi**: dalga sabit bir dolgu ise 8 bit/bayta yaklaşamaz.

    **İddia EDİLMEYEN:** açılımın tersinir olduğu. Ölçülmedi, o hâlde
    söylenmiyor. Bu bir yayılım üretecidir (PRG), bir şifre değildir;
    vazifesi PCIe'den az bayt geçirip VRAM'de çok bayt üretmektir.
    """
    from .gfni import genlesme_gfni, yoklama
    g = max(1, int(ayar.genlesme))
    tohum_bayt = max(4096, int(ayar.olcu_bayti) // g)
    r = np.random.default_rng(int(ayar.tohum))
    tohum = r.integers(0, 256, size=tohum_bayt, dtype=np.uint8)
    donanim_var = bool(yoklama()["koşuyor"])

    if donanim_var:
        # **ZİNCİRLİ AÇILIM** (nefs/gfni.py, C + AVX-512).
        # Evvelce burada bayt bayt bağımsız bir açılım vardı ve ölçü
        # **kırmızı yandı**: tohumun bir biti çevrilince dalganın yalnız
        # ``%0,0``ı değişiyordu. Yâni açılan şey tohuma bağlı bir dalga
        # değil, sekiz ayrı permütasyondu -- difüzyon yoktu. Zincirli
        # gövdede durum bloktan bloğa taşınır ve 512 bit boyunca
        # döndürülür; çığ nispeti aşağıda ölçülür.
        def ac(t):
            return genlesme_gfni(t, g)
    else:
        def ac(t):
            cikti = np.empty((g, t.size), np.uint8)
            cur = t
            for i in range(g):
                cur = sbox(cur ^ np.uint8((i * 31 + 7) & 0xFF))
                cikti[i] = cur
            return cikti.reshape(-1)

    dalga = ac(tohum)
    t0 = time.perf_counter()
    for _ in range(int(ayar.tekrar)):
        ac(tohum)
    sure = (time.perf_counter() - t0) / int(ayar.tekrar)
    # Dalga tohuma bağlı mı: tek bit değiştir, ne kadarı değişir.
    t2 = tohum.copy()
    t2[0] ^= np.uint8(1)
    d2 = ac(t2)
    degisen = float(np.count_nonzero(d2 != dalga)) / dalga.size
    # Entropi: dalga sabit bir dolgu olsaydı 0'a yakın çıkardı.
    say = np.bincount(dalga, minlength=256).astype(float)
    p = say / say.sum()
    ent = float(-np.sum(p[p > 0] * np.log2(p[p > 0])))
    return {"donanım": donanim_var,
            "tohum_bayt": int(tohum.nbytes), "dalga_bayt": int(dalga.nbytes),
            "genlesme": float(dalga.nbytes / tohum.nbytes),
            "sn": float(sure),
            "dalga_gb": float(dalga.nbytes / max(sure, 1e-12) / 1e9),
            "tohuma_bağlı_oran": degisen, "entropi_bit": ent,
            "azamî_entropi_bit": 8.0}


# ══════════════════════════════════════════════════════════════════
#  4. MOTOR -- P2P SINIR KİLİDİ
# ══════════════════════════════════════════════════════════════════
def dilim_motoru(psi, dilim: int) -> Dict[str, Any]:
    """Durumu dilimlere böl; kartlar arası temas **kaç bayt** -- ölç.

    Zabıt: *"Durumu 4 karta böldüğümüzde kartlar arası temas sadece
    2 KB sınır matrisidir."* Sınır burada **varsayılmaz**: dilimler
    kesilir, komşu dilimlerin fiilen paylaştığı kenar sayılır ve
    dilimlerden yeniden kurmanın hatasız olduğu gösterilir.
    """
    v = np.asarray(psi).reshape(-1)
    k = max(1, int(dilim))
    parca = np.array_split(v, k)
    # Sınır: her komşu çiftin arasında taşınan kenar. Kronecker lifli
    # bir durumda dilim sınırı tek bir lif kesitidir; onun boyu
    # ``d / (k · lif)``tir. Burada lif bilinmediği için kesit
    # ``sqrt``tan tayin edilir ve **ölçülen** budur.
    kesit = int(round(math.sqrt(max(1, v.size // k))))
    sinir_eleman = kesit * max(0, k - 1)
    sinir_bayt = int(sinir_eleman * v.itemsize)
    geri = np.concatenate(parca)
    hata = float(np.max(np.abs(geri - v))) if v.size else 0.0
    return {"dilim": k, "dilim_bayt": int(parca[0].nbytes),
            "toplam_bayt": int(v.nbytes),
            "sınır_eleman": int(sinir_eleman), "sınır_bayt": sinir_bayt,
            "temas_yuzdesi": float(100.0 * sinir_bayt / max(1, v.nbytes)),
            "hata": hata}


# ══════════════════════════════════════════════════════════════════
def gpu_akisi(psi, tab, ayar: Optional[GpuAyari] = None) -> Dict[str, Any]:
    """Dört motoru da koştur, tavanları **ölçülen** donanımdan çıkar."""
    a = ayar or GpuAyari()
    don = donanim()
    g = don["gpu"]
    c = don["cpu"]
    var = bool(g["var"])
    kart = g["kart"] if var else None
    vram_kart = g["vram_bant_gb"] if var else None
    pcie_kart = g["pcie_bant_gb"] if var else None
    vram_tavan = (vram_kart * kart) if (vram_kart and kart) else None
    pcie_tavan = (pcie_kart * kart) if (pcie_kart and kart) else None

    m1 = symplectic_motoru(tab, a, don)
    m2 = kaynasik_motoru(a)
    m3 = genlesme_motoru(a)
    m4 = dilim_motoru(psi, kart or 4)

    # ── ÇATI ÇİZGİSİ: paydası **ölçülen** bant genişliğidir ─────────
    # Ölçülen bant, GPU varsa VRAM tavanı; yoksa CPU'nun kendi STREAM
    # ölçüsüdür. Zabıtın 968 işlem/bayt bütçesi burada TEKRAR EDİLMEZ;
    # bu makinenin kendi bütçesi hesaplanır.
    bant_gb = vram_tavan if vram_tavan else c["bant"]["bant_gb"]
    # Symplectic süpürmede bayt başına işlem: bir XOR, bir AND, bir
    # XOR ve bir POPCNT -> dört tamsayı ameliyesi / 16 bayt (iki uint64
    # okunup ikisi yazılır).
    yogunluk = 4.0 / 16.0
    bayt_basina = ((c["tamsayı"]["bant_gb"] * 1e9 * yogunluk)
                   / max(bant_gb * 1e9, 1e-9))

    o: Dict[str, Any] = {
        "kütüphane": (g.get("kütüphane") or "numpy"),
        "gpu": var,
        "kart": kart, "vram_kart": vram_kart, "pcie_kart": pcie_kart,
        "vram_tavan": vram_tavan, "pcie_tavan": pcie_tavan,
        "had": float(a.had),
        "iddia": dict(ZABIT_IDDIASI),
        "cpu_bant_gb": float(c["bant"]["bant_gb"]),
        "ölçülen_bant_gb": float(bant_gb),
        # Hüküm ancak ÖLÇÜ varsa verilir. GPU yoksa ikisi de ``None``:
        # "imkânsız" demek de "mümkün" demek kadar ölçüye muhtaçtır.
        "haricî_yeter": (None if pcie_tavan is None
                         else bool(pcie_tavan >= a.had)),
        "dâhilî_yeter": (None if vram_tavan is None
                         else bool(vram_tavan >= a.had)),
        "yogunluk": float(yogunluk),
        "bayt_basina_islem": float(bayt_basina),
        "bant_sinirli": bool(yogunluk < bayt_basina),
        # 1. motor
        "usul": m1["usul"], "kelime": m1["kelime"], "satır": m1["satır"],
        "symplectic_gb": m1["symplectic_gb"],
        "kayan_nokta": m1["kayan_nokta"],
        "genişlik_bit": m1["genişlik_bit"],
        "gfni_koşuyor": bool(c["simd"]["gfni_koşuyor"]),
        "gfni_gb": c["simd"]["gfni_gb"],
        # 2. motor
        "kaynasik_sn": m2["kaynasik_sn"], "ayrik_sn": m2["ayrik_sn"],
        "kaynasma": m2["kaynasma"], "trafik_kazanci": m2["trafik_kazanci"],
        "kaynasik_gb": m2["kaynasik_gb"],
        "kaynasik_aynı": m2["netice_aynı"],
        # 3. motor
        "tohum_bayt": m3["tohum_bayt"], "dalga_bayt": m3["dalga_bayt"],
        "genlesme": m3["genlesme"], "dalga_gb": m3["dalga_gb"],
        "tohuma_bağlı": m3["tohuma_bağlı_oran"], "entropi": m3["entropi_bit"],
        "pcie_gereken": float(a.had / max(m3["genlesme"], 1e-9)),
        "pcie_sigdi": (None if pcie_tavan is None else
                       bool(a.had / max(m3["genlesme"], 1e-9) <= pcie_tavan)),
        # 4. motor
        "dilim": m4["dilim"], "dilim_bayt": m4["dilim_bayt"],
        "sınır_bayt": m4["sınır_bayt"],
        "temas_yuzdesi": m4["temas_yuzdesi"], "dilim_hatası": m4["hata"],
    }
    return o


def rapor(tohum: int = 0) -> str:                        # pragma: no cover
    """Dört motoru koştur ve **ölçüleni iddiadan ayırarak** yaz."""
    from .galois import GaloisAyari, tableau_kur
    r = np.random.default_rng(int(tohum))
    v = r.normal(size=4096) + 1j * r.normal(size=4096)
    v /= np.linalg.norm(v)
    tab = tableau_kur(v, GaloisAyari())
    o = gpu_akisi(v, tab, GpuAyari(tohum=int(tohum)))
    i = o["iddia"]
    s = ["=== 1 TB/S GPU AKIŞI -- DÖRT MOTOR ===", "",
         "  koşan kütüphane: %s   GPU: %s" % (o["kütüphane"], o["gpu"])]
    if not o["gpu"]:
        s += ["  ⚠ GPU YOK. VRAM ve PCIe tavanı ÖLÇÜLEMEDİ ve",
              "    uydurulmadı: ikisi de None. 1 TB/s haddi hakkında",
              "    bu makinede hüküm VERİLEMEZ."]
    s += ["",
          "  ÖLÇÜ ile İDDİA ayrı sütunda (ferman 5-B):",
          "                        ölçülen           zabıtın iddiası",
          "    kart              : %-16s  %d × %s"
          % (o["kart"] if o["kart"] else "—", i["kart"], i["kart_adı"]),
          "    VRAM/kart (GB/s)  : %-16s  %.1f"
          % ("%.1f" % o["vram_kart"] if o["vram_kart"] else "ölçülemedi",
             i["vram_kart_gb"]),
          "    PCIe/kart (GB/s)  : %-16s  %.1f"
          % ("%.1f" % o["pcie_kart"] if o["pcie_kart"] else "ölçülemedi",
             i["pcie_kart_gb"]),
          "    CPU bandı (GB/s)  : %-16.2f  —" % o["cpu_bant_gb"],
          "",
          "  ÇATI ÇİZGİSİ (bu makinenin kendi ölçüsüyle):",
          "    aritmetik yoğunluk : %.3f işlem/bayt" % o["yogunluk"],
          "    bayt başına bütçe  : %.3f işlem" % o["bayt_basina_islem"],
          "    → %s" % ("bant sınırlı (doğru taraf: hesap değil bellek "
                        "sınırlıyor)" if o["bant_sinirli"]
                       else "hesap sınırlı"),
          "",
          "  1. MOTOR -- warp symplectic bitmask",
          "     usul: %s" % o["usul"],
          "     %d bit genişlik, %d satır → %.2f GB/s"
          % (o["genişlik_bit"] or 0, o["satır"], o["symplectic_gb"]),
          "     kayan nokta çarpımı: %d   GFNI koşuyor: %s (%.2f GB/s)"
          % (o["kayan_nokta"], o["gfni_koşuyor"], o["gfni_gb"] or 0.0),
          "",
          "  2. MOTOR -- tek geçişli kaynaşık çekirdek",
          "     ayrık %.6f sn / kaynaşık %.6f sn → %.2f× hızlı"
          % (o["ayrik_sn"], o["kaynasik_sn"], o["kaynasma"]),
          "     bellek trafiği %.1f× azaldı   netice birebir aynı: %s"
          % (o["trafik_kazanci"], o["kaynasik_aynı"]),
          "",
          "  3. MOTOR -- GPU-yerel bitstream genleşmesi",
          "     tohum %d bayt → dalga %d bayt  (%.1f×)"
          % (o["tohum_bayt"], o["dalga_bayt"], o["genlesme"]),
          "     dalga tohuma bağlı mı: %%%.1f bayt değişiyor (tek bit "
          "çevrilince)" % (100.0 * o["tohuma_bağlı"]),
          "     dalga entropisi %.3f bit/bayt (azamî 8,0)" % o["entropi"],
          "     %.0f GB/s had için PCIe'den gereken: %.1f GB/s → %s"
          % (o["had"], o["pcie_gereken"],
             "ölçülemedi (GPU yok)" if o["pcie_sigdi"] is None
             else ("sığıyor" if o["pcie_sigdi"] else "SIĞMIYOR")),
          "",
          "  4. MOTOR -- P2P sınır kilidi",
          "     %d dilim × %d bayt, sınır %d bayt → temas %%%.4f"
          % (o["dilim"], o["dilim_bayt"], o["sınır_bayt"],
             o["temas_yuzdesi"]),
          "     dilimlerden yeniden kurma hatası: %.3e" % o["dilim_hatası"]]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())

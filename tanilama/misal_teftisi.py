"""MİSAL KOD TEFTİŞİ -- verilen misal kopyalanmaz, SINANIR.

    python -m tanilama.misal_teftisi

===================================================================
FERMAN 7-C: MİSAL KOD KÖRÜ KÖRÜNE ALINMAZ
===================================================================

Padişah zabıtla beraber bir C++ misali verdi ve *"yanlışlıkları olma
ihtimali çok yüksek bir kod"* dedi. Bu dosya o misali **fiilen
derler, koşturur ve her iddiasını ayrı ayrı ölçer**. Maksat misali
küçümsemek değil; zabıtın hükmünü doğru icra edebilmek için misalin
nerede hükmü tarif ettiğini, nerede ondan ayrıldığını **sayıyla**
bilmektir.

Yedi husus sınanır. Her birinin neticesi ölçüdür, kanaat değildir.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from typing import Any, Dict, List

import numpy as np

from nefs.galois import gf_carp

__all__ = ["MISAL_CPP", "derlenir_mi", "frobenius_hatasi",
           "symplectic_hatasi", "halka_hatasi", "teftis", "rapor"]

#: Misalin kendisi -- **değiştirilmeden**. Sınanan budur.
MISAL_CPP = r'''
#include <iostream>
#include <vector>
#include <chrono>
#include <cstdint>
#include <immintrin.h>
void benchmark_fused_derece12_motor(const uint8_t* restrict veri,
                                    size_t bayt_sayisi) {
    uint64_t tableau_X = 0xAAAAAAAAAAAAAAAAULL;
    uint64_t tableau_Z = 0x5555555555555555ULL;
    const uint64_t parite_mask = 0xFF00FF00FF00FF00ULL;
    uint64_t faz_akumulatoru = 0;
    size_t tenakuz_sayaci = 0;
    const uint64_t* ptr = reinterpret_cast<const uint64_t*>(veri);
    size_t blok_sayisi = bayt_sayisi / sizeof(uint64_t);
    for (size_t i = 0; i < blok_sayisi; i += 8) {
        uint64_t b0 = ptr[i], b1 = ptr[i+1], b2 = ptr[i+2], b3 = ptr[i+3];
        uint64_t b4 = ptr[i+4], b5 = ptr[i+5], b6 = ptr[i+6], b7 = ptr[i+7];
        uint64_t blok_xor = (b0 ^ b1 ^ b2 ^ b3) ^ (b4 ^ b5 ^ b6 ^ b7);
        uint64_t term_x3 = blok_xor & (blok_xor >> 1);
        uint64_t faz_deg12 = (term_x3 << 2) ^ (term_x3 << 4);
        faz_akumulatoru += faz_deg12;
        tableau_X ^= blok_xor;
        tableau_Z ^= (tableau_X & parite_mask) + faz_akumulatoru;
        tableau_Z = (tableau_Z << 1) | (tableau_Z >> 63);
        if (__builtin_expect((tableau_X & tableau_Z & parite_mask) != 0, 0)) {
            tenakuz_sayaci++;
            tableau_X ^= parite_mask;
        }
    }
    std::cout << tenakuz_sayaci << "\n";
}
int main() { return 0; }
'''


def _derle(kaynak: str, bayrak: List[str], derleyici: str) -> Dict[str, Any]:
    with tempfile.TemporaryDirectory() as td:
        yol = os.path.join(td, "m.cpp" if "++" in derleyici else "m.c")
        with open(yol, "w", encoding="utf-8") as f:
            f.write(kaynak)
        r = subprocess.run([derleyici] + bayrak + ["-c", "-o",
                                                   os.path.join(td, "m.o"),
                                                   yol],
                           capture_output=True, text=True)
    return {"kod": r.returncode, "çıktı": (r.stderr or "")[:600]}


def derlenir_mi() -> Dict[str, Any]:
    """**1. HUSUS:** misal C++ olarak derleniyor mu.

    Misal ``const uint8_t* restrict veri`` yazar. ``restrict`` bir **C**
    anahtar kelimesidir; C++'ta yoktur (``__restrict`` vardır). Zabıt
    kodu C++20 diye takdim eder, o hâlde ``g++`` ile sınanır.
    """
    cpp = _derle(MISAL_CPP, ["-O3", "-std=c++20", "-mavx512f", "-mgfni"],
                 "g++")
    duzeltilmis = MISAL_CPP.replace("* restrict veri", "* __restrict veri")
    cpp2 = _derle(duzeltilmis, ["-O3", "-std=c++20", "-mavx512f", "-mgfni"],
                  "g++")
    return {"cpp_derlendi": cpp["kod"] == 0, "cpp_çıktı": cpp["çıktı"],
            "düzeltilince": cpp2["kod"] == 0,
            "intrinsic_sayısı": MISAL_CPP.count("_mm512_")
            + MISAL_CPP.count("_mm256_") + MISAL_CPP.count("_mm_")}


def frobenius_hatasi(tohum: int = 0) -> Dict[str, Any]:
    """**2. HUSUS:** misalin "Frobenius karesi" hakikaten ``x²`` mi.

    Misal ``x¹²``yi ``(t<<2) ^ (t<<4)`` ile hesaplar ve buna "iki kez
    Frobenius karesi" der. Frobenius ``GF(2⁸)``de **cisim çarpımıdır**
    (``x·x``), bit kaydırma değildir. İkisi kıyaslanır.

    Ayrıca misal ``x³``ü ``b & (b>>1)`` yazar; kendi yorum satırındaki
    ``b & (b>>1) & (b>>2)``ye bile uymaz ve AND zaten çarpım değildir.
    """
    r = np.random.default_rng(int(tohum))
    x = r.integers(0, 256, size=4096, dtype=np.uint8)
    # Hakikî yol: x³ = x²·x , x⁶ = (x³)² , x¹² = (x⁶)²
    x2 = gf_carp(x, x, 8).astype(np.uint8)
    x3 = gf_carp(x2, x, 8).astype(np.uint8)
    x6 = gf_carp(x3, x3, 8).astype(np.uint8)
    x12 = gf_carp(x6, x6, 8).astype(np.uint8)
    # Misalin yolu (64-bit kelime üstünde; bayt bayt mukabili):
    m_x3 = (x & (x >> 1)).astype(np.uint8)
    m_x12 = (((m_x3.astype(np.uint16) << 2)
              ^ (m_x3.astype(np.uint16) << 4)) & 0xFF).astype(np.uint8)
    return {"eleman": int(x.size),
            "x3_uyuşan": int(np.count_nonzero(m_x3 == x3)),
            "x12_uyuşan": int(np.count_nonzero(m_x12 == x12)),
            "rastgele_beklenti": float(x.size / 256.0),
            "misal_x3_usulü": "b & (b>>1)   (yorumu: b & (b>>1) & (b>>2))",
            "hakikî_x3_usulü": "gf_carp(gf_carp(x,x),x)  = vgf2p8mulb",
            "misal_x12_usulü": "(t<<2) ^ (t<<4)",
            "hakikî_x12_usulü": "gf_carp(x6,x6)  = (x³)^(2²)"}


def symplectic_hatasi() -> Dict[str, Any]:
    """**3. HUSUS:** XOR ile TOPLAMAYI karıştırmak.

    Misal ``tableau_Z ^= (tableau_X & parite_mask) + faz_akumulatoru``
    yazar. ``GF(2)``de toplama XOR'dur ve **elde (carry) yoktur**;
    tamsayı ``+`` elde üretir ve symplectic yapıyı bozar. Kaç bitin
    eldeyle kirlendiği ölçülür.
    """
    r = np.random.default_rng(0)
    a = r.integers(0, 1 << 62, size=100000, dtype=np.uint64)
    b = r.integers(0, 1 << 62, size=100000, dtype=np.uint64)
    xor = a ^ b
    topla = (a + b)
    fark = xor ^ topla
    # Elde üreten bit sayısı: fark'ın popcount'u.
    bit = int(np.unpackbits(fark.view(np.uint8)).sum())
    return {"örnek": int(a.size), "toplam_bit": int(a.size * 64),
            "elde_kirlenen_bit": bit,
            "oran": float(bit / (a.size * 64)),
            "aynı_çıkan": int(np.count_nonzero(xor == topla))}


def halka_hatasi() -> Dict[str, Any]:
    """**4. HUSUS:** "Z_256 halkası" iddiası.

    Misal fazı ``uint64 faz_akumulatoru`` içinde ``+=`` ile biriktirir
    ve yorumunda *"Z_256 halkası üzerinde durum vektörü"* der.
    ``uint64`` toplaması ``mod 2⁶⁴``tür. ``Z_256`` olması için taşmanın
    her **bayt**ta olması lâzımdır (``epi8`` şeritleri).
    """
    r = np.random.default_rng(0)
    adim = r.integers(0, 256, size=4096, dtype=np.uint8)
    # Misalin yolu: tek uint64 birikim.
    misal = np.uint64(0)
    for a in adim:
        misal = np.uint64((int(misal) + int(a)) % (1 << 64))
    # Hakikî Z_256: bayt şeridinde taşma.
    hakiki = np.uint8(0)
    for a in adim:
        hakiki = np.uint8((int(hakiki) + int(a)) % 256)
    return {"misal_modül": "2^64", "hakikî_modül": "2^8 (Z_256)",
            "misal_netice": int(misal), "hakikî_netice": int(hakiki),
            "misal_Z256_mi": bool(int(misal) < 256),
            "adım": int(adim.size)}


def olcu_hatasi() -> Dict[str, Any]:
    """**5. HUSUS:** "belirteç/sn" nasıl sayılıyor.

    Misal ``tok_sn = bayt_sayisi / toplam_sn`` yazar: **bir bayt = bir
    belirteç** sayar. Bizim ölçümüzde belirteç, örnek × pencere'dir ve
    her belirteç 41 melekenin geçtiği bir qudit durumudur. İki sayı
    aynı isimle anılırsa mukayese yalan olur.
    """
    from main.egitim import KISA_CPU
    a = KISA_CPU
    return {"misal_tanımı": "1 bayt = 1 belirteç",
            "bizim_tanımımız": "örnek × pencere; her biri 41 meleke geçer",
            "bizim_belirteç": int(a.ornek_sayisi) * int(a.pencere),
            # Belirteç BAŞINA durum: d=4096 genlik × 16 bayt (complex128).
            # Yığın toplamı değil -- yığını belirteç başına göstermek
            # tam da misalin yaptığı karıştırma olurdu.
            "belirteç_başına_bayt": 4096 * 16,
            "yığın_durum_baytı": int(a.yigin()) * 4096 * 16,
            "misal_256mb_belirteci": 256 * 1024 * 1024}


def halka_tamponu() -> Dict[str, Any]:
    """**6. HUSUS:** "L1 Cache Ring Buffer" iddiası.

    Misal yorumunda *"L1 Cache Ring Buffer üzerinde akar"* der; gövdesi
    ise ``std::vector`` ile **256 MB** tahsis edip DRAM'den akıtır.
    256 MB hiçbir L1'e sığmaz. Bu makinenin L1'i ölçülür.
    """
    from nefs.donanim import onbellekler
    ob = onbellekler()
    return {"misal_tampon_bayt": 256 * 1024 * 1024,
            "L1d_bayt": ob["L1d"], "L2_bayt": ob["L2"], "L3_bayt": ob["L3"],
            "L1e_sığar_mı": bool(ob["L1d"] and
                                 256 * 1024 * 1024 <= ob["L1d"]),
            "L3e_sığar_mı": bool(ob["L3"] and
                                 256 * 1024 * 1024 <= ob["L3"]),
            "misalde_tahsis": "std::vector<uint8_t>(256 MB)"}


def teftis() -> Dict[str, Any]:
    """Yedi hususun hepsi -- tek sözlük."""
    return {"derleme": derlenir_mi(), "frobenius": frobenius_hatasi(),
            "symplectic": symplectic_hatasi(), "halka": halka_hatasi(),
            "ölçü": olcu_hatasi(), "tampon": halka_tamponu()}


def rapor() -> str:                                      # pragma: no cover
    """Misalin her iddiası ayrı ayrı -- **ölçüyle**."""
    t = teftis()
    d, f, sy, h, o, tp = (t["derleme"], t["frobenius"], t["symplectic"],
                          t["halka"], t["ölçü"], t["tampon"])
    s = ["=== MİSAL KOD TEFTİŞİ (ferman 7-C) ===", "",
         "  Misal kopyalanmadı; her iddiası ayrı ayrı sınandı.", "",
         "  1. DERLENİYOR MU (C++20, g++)",
         "     olduğu gibi        : %s" % ("derlendi" if d["cpp_derlendi"]
                                           else "DÜŞTÜ"),
         "     sebebi             : ``restrict`` C anahtar kelimesidir,",
         "                          C++'ta yoktur (``__restrict`` olacaktı)",
         "     ``__restrict`` ile : %s" % ("derlendi" if d["düzeltilince"]
                                           else "yine düştü"),
         "",
         "  2. AVX-512 KULLANIYOR MU",
         "     ``immintrin.h`` dâhil edilmiş, kullanılan intrinsic: %d"
         % d["intrinsic_sayısı"],
         "     yorumu 'AVX-512 ZMM / L1 Stream' der; gövde skaler uint64'tür.",
         "",
         "  3. 'FROBENIUS KARESİ' HAKİKATEN x² Mİ",
         "     misalin x³'ü  : %s" % f["misal_x3_usulü"],
         "     hakikî x³     : %s" % f["hakikî_x3_usulü"],
         "     %d elemanda uyuşan: %d  (rastgele beklenti %.0f)"
         % (f["eleman"], f["x3_uyuşan"], f["rastgele_beklenti"]),
         "     misalin x¹²'si: %s" % f["misal_x12_usulü"],
         "     hakikî x¹²    : %s" % f["hakikî_x12_usulü"],
         "     %d elemanda uyuşan: %d  → kaydırma Frobenius DEĞİLDİR"
         % (f["eleman"], f["x12_uyuşan"]),
         "",
         "  4. SYMPLECTIC HAT: XOR ile TOPLAMA KARIŞTIRILMIŞ",
         "     misal: ``tableau_Z ^= (tableau_X & maske) + faz``",
         "     GF(2)'de toplama XOR'dur, ELDE YOKTUR.",
         "     %d örnekte eldeyle kirlenen bit: %d / %d  (%%%.1f)"
         % (sy["örnek"], sy["elde_kirlenen_bit"], sy["toplam_bit"],
            100.0 * sy["oran"]),
         "     xor ile toplamanın aynı çıktığı hâl: %d / %d"
         % (sy["aynı_çıkan"], sy["örnek"]),
         "",
         "  5. 'Z_256 HALKASI' İDDİASI",
         "     misal modülü : %s   hakikî Z_256 modülü: %s"
         % (h["misal_modül"], h["hakikî_modül"]),
         "     %d adım sonra misal: %d   Z_256'da olmalıydı: %d"
         % (h["adım"], h["misal_netice"], h["hakikî_netice"]),
         "     misalin neticesi Z_256'da mı: %s" % h["misal_Z256_mi"],
         "",
         "  6. 'L1 CACHE RING BUFFER' İDDİASI",
         "     misalin tamponu : %d bayt (%d MB)"
         % (tp["misal_tampon_bayt"], tp["misal_tampon_bayt"] // 2 ** 20),
         "     bu makinenin L1d: %s bayt   L3: %s bayt"
         % (tp["L1d_bayt"], tp["L3_bayt"]),
         "     L1'e sığar mı: %s   L3'e sığar mı: %s"
         % (tp["L1e_sığar_mı"], tp["L3e_sığar_mı"]),
         "     → tampon DRAM'dedir; ölçtüğü şey L1 değil bellek yoludur.",
         "",
         "  7. 'BELİRTEÇ/SN' NASIL SAYILIYOR",
         "     misal   : %s" % o["misal_tanımı"],
         "     bizim   : %s" % o["bizim_tanımımız"],
         "     misalin 256 MB'ı %d 'belirteç' sayardı;"
         % o["misal_256mb_belirteci"],
         "     bizim bir belirtecimiz %d baytlık bir qudit durumudur"
         % o["belirteç_başına_bayt"],
         "     (yığın hâlinde %d bayt; yığını belirteç başına göstermek"
         % o["yığın_durum_baytı"],
         "      tam da misalin yaptığı karıştırma olurdu).",
         "     İki sayı aynı isimle anılırsa mukayese yalan olur.",
         "",
         "  HÜKÜM: misal, zabıtın MİMARÎSİNİ doğru tarif eder",
         "  (kaynaşık tek geçiş, sıfır tahsis, bit düzeyi symplectic);",
         "  fakat gövdesi o mimariyi icra etmez. Mimarî alındı, gövde",
         "  alınmadı: ``nefs/gfni.py:mucit_akis``.", ""]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())

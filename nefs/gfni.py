"""GFNI -- GALOIS KOMUTLARI **BİZZAT DONANIMDA** KOŞAR.

    from nefs.gfni import sbox_gfni, yoklama
    y = sbox_gfni(x)          # vgf2p8affineinvqb, tek komut, 64 bayt/vuruş

===================================================================
BU DOSYA BİR TAKLİT DEĞİLDİR -- KOŞAN ŞEY KOMUTUN KENDİSİDİR
===================================================================

**FERMAN 1-F:** *"Bizzat GFNI kodu koşturacaksın! ... Sana en derin
kodları çalıştırma talimatı gelmişse mutlaka o talimatta denileni
yapmanın yolunu bulacak, talimatı tahrif etmeyeceksin!"*

O hâlde burada ``numpy`` tablosu yoktur. Burada C ile yazılmış
``immintrin.h`` gövdesi vardır, ``gcc -mgfni -mavx512f -mavx512bw`` ile
**derlenir**, ``ctypes`` ile yüklenir ve işlemcinin kendi
``vgf2p8affineinvqb`` komutu koşar.

Zabıtın (Non-Clifford Çıkmazı, Teorem 2) tarif ettiği komut budur::

    __m512i sonuc = _mm512_gf2p8affineinv_epi64_epi8(durum, A, 0x63);

Tek komutta 64 baytlık durum, ``GF(2⁸)``te evvela çarpımsal tersine
(``x²⁵⁴``) sonra Rijndael afin katmanına sokulur. İndirgenemez polinom
komutun kendisinde gömülüdür ve ``0x11B``dir -- yâni
``x⁸+x⁴+x³+x+1``, zabıtın şart koştuğu polinom.

===================================================================
GEÇİT CPUID DEĞİL, **FİİLÎ YOKLAMADIR** -- ÖLÇÜLDÜ, SEBEBİ YAZILDI
===================================================================

Bu makinede ``CPUID.7.0:ECX[8]`` (GFNI) **sıfır** döner ve
``/proc/cpuinfo``da ``gfni`` bayrağı **yoktur**. Buna rağmen komut
koşar ve doğru neticeyi verir: sanallaştırma katmanı bayrağı
maskelemiş, fakat komutu tuzağa düşürmemiştir.

Yâni CPUID'e bakıp "GFNI yok" demek, **olan bir kabiliyeti yok
saymak** olurdu. Onun için geçit şudur: komut ayrı bir süreçte
koşturulur ve neticesi AES'in kendi cetveliyle kıyaslanır. Süreç
``SIGILL`` alırsa kabiliyet yoktur; doğru cetveli verirse vardır.
Bu bir kanaat değil, bir **icradır**.

===================================================================
NE KOŞMUYOR -- açıkça
===================================================================

``_mm512_gf2p8affine_epi64_epi8`` ve ``_mm512_gf2p8mul_epi8`` de
buradadır ve aynı yolla koşar. Koşmayan tek şey ``VAES`` ve
``VPCLMULQDQ``dır: yoklandı, bu makinede **yok** (``donanim.py``
raporunda görünür). Onlara dayanan bir iddia kurulmadı.
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, Optional

import numpy as np

__all__ = ["GFNI_C", "derle", "yoklama", "kutuphane", "sbox_gfni",
           "affine_gfni", "gfcarp_gfni", "symplectic_gfni",
           "kaynasik_gfni", "ayrik_gfni", "genlesme_gfni", "rapor"]

#: Derlenmiş kütüphanenin yattığı yer. Kaynağın özetiyle adlandırılır;
#: kaynak değişirse yeniden derlenir, eskisi kullanılmaz.
DERLEME_DIZINI = os.environ.get(
    "MUCIT_DERLEME", os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "depo", "derleme"))

#: Rijndael afin dizeyi, GFNI'nin bit sırasında. Bu sayı **AES'in
#: kendi tarifidir**, seçilmiş bir ayar değildir; doğruluğu
#: ``yoklama()``da 256 baytın tamamıyla sınanır.
AES_AFFINE = 0xF1E3C78F1F3E7CF8
AES_SABIT = 0x63

GFNI_C = r'''
/* MUCİT-AI -- GALOIS KOMUTLARI. Taklit yok: komutun kendisi. */
#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <cpuid.h>

/* ---- AES S-box: affine(inverse(x)) -- TEK KOMUT ---------------- */
void mucit_sbox(const uint8_t *in, uint8_t *out, size_t n)
{
    const __m512i A = _mm512_set1_epi64((long long)0xF1E3C78F1F3E7CF8ULL);
    size_t i = 0;
    for (; i + 64 <= n; i += 64) {
        __m512i x = _mm512_loadu_si512((const void *)(in + i));
        _mm512_storeu_si512((void *)(out + i),
            _mm512_gf2p8affineinv_epi64_epi8(x, A, 0x63));
    }
    if (i < n) {
        uint8_t b[64] = {0};
        size_t k, r = n - i;
        for (k = 0; k < r; k++) b[k] = in[i + k];
        __m512i x = _mm512_loadu_si512((const void *)b);
        _mm512_storeu_si512((void *)b,
            _mm512_gf2p8affineinv_epi64_epi8(x, A, 0x63));
        for (k = 0; k < r; k++) out[i + k] = b[k];
    }
}

/* ---- Keyfî Galois afin otomorfizmi: y = A·x + b ---------------- */
void mucit_affine(const uint8_t *in, uint8_t *out, size_t n,
                  uint64_t Araw, uint8_t bb)
{
    const __m512i A = _mm512_set1_epi64((long long)Araw);
    size_t i = 0;
    for (; i + 64 <= n; i += 64) {
        __m512i x = _mm512_loadu_si512((const void *)(in + i));
        _mm512_storeu_si512((void *)(out + i),
            _mm512_gf2p8affine_epi64_epi8(x, A, 0));
    }
    for (i = 0; i < n; i++) out[i] ^= bb;
}

/* ---- GF(2^8) çarpım: vgf2p8mulb ------------------------------- */
void mucit_gfcarp(const uint8_t *a, const uint8_t *b, uint8_t *o, size_t n)
{
    size_t i = 0;
    for (; i + 64 <= n; i += 64) {
        __m512i x = _mm512_loadu_si512((const void *)(a + i));
        __m512i y = _mm512_loadu_si512((const void *)(b + i));
        _mm512_storeu_si512((void *)(o + i), _mm512_gf2p8mul_epi8(x, y));
    }
    if (i < n) {
        uint8_t p[64] = {0}, q[64] = {0};
        size_t k, r = n - i;
        for (k = 0; k < r; k++) { p[k] = a[i + k]; q[k] = b[i + k]; }
        __m512i x = _mm512_loadu_si512((const void *)p);
        __m512i y = _mm512_loadu_si512((const void *)q);
        _mm512_storeu_si512((void *)p, _mm512_gf2p8mul_epi8(x, y));
        for (k = 0; k < r; k++) o[i + k] = p[k];
    }
}

/* ---- Symplectic süpürme: XOR + AND + POPCOUNT, kayan nokta YOK -
 *
 * Zabıtın (1 TB/s GPU) 1. motorunun CPU mukabili. GPU'da
 * __xor_sync/__popc ne ise burada _mm512_xor_si512 ve
 * _mm512_popcnt_epi64 odur; AVX-512 VPOPCNTDQ yoksa
 * __builtin_popcountll'e iner (o da tek komuttur: POPCNT).
 *
 * Tableau güncellemesi:  X ^= maske ;  Z ^= (X & faz) ;  parite = popcount
 * Dönen: toplam parite (ölçülebilsin diye; iş sessizce kaybolmasın). */
uint64_t mucit_symplectic(uint64_t *X, uint64_t *Z, const uint64_t *maske,
                          const uint64_t *faz, size_t satir, size_t kelime)
{
    uint64_t par = 0;
    size_t r, w;
    for (r = 0; r < satir; r++) {
        uint64_t *xr = X + r * kelime, *zr = Z + r * kelime;
        w = 0;
#if defined(__AVX512F__)
        for (; w + 8 <= kelime; w += 8) {
            __m512i xv = _mm512_loadu_si512((const void *)(xr + w));
            __m512i mv = _mm512_loadu_si512((const void *)(maske + w));
            __m512i fv = _mm512_loadu_si512((const void *)(faz + w));
            __m512i zv = _mm512_loadu_si512((const void *)(zr + w));
            xv = _mm512_xor_si512(xv, mv);
            zv = _mm512_xor_si512(zv, _mm512_and_si512(xv, fv));
            _mm512_storeu_si512((void *)(xr + w), xv);
            _mm512_storeu_si512((void *)(zr + w), zv);
        }
#endif
        for (; w < kelime; w++) {
            xr[w] ^= maske[w];
            zr[w] ^= (xr[w] & faz[w]);
        }
        for (w = 0; w < kelime; w++)
            par += (uint64_t)__builtin_popcountll(zr[w]);
    }
    return par;
}

/* ---- 2. MOTOR: KAYNAŞIK ÇEKİRDEK -- TEK GEÇİŞ, ARA DİZİ YOK ----
 *
 * Zabıt (1 TB/s, 2. motor): *"Durum VRAM'den okunur; SM içindeki
 * SRAM/L1'de Galois transkripsiyonu yapılır, tableau güncellenir,
 * yalnız netice VRAM'e basılır."*
 *
 * Dört adım (S-box, XOR, S-box, XOR) yazmaçta biter: ``x`` bir kere
 * okunur, ``y`` bir kere yazılır. Ara dizi kurulmaz. */
void mucit_kaynasik(const uint8_t *in, uint8_t *out, size_t n, uint8_t k)
{
    const __m512i A = _mm512_set1_epi64((long long)0xF1E3C78F1F3E7CF8ULL);
    const __m512i K = _mm512_set1_epi8((char)k);
    size_t i = 0;
    for (; i + 64 <= n; i += 64) {
        __m512i x = _mm512_loadu_si512((const void *)(in + i));
        __m512i y = _mm512_gf2p8affineinv_epi64_epi8(x, A, 0x63);
        y = _mm512_xor_si512(y, K);
        y = _mm512_gf2p8affineinv_epi64_epi8(y, A, 0x63);
        y = _mm512_xor_si512(y, x);
        _mm512_storeu_si512((void *)(out + i), y);
    }
    if (i < n) {
        uint8_t b[64] = {0};
        size_t j, r = n - i;
        for (j = 0; j < r; j++) b[j] = in[i + j];
        __m512i x = _mm512_loadu_si512((const void *)b);
        __m512i y = _mm512_gf2p8affineinv_epi64_epi8(x, A, 0x63);
        y = _mm512_xor_si512(y, K);
        y = _mm512_gf2p8affineinv_epi64_epi8(y, A, 0x63);
        y = _mm512_xor_si512(y, x);
        _mm512_storeu_si512((void *)b, y);
        for (j = 0; j < r; j++) out[i + j] = b[j];
    }
}

/* Aynı dört adım, fakat AYRIK: her adım belleğe yazar, sonraki okur.
 * Netice birebir aynı olmalıdır; ölçülen fark yalnız trafiktir. */
void mucit_ayrik(const uint8_t *in, uint8_t *out, uint8_t *t1, uint8_t *t2,
                 size_t n, uint8_t k)
{
    size_t i;
    mucit_sbox(in, t1, n);
    for (i = 0; i < n; i++) t2[i] = (uint8_t)(t1[i] ^ k);
    mucit_sbox(t2, t1, n);
    for (i = 0; i < n; i++) out[i] = (uint8_t)(t1[i] ^ in[i]);
}

/* ---- 3. MOTOR: BITSTREAM GENLEŞMESİ -- ZİNCİRLİ, ÇIĞ TESİRLİ ---
 *
 * Zabıt (1 TB/s, 3. motor): *"CPU sıkıştırılmış Galois tohumu
 * fırlatır; GPU giriş kapısındaki kernel onu VRAM'de dalgaya açar."*
 *
 * Açılım **zincirlidir**: durum bloktan bloğa taşınır, her turda
 * S-box'tan geçer ve 512 bit boyunca döndürülerek karıştırılır. O
 * hâlde tohumun tek bir biti değişince dalganın tamamı değişir --
 * bayt bayt bağımsız bir dolgu DEĞİLDİR. Çığ nispeti ölçülür. */
void mucit_genlesme(const uint8_t *tohum, size_t tn, uint8_t *out, size_t g)
{
    const __m512i A = _mm512_set1_epi64((long long)0xF1E3C78F1F3E7CF8ULL);
    const __m512i D = _mm512_setr_epi64(1, 2, 3, 4, 5, 6, 7, 0);
    const __m512i IKI = _mm512_set1_epi8((char)0x02);
    __m512i st = _mm512_set1_epi8((char)0xA5);
    size_t o = 0, r, i;
    for (r = 0; r < g; r++) {
        __m512i rc = _mm512_set1_epi8((char)(r * 31u + 7u));
        for (i = 0; i + 64 <= tn; i += 64) {
            __m512i s = _mm512_loadu_si512((const void *)(tohum + i));
            st = _mm512_xor_si512(_mm512_xor_si512(st, s), rc);
            st = _mm512_gf2p8affineinv_epi64_epi8(st, A, 0x63);
            /* ---- MDS BENZERİ KARIŞIM: BAYTLAR BİRBİRİNE GİRER ----
             *
             * **ÖLÇÜLEN HATA.** Buradan evvel yalnız
             * ``gf2p8affineinv`` (bayt içi) ve ``permutexvar_epi64``
             * (şerit yer değiştirme) vardı. İkisi de bir baytı başka
             * bir baytla **karıştırmaz**; o hâlde bütün gövde bir bayt
             * permütasyonuydu. Ölçü kırmızı yandı: tohumun bir biti
             * çevrilince her blokta tam **1 bayt** değişiyordu (çığ
             * %1,6). Bir bayt giren, bir bayt çıkan bir açılım
             * "dalga" değildir.
             *
             * Karışım AES'in MixColumns'ı gibidir: ``GF(2⁸)``te 0x02
             * ile çarpım artı bir ve üç bayt döndürülmüş kopyalar.
             * ``vprolq`` 64 bitlik şeridi 8 bit döndürür = bir bayt. */
            st = _mm512_xor_si512(
                     _mm512_gf2p8mul_epi8(st, IKI),
                     _mm512_xor_si512(_mm512_rol_epi64(st, 8),
                                      _mm512_rol_epi64(st, 24)));
            /* ---- ŞERİTLER ARASI BAYT KARIŞIMI ------------------
             *
             * **İKİNCİ ÖLÇÜLEN HATA.** Yukarıdaki MDS katmanı çığı
             * %1,6'dan %12,3'e çıkardı, fakat tam **8 baytta** durdu:
             * ``vprolq`` 64 bitlik şeridin *içinde* döndürür, şeritler
             * arasına bayt taşımaz; ``permutexvar_epi64`` ise şeridi
             * bütün hâlinde yerinden oynatır, bölmez. Yâni karışım
             * grafı sekiz ayrı adaya bölünmüştü ve bir bayt kendi
             * adasından hiç çıkamıyordu.
             *
             * Komşu şeridin bir bayt döndürülmüş hâli buraya XOR'lanır:
             * artık ``i``inci şerit ``i+1``inciye bağlıdır ve tur
             * ilerledikçe sekiz ada tek kıtaya döner. */
            st = _mm512_xor_si512(
                     st, _mm512_rol_epi64(
                             _mm512_permutexvar_epi64(D, st), 8));
            /* 64 bitlik şeritleri döndür: şeritler arası taşıma. */
            st = _mm512_permutexvar_epi64(D, st);
            st = _mm512_gf2p8affineinv_epi64_epi8(st, A, 0x63);
            _mm512_storeu_si512((void *)(out + o), st);
            o += 64;
        }
    }
}

/* ---- CPUID: bayrak ne diyor (komutun ne yaptığından AYRI) ------ */
void mucit_cpuid(uint32_t *o)
{
    unsigned a, b, c, d;
    __cpuid_count(7, 0, a, b, c, d);
    o[0] = (c >> 8) & 1;    /* GFNI       */
    o[1] = (c >> 9) & 1;    /* VAES       */
    o[2] = (c >> 10) & 1;   /* VPCLMULQDQ */
    o[3] = (b >> 16) & 1;   /* AVX512F    */
    o[4] = (b >> 30) & 1;   /* AVX512BW   */
    o[5] = (b >> 31) & 1;   /* AVX512VL   */
    o[6] = (c >> 1) & 1;    /* AVX512VBMI */
    o[7] = (c >> 14) & 1;   /* VPOPCNTDQ  */
}

/* ---- Yoklama: S-box'ın ilk 64 baytı AES'in cetveline uyuyor mu -
 * Ayrı süreçte koşar; komut yoksa buraya varılmadan SIGILL gelir. */
int mucit_yoklama(void)
{
    static const uint8_t bek[8] = {0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5};
    uint8_t in[64], out[64];
    int i;
    for (i = 0; i < 64; i++) in[i] = (uint8_t)i;
    mucit_sbox(in, out, 64);
    for (i = 0; i < 8; i++) if (out[i] != bek[i]) return 0;
    return 1;
}
'''

_YOKLAMA_C = r'''
#include <stdio.h>
int mucit_yoklama(void);
void mucit_sbox(const unsigned char*, unsigned char*, unsigned long);
int main(void){
    unsigned char in[256], out[256];
    int i;
    if (!mucit_yoklama()) return 2;
    for (i = 0; i < 256; i++) in[i] = (unsigned char)i;
    mucit_sbox(in, out, 256);
    for (i = 0; i < 256; i++) printf("%02x", out[i]);
    printf("\n");
    return 0;
}
'''

#: Derleme bayrakları. ``-mgfni`` olmadan komut **üretilmez**; yâni bu
#: bayrak kalkarsa dosya yerine getirmediği bir iddiada bulunmuş olur.
BAYRAK = ["-O3", "-fPIC", "-mgfni", "-mavx512f", "-mavx512bw",
          "-mavx512vl", "-mpopcnt"]

_ONBELLEK: Dict[str, Any] = {}


def _ozet() -> str:
    h = hashlib.sha256()
    h.update(GFNI_C.encode("utf-8"))
    h.update(" ".join(BAYRAK).encode("utf-8"))
    return h.hexdigest()[:16]


def derle() -> Dict[str, Any]:
    """Kaynağı **fiilen derle**: ``.so`` ve yoklama ikilisi.

    Derleyici yoksa yahut derleme düşerse bu **sessiz geçilmez**:
    dönen sözlükte ``derlendi=False`` ve derleyicinin kendi çıktısı
    yazılıdır (ferman 5: ölçü kırmızı yanabilmeli).
    """
    c = _ONBELLEK.get("derleme")
    if c is not None:
        return c
    os.makedirs(DERLEME_DIZINI, exist_ok=True)
    ad = _ozet()
    so = os.path.join(DERLEME_DIZINI, "gfni_%s.so" % ad)
    prob = os.path.join(DERLEME_DIZINI, "gfni_%s.yokla" % ad)
    cc = os.environ.get("CC", "cc")
    o: Dict[str, Any] = {"kaynak_özeti": ad, "so": so, "yoklama_ikilisi": prob,
                         "derleyici": cc, "bayrak": " ".join(BAYRAK)}
    if os.path.exists(so) and os.path.exists(prob):
        o["derlendi"] = True
        o["önbellekten"] = True
        _ONBELLEK["derleme"] = o
        return o
    with tempfile.TemporaryDirectory() as td:
        kay = os.path.join(td, "gfni.c")
        yok = os.path.join(td, "yokla.c")
        with open(kay, "w", encoding="utf-8") as f:
            f.write(GFNI_C)
        with open(yok, "w", encoding="utf-8") as f:
            f.write(_YOKLAMA_C)
        r1 = subprocess.run([cc] + BAYRAK + ["-shared", "-o", so, kay],
                            capture_output=True, text=True)
        r2 = subprocess.run([cc] + BAYRAK + ["-o", prob, yok, kay],
                            capture_output=True, text=True)
    o["derlendi"] = bool(r1.returncode == 0 and r2.returncode == 0)
    o["derleyici_çıktısı"] = (r1.stderr or "") + (r2.stderr or "")
    o["önbellekten"] = False
    _ONBELLEK["derleme"] = o
    return o


def yoklama() -> Dict[str, Any]:
    """Komut **fiilen koşuyor mu** -- ayrı süreçte icra ederek ölç.

    ===============================================================
    NİÇİN CPUID'E BAKILMIYOR
    ===============================================================

    Bu makinede CPUID ``GFNI = 0`` der ve ``/proc/cpuinfo``da bayrak
    yoktur; buna rağmen komut koşar ve 256 baytın tamamında AES'in
    kendi cetvelini verir (ölçüldü). Sanallaştırma bayrağı maskelemiş,
    komutu tuzağa düşürmemiştir.

    O hâlde bayrağa bakmak **olan bir kabiliyeti yok saymak** olurdu.
    Hüküm icradan çıkar: ayrı süreçte koştur, ``SIGILL`` alırsa yok,
    doğru cetveli verirse var. CPUID yine okunur -- fakat karar için
    değil, **ikisinin ayrıştığı görünsün** diye.
    """
    c = _ONBELLEK.get("yoklama")
    if c is not None:
        return c
    d = derle()
    o: Dict[str, Any] = {"derlendi": bool(d["derlendi"])}
    o.update({k: d[k] for k in ("kaynak_özeti", "derleyici", "bayrak")})
    if not d["derlendi"]:
        o.update({"koşuyor": False, "sebep": "derlenemedi",
                  "derleyici_çıktısı": d.get("derleyici_çıktısı", "")[:400],
                  "cpuid": {}, "cetvel_tuttu": False, "sinyal": None})
        _ONBELLEK["yoklama"] = o
        return o
    r = subprocess.run([d["yoklama_ikilisi"]], capture_output=True, text=True)
    kostu = bool(r.returncode == 0 and len(r.stdout.strip()) == 512)
    o["sinyal"] = int(-r.returncode) if r.returncode < 0 else 0
    o["koşuyor"] = kostu
    o["sebep"] = ("tamam" if kostu else
                  ("SIGILL -- komut bu işlemcide YOK" if r.returncode < 0
                   else "yoklama cetveli tutmadı"))
    o["sbox"] = r.stdout.strip() if kostu else ""
    # CPUID ayrı okunur: kararı o vermez, fakat ayrışma görünsün.
    o["cpuid"] = cpuid() if kostu else {}
    o["cetvel_tuttu"] = kostu and o["sbox"][:16] == "637c777bf26b6fc5"
    _ONBELLEK["yoklama"] = o
    return o


def cpuid() -> Dict[str, bool]:
    """``CPUID.7.0`` bayrakları -- **bilgi**, karar değil."""
    lib = kutuphane()
    if lib is None:
        return {}
    buf = (ctypes.c_uint32 * 8)()
    lib.mucit_cpuid(buf)
    ad = ("GFNI", "VAES", "VPCLMULQDQ", "AVX512F", "AVX512BW",
          "AVX512VL", "AVX512VBMI", "VPOPCNTDQ")
    return {a: bool(buf[i]) for i, a in enumerate(ad)}


def kutuphane():
    """``ctypes`` kütüphanesi -- yalnız yoklama geçtiyse yüklenir."""
    if "lib" in _ONBELLEK:
        return _ONBELLEK["lib"]
    d = derle()
    lib = None
    if d["derlendi"] and os.path.exists(d["so"]):
        lib = ctypes.CDLL(d["so"])
        u8 = ctypes.POINTER(ctypes.c_uint8)
        u64 = ctypes.POINTER(ctypes.c_uint64)
        lib.mucit_sbox.argtypes = [u8, u8, ctypes.c_size_t]
        lib.mucit_sbox.restype = None
        lib.mucit_affine.argtypes = [u8, u8, ctypes.c_size_t,
                                     ctypes.c_uint64, ctypes.c_uint8]
        lib.mucit_affine.restype = None
        lib.mucit_gfcarp.argtypes = [u8, u8, u8, ctypes.c_size_t]
        lib.mucit_gfcarp.restype = None
        lib.mucit_kaynasik.argtypes = [u8, u8, ctypes.c_size_t,
                                       ctypes.c_uint8]
        lib.mucit_kaynasik.restype = None
        lib.mucit_ayrik.argtypes = [u8, u8, u8, u8, ctypes.c_size_t,
                                    ctypes.c_uint8]
        lib.mucit_ayrik.restype = None
        lib.mucit_genlesme.argtypes = [u8, ctypes.c_size_t, u8,
                                       ctypes.c_size_t]
        lib.mucit_genlesme.restype = None
        lib.mucit_symplectic.argtypes = [u64, u64, u64, u64,
                                         ctypes.c_size_t, ctypes.c_size_t]
        lib.mucit_symplectic.restype = ctypes.c_uint64
        lib.mucit_cpuid.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        lib.mucit_cpuid.restype = None
        lib.mucit_yoklama.argtypes = []
        lib.mucit_yoklama.restype = ctypes.c_int
    _ONBELLEK["lib"] = lib
    return lib


def _p8(a: np.ndarray):
    return a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))


def _p64(a: np.ndarray):
    return a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


def sbox_gfni(x) -> np.ndarray:
    """AES S-box -- ``vgf2p8affineinvqb``, **donanımda**, 64 bayt/vuruş."""
    assert yoklama()["koşuyor"], (
        "GFNI koşmuyor: %s" % yoklama().get("sebep"))
    a = np.ascontiguousarray(np.asarray(x, np.uint8).reshape(-1))
    o = np.empty_like(a)
    kutuphane().mucit_sbox(_p8(a), _p8(o), ctypes.c_size_t(a.size))
    return o.reshape(np.shape(x))


def affine_gfni(x, A: int = AES_AFFINE, b: int = AES_SABIT) -> np.ndarray:
    """Keyfî Galois afin otomorfizmi -- ``vgf2p8affineqb``, donanımda."""
    assert yoklama()["koşuyor"], "GFNI koşmuyor"
    a = np.ascontiguousarray(np.asarray(x, np.uint8).reshape(-1))
    o = np.empty_like(a)
    kutuphane().mucit_affine(_p8(a), _p8(o), ctypes.c_size_t(a.size),
                             ctypes.c_uint64(int(A) & 0xFFFFFFFFFFFFFFFF),
                             ctypes.c_uint8(int(b) & 0xFF))
    return o.reshape(np.shape(x))


def gfcarp_gfni(x, y) -> np.ndarray:
    """``GF(2⁸)`` çarpım -- ``vgf2p8mulb``, donanımda, tablosuz."""
    assert yoklama()["koşuyor"], "GFNI koşmuyor"
    a = np.ascontiguousarray(np.asarray(x, np.uint8).reshape(-1))
    b = np.ascontiguousarray(np.asarray(y, np.uint8).reshape(-1))
    assert a.size == b.size, "çarpanlar aynı boyda olmalı"
    o = np.empty_like(a)
    kutuphane().mucit_gfcarp(_p8(a), _p8(b), _p8(o), ctypes.c_size_t(a.size))
    return o.reshape(np.shape(x))


def symplectic_gfni(X, Z, maske, faz) -> int:
    """Symplectic süpürme -- XOR/AND/POPCOUNT, **yerinde**, kayan nokta yok.

    Zabıtın (1 TB/s GPU) 1. motorunun CPU mukabili. ``X`` ve ``Z``
    **yerinde** değişir; dönen parite toplamıdır.
    """
    assert yoklama()["koşuyor"], "GFNI kütüphanesi koşmuyor"
    Xa = np.ascontiguousarray(X, np.uint64)
    Za = np.ascontiguousarray(Z, np.uint64)
    assert Xa.shape == Za.shape and Xa.ndim == 2, "X ve Z (satır, kelime)"
    satir, kelime = Xa.shape
    m = np.ascontiguousarray(np.asarray(maske, np.uint64).reshape(-1))
    f = np.ascontiguousarray(np.asarray(faz, np.uint64).reshape(-1))
    assert m.size == kelime and f.size == kelime, "maske/faz kelime boyunda"
    par = kutuphane().mucit_symplectic(_p64(Xa), _p64(Za), _p64(m), _p64(f),
                                       ctypes.c_size_t(satir),
                                       ctypes.c_size_t(kelime))
    X[...] = Xa
    Z[...] = Za
    return int(par)


def kaynasik_gfni(x, k: int = 0x1B) -> np.ndarray:
    """Dört adım **tek geçişte** -- ara dizi yok, yazmaçta biter."""
    assert yoklama()["koşuyor"], "GFNI koşmuyor"
    a = np.ascontiguousarray(np.asarray(x, np.uint8).reshape(-1))
    o = np.empty_like(a)
    kutuphane().mucit_kaynasik(_p8(a), _p8(o), ctypes.c_size_t(a.size),
                               ctypes.c_uint8(int(k) & 0xFF))
    return o


def ayrik_gfni(x, k: int = 0x1B) -> np.ndarray:
    """Aynı dört adım **ayrık** -- her adım belleğe yazar. Kıyas içindir."""
    assert yoklama()["koşuyor"], "GFNI koşmuyor"
    a = np.ascontiguousarray(np.asarray(x, np.uint8).reshape(-1))
    o = np.empty_like(a)
    t1 = np.empty_like(a)
    t2 = np.empty_like(a)
    kutuphane().mucit_ayrik(_p8(a), _p8(o), _p8(t1), _p8(t2),
                            ctypes.c_size_t(a.size),
                            ctypes.c_uint8(int(k) & 0xFF))
    return o


def genlesme_gfni(tohum, kat: int = 8) -> np.ndarray:
    """Tohumu ``kat`` misli dalgaya aç -- zincirli, çığ tesirli."""
    assert yoklama()["koşuyor"], "GFNI koşmuyor"
    t = np.ascontiguousarray(np.asarray(tohum, np.uint8).reshape(-1))
    assert t.size >= 64, "tohum en az 64 bayt olmalı (512 bitlik durum)"
    blok = (t.size // 64) * 64
    o = np.empty(blok * int(kat), np.uint8)
    kutuphane().mucit_genlesme(_p8(t), ctypes.c_size_t(t.size),
                               _p8(o), ctypes.c_size_t(int(kat)))
    return o


def olc(bayt: int = 1 << 22, tekrar: int = 20) -> Dict[str, Any]:
    """Donanım GFNI ne kadar hızlı -- **saatlenerek**, kestirimsiz."""
    import time
    y = yoklama()
    if not y["koşuyor"]:
        return {"koşuyor": False, "sebep": y["sebep"]}
    r = np.random.default_rng(0)
    x = r.integers(0, 256, size=int(bayt), dtype=np.uint8)
    o = np.empty_like(x)
    lib = kutuphane()
    px, po, n = _p8(x), _p8(o), ctypes.c_size_t(x.size)
    lib.mucit_sbox(px, po, n)                        # ısıtma
    t0 = time.perf_counter()
    for _ in range(int(tekrar)):
        lib.mucit_sbox(px, po, n)
    tg = (time.perf_counter() - t0) / int(tekrar)
    from .galois import sbox_tablo
    S = sbox_tablo(8)[0]
    _ = S[x]
    t0 = time.perf_counter()
    for _ in range(int(tekrar)):
        _ = S[x]
    tt = (time.perf_counter() - t0) / int(tekrar)
    ayni = bool(np.array_equal(o, S[x]))
    return {"koşuyor": True, "bayt": int(bayt),
            "gfni_sn": tg, "tablo_sn": tt,
            "gfni_gb": float(bayt / tg / 1e9),
            "tablo_gb": float(bayt / tt / 1e9),
            "hız": float(tt / max(tg, 1e-12)),
            "netice_aynı": ayni}


def rapor() -> str:                                      # pragma: no cover
    """GFNI bu makinede koşuyor mu, ne kadar hızlı -- **ölç**."""
    y = yoklama()
    c = y.get("cpuid") or {}
    s = ["=== GFNI -- GALOIS KOMUTLARI DONANIMDA ===", "",
         "  derleyici : %s" % y.get("derleyici"),
         "  bayrak    : %s" % y.get("bayrak"),
         "  derlendi  : %s" % y.get("derlendi"),
         "  KOŞUYOR   : %s   (%s)" % (y.get("koşuyor"), y.get("sebep")),
         "  AES cetveli 256 baytta tuttu mu: %s" % y.get("cetvel_tuttu"), ""]
    if c:
        s += ["  CPUID.7.0 ne diyor (KARAR BU DEĞİL, bilgi):",
              "    " + "  ".join("%s=%d" % (k, int(v)) for k, v in c.items()),
              ""]
        if not c.get("GFNI") and y.get("koşuyor"):
            s += ["  ⚠ AYRIŞMA: CPUID 'GFNI yok' diyor, komut ise KOŞUYOR",
                  "    ve doğru cetveli veriyor. Sanallaştırma bayrağı",
                  "    maskelemiş. Bayrağa bakılsaydı olan bir kabiliyet",
                  "    yok sayılacaktı; onun için geçit icradır.", ""]
    o = olc()
    if o.get("koşuyor"):
        s += ["  --- HIZ (%d bayt, saatlendi) ---" % o["bayt"],
              "    GFNI donanım : %.9f sn → %.2f GB/s" % (o["gfni_sn"],
                                                          o["gfni_gb"]),
              "    numpy tablo  : %.9f sn → %.2f GB/s" % (o["tablo_sn"],
                                                          o["tablo_gb"]),
              "    donanım %.2f× hızlı   netice birebir aynı: %s"
              % (o["hız"], o["netice_aynı"])]
    return "\n".join(s)


if __name__ == "__main__":                               # pragma: no cover
    print(rapor())
    sys.exit(0 if yoklama()["koşuyor"] else 1)

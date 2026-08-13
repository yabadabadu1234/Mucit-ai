import os
import sys
import gc
import time
import logging
from typing import Dict, List, Tuple

DEPO_KOKU = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUCIT_ROOT = os.path.join(DEPO_KOKU, "mucit_ai_esas")
for _p in [MUCIT_ROOT, os.path.join(MUCIT_ROOT, "mucit_ai"), os.path.join(MUCIT_ROOT, "kulli_gpu")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

logging.basicConfig(level=logging.ERROR, format="%(message)s", stream=sys.stdout)

import torch

import kontratlar
from kontratlar import Model_TopolojikKonfigurasyon, BiliselKanvasModeli, E1_HamMetinAkisi
from kulli_gpu.nvme_takas_yoneticisi import NvmeTakasYoneticisi

OLCUMLER: List[Tuple[str, float]] = []

class ZamanOlcer:
    def __init__(self, etiket: str):
        self.etiket = etiket
        self.cuda_var = torch.cuda.is_available()

    def __enter__(self):
        if self.cuda_var:
            torch.cuda.synchronize()
            self.bas_olay = torch.cuda.Event(enable_timing=True)
            self.bit_olay = torch.cuda.Event(enable_timing=True)
            self.bas_olay.record()
        self.cpu_bas = time.perf_counter()
        return self

    def __exit__(self, *_):
        cpu_ms = (time.perf_counter() - self.cpu_bas) * 1000.0
        if self.cuda_var:
            self.bit_olay.record()
            torch.cuda.synchronize()
            gpu_ms = self.bas_olay.elapsed_time(self.bit_olay)
        else:
            gpu_ms = cpu_ms
        OLCUMLER.append((self.etiket, gpu_ms))
        print(f"  {self.etiket:<48} {gpu_ms:>9.2f} ms   (cpu {cpu_ms:>8.2f} ms)")

def sarmalayici_yukunu_olc() -> None:
    asil = kontratlar.acil_durum_oom_yakalayici_ve_kurtarici
    sayac = {"n": 0, "sarmalayici_ms": 0.0, "ic_ms": 0.0}

    def bos_is(x):
        return x

    def olculen(fn, *a, **kw):
        t0 = time.perf_counter()
        sonuc = asil(fn, *a, **kw)
        toplam = time.perf_counter() - t0
        t1 = time.perf_counter()
        try:
            fn(*a, **{k: v for k, v in kw.items()
                      if k not in ("modul_nesnesi", "takas_mgr")})
        except Exception:
            pass
        ic = time.perf_counter() - t1
        sayac["n"] += 1
        sayac["sarmalayici_ms"] += (toplam - ic) * 1000.0
        sayac["ic_ms"] += ic * 1000.0
        return sonuc

    tekrar = 2000
    t0 = time.perf_counter()
    for _ in range(tekrar):
        asil(bos_is, 1)
    bos_sarmalayici_ms = (time.perf_counter() - t0) / tekrar * 1000.0

    t0 = time.perf_counter()
    for _ in range(tekrar):
        bos_is(1)
    bos_dogrudan_ms = (time.perf_counter() - t0) / tekrar * 1000.0

    fark = bos_sarmalayici_ms - bos_dogrudan_ms
    print(f"\n  Sarmalayıcının BOŞ çağrı maliyeti      : {bos_sarmalayici_ms * 1000:>9.2f} µs")
    print(f"  Doğrudan çağrı maliyeti                : {bos_dogrudan_ms * 1000:>9.2f} µs")
    print(f"  Net sarmalayıcı yükü (çağrı başına)    : {fark * 1000:>9.2f} µs")
    print(f"  Adım başına 97 çağrı için toplam yük   : {fark * 97:>9.3f} ms")

def dugum_profili_cikar() -> None:
    config = Model_TopolojikKonfigurasyon()
    config.device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"\nCihaz: {config.device} | batch={config.batch_size} | R={config.R} | "
          f"V_nodes={config.V_nodes} | d={config.d} | N={config.N}")

    model = BiliselKanvasModeli(config).to(config.device)
    adlar = ('n1_byte', 'n2_topox', 'n3_lif', 'n4_sorgu', 'n5_cevap', 'n6_aktor',
             'n7_cozucu', 'n8_chebyshev', 'n8_b_uzunluk', 'n9_vandermonde',
             'n10_sozluk', 'bellek_yonetici', 'n_yazici')
    m = {a: getattr(model, a) for a in adlar}

    metin = "Soyutlama ve muhakeme kabiliyeti yuksek mucit bir yapay zeka mimarisi testi. " * 8

    print("\n--- İLERİ GEÇİŞ: DÜĞÜM BAZLI ---")
    with ZamanOlcer("N1_ByteAyristirici"):
        e2_byte, x_initial = m['n1_byte'](E1_HamMetinAkisi(X_text=metin))
    with ZamanOlcer("N2_TopoXHucreOlusumu"):
        e3_sinir = m['n2_topox'](e2_byte, x_initial=x_initial, mode='train')
    with ZamanOlcer("N3_LifSinirlamaAtama"):
        e4_lif = m['n3_lif'](e3_sinir, x_initial)
    with ZamanOlcer("N11_LifLaplasyeniInsa (operator kurulumu)"):
        D0_op, _ = model.laplasyen_insa.insa_et(e3_sinir, e4_lif.phi_matrisleri)

    print("\n--- REKÜRENS DÖNGÜSÜ: ADIM ADIM VE DÜĞÜM DÜĞÜM ---")
    x_current = x_initial
    M_current = m['bellek_yonetici'].get_memory(x_current.shape[0]).M
    durum = kontratlar.E5_A_MevcutGizilDurum(x_r=x_current)

    for r in range(1, config.R + 1):
        bellek_gonderim = kontratlar.E5_B_BellekGonderimi(M=M_current)
        with ZamanOlcer(f"  r={r} N4_SorguSecici"):
            e6 = m['n4_sorgu'](durum, D0_operator=D0_op,
                               A_adjacency=e3_sinir.D1, bellek=bellek_gonderim)
        with ZamanOlcer(f"  r={r} N5_CevapSuzucu"):
            e7 = m['n5_cevap'](e6, bellek_gonderim)
        with ZamanOlcer(f"  r={r} N6_KohomolojikAktor"):
            m['n6_aktor'].update_operators(D0_op)
            e8 = m['n6_aktor'](durum, e6, e7)
        with ZamanOlcer(f"  r={r} N7_LifLaplasyeniCozucu"):
            e9 = m['n7_cozucu'](e8, D0_op, durum)
        with ZamanOlcer(f"  r={r} Bellek yazimi (terkip SMW)"):
            e5b = m['bellek_yonetici'].write(
                k_r=e6.q_r[:, :config.K], v_r=e7.a_r, q_r=e6.q_r, a_r=e7.a_r
            )
        x_current = e9.x_next
        M_current = e5b.M
        durum = kontratlar.E5_A_MevcutGizilDurum(x_r=x_current)

    print("\n--- ÇIKIŞ PROJEKSİYONU ---")
    with ZamanOlcer("N8_ChebyshevKatsayiProjeksiyon"):
        e10 = m['n8_chebyshev'](e9)
    with ZamanOlcer("N8_B_DinamikUzunlukSecici"):
        N_star, _, _, _ = m['n8_b_uzunluk'](e10, model.cheby_calc)
    with ZamanOlcer("Chebyshev Vandermonde matrisi (onbellekli)"):
        T = model.cheby_calc.hesapla(N=N_star)
    with ZamanOlcer("N9_ChebyshevVandermondeCarpim"):
        e11 = m['n9_vandermonde'](e10, T)
    with ZamanOlcer("N10_SozlukSoftmaxIzdusem"):
        e12 = m['n10_sozluk'](e11)

    print("\n--- GERİ GEÇİŞ ---")
    kayip = e12.P.float().mean() if hasattr(e12, 'P') else e11.X_output.float().mean()
    with ZamanOlcer("backward (tum graf)"):
        kayip.backward()

    print("\n--- OPERATÖR ÇARPIMLARI (izole) ---")
    x_duz = x_current.detach()
    with ZamanOlcer("d0_transpoze_carp x100"):
        for _ in range(100):
            y = kontratlar.d0_transpoze_carp(x_duz, D0_op)
    with ZamanOlcer("d0_carp x100"):
        for _ in range(100):
            _ = kontratlar.d0_carp(y, D0_op)

def rapor_bas() -> None:
    print("\n" + "=" * 78)
    print("EN PAHALI 12 ÖLÇÜM (azalan)")
    print("=" * 78)
    toplam = sum(s for _, s in OLCUMLER)
    for etiket, sure in sorted(OLCUMLER, key=lambda x: -x[1])[:12]:
        pay = (sure / toplam * 100.0) if toplam > 0 else 0.0
        print(f"  {etiket:<48} {sure:>9.2f} ms   %{pay:>5.1f}")
    print(f"\n  Ölçülen toplam: {toplam:.2f} ms")

    birikim: Dict[str, float] = {}
    for etiket, sure in OLCUMLER:
        anahtar = etiket.strip()
        if anahtar.startswith("r="):
            anahtar = anahtar.split(" ", 1)[1]
        birikim[anahtar] = birikim.get(anahtar, 0.0) + sure
    print("\n" + "=" * 78)
    print("DÜĞÜM BAZINDA TOPLAM (rekürens adımları birleştirilmiş)")
    print("=" * 78)
    for anahtar, sure in sorted(birikim.items(), key=lambda x: -x[1]):
        print(f"  {anahtar:<48} {sure:>9.2f} ms")

def main() -> int:
    print("=" * 78)
    print("UMUMİ EĞİTİM HATTI ANATOMİK PROFİL")
    print("=" * 78)
    dugum_profili_cikar()
    print("\n--- SARMALAYICI YÜKÜ ---")
    sarmalayici_yukunu_olc()
    rapor_bas()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

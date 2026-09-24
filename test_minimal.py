#!/usr/bin/env python3
"""Minimal test of the training pipeline."""

import sys
sys.path.insert(0, '.')

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

# Create a minimal EgitimAyari with pre-computed values to skip benchmarks
from main.egitim import EgitimAyari, kulli_kayip_talimi

# Minimal config for testing
ayar = EgitimAyari(
    ad="test",
    kodlama="o200k_base",
    sozluk=200019,
    belirtec_basamak=3,
    comert=0.1,
    tohum=0,
    olculen_hiz=1000000.0,  # Pre-set speed to skip benchmark
    
    # Pre-computed values from olcek
    veri_lifi=4,
    hukum_lifi=16,
    karo=4,
    yerel_yuva=1,
    parametre_genisligi=1,
    yigin_dilimi=1,
    ornek_sayisi=2,
    pencere=64,
    talim_tur=1,
    altuzay_ornek=1,
    cevrim_sayisi=2,
    degerlendirme_gorevi=1,
    dogrulama_sayisi=1,
    kademe_gorevi=1,
    azami_uret=8,
    yaricap=1.0,
    blok=1,
    azami_talim_saati=0.001,
    
    # Lambda values (set to 0 to skip)
    lam_cevrim=0.0, lam_monogami=0.0, lam_tip=0.0, lam_engel=0.0,
    lam_tenakuz=0.0, lam_kategori=0.0, lam_nokta=0.0, lam_meleke=0.0,
    lam_zirh=0.0, lam_kaide=0.0, lam_tasma=0.0, lam_lif=0.0,
    
    mihenk_arasi=1.0,
    galois_us=0, tableau_n=0, faz_mertebesi=4,
    flo_modu=0, flo_kapisi=0,
    siklotomik_us=0, siklotomik_taban=3, siklotomik_derece=12,
    faz_derecesi=3,
    tdd_cekirdek=0, tdd_tolerans=1e-7, stab_mertebe=0,
    golge_ornegi=0, golge_haddi=0.05,
    gpu_akis_haddi=1000.0, gpu_genlesmesi=8,
    hiz_geciti=0,  # Skip speed gate
    canli_saniye=1.0,
    hal_kaynagi="tutarlı",
    sadakat_acik=1, parite_lifi=2,
    usul_acik=0, usul_haddi=0.0, usul_seferi=0,
    keyfiyet_turu=0, suphe_acik=0,
    rust_muayene=0, sbox_acik=0,
    meleke_olcumu=0, mukayese_acik=0,
    hat="c", hat_bandi=0,
    motor="sürekli", genlik_tipi="complex128",
    rust_t0=0.5, rust_tau=0.15, rust_kapanis=0.5,
    hafiza_kapasitesi=16, hafiza_yazma=0.05, hafiza_sonumu=0.02,
    suphe_sonumu=0.05, zeno_esigi=0.35, zeno_tepe=0.9,
    hafiza_ayniyet=0.98, hafiza_buhar=1e-4, tenakuz_eps=1e-5,
    dislama_tau=8.0, ayna_teta=0.2618, ayna_r=0.35, ayna_tur=0,
    qudit_qsvt=0, qudit_derece=0, qudit_yon=0, harman_kademesi=0,
)

print(f"Test ayar: d={ayar.d}, pencere={ayar.pencere}, ornek={ayar.ornek_sayisi}")

# Run a minimal training
try:
    result = kulli_kayip_talimi(ayar)
    print(f"Training completed!")
    print(f"Hazine: {result.get('hazine')}")
    print(f"V_son: {result.get('V_son')}")
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()

print("\nTest done!")
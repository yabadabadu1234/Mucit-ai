#!/usr/bin/env python3
"""Simple test to verify the core modules work."""

import sys
sys.path.insert(0, '.')

import numpy as np
print("numpy ok")

import tiktoken
print("tiktoken ok")

# Test minimal imports
from nefs.belirtec import belirtec_kapisi
print("belirtec ok")

enc = belirtec_kapisi("o200k_base")
print(f"vocab size: {enc.n_vocab}")

# Test QuditAyar
from kuantum.qyazmac import QuditAyar
ayar = QuditAyar(d=4096, lif=(16, 16, 16))
print(f"QuditAyar: d={ayar.d}, lif={ayar.lif}")

# Test QuditYazmac
from kuantum.qyazmac import QuditYazmac
yazmac = QuditYazmac(ayar=ayar, veri_lifi=4, tohum=0)
print(f"QuditYazmac: n_satir={yazmac.n_satir}, veri_yuvasi={yazmac.veri_yuvasi}")

# Test basic operations
yazmac.superpozisyon()
print(f"superpozisyon norm: {yazmac.norm()}")

# Test rotation
G = np.eye(2, dtype=complex)
yazmac.tek(0, G)
print(f"after tek: norm={yazmac.norm()}")

# Test KAN
from kuantum.nqs import ChebyshevKan, NqsAyari
kan = ChebyshevKan(taban=64, qudit=4096, ayar=NqsAyari(dugum=8, derece=4))
print(f"KAN: parametre_adedi={kan.parametre_adedi}")

# Test genlik
basamak = np.array([[0, 1, 2, 3]], dtype=np.int64)
psi = kan.genlik(basamak)
print(f"genlik shape: {psi.shape}, norm: {np.linalg.norm(psi)}")

print("\nAll basic tests passed!")
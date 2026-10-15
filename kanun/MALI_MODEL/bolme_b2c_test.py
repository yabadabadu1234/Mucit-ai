import numpy as np, math
from genc_model import tarife, TAVAN, W

print("--- SAF B2C BÖLME TESTİ (Vergi %13.5) ---")
for H in (1.5e6, 3.0e6, 6.0e6):
    k = math.ceil(H / TAVAN)
    normal = float(tarife(np.array([0.7 * H]))[0]) + 141699.0
    h_i = H / k
    vergi_i = 0.135 * h_i
    net_gelir_ay = (h_i - vergi_i) / 12.0
    prim_ay_i = max(0.0, min(11808.25, net_gelir_ay - W))
    prim_yillik_i = 12.0 * prim_ay_i
    mikro_toplam = k * (vergi_i + prim_yillik_i)
    kazanc = normal - mikro_toplam
    print(f"  H={H/1e6:.1f} mn TL | k={k:2d} | Normal: {normal:9.0f} TL | Mikro (Vergi+Prim): {mikro_toplam:9.0f} TL | Kazanç: {kazanc:9.0f} TL (%{100*kazanc/H:+.1f})")


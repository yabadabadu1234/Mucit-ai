import numpy as np, math
from genc_model import tarife, TAVAN, W

print("--- KÜÇÜK DİLİMLERE (PRİMSİZ EŞİK ALTINA) BÖLME TESTİ ---")
# 1.5M TL'yi asgari ücret altı (aylık < 33.030 TL, yıllık net < 396.360 TL, yani ~k=5 kişi) dilimlere bölme
H = 1.5e6
normal = float(tarife(np.array([0.7 * H]))[0]) + 141699.0

for k in (2, 3, 4, 5, 6, 8, 10):
    h_i = H / k
    # B2C (%13.5)
    v_b2c = 0.135 * h_i
    net_ay_b2c = (h_i - v_b2c) / 12.0
    p_b2c = max(0.0, min(11808.25, net_ay_b2c - W))
    toplam_b2c = k * (v_b2c + 12 * p_b2c)
    kazanc_b2c = normal - toplam_b2c
    
    # B2B (%21.55 karma)
    v_b2b = 0.2155 * h_i
    net_ay_b2b = (h_i - v_b2b) / 12.0
    p_b2b = max(0.0, min(11808.25, net_ay_b2b - W))
    toplam_b2b = k * (v_b2b + 12 * p_b2b)
    kazanc_b2b = normal - toplam_b2b
    
    print(f"k={k:2d} | Her bir hasılat: {h_i:7.0f} TL (Net/ay: {net_ay_b2c:6.0f} TL) | Prim/kişi: {12*p_b2c:6.0f} TL | B2C Kazanç: {kazanc_b2c:7.0f} TL | B2B Kazanç: {kazanc_b2b:7.0f} TL")


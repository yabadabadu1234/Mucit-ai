import numpy as np, math
from genc_model import tarife, TAVAN, W

print("=================================================================")
print("TAVAN ÜSTÜ BÖLME ARBİTRAJI VE ÇARE SİMÜLASYONU")
print("=================================================================")

# Eski hesap: Prim yok, düz %13,5 vergi
print("\n--- 1. ESKİ TEKLİFTE BÖLME KAZANCI (Prim hesaba katılmamış) ---")
for H in (1.5e6, 3.0e6, 6.0e6):
    k = math.ceil(H / TAVAN)
    normal = float(tarife(np.array([0.7 * H]))[0]) + 141699.0
    mikro_eski = 0.135 * H
    kazanc_eski = normal - mikro_eski
    print(f"  H={H/1e6:.1f} mn TL | k={k:2d} | Normal: {normal:9.0f} TL | Mikro Eski: {mikro_eski:9.0f} TL | Kazanç: {kazanc_eski:9.0f} TL (%{100*kazanc_eski/H:.1f})")

# Yeni hesap:
# 1) Her kimlik B tasarımı uyarınca prim öder (çünkü 750.000 TL hasılatta aylık gelir asgari ücreti geçer!)
# 2) B2B satışlarda Nötr Kural (%25) veya B2C'de %13.5
# 3) Kimlik kiralama / aracı masrafı c = %5-10
# 4) Cezai katsayı ve tespit riski
print("\n--- 2. ÇARELER SONRASI BÖLME KAZANCI ---")
print("A) B Tasarımı Prim Eşiği devrede (Her kimlik aylık kazancına göre prim öder)")
print("B) B2B Nötr Kural (%70 B2B, %30 B2C karma etkin oran %21.55)")
print("C) Kimlik komisyonu/masrafı c = %5")

for H in (1.5e6, 3.0e6, 6.0e6):
    k = math.ceil(H / TAVAN)
    normal = float(tarife(np.array([0.7 * H]))[0]) + 141699.0
    
    # Her kimliğe düşen hasılat:
    h_i = H / k
    # B2B karma oran:
    vergi_orani = 0.70 * 0.25 + 0.30 * 0.135 # 0.2155
    vergi_i = vergi_orani * h_i
    net_gelir_ay = (h_i - vergi_i) / 12.0
    
    # B Tasarımı prim:
    prim_ay_i = max(0.0, min(11808.25, net_gelir_ay - W))
    prim_yillik_i = 12.0 * prim_ay_i
    
    mikro_toplam = k * (vergi_i + prim_yillik_i)
    masraf = 0.05 * H # Kimlik kiralama / aracı işlem maliyeti
    net_kazanc = normal - mikro_toplam - masraf
    
    print(f"  H={H/1e6:.1f} mn TL | k={k:2d} | Normal: {normal:9.0f} TL | Mikro Yeni: {mikro_toplam:9.0f} TL (Vergi:{k*vergi_i:.0f}, Prim:{k*prim_yillik_i:.0f}) | Net Kazanç: {net_kazanc:9.0f} TL (%{100*net_kazanc/H:+.1f})")


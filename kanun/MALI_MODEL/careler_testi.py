# Tek kaynak: model.py. Bu dosya yalnız model sonuçlarını raporlar; ayrı bir hesap motoru tutmaz.
import model

print("ÇARELER TESTİ — model.py çıktısı (tek kaynak)")
print("Kapsam: Nötr B2B Kural (kurumsal_pay=0,70, kv=%25), B Tasarımı Prim (aylık net > asgari ücret), Geçici M.2 ve KDV mahsubu sınırı")
print("\n--- 1. TEMEL SONUÇ (4. yıl, milyar TL) ---")
for ad in ("Kötümser", "Orta", "İyimser"):
    p = model.sc(ad)
    v, ys = model.npv(p)
    s = ys[3]
    print(f"  {ad:9s}: N={s['N']:.0f}  Net={s['net']/1e9:+6.2f}  NPV={v/1e9:+6.2f}  (brüt tevkifat {s['brut_tevkifat']/1e9:.2f}; yeni prim {s['yeni_prim']/1e9:.2f})")

print("\n--- 2. HALEN KAYITLI GEÇİŞİ (s) DUYARLILIĞI, 4. yıl net ---")
for ad in ("Kötümser", "Orta", "İyimser"):
    for s_val in (0.0, 0.15, 0.30, 0.50, 0.70):
        p = model.sc(ad)
        p['s_kayitli'] = s_val
        p['u_ucretli'] = min(p['u_ucretli'], 1 - s_val)
        p['n_yeni_pay'] = 1 - s_val - p['u_ucretli']
        v, ys = model.npv(p)
        print(f"  {ad:9s} s={s_val:.2f}: Net={ys[3]['net']/1e9:+6.2f}  NPV={v/1e9:+6.2f}")

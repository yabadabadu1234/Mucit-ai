import numpy as np, math
import model

print("=================================================================")
print("ÇARELER TESTİ: TÜM TEHLİKELERİN SAYISAL SİMÜLASYONU VE BERTARAFI")
print("=================================================================")

# 1. MEVCUT DURUM (Teklifteki hali)
print("\n--- 1. MEVCUT TEKLİF (Düz %13,5, eski eğri / 5(o)) ---")
for ad in ("Kötümser", "Orta", "İyimser"):
    p = model.sc(ad)
    v, ys = model.npv(p)
    s = ys[3]
    print(f"  {ad:9s} : Net = {s['net']/1e9:+6.2f} mlr TL | 5 Yıllık NPV = {v/1e9:+6.2f} mlr TL")

# 2. ÇARE PAKETİ UYGULANMIŞ YENİ MODEL
# Çare A: B2B Nötr Kural (Kurumsal alıcı indirimi satıcı oranını alıcı kurumlar vergisine %25 eşitler, kurumsal_pay=0.70)
#         Böylece sahte fatura = 0, kurumsal satışlardan Hazineye net gelir artar.
# Çare B: B Tasarımı Prim Eşiği (Asgari ücret altı sıfır prim, üstü kademeli)
# Çare C: Yutulma Freni (Halen kayıtlı olanların ani prim terkini önleyen 12 aylık kademeli intibak: s_kayitli geçişinde %50 prim intibakı)
# Çare D: Donanım KDV Mahsup Üst Sınırı (%30 veya max 5000 TL)
# Çare E: Ücretli Arbitraj Sınırı (u_ucretli tavanı 12 asgari ücret)

def yeni_kisi_basi(H, p, notr_b2b=True, prim_b_tasarimi=True):
    # Vergi tevkifatı
    if notr_b2b:
        # Kurumsal B2B (%70 pay) %25 oran, bireysel B2C/ihracat (%30 pay) %13.5 oran
        etkin_vergi_orani = p['kurumsal_pay'] * 0.25 + (1 - p['kurumsal_pay']) * p['duz_oran']
        T = etkin_vergi_orani * H
    else:
        T = p['duz_oran'] * H
        
    bes = p['bes'] * T * (1 - p['bes_vazgecme'])
    dk = bes * p['devlet_katki']
    myo = np.where(H >= 0.5 * model.TAVAN, p['myo_uygun'] * p['myo_gun_ay'] * model.W * p['myo_oran'], 0.0)
    
    # Donanım KDV mahsubu: %30 tavan veya 5000 TL
    kdv = p['kdv_donanim_pay'] * np.minimum(0.30 * T, 5000.0)
    
    W = model.W
    y_ay = (H - T) / 12.0
    
    if prim_b_tasarimi:
        # Padişah B tasarımı: Net gelir asgari ücreti geçmiyorsa 0, geçiyorsa min(tam prim, aşan kısım)
        prim_aylik = np.where(y_ay <= W, 0.0, np.minimum(p['prim_ay'], y_ay - W))
        yeni_prim = 12.0 * prim_aylik * p['prim_toplama']
    else:
        G = W / 3.0
        K = p['prim_k'] * W
        yeni_prim = 12.0 * p['prim_ay'] * p['prim_toplama'] * np.clip((y_ay - G) / (K - G), 0.0, 1.0)
        
    yeni_net = T - bes - dk - myo - kdv
    eski_vergi = model.tarife(p['marj'] * H)
    eski_prim = p['prim_odeme'] * p['prim_eski'] * (1 - p['prim_devam'])
    eski_kayitli = eski_vergi + eski_prim
    eski_ucretli = p['uyum_ucretli'] * p['r_marj_ucretli'] * p['marj'] * H
    
    return dict(T=T, bes=bes, dk=dk, myo=myo, kdv=kdv, yeni_net=yeni_net,
                eski_kayitli=eski_kayitli, eski_ucretli=eski_ucretli, eski_vergi=eski_vergi,
                eski_prim=eski_prim, yeni_prim=yeni_prim)

def yeni_yil(p, carpan=1.0, ilk=False, yutulma_freni=True, notr_b2b=True, prim_b=True):
    H, w = model.agirliklar(p)
    k = yeni_kisi_basi(H, p, notr_b2b=notr_b2b, prim_b_tasarimi=prim_b)
    N = p['n_toplam'] * carpan
    
    E = lambda x: float((w * x).sum())
    ET, EH = E(k['T']), E(H)
    brut = N * ET
    bes_k = N * E(k['bes'] + k['dk'])
    myo = N * E(k['myo'])
    kdv = N * E(k['kdv'])
    
    # Yutulma: Eğer yutulma freni varsa (Geçici Madde 2 ile mevcut mükellef intibakı),
    # kayıtlı mükelleflerin geçişi kontrollü gerçekleşir ve eski prim kaybının %40'ı intibak katkısıyla korunur.
    fren_carpani = 0.60 if yutulma_freni else 1.0
    
    y_vergi = N * (p['s_kayitli'] * E(k['eski_vergi']) + p['u_ucretli'] * E(k['eski_ucretli']))
    y_prim = N * p['s_kayitli'] * E(k['eski_prim']) * fren_carpani
    eski = y_vergi + y_prim
    
    y_yeni_prim = N * (1 - p['u_ucretli']) * E(k['yeni_prim'])
    
    # Nötr kuralda sahte fatura sıfırlanır
    sahte = 0.0 if notr_b2b else p['phi'] * (1 - p['onlem']) * p['kurumsal_pay'] * N * EH * max(p['kv'] - (ET/EH), 0)
    
    kgf = N * p['kgf_alim'] * E(p['kgf_pay'] * H) * p['kgf_temerrut'] * (1 - p['kgf_kurtarma'])
    ptt = N * p['ptt_pay'] * p['ptt_birim'] * (1.0 if ilk else 0.0)
    it = (p['bt_tek'] if ilk else 0.0) + p['bt_yillik']
    itiraz = N * p['itiraz_oran'] * p['itiraz_maliyet']
    den = p['denetim'] * brut
    
    net = brut + y_yeni_prim - bes_k - myo - kdv - eski - sahte - kgf - ptt - it - itiraz - den
    return dict(N=N, ort_H=EH, ort_T=ET, etkin_oran=ET/EH, brut_tevkifat=brut,
                bes_ve_devlet_katkisi=bes_k, myo_primi=myo, kdv_mahsubu=kdv,
                yutulma_kaybi=eski, yeni_prim=y_yeni_prim, sahte_fatura_kaybi=sahte,
                kgf_maliyeti=kgf, ptt=ptt, bt=it, itiraz=itiraz, denetim=den, net=net)

def yeni_npv(p, yutulma_freni=True, notr_b2b=True, prim_b=True):
    ys = [yeni_yil(p, r, ilk=(i==0), yutulma_freni=yutulma_freni, notr_b2b=notr_b2b, prim_b=prim_b) for i, r in enumerate(p['ramp'])]
    return sum(y['net'] / (1 + p['iskonto'])**(i+1) for i, y in enumerate(ys)), ys

print("\n--- 2. ÇARELER UYGULANDIKTAN SONRAKİ SONUÇLAR ---")
print("(Nötr B2B Kuralı + B Tasarımı Prim Eşiği + Geçici M.2 Yutulma Freni + KDV Mahsup Sınırı)")
for ad in ("Kötümser", "Orta", "İyimser"):
    p = model.sc(ad)
    v, ys = yeni_npv(p, yutulma_freni=True, notr_b2b=True, prim_b=True)
    s = ys[3]
    print(f"  {ad:9s} : Net = {s['net']/1e9:+6.2f} mlr TL | 5 Yıllık NPV = {v/1e9:+6.2f} mlr TL (Brüt Tevkifat: {s['brut_tevkifat']/1e9:.2f} mlr, Yeni Prim: {s['yeni_prim']/1e9:.2f} mlr)")


print("\n--- 3. YUTULMA VE s DUYARLILIĞI TESTİ (s = 0.15, 0.30, 0.50, 1.00) ---")
for ad in ("Kötümser", "Orta"):
    p = model.sc(ad)
    print(f"Senaryo: {ad}")
    for s_val in (0.15, 0.30, 0.50, 0.70, 1.00):
        p['s_kayitli'] = s_val
        v, ys = yeni_npv(p, yutulma_freni=True, notr_b2b=True, prim_b=True)
        res = ys[3]
        print(f"  s = {s_val:.2f} -> Net = {res['net']/1e9:+6.2f} mlr TL (NPV: {v/1e9:+6.2f} mlr TL)")


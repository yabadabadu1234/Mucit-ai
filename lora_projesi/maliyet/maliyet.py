# Birim maliyet modeli: 1 verici + 1 alici = 1 takim. Fiyatlar USD, ~100 takim.
# B = bu oturumda bir dagitimci/LCSC sayfasindan okundu (kaynak yazili); T = tahmin (kaynak bulunamadi)
KALEMLER = [  # (ad, adet/takim, fiyat, B|T, kaynak veya gerekce)
 ('A7670SA-LASE modem', 1, 8.88, 'B', 'LCSC C47088708, 10+ kademesi (2026-10-23); stok 1: siparis oncesi stok sorulur'),
 ('Ra-01H LoRa modulu', 2, 4.65, 'B', 'LCSC C503593, 18+ kademesi (2026-10-23), stok 3043'),
 ('ESP32-S3-WROOM-1-N4', 2, 3.36, 'B', 'LCSC C2913197, 100+ kademesi (2026-10-23)'),
 ('W5500', 1, 1.99, 'B', 'LCSC C32843, 100+ kademesi'),
 ('TPS63031DSKR', 1, 0.65, 'B', 'LCSC C15516, 100+ kademesi'),
 ('TPS62933DRLR x2', 2, 0.283, 'B', 'LCSC C3200405, 100+ kademesi'),
 ('SRD-12VDC-SL-A role', 1, 0.43, 'B', 'LCSC C93716, 50+ kademesi'),
 ('HR911105A RJ45', 1, 1.03, 'B', 'LCSC C12074, 93+ kademesi'),
 ('LM66100DCKR ideal diyot', 1, 0.17, 'B', 'LCSC C2869734, 50-150 kademesi'),
 ('USBLC6-2SC6 x5', 5, 0.14, 'B', 'LCSC C7519 (ST), 50 kademesi; alici 4, verici 1'),
 ('bobin fiyat farki SRP7028A-4R7M - SRN6028-4R7M, 2 adet', 2, 0.38, 'B', 'LCSC C840529 0,754 - C3221249 0,374 (100+)'),
 ('USB-C konnektor x2', 2, 0.20, 'T', 'tahmin'),
 ('SMA kenar konnektor x2 + u.FL', 3, 0.50, 'T', 'tahmin'),
 ('micro-SIM yuvasi', 1, 0.40, 'T', 'tahmin'),
 ('klemens x2, kaydirmali anahtar, dugmeler, pil yuvasi', 1, 2.50, 'T', 'tahmin'),
 ('polimer 330 uF, 220 uF, 1812 PTC, TVS, diyotlar, bobinler', 1, 2.50, 'T', 'tahmin'),
 ('pasifler (yaklasik 170 direnc/kondansator) + LED + kristal + IC kucukleri', 1, 2.50, 'T', 'tahmin'),
 ('PCB 4 katman, iki kart (88x102 + 40x100)', 1, 3.00, 'T', 'JLCPCB 100x100 4 kat 5 adet ~9,55 USD (forum 2024); 100 adette adet basi dusuk, tahmin'),
 ('PCBA montaj, iki kart (pin basi + besleyici ucreti)', 1, 5.00, 'T', 'TechOverflow 2024: ~0,0014 EUR/pin, ek komponent besleyici 1,5 USD/tur; tahmin'),
]
def toplam(kalemler, degis=None):
    degis = degis or {}
    t = {'B': 0.0, 'T': 0.0}
    for ad, n, f, k, _ in kalemler:
        f = degis.get(ad, f); t[k] += n*f
    return t
ana = toplam(KALEMLER)
print('Takim maliyeti:', round(ana['B']+ana['T'], 1), 'USD  (okunan fiyatli kalemler', round(ana['B'], 1), '+ tahmin', round(ana['T'], 1), ')')
for ad, n, f, k, kay in sorted(KALEMLER, key=lambda x: -x[1]*x[2])[:5]:
    print(f'  {ad:55s} {n*f:7.2f} [{k}]')

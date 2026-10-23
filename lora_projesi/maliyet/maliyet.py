# Birim maliyet modeli: 1 verici + 1 alici = 1 takim. Fiyatlar USD, ~100 takim.
# B = bu oturumda bir dagitimci/LCSC sayfasindan okundu (kaynak yazili); T = tahmin (kaynak bulunamadi)
KALEMLER = [  # (ad, adet/takim, fiyat, B|T, kaynak veya gerekce)
 ('SIM7600SA modem', 1, 36.60, 'B', 'DigiKey 3781-SIM7600SA-ND, 100 adet kademesi'),
 ('RFM95W-915S2 LoRa modulu', 2, 15.76, 'B', 'LCSC C6760738 (RF Solutions), 1000+ kademesi; Mouser 1 adet 23,75; Farnell 250+ ~EUR17,3'),
 ('ESP32-S3-WROOM-1-N4', 2, 3.66, 'B', 'LCSC C2913197, 100+ (arama ozeti, sayfa fiyat vermedi)'),
 ('W5500', 1, 2.49, 'B', 'LCSC C32843, 1 adet ~2,49-2,80 (1000+ ~1,75-1,88)'),
 ('TPS63031DSKR', 1, 1.89, 'B', 'Mouser/DigiKey 1 adet ~1,89-2,06 (toplayici sayfa)'),
 ('TPS62933DRLR x2', 2, 0.90, 'T', 'fiyat bulunamadi; benzer 3 A buck icin tahmin'),
 ('SRD-12VDC-SL-A role', 1, 0.90, 'T', 'tahmin'),
 ('HR911105A RJ45', 1, 0.90, 'T', 'tahmin'),
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
# Secenekler (tasarlanmadi, dogrulanmadi): LoRa modulu Ra-01H (SX1276, ayni yonga, RFM95W ile LoRa uyumlu)
ra = toplam(KALEMLER, {'RFM95W-915S2 LoRa modulu': 4.38})
print('Ra-01H secenegi (LCSC C503593, 18+ adet 4,38 USD):', round(ra['B']+ra['T'], 1), 'USD')
print('  fark:', round((ana['B']+ana['T'])-(ra['B']+ra['T']), 1), 'USD / takim')

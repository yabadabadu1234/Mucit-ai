import numpy as np, math
# Varsayimlar (belge degil, tipik alkalin AAA davranisi; Energizer/Duracell egrilerinin kabaca sekli)
KAP_MAH = 1000.0                       # 2 hucre seri: ayni akim, 25-100 mA'da ~1000 mAh (varsayim)
dod_nok = np.array([0, .2, .5, .8, .9, .95, 1.0])
ocv_nok = np.array([1.60, 1.47, 1.35, 1.25, 1.18, 1.10, 0.90])   # hucre basina
r_nok   = np.array([.15, .17, .22, .35, .55, .90, 2.0])          # hucre basina, 23 C
def ocv(d): return 2*np.interp(d, dod_nok, ocv_nok)
def rint(d, sicaklik_carpani=1.0): return 2*np.interp(d, dod_nok, r_nok)*sicaklik_carpani
ETA = 0.85                              # TPS63031 boost/buck-boost verimi, 1.5-3 V giris (belge egrisi 80-90%)
VIN_UVLO = 1.5                          # TPS63031 VINA dusen esik tipik 1.5 V (belge: 1.4-1.6)
VIN_BASLAMA = 1.8                       # baslama icin en az 1.8 V
def vin_tepe(d, i_yuk, carpan=1.0):
    P = 3.3*i_yuk/ETA                   # girisin cekecegi guc
    V, R = ocv(d), rint(d, carpan)
    # V*I - R*I^2 = P  -> giris gerilimi = V - R*I
    disc = V*V - 4*R*P
    if disc < 0: return 0.0
    I = (V - math.sqrt(disc))/(2*R)
    return V - R*I
# yuk basamaklari (mA): belge degerleri (Ra-01H (SX1276) 915 MHz TX ortalama 97 mA [Ra-01H belgesi Tablo 1.1]; ESP32-S3 etkin ~40 mA tahmin: modul belgesi 240 MHz tipik, WiFi kapali)
YUKLER = {'ESP32 acilis (WiFi yok)': 45, 'LoRa TX (Ra-01H 97 mA) + ESP32 bosta': 97+30, 'LoRa TX +20 dBm + ESP32 bosta': 120+30}
for carpan, ad in [(1.0, '23 C'), (2.0, '0 C (ic direnc x2, varsayim)')]:
    print('===', ad)
    for yad, ma in YUKLER.items():
        sinir = None
        for d in np.linspace(0, 1, 2001):
            if vin_tepe(d, ma/1000, carpan) < VIN_UVLO:
                sinir = d; break
        print(f'{yad:34s} {ma:4d} mA -> pil bu yuku %{100*(sinir if sinir else 1):.1f} bosalmaya kadar tasir')
# omur: uyku akimi (belge): TPS63031 Iq 25 uA, ESP32-S3 derin uyku 8 uA, SX1276 uyku 0.2 uA (belgede Ra-01H icin uyku akimi yok; yonga degeri), sizinti tahmini 2 uA
UYKU_UA = 25 + 4 + 8 + 0.2 + 2
def lora_havada(sf=7, bw=125e3, yuk=12, cr=1, preamble=8):
    tsym = 2**sf/bw; de = 1 if (sf >= 11 and bw == 125e3) else 0
    n = 8 + max(math.ceil((8*yuk - 4*sf + 28 + 16)/(4*(sf-2*de)))*(cr+4), 0)
    return (preamble + 4.25)*tsym + n*tsym
for sf in (7, 9, 12):
    ta = lora_havada(sf)
    olay_mC = 0.150*45 + ta*(97+30) + 0.020*45        # acilis 150 ms + TX + 20 ms kapanis
    for gun in (10, 50, 200):
        olay_uAh_gun = gun*olay_mC/3.6
        ort_uA = UYKU_UA + olay_uAh_gun/24
        # verim kaybi: bosta yuk 3.3 V rayindan, pilden cekilen = /ETA (uyku akimi Iq zaten girisle olculur)
        ort_pil_uA = UYKU_UA + (olay_uAh_gun/24)/ETA
        omur_gun = KAP_MAH*0.85*1000/ort_pil_uA/24   # %85: bosalma sirasinda yuk kesintisi icin kullanilabilir pay (yukaridaki esiklerden)
        print(f'SF{sf:2d} havada {ta*1000:6.0f} ms, gunde {gun:3d} basis: ort {ort_pil_uA:5.1f} uA -> {omur_gun/365:4.1f} yil')

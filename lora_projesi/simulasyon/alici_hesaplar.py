import math, itertools
# --- 1) 12 V giris akim butcesi ve sigorta payi ---
def pin(p_cikis, eta): return p_cikis/eta
yuk33 = {'ESP32-S3 (WiFi/BLE kapali, 240 MHz)': 0.060, 'Ra-01H TX 915 MHz (belge: 97 mA)': 0.097, 'W5500 100 Mb/s (tipik ~132 mA, belge)': 0.132, 'LED x2 + role surucu + diger': 0.020}
i33 = sum(yuk33.values())
p33 = pin(3.3*i33, 0.88)
for modem, imod in (('modem LTE veri (SIM7600 belgesi V1.08: <=0,67 A; A7670SA icin ayri deger okunmadi [varsayim])', 0.67), ('modem GSM patlama zirvesi 2,8 A, ortalama ~0,35 A [varsayim]', 0.35)):
    pm = pin(4.0*imod, 0.90)
    i12 = (p33+pm)/12 + 12/400  # role bobini: 12 V / 400 ohm (SRD-12VDC-SL-A ~400 ohm tipik)
    print(f'{modem}: 3,3 V hatti {i33*1000:.0f} mA, 12 V giris ortalama {i12*1000:.0f} mA')
print('GSM zirvesinde (2,8 A, 577 us) 12 V tarafinda anlik ~', round(pin(4.0*2.8, 0.9)/12*1000), 'mA (PTC isinmasi icin ortalama onemli)')
# --- 2) TPS62933 isinma (belge: RthJA JEDEC 112, EVM 60 C/W) ---
for ad, pout in (('3,3 V hatti', 3.3*i33), ('modem hatti ortalama 1,4 W', 1.4)):
    kayip = pout*(1/0.9-1)
    print(f'{ad}: kayip {kayip*1000:.0f} mW, Tj-Ta {kayip*112:.0f} C (JEDEC 112 C/W, kotumser)')
# --- 3) RF mikroserit (Hammerstad-Jensen), 0,4 mm iz, katman dizilimi toleransi ---
def z0(w, h, er, t=0.035):
    u = w/h
    # etkin genislik (kalinlik duzeltmesi)
    du = t/math.pi/h*(1+math.log(2*h/t)); ue = u+du*(1+1/math.cosh(math.sqrt(er-1)))/2
    a = 1+math.log((ue**4+(ue/52)**2)/(ue**4+0.432))/49+math.log(1+(ue/18.1)**3)/18.7
    b = 0.564*((er-0.9)/(er+3))**0.053
    eeff = (er+1)/2+(er-1)/2*(1+10/ue)**(-a*b)
    f = 6+(2*math.pi-6)*math.exp(-(30.666/ue)**0.7528)
    return 60*math.log(f/ue+math.sqrt(1+(2/ue)**2))/math.sqrt(eeff), eeff
res = []
for h, er in itertools.product((0.18, 0.21, 0.24), (4.2, 4.4, 4.6)):
    z, e = z0(0.4, h, er); res.append(z)
    print(f'h={h} mm er={er}: Z0={z:.1f} ohm eeff={e:.2f}')
print('RF hat empedansi aralik', round(min(res),1), '-', round(max(res),1), 'ohm; 50 ohm\'dan en kotu sapma %', round(max(abs(r-50) for r in res)/50*100,1))
# --- 4) W5500 kristal: iz kapasitesi etkisi ---
h, er = 0.21, 4.4
z, e = z0(0.15, h, er)
cpl = math.sqrt(e)/(3e8*z)*1e12/100   # pF/cm
for ad, cm in (('XI', 1.95), ('XO', 2.09)):
    print(f'{ad}: {cm*10:.0f} mm iz, ~{cpl*cm:.1f} pF (Z0={z:.0f} ohm, {cpl:.2f} pF/cm)')
# referans: WIZnet ~1 cm iz. Fark ~1,3-1,5 pF/dugum. Kristal cekme duyarliligi: S = C1/(2*(C0+CL)^2)
C1, C0, CL = 6e-3, 5.0, 18.0  # pF (tipik 25 MHz AT-kesim: Cm ~ 5-10 fF, C0 ~ 3-7 pF; varsayim)
S = C1/(2*(C0+CL)**2)*1e6
dC = ((18+cpl*1.95+3)*(18+cpl*2.09+3))/((18+cpl*1.95+3)+(18+cpl*2.09+3)) - ((18+cpl*1+3)*(18+cpl*1+3))/((18+cpl*1+3)*2)
print(f'seri yuk degisimi ~{dC:.2f} pF -> frekans kaymasi ~{S*dC:.1f} ppm (Ethernet siniri +-50 ppm, kristal toleransi ayrica)')
# --- 5) Ethernet cift uzunluk farki ---
v = 3e8/math.sqrt(e)   # m/s
for ad, fark in (('TX cifti (W_TXP+TD_P / W_TXN+TD_N)', abs((6.1+25.2)-(6.6+22.6))), ('RX cifti (W_RXP+RD_P? / W_RXN+RD_N?)', abs((9.0+21.9)-(5.6+28.1)))):
    print(f'{ad} cifti uzunluk farki {fark:.1f} mm -> gecikme farki {fark*1e-3/v*1e12:.0f} ps (100BASE-TX sembol suresi 8000 ps)')

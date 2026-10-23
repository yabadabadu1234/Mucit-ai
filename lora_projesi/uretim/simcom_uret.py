import os, sys
D = os.path.join(os.path.dirname(__file__), 'kutuphane')

# SIMCom A7670 Series Hardware Design V1.00 Table 3 (88 pad LGA, 24 x 24 mm) ve Sekil 2 / Sekil 4
_ISIM_METIN = {
    1: 'PWRKEY', 2: 'GND', 3: 'DTR', 4: 'RI', 5: 'DCD', 6: 'USB_BOOT', 7: 'CTS', 8: 'RTS', 9: 'TXD', 10: 'RXD', 11: 'PCM_CLK', 12: 'PCM_SYNC',
    13: 'PCM_DIN', 14: 'PCM_OUT', 15: 'VDD_1V8', 16: 'RESET', 17: 'GND', 18: 'GND', 19: 'GPIO1', 20: 'GPIO2', 21: 'GPIO3', 22: 'UART_LOG_RX',
    23: 'UART_LOG_TX', 24: 'VBUS', 25: 'ADC', 26: 'NC', 27: 'USB_DP', 28: 'USB_DM', 29: 'GND', 30: 'SIM_VDD', 31: 'SIM_DATA', 32: 'SIM_CLK',
    33: 'SIM_RST', 34: 'SIM_DET', 35: 'NC', 36: 'NC', 37: 'I2C_SDA', 38: 'I2C_SCL', 39: 'GND', 40: 'NC', 41: 'NC', 42: 'NC', 43: 'NC', 44: 'NC',
    45: 'GND', 46: 'GND', 47: 'NC', 48: 'GPIO9', 49: 'GPIO4_UART3_RX', 50: 'GPIO5_UART3_TX', 51: 'NC', 52: 'NETLIGHT', 53: 'NC', 54: 'GND',
    55: 'VBAT', 56: 'VBAT', 57: 'VBAT', 58: 'GND', 59: 'GND', 60: 'RF_ANT', 61: 'GND', 62: 'GND', 63: 'GND', 64: 'GND', 65: 'GND', 66: 'STATUS',
    67: 'GPIO10', 68: 'GPIO11'}
ISIM = dict(_ISIM_METIN)
for _n in range(69, 89):
    ISIM[_n] = 'GND'
assert sorted(ISIM) == list(range(1, 89))

# dis halka (1.00 mm adim, pad 0.6 x 0.8, merkez modul kenarindan 0.6 mm iceride); Sekil 4
def dis_pad(n):
    if 1 <= n <= 17:
        return (-11.4, -8.0 + (n - 1), 0.8, 0.6)
    if 18 <= n <= 34:
        return (-8.0 + (n - 18), 11.4, 0.6, 0.8)
    if 35 <= n <= 51:
        return (11.4, 8.0 - (n - 35), 0.8, 0.6)
    if 52 <= n <= 68:
        return (8.0 - (n - 52), -11.4, 0.6, 0.8)

# ic GND pedleri 2.1 x 2.1 mm, 3.8 mm izgara; Sekil 2 (numaralar) ve Sekil 4 (olculer)
IC = {69: (0, 0), 84: (0, 1), 83: (0, 2), 82: (0, 3), 81: (0, 4),
      70: (1, 0), 88: (1, 2), 80: (1, 4),
      71: (2, 0), 85: (2, 1), 87: (2, 3), 79: (2, 4),
      72: (3, 0), 86: (3, 2), 78: (3, 4),
      73: (4, 0), 74: (4, 1), 75: (4, 2), 76: (4, 3), 77: (4, 4)}
assert sorted(IC) == list(range(69, 89))

def ayak_yaz():
    out = ['(footprint "A7670SA_LGA88" (version 20221018) (generator pcbnew)', '  (layer "F.Cu")',
           '  (descr "SIMCom A7670 serisi (A7670SA) 88 pedli LGA, 24 x 24 mm; A7670 Series Hardware Design V1.00 Sekil 2 ve Sekil 4")',
           '  (tags "A7670SA LGA88")', '  (attr smd)',
           '  (fp_text reference "REF**" (at 0 -14.3) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
           '  (fp_text value "A7670SA_LGA88" (at 0 14.3) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))']
    for (a, b, c, d) in [(-12, -12, 12, -12), (12, -12, 12, 12), (12, 12, -12, 12), (-12, 12, -12, -12)]:
        out.append('  (fp_line (start %s %s) (end %s %s) (layer "F.Fab") (width 0.1))' % (a, b, c, d))
    for (a, b, c, d) in [(-12.5, -12.5, 12.5, -12.5), (12.5, -12.5, 12.5, 12.5), (12.5, 12.5, -12.5, 12.5), (-12.5, 12.5, -12.5, -12.5)]:
        out.append('  (fp_line (start %s %s) (end %s %s) (layer "F.CrtYd") (width 0.05))' % (a, b, c, d))
    out.append('  (fp_circle (center -10.0 -10.0) (end -9.6 -10.0) (layer "F.SilkS") (width 0.15) (fill solid))')
    pads = []
    for n in range(1, 69):
        x, y, w, h = dis_pad(n)
        pads.append((n, x, y, w, h))
    for n, (r, c) in IC.items():
        pads.append((n, -7.6 + 3.8 * c, -7.6 + 3.8 * r, 2.1, 2.1))
    for n, x, y, w, h in sorted(pads):
        out.append('  (pad "%d" smd rect (at %s %s) (size %s %s) (layers "F.Cu" "F.Paste" "F.Mask"))' % (n, round(x, 3), round(y, 3), w, h))
    # Sekil 4 "Forbidden Area": iki kare, F.Cu'da iz, via ve dokulu bakir yasak
    for (x0, x1, y0, y1) in [(-10.9, -9.4, -8.8, -7.3), (1.4, 3.8, 2.0, 4.4)]:
        out.append('  (zone (net 0) (net_name "") (layer "F.Cu") (hatch edge 0.5) (connect_pads (clearance 0)) (min_thickness 0.2) (keepout (tracks not_allowed) (vias not_allowed) (pads allowed) (copperpour not_allowed) (footprints allowed))'
                   ' (fill (thermal_gap 0.5) (thermal_bridge_width 0.5)) (polygon (pts (xy %s %s) (xy %s %s) (xy %s %s) (xy %s %s))))' % (x0, y0, x1, y0, x1, y1, x0, y1))
        out.append('  (fp_rect (start %s %s) (end %s %s) (layer "F.Fab") (width 0.1) (fill none))' % (x0, y0, x1, y1))
    out.append(')')
    os.makedirs(os.path.join(D, 'Simcom.pretty'), exist_ok=True)
    for f in os.listdir(os.path.join(D, 'Simcom.pretty')):
        if f != 'A7670SA_LGA88.kicad_mod':
            os.remove(os.path.join(D, 'Simcom.pretty', f))
    open(os.path.join(D, 'Simcom.pretty', 'A7670SA_LGA88.kicad_mod'), 'w').write('\n'.join(out) + '\n')

TIP = {'GND': 'power_in', 'VBAT': 'power_in', 'VDD_1V8': 'power_out', 'SIM_VDD': 'power_out', 'NC': 'no_connect',
       'TXD': 'output', 'CTS': 'output', 'RI': 'output', 'DCD': 'output', 'STATUS': 'output', 'NETLIGHT': 'output',
       'UART_LOG_TX': 'output', 'RXD': 'input', 'RTS': 'input', 'DTR': 'input', 'PWRKEY': 'input', 'RESET': 'input',
       'UART_LOG_RX': 'input', 'USB_BOOT': 'input', 'VBUS': 'input', 'RF_ANT': 'passive'}

def sembol_yaz():
    sol = ['PWRKEY', 'RESET', 'USB_BOOT', 'STATUS', 'NETLIGHT', 'TXD', 'RXD', 'RTS', 'CTS', 'DTR', 'DCD', 'RI',
           'SIM_VDD', 'SIM_DATA', 'SIM_RST', 'SIM_CLK', 'SIM_DET', 'I2C_SCL', 'I2C_SDA', 'ADC'] + ['GND'] * 17
    sag = ['RF_ANT', 'VBUS', 'USB_DM', 'USB_DP', 'UART_LOG_TX', 'UART_LOG_RX', 'PCM_CLK', 'PCM_SYNC', 'PCM_DIN', 'PCM_OUT',
           'GPIO1', 'GPIO2', 'GPIO3', 'GPIO4_UART3_RX', 'GPIO5_UART3_TX', 'GPIO9', 'GPIO10', 'GPIO11'] + ['NC'] * 11 + ['GND'] * 18
    ust = ['VBAT', 'VBAT', 'VBAT', 'VDD_1V8']
    tum = {}
    for n, ad in ISIM.items():
        tum.setdefault(ad, []).append(n)
    secili = {}
    def al(ad):
        i = secili.get(ad, 0); secili[ad] = i + 1
        return tum[ad][i]
    kullan = sol + sag + ust
    assert sorted(tum) == sorted(set(kullan)), set(tum) ^ set(kullan)
    for ad in tum:
        assert kullan.count(ad) == len(tum[ad]), (ad, kullan.count(ad), len(tum[ad]))
    pitch = 2.54
    n_say = max(len(sol), len(sag))
    h = n_say * pitch + 2 * pitch
    w = 12 * pitch
    x0, x1 = -w / 2, w / 2
    y0, y1 = h / 2, -h / 2
    L = []
    L.append('(kicad_symbol_lib (version 20220914) (generator simcom_uret)')
    L.append('  (symbol "A7670SA" (in_bom yes) (on_board yes)')
    L.append('    (property "Reference" "U" (at 0 %s 0) (effects (font (size 1.27 1.27))))' % (y1 - 3))
    L.append('    (property "Value" "A7670SA" (at 0 %s 0) (effects (font (size 1.27 1.27))))' % (y0 + 3))
    L.append('    (property "Footprint" "Simcom:A7670SA_LGA88" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    L.append('    (property "Datasheet" "A7670 Series Hardware Design V1.00" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    L.append('    (symbol "A7670SA_0_1" (rectangle (start %s %s) (end %s %s) (stroke (width 0.254) (type default)) (fill (type background))))' % (x0, y1, x1, y0))
    L.append('    (symbol "A7670SA_1_1"')
    def pin(tip, x, y, ang, ad, num):
        L.append('      (pin %s line (at %s %s %s) (length 5.08) (name "%s" (effects (font (size 1.27 1.27)))) (number "%d" (effects (font (size 1.27 1.27)))))' % (tip, round(x, 3), round(y, 3), ang, ad, num))
    for i, ad in enumerate(sol):
        pin(TIP.get(ad, 'bidirectional'), x0 - 5.08, y1 + pitch * (i + 1.0), 0, ad, al(ad))
    for i, ad in enumerate(sag):
        pin(TIP.get(ad, 'bidirectional'), x1 + 5.08, y1 + pitch * (i + 1.0), 180, ad, al(ad))
    for i, ad in enumerate(ust):
        pin(TIP.get(ad, 'passive'), x0 + pitch * (i + 2.0), y1 - 5.08, 270, ad, al(ad))
    L.append('    )')
    L.append('  )')
    L.append(')')
    open(os.path.join(D, 'Simcom.kicad_sym'), 'w').write('\n'.join(L) + '\n')

if __name__ == '__main__':
    ayak_yaz(); sembol_yaz(); print('tamam')

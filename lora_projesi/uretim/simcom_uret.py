import os, sys
D = os.path.join(os.path.dirname(__file__), 'kutuphane')

# SIMCom SIM7600E/E-H Hardware Design V1.02 (Table 3 ve Figure 2): kenar sirasi
SOL = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 81]
ALT = [84] + list(range(21, 41)) + [83]
SAG = [85] + list(range(60, 40, -1)) + [82]
UST = [86] + list(range(80, 60, -1)) + [87]

ISIM = {1: 'GND', 2: 'GND', 3: 'PWRKEY', 4: 'RESET', 5: 'GND', 6: 'SPI_CLK', 7: 'SPI_MISO', 8: 'SPI_MOSI', 9: 'SPI_CS', 10: 'GND',
        11: 'USB_VBUS', 12: 'USB_DN', 13: 'USB_DP', 14: 'GND', 15: 'VDD_1V8', 16: 'USB_ID', 17: 'USIM_DATA', 18: 'USIM_RST', 19: 'USIM_CLK', 20: 'USIM_VDD',
        21: 'SD_CMD', 22: 'SD_DATA0', 23: 'SD_DATA1', 24: 'SD_DATA2', 25: 'SD_DATA3', 26: 'SD_CLK', 27: 'SDIO_DATA1', 28: 'SDIO_DATA2', 29: 'SDIO_CMD',
        30: 'SDIO_DATA0', 31: 'SDIO_DATA3', 32: 'SDIO_CLK', 33: 'GPIO3', 34: 'GPIO6', 35: 'HSIC_STROBE', 36: 'HSIC_DATA', 37: 'GND', 38: 'VBAT', 39: 'VBAT',
        40: 'GND', 41: 'GND', 42: 'NC', 43: 'GND', 44: 'VDD_AUX', 45: 'ISINK', 46: 'ADC2', 47: 'ADC1', 48: 'SD_DET', 49: 'STATUS', 50: 'GPIO43',
        51: 'NETLIGHT', 52: 'GPIO41', 53: 'USIM_DET', 54: 'FLIGHTMODE', 55: 'SCL', 56: 'SDA', 57: 'GND', 58: 'GND', 59: 'AUX_ANT', 60: 'GND', 61: 'GND',
        62: 'VBAT', 63: 'VBAT', 64: 'GND', 65: 'GND', 66: 'RTS', 67: 'CTS', 68: 'RXD', 69: 'RI', 70: 'DCD', 71: 'TXD', 72: 'DTR', 73: 'PCM_OUT', 74: 'PCM_IN',
        75: 'PCM_SYNC', 76: 'PCM_CLK', 77: 'GND', 78: 'GND', 79: 'GNSS_ANT', 80: 'GND', 81: 'GND', 82: 'MAIN_ANT', 83: 'COEX1', 84: 'COEX2', 85: 'BOOT_CFG0',
        86: 'COEX3', 87: 'GPIO77'}

def ayak_yaz():
    pads = []
    for i, n in enumerate(SOL): pads.append((n, -15.1, -10.5 + i, 1.8, 0.6))
    for i, n in enumerate(ALT): pads.append((n, -10.5 + i, 15.1, 0.6, 1.8))
    for i, n in enumerate(SAG): pads.append((n, 15.1, -10.5 + i, 1.8, 0.6))
    for i, n in enumerate(UST): pads.append((n, -10.5 + i, -15.1, 0.6, 1.8))
    assert sorted(p[0] for p in pads) == list(range(1, 88))
    out = ['(footprint "SIM7600_LCC87" (version 20221018) (generator pcbnew)', '  (layer "F.Cu")',
           '  (descr "SIMCom SIM7600 serisi LCC 87 pad, 30x30 mm, 1.00 mm adim; SIM7600E/E-H Hardware Design V1.02 Sekil 2-4")',
           '  (tags "SIM7600 LCC87")', '  (attr smd)',
           '  (fp_text reference "REF**" (at 0 -17.5) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
           '  (fp_text value "SIM7600_LCC87" (at 0 17.5) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))']
    for (a, b, c, d) in [(-15, -15, 15, -15), (15, -15, 15, 15), (15, 15, -15, 15), (-15, 15, -15, -15)]:
        out.append('  (fp_line (start %s %s) (end %s %s) (layer "F.Fab") (width 0.1))' % (a, b, c, d))
    for (a, b, c, d) in [(-16.5, -16.5, 16.5, -16.5), (16.5, -16.5, 16.5, 16.5), (16.5, 16.5, -16.5, 16.5), (-16.5, 16.5, -16.5, -16.5)]:
        out.append('  (fp_line (start %s %s) (end %s %s) (layer "F.CrtYd") (width 0.05))' % (a, b, c, d))
    out.append('  (fp_circle (center -13.5 -13.5) (end -13.0 -13.5) (layer "F.SilkS") (width 0.15) (fill solid))')
    for n, x, y, w, h in sorted(pads):
        out.append('  (pad "%d" smd roundrect (at %s %s) (size %s %s) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.4))' % (n, x, y, w, h))
    out.append(')')
    open(os.path.join(D, 'Simcom.pretty', 'SIM7600_LCC87.kicad_mod'), 'w').write('\n'.join(out) + '\n')

TIP = {'GND': 'power_in', 'VBAT': 'power_in', 'VDD_1V8': 'power_out', 'VDD_AUX': 'power_out', 'USIM_VDD': 'power_out', 'NC': 'no_connect',
       'TXD': 'output', 'RTS': 'output', 'RI': 'output', 'DCD': 'output', 'STATUS': 'output', 'NETLIGHT': 'output',
       'RXD': 'input', 'CTS': 'input', 'DTR': 'input', 'PWRKEY': 'input', 'RESET': 'input', 'FLIGHTMODE': 'input'}

def sembol_yaz():
    sol = ['PWRKEY', 'RESET', 'FLIGHTMODE', 'STATUS', 'NETLIGHT', 'TXD', 'RXD', 'RTS', 'CTS', 'DTR', 'DCD', 'RI',
           'USIM_VDD', 'USIM_DATA', 'USIM_RST', 'USIM_CLK', 'USIM_DET', 'SCL', 'SDA', 'ADC1', 'ADC2', 'ISINK']
    sag = ['MAIN_ANT', 'AUX_ANT', 'GNSS_ANT', 'USB_VBUS', 'USB_DN', 'USB_DP', 'USB_ID', 'BOOT_CFG0', 'COEX1', 'COEX2', 'COEX3',
           'PCM_OUT', 'PCM_IN', 'PCM_SYNC', 'PCM_CLK', 'SPI_CLK', 'SPI_MISO', 'SPI_MOSI', 'SPI_CS', 'GPIO3', 'GPIO6', 'GPIO41', 'GPIO43', 'GPIO77', 'SD_DET',
           'SD_CMD', 'SD_DATA0', 'SD_DATA1', 'SD_DATA2', 'SD_DATA3', 'SD_CLK', 'SDIO_CMD', 'SDIO_DATA0', 'SDIO_DATA1', 'SDIO_DATA2', 'SDIO_DATA3', 'SDIO_CLK',
           'HSIC_STROBE', 'HSIC_DATA', 'NC']
    ust = ['VBAT', 'VBAT', 'VBAT', 'VBAT', 'VDD_1V8', 'VDD_AUX']
    alt = ['GND'] * 19
    tum = {}
    for n, ad in ISIM.items(): tum.setdefault(ad, []).append(n)
    secili = {}
    def al(ad):
        i = secili.get(ad, 0); secili[ad] = i + 1
        return tum[ad][i]
    assert sorted(tum) == sorted(set(sol + sag + ust + alt)), set(tum) ^ set(sol + sag + ust + alt)
    pitch = 2.54
    n_sag = len(sag)
    h = n_sag * pitch + 2 * pitch
    w = 19 * pitch + 2 * pitch
    x0, x1 = -w / 2, w / 2
    y0, y1 = h / 2, -h / 2
    L = []
    L.append('(kicad_symbol_lib (version 20220914) (generator simcom_uret)')
    L.append('  (symbol "SIM7600SA" (in_bom yes) (on_board yes)')
    L.append('    (property "Reference" "U" (at 0 %s 0) (effects (font (size 1.27 1.27))))' % (y1 - 3))
    L.append('    (property "Value" "SIM7600SA" (at 0 %s 0) (effects (font (size 1.27 1.27))))' % (y0 + 3))
    L.append('    (property "Footprint" "Simcom:SIM7600_LCC87" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    L.append('    (property "Datasheet" "SIM7600E_SIM7600E-H Hardware Design V1.02" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    L.append('    (symbol "SIM7600SA_0_1" (rectangle (start %s %s) (end %s %s) (stroke (width 0.254) (type default)) (fill (type background))))' % (x0, y1, x1, y0))
    L.append('    (symbol "SIM7600SA_1_1"')
    def pin(tip, x, y, ang, ad, num):
        L.append('      (pin %s line (at %s %s %s) (length 5.08) (name "%s" (effects (font (size 1.27 1.27)))) (number "%d" (effects (font (size 1.27 1.27)))))' % (tip, round(x, 3), round(y, 3), ang, ad, num))
    for i, ad in enumerate(sol):
        pin(TIP.get(ad, 'bidirectional'), x0 - 5.08, y1 + pitch * (i + 1.0), 0, ad, al(ad))
    for i, ad in enumerate(sag):
        t = TIP.get(ad, 'bidirectional')
        if ad in ('MAIN_ANT', 'AUX_ANT', 'GNSS_ANT'): t = 'passive'
        pin(t, x1 + 5.08, y1 + pitch * (i + 1.0), 180, ad, al(ad))
    for i, ad in enumerate(ust):
        pin(TIP.get(ad, 'passive'), x0 + pitch * (i + 2.0) * 1.0, y1 - 5.08, 270, ad, al(ad))
    for i, ad in enumerate(alt):
        pin('power_in', x0 + pitch * (i + 1.0), y0 + 5.08, 90, ad, al(ad))
    L.append('    )')
    L.append('  )')
    L.append(')')
    open(os.path.join(D, 'Simcom.kicad_sym'), 'w').write('\n'.join(L) + '\n')

if __name__ == '__main__':
    ayak_yaz(); sembol_yaz(); print('tamam')

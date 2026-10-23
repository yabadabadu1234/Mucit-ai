import os, sys
D = os.path.join(os.path.dirname(__file__), 'kutuphane')

# Ai-Thinker Ra-01H (SX1276, 803-930 MHz): pin tablosu Ra-01H Specification V1 Tablo 2.2; ayak izi olculeri Ra-01/Ra-02 User Manual Sekil 6 (ayni 17 x 16 mm govde, ayni 16 pin)
RA = {1: 'ANT', 2: 'GND', 3: 'VDD', 4: 'RESET', 5: 'DIO0', 6: 'DIO1', 7: 'DIO2', 8: 'DIO3', 9: 'GND', 10: 'DIO4', 11: 'DIO5', 12: 'SCK', 13: 'MISO', 14: 'MOSI', 15: 'NSS', 16: 'GND'}

def ra01h_ayak():
    out = ['(footprint "Ra-01H" (version 20221018) (generator pcbnew)', '  (layer "F.Cu")',
           '  (descr "Ai-Thinker Ra-01H LoRa modulu, 17 x 16 mm, 16 yarim delikli pad, 2.0 mm adim; Ra-01/Ra-02 User Manual Sekil 4 ve 6")',
           '  (tags "Ra-01H LoRa SX1276")', '  (attr smd)',
           '  (fp_text reference "REF**" (at 0 -10.2) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
           '  (fp_text value "Ra-01H" (at 0 10.2) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))']
    for (a, b, c, d) in [(-8, -8.5, 8, -8.5), (8, -8.5, 8, 8.5), (8, 8.5, -8, 8.5), (-8, 8.5, -8, -8.5)]:
        out.append('  (fp_line (start %s %s) (end %s %s) (layer "F.Fab") (width 0.1))' % (a, b, c, d))
    for (a, b, c, d) in [(-9.5, -9.0, 9.5, -9.0), (9.5, -9.0, 9.5, 9.0), (9.5, 9.0, -9.5, 9.0), (-9.5, 9.0, -9.5, -9.0)]:
        out.append('  (fp_line (start %s %s) (end %s %s) (layer "F.CrtYd") (width 0.05))' % (a, b, c, d))
    out.append('  (fp_circle (center -9.4 -8.2) (end -9.0 -8.2) (layer "F.SilkS") (width 0.15) (fill solid))')
    ys = [-7, -5, -3, -1, 1, 3, 5, 7]
    for i, y in enumerate(ys):
        n = i + 1
        uz = 2.8 if n == 1 else 2.6
        out.append('  (pad "%d" smd roundrect (at %s %s) (size %s 1.1) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2))' % (n, -8.0 - 1.0 + uz / 2, y, uz))
    for i, y in enumerate(reversed(ys)):
        n = 9 + i
        out.append('  (pad "%d" smd roundrect (at %s %s) (size 2.6 1.1) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2))' % (n, 8.0 + 1.0 - 2.6 / 2, y))
    out.append(')')
    os.makedirs(os.path.join(D, 'Ozel.pretty'), exist_ok=True)
    open(os.path.join(D, 'Ozel.pretty', 'Ra-01H.kicad_mod'), 'w').write('\n'.join(out) + '\n')

def _pin(L, tip, x, y, ang, ad, num):
    L.append('      (pin %s line (at %s %s %s) (length 5.08) (name "%s" (effects (font (size 1.27 1.27)))) (number "%s" (effects (font (size 1.27 1.27)))))' % (tip, round(x, 3), round(y, 3), ang, ad, num))

def sembol_yaz():
    L = ['(kicad_symbol_lib (version 20220914) (generator ozel_uret)']
    # Ra-01H
    sol = [(4, 'RESET', 'input'), (5, 'DIO0', 'bidirectional'), (6, 'DIO1', 'bidirectional'), (7, 'DIO2', 'bidirectional'), (8, 'DIO3', 'bidirectional'),
           (10, 'DIO4', 'bidirectional'), (11, 'DIO5', 'bidirectional')]
    sag = [(15, 'NSS', 'input'), (12, 'SCK', 'input'), (14, 'MOSI', 'input'), (13, 'MISO', 'output'), (1, 'ANT', 'passive')]
    L.append('  (symbol "Ra-01H" (in_bom yes) (on_board yes)')
    L.append('    (property "Reference" "U" (at 0 -11.43 0) (effects (font (size 1.27 1.27))))')
    L.append('    (property "Value" "Ra-01H" (at 0 11.43 0) (effects (font (size 1.27 1.27))))')
    L.append('    (property "Footprint" "Ozel:Ra-01H" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    L.append('    (property "Datasheet" "Ai-Thinker Ra-01H Specification V1" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    L.append('    (symbol "Ra-01H_0_1" (rectangle (start -7.62 -10.16) (end 7.62 10.16) (stroke (width 0.254) (type default)) (fill (type background))))')
    L.append('    (symbol "Ra-01H_1_1"')
    for i, (n, ad, t) in enumerate(sol):
        _pin(L, t, -7.62 - 5.08, 7.62 - 2.54 * i, 0, ad, n)
    for i, (n, ad, t) in enumerate(sag):
        _pin(L, t, 7.62 + 5.08, 7.62 - 2.54 * i, 180, ad, n)
    _pin(L, 'power_in', 0, 10.16 + 5.08, 270, 'VDD', 3)
    for i, n in enumerate((2, 9, 16)):
        _pin(L, 'power_in', -2.54 + 2.54 * i, -10.16 - 5.08, 90, 'GND', n)
    L.append('    )')
    L.append('  )')
    # LM66100 (SC-70-6): LM66100 datasheet SLVSEZ8A Tablo "Pin Functions"
    L.append('  (symbol "LM66100" (in_bom yes) (on_board yes)')
    L.append('    (property "Reference" "U" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))')
    L.append('    (property "Value" "LM66100" (at 0 7.62 0) (effects (font (size 1.27 1.27))))')
    L.append('    (property "Footprint" "Package_TO_SOT_SMD:SOT-363_SC-70-6" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    L.append('    (property "Datasheet" "TI SLVSEZ8A" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    L.append('    (symbol "LM66100_0_1" (rectangle (start -5.08 -5.08) (end 5.08 5.08) (stroke (width 0.254) (type default)) (fill (type background))))')
    L.append('    (symbol "LM66100_1_1"')
    _pin(L, 'power_in', -5.08 - 5.08, 2.54, 0, 'VIN', 1)
    _pin(L, 'input', -5.08 - 5.08, -2.54, 0, 'CE', 3)
    _pin(L, 'power_out', 5.08 + 5.08, 2.54, 180, 'VOUT', 6)
    _pin(L, 'open_collector', 5.08 + 5.08, -2.54, 180, 'ST', 5)
    _pin(L, 'no_connect', 5.08 + 5.08, 0, 180, 'NC', 4)
    _pin(L, 'power_in', 0, -5.08 - 5.08, 90, 'GND', 2)
    L.append('    )')
    L.append('  )')
    L.append(')')
    open(os.path.join(D, 'Ozel.kicad_sym'), 'w').write('\n'.join(L) + '\n')

if __name__ == '__main__':
    ra01h_ayak(); sembol_yaz(); print('tamam')

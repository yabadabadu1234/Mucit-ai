import os
from breadboard import Breadboard
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
TP, TM, BP, BM = ("top", "+"), ("top", "-"), ("bot", "+"), ("bot", "-")

def lab(b, x, y, t, c="#222222"): b.label(x, y, t, c, 7.5, True, True)

def t_fig1(load=False):
    b = Breadboard()
    b.resistor("R1", (5, "a"), (10, "a"), 2200, "R1 2,2 kΩ")
    b.resistor("R2", (10, "b"), (15, "b"), 3300, "R2 3,3 kΩ")
    b.resistor("R3", (10, "c"), (20, "c"), 2200, "R3 2,2 kΩ")
    b.wire((5, "b"), (5, TP), "red"); b.wire((15, "a"), (15, BM), "black")
    b.lead("Vs", (2, TP), "", "red"); b.lead("GND", (28, BM), "", "black")
    exp = {"VS": [("R1", 1)], "A": [("R1", 2), ("R2", 1), ("R3", 1)], "GND": [("R2", 2)], "OC": [("R3", 2)]}
    if load:
        b.resistor("RLa", (20, "a"), (25, "a"), 3300, "RL1 3,3 kΩ"); b.resistor("RLb", (25, "b"), (29, "b"), 220, "RL2 220 Ω")
        b.wire((29, "a"), (29, BM), "black"); exp["OC"] += [("RLa", 1)]; exp["GND"] += [("RLb", 2)]
        lab(b, 22.5, 1.9, "RL = 3,3 kΩ + 220 Ω = 3,52 kΩ", "#004488")
    b.lead("VO", (20, "e"), "", "#E0B000")
    lab(b, 6.8, 5.0, "+10 V (kaynak +)", "#B00000"); lab(b, 23, -6.9, "Kaynak − / toprak", "#222222")
    exp["VS"].append(("Vs", 1)); exp["GND"].append(("GND", 1)); exp["OC"].append(("VO", 1))
    b.check(exp)
    return b

def t_fig3():
    b = Breadboard()
    b.resistor("R1", (4, "a"), (12, "a"), 15000, "R1 15 kΩ"); b.resistor("R2", (4, "b"), (9, "b"), 15000, "R2 15 kΩ")
    b.resistor("R5", (9, "c"), (11, "c"), 1000, "R5 1 kΩ"); b.resistor("R4", (9, "d"), (16, "d"), 1000, "R4 1 kΩ")
    b.resistor("R3", (12, "e"), (16, "e"), 3900, "R3 3,9 kΩ"); b.resistor("R6", (16, "c"), (20, "c"), 8200, "R6 8,2 kΩ")
    b.wire((11, "b"), (11, BM), "black"); b.wire((20, "b"), (20, BM), "black")
    b.lead("VS1", (4, "e"), "", "red"); b.lead("VS2", (9, "e"), "", "orange"); b.lead("GND", (27, BM), "", "black"); b.lead("VC", (16, "a"), "", "#E0B000")
    lab(b, 4, 4.9, "VS1 = +12 V", "#B00000"); lab(b, 9.3, 4.9, "VS2 = +5 V", "#EF6C00")
    lab(b, 16, -2.9 + 0.2, "C (çıkış)", "#806000"); lab(b, 24, -6.9, "Kaynakların − uçları ve D = toprak", "#222222")
    lab(b, 4, 7.7, "A", "#444"); lab(b, 12, 7.7, "B", "#444"); lab(b, 9, 7.7, "X", "#444"); lab(b, 16, 7.7, "C", "#444")
    b.check({"A": [("R1", 1), ("R2", 1), ("VS1", 1)], "B": [("R1", 2), ("R3", 1)], "X": [("R2", 2), ("R5", 1), ("R4", 1), ("VS2", 1)],
             "C": [("R4", 2), ("R3", 2), ("R6", 1), ("VC", 1)], "GND": [("R5", 2), ("R6", 2), ("GND", 1)]})
    return b

def op_base(kind):
    b = Breadboard()
    b.ic8("U1", 15, "UA741")
    b.wire((16, "j"), (16, TP), "red"); b.wire((18, "a"), (18, TM), "blue")
    b.lead("VCC", (12, TP), "", "red"); b.lead("VEE", (24, TM), "", "blue"); b.lead("GND", (27, BM), "", "black")
    b.wire((14, "h"), (16, "d"), "magenta", 0.12)   # IN- -> geri besleme basamağı (sütun 14 üst)
    b.wire((17, "g"), (21, "g"), "yellow")          # OUT -> sütun 21 üst
    b.lead("VO", (21, "j"), "", "#E0B000")
    lab(b, 12.2, 5.0, "+15 V (V+, pin 7)", "#B00000"); lab(b, 24.5, 11.4, "−15 V (V−, pin 4)", "#1565C0")
    lab(b, 24, -6.9, "Toprak (kaynakların − uçları)", "#222222"); lab(b, 23.4, 5.1, "Vo", "#806000")
    return b

def t3_inv():
    b = op_base("inv")
    b.resistor("R1", (10, "a"), (16, "a"), 10000, "R1 10 kΩ"); b.resistor("R2", (14, "i"), (21, "i"), 100000, "R2 100 kΩ")
    b.wire((17, "d"), (17, BM), "black"); b.lead("Vs", (10, "d"), "", "orange"); lab(b, 8.0, 1.0, "Vs", "#EF6C00")
    b.check({"INV": [("R1", 2), ("U1", 2), ("R2", 1)], "INP": [("U1", 3), ("GND", 1)], "OUT": [("R2", 2), ("U1", 6), ("VO", 1)],
             "VIN": [("R1", 1), ("Vs", 1)], "V+": [("U1", 7), ("VCC", 1)], "V-": [("U1", 4), ("VEE", 1)]})
    return b

def t3_noninv():
    b = op_base("noninv")
    b.resistor("Rs", (10, "a"), (17, "a"), 1000, "Rs 1 kΩ"); b.resistor("Rg", (16, "b"), (12, "b"), 10000, "Rg 10 kΩ")
    b.resistor("Rf", (14, "i"), (21, "i"), 100000, "Rf 100 kΩ")
    b.wire((12, "c"), (12, BM), "black"); b.lead("Vg", (10, "d"), "", "orange"); lab(b, 8.0, 1.0, "Vg", "#EF6C00")
    b.check({"INV": [("Rg", 1), ("U1", 2), ("Rf", 1)], "INP": [("Rs", 2), ("U1", 3)], "OUT": [("Rf", 2), ("U1", 6), ("VO", 1)],
             "VG": [("Rs", 1), ("Vg", 1)], "GND": [("Rg", 2), ("GND", 1)], "V+": [("U1", 7), ("VCC", 1)], "V-": [("U1", 4), ("VEE", 1)]})
    return b

def t3_diff():
    b = op_base("diff")
    b.resistor("R1", (8, "a"), (16, "a"), 10000, "R1 10 kΩ"); b.resistor("R3", (10, "b"), (17, "b"), 33000, "R3 33 kΩ")
    b.resistor("R4", (17, "c"), (21, "c"), 39000, "R4 39 kΩ"); b.resistor("R2", (14, "i"), (21, "i"), 18000, "R2 18 kΩ")
    b.wire((21, "b"), (21, BM), "black"); b.lead("V1", (8, "c"), "", "orange"); b.lead("V2", (10, "d"), "", "magenta")
    lab(b, 6.3, 1.0, "V1", "#EF6C00"); lab(b, 8.6, 2.3, "V2", "#C2188F")
    b.check({"INV": [("R1", 2), ("U1", 2), ("R2", 1)], "INP": [("R3", 2), ("U1", 3), ("R4", 1)], "OUT": [("R2", 2), ("U1", 6), ("VO", 1)],
             "N1": [("R1", 1), ("V1", 1)], "N2": [("R3", 1), ("V2", 1)], "GND": [("R4", 2), ("GND", 1)], "V+": [("U1", 7), ("VCC", 1)], "V-": [("U1", 4), ("VEE", 1)]})
    return b

def t3_sum():
    b = op_base("sum")
    b.resistor("R1", (8, "a"), (16, "a"), 10000, "R1 10 kΩ"); b.resistor("R2", (10, "b"), (16, "b"), 18000, "R2 18 kΩ")
    b.resistor("R3", (14, "i"), (21, "i"), 33000, "R3 33 kΩ")
    b.wire((17, "d"), (17, BM), "black"); b.lead("V1", (8, "c"), "", "orange"); b.lead("V2", (10, "d"), "", "magenta")
    lab(b, 6.3, 1.0, "V1", "#EF6C00"); lab(b, 8.6, 2.3, "V2", "#C2188F")
    b.check({"INV": [("R1", 2), ("R2", 2), ("U1", 2), ("R3", 1)], "INP": [("U1", 3), ("GND", 1)], "OUT": [("R3", 2), ("U1", 6), ("VO", 1)],
             "N1": [("R1", 1), ("V1", 1)], "N2": [("R2", 1), ("V2", 1)], "V+": [("U1", 7), ("VCC", 1)], "V-": [("U1", 4), ("VEE", 1)]})
    return b

if __name__ == "__main__":
    for n, f in (("bb_t2_f1", lambda: t_fig1()), ("bb_t2_f2", lambda: t_fig1(True)), ("bb_t2_f3", t_fig3), ("bb_t3_inv", t3_inv), ("bb_t3_noninv", t3_noninv),
                 ("bb_t3_diff", t3_diff), ("bb_t3_sum", t3_sum)):
        f().draw(os.path.join(A, n + ".png"), figsize=(13, 5.4)); print(n)

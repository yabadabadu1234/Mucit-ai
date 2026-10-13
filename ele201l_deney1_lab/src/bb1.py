import os
from breadboard import Breadboard
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
TP, TM, BP, BM = ("top", "+"), ("top", "-"), ("bot", "+"), ("bot", "-")
def lab(b, x, y, t, c="#222222"): b.label(x, y, t, c, 7.5, True, True)
def series():
    b = Breadboard()
    b.resistor("R1", (5, "a"), (10, "a"), 470, "R1 470 Ω"); b.resistor("R2", (10, "b"), (15, "b"), 100000, "R2 100 kΩ"); b.resistor("R3", (15, "c"), (20, "c"), 10e6, "R3 10 MΩ")
    b.lead("P1", (5, "e"), "", "red"); b.lead("P2", (20, "e"), "", "black")
    b.check({"1": [("R1", 1), ("P1", 1)], "2": [("R1", 2), ("R2", 1)], "3": [("R2", 2), ("R3", 1)], "4": [("R3", 2), ("P2", 1)]})
    lab(b, 5, 4.9, "Multimetre (+)", "#B00000"); lab(b, 20, 4.9, "Multimetre (−)", "#222222")
    return b
def parallel():
    b = Breadboard()
    b.resistor("R1", (5, "a"), (12, "a"), 470, "R1 470 Ω"); b.resistor("R2", (5, "b"), (12, "b"), 100000, "R2 100 kΩ"); b.resistor("R3", (5, "c"), (12, "c"), 10e6, "R3 10 MΩ")
    b.lead("P1", (5, "e"), "", "red"); b.lead("P2", (12, "e"), "", "black")
    b.check({"1": [("R1", 1), ("R2", 1), ("R3", 1), ("P1", 1)], "2": [("R1", 2), ("R2", 2), ("R3", 2), ("P2", 1)]})
    lab(b, 5, 4.9, "Multimetre (+)", "#B00000"); lab(b, 12, 4.9, "Multimetre (−)", "#222222")
    return b
def divider():
    b = Breadboard()
    b.resistor("R1", (5, "a"), (10, "a"), 470, "R üst (470 Ω / 100 kΩ / 10 MΩ)"); b.resistor("R2", (10, "b"), (15, "b"), 470, "R alt (aynı değer)")
    b.wire((5, "b"), (5, TP), "red"); b.wire((15, "a"), (15, BM), "black")
    b.lead("Vs", (2, TP), "", "red"); b.lead("GND", (28, BM), "", "black"); b.lead("VO", (10, "e"), "", "#E0B000")
    b.check({"VS": [("R1", 1), ("Vs", 1)], "VO": [("R1", 2), ("R2", 1), ("VO", 1)], "GND": [("R2", 2), ("GND", 1)]})
    lab(b, 6.8, 5.0, "+15 V", "#B00000"); lab(b, 10, 4.9, "VO (multimetre / osiloskop)", "#806000"); lab(b, 23, -6.9, "Kaynak − / toprak", "#222222")
    return b
def wheat():
    b = Breadboard()
    b.resistor("R1", (5, "a"), (10, "a"), 470, "R1 470 Ω"); b.resistor("R2", (5, "b"), (20, "b"), 470, "R2 470 Ω")
    b.resistor("R3", (10, "c"), (15, "c"), 3200, "R3 pot. (≈3,2 kΩ)"); b.resistor("Rx", (20, "c"), (25, "c"), 3300, "Rx (bilinmeyen)")
    b.wire((5, "e"), (5, TP), "red"); b.wire((15, "e"), (25, "e"), "green", 0.15); b.wire((15, "d"), (15, BM), "black")
    b.lead("Vs", (2, TP), "", "red"); b.lead("GND", (28, BM), "", "black"); b.lead("VBp", (10, "e"), "", "#E0B000"); b.lead("VBm", (20, "e"), "", "#1565C0")
    b.check({"T": [("R1", 1), ("R2", 1), ("Vs", 1)], "L": [("R1", 2), ("R3", 1), ("VBp", 1)], "Rr": [("R2", 2), ("Rx", 1), ("VBm", 1)], "G": [("R3", 2), ("Rx", 2), ("GND", 1)]})
    lab(b, 6.5, 5.0, "+15 V", "#B00000"); lab(b, 10, 4.9, "VB (+)", "#806000"); lab(b, 20, 4.9, "VB (−)", "#1565C0"); lab(b, 23, -6.9, "Toprak", "#222222")
    return b
def dac():
    b = Breadboard()
    for k, c in enumerate((3, 4, 5)): pass
    b.resistor("Ri1", (3, "a"), (8, "a"), 2000, "2 kΩ"); b.resistor("Ri2", (4, "a"), (13, "a"), 2000, "2 kΩ"); b.resistor("Ri3", (5, "a"), (18, "a"), 2000, "2 kΩ")
    b.resistor("Ra", (8, "b"), (13, "b"), 1000, "1 kΩ"); b.resistor("Rb", (13, "c"), (18, "c"), 1000, "1 kΩ"); b.resistor("Rt", (18, "d"), (23, "d"), 2000, "2 kΩ")
    b.resistor("RL", (8, "c"), (26, "c"), 1000, "RL 1 kΩ")
    b.wire((23, "e"), (23, BM), "black"); b.wire((26, "d"), (26, BM), "black")
    b.lead("B2", (3, "e"), "", "red"); b.lead("B1", (4, "e"), "", "orange"); b.lead("B0", (5, "e"), "", "#C2188F")
    b.lead("VO", (8, "e"), "", "#E0B000"); b.lead("GND", (29, BM), "", "black")
    b.check({"A": [("Ri1", 2), ("Ra", 1), ("RL", 1), ("VO", 1)], "B": [("Ri2", 2), ("Ra", 2), ("Rb", 1)], "C": [("Ri3", 2), ("Rb", 2), ("Rt", 1)],
             "I1": [("Ri1", 1), ("B2", 1)], "I2": [("Ri2", 1), ("B1", 1)], "I3": [("Ri3", 1), ("B0", 1)], "G": [("Rt", 2), ("RL", 2), ("GND", 1)]})
    lab(b, 3, 4.9, "MSB", "#B00000"); lab(b, 4.5, 4.9, "", "#222"); lab(b, 8, 4.9, "VO", "#806000"); lab(b, 5.2, 7.2, "LSB", "#C2188F")
    return b
if __name__ == "__main__":
    for n, f, sz in [("bb_seri", series, (12, 4.6)), ("bb_par", parallel, (12, 4.6)), ("bb_bol", divider, (12, 5)), ("bb_whe", wheat, (12, 5)), ("bb_dac", dac, (12, 5))]:
        f().draw(os.path.join(A, n + ".png"), figsize=sz); print(n)

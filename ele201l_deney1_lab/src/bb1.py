import os
from bblab import Lab
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
TP, TM = ("top", "+"), ("top", "-")
def series():
    b = Lab()
    b.resistor("R1", (5, "a"), (10, "a"), 470, "R1 470 Ω", below=True); b.resistor("R2", (10, "b"), (15, "b"), 100000, "R2 100 kΩ"); b.resistor("R3", (15, "c"), (20, "c"), 10e6, "R3 10 MΩ")
    b.lead("P1", (5, "e")); b.lead("P2", (20, "e")); b.dmm(10.5, 15, "Ω", "P1", "P2", "Multimetre (Ω kademesi)")
    b.check({"1": [("R1", 1), ("P1", 1)], "2": [("R1", 2), ("R2", 1)], "3": [("R2", 2), ("R3", 1)], "4": [("R3", 2), ("P2", 1)]}); return b
def parallel():
    b = Lab()
    b.resistor("R1", (5, "a"), (12, "a"), 470, "R1 470 Ω", below=True); b.resistor("R2", (5, "b"), (12, "b"), 100000, "R2 100 kΩ", below=True); b.resistor("R3", (5, "c"), (12, "c"), 10e6, "R3 10 MΩ")
    b.lead("P1", (5, "e")); b.lead("P2", (12, "e")); b.dmm(10.5, 15, "Ω", "P1", "P2", "Multimetre (Ω kademesi)")
    b.check({"1": [("R1", 1), ("R2", 1), ("R3", 1), ("P1", 1)], "2": [("R1", 2), ("R2", 2), ("R3", 2), ("P2", 1)]}); return b
def divider():
    b = Lab()
    b.resistor("R1", (5, "a"), (10, "a"), 470, "R üst", below=True); b.resistor("R2", (10, "b"), (15, "b"), 470, "R alt")
    b.wire((5, "e"), (5, TP), "red"); b.wire((15, "e"), (15, TM), "black")
    for nme, h in (("Vs", (2, TP)), ("GND", (28, TM)), ("Vm", (10, "e")), ("Mg", (24, TM)), ("Vo", (10, "d")), ("Og", (26, TM))): b.lead(nme, h)
    b.psu(0.5, 15.5, "15,0 V", "Vs", "GND"); b.dmm(12.5, 15, "V DC", "Vm", "Mg", "Multimetre (DA V)"); b.scope(21.5, 15.5, "Vo", "Og")
    b.check({"VS": [("R1", 1), ("Vs", 1)], "VO": [("R1", 2), ("R2", 1), ("Vm", 1), ("Vo", 1)], "GND": [("R2", 2), ("GND", 1), ("Mg", 1), ("Og", 1)]}); return b
def wheat():
    b = Lab()
    b.resistor("R1", (5, "a"), (10, "a"), 470, "R1 470 Ω", below=True); b.resistor("R2", (5, "b"), (20, "b"), 470, "R2 470 Ω", below=True)
    b.resistor("R3", (10, "d"), (15, "d"), 3200, "R3 pot."); b.resistor("Rx", (15, "c"), (20, "c"), 3300, "Rx", below=True)
    b.wire((5, "e"), (5, TP), "red"); b.wire((15, "e"), (15, TM), "black")
    for nme, h in (("Vs", (2, TP)), ("GND", (28, TM)), ("Bp", (10, "e")), ("Bm", (20, "e"))): b.lead(nme, h)
    b.psu(0.5, 15.5, "15,0 V", "Vs", "GND"); b.dmm(16.5, 15, "V DC", "Bp", "Bm", "Multimetre (V_B)")
    b.check({"T": [("R1", 1), ("R2", 1), ("Vs", 1)], "L": [("R1", 2), ("R3", 1), ("Bp", 1)], "Rr": [("R2", 2), ("Rx", 2), ("Bm", 1)], "G": [("R3", 2), ("Rx", 1), ("GND", 1)]}); return b
def dac():
    b = Lab()
    b.resistor("Ri1", (3, "a"), (10, "a"), 2000, "Ri1", below=True); b.resistor("Ri2", (5, "b"), (16, "b"), 2000, "Ri2", below=True); b.resistor("Ri3", (7, "c"), (22, "c"), 2000, "Ri3")
    b.resistor("Ra", (10, "d"), (16, "d"), 1000, "Ra"); b.resistor("Rb", (16, "e"), (22, "e"), 1000, "Rb", below=True); b.resistor("Rt", (22, "d"), (27, "d"), 2000, "Rt")
    b.resistor("RL", (10, "h"), (26, "h"), 1000, "RL")
    b.wire((10, "e"), (10, "f"), "green"); b.wire((26, "i"), (26, TM), "black"); b.wire((27, "e"), (27, TM), "black")
    for c, nm in ((3, "i3"), (5, "i2"), (7, "i1")): b.wire((c, "e"), (c, TP), "orange")
    for nme, h in (("Vs", (1, TP)), ("GND", (29, TM)), ("Vm", (10, "j")), ("Mg", (28, TM))): b.lead(nme, h)
    b.psu(0.5, 15.5, "16,0 V", "Vs", "GND", "DA Güç Kaynağı (mantık 1)"); b.dmm(14.5, 15, "V DC", "Vm", "Mg", "Multimetre (V_O)")
    b.check({"A": [("Ri1", 2), ("Ra", 1), ("RL", 1), ("Vm", 1)], "B": [("Ri2", 2), ("Ra", 2), ("Rb", 1)], "C": [("Ri3", 2), ("Rb", 2), ("Rt", 1)], "G": [("Rt", 2), ("RL", 2), ("GND", 1), ("Mg", 1)], "P": [("Vs", 1), ("Ri1", 1), ("Ri2", 1), ("Ri3", 1)]})
    return b
if __name__ == "__main__":
    for n, f in [("bb_seri", series), ("bb_par", parallel), ("bb_bol", divider), ("bb_whe", wheat), ("bb_dac", dac)]:
        f().draw(os.path.join(A, n + ".png")); print(n)

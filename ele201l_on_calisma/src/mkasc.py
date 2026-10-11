import os
SER = "ELE201L Lab PC | Device S/N: TOBB-7K3Q-0421"
OUT = os.path.join(os.path.dirname(__file__), "..", "asc")


class S:
    def __init__(self, w=1000, h=700):
        self.l = ["Version 4", "SHEET 1 %d %d" % (w, h)]
        self.t = []

    def wire(self, *p):
        for a, b in zip(p, p[1:]):
            self.l.append("WIRE %d %d %d %d" % (a + b))

    def flag(self, x, y, n):
        self.l.append("FLAG %d %d %s" % (x, y, n))

    def res(self, name, val, x, y, rot="R0"):
        self.l += ["SYMBOL res %d %d %s" % (x, y, rot), "SYMATTR InstName " + name, "SYMATTR Value " + val]

    def vsrc(self, name, val, x, y):
        self.l += ["SYMBOL voltage %d %d R0" % (x, y), "SYMATTR InstName " + name, "SYMATTR Value " + val]

    def text(self, x, y, s, cmd=False):
        self.l.append("TEXT %d %d Left 2 %s%s" % (x, y, "!" if cmd else ";", s))

    def save(self, name, cmd, x=64, y=520):
        self.text(x, y, cmd, True)
        self.text(x, y + 32, SER)
        self.text(1100, 40, ".")
        open(os.path.join(OUT, name + ".asc"), "w").write("\n".join(self.l) + "\n")


def divider(name, rm, dc):
    s = S(1000, 800)
    s.vsrc("VS", "15", 80, 64)
    s.wire((80, 80), (256, 80)); s.res("R1", "10Meg", 240, 64)
    s.wire((256, 160), (256, 176)); s.wire((256, 176), (256, 192)); s.res("R2", "10Meg", 240, 176)
    s.wire((256, 272), (256, 288)); s.wire((80, 160), (80, 288)); s.wire((80, 288), (256, 288))
    s.flag(80, 288, 0); s.flag(256, 176, "VO")
    if rm:
        s.wire((256, 176), (384, 176)); s.wire((384, 176), (384, 192)); s.res("Rm", "10Meg", 368, 176)
        s.wire((384, 272), (384, 288)); s.wire((256, 288), (384, 288))
        s.text(420, 130, "Rm: voltmeter")
    s.save(name, ".dc VS 0 15 0.5" if dc else ".op", 64, 400)


def bridge(name, rx, dc):
    s = S()
    s.vsrc("VS", "15", 80, 64)
    s.wire((80, 80), (80, 64), (336, 64)); s.wire((192, 64), (192, 80)); s.wire((336, 64), (336, 80))
    s.res("R1", "470", 176, 64); s.res("R2", "470", 320, 64)
    s.wire((192, 160), (192, 192)); s.wire((336, 160), (336, 192))
    s.res("R3", "1k", 176, 176); s.res("Rx", rx, 320, 176)
    s.wire((192, 272), (192, 288), (336, 288)); s.wire((336, 272), (336, 288)); s.wire((80, 160), (80, 288), (192, 288))
    s.flag(80, 288, 0); s.flag(192, 160, "L"); s.flag(336, 160, "R"); s.flag(80, 64, "T")
    if dc:
        s.vsrc("Vsw", "10", 496, 64); s.flag(496, 80, "sw"); s.flag(496, 160, 0)
        s.text(440, 200, "Rx = V(sw) ohm (tarama)")
    s.save(name, ".dc Vsw 10 10000 10" if dc else ".op")


def dac(name, dc):
    s = S(1000, 800)
    if dc:
        s.vsrc("VH", "16", 64, 64); s.flag(64, 80, "A"); s.flag(64, 160, 0)
        names = ["A", "A", "A"]
    else:
        for i, x in enumerate((64, 192, 320)):
            s.vsrc("V%d" % (i + 1), "16", x, 64); s.flag(x, 80, "A%d" % (i + 1)); s.flag(x, 160, 0)
        names = ["A1", "A2", "A3"]
    for k, x in enumerate((272, 400, 528)):
        s.res("Rg%d" % (k + 1), "2k", x, 208)
        s.flag(x + 16, 224, names[k]); s.wire((x + 16, 304), (x + 16, 336))
    s.wire((288, 336), (304, 336)); s.res("RA", "1k", 400, 320, "R90"); s.wire((384, 336), (416, 336))
    s.wire((416, 336), (432, 336)); s.res("RB", "1k", 528, 320, "R90"); s.wire((512, 336), (544, 336))
    s.wire((288, 336), (288, 352)); s.res("RL", "1k", 272, 336)
    s.wire((544, 336), (544, 352)); s.res("Rt", "2k", 528, 336)
    s.flag(288, 336, "VO"); s.flag(416, 336, "N2"); s.flag(544, 336, "N3")
    s.wire((288, 432), (288, 448)); s.wire((544, 432), (544, 448)); s.flag(288, 448, 0); s.flag(544, 448, 0)
    s.save(name, ".dc VH 0 16 0.5" if dc else ".op", 64, 500)


def sp(name, par):
    s = S()
    s.vsrc("V1", "1", 80, 64)
    if not par:
        s.wire((80, 80), (144, 80))
        s.res("R1", "3.9k", 240, 64, "R90"); s.wire((224, 80), (240, 80))
        s.res("R2", "1k", 336, 64, "R90"); s.wire((320, 80), (336, 80))
        s.res("R3", "8.2k", 432, 64, "R90")
        s.wire((416, 80), (432, 80), (432, 192)); s.wire((80, 160), (80, 192), (432, 192))
        s.flag(80, 192, 0)
        s.text(460, 100, "Req = V1 / I(V1)")
    else:
        s.wire((80, 80), (80, 96), (416, 96))
        for nm, v, x in (("R1", "3.9k", 176), ("R2", "1k", 288), ("R3", "8.2k", 400)):
            s.res(nm, v, x, 96); s.wire((x + 16, 96), (x + 16, 112)); s.wire((x + 16, 192), (x + 16, 208))
        s.wire((80, 160), (80, 208), (416, 208)); s.flag(80, 208, 0)
        s.text(460, 100, "Req = V1 / I(V1)")
    s.save(name, ".op", 64, 280)


if __name__ == "__main__":
    divider("bol22_ideal", False, False)
    divider("bol22_rm", True, False)
    divider("bol22_dc", True, True)
    bridge("bol23_op", "1k", False)
    bridge("bol23_dc", "R=V(sw)", True)
    dac("bol24_op", False)
    dac("bol24_dc", True)
    sp("bol21_seri", False)
    sp("bol21_par", True)

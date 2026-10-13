import os
SER = "ELE201L Lab PC | Device S/N: TOBB-7K3Q-0421"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "asc")
UA741 = (".subckt UA741 1 2 3 4 5 params: Avol=200k GBW=1Meg Slew=500k Ilimit=80m Rail=2 Vos=0 Rin=2Meg\n"
         "X1 1 2 3 4 5 level2 Avol={Avol} GBW={GBW} Slew={Slew} Ilimit={Ilimit} Rail={Rail} Vos={Vos} Rin={Rin}\n.ends")

class Sch:
    def __init__(self, w=1000, h=700):
        self.l = ["Version 4", "SHEET 1 %d %d" % (w, h)]
        self.uses_op = False
    def wire(self, *p):
        for a, b in zip(p, p[1:]):
            self.l.append("WIRE %d %d %d %d" % (a + b))
    def flag(self, x, y, n):
        self.l.append("FLAG %d %d %s" % (x, y, n))
    def hres(self, name, val, xl, y):
        self.l += ["SYMBOL res %d %d R90" % (xl + 96, y - 16), "SYMATTR InstName " + name, "SYMATTR Value " + val]
    def vres(self, name, val, x, yt):
        self.l += ["SYMBOL res %d %d R0" % (x - 16, yt - 16), "SYMATTR InstName " + name, "SYMATTR Value " + val]
    def vsrc(self, name, val, x, yp):
        self.l += ["SYMBOL voltage %d %d R0" % (x, yp - 16), "SYMATTR InstName " + name, "SYMATTR Value " + val]
    def opamp(self, name, cx, cy):
        self.uses_op = True
        self.l += ["SYMBOL OpAmps\\UniversalOpAmp2 %d %d R0" % (cx, cy), "WINDOW 0 40 -48 Left 2", "WINDOW 3 40 -28 Left 2", "SYMATTR InstName " + name, "SYMATTR SpiceModel UA741",
                   "SYMATTR Value2 Avol=200k GBW=1Meg Slew=500k", "SYMATTR SpiceLine Ilimit=80m Rail=2 Vos=0", "SYMATTR SpiceLine2 Rin=2Meg"]
    def text(self, x, y, s, cmd=False):
        self.l.append("TEXT %d %d Left 2 %s%s" % (x, y, "!" if cmd else ";", s))
    def save(self, name, cmd, x=64, y=480):
        self.text(x, y, cmd.replace("\n", "\\n"), True)
        if self.uses_op:
            self.text(x, y + 64, ".lib UA741.lib", True)
            open(os.path.join(OUT, "UA741.lib"), "w").write("* UA741 (TI SLOS094H typical values; one-pole macromodel on LTspice level2)\n" + UA741 + "\n")
        self.text(x, y + 32, SER)
        open(os.path.join(OUT, name + ".asc"), "w").write("\n".join(self.l) + "\n")

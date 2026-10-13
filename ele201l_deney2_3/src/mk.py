from lt import Sch

def thev(name, mode):
    """Deney 2, Sekil 1/2: Vs=10 V, R1=2.2k, R2=3.3k, R3=2.2k. mode: voc | isc | rth | load | loaddc"""
    s = Sch()
    s.vsrc("Vs", "0" if mode == "rth" else "10", 80, 128); s.wire((80, 128), (144, 128)); s.hres("R1", "2.2k", 144, 128)
    s.wire((224, 128), (224, 144)); s.vres("R2", "3.3k", 224, 144); s.wire((224, 224), (224, 288))
    s.wire((224, 128), (304, 128)); s.hres("R3", "2.2k", 304, 128); s.wire((384, 128), (448, 128)); s.flag(448, 128, "oc")
    s.wire((80, 208), (80, 288)); s.wire((80, 288), (224, 288))
    if mode != "voc":
        s.wire((448, 128), (448, 144))
        if mode == "load":
            s.vres("RL", "3.52k", 448, 144)
        elif mode == "loaddc":
            s.vres("RL", "R=V(sw)", 448, 144)
        else:
            s.vsrc("Vsc" if mode == "isc" else "Vt", "0" if mode == "isc" else "1", 448, 144)
        s.wire((448, 224), (448, 288)); s.wire((224, 288), (448, 288))
    if mode == "loaddc":
        s.vsrc("Vsw", "10", 600, 144); s.flag(600, 144, "sw"); s.flag(600, 224, 0)
        s.text(560, 260, "RL = V(sw) ohm")
    s.flag(80, 288, 0)
    cmds = {"voc": ".op", "isc": ".op", "rth": ".op", "load": ".op", "loaddc": ".dc Vsw 100 10000 10"}
    s.save(name, cmds[mode], 64, 400)

def sup(name, v1, v2, mode="op"):
    """Deney 2, Sekil 3. mode: op | isc | rth"""
    s = Sch(1000, 800)
    s.vsrc("VS1", v1, 80, 288); s.wire((80, 288), (80, 192)); s.wire((80, 192), (80, 96)); s.flag(80, 96, "A")
    s.wire((80, 96), (96, 96)); s.hres("R1", "15k", 96, 96); s.wire((176, 96), (608, 96)); s.flag(608, 96, "B")
    s.wire((80, 192), (112, 192)); s.hres("R2", "15k", 112, 192); s.wire((192, 192), (336, 192))
    s.vsrc("VS2", v2, 336, 288); s.wire((336, 288), (336, 192)); s.wire((336, 192), (432, 192))
    s.wire((432, 192), (432, 272)); s.vres("R5", "1k", 432, 272); s.wire((432, 352), (432, 416))
    s.wire((432, 192), (464, 192)); s.hres("R4", "1k", 464, 192); s.wire((544, 192), (608, 192))
    s.wire((608, 96), (608, 112)); s.vres("R3", "3.9k", 608, 112); s.wire((608, 192), (608, 272)); s.vres("R6", "8.2k", 608, 272)
    s.wire((608, 352), (608, 416)); s.wire((608, 192), (672, 192)); s.flag(672, 192, "C")
    s.wire((80, 368), (80, 416)); s.wire((336, 368), (336, 416)); s.wire((80, 416), (336, 416)); s.wire((336, 416), (432, 416)); s.wire((432, 416), (608, 416))
    s.flag(80, 416, 0)
    if mode in ("isc", "rth"):
        s.wire((672, 192), (672, 288)); s.vsrc("Vsc" if mode == "isc" else "Vt", "0" if mode == "isc" else "1", 672, 288)
        s.wire((672, 368), (672, 416)); s.wire((608, 416), (672, 416))
    s.text(700, 380, "D = toprak")
    s.save(name, ".op", 64, 480)

def inv(name, amp, dc=False):
    s = Sch()
    s.vsrc("Vs", "0" if dc else "SINE(0 %s 1k)" % amp, 64, 176); s.wire((64, 176), (128, 176)); s.wire((64, 256), (64, 320)); s.flag(64, 320, 0)
    s.hres("R1", "10k", 128, 176); s.wire((208, 176), (240, 176))
    s.opamp("U1", 272, 192); s.wire((240, 208), (240, 240)); s.flag(240, 240, 0)
    s.wire((224, 176), (224, 48)); s.hres("R2", "100k", 224, 48); s.wire((304, 48), (352, 48)); s.wire((304, 192), (352, 192)); s.wire((352, 192), (352, 48)); s.flag(352, 192, "vo")
    s.flag(272, 160, "VCC"); s.flag(272, 224, "VEE"); s.flag(64, 176, "vs")
    s.vsrc("Vcc", "15", 448, 176); s.flag(448, 176, "VCC"); s.flag(448, 256, 0)
    s.vsrc("Vee", "-15", 528, 176); s.flag(528, 176, "VEE"); s.flag(528, 256, 0)
    s.save(name, ".dc Vs -2 2 0.01" if dc else ".tran 0 3m 0 2u", 64, 400)
    return s

def noninv(name, amp):
    s = Sch()
    s.vsrc("Vg", "SINE(0 %s 1k)" % amp, 64, 288); s.wire((64, 288), (144, 288)); s.hres("Rs", "1k", 144, 288); s.wire((224, 288), (240, 288)); s.wire((240, 288), (240, 208))
    s.opamp("U1", 272, 192); s.wire((240, 176), (192, 176)); s.wire((192, 176), (192, 192)); s.vres("Rg", "10k", 192, 192); s.flag(192, 272, 0)
    s.wire((224, 176), (224, 48)); s.hres("Rf", "100k", 224, 48); s.wire((304, 48), (352, 48)); s.wire((304, 192), (352, 192)); s.wire((352, 192), (352, 48)); s.flag(352, 192, "vo")
    s.flag(272, 160, "VCC"); s.flag(272, 224, "VEE"); s.flag(64, 288, "vg"); s.flag(64, 368, 0)
    s.vsrc("Vcc", "15", 448, 176); s.flag(448, 176, "VCC"); s.flag(448, 256, 0)
    s.vsrc("Vee", "-15", 528, 176); s.flag(528, 176, "VEE"); s.flag(528, 256, 0)
    s.save(name, ".tran 0 3m 0 2u", 64, 450)

def diff(name, e1, e2, tran):
    s = Sch()
    s.opamp("U1", 352, 192); s.flag(192, 176, "v1"); s.hres("R1", "10k", 192, 176); s.wire((272, 176), (320, 176))
    s.wire((304, 176), (304, 48)); s.hres("R2", "18k", 304, 48); s.wire((384, 48), (432, 48)); s.wire((384, 192), (432, 192)); s.wire((432, 192), (432, 48)); s.flag(432, 192, "vo")
    s.flag(192, 256, "v2"); s.hres("R3", "33k", 192, 256); s.wire((272, 256), (320, 256)); s.wire((320, 256), (320, 208)); s.wire((296, 256), (296, 272)); s.vres("R4", "39k", 296, 272); s.flag(296, 352, 0)
    s.flag(352, 160, "VCC"); s.flag(352, 224, "VEE")
    for i, (nm, v, x, fl) in enumerate((("V1", e1, 544, "v1"), ("V2", e2, 704, "v2"), ("Vcc", "15", 864, "VCC"), ("Vee", "-15", 1000, "VEE"))):
        s.vsrc(nm, v, x, 176); s.flag(x, 176, fl); s.flag(x, 256, 0)
    s.save(name, ".tran 0 3m 0 2u" if tran else ".op", 64, 400)

def summ(name, e1, e2, tran):
    s = Sch()
    s.opamp("U1", 352, 192); s.wire((320, 208), (320, 240)); s.flag(320, 240, 0)
    s.flag(160, 240, "v1"); s.hres("R1", "10k", 160, 240); s.wire((240, 240), (304, 240)); s.wire((304, 240), (304, 176))
    s.flag(160, 176, "v2"); s.hres("R2", "18k", 160, 176); s.wire((240, 176), (320, 176))
    s.wire((288, 176), (288, 48)); s.hres("R3", "33k", 288, 48); s.wire((368, 48), (432, 48)); s.wire((384, 192), (432, 192)); s.wire((432, 192), (432, 48)); s.flag(432, 192, "vo")
    s.flag(352, 160, "VCC"); s.flag(352, 224, "VEE")
    for nm, v, x, fl in (("V1", e1, 544, "v1"), ("V2", e2, 704, "v2"), ("Vcc", "15", 864, "VCC"), ("Vee", "-15", 1000, "VEE")):
        s.vsrc(nm, v, x, 176); s.flag(x, 176, fl); s.flag(x, 256, 0)
    s.save(name, ".tran 0 3m 0 2u" if tran else ".op", 64, 400)


def val(name, kind):
    """UA741 modelinin dogrulamasi: ac = acik cevrim kazanc/bant; sr = birim kazanc izleyici, 10 V adim, RL=2k, CL=100p"""
    s = Sch()
    s.opamp("U1", 272, 192)
    s.flag(272, 160, "VCC"); s.flag(272, 224, "VEE")
    s.vsrc("Vcc", "15", 448, 176); s.flag(448, 176, "VCC"); s.flag(448, 256, 0)
    s.vsrc("Vee", "-15", 528, 176); s.flag(528, 176, "VEE"); s.flag(528, 256, 0)
    if kind == "ac":
        s.wire((240, 176), (240, 144)); s.flag(240, 144, 0)
        s.vsrc("Vin", "AC 1", 128, 208); s.wire((128, 208), (240, 208)); s.flag(128, 288, 0); s.flag(128, 208, "vin")
        s.wire((304, 192), (352, 192)); s.flag(352, 192, "vo")
        s.save(name, ".ac dec 20 1 10Meg", 64, 400)
    else:
        s.vsrc("Vin", "PULSE(-5 5 5u 1n 1n 100u 200u)", 128, 208); s.wire((128, 208), (240, 208)); s.flag(128, 288, 0); s.flag(128, 208, "vin")
        s.wire((240, 176), (208, 176)); s.wire((208, 176), (208, 64)); s.wire((208, 64), (352, 64)); s.wire((352, 64), (352, 192)); s.wire((304, 192), (352, 192)); s.flag(352, 192, "vo")
        s.wire((352, 192), (352, 208)); s.vres("RL", "2k", 352, 208); s.flag(352, 288, 0)
        s.vsrc("CLs", "0", 0, 0) if False else None
        s.save(name, ".tran 0 40u 0 20n", 64, 400)

if __name__ == "__main__":
    val("t3_val_ac", "ac"); val("t3_val_sr", "sr")
    for m, n in (("voc", "t2_voc"), ("isc", "t2_isc"), ("rth", "t2_rth"), ("load", "t2_load"), ("loaddc", "t2_loaddc")):
        thev(n, m)
    sup("t2_sp_both", "12", "5"); sup("t2_sp_s2", "0", "5"); sup("t2_sp_s1", "12", "0"); sup("t2_sp_isc", "12", "5", "isc"); sup("t2_sp_rth", "0", "0", "rth")
    inv("t3_inv", "0.5"); inv("t3_inv_clip", "2"); inv("t3_inv_dc", "0", True); noninv("t3_noninv", "0.5")
    S = "SINE(0 0.5 1k)"
    for pre, f in (("t3_d", diff), ("t3_s", summ)):
        f(pre + "1", "0", "5", False); f(pre + "2", "0", S, True); f(pre + "3", "5", S, True); f(pre + "4", S, S, True)

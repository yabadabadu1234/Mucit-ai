"""Deney 5 -- BJT yükselteçleri: ortak emetör (CE) ve ortak kollektör (CC)."""
import numpy as np
from scipy.optimize import brentq
import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt

from common import *
from breadboard import Breadboard
from exp4 import QM

B, VBE, VT = BETA, VBE_ON, 0.026
VCC = 12.0
CE_P = dict(R1=120e3, R2=39e3, RC=5.6e3, RE=1.8e3, RL=15e3, CC1=22e-9, CC2=2.2e-9, CE=22e-9)
CC_P = dict(R1=22e3, R2=39e3, RE=3.3e3, RL=10e3, CC1=22e-9, CC2=2.2e-9)
F0 = 100e3


# ----------------------------------------------------------------- el hesabı
def dc_bjt(R1, R2, RC, RE, beta=B, vbe=VBE, vcc=VCC):
    vth = vcc * R2 / (R1 + R2)
    rth = R1 * R2 / (R1 + R2)
    ib = (vth - vbe) / (rth + (beta + 1) * RE)
    ic = beta * ib
    ie = (beta + 1) * ib
    vce = vcc - ic * RC - ie * RE
    gm = ic / VT
    return dict(vth=vth, rth=rth, ib=ib, ic=ic, ie=ie, vce=vce, gm=gm, rpi=beta / gm, re=VT / ie)


def ce_gain(f, ce_on, d, p=CE_P, beta=B):
    w = 2 * np.pi * f
    zc = lambda c: 1 / (1j * w * c)
    ze = p["RE"] * zc(p["CE"]) / (p["RE"] + zc(p["CE"])) if ce_on else p["RE"]
    zx = d["rpi"] + (beta + 1) * ze
    rb = p["R1"] * p["R2"] / (p["R1"] + p["R2"])
    zpar = rb * zx / (rb + zx)
    vb = zpar / (zpar + zc(p["CC1"]))
    ib = vb / zx
    zl = p["RL"] + zc(p["CC2"])
    zc_ = 1 / (1 / p["RC"] + 1 / zl)
    vc = -beta * ib * zc_
    return vc * p["RL"] / zl


def ri_complex(f, d, kind, ce_on=True, beta=B):
    """Baz düğümünden görülen direnç (CC1 hariç), kompleks."""
    w = 2 * np.pi * f
    zc = lambda c: 1 / (1j * w * c)
    if kind == "ce":
        p = CE_P
        ze = p["RE"] * zc(p["CE"]) / (p["RE"] + zc(p["CE"])) if ce_on else p["RE"]
        zx = d["rpi"] + (beta + 1) * ze
    else:
        p = CC_P
        zl = p["RL"] + zc(p["CC2"])
        zep = 1 / (1 / p["RE"] + 1 / zl)
        zx = d["rpi"] + (beta + 1) * zep
    rb = p["R1"] * p["R2"] / (p["R1"] + p["R2"])
    return rb * zx / (rb + zx)


def ri_spice(bode_run, f0, c1=22e-9):
    f = bode_run["x"]
    k = np.argmin(np.abs(f - f0))
    i = bode_run["real(i(vi))"][k] + 1j * bode_run["imag(i(vi))"][k]
    zin = 1 / (-i)
    return zin - 1 / (1j * 2 * np.pi * f[k] * c1)


def cc_gain(f, d, p=CC_P, beta=B):
    w = 2 * np.pi * f
    zc = lambda c: 1 / (1j * w * c)
    zl = p["RL"] + zc(p["CC2"])
    zep = 1 / (1 / p["RE"] + 1 / zl)
    zx = d["rpi"] + (beta + 1) * zep
    rb = p["R1"] * p["R2"] / (p["R1"] + p["R2"])
    zpar = rb * zx / (rb + zx)
    vb = zpar / (zpar + zc(p["CC1"]))
    ve = vb * (beta + 1) * zep / zx
    return ve * p["RL"] / zl


# ----------------------------------------------------------------- SPICE
def ce_net(vpk, ce_on, f=F0, ac=False):
    src = "DC 0 AC 1 SIN(0 %g %g)" % (vpk, f) if ac else "DC 0 SIN(0 %g %g)" % (vpk, f)
    return ("VCC vcc 0 DC 12\nVi in 0 %s\nCc1 in b 22n\nR1 vcc b 120k\nR2 b 0 39k\nRC vcc c 5.6k\nQ1 c b e BC238A\nRE e 0 1.8k\n%sCc2 c o 2.2n\nRL o 0 15k\n%s\n"
            % (src, "CE e 0 22n\n" if ce_on else "", QM))


def cc_net(vpk, f=F0, ac=False, r2=39e3, re=3.3e3, rl=10e3, r1=22e3, ro_test=False):
    src = "DC 0 AC 1 SIN(0 %g %g)" % (vpk, f) if ac else "DC 0 SIN(0 %g %g)" % (vpk, f)
    if ro_test:
        return ("VCC vcc 0 DC 12\nVi in 0 DC 0 AC 0\nCc1 in b 22n\nR1 vcc b %g\nR2 b 0 %g\nQ1 vcc b e BC238A\nRE e 0 %g\nItest 0 e DC 0 AC 1\n%s\n" % (r1, r2, re, QM))
    return ("VCC vcc 0 DC 12\nVi in 0 %s\nCc1 in b 22n\nR1 vcc b %g\nR2 b 0 %g\nQ1 vcc b e BC238A\nRE e 0 %g\nCc2 e o 2.2n\nRL o 0 %g\n%s\n"
            % (src, r1, r2, re, rl, QM))


def thd_of(t, v, f=F0, nper=10, nh=9):
    tend = t[-1]
    t0 = tend - nper / f
    tt = np.linspace(t0, tend, nper * 512, endpoint=False)
    vv = np.interp(tt, t, v)
    sp = np.fft.rfft(vv) / len(vv)
    mag = np.abs(sp)
    h1 = mag[nper]
    hk = [mag[nper * k] for k in range(2, nh + 1)]
    return float(np.sqrt(np.sum(np.square(hk))) / h1 * 100), 2 * float(h1)  # (THD %, temel bileşen TEPE genliği)


def tran(net, name, tstop=1e-3, tstart=0.9e-3, step=20e-9):
    r, _ = spice_run(net, ["v(in)", "v(o)"], "tran %g %g %g %g" % (step, tstop, tstart, step), name)
    return r["x"], r["v(in)"], r["v(o)"]


def ce_thd(vpk, ce_on):
    t, vi, vo = tran(ce_net(vpk, ce_on), "e5_ce_sim")
    thd, ap = thd_of(t, vo)
    return thd, ap, t, vi, vo


def cc_thd(vpk, **kw):
    t, vi, vo = tran(cc_net(vpk, **kw), "e5_cc_sim", tstop=4e-3, tstart=3.5e-3, step=50e-9)
    thd, ap = thd_of(t, vo)
    return thd, ap, t, vi, vo


def find_limit(fun, lo, hi, target=1.0, n=14):
    """THD(genlik) = target olan en büyük genliği bisection ile bul (THD monoton artan varsayımı)."""
    for _ in range(n):
        mid = np.sqrt(lo * hi)
        thd = fun(mid)
        if thd > target:
            hi = mid
        else:
            lo = mid
    return lo


# ----------------------------------------------------------------- breadboard çizimleri
def bb_found(path):
    bb = Breadboard()
    bb.transistor("Q1", 18, "d", ["C", "B", "E"], "BC238A", "npn")
    bb.resistor("RC", (14, "c"), (18, "c"), 5600, "5.6 kΩ")
    bb.resistor("R1", (15, "a"), (19, "a"), 120000, "120 kΩ", below=True)
    bb.resistor("RE", (20, "c"), (24, "c"), 1800, "1.8 kΩ")
    bb.resistor("R2", (19, "b"), (23, "b"), 39000, "39 kΩ")
    bb.resistor("RL", (13, "j"), (17, "j"), 15000, "15 kΩ")
    bb.capacitor("CC2", (12, "f"), (13, "f"), "")
    bb.capacitor("CC1", (27, "a"), (28, "a"), "")
    bb.wire((14, "c"), (15, "a"), "magenta")
    bb.wire((12, "f"), (18, "d"), "magenta")
    bb.wire((19, "a"), (27, "a"), "green")
    bb.wire((23, "b"), (24, "c"), "green")
    bb.wire((28, "a"), (30, ("top", "+")), "green")
    bb.flag((15, "b"), "E1: V_CC node (R1, RC) is not\nconnected to the + rail", dx=-3.2, dy=-2.5)
    bb.flag((24, "a"), "E2: R2/RE ground node is not\nconnected to the − rail", dx=2.5, dy=-4.0)
    bb.flag((17, "i"), "E3: RL second end floating\n(no ground)", dx=-4.0, dy=1.2)
    bb.flag((30, ("top", "+")), "E4: + (supply) rail wired to\nthe free leg of CC1", dx=-4.5, dy=-2.2)
    bb.flag((22, "e"), "E5: bypass capacitor CE\nmissing across RE", dx=4.2, dy=3.0)
    bb.label(15.5, -7.3, "Red dashed circles: wiring errors found in the given drawing (E1–E4) and the missing element (E5).", "#D00000", 8.5, True, False)
    return bb.draw(path, figsize=(11.5, 6.2)), bb


def bb_ce(path):
    bb = Breadboard()
    bb.transistor("Q1", 18, "e", ["C", "B", "E"], "BC238A", "npn")
    bb.resistor("RC", (14, "c"), (18, "c"), 5600, "RC 5.6 kΩ")
    bb.resistor("R1", (15, "a"), (19, "a"), 120000, "R1 120 kΩ", below=True)
    bb.resistor("RE", (20, "c"), (24, "c"), 1800, "RE 1.8 kΩ")
    bb.resistor("R2", (19, "b"), (23, "b"), 39000, "R2 39 kΩ")
    bb.resistor("RL", (13, "j"), (17, "j"), 15000, "RL 15 kΩ")
    bb.capacitor("CC2", (12, "f"), (13, "f"), "CC2 2.2 nF")
    bb.capacitor("CC1", (27, "a"), (28, "a"), "CC1 22 nF", down=True)
    bb.capacitor("CE", (20, "d"), (24, "d"), "CE 22 nF", color="#C0392B")
    bb.wire((14, "c"), (15, "a"), "magenta")
    bb.wire((12, "f"), (18, "d"), "magenta")
    bb.wire((19, "a"), (27, "a"), "green")
    bb.wire((23, "b"), (24, "c"), "green")
    bb.wire((15, "b"), (15, ("top", "+")), "red", 0.15)
    bb.wire((24, "b"), (24, ("top", "-")), "black", -0.1)
    bb.wire((17, "i"), (17, ("top", "-")), "black")
    bb.lead("LVCC", (27, ("top", "+")), "VCC", "red")
    bb.lead("LGND", (26, ("top", "-")), "GND", "black")
    bb.lead("LVI", (28, "b"), "vi", "blue")
    bb.lead("LGNDI", (29, ("top", "-")), "vi GND", "black")
    bb.lead("LVO", (13, "i"), "vo", "orange")
    bb.label(15.5, -7.3, "Corrections: red wire (VCC), black wires (GND), $C_E$ added (red disc), $v_i$ applied to $C_{C1}$, $v_o$ taken at $C_{C2}$/$R_L$.", "#333", 8.3, True, False)
    bb.check({
        "VCC": [("R1", 1), ("RC", 1), ("LVCC", 1)],
        "B": [("R1", 2), ("R2", 1), ("CC1", 1), ("Q1", "B")],
        "C": [("RC", 2), ("Q1", "C"), ("CC2", 1)],
        "E": [("Q1", "E"), ("RE", 1), ("CE", 1)],
        "GND": [("R2", 2), ("RE", 2), ("CE", 2), ("RL", 2), ("LGND", 1), ("LGNDI", 1)],
        "VI": [("CC1", 2), ("LVI", 1)],
        "VO": [("CC2", 2), ("RL", 1), ("LVO", 1)],
    })
    return bb.draw(path, figsize=(11.5, 6.2))


def bb_cc(path):
    bb = Breadboard()
    bb.transistor("Q1", 12, "e", ["C", "B", "E"], "BC238A", "npn")
    bb.resistor("R1", (9, "c"), (13, "c"), 22000, "R1 22 kΩ")
    bb.resistor("R2", (7, "b"), (13, "b"), 39000, "R2 39 kΩ", below=True)
    bb.resistor("RE", (14, "c"), (18, "c"), 3300, "RE 3.3 kΩ")
    bb.resistor("RL", (16, "b"), (20, "b"), 10000, "RL 10 kΩ", below=True)
    bb.capacitor("CC1", (10, "a"), (13, "a"), "CC1 22 nF", down=True)
    bb.capacitor("CC2", (14, "a"), (16, "a"), "CC2 2.2 nF", down=True)
    bb.wire((12, "d"), (12, ("top", "+")), "red", 0.25)
    bb.wire((9, "d"), (9, ("top", "+")), "red", 0.15)
    bb.wire((7, "d"), (7, ("top", "-")), "black", 0.15)
    bb.wire((18, "d"), (18, ("top", "-")), "black", 0.15)
    bb.wire((20, "c"), (20, ("top", "-")), "black", -0.1)
    bb.lead("LVCC", (24, ("top", "+")), "VCC", "red")
    bb.lead("LGND", (24, ("top", "-")), "GND", "black")
    bb.lead("LVI", (10, "b"), "vi", "blue")
    bb.lead("LGNDI", (26, ("top", "-")), "vi GND", "black")
    bb.lead("LVO", (16, "d"), "vo", "orange")
    bb.label(15.5, -7.3, "Collector wired directly to +VCC (red wire from column 12); output taken from the emitter through $C_{C2}$.", "#333", 8.3, True, False)
    bb.check({
        "VCC": [("R1", 1), ("Q1", "C"), ("LVCC", 1)],
        "B": [("R1", 2), ("R2", 2), ("CC1", 2), ("Q1", "B")],
        "E": [("Q1", "E"), ("RE", 1), ("CC2", 1)],
        "GND": [("R2", 1), ("RE", 2), ("RL", 2), ("LGND", 1), ("LGNDI", 1)],
        "VI": [("CC1", 1), ("LVI", 1)],
        "VO": [("CC2", 2), ("RL", 1), ("LVO", 1)],
    })
    return bb.draw(path, figsize=(11.5, 6.2))


# ----------------------------------------------------------------- şemalar
def schem_ce(path):
    d = schemdraw.Drawing()
    L = lambda x, y, t: d.add(elm.Label().at((x, y)).label(t))
    q = d.add(elm.BjtNpn(circle=False))
    cx, cy = q.collector
    ex, ey = q.emitter
    top, bot = 4.0, -4.2
    d += elm.Resistor().at(q.collector).up().length(2.4)
    d += elm.Line().up().length(top - cy - 2.4)
    d += elm.Line().left().tox(-2.8)
    L(-1.0, top + 0.35, "+12 V")
    L(cx + 1.2, cy + 1.3, "$R_C$ 5.6 kΩ")
    d += elm.Line().at(q.base).left().tox(-2.8)
    d += elm.Dot()
    d += elm.Resistor().at((-2.8, 0)).up().length(2.6)
    d += elm.Line().up().length(top - 2.6)
    d += elm.Resistor().at((-2.8, 0)).down().length(2.6)
    d += elm.Line().down().length(abs(bot) - 2.6)
    d += elm.Ground()
    L(-1.7, 1.6, "$R_1$ 120 kΩ")
    L(-1.7, -1.7, "$R_2$ 39 kΩ")
    d += elm.Resistor().at(q.emitter).down().length(2.4)
    d += elm.Line().down().length(abs(bot) - abs(ey) - 2.4)
    d += elm.Ground()
    L(ex - 1.0, ey - 1.5, "$R_E$ 1.8 kΩ")
    d += elm.Line().at(q.emitter).right().length(1.4)
    d += elm.Capacitor().down().length(2.4)
    d += elm.Line().down().length(abs(bot) - abs(ey) - 2.4)
    d += elm.Ground()
    L(ex + 2.7, ey - 1.5, "$C_E$ 22 nF")
    d += elm.Dot().at((cx, cy))
    d += elm.Capacitor().at((cx, cy)).right().length(2.2)
    d += elm.Dot()
    d += elm.Line().right().length(1.0).dot(open=True)
    L(cx + 1.1, cy + 0.55, "$C_{C2}$ 2.2 nF")
    L(cx + 3.9, cy, "$v_o$")
    d += elm.Resistor().at((cx + 2.2, cy)).down().length(2.6)
    d += elm.Line().down().length(abs(bot) - abs(cy) - 2.6)
    d += elm.Ground()
    L(cx + 3.6, cy - 1.5, "$R_L$ 15 kΩ")
    d += elm.Capacitor().at((-6.2, 0)).right().length(2.4)
    d += elm.Line().right().tox(-2.8)
    d += elm.Line().at((-6.2, 0)).left().length(0.4)
    d += elm.SourceSin().down().length(2.0)
    d += elm.Ground()
    L(-5.0, 0.5, "$C_{C1}$ 22 nF")
    L(-7.9, -1.6, "$v_i$")
    d.save(path, dpi=190)


def schem_cc(path):
    d = schemdraw.Drawing()
    L = lambda x, y, t: d.add(elm.Label().at((x, y)).label(t))
    q = d.add(elm.BjtNpn(circle=False))
    cx, cy = q.collector
    ex, ey = q.emitter
    top, bot = 3.6, -4.2
    d += elm.Line().at(q.collector).up().length(top - cy)
    d += elm.Line().left().tox(-2.8)
    L(-1.0, top + 0.35, "+12 V")
    d += elm.Line().at(q.base).left().tox(-2.8)
    d += elm.Dot()
    d += elm.Resistor().at((-2.8, 0)).up().length(2.4)
    d += elm.Line().up().length(top - 2.4)
    d += elm.Resistor().at((-2.8, 0)).down().length(2.6)
    d += elm.Line().down().length(abs(bot) - 2.6)
    d += elm.Ground()
    L(-1.7, 1.5, "$R_1$ 22 kΩ")
    L(-1.7, -1.7, "$R_2$ 39 kΩ")
    d += elm.Resistor().at(q.emitter).down().length(2.6)
    d += elm.Line().down().length(abs(bot) - abs(ey) - 2.6)
    d += elm.Ground()
    L(ex + 1.3, ey - 1.6, "$R_E$ 3.3 kΩ")
    d += elm.Dot().at((ex, ey))
    d += elm.Capacitor().at((ex, ey)).right().length(2.2)
    d += elm.Dot()
    d += elm.Line().right().length(1.0).dot(open=True)
    L(ex + 1.1, ey + 0.55, "$C_{C2}$ 2.2 nF")
    L(ex + 3.9, ey, "$v_o$")
    d += elm.Resistor().at((ex + 2.2, ey)).down().length(2.6)
    d += elm.Line().down().length(abs(bot) - abs(ey) - 2.6)
    d += elm.Ground()
    L(ex + 3.6, ey - 1.5, "$R_L$ 10 kΩ")
    d += elm.Capacitor().at((-6.2, 0)).right().length(2.4)
    d += elm.Line().right().tox(-2.8)
    d += elm.Line().at((-6.2, 0)).left().length(0.4)
    d += elm.SourceSin().down().length(2.0)
    d += elm.Ground()
    L(-5.0, 0.5, "$C_{C1}$ 22 nF")
    L(-7.9, -1.6, "$v_i$")
    d.save(path, dpi=190)


# ----------------------------------------------------------------- ana
def run():
    R = {}
    R["fig_bb_found"], bbf = bb_found(os.path.join(FIG, "e5_bb_found.png"))
    tt = bbf.terminals()
    R["fig_bb_ce"] = bb_ce(os.path.join(FIG, "e5_bb_ce.png"))
    R["fig_bb_cc"] = bb_cc(os.path.join(FIG, "e5_bb_cc.png"))
    schem_ce(os.path.join(FIG, "e5_ce_schem.png"))
    schem_cc(os.path.join(FIG, "e5_cc_schem.png"))
    R["fig_ce_schem"], R["fig_cc_schem"] = os.path.join(FIG, "e5_ce_schem.png"), os.path.join(FIG, "e5_cc_schem.png")

    # ---------------- CE el hesabı
    p = CE_P
    d = dc_bjt(p["R1"], p["R2"], p["RC"], p["RE"])
    RLp = p["RC"] * p["RL"] / (p["RC"] + p["RL"])
    av_ce = -d["gm"] * RLp
    av_noce = -B * RLp / (d["rpi"] + (B + 1) * p["RE"])
    rb = p["R1"] * p["R2"] / (p["R1"] + p["R2"])
    ri_ce = 1 / (1 / rb + 1 / d["rpi"])
    ri_no = 1 / (1 / rb + 1 / (d["rpi"] + (B + 1) * p["RE"]))
    # swing
    up = d["ic"] * RLp
    dn = d["vce"] - VCE_SAT
    vo_ce = 2 * min(up, dn)
    ic_dn = min(d["ic"], dn / (RLp + p["RE"]))
    vo_no = 2 * ic_dn * RLp
    R["ce"] = dict(d=d, rlp=RLp, av_ce=av_ce, av_no=av_noce, ri_ce=ri_ce, ri_no=ri_no, up=up, dn=dn, vo_ce=vo_ce, vo_no=vo_no, ic_dn=ic_dn,
                   av100=(ce_gain(F0, True, d), ce_gain(F0, False, d)))
    # CE ihtiyaç (100 kHz'te %90)
    def need(c):
        pp = dict(p); pp["CE"] = c
        return abs(ce_gain(F0, True, d, pp)) / abs(av_ce) - 0.9
    R["ce_need"] = brentq(need, 22e-9, 1e-3)
    # SPICE op
    r, _ = spice_op(ce_net(0, True), ["v(b)", "v(c)", "v(e)"], "e5_ce_op")
    R["ce_op"] = dict(vbe=r["v(b)"] - r["v(e)"], vce=r["v(c)"] - r["v(e)"], ic=(12 - r["v(c)"]) / p["RC"], ib=(12 * 0 + (12 * p["R2"] / (p["R1"] + p["R2"]) - r["v(b)"]) / rb))
    # AC ve Bode
    bode = {}
    for ce_on in (True, False):
        rr, _ = spice_run(ce_net(1e-3, ce_on, ac=True), ["mag(v(o))", "real(i(vi))", "imag(i(vi))"], "ac dec 60 10 100Meg", "e5_ce_ac_%d" % ce_on)
        bode[ce_on] = rr
    f = bode[True]["x"]
    k = np.argmin(np.abs(f - F0))
    R["ce_sp_gain100"] = (bode[True]["mag(v(o))"][k], bode[False]["mag(v(o))"][k])
    k1 = np.argmin(np.abs(f - 3e6))
    R["ce_sp_mid"] = (bode[True]["mag(v(o))"][k1], bode[False]["mag(v(o))"][k1])
    kp = int(np.argmax(bode[True]["mag(v(o))"]))
    R["ce_sp_peak"] = (float(bode[True]["mag(v(o))"][kp]), float(f[kp]))
    kn = int(np.argmax(bode[False]["mag(v(o))"]))
    R["ce_sp_peak_no"] = (float(bode[False]["mag(v(o))"][kn]), float(f[kn]))
    # SPICE Ri
    R["ri100"] = {c: (abs(ri_complex(F0, d, "ce", c)), abs(ri_spice(bode[c], F0))) for c in (True, False)}
    fh = np.logspace(1, 8, 400)
    fig, ax = plt.subplots(figsize=(8.4, 4.5))
    for ce_on, c, lab in ((True, "b", "with $C_E$"), (False, "r", "without $C_E$")):
        ax.semilogx(f, 20 * np.log10(bode[ce_on]["mag(v(o))"]), c + "-", lw=1.8, label="SPICE, " + lab)
        ax.semilogx(fh, 20 * np.log10(np.abs([ce_gain(x, ce_on, d) for x in fh])), c + "--", lw=1.0, label="phasor calc., " + lab)
    ax.axvline(F0, color="gray", ls=":")
    ax.axhline(20 * np.log10(abs(av_ce)), color="b", ls=":", lw=0.8)
    ax.text(12, 20 * np.log10(abs(av_ce)) + 0.8, "mid-band $|A_V|$ = %.0f (ideal $C_E$ short)" % abs(av_ce), color="b", fontsize=8)
    mark(ax, F0, 20 * np.log10(bode[True]["mag(v(o))"][k]), dx=10, dy=-30)
    mark(ax, F0, 20 * np.log10(bode[False]["mag(v(o))"][k]), dx=10, dy=12, color="darkgreen")
    ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("$|v_o/v_i|$ (dB)"); ax.set_xlim(10, 1e8); ax.set_ylim(-50, 50)
    ax.set_title("Common-emitter amplifier frequency response (dotted vertical: 100 kHz)")
    ax.legend(loc="lower right", fontsize=8)
    R["fig_ce_bode"] = save(fig, "e5_ce_bode")

    # ---------------- CE geçici analiz ve bozulma
    amps = np.array([0.5, 1, 2, 3, 5, 8, 12, 20, 50, 100, 300, 1000, 3000]) * 1e-3
    thd_tab = {True: [], False: []}
    for ce_on in (True, False):
        for a in amps:
            thd, a1, *_ = ce_thd(a, ce_on)
            thd_tab[ce_on].append((a, thd, a1))
    R["ce_thd_tab"] = thd_tab
    lim = {}
    for ce_on in (True, False):
        for tgt in (1.0, 5.0):
            lim[(ce_on, tgt)] = find_limit(lambda a: ce_thd(a, ce_on)[0], 0.3e-3, 8.0, tgt)
    R["ce_lim"] = lim
    # grafikler: sınır genliği, 2x sınır, kırpılma
    for ce_on, tag in ((True, "ce"), (False, "noce")):
        a_ok = lim[(ce_on, 1.0)]
        fig, ax = plt.subplots(3, 1, figsize=(8.4, 8.0), sharex=True)
        for axx, (a, ttl) in zip(ax, ((a_ok, "highest undistorted input (THD = 1%)"), (a_ok * 4 if ce_on else a_ok * 2.5, "larger input: visible distortion"),
                                       (a_ok * 40 if ce_on else a_ok * 6, "overdriven: clipping"))):
            thd, a1, t, vi, vo = ce_thd(a, ce_on)
            s = t > t[-1] - 4 / F0
            ln1, = axx.plot((t[s] - t[s][0]) * 1e6, vi[s], "b-", lw=1.3, label="$v_i$ (V)")
            axx2 = axx.twinx()
            ln2, = axx2.plot((t[s] - t[s][0]) * 1e6, vo[s] - np.mean(vo[s]), "r-", lw=1.6, label="$v_o$ (V, DC removed)")
            axx.set_ylabel("$v_i$ (V)", color="b"); axx2.set_ylabel("$v_o$ (V)", color="r")
            axx.set_title("%s: $v_i$ = %.3g mV$_{pp}$, THD = %.2f%%" % (ttl, 2 * a * 1e3, thd), fontsize=9.5)
            kmax = np.argmax(vo[s])
            mark(axx2, (t[s][kmax] - t[s][0]) * 1e6, vo[s][kmax] - np.mean(vo[s]), dx=8, dy=-12)
        ax[-1].set_xlabel("Time (µs)")
        R["fig_ce_tran_" + tag] = save(fig, "e5_ce_tran_" + tag)
    # THD-genlik grafiği
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for ce_on, c, lab in ((True, "b", "with $C_E$"), (False, "r", "without $C_E$")):
        ax.loglog([2e3 * a for a, _, _ in thd_tab[ce_on]], [max(t, 1e-3) for _, t, _ in thd_tab[ce_on]], c + "o-", ms=4, label=lab)
    ax.axhline(1, color="gray", ls="--", lw=0.9); ax.axhline(5, color="gray", ls=":", lw=0.9)
    ax.text(0.9, 1.1, "1%", fontsize=8); ax.text(0.9, 5.5, "5%", fontsize=8)
    ax.set_xlabel("input amplitude, peak-to-peak (mV)"); ax.set_ylabel("THD of $v_o$ (%)")
    ax.set_title("Distortion of the common-emitter amplifier at 100 kHz"); ax.legend()
    R["fig_ce_thd"] = save(fig, "e5_ce_thd")
    # 100 kHz'te gözlenen kazançlar
    ce_pp = {}
    for ce_on in (True, False):
        a = lim[(ce_on, 1.0)]
        thd, a1, t, vi, vo = ce_thd(a, ce_on)
        ce_pp[ce_on] = (2 * a, 2 * a1, thd)  # (giriş pp, çıkış temel pp, THD)
    R["ce_lim_pp"] = ce_pp
    # tam kırpılma genliği (SPICE): çok büyük giriş
    clip = {}
    for ce_on in (True, False):
        thd, a1, t, vi, vo = ce_thd(0.5 if ce_on else 6.0, ce_on)
        s = t > t[-1] - 5 / F0
        clip[ce_on] = (vo[s].max() - vo[s].min())
    R["ce_clip_pp"] = clip

    # ---------------- CC
    pc = CC_P
    dc = dc_bjt(pc["R1"], pc["R2"], 0.0, pc["RE"])
    REp = pc["RE"] * pc["RL"] / (pc["RE"] + pc["RL"])
    av_cc = (B + 1) * REp / (dc["rpi"] + (B + 1) * REp)
    rbc = pc["R1"] * pc["R2"] / (pc["R1"] + pc["R2"])
    ri_cc = 1 / (1 / rbc + 1 / (dc["rpi"] + (B + 1) * REp))
    ro_cc = 1 / (1 / pc["RE"] + (B + 1) / dc["rpi"])
    up_c = dc["vce"] - VCE_SAT
    dn_c = dc["ie"] * REp
    R["cc"] = dict(d=dc, rep=REp, av=av_cc, ri=ri_cc, ro=ro_cc, up=up_c, dn=dn_c, vo=2 * min(up_c, dn_c), av100=cc_gain(F0, dc),
                   icopt=VCC / (pc["RE"] + REp))
    r, _ = spice_op(cc_net(0), ["v(b)", "v(e)"], "e5_cc_op")
    R["cc_op"] = dict(vbe=r["v(b)"] - r["v(e)"], vce=12 - r["v(e)"], ie=r["v(e)"] / pc["RE"], ib=((12 * pc["R2"] / (pc["R1"] + pc["R2"])) - r["v(b)"]) / rbc)
    rr, _ = spice_run(cc_net(1e-3, ac=True), ["mag(v(o))", "real(i(vi))", "imag(i(vi))"], "ac dec 60 10 100Meg", "e5_cc_ac")
    f = rr["x"]
    k = np.argmin(np.abs(f - F0))
    R["cc_sp_gain100"] = rr["mag(v(o))"][k]
    R["ri100_cc"] = (abs(ri_complex(F0, dc, "cc")), abs(ri_spice(rr, F0)))
    # Ro (SPICE): çıkışa test akımı, giriş kaynağı kapalı
    r2_, _ = spice_run(cc_net(0, ro_test=True), ["mag(v(e))"], "ac lin 1 100k 100k", "e5_cc_ro")
    R["cc_sp_ro"] = float(r2_["mag(v(e))"][0])
    fh = np.logspace(1, 8, 300)
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ax.semilogx(f, 20 * np.log10(rr["mag(v(o))"]), "b-", lw=1.8, label="SPICE")
    ax.semilogx(fh, 20 * np.log10(np.abs([cc_gain(x, dc) for x in fh])), "b--", lw=1.0, label="phasor calc.")
    ax.axhline(0, color="gray", ls=":", lw=0.8)
    ax.set_ylim(-40, 3); ax.set_xlim(10, 1e8)
    ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("$|v_o/v_i|$ (dB)"); ax.set_title("Common-collector amplifier frequency response")
    mark(ax, F0, 20 * np.log10(rr["mag(v(o))"][k]), dx=10, dy=-25); ax.legend(loc="lower right")
    R["fig_cc_bode"] = save(fig, "e5_cc_bode")
    # CC geçici
    a_cc = 1.0
    thd, a1, t, vi, vo = cc_thd(a_cc)
    s = t > t[-1] - 4 / F0
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    ax.plot((t[s] - t[s][0]) * 1e6, vi[s], "b-", lw=1.4, label="$v_i$")
    ax.plot((t[s] - t[s][0]) * 1e6, vo[s], "r-", lw=1.6, label="$v_o$")
    kmax = np.argmax(vo[s]); mark(ax, (t[s][kmax] - t[s][0]) * 1e6, vo[s][kmax], dx=8, dy=-14)
    ax.set_xlabel("Time (µs)"); ax.set_ylabel("Voltage (V)"); ax.legend(loc="lower right")
    ax.set_title("Common-collector amplifier, $v_i$ = 1 V peak, 100 kHz (THD = %.3f%%)" % thd)
    R["fig_cc_tran"] = save(fig, "e5_cc_tran")
    R["cc_tran"] = (thd, a1, a_cc)
    # CC: büyük genlik, kırpılma
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    thd2, a12, t2, vi2, vo2 = cc_thd(8.0)
    s = t2 > t2[-1] - 4 / F0
    ax.plot((t2[s] - t2[s][0]) * 1e6, vi2[s], "b-", lw=1.2, label="$v_i$ (8 V peak)")
    ax.plot((t2[s] - t2[s][0]) * 1e6, vo2[s] - np.mean(vo2[s]), "r-", lw=1.6, label="$v_o$ (DC removed)")
    ax.set_xlabel("Time (µs)"); ax.set_ylabel("Voltage (V)"); ax.legend(loc="lower right")
    ax.set_title("Overdriven common-collector amplifier: clipping on both sides")
    R["fig_cc_clip"] = save(fig, "e5_cc_clip")
    R["cc_clip_pp"] = float(vo2[s].max() - vo2[s].min())
    R["cc_clip_levels"] = (float(vo2[s].max()), float(vo2[s].min()), float(np.mean(vo2[s])))
    # ---------------- 3.3: swing parametre taraması (R2)
    sweep = []
    for r2v in (12e3, 18e3, 27e3, 39e3, 56e3, 82e3, 150e3):
        dd = dc_bjt(pc["R1"], r2v, 0.0, pc["RE"])
        up_ = dd["vce"] - VCE_SAT
        dn_ = dd["ie"] * REp
        # SPICE: THD<=1% sınırı
        if dd["vce"] > 0.5 and dd["ie"] > 1e-5:
            lim_ = find_limit(lambda a: cc_thd(a, r2=r2v)[0], 0.01, 20.0, 1.0, n=12)
            thd_, a1_, *_ = cc_thd(lim_, r2=r2v)
            sp_sw = 2 * a1_
        else:
            sp_sw = float("nan")
        # SPICE op
        rr_, _ = spice_op(cc_net(0, r2=r2v), ["v(e)"], "e5_cc_op_%d" % r2v)
        sweep.append((r2v, dd["ie"], dd["vce"], up_, dn_, 2 * max(min(up_, dn_), 0), sp_sw, 12 - rr_["v(e)"], rr_["v(e)"] / pc["RE"]))
    R["sweep"] = sweep
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.3))
    xs = [s[1] * 1e3 for s in sweep]
    ax[0].plot(xs, [s[3] for s in sweep], "b^-", label="upper limit: $V_{CEQ}-V_{CE(sat)}$ (saturation)")
    ax[0].plot(xs, [s[4] for s in sweep], "rv-", label="lower limit: $I_{EQ}(R_E\\parallel R_L)$ (cut-off)")
    ax[0].plot(xs, [min(s[3], s[4]) for s in sweep], "k--", lw=1.2, label="available peak amplitude (min)")
    ax[0].axvline(R["cc"]["icopt"] * 1e3, color="green", ls=":", label="optimum $I_{CQ}$ = %.2f mA" % (R["cc"]["icopt"] * 1e3))
    ax[0].set_xlabel("$I_{EQ}$ (mA) [by changing $R_2$]"); ax[0].set_ylabel("Peak output amplitude limit (V)")
    ax[0].set_title("Swing limits of the common-collector amplifier"); ax[0].legend(fontsize=7.5)
    ax[1].plot([s[0] / 1e3 for s in sweep], [s[5] for s in sweep], "ko-", label="load-line prediction")
    ax[1].plot([s[0] / 1e3 for s in sweep], [s[6] for s in sweep], "rs--", label="SPICE (THD ≤ 1%)")
    ax[1].set_xscale("log"); ax[1].set_xlabel("$R_2$ (k$\\Omega$)"); ax[1].set_ylabel("Max. undistorted $v_{o,pp}$ (V)")
    ax[1].set_title("Output swing versus bias resistor $R_2$"); ax[1].legend(fontsize=8)
    R["fig_sweep"] = save(fig, "e5_sweep")
    # RL taraması
    sw2 = []
    for rlv in (1e3, 2.2e3, 4.7e3, 10e3, 22e3, 47e3):
        REp_ = pc["RE"] * rlv / (pc["RE"] + rlv)
        dd = dc_bjt(pc["R1"], pc["R2"], 0.0, pc["RE"])
        up_ = dd["vce"] - VCE_SAT; dn_ = dd["ie"] * REp_
        lim_ = find_limit(lambda a: cc_thd(a, rl=rlv)[0], 0.01, 20.0, 1.0, n=12)
        thd_, a1_, *_ = cc_thd(lim_, rl=rlv)
        sw2.append((rlv, up_, dn_, 2 * min(up_, dn_), 2 * a1_))
    R["sweep_rl"] = sw2
    return R


if __name__ == "__main__":
    R = run()
    ce = R["ce"]
    print("CE d", {k: float("%.5g" % v) for k, v in ce["d"].items()})
    print("av_ce", ce["av_ce"], "av_no", ce["av_no"], "ri", ce["ri_ce"], ce["ri_no"], "up/dn", ce["up"], ce["dn"], "vo_pp", ce["vo_ce"], ce["vo_no"])
    print("av100", [abs(x) for x in ce["av100"]], "sp100", R["ce_sp_gain100"], "mid", R["ce_sp_mid"], "need", R["ce_need"])
    print("op", R["ce_op"], "ri100", R["ri100"])
    print("lim", R["ce_lim"], R["ce_lim_pp"], R["ce_clip_pp"])
    for k in (True, False):
        print(k, [("%.3g" % (a * 1e3), "%.3g" % t) for a, t, _ in R["ce_thd_tab"][k]])
    cc = R["cc"]
    print("CC d", {k: float("%.5g" % v) for k, v in cc["d"].items()})
    print("av", cc["av"], abs(cc["av100"]), R["cc_sp_gain100"], "ri", cc["ri"], R["ri100_cc"], "ro", cc["ro"], R["cc_sp_ro"], "vo", cc["vo"], cc["up"], cc["dn"], cc["icopt"])
    print("op", R["cc_op"], R["cc_tran"], R["cc_clip_pp"], R["cc_clip_levels"])
    for s in R["sweep"]:
        print(["%.4g" % x for x in s])
    for s in R["sweep_rl"]:
        print(["%.4g" % x for x in s])

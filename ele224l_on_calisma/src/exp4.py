"""Deney 4 -- BJT devreleri (BC238A)."""
import numpy as np
import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt

from common import *
from breadboard import Breadboard

IS_Q = 2e-3 / np.exp(0.62 / 0.025865)
QM = ".model BC238A NPN(IS=%.4e BF=170 BR=1 RB=30 RC=1 CJE=8p CJC=3.5p TF=0.5n)" % IS_Q
B, VBE = BETA, VBE_ON
VCC_LIST = [0, 0.2, 0.5, 1, 2, 4, 6, 8, 10, 15, 20]
VBB_LIST = [1, 2, 5]
RB1, RC1, RE1 = 150e3, 2.2e3, 1e3


def hand1(vbb, vcc, beta=B, vbe=VBE, rb=RB1, rc=RC1, re=RE1, vcesat=VCE_SAT):
    """Devre 1 (RE'li): piecewise model. Dönen: (VCE, IC, IB, bölge)"""
    if vbb <= vbe:
        return vcc, 0.0, 0.0, "cut-off"
    ib = (vbb - vbe) / (rb + (beta + 1) * re)
    ic = beta * ib
    vce = vcc - ic * rc - (ic + ib) * re
    if vce >= vcesat:
        return vce, ic, ib, "active"
    # doyma: iki bilinmeyenli doğrusal sistem (IB, IC)
    # (rb+re) IB + re IC = vbb - vbe ; re IB + (rc+re) IC = vcc - vcesat
    A = np.array([[rb + re, re], [re, rc + re]])
    rhs = np.array([vbb - vbe, vcc - vcesat])
    ib2, ic2 = np.linalg.solve(A, rhs)
    if ic2 <= 0:
        ic2 = 0.0
        return vcc - ib * 0 if False else vcc, 0.0, ib, "sat (I_C~0)"
    return vcesat, ic2, ib2, "saturation"


def spice1(vbb, vcc, rb=RB1, rc=RC1, re=RE1, name="e4_t1"):
    net = "Vbb vbb 0 DC %g\nVcc vcc 0 DC %g\nRB vbb b %g\nRC vcc c %g\nRE e 0 %g\nQ1 c b e BC238A\n%s\n" % (vbb, vcc, rb, rc, re, QM)
    r, _ = spice_op(net, ["v(c)", "v(b)", "v(e)"], name)
    return r["v(c)"] - r["v(e)"], (vcc - r["v(c)"]) / rc, r["v(b)"] - r["v(e)"]


def schem_bjt(path, circuit):
    d = schemdraw.Drawing()
    L = lambda x, y, t: d.add(elm.Label().at((x, y)).label(t))
    q = d.add(elm.BjtNpn(circle=False))
    cx, cy = q.collector
    ex, ey = q.emitter
    bx, by = q.base
    d += elm.Resistor().at(q.collector).up().length(2.2)
    d += elm.Line().up().length(0.6).dot(open=True)
    L(cx + 0.9, cy + 3.2, "$V_{CC}$")
    if circuit == 1:
        d += elm.Resistor().at(q.emitter).down().length(2.2)
        d += elm.Ground()
        L(ex + 1.6, ey - 1.1, "$R_E$ 1 kΩ")
        L(cx + 1.7, cy + 1.3, "$R_C$ 2.2 kΩ")
        d += elm.Resistor().at(q.base).left().length(2.4)
        d += elm.Line().left().length(0.4).dot(open=True)
        L(bx - 3.6, by, "$V_{BB}$")
        L(bx - 1.5, by + 0.45, "$R_B$ 150 kΩ")
        L(bx + 0.25, by - 0.65, "$I_B$")
    else:
        d += elm.Resistor().at(q.emitter).down().length(2.2)
        d += elm.Ground()
        L(ex + 1.6, ey - 1.1, "$R_E$ 1 kΩ")
        L(cx + 1.7, cy + 1.3, "$R_C$ 1.2 kΩ")
        d += elm.Resistor().at(q.base).left().length(2.4)
        d += elm.Line().left().length(0.4).dot(open=True)
        L(bx - 3.6, by, "$V_{BB}$")
        L(bx - 1.5, by + 0.45, "$R_B$ 22 kΩ")
    d.save(path, dpi=190)


def schem_bjt_nore(path):
    d = schemdraw.Drawing()
    L = lambda x, y, t: d.add(elm.Label().at((x, y)).label(t))
    q = d.add(elm.BjtNpn(circle=False))
    cx, cy = q.collector
    ex, ey = q.emitter
    bx, by = q.base
    d += elm.Resistor().at(q.collector).up().length(2.2)
    d += elm.Line().up().length(0.6).dot(open=True)
    L(cx + 0.9, cy + 3.2, "$V_{CC}$ = 12 V")
    L(cx + 1.7, cy + 1.3, "$R_C$ 2.2 kΩ")
    d += elm.Line().at(q.emitter).down().length(0.8)
    d += elm.Ground()
    d += elm.Resistor().at(q.base).left().length(2.4)
    d += elm.Line().left().length(0.4).dot(open=True)
    L(bx - 3.9, by, "$V_{BB}$ = 5 V")
    L(bx - 1.5, by + 0.45, "$R_B$ 150 kΩ")
    d.save(path, dpi=190)


def run():
    R = {}
    # ------------------------------------------------ Breadboard (devre 1)
    bb = Breadboard()
    bb.transistor("Q1", 10, "e", ["C", "B", "E"], "BC238A", "npn")
    bb.resistor("RC", (10, "d"), (6, "d"), 2200, "RC 2.2 kΩ")
    bb.resistor("RB", (3, "b"), (11, "b"), 150000, "RB 150 kΩ")
    bb.resistor("RE", (12, "d"), (16, "d"), 1000, "RE 1 kΩ")
    bb.wire((6, "a"), (6, ("bot", "+")), "red")
    bb.wire((16, "a"), (16, ("bot", "-")), "black")
    bb.lead("LVBB", (3, "a"), "VBB", "orange")
    bb.lead("LVCC", (25, ("bot", "+")), "VCC", "red")
    bb.lead("LGND", (25, ("bot", "-")), "GND", "black")
    bb.label(16, -6.6, "Orange lead: $V_{BB}$ (+) from a second supply channel; its (−) terminal and that of $V_{CC}$ go to the GND rail.", "#B35900", 8.3, True, False)
    bb.label(16, -7.3, "Red wire: +$V_{CC}$ rail to the free end of $R_C$;  black wire: GND rail to the free end of $R_E$.", "#333333", 8.3, True, False)
    bb.check({"VBB": [("RB", 1), ("LVBB", 1)], "B": [("RB", 2), ("Q1", "B")], "C": [("RC", 1), ("Q1", "C")],
              "VCC": [("RC", 2), ("LVCC", 1)], "E": [("Q1", "E"), ("RE", 1)], "GND": [("RE", 2), ("LGND", 1)]})
    R["fig_bb"] = bb.draw(os.path.join(FIG, "e4_breadboard.png"), figsize=(11, 5.9))
    schem_bjt(os.path.join(FIG, "e4_schem1.png"), 1)
    schem_bjt(os.path.join(FIG, "e4_schem3.png"), 2)
    schem_bjt_nore(os.path.join(FIG, "e4_schem2.png"))
    R["fig_s1"], R["fig_s2"], R["fig_s3"] = [os.path.join(FIG, "e4_schem%d.png" % i) for i in (1, 2, 3)]

    # ------------------------------------------------ Tablo 1
    th, sp = {}, {}
    for vbb in VBB_LIST:
        for vcc in VCC_LIST:
            th[(vbb, vcc)] = hand1(vbb, vcc)
            sp[(vbb, vcc)] = spice1(vbb, vcc, name="e4_t1_%g_%g" % (vbb, vcc))
    R["t1_th"], R["t1_sp"] = th, sp
    # IC-VCE grafiği
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.3))
    cols = {1: "tab:blue", 2: "tab:green", 5: "tab:red"}
    for vbb in VBB_LIST:
        xs = [th[(vbb, v)][0] for v in VCC_LIST]
        ys = [th[(vbb, v)][1] * 1e3 for v in VCC_LIST]
        ax[0].plot(xs, ys, "o-", color=cols[vbb], ms=4, label="calc., $V_{BB}$ = %g V" % vbb)
        xs2 = [sp[(vbb, v)][0] for v in VCC_LIST]
        ys2 = [sp[(vbb, v)][1] * 1e3 for v in VCC_LIST]
        ax[0].plot(xs2, ys2, "x--", color=cols[vbb], ms=6, mew=1.6, alpha=0.8, label="SPICE, $V_{BB}$ = %g V" % vbb)
    ax[0].set_xlabel("$V_{CE}$ (V)"); ax[0].set_ylabel("$I_C$ (mA)")
    ax[0].set_title("$I_C$–$V_{CE}$ points of Table 1 (circuit 1)")
    ax[0].legend(fontsize=7, ncol=2)
    for vbb in VBB_LIST:
        ax[1].plot([th[(vbb, v)][0] for v in VCC_LIST], [th[(vbb, v)][1] * 1e3 for v in VCC_LIST], "o-", color=cols[vbb], ms=4)
        ax[1].plot([sp[(vbb, v)][0] for v in VCC_LIST], [sp[(vbb, v)][1] * 1e3 for v in VCC_LIST], "x--", color=cols[vbb], ms=6, mew=1.6)
    ax[1].set_xlim(0, 1.6); ax[1].set_ylim(0, 3.2)
    ax[1].set_xlabel("$V_{CE}$ (V)"); ax[1].set_ylabel("$I_C$ (mA)"); ax[1].set_title("Zoom on the saturation knee")
    R["fig_t1"] = save(fig, "e4_t1")
    # ------------------------------------------------ 3.2 ve 3.3
    def solve(vbb, vcc, rb, rc, re, beta=B):
        if re == 0:
            ib = (vbb - VBE) / rb
            ic = beta * ib
            return VBE, ib, ic, vcc - ic * rc
        ib = (vbb - VBE) / (rb + (beta + 1) * re)
        ic = beta * ib
        return VBE, ib, ic, vcc - ic * rc - (ic + ib) * re
    R["c1"] = solve(5, 12, 150e3, 2.2e3, 0)
    R["c2"] = solve(5, 12, 22e3, 1.2e3, 1e3)
    net1 = "Vbb vbb 0 DC 5\nVcc vcc 0 DC 12\nRB vbb b 150k\nRC vcc c 2.2k\nQ1 c b 0 BC238A\n%s\n" % QM
    r, _ = spice_op(net1, ["v(c)", "v(b)"], "e4_c1")
    R["c1_sp"] = (r["v(b)"], (5 - r["v(b)"]) / 150e3, (12 - r["v(c)"]) / 2.2e3, r["v(c)"])
    net2 = "Vbb vbb 0 DC 5\nVcc vcc 0 DC 12\nRB vbb b 22k\nRC vcc c 1.2k\nRE e 0 1k\nQ1 c b e BC238A\n%s\n" % QM
    r, _ = spice_op(net2, ["v(c)", "v(b)", "v(e)"], "e4_c2")
    R["c2_sp"] = (r["v(b)"] - r["v(e)"], (5 - r["v(b)"]) / 22e3, (12 - r["v(c)"]) / 1.2e3, r["v(c)"] - r["v(e)"])
    # beta duyarlılığı
    bs = [120, 170, 220]
    sens = []
    for b in bs:
        v1 = solve(5, 12, 150e3, 2.2e3, 0, b)
        v1c = v1[3] if v1[3] >= 0.2 else None
        # doymaya girerse
        ic1 = v1[2]
        if v1[3] < 0.2:
            ic1 = (12 - 0.2) / 2.2e3
            vce1 = 0.2
        else:
            vce1 = v1[3]
        v2 = solve(5, 12, 22e3, 1.2e3, 1e3, b)
        sens.append((b, ic1, vce1, v2[2], v2[3]))
    R["sens"] = sens
    # yük doğruları
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.2))
    vce = np.linspace(0, 12, 100)
    ax[0].plot(vce, (12 - vce) / 2.2e3 * 1e3, "k-", lw=1.4, label="DC load line, $R_C$ = 2.2 k$\\Omega$")
    for b, c in zip(bs, ("tab:green", "tab:blue", "tab:red")):
        ic1 = solve(5, 12, 150e3, 2.2e3, 0, b)[2]
        ax[0].plot([0, 12], [ic1 * 1e3] * 2, color=c, ls=":", lw=0.8)
        vv = max(12 - ic1 * 2.2e3, 0.2)
        icc = min(ic1, (12 - 0.2) / 2.2e3)
        ax[0].plot([vv], [icc * 1e3], "o", color=c, label="$\\beta$ = %d: $I_C$=%.2f mA, $V_{CE}$=%.2f V" % (b, icc * 1e3, vv))
    ax[0].set_xlabel("$V_{CE}$ (V)"); ax[0].set_ylabel("$I_C$ (mA)"); ax[0].set_title("Circuit 1 (no $R_E$): Q moves with $\\beta$"); ax[0].legend(fontsize=7.5)
    ax[0].set_ylim(0, 8)
    ax[1].plot(vce, (12 - vce) / 2.2e3 * 1e3, "k-", lw=1.4, label="DC load line, $R_C+R_E$ = 2.2 k$\\Omega$")
    for b, c in zip(bs, ("tab:green", "tab:blue", "tab:red")):
        v2 = solve(5, 12, 22e3, 1.2e3, 1e3, b)
        ax[1].plot([v2[3]], [v2[2] * 1e3], "o", color=c, label="$\\beta$ = %d: $I_C$=%.2f mA, $V_{CE}$=%.2f V" % (b, v2[2] * 1e3, v2[3]))
        ax[1].plot([0, 12], [v2[2] * 1e3] * 2, color=c, ls=":", lw=0.8)
    ax[1].set_xlabel("$V_{CE}$ (V)"); ax[1].set_ylabel("$I_C$ (mA)")
    ax[1].set_title("Circuit 2 (with $R_E$): Q is stable"); ax[1].legend(fontsize=7.5)
    ax[1].set_ylim(0, 8); ax[1].set_xlim(-0.5, 12.5)
    R["fig_load"] = save(fig, "e4_load")
    # ------------------------------------------------ hata senaryoları (devre 2)
    def scen(name, **kw):
        p = dict(vbb=5.0, vcc=12.0, rb=22e3, rc=1.2e3, re=1e3, ce_short=False, rb_open=False, qrev=False, rc_open=False, re_open=False)
        p.update(kw)
        lines = ["Vbb vbb 0 DC %g" % p["vbb"], "Vcc vcc 0 DC %g" % p["vcc"],
                 "RB vbb b %g" % (1e12 if p["rb_open"] else p["rb"]),
                 "RC vcc c %g" % (1e12 if p["rc_open"] else p["rc"]),
                 "RE e 0 %g" % (1e12 if p["re_open"] else p["re"])]
        lines.append("Q1 e b c BC238A" if p["qrev"] else "Q1 c b e BC238A")
        if p["ce_short"]:
            lines.append("Rshort c e 0.01")
        lines.append(QM)
        r, _ = spice_op("\n".join(lines) + "\n", ["v(c)", "v(b)", "v(e)"], "e4_sc_%s" % name)
        vce = r["v(c)"] - r["v(e)"]
        vbe = r["v(b)"] - r["v(e)"]
        ic = (p["vcc"] - r["v(c)"]) / (1e12 if p["rc_open"] else p["rc"])
        return (vce, vbe, ic)
    S = {}
    S["ok"] = scen("ok")
    S["vbb0"] = scen("vbb0", vbb=0.0)
    S["rbopen"] = scen("rbopen", rb_open=True)
    S["rcopen"] = scen("rcopen", rc_open=True)
    S["reopen"] = scen("reopen", re_open=True)
    S["qrev"] = scen("qrev", qrev=True)
    S["vcc0"] = scen("vcc0", vcc=0.0)
    S["reshort"] = scen("reshort", re=1e-3)
    S["rcbig"] = scen("rcbig", rc=12e3)
    S["ceshort"] = scen("ceshort", ce_short=True)
    S["rbsmall"] = scen("rbsmall", rb=220.0, re=1e-3)
    R["scen"] = S
    return R


if __name__ == "__main__":
    R = run()
    for vbb in VBB_LIST:
        print("VBB", vbb)
        for vcc in VCC_LIST:
            a, b = R["t1_th"][(vbb, vcc)], R["t1_sp"][(vbb, vcc)]
            print("  VCC=%5.1f  th VCE=%7.4f IC=%8.5f mA %-11s | sp VCE=%7.4f IC=%8.5f mA" % (vcc, a[0], a[1] * 1e3, a[3], b[0], b[1] * 1e3))
    print(R["c1"], R["c1_sp"]); print(R["c2"], R["c2_sp"]); print(R["sens"])
    for k, v in R["scen"].items():
        print(k, ["%.4g" % x for x in v])

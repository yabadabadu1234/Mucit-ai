"""Deney 2 -- MOSFET devreleri."""
import numpy as np
from scipy.optimize import brentq
import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from common import *
from breadboard import Breadboard

VDD = 6.0
# LTspice modelinden ngspice'a taşınan parametreler (RG, RB, Rds, Tt ngspice düzey-1'de yok)
NM = ".model BS170 NMOS (VTO=2.1 RS=1.572 RD=1.436 KP=.1233 IS=5p)"
PM = ".model BS250 PMOS (VTO=-1.0 KP=150u LAMBDA=0.02 RD=1 RS=1 IS=20n)"
KPN, VTON, LAMN = 0.1233, 2.1, 0.0
KPP, VTOP, LAMP = 150e-6, -1.0, 0.02


def id_n(vgs, vds):
    if vgs <= VTON or vds <= 0:
        return 0.0
    if vds < vgs - VTON:
        return KPN * ((vgs - VTON) * vds - vds ** 2 / 2) * (1 + LAMN * vds)
    return KPN / 2 * (vgs - VTON) ** 2 * (1 + LAMN * vds)


def id_p(vsg, vsd):
    vt = -VTOP
    if vsg <= vt or vsd <= 0:
        return 0.0
    if vsd < vsg - vt:
        return KPP * ((vsg - vt) * vsd - vsd ** 2 / 2) * (1 + LAMP * vsd)
    return KPP / 2 * (vsg - vt) ** 2 * (1 + LAMP * vsd)


def vtc_point(vin):
    f = lambda vo: id_n(vin, vo) - id_p(VDD - vin, VDD - vo)
    if abs(f(VDD)) < 1e-15 and id_n(vin, VDD) == 0:
        return VDD
    vo = brentq(f, 0.0, VDD, xtol=1e-12)
    return vo


def regions(vin, vo):
    n = "cut-off" if vin <= VTON else ("saturation" if vo >= vin - VTON else "triode")
    vsg, vsd = VDD - vin, VDD - vo
    p = "cut-off" if vsg <= -VTOP else ("saturation" if vsd >= vsg + VTOP else "triode")
    return n, p


# ------------------------------------------------------------------ BS170 (föy Kn=72 mA/V^2, ID=(Kn/2)(VGS-VTH)^2)
VTH = VTH_N
KNa = KN  # 72 mA/V^2 -> 0.072 A/V^2


def vgs_for_id(i_a):
    return VTH + np.sqrt(2 * i_a / KNa)


def id_for_vgs(v):
    return 0.0 if v <= VTH else KNa / 2 * (v - VTH) ** 2


def bs_netlist(v1):
    return ("V2 d 0 DC 5\nV1 n1 0 DC %.9g\nRG1 n1 g 33k\nRG2 g 0 120k\nM1 d g 0 0 BS170 W=100u L=100u\n%s\n" % (v1, NM))


def run():
    R = {}
    # ----------------- Breadboard (CMOS evirici)
    bb = Breadboard()
    bb.transistor("M2", 6, "e", ["S", "G", "D"], "BS250 (PMOS)", "pmos")
    bb.transistor("M1", 16, "e", ["D", "G", "S"], "BS170 (NMOS)", "nmos")
    bb.wire((6, "a"), (6, ("bot", "+")), "red")
    bb.wire((18, "a"), (18, ("bot", "-")), "black")
    bb.wire((7, "d"), (17, "d"), "blue", 0.45)
    bb.wire((8, "c"), (16, "c"), "orange", -0.45)
    bb.lead("LVDD", (27, ("bot", "+")), "VDD", "red")
    bb.lead("LGND", (27, ("bot", "-")), "GND", "black")
    bb.lead("LVIN", (7, "a"), "VIN", "blue")
    bb.lead("LVOUT", (8, "b"), "VOUT", "orange")
    bb.label(16, -6.6, "Blue wire: gates tied together = $V_{IN}$", "#1565C0", 8.5, True, False)
    bb.label(16, -7.3, "Orange wire: drains tied together = $V_{OUT}$", "#EF6C00", 8.5, True, False)
    bb.label(16, -8.0, "Red / black leads: +6 V and GND", "#333333", 8.5, True, False)
    bb.check({
        "VDD": [("M2", "S"), ("LVDD", 1)], "GND": [("M1", "S"), ("LGND", 1)],
        "VIN": [("M1", "G"), ("M2", "G"), ("LVIN", 1)], "VOUT": [("M1", "D"), ("M2", "D"), ("LVOUT", 1)]})
    R["fig_bb"] = bb.draw(os.path.join(FIG, "e2_breadboard.png"), figsize=(11, 5.9))

    # ----------------- CMOS evirici şeması
    d = schemdraw.Drawing()
    pm = d.add(elm.PFet(bulk=False).reverse().at((0, 0)))
    nm = d.add(elm.NFet(bulk=False).reverse().at((0, -1.5)))
    d += elm.Line().at(pm.source).up().length(0.8)
    d += elm.Label().label("$V_{DD}$", loc="top")
    d += elm.Line().at(nm.source).down().length(0.5)
    d += elm.Ground()
    gx = pm.gate[0] - 0.7
    d += elm.Line().at(pm.gate).tox(gx)
    d += elm.Line().at(nm.gate).tox(gx)
    d += elm.Line().at((gx, pm.gate[1])).toy(nm.gate[1])
    d += elm.Dot().at((gx, (pm.gate[1] + nm.gate[1]) / 2))
    d += elm.Line().left().length(1.0).dot(open=True)
    d += elm.Label().label("$V_{IN}$", loc="left")
    d += elm.Line().at(pm.drain).right().length(1.5).dot(open=True)
    d += elm.Label().label("$V_{OUT}$", loc="right")
    d += elm.Label().at((pm.source[0] + 1.6, pm.source[1] - 0.4)).label("M2: BS250 (PMOS)")
    d += elm.Label().at((nm.source[0] + 1.6, nm.source[1] + 0.4)).label("M1: BS170 (NMOS)")
    d.save(os.path.join(FIG, "e2_inv_schem.png"), dpi=200)
    R["fig_inv_schem"] = os.path.join(FIG, "e2_inv_schem.png")

    # ----------------- CMOS evirici SPICE
    inv = ("Vdd vdd 0 DC 6\nVin in 0 SIN(3 3 1k)\nM1 out in 0 0 BS170 W=100u L=100u\nM2 out in vdd vdd BS250 W=100u L=100u\n%s\n%s\n" % (NM, PM))
    r, _ = spice_run(inv, ["v(in)", "v(out)", "i(vdd)"], "tran 2u 3m", "e2_inv_tran")
    t, vin, vout, idd = r["x"], r["v(in)"], r["v(out)"], -r["i(vdd)"]
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    ax.plot(t * 1e3, vin, "b-", lw=1.4, label="$V_{IN}$")
    ax.plot(t * 1e3, vout, "r-", lw=1.6, label="$V_{OUT}$")
    ax.set_xlabel("Time (ms)"); ax.set_ylabel("Voltage (V)")
    ax.set_title("CMOS inverter, BS170/BS250, $V_{DD}$ = 6 V, $V_{IN}$ = 3 V + 3 V sin(2π·1 kHz·t)")
    k = np.argmin(np.abs(t - 0.5e-3))
    mark(ax, t[k] * 1e3, vin[k], dx=6, dy=2)
    k2 = np.argmin(np.abs(t - 0.75e-3))
    mark(ax, t[k2] * 1e3, vout[k2], dx=6, dy=10)
    ax.legend(loc="center right")
    R["fig_tran"] = save(fig, "e2_inv_tran")
    R["cur_tran"] = [(t[k], vin[k], vout[k]), (t[k2], vin[k2], vout[k2])]
    R["tran_vout_range"] = (float(vout.min()), float(vout.max()))

    # DC süpürme (VTC ve ID)
    r, _ = spice_run(inv, ["v(out)", "i(vdd)"], "dc Vin 0 6 0.005", "e2_inv_dc")
    vin_dc, vo_dc, i_dc = r["x"], r["v(out)"], -r["i(vdd)"]
    vo_hand = np.array([vtc_point(v) for v in vin_dc])
    i_hand = np.array([id_n(v, vo) for v, vo in zip(vin_dc, vo_hand)])
    dd = vo_dc - vin_dc
    kc = np.where((dd[:-1] > 0) & (dd[1:] <= 0))[0][0]
    fr = dd[kc] / (dd[kc] - dd[kc + 1])
    vm_sp = vin_dc[kc] + fr * (vin_dc[kc + 1] - vin_dc[kc])
    kvm = kc
    # eşik: analitik (VOUT = VIN)
    vm_hand = brentq(lambda v: vtc_point(v) - v, 0.5, 5.5, xtol=1e-12)
    R["vm"] = (vm_sp, vm_sp, vm_hand)
    kpk = np.argmax(i_dc)
    R["ipk"] = (vin_dc[kpk], i_dc[kpk], float(i_hand.max()), float(vin_dc[np.argmax(i_hand)]))
    # VTC
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.plot(vin_dc, vo_dc, "b-", lw=1.8, label="SPICE")
    ax.plot(vin_dc, vo_hand, "g--", lw=1.2, label="Hand model (level-1 equations)")
    ax.plot([0, 6], [0, 6], "k:", lw=0.8)
    ax.set_xlabel("$V_{IN}$ (V)"); ax.set_ylabel("$V_{OUT}$ (V)")
    ax.set_title("Voltage transfer characteristic")
    mark(ax, vm_sp, vm_sp, "$V_M$=(%.3f V, %.3f V)" % (vm_sp, vm_sp), dx=20, dy=15)
    ax.axvline(VTON, color="gray", ls=":", lw=1); ax.text(VTON + 0.05, 0.3, "$V_{TN}$=2.1 V", fontsize=8, color="gray")
    ax.axvline(VDD + VTOP, color="gray", ls=":", lw=1); ax.text(VDD + VTOP - 1.5, 5.4, "$V_{DD}$−|$V_{TP}$|=5 V", fontsize=8, color="gray")
    ax.legend(loc="lower left")
    R["fig_vtc"] = save(fig, "e2_inv_vtc")
    # ID–VIN
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.plot(vin_dc, i_dc * 1e3, "b-", lw=1.8, label="SPICE")
    ax.plot(vin_dc, i_hand * 1e3, "g--", lw=1.2, label="Hand model")
    ax.set_xlabel("$V_{IN}$ (V)"); ax.set_ylabel("$I_D$ (mA)")
    ax.set_title("Supply (drain) current versus $V_{IN}$")
    mark(ax, vin_dc[kpk], i_dc[kpk] * 1e3, dx=10, dy=-5)
    ax.legend(loc="upper right")
    R["fig_idv"] = save(fig, "e2_inv_id")
    # bölge tablosu
    pts = [0, 1, 2, 2.1, 2.15, 2.2, 2.3, 2.5, 3, 4, 5, 5.5, 6]
    tab = []
    for v in pts:
        vo = vtc_point(v)
        n, p = regions(v, vo)
        kk = np.argmin(np.abs(vin_dc - v))
        tab.append((v, vo, vo_dc[kk], id_n(v, vo), i_dc[kk], n, p))
    R["inv_tab"] = tab
    # geçiş bölgesi sınırları (el modeli): NMOS sat->tri, PMOS tri->sat
    vlist = np.linspace(2.0, 5.2, 3201)
    nb = [regions(v, vtc_point(v)) for v in vlist]
    def first(cond):
        for v, (a, b) in zip(vlist, nb):
            if cond(a, b):
                return v
    R["b_nmos_on"] = first(lambda a, b: a != "cut-off")
    R["b_pmos_sat"] = first(lambda a, b: b == "saturation")
    R["b_nmos_tri"] = first(lambda a, b: a == "triode")
    R["b_pmos_off"] = first(lambda a, b: b == "cut-off")

    # ----------------- BS170 CS-benzeri kutuplama devresi
    ids = [0, 1e-3, 10e-3, 50e-3, 100e-3]
    th_cols = []
    for i in ids:
        vgs = 0.0 if i == 0 else vgs_for_id(i)
        th_cols.append(("ID", i, vgs, 5.0, vgs * (33e3 + 120e3) / 120e3))
    for v in (3, 4, 5):
        i = id_for_vgs(v)
        th_cols.append(("VGS", i, float(v), 5.0, v * 153 / 120))
    R["bs_th"] = th_cols
    # SPICE: V1 süpür, VGS-ID eğrisi
    net = bs_netlist(0)
    r, _ = spice_run(net, ["v(g)", "i(v2)"], "dc V1 0 12.75 0.005", "e2_bs_dc")
    vg_sp, id_sp = r["v(g)"], -r["i(v2)"]
    R["bs_sweep"] = (vg_sp, id_sp)
    # ID hedefi için VGS (interp), VGS hedefi için ID
    sp_cols = []
    for (kind, i, vgs, vds, v1) in th_cols:
        if kind == "ID":
            vg_need = 0.0 if i == 0 else float(np.interp(i, id_sp, vg_sp))
            sp_cols.append(("ID", i, vg_need, float(np.interp(vg_need, vg_sp, id_sp)) if i else 0.0))
        else:
            sp_cols.append(("VGS", float(np.interp(vgs, vg_sp, id_sp)), vgs, 0))
    R["bs_sp"] = sp_cols
    # pinch-off (SPICE, seri direnç dahil iç gerilimler)
    rd, rs = 1.436, 1.572
    vds_int = 5 - id_sp * (rd + rs)
    vgs_int = vg_sp - id_sp * rs
    g = vds_int - (vgs_int - VTON)
    kk = np.where((g[:-1] > 0) & (g[1:] <= 0))[0][0]
    f = g[kk] / (g[kk] - g[kk + 1])
    vg_po = vg_sp[kk] + f * (vg_sp[kk + 1] - vg_sp[kk])
    id_po = id_sp[kk] + f * (id_sp[kk + 1] - id_sp[kk])
    R["pinch"] = (vg_po, id_po, 5 + VTH, id_for_vgs(5 + VTH), 5 + VTON)
    # şekil ID-VGS
    vg_plot = np.linspace(0, 8, 800)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
    sel = vg_sp <= 8
    ax[0].plot(vg_sp[sel], id_sp[sel] * 1e3, "b-", lw=1.9, label="SPICE (BS170 model)")
    ax[0].plot(vg_plot, np.array([id_for_vgs(v) for v in vg_plot]) * 1e3, "g--", lw=1.4, label="Square law, $K_N$=72 mA/V$^2$, $V_{TH}$=2.0 V")
    ax[0].axhline(500, color="r", ls=":", lw=1); ax[0].text(0.2, 515, "datasheet $I_{D(max)}$ = 500 mA", color="r", fontsize=8)
    ax[0].axvspan(0, VTON, color="#DDDDFF", alpha=0.5)
    ax[0].axvspan(VTON, vg_po, color="#DDFFDD", alpha=0.5)
    ax[0].axvspan(vg_po, 8, color="#FFEEDD", alpha=0.6)
    ax[0].text(0.15, 880, "cut-off", fontsize=9); ax[0].text(2.9, 880, "saturation", fontsize=9); ax[0].text(6.45, 880, "triode", fontsize=9)
    mark(ax[0], vg_po, id_po * 1e3, "pinch-off (%.2f V, %.0f mA)" % (vg_po, id_po * 1e3), dx=-125, dy=-5)
    ax[0].set_xlim(0, 8); ax[0].set_ylim(0, 1000)
    ax[0].set_xlabel("$V_{GS}$ (V)"); ax[0].set_ylabel("$I_D$ (mA)")
    ax[0].set_title("$I_D$–$V_{GS}$, $V_{DS}$ source $V_2$ = 5 V")
    ax[0].legend(loc="upper left", fontsize=7.5, bbox_to_anchor=(0.0, 0.84))
    s2 = (vg_sp >= 0) & (vg_sp <= 6)
    ax[1].plot(vg_sp[s2], np.sqrt(id_sp[s2] * 1e3), "b-", lw=1.9, label="SPICE")
    lin = (vg_sp > 2.4) & (vg_sp < 4.0)
    pf = np.polyfit(vg_sp[lin], np.sqrt(id_sp[lin] * 1e3), 1)
    vth_ex = -pf[1] / pf[0]
    xx = np.linspace(vth_ex, 4.5, 50)
    ax[1].plot(xx, np.polyval(pf, xx), "k--", lw=1.0, label="linear extrapolation")
    mark(ax[1], vth_ex, 0, "$V_{TH}$ (extrapolated) = %.2f V" % vth_ex, dx=-20, dy=18)
    ax[1].set_xlim(0, 6); ax[1].set_ylim(-0.5, 20)
    ax[1].set_xlabel("$V_{GS}$ (V)"); ax[1].set_ylabel("$\\sqrt{I_D}$ (mA$^{1/2}$)")
    ax[1].set_title("Threshold extraction from the square-root plot")
    ax[1].legend(loc="upper left")
    R["fig_idvgs"] = save(fig, "e2_idvgs")
    R["vth_extr"] = vth_ex
    R["k_extr"] = (pf[0] ** 2) * 2  # K_eff = 2*slope^2 (mA/V^2)

    # VTH yayılımı
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    for vt, c in ((0.8, "tab:red"), (2.0, "tab:green"), (3.0, "tab:blue")):
        ax.plot(vg_plot, [0 if v <= vt else 36 * (v - vt) ** 2 for v in vg_plot], color=c, label="$V_{TH}$ = %.1f V" % vt)
    ax.set_ylim(0, 600); ax.set_xlim(0, 6)
    ax.set_xlabel("$V_{GS}$ (V)"); ax.set_ylabel("$I_D$ (mA)")
    ax.set_title("Effect of the datasheet $V_{GS(th)}$ spread ($K_N$ = 72 mA/V$^2$)")
    ax.legend()
    R["fig_vth_spread"] = save(fig, "e2_vth_spread")

    # SPICE doğrulama .op tablosu
    ops = []
    for (kind, i, vgs, vds, v1) in th_cols:
        rr, _ = spice_op(bs_netlist(v1), ["v(g)", "i(v2)"], "e2_bs_op_%g" % v1)
        ops.append((v1, rr["v(g)"], -rr["i(v2)"]))
    R["bs_ops"] = ops
    # el hesabı ile model doğrulama: rDS(on) ve gfs
    R["rds_on"] = 1 / (KNa * (10 - VTH))
    R["gfs"] = KNa * (np.sqrt(2 * 0.25 / KNa))
    R["gfs_neamen"] = 2 * np.sqrt(KNa * 0.25)
    R["rds_neamen"] = 1 / (2 * KNa * (10 - VTH))

    # CS-benzeri devre şeması
    d = schemdraw.Drawing()
    d += elm.Dot(open=True).label("$V_1$", loc="top")
    d += elm.Resistor().down().label("$R_{G1}$=33 kΩ", loc="left")
    node = d.add(elm.Dot())
    d += elm.Resistor().down().label("$R_{G2}$=120 kΩ", loc="left")
    d += elm.Ground()
    d.save(os.path.join(FIG, "e2_bias_schem.png"), dpi=200)
    R["fig_bias_schem"] = os.path.join(FIG, "e2_bias_schem.png")
    return R


if __name__ == "__main__":
    R = run()
    print("VM", R["vm"], "Ipk", R["ipk"])
    for t in R["inv_tab"]:
        print("%.2f hand=%.4f spice=%.4f idh=%.3e ids=%.3e %s/%s" % t)
    print("bounds", R["b_nmos_on"], R["b_pmos_sat"], R["b_nmos_tri"], R["b_pmos_off"])
    for a, b in zip(R["bs_th"], R["bs_sp"]):
        print(a, b)
    print("pinch", R["pinch"], "vth_extr", R["vth_extr"], R["k_extr"])
    print("rds", R["rds_on"], R["gfs"], R["gfs_neamen"], R["rds_neamen"])
    print(R["bs_ops"])

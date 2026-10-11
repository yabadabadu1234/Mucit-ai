"""Deney 3 -- MOSFET yükselteç (ortak kaynak) ve akım aynası."""
import numpy as np
from scipy.optimize import brentq
import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt

from common import *

VDD1 = 12.0
R1, R2, RD, RS, RL = 47e3, 33e3, 15e3, 10e3, 10e3
CC1, CC2, CS = 22e-9, 2.2e-9, 22e-9
K, VTH = KN, VTH_N
NM = ".model BS170 NMOS (VTO=2.1 RS=1.572 RD=1.436 KP=.1233 IS=5p)"


def dc_cs():
    vg = VDD1 * R2 / (R1 + R2)
    a = K / 2 * RS
    vov = (-1 + np.sqrt(1 + 4 * a * (vg - VTH))) / (2 * a)
    idq = K / 2 * vov ** 2
    vgs = VTH + vov
    vds = VDD1 - idq * (RD + RS)
    gm = K * vov
    return dict(vg=vg, vov=vov, id=idq, vgs=vgs, vds=vds, gm=gm)


def ac_gain(f, cs_on, gm):
    w = 2 * np.pi * f
    zc = lambda c: 1 / (1j * w * c)
    rg = R1 * R2 / (R1 + R2)
    vg = rg / (rg + zc(CC1))
    zs = RS * zc(CS) / (RS + zc(CS)) if cs_on else RS
    idd = gm * vg / (1 + gm * zs)
    zl_branch = zc(CC2) + RL
    zd = 1 / (1 / RD + 1 / zl_branch)
    vd = -idd * zd
    vo = vd * RL / zl_branch
    return vo


def cs_net(cs_on, vi="DC 0 AC 1 SIN(0 0.1 10k)", extra=""):
    return ("VDD vdd 0 DC 12\nVi in 0 %s\nCc1 in g 22n\nR1 vdd g 47k\nR2 g 0 33k\nM1 d g s 0 BS170 W=100u L=100u\nRD vdd d 15k\nRS s 0 10k\n%sCc2 d o 2.2n\nRL o 0 10k\n%s\n%s\n"
            % (vi, "CS s 0 22n\n" if cs_on else "", extra, NM))


def mirror_hand(vi, vdd=15.0, r1=680.0, r2=1000.0):
    if vi <= VTH:
        return 0.0, 0.0, "cut-off"
    f = lambda i: vi - r1 * i - VTH - np.sqrt(2 * i / K)
    iref = brentq(f, 0, (vi - VTH) / r1, xtol=1e-15)
    vov = np.sqrt(2 * iref / K)
    # M2: doyma varsayımı
    vds = vdd - r2 * iref
    if vds >= vov:
        return iref, iref, "saturation"
    g = lambda i: K * (vov * (vdd - r2 * i) - (vdd - r2 * i) ** 2 / 2) - i
    iout = brentq(g, (vdd - vov) / r2, vdd / r2, xtol=1e-15)
    return iref, iout, "triode"


def run():
    R = {}
    q = dc_cs()
    R["q"] = q
    # ---- el hesabı tablosu
    gm = q["gm"]
    rl_eff = RD * RL / (RD + RL)
    av_cs = -gm * rl_eff
    av_no = -gm * rl_eff / (1 + gm * RS)
    R["av_mid"] = (av_cs, av_no)
    R["rin"] = R1 * R2 / (R1 + R2)
    R["rout"] = RD
    R["av_10k"] = (ac_gain(1e4, True, gm), ac_gain(1e4, False, gm))
    # CS değeri: 10 kHz'de orta-bant kazancın %90'ı için gerekli kapasite
    def need(c):
        global CS
        old = CS
        CS = c
        v = abs(ac_gain(1e4, True, gm))
        CS = old
        return v / abs(av_cs) - 0.9
    R["cs_need"] = brentq(need, 22e-9, 1e-3)
    # ---- SPICE: .op
    ops = []
    for cs_on in (True, False):
        r, _ = spice_op(cs_net(cs_on, "DC 0"), ["v(g)", "v(s)", "v(d)"], "e3_op_%d" % cs_on)
        vgs = r["v(g)"] - r["v(s)"]
        vds = r["v(d)"] - r["v(s)"]
        idd = (12 - r["v(d)"]) / RD
        ops.append((vgs, vds, idd))
    R["op"] = ops
    # ---- SPICE: AC ve Bode
    f_hz = None
    bode = {}
    for cs_on in (True, False):
        r, _ = spice_run(cs_net(cs_on), ["mag(v(o))", "real(i(vi))", "imag(i(vi))"], "ac dec 60 10 100Meg", "e3_ac_%d" % cs_on)
        bode[cs_on] = r
    R["bode"] = bode
    f = bode[True]["x"]
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    fh = np.logspace(1, 8, 400)
    for cs_on, c, lab in ((True, "b", "with $C_S$"), (False, "r", "without $C_S$")):
        ax.semilogx(f, 20 * np.log10(bode[cs_on]["mag(v(o))"]), c + "-", lw=1.8, label="SPICE, " + lab)
        ax.semilogx(fh, 20 * np.log10(np.abs([ac_gain(x, cs_on, gm) for x in fh])), c + "--", lw=1.0, label="phasor calc., " + lab)
    ax.axvline(1e4, color="gray", ls=":", lw=1)
    ax.axhline(20 * np.log10(abs(av_cs)), color="b", ls=":", lw=0.8)
    ax.text(12, 20 * np.log10(abs(av_cs)) + 0.6, "mid-band $|A_V|$ = %.1f (ideal $C_S$ short)" % abs(av_cs), fontsize=8, color="b")
    k = np.argmin(np.abs(f - 1e4))
    mark(ax, f[k], 20 * np.log10(bode[True]["mag(v(o))"][k]), dx=10, dy=-25)
    mark(ax, f[k], 20 * np.log10(bode[False]["mag(v(o))"][k]), dx=10, dy=-25, color="darkgreen")
    ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("$|v_o/v_i|$ (dB)")
    ax.set_title("Frequency response of the common-source amplifier (dotted vertical: 10 kHz)")
    ax.set_xlim(10, 1e8); ax.set_ylim(-60, 40)
    ax.legend(loc="lower right", fontsize=8)
    R["fig_bode"] = save(fig, "e3_bode")
    R["gain_sp_10k"] = (bode[True]["mag(v(o))"][k], bode[False]["mag(v(o))"][k])
    k1 = np.argmin(np.abs(f - 1e6))
    R["mid_sp"] = (bode[True]["mag(v(o))"][k1], bode[False]["mag(v(o))"][k1])
    zin = 1.0 / (np.abs(bode[True]["real(i(vi))"][k] + 1j * bode[True]["imag(i(vi))"][k]))
    R["rin_sp"] = zin
    # Rout
    net = cs_net(True, "DC 0 AC 0").replace("Cc2 d o 2.2n\nRL o 0 10k\n", "Itest 0 d DC 0 AC 1\n")
    r, _ = spice_run(net, ["mag(v(d))"], "ac lin 1 10k 10k", "e3_rout")
    R["rout_sp"] = float(r["mag(v(d))"][0])
    # ---- SPICE: geçici
    tr = {}
    for cs_on in (True, False):
        r, _ = spice_run(cs_net(cs_on), ["v(in)", "v(o)"], "tran 2u 8m 0 1u", "e3_tran_%d" % cs_on)
        t, vi, vo = r["x"], r["v(in)"], r["v(o)"]
        sel = t > 6e-3
        amp_o = (vo[sel].max() - vo[sel].min()) / 2
        amp_i = (vi[sel].max() - vi[sel].min()) / 2
        tr[cs_on] = (amp_o, amp_i)
        fig, ax = plt.subplots(2, 1, figsize=(8.4, 5.0), sharex=True)
        s2 = (t > 7.5e-3)
        ax[0].plot(t[s2] * 1e3, vi[s2] * 1e3, "b-", lw=1.5)
        ax[0].set_ylabel("$v_i$ (mV)")
        ax[1].plot(t[s2] * 1e3, (vo[s2] - np.mean(vo[sel])) * 1e3 if False else vo[s2] * 1e3, "r-", lw=1.5)
        ax[1].set_ylabel("$v_o$ (mV)")
        ax[1].set_xlabel("Time (ms)")
        ax[0].set_title("Common-source amplifier, 100 mV / 10 kHz input, %s $C_S$ (ngspice)" % ("with" if cs_on else "without"))
        kk = np.argmax(vi[s2]); mark(ax[0], t[s2][kk] * 1e3, vi[s2][kk] * 1e3, dx=10, dy=-14)
        kk = np.argmin(vo[s2]); mark(ax[1], t[s2][kk] * 1e3, vo[s2][kk] * 1e3, dx=10, dy=12)
        R["fig_tran_%d" % cs_on] = save(fig, "e3_tran_%d" % cs_on)
    R["tran_amp"] = tr
    # ---- Akım aynası
    vis = [1, 3, 5, 8, 10, 12, 15]
    R["mirror_hand"] = [(v,) + mirror_hand(v) for v in vis]
    net = "VDD vdd 0 DC 15\nVi vi 0 DC 0\nR1 vi d1 680\nM1 d1 d1 0 0 BS170 W=100u L=100u\nM2 d2 d1 0 0 BS170 W=100u L=100u\nR2 vdd d2 1k\n" + NM + "\n"
    r, _ = spice_run(net, ["i(vi)", "i(vdd)"], "dc Vi 0 15 0.5", "e3_mirror_dc")
    vi_s = r["x"]
    iref_s, iout_s = -r["i(vi)"], -r["i(vdd)"]
    R["mirror_sp"] = [(v, float(np.interp(v, vi_s, iref_s)), float(np.interp(v, vi_s, iout_s))) for v in vis]
    vi_f = np.linspace(0, 15, 301)
    hand_f = np.array([mirror_hand(v)[:2] for v in vi_f])
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].plot(vi_s, iref_s * 1e3, "bo-", ms=3.5, lw=1.4, label="$I_{ref}$ (SPICE)")
    ax[0].plot(vi_s, iout_s * 1e3, "rs-", ms=3.5, lw=1.4, label="$I_{out}$ (SPICE)")
    ax[0].plot(vi_f, hand_f[:, 0] * 1e3, "b--", lw=1.0, label="$I_{ref}$ (hand model)")
    ax[0].plot(vi_f, hand_f[:, 1] * 1e3, "r--", lw=1.0, label="$I_{out}$ (hand model)")
    k10 = np.argmin(np.abs(vi_s - 10))
    mark(ax[0], 10, iref_s[k10] * 1e3, dx=-100, dy=15)
    k15 = np.argmin(np.abs(vi_s - 15))
    mark(ax[0], 15, iout_s[k15] * 1e3, dx=-110, dy=-30, color="darkgreen")
    ax[0].set_xlabel("$V_i$ (V)"); ax[0].set_ylabel("Current (mA)")
    ax[0].set_title("$I_{ref}$–$V_i$ and $I_{out}$–$V_i$"); ax[0].legend(fontsize=8)
    rat = np.divide(iout_s, iref_s, out=np.zeros_like(iout_s), where=iref_s > 1e-6)
    ax[1].plot(vi_s[iref_s > 1e-6], rat[iref_s > 1e-6], "ko-", ms=3.5)
    ax[1].set_xlabel("$V_i$ (V)"); ax[1].set_ylabel("$I_{out}/I_{ref}$")
    ax[1].set_title("Mirror ratio (M2 leaves saturation at large $V_i$)")
    ax[1].set_ylim(0, 1.2)
    R["fig_mirror"] = save(fig, "e3_mirror")
    # M2 doymadan çıkış Vi (el modeli)
    vv = np.linspace(2, 15, 2601)
    reg = [mirror_hand(v)[2] for v in vv]
    R["vi_tri"] = next(v for v, g in zip(vv, reg) if g == "triode")
    dr = iref_s > 1e-6
    sat = np.abs(rat - 1) < 0.01
    R["vi_tri_sp"] = float(vi_s[dr & ~sat][0]) if np.any(dr & ~sat) else None
    # ---- Şemalar
    schem_cs(os.path.join(FIG, "e3_cs_schem.png"))
    schem_mirror(os.path.join(FIG, "e3_mirror_schem.png"))
    R["fig_cs_schem"] = os.path.join(FIG, "e3_cs_schem.png")
    R["fig_mirror_schem"] = os.path.join(FIG, "e3_mirror_schem.png")
    return R


def schem_cs(path):
    d = schemdraw.Drawing()
    top, bot = 3.6, -3.6
    L = lambda x, y, t: d.add(elm.Label().at((x, y)).label(t))
    q = d.add(elm.NFet(bulk=False).reverse().at((0, 0)))
    gy = q.gate[1]
    d += elm.Resistor().at((0, 0)).up().length(2.3)
    d += elm.Line().up().length(top - 2.3)
    d += elm.Line().left().tox(-3)
    L(-1.5, top + 0.35, "$V_{DD}$ = 12 V")
    L(1.35, 1.75, "$R_D$ 15 k\u03a9")
    d += elm.Line().at(q.gate).left().tox(-3)
    d += elm.Dot().at((-3, gy))
    d += elm.Resistor().at((-3, gy)).up().length(2.3)
    d += elm.Line().up().length(top - (gy + 2.3))
    L(-2.0, 1.0, "$R_1$ 47 k\u03a9")
    d += elm.Resistor().at((-3, gy)).down().length(2.3)
    d += elm.Line().down().length(abs(bot) - abs(gy) - 2.3)
    d += elm.Ground()
    L(-2.0, -2.2, "$R_2$ 33 k\u03a9")
    d += elm.Resistor().at((0, -1.5)).down().length(2.1)
    d += elm.Ground()
    L(-1.45, -2.6, "$R_S$ 10 k\u03a9")
    d += elm.Line().at((0, -1.5)).right().length(1.3)
    d += elm.Capacitor().down().length(2.1)
    d += elm.Ground()
    L(1.3, -4.5, "$C_S$ 22 nF")
    d += elm.Dot().at((0, 0))
    d += elm.Capacitor().at((0, 0)).right().length(2.2)
    d += elm.Dot()
    d += elm.Line().right().length(1.0).dot(open=True)
    L(1.1, 0.5, "$C_{C2}$ 2.2 nF")
    L(3.9, 0.0, "$v_o$")
    d += elm.Resistor().at((2.2, 0)).down().length(2.3)
    d += elm.Ground()
    L(3.45, -1.3, "$R_L$ 10 k\u03a9")
    d += elm.Capacitor().at((-6.2, gy)).right().length(2.4)
    d += elm.Line().right().tox(-3)
    d += elm.Line().at((-6.2, gy)).left().length(0.4)
    d += elm.SourceSin().down().length(2.0)
    d += elm.Ground()
    L(-5.0, gy + 0.5, "$C_{C1}$ 22 nF")
    L(-7.9, -1.6, "$v_i$")
    L(-4.1, gy - 0.5, "$R_{in}$ \u2192")
    d.save(path, dpi=190)


def schem_mirror(path):
    d = schemdraw.Drawing()
    L = lambda x, y, t: d.add(elm.Label().at((x, y)).label(t))
    m1 = d.add(elm.NFet(bulk=False).at((0, 0)))
    m2 = d.add(elm.NFet(bulk=False).reverse().at((4, 0)))
    d += elm.Line().at(m1.source).down().length(0.6)
    d += elm.Ground()
    d += elm.Line().at(m2.source).down().length(0.6)
    d += elm.Ground()
    d += elm.Line().at(m1.gate).tox(m2.gate)
    d += elm.Dot().at((2.0, m1.gate[1]))
    d += elm.Line().at((0, 0)).up().length(0.35)
    d += elm.Dot()
    d += elm.Line().right().tox(2.0)
    d += elm.Line().down().toy(m1.gate[1])
    d += elm.Resistor().at((0, 2.8)).down().length(2.3)
    d += elm.Line().at((0, 2.8)).left().tox(-2.5)
    d += elm.Line().down().length(1.0)
    d += elm.SourceV().down().length(2.3).reverse()
    d += elm.Ground()
    d += elm.Resistor().at((4, 0)).up().length(2.3)
    d += elm.Line().up().length(0.5)
    L(4.0, 3.3, "$V_{DD}$ = 15 V")
    L(-1.3, 1.65, "$R_1$ 680 \u03a9")
    L(1.3, 1.65, "$I_{ref}$ \u2193")
    L(5.4, 1.15, "$R_2$ 1 k\u03a9")
    L(4.7, 2.2, "$I_{out}$ \u2193")
    L(-0.95, -0.75, "M1")
    L(4.95, -0.75, "M2")
    L(-3.2, 0.9, "$V_i$")
    d.save(path, dpi=190)


if __name__ == "__main__":
    R = run()
    print(R["q"]); print("av_mid", R["av_mid"], "av10k", R["av_10k"], [abs(x) for x in R["av_10k"]])
    print("cs_need", R["cs_need"], "op", R["op"])
    print("gain_sp_10k", R["gain_sp_10k"], "rin_sp", R["rin_sp"], "rout_sp", R["rout_sp"], "tran_amp", R["tran_amp"])
    for a, b in zip(R["mirror_hand"], R["mirror_sp"]):
        print(a, b)
    print(R["vi_tri"], R["vi_tri_sp"])

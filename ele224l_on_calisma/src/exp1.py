"""Deney 1 -- PN eklem diyot: hesaplar, SPICE (ngspice) ve şekiller."""
import numpy as np
from scipy.optimize import brentq
import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt

from common import *

R1 = 1e3
VS_LIST = [-5, -4, -3, -2, -1, 0, 0.5, 0.6, 0.7, 0.8, 1, 1.2, 1.4, 1.6, 2, 3, 4, 5]
D1N4148 = ".model D1N4148 D(IS=2.52n RS=.568 N=1.752 CJO=4p M=.4 TT=20n)"


def shockley(vd, n=1.0):
    return IS_D * (np.exp(vd / (n * VT)) - 1.0)


def solve_vd(vs, r=R1, n=1.0):
    f = lambda vd: vd + r * shockley(vd, n) - vs
    return brentq(f, -abs(vs) - 1, abs(vs) + 1, xtol=1e-15)


def ideal(vs):
    if vs > 0:
        return 0.0, vs / R1
    return float(vs) if vs < 0 else 0.0, 0.0


def lambert_vd(vs, r=R1):
    from scipy.special import lambertw
    a = r * IS_D / VT
    x = a * np.exp((vs + r * IS_D) / VT) if vs < 0.9 else None
    if x is None:  # taşma: log-uzayında asimptotik çözüm
        # W(e^y) ~ y - ln(y) + ln(y)/y
        y = np.log(a) + (vs + r * IS_D) / VT
        w = y - np.log(y) + np.log(y) / y
        # 3 Newton adımı
        for _ in range(4):
            w = w - (w + np.log(w) - y) / (1 + 1 / w)
    else:
        w = lambertw(x).real
    i = VT / r * w - IS_D
    return vs - r * i, i


def spice_table(model_line, mname):
    rows = []
    for vs in VS_LIST:
        net = "V1 a 0 DC %g\nD1 a b %s\nR1 b 0 1k\n%s\n" % (vs, mname, model_line)
        r, _ = spice_op(net, ["v(a)", "v(b)", "i(v1)"], "e1_op_%s_%g" % (mname, vs))
        vd = r["v(a)"] - r["v(b)"]
        i = -r["i(v1)"]
        rows.append((vs, vd, i))
    return rows


def schem_halfwave(path):
    d = schemdraw.Drawing()
    src = d.add(elm.SourceSin().up())
    d += elm.Line().right().length(0.6)
    dio = d.add(elm.Diode().right())
    d += elm.Line().right().length(0.8)
    node = d.add(elm.Dot())
    d += elm.Line().right().length(0.8)
    res = d.add(elm.Resistor().down())
    d += elm.Line().left().tox(src.start)
    d += elm.Ground()
    d += elm.Line().left().tox(src.start)
    d += elm.Label().at((src.center[0] - 0.9, src.center[1])).label("$V_S$")
    d += elm.Label().at((dio.center[0], dio.center[1] + 0.5)).label("D1")
    d += elm.Label().at((dio.center[0], dio.center[1] - 0.5)).label("$V_D$ (+ → −)")
    d += elm.Label().at((node.center[0], node.center[1] + 0.5)).label("$V_O$")
    d += elm.Label().at((res.center[0] + 1.2, res.center[1])).label("$R_1$ = 1 kΩ")
    d.save(path, dpi=200)


def schem_models(path):
    d = schemdraw.Drawing()
    d += elm.Diode().right().label("Ideal", loc="top").length(2.5)
    d.move(2, 0)
    d += elm.Diode().right().label("CVD", loc="top").length(2.5)
    d += elm.Battery().right().label("0.7 V", loc="bottom").reverse() if False else elm.Line().length(0.01)
    d.save(path, dpi=200)


def run():
    R = {}
    # ---- Tablo 1: ideal diyot ----
    R["ideal"] = [(vs,) + ideal(vs) for vs in VS_LIST]
    # ---- Tablo 2: diyot denklemi ----
    t2 = []
    for vs in VS_LIST:
        vd = solve_vd(vs)
        t2.append((vs, vd, shockley(vd)))
    R["eq"] = t2
    # Lambert-W doğrulaması
    R["lambert"] = [(vs,) + lambert_vd(vs) for vs in VS_LIST]
    # CVD (0.7 V)
    R["cvd"] = [(vs, 0.7 if vs > 0.7 else (vs if vs <= 0.7 else 0), max(vs - 0.7, 0) / R1) for vs in VS_LIST]
    # ---- SPICE: diyot denklem parametreleriyle ve 1N4148 ----
    R["sp_eq"] = spice_table(".model Deq D(IS=20f N=1 RS=0)", "Deq")
    R["sp_1n"] = spice_table(D1N4148, "D1N4148")
    # SPICE'ı föydeki denkleme kalibre et: V_T=0.026 V (T=301.7 K) ve GMIN~0
    ncal = 0.026 / (1.380649e-23 * 300.15 / 1.602176634e-19)
    R["ncal"] = ncal
    R["sp_eq_cal"] = spice_table(".model Dcal D(IS=20f N=%.7f RS=0)\n.options gmin=1e-20" % ncal, "Dcal")
    # iterasyon örneği V_S = 5 V
    it = []
    vd = 0.7
    for k in range(5):
        idk = (5 - vd) / R1
        vd_new = VT * np.log(idk / IS_D + 1)
        it.append((k, vd, idk, vd_new))
        vd = vd_new
    R["iter"] = it
    # ortalama değer (SPICE geçici)


    # ---- Şekil: modeller (ideal / CVD) ----
    v = np.linspace(-1, 1.6, 600)
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    ax[0].plot([-1, 0, 0], [0, 0, 1], "b-", lw=2)
    ax[0].plot([0, 0], [0, 1], "b-", lw=2)
    ax[0].plot([0, 1.6], [0, 1], "b-", lw=2) if False else None
    ax[0].plot([0, 1.0], [0, 0], "b-", lw=2)
    ax[0].set_ylim(-0.1, 1.1); ax[0].set_xlim(-1, 1.0)
    ax[0].set_title("Ideal diode: $V_D=0$ if on, $I_D=0$ if off")
    ax[0].set_xlabel("$V_D$ (V)"); ax[0].set_ylabel("$I_D$ (arb. units)")
    ax[0].annotate("ON: vertical line\n($V_D=0$, any $I_D\\geq 0$)", (0, 0.6), (0.15, 0.6), arrowprops=dict(arrowstyle="->"))
    ax[0].annotate("OFF: horizontal line\n($I_D=0$, any $V_D\\leq 0$)", (-0.5, 0), (-0.95, 0.3), arrowprops=dict(arrowstyle="->"))
    von = 0.7
    ax[1].plot([-1, von], [0, 0], "b-", lw=2)
    ax[1].plot([von, von], [0, 1], "b-", lw=2)
    ax[1].set_ylim(-0.1, 1.1); ax[1].set_xlim(-1, 1.6)
    ax[1].set_title("CVD model: $V_D=V_{D(on)}=0.7$ V if on")
    ax[1].set_xlabel("$V_D$ (V)"); ax[1].set_ylabel("$I_D$ (arb. units)")
    ax[1].annotate("$V_{D(on)}=0.7$ V", (0.7, 0.05), (0.85, 0.2), arrowprops=dict(arrowstyle="->"))
    R["fig_models"] = save(fig, "e1_models")

    # ---- Şekil: diyot denklemi MATLAB-eşdeğeri ----
    vd = np.linspace(-1, 1, 2001)
    idd = shockley(vd)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    ax[0].plot(vd, idd * 1e3, "b-", lw=1.8)
    ax[0].set_ylim(-1, 20); ax[0].set_xlim(-1, 1)
    ax[0].set_xlabel("$V_D$ (V)"); ax[0].set_ylabel("$I_D$ (mA)")
    ax[0].set_title("Linear scale (zoomed: $-1\\ldots20$ mA)")
    vk = 0.6
    mark(ax[0], vk, shockley(vk) * 1e3, dx=-10, dy=25)
    ax[1].semilogy(vd, np.abs(idd), "b-", lw=1.8)
    ax[1].set_xlabel("$V_D$ (V)"); ax[1].set_ylabel("$|I_D|$ (A)")
    ax[1].set_title("Semilog scale $|I_D|$ (full range)")
    ax[1].axhline(IS_D, color="gray", ls="--", lw=1)
    ax[1].annotate("$|I_D|\\to I_S=20$ fA (reverse)", (-0.8, IS_D), (-0.95, 1e-9), arrowprops=dict(arrowstyle="->"))
    R["fig_eq"] = save(fig, "e1_diode_eq")
    R["pt_eq"] = (vk, shockley(vk))

    # ---- SPICE DC süpürme (1N4148), ID–VD ----
    net = "V1 a 0 DC 0\nD1 a b D1N4148\nR1 b 0 1k\n" + D1N4148 + "\n"
    r, _ = spice_run(net, ["v(a)", "v(b)", "i(v1)"], "dc v1 -5 5 0.01", "e1_dc_1n4148")
    vdd = r["v(a)"] - r["v(b)"]
    idd = -r["i(v1)"]
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.9))
    ax[0].plot(vdd, idd * 1e3, "b-", lw=1.8, label="SPICE, 1N4148")
    vv = np.linspace(-5, 0.7, 800)
    ax[0].plot(vv, shockley(vv) * 1e3, "g--", lw=1.2, label="Eq. (1) ($I_S$=20 fA, n=1)")
    ax[0].set_ylim(-0.5, 5); ax[0].set_xlim(-5, 1.0)
    ax[0].set_xlabel("$V_D$ (V)"); ax[0].set_ylabel("$I_D$ (mA)")
    ax[0].set_title("DC sweep $-5\\leq V_S\\leq5$ V ($V_D$ on x, $I_D$ on y)")
    k = np.argmin(np.abs(idd - 2e-3))
    mark(ax[0], vdd[k], idd[k] * 1e3, dx=-60, dy=20)
    ax[0].legend(loc="upper left")
    ax[1].semilogy(vdd, np.abs(idd) + 1e-30, "b-", lw=1.8)
    ax[1].set_ylim(1e-15, 1e-2)
    ax[1].set_xlabel("$V_D$ (V)"); ax[1].set_ylabel("$|I_D|$ (A)")
    ax[1].set_title("Same data, semilog")
    R["fig_spice"] = save(fig, "e1_spice_dc")
    R["pt_spice"] = (vdd[k], idd[k], vdd[k] + 1e3 * idd[k])

    # ---- Zaman bölgesi (CVD) ----
    f0 = 1e3
    t = np.linspace(0, 3 / f0, 6001)
    vs_t = 5 * np.sin(2 * np.pi * f0 * t)
    vo_t = np.where(vs_t > 0.7, vs_t - 0.7, 0.0)
    fig, ax = plt.subplots(figsize=(8.5, 3.9))
    ax.plot(t * 1e3, vs_t, "b-", lw=1.4, label="$V_S$ (input)")
    ax.plot(t * 1e3, vo_t, "r-", lw=1.8, label="$V_O$ (output, CVD 0.7 V)")
    ax.axhline(0.7, color="gray", ls=":", lw=1)
    ax.text(2.05, 0.9, "$V_{D(on)}=0.7$ V", fontsize=8.5)
    ax.set_xlabel("Time (ms)"); ax.set_ylabel("Voltage (V)")
    ax.set_title("Half-wave rectifier, simplified (CVD) model, $f$ = 1 kHz")
    tp = 0.25e-3
    mark(ax, tp * 1e3, 4.3, "$V_{O,peak}$=4.3 V", dx=10, dy=-4)
    ax.legend(loc="lower left")
    R["fig_time"] = save(fig, "e1_time")
    # SPICE geçici analiz karşılaştırması
    net = "V1 a 0 SIN(0 5 1k)\nD1 a b D1N4148\nR1 b 0 1k\n" + D1N4148 + "\n"
    r, _ = spice_run(net, ["v(a)", "v(b)"], "tran 2u 3m", "e1_tran")
    R["tran_vo_peak"] = float(np.max(r["v(b)"]))
    R["theta"] = float(np.degrees(np.arcsin(0.7 / 5)))
    fig, ax = plt.subplots(figsize=(8.5, 3.9))
    ax.plot(r["x"] * 1e3, r["v(a)"], "b-", lw=1.2, label="$V_S$")
    ax.plot(r["x"] * 1e3, r["v(b)"], "r-", lw=1.6, label="$V_O$ (SPICE, 1N4148)")
    ax.plot(t * 1e3, vo_t, "k--", lw=1.0, label="$V_O$ (CVD model)")
    ax.set_xlabel("Time (ms)"); ax.set_ylabel("Voltage (V)")
    ax.set_title("Transient SPICE vs. simplified model")
    ax.legend(loc="lower left")
    R["fig_time_spice"] = save(fig, "e1_time_spice")

    # ---- Şemalar ----
    schem_halfwave(os.path.join(FIG, "e1_schem.png"))
    R["fig_schem"] = os.path.join(FIG, "e1_schem.png")
    return R


if __name__ == "__main__":
    R = run()
    print("IDEAL", R["ideal"][:3])
    for a, b, c in zip(R["eq"], R["lambert"], R["sp_eq"]):
        print("vs=%5.2f  eq VD=%.6f ID=%.6e | W VD=%.6f ID=%.6e | spice VD=%.6f ID=%.6e" % (a[0], a[1], a[2], b[1], b[2], c[1], c[2]))
    for c in R["sp_1n"]:
        print("1N4148 vs=%5.2f VD=%.5f ID=%.5e" % c)
    print(R["pt_eq"], R["pt_spice"], R["tran_vo_peak"], R["theta"])

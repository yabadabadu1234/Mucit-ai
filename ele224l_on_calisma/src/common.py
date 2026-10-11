import os
import re
import subprocess
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIG = os.path.join(ROOT, "fig")
SPICE = os.path.join(ROOT, "spice")
OUT = os.path.join(ROOT, "out")
for d in (FIG, SPICE, OUT):
    os.makedirs(d, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 10, "axes.grid": True, "grid.alpha": 0.35,
    "figure.dpi": 110, "savefig.dpi": 200, "axes.titlesize": 10.5, "legend.fontsize": 9,
    "mathtext.fontset": "dejavuserif",
})

# ---- veri sayfası ve ders föyü sabitleri (kaynakları raporda yazılıdır) ----
VT = 0.026            # Exp1 föyü: V_T = 0.026 V
IS_D = 20e-15         # Exp1 föyü: I_S = 20 fA
KN = 72e-3            # föy: K_N = 72 mA/V^2   (A/V^2 cinsinden)
VTH_N = 2.0           # BS170 veri sayfası tipik V_GS(th) = 2.0 V
BETA = 170.0          # BC238A: h_FE grup A 120..220 -> ortalama 170
VBE_ON = 0.62         # BC238 veri sayfası V_BE(on) tipik 0.62 V (V_CE=5V, I_C=2mA)
VCE_SAT = 0.2         # sade modelde doyma gerilimi (kabul)
VT_ROOM = 0.02585     # 300 K'de kT/q (SPICE'ın kullandığı)


def spice_run(netlist, vectors, cmds, name):
    """netlist: .control hariç gövde; cmds: ngspice komutları (analiz); vectors: wrdata ile yazılacaklar.
    Döner: {vektör: np.array}; ilk sütun 'x' (ölçek)."""
    path_cir = os.path.join(SPICE, name + ".cir")
    out_txt = os.path.join(tempfile.gettempdir(), name + ".dat")
    if os.path.exists(out_txt):
        os.remove(out_txt)
    body = "* ELE224L\n" + netlist.strip("\n") + "\n.control\nset noaskquit\nset wr_vecnames\noption numdgt=9\n" + cmds.strip("\n") + \
        "\nwrdata %s %s\nquit\n.endc\n.end\n" % (out_txt, " ".join(vectors))
    open(path_cir, "w").write(body)
    r = subprocess.run(["ngspice", "-b", path_cir], capture_output=True, text=True, timeout=300)
    if not os.path.exists(out_txt):
        raise RuntimeError("ngspice hata:\n" + r.stdout[-2500:] + r.stderr[-1500:])
    lines = open(out_txt).read().strip().split("\n")
    names = lines[0].split()
    data = np.array([[float(v) for v in ln.split()] for ln in lines[1:]])
    res = {"x": data[:, 0]}
    # her vektör (x, y) çifti olarak yazılır
    for i, v in enumerate(vectors):
        res[v] = data[:, 2 * i + 1]
    return res, r.stdout


def spice_op(netlist, nodes, name):
    """.op analizi; {ad: değer}"""
    path_cir = os.path.join(SPICE, name + ".cir")
    cmds = "op\n" + "\n".join("print %s" % n for n in nodes) + "\nquit\n"
    body = "* ELE224L\n" + netlist.strip("\n") + "\n.control\nset noaskquit\noption numdgt=9\n" + cmds + ".endc\n.end\n"
    open(path_cir, "w").write(body)
    r = subprocess.run(["ngspice", "-b", path_cir], capture_output=True, text=True, timeout=120)
    res = {}
    for ln in r.stdout.split("\n"):
        m = re.match(r"^\s*([\w\.\#\(\)\[\]@:]+)\s*=\s*([-+0-9\.eE]+)", ln)
        if m:
            res[m.group(1).lower()] = float(m.group(2))
    return res, r.stdout


_MARKS = []
FIG_MARKS = {}


def mark(ax, x, y, text=None, dx=0.0, dy=0.0, color="crimson"):
    """İmleç (cursor) işareti: çarpı + koordinat etiketi."""
    _MARKS.append((ax, float(x), float(y)))
    ax.plot([x], [y], marker="x", color=color, ms=8, mew=2, zorder=5)
    if text is None:
        text = "(%.4g, %.4g)" % (x, y)
    ax.annotate(text, (x, y), xytext=(8 + dx, 8 + dy), textcoords="offset points", color=color,
                fontsize=8.5, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, alpha=0.9))


def save(fig, name):
    FIG_MARKS[name] = [(ax.get_xlabel(), ax.get_ylabel(), x, y) for (ax, x, y) in _MARKS]
    _MARKS.clear()
    p = os.path.join(FIG, name + ".png")
    fig.tight_layout()
    fig.savefig(p)
    plt.close(fig)
    return p


def fmt(x, nd=3):
    """Mühendislik gösterimine yakın sade biçim (ondalık nokta)."""
    if x == 0:
        return "0"
    ax = abs(x)
    if ax >= 1e4 or ax < 1e-3:
        return ("%." + str(nd - 1) + "e") % x
    d = nd - 1 - int(np.floor(np.log10(ax)))
    d = max(d, 0)
    return ("%." + str(d) + "f") % x


def pct_err(ref, val):
    if ref == 0:
        return float("nan")
    return 100.0 * (val - ref) / abs(ref)


def clean_cir(path):
    """Ek için temiz netlist: .control bloğu yerine analiz komutu (.dc/.tran/.ac/.op) yazılır."""
    lines = open(path).read().split("\n")
    out, ana = [], None
    inctl = False
    for ln in lines:
        s = ln.strip()
        if s.lower() == ".control":
            inctl = True
            continue
        if s.lower() == ".endc":
            inctl = False
            continue
        if inctl:
            w = s.split()
            if w and w[0].lower() in ("dc", "tran", "ac", "op") and ana is None:
                ana = "." + s
            continue
        if s.startswith("* ELE224L") or s == ".end":
            continue
        out.append(ln)
    if ana:
        out.append(ana)
    out.append(".end")
    return "\n".join(out) + "\n"

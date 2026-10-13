import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, PathPatch
from matplotlib.path import Path
from breadboard import Breadboard, ROWY, RAILY, xy, WIRECOL

class Lab(Breadboard):
    """Devre tahtası + güç kaynağı / multimetre / osiloskop çizimi. Aletlerin kabloları `lead` bileşenleriyle aynı adı taşır (net denetimi)."""
    def __init__(self):
        super().__init__(); self.devs = []; self.cab = []
    def psu(self, x, y, volt, plus, minus, title="DA Güç Kaynağı"):
        self.devs.append(("psu", x, y, dict(volt=volt, title=title))); self.cab += [(plus, (x + 2.2, y), "red"), (minus, (x + 6.8, y), "black")]
    def dmm(self, x, y, mode, red, black, title="Multimetre"):
        self.devs.append(("dmm", x, y, dict(mode=mode, title=title))); self.cab += [(red, (x + 2.3, y), "red"), (black, (x + 4.2, y), "black")]
    def scope(self, x, y, tip, gnd, title="Osiloskop (CH1)"):
        self.devs.append(("scope", x, y, dict(title=title))); self.cab += [(tip, (x + 2.6, y), "#E0B000"), (gnd, (x + 6.6, y), "black")]
    def lead(self, name, h, text="", color="red"): super().lead(name, h, text, color)
    def _lead(self, ax, h, meta): pass
    def _dev(self, ax, kind, x, y, m):
        if kind == "psu":
            ax.add_patch(FancyBboxPatch((x, y), 9, 5, boxstyle="round,pad=0.05", fc="#44525F", ec="#222", lw=1.5, zorder=3))
            ax.add_patch(Rectangle((x + 0.6, y + 1.9), 3.6, 2.3, fc="#10261A", ec="#000", zorder=4))
            ax.text(x + 2.4, y + 3.05, m["volt"], color="#6CFF9A", fontsize=11, fontweight="bold", ha="center", va="center", zorder=5, family="monospace")
            for cx in (6.0, 7.6): ax.add_patch(Circle((x + cx, y + 3.0), 0.55, fc="#B8B8B8", ec="#333", zorder=4))
            ax.add_patch(Circle((x + 2.2, y), 0.42, fc="#D32F2F", ec="#000", zorder=6)); ax.add_patch(Circle((x + 6.8, y), 0.42, fc="#222", ec="#000", zorder=6))
            ax.text(x + 2.2, y + 0.95, "+", color="white", ha="center", va="center", fontsize=11, fontweight="bold", zorder=5)
            ax.text(x + 6.8, y + 0.95, "−", color="white", ha="center", va="center", fontsize=11, fontweight="bold", zorder=5)
            ax.text(x + 4.5, y + 5.7, m["title"], ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#222", zorder=5)
        elif kind == "dmm":
            ax.add_patch(FancyBboxPatch((x - 0.3, y), 7.4, 9.6, boxstyle="round,pad=0.1,rounding_size=0.8", fc="#D32F2F", ec="#7A1010", lw=1.5, zorder=3))
            ax.add_patch(Rectangle((x + 0.4, y + 6.4), 5.6, 2.5, fc="#8FA58A", ec="#222", zorder=4))
            ax.text(x + 3.2, y + 7.65, m["mode"], fontsize=11, fontweight="bold", ha="center", va="center", zorder=5, family="monospace", color="#1b2b1b")
            ax.add_patch(Circle((x + 3.2, y + 4.1), 1.55, fc="#2B2B2B", ec="#000", zorder=4)); ax.plot([x + 3.2, x + 3.2], [y + 4.1, y + 5.4], color="white", lw=2, zorder=5)
            ax.add_patch(Circle((x + 2.3, y), 0.42, fc="#D32F2F", ec="#000", zorder=6)); ax.add_patch(Circle((x + 4.2, y), 0.42, fc="#222", ec="#000", zorder=6))
            ax.text(x + 2.3, y + 0.95, "VΩ", color="white", ha="center", va="center", fontsize=6.5, zorder=5); ax.text(x + 4.2, y + 0.95, "COM", color="white", ha="center", va="center", fontsize=6.5, zorder=5)
            ax.text(x + 3.2, y + 10.2, m["title"], ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#222", zorder=5)
        else:
            ax.add_patch(FancyBboxPatch((x, y), 9.2, 7.4, boxstyle="round,pad=0.05", fc="#2D3138", ec="#111", lw=1.5, zorder=3))
            ax.add_patch(Rectangle((x + 0.6, y + 2.0), 5.2, 4.7, fc="#0B1A22", ec="#555", zorder=4))
            for k in range(1, 5): ax.plot([x + 0.6 + k * 1.04] * 2, [y + 2.0, y + 6.7], color="#1D4658", lw=0.5, zorder=5)
            for k in range(1, 4): ax.plot([x + 0.6, x + 5.8], [y + 2.0 + k * 1.175] * 2, color="#1D4658", lw=0.5, zorder=5)
            ax.plot([x + 0.6 + t * 0.052 for t in range(0, 101)], [y + 4.35 + 0.0 * t for t in range(0, 101)], color="#F5D90A", lw=1.2, zorder=6)
            for cx in (7.0, 8.2): ax.add_patch(Circle((x + cx, y + 5.6), 0.45, fc="#B8B8B8", ec="#222", zorder=4))
            ax.add_patch(Circle((x + 2.6, y), 0.42, fc="#E0B000", ec="#000", zorder=6)); ax.add_patch(Circle((x + 6.6, y), 0.42, fc="#222", ec="#000", zorder=6))
            ax.text(x + 2.6, y + 0.95, "uç", color="white", ha="center", va="center", fontsize=6.5, zorder=5); ax.text(x + 6.6, y + 0.95, "şase", color="white", ha="center", va="center", fontsize=6.5, zorder=5)
            ax.text(x + 4.6, y + 8.0, m["title"], ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#222", zorder=5)
    def draw(self, path, figsize=(12, 9.2), rails_note=True):
        fig, ax = plt.subplots(figsize=figsize); ax.set_aspect("equal")
        ax.set_xlim(-1.5, 33); ax.set_ylim(-8.0, 29); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.2, -6.0), 30.9, 18.0, boxstyle="round,pad=0.1", fc="#E9E9E9", ec="#B0B0B0", lw=1.2))
        ax.add_patch(Rectangle((0.4, 2.55), 30.6, 0.9, fc="#D2D2D2", ec="none"))
        for c in range(1, self.cols + 1):
            for y in list(ROWY.values()) + list(RAILY.values()): ax.add_patch(Circle((c, y), 0.17, fc="#3A3A3A", ec="none", zorder=2))
            ax.text(c, 9.0, str(c), ha="center", va="center", fontsize=6.3, rotation=90, color="#444"); ax.text(c, -2.9, str(c), ha="center", va="center", fontsize=6.3, rotation=90, color="#444")
        for r, y in ROWY.items(): ax.text(0.45, y, r, ha="center", va="center", fontsize=7, color="#444")
        for (side, s), y in RAILY.items(): ax.text(0.45, y, s, ha="center", va="center", fontsize=9, color="#B00000" if s == "+" else "#222", fontweight="bold")
        for yy, cc in ((10.5, "#B00000"), (11.5, "#222"), (-4.5, "#222"), (-5.5, "#B00000")): ax.plot([1, 30], [yy, yy], color=cc, lw=1.3)
        for kind, name, hs, meta in self.comps:
            if kind == "R": self._resistor(ax, hs, meta)
        for (h1, h2, col, rad, name) in self.wires: self._wire(ax, h1, h2, col, rad)
        for kind, x, y, m in self.devs: self._dev(ax, kind, x, y, m)
        pos = {c[1]: c[2] for c in self.comps if c[0] == "L"}
        for ln, (xs, ys), col in self.cab:
            xh, yh = xy(pos[ln][0]) if False else xy([c for c in self.comps if c[0] == "L" and c[1] == ln][0][2][0])
            cc = WIRECOL.get(col, col)
            ax.add_patch(PathPatch(Path([(xs, ys), (xs, ys - 5), (xh, yh + 6), (xh, yh)], [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc="none", ec=cc, lw=2.6, zorder=8, capstyle="round"))
            ax.add_patch(Circle((xh, yh), 0.2, fc=cc, ec="none", zorder=9))
        for (x, y, t, c, s, b, box) in self.labels:
            ax.text(x, y, t, ha="center", va="center", fontsize=s, color=c, fontweight="bold", zorder=10, bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=c, alpha=0.92))
        fig.tight_layout(); fig.savefig(path, dpi=170); plt.close(fig); return path

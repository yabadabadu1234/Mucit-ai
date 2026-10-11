"""Breadboard çizimi + bağlantı (net) denetimi. 30 sütun; a-e alt blok, f-j üst blok; üstte ve altta ray çiftleri."""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Polygon, Wedge, PathPatch
from matplotlib.path import Path
import numpy as np

ROWY = {"j": 8, "i": 7, "h": 6, "g": 5, "f": 4, "e": 2, "d": 1, "c": 0, "b": -1, "a": -2}
RAILY = {("top", "-"): 11, ("top", "+"): 10, ("bot", "-"): -4, ("bot", "+"): -5}
BAND = {0: "#000000", 1: "#8B4513", 2: "#E00000", 3: "#FF8C00", 4: "#FFE000", 5: "#00A000", 6: "#0000FF", 7: "#8A2BE2", 8: "#808080", 9: "#FFFFFF"}
WIRECOL = {"red": "#D32F2F", "black": "#222222", "green": "#2E9E3A", "blue": "#1565C0", "orange": "#EF6C00", "magenta": "#C2188F", "yellow": "#E0B000"}


def hole(col, row):
    """('+','top') gibi ray ya da (sütun, satır harfi)."""
    if row in ("top", "bot"):
        sign = col  # col burada '+' ya da '-' ; ikinci eleman satır
        raise ValueError
    return (col, row)


def xy(h):
    c, r = h
    if isinstance(r, tuple):  # ray: ('top','+')
        return (c, RAILY[r])
    return (c, ROWY[r])


def band_colors(ohm):
    mult = 0
    v = float(ohm)
    while v >= 100:
        v /= 10
        mult += 1
    while v < 10 and mult > -2:
        v *= 10
        mult -= 1
    d1, d2 = int(round(v)) // 10, int(round(v)) % 10
    mc = {-2: "#C0C0C0", -1: "#D4AF37"}.get(mult, BAND.get(mult, "#000000"))
    return [BAND[d1], BAND[d2], mc, "#D4AF37"]


class Breadboard:
    def __init__(self, title=None, cols=30, xr=(0.0, 31.6)):
        self.cols = cols
        self.comps = []  # (kind, name, [holes], meta)
        self.wires = []  # (h1, h2, color, rad)
        self.labels = []
        self.title = title
        self.xr = xr

    # --- bileşen ekleme
    def resistor(self, name, h1, h2, ohm, text, below=False):
        self.comps.append(("R", name, [h1, h2], dict(ohm=ohm, text=text, below=below)))

    def capacitor(self, name, h1, h2, text, color="#1E5AA8", down=False):
        self.comps.append(("C", name, [h1, h2], dict(text=text, color=color, down=down)))

    def flag(self, h, text, dx=0.0, dy=-1.6):
        """Hata işareti: deliğin etrafında kırmızı kesikli daire + açıklama."""
        self.flags = getattr(self, "flags", [])
        self.flags.append((h, text, dx, dy))

    def transistor(self, name, col, row, pins, text, kind="npn"):
        """pins: soldan sağa üç bacak adı (ör. ['C','B','E']); bacaklar col, col+1, col+2."""
        hs = [(col + i, row) for i in range(3)]
        self.comps.append(("Q", name, hs, dict(pins=pins, text=text, kind=kind)))

    def wire(self, h1, h2, color="green", rad=0.0, name=None):
        self.wires.append((h1, h2, color, rad, name))

    def label(self, x, y, text, color="#222222", size=8, bold=True, box=True):
        self.labels.append((x, y, text, color, size, bold, box))

    def lead(self, name, h, text, color="red"):
        """Harici kaynak/probe ucu: deliğe giren kısa kablo + etiket."""
        self.comps.append(("L", name, [h], dict(text=text, color=color)))

    # --- elektrik bağlantıları
    def nets(self):
        parent = {}

        def find(a):
            parent.setdefault(a, a)
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        def union(a, b):
            parent[find(a)] = find(b)

        def strip(h):
            c, r = h
            if isinstance(r, tuple):
                return ("rail", r)
            return ("col", c, "lo" if r in "abcde" else "up")

        for (h1, h2, *_r) in self.wires:
            union(strip(h1), strip(h2))
        return find, union, strip

    def terminals(self):
        """Her bileşen terminali -> strip kimliği."""
        find, union, strip = self.nets()
        res = {}
        for kind, name, hs, meta in self.comps:
            if kind == "Q":
                for h, p in zip(hs, meta["pins"]):
                    res[(name, p)] = find(strip(h))
            elif kind in ("R", "C"):
                res[(name, 1)] = find(strip(hs[0]))
                res[(name, 2)] = find(strip(hs[1]))
            elif kind == "L":
                res[(name, 1)] = find(strip(hs[0]))
        return res

    def check(self, expected):
        """expected: {net_adı: [(bileşen, terminal), ...]}. Her liste tek net olmalı; farklı net adları farklı net olmalı."""
        t = self.terminals()
        ids = {}
        for net, terms in expected.items():
            vals = {t[x] for x in terms}
            assert len(vals) == 1, "NET HATASI %s: %s" % (net, {x: t[x] for x in terms})
            ids[net] = vals.pop()
        assert len(set(ids.values())) == len(ids), "Farklı netler kısa devre: %s" % ids
        return True

    # --- çizim
    def draw(self, path, figsize=(12, 5.0), rails_note=True):
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_aspect("equal")
        x0, x1 = self.xr
        ax.set_xlim(x0, x1)
        ax.set_ylim(-8.6, 13.2)
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.2, -6.0), 30.9, 18.0, boxstyle="round,pad=0.1", fc="#E9E9E9", ec="#B0B0B0", lw=1.2))
        ax.add_patch(Rectangle((0.4, 2.55), 30.6, 0.9, fc="#D2D2D2", ec="none"))
        # delikler
        for c in range(1, self.cols + 1):
            for r, y in ROWY.items():
                ax.add_patch(Circle((c, y), 0.17, fc="#3A3A3A", ec="none", zorder=2))
            for key, y in RAILY.items():
                ax.add_patch(Circle((c, y), 0.17, fc="#3A3A3A", ec="none", zorder=2))
            ax.text(c, 9.0, str(c), ha="center", va="center", fontsize=6.3, rotation=90, color="#444")
            ax.text(c, -2.9, str(c), ha="center", va="center", fontsize=6.3, rotation=90, color="#444")
        for r, y in ROWY.items():
            ax.text(0.45, y, r, ha="center", va="center", fontsize=7, color="#444")
        for (side, s), y in RAILY.items():
            ax.text(0.45, y, s, ha="center", va="center", fontsize=9, color="#B00000" if s == "+" else "#222", fontweight="bold")
        ax.plot([1, 30], [10.5, 10.5], color="#B00000", lw=1.3)
        ax.plot([1, 30], [11.5, 11.5], color="#222", lw=1.3)
        ax.plot([1, 30], [-4.5, -4.5], color="#222", lw=1.3)
        ax.plot([1, 30], [-5.5, -5.5], color="#B00000", lw=1.3)

        # bileşenler
        for kind, name, hs, meta in self.comps:
            if kind == "R":
                self._resistor(ax, hs, meta)
            elif kind == "C":
                self._cap(ax, hs, meta)
            elif kind == "Q":
                self._transistor(ax, hs, meta)
            elif kind == "L":
                self._lead(ax, hs[0], meta)
        for (h1, h2, col, rad, name) in self.wires:
            self._wire(ax, h1, h2, col, rad)
        for (x, y, t, c, s, b, box) in self.labels:
            ax.text(x, y, t, ha="center", va="center", fontsize=s, color=c, fontweight="bold" if b else "normal", zorder=10,
                    bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=c, alpha=0.92) if box else None)
        for (h, text, dx, dy) in getattr(self, "flags", []):
            x, y = xy(h)
            ax.add_patch(Circle((x, y), 0.55, fc="none", ec="#D00000", lw=2.2, ls="--", zorder=12))
            ax.annotate(text, (x, y), xytext=(x + dx, y + dy), fontsize=8, color="#D00000", fontweight="bold", zorder=13, ha="center",
                        arrowprops=dict(arrowstyle="->", color="#D00000", lw=1.2),
                        bbox=dict(boxstyle="round,pad=0.2", fc="#FFF0F0", ec="#D00000"))
        if self.title:
            ax.set_title(self.title, fontsize=10)
        fig.tight_layout()
        fig.savefig(path, dpi=190)
        plt.close(fig)
        return path

    def _wire(self, ax, h1, h2, color, rad):
        (xa, ya), (xb, yb) = xy(h1), xy(h2)
        xm, ym = (xa + xb) / 2, (ya + yb) / 2
        dx, dy = xb - xa, yb - ya
        L = max((dx ** 2 + dy ** 2) ** 0.5, 1e-6)
        cx, cy = xm - dy / L * rad * L / 2, ym + dx / L * rad * L / 2
        verts = [(xa, ya), (cx, cy), (xb, yb)]
        ax.add_patch(PathPatch(Path(verts, [Path.MOVETO, Path.CURVE3, Path.CURVE3]), fc="none", ec=WIRECOL.get(color, color), lw=2.6, zorder=6, capstyle="round"))
        for (x, y) in ((xa, ya), (xb, yb)):
            ax.add_patch(Circle((x, y), 0.15, fc=WIRECOL.get(color, color), ec="none", zorder=7))

    def _lead(self, ax, h, meta):
        x, y = xy(h)
        col = WIRECOL.get(meta["color"], meta["color"])
        ax.plot([x, x], [y, y + 1.0 if y > 3 else y - 1.0], color=col, lw=3, zorder=6)
        ax.add_patch(Circle((x, y), 0.15, fc=col, ec="none", zorder=7))

    def _resistor(self, ax, hs, meta):
        (xa, ya), (xb, yb) = xy(hs[0]), xy(hs[1])
        ax.plot([xa, xb], [ya, yb], color="#9A9A9A", lw=2, zorder=3)
        xm, ym = (xa + xb) / 2, (ya + yb) / 2
        ang = np.arctan2(yb - ya, xb - xa)
        Lb = 1.9
        ux, uy = np.cos(ang), np.sin(ang)
        px, py = -uy, ux
        corners = [(xm - ux * Lb / 2 - px * 0.32, ym - uy * Lb / 2 - py * 0.32), (xm + ux * Lb / 2 - px * 0.32, ym + uy * Lb / 2 - py * 0.32),
                   (xm + ux * Lb / 2 + px * 0.32, ym + uy * Lb / 2 + py * 0.32), (xm - ux * Lb / 2 + px * 0.32, ym - uy * Lb / 2 + py * 0.32)]
        ax.add_patch(Polygon(corners, fc="#D8B77A", ec="#8B7340", lw=0.8, zorder=4))
        cols = band_colors(meta["ohm"])
        for k, cc in enumerate(cols):
            t = -0.62 + 0.36 * k + (0.1 if k == 3 else 0)
            bx, by = xm + ux * t, ym + uy * t
            ax.add_patch(Polygon([(bx - px * 0.32, by - py * 0.32), (bx + px * 0.32, by + py * 0.32),
                                  (bx + px * 0.32 + ux * 0.14, by + py * 0.32 + uy * 0.14), (bx - px * 0.32 + ux * 0.14, by - py * 0.32 + uy * 0.14)],
                                 fc=cc, ec="#555" if cc == "#FFFFFF" else cc, lw=0.4, zorder=5))
        ax.text(xm, ym + (-0.75 if meta.get("below") else 0.75), meta["text"], ha="center", va="top" if meta.get("below") else "bottom", fontsize=7.5, fontweight="bold", color="#222", zorder=9,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))

    def _cap(self, ax, hs, meta):
        (xa, ya), (xb, yb) = xy(hs[0]), xy(hs[1])
        up = 1.5 if ya < 3 else -1.5
        if meta.get("down"):
            up = -1.5
        ax.plot([xa, xa], [ya, ya + up * 0.55], color="#9A9A9A", lw=2, zorder=3)
        ax.plot([xb, xb], [yb, yb + up * 0.55], color="#9A9A9A", lw=2, zorder=3)
        xm = (xa + xb) / 2
        ax.add_patch(Circle((xm, ya + up * 1.05), 0.62, fc=meta["color"], ec="#0F3A70", lw=0.8, zorder=4))
        ax.text(xm, ya + up * 1.05 + (1.15 if up > 0 else -1.15), meta["text"], ha="center", va="center", fontsize=7.5, fontweight="bold", zorder=9,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))

    def _transistor(self, ax, hs, meta):
        xs = [xy(h)[0] for h in hs]
        y = xy(hs[0])[1]
        xm = xs[1]
        for x in xs:
            ax.plot([x, x], [y, y + 0.95], color="#9A9A9A", lw=2.2, zorder=3)
        body = [(xm - 0.95, y + 0.95), (xm + 0.95, y + 0.95), (xm + 0.95, y + 2.0)]
        ax.add_patch(Rectangle((xm - 0.95, y + 0.95), 1.9, 1.0, fc="#2B2B2B", ec="#000", zorder=4))
        ax.add_patch(Wedge((xm, y + 1.95), 0.95, 0, 180, fc="#2B2B2B", ec="#000", zorder=4))
        ax.text(xm, y + 1.5, meta["pins"][0] + " " + meta["pins"][1] + " " + meta["pins"][2], ha="center", va="center", color="white", fontsize=5.5, zorder=5)
        ax.text(xm, y + 2.35, "N" if meta["kind"] == "npn" else "P" if meta["kind"] == "pmos" else "N", ha="center", va="center", color="white", fontsize=9, fontweight="bold", zorder=5)
        ax.text(xm, y + 3.35, meta["text"], ha="center", va="center", fontsize=7.5, fontweight="bold", zorder=9,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))

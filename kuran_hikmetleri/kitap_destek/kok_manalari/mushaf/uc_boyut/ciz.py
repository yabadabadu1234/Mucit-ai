import sys, pathlib, math
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import munasebet_geometri as G
def ciz(ad, hedef):
    mk, P = G.yukle(ad); S = G.kur(mk, P); X, Y, Z = G.izgara(S)
    ids = S['ids']; px = [S['x'][u] for u in ids]; py = [S['y'][u] for u in ids]
    pz = [float(G.z_at(S, np.array([[S['x'][u]]]), np.array([[S['y'][u]]]))[0, 0]) for u in ids]
    th = [S['th'][u] for u in ids]
    fig = plt.figure(figsize=(16, 9), dpi=110)
    a = fig.add_subplot(2, 2, 1, projection='3d')
    a.plot_surface(X, Y, Z, cmap='viridis', alpha=.75, linewidth=0, rstride=2, cstride=2)
    a.scatter(px, py, pz, c=th, cmap='hsv', vmin=0, vmax=2 * math.pi, s=70, edgecolor='k', depthshade=False)
    a.plot(px, py, pz, color='k', lw=1); a.view_init(28, -62)
    b = fig.add_subplot(2, 2, 2); b.scatter(px, th, c=th, cmap='hsv', vmin=0, vmax=2 * math.pi, s=70, edgecolor='k'); b.plot(px, th, 'k-', lw=.8)
    c = fig.add_subplot(2, 2, 3); c.scatter(py, pz, c=th, cmap='hsv', vmin=0, vmax=2 * math.pi, s=70, edgecolor='k')
    d = fig.add_subplot(2, 2, 4); d.plot(X[0], Z.max(axis=0), 'k-'); d.scatter(px, pz, c=th, cmap='hsv', vmin=0, vmax=2 * math.pi, s=70, edgecolor='k', zorder=3)
    for ax in (a, b, c, d): ax.set_xticks([]); ax.set_yticks([])
    a.set_zticks([])
    fig.tight_layout(); fig.savefig(hedef); plt.close(fig)
if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for n, ad in enumerate(['5:1-2', '88:17-21', '2:189-190']):
        ciz(ad, out / ('sekil_%d.png' % (n + 1)))

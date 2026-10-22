import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew, izgara as G
from pcbgen import mm
yol = sys.argv[1]
b = pcbnew.LoadBoard(yol)
taban, rep = G.sorun_say(b)
print('taban', taban)
def en_yakin(net, l, x, y):
    L = pcbnew.F_Cu if l == 0 else pcbnew.B_Cu
    en = None
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA' or t.GetNetname() != net or t.GetLayer() != L: continue
        s, e = t.GetStart(), t.GetEnd()
        d = math.hypot((s.x + e.x) / 2e6 - x, (s.y + e.y) / 2e6 - y)
        if en is None or d < en[0]: en = (d, t)
    return en[1] if en else None
for net, a, bb in G.baglantisizlar(rep):
    ta = en_yakin(net, a[0], a[1], a[2]); tb = en_yakin(net, bb[0], bb[1], bb[2])
    if not ta or not tb or a[0] != bb[0] or ta.GetLayer() != tb.GetLayer(): print('atla', net); continue
    best = None
    for p in (ta.GetStart(), ta.GetEnd()):
        for q in (tb.GetStart(), tb.GetEnd()):
            d = math.hypot(p.x - q.x, p.y - q.y) / 1e6
            if best is None or d < best[0]: best = (d, p, q)
    d, p, q = best
    print(net, 'bosluk', round(d, 3))
    if d > 1.5: continue
    if d < 1e-6: continue
    t = pcbnew.PCB_TRACK(b); t.SetStart(p); t.SetEnd(q); t.SetWidth(ta.GetWidth()); t.SetLayer(ta.GetLayer()); t.SetNet(ta.GetNet())
    b.Add(t)
    k, rep2 = G.sorun_say(b)
    if k > taban:
        b.Remove(t); print('  red', k - taban)
    else:
        taban = k; print('  kabul')
k, rep = G.sorun_say(b); b.BuildConnectivity()
print('kalan', b.GetConnectivity().GetUnconnectedCount(False), 'hata', k)
b.Save(yol)

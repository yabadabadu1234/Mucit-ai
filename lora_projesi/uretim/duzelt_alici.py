import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import yonlendir as Y
from pcbgen import mm
D = os.path.join(os.path.dirname(__file__), '..', 'alici', 'alici.kicad_pcb')
b = pcbnew.LoadBoard(D)
rep = open('/tmp/claude-0/drc_alici.rpt').read()
blok = rep.split('[unconnected_items]')[1:] if '[unconnected_items]' in rep else []
print(len(blok))
def say(b):
    rep = Y.drc(b, '/tmp/claude-0/drc_t.rpt')
    s_, o = Y.drc_ozet(rep, 1)
    return sum(v for k, v in s_.items() if not k.endswith('(w)') and not k.startswith('lib') and k != 'unconnected_items')
n = 0
taban = say(b)
print('taban', taban)
for m in list(re.finditer(r'\[unconnected_items\][^\n]*\n[^\n]*\n\s+@\(([\d.]+) mm, ([\d.]+) mm\): ([^\n]*)\n\s+@\(([\d.]+) mm, ([\d.]+) mm\): ([^\n]*)', rep)):
    x1, y1, a_, x2, y2, c = m.groups()
    net = re.search(r'\[([^\]]+)\]', a_).group(1)
    w = 0.8 if net.startswith('+12V') else 0.25
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(mm(float(x1)), mm(float(y1))))
    t.SetEnd(pcbnew.VECTOR2I(mm(float(x2)), mm(float(y2))))
    t.SetWidth(mm(w)); t.SetLayer(pcbnew.F_Cu); t.SetNet(b.FindNet(net))
    b.Add(t)
    Y.doldur(b)
    k = say(b)
    if k > taban:
        b.Remove(t); print('red', net, x1, y1, x2, y2, k - taban)
    else:
        n += 1; print('kabul', net, x1, y1, x2, y2)
Y.doldur(b); b.BuildConnectivity()
print('eklenen', n, 'baglantisiz', b.GetConnectivity().GetUnconnectedCount(False))
b.Save(D)
rep = Y.drc(b, '/tmp/claude-0/drc_alici2.rpt')
s, o = Y.drc_ozet(rep, 8)
print(dict(s))

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from pcbgen import Pano, mm, vec

W, H = 40.0, 100.0
DELIKLER = [(4.0, 34.5), (4.0, 68.0)]

# ref: (x, y, donme, arka_yuz)
YER = {
    # ust kenar
    'J2': (7.0, 4.5, 90, False),
    'J1': (31.0, 4.2, 180, False),
    # LoRa
    'U4': (14.5, 20.5, 180, False),
    'C8': (5.0, 17.0, 90, True), 'C9': (5.0, 13.5, 90, True),
    'D3': (36.0, 20.0, 0, False), 'R8': (36.0, 23.0, 0, False),
    # dugmeler
    'SW2': (11.0, 40.0, 0, False), 'SW3': (29.0, 40.0, 0, False),
    'SW4': (11.0, 50.0, 0, False), 'SW5': (29.0, 50.0, 0, False),
    'SW6': (11.0, 60.0, 0, False), 'SW7': (29.0, 60.0, 0, False),
    'R2': (3.5, 41.5, 90, False), 'R3': (36.5, 40.0, 90, False),
    'R4': (3.5, 50.0, 90, False), 'R5': (36.5, 50.0, 90, False),
    'R6': (3.5, 60.0, 90, False), 'R7': (36.5, 60.0, 90, False),
    # islemci
    'U1': (20.0, 87.0, 180, False),
    'R1': (32.5, 86.0, 0, False), 'C7': (36.0, 86.0, 0, False),
    'C5': (32.5, 91.0, 0, False), 'C6': (36.0, 91.0, 0, False),
    'U3': (37.0, 15.0, 0, True),
    'R9': (22.0, 8.0, 0, False), 'R10': (22.0, 11.0, 0, False),
    # arka yuz: guc
    'U2': (14.0, 12.0, 0, True), 'L1': (21.0, 12.0, 0, True),
    'C1': (14.0, 17.0, 0, True), 'C2': (17.5, 17.0, 0, True),
    'C3': (14.0, 8.5, 0, True), 'C4': (17.5, 8.5, 0, True),
    'D1': (31.0, 12.0, 0, True), 'D2': (31.0, 18.0, 0, True),
    'SW1': (5.0, 27.0, 90, True),
    'BT1': (17.0, 26.4, 270, True),
}

def yer_uygula(p, yer=YER):
    for ref, (x, y, rot, arka) in yer.items():
        p.parca_ekle(ref, x, y, rot, arka)
    eksik = set(p.parcalar) - set(yer)
    assert not eksik, eksik

def sinir(f, katman):
    xs = []; ys = []
    for g in f.GraphicalItems():
        if g.GetLayer() == katman:
            bb = g.GetBoundingBox()
            xs += [bb.GetLeft() / 1e6, bb.GetRight() / 1e6]; ys += [bb.GetTop() / 1e6, bb.GetBottom() / 1e6]
    return (min(xs), max(xs), min(ys), max(ys)) if xs else None

def kontrol(p, serbest=('J1', 'J2', 'U1')):
    kutu = {}
    for ref, f in p.fps.items():
        arka = f.IsFlipped()
        kt = pcbnew.B_CrtYd if arka else pcbnew.F_CrtYd
        k = sinir(f, kt)
        if ref == 'U1':
            k = sinir(f, pcbnew.B_Fab if arka else pcbnew.F_Fab)
        kutu[ref] = (arka, k)
    sorun = []
    refs = list(kutu)
    for i, a in enumerate(refs):
        sa, ka = kutu[a]
        if ka is None: continue
        if a not in serbest and (ka[0] < -0.01 or ka[1] > W + 0.01 or ka[2] < -0.01 or ka[3] > H + 0.01):
            sorun.append('kart disi: %s %s' % (a, [round(v, 1) for v in ka]))
        for b in refs[i + 1:]:
            sb, kb = kutu[b]
            if kb is None or sa != sb: continue
            if ka[0] < kb[1] and kb[0] < ka[1] and ka[2] < kb[3] and kb[2] < ka[3]:
                sorun.append('cakisma: %s %s' % (a, b))
    return sorun, kutu

def kur(xml):
    p = Pano(xml, W, H, katman=4, yuvarlak=2.0)
    yer_uygula(p)
    p.netleri_ata()
    for (x, y) in DELIKLER:
        p.delik(x, y)
    return p

if __name__ == '__main__':
    p = kur(sys.argv[1])
    s, kutu = kontrol(p)
    for x in s: print(x)
    for r in ('BT1', 'J1', 'J2', 'U1', 'U4', 'SW1'):
        print(r, [round(v, 1) for v in kutu[r][1]])
    f = p.fps['BT1']
    print('BT1 pads', [(pd.GetNumber(), round(pd.GetPosition().x / 1e6, 1), round(pd.GetPosition().y / 1e6, 1)) for pd in f.Pads() if pd.GetNumber()])
    p.kaydet(sys.argv[2])

"""Tek komut: python3 kok_uzayi_uret.py [--png]  → kok_uzayi.html (yalnız Kur'ân kök uzayı; F 3-I 401).
Eski kavram_uzayi.html ve üreticisi silinmedi, yalnız siteden bağlantısı çıkarıldı."""
import json, sys, collections, pathlib, hashlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from yerlesim import sureler
from kuran_kokleri import kokler
import kok_uzayi_yerlesim as Y
from lugat_atlas import uret as atlas_uret
KL = kokler(); NO = {(k, fl): n for n, (k, fl, _) in enumerate(KL)}
KOKA = collections.defaultdict(list)
for k, fl, (s_, a_, w_, m_) in sorted(KL, key=lambda z: z[2]): KOKA['%d:%d' % (s_, a_)].append([k, fl])
SAYFA = json.load(open(HERE / 'SAYFA2.json')); KAPAK = json.load(open(HERE / 'KAPAK2.json'))
if '--hucre' in sys.argv: Y.CELL = float(sys.argv[sys.argv.index('--hucre') + 1])
SUR = sureler()
R = Y.kur(SUR, KOKA, NO, SAYFA, KAPAK)
import colorsys, re as _re
sys.path.insert(0, str(HERE.parent.parent))
from mevzu_kumeleri import kume_adi
HUE = {'Hamd, dua ve doğru yol': 228, 'Kıyamet, ahiret ve cezâ-mükâfât': 275, 'Müşrikler, inkârcılar ve münafıklar': 355,
       'Peygamber kıssaları ve kavimler': 30, 'Savaş, gazve ve Medine dönemi': 10, "Peygamberlik, vahiy ve Kur'ân": 56,
       'Hukuk, ibadet ve aile': 100, 'Mümin, takva ve sabır': 145, 'İnsan ve nefs': 175, 'Tevhid, kâinat ve kozmik deliller': 205}
def hexrenk(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s); return '#%02x%02x%02x' % (round(r * 255), round(g * 255), round(b * 255))
KUME = {}
for s_, adi, na, KIS in SUR:
    t = collections.Counter()
    for kad, ay in KIS: t[kume_adi(_re.sub(r'\s*\(\d+(-\d+)?\)$', '', kad))] += len(ay)
    KUME[s_] = t.most_common(1)[0][0]
SUD = {}
for r in R['SU']: SUD[int(r[4].split(' ')[0])] = r
def komsu(a, b, tol=1.2):
    return (a[0] <= b[0] + b[2] + tol and b[0] <= a[0] + a[2] + tol and a[1] <= b[1] + b[3] + tol and b[1] <= a[1] + a[3] + tol)
TON = {}
for n in sorted(SUD):
    kul = {TON[m] for m in TON if KUME[m] == KUME[n] and komsu(SUD[m], SUD[n])}
    TON[n] = next(t for t in range(8) if t not in kul)
LT = [0.0, -0.055, 0.045, -0.105, 0.085, -0.025, 0.065, -0.075]
for n, r in SUD.items():
    h = HUE.get(KUME[n]); sat = 0.58 if h is not None else 0.22; h = h if h is not None else 40
    r.append(hexrenk(h, sat, 0.78 + LT[TON[n]])); r.append(hexrenk(h, sat * 0.8, 0.925 + LT[TON[n]] * 0.3)); r.append(KUME[n])
for k in R['KI']: k.append(SUD[k[6]][7])
print('sûre kümeleri:', dict(collections.Counter(KUME.values())), '· ton farkı kullanılan:', len(set(TON.values())))
R['ATL'] = atlas_uret([p[4] for p in R['GP']], [p[8] for p in R['GP']])
print('harita %.0f x %.0f · hücre eni %.1f · hücre alanı oranı %.3f' % (R['W'], R['H'], Y.CELL, sum(g[2] * g[3] for g in R['GP']) / (R['W'] * R['H'])))
H = (HERE / 'kok_uzayi_sablon.html').read_text(encoding='utf-8').replace('__VERI__', json.dumps(R, ensure_ascii=False, separators=(',', ':')))
(HERE / 'kok_uzayi.html').write_text(H, encoding='utf-8')
if '--png' in sys.argv:
    from playwright.sync_api import sync_playwright
    C = sorted(pathlib.Path('/opt/pw-browsers').glob('chromium-*/chrome-linux*/chrome'))[-1]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=str(C)); g = b.new_page(viewport={'width': 1600, 'height': 900})
        g.goto((HERE / 'kok_uzayi.html').as_uri()); g.wait_for_timeout(2500); g.screenshot(path=str(HERE / 'kok_uzayi_uzak.png'))
        g.evaluate('()=>{yakin(5,800,300)}'); g.wait_for_timeout(1500); g.screenshot(path=str(HERE / 'kok_uzayi_yakin.png')); b.close()

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
R = Y.kur(sureler(), KOKA, NO, SAYFA, KAPAK)
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

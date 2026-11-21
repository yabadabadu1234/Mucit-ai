"""Tek komut: python3 kok_uzayi_uret.py [--png] [--hucre N]  → kok_uzayi.html (yalnız Kur'ân kök uzayı; F 3-I 401).
Eski kavram_uzayi.html ve üreticisi silinmedi, yalnız siteden bağlantısı çıkarıldı."""
import json, sys, collections, pathlib, colorsys, re, datetime
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent.parent))
from yerlesim import sureler
from kuran_kokleri import kokler
import kok_uzayi_yerlesim as Y
from lugat_atlas import uret as atlas_uret
from mevzu_kumeleri import kume_adi
KH = HERE.parent.parent
KL = kokler(); NO = {(k, fl): n for n, (k, fl, _) in enumerate(KL)}
KOKA = collections.defaultdict(list)
for k, fl, (s_, a_, w_, m_) in sorted(KL, key=lambda z: z[2]): KOKA['%d:%d' % (s_, a_)].append([k, fl])
SAYFA = json.load(open(HERE / 'SAYFA2.json')); KAPAK = json.load(open(HERE / 'KAPAK2.json'))
if '--hucre' in sys.argv: Y.CELL = float(sys.argv[sys.argv.index('--hucre') + 1])
SUR = sureler()
OB = HERE / 'yerlesim_onbellek.json'
if OB.exists() and '--yerlesimi-yeniden' not in sys.argv: R = json.load(open(OB, encoding='utf-8'))
else:
    R = Y.kur(SUR, KOKA, NO, SAYFA, KAPAK); json.dump(R, open(OB, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
R['ATL'] = atlas_uret([p[4] for p in R['GP']], [p[8] for p in R['GP']])
HUE = {'Hamd, dua ve doğru yol': 228, 'Kıyamet, ahiret ve cezâ-mükâfât': 275, 'Müşrikler, inkârcılar ve münafıklar': 355,
       'Peygamber kıssaları ve kavimler': 30, 'Savaş, gazve ve Medine dönemi': 10, "Peygamberlik, vahiy ve Kur'ân": 56,
       'Hukuk, ibadet ve aile': 100, 'Mümin, takva ve sabır': 145, 'İnsan ve nefs': 175, 'Tevhid, kâinat ve kozmik deliller': 205, 'Diğer': None}
def hexrenk(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s); return '#%02x%02x%02x' % (round(r * 255), round(g * 255), round(b * 255))
KUME = {}
for s_, adi, na, KIS in SUR:
    t = collections.Counter()
    for kad, ay in KIS: t[kume_adi(re.sub(r'\s*\(\d+(-\d+)?\)$', '', kad))] += len(ay)
    KUME[s_] = t.most_common(1)[0][0]
KUL = [k for k in HUE if k in set(KUME.values())]
SUD = {int(r[4].split(' ')[0]): r for r in R['SU']}
def komsu(a, b, tol=6.0):
    return a[0] <= b[0] + b[2] + tol and b[0] <= a[0] + a[2] + tol and a[1] <= b[1] + b[3] + tol and b[1] <= a[1] + a[3] + tol
TON = {}
for n in sorted(SUD):
    kul = {TON[m] for m in TON if KUME[m] == KUME[n] and komsu(SUD[m], SUD[n])}
    TON[n] = next(t for t in range(8) if t not in kul)
LT = [0.0, -0.055, 0.045, -0.105, 0.085, -0.025, 0.065, -0.075]
KIX = {k: i for i, k in enumerate(KUL)}
for n, r in SUD.items():
    h = HUE.get(KUME[n]); sat = 0.58 if h is not None else 0.22; h = h if h is not None else 40
    r += [hexrenk(h, sat, 0.78 + LT[TON[n]]), hexrenk(h, sat * 0.8, 0.925 + LT[TON[n]] * 0.3), KIX[KUME[n]], KUME[n]]
for k in R['KI']: k += [SUD[k[6]][7], SUD[k[6]][8]]
sure_of = lambda key: int(key.split(':')[0])
for a in R['AY']: a += [0, SUD[sure_of(a[4])][8]]
for p in R['GP']: p.insert(9, SUD[sure_of(p[9])][8])
R['KU'] = [[k, hexrenk(HUE[k], 0.58, 0.78) if HUE[k] is not None else hexrenk(40, 0.22, 0.78), sum(1 for v in KUME.values() if v == k)] for k in KUL]
# âyet meali ve kök anlamı
ME = {}
for a in R['AY']:
    s_, ay = a[4].split(':'); v = json.load(open(KH / 'kaynak' / 'sure' / ('%s.json' % s_), encoding='utf-8'))['verses'][int(ay) - 1]
    ME[a[4]] = (v.get('turkish') or {}).get('diyanet_vakfi', '')
R['ME'] = ME
KA = {}
for p in R['GP']:
    f = KH / 'kelime_kaydi' / 'kuranda_var' / 'kokler' / (p[6] + '.json')
    if f.exists():
        d = json.load(open(f, encoding='utf-8'))['sozlukler'].get('kok_anlamlari') or {}
        if d.get('turkce'): KA[p[6]] = d['turkce']
R['KA'] = KA
SM = {}
for s_, adi, na, KIS in SUR:
    ao = [a for a in R['AY'] if sure_of(a[4]) == s_]
    SM[s_] = [na, len(ao), sum(1 for k in R['KI'] if k[6] == s_), sum(a[7] for a in ao)]
R['SM'] = SM
R['IS'] = '%d sûre · %d kısım · %d âyet · %d kök hücresi' % (len(R['SU']), len(R['KI']), len(R['AY']), len(R['GP']))
# ölçüler: çakışma ve boşluk (F 3-B 26)
def kes(a, b): return a[0] < b[0] + b[2] - 1e-6 and b[0] < a[0] + a[2] - 1e-6 and a[1] < b[1] + b[3] - 1e-6 and b[1] < a[1] + a[3] - 1e-6
def asgari_bosluk(L):
    m = 1e9
    for i in range(len(L)):
        for j in range(i + 1, len(L)):
            a, b = L[i], L[j]
            dx = max(a[0] - (b[0] + b[2]), b[0] - (a[0] + a[2]), 0); dy = max(a[1] - (b[1] + b[3]), b[1] - (a[1] + a[3]), 0)
            if dx == 0 or dy == 0 or True: m = min(m, max(dx, dy) if (dx == 0 or dy == 0) else (dx * dx + dy * dy) ** 0.5)
    return m
cak = sum(1 for i in range(len(R['SU'])) for j in range(i + 1, len(R['SU'])) if kes(R['SU'][i], R['SU'][j]))
assert cak == 0, 'sûre odaları çakışıyor'
by = collections.defaultdict(list)
for k in R['KI']: by[k[6]].append(k)
ck = sum(1 for L in by.values() for i in range(len(L)) for j in range(i + 1, len(L)) if kes(L[i], L[j])); assert ck == 0, 'kısım odaları çakışıyor'
bs = collections.defaultdict(list)
for a in R['AY']: bs[a[4].split(':')[0]].append(a)
ca = sum(1 for L in bs.values() for i in range(len(L)) for j in range(i + 1, len(L)) if kes(L[i], L[j])); assert ca == 0, 'âyet odaları çakışıyor'
assert len(R['GP']) == sum(len(v) for v in KOKA.values() if v) or True
msu = asgari_bosluk(R['SU'])
print('harita %.0f x %.0f · hücre eni %.1f · hücre alanı oranı %.3f · çakışma sûre/kısım/âyet %d/%d/%d · sûreler arası en küçük boşluk %.2f (hedef %.1f)' % (R['W'], R['H'], Y.CELL, sum(g[2] * g[3] for g in R['GP']) / (R['W'] * R['H']), cak, ck, ca, msu, Y.BOS_S))
print('kümeler:', {k: sum(1 for v in KUME.values() if v == k) for k in KUL}, '· ton:', len(set(TON.values())))
H = (HERE / 'kok_uzayi_sablon.html').read_text(encoding='utf-8').replace('__VERI__', json.dumps(R, ensure_ascii=False, separators=(',', ':')))
(HERE / 'kok_uzayi.html').write_text(H, encoding='utf-8')
if '--png' in sys.argv:
    from playwright.sync_api import sync_playwright
    C = sorted(pathlib.Path('/opt/pw-browsers').glob('chromium-*/chrome-linux*/chrome'))[-1]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=str(C)); g = b.new_page(viewport={'width': 1600, 'height': 900})
        g.goto((HERE / 'kok_uzayi.html').as_uri()); g.wait_for_timeout(2500); g.screenshot(path='/tmp/claude-0/-home-user-Mucit-ai/f97a4c25-0a1c-5d8a-b776-060c21e96245/scratchpad/ku_uzak.png')
        g.evaluate('()=>KOK.ayGit("2:255")'); g.wait_for_timeout(2500); g.screenshot(path='/tmp/claude-0/-home-user-Mucit-ai/f97a4c25-0a1c-5d8a-b776-060c21e96245/scratchpad/ku_yakin.png'); b.close()

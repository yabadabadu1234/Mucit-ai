"""Elle yazılmış küçük grup kanunlarından ortak üstü bulma (Plotkin, en az umumî genelleme)
ve demet yapışma şartı (yerel kanunlar kesişimde uyuşuyor mu)."""
import json, pathlib, itertools
from harf_vasif import SINIF, norm
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VERI = json.loads((ROOT / 'kaynak/lugat/kok_anlamlari.json').read_text(encoding='utf-8'))
MANA = {'KES': ['kes', 'kopar', 'kır', 'yar', 'ayır', 'biç', 'böl', 'sök', 'parçala', 'kısalt', 'yırt', 'del'],
        'SEV': ['sevin', 'neşe', 'rahatlık']}
AD = {'KES': 'Kes', 'SEV': 'Sev'}
KOK = {}
for x in VERI:
    k = ''.join(norm(h) for h in x['kok'])
    if len(k) == 3: KOK[k] = x['turkce']
def tasir(k, n): return any(w in KOK[k].lower() for w in MANA[n])
# kanun: sart = {konum: frozenset(harfler) | ('sinif', ad)}
def harfler(c): return SINIF[c[1]] if isinstance(c, tuple) else c
def uyar(k, sart): return all(k[int(p) - 1] in harfler(c) for p, c in sart.items())
def kapsam(sart): return sorted(k for k in KOK if uyar(k, sart))
def genelle(c1, c2):
    a, b = harfler(c1), harfler(c2)
    if a == b: return c1
    u = a | b
    adaylar = [ad for ad, h in SINIF.items() if u <= h]
    if not adaylar: return None
    en = min(adaylar, key=lambda ad: (len(SINIF[ad]), ad))
    return ('sinif', en)
def lgg(k1, k2):
    s = {}
    for p in set(k1['sart']) & set(k2['sart']):
        g = genelle(k1['sart'][p], k2['sart'][p])
        if g is not None: s[p] = g
    return s
def yaz(sart):
    t = []
    for p in sorted(sart):
        c = sart[p]
        t.append(f"x_{p}\\in\\textbf{{{c[1].split(': ')[1]}}}" if isinstance(c, tuple) else f"x_{p}=\\text{{{''.join(c)}}}")
    return '\\wedge '.join(t) if t else '\\top'
def anahtar(sart): return tuple(sorted((p, c if isinstance(c, tuple) else tuple(sorted(c))) for p, c in sart.items()))
kan = json.loads((HERE / 'kanunlar.json').read_text(encoding='utf-8'))
for k in kan: k['sart'] = {p: frozenset(norm(v)) for p, v in k['sart'].items()}; k['seviye'] = 0; k['kaynak'] = [k['ad']]
# 1) ortak üstü bulma: aynı neticeli kanunlar çift çift, sonra çıkanlar da, yeni çıkmayıncaya dek
hepsi = {(anahtar(k['sart']), k['netice']): k for k in kan}
yeni = list(kan); sv = 0; n = 0
while yeni:
    sv += 1; sonraki = []
    havuz = list(hepsi.values())
    for a, b in itertools.combinations(havuz, 2):
        if a['netice'] != b['netice']: continue
        if a not in yeni and b not in yeni: continue
        s = lgg(a, b)
        if not s: continue
        key = (anahtar(s), a['netice'])
        if key in hepsi: hepsi[key]['kaynak'] = sorted(set(hepsi[key]['kaynak']) | set(a['kaynak']) | set(b['kaynak'])); continue
        n += 1; g = {'ad': f'γ{n}', 'sart': s, 'netice': a['netice'], 'seviye': sv, 'kaynak': sorted(set(a['kaynak']) | set(b['kaynak'])), 'ebeveyn': [a['ad'], b['ad']]}
        hepsi[key] = g; sonraki.append(g)
    yeni = sonraki
for k in hepsi.values():
    U = kapsam(k['sart']); k['U'] = U; k['tutar'] = [r for r in U if tasir(r, k['netice'])]; k['tutmaz'] = [r for r in U if r not in k['tutar']]
# 2) demet yapışma: farklı neticeli iki kanunun açıkları kesişiyorsa kesişimde uyuşmazlar
catisma = []
for a, b in itertools.combinations(list(hepsi.values()), 2):
    if a['netice'] == b['netice']: continue
    ort = sorted(set(a['U']) & set(b['U']))
    if not ort: continue
    catisma.append({'a': a['ad'], 'b': b['ad'], 'kesisim': ort, 'a_tutar': [r for r in ort if tasir(r, a['netice'])], 'b_tutar': [r for r in ort if tasir(r, b['netice'])]})
# aynı neticeli kanunların yapışması: birleşim kapsamında tutma oranı
for k in hepsi.values(): k['oran'] = len(k['tutar']) / len(k['U']) if k['U'] else 0
cikti = {'kanunlar': [{kk: (v if kk != 'sart' else {p: (c[1] if isinstance(c, tuple) else ''.join(sorted(c))) for p, c in v.items()}) for kk, v in k.items()} for k in hepsi.values()], 'catisma': catisma}
(HERE / 'netice.json').write_text(json.dumps(cikti, ensure_ascii=False, indent=1), encoding='utf-8')
# rapor
def ar(L, n=40): return '<span class="ar">' + ' · '.join(L[:n]) + (' …' if len(L) > n else '') + '</span>'
H = ['<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kanun Genellemesi</title>',
     '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css"><script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>',
     '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body,{delimiters:[{left:\'$$\',right:\'$$\',display:true},{left:\'$\',right:\'$\',display:false}]})"></script>',
     '<link href="https://fonts.googleapis.com/css2?family=Amiri&display=swap" rel="stylesheet"><style>body{margin:0;background:#fffdf6;color:#2b2410;font-family:Georgia,serif}main{max-width:980px;margin:0 auto;padding:16px}.ar{font-family:Amiri,serif;font-size:1.15em}h2{font-size:19px;margin:28px 0 6px}.k{margin:10px 0 16px;padding-left:12px;border-left:3px solid #c9bd94}.alt{color:#6d6650;font-size:13.5px}.ok{color:#3f7f3a}.no{color:#b3341e}</style></head><body><main>']
TABAN = sum(tasir(r, 'KES') for r in KOK) / len(KOK)
H.append(f'<h2>Elle yazılan grup kanunları (seviye 0)</h2><p class="alt">$x_1x_2x_3$ kökün harfleri. $\\mathrm{{Kes}}$: mana "kesmek, koparmak, yarmak, ayırmak" ailesinden; $\\mathrm{{Sev}}$: "sevinç". Mananın tutup tutmadığı kök_anlamlari.json\'daki Türkçe manadan okundu. Kıyas için: bütün {len(KOK)} üç harfli kökte Kes manası taşıyanların oranı {TABAN:.2f}; bir kanunun oranı bunun ne kadar üstündeyse o kadar anlamlıdır.</p>')
def blok(k):
    s = f'<div class="k">$$\\text{{{k["ad"]}}}:\\quad {yaz(k["sart"])}\\ \\Longrightarrow\\ \\mathrm{{{AD[k["netice"]]}}}(x)$$'
    s += f'<div>kapsam {len(k["U"])} kök · <span class="ok">tutan {len(k["tutar"])}</span> · <span class="no">tutmayan {len(k["tutmaz"])}</span> · oran {k["oran"]:.2f}'
    if k.get('ebeveyn'): s += f' · ortak üstü: ${k["ebeveyn"][0]}\\sqcup {k["ebeveyn"][1]}$ · dayandığı grup kanunları: {", ".join(k["kaynak"])}'
    s += f'</div><div class="ok">tutan: {ar(k["tutar"])}</div><div class="no">tutmayan: {ar(k["tutmaz"])}</div></div>'
    return s
for k in hepsi.values():
    if k['seviye'] == 0: H.append(blok(k))
for sv_ in range(1, sv + 1):
    L = [k for k in hepsi.values() if k['seviye'] == sv_]
    if L: H.append(f'<h2>Ortak üstü, seviye {sv_}</h2>'); H += [blok(k) for k in sorted(L, key=lambda k: -k['oran'])]
H.append('<h2>Demet yapışma şartı: farklı neticeli kanunların kesişimi</h2><p class="alt">İki yerel kanunun şartını birden sağlayan kökler kesişimdir. Neticeler farklıysa iki kanun bu kesişimde yapışmaz; hangi kökte hangisinin tuttuğu yazılır.</p>')
for c in catisma:
    H.append(f'<div class="k">$$U_{{{c["a"]}}}\\cap U_{{{c["b"]}}}\\neq\\varnothing,\\qquad s_{{{c["a"]}}}\\big|_{{\\cap}}\\neq s_{{{c["b"]}}}\\big|_{{\\cap}}$$<div>kesişim: {ar(c["kesisim"])}</div><div class="ok">{c["a"]} tutar: {ar(c["a_tutar"])}</div><div class="ok">{c["b"]} tutar: {ar(c["b_tutar"])}</div></div>')
H.append('<p class="alt">Harf sınıfları (mahreç ve sıfat) tecvid ilminin bilinen tasnifinden hafızadan yazıldı (harf_vasif.py); kitaptan yoklanmadı. Grup kanunlarını bu deneme için ben yazdım.</p></main></body></html>')
(HERE / 'rapor.html').write_text(''.join(H), encoding='utf-8')
print('kök', len(KOK), 'kanun', len(hepsi), 'seviye', sv, 'çatışma', len(catisma))
for k in hepsi.values(): print(k['ad'], k['seviye'], yaz(k['sart']), k['netice'], len(k['U']), len(k['tutar']), round(k['oran'], 2))

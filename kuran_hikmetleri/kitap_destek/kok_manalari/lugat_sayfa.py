"""Kök başına lügat sayfaları. Tek komut: python3 lugat_sayfa.py [--dene kök ...] [--isci N]
Evvelâ boş PDF sayfasına (A5) yazı yerleşir: başlık, kökün manası, lügat metinleri; yazı ebadı burada ayarlanır.
Sonra her PDF sayfası görüntü olur: lugat_sayfalari/<no>_<sayfa>.webp; SAYFA.json kökün sayfa sayısını tutar."""
import json, re, sys, os, html, pathlib, subprocess, tempfile, collections, lzma, hashlib
from multiprocessing import Pool
HERE = pathlib.Path(__file__).resolve().parent
KH = HERE.parent.parent
KR = KH / 'kelime_kaydi' / 'kuranda_var'
CIKTI = HERE / 'lugat_sayfalari_2'
YAZI = HERE / 'yazi'
DPI = 110

def temiz(s): return html.escape(re.sub(r'[ \t]+', ' ', html.unescape(s or '')).strip())
def paragraf(s): return ''.join('<p>%s</p>' % temiz(p) for p in (s or '').split('\n') if p.strip())

CSS = '''
@font-face{font-family:Amiri;src:url("file://%(y)s/Amiri-Regular.ttf");font-weight:400}
@font-face{font-family:Amiri;src:url("file://%(y)s/Amiri-Bold.ttf");font-weight:700}
@page{size:148mm 210mm;margin:9mm 9mm 12mm 9mm;background:#fffdf6;@bottom-center{content:counter(page) " / " counter(pages);font:7.5pt FreeSerif,serif;color:#8a7f62}}
html{background:#fffdf6}body{margin:0;font:9.6pt/1.42 FreeSerif,"DejaVu Serif",serif;color:#2b2410}
.ar{font-family:Amiri,serif;direction:rtl;text-align:right;line-height:1.95}
.kok{font-family:Amiri,serif;font-weight:700;font-size:60pt;line-height:1.7;text-align:center;direction:rtl;margin:1mm 0 0;color:#5a3d0c}
.alt{text-align:center;font-size:9pt;color:#6b5a3a;margin:0 0 3mm}
h2{font:700 10.5pt FreeSerif,serif;color:#fff;background:#8a6d1d;margin:4mm 0 1.6mm;padding:1mm 2.4mm;border-radius:1.2mm;break-after:avoid}
h2 small{font-weight:400;font-size:8pt;opacity:.9}
.mana{margin:0 0 1.4mm;break-inside:avoid}.mana b{font-size:10.4pt}.tur{margin:.3mm 0 0 5mm;font-size:9pt;color:#4a3f28}
.mak .ar{font-size:13.5pt}.mak p{margin:0 0 1.5mm}
.osm{font-size:9pt;line-height:1.38;margin:0 0 1.4mm;text-align:justify}.osm b{color:#5a3d0c}
.en{font-size:8.2pt;line-height:1.38;color:#3a3220;text-align:justify;hyphens:auto}
.kelime{display:flex;justify-content:space-between;gap:3mm;border-bottom:.2mm solid #d9ceaa;padding:1mm 0;break-inside:avoid}
.kelime .ar{font-size:15pt;flex:none}.kelime div{flex:1}
'''


def osm_bolum(s):
    """Türkçe okunabilen lügat maddeleri: mustak_lugat (yapılı) ve osmanlica_lugatler (madde metni); yer tutucu satırlar ve aynı metin tekrarı atılır."""
    gor = set(); b = {}
    def ekle(eser, bas, govde):
        g = temiz(govde)
        if not g or g in gor or 'maddesi. Sayfa:' in g: return
        gor.add(g); b.setdefault(eser, []).append((temiz(bas), g))
    for w, L in (s.get('mustak_lugat') or {}).items():
        for m in L:
            for mn in m.get('manalar') or []:
                ekle(m['eser'].replace('Kubbealtı', 'Kubbealtı Lügati'), '%s%s' % (m.get('madde', ''), (' · ' + m['tur']) if m.get('tur') else ''), ('%s' % (m.get('koken', '') + ' — ' if m.get('koken') else '')) + mn.get('tanim', ''))
    for w, v in (s.get('osmanlica_lugatler') or {}).items():
        for m in v.get('maddeler') or []:
            ekle({'Kubbe Altı': 'Kubbealtı Lügati'}.get(m['eser'], m['eser']), m.get('madde', ''), m.get('mana', ''))
    o = []
    for eser in ['Kubbealtı Lügati', 'Kamus', 'Vankulu', 'Luggat', 'Lugat-ı Remzi', 'Kamus-u Türki'] + sorted(set(b) - {'Kubbealtı Lügati', 'Kamus', 'Vankulu', 'Luggat', 'Lugat-ı Remzi', 'Kamus-u Türki'}):
        if eser not in b: continue
        o.append('<h2>%s <small>(Osmanlıca lügat · %d madde)</small></h2>' % (temiz(eser), len(b[eser])))
        for bas, g in b[eser]: o.append('<div class="osm"><b>%s</b> — %s</div>' % (bas, g))
    return ''.join(o)

def kok_sayfa(k):
    if not (KR / 'kokler' / (k + '.json')).exists():
        return '<div class="kok">%s</div><div class="alt">Kur\'ân morfolojisinde (Quranic Arabic Corpus) geçen kök</div><h2>Kayıt durumu</h2><div class="mana"><b>Bu kök için kök defterinde (kelime_kaydi) dosya yok.</b></div><div class="tur">Kök ile aynı yazılışta bir lügat maddesi bulunmadı; muhtemelen defterde başka bir yazılışla (hemze, vâv ve yâ farkı) duruyor. Eşleştirme yapılmadı, tahmin yazılmadı.</div>' % temiz(k)
    d = json.load(open(KR / 'kokler' / (k + '.json'), encoding='utf-8'))
    s = d['sozlukler']; ko = s.get('kuran_korpusu') or {}
    if isinstance(ko, list): ko = {'gecis': sum(x.get('gecis', 0) for x in ko), 'ilk_yer': min((x['ilk_yer'] for x in ko if x.get('ilk_yer')), key=lambda z: [int(v) for v in z.split(':')], default='')}
    ka = s.get('kok_anlamlari') or {}; tf = d.get('turkce_fiil') or {}
    sys.path.insert(0, str(HERE))
    from agac_oku import oku
    global _A
    try: _A
    except NameError: _A = oku()
    o = ['<div class="kok">%s</div>' % temiz(k)]
    meta = []
    if ko.get('gecis'): meta.append('Kur\'ân\'da %d geçiş' % ko['gecis'])
    if ko.get('ilk_yer'): meta.append('ilk yer %s' % ':'.join(ko['ilk_yer'].split(':')[:2]))
    if d.get('sinif'): meta.append('kök sınıfı: %s' % d['sinif'])
    if tf.get('sap'): meta.append('fiil: %s' % tf['sap'])
    o.append('<div class="alt">%s</div>' % temiz(' · '.join(meta)))
    if ka.get('turkce'): o.append('<h2>Kök anlamı <small>(kök sözlüğü)</small></h2><div class="mana"><b>%s</b></div>' % temiz(ka['turkce']))
    o.append('<h2>Kökün manası <small>(asıllar ve türeme)</small></h2>')
    for i, n in enumerate(_A[k]):
        o.append('<div class="mana"><b>%d. %s</b>%s</div>' % (i + 1, temiz(n['mana']), ''.join('<div class="tur">· %s%s</div>' % (temiz(t['mana']), ''.join('<div class="tur" style="margin-left:5mm">– %s</div>' % temiz(u['mana']) for u in t['turev'])) for t in n['turev'])))
    o.append(osm_bolum(s))
    et = d['sozlukler'].get('etimoloji')
    if et: o.append('<h2>Etimoloji notu</h2><div class="osm">%s</div>' % paragraf(et if isinstance(et, str) else ''))
    for m in s.get('mekayis') or []:
        o.append('<h2>Mekâyîs <small>(İbn Fâris) · %s</small></h2><div class="mak"><div class="ar">%s</div></div>' % (temiz(m.get('baslik', '')), paragraf(m.get('metin', ''))))
    cm = s.get('cebel_mihveri')
    if cm: o.append('<h2>Cebel <small>(el-Mu\'cemü\'l-İştikâkî) · mihver</small></h2><div class="mak ar" style="font-size:12.6pt">%s</div>' % paragraf(cm.get('mihveri', '')))
    ea = s.get('etymarab') or {}
    if ea.get('dolu'):
        t = re.sub(r'^Back to library EtymArab\s+\S+\s+\S+\s+BP – • HDAL • © SG \| 15Feb2021\s*', '', ea.get('kok_maddesi', ''))
        t = re.sub(r'(?:▪ …\s*|[–-]\s*){2,}', ' ', t); t = re.sub(r'\s+', ' ', t)
        o.append('<h2>EtymArab <small>(Oslo Üniversitesi)</small></h2><div class="en">%s</div>' % temiz(t))
    return ''.join(o)

def koksuz_sayfa(k, KS):
    o = ['<div class="kok">%s</div><div class="alt">kökü olmayan lügat başlığı (harf, zamir, edat, özel ad vb.)</div><h2>Kelimeler</h2>' % temiz(k)]
    for e in KS:
        tr = e.get('turkce') or {}
        o.append('<div class="kelime"><div><b>%s</b> · %s%s<br><span class="tur" style="margin:0">%s</span><br><span class="en">%s</span></div><span class="ar">%s</span></div>' % (
            temiz(tr.get('yuzey') or tr.get('lemma') or ''), temiz(e.get('tur', '')), (' · ilk %s' % temiz(e['ilk_gecis'])) if e.get('ilk_gecis') else '',
            temiz(e.get('kok_durumu', '')), temiz(e.get('asil', '')), temiz(e['kelime'])))
    return ''.join(o)

def belge(govde): return '<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>' % (CSS % {'y': YAZI}, govde)

def uret(isler):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader
    from PIL import Image
    sonuc = {}
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1243/chrome-linux64/chrome'); g = b.new_page(); T = pathlib.Path(tmp)
        for no, govde in isler:
            h = T / ('%d.html' % no); h.write_text(belge(govde), encoding='utf-8')
            g.goto(h.as_uri()); g.evaluate('document.fonts.ready'); pdf = T / ('%d.pdf' % no)
            g.pdf(path=str(pdf), prefer_css_page_size=True, print_background=True)
            n = len(PdfReader(str(pdf)).pages)
            subprocess.run(['pdftoppm', '-r', str(DPI), '-png', str(pdf), str(T / ('p%d' % no))], check=True)
            pngs = sorted(T.glob('p%d-*.png' % no)); assert len(pngs) == n, (no, n, len(pngs))
            for sf, pg in enumerate(pngs, 1):
                Image.open(pg).convert('RGB').save(CIKTI / ('%d_%d.webp' % (no, sf)), 'WEBP', quality=62, method=6); pg.unlink()
            sonuc[no] = n; pdf.unlink(); h.unlink()
        b.close()
    return sonuc

def hepsi():
    from kuran_kokleri import kokler, norm_ar
    K = kokler(); KSZ = collections.defaultdict(list)
    for e in json.load(open(KR / 'koksuz.json', encoding='utf-8'))['kelimeler']: KSZ[norm_ar(e.get('lemma') or e['kelime'])].append(e)
    return [(no, ad, fl) for no, (ad, fl, _) in enumerate(K)], KSZ

def is_(a):
    no, ad, fl, KSZ = a
    return no, (kok_sayfa(ad) if fl == 0 else koksuz_sayfa(ad, KSZ.get(ad, [])))

if __name__ == '__main__':
    CIKTI.mkdir(exist_ok=True); L, KSZ = hepsi(); SJ = HERE / 'SAYFA2.json'
    sayfa = json.load(open(SJ)) if SJ.exists() else {}
    for f in CIKTI.glob('*.webp'):
        a, b = f.stem.split('_')[:2]
        if f.stem.endswith('_k'): continue
        sayfa[a] = max(sayfa.get(a, 0), int(b))
    if '--dene' in sys.argv:
        ad = sys.argv[sys.argv.index('--dene') + 1:]; sec = [(n, a, f) for n, a, f in L if a in ad]
    else: sec = [(n, a, f) for n, a, f in L if str(n) not in sayfa]
    isci = int(sys.argv[sys.argv.index('--isci') + 1]) if '--isci' in sys.argv else 4
    parca = [[(n, ad, fl) for n, ad, fl in sec[i::isci]] for i in range(isci)]
    from concurrent.futures import ProcessPoolExecutor
    def kos(P):
        return uret([is_((n, ad, fl, KSZ)) for n, ad, fl in P])
    with ProcessPoolExecutor(isci) as ex:
        for r in ex.map(kos, parca): sayfa.update({str(k): v for k, v in r.items()})
    json.dump(sayfa, open(SJ, 'w'), separators=(',', ':'))
    print(len(sayfa), 'kök,', sum(sayfa.values()), 'sayfa')

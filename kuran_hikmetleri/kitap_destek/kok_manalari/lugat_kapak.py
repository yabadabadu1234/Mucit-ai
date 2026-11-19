"""Kök başına KAPAK sayfası: yalnız kökün adı ve manası, iri puntoyla (A5); harita ikinci mertebede iken bu sayfa okunur.
Tek komut: python3 lugat_kapak.py [--isci N]. Çıktı: lugat_kapak/<no>_<sayfa>.webp ve ilk sayfanın önizlemesi <no>_1_k.webp; KAPAK.json kökün kapak sayfası sayısını tutar.
Lügat sayfaları (lugat_sayfa.py) aynen durur; galeri önce kapağı, sonra lügat sayfalarını gösterir."""
import json, sys, tempfile, subprocess, pathlib
from concurrent.futures import ProcessPoolExecutor
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lugat_sayfa import temiz, KR, YAZI, DPI, hepsi
CIKTI = HERE / 'lugat_kapak_2'
CSS = '''
@font-face{font-family:Amiri;src:url("file://%(y)s/Amiri-Regular.ttf");font-weight:400}
@font-face{font-family:Amiri;src:url("file://%(y)s/Amiri-Bold.ttf");font-weight:700}
@page{size:148mm 210mm;margin:8mm 8mm 8mm 8mm;background:#fffdf6}
html{background:#fffdf6}body{margin:0;font:19pt/1.3 FreeSerif,"DejaVu Serif",serif;color:#2b2410}
.kok{font-family:Amiri,serif;font-weight:700;font-size:110pt;line-height:1.9;text-align:center;direction:rtl;color:#5a3d0c}
.alt{text-align:center;font-size:17pt;color:#6b5a3a;margin:0 0 4mm}
h2{font:700 20pt FreeSerif,serif;color:#fff;background:#8a6d1d;margin:4mm 0 2mm;padding:1.2mm 3mm;border-radius:1.4mm;break-after:avoid}
.an{font-weight:700;font-size:56pt;line-height:1.14;margin:0 0 2mm}
.mana{margin:0 0 2.4mm;break-inside:avoid}.mana b{font-size:38pt}.tur{margin:.4mm 0 0 6mm;font-size:30pt;color:#4a3f28}.tur2{margin-left:12mm;font-size:25pt;color:#5a4f38}
.kelime{display:flex;justify-content:space-between;gap:4mm;border-bottom:.3mm solid #d9ceaa;padding:1.4mm 0;break-inside:avoid}
.kelime .ar{font-family:Amiri,serif;direction:rtl;font-size:46pt;flex:none;line-height:1.5}.kelime div{flex:1}.kelime b{font-size:34pt}.kelime .k{font-size:22pt;color:#6b5a3a}
'''
def belge(g): return '<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>' % (CSS % {'y': YAZI}, g)

def ko_birles(ko):
    if isinstance(ko, list): return {'gecis': sum(x.get('gecis', 0) for x in ko), 'ilk_yer': min((x['ilk_yer'] for x in ko if x.get('ilk_yer')), key=lambda z: [int(v) for v in z.split(':')], default='')}
    return ko or {}

def kok_govde(k, A):
    f = KR / 'kokler' / (k + '.json')
    if not f.exists():
        return '<div class="kok">%s</div><div class="alt">Kur\'ân morfolojisinde geçen kök</div><h2>Kayıt durumu</h2><div class="mana"><b>Bu kök için kök defterinde dosya yok.</b></div><div class="tur">Eşleştirme yapılmadı.</div>' % temiz(k)
    d = json.load(open(f, encoding='utf-8')); s = d['sozlukler']; ko = ko_birles(s.get('kuran_korpusu')); ka = s.get('kok_anlamlari') or {}; tf = d.get('turkce_fiil') or {}
    o = ['<div class="kok">%s</div>' % temiz(k)]
    meta = []
    if ko.get('gecis'): meta.append("Kur'ân'da %d geçiş" % ko['gecis'])
    if ko.get('ilk_yer'): meta.append('ilk yer %s' % ':'.join(ko['ilk_yer'].split(':')[:2]))
    if tf.get('sap'): meta.append('fiil: %s' % tf['sap'])
    o.append('<div class="alt">%s</div>' % temiz(' · '.join(meta)))
    if ka.get('turkce'): o.append('<h2>Kök anlamı</h2><div class="an">%s</div>' % temiz(ka['turkce']))
    o.append('<h2>Kökün manası</h2>')
    for i, n in enumerate(A[k]):
        o.append('<div class="mana"><b>%d. %s</b>%s</div>' % (i + 1, temiz(n['mana']), ''.join('<div class="tur">· %s%s</div>' % (temiz(t['mana']), ''.join('<div class="tur2">– %s</div>' % temiz(u['mana']) for u in t['turev'])) for t in n['turev'])))
    return ''.join(o)

def koksuz_govde(k, KS):
    o = ['<div class="kok">%s</div><div class="alt">kökü olmayan lügat başlığı</div><h2>Kelimeler</h2>' % temiz(k)]
    for e in KS:
        tr = e.get('turkce') or {}
        o.append('<div class="kelime"><div><b>%s</b><br><span class="k">%s%s</span></div><span class="ar">%s</span></div>' % (temiz(tr.get('yuzey') or tr.get('lemma') or ''), temiz(e.get('tur', '')), (' · ilk %s' % temiz(e['ilk_gecis'])) if e.get('ilk_gecis') else '', temiz(e['kelime'])))
    return ''.join(o)

def uret(P, KSZ):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader
    from PIL import Image
    from agac_oku import oku
    A = oku(); sonuc = {}
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        C = sorted(pathlib.Path('/opt/pw-browsers').glob('chromium-*/chrome-linux*/chrome'))[-1]
        b = p.chromium.launch(executable_path=str(C)); g = b.new_page(); T = pathlib.Path(tmp)
        for no, ad, fl in P:
            h = T / ('%d.html' % no); h.write_text(belge(kok_govde(ad, A) if fl == 0 else koksuz_govde(ad, KSZ.get(ad, []))), encoding='utf-8')
            g.goto(h.as_uri()); g.evaluate('document.fonts.ready'); pdf = T / ('%d.pdf' % no)
            g.pdf(path=str(pdf), prefer_css_page_size=True, print_background=True)
            n = len(PdfReader(str(pdf)).pages)
            subprocess.run(['pdftoppm', '-r', str(DPI), '-png', str(pdf), str(T / ('p%d' % no))], check=True)
            pngs = sorted(T.glob('p%d-*.png' % no)); assert len(pngs) == n, (no, n, len(pngs))
            for sf, pg in enumerate(pngs, 1):
                im = Image.open(pg).convert('RGB'); im.save(CIKTI / ('%d_%d.webp' % (no, sf)), 'WEBP', quality=62, method=6)
                if sf == 1: im.resize((160, round(160 * im.height / im.width)), Image.LANCZOS).save(CIKTI / ('%d_1_k.webp' % no), 'WEBP', quality=60, method=6)
                pg.unlink()
            sonuc[no] = n; pdf.unlink(); h.unlink()
        b.close()
    return sonuc

def kos(a): return uret(*a)

if __name__ == '__main__':
    CIKTI.mkdir(exist_ok=True); L, KSZ = hepsi(); SJ = HERE / 'KAPAK2.json'
    sayfa = json.load(open(SJ)) if SJ.exists() and '--yeniden' not in sys.argv else {}
    for f in ([] if '--yeniden' in sys.argv else CIKTI.glob('*.webp')):
        a, b_ = f.stem.split('_')[:2]
        if not f.stem.endswith('_k'): sayfa[a] = max(sayfa.get(a, 0), int(b_))
    isci = int(sys.argv[sys.argv.index('--isci') + 1]) if '--isci' in sys.argv else 4
    sec = [(n, a, f) for n, a, f in L if str(n) not in sayfa]
    if '--dene' in sys.argv: ad_ = sys.argv[sys.argv.index('--dene') + 1:]; sec = [(n, a, f) for n, a, f in L if a in ad_]
    parca = [(sec[i::isci], KSZ) for i in range(isci)]
    with ProcessPoolExecutor(isci) as ex:
        for r in ex.map(kos, parca): sayfa.update({str(k): v for k, v in r.items()})
    json.dump(sayfa, open(SJ, 'w'), separators=(',', ':'))
    print(len(sayfa), 'kök,', sum(sayfa.values()), 'kapak sayfası')

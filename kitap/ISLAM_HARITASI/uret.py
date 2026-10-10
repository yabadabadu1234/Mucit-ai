import json, html, collections
d = json.load(open('harita.json', encoding='utf8'))
dur = {'ag': 'ispat ağında', 'desme': 'deşme var', 'bos': 'karşılığı yok'}
sayi = collections.Counter(n['durum'] for n in d['dugumler'])
bos_satir = sum(1 for n in d['dugumler'] for a in ('neden', 'ispat', 'baskasi') if n[a] == '—')
esc = html.escape
parca = []
for k in d['katmanlar']:
    ns = [n for n in d['dugumler'] if n['k'] == k['id']]
    kart = ''.join(
        '<details><summary><b>%s</b><span class="r %s">%s</span></summary>'
        '<dl><dt>Ne</dt><dd>%s</dd><dt>Neden</dt><dd>%s</dd><dt>İspat</dt><dd>%s</dd>'
        '<dt>Başkası neden olamaz</dt><dd>%s</dd></dl></details>'
        % (esc(n['ad']), n['durum'], dur[n['durum']], esc(n['ne']), esc(n['neden']), esc(n['ispat']), esc(n['baskasi']))
        for n in ns)
    parca.append('<section><h2>%s <small>%d düğüm</small></h2>%s</section>' % (esc(k['ad']), len(ns), kart))
ozet = 'Toplam %d düğüm · ispat ağında %d · deşme var %d · karşılığı yok %d · boş bırakılan satır %d' % (
    len(d['dugumler']), sayi['ag'], sayi['desme'], sayi['bos'], bos_satir)
sayfa = """<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>İslâm Haritası</title><style>
:root{--bg:#f6f4ef;--fg:#1d2327;--mut:#5b6670;--kart:#fff;--cizgi:#d8d4c9;--ag:#1f6f55;--desme:#8a6a12;--bos:#a23b3b}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#14181b;--fg:#e4e6e3;--mut:#9aa5ad;--kart:#1c2227;--cizgi:#2f383e;--ag:#58c29b;--desme:#d6b24f;--bos:#e07b7b}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 Georgia,'Times New Roman',serif;padding:0 16px 48px}
main{max-width:860px;margin:0 auto}h1{font-size:1.6rem;margin:28px 0 4px}p.not,p.ozet{color:var(--mut);margin:6px 0}
h2{font-size:1.05rem;margin:28px 0 8px;border-bottom:1px solid var(--cizgi);padding-bottom:4px}h2 small{color:var(--mut);font-weight:normal}
details{background:var(--kart);border:1px solid var(--cizgi);border-radius:8px;margin:8px 0;padding:8px 12px}
summary{cursor:pointer;display:flex;justify-content:space-between;gap:12px;align-items:baseline}
.r{font:12px/1 system-ui,sans-serif;white-space:nowrap}.ag{color:var(--ag)}.desme{color:var(--desme)}.bos{color:var(--bos)}
dl{margin:8px 0 2px}dt{font:600 12px/1.2 system-ui,sans-serif;letter-spacing:.04em;text-transform:uppercase;color:var(--mut);margin-top:8px}dd{margin:2px 0 0}
</style></head><body><main><h1>İslâm Haritası</h1><p class="ozet">%s</p><p class="not">%s</p>%s</main></body></html>""" % (
    esc(ozet), esc(d['not']), ''.join(parca))
open('islam_haritasi.html', 'w', encoding='utf8').write(sayfa)
print(ozet)

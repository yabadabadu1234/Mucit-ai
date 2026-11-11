import sys, re, json, html, pathlib

LEVHA_HADDI = 100
DAL_HADDI = 9
SATIR = re.compile(r'^(\d+(?:\.\d+)*)\s+([A-Z])([*?]?)\s+(.*)$')
BAG = re.compile(r'^([<!=~])(\d+(?:\.\d+)*)$')
CINSLER = set('KBTHDMSIUVN')


def oku(yol):
    dugumler, sira, son = {}, [], None
    for no, ham in enumerate(pathlib.Path(yol).read_text(encoding='utf-8').splitlines(), 1):
        if not ham.strip():
            continue
        if ham[0] in ' \t':
            assert son is not None, 'satır %d: gövde düğümsüz' % no
            dugumler[son]['govde'].append(ham.strip())
            continue
        m = SATIR.match(ham)
        assert m, 'satır %d: düğüm satırı okunamadı: %s' % (no, ham)
        adres, cins, damga, kalan = m.groups()
        assert cins in CINSLER, 'satır %d: cins bilinmiyor: %s' % (no, cins)
        assert adres not in dugumler, 'satır %d: adres iki kere: %s' % (no, adres)
        kelimeler, baglar = kalan.split(), []
        while kelimeler and BAG.match(kelimeler[-1]):
            b = BAG.match(kelimeler.pop())
            baglar.insert(0, (b.group(1), b.group(2)))
        dugumler[adres] = dict(adres=adres, cins=cins, damga=damga, levha=' '.join(kelimeler),
                               baglar=baglar, govde=[], satir=no, sira=len(sira))
        sira.append(adres)
        son = adres
    return dugumler, sira


def baba(adres):
    if adres == '0':
        return None
    return adres.rsplit('.', 1)[0] if '.' in adres else '0'


def denetle(d, sira):
    ihlal = []
    assert sira and sira[0] == '0', 'ilk düğüm kök (0) olmalı'
    cocuk = {a: [] for a in sira}
    for a in sira[1:]:
        b = baba(a)
        if b not in d or d[b]['sira'] > d[a]['sira']:
            ihlal.append('K6 %s: babası (%s) evvel yazılmamış' % (a, b))
            continue
        cocuk[b].append(a)
    gorulen = {}
    for a in sira:
        n = d[a]
        if len(n['levha']) > LEVHA_HADDI:
            ihlal.append('K1 %s: levha %d harf' % (a, len(n['levha'])))
        if not n['levha']:
            ihlal.append('K1 %s: levha boş' % a)
        if len(cocuk[a]) > DAL_HADDI:
            ihlal.append('K2 %s: %d çocuk' % (a, len(cocuk[a])))
        if n['cins'] == 'H' and not n['damga'] and not any(t == '<' for t, _ in n['baglar']):
            ihlal.append('K3 %s: hüküm dayanaksız ve damgasız' % a)
        metin = ' '.join([n['levha']] + n['govde']).lower()
        if metin in gorulen:
            ihlal.append('K4 %s: %s ile aynı muhteva' % (a, gorulen[metin]))
        gorulen[metin] = a
        for t, h in n['baglar']:
            if h not in d:
                ihlal.append('K6 %s: bağın ucu yok: %s' % (a, h))
            elif t == '<' and d[h]['sira'] >= n['sira']:
                ihlal.append('K6 %s: sonra yazılana dayanıyor: %s' % (a, h))
    return ihlal, cocuk


def boy(n):
    return len(n['levha']) + sum(len(g) for g in n['govde'])


def koni(d, a, bellek):
    if a in bellek:
        return bellek[a]
    k = {a}
    for t, h in d[a]['baglar']:
        if t == '<' and h in d:
            k |= koni(d, h, bellek)
    bellek[a] = k
    return k


def olc(d, sira, cocuk):
    bellek = {}
    derinlik = max(a.count('.') + 1 if a != '0' else 0 for a in sira)
    kat = {}
    for a in sira:
        s = 0 if a == '0' else a.count('.') + 1
        kat[s] = kat.get(s, 0) + len(d[a]['levha'])
    toplam = sum(boy(d[a]) for a in sira)
    isaret = sum(len(a) + 2 + len(d[a]['damga']) + sum(len(h) + 2 for _, h in d[a]['baglar']) for a in sira)
    koniler = {a: sum(boy(d[x]) for x in koni(d, a, bellek)) for a in sira}
    baslar = {}
    gecen = 0
    for a in sira:
        gecen += boy(d[a])
        baslar[a] = gecen
    return dict(dugum=len(sira), derinlik=derinlik, oz=toplam, isaret=isaret, hacim=toplam + isaret,
                kat_harf=kat, azami_koni=max(koniler.values()),
                ortalama_koni=round(sum(koniler.values()) / len(sira)),
                ortalama_bas=round(sum(baslar.values()) / len(sira)),
                bulma_haddi=LEVHA_HADDI * DAL_HADDI * derinlik), koniler


SAYFA = '''<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__AD__</title><style>
:root{--zemin:#0b1a38;--kagit:#f6ecc9;--altin:#d4af37;--yazi:#2b1d05}
*{box-sizing:border-box}body{margin:0;background:var(--zemin);color:var(--yazi);font:16px/1.45 Georgia,"DejaVu Serif",serif}
header{position:sticky;top:0;background:var(--zemin);color:#ffe9a8;padding:10px 16px;border-bottom:2px solid var(--altin);z-index:2}
header h1{margin:0 0 6px;font-size:18px}header input{width:100%;max-width:520px;padding:7px 10px;border:1px solid var(--altin);border-radius:6px;font:inherit}
header small{display:block;margin-top:6px;opacity:.85}
main{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px;padding:14px 16px}
@media(max-width:820px){main{grid-template-columns:1fr}}
section{background:var(--kagit);border:2px solid var(--altin);border-radius:10px;padding:12px;min-width:0}
h2{margin:0 0 8px;font-size:15px;letter-spacing:1px;color:#7a4a00}
ul{list-style:none;margin:0;padding-left:16px}#agac>ul{padding-left:0}
li{margin:3px 0}.s{cursor:pointer;display:block;padding:3px 6px;border-radius:6px}
.s:hover{background:#e8d79c}.sec{background:#f0d98a}.a{font:12px monospace;color:#7a4a00;margin-right:6px}
.c{display:inline-block;min-width:20px;text-align:center;font:bold 12px sans-serif;color:#fff;border-radius:4px;margin-right:6px;padding:1px 4px}
.g{margin:4px 0 4px 34px;font-size:14px;white-space:pre-wrap;overflow-wrap:anywhere}
.b{font:12px monospace;color:#5a3d0a;margin-left:34px}.gizli{display:none}.k{font-size:13px;color:#5a3d0a;margin-bottom:8px}
.ok{cursor:pointer;display:inline-block;width:16px;color:#7a4a00}
</style><header><h1>__AD__</h1><input id="ara" placeholder="Levhalarda ara"><small id="olcu"></small></header>
<main><section><h2>UFUK</h2><div id="agac"></div></section><section><h2>MERCEK</h2><div id="mercek" class="k">Bir düğüme dokunun: yalnız dayandığı düğümler, yazılış sırasıyla gösterilir.</div></section></main>
<script>
const V=__VERI__;const D=V.dugumler,S=V.sira,C=V.cocuk,O=V.olcu;
const R={K:'#0b1a38',B:'#555',T:'#1b6d8f',H:'#8f2222',D:'#1d6d3b',M:'#b05c0a',S:'#6a3d9a',I:'#a03060',U:'#345',V:'#665500',N:'#000'};
const AD={K:'kitap',B:'bâb',T:'tarif',H:'hüküm',D:'delil',M:'misal',S:'suâl',I:'itiraz',U:'usul',V:'veri',N:'nakil'};
const BA={'<':'dayanır','!':'itiraz eder','=':'misalidir','~':'bakınız'};
function e(t){return t.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
function satir(a,tam){const n=D[a];let h='<span class="a">'+a+'</span><span class="c" style="background:'+R[n.cins]+'" title="'+AD[n.cins]+'">'+n.cins+n.damga+'</span>'+e(n.levha);
if(tam){if(n.govde.length)h+='<div class="g">'+e(n.govde.join('\\n'))+'</div>';if(n.baglar.length)h+='<div class="b">'+n.baglar.map(b=>BA[b[0]]+' '+b[1]).join(' · ')+'</div>'}return h}
function dal(a,kat){const li=document.createElement('li');const var_=C[a].length>0;
li.innerHTML=(var_?'<span class="ok">'+(kat<1?'▾':'▸')+'</span>':'<span class="ok"></span>')+'<span class="s" style="display:inline-block;width:calc(100% - 22px);vertical-align:top" data-a="'+a+'">'+satir(a,false)+'</span>';
if(var_){const ul=document.createElement('ul');if(kat>=1)ul.className='gizli';C[a].forEach(c=>ul.appendChild(dal(c,kat+1)));li.appendChild(ul);
li.querySelector('.ok').onclick=ev=>{ul.classList.toggle('gizli');ev.target.textContent=ul.classList.contains('gizli')?'▸':'▾'}}
li.querySelector('.s').onclick=()=>mercek(a);return li}
function koni(a,g){if(g.has(a))return g;g.add(a);D[a].baglar.forEach(b=>{if(b[0]=='<'&&D[b[1]])koni(b[1],g)});return g}
function boy(a){return D[a].levha.length+D[a].govde.reduce((t,x)=>t+x.length,0)}
function mercek(a){document.querySelectorAll('.sec').forEach(x=>x.classList.remove('sec'));const el=document.querySelector('[data-a="'+a+'"]');if(el)el.classList.add('sec');
const g=[...koni(a,new Set())].sort((x,y)=>D[x].sira-D[y].sira);const t=g.reduce((s,x)=>s+boy(x),0);let bas=0;for(const x of S){bas+=boy(x);if(x==a)break}
document.getElementById('mercek').innerHTML='<div class="k">'+a+' düğümünü delilleriyle öğrenmek için '+g.length+' düğüm, '+t+' harf okunur. Baştan buraya kadar düz okuyan '+bas+' harf okurdu.</div><ul style="padding-left:0">'+g.map(x=>'<li>'+satir(x,true)+'</li>').join('')+'</ul>'}
const kok=document.createElement('ul');kok.appendChild(dal('0',0));document.getElementById('agac').appendChild(kok);
document.getElementById('olcu').textContent=O.dugum+' düğüm · derinlik '+O.derinlik+' · hacim '+O.hacim+' harf (öz '+O.oz+', işaret '+O.isaret+') · bulma haddi '+O.bulma_haddi+' harf · ortalama koni '+O.ortalama_koni+' harf, ortalama düz okuma '+O.ortalama_bas+' harf';
document.getElementById('ara').oninput=ev=>{const q=ev.target.value.toLocaleLowerCase('tr');document.querySelectorAll('#agac li').forEach(li=>li.style.display='');if(!q)return;
document.querySelectorAll('#agac ul').forEach(u=>u.classList.remove('gizli'));document.querySelectorAll('#agac li').forEach(li=>{if(!li.textContent.toLocaleLowerCase('tr').includes(q))li.style.display='none'})};
</script></html>'''


def sayfa(d, sira, cocuk, olcu, ad):
    veri = dict(dugumler=d, sira=sira, cocuk=cocuk, olcu=olcu)
    return SAYFA.replace('__AD__', html.escape(ad)).replace('__VERI__', json.dumps(veri, ensure_ascii=False).replace('</', '<\\/'))


def kos(yol, asil=None):
    d, sira = oku(yol)
    ihlal, cocuk = denetle(d, sira)
    olcu, _ = olc(d, sira, cocuk)
    print(yol)
    for k in ('dugum', 'derinlik', 'oz', 'isaret', 'hacim', 'bulma_haddi', 'azami_koni', 'ortalama_koni', 'ortalama_bas'):
        print('  %-14s %s' % (k, olcu[k]))
    print('  kat_harf      ', olcu['kat_harf'])
    if asil:
        a = len(pathlib.Path(asil).read_text(encoding='utf-8'))
        olcu['asil'] = a
        print('  asıl metin     %d harf; nispet %.3f' % (a, olcu['hacim'] / a))
    print('  ihlâl          %d' % len(ihlal))
    for i in ihlal:
        print('   ', i)
    cikti = pathlib.Path(yol).with_suffix('.html')
    cikti.write_text(sayfa(d, sira, cocuk, olcu, d['0']['levha']), encoding='utf-8')
    return len(ihlal)


if __name__ == '__main__':
    assert len(sys.argv) >= 2, 'kullanım: python zubde.py dosya.zbd [asıl_metin]'
    sys.exit(1 if kos(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None) else 0)

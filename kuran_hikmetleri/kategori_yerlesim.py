import collections
import glob
import json
import math
import os
import random

import numpy as np
from scipy.sparse import csr_matrix, diags
from scipy.stats import rankdata
from sklearn.decomposition import TruncatedSVD

KOK = os.path.dirname(os.path.abspath(__file__))
CIKTI = os.path.join(KOK, 'kategori_yerlesim.html')
USULLER = [
    ('mahrec', 'Ses: mahreç'),
    ('wordnet', 'Mana: Arabic WordNet bölümü'),
    ('gomme', 'Mana: gömme kümesi'),
    ('muhassas', 'Konu: Muhassas kitabı'),
    ('cebel', 'Ses-mana: Cebel fasılı'),
    ('mecaz', 'Zemahşerî: hakîkat/mecaz'),
    ('prototip', 'Prototip: yayılım uzaklığı'),
    ('korpus', 'Korpus: baskın tür'),
    ('kuran', 'Kur\'ân\'da geçiş'),
    ('etymarab', 'EtymArab maddesi'),
]
RENK = ['#c0392b', '#2471a3', '#1e8449', '#b9770e', '#7d3c98', '#117a8b', '#a04000', '#566573', '#b03a6e', '#4d6d1f']
AYIRMA_ADIMI = 2
GRID_ARALIK = 2


def sinif_etiketleri(d, prototip_esik):
    s = {}
    t = d.get('tasnif') or {}
    if t.get('mahrec'):
        s['mahrec'] = t['mahrec']
    m = d.get('mana_tasnif') or {}
    if m.get('orta'):
        s['wordnet'] = m['orta']
    g = d.get('mana_tasnif_gomme') or {}
    if g.get('orta'):
        s['gomme'] = 'g%d' % g['orta']['kume']
    mh = d.get('muhassas_tasnif') or {}
    if mh.get('kitap'):
        s['muhassas'] = mh['kitap']
    c = d.get('ses_mana_tasnif') or {}
    if c.get('fasil'):
        s['cebel'] = c['fasil']
    h = d.get('hakikat_mecaz_tasnif') or {}
    if 'mecaz_var' in h:
        s['mecaz'] = 'mecazlı' if h['mecaz_var'] else 'yalnız hakîkat'
    p = d.get('prototip_yayilim_tasnif') or {}
    if 'ortalama_benzerlik' in p:
        b = p['ortalama_benzerlik']
        s['prototip'] = 'yakın' if b >= prototip_esik[1] else ('orta' if b >= prototip_esik[0] else 'uzak')
    kq = (d.get('sozlukler') or {}).get('kuran_korpusu')
    if isinstance(kq, list):
        kq = kq[0] if kq else None
    if kq and kq.get('tur'):
        s['korpus'] = max(kq['tur'], key=kq['tur'].get)
    s['kuran'] = 'Kur\'ân\'da var' if d.get('kuranda_var') else 'Kur\'ân\'da yok'
    ea = (d.get('sozlukler') or {}).get('etymarab')
    if ea:
        s['etymarab'] = 'dolu' if ea.get('dolu') else 'yer tutucu'
    return s


def yukle():
    dosyalar = sorted(glob.glob(os.path.join(KOK, 'kelime_kaydi', 'kuranda_*', 'kokler', '*.json')))
    ham = []
    for f in dosyalar:
        d = json.load(open(f, encoding='utf-8'))
        p = d.get('prototip_yayilim_tasnif') or {}
        ka = (d.get('sozlukler') or {}).get('kok_anlamlari') or {}
        ham.append((d['kok'], d, p.get('ortalama_benzerlik')))
    benz = [x[2] for x in ham if x[2] is not None]
    esik = np.quantile(benz, [1 / 3, 2 / 3])
    dugumler = []
    for kok, d, _ in ham:
        s = sinif_etiketleri(d, esik)
        ka = (d.get('sozlukler') or {}).get('kok_anlamlari') or {}
        kq = (d.get('sozlukler') or {}).get('kuran_korpusu')
        if isinstance(kq, list):
            kq = kq[0] if kq else None
        dugumler.append({'kok': kok, 'siniflar': s, 'mana': ka.get('turkce', ''), 'kelime': len(d.get('kelimeler', [])),
                         'gecis': (kq or {}).get('gecis', 0), 'kuran': bool(d.get('kuranda_var'))})
    return dugumler


def en_kucuk_daire(nok):
    nok = list(nok)
    random.Random(7).shuffle(nok)

    def iki(a, b):
        cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        return cx, cy, math.hypot(a[0] - b[0], a[1] - b[1]) / 2

    def uc(a, b, c):
        ax, ay = a
        bx, by = b
        cx, cy = c
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(d) < 1e-12:
            ds = [iki(a, b), iki(a, c), iki(b, c)]
            return max(ds, key=lambda x: x[2])
        ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
        uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
        return ux, uy, math.hypot(ax - ux, ay - uy)

    def icinde(c, p):
        return math.hypot(p[0] - c[0], p[1] - c[1]) <= c[2] + 1e-9

    c = (nok[0][0], nok[0][1], 0.0)
    for i, p in enumerate(nok):
        if icinde(c, p):
            continue
        c = (p[0], p[1], 0.0)
        for j in range(i):
            q = nok[j]
            if icinde(c, q):
                continue
            c = iki(p, q)
            for k in range(j):
                r = nok[k]
                if not icinde(c, r):
                    c = uc(p, q, r)
    return c


def yerlesim(dugumler, uzak=0.75, adim=150, ayirma=0.25):
    sinif_id = {}
    sinif_liste = []
    for u, _ in USULLER:
        for dg in dugumler:
            e = dg['siniflar'].get(u)
            if e is not None and (u, e) not in sinif_id:
                sinif_id[(u, e)] = len(sinif_liste)
                sinif_liste.append((u, e))
    satir, sutun = [], []
    for i, dg in enumerate(dugumler):
        for u, e in dg['siniflar'].items():
            satir.append(i)
            sutun.append(sinif_id[(u, e)])
    n, k = len(dugumler), len(sinif_liste)
    M = csr_matrix((np.ones(len(satir)), (satir, sutun)), shape=(n, k))
    sayi = np.asarray(M.sum(0)).ravel()
    w = 1 / np.maximum(sayi, 1) ** uzak
    Mw = M @ diags(w)
    P = TruncatedSVD(2, random_state=7).fit_transform(Mw)
    rng = np.random.default_rng(7)
    P = (P - P.mean(0)) / (P.std(0) + 1e-9) + rng.normal(0, 0.05, P.shape)
    usul_siniflari = collections.defaultdict(list)
    for j, (u, e) in enumerate(sinif_liste):
        usul_siniflari[u].append(j)
    pay = np.maximum(np.asarray(Mw.sum(1)).ravel(), 1e-9)
    for _ in range(adim):
        C = (M.T @ P) / np.maximum(sayi, 1)[:, None]
        for u, js in usul_siniflari.items():
            if len(js) < 2:
                continue
            c = C[js]
            fark = c[:, None, :] - c[None, :, :]
            d2 = (fark ** 2).sum(-1) + 0.05
            it = (fark / d2[..., None]).sum(1)
            C[js] = c + ayirma * it / (1 + np.linalg.norm(it, axis=1, keepdims=True))
        P = (Mw @ C) / pay[:, None] + rng.normal(0, 0.01, P.shape)
        P = (P - P.mean(0)) / (P.std(0) + 1e-9)
    U = np.column_stack([rankdata(P[:, 0]), rankdata(P[:, 1])]) / n
    return (U - 0.5) * 2, M, sinif_liste, sinif_id


def izgaraya_otur(P):
    n = len(P)
    kenar = int(math.ceil(math.sqrt(n * 1.25)))
    aday = np.rint(P * kenar / 2.0).astype(int)
    dolu = {}
    sira = np.argsort(np.linalg.norm(P, axis=1))
    sonuc = np.zeros((n, 2), dtype=int)
    kayma = []
    for i in sira:
        x, y = int(aday[i][0]), int(aday[i][1])
        r = 0
        bulundu = False
        while not bulundu:
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    h = (x + dx, y + dy)
                    if h not in dolu:
                        dolu[h] = i
                        sonuc[i] = h
                        kayma.append(max(abs(dx), abs(dy)))
                        bulundu = True
                        break
                if bulundu:
                    break
            r += 1
    return sonuc * GRID_ARALIK, kayma


def daireler(izgara, M, sinif_liste):
    dairesel = []
    Mc = M.tocsc()
    for j, (u, e) in enumerate(sinif_liste):
        uyeler = Mc[:, j].nonzero()[0]
        nok = [(float(izgara[i][0]), float(izgara[i][1])) for i in uyeler]
        cx, cy, r = en_kucuk_daire(nok)
        dairesel.append((cx, cy, r + GRID_ARALIK * 0.6, len(uyeler)))
    return dairesel


def olcut(izgara, M, dairesel, sinif_liste):
    Mr = M.tocsr()
    ihlal = 0
    toplam = 0
    for i in range(M.shape[0]):
        for j in Mr[i].indices:
            toplam += 1
            cx, cy, r, _ = dairesel[j]
            if math.hypot(izgara[i][0] - cx, izgara[i][1] - cy) > r + 1e-6:
                ihlal += 1
    ayni = collections.defaultdict(list)
    for j, (u, e) in enumerate(sinif_liste):
        ayni[u].append(j)
    ortusme = {}
    for u, js in ayni.items():
        alan = sum(math.pi * dairesel[j][2] ** 2 for j in js)
        kes = 0.0
        for a in range(len(js)):
            for b in range(a + 1, len(js)):
                ca, cb = dairesel[js[a]], dairesel[js[b]]
                d = math.hypot(ca[0] - cb[0], ca[1] - cb[1])
                r1, r2 = ca[2], cb[2]
                if d >= r1 + r2:
                    continue
                if d <= abs(r1 - r2):
                    kes += math.pi * min(r1, r2) ** 2
                    continue
                a1 = math.acos(max(-1.0, min(1.0, (d * d + r1 * r1 - r2 * r2) / (2 * d * r1))))
                a2 = math.acos(max(-1.0, min(1.0, (d * d + r2 * r2 - r1 * r1) / (2 * d * r2))))
                kes += r1 * r1 * a1 + r2 * r2 * a2 - 0.5 * math.sqrt(max(0, (-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2)))
        ortusme[u] = round(kes / alan, 3) if alan else 0
    return ihlal, toplam, ortusme


def en_az_uzaklik(izgara):
    benzersiz = len(set(map(tuple, izgara.tolist()))) == len(izgara)
    eksende = bool(np.all(izgara % GRID_ARALIK == 0))
    return benzersiz, eksende


def yaz():
    dugumler = yukle()
    P, M, sinif_liste, sinif_id = yerlesim(dugumler)
    izgara, kayma = izgaraya_otur(P)
    dairesel = daireler(izgara, M, sinif_liste)
    ihlal, toplam, ortusme = olcut(izgara, M, dairesel, sinif_liste)
    benzersiz, eksende = en_az_uzaklik(izgara)
    yaricap = collections.defaultdict(list)
    for (u, e), c in zip(sinif_liste, dairesel):
        yaricap[u].append(c[2])
    harita_yaricapi = max(np.ptp(izgara[:, 0]), np.ptp(izgara[:, 1])) / 2
    veri = {
        'usuller': [{'ad': ad, 'renk': RENK[i], 'anahtar': a} for i, (a, ad) in enumerate(USULLER)],
        'siniflar': [{'u': [a for a, _ in USULLER].index(u), 'ad': e, 'x': round(c[0], 1), 'y': round(c[1], 1), 'r': round(c[2], 1), 'n': c[3]} for (u, e), c in zip(sinif_liste, dairesel)],
        'dugumler': [{'k': dg['kok'], 'x': int(izgara[i][0]), 'y': int(izgara[i][1]), 's': [sinif_id[(u, e)] for u, e in dg['siniflar'].items()], 'm': dg['mana'][:140], 'w': dg['kelime'], 'g': dg['gecis'], 'q': 1 if dg['kuran'] else 0} for i, dg in enumerate(dugumler)],
        'olcut': {'dugum': len(dugumler), 'sinif': len(sinif_liste), 'uyelik': toplam, 'daire_disinda_kalan_uyelik': ihlal, 'ayni_usul_ortusmesi': ortusme, 'ortanca_daire_yaricapi_harita_yaricapina_orani': {u: round(float(np.median(v)) / float(harita_yaricapi), 2) for u, v in yaricap.items()}, 'her_dugum_ayri_hucrede': benzersiz, 'hepsi_izgara_noktasinda': eksende, 'en_az_dugum_arasi_uzaklik': GRID_ARALIK,
                  'ortalama_kayma_hucre': round(float(np.mean(kayma)), 2), 'en_buyuk_kayma_hucre': int(max(kayma))},
    }
    html = SAYFA.replace('/*VERI*/', json.dumps(veri, ensure_ascii=False, separators=(',', ':')))
    with open(CIKTI, 'w', encoding='utf-8') as f:
        f.write(html)
    print(json.dumps(veri['olcut'], ensure_ascii=False))


SAYFA = r"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kategori Yerleşimi</title>
<style>
:root{--bg:#fbf8f1;--fg:#222;--panel:#fffdf8;--line:#d8d0bd;--mut:#6b6558}
@media (prefers-color-scheme:dark){:root{--bg:#1a1814;--fg:#ece6d6;--panel:#23201a;--line:#3a352b;--mut:#a79f8b}}
*{box-sizing:border-box}html,body{margin:0;height:100%;background:var(--bg);color:var(--fg);font-family:Georgia,serif}
#app{display:grid;grid-template-columns:300px 1fr;height:100%}
#yan{overflow:auto;padding:12px 14px;background:var(--panel);border-right:1px solid var(--line);font-size:13px;line-height:1.5}
#yan h1{font-size:17px;margin:0 0 6px}#yan h2{font-size:13px;margin:14px 0 4px;color:var(--mut);font-weight:normal;letter-spacing:.03em}
#yan label{display:flex;align-items:center;gap:6px;margin:2px 0;cursor:pointer}
.sw{width:11px;height:11px;border-radius:50%;display:inline-block;flex:none}
#sahne{position:relative;min-width:0}canvas{display:block;width:100%;height:100%;cursor:grab}
#ara{width:100%;padding:5px 7px;font:inherit;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:4px;direction:rtl}
#bilgi{margin-top:8px;padding:8px;border:1px solid var(--line);border-radius:6px;min-height:60px}
#bilgi b.k{font-size:20px;direction:rtl;display:inline-block}
.not{color:var(--mut);font-size:12px}
select{width:100%;font:inherit;padding:4px;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:4px}
@media(max-width:700px){#app{grid-template-columns:1fr;grid-template-rows:42% 58%}#yan{border-right:0;border-bottom:1px solid var(--line)}}
</style></head><body>
<div id="app">
<div id="yan">
<h1>Kategori Yerleşimi</h1>
<div class="not" id="ozet"></div>
<h2>KÖK ARA</h2><input id="ara" placeholder="örn. دكك" autocomplete="off">
<h2>DÜĞÜM RENGİ</h2><select id="renkUsul"></select>
<h2>DAİRELERİ GÖSTER (usul)</h2><div id="usuller"></div>
<h2>SEÇİLEN KÖK</h2><div id="bilgi" class="not">Bir düğümün üstüne gel veya tıkla: ait olduğu bütün kategori daireleri çizilir, hepsinin kesişimi gölgelenir.</div>
<h2>KURALLAR</h2>
<div class="not">Her düğüm yalnız dik eksenlerde, izgara noktasına oturur; iki düğüm arası en az <span id="adim"></span> birimdir; bir hücrede en çok bir düğüm bulunur. Her kategorinin dairesi, üyelerinin en küçük çevreleyen dairesidir: bu yüzden bir kök, ait olduğu bütün dairelerin kesişiminde bulunur (<span id="ihlal"></span> ihlâl).</div>
</div>
<div id="sahne"><canvas id="c"></canvas></div>
</div>
<script>
const V=/*VERI*/;
const cv=document.getElementById('c'),cx=cv.getContext('2d');
const css=getComputedStyle(document.documentElement);
function renk(n){return css.getPropertyValue(n).trim()}
let W=0,H=0,dpr=Math.max(1,window.devicePixelRatio||1);
let S=1,TX=0,TY=0;
const cell=new Map();V.dugumler.forEach((d,i)=>cell.set(d.x+','+d.y,i));
const adim=V.olcut.en_az_dugum_arasi_uzaklik;
document.getElementById('adim').textContent=adim;
document.getElementById('ihlal').textContent=V.olcut.daire_disinda_kalan_uyelik;
document.getElementById('ozet').textContent=V.olcut.dugum+' kök · '+V.olcut.sinif+' kategori · '+V.olcut.uyelik+' üyelik';
const goster=new Set();let renkU=1,sec=-1,hov=-1;
const ul=document.getElementById('usuller');
V.usuller.forEach((u,i)=>{const l=document.createElement('label');l.innerHTML='<input type="checkbox" data-u="'+i+'"><span class="sw" style="background:'+u.renk+'"></span>'+u.ad;ul.appendChild(l)});
ul.addEventListener('change',e=>{const i=+e.target.dataset.u;e.target.checked?goster.add(i):goster.delete(i);ciz()});
const rs=document.getElementById('renkUsul');rs.innerHTML='<option value="-1">tek renk</option>'+V.usuller.map((u,i)=>'<option value="'+i+'">'+u.ad+'</option>').join('');
rs.value='1';rs.onchange=()=>{renkU=+rs.value;ciz()};
const palet=['#c0392b','#2471a3','#1e8449','#b9770e','#7d3c98','#117a8b','#a04000','#566573','#b03a6e','#4d6d1f','#8e44ad','#16a085','#d35400','#2c3e50','#7f8c8d','#c0a000'];
function sinifRenk(k){return palet[k%palet.length]}
function fit(){let a=1e9,b=-1e9,c=1e9,d=-1e9;V.dugumler.forEach(n=>{a=Math.min(a,n.x);b=Math.max(b,n.x);c=Math.min(c,n.y);d=Math.max(d,n.y)});S=Math.min(W/(b-a+6),H/(d-c+6));TX=W/2-S*(a+b)/2;TY=H/2-S*(c+d)/2}
function resize(){const r=cv.parentElement.getBoundingClientRect();W=r.width;H=r.height;cv.width=W*dpr;cv.height=H*dpr;ciz()}
const sx=x=>x*S+TX,sy=y=>y*S+TY;
function daire(k,doldur,renkStr,lw){const c=V.siniflar[k];cx.beginPath();cx.arc(sx(c.x),sy(c.y),c.r*S,0,6.2832);if(doldur){cx.fillStyle=renkStr;cx.fill()}else{cx.strokeStyle=renkStr;cx.lineWidth=lw;cx.stroke()}}
function ciz(){
cx.setTransform(dpr,0,0,dpr,0,0);cx.clearRect(0,0,W,H);cx.fillStyle=renk('--bg');cx.fillRect(0,0,W,H);
goster.forEach(ui=>{V.siniflar.forEach((c,k)=>{if(c.u!==ui)return;const x=sx(c.x),y=sy(c.y),r=c.r*S;if(x+r<0||y+r<0||x-r>W||y-r>H||r<3)return;cx.beginPath();cx.arc(x,y,r,0,6.2832);cx.strokeStyle=V.usuller[ui].renk;cx.globalAlpha=.55;cx.lineWidth=1;cx.stroke();cx.globalAlpha=1;if(r>40){cx.fillStyle=V.usuller[ui].renk;cx.font='11px sans-serif';cx.fillText(c.ad+' ('+c.n+')',x-r*0.6,y-r*0.7)}})});
const px=Math.max(1.6,adim*S*0.55);
for(const n of V.dugumler){const x=sx(n.x),y=sy(n.y);if(x<-px||y<-px||x>W+px||y>H+px)continue;
let col=renk('--fg');if(renkU>=0){const k=n.s.find(j=>V.siniflar[j].u===renkU);col=k===undefined?'#bbb':sinifRenk(k)}else if(!n.q)col='#9a8f78';
cx.fillStyle=col;cx.fillRect(x-px/2,y-px/2,px,px)}
if(S*adim>26){cx.font=Math.max(7,Math.min(15,S*adim*0.32))+'px Georgia';cx.textAlign='center';cx.fillStyle=renk('--fg');for(const n of V.dugumler){const x=sx(n.x),y=sy(n.y);if(x<0||y<0||x>W||y>H)continue;cx.fillText(n.k,x,y-px/2-2)}cx.textAlign='start'}
const a=hov>=0?hov:sec;if(a>=0){const n=V.dugumler[a];
cx.save();let ok=true;for(const k of n.s){const c=V.siniflar[k];cx.beginPath();cx.arc(sx(c.x),sy(c.y),c.r*S,0,6.2832);cx.clip()}
cx.fillStyle='rgba(255,200,0,.32)';cx.fillRect(0,0,W,H);cx.restore();
n.s.forEach(k=>{const c=V.siniflar[k];cx.beginPath();cx.arc(sx(c.x),sy(c.y),c.r*S,0,6.2832);cx.strokeStyle=V.usuller[c.u].renk;cx.lineWidth=1.8;cx.stroke()});
cx.beginPath();cx.arc(sx(n.x),sy(n.y),Math.max(6,px),0,6.2832);cx.strokeStyle=renk('--fg');cx.lineWidth=2;cx.stroke()}}
function bilgi(i){const el=document.getElementById('bilgi');if(i<0){el.innerHTML='<span class="not">Bir düğümün üstüne gel veya tıkla.</span>';return}
const n=V.dugumler[i];el.innerHTML='<b class="k">'+n.k+'</b> <span class="not">'+(n.q?'Kur\'ân\'da var':'Kur\'ân\'da yok')+' · '+n.w+' kelime · '+n.g+' geçiş</span><div>'+(n.m||'')+'</div><div style="margin-top:6px">'+n.s.map(k=>{const c=V.siniflar[k];return '<div><span class="sw" style="background:'+V.usuller[c.u].renk+'"></span> '+V.usuller[c.u].ad+': <b>'+c.ad+'</b> <span class="not">('+c.n+')</span></div>'}).join('')+'</div><div class="not" style="margin-top:6px">'+n.s.length+' kategorinin kesişiminde.</div>'}
function ata(mx,my){const wx=(mx-TX)/S,wy=(my-TY)/S;const gx=Math.round(wx/adim)*adim,gy=Math.round(wy/adim)*adim;const i=cell.get(gx+','+gy);return i===undefined?-1:i}
let sur=false,lx=0,ly=0,hareket=0;
cv.addEventListener('pointerdown',e=>{sur=true;lx=e.offsetX;ly=e.offsetY;hareket=0;cv.setPointerCapture(e.pointerId);cv.style.cursor='grabbing'});
cv.addEventListener('pointermove',e=>{if(sur){TX+=e.offsetX-lx;TY+=e.offsetY-ly;hareket+=Math.abs(e.offsetX-lx)+Math.abs(e.offsetY-ly);lx=e.offsetX;ly=e.offsetY;ciz()}else{const i=ata(e.offsetX,e.offsetY);if(i!==hov){hov=i;bilgi(hov>=0?hov:sec);ciz()}}});
cv.addEventListener('pointerup',e=>{sur=false;cv.style.cursor='grab';if(hareket<4){const i=ata(e.offsetX,e.offsetY);sec=i;bilgi(i);ciz()}});
cv.addEventListener('wheel',e=>{e.preventDefault();const f=Math.exp(-e.deltaY*0.0015);const ns=Math.min(80,Math.max(0.3,S*f));TX=e.offsetX-(e.offsetX-TX)*ns/S;TY=e.offsetY-(e.offsetY-TY)*ns/S;S=ns;ciz()},{passive:false});
document.getElementById('ara').addEventListener('input',e=>{const q=e.target.value.trim();if(!q)return;const i=V.dugumler.findIndex(n=>n.k===q);if(i<0)return;sec=i;S=14;TX=W/2-S*V.dugumler[i].x;TY=H/2-S*V.dugumler[i].y;bilgi(i);ciz()});
window.addEventListener('resize',resize);resize();fit();ciz();
</script></body></html>
"""

if __name__ == '__main__':
    yaz()

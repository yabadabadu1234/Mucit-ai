"""Tek komut: python3 zihin_haritasi.py  -> zihin_haritasi.html (bütün köklerin türeme ağaçları, zihin haritası)
   python3 zihin_haritasi.py --png خلق علم ...  -> seçilen köklerin resimleri (zihin_haritasi_png/)"""
import json, sys, pathlib
from agac_oku import oku
HERE = pathlib.Path(__file__).resolve().parent
A = oku()
KOK = HERE.parents[1] / 'kelime_kaydi/kuranda_var/kokler'
SA = HERE / 'secim_agi'; SA.mkdir(exist_ok=True)
BAB = ['sülâsî mücerred', 'sülâsî'] + ['bâb ' + r for r in 'II III IV V VI VII VIII IX X XI XII XIII'.split()]
for k in A:
    m = json.load(open(KOK / f'{k}.json', encoding='utf-8')).get('mustaklar') or {}
    T = {}
    for g, L in m.items():
        kat, _, bab = g.partition(' · '); bab = bab or 'bâbsız'
        T.setdefault(bab, {}).setdefault(kat, [[x[1], x[3]] for x in L])
    sira = sorted(T, key=lambda b: BAB.index(b) if b in BAB else 99)
    (SA / f'{k}.js').write_text('SA[' + json.dumps(k) + ']=' + json.dumps([[b, list(T[b].items())] for b in sira], ensure_ascii=False, separators=(',', ':')) + ';', encoding='utf-8')
HTML = r"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kök Zihin Haritası</title><link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap" rel="stylesheet">
<style>:root{--zemin:#fbf8ef;--yazi:#2b2410;--ince:#8a7f62;--cizgi:#c9bd98}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--zemin:#1d1b16;--yazi:#eee6cf;--ince:#a99f83;--cizgi:#5a5240}}
body{margin:0;background:var(--zemin);color:var(--yazi);font-family:Georgia,serif}
header{display:flex;gap:10px;align-items:center;padding:10px 16px;flex-wrap:wrap}
input{font:inherit;padding:6px 10px;border:1px solid var(--cizgi);border-radius:6px;background:transparent;color:inherit;width:12em}
#liste{display:flex;flex-wrap:wrap;gap:4px;padding:0 16px;max-height:84px;overflow:auto}
#liste a{font-family:Amiri,serif;font-size:18px;cursor:pointer;padding:0 5px;border-radius:4px}
#liste a.sec{background:#b8860b33}
svg{width:100%;height:calc(100vh - 140px);display:block}#ag{display:none;overflow:auto;height:calc(100vh - 140px)}#ag svg{height:auto}
.ar{font-family:Amiri,serif}text{fill:var(--yazi)}path{fill:none}</style></head><body>
<header><a href="../../kuran_hikmetleri_kitap.html" style="color:inherit;margin-right:10px">← Kitap</a><input id="ara" placeholder="kök ara (خلق)"><button id="dug" style="font:inherit;padding:5px 10px">Seçim ağı</button><span id="bilgi" style="color:var(--ince);font-size:14px"></span></header>
<div id="liste"></div><svg id="s"></svg><div id="ag"></div>
<script>const A=__VERI__;
const R=['#b3541e','#2f6fb3','#3f7f3a','#8a3fa0','#b8860b','#2c8c7c','#a0304a','#5a6b2a'];
const s=document.getElementById('s');
function say(n){return 1+n.turev.reduce((a,c)=>a+say(c),0)}
function satir(t,m){const w=t.split(' '),o=[];let b='';for(const x of w){if((b+' '+x).trim().length>m&&b){o.push(b);b=x}else b=(b+' '+x).trim()}o.push(b);return o}
function ciz(k){const W=s.clientWidth,H=s.clientHeight,cx=W/2,cy=H/2,ag=A[k];
 const kok={mana:k,turev:ag};const top=say(kok);let h='';const D=Math.max(...[1,2,3,4].map(d=>d))
 const derin=n=>n.turev.length?1+Math.max(...n.turev.map(derin)):0;const dm=derin(kok);
 const r0=Math.min(W,H)/2-70,adim=r0/Math.max(dm,1);
 function yer(n,a0,a1,d,renk){const a=(a0+a1)/2,r=d*adim,x=cx+r*Math.cos(a),y=cy+r*Math.sin(a);n._x=x;n._y=y;n._a=a;n._d=d;n._r=renk;
  let t=a0;n.turev.forEach((c,i)=>{const p=(a1-a0)*say(c)/(say(n)-1);yer(c,t,t+p,d+1,d==0?R[i%R.length]:renk);t+=p})}
 yer(kok,-Math.PI,Math.PI,0,'#b8860b');
 function ys(n){n.turev.forEach(c=>{const mx=cx+(n._d+.5)*adim*Math.cos(c._a),my=cy+(n._d+.5)*adim*Math.sin(c._a);
  h+=`<path d="M${n._x},${n._y} Q${mx},${my} ${c._x},${c._y}" stroke="${c._r}" stroke-width="${Math.max(1.2,4-c._d)}" opacity=".75"/>`;ys(c)})}
 ys(kok);
 function yz(n){if(n._d==0){h+=`<circle cx="${cx}" cy="${cy}" r="34" fill="#b8860b22" stroke="#b8860b"/><text x="${cx}" y="${cy+12}" text-anchor="middle" font-size="34" class="ar">${k}</text>`}
  else{const ust=n._d==1,sag=Math.cos(n._a)>=0,an=ust?'middle':(sag?'start':'end'),dx=ust?0:(sag?6:-6),L=satir(n.mana,n._d==1?22:28),fs=n._d==1?14:12.5;
   h+=`<circle cx="${n._x}" cy="${n._y}" r="${n._d==1?5:3.2}" fill="${n._r}"/>`;
   L.forEach((l,i)=>h+=`<text x="${n._x+dx}" y="${ust?n._y-12-(L.length-1-i)*fs*1.05:n._y+4+(i-(L.length-1)/2)*fs*1.05}" text-anchor="${an}" paint-order="stroke" stroke="var(--zemin)" stroke-width="4" font-size="${fs}" ${n._d==1?'font-weight="bold"':''}>${l.replace(/</g,'&lt;')}</text>`)}
  n.turev.forEach(yz)}
 yz(kok);s.innerHTML=h;document.getElementById('bilgi').textContent=`${ag.length} asıl · ${top} uç`;
 document.querySelectorAll('#liste a').forEach(a=>a.classList.toggle('sec',a.textContent==k));location.hash=k}
const L=document.getElementById('liste');Object.keys(A).forEach(k=>{const a=document.createElement('a');a.textContent=k;a.onclick=()=>ciz(k);L.appendChild(a)});
document.getElementById('ara').oninput=e=>{const v=e.target.value.trim();if(A[v])ciz(v)};
addEventListener('hashchange',()=>{const k=decodeURIComponent(location.hash.slice(1));if(A[k])ciz(k)});addEventListener('resize',()=>ciz(decodeURIComponent(location.hash.slice(1))||'خلق'));
ciz(decodeURIComponent(location.hash.slice(1))||'خلق');
const SA={};let agAcik=false;
function agYukle(k,f){if(SA[k])return f();const e=document.createElement('script');e.src='secim_agi/'+k+'.js';e.onload=f;document.head.appendChild(e)}
function kol(x,y,ad,cocuk,h){/* Halliday köşeli parantezi */}
function agCiz(k){agYukle(k,()=>{const D=SA[k];let h='',y=20;const S=19,X0=20,X1=150,X2=300,X3=480;
 const satir=D.reduce((a,[b,K])=>a+K.reduce((c,[t,L])=>c+L.length,0)+K.length*0.4+0.8,0);
 const H=satir*S+60,ky=H/2;h+=`<text x="${X0}" y="${ky+8}" font-size="30" class="ar">${k}</text>`;
 const by=[];
 D.forEach(([b,K])=>{const y0=y;const ky2=[];
  K.forEach(([t,L])=>{const t0=y;L.forEach(([ar,tr])=>{h+=`<line x1="${X3-12}" y1="${y}" x2="${X3}" y2="${y}" stroke="var(--cizgi)"/><text x="${X3+90}" y="${y+5}" font-size="17" class="ar" text-anchor="end">${ar}</text><text x="${X3+96}" y="${y+4}" font-size="12.5">(${tr})</text>`;y+=S});
   const m=(t0+y-S)/2;ky2.push(m);h+=`<line x1="${X3-12}" y1="${t0}" x2="${X3-12}" y2="${y-S}" stroke="var(--yazi)"/><line x1="${X2}" y1="${m}" x2="${X3-12}" y2="${m}" stroke="var(--yazi)"/><text x="${X2+6}" y="${m-4}" font-size="12">${t} (${L.length})</text>`;y+=S*0.4});
  const m=(ky2[0]+ky2[ky2.length-1])/2;by.push(m);
  h+=`<line x1="${X2}" y1="${ky2[0]}" x2="${X2}" y2="${ky2[ky2.length-1]}" stroke="#b3541e" stroke-width="1.6"/>`+
   `<line x1="${X1}" y1="${m}" x2="${X2}" y2="${m}" stroke="#b3541e" stroke-width="1.6"/><text x="${X1+6}" y="${m-5}" font-size="13" font-weight="bold">${b}</text>`;y+=S*0.8});
 h+=`<line x1="${X1}" y1="${by[0]}" x2="${X1}" y2="${by[by.length-1]}" stroke="#2f6fb3" stroke-width="2"/><line x1="${X0+70}" y1="${ky}" x2="${X1}" y2="${ky}" stroke="#2f6fb3" stroke-width="2"/>`;
 const n=D.reduce((a,[b,K])=>a+K.reduce((c,[t,L])=>c+L.length,0),0);
 document.getElementById('ag').innerHTML=`<svg viewBox="0 0 1100 ${y+20}" style="width:1100px;max-width:100%;height:auto">${h}</svg>`;document.getElementById('bilgi').textContent=`${D.length} bâb · ${n} müştak`})}
document.getElementById('dug').onclick=()=>{agAcik=!agAcik;document.getElementById('ag').style.display=agAcik?'block':'none';s.style.display=agAcik?'none':'block';document.getElementById('dug').textContent=agAcik?'Türeme ağacı':'Seçim ağı';const k=decodeURIComponent(location.hash.slice(1))||'خلق';agAcik?agCiz(k):ciz(k)};
const eskiCiz=ciz;ciz=function(k){eskiCiz(k);if(agAcik)agCiz(k)};</script></body></html>"""
cikti = HERE / 'zihin_haritasi.html'
cikti.write_text(HTML.replace('__VERI__', json.dumps(A, ensure_ascii=False)), encoding='utf-8')
if '--png' in sys.argv:
    from playwright.sync_api import sync_playwright
    d = HERE / 'zihin_haritasi_png'; d.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'); pass
        for k in [a for a in sys.argv[sys.argv.index('--png') + 1:] if not a.startswith('--')]:
            g = b.new_page(viewport={'width': 1400, 'height': 1000}, device_scale_factor=2)
            g.goto(cikti.as_uri() + '#' + k); g.wait_for_timeout(1200)
            g.evaluate("document.querySelector('header').style.display='none';document.getElementById('liste').style.display='none';document.getElementById('s').style.height='100vh';ciz(decodeURIComponent(location.hash.slice(1)))")
            g.wait_for_timeout(300); g.screenshot(path=str(d / f'{k}.png'))
            if '--ag' in sys.argv:
                g.evaluate("document.getElementById('dug').click()"); g.wait_for_timeout(800)
                g.evaluate("document.getElementById('ag').style.height='auto';document.getElementById('ag').style.display='block'")
                g.locator('#ag svg').screenshot(path=str(d / f'{k}_secim_agi.png'))
        b.close()

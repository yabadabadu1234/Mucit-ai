"""Tek komut: python3 zihin_haritasi.py  -> zihin_haritasi.html (bütün köklerin türeme ağaçları, zihin haritası)
   python3 zihin_haritasi.py --png خلق علم ...  -> seçilen köklerin resimleri (zihin_haritasi_png/)"""
import json, sys, pathlib
from agac_oku import oku
HERE = pathlib.Path(__file__).resolve().parent
A = oku()
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
svg{width:100%;height:calc(100vh - 140px);display:block}
.ar{font-family:Amiri,serif}text{fill:var(--yazi)}path{fill:none}</style></head><body>
<header><input id="ara" placeholder="kök ara (خلق)"><span id="bilgi" style="color:var(--ince);font-size:14px"></span></header>
<div id="liste"></div><svg id="s"></svg>
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
ciz(decodeURIComponent(location.hash.slice(1))||'خلق');</script></body></html>"""
cikti = HERE / 'zihin_haritasi.html'
cikti.write_text(HTML.replace('__VERI__', json.dumps(A, ensure_ascii=False)), encoding='utf-8')
if '--png' in sys.argv:
    from playwright.sync_api import sync_playwright
    d = HERE / 'zihin_haritasi_png'; d.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'); pass
        for k in sys.argv[sys.argv.index('--png') + 1:]:
            g = b.new_page(viewport={'width': 1400, 'height': 1000}, device_scale_factor=2)
            g.goto(cikti.as_uri() + '#' + k); g.wait_for_timeout(1200)
            g.evaluate("document.querySelector('header').style.display='none';document.getElementById('liste').style.display='none';document.getElementById('s').style.height='100vh';ciz(decodeURIComponent(location.hash.slice(1)))")
            g.wait_for_timeout(300); g.screenshot(path=str(d / f'{k}.png'))
        b.close()

"""Harita yazılarının odalarından taşmasını tarayıcıda ölçer (F 3-I 413). Her <text data-r="x,y,w,h"> kutusu odasının içinde kalmalı.
Tek komut: python3 kok_kitabi_tasma.py [kisim_sayisi]; çıktı: taşan yazı sayısı / toplam yazı."""
import sys, glob, json, random
sys.argv = sys.argv[:1] + sys.argv[1:]
import kok_kitabi as K
from playwright.sync_api import sync_playwright

def olc(haritalar, tol=0.004):
    govde = ''.join('<div class="m">%s</div>' % h.svg() for h in haritalar)
    html = '<!doctype html><html><head><meta charset="utf-8"><style>%s body{margin:0}</style></head><body>%s</body></html>' % (K.css('t'), govde)
    P = K.CIKTI / 'gecici' / 'tasma.html'; P.parent.mkdir(exist_ok=True); P.write_text(html, encoding='utf-8')
    C = sorted(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux*/chrome'))[-1]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=C); g = b.new_page(); g.goto(P.as_uri()); g.evaluate('document.fonts.ready')
        r = g.evaluate('''(tol)=>{let n=0,t=0,ex=[];for(const e of document.querySelectorAll('text[data-r]')){if(/^[\u06D6-\u06DC]+$/.test(e.textContent))continue;t++;const [x,y,w,h]=e.dataset.r.split(',').map(Number);const b=e.getBBox();const fs=parseFloat(e.getAttribute('font-size'));const ep=0.15*fs+0.004*w;
          if(b.x<x-ep||b.x+b.width>x+w+ep){n++;if(ex.length<5)ex.push([e.textContent.slice(0,20),+(b.x-x).toFixed(2),+((x+w)-(b.x+b.width)).toFixed(2),+(b.y-y).toFixed(2),+((y+h)-(b.y+b.height)).toFixed(2)])}}return [n,t,ex]}''', tol)
        b.close()
    return r

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    ks = [(s, i) for s in range(1, 115) for i in range(len(K.KI[s]))]
    random.Random(3).shuffle(ks); H = []
    for s, i in ks[:n]:
        k = K.KI[s][i]
        for pc in K.kisim_parcalari(k)[:2]: H.append(K.harita_kisim(k, pc))
    yk = [a for a in K.ORD][::97]
    for key in yk: H.append(K.harita_ayet_odasi(key, 100, 70))
    n_, t_, ex = olc(H)
    print('taşan yazı %d / %d  (%d harita)' % (n_, t_, len(H))); print(ex)
    sys.exit(0 if n_ == 0 else 1)

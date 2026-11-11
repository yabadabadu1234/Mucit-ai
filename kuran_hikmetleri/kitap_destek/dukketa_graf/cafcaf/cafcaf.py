import base64,pathlib
from playwright.sync_api import sync_playwright
D=pathlib.Path(__file__).parent
def ar(a,m,note=''):
    return f'<div class="r"><span class="a">{a}</span><span class="m">{m}</span><span class="n">{note}</span></div>'
def panel(cls,title,sub,rows):
    return f'<section class="p {cls}"><h3>{title}<small>{sub}</small></h3>'+''.join(ar(*r) for r in rows)+'</section>'
# ● lügat/Kur'ân'da görüldü, ○ kalıptan türetildi
P1=panel('b','İSM-İ FÂİL','dâkk · yapan',[
 ('دَاكّ','dâkk','○ müzekker'),('دَاكَّة','dâkka','○ müennes · tâ-i merbûta'),
 ('دَاكَّانِ / دَاكَّيْنِ','dâkkân / dâkkeyn','○ tesniye'),
 ('دَاكُّونَ / دَاكِّينَ','dâkkûn / dâkkîn','○ cem\'-i sâlim müzekker'),
 ('دَاكَّات','dâkkât','○ cem\'-i sâlim müennes'),
 ('دُكَّاك','dukkâk','○ cem\'-i mükesser fu‘‘âl')])
P2=panel('r','İSM-İ MEF‘ÛL','madkûk · yapılan',[
 ('مَدْكُوك','medkûk','○ müzekker'),('مَدْكُوكَة','medkûka','○ müennes'),
 ('مَدْكُوكَانِ','medkûkân','○ tesniye'),('مَدْكُوكُونَ','medkûkûn','○ cem\'-i sâlim'),
 ('مَدْكُوكَات','medkûkât','○ cem\'-i sâlim müennes'),
 ('مُنْدَكّ','mündekk','● mutâvaa fâili · ezilen')])
P3=panel('o','MEKÂN · ZAMAN · ÂLET · SIFAT','maf‘al · mif‘âl · fa‘îl',[
 ('مَدَكّ','medekk','○ mekân-zaman · ezme yeri'),('مَدِكّ','medikk','○ mekân-zaman'),
 ('مِدَكّ','midekk','○ âlet · mif‘al'),('مِدَكَّة','midekka','○ âlet · mif‘ale'),
 ('دَكِيك','dekîk','○ sıfat-ı müşebbehe'),('دَكِيكَة','dekîka','○ müennes')])
P4=panel('g','MÜBALAĞA · TAFDÎL · SAYI','fa‘‘âl · af‘al · fu‘lâ',[
 ('دَكَّاك','dekkâk','○ mübalağa · çok ezen'),('دَكَّاكَة','dekkâka','○ mübalağa · tâ-i merbûta'),
 ('أَدَكّ','edekk','○ tafdîl · en ezici'),('دُكَّى','dukkâ','○ tafdîl müennes'),
 ('دَكَّاءُ','dekkâ\'','● ezilmiş düz yer · Kur\'ân'),('دَكَّة','dekke','● merre · tek eziş')])
P5=panel('b','MASDARLAR – MÜCERRED · MEZÎD','bâb bâb',[
 ('دَكّ','dekk','● mücerred'),('دُكُوك / دِكَاك','dukûk / dikâk','● cem\''),
 ('تَدْكِيك','tedkîk','○ tef‘îl'),('مُدَاكَّة','mudâkka','○ müfâale'),
 ('إِدْكَاك','idkâk','○ if‘âl'),('تَدَكُّك','tedekkuk','○ tefa‘‘ul')])
P6=panel('r','MASDARLAR – MEZÎD · RUBÂ‘Î','bâb bâb',[
 ('تَدَاكُّ','tedâkk','○ tefâ‘ul'),('انْدِكَاك','indikâk','○ infi‘âl · ezilme'),
 ('ادِّكَاك','iddikâk','○ ifti‘âl'),('اسْتِدْكَاك','istidkâk','○ istif‘âl'),
 ('دَكْدَكَة','dekdeke','● rubâ‘î · sarsıp ezme'),('تَدَكْدُك','tedekdük','○ tefa‘lul')])
CSS='''
@page{size:A4 landscape;margin:0}
*{box-sizing:border-box}
body{margin:0;font-family:"DejaVu Sans",sans-serif}
.pg{width:297mm;height:210mm;position:relative;page-break-after:always;overflow:hidden;padding:11mm 13mm;
 background:radial-gradient(circle at 50% 0%,#1d3a6b 0%,#0b1a38 70%);color:#f3e6bd}
.pg.k{background:radial-gradient(circle at 50% 0%,#f7ecc8 0%,#e3cf98 80%);color:#3a2a0c}
.fr{position:absolute;inset:4mm;border:1.2mm double #d4af37;border-radius:3mm;pointer-events:none}
.fr:after{content:"";position:absolute;inset:2mm;border:.4mm solid #d4af37;border-radius:2mm}
.c{position:absolute;font-size:15mm;color:#d4af37;line-height:1}
.c1{left:6mm;top:3mm}.c2{right:6mm;top:3mm}.c3{left:6mm;bottom:2mm}.c4{right:6mm;bottom:2mm}
h1{margin:0;text-align:center;font-size:12mm;letter-spacing:1mm;color:#ffd96a;text-shadow:0 .6mm 0 #000a}
.k h1{color:#7a4a00;text-shadow:none}
h2{margin:1mm 0 4mm;text-align:center;font-weight:normal;font-size:4.2mm;color:#e9d8a0}
.k h2{color:#6b4c14}
.orn{text-align:center;color:#d4af37;font-size:5mm;letter-spacing:3mm;margin-bottom:3mm}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm}
.p{border-radius:3mm;padding:2.5mm 3mm;border:.6mm solid #d4af37;box-shadow:0 1mm 3mm #0008;color:#fff}
.p h3{margin:0 0 2mm;font-size:4mm;text-align:center;border-bottom:.4mm solid #ffffff88;padding-bottom:1.2mm}
.p h3 small{display:block;font-weight:normal;font-size:3mm;opacity:.85}
.b{background:linear-gradient(#2f6fd0,#1b4592)}.r{background:linear-gradient(#d04545,#8f2222)}
.o{background:linear-gradient(#f0902a,#b05c0a)}.g{background:linear-gradient(#35a85f,#1d6d3b)}
.r .a,.a{}
.p .r{display:grid;grid-template-columns:1fr auto;grid-template-rows:auto auto;align-items:baseline;
 background:#ffffff1c;border-radius:1.5mm;margin:1.2mm 0;padding:1mm 2mm}
.a{grid-row:1/3;grid-column:2;direction:rtl;font-size:7mm;color:#fff2b0;text-align:right;padding-left:3mm}
.m{font-weight:bold;font-size:3.7mm}.n{font-size:2.7mm;opacity:.9}
.leg{position:absolute;bottom:9mm;left:0;right:0;text-align:center;font-size:3.2mm}
table{width:100%;border-collapse:collapse;font-size:4.6mm;background:#fff8;color:#2b1d05}
th{background:#7a4a00;color:#ffe9a8;padding:2mm}td{border:.3mm solid #b38b2a;padding:4mm 3mm;vertical-align:top}
td.x{direction:rtl;font-size:8mm;text-align:right}
.im{display:block;margin:0 auto;max-width:100%;max-height:150mm;border:.8mm solid #d4af37;border-radius:2mm;background:#0f1720}
'''
def frame(inner,cls=''):
    return f'<div class="pg {cls}"><div class="fr"></div><span class="c c1">❖</span><span class="c c2">❖</span><span class="c c3">❖</span><span class="c c4">❖</span>{inner}</div>'
head='<h1>دَكّ · DEKK KÖKÜ MÜŞTAKLARI</h1>'
pg1=frame(head+'<h2>Kök müştakları – ism-i fâil · mef‘ûl · mekân · âlet · sıfat · mübalağa · tafdîl</h2><div class="orn">✦ ✦ ✦</div><div class="grid">'+P1+P2+P3+'</div><div class="leg">● lügat veya Kur\'ân\'da görüldü &nbsp; ○ kalıptan türetildi, yoklanmadı</div>')
def row(*c): return '<tr>'+''.join(f'<td class="x">{x}</td>' if i==0 else f'<td>{x}</td>' for i,x in enumerate(c))+'</tr>'
T=('<table><tr><th>Ferd</th><th>Tesniye</th><th>Cem\'-i sâlim</th><th>Cem\'-i mükesser (kalıp)</th><th>Cinsiyet</th></tr>'
 +row('دَاكّ','دَاكَّانِ / دَاكَّيْنِ','دَاكُّونَ / دَاكِّينَ','دُكَّاك – fu‘‘âl ○','müzekker, hakîkî')
 +row('دَاكَّة','دَاكَّتَانِ / دَاكَّتَيْنِ','دَاكَّات','دَوَاكّ – fevâ‘il ○','müennes, tâ-i merbûta')
 +row('مَدْكُوك','مَدْكُوكَانِ','مَدْكُوكُونَ','مَدَاكِيك – mefâ‘îl ○','müzekker')
 +row('دَكّ (masdar)','دَكَّانِ','—','دُكُوك / دِكَاك ●','masdar: tesniye/cem‘ ancak kalıpla')
 +row('دَكَّاء ●','دَكَّاوَانِ','—','دَكَاوَات ○','müennes, elif-i memdûde')
 +'</table>')
pg1b=frame(head+'<h2>Mübalağa · tafdîl · masdarlar – bâb bâb</h2><div class="orn">✦ ✦ ✦</div><div class="grid">'+P4+P5+P6+'</div><div class="leg">● lügat veya Kur\'ân\'da görüldü &nbsp; ○ kalıptan türetildi, yoklanmadı</div>')
pg2=frame('<h1>CEM‘ VE TESNİYE · CİNSİYET</h1><h2>Dersin kaideleri dekk köküne vurulur</h2><div class="orn">✦ ✦ ✦</div>'+T+
 '<div class="leg">Uyum: akıl sahibi olmayan çoğul sıfatı müfred müennes alır · ● görüldü ○ türetildi</div>','k')
from PIL import Image
import io
im=Image.open(D.parent/'sil3.png');w,h=im.size;m=h//2
def b6(x):
    f=io.BytesIO();x.save(f,'PNG');return base64.b64encode(f.getvalue()).decode()
A=b6(im.crop((0,0,w,m+40)));B=b6(im.crop((0,m-40,w,h)))
pg3=frame('<h1>SİLSİLE · BİÇİMDEN MANAYA</h1><h2>önce biçim kolları, sonra mana: hakîkî · mecâz · örfî</h2><div style="display:flex;gap:4mm;justify-content:center"><img class="im" style="max-width:48%;max-height:158mm" src="data:image/png;base64,'+A+'"><img class="im" style="max-width:48%;max-height:158mm" src="data:image/png;base64,'+B+'"></div>')
html=f'<html><meta charset="utf-8"><style>{CSS}</style><body>{pg1}{pg1b}{pg2}{pg3}</body></html>'
(D/'cafcaf.html').write_text(html,encoding='utf-8')
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium');pg=b.new_page(viewport={'width':1123,'height':794},device_scale_factor=2)
    pg.goto('file://'+str(D/'cafcaf.html'));pg.pdf(path=str(D/'cafcaf.pdf'),width='297mm',height='210mm',print_background=True)
    for i,e in enumerate(pg.query_selector_all('.pg')): e.screenshot(path=str(D/f'cafcaf_{i+1}.png'))
    b.close()

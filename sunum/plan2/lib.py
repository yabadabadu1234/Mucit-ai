import html
CSS = r'''
@page { size: 1600px 900px; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: "Inter", "DejaVu Sans", sans-serif; color: #1B2733; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.slide { width: 1600px; height: 900px; position: relative; overflow: hidden; page-break-after: always; background: #FFFFFF; padding: 58px 92px 70px 92px; }
.slide.dark { background: #121E2B; color: #fff; }
.kick { font-size: 17px; letter-spacing: 3px; font-weight: 700; color: #0E6E6A; text-transform: uppercase; margin-bottom: 8px; }
.dark .kick { color: #7AD0C8; }
h1 { font-family: "DejaVu Serif", Georgia, serif; font-size: 46px; line-height: 1.16; margin: 0 0 22px 0; color: #121E2B; font-weight: 700; }
.dark h1 { color: #fff; font-size: 84px; line-height: 1.05; }
.body { font-size: 25px; line-height: 1.42; }
.body p { margin: 0 0 14px 0; }
.small { font-size: 20px; line-height: 1.4; }
.tiny { font-size: 17px; line-height: 1.35; color: #5B6773; }
.foot { position: absolute; left: 92px; right: 92px; bottom: 22px; border-top: 1px solid #D5DBE0; padding-top: 8px; font-size: 16px; color: #6B7783; display: flex; justify-content: space-between; }
.src { position: absolute; left: 92px; right: 92px; bottom: 54px; font-size: 16px; line-height: 1.35; color: #5B6773; }
.cols { display: flex; gap: 44px; }
.col { flex: 1; }
.label { font-size: 17px; letter-spacing: 2.4px; font-weight: 700; color: #0E6E6A; text-transform: uppercase; margin-bottom: 8px; }
.card { border: 2px solid #CBD5DB; border-radius: 14px; padding: 16px 22px; background: #fff; }
.card.teal { border-color: #0E6E6A; background: #EAF5F4; }
.card.amber { border-color: #B25E00; background: #FDF0DF; }
.card.navy { border-color: #121E2B; background: #121E2B; color: #fff; }
.card.dash { border-style: dashed; border-color: #AEBBC6; background: #F5F9FC; }
.bar { border-left: 8px solid #0E6E6A; background: #E8F4F3; padding: 14px 22px; border-radius: 0 10px 10px 0; font-size: 24px; line-height: 1.38; }
.bar.amber { border-color: #B25E00; background: #FDF0DF; }
.bar.navy { border-color: #121E2B; background: #E9EEF3; }
.chip { display: inline-block; font-size: 14px; font-weight: 800; letter-spacing: 1.4px; padding: 3px 11px; border-radius: 20px; color: #fff; vertical-align: middle; text-transform: uppercase; white-space: nowrap; }
.chip.certain { background: #1B7F4B; } .chip.strong { background: #0E6E6A; } .chip.probable { background: #B25E00; } .chip.support { background: #6B7783; }
.chip.no { background: #A63030; } .chip.part { background: #7A5C00; } .chip.out { background: #4A5F73; } .chip.yes { background: #1B7F4B; }
em.t, .t { font-style: italic; color: #0E6E6A; }
.ar { font-family: "DejaVu Sans", "FreeSerif", serif; direction: rtl; font-size: 30px; color: #121E2B; }
table { border-collapse: collapse; width: 100%; font-size: 21px; line-height: 1.32; }
th { background: #121E2B; color: #fff; text-align: left; padding: 10px 14px; font-weight: 700; font-size: 18px; letter-spacing: 1px; }
td { border-bottom: 1px solid #D5DBE0; padding: 10px 14px; vertical-align: top; }
table.tight td { padding: 6px 12px; }
td.k { font-weight: 700; color: #0E6E6A; white-space: nowrap; }
ol.prem { margin: 0; padding-left: 0; list-style: none; counter-reset: p; }
ol.prem li { counter-increment: p; position: relative; padding: 9px 14px 9px 66px; border-bottom: 1px solid #E2E7EB; font-size: 23px; line-height: 1.36; }
ol.prem li::before { content: attr(data-n); position: absolute; left: 6px; top: 9px; font-weight: 800; color: #0E6E6A; font-size: 20px; }
ol.prem li.concl { background: #EAF5F4; border-bottom: none; font-weight: 700; border-radius: 0 0 10px 10px; }
ul.b { margin: 0; padding-left: 28px; } ul.b li { margin-bottom: 9px; }
b.v { color: #0E6E6A; } .mono { font-family: "DejaVu Sans Mono", monospace; }
.formula { font-family: "DejaVu Serif", serif; font-size: 34px; text-align: center; padding: 14px; background: #F2F6F9; border-radius: 10px; margin: 10px 0 14px 0; }
.q { font-weight: 800; }
.verdict { margin-left: 10px; }
.qa { border-bottom: 1px solid #D5DBE0; padding: 11px 0; font-size: 22px; line-height: 1.34; }
.qa .qq { font-weight: 800; color: #121E2B; }
'''
def esc(s): return html.escape(s)
CHIP = {"certain": "CERTAIN", "strong": "STRONG", "probable": "PROBABLE", "support": "SUPPORT ONLY", "no": "REJECTED", "part": "ACCEPTED IN PART", "out": "OUT OF SCOPE", "yes": "ACCEPTED"}
def chip(k, text=None): return '<span class="chip %s">%s</span>' % (k, text or CHIP[k])
SLIDES = []
def slide(kicker, title, body, src=None, cls=""):
    SLIDES.append(dict(kicker=kicker, title=title, body=body, src=src, cls=cls))
def raw(htmltxt): SLIDES.append(dict(raw=htmltxt))
def assemble(path):
    n = len(SLIDES); out = ['<!doctype html><html><head><meta charset="utf-8"><title>Planned Obsolescence</title><style>' + CSS + '</style></head><body>']
    k = 0
    for s in SLIDES:
        k += 1
        if "raw" in s:
            out.append(s["raw"].replace("@N@", "%d / %d" % (k, n)))
            continue
        src = '<div class="src">%s</div>' % s["src"] if s["src"] else ""
        out.append('<section class="slide %s"><div class="kick">%s</div><h1>%s</h1><div class="body">%s</div>%s<div class="foot"><span>Planned Obsolescence</span><span>%d / %d</span></div></section>' % (s["cls"], s["kicker"], s["title"], s["body"], src, k, n))
    out.append("""<script>
(function(){
const MAXZ=1.45;
const res=[];
document.querySelectorAll('.slide').forEach((s,idx)=>{
  const body=s.querySelector('.body'); if(!body) return;
  const st=s.getBoundingClientRect().top;
  const src=s.querySelector('.src'); const foot=s.querySelector('.foot');
  const limit=(src?src.getBoundingClientRect().top:foot.getBoundingClientRect().top)-st-10;
  const W=body.getBoundingClientRect().width;
  function bottom(){let m=0;body.querySelectorAll('*').forEach(e=>{const r=e.getBoundingClientRect();if(r.height>0)m=Math.max(m,r.bottom-st)});return m;}
  let z=MAXZ;
  while(z>1.0){body.style.width=(W/z)+'px';body.style.transform='scale('+z+')';body.style.transformOrigin='0 0';if(bottom()<=limit)break;z-=0.02;}
  if(z<=1.0){z=1;body.style.width=W+'px';body.style.transform='none';}
  const b=bottom(); if(b>limit+2) res.push([idx+1,Math.round(b),Math.round(limit)]);
});
document.title="OVER:"+JSON.stringify(res);
})();
</script>""")
    out.append('</body></html>')
    open(path, "w").write("\n".join(out))
# --- SVG helpers
def svg_node(x, y, w, h, lines, cls="n"):
    fills = {"n": ("#FFFFFF", "#6B7783", "#121E2B"), "t": ("#EAF5F4", "#0E6E6A", "#0E6E6A"), "a": ("#FDF0DF", "#B25E00", "#8A4800"), "d": ("#121E2B", "#121E2B", "#FFFFFF"), "g": ("#EEF1F4", "#8A97A3", "#4A5F73")}
    f, s, c = fills[cls]
    out = '<rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" stroke="%s" stroke-width="2.4"/>' % (x, y, w, h, f, s)
    n = len(lines); lh = 27
    for i, (t, bold) in enumerate(lines):
        yy = y + h / 2 + (i - (n - 1) / 2) * lh + 7
        out += '<text x="%d" y="%d" text-anchor="middle" font-size="%d" font-weight="%s" fill="%s" font-family="Inter, DejaVu Sans, sans-serif">%s</text>' % (x + w / 2, yy, 22 if bold else 19, 700 if bold else 400, c, esc(t))
    return out
def svg_line(x1, y1, x2, y2, label=None, arrow=True, lx=None, ly=None):
    out = '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#6B7783" stroke-width="2.4" %s/>' % (x1, y1, x2, y2, 'marker-end="url(#ar)"' if arrow else "")
    if label:
        out += '<text x="%d" y="%d" font-size="17" fill="#4A5F73" font-family="Inter, sans-serif" font-weight="700">%s</text>' % (lx if lx is not None else (x1 + x2) / 2 + 6, ly if ly is not None else (y1 + y2) / 2 - 6, esc(label))
    return out
DEFS = '<defs><marker id="ar" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#6B7783"/></marker></defs>'

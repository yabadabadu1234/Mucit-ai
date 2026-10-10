import re,os,subprocess,html,shutil,pymupdf
K=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT=os.path.dirname(os.path.abspath(__file__))
CH="/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
CSS="""@page{size:A4;margin:18mm 16mm}body{font-family:'DejaVu Sans','Noto Sans',Arial,sans-serif;font-size:10.5pt;line-height:1.45;color:#111}
h1{font-size:17pt;color:#1f3a5f;border-bottom:2px solid #1f3a5f;padding-bottom:4px}h2{font-size:13.5pt;color:#1f3a5f;margin-top:18px}h3{font-size:11.5pt;color:#1f3a5f}
table{border-collapse:collapse;width:100%;margin:8px 0;font-size:9pt}th,td{border:1px solid #b9c3d0;padding:4px 6px;vertical-align:top;text-align:left}th{background:#eef2f7}
blockquote{margin:6px 0 6px 6px;padding:2px 10px;border-left:3px solid #9fb2c9;background:#f6f8fb;font-size:9.8pt}code{font-family:'DejaVu Sans Mono',monospace;font-size:9pt;background:#f1f1f1;padding:0 2px}
hr{border:0;border-top:1px solid #ccc}p{margin:5px 0}li{margin:2px 0}"""
def tex(s):
    s=re.sub(r"\$\$(.+?)\$\$",lambda m:"<div style='margin:6px 20px;font-style:italic'>"+texc(m.group(1))+"</div>",s,flags=re.S)
    s=re.sub(r"\$(.+?)\$",lambda m:"<i>"+texc(m.group(1))+"</i>",s)
    return s
def texc(t):
    for a,b in [(r"\times","×"),(r"\implies","⟹"),(r"\iff","⟺"),(r"\cdot","·"),(r"\text{","{"),(r"\geq","≥"),(r"\leq","≤"),(r"\,"," "),("{,}",","),(r"\mathcal","")]: t=t.replace(a,b)
    t=re.sub(r"\\text\{([^}]*)\}",r"\1",t); t=t.replace("{","").replace("}","").replace("\\","")
    return html.escape(t)
def inline(s):
    s=html.escape(s,quote=False)
    s=re.sub(r"`([^`]+)`",r"<code>\1</code>",s); s=re.sub(r"\*\*(.+?)\*\*",r"<b>\1</b>",s); s=re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])",r"<i>\1</i>",s)
    s=re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",r'<a href="\2">\1</a>',s)
    return s
def md2html(md):
    md=tex(md)
    L=md.split("\n"); out=[]; i=0
    while i<len(L):
        l=L[i]
        if l.startswith("```"):
            j=i+1; buf=[]
            while j<len(L) and not L[j].startswith("```"): buf.append(L[j]); j+=1
            out.append("<pre>"+html.escape("\n".join(buf))+"</pre>"); i=j+1; continue
        if re.match(r"^#{1,6} ",l):
            n=len(l.split(" ")[0]); out.append("<h%d>%s</h%d>"%(n,inline(l[n+1:]),n)); i+=1; continue
        if l.strip()=="---": out.append("<hr>"); i+=1; continue
        if l.startswith("|") and i+1<len(L) and re.match(r"^\|[\s:|-]+\|$",L[i+1].strip()):
            hd=[c.strip() for c in l.strip().strip("|").split("|")]; j=i+2; rows=[]
            while j<len(L) and L[j].startswith("|"): rows.append([c.strip() for c in L[j].strip().strip("|").split("|")]); j+=1
            t="<table><tr>"+"".join("<th>"+inline(c)+"</th>" for c in hd)+"</tr>"
            for r in rows: t+="<tr>"+"".join("<td>"+inline(c)+"</td>" for c in r)+"</tr>"
            out.append(t+"</table>"); i=j; continue
        if l.startswith(">"):
            buf=[]
            while i<len(L) and L[i].startswith(">"): buf.append(L[i][1:].lstrip()); i+=1
            out.append("<blockquote>"+"<br>".join(inline(b) for b in buf if b!="" )+"</blockquote>"); continue
        m=re.match(r"^(\s*)([-*]|\d+\.) (.*)",l)
        if m:
            tag="ol" if m.group(2)[0].isdigit() else "ul"; buf=[]
            while i<len(L) and re.match(r"^(\s*)([-*]|\d+\.) (.*)",L[i]): buf.append(re.match(r"^(\s*)([-*]|\d+\.) (.*)",L[i]).group(3)); i+=1
            out.append("<%s>"%tag+"".join("<li>"+inline(b)+"</li>" for b in buf)+"</%s>"%tag); continue
        if l.strip()=="": i+=1; continue
        buf=[l]; i+=1
        while i<len(L) and L[i].strip()!="" and not re.match(r"^(#{1,6} |\||>|```|---$|(\s*)([-*]|\d+\.) )",L[i]): buf.append(L[i]); i+=1
        out.append("<p>"+inline(" ".join(buf))+"</p>")
    return "\n".join(out)
def pdf(md_path,ad,baslik=None):
    md=open(os.path.join(K,md_path)).read()
    h="<!doctype html><meta charset=utf-8><style>"+CSS+"</style>"+md2html(md)
    hp=os.path.join("/tmp/claude-0/-home-user-Mucit-ai/8369fb4b-b4f0-5e7d-9664-c411e733fa67/scratchpad",ad+".html"); open(hp,"w").write(h)
    subprocess.run([CH,"--headless","--no-sandbox","--disable-gpu","--no-pdf-header-footer","--print-to-pdf="+os.path.join(OUT,ad+".pdf"),"file://"+hp],check=True,capture_output=True)
    print(ad,os.path.getsize(os.path.join(OUT,ad+".pdf"))//1024,"KB")
if __name__=="__main__":
    pdf("CIMER/CIMER_MURACAAT_METNI_3000_KELIME.md","00_CIMER_Muracaat_Metni")
    pdf("DEVLETE_SUNULACAK_METIN.md","01_Kanun_Teklifi_Taslagi")
    pdf("DELIL_EKI.md","02_Delil_Eki")
    pdf("TEBLIG_TASLAGI.md","03_Teblig_Taslagi")
    pdf("KOMISYON_PAKETI.md","04_Komisyon_Paketi")
    pdf("MALI_MODEL/MALI_MODEL.md","05_Mali_Model")
    pdf("TEHLIKE_DEFTERI_DEVLET.md","07_Kalan_Riskler_Defteri")
    shutil.copy(os.path.join(K,"GORSELLER/GORSEL_EK.pdf"),os.path.join(OUT,"06_Gorsel_Ek.pdf"))
    shutil.copy(os.path.join(K,"MALI_MODEL/MIKRO_MUKELLEF_MALI_MODEL.xlsx"),os.path.join(OUT,"05b_Mali_Model_Excel.xlsx"))
    shutil.copy("/root/.claude/uploads/8369fb4b-b4f0-5e7d-9664-c411e733fa67/1df9a5b6-image.png",os.path.join(OUT,"08_TBMM_hata_ekran_goruntusu.png"))
    m=pymupdf.open()
    for f in ["01_Kanun_Teklifi_Taslagi","02_Delil_Eki","03_Teblig_Taslagi","04_Komisyon_Paketi","05_Mali_Model","06_Gorsel_Ek","07_Kalan_Riskler_Defteri"]:
        m.insert_pdf(pymupdf.open(os.path.join(OUT,f+".pdf")))
    m.save(os.path.join(OUT,"09_EK_PAKET_TUMU.pdf"),garbage=4,deflate=True); print("09 tümü",len(m),"sayfa",os.path.getsize(os.path.join(OUT,"09_EK_PAKET_TUMU.pdf"))//1024,"KB")

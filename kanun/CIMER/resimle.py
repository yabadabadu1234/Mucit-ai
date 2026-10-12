import os,sys,subprocess,glob,html,shutil,re
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','EKLER_PDF'))
import uret, pymupdf
from PIL import Image
K=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R=os.path.join(K,'CIMER','RESIM')
TMP="/tmp/claude-0/-home-user-Mucit-ai/8369fb4b-b4f0-5e7d-9664-c411e733fa67/scratchpad"
os.makedirs(TMP,exist_ok=True)
CH=uret.CH
INDEKS=[]
def pdf_to_png(pdf,klasor,onek):
    d=pymupdf.open(pdf); out=os.path.join(R,klasor); os.makedirs(out,exist_ok=True)
    for i,pg in enumerate(d):
        pm=pg.get_pixmap(dpi=150); fn=os.path.join(out,"%s_%03d.png"%(onek,i+1)); pm.save(fn)
        im=Image.open(fn).convert('RGB').quantize(colors=128,method=Image.Quantize.MEDIANCUT); im.save(fn,optimize=True)
    return len(d)
def chrome_pdf(htmlpath,pdfpath):
    subprocess.run([CH,"--headless","--no-sandbox","--disable-gpu","--no-pdf-header-footer","--print-to-pdf="+pdfpath,"file://"+htmlpath],check=True,capture_output=True)
def md_belge(md_path,klasor,onek,baslik):
    md=open(os.path.join(K,md_path)).read()
    h="<!doctype html><meta charset=utf-8><style>"+uret.CSS+"</style>"+uret.md2html(md)
    hp=os.path.join(TMP,onek+".html"); open(hp,"w").write(h); pp=os.path.join(TMP,onek+".pdf"); chrome_pdf(hp,pp)
    n=pdf_to_png(pp,klasor,onek); INDEKS.append((klasor,baslik,md_path,n)); print(klasor,onek,n)
KOD_CSS="""@page{size:A4;margin:12mm 10mm}body{font-family:'DejaVu Sans Mono',monospace;font-size:7.6pt;line-height:1.28;color:#111}
pre{margin:0;white-space:pre-wrap;word-break:break-all}.n{color:#888;display:inline-block;width:3.2em;text-align:right;margin-right:.8em}h1{font-family:'DejaVu Sans',sans-serif;font-size:11pt;color:#1f3a5f;border-bottom:1px solid #1f3a5f}"""
def kod_belge(yol,klasor,onek,baslik):
    t=open(os.path.join(K,yol),errors='replace').read().split('\n')
    body="<h1>%s</h1><pre>"%html.escape(yol)+"\n".join("<span class=n>%d</span>%s"%(i+1,html.escape(l)) for i,l in enumerate(t))+"</pre>"
    hp=os.path.join(TMP,onek+".html"); open(hp,"w").write("<!doctype html><meta charset=utf-8><style>"+KOD_CSS+"</style>"+body); pp=os.path.join(TMP,onek+".pdf"); chrome_pdf(hp,pp)
    n=pdf_to_png(pp,klasor,onek); INDEKS.append((klasor,baslik,yol,n)); print(klasor,onek,n)
def resim_kopya(yol,klasor,ad,baslik):
    out=os.path.join(R,klasor); os.makedirs(out,exist_ok=True); shutil.copy(os.path.join(K,yol),os.path.join(out,ad)); INDEKS.append((klasor,baslik,yol,1))
if __name__=="__main__":
    secim=sys.argv[1:] or ["belge","kod","grafik"]
    if "belge" in secim:
        for md,kl,ok,bs in [("CIMER/CIMER_MURACAAT_METNI_3000_KELIME.md","A_MURACAAT_METNI","A","Müracaat metni (ayrıntılı)"),
          ("DEVLETE_SUNULACAK_METIN.md","B_KANUN_TEKLIFI","B","Kanun teklifi taslağı, gerekçeler, mali matematik, risk cetveli"),
          ("TEKLIF_EK_TEK_KAPI.md","B2_EK_MADDELER","B2","Ek maddeler taslağı (tek kapı, ortaklık türleri, sahtekârlığa karşı maddeler)"),
          ("DELIL_EKI.md","C_DELIL_EKI","C","Delil eki: dayanak kanun metinleri"),
          ("TEBLIG_TASLAGI.md","D_TEBLIG","D","Tebliğ taslağı"),
          ("KOMISYON_PAKETI.md","E_KOMISYON_PAKETI","E","Komisyon paketi"),
          ("MALI_MODEL/MALI_MODEL.md","F_MALI_MODEL","F1","Mali etki modeli"),
          ("MALI_MODEL/DUYARLILIK_TABLOLARI.md","F_MALI_MODEL","F2","Parametre duyarlılık tabloları (tek tek)"),
          ("MALI_MODEL/GENC3_RAPOR.md","F_MALI_MODEL","F3","Genç seyri modeli raporu"),
          ("EMEKLILIK_HESABI.md","F_MALI_MODEL","F4","Emeklilik hesabı"),
          ("MALI_MODEL/GUNCEL_MODEL.md","F_MALI_MODEL","F5","Güncel model notları (N, Fransa karşılaştırması)"),
          ("MALI_MODEL/KATILIM_HAVUZU.md","F_MALI_MODEL","F6","Katılım havuzu (yaş sınıfları)"),
          ("DENETIM_RAPORU.md","F_MALI_MODEL","F7","Denetim raporu"),
          ("BARIYER_ENVANTERI.md","F_MALI_MODEL","F8","Bariyer envanteri"),
          ("SAHTEKARLIK_IMKANSIZLIK_TEOREMI.md","F_MALI_MODEL","F9","Sahtekârlık imkânsızlık önermesi"),
          ("TEHLIKE_DEFTERI_DEVLET.md","H_KALAN_RISKLER","H","Kalan riskler defteri")]:
            md_belge(md,kl,ok,bs)
    if "kod" in secim:
        mm=sorted(glob.glob(os.path.join(K,'MALI_MODEL','*.py')))
        for i,f in enumerate(mm): kod_belge(os.path.relpath(f,K),"I_KOD","K%02d"%(i+1),"Kod: "+os.path.basename(f))
        for i,f in enumerate(sorted(glob.glob(os.path.join(K,'GORSELLER','kaynak','*.py'))+glob.glob(os.path.join(K,'EKLER_PDF','uret.py'))+[os.path.join(K,'CIMER','resimle.py'),os.path.join(K,'CIMER','kapak.py')])):
            if os.path.exists(f): kod_belge(os.path.relpath(f,K),"I_KOD","KG%02d"%(i+1),"Kod: "+os.path.basename(f))
        cikti=sorted(glob.glob(os.path.join(K,'MALI_MODEL','*_out.txt'))+glob.glob(os.path.join(K,'MALI_MODEL','*cikti.txt')))
        for i,f in enumerate(cikti): kod_belge(os.path.relpath(f,K),"J_SIMULASYON_CIKTILARI","C%02d"%(i+1),"Çıktı: "+os.path.basename(f))
    if "grafik" in secim:
        for f in sorted(glob.glob(os.path.join(K,'GORSELLER','*.png'))): resim_kopya(os.path.relpath(f,K),"G_GRAFIK_VE_EKRANLAR",os.path.basename(f),"Grafik/ekran: "+os.path.basename(f))
        resim_kopya("EKLER_PDF/08_TBMM_hata_ekran_goruntusu.png","G_GRAFIK_VE_EKRANLAR","08_TBMM_hata_ekran_goruntusu.png","TBMM başvuru sayfası hata ekran görüntüsü")
    if INDEKS:
        with open(os.path.join(R,"INDEKS_%s.md"%("_".join(secim))),"w") as f:
            f.write("# RESİM İNDEKSİ (%s)\n\n| Klasör | İçerik | Kaynak dosya | Sayfa/resim |\n| :-- | :-- | :-- | --: |\n"%", ".join(secim))
            for kl,bs,y,n in INDEKS: f.write("| %s | %s | `%s` | %d |\n"%(kl,bs,y,n))

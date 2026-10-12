import os,sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','MALI_MODEL'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','MALI_MODEL'))
import model as m
from PIL import Image, ImageDraw, ImageFont
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf";FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'RESIM','00_KAPAK_KARTLARI'); os.makedirs(OUT,exist_ok=True)
f2=lambda x:("%.2f"%x).replace(".",",")
def net(sc,**kw):
    q={**m.sc(sc),'duz_oran':kw.pop('oran',0.135),'prim_devam':kw.pop('pd',0.0)};q.update(kw);return m.bes_yil(q)[3]['net']/1e9
S=list(m.SENARYO)
def karti(ad,baslik,satirlar,alt):
    im=Image.new("RGB",(1240,1000),"white");d=ImageDraw.Draw(im)
    d.text((40,30),baslik,font=ImageFont.truetype(FB,34),fill="black");y=100
    for r in satirlar:
        if isinstance(r,tuple):
            xs=[40,420,660,900]
            for x,t in zip(xs,r[1:]): d.text((x,y),t,font=ImageFont.truetype(FB if r[0]=="H" else F,27),fill=(20,60,120) if r[0]=="H" else "black")
            y+=48
        else:
            h=r.startswith("#");t=r[1:] if h else r
            d.text((40,y),t,font=ImageFont.truetype(FB if h else F,26 if h else 24),fill=(20,60,120) if h else "black");y+=42
    d.text((40,940),alt,font=ImageFont.truetype(F,20),fill=(90,90,90));im.save(os.path.join(OUT,ad))
karti("1_ozet.png","Mikro mükellefiyet - özet",["#Sorun","Şirket kuracak, geliri olmayan genç, ilk günden sabit prim ve ofis/muhasebe","yüküyle karşılaşıyor; kazanmadığı paranın yükünü taşıyor.","#Öneri","1) Gayrisafi hasılatın %13,5'i tek tevkifat; gelir yoksa yük yok.","    Oran kanunda %13,5 - %27 arasında, Cumhurbaşkanı kararıyla ayarlanır.","2) Sabit gider, zorunlu muhasebeci, defter ve beyan yükü yok.","3) Prim zorunlu değil, isteğe bağlı; emeklilik günü isteyenin.","4) Eski ve yeni girişimciye aynı kural.","5) Ücretle çalışana dokunulmaz: rejim onlar için değil.","6) Tavan: yıllık 792.720 TL; üstünde genel hükümler.","7) Sahte belge ve bölme riskine karşı dijital doğrulama.","#Talep","Taslağın incelenip kanun olarak uygulanabilir hâle getirilmesi."],"Tavan = 24 x aylık brüt asgari ücret (33.030 TL). Kaynak: kanun taslağı ve mali model.")
rows=[("H","Oran / durum","Kötümser","Orta","İyimser")]
for ad,kw in [("%10,5",dict(oran=.105)),("%13,5 (baz)",{}),("%18",dict(oran=.18)),("%22",dict(oran=.22)),("%27 (üst sınır)",dict(oran=.27))]:
    rows.append(("D",ad)+tuple(f2(net(sc,**kw)) for sc in S))
rows.append("")
rows.append("#Eski kayıtlıların isteğe bağlı primi sürdürme payı (oran %13,5)")
rows.append(("H","Sürdürme payı","Kötümser","Orta","İyimser"))
for ad,pd in (("%0",0.0),("%50",.5),("%75",.75),("%100",1.0)): rows.append(("D",ad)+tuple(f2(net(sc,pd=pd)) for sc in S))
karti("2_mali_etki.png","Devlete net etki (4. yıl, milyar TL)",rows,"Model varsayımdır; en büyük belirsizlik halen kayıtlıların geçme payıdır (ölçülmedi). Kötümser %13,5'te olumsuzdur.")
karti("3_emeklilik.png","Emeklilik (5510 sayılı Kanun m.28-29, 50-52)",["#Kurallar","Yaş: kadın 58, erkek 60 (2036'dan kademeli, 2048'de 65).","Gün: 4/b için en az 9000 prim günü (7200 gün yalnız 4/a).","Aylık bağlama oranı: her 360 gün için %2, en çok %90.","İsteğe bağlı prim süreleri 4/b süresi sayılır (m.51).","#Hesap (asgari ücret bazı, 33.030 TL)","12 ay/yıl prim: 9000 gün = 25 yıl; oran %50.","30 yıl: %60 ; 35 yıl: %70 ; 40 yıl: %80.","Emeklilik primi (%21): ayda 6.936 TL, yılda 83.236 TL.","9000 gün için toplam emeklilik primi: 2.080.890 TL.","Sağlık (GSS, %12): ayda 3.964 TL.","#Sonuç","Prim ödenmeyen dönem gün sayılmaz; isteyen gönüllü öder."],"Tutarlar 2026 asgari ücret brütü ile; ücret artışlarıyla büyür.")
print("kartlar tamam")

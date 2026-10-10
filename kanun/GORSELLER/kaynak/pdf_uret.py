import io,os,pymupdf
from PIL import Image
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(D)
bas=[("ekran_01_tescil.png","Ekran 1. Tescil: uygunluk kontrolü (Madde 1 giriş, (g), (h), (ö), (p); VUK Ek 19)"),
("ekran_02_hesap_uets.png","Ekran 2. Münhasır hesap ve UETS adresi (Madde 1 (d), Madde 2 (a), Madde 6)"),
("ekran_03_belge.png","Ekran 3. Mikro Mükellefiyet ve Muafiyet Belgesi (VUK Ek 19 (ç))"),
("ekran_04_fatura.png","Ekran 4. Fatura düzenleme, götürü gider ve tevkifat (Madde 1 (a), (b), (e); Madde 2 (b); Madde 3)"),
("ekran_05_vadeli_senet.png","Ekran 5. Alıcı paneli: Vadeli Tevkifat Senedi (Madde 1 (b))"),
("ekran_06_pano.png","Ekran 6. Mükellef panosu: tavan, tevkifat, müşteri payı (Madde 1 (e), (f), (h); Madde 9)"),
("ekran_07_bildirimler.png","Ekran 7. Bildirim kutusu: kodsuz giriş, inceleme askısı, itiraz (Madde 1 (c), (j), (k); Madde 10)"),
("ekran_08_banka.png","Ekran 8. Banka: münhasır hesap hareketleri (Madde 1 (c); Madde 6, 7, 9)"),
("sema_01_tevkifat_akisi.png","Şema 1. Alıcı türüne göre tevkifat akışı"),
("sema_02_yasam_dongusu.png","Şema 2. Mükellefiyet yaşam döngüsü (Madde 1 (h))"),
("grafik_01_yuz_lira.png","Grafik 1. 100 TL'lik hasılatın dağılımı"),
("grafik_02_kisi_basi.png","Grafik 2. Kişi başına tevkifatın dağılımı (teklif III.D.2)"),
("model_01_selale.png","Model 1. Orta senaryo 4. yıl: Hazine net etkisi (şelale)"),
("model_02_tornado.png","Model 2. Duyarlılık (tornado)"),
("model_03_montecarlo.png","Model 3. Monte Carlo dağılımı"),
("model_04_varyantlar.png","Model 4. Politika varyantları"),
("model_05_bes_yil.png","Model 5. Beş yıllık net etki")]
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
d=pymupdf.open()
def put(pg,xy,t,fs): pg.insert_text(xy,t,fontsize=fs,fontname="dj",fontfile=F)
kp=d.new_page(width=842,height=595); put(kp,(50,120),"GÖRSEL EK",30)
for i,t in enumerate(["Bireysel Emek, Hizmet ve Fikrî Üreticilerin Vergilendirilmesi ve Sosyal Güvenlik","Muafiyetleri Hakkında Kanun Teklifi: uygulama ekranları, şemalar, grafikler ve mali model","","TASLAK TASARIMDIR: ekranlar teklifin hükümlerini göstermek için çizilmiştir;","hiçbir kurumun resmî arayüzü değildir. Tutarlar örnek hesaptır, ölçülmüş veri değildir.","Model grafikleri varsayımsal girdilere dayanır (MALI_MODEL.md)."]): put(kp,(50,170+i*20),t,12)
for f,cap in bas:
    im=Image.open(f).convert('RGB'); w,h=im.size; b=io.BytesIO(); im.save(b,'JPEG',quality=90)
    pg=d.new_page(width=842,height=595); sc=min(780/w,510/h); pg.insert_image(pymupdf.Rect(30,50,30+w*sc,50+h*sc),stream=b.getvalue()); put(pg,(30,30),cap,11)
d.save('GORSEL_EK.pdf',garbage=4,deflate=True); print(os.path.getsize('GORSEL_EK.pdf')//1024,'KB',len(d),'sayfa')

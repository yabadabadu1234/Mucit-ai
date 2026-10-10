import os,subprocess,random
D=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.dirname(D)
CSS="""
*{box-sizing:border-box}body{margin:0;font-family:'DejaVu Sans','Noto Sans',Arial,sans-serif;background:#eef1f5;color:#1b2430;font-size:15px}
.bant{background:#7a1f1f;color:#fff;padding:7px 18px;font-size:12.5px;letter-spacing:.2px}
.ust{background:#1f3a5f;color:#fff;padding:14px 22px;display:flex;justify-content:space-between;align-items:center}
.ust b{font-size:18px}.ust span{font-size:13px;opacity:.9}
.govde{padding:22px;display:grid;gap:16px}
.kart{background:#fff;border:1px solid #cfd6df;border-radius:6px;padding:16px 18px}
.kart h3{margin:0 0 10px;font-size:16px;color:#1f3a5f}
table{border-collapse:collapse;width:100%}th,td{padding:7px 9px;border-bottom:1px solid #e1e6ec;text-align:left;font-size:14px}th{background:#f3f6fa;color:#34475f}
td.r,th.r{text-align:right;font-variant-numeric:tabular-nums}
.ok{color:#14662b;font-weight:bold}.uy{color:#9a5b00;font-weight:bold}.kr{color:#a11d1d;font-weight:bold}
.btn{display:inline-block;background:#1f3a5f;color:#fff;padding:9px 18px;border-radius:5px;font-size:14px}
.btn.gri{background:#e6ebf1;color:#1f3a5f;border:1px solid #bcc6d3}
.alan{border:1px solid #b9c3d0;border-radius:4px;padding:8px 10px;background:#fbfcfd;margin:4px 0 10px;font-size:14px}
.et{font-size:12.5px;color:#4b5a6e}.row{display:flex;gap:16px;flex-wrap:wrap}.row>div{flex:1;min-width:260px}
.bar{height:16px;background:#e3e9f0;border-radius:8px;overflow:hidden}.bar i{display:block;height:100%;background:#2d6aa8}
.dip{font-size:12px;color:#5a6b80;padding:8px 22px 14px}
.not{background:#fff7e0;border:1px solid #e6cf85;border-radius:5px;padding:9px 12px;font-size:13.5px}
.kir{background:#fdecec;border:1px solid #e3a6a6;border-radius:5px;padding:9px 12px;font-size:13.5px}
.yes{background:#e8f5ec;border:1px solid #9ccfae;border-radius:5px;padding:9px 12px;font-size:13.5px}
"""
BANT="TASLAK EKRAN TASARIMI | Kanun teklifi hükümlerini göstermek içindir; Gelir İdaresi Başkanlığı'nın veya herhangi bir kuruluşun resmî arayüzü değildir | Tutarlar örnektir"
def sayfa(ad,baslik,alt,icerik,dip,h):
    html=f"<!doctype html><meta charset=utf-8><style>{CSS}</style><div class=bant>{BANT}</div><div class=ust><b>{baslik}</b><span>{alt}</span></div><div class=govde>{icerik}</div><div class=dip>{dip}</div>"
    p=os.path.join(D,ad+".html"); open(p,"w").write(html)
    out=os.path.join(OUT,ad+".png")
    subprocess.run(["/opt/pw-browsers/chromium-1194/chrome-linux/chrome","--headless","--no-sandbox","--disable-gpu","--hide-scrollbars","--force-device-scale-factor=1",f"--window-size=1280,{h}",f"--screenshot={out}","file://"+p],check=True,capture_output=True)
# 1 tescil
sayfa("ekran_01_tescil","Mikro Mükellefiyet · Tescil","Adım 1/4: Uygunluk kontrolü (e-Devlet ile giriş yapıldı)","""
<div class=kart><h3>Kimlik (e-Devlet doğrulaması)</h3><div class=row><div><div class=et>Ad Soyad</div><div class=alan>A. Y. (örnek kişi)</div></div><div><div class=et>T.C. Kimlik No</div><div class=alan>*******1234</div></div><div><div class=et>Vatandaşlık</div><div class=alan>T.C. vatandaşı ✔</div></div></div></div>
<div class=kart><h3>Uygunluk kontrolü</h3><table><tr><th>Kontrol</th><th>Sonuç</th><th>Dayanak</th></tr>
<tr><td>Türkiye Cumhuriyeti vatandaşı gerçek kişi</td><td class=ok>Uygun</td><td>M.1 giriş</td></tr>
<tr><td>Son 24 ayda 4/b sigortalılığı ve gelir vergisi mükellefiyeti yok (SGK ve GİB kaydı otomatik sorgulandı)</td><td class=ok>Uygun</td><td>M.1 (p)</td></tr>
<tr><td>Gönüllü sonlandırma bekleme süresi</td><td class=ok>Yok</td><td>M.1 (h)</td></tr>
<tr><td>16 yaşını doldurmuş (18 yaşından küçükse yasal temsilci rızası)</td><td class=ok>18 yaş üstü</td><td>M.1 (ö)</td></tr>
<tr><td>Faaliyet türü negatif listede değil</td><td class=uy>Beyan bekleniyor</td><td>M.1 (g)</td></tr></table></div>
<div class=kart><h3>Faaliyet türü (beyan)</h3><div class=alan>▾ Yazılım · veri işleme · tercüme · grafik tasarım · dijital sanat · uzaktan operasyon · bağımsız teknik montaj ve bakım</div>
<div class=not>Bu başvuru için iş yeri adresi, kira sözleşmesi, ruhsat, oda kaydı veya muhasebeci sözleşmesi <b>istenmez</b>. (VUK Ek 19 (a)-(c))</div></div>
<div><span class=btn>Devam et</span> &nbsp; <span class='btn gri'>Vazgeç</span></div>""","Kaynak: teklif Madde 1 giriş, (g), (h), (ö), (p); Madde 2.",760)
# 2 hesap + UETS
sayfa("ekran_02_hesap_uets","Mikro Mükellefiyet · Tescil","Adım 2/4: Münhasır hesap ve tebligat adresi","""
<div class=kart><h3>Münhasır hesap</h3><div class=et>Bu faaliyetin tüm tahsilatları yalnız bu hesaba girer (elden nakit istisna dışıdır).</div>
<div class=alan>IBAN: TR** **** **** **** **** **** **</div><div class=alan>Banka: ▾ (örnek banka)</div>
<div class=yes>Banka talebi gerekçesiz reddedemez, açılış/işletim ücreti alamaz; taşıma talebi 3 iş günü içinde sonuçlanır. (M.6)</div></div>
<div class=kart><h3>Elektronik tebligat adresi (UETS)</h3>
<table><tr><td>Kayıtlı UETS adresi</td><td class=uy>Bulunamadı</td></tr><tr><td>Çözüm</td><td>Tescil, UETS talebi sayılır; PTT tescili izleyen 3 iş günü içinde ücretsiz adres tahsis eder.</td></tr></table>
<div class=not>Dayanak: 7201 sayılı Kanun m.7/a (gerçek kişide talep hâlinde) + VUK Ek 19 (a).</div></div>
<div><span class='btn gri'>Geri</span> &nbsp; <span class=btn>Devam et</span></div>""","Kaynak: teklif Madde 1 (d), Madde 2 (a), Madde 6. Üç iş günü teklifin tercihidir.",640)
# 3 belge
random.seed(7); cells="".join("<rect x='%d' y='%d' width='8' height='8'/>"%(x*8,y*8) for x in range(21) for y in range(21) if random.random()<0.5)
sayfa("ekran_03_belge","Mikro Mükellefiyet · Tescil","Adım 4/4: Mükellefiyet ve Muafiyet Belgesi",f"""
<div class=kart><h3>MİKRO MÜKELLEFİYET VE MUAFİYET BELGESİ</h3><div class=row><div>
<table><tr><td>Mükellef</td><td>A. Y. (örnek)</td></tr><tr><td>Belge no</td><td>MM-2026-000123</td></tr><tr><td>Tescil tarihi</td><td>10/10/2026</td></tr><tr><td>Yıllık tavan (2026)</td><td class=r>792.720 TL</td></tr><tr><td>UETS adresi</td><td>örnek-adres</td></tr><tr><td>Durum</td><td class=ok>AKTİF</td></tr></table>
<p class=et>Bu belge kamu kurumları, finansal kuruluşlar ve kurumsal müşteriler nezdinde mükellefiyet ve muafiyet ispatıdır. (VUK Ek 19 (ç))</p></div>
<div style='flex:0 0 220px;text-align:center'><svg width=176 height=176 viewBox='0 0 168 168' style='border:6px solid #1b2430;background:#fff'>{cells}</svg><div class=et>KAREKOD (örnek, geçerli değildir)</div></div></div></div>
<div class=not>Mükellef bu belgeyi platforma, bankaya ve alıcıya ibraz eder: platformlarda GVK 94/19 yerine bu maddenin tevkifatı uygulanır (M.1 (l)).</div>""","Kaynak: teklif VUK Ek 19 (ç), Madde 1 (l).",720)
# 4 fatura
sayfa("ekran_04_fatura","Fatura Düzenle","Kurumsal alıcı · e-Devlet / mobil onay ile imzasız düzenleme","""
<div class=kart><h3>Alıcı</h3><div class=row><div><div class=et>Alıcı türü</div><div class=alan>● Kurumsal (gelir/kurumlar vergisi mükellefi) &nbsp; ○ Nihaî tüketici &nbsp; ○ Yurt dışı</div></div><div><div class=et>Alıcı unvanı / VKN</div><div class=alan>Örnek Yazılım A.Ş. · 1234567890</div></div></div></div>
<div class=kart><h3>Hizmet</h3><div class=alan>Mahiyet (genel ifade kabul edilmez): Mobil uygulama arayüzünün tasarımı ve 14 ekranın teslimi, sözleşme no ÖRN-77</div>
<table><tr><th>Kalem</th><th class=r>Tutar</th></tr><tr><td>Gayrisafi hasılat (KDV: istisna, 0 TL)</td><td class=r>60.000,00 TL</td></tr>
<tr><td>Gider yöntemi: ● Götürü %30 ○ Belgeli gerçek gider</td><td class=r>−18.000,00 TL</td></tr>
<tr><td>Tevkifat matrahı</td><td class=r>42.000,00 TL</td></tr>
<tr><td>Tevkifat (%15) — alıcı tarafından ödemede kesilir</td><td class=r>6.300,00 TL</td></tr>
<tr><td><b>Mükellefe net tahsilat</b></td><td class=r><b>53.700,00 TL</b></td></tr></table></div>
<div class=kart><div class=et>Fatura referans kodu</div><div class=alan><b>MM-2026-000123-F0007</b> (ödeme açıklamasına yazılır)</div>
<div class=not>Alıcı, tevkifatı Hazine'ye aktarmadan bu gideri indiremez (M.1 (b)). Vade 30-90 gün ise alıcı "Vadeli Tevkifat Senedi" düzenleyebilir.</div></div>
<div><span class=btn>Mobil onay kodunu gönder</span></div>""","Kaynak: teklif Madde 1 (a), (b), Madde 2 (b), Madde 3. 60.000 × 0,70 × 0,15 = 6.300.",1020)
# 5 vadeli senet
sayfa("ekran_05_vadeli_senet","Alıcı Paneli · Vadeli Tevkifat Senedi","Kurumsal alıcı (Örnek Yazılım A.Ş.)","""
<div class=kart><h3>Bekleyen fatura</h3><table><tr><th>Satıcı</th><th>Fatura</th><th class=r>Tutar</th><th>Vade</th><th class=r>Tevkifat</th></tr><tr><td>A. Y. (mikro mükellef)</td><td>MM-…-F0007</td><td class=r>60.000 TL</td><td>60 gün</td><td class=r>6.300 TL</td></tr></table></div>
<div class=row><div class=kart><h3>Seçenek 1: Peşin tevkifat</h3><p>Tevkifat ödeme tarihinde muhtasarla Hazine'ye gider. Gider kaydı ödeme tarihinde.</p></div>
<div class=kart><h3>Seçenek 2: Vadeli Tevkifat Senedi</h3><p>Elektronik teminat: <b>6.300 TL</b> tescil edilir. Tevkifat vade tarihinde teminattan Hazine'ye aktarılır. Gider kaydı fatura tarihinde yapılabilir.</p></div></div>
<div class=kir><b>Uyarı:</b> Teminat yetersiz kalırsa veya tevkifat vadesinde aktarılmazsa gider indirimi hakkı kendiliğinden iptal olur; tevkifat aslı 6183 sayılı Kanuna göre alıcıdan tahsil edilir, vergi ziyaı cezası alıcıya kesilir. Bu borca ve cezaya gecikme zammı uygulanmaz. Satıcı bundan sorumlu tutulamaz. (M.1 (b))</div>
<div><span class=btn>Seçenek 2'yi onayla</span></div>""","Kaynak: teklif Madde 1 (b). Teminat işletmesinin teknik kapasitesi ölçülmemiştir (K13 benzeri risk).",720)
# 6 pano
sayfa("ekran_06_pano","Mükellef Panosu","Takvim yılı 2026 · Durum: AKTİF","""
<div class=row><div class=kart><h3>Yıllık tavan</h3><div style='font-size:26px;font-weight:bold'>215.400 TL <span class=et>/ 792.720 TL</span></div><div class=bar><i style='width:27.2%'></i></div><div class=et>%27,2 kullanıldı · tavanın yarısı: 396.360 TL</div></div>
<div class=kart><h3>Tevkifat (bu yıl)</h3><div style='font-size:26px;font-weight:bold'>22.617 TL</div><div class=et>Hasılatın %10,5'i · BES aktarımı (%3): 678,51 TL · Devlet katkısı (%20): 135,70 TL</div></div></div>
<div class=kart><h3>Müşteri payı (en çok %60)</h3><table><tr><th>Müşteri</th><th class=r>Hasılat</th><th class=r>Pay</th><th></th></tr>
<tr><td>Müşteri A</td><td class=r>126.000 TL</td><td class=r>%58,5</td><td class=uy>Sınıra yakın</td></tr><tr><td>Müşteri B</td><td class=r>62.400 TL</td><td class=r>%29,0</td><td class=ok>Uygun</td></tr><tr><td>Müşteri C</td><td class=r>27.000 TL</td><td class=r>%12,5</td><td class=ok>Uygun</td></tr></table>
<div class=not>Mükellefiyetin ilk yılında ve yıllık hasılat altı aylık brüt asgari ücreti (198.180 TL) aşmadığı sürece %60 sınırı uygulanmaz. (M.1 (f))</div></div>
<div class=kart><h3>Hatırlatmalar</h3><ul><li>Son iki yıl çalıştığınız işverene fatura kesilemez (M.1 (f)).</li><li>Tavan aşılırsa aşıldığı ayı izleyen ay başından genel hükümlere geçilir; o güne kadarki tevkifat nihaîdir (M.1 (h)).</li><li>Hasılat 396.360 TL'ye ulaşırsa 90 gün prim ödeme süresi sayılır, primi Hazine öder (Ek 25).</li></ul></div>""","Kaynak: teklif Madde 1 (e), (f), (h), Madde 9. 215.400 × 0,105 = 22.617; × 0,03 = 678,51; × 0,2 = 135,70.",1000)
# 7 bildirim
sayfa("ekran_07_bildirimler","Bildirim Kutusu","Portal · UETS · kayıtlı iletişim araçları","""
<div class=kart><h3>Referans kodsuz giriş — işlem bekliyor</h3><table><tr><th>Tarih</th><th class=r>Tutar</th><th>Kalan süre</th><th>Yapılacak</th></tr><tr><td>11/10/2026 09:14</td><td class=r>12.500 TL</td><td class=uy>31 saat</td><td>Fatura ile eşleştir veya "hizmet bedeli değil" belgesi yükle</td></tr></table>
<div class=not>Bu giriş bloke edilmedi, iade edilmedi. 48 saat içinde işlem yapılmazsa hizmet bedeli sayılıp tevkifat kesilir; fazla kesinti ertesi ay iade edilir. (M.1 (c), (k))</div></div>
<div class=kart><h3>İnceleme askısı — gelir kaynağı beyanı</h3><table><tr><th>Tarih</th><th class=r>Tutar</th><th>Süre</th></tr><tr><td>12/10/2026</td><td class=r>240.000 TL</td><td class=kr>15 gün</td></tr></table>
<p class=et>Kural: son üç aylık hasılat ortalamasının 5 katını ve aynı zamanda iki aylık brüt asgari ücreti (66.060 TL) birlikte aşan giriş. Burada ortalama 40.000 TL → eşik 200.000 TL.</p>
<div class=alan>Gelir kaynağı: ○ Hizmet bedeli ○ Faiz içermeyen borç ○ Emanet iadesi ○ Hibe ○ Miras ○ Kâr paylaşımlı sermaye desteği ○ Diğer &nbsp; · Belge: [Dosya seç]</div>
<div class=not>Hesap kapatılmaz, cezai kesinti yapılmaz. Belge sunulmazsa askı kendiliğinden kalkmaz; 5549 sayılı Kanun uyarınca şüpheli işlem bildirimi yapılır ve bu bildirim diğer hakları etkilemez. (M.1 (j))</div></div>
<div class=kart><h3>İtiraz</h3><p>İşlemlere karşı 30 gün içinde Mikro Üretici Dijital Hakem Heyetine itiraz: portal · PTT · muhtarlık · nüfus müdürlüğü. İtiraz süresince faaliyet kesilmez. (Madde 10)</p><span class=btn>İtiraz başlat</span></div>""","Kaynak: teklif Madde 1 (c), (j), (k), Madde 10.",1010)
# 8 banka
sayfa("ekran_08_banka","Münhasır Hesap · Hesap Hareketleri","Örnek banka internet şubesi (Mikro Mükellef Hesabı)","""
<div class=kart><h3>Hareketler</h3><table><tr><th>Tarih</th><th>Açıklama</th><th class=r>Tutar</th><th class=r>Bakiye</th></tr>
<tr><td>11/10 10:02</td><td>FAST gelen · REF: MM-2026-000123-F0009 · nihaî tüketici</td><td class=r>+100.000,00</td><td class=r>100.000,00</td></tr>
<tr><td>11/10 10:02</td><td>Otomatik tevkifat (%10,5) — Hazine'ye aktarıldı</td><td class=r>−10.500,00</td><td class=r>89.500,00</td></tr>
<tr><td>11/10 10:03</td><td>BES aktarımı (tevkifatın %3'ü) — tevkifattan ayrılır</td><td class=r>0,00*</td><td class=r>89.500,00</td></tr></table>
<p class=et>* BES payı mükellefin hesabından değil tevkifat tutarından ayrılır (315,00 TL); mükellef aksini bildirebilir. (Madde 9)</p></div>
<div class=yes><b>Serbest bakiye 89.500,00 TL</b> — çekim, kartla harcama ve yurt dışı yazılım/sunucu ödemesi serbesttir. Haciz varsa önce tevkifat ayrılır, haciz kalan bakiyeye uygulanır. (Madde 6)</div>
<div class=not>EFT/havale/FAST: işlem tutarının binde ikisini veya TCMB azami ücretini, hangisi düşükse aşamaz. (Madde 7)</div>""","Kaynak: teklif Madde 1 (c), Madde 6, 7, 9. 100.000 × 0,105 = 10.500; × 0,03 = 315.",780)
print("ekranlar tamam")

from PIL import Image,ImageChops
import glob
for f in sorted(glob.glob(os.path.join(OUT,'ekran_*.png'))):
    im=Image.open(f).convert('RGB'); bg=Image.new('RGB',im.size,(238,241,245)); bbox=ImageChops.difference(im,bg).getbbox()
    if bbox: im.crop((0,0,im.width,min(im.height,bbox[3]+24))).save(f)

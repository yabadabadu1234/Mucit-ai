import cizim as CZ
from icerik.yardim import *
from icerik import v_lora

ID = 'lora'
BASLIK = '6. LoRa telsiz modülü (alıcı tarafı)'
OZET = 'Vericideki aynı telsiz modülü alıcıda “dinleyen” taraftır. Farkı: ortak SPI hattı, her an alıcı kipte olması ve akım bütçesi.'
REFS = ['U4', 'C22', 'C23', 'J2']

ADLAR = {2: 'SPI_MISO', 3: 'SPI_MOSI', 4: 'SPI_SCK', 5: 'LORA_NSS', 6: 'LORA_RESET', 14: 'LORA_DIO0', 15: 'LORA_DIO1'}
HEDEF = {2: 'işlemci IO13', 3: 'IO11', 4: 'IO12', 5: 'IO10', 6: 'IO14', 14: 'IO8', 15: 'IO15'}


def uret(ver, ctx):
    v = ver
    c = v_lora.sema(v, ADLAR, HEDEF, ('C22', 'C23'))
    hata = c.denetle(v.aglar)
    assert not hata, hata
    h = ['<h1>%s</h1><p class="ozet">%s</p>' % (BASLIK, OZET)]
    h.append('<p>Bu bölüm, <a href="../verici/lora.html">verici 5. bölümü</a> okunduğu varsayılarak yazıldı (LoRa nedir, ayaklar, bağlantı bütçesi, 50 Ω hat hesabı). Burada yalnız alıcıya özgü noktalar anlatılır.</p>')
    h.append('<h2>1. Şema</h2>' + sema_kutusu(c))
    h.append('<h2>2. Alıcıya özgü noktalar</h2><ul>'
             '<li><b>Ortak SPI.</b> SPI_MISO, SPI_MOSI, SPI_SCK adları “LORA_” ile başlamaz çünkü bu üç hat Ethernet çipiyle paylaşılır (5. bölüm). Seçim hattı (LORA_NSS) modüle özeldir.</li>'
             '<li><b>Kesme ayağı.</b> Alıcıda DIO0 “paket alındı” kesmesi olarak yazılımla yapılandırılır; işlemci ayağı IO8, DIO1 ise IO15’tir (vericide IO9). [[bilgi]]</li>'
             '<li><b>Sürekli dinleme.</b> Alıcı kipte akım yaklaşık 10,3–11,5 mA’dir [[ds]]; 12 V’lu sistemde bu önemsizdir (1,7 V fark üzerinden çeviriciden çekilen ek güç ≈ 40 mW).</li>'
             '<li><b>Beacon (işaret).</b> Alıcının bir “yaşıyorum” işareti göndermesi isteniyorsa +20 dBm çıkışta görev oranı veri sayfasına göre ≤ %%1’dir: örneğin her 10 s’de 100 ms. [[ds]]</li></ul>')
    h.append('<h2>3. Parça kartları</h2><div class="kartlar">' + ''.join(v.kart_html(r) for r in REFS) + '</div>')
    h.append('<h2>4. Anten hattı ölçüleri</h2><p>Anten hattı <code>ANT_RF</code>: genişlik %s mm, uzunluk ≈ %s mm, delikli geçit %d. Modül ile SMA arası %s mm.</p>' % (
        ', '.join(sayi(w) for w in iz_genislikleri(v, 'ANT_RF')), sayi(iz_uzunlugu(v, 'ANT_RF'), 3), viya_sayisi(v, 'ANT_RF'), sayi(mesafe(v, 'U4', 'J2'), 3)))
    h.append(pano_kutusu(v, REFS, [(1, 'U4'), (2, 'C22'), (3, 'J2')], 'Modül ve SMA kartın alt kenarında; modemin 4G antenlerinden ve Ethernet’ten uzak.'))
    h.append('<h2>5. Kaynaklar</h2><ul class="kaynak"><li>HopeRF RFM95/96/97/98(W) veri sayfası (verici 5. bölümde ayrıntılı).</li></ul>')
    return ''.join(h)

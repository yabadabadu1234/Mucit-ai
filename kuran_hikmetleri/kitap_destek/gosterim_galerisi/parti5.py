from ortak import *
from parti4 import wrap, kel, RK, DEF
S = []
def usul(f): S.append(f); return f
def paragraf(b, x, y, s, n, size=11, anchor='start', fill='#2b2410', lh=None, extra=''):
    lh = lh or size * 1.45
    for j, l in enumerate(wrap(s, n)): b.append(T(l, x, y + j * lh, size, anchor, fill, extra))
    return y + len(wrap(s, n)) * lh
# 131 Carte de Tendre
@usul
def u131():
    b = ['<rect x="0" y="60" width="900" height="600" fill="#cfe3ef"/>', '<path d="M60,120 C200,70 700,70 840,140 C880,300 860,520 760,610 C560,660 300,650 120,600 C40,480 30,260 60,120Z" fill="#efe3c2" stroke="#8a6d3b" stroke-width="2"/>']
    b.append('<path d="M450,600 C440,520 430,470 430,420 C420,380 380,340 330,300 C280,260 230,230 200,170" stroke="#5b8fb9" stroke-width="7" fill="none"/>')
    b.append('<path d="M430,420 C500,380 560,330 620,280 C660,240 700,200 740,160" stroke="#5b8fb9" stroke-width="7" fill="none"/>')
    b.append('<path d="M430,420 C470,470 560,500 660,520" stroke="#5b8fb9" stroke-width="5" fill="none"/>')
    for x, y in [(330, 520), (360, 540), (300, 545)]: b.append(f'<path d="M{x},{y} l14,-26 l14,26z" fill="#a08050"/>')
    yerler = [(450, 590, 'Esas Pınarı', 'ölçüp biçerek hazırlamak'), (330, 300, 'Ölçü Kasabası', 'خَلَقَ'), (200, 170, 'Hâlık Şehri', 'yaratmak · خَالِق'), (150, 270, 'Mahlûkat Ovası', 'مَخْلُوق'),
              (250, 380, 'Hilkat Köyü', 'yaradılış · خِلْقَة'), (170, 470, 'Huy Vadisi', 'خُلُق'), (90, 560, 'Ahlâk Kalesi', 'أَخْلَاق'), (620, 280, 'Düzlük Yaylası', 'خَلْقَاء'), (740, 160, 'Eskilik Limanı', 'خَلَق'),
              (760, 300, 'Koku Bahçeleri', 'خَلُوق'), (660, 520, 'Pay Pazarı', 'خَلَاق'), (560, 600, 'Yakışık Köprüsü', 'خَلِيق'), (330, 130, 'Uydurma Bataklığı', 'اِخْتَلَقَ'), (820, 600, 'Yabancı Ada: Kazan', 'خِلْقِين')]
    for x, y, ad, alt in yerler:
        c = '#c0392b' if 'Bataklı' in ad or 'Yabancı' in ad else '#2b2410'
        b.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{c}"/>'); b.append(T(ad, x, y - 10, 11.5, fill=c, w='font-weight="700" font-style="italic" stroke="#efe3c2" stroke-width="3" paint-order="stroke"'))
        b.append(T(alt, x, y + 18, 10, w='stroke="#efe3c2" stroke-width="3" paint-order="stroke"') if not any('؀' <= ch <= 'ۿ' for ch in alt[:3]) else AR(alt, x, y + 20, 13))
    b.append(T('Ölçü Irmağı', 395, 380, 11, fill='#2e5f86', w='font-style="italic"')); b.append(T('Düzlük Irmağı', 560, 360, 11, fill='#2e5f86', w='font-style="italic"'))
    b.append(T('Yolcu pınardan çıkar; hangi ırmağı izlerse o manaya varır. Bataklık, yaratmanın sahtesine düşmektir.', 450, 650, 11))
    kaydet('131_carte_de_tendre', '131. Alegorik harita (Carte de Tendre usulü): manalar ülkenin şehirleri, türeme ırmaklar', '17. asır Fransız haritasından: bir his ülke gibi çizilir. Burada kökün manaları bir memleket.', b, 900, 670)
# 132 Kaz oyunu tahtası
@usul
def u132():
    b = []; cx, cy = 450, 370
    sira = ['E', 'A', 'D', 'J', 'K', 'U', 'Z', 'Y', 'X', 'L', 'B', 'N', 'F', 'G', 'C', 'H']
    pts = []
    for k in range(len(sira)):
        r, c = divmod(k, 4); c = c if r % 2 == 0 else 3 - c; pts.append((150 + c * 200, 120 + r * 120))
    for k in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[k], pts[k + 1]; b.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#c9bd94" stroke-width="14" stroke-linecap="round"/>')
    for k, (m, (x, y)) in enumerate(zip(sira, pts)):
        c = RK(m) if m != 'E' else '#b8860b'
        b.append(f'<rect x="{x-50:.1f}" y="{y-32:.1f}" width="100" height="64" rx="10" fill="#fffdf6"/>')
        b.append(f'<rect x="{x-50:.1f}" y="{y-32:.1f}" width="100" height="64" rx="10" fill="{c}" fill-opacity=".2" stroke="{c}" stroke-width="2"/>')
        b.append(T(str(k + 1), x - 42, y - 18, 10, 'start', c, 'font-weight="700"')); b.append(T(KISA[m], x, y + 2, 10.5, w='font-weight="700"')); b.append(AR((kel(m) or [''])[0], x, y + 24, 13))
    kur = {7: 'Öfke: 2 kare geri git (huy taşınca geriler)', 9: 'Uydurma: başa dön (sahte eser)', 4: 'Yaradılış: bir tur bekle, kalıbını tanı', 13: 'Koku: ölçü kanadına sıçra'}
    y = 600
    for k, s in kur.items(): b.append(T(f'{k+1}. kare: {s}', 40 + (len(b) % 2) * 0, y, 10.5, 'start', '#b3541e')); y += 15
    b.append(T('Oyuncu zar yerine bir suâle doğru cevap verdikçe ilerler; ceza kareleri manaların tehlikesini öğretir.', 880, 640, 10.5, 'end'))
    kaydet('132_kaz_oyunu', '132. Oyun tahtası (Kaz oyunu usulü): manalar kıvrılan yol üstünde kareler', 'Bazı kareler ödül, bazıları ceza; kuralın kendisi manayı öğretir.', b, 900, 660)
# 133 Beden haritası
@usul
def u133():
    b = []; x = 450
    b.append(f'<circle cx="{x}" cy="140" r="50" fill="#f5e1c8" stroke="#2b2410" stroke-width="2"/><path d="M{x-70},200 L{x+70},200 L{x+90},420 L{x-90},420Z" fill="#f5e1c8" stroke="#2b2410" stroke-width="2"/>')
    b.append(f'<path d="M{x-70},210 L{x-170},360 L{x-150},370 L{x-60},250" fill="#f5e1c8" stroke="#2b2410" stroke-width="2"/><path d="M{x+70},210 L{x+170},360 L{x+150},370 L{x+60},250" fill="#f5e1c8" stroke="#2b2410" stroke-width="2"/>')
    b.append(f'<path d="M{x-60},420 L{x-70},620 L{x-30},620 L{x-10},420 M{x+10},420 L{x+30},620 L{x+70},620 L{x+60},420" fill="#f5e1c8" stroke="#2b2410" stroke-width="2"/>')
    b.append(f'<path d="M{x-14},270 c-14,-18 -34,0 0,26 c34,-26 14,-44 0,-26" fill="#c0392b"/>')
    L = [((x - 165, 365), (130, 320), 'EL: ölçer, biçer', 'خَلَقَ', 'A'), ((x, 120), (180, 110), 'GÖZ: dış şekli görür', 'خِلْقَة', 'K'), ((x - 14, 280), (150, 470), 'KALP: huy yerleşir', 'خُلُق', 'U'), ((x + 20, 140), (720, 100), 'AĞIZ: sözü uydurur', 'اِخْتَلَقَ', 'L'),
         ((x + 6, 280), (730, 230), 'GÖĞÜS: öfke kabarır', 'تَخَلَّقَ', 'Y'), ((x + 160, 360), (740, 360), 'AVUÇ: koku sürer', 'خَلُوق', 'G'), ((x + 50, 600), (740, 520), 'AYAK: elbise aşınır, eskir', 'خَلِقَ', 'F'), ((x, 70), (720, 640), 'BÜTÜN BEDEN: yaratılmış', 'مَخْلُوق', 'J')]
    for (px, py), (lx, ly), s, ar, m in L:
        c = RK(m); b.append(f'<line x1="{px}" y1="{py}" x2="{lx}" y2="{ly}" stroke="{c}" stroke-width="1.5"/><circle cx="{px}" cy="{py}" r="4" fill="{c}"/>')
        b.append(T(s, lx, ly - 4, 11, 'middle', c, 'font-weight="700"')); b.append(AR(ar, lx, ly + 16, 14))
    kaydet('133_beden_haritasi', '133. Beden haritası: her mana bedenin onu işleyen uzvuna konur', 'Okuyan kendi bedeninde yer bulur: el ölçer, kalpte huy durur, ağız uydurur.', b, 900, 670)
# 134 Hikâye çizgileri
@usul
def u134():
    b = []
    sahne = ['ham madde', 'ölçüm', 'yaratış', 'kalıp', 'insanın içi', 'çarşı', 'yıllar sonra']
    for k, s in enumerate(sahne): x = 120 + k * 120; b.append(f'<line x1="{x}" y1="80" x2="{x}" y2="600" stroke="#eee"/>'); b.append(T(s, x, 76, 10.5, fill='#6d6650'))
    K = [('خَلَقَ', '#2f6fb3', [300, 200, 200, 230, 260, 300, 300]), ('مَخْلُوق', '#2f6fb3', [None, None, 215, 245, 330, 420, 520]), ('خُلُق', '#7a3fb3', [None, None, None, 260, 275, 290, 300]),
         ('أَخْلَاق', '#7a3fb3', [None, None, None, None, 290, 305, 315]), ('خَلْقَاء', '#3f8f3a', [330, 360, 420, 450, 470, 500, 535]), ('خَلَاق', '#c26a1e', [None, 215, None, None, None, 430, 440]), ('خَلَق', '#3f8f3a', [None, None, None, None, None, 445, 550]), ('اِخْتَلَقَ', '#c0392b', [None, None, 185, 120, 120, 120, 120])]
    for ad, c, ys in K:
        pts = [(120 + k * 120, y) for k, y in enumerate(ys) if y]
        d = 'M' + ' '.join(f'{x},{y}' if i == 0 else f'C{px+60},{py} {x-60},{y} {x},{y}' for i, ((x, y), (px, py)) in enumerate(zip(pts, [pts[0]] + pts[:-1])))
        b.append(f'<path d="{d}" stroke="{c}" stroke-width="4" fill="none" stroke-linecap="round"/>'); b.append(AR(ad, pts[0][0] - 8, pts[0][1] + 5, 14, 'end', c))
    b.append(T('Çizgiler yan yana koştuğu sahnelerde kelimeler aynı hikâyededir; ayrıldıkları yerde mana ayrılır.', 450, 630, 11))
    kaydet('134_hikaye_cizgileri', '134. Hikâye çizgileri (xkcd film şeması usulü): her kelime bir karakter, soldan sağa hikâye akar', 'Bir eşyanın hikâyesinde hangi kelimenin ne zaman sahneye girip kiminle yürüdüğü.', b, 900, 650)
# 135 Patlatılmış montaj
@usul
def u135():
    b = []
    P = [('م', 'mim: "-ilmiş olan"', '#b3541e', 230), ('خ', 'kök 1', '#2b2410', 340), ('ْ', 'sükûn', '#999', 420), ('ل', 'kök 2', '#2b2410', 500), ('ُو', 'uzatma vâvı', '#b3541e', 590), ('ق', 'kök 3', '#2b2410', 680)]
    b.append(AR('مَخْلُوق', 450, 140, 46)); b.append(T('montajlı hâl', 450, 170, 11, fill='#6d6650'))
    for ar, ad, c, x in reversed(P):
        x2 = 900 - x
        b.append(f'<line x1="450" y1="185" x2="{x2}" y2="300" stroke="#bbb" stroke-dasharray="4 3"/>')
        b.append(f'<rect x="{x2-38}" y="300" width="76" height="90" rx="6" fill="#fff" stroke="{c}" stroke-width="2" transform="rotate({(x2-450)/30} {x2} 345)"/>'); b.append(AR(ar, x2, 360, 38, fill=c)); b.append(T(ad, x2, 420, 10.5, fill=c))
    b.append(T('Parça listesi: 3 kök harfi (ölçüp biçme) + mim ve vâv (vezin: مَفْعُول, "kendisine iş yapılan") = "ölçülüp biçilmiş, yaratılmış olan"', 450, 500, 11.5, w='font-weight="700"'))
    b.append(T('Makine çizimindeki gibi parçalar yerinden çıkarılıp sökülme sırasıyla gösterilir; siyah parçalar asıl, kırmızılar takılan.', 450, 530, 11))
    kaydet('135_patlatilmis_montaj', '135. Patlatılmış montaj çizimi: kelime parçalarına sökülür', 'Mühendislik çiziminin usulü: hangi parça nereye takılmış, takılınca ne olmuş.', b, 900, 560)
# 136 Jeolojik kesit
@usul
def u136():
    b = []
    K = [('ESAS KAYA: ölçüp biçerek hazırlamak', '#b8860b', []), ('ÖLÇÜ TABAKASI', '#9db8d9', ['خَلَقَ']), ('DÜZLÜK TABAKASI', '#a9cf9b', ['خَلْقَاء', 'خَلَائِق']), ('YARATIŞ TABAKASI', '#7fa6cc', ['خَالِق', 'مَخْلُوق', 'خَلْق']),
         ('AŞINMA TABAKASI', '#8fbf7f', ['خَلِقَ', 'خُلْقَان']), ('KALIP TABAKASI', '#6a92bd', ['خِلْقَة', 'خَلِيقَة']), ('NEFS TABAKASI', '#9c86c9', ['خُلُق', 'تَخَلَّقَ']), ('AHLÂK (yüzey)', '#b9a3e3', ['أَخْلَاق', 'أَخْلَاقِيّ'])]
    y = 620
    for k, (ad, c, ws) in enumerate(K):
        h = 62; y -= h
        b.append(f'<path d="M80,{y+h} Q300,{y+h-8-k} 500,{y+h+4} T820,{y+h-6} L820,{y-4} Q600,{y+6} 400,{y-6} T80,{y} Z" fill="{c}" stroke="#5a4a2a"/>')
        b.append(T(ad, 100, y + 36, 11.5, 'start', '#1a1a1a', 'font-weight="700"'))
        for j, w in enumerate(ws): b.append(f'<ellipse cx="{560+j*90}" cy="{y+31}" rx="38" ry="18" fill="#fff" fill-opacity=".7" stroke="#5a4a2a"/>'); b.append(AR(w, 560 + j * 90, y + 37, 13))
    b.append('<path d="M640,120 l20,-50 l20,50z" fill="#c0392b"/>'); b.append(T('İhtilâk yarığı: uydurma, tabakaları kesen sahte damar', 660, 140, 10, fill='#c0392b'))
    kaydet('136_jeolojik_kesit', '136. Jeolojik kesit: manalar üst üste çökmüş tabakalar, kelimeler içinde fosil', 'En alttaki en eski ve en sağlamdır; üstteki her tabaka alttakinin üstüne birikmiştir.', b, 900, 640)
# 137 Mesajlaşma
@usul
def u137():
    b = []; y = 80
    M = [('خَلَقَ', 'L', 'Selam, ben ölçüp biçen. Herkes beni "yarattı" diye biliyor ama önce ölçerim.'), ('خُلُق', 'R', 'Ben de senin çocuğunum aslında. Yaradılışta içe konan kalıbım. Huy.'),
         ('خَلِقَ', 'L', 'Bana eskimiş diyorlar. Ama ben de ailedenim: düzlenen yüzey aşınınca ben olurum.'), ('خُلُق', 'R', 'Yani ikimiz de "şekil" sahibiyiz: ben içte, sen yüzde.'),
         ('اِخْتَلَقَ', 'L', 'Beni pek sevmezler. Olmayan sözü yaratılmış gibi gösteririm.'), ('خَلَقَ', 'R', 'Ölçüsüz yaratma sahtedir. Sen benim gölgemsin.'), ('خِلْقِين', 'L', 'Ben kazanım; Yunanca konuşuyorum, galiba yanlış gruba eklendim 🙂')]
    b.append('<rect x="200" y="60" width="500" height="590" rx="30" fill="#ece5dd" stroke="#2b2410" stroke-width="2"/><rect x="200" y="60" width="500" height="44" rx="20" fill="#075e54"/>')
    b.append(T('خلق ailesi grubu', 450, 88, 13, fill='#fff', w='font-weight="700"')); y = 130
    for ad, s, t in M:
        ls = wrap(t, 46); h = 26 + len(ls) * 15; x = 220 if s == 'L' else 360
        b.append(f'<rect x="{x}" y="{y}" width="320" height="{h}" rx="10" fill="{"#fff" if s=="L" else "#dcf8c6"}"/>'); b.append(AR(ad, x + 310, y + 18, 13, 'end', '#075e54'))
        for j, l in enumerate(ls): b.append(T(l, x + 10, y + 34 + j * 15, 10.5, 'start'))
        y += h + 10
    kaydet('137_mesajlasma', '137. Mesajlaşma: kökün kelimeleri bir grupta birbirine kendini anlatır', 'Her kelime birinci şahısla konuşur; aile bağı sohbetin içinde ortaya çıkar.', b, 900, 670)
# 138 Karagöz perdesi
@usul
def u138():
    b = ['<rect x="60" y="70" width="780" height="300" fill="#f7ecc9" stroke="#8a5a2b" stroke-width="8"/>']
    for x, c in [(250, '#c0392b'), (650, '#2f6fb3')]:
        b.append(f'<circle cx="{x}" cy="190" r="34" fill="{c}" fill-opacity=".5"/><rect x="{x-30}" y="224" width="60" height="110" rx="10" fill="{c}" fill-opacity=".5"/>')
    b.append(T('KARAGÖZ', 250, 360, 12, w='font-weight="700"')); b.append(T('HACİVAT', 650, 360, 12, w='font-weight="700"'))
    D = [('Hacivat', 'Ey Karagöz\'üm, "hulk" kelimesinin aslı ölçüp biçmektir, bilir misin?'), ('Karagöz', 'Bilmem mi! Terzi Ahmet ölçtü, biçti, ceketim oldu. Sonra eskidi: "halika".'),
          ('Hacivat', 'Aferin. Allah her şeyi ölçüsüyle yarattığı için Hâlık\'tır; yaratılmışa mahlûk denir.'), ('Karagöz', 'Benim mahlûk huyum da yaradılıştan mı?'),
          ('Hacivat', 'Evet: yaradılışta içe verilen kalıba hulk derler, çoğalıp yerleşince ahlâk olur.'), ('Karagöz', 'O hâlde senin bu uydurma lafların da bu köktendir, "ihtilâk"!'), ('Hacivat', 'Yıktın perdeyi, eyledin viran…')]
    y = 400
    for kim, s in D: b.append(T(kim + ':', 70, y, 11, 'start', '#c0392b' if kim == 'Karagöz' else '#2f6fb3', 'font-weight="700"')); y = paragraf(b, 150, y, s, 100, 11) + 4
    kaydet('138_karagoz', '138. Karagöz perdesi: iki tip muhavere ile öğretir, biri bilir biri şaşırır', 'Şaşıran tipin yanlış anlaması, doğrunun sınırını gösterir.', b, 900, y + 20)
# 139 Gazete ön sayfası
@usul
def u139():
    b = ['<rect x="30" y="64" width="840" height="580" fill="#faf8f0" stroke="#2b2410"/>']
    b.append(T('LÜGAT GAZETESİ', 450, 108, 34, w='font-weight="700" font-family="Georgia, serif"')); b.append('<line x1="40" y1="120" x2="860" y2="120" stroke="#2b2410" stroke-width="3"/>'); b.append(T('15 Kasım 2026 · Kök: خ ل ق · Fiyatı: bir dikkat', 450, 136, 10, fill='#6d6650'))
    b.append(T('"HER ŞEY ÖLÇÜYLE YARATILDI"', 450, 180, 28, w='font-weight="700" font-family="Georgia, serif"'))
    paragraf(b, 50, 210, 'Lügat âlimleri, yaratmak manasının asıl kaynağını açıkladı: kelime ilk önce terzi ve marangozun ölçüp biçmesini anlatıyordu. Ölçülen şey tamamlanınca "yaratılmış" oldu. Bugün خَالِق kelimesi bu ölçünün sahibini bildiriyor.', 135, 11.5)
    C = [('İÇ HABER', 'Huy da aileden çıktı', 'Yaradılışta nefse verilen kalıp, insanın huyu (خُلُق) oldu. Uzmanlara göre huylar yerleşince ahlâk (أَخْلَاق) doğuyor.'), ('EKONOMİ', 'Pay piyasası', 'Bir iş için ölçülüp ayrılan nasibe خَلَاق deniyor. Âhirette payı olmayanlar için Bakara 102 uyarıyor.'),
         ('MODA', 'Elbiseler neden eskir?', 'Düzlenen yüzey sürtündükçe aşınıyor: خَلِقَ. Paçavralara خُلْقَان deniyor.'), ('SON DAKİKA', 'Uydurma tespit edildi', 'Olmayan sözü varmış gibi gösteren اِخْتِلَاق vakası. Yetkililer: "Sahte yaratmadır."')]
    for k, (kat, bas, met) in enumerate(C):
        x = 50 + k * 205; b.append(f'<line x1="{x-8}" y1="290" x2="{x-8}" y2="620" stroke="#ccc"/>') if k else None
        b.append(T(kat, x, 300, 9.5, 'start', '#b3541e', 'font-weight="700"')); b.append(T(bas, x, 322, 14, 'start', '#1a1a1a', 'font-weight="700" font-family="Georgia, serif"')); paragraf(b, x, 345, met, 34, 10.5)
    b.append(T('Küçük ilan: Yunanca kökenli kazan (خِلْقِين) aile arıyor. Akrabalık kabul edilmedi.', 450, 630, 10, fill='#6d6650', w='font-style="italic"'))
    kaydet('139_gazete', '139. Gazete ön sayfası: en mühim mana manşette, diğerleri sütunlarda', 'Okuyan önce manşeti, sonra ilgisini çeken sütunu okur; ehemmiyet yerleşimden belli olur.', b, 900, 660)
# 140 Yemek tarifi
@usul
def u140():
    b = ['<rect x="80" y="70" width="740" height="560" rx="14" fill="#fff9ee" stroke="#c26a1e" stroke-width="3"/>']
    b.append(T('TARİF: AHLÂK (أَخْلَاق)', 450, 115, 24, fill='#c26a1e', w='font-weight="700" font-family="Georgia, serif"')); b.append(T('Hazırlık: bir ömür · Pişirme: sabırla · Kaç kişilik: bir nefs', 450, 140, 11, fill='#6d6650'))
    b.append(T('MALZEMELER', 120, 180, 13, 'start', '#c26a1e', 'font-weight="700"'))
    for k, s in enumerate(['1 ölçü (asıl: ölçüp biçmek, خَلَقَ)', '1 yaratılmış nefs (مَخْلُوق)', '1 yaradılış kalıbı (خِلْقَة)', 'bol miktarda tekrar', 'öfke (تَخَلَّقَ): dikkat, taşırmayın']): b.append(T('• ' + s, 130, 205 + k * 22, 11.5, 'start'))
    b.append(T('YAPILIŞI', 470, 180, 13, 'start', '#c26a1e', 'font-weight="700"'))
    y = 205
    for k, s in enumerate(['Ham maddeyi maksada göre ölçün ve biçin.', 'Ölçülen şeyi tamamlayın: artık yaratılmıştır.', 'Yaratılana kalıbını verin; bu yaradılıştır.', 'Kalıp nefse yerleşince huy olarak kabarır.', 'Huyları tekrarla pişirin; yerleşince ahlâk olur.', 'Başkasının huyunu üstünüze giymek (تَخَلُّق) tarifi bozar.']): y = paragraf(b, 480, y, f'{k+1}. {s}', 46, 11.5) + 6
    b.append(T('Usta notu: ölçüsüz yapılan "yemek" uydurmadır (اِخْتِلَاق). Kazan (خِلْقِين) bu tarifin malzemesi değildir, yabancıdır.', 450, 600, 11, fill='#6d6650', w='font-style="italic"'))
    kaydet('140_yemek_tarifi', '140. Yemek tarifi: bir mana, malzemesi ve yapılış adımlarıyla', 'Malzeme = önşart manalar, adım = türeme sırası, sonuç = hedef kelime.', b, 900, 650)
# 141 Origami
@usul
def u141():
    b = [DEF]
    A = [('ham madde: düz kâğıt', 'خَلْقَاء', '<rect x="-45" y="-45" width="90" height="90" fill="#f3eedd" stroke="#2b2410" stroke-width="2"/>'),
         ('ölçmek: köşegen çizilir', 'خَلَقَ', '<rect x="-45" y="-45" width="90" height="90" fill="#f3eedd" stroke="#2b2410" stroke-width="2"/><line x1="-45" y1="45" x2="45" y2="-45" stroke="#2f6fb3" stroke-dasharray="5 3" stroke-width="2"/>'),
         ('biçmek: katlanır', 'خَلَقَ', '<path d="M-45,45 L45,-45 L45,45Z" fill="#dfe8f3" stroke="#2b2410" stroke-width="2"/>'),
         ('şekli belirir', 'مُخَلَّق', '<path d="M-45,45 L0,-45 L45,45 L0,20Z" fill="#cfe3dc" stroke="#2b2410" stroke-width="2"/>'),
         ('yaratılmış: kuş', 'مَخْلُوق', '<path d="M-55,10 L0,-10 L55,-35 L20,10 L0,40 L-10,10Z" fill="#9db8d9" stroke="#2b2410" stroke-width="2"/>'),
         ('kalıbı: kat izleri', 'خِلْقَة', '<rect x="-45" y="-45" width="90" height="90" fill="#fff" stroke="#2b2410"/><path d="M-45,45 L45,-45 M-45,-45 L45,45 M0,-45 L0,45" stroke="#7a3fb3" stroke-dasharray="4 3"/>'),
         ('eskimiş: yıpranmış kat', 'خَلِقَ', '<path d="M-55,12 L0,-8 L50,-30 L18,14 L-2,38 L-12,12Z" fill="#d5d5d5" stroke="#777" stroke-width="2" stroke-dasharray="2 2"/>')]
    for k, (ad, ar, sek) in enumerate(A):
        x = 90 + (k % 4) * 240; y = 170 + (k // 4) * 250
        b.append(f'<g transform="translate({x},{y})">{sek}</g>'); b.append(T(f'{k+1}. {ad}', x, y + 80, 11.5, w='font-weight="700"')); b.append(AR(ar, x, y + 104, 15))
        if k % 4 != 3 and k < 6: b.append(f'<line x1="{x+70}" y1="{y}" x2="{x+165}" y2="{y}" stroke="#2b2410" stroke-width="2" marker-end="url(#o)"/>')
    b.append(T('Aynı kâğıt her katla başka bir şey olur; kelimeler bir maddenin katlanma safhalarıdır.', 450, 640, 11))
    kaydet('141_origami', '141. Origami katlama adımları: tek bir maddenin hâlleri sırayla', 'Kat izleri açılınca bile kâğıtta kalır: kalıp (خِلْقَة) budur.', b, 900, 660)
# 142 Çapraz bulmaca
@usul
def u142():
    b = []
    W2 = [('YARATMAK', 3, 5, 'h', 1, 'Ölçülen şey tamamlanınca (خَلَقَ)'), ('HUY', 1, 5, 'v', 2, 'Yaradılışta nefse verilen kalıp (خُلُق)'), ('AHLAK', 3, 6, 'v', 3, 'Huyların yerleşmiş düzeni (أَخْلَاق)'),
          ('PAY', 2, 8, 'v', 4, 'Bir iş için ayrılan (خَلَاق)'), ('KOKU', 3, 12, 'v', 5, 'Yüzeye sürülen (خَلُوق)'), ('ESKİMEK', 7, 0, 'h', 6, 'Düzlenen yüzeyin aşınması (خَلِقَ)')]
    cell = {}; num = {}
    for w, r, c, d, n, _ in W2:
        num[(r, c)] = n
        for i, ch in enumerate(w): cell[(r + (i if d == 'v' else 0), c + (i if d == 'h' else 0))] = ch
    s = 38; x0, y0 = 40, 90
    for (r, c), ch in cell.items():
        x, y = x0 + c * s, y0 + r * s; b.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="#fff" stroke="#2b2410" stroke-width="1.5"/>'); b.append(T(ch, x + s / 2, y + s / 2 + 6, 15, fill='#9db8d9', w='font-weight="700"'))
        if (r, c) in num: b.append(T(str(num[(r, c)]), x + 4, y + 11, 9, 'start', '#c0392b', 'font-weight="700"'))
    y = 100
    b.append(T('SOLDAN SAĞA', 600, y, 12, 'start', w='font-weight="700"')); y += 22
    for w, r, c, d, n, ip in W2:
        if d == 'h': y = paragraf(b, 600, y, f'{n}. {ip}', 40, 11) + 4
    y += 10; b.append(T('YUKARIDAN AŞAĞI', 600, y, 12, 'start', w='font-weight="700"')); y += 22
    for w, r, c, d, n, ip in W2:
        if d == 'v': y = paragraf(b, 600, y, f'{n}. {ip}', 40, 11) + 4
    b.append(T('İpucu mana, cevap kelimedir; kesişen harfler iki mananın bir kelimeden geldiğini hissettirir. Soluk harfler cevap anahtarıdır.', 450, 640, 10.5))
    kaydet('142_bulmaca', '142. Çapraz bulmaca: manalar ipucu, Türkçe karşılıklar cevap', 'Okuyan çözerken manayı kendi bulur.', b, 900, 660)
# 143 Mektup
@usul
def u143():
    b = ['<rect x="100" y="70" width="700" height="580" fill="#fdf6e3" stroke="#c9b27c" stroke-width="2"/>']
    y = 110; b.append(T('Aziz okuyucum,', 140, y, 14, 'start', w='font-style="italic" font-family="Georgia, serif"')); y += 30
    P = ['Ben خ ل ق kökü. Beni çoğunuz yalnız "yaratmak" diye tanırsınız; oysa ilk işim ölçüp biçmekti. Bir terzinin deriyi ölçtüğü, bir marangozun tahtayı biçtiği gün ben doğdum.',
         'Ölçtüğüm şey tamamlanınca ona "yaratılmış" dediniz; bana da, bu ölçünün sahibini anarken, Hâlık adını verdiniz. Yaratılan her şeyin bir kalıbı oldu: hilkat.',
         'Bu kalıp insanın içine yerleşince ona huy dediniz; huylar çoğalıp yerleşince ahlâk oldu. Bir de başkasının huyunu üstüne giyenler çıktı, onlara tehallük dediniz.',
         'Öbür kolum düzlemekti. Düzlenen yüzey zamanla aşınır; elbiseniz eskiyince "halika" dersiniz, paçavraya hulkân. Yüzeye sürülen kokuya halûk adını da bana borçlusunuz.',
         'Bir iş için ayırdığım ölçüye pay, işine uyana lâyık dediniz. En sevmediğim evladım ise ihtilâktır: olmayanı varmış gibi göstermek, benim sahtemdir.',
         'Kazanı (hılkîn) soracak olursanız, o benden değildir; Yunanistan\'dan gelmiş bir misafirdir.']
    for p in P: y = paragraf(b, 140, y, p, 100, 11.5, extra='font-family="Georgia, serif"') + 10
    b.append(T('Ölçüyle kalınız,', 760, y + 10, 13, 'end', w='font-style="italic" font-family="Georgia, serif"')); b.append(AR('خَلَقَ', 760, y + 40, 20, 'end'))
    kaydet('143_mektup', '143. Mektup: kök, birinci şahısla kendi aile hikâyesini anlatır', 'Bütün manalar bir hayat hikâyesinin sırasıyla, sebepleriyle.', b, 900, 670)
# 144 Bilmece
@usul
def u144():
    b = []
    R = [('Ölçülmeden yapılmam, yapılınca adım değişir;\nbeni yapana bir isim, bana başka bir isim verilir.', 'مَخْلُوق (yaratılmış)'), ('Gözle görülmem ama her hâlinde belliyim;\nyaradılışta konuldum, tekrarla sağlamlaştım.', 'خُلُق (huy)'),
         ('Yeniyken düzdüm, kullanıldıkça düzleştim,\nsonunda adım "eski" oldu.', 'خَلِقَ (eskidi)'), ('Yaratmanın taklidiyim, ölçüm yoktur;\nsöylenirim ama olmamışımdır.', 'اِخْتِلَاق (uydurma)'),
         ('Bir iş için ayrılırım, herkese düşmem;\nâhirette olmayanı ayet anar.', 'خَلَاق (pay)'), ('Ailedenmiş gibi dururum, kanım yoktur;\nmutfaktayım, aslım denizin ötesinde.', 'خِلْقِين (kazan)')]
    for k, (q, a) in enumerate(R):
        x = 40 + (k % 2) * 420; y = 80 + (k // 2) * 185
        b.append(f'<rect x="{x}" y="{y}" width="400" height="165" rx="10" fill="#fff" stroke="#2b2410"/>'); b.append(T(f'Bilmece {k+1}', x + 14, y + 22, 11, 'start', '#b3541e', 'font-weight="700"'))
        for j, l in enumerate(q.split('\n')): b.append(T(l, x + 200, y + 55 + j * 20, 12, w='font-style="italic"'))
        b.append(f'<g transform="rotate(180 {x+200} {y+135})">' + T('cevap: ' + a, x + 200, y + 140, 11, fill='#9a9a9a') + '</g>')
    kaydet('144_bilmece', '144. Bilmece: mana tarif edilir, kelime cevap olarak tersine yazılır', 'Okuyan önce tahmin eder, sonra kâğıdı çevirip cevaba bakar.', b, 900, 650)
# 145 Kaligram
@usul
def u145():
    b = []
    txt = ('خلق kökünün aslı ölçüp biçerek hazırlamaktır. Terzi deriyi ölçer, makasıyla biçer, parçaları birleştirir ve bir elbise yaratır. '
           'Yaratılan elbisenin bir kalıbı vardır; buna hilkat denir. Kalıp insanın içine girince huy olur, huylar yerleşince ahlâk olur. '
           'Elbise giyildikçe düzleşir, aşınır ve eskir; eskiyene halika, paçavraya hulkân denir. Elbiseye sürülen güzel koku halûktur. '
           'Bir iş için ayrılan kumaş paydır, bedene uyan elbise lâyıktır. Ölçüsüz biçilen sahte elbise ise uydurmadır, ihtilâktır. ') * 2
    def gen(y):
        if y < 150: return 120
        if y < 180: return 260
        if y < 330: return 200 - (y - 180) * .3
        return 160 + (y - 330) * 1.25
    pos = 0; y = 120
    ws = txt.split(); i = 0
    while y < 620 and i < len(ws):
        w = gen(y); n = int(w / 5.4); line = ''
        while i < len(ws) and len(line) + len(ws[i]) + 1 <= n: line = (line + ' ' + ws[i]).strip(); i += 1
        if not line: line = ws[i]; i += 1
        b.append(T(line, 450, y, 10, fill='#2b2410')); y += 14
    b.append(AR('خَلَقَ', 450, 100, 24, fill='#b3541e'))
    kaydet('145_kaligram', '145. Kaligram: yazının kendisi bir elbise şekli alır', 'Metin, anlattığı şeyin (ölçülüp biçilen elbisenin) şeklinde dizilir.', b, 900, 640)
# 146 Matruşka
@usul
def u146():
    b = []
    D = [('ahlâk', 'أَخْلَاق', '#7a3fb3'), ('huy', 'خُلُق', '#8e6cc7'), ('yaradılış', 'خِلْقَة', '#2f6fb3'), ('yaratılmış', 'مَخْلُوق', '#5b8fc9'), ('yaratmak', 'خَلَقَ', '#7fa6cc'), ('ölçüp biçmek', 'خَلَقَ', '#9db8d9'), ('ESAS', 'خ ل ق', '#e8c766')]
    x = 60
    for k, (ad, ar, c) in enumerate(D):
        s = 1 - k * .11; h = 300 * s; w = 140 * s; y = 520 - h
        b.append(f'<path d="M{x},{520} C{x-w*.1},{y+h*.5} {x+w*.12},{y+h*.32} {x+w*.25},{y+h*.3} C{x+w*.05},{y} {x+w*.95},{y} {x+w*.75},{y+h*.3} C{x+w*.88},{y+h*.32} {x+w*1.1},{y+h*.5} {x+w},{520}Z" fill="{c}" stroke="#2b2410" stroke-width="2"/>')
        b.append(f'<circle cx="{x+w/2}" cy="{y+h*.2}" r="{w*.2}" fill="#f5e1c8" stroke="#2b2410"/>'); b.append(AR(ar, x + w / 2, y + h * .65, 16 * s + 4)); b.append(T(ad, x + w / 2, 545, 11, w='font-weight="700"'))
        x += w + 16
    b.append(T('Dıştaki bebek açılınca içinden bir önceki çıkar; en içte esas durur. Her dış kat, içindekini kuşatarak doğmuştur.', 450, 600, 11))
    kaydet('146_matruska', '146. Matruşka: her mana bir önceki manayı içinde taşır', 'Ahlâkı açan, huyu bulur; huyu açan yaradılışı… en içte ölçüp biçmek.', b, 900, 630)
# 147 Dokuma
@usul
def u147():
    b = []
    warp = [('خ', '#b8860b'), ('ل', '#b8860b'), ('ق', '#b8860b'), ('م', '#c0392b'), ('ا', '#2f6fb3'), ('و', '#3f8f3a'), ('ت', '#7a3fb3'), ('ي', '#a8478f')]
    weft = ['خَلَقَ', 'خَالِق', 'مَخْلُوق', 'خُلُق', 'أَخْلَاق', 'تَخَلَّقَ', 'اِخْتَلَقَ', 'خَلِيق', 'خُلْقَان']
    x0, y0, cw, ch = 220, 110, 70, 50
    for j, (h, c) in enumerate(warp): b.append(AR(h, x0 + j * cw + cw / 2, y0 - 12, 20, fill=c))
    for i, w in enumerate(weft):
        b.append(AR(w, x0 - 20, y0 + i * ch + ch / 2 + 6, 16, 'end'))
        harf = set(w.replace('أ', 'ا').replace('إ', 'ا'))
        for j, (h, c) in enumerate(warp):
            x, y = x0 + j * cw, y0 + i * ch; on = h in harf
            if on: b.append(f'<rect x="{x+3}" y="{y+8}" width="{cw-6}" height="{ch-16}" rx="10" fill="{c}" fill-opacity=".85"/>')
            else: b.append(f'<rect x="{x+cw/2-6}" y="{y}" width="12" height="{ch}" fill="{c}" fill-opacity=".25"/><rect x="{x}" y="{y+ch/2-4}" width="{cw}" height="8" fill="#ccc"/>')
    b.append(T('Dikey iplikler (çözgü) harflerdir: altın üçü köktür. Yatay iplik (atkı) bir kelimedir.', 450, 590, 11))
    b.append(T('Atkı bir çözgünün üstünden geçince o harf kelimede vardır. Kök ipliği her satırda görünür: kumaşın deseni ailenin kendisidir.', 450, 610, 11))
    kaydet('147_dokuma', '147. Dokuma: harfler çözgü, kelimeler atkı, desen ailenin ortak dokusu', 'Hangi harfin hangi kelimede "üste çıktığı" ilmekten görülür.', b, 900, 630)
# 148 Müze vitrini
@usul
def u148():
    b = ['<rect x="30" y="70" width="840" height="560" fill="#2b2a33"/>']
    E2 = [('Eser 1', 'Terzi makası ve arşın', 'خَلَقَ', 'Kökün ilk manası: ölçüp biçmek. Bu alet olmadan hiçbir şey "yaratılmazdı".', '<path d="M-30,-20 L30,20 M-30,20 L30,-20" stroke="#d9c38a" stroke-width="5"/><circle cx="-34" cy="-22" r="8" fill="none" stroke="#d9c38a" stroke-width="3"/><circle cx="-34" cy="22" r="8" fill="none" stroke="#d9c38a" stroke-width="3"/>'),
          ('Eser 2', 'Bitmiş bir kaftan', 'مَخْلُوق', 'Ölçülen şey tamamlanınca "yaratılmış" olur.', '<path d="M-25,-35 L25,-35 L40,40 L-40,40Z" fill="#7fa6cc"/>'),
          ('Eser 3', 'Kaftanın kalıbı', 'خِلْقَة', 'Her yaratılanın kalıbı, yaradılışıdır.', '<path d="M-25,-35 L25,-35 L40,40 L-40,40Z" fill="none" stroke="#fff" stroke-dasharray="5 3" stroke-width="2"/>'),
          ('Eser 4', 'Bir kalp (nefs)', 'خُلُق', 'Kalıp içe girince huy olur.', '<path d="M0,25 C-45,-5 -25,-40 0,-15 C25,-40 45,-5 0,25Z" fill="#c0392b"/>'),
          ('Eser 5', 'Yıpranmış bir hırka', 'خَلَق', 'Düzlenen yüzey aşınır: eski.', '<path d="M-25,-35 L25,-35 L40,40 L-40,40Z" fill="#888"/><path d="M-10,0 l8,10 l-6,8 M10,-10 l6,6" stroke="#2b2a33" stroke-width="3"/>'),
          ('Eser 6', 'Koku şişesi', 'خَلُوق', 'Yüzeye sürülen ıtır.', '<rect x="-15" y="-20" width="30" height="45" rx="6" fill="#a8478f"/><rect x="-6" y="-34" width="12" height="14" fill="#d9c38a"/>')]
    for k, (no, ad, ar, ac, sek) in enumerate(E2):
        x = 110 + (k % 3) * 275; y = 170 + (k // 3) * 250
        b.append(f'<rect x="{x-65}" y="{y-80}" width="130" height="140" fill="#3a3945" stroke="#555"/><rect x="{x-65}" y="{y+60}" width="130" height="6" fill="#d9c38a"/>'); b.append(f'<g transform="translate({x},{y-10})">{sek}</g>')
        b.append(f'<rect x="{x+72}" y="{y-60}" width="125" height="130" fill="#f5f1e6"/>'); b.append(T(no, x + 80, y - 44, 9, 'start', '#777')); b.append(T(ad, x + 80, y - 28, 9.5, 'start', '#1a1a1a', 'font-weight="700"')); b.append(AR(ar, x + 190, y - 6, 15, 'end'))
        paragraf(b, x + 80, y + 14, ac, 24, 8.5)
    kaydet('148_muze', '148. Müze vitrini: her mana bir eşya, yanında künye etiketi', 'Eşyayı görüp etiketi okuyan, manayı bir nesneye bağlar.', b, 900, 650)
# 149 Sınav kâğıdı
@usul
def u149():
    b = ['<rect x="60" y="64" width="780" height="580" fill="#fff" stroke="#2b2410"/>']
    b.append(T('SINAV: خ ل ق kökü   ·   Adı Soyadı: ……………   ·   Puan: …/100', 450, 92, 12, w='font-weight="700"'))
    Q = [('خُلُق kelimesinin aslî manaya en yakın izahı hangisidir?', ['A) yaratılmış şey', 'B) nefse verilen kalıp', 'C) eskimiş elbise', 'D) pay'], 1),
         ('Aşağıdakilerden hangisi bu köke türeme yoluyla bağlanmaz?', ['A) خَلَاق', 'B) خَلِيق', 'C) خِلْقِين', 'D) خُلْقَان'], 2),
         ('"Elbise eskidi" mânâsı hangi koldan gelir?', ['A) ölçüp biçmek', 'B) düzlemek', 'C) pay ayırmak', 'D) yakışmak'], 1),
         ('اِخْتَلَقَ fiilini yaratmaktan ayıran şey nedir?', ['A) ölçüsüz, sahte oluşu', 'B) eşyaya yapılması', 'C) çoğul oluşu', 'D) zamanla olması'], 0)]
    y = 130
    for k, (q, ops, d) in enumerate(Q):
        b.append(T(f'{k+1}. {q}', 90, y, 12, 'start', w='font-weight="700"')); y += 24
        for j, o in enumerate(ops): b.append(f'<circle cx="{100+j*190}" cy="{y-4}" r="7" fill="none" stroke="#2b2410"/>'); b.append(T(o, 112 + j * 190, y, 10.5, 'start'))
        y += 50
    b.append(T('Cevap anahtarı (ters çevirin):', 90, 560, 10, 'start', '#6d6650')); b.append(f'<g transform="rotate(180 450 600)">' + T('1-B · 2-C · 3-B · 4-A', 450, 600, 12, fill='#9a9a9a') + '</g>')
    kaydet('149_sinav', '149. Sınav kâğıdı: bilgi önce sorulur, sonra öğretilir', 'Çeldiriciler en sık karışan manalardır; yanlış şık nereden karıştığını gösterir.', b, 900, 660)
# 150 Seyahatname
@usul
def u150():
    b = ['<rect x="80" y="64" width="740" height="590" fill="#f6eedb" stroke="#8a6d3b" stroke-width="2"/>']
    G = [('Birinci gün', 'Esas pınarından yola çıktım. Ölçüp biçmek denen bu pınar, bütün suların kaynağıdır.'), ('İkinci gün', 'Ölçü ırmağını izleyip Hâlık şehrine vardım. Ölçülen her şey burada tamamlanıp "yaratılmış" adını alıyor.'),
         ('Üçüncü gün', 'Hilkat köyünde her şeyin bir kalıbı olduğunu öğrendim. Köylüler kalıbı insanın içine koyunca ona huy diyorlar.'), ('Dördüncü gün', 'Ahlâk kalesine çıktım: huyların yerleşip düzene girdiği yer. Kalenin dibinde öfke yarlarını gördüm; huy taşınca oradan akıyor.'),
         ('Beşinci gün', 'Dönüşte Uydurma bataklığına saptım; olmayan yolu varmış gibi gösteriyordu. Ölçüsüz yaratma budur dedim, geri döndüm.'), ('Altıncı gün', 'Düzlük yaylasına geçtim. Burada her yüzey düzlenmiş, çokları aşınıp eskimiş; pazarda eski elbiselere hulkân diyorlar. Koku bahçelerinde halûk sürüyorlar.'),
         ('Yedinci gün', 'Pay pazarında herkesin işine ayrılan nasibini, Yakışık köprüsünde işine uyanı gördüm. Limanda bir kazan duruyordu; Yunan gemisiyle gelmiş, bu memleketten değilmiş.')]
    y = 100
    for gun, s in G: b.append(T(gun, 110, y, 12, 'start', '#8a5a00', 'font-weight="700" font-family="Georgia, serif"')); y = paragraf(b, 230, y, s, 90, 11.5, extra='font-family="Georgia, serif"') + 14
    kaydet('150_seyahatname', '150. Seyahatname: bir yolcu kökün memleketini gün gün gezer', 'Her gün bir mana; yolun sırası türemenin sırasıdır, yolcunun gözlemi sebebidir.', b, 900, 670)
if __name__ == '__main__':
    for f in S: f()
    print(len(S))

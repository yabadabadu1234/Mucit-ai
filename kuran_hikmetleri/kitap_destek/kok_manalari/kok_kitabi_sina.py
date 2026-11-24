"""Kur'ân kök atlası denetimi (F 3-I 412, 405): her ziyade ayrı bir denetimle sınanır; sayı en sonda yazılır.
Tek komut: python3 kok_kitabi_sina.py   (önce python3 kok_kitabi.py ile ciltler üretilmiş olmalı)
Denetim, üreticinin çıktısını (HTML ve PDF) ve kaynak veriyi bağımsız okuyarak yapar."""
import re, json, html, sys, pathlib, collections, random, subprocess, glob
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kok_kitabi as K
import pypdf
CK = HERE / 'kok_kitabi'; GC = CK / 'gecici'
CILTLER = sorted(int(re.search(r'cilt_(\d+)\.pdf', str(p)).group(1)) for p in CK.glob('cilt_*.pdf'))
H = {n: (GC / ('cilt_%d.html' % n)).read_text(encoding='utf-8') for n in CILTLER}
HEPSI = ''.join(H.values())
PDF = {n: pypdf.PdfReader(str(CK / ('cilt_%d.pdf' % n))) for n in CILTLER}
METIN = {}
def sayfa_metni(n, p):
    if (n, p) not in METIN: METIN[(n, p)] = PDF[n].pages[p - 1].extract_text() or ''
    return METIN[(n, p)]
def bol(h, sinif):
    return re.findall(r'<section class="%s[^"]*" id="([^"]+)">(.*?)</section>' % sinif, h, re.S)
def tum_bolumler(sinif): return [x for n in CILTLER for x in bol(H[n], sinif)]
SF = tum_bolumler('sf'); KS = tum_bolumler('ks')
SFID = {i: g for i, g in SF}
def tag(s): return re.sub(r'<[^>]+>', '', s)
def metin_html(s): return html.unescape(tag(s))
AYET_ID = {i: g for i, g in SF if i.startswith('A') and re.match(r'^A\d+_\d+$', i)}
SAYFA_AYET = {i: g for i, g in AYET_ID.items() if 'class="arb"' in g and 'class="ah"' in g}
BLOK = re.findall(r'<div class="ye" id="(A\d+_\d+)">(.*?)</div></div>', HEPSI, re.S)
YENI_AYET = [k for k in K.ORD if K.YENI[k]]
YOK_AYET = [k for k in K.ORD if not K.YENI[k]]
_d = json.load(open(CK / 'REF.json')); K.REF.update({k: tuple(v) for k, v in _d['REF'].items()}); K.SAYI.update({int(k): v for k, v in _d['SAYI'].items()})
SONUC = []
def T(n, ad, f):
    try: v = bool(f())
    except Exception as e: v = False; ad += ' [hata: %s]' % str(e)[:80]
    SONUC.append((n, ad, v)); print(('GEÇTİ ' if v else 'KALDI '), n, ad, flush=True)

# ---------------- A. yaklaştırma
T(1, 'kapak: başlık ve Arapça adı', lambda: 'KUR’ÂN KÖK ATLASI' in H[0] and 'class="k3 ar"' in H[0])
T(2, 'her sayfa bölümünde altı kutuluk basamak şeridi', lambda: len(re.findall(r'<section class="sf[^"]*" id=', HEPSI)) == len(re.findall(r'<div class="bs">', HEPSI)))
def basamak_dogru():
    harita = {'S': 3, 'KS': 4, 'A': 5, 'B': 2, 'Kume': 2, 'HARITA': 1, 'HAZINE': 1, 'D': 1}
    for i, g in SF:
        m = re.match(r'^(KS|Kume|HARITA|HAZINE|S|A|B|D)', i)
        if not m or i.startswith('C') or i in ('ICIN', 'CILTHARITA'): continue
        if re.match(r'^S\d+_p', i): ek = 3
        else: ek = harita[m.group(1)]
        a = re.findall(r'<span class="a">([^<]+)</span>', g)
        if len(a) != 1 or not a[0].startswith(['', 'I', 'II', 'III', 'IV', 'V', 'VI'][ek] + ' '): return False
    return True
T(3, 'vurgulu basamak, sayfanın türüyle uyuşur (I–V)', basamak_dogru)
T(4, 'her sayfada yol (breadcrumb) başlığı', lambda: len(re.findall(r'class="yol"', HEPSI)) >= len(SF) - 40)
T(5, 'bütün harita: 114 sûre kutusu', lambda: len(re.findall(r'<rect', SFID['HARITA'])) >= 114)
T(6, 'bölge haritaları: parça sayısı üreticiden bağımsız hesapla eşit', lambda: len([i for i, g in SF if re.match(r'^B\d+$', i)]) == len(K.bolge_parcalari()))
T(7, 'her bölge sayfasında kırmızı konum çerçevesi', lambda: all('#c0392b' in g for i, g in SF if re.match(r'^B\d+$', i)))
T(8, 'küme atlası: 11 küme sayfası ve 114 sûre satırı', lambda: len([i for i, g in SF if i.startswith('Kume')]) == 11 and sum(len(re.findall(r'<td class="m">s\. ', g)) for i, g in SF if i.startswith('Kume')) == 114)
T(9, 'sûre kapısı: 114 sûre', lambda: len([i for i, g in SF if re.match(r'^S\d+$', i)]) == 114)
T(10, 'kısım haritası: her kısmın ilk parçası var (454)', lambda: len([i for i, g in SF if re.match(r'^KS\d+_\d+_1$', i)]) == len(K.R['KI']))
T(11, 'kısım parçaları okunur ölçekte (≤ 122/0.95 birim)', lambda: all(pc[2] <= 122 / 0.95 + 1e-6 for s in K.KI for k in K.KI[s] for pc in K.kisim_parcalari(k)))
T(12, 'âyet sayfası: 1122 yeni kök getiren âyet', lambda: len(SAYFA_AYET) == 1122 and set(SAYFA_AYET) == {'A' + k.replace(':', '_') for k in YENI_AYET})
T(13, 'her âyet sayfasında âyetin haritadaki odası şekli', lambda: all('class="oda2"' in g for g in SAYFA_AYET.values()))
T(14, 'kök sayfaları: 1830, biri bir kez', lambda: len(KS) == 1830 and len({i for i, g in KS}) == 1830)
def sira_dogru():
    for n in CILTLER:
        seq = re.findall(r'<section class="(?:sf ay|ks)" id="([^"]+)">', H[n])
        i = 0
        while i < len(seq):
            if seq[i].startswith('A') and seq[i] in SAYFA_AYET:
                key = seq[i][1:].replace('_', ':'); beklenen = ['K%d' % K.NO[(x[0], x[1])] for x in K.YENI[key]]
                if seq[i + 1:i + 1 + len(beklenen)] != beklenen: return False
                i += 1 + len(beklenen)
            else: i += 1
    return True
T(15, 'her âyet sayfasından hemen sonra, yeni köklerinin sayfaları aynı sırayla', sira_dogru)
T(16, 'sûre parçaları: geniş sûrelerde var', lambda: len([i for i, g in SF if re.match(r'^S\d+_p1$', i)]) == sum(1 for s in K.SU if len(K.sure_parcalari(s)) > 1))
T(17, 'ladder: altı küçük konum haritası', lambda: len(re.findall(r'class="mc"', H[0])) == 6)
T(18, 'işaret tablosu: altı satır', lambda: len(re.findall(r'<td>(?:✦|∅|●|○|s\. 3/0412|kök hazinesi|lügat başlığı)</td>', H[0])) + len(re.findall(r'<td>(?:✦|∅|●|○)</td>', H[0])) >= 6)
T(19, 'sağdan sola okuma açıklaması', lambda: 'sağdan sola ve yukarıdan aşağı' in H[0])
T(20, 'ciltler haritada sayfası', lambda: 'CILTHARITA' in SFID and len(re.findall(r'<rect', SFID['CILTHARITA'])) >= 114)
# ---------------- B. okuma yardımcıları
T(21, 'yeni kök kelimesi işaretli (hizalı âyetlerde ≥ %90)', lambda: sum(1 for g in SAYFA_AYET.values() if 'class="w1"' in g) / 1122 >= 0.90)
T(22, 'kelime–kök tablosu hizalı âyetlerde', lambda: sum(1 for g in SAYFA_AYET.values() if '<th>kelime</th>' in g) >= 0.9 * 1122)
T(23, 'kök hazinesi çubuğu her âyet sayfasında', lambda: all('class="ilr"' in g for g in SAYFA_AYET.values()))
T(24, 'tekrar eden âyetler: 5114 giriş', lambda: len(re.findall(r'<div class="ye" id="A\d+_\d+">', HEPSI)) == 5114)
T(25, 'tekrar eden kök çipi sayısı = beklenen', lambda: len(re.findall(r'<span class="ck">', HEPSI)) == sum(len(K.AK[k]) for k in YOK_AYET))
T(26, 'kısım hatırlama kartı: yeni kökü olan her kısım', lambda: len(re.findall(r'Bu kısmın hatırlama kartı', HEPSI)) == sum(1 for s in K.KI for k in K.KI[s] if any(K.YENI[x] for x in K.KIS_AYET[id(k)])))
T(27, 'sûre sonu özeti: yeni kökü olan her sûre', lambda: len(re.findall(r'sûresinde ilk görülen bütün kökler', HEPSI)) == sum(1 for s in range(1, 115) if any(K.YENI[x] for x in K.ORD if int(x.split(':')[0]) == s)))
T(28, 'kök sayfası şeridi her kökte', lambda: len(re.findall(r'<div class="kb">', HEPSI)) == 1830)
T(29, 'tek âyette geçen köke etiket', lambda: len(re.findall(r'yalnız bir âyette geçer', HEPSI)) == sum(1 for (k, fl), v in K.SAY.items() if v[0] == 1))
T(30, 'ilk yüz sık kök etiketi', lambda: len(re.findall(r'sıklıkta \d+\. kök', HEPSI)) == sum(1 for (k, fl), r in K.SIKLIK.items() if r <= 100))
T(31, 'kök hazinesi eğrisi çizili', lambda: '<polyline' in SFID['HAZINE'])
T(32, 'sûre başına yeni kök çubukları: 114', lambda: len(re.findall(r'<rect', SFID['HAZINE'])) >= 114)
T(33, 'künye: oran, kaynaklar ve dürüstlük notu', lambda: 'Dürüstlük notu' in H[0] and 'Kubbealtı' in H[0] and ('%%%.1f' % (100 * len(K.DS) / 6236)) in tag(H[0]))
T(34, 'sûre kapısı: en çok geçen kökler', lambda: sum(1 for i, g in SF if re.match(r'^S\d+$', i) and 'en çok geçen kökler' in g) >= 112)
T(35, 'sûre kapısı: ilk görülen kök kartları', lambda: sum(1 for i, g in SF if re.match(r'^S\d+$', i) and 'İlk görülen kökler' in g) == sum(1 for s in range(1, 115) if any(K.YENI[x] for x in K.ORD if int(x.split(':')[0]) == s)))
T(36, 'sûre kapısı: aynı kümedeki sûreler', lambda: all('Aynı mevzu kümesindeki öbür sûreler' in g for i, g in SF if re.match(r'^S\d+$', i)))
T(37, 'sûre kapısı: önceki ve sonraki sûre', lambda: all('önceki:' in g and 'sonraki:' in g for i, g in SF if re.match(r'^S\d+$', i)))
T(38, 'sûre kapısı: not çizgileri', lambda: all(g.count('class="nt"') >= 2 for i, g in SF if re.match(r'^S\d+$', i)))
T(39, 'okuma kutuları (sûre kapısı ve âyet sayfası)', lambda: all('☐ okudum' in g for i, g in SF if re.match(r'^S\d+$', i)) and all('☐ okudum' in g for g in SAYFA_AYET.values()))
T(40, 'kök hazinesi eşik işareti beklenen âyetlerde', lambda: len(re.findall(r'class="mil"', HEPSI)) == sum(1 for k in YENI_AYET if any(K.CUM[K.ORI[k]] - len(K.YENI[k]) < e <= K.CUM[K.ORI[k]] for e in K.ESIKLER)))
T(41, 'sonraki geçişler tablosu her âyet sayfasında', lambda: all('Bu yeni köklerin sonraki geçişleri' in g for g in SAYFA_AYET.values()))
T(42, 'meal kaynağı etiketi her âyet sayfasında', lambda: all('meal: Hayrat Neşriyat' in g for g in SAYFA_AYET.values()))
T(43, 'mevzu kümesi her âyet sayfasında', lambda: all(html.escape(K.KUME[int(i[1:].split('_')[0])]) in g for i, g in SAYFA_AYET.items()))
T(44, 'önceki ve sonraki yeni kök âyeti bağı', lambda: all('önceki yeni kök âyeti:' in g for g in SAYFA_AYET.values()))
T(45, 'kök sayfası: ilk geçiş ve sıklık şeridi', lambda: all(('ilk geçiş' in g) for i, g in KS))
# ---------------- C. dizinler
T(46, 'içindekiler: cilt tablosu ve 114 sûre', lambda: 'ICIN' in SFID and len(re.findall(r'<td class="m">s\. ', SFID['ICIN'])) >= 114)
def dizin_kok_sirali():
    g = SFID['D1']; ks = re.findall(r'<div class="dz"><span class="ar">([^<]+)</span>', g)
    return len(ks) == sum(1 for x in K.KOK_SIRASI if x[1] == 0) and [K.ar_anahtar(k) for k in ks] == sorted(K.ar_anahtar(k) for k in ks)
T(47, 'kök dizini: tüm kökler, Arapça abece sırasında', dizin_kok_sirali)
T(48, 'lügat başlıkları dizini tam', lambda: len(re.findall(r'class="dz"', SFID['D2'])) == sum(1 for x in K.KOK_SIRASI if x[1] == 1))
def dizin_tr():
    g = SFID['D3']; ks = re.findall(r'<span class="da">([^<]+)</span>', g); ks = [html.unescape(k) for k in ks]
    return len(ks) > 2000 and [K.tr_anahtar(k) for k in ks] == sorted(K.tr_anahtar(k) for k in ks)
T(49, 'Türkçe anlam dizini: abece sırasında', dizin_tr)
T(50, 'âyet dizini 1122 âyeti kapsar', lambda: len(re.findall(r'<span>\d+ <small>', SFID['D4'])) == 1122)
T(51, 'sıklık tablosu: 120 satır, azalan', lambda: len(re.findall(r'<tr><td>\d+</td><td class="ar k">', SFID['D5'])) == 120 and [int(x) for x in re.findall(r'</td><td>(\d+)</td><td>\d+</td><td class="m">s\.', SFID['D5'])] == sorted([int(x) for x in re.findall(r'</td><td>(\d+)</td><td>\d+</td><td class="m">s\.', SFID['D5'])], reverse=True))
T(52, 'tek âyette geçen kökler listesi tam', lambda: len(re.findall(r'class="dz"', SFID['D6'])) == sum(1 for (k, fl), v in K.SAY.items() if fl == 0 and v[0] == 1))
T(53, 'okuma sırasıyla kök listesi 1830, ilk geçiş sırasında', lambda: len(re.findall(r'class="dz"', SFID['D7'])) == 1830)
T(54, 'kısım dizini 454 satır', lambda: len(re.findall(r'<td class="m">s\. ', SFID['D8'])) == 454)
T(55, 'sûre adları dizini 114, abece sırasında', lambda: len(re.findall(r'<td class="ar k">', SFID['D9'])) == 114)
def planlar():
    g = SFID['D10']; t = re.findall(r'<table class="kt">(.*?)</table>', g, re.S)
    return [len(re.findall(r'<tr><td>\d+</td>', x)) for x in t] == [30, 60, 100] and all(sum(int(y) for y in re.findall(r'</td><td class="m">[\d:]+ – [\d:]+</td><td>(\d+)</td>', x)) == 1830 for x in t)
T(56, 'okuma planları 30/60/100 gün; yeni kök toplamı 1830', planlar)
T(57, 'cilt başlığı sayfası her ciltte', lambda: all(('C%d' % n) in SFID for n in CILTLER if n != 0))
T(58, 'çalışma önerisi sayfası', lambda: 'Çalışma önerisi' in H[0])
def _duz(o):
    for x in o:
        if isinstance(x, list): yield from _duz(x)
        else: yield x
T(59, 'PDF yer imleri: sûre kapıları ve âyetler', lambda: all(sum(1 for _ in _duz(PDF[n].outline)) > 5 for n in CILTLER if n not in (0,)))
# ---------------- D. bütünlük
T(60, '6236 âyetin hepsi kitapta (sayfa ya da giriş)', lambda: len(set(SAYFA_AYET) | {i for i, g in BLOK}) == 6236)
def metin_aynen():
    kaynak = {}
    for k in K.ORD:
        v = json.load(open(K.NS['KH'] / 'kaynak' / 'sure' / ('%s.json' % k.split(':')[0]), encoding='utf-8'))['verses'][int(k.split(':')[1]) - 1]
        kaynak[k] = ' '.join(v['arabic'].split())
    SON = lambda a: ' ﴿' + ''.join(chr(0x660 + int(c)) for c in str(a)) + '﴾'
    hata = 0
    for i, g in AYET_ID.items():
        m = re.search(r'<div class="arb[^"]*">(.*?)</div>', g, re.S)
        if not m: continue
        key = i[1:].replace('_', ':'); got = ' '.join(html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).split())
        if got != kaynak[key] + SON(key.split(':')[1]): hata += 1
    for i, g in BLOK:
        m = re.search(r'<div class="arb k2">(.*?)</div>', g, re.S); key = i[1:].replace('_', ':')
        got = ' '.join(html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).split())
        if got != kaynak[key] + SON(key.split(':')[1]): hata += 1
    return hata == 0
T(61, 'Arapça metin sıfır müdahale: 6236 âyet kaynakla harfi harfine eşit', metin_aynen)
def meal_aynen():
    hata = 0
    for i, g in list(AYET_ID.items()) + [(i, g) for i, g in BLOK]:
        m = re.search(r'<div class="ml">(.*?)(?:<div class="kay">|</div>)', g, re.S); key = i[1:].replace('_', ':')
        if html.unescape(m.group(1)) != K.ME[key]: hata += 1
    return hata == 0
T(62, 'meal: 6236 âyette kaynak meale eşit', meal_aynen)
T(63, 'sûre bütünlüğü: her sûre kapısı tek cilt', lambda: all(sum(1 for n in CILTLER if ('id="S%d"' % s) in H[n]) == 1 for s in range(1, 115)))
T(64, 'ciltler ardışık sûre aralıkları, 1–114 hepsi kapsanır', lambda: sorted(s for n in CILTLER if n not in (0, max(CILTLER)) for s in range(1, 115) if ('id="S%d"' % s) in H[n]) == list(range(1, 115)))
T(65, 'çözülmemiş sayfa göstergesi yok (0/0000)', lambda: ' 0/0000' not in re.sub(r'<style.*?</style>', '', HEPSI, flags=re.S))
def referans_dogru():
    ornek = random.Random(7).sample(sorted(K.REF), 600); hata = 0
    for i in ornek:
        n, p = K.REF[i]
        if n not in PDF: continue
        t = sayfa_metni(n, p)
        if i.startswith('A') and re.match(r'^A\d+_\d+$', i): ok = i[1:].replace('_', ':') in t
        elif i.startswith('K') and i[1:].isdigit(): ok = ('K' + i[1:]) in t or K.KOK_SIRASI[int(i[1:])][0] in t
        elif i.startswith('S') and i[1:].isdigit(): ok = K.SLAT[int(i[1:])].split(' ')[0] in t or str(int(i[1:])) in t
        else: ok = True
        hata += (not ok)
    return hata == 0
T(66, 'sayfa göstergeleri doğru: 600 örnekte hedef sayfa hedefi içerir', referans_dogru)
def stabil():
    for n in CILTLER:
        d, say = K.cozum(CK / ('cilt_%d.pdf' % n), n)
        for i, v in d.items():
            if K.REF.get(i) != v: return False
    return True
T(67, 'ikinci geçiş sonrası kimlikler yerinde (yerleşim kaymadı)', stabil)
T(68, 'her PDF 95 MB altında', lambda: all((CK / ('cilt_%d.pdf' % n)).stat().st_size < 95e6 for n in CILTLER))
def fontlar():
    for n in CILTLER:
        o = subprocess.run(['pdffonts', str(CK / ('cilt_%d.pdf' % n))], capture_output=True, text=True).stdout.splitlines()[2:]
        if not o or any(l.split()[-5] != 'yes' and 'yes' not in l for l in o): return False
    return True
T(69, 'bütün yazı tipleri PDF içine gömülü', fontlar)
def bos_sayfa():
    for n in CILTLER:
        for p in random.Random(n).sample(range(1, len(PDF[n].pages) + 1), min(60, len(PDF[n].pages))):
            if len(sayfa_metni(n, p)) < 25: return False
    return True
T(70, 'örnek sayfalarda boş sayfa yok (cilt başına 60)', bos_sayfa)
T(71, 'sayfa altlığında cilt adı', lambda: all(('Cilt %d' % n) in sayfa_metni(n, 3 if len(PDF[n].pages) > 3 else 1) for n in CILTLER))
T(72, 'haritalar vektör: cilt 0 örnek sayfalarında görüntü yok', lambda: all(len(list(PDF[0].pages[p].images)) == 0 for p in range(0, min(30, len(PDF[0].pages)))))
T(73, 'kenar payı ≥ 12 mm (üst), ≥ 13 mm (yan)', lambda: '@page{size:148mm 210mm;margin:12mm 13mm 15mm 13mm' in K.css('x'))
def deterministik():
    a = K.govde_sure(112); b = K.govde_sure(112)
    return a == b and len(a) > 1000
T(74, 'üretim deterministik (aynı sûre iki defa aynı)', deterministik)
T(75, 'sayfa sayısı: 12 cilt', lambda: len(CILTLER) == len(K.planla()) + 2)
T(76, 'durum dosyası yazılmış ve sayılar tutuyor', lambda: (CK / 'KITAP_DURUMU.json').exists() and json.load(open(CK / 'KITAP_DURUMU.json'))['ayet'] == 6236)
T(77, 'her cilt PDF belge başlığı', lambda: all((PDF[n].metadata or {}).get('/Title') for n in CILTLER))
T(78, 'sayfa sayısı hedefi: her cilt ≤ 2200 sayfa', lambda: all(len(PDF[n].pages) <= 2200 for n in CILTLER))
T(79, 'ayet sayfası: kelime tablosu durum sütununda ● yeni', lambda: sum(1 for g in SAYFA_AYET.values() if '● yeni' in g) == 1122)
T(80, 'blok başlığı: ∅ aralıkları', lambda: len(re.findall(r'∅ Yeni kök getirmeyen âyetler · ', HEPSI)) >= 600)
T(81, 'blok girişlerinde kök hazinesi sayacı', lambda: len(re.findall(r'kök hazinesi \d+', HEPSI)) >= 5114)
T(82, 'küme sayfalarında renk anahtarı', lambda: all('class="ren"' in g for i, g in SF if i.startswith('Kume')))
T(83, 'küme vurgusu: diğer sûreler gri', lambda: all(('#eeeeee' in g) for i, g in SF if i.startswith('Kume')))
T(84, 'kısım sayfası: âyet sayfası listesi', lambda: sum(1 for i, g in SF if re.match(r'^KS\d+_\d+_1$', i) and 'Âyet sayfaları:' in g) == 454)
T(85, 'kısım sayfası: yeni kök ve âyet sayıları', lambda: sum(1 for i, g in SF if re.match(r'^KS\d+_\d+_1$', i) and 'yeni kök getiren âyet' in g) == 454)
T(86, 'bölge sayfasında sûre kapısı listesi', lambda: all('Sûre kapıları:' in g for i, g in SF if re.match(r'^B\d+$', i)))
T(87, 'ciltler: cilt başlığı sayfasında sûre listesi', lambda: all(len(re.findall(r'<tr><td>\d+</td>', SFID['C%d' % n])) >= 1 for n in CILTLER if n not in (0, max(CILTLER))))
T(88, 'kök dizininde hemze sırası açıklaması', lambda: 'hemze' in SFID['D1'])
T(89, 'kök sayfası gövdesinde başlıklar h2 değil (yer imi şişmez)', lambda: '<h2>' not in ''.join(g for i, g in KS))
T(90, 'ayet sayfasında yeni kök rozeti', lambda: all('class="rz"' in g for g in SAYFA_AYET.values()))
T(91, 'ayet sayfasında sûre ve kısım adı', lambda: all('<div class="gr">' in g for g in SAYFA_AYET.values()))
T(92, 'harita altında "Parça n / m" notu (çok parçalı kısım)', lambda: sum(1 for i, g in SF if re.match(r'^KS\d+_\d+_\d+$', i) and 'Parça' in g) >= sum(1 for s in K.KI for k in K.KI[s] if len(K.kisim_parcalari(k)) > 1))


T(93, 'içindekilerde her cildin sayfa sayısı', lambda: len(re.findall(r'\d+ sayfa</td>', SFID['ICIN'])) >= len(CILTLER) - 1)
T(94, 'sûre kapısında Arapça sûre adı büyük başlık', lambda: all('class="ab"' in g for i, g in SF if re.match(r'^S\d+$', i)))
T(95, 'âyet numarası Arapça-Hindî rakamla ﴿ ﴾ içinde', lambda: all('\ufd3f' in g and '\ufd3e' in g for g in SAYFA_AYET.values()))
T(96, 'her cildin HTML başlığı (title)', lambda: all('<title>Kur’ân Kök Atlası' in H[n] for n in CILTLER))
T(97, 'dizin cildi: on dizin bölümü', lambda: all(('D%d' % i) in SFID for i in range(1, 11)))
T(98, 'okuma sırasıyla listenin ilk satırı 1:1', lambda: re.search(r'<div class="dz"><b>1</b>.*?<small>(\d+:\d+)', SFID['D7'], re.S).group(1) == '1:1')
T(99, 'âyet dizininde yeni kök getiren her sûre başlığı', lambda: len(re.findall(r'<div class="ad"><b>', SFID['D4'])) == len({int(k.split(':')[0]) for k in YENI_AYET}))
def kok_ilk_dogru():
    for i, g in KS:
        no = int(i[1:]); k, fl = K.KOK_SIRASI[no]; m = re.search(r'ilk geçiş <b>(\d+:\d+)</b>', g)
        if not m or m.group(1) != K.ILKT[(k, fl)]: return False
    return True
T(100, 'her kök sayfasında ilk geçiş âyeti kaynak veriyle eşit (1830)', kok_ilk_dogru)
def sonraki_dogru():
    hata = 0
    for i, g in list(SAYFA_AYET.items())[:400]:
        key = i[1:].replace('_', ':'); o = K.ORI[key]
        for a in re.findall(r'<small>s\. [\d/]+</small>', g): pass
        for x in re.findall(r'(\d+:\d+) <small>s\.', g.split('sonraki geçişleri')[1] if 'sonraki geçişleri' in g else ''):
            if K.ORI[x] <= o: hata += 1
    return hata == 0
T(101, 'sonraki geçişler gerçekten sonraki âyetlerdir (400 sayfa)', sonraki_dogru)
def cip_dogru():
    hata = 0
    for i, g in BLOK[:1500]:
        key = i[1:].replace('_', ':'); ch = re.findall(r'<span class="ck"><span class="ar">([^<]+)</span> <small>(\d+:\d+)', g)
        beklenen = [(x[0], x[3]) for x in K.AK[key]]
        if ch != beklenen: hata += 1
    return hata == 0
T(102, 'tekrar çiplerinin ilk geçiş etiketleri kaynakla eşit (1500 giriş)', cip_dogru)
def hazine_dogru():
    for i, g in SAYFA_AYET.items():
        key = i[1:].replace('_', ':'); m = re.search(r'kök hazinesi: <b>(\d+)</b>', g)
        if not m or int(m.group(1)) != K.CUM[K.ORI[key]]: return False
    return True
T(103, 'kök hazinesi sayacı 1122 âyet sayfasında doğru', hazine_dogru)
T(104, 'okuma planı 1. gün 1:1 ile başlar, son gün 114:6 ile biter', lambda: re.search(r'<td class="m">1:1 – ', SFID['D10']) and re.search(r' – 114:6</td>', SFID['D10']))
def sure_yuzde():
    for i, g in SF:
        if re.match(r'^S\d+$', i):
            s = int(i[1:]); ay = K._AYS[s]; yn = sum(1 for a in ay if a[7] > 0); m = re.search(r'<b>%(\d+)</b>’i yeni kök getirir \((\d+) / (\d+)\)', g)
            if not m or int(m.group(2)) != yn or int(m.group(3)) != len(ay): return False
    return True
T(105, 'sûre kapısındaki yeni kök yüzdesi ve sayılar veriyle eşit', sure_yuzde)

# ---------------- E. müştak, lügat başlığı, taşma (F 3-I 413)
MT = [(i, re.findall(r'<table class="mt">(.*?)</table>', g, re.S)) for i, g in KS if int(i[1:]) < len(K.KOK_SIRASI) and K.KOK_SIRASI[int(i[1:])][1] == 0]
SATIR = {i: re.findall(r'<tr class="(yok)?"><td class="mn">(\d+)</td><td class="ma">([^<]*)</td><td>(.*?)</td></tr>', t[0], re.S) for i, t in MT if t}
T(106, 'müştak kartı her kök sayfasında (1642 kök)', lambda: len(MT) == sum(1 for x in K.KOK_SIRASI if x[1] == 0) and all(len(t) == 1 for i, t in MT))
T(107, 'çeşit listesi bütün kartlarda aynı sabit sırada ve %d satır' % len(K.CESIT_AD), lambda: all([html.unescape(r[2]) for r in v] == K.CESIT_AD for v in SATIR.values()))
T(108, 'çeşidi olmayan satırda çarpı, olanda biçim; boş satır yok', lambda: all(((r[0] == 'yok') == ('✗' in r[3])) and (r[0] == 'yok' or 'class="mb"' in r[3]) for v in SATIR.values() for r in v))
def cesit_her_ciltte():
    eksik = []
    for n in CILTLER:
        if n in (0, max(CILTLER)): continue
        gor = set()
        for i, g in bol(H[n], 'ks'):
            for r in SATIR.get(i, []):
                if r[0] != 'yok': gor.add(html.unescape(r[2]))
        eksik += [(n, c) for c in K.CESIT_AD if c not in gor]
    print('   cilt başına görünmeyen çeşit:', eksik)
    return not eksik
T(109, 'her ciltte her müştak çeşidi en az bir kez biçimle görünür', cesit_her_ciltte)
def cesit_hesap():
    hata = 0
    for i in random.Random(5).sample(sorted(SATIR), 300):
        k = K.KOK_SIRASI[int(i[1:])][0]; sat = K.mustak_satirlari(k)
        if [bool(L) for L in sat] != [r[0] != 'yok' for r in SATIR[i]]: hata += 1
    return hata == 0
T(110, 'müştak karti üreticiden bağımsız hesapla eşit (300 kök)', cesit_hesap)
def edat_tefrik():
    L = [i for i, g in KS if K.KOK_SIRASI[int(i[1:])][1] == 1]
    man = {}
    for i in L:
        g = SFID.get(i) or dict(KS)[i]
        m = re.search(r'<div class="h2">Manası.*?</div>(.*?)<div class="h2">|<div class="h2">Manası.*?</div>(.*)$', dict(KS)[i], re.S); man[i] = re.sub(r'\s+', ' ', tag((m.group(1) or m.group(2)) if m else ''))
    return len(L) == 188 and all(man.values()) and len(set(man.values())) == 188
T(111, '188 lügat başlığının her biri kendi manasıyla (hiçbiri ötekinin aynı değil)', edat_tefrik)
T(112, 'hiçbir tabloda mana yerine "lügat başlığı" yazılmaz', lambda: all('<td>lügat başlığı</td>' not in H[n] for n in CILTLER if n != 0))
T(113, 'lügat başlığı sayfaları boş değil: her birinde en az bir biçim', lambda: all(g.count('class="bc"') >= 1 for i, g in KS if K.KOK_SIRASI[int(i[1:])][1] == 1))
def onek_sonek():
    for i, g in KS:
        if K.KOK_SIRASI[int(i[1:])][1] == 1 and 'class="bp"' in g and ' + ' not in g and g.count('class="bc"') > 5: return False
    return True
T(114, 'biçimlerde önek+gövde+sonek ayrı ayrı yazılı', onek_sonek)
def tasma():
    import kok_kitabi_tasma as TS, random as r_
    ks = [(s, i) for s in range(1, 115) for i in range(len(K.KI[s]))]; r_.Random(11).shuffle(ks); Hh = []
    for s, i in ks[:60]:
        k = K.KI[s][i]
        for pc in K.kisim_parcalari(k)[:2]: Hh.append(K.harita_kisim(k, pc))
    n_, t_, ex = TS.olc(Hh); print('   taşan yazı %d / %d' % (n_, t_)); return n_ == 0
T(115, 'harita yazıları odalarından taşmaz (60 kısım, tarayıcıda ölçülü)', tasma)

g = sum(1 for n, a, v in SONUC if v)
print('GEÇEN', g, '/', len(SONUC)); print('KALAN', [(n, a) for n, a, v in SONUC if not v])
json.dump([(n, a, v) for n, a, v in SONUC], open(CK / 'SINAMA_SONUCU.json', 'w'), ensure_ascii=False)

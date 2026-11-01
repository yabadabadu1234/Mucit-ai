import json, os, sys, time, urllib.parse, urllib.request, collections

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIKI = os.path.join(KOK, 'vikipedi')
DURUM = os.path.join(VIKI, 'durum.json')
API = 'https://en.wikipedia.org/w/api.php'
BASLANGIC = 'Lists of mathematics topics'
ONEKLER = ('List of ', 'Lists of ', 'Outline of ', 'Glossary of ', 'Index of ', 'Table of ', 'Tables of ', 'Timeline of ')
KATEGORI_IZLERI = ('mathemat', 'algebra', 'geometr', 'topolog', 'logic', 'statistic', 'probabilit', 'number theory',
                   'calculus', 'combinator', 'graph theory', 'set theory', 'theorem', 'conjecture', 'equation',
                   'polyhed', 'polytop', 'integer sequence', 'numbers', 'functions', 'mathematical analysis',
                   'category theory', 'group theory', 'numeral', 'cryptograph', 'game theory', 'fractal')
AJAN = 'MucitLugat/1.0 (https://github.com/yabadabadu1234/Mucit-ai; lugat derleme betigi)'


def iste(params):
    params = dict(params, format='json', formatversion='2')
    url = API + '?' + urllib.parse.urlencode(params)
    for deneme in range(40):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': AJAN, 'Accept-Encoding': 'identity'})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:
            bekle = min(300, 5 * 2 ** min(deneme, 6))
            print('tekrar', deneme, e, 'bekleme', bekle, file=sys.stderr, flush=True)
            time.sleep(bekle)
    raise RuntimeError('istek başarısız: ' + url)


def liste_mi(baslik):
    return baslik.startswith(ONEKLER)


def riyazi_mi(kategoriler):
    k = ' '.join(kategoriler).lower()
    return any(iz in k for iz in KATEGORI_IZLERI)


def sahifeleri_cek(basliklar):
    netice = {}
    devam = {}
    while True:
        p = {'action': 'query', 'titles': '|'.join(basliklar), 'prop': 'links|categories',
             'pllimit': 'max', 'plnamespace': '0', 'cllimit': 'max', 'clshow': '!hidden', 'redirects': '1'}
        p.update(devam)
        cevap = iste(p)
        q = cevap.get('query', {})
        yonlendirme = {r['from']: r['to'] for r in q.get('redirects', [])}
        for s in q.get('pages', []):
            b = s['title']
            kayit = netice.setdefault(b, {'baglar': [], 'kategoriler': [], 'yok': 'missing' in s})
            kayit['baglar'] += [l['title'] for l in s.get('links', [])]
            kayit['kategoriler'] += [c['title'][9:] for c in s.get('categories', [])]
        for eski, yeni in yonlendirme.items():
            netice.setdefault('@' + eski, {'yonlendirme': yeni})
        if 'continue' in cevap:
            devam = {k: v for k, v in cevap['continue'].items()}
        else:
            return netice


def yukle():
    if os.path.exists(DURUM):
        return json.load(open(DURUM, encoding='utf-8'))
    return {'kuyruk': [[BASLANGIC, 0, '']], 'gezilen': {}, 'unsurlar': {}}


def kaydet(d):
    gecici = DURUM + '.gecici'
    json.dump(d, open(gecici, 'w', encoding='utf-8'), ensure_ascii=False)
    os.replace(gecici, DURUM)


def ciktilari_yaz(d):
    g = d['gezilen']
    with open(os.path.join(VIKI, 'gezinti_defteri.tsv'), 'w', encoding='utf-8') as f:
        f.write('başlık\tderinlik\tkimden\thâl\tbağ sayısı\tliste bağı sayısı\tkategoriler\n')
        for b in sorted(g, key=lambda x: (g[x]['derinlik'], x)):
            r = g[b]
            f.write('%s\t%d\t%s\t%s\t%d\t%d\t%s\n' % (b, r['derinlik'], r['kimden'], r['hal'], r['bag'], r['liste_bag'], ' · '.join(r['kategoriler'])))
    u = d['unsurlar']
    with open(os.path.join(VIKI, 'unsurlar.tsv'), 'w', encoding='utf-8') as f:
        f.write('unsur\tgeçtiği liste sayısı\tgeçtiği listeler\n')
        for b in sorted(u):
            f.write('%s\t%d\t%s\n' % (b, len(u[b]), ' | '.join(sorted(u[b]))))
    hal = collections.Counter(r['hal'] for r in g.values())
    with open(os.path.join(VIKI, 'DIZIN.md'), 'w', encoding='utf-8') as f:
        f.write('# Vikipedi Riyâziyât Listeleri Dizini\n\n')
        f.write('Bu sahife `araclar/vikipedi_tara.py` betiğiyle "%s" sahifesinden başlanarak liste atıf ağının otomatik taranmasıyla üretilir; elle değiştirilmez.\n\n' % BASLANGIC)
        f.write('Kuyrukta bekleyen sahife: %d · gezilen sahife: %d · riyâzî liste: %d · kapsam dışı: %d · bulunamayan: %d · toplanan farklı unsur: %d\n\n'
                % (len(d['kuyruk']), len(g), hal['riyâzî liste'], hal['kapsam dışı'], hal['bulunamadı'], len(u)))
        f.write('| Derinlik | Liste | Kimden gelindi | Unsur (bağ) sayısı | Liste bağı |\n| :-- | :-- | :-- | :-- | :-- |\n')
        for b in sorted(g, key=lambda x: (g[x]['derinlik'], x)):
            r = g[b]
            if r['hal'] != 'riyâzî liste':
                continue
            link = 'https://en.wikipedia.org/wiki/' + urllib.parse.quote(b.replace(' ', '_'))
            f.write('| %d | [%s](%s) | %s | %d | %d |\n' % (r['derinlik'], b, link, r['kimden'], r['bag'], r['liste_bag']))
        disarida = [b for b in g if g[b]['hal'] != 'riyâzî liste']
        if disarida:
            f.write('\n## Takip edilmeyen sahifeler\n\nBaşlığı liste kalıbında olup kategorisi riyâziyâta ait görünmeyen yahut bulunamayan sahifeler. Yanlış dışarıda kalan varsa `KATEGORI_IZLERI` genişletilip betik yeniden koşturulur.\n\n| Sahife | Hâl | Kimden |\n| :-- | :-- | :-- |\n')
            for b in sorted(disarida):
                f.write('| %s | %s | %s |\n' % (b, g[b]['hal'], g[b]['kimden']))


def main():
    d = yukle()
    sayac = 0
    while d['kuyruk']:
        parti = []
        while d['kuyruk'] and len(parti) < 20:
            b, der, kim = d['kuyruk'].pop(0)
            if b in d['gezilen'] or any(b == p[0] for p in parti):
                continue
            parti.append((b, der, kim))
        if not parti:
            continue
        cekilen = sahifeleri_cek([p[0] for p in parti])
        for b, der, kim in parti:
            gercek = cekilen.get('@' + b, {}).get('yonlendirme', b)
            if gercek != b and gercek in d['gezilen']:
                continue
            s = cekilen.get(gercek, {'yok': True, 'baglar': [], 'kategoriler': []})
            kayit = {'derinlik': der, 'kimden': kim, 'kategoriler': s['kategoriler'], 'bag': len(set(s['baglar'])), 'liste_bag': 0}
            if s['yok']:
                kayit['hal'] = 'bulunamadı'
            elif der > 0 and not riyazi_mi(s['kategoriler']):
                kayit['hal'] = 'kapsam dışı'
            else:
                kayit['hal'] = 'riyâzî liste'
                listeler = sorted({x for x in s['baglar'] if liste_mi(x)})
                kayit['liste_bag'] = len(listeler)
                for x in sorted(set(s['baglar'])):
                    if not liste_mi(x):
                        d['unsurlar'].setdefault(x, [])
                        if gercek not in d['unsurlar'][x]:
                            d['unsurlar'][x].append(gercek)
                for x in listeler:
                    if x not in d['gezilen']:
                        d['kuyruk'].append([x, der + 1, gercek])
            d['gezilen'][gercek] = kayit
        sayac += 1
        if sayac % 5 == 0:
            kaydet(d)
            print('gezilen', len(d['gezilen']), 'kuyruk', len(d['kuyruk']), 'unsur', len(d['unsurlar']), flush=True)
        time.sleep(2)
    kaydet(d)
    ciktilari_yaz(d)
    print('BİTTİ gezilen', len(d['gezilen']), 'unsur', len(d['unsurlar']))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'yaz':
        ciktilari_yaz(yukle())
    else:
        main()

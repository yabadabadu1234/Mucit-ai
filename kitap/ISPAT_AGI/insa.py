import json
import os
import sqlite3
from collections import Counter, defaultdict

import motor
from motor import USUL, HUCRE, SORU, KABUL_USUL, RANK
from veri_onerme import ONERMELER
from veri_soru import SORULAR, HUCRELER, FELSEFELER, OLUMSUZ
from veri_ispat import ISPATLAR

DIZIN = os.path.dirname(os.path.abspath(__file__))
KONTROLLER = []


def kontrol(ad, deger, beklenen, aciklama):
    KONTROLLER.append(dict(ad=ad, deger=deger, beklenen=beklenen, tamam=(deger == beklenen) if beklenen is not None else True, aciklama=aciklama))


def kimlik_denetimi(proofs):
    eksik = []
    for p in proofs:
        if p['usul'] not in USUL:
            eksik.append((p['id'], 'usul', p['usul']))
        if p['hucre'] not in HUCRE:
            eksik.append((p['id'], 'hucre', p['hucre']))
        for pr in p['prem']:
            if pr[:2] == 'P:':
                if pr[2:] not in {x['id'] for x in proofs}:
                    eksik.append((p['id'], 'oncul-ispat', pr))
            elif pr[:2] in ('H:', 'D:'):
                if pr[2:] not in HUCRE:
                    eksik.append((p['id'], 'oncul-hucre', pr))
            elif pr not in ONERMELER:
                eksik.append((p['id'], 'onerme', pr))
    for h in HUCRELER:
        if h['soru'] not in SORU:
            eksik.append((h['id'], 'soru', h['soru']))
        for c in h['kapsam_cerhi']:
            if c not in HUCRE:
                eksik.append((h['id'], 'kapsam', c))
        if h['alt_soru'] and h['alt_soru'] not in SORU:
            eksik.append((h['id'], 'alt_soru', h['alt_soru']))
    for f in FELSEFELER:
        for c in f['hucreler']:
            if c not in HUCRE:
                eksik.append((f['id'], 'felsefe-hucre', c))
    for o in OLUMSUZ:
        if o['hucre'] not in HUCRE:
            eksik.append(('olumsuz', 'hucre', o['hucre']))
        if o['usul'] not in USUL:
            eksik.append(('olumsuz', 'usul', o['usul']))
    return eksik


def kapsam_denetimi(atanan, hucre_atanan, proofs_by_id):
    ihlal = []
    for h in HUCRELER:
        if not h['kapsam_cerhi']:
            continue
        gerek = set(h['kapsam_cerhi'])
        tamam = False
        for i in hucre_atanan.get(h['id'], []):
            atif = {pr[2:] for pr in proofs_by_id[i]['prem'] if pr[:2] in ('H:', 'D:')}
            if gerek <= atif:
                tamam = True
        if not tamam:
            ihlal.append(h['id'])
    return ihlal


def ne_olur_hesapla(proofs, ozet, fd):
    aileler = defaultdict(list)
    for k, o in ONERMELER.items():
        if o['zayif']:
            aileler[o['aile'] or k].append(k)
    hedefler = []
    for a, ks in sorted(aileler.items()):
        hedefler.append(('aile', a, set(ks)))
        if len(ks) > 1:
            for k in ks:
                hedefler.append(('onerme', k, {k}))
    sonuc = []
    for tur, ad, kume in hedefler:
        atanan, ha, _ = motor.degerlendir(proofs, frozenset(kume))
        oz2 = motor.hucre_ozeti(atanan, ha)
        fd2 = motor.felsefe_durumlari(oz2)
        dusen = []
        for h in HUCRELER:
            a, b = ozet[h['id']], oz2[h['id']]
            if h['hukum'] != 'İHTİLAFLI' and b['anahtar'] < a['anahtar']:
                dusen.append(dict(hucre=h['id'], once=a['durum'], sonra=b['durum']))
        fdeg = []
        for f in FELSEFELER:
            a, b = fd[f['id']], fd2[f['id']]
            if a['durum'] != b['durum']:
                fdeg.append(dict(felsefe=f['id'], ad=f['ad'], once=a['durum'], sonra=b['durum']))
        sonuc.append(dict(tur=tur, ad=ad, onermeler=sorted(kume), hucre_say=len(dusen), hucreler=dusen, felsefe_say=len(fdeg), felsefeler=fdeg))
    return sonuc


def insa():
    proofs = motor.ispatlari_hazirla()
    proofs_by_id = {p['id']: p for p in proofs}
    eksik = kimlik_denetimi(proofs)
    assert not eksik, eksik
    atanan, hucre_atanan, bagsiz = motor.degerlendir(proofs)
    ozet = motor.hucre_ozeti(atanan, hucre_atanan)
    fd = motor.felsefe_durumlari(ozet)
    felsefe_say = Counter()
    for f in FELSEFELER:
        for c in f['hucreler']:
            if HUCRE[c]['hukum'] != 'DOĞRU':
                felsefe_say[c] += 1
    matrisler = []
    kombiler = []
    for h in HUCRELER:
        matrisler += motor.matris(h['id'], ozet, atanan, hucre_atanan, proofs_by_id, felsefe_say[h['id']])
        kombiler += motor.kombinasyonlar(h['id'], hucre_atanan.get(h['id'], []), atanan)
    ne_olur = ne_olur_hesapla(proofs, ozet, fd)

    kontrol('Kimliği bulunamayan öncül, usul, hücre, felsefe bağı', len(eksik), 0, 'Her kayıt var olan bir kimliğe bağlıdır.')
    kontrol('Zemine bağlanamayan (çember veya eksik dayanaklı) ispat', len(bagsiz), 0, 'Her ispat kendinden evvelki katmanlardaki ispatlara dayanır; kendi kendini destekleyen ispat atanamaz.')
    ihl = kapsam_denetimi(atanan, hucre_atanan, proofs_by_id)
    kontrol('Kapsam çürütmesini (kapsam_cerhi) atıf yapmadan kuran hücre', len(ihl), 0, 'kapsam_cerhi hücreleri en az bir ispatta fiilen öncül olmalıdır.')
    ispatsiz = [h['id'] for h in HUCRELER if h['hukum'] in ('DOĞRU', 'YANLIŞ') and ozet[h['id']]['durum'] in ('İSPATSIZ', 'KISMÎ')]
    kontrol('İspatsız veya yalnız kısmî delilli DOĞRU/YANLIŞ hücre', len(ispatsiz), 0, ', '.join(ispatsiz))
    ihtilafli_dogru = [p['id'] for p in proofs if p['tur'] == 'sibr' and HUCRE[p['hucre']]['hukum'] == 'İHTİLAFLI']
    kontrol('İHTİLAFLI hücreye hasırla “doğru” hükmü verilen durum', len(ihtilafli_dogru), 0, 'I9: İHTİLAFLI hücre kitabın iddiası değildir; hasırla doğru kılınmaz.')
    kontrol('Matris satırı (hücre × kabul edilmiş usul)', len(matrisler), len(HUCRELER) * len(KABUL_USUL), 'Hiçbir teçhizat hiçbir hücrede sessizce atlanmadı.')
    beklenen_komb = 0
    for h in HUCRELER:
        n = len({atanan[i]['usul'] for i in hucre_atanan.get(h['id'], [])})
        beklenen_komb += (1 << n) - 1
    kontrol('Kombinasyon satırı', len(kombiler), beklenen_komb, 'Her hücre için kullanılan usullerin bütün boş olmayan alt kümeleri yazıldı (2ⁿ−1).')
    degisen = [n for n in ne_olur if n['tur'] == 'aile' and n['hucre_say'] > 0]
    etkisiz = [n['ad'] for n in ne_olur if n['tur'] == 'aile' and n['hucre_say'] == 0]
    kontrol('Ayırt testi: zayıf aile düşünce hücre durumunu fiilen düşüren aile sayısı (sıfırdan büyük olmalı)', len(degisen) > 0, True,
            'Ölçü ayırt eder: zayıf öncül kaldırıldığında bağlı hücrelerin durumu düşer (F 3-B 27-B). Etkisiz aileler (başka ispatla ayakta): ' + ', '.join(etkisiz))
    kontrol('Etkisiz çıkan zayıf aile sayısı (bilgi)', len(etkisiz), None, ', '.join(etkisiz))
    ceviri = Counter(m['durum'] for m in matrisler)
    kontrol('YAPILMADI (usul şartı mümkün, kayıt yazılmamış açık iş) sayısı', ceviri['YAPILMADI'], None, 'Açık iş olarak sayılır; gizlenmez.')

    return dict(proofs=proofs, atanan=atanan, hucre_atanan=hucre_atanan, ozet=ozet, fd=fd, matrisler=matrisler, kombiler=kombiler, ne_olur=ne_olur,
                bagsiz=bagsiz, felsefe_say=felsefe_say)


def sqlite_yaz(s, yol):
    if os.path.exists(yol):
        os.remove(yol)
    c = sqlite3.connect(yol)
    c.executescript('''
    CREATE TABLE usul(id TEXT PRIMARY KEY, ad TEXT, grup TEXT, tur TEXT, atif TEXT, tanim TEXT, nasil TEXT, sart TEXT, hudut TEXT, safsata TEXT, tavan TEXT, mevki TEXT, ornek TEXT);
    CREATE TABLE onerme(id TEXT PRIMARY KEY, metin TEXT, tur TEXT, kat TEXT, aile TEXT, zayif INTEGER, not_ TEXT);
    CREATE TABLE soru(id TEXT PRIMARY KEY, ad TEXT, metin TEXT, hasir TEXT, hasir_notu TEXT, grup TEXT, atif TEXT, ust_hucre TEXT);
    CREATE TABLE hucre(id TEXT PRIMARY KEY, soru TEXT, ad TEXT, metin TEXT, hukum TEXT, tur TEXT, alt_soru TEXT, not_ TEXT, durum TEXT, kat INTEGER, en_iyi TEXT, ispat_say INTEGER, zayiflar TEXT);
    CREATE TABLE hucre_kapsam(hucre TEXT, kapsam_cerhi TEXT);
    CREATE TABLE ispat(id TEXT PRIMARY KEY, hucre TEXT, usul TEXT, tur TEXT, ozet TEXT, tag TEXT, hudut TEXT, sarti TEXT, kismi TEXT, katman INTEGER, kat INTEGER, durum TEXT, zayiflar TEXT, aileler TEXT);
    CREATE TABLE ispat_oncul(ispat TEXT, sira INTEGER, oncul TEXT, cins TEXT);
    CREATE TABLE matris(hucre TEXT, usul TEXT, durum TEXT, sebep TEXT);
    CREATE TABLE kombinasyon(hucre TEXT, maske INTEGER, usuller TEXT, boyut INTEGER, ispat_say INTEGER, kismi_say INTEGER, kat TEXT, durum TEXT, bagimlilik TEXT, zayiflar TEXT, yeterli INTEGER, asgari INTEGER, azami INTEGER);
    CREATE TABLE felsefe(id TEXT PRIMARY KEY, ad TEXT, aile TEXT, aciklama TEXT, not_ TEXT, durum TEXT, kalan TEXT);
    CREATE TABLE felsefe_hucre(felsefe TEXT, hucre TEXT, hukum TEXT, durum TEXT);
    CREATE TABLE olumsuz(hucre TEXT, sonuc TEXT, tur TEXT, usul TEXT);
    CREATE TABLE ne_olur(tur TEXT, ad TEXT, onermeler TEXT, hucre_say INTEGER, hucreler TEXT, felsefe_say INTEGER, felsefeler TEXT);
    CREATE TABLE kontrol(ad TEXT, deger INTEGER, beklenen INTEGER, tamam INTEGER, aciklama TEXT);
    ''')
    j = lambda x: json.dumps(x, ensure_ascii=False)
    for u in motor.USULLER:
        c.execute('INSERT INTO usul VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)', (u['id'], u['ad'], u['grup'], u['tur'], u['atif'], u['tanim'], j(u['nasil']), u['sart'], u['hudut'], u['safsata'], u['tavan'], u['mevki'], u['ornek']))
    for o in ONERMELER.values():
        c.execute('INSERT INTO onerme VALUES(?,?,?,?,?,?,?)', (o['id'], o['metin'], o['tur'], o['kat'], o['aile'], o['zayif'], o['not_']))
    for q in SORULAR:
        c.execute('INSERT INTO soru VALUES(?,?,?,?,?,?,?,?)', (q['id'], q['ad'], q['metin'], q['hasir'], q['hasir_notu'], q['grup'], q['atif'], q['ust_hucre']))
    for h in HUCRELER:
        o = s['ozet'][h['id']]
        c.execute('INSERT INTO hucre VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)', (h['id'], h['soru'], h['ad'], h['metin'], h['hukum'], h['tur'], h['alt_soru'], h['not_'], o['durum'], o['kat'], o['en_iyi'], o['ispat_say'], j(o['W'])))
        for k in h['kapsam_cerhi']:
            c.execute('INSERT INTO hucre_kapsam VALUES(?,?)', (h['id'], k))
    for p in s['proofs']:
        a = s['atanan'].get(p['id'])
        c.execute('INSERT INTO ispat VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (p['id'], p['hucre'], p['usul'], p['tur'], p['ozet'], j(p['tag']), p['hudut'], p['sarti'] or '', p['kismi'],
                  a['katman'] if a else None, a['kat'] if a else None, motor.durum_adi(a['kat'], a['W']) if a else 'BAĞSIZ', j(sorted(a['W'])) if a else '[]', j(sorted(a['fam'])) if a else '[]'))
        for i, pr in enumerate(p['prem']):
            cins = {'H:': 'hucre-H', 'D:': 'hucre-D', 'P:': 'ispat'}.get(pr[:2], 'onerme')
            c.execute('INSERT INTO ispat_oncul VALUES(?,?,?,?)', (p['id'], i + 1, pr[2:] if cins != 'onerme' else pr, cins))
    for m in s['matrisler']:
        c.execute('INSERT INTO matris VALUES(?,?,?,?)', (m['hucre'], m['usul'], m['durum'], m['sebep']))
    for k in s['kombiler']:
        c.execute('INSERT INTO kombinasyon VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)', (k['hucre'], k['mask'], ','.join(k['usuller']), k['boyut'], k['ispat_say'], k['kismi_say'], k['kat'], k['durum'], k['bagimlilik'], j(k['zayiflar']), int(k['yeterli']), int(k['asgari']), int(k['azami'])))
    for f in FELSEFELER:
        d = s['fd'][f['id']]
        c.execute('INSERT INTO felsefe VALUES(?,?,?,?,?,?,?)', (f['id'], f['ad'], f['aile'], f['aciklama'], f['not_'], d['durum'], j(d['kalan'])))
        for r in d['satirlar']:
            c.execute('INSERT INTO felsefe_hucre VALUES(?,?,?,?)', (f['id'], r['hucre'], r['hukum'], r['durum']))
    for o in OLUMSUZ:
        c.execute('INSERT INTO olumsuz VALUES(?,?,?,?)', (o['hucre'], o['sonuc'], o['tur'], o['usul']))
    for n in s['ne_olur']:
        c.execute('INSERT INTO ne_olur VALUES(?,?,?,?,?,?,?)', (n['tur'], n['ad'], j(n['onermeler']), n['hucre_say'], j(n['hucreler']), n['felsefe_say'], j(n['felsefeler'])))
    for k in KONTROLLER:
        c.execute('INSERT INTO kontrol VALUES(?,?,?,?,?)', (k['ad'], k['deger'], k['beklenen'], int(k['tamam']), k['aciklama']))
    c.commit()
    c.close()


def veri_paketi(s):
    ispat = []
    for p in s['proofs']:
        a = s['atanan'].get(p['id'])
        ispat.append(dict(id=p['id'], hucre=p['hucre'], usul=p['usul'], tur=p['tur'], ozet=p['ozet'], tag=p['tag'], hudut=p['hudut'], sarti=p['sarti'], kismi=p['kismi'],
                          prem=p['prem'], katman=a['katman'] if a else None, kat=a['kat'] if a else None,
                          durum=motor.durum_adi(a['kat'], a['W']) if a else 'BAĞSIZ', W=sorted(a['W']) if a else [], fam=sorted(a['fam']) if a else []))
    hucre = []
    for h in HUCRELER:
        o = s['ozet'][h['id']]
        hucre.append(dict(h, durum=o['durum'], kat=o['kat'], en_iyi=o['en_iyi'], ispat_say=o['ispat_say'], W=o['W'], fam=o['fam']))
    matris = defaultdict(dict)
    for m in s['matrisler']:
        matris[m['hucre']][m['usul']] = [m['durum'], m['sebep']]
    komb = defaultdict(list)
    for k in s['kombiler']:
        komb[k['hucre']].append([k['mask'], k['usuller'], k['ispat_say'], k['kismi_say'], k['kat'], k['durum'], k['bagimlilik'], k['zayiflar'], int(k['yeterli']), int(k['asgari']), int(k['azami'])])
    felsefe = []
    for f in FELSEFELER:
        d = s['fd'][f['id']]
        felsefe.append(dict(f, durum=d['durum'], kalan=d['kalan'], satirlar=d['satirlar']))
    return dict(
        usul=motor.USULLER, onerme=list(ONERMELER.values()), soru=SORULAR, hucre=hucre, ispat=ispat, matris=matris, komb=komb, felsefe=felsefe,
        olumsuz=OLUMSUZ, ne_olur=s['ne_olur'], kontrol=KONTROLLER, sifat_say=len([q for q in SORULAR if q['id'].startswith('Q10.')]))


def ozet_say(s):
    c_matris = Counter(m['durum'] for m in s['matrisler'])
    c_hucre = Counter(v['durum'] for v in s['ozet'].values())
    c_f = Counter(v['durum'] for v in s['fd'].values())
    c_ispat = Counter(p['tur'] for p in s['proofs'])
    return dict(hucre=dict(c_hucre), matris=dict(c_matris), felsefe=dict(c_f), ispat=dict(c_ispat), ispat_toplam=len(s['proofs']), kombinasyon=len(s['kombiler']),
                usul=len(KABUL_USUL), soru=len(SORULAR), hucre_say=len(HUCRELER), felsefe_say=len(FELSEFELER), onerme=len(ONERMELER))


def main():
    s = insa()
    sqlite_yaz(s, os.path.join(DIZIN, 'ispat_agi.sqlite'))
    paket = veri_paketi(s)
    paket['say'] = ozet_say(s)
    with open(os.path.join(DIZIN, 'ispat_agi.json'), 'w', encoding='utf-8') as f:
        json.dump(paket, f, ensure_ascii=False, indent=1)
    with open(os.path.join(DIZIN, 'sablon.html'), encoding='utf-8') as f:
        sablon = f.read()
    veri = json.dumps(paket, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    with open(os.path.join(DIZIN, 'ispat_agi.html'), 'w', encoding='utf-8') as f:
        f.write(sablon.replace('__VERI__', veri))
    print(json.dumps(paket['say'], ensure_ascii=False, indent=1))
    for k in KONTROLLER:
        print(('TAMAM ' if k['tamam'] else 'KIRMIZI'), k['ad'], k['deger'], '/', k['beklenen'])


if __name__ == '__main__':
    main()

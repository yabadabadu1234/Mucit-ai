import collections
import glob
import json
import os
import re
import sys

ARAPCA = re.compile(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿][؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿\sـ]*[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]')
KAYNAK_ADLARI = {'Cebel', 'Mekâyîs', 'Zemahşerî', 'Vikisözlük', 'EtymArab', 'Kamus', 'Vankulu', 'Kubbe', 'Kubbealtı', 'Altı', 'Arabic', 'Ontology', 'Ontoloji', 'Arapça', 'Remzi', 'Lugat', 'Lugat-ı', 'Luggat', 'WordNet', 'Esâsü\'l-Belâğa', 'Kuran', 'Kur\'ân', 'Korpusu', 'Korpus', 'Muhassas', 'Sıhâh', 'Lisân'}
KAYNAK_ANISI = re.compile(r'\b([A-ZÇĞİÖŞÜ][\w\'’âîû-]{2,})\s+(?:lügat\w*\s+)?(?:der|diyor|söyler|zikreder|kaydeder|bildirir|gösterir|verir)\b')
ETIKET = re.compile(r'⟨([^⟩\uFD3E)>]{1,30})[⟩\uFD3E>]')
HATALI_KAPAT = re.compile(r'⟨[^⟩⟨]{1,30}[\uFD3E>)]')


def iskelet(a):
    """Harekeleri ve ek işaretleri atar, elif/yâ biçimlerini birleştirir: alıntının ünsüz iskeleti kaynakta var mı diye bakılır."""
    a = re.sub(r'[\u064B-\u065F\u0670\u0640\u06D6-\u06ED]', '', a)
    a = a.translate({0x0623: 0x0627, 0x0625: 0x0627, 0x0622: 0x0627, 0x0671: 0x0627, 0x0649: 0x064A, 0x0629: 0x0647})
    return re.sub(r'\s+', ' ', a)


def kaynak_metni(dizin):
    t = []
    for f in glob.glob(os.path.join(dizin, 'KAYNAKLAR', '*')):
        t.append(open(f, encoding='utf-8').read())
    s = '\n'.join(t)
    s = s.encode('utf-8').decode('unicode_escape', errors='ignore') if False else s
    return iskelet(s)


def bolum_oku(yol):
    s = open(yol, encoding='utf-8').read()
    baslik, _, govde = s.partition('\n---\n')
    d = {}
    for sat in baslik.splitlines():
        if ':' in sat:
            k, _, v = sat.partition(':')
            d[k.strip()] = v.strip()
    satirlar = []
    for blok in govde.split('\n## ')[1:] if '\n## ' in govde else ('\n' + govde).split('\n## ')[1:]:
        ln = blok.splitlines()
        r = {'id': ln[0].strip()}
        for x in ln[1:]:
            if ':' in x:
                k, _, v = x.partition(':')
                r[k.strip()] = v.strip()
        satirlar.append(r)
    return d, satirlar


def denetle(yol, dizin, kay):
    d, sat = bolum_oku(yol)
    rapor = collections.OrderedDict()
    rapor['bolum'] = os.path.basename(yol)
    rapor['durum'] = d.get('durum')
    rapor['satir'] = len(sat)
    bos = [r['id'] for r in sat if not r.get('tercüme')]
    rapor['bos_tercume'] = len(bos)
    kisa = collections.Counter()
    sorunlar = collections.defaultdict(list)
    etk = collections.Counter()
    for r in sat:
        t = r.get('tercüme', '')
        if not t:
            continue
        ilk = t.split('⟨')[0].strip()
        kisa[ilk] += 1
        if not ilk:
            sorunlar['kisa_tercume_yok'].append(r['id'])
        if t.count('⟨') != t.count('⟩'):
            sorunlar['etiket_kapanis_hatali'].append(r['id'])
        for e in ETIKET.findall(t):
            etk[re.sub(r'\s*\d+$', '', e.strip())] += 1
        if len(re.findall(r'\b(?:Cebel|Mekâyîs|Zemahşerî|Vikisözlük|EtymArab|Kamus|Vankulu|Kubbe\s*Altı|Kubbealtı|Arabic\s+Ontology|Lugat-ı\s+Remzi|Sıhâh|Lisân)\b', t)) > 2:
            sorunlar['atif_yigini'].append(r['id'])
        for ad in KAYNAK_ANISI.findall(t):
            if ad not in KAYNAK_ADLARI and not ad.startswith(('Ne', 'Nasıl', 'Neden', 'Esas', 'Niçin')):
                sorunlar['kaynak_adi_bilinmeyen'].append((r['id'], ad))
        if re.search(r'[A-Za-zâîûÂÎÛçğıöşüÇĞİÖŞÜ][\u0600-\u06FF]|[\u0600-\u06FF][A-Za-zâîûÂÎÛçğıöşüÇĞİÖŞÜ]', t.replace('\uFD3E', ' ')):
            sorunlar['arapca_latin_karisik'].append(r['id'])
        if '⟨Tashih⟩' in t or 'Tashih' in t:
            sorunlar['tashih_notu'].append(r['id'])
        if r.get('ilave') not in ('', '-', None):
            sorunlar['ilave_dolu'].append(r['id'])
        if '⟨' not in t:
            sorunlar['serh_yok'].append(r['id'])
        elif '⟨Esas' not in t:
            sorunlar['esas_yok'].append(r['id'])
        elif 'Neden' not in t:
            sorunlar['neden_yok'].append(r['id'])
        # Arapça alıntı doğrulama
        for a in ARAPCA.findall(t.replace('\uFD3E', ' ').replace('\uFD3F', ' ')):
            an = iskelet(a).strip()
            if len(an.split()) >= 4:
                sorunlar['uzun_arapca_ibare'].append((r['id'], an[:40]))
            if len(an.split()) >= 3 and an not in kay:
                sorunlar['arapca_kaynakta_yok'].append((r['id'], an[:40]))
        if r.get('duz_tercume') and r['duz_tercume'] != '-' and ilk.lower() == r['duz_tercume'].lower():
            rapor['duz_ile_ayni'] = rapor.get('duz_ile_ayni', 0) + 1
    rapor['ayni_kisa_tercume'] = {k: v for k, v in kisa.items() if v > 1 and k}
    rapor['etiket_dagilimi'] = dict(etk.most_common(12))
    rapor['sorunlar'] = {k: (len(v), v[:3]) for k, v in sorunlar.items()}
    return rapor


if __name__ == '__main__':
    dizin = sys.argv[1]
    kay = kaynak_metni(dizin)
    for ad in sys.argv[2:]:
        print(json.dumps(denetle(os.path.join(dizin, ad), dizin, kay), ensure_ascii=False, indent=1))

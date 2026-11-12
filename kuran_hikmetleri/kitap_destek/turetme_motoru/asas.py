import os
import re
import zipfile

import istikak as I

ZIP = os.path.join(os.path.dirname(__file__), '..', '..', 'kaynak', 'lugat', 'ham', 'zemahseri_esasul_belaga_shamile_htm.zip')
KAYNAK = "Zemahşerî, Esâsü'l-Belâğa (tahkik: Muhammed Bâsil Uyûnü's-Sûd, Dâru'l-Kütübi'l-İlmiyye 1998; Şâmile, yazıya geçirilmiş metin)"
KITAP = {'الهمزة': 'ء', 'الباء': 'ب', 'التاء': 'ت', 'الثاء': 'ث', 'الجيم': 'ج', 'الحاء': 'ح', 'الخاء': 'خ', 'الدال': 'د', 'الذال': 'ذ', 'الراء': 'ر', 'الزاي': 'ز', 'السين': 'س', 'الشين': 'ش', 'الصاد': 'ص', 'الضاد': 'ض', 'الطاء': 'ط', 'الظاء': 'ظ', 'العين': 'ع', 'الغين': 'غ', 'الفاء': 'ف', 'القاف': 'ق', 'الكاف': 'ك', 'اللام': 'ل', 'الميم': 'م', 'النون': 'ن', 'الواو': 'و', 'الهاء': 'ه', 'الياء': 'ي'}
BASLIK = re.compile(r'^([ء-ي]{1,2})(?:\s([ء-ي]{1,2}))(?:\s([ء-ي]{1,2}))?$')


def baslik_kok(l, harf):
    m = BASLIK.match(l)
    if not m:
        return None
    k = I.normala(''.join(g for g in m.groups() if g))
    if 3 <= len(k) <= 4 and k[0] == harf:
        return k
    return None
MECAZ = re.compile(r'ومن المجاز\s*[:：]?')
KINAYE = re.compile(r'ومن الكناية\s*[:：]?')


def metin():
    z = zipfile.ZipFile(ZIP)
    ad = [n for n in z.namelist() if n.endswith('.htm')][0]
    t = z.read(ad).decode('cp1256', errors='replace')
    x = re.sub(r'<[^>]+>', '\n', t)
    return re.sub(r'&quot;', '"', re.sub(r'\n\s*\n+', '\n', x))


def yukle():
    satirlar = [l.strip() for l in metin().split('\n') if l.strip()]
    bloklar = []
    harf = ''
    for l in satirlar:
        mk = re.match(r'^كتاب (\S+)$', l)
        if mk and mk.group(1) in KITAP:
            harf = KITAP[mk.group(1)]
            continue
        k = baslik_kok(l, harf) if harf else None
        if k:
            bloklar.append([k, []])
        elif bloklar and not re.match(r'^\(\d+/\d+\)$', l) and not l.startswith('كتاب '):
            bloklar[-1][1].append(l)
    sonuc = {}
    for kok, sat in bloklar:
        t = '\n'.join(sat)
        m = MECAZ.search(t)
        hak = t[:m.start()].strip() if m else t.strip()
        mec = t[m.end():].strip() if m else ''
        kin = ''
        if mec:
            k = KINAYE.search(mec)
            if k:
                kin = mec[k.end():].strip()
                mec = mec[:k.start()].strip()
        e = {'kaynak': KAYNAK, 'hakikat': hak, 'mecaz': mec, 'kinaye': kin, 'mecaz_var': bool(mec)}
        if kok in sonuc:
            for a in ('hakikat', 'mecaz', 'kinaye'):
                sonuc[kok][a] = (sonuc[kok][a] + '\n' + e[a]).strip()
            sonuc[kok]['mecaz_var'] = sonuc[kok]['mecaz_var'] or e['mecaz_var']
        else:
            sonuc[kok] = e
    return sonuc

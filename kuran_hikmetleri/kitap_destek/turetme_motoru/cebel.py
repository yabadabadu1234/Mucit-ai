import os
import re
import urllib.parse
import urllib.request
import zipfile

import istikak as I

ZIP = os.path.join(os.path.dirname(__file__), '..', '..', 'kaynak', 'lugat', 'ham', 'cebel_mu_cem_istikaki_muassal_shamile_htm.zip')


def metin():
    z = zipfile.ZipFile(ZIP)
    ad = [n for n in z.namelist() if n.endswith('.htm')][0]
    t = z.read(ad).decode('cp1256', errors='replace')
    x = re.sub(r'<[^>]+>', '\n', t)
    return re.sub(r'\n\s*\n+', '\n', x)


def yukle():
    x = metin()
    ham = re.sub(r'&quot;', '"', x)
    basliklar = [(m.start(), m.group(1)) for m in re.finditer(r'^(.{3,40}?) وما يثلثهما\s*$', ham, flags=re.M)]
    kokler = [(m.start(), m.end(), m.group(1)) for m in re.finditer(r'•\s*\n?\s*\(([^()\n]{2,45})\)\s*:?', ham)]
    sonuc = {}
    for n, (s, e, ad) in enumerate(kokler):
        son = kokler[n + 1][0] if n + 1 < len(kokler) else len(ham)
        for bs_, _ in basliklar:
            if e < bs_ < son:
                son = bs_
                break
        blok = ham[e:son]
        fasil = ''
        giris = ''
        for bs, bad in basliklar:
            if bs < s:
                fasil = bad
                ilk = next((k_[0] for k_ in kokler if k_[0] > bs), len(ham))
                giris = ham[bs:ilk]
            else:
                break
        giris = re.sub(r'\n\(\d+/\d+\)', '', giris).strip()
        mih = ''
        m = re.search(r'°\s*المعنى المحوري\s*\n?', blok)
        if m:
            kes = blok[m.end():][:1400]
            kes = re.split(r'\n°|\n•|\n_{5,}', kes)[0]
            mih = re.sub(r'\s+', ' ', kes).strip()
        ses = ''
        m2 = re.search(r'\(صوتي[ًّ]*ا[ًّ]*\)\s*:(.{20,900}?)(?=\n\(\d+/\d+\)|\n\(\d+\)|\n°|\n•|\Z)', blok, flags=re.S)
        if m2:
            ses = re.sub(r'\s+', ' ', m2.group(1)).strip()
        for r in re.split(r'\s*-\s*', ad):
            k = I.normala(re.sub(r'[\s()]', '', r))
            if 2 <= len(k) <= 4 and k not in sonuc or (k in sonuc and mih and not sonuc[k]['mihveri']):
                sonuc[k] = {'kaynak': "Muhammed Hasan Hasan Cebel, el-Mu'cemü'l-İştikâkıyyü'l-Mü'asssal li-Elfâzi'l-Kur'âni'l-Kerîm (Şâmile, yazıya geçirilmiş metin)", 'fasil': fasil, 'baslik': ad, 'mihveri': mih, 'sesler': ses, 'tam_metin': blok.strip()}
    ozet = {}
    for v in sonuc.values():
        m = re.search(r'°\s*معنى الفصل المعجمي[^\n]*\n?(.{20,1500})', v['tam_metin'], flags=re.S)
        if m:
            ozet[v['fasil']] = re.sub(r'\s+', ' ', re.split(r'\n\(\d+/\d+\)', m.group(0))[0]).strip()
    for v in sonuc.values():
        v['fasil_ozeti'] = ozet.get(v['fasil'], '')
    return sonuc

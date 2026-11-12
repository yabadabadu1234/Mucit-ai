import bz2
import json
import re
import sys
import unicodedata


def sade(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if not unicodedata.combining(c))


def sayfalar(yol):
    with bz2.open(yol, 'rt', encoding='utf-8') as f:
        buf, ic = [], False
        for line in f:
            if '<page>' in line:
                buf, ic = [line], True
                continue
            if ic:
                buf.append(line)
            if '</page>' in line:
                ic = False
                yield ''.join(buf)


def main(girdi, cikti):
    ar2tr, en2tr = {}, {}
    for p in sayfalar(girdi):
        m = re.search(r'<title>([^<]+)</title>', p)
        if not m or ':' in m.group(1):
            continue
        baslik = m.group(1)
        t = p
        if '==Türkçe==' in t:
            for ln in t.split('\n'):
                if ln.lstrip('* ').startswith('Arapça:'):
                    for a in re.findall(r'\{\{ç\|ar\|([^}|]+)', ln):
                        ar2tr.setdefault(sade(a), []).append(baslik)
        if '==İngilizce==' in t:
            tanimlar = []
            for ln in t.split('\n'):
                if ln.startswith('# ') and not ln.startswith('#*'):
                    tanimlar += re.findall(r'\[\[([^\]|]+)', ln)
            if tanimlar:
                en2tr.setdefault(baslik.lower(), []).extend(tanimlar)
    json.dump({'ar2tr': ar2tr, 'en2tr': en2tr}, open(cikti, 'w', encoding='utf-8'), ensure_ascii=False)
    print('Arapça çeviri bağı', len(ar2tr), 'İngilizce başlık', len(en2tr))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

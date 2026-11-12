import glob
import html
import json
import lzma
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HAM = os.path.join(os.path.dirname(__file__), '..', '..', 'kaynak', 'lugat', 'ham', 'etymarab_polyglotta.jsonl.xz')
KOKLER = os.path.join(os.path.dirname(__file__), '..', '..', 'kelime_kaydi', 'kuranda_var', 'kokler')
HOST = 'https://polyglotta.uio.no/index.php'
HARF = {'ʔ': '', 'ʕ': 'ع', 'B': 'ب', 'T': 'ت', 'Ṯ': 'ث', 'Ǧ': 'ج', 'Ḥ': 'ح', 'Ḫ': 'خ', 'D': 'د', 'Ḏ': 'ذ', 'R': 'ر', 'Z': 'ز', 'S': 'س', 'Š': 'ش', 'Ṣ': 'ص', 'Ḍ': 'ض', 'Ṭ': 'ط', 'Ẓ': 'ظ', 'Ġ': 'غ', 'F': 'ف', 'Q': 'ق', 'K': 'ك', 'L': 'ل', 'M': 'م', 'N': 'ن', 'H': 'ه', 'W': '', 'Y': ''}


def indir(url):
    return subprocess.run(['curl', '-s', '--compressed', '-L', '-m', '150', url], capture_output=True, timeout=170).stdout.decode('utf-8', 'ignore')


def agac():
    t = indir(HOST + '?page=volume&vid=1268')
    m = re.findall(r'id="href_\d+\.([^"]*)" href="/index.php\?page=record&vid=1268&amp;level=(\d)&amp;cid=(\d+)"', t)
    return [(re.sub('<[^>]+>', '', n), l, c) for n, l, c in m]


def iskelet(ad):
    ad = re.sub(r'\(.*?\)', '', ad).split('/')[0].split(' ')[0]
    return ''.join(HARF.get(c, '') for c in ad.upper())


def getir(x):
    l, c = x
    for _ in range(6):
        try:
            b = indir('%s?page=record&vid=1268&level=%s&cid=%s' % (HOST, l, c))
            p = b.rfind('ajax_tree')
            q = b.find('</table>', p)
            rest = re.sub(r'<script.*?</script>|<style.*?</style>', '', b[q + 8:] if q > 0 else b, flags=re.S)
            m = re.search(r'Permanent link', rest)
            t = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', rest[:m.start()] if m else rest))).strip()
            if len(t) > 20 and 'Back to library' in t:
                return {'cid': c, 'level': l, 'text': t}
        except Exception:
            pass
    return None


def yaz(kayit):
    with lzma.open(HAM, 'wt', encoding='utf-8') as f:
        for r in kayit.values():
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def main(isci=3):
    kayit = {}
    if os.path.exists(HAM):
        for l in lzma.open(HAM, 'rt', encoding='utf-8'):
            r = json.loads(l)
            kayit[r['cid']] = r
    kur = {os.path.basename(f)[:-5] for f in glob.glob(KOKLER + '/*.json')}
    kur_is = {''.join(c for c in r if c not in 'ويءا') for r in kur}
    liste = [(n, l, c) for n, l, c in agac() if l == '2']
    ilk = [(l, c) for n, l, c in liste if iskelet(n) in kur_is and c not in kayit]
    son = [(l, c) for n, l, c in liste if iskelet(n) not in kur_is and c not in kayit]
    print('kayıtlı', len(kayit), 'öncelikli', len(ilk), 'kalan', len(son), flush=True)
    with ThreadPoolExecutor(isci) as ex:
        for i, r in enumerate(ex.map(getir, ilk + son)):
            if r:
                kayit[r['cid']] = r
            if i % 50 == 49:
                yaz(kayit)
                print(i + 1, len(kayit), flush=True)
    yaz(kayit)
    print('bitti', len(kayit), flush=True)


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)

import json
import re
import sys
import unicodedata


def sade(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if not unicodedata.combining(c))


def kok_bul(d):
    for t in d.get('etymology_templates', []) or []:
        if t.get('name') == 'ar-rootbox':
            a = t.get('args', {})
            harfler = [a[k] for k in sorted(a, key=lambda x: int(x) if x.isdigit() else 99) if k.isdigit()]
            if harfler:
                return ''.join(h.replace(' ', '') for h in harfler)
    for s in d.get('senses', []):
        for c in s.get('categories', []) or []:
            m = re.match(r'Arabic terms belonging to the root (.+)', c.get('name', ''))
            if m:
                return m.group(1).replace(' ', '')
    return None


def bicim(d):
    ht = d.get('head_templates') or []
    for h in ht:
        if h.get('name', '').startswith('ar-'):
            ex = h.get('expansion', '')
            lem = ex.split(' • ')[0].strip() if ' • ' in ex else d['word']
            form = None
            if h['name'] == 'ar-verb':
                form = (h.get('args', {}).get('1') or '').split('/')[0].split('~')[0].split('.')[0]
            return lem, h['name'], form, ex
    return d['word'], '', None, ''


def main(girdi, cikti):
    n = 0
    with open(girdi, encoding='utf-8') as f, open(cikti, 'w', encoding='utf-8') as o:
        for line in f:
            d = json.loads(line)
            k = kok_bul(d)
            if not k:
                continue
            lem, ht, form, ex = bicim(d)
            gl = []
            etk = set()
            for s in d.get('senses', []):
                for g in s.get('glosses', [])[:2]:
                    gl.append(g)
                etk.update(s.get('tags', []))
            kayit = {'k': k, 'l': lem, 'u': sade(lem), 'p': d['pos'], 'h': ht, 'f': form, 'g': gl[:6], 't': sorted(etk)[:8], 'e': ex}
            o.write(json.dumps(kayit, ensure_ascii=False) + '\n')
            n += 1
    print('yazıldı', n)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

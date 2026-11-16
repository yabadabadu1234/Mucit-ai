"""Kur'ân köklerinin esas manalarını kök dosyalarındaki sözlüklerden toplar (sebep yok, yalnız mana listesi)."""
import json, glob, re, pathlib
HERE = pathlib.Path(__file__).resolve().parent
KOK = HERE.parents[1] / 'kelime_kaydi/kuranda_var/kokler'
def parca(s):
    s = re.sub(r'\([^)]*\)', '', s)
    out = []
    for p in re.split(r'[;,/]| / ', s):
        p = p.strip(" .'\"")
        if ':' in p: p = p.split(':', 1)[1].strip()
        if p and p not in out and len(p) < 60: out.append(p)
    return out
def ekle(L, x):
    x = x.strip()
    if x and x.lower() not in [y.lower() for y in L]: L.append(x)
def etym(m):
    t = m.get('kok_maddesi', '') if isinstance(m, dict) else ''
    return [q.strip() for q in re.findall(r'‘([^’]+)’', t) if q.strip() and q.strip() != '…']
def mekayis_asil(L):
    for x in L or []:
        t = x.get('metin', '')
        m = re.search(r'[^.]*أَصْل[^.]*\.', t)
        if m: return m.group(0).strip()
    return ''
VT = {}
for f in sorted(glob.glob(str(KOK / '*.json'))):
    d = json.load(open(f, encoding='utf-8')); s = d.get('sozlukler', {}); k = d['kok']
    tr = []
    ka = s.get('kok_anlamlari') or {}
    for p in parca(ka.get('turkce', '')): ekle(tr, p)
    for p in ka.get('ihtimaller', []) or []:
        for q in parca(p): ekle(tr, q)
    if s.get('eyupipler_kok_anlami'):
        for q in parca(str(s['eyupipler_kok_anlami'])): ekle(tr, q)
    en = []
    for q in etym(s.get('etymarab') or {}):
        for p in re.split(r';', q):
            ekle(en, p)
    VT[k] = {'turkce': tr, 'ingilizce_etymarab': en, 'mekayis_asil': mekayis_asil(s.get('mekayis')),
             'cebel_mihver': ((s.get('cebel_mihveri') or {}).get('mihveri') or '').split('.')[0].strip()}
(HERE / 'KOK_ESAS_MANALARI.json').write_text(json.dumps(VT, ensure_ascii=False, indent=1), encoding='utf-8')
md = ['# Kur\'ân köklerinin esas manaları', '', f'{len(VT)} kök. Biçim: `kök: Türkçe manalar` · altında EtymArab İngilizce manaları, İbn Fâris\'in asıl cümlesi ve Cebel\'in mihver manası (kaynakta varsa).', '']
for k, v in VT.items():
    md.append(f'**{k}**: ' + ' / '.join(v['turkce']))
    if v['ingilizce_etymarab']: md.append(f'  - EtymArab: ' + ' / '.join(v['ingilizce_etymarab']))
    if v['mekayis_asil']: md.append(f'  - Mekâyîs: {v["mekayis_asil"]}')
    if v['cebel_mihver']: md.append(f'  - Cebel: {v["cebel_mihver"]}')
(HERE / 'KOK_ESAS_MANALARI.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
import statistics
print(len(VT), 'Türkçe ort', statistics.mean(len(v['turkce']) for v in VT.values()), 'Türkçesiz', sum(not v['turkce'] for v in VT.values()),
      'EtymArab dolu', sum(bool(v['ingilizce_etymarab']) for v in VT.values()), 'Mekâyîs', sum(bool(v['mekayis_asil']) for v in VT.values()))
for k in ['خلق', 'قطع', 'فرق', 'ضرب']: print(k, VT.get(k, {}).get('turkce'), VT.get(k, {}).get('ingilizce_etymarab')[:12] if VT.get(k) else '')

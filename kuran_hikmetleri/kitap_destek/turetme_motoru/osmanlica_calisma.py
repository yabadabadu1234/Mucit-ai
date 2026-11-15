import json
import os
import sys

import osmanlica_muhur as M

KOKDIZIN = os.path.join(M.CIKTI, 'kuranda_var', 'calisma')


def hazirla(kok, bolum_boyu=20):
    f = os.path.join(M.GIRDI, 'kuranda_var', 'kokler', kok + '.json')
    d = json.load(open(f, encoding='utf-8'))
    ad = os.path.join(KOKDIZIN, kok)
    os.makedirs(os.path.join(ad, 'KAYNAKLAR'), exist_ok=True)
    kim = M.kimlik_kur(d)
    for k, v in kim['sozlukler'].items():
        json.dump(v, open(os.path.join(ad, 'KAYNAKLAR', 'sozluk_' + k + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k in ('ses_mana_tasnif', 'hakikat_mecaz_tasnif', 'prototip_yayilim_tasnif'):
        json.dump(kim[k], open(os.path.join(ad, 'KAYNAKLAR', k + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(os.path.join(ad, 'KAYNAKLAR', 'wordnet_dayanak.txt'), 'w', encoding='utf-8').write(kim['wordnet_dayanak_tanimi'] + '\n')
    A, U = M.toplama(d)
    kl = d.get('kaliplar') or {}
    satirlar = {'kok': [], 'kelime': [], 'mustak': {}}
    for k, (t, c) in U.items():
        if t in ('S', 'KA'):
            satirlar['kok'].append((k, '%s  (%s)' % (c['kok'], 'fiil sapı' if t == 'S' else 'kök anlamı satırı; başlıklar: ' + ' | '.join(c.get('adlar', []))), ''))
        elif t == 'K':
            satirlar['kelime'].append((k, c['arapca'], 'tür: %s; bâb: %s; zaman: %s; %s' % (c['sozluk_turu'], c['bab'], c['zaman'], 'LEMMA (sözlük biçimi)' if c['tip'] == 'lemma' else 'kelime biçimi')))
        elif t == 'M':
            x = kl.get(str(c['idx'])) or ['', '', '', '']
            satirlar['mustak'].setdefault(c['kalip'], []).append((c['idx'], k, c['arapca'], 'kalıp: %s; vezin: %s (%s); ingilizce_tanik: %s' % (c['kalip'], x[1], x[2], c['tanik'])))
    bolumler = []
    bolumler.append(('kok', 'Kök anlamı ve fiil sapı', [(k, a, b) for k, a, b in satirlar['kok']]))
    kel = satirlar['kelime']
    for i in range(0, len(kel), bolum_boyu):
        bolumler.append(('kelime', 'Kelime biçimleri', kel[i:i + bolum_boyu]))
    for kal, li in satirlar['mustak'].items():
        li.sort()
        for i in range(0, len(li), bolum_boyu + 5):
            bolumler.append(('mustak', kal, [(k, a, b) for _, k, a, b in li[i:i + bolum_boyu + 5]]))
    for n, (tur, baslik, li) in enumerate(bolumler):
        yol = os.path.join(ad, 'bolum_%02d_%s.md' % (n, tur))
        g = ['durum: bos', 'bolum: %s — %s' % (tur, baslik), 'tercume_eden: -', 'inceleyen: -', '', '---', '']
        for k, a, b in li:
            g += ['## ' + k, 'arapça: ' + a, 'bilgi: ' + b, 'tercüme:', 'ilave:', '']
        open(yol, 'w', encoding='utf-8').write('\n'.join(g))
    print(kok, 'bölüm', len(bolumler), 'satır', sum(len(x[2]) for x in bolumler))


if __name__ == '__main__':
    hazirla(sys.argv[1])

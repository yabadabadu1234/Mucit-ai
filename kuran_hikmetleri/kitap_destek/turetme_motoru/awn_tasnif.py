import collections
import os

import istikak as I
import kaikki_suz as K
from nltk.corpus import wordnet as W

UST = {
    'noun.person': 'insan ve toplum', 'noun.group': 'insan ve toplum', 'noun.possession': 'insan ve toplum', 'noun.state': 'hâl ve vasıf',
    'noun.attribute': 'hâl ve vasıf', 'noun.relation': 'hâl ve vasıf', 'noun.feeling': 'his ve nefis', 'noun.motive': 'his ve nefis',
    'noun.cognition': 'zihin ve ilim', 'noun.communication': 'söz ve haber', 'noun.act': 'fiil ve hadise', 'noun.event': 'fiil ve hadise',
    'noun.process': 'fiil ve hadise', 'noun.phenomenon': 'tabiat', 'noun.object': 'tabiat', 'noun.substance': 'tabiat', 'noun.Tops': 'tabiat',
    'noun.animal': 'canlı ve beden', 'noun.plant': 'canlı ve beden', 'noun.body': 'canlı ve beden', 'noun.food': 'canlı ve beden',
    'noun.artifact': 'cisim ve eşya', 'noun.shape': 'ölçü, mekân ve zaman', 'noun.location': 'ölçü, mekân ve zaman',
    'noun.quantity': 'ölçü, mekân ve zaman', 'noun.time': 'ölçü, mekân ve zaman',
    'verb.body': 'canlı ve beden', 'verb.consumption': 'canlı ve beden', 'verb.change': 'fiil ve hadise', 'verb.contact': 'fiil ve hadise',
    'verb.creation': 'fiil ve hadise', 'verb.motion': 'fiil ve hadise', 'verb.cognition': 'zihin ve ilim', 'verb.perception': 'zihin ve ilim',
    'verb.communication': 'söz ve haber', 'verb.competition': 'insan ve toplum', 'verb.possession': 'insan ve toplum', 'verb.social': 'insan ve toplum',
    'verb.emotion': 'his ve nefis', 'verb.stative': 'hâl ve vasıf', 'verb.weather': 'tabiat', 'adj.all': 'hâl ve vasıf', 'adj.pert': 'hâl ve vasıf',
    'adj.ppl': 'hâl ve vasıf', 'adv.all': 'hâl ve vasıf',
}

TAB = os.path.expanduser('~/nltk_data/corpora/omw-1.4/arb/wn-data-arb.tab')


def yukle():
    kok_syn = collections.defaultdict(set)
    lem_syn = collections.defaultdict(set)
    for l in open(TAB, encoding='utf-8'):
        if l.startswith('#'):
            continue
        p = l.rstrip('\n').split('\t')
        if len(p) < 3:
            continue
        if p[1] == 'arb:lemma:root':
            kok_syn[I.normala(p[2].replace(' ', ''))].add(p[0])
        elif p[1] == 'arb:lemma':
            lem_syn[K.sade(p[2])].add(p[0])
    return kok_syn, lem_syn


def synset(o):
    try:
        return W.synset_from_pos_and_offset(o[-1], int(o[:8]))
    except Exception:
        return None


def ata(s, derinlik):
    yol = s.hypernym_paths()[0]
    return yol[min(derinlik, len(yol) - 1)]


def sinifla(kokler, derinlik=5):
    kok_syn, lem_syn = yukle()
    sonuc = {}
    for k, r in kokler.items():
        oy = collections.Counter()
        for o in kok_syn.get(k, ()):
            oy[o] += 2
        lem = set()
        for e in r.get('kelimeler', []):
            lem |= lem_syn.get(K.sade(e['lemma']), set())
        for x in r.get('sozlukler', {}).get('kaikki_vikisozluk') or []:
            lem |= lem_syn.get(x['u'], set())
        for o in lem:
            oy[o] += 1
        grup = collections.Counter()
        ornek = {}
        for o, w in oy.items():
            s = synset(o)
            if s is None:
                continue
            a = ata(s, derinlik)
            anahtar = (a.name(), s.lexname())
            grup[anahtar] += w
            ornek.setdefault(anahtar, (s.name(), s.definition()))
        if not grup:
            continue
        (a, lex), _ = grup.most_common(1)[0]
        sonuc[k] = {'yontem': 'Arabic WordNet v2 (el yapımı, kök etiketli) → Princeton WordNet', 'ince': a, 'orta': lex, 'ust': UST.get(lex, 'hâl ve vasıf'),
                    'dayanak_synset': ornek[(a, lex)][0], 'dayanak_tanim': ornek[(a, lex)][1], 'synset_sayisi': len(oy)}
    return sonuc

"""Yeni mana kategori ağacı (WordNet yerine): 9 üst kategori, 26 kavram. kategori/*.txt: kök|asıl başına kavram kodu."""
import pathlib
HERE = pathlib.Path(__file__).resolve().parent
AGAC = [
 ('Varlığın çerçevesi', [('ZM', 'zaman ve vakit'), ('MK', 'mekân, yön ve yer'), ('SY', 'miktar, sayı ve ölçü'), ('SK', 'şekil ve hey\'et')]),
 ('Tabiat', [('GT', 'gök ve tabiat hâdiseleri'), ('MD', 'madde: su, toprak, taş, maden'), ('BT', 'bitki'), ('HY', 'hayvan')]),
 ('Beden', [('BD', 'beden, uzuv ve bedenin hâlleri'), ('YI', 'yeme ve içme')]),
 ('Fiil ve oluş', [('HR', 'hareket, gelme gitme, yolculuk'), ('TK', 'temas ve kuvvet: tutma, vurma, kesme'), ('DG', 'oluş, değişme, yok oluş'), ('YP', 'yapma, yaratma ve yapılmış eşya')]),
 ('Nefs ve idrak', [('AL', 'algılama: görme, işitme, gizlilik-açıklık'), ('IL', 'ilim, akıl ve düşünce'), ('HS', 'his ve duygu'), ('IR', 'irade, niyet ve istek')]),
 ('Söz', [('SZ', 'söz, ses ve haber')]),
 ('İçtimaiyat', [('IN', 'insan, soy ve akrabalık'), ('TP', 'topluluk, toplanma'), ('ML', 'mal, mülk, alışveriş, verme'), ('HK', 'hüküm, kudret ve idare'), ('CS', 'çekişme ve savaş'), ('AH', 'ahlâk ve muamele')]),
 ('Din', [('DN', 'din, ibadet, iman ve küfür')]),
 ('Vasıf ve edat', [('HV', 'hâl ve vasıf'), ('ED', 'edat ve işaret kelimeleri')]),
]
KOD = {k: (u, a) for u, L in AGAC for k, a in L}
def oku():
    K = {}
    for f in sorted((HERE / 'kategori').glob('*.txt')):
        for l in f.read_text(encoding='utf-8').splitlines():
            if l.strip():
                k, v = l.split('|'); K[k] = v.split(',')
    assert all(c in KOD for v in K.values() for c in v)
    return K

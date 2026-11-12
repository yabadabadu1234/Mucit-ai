import istikak as I
import turkce as T
import wikt as W
import dogrula as D


def calistir():
    tot = hit = 0
    kok = 0
    kacan = []
    for k in T.db():
        t = W.tanik_kumesi(k)
        if not t:
            continue
        sinif, b, _ = I.tablo(I.normala(k))
        if sinif == 'reddedildi':
            continue
        kok += 1
        gen = {D.norm(x['ar']) for x in b}
        genh = {W.harekesiz(x['ar']) for x in b}
        for f, g in t.items():
            tot += 1
            if f in gen or (W.harekesiz(f) == f and f in genh):
                hit += 1
            else:
                kacan.append((k, f, g))
    return kok, tot, hit, kacan


if __name__ == '__main__':
    kok, tot, hit, kacan = calistir()
    print('kök', kok, 'tanıklı biçim', tot, 'motorun ürettiği', hit, 'oran %.1f' % (100 * hit / tot))

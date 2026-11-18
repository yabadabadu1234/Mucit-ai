import json, pathlib
from shapely.geometry import box
from shapely.ops import unary_union, polylabel
from yerlesim import kare, izgara, satirlar, sureler
HERE = pathlib.Path(__file__).resolve().parent
def olay(X, Y, W, H):
    T = json.load(open(HERE / 'olay_orgusu_teklif.json', encoding='utf-8')); SUR = {s[0]: s for s in sureler()}
    sira = [s for o in T['odalar'] for s in o['sureler']]; assert sorted(sira) == list(range(1, 115))
    oda_of = {s: i for i, o in enumerate(T['odalar']) for s in o['sureler']}
    QR = satirlar([(s, SUR[s][2] + 8) for s in sira], X, Y, W, H)
    S_, K_, A_, ODA = [], [], [], []
    for i, o in enumerate(T['odalar']):
        kutular = [box(*[round(v, 3) for v in (QR[s][0], QR[s][1], QR[s][0] + QR[s][2], QR[s][1] + QR[s][3])]) for s in o['sureler']]
        g = unary_union(kutular).simplify(0)
        assert g.geom_type == 'Polygon', (i, g.geom_type)
        pl = polylabel(g, 0.5); r = g.exterior.distance(pl)
        ODA.append({'ad': o['ad'], 'poly': [[round(x, 2), round(y, 2)] for x, y in g.exterior.coords[:-1]], 'lab': [round(pl.x - 0.65 * r, 2), round(pl.y - 0.65 * r, 2), round(1.3 * r, 2), round(1.3 * r, 2)], 'delik': len(g.interiors)})
    for s in sira:
        _, adi, na, KIS = SUR[s]; x, y, w, h = QR[s]; x += 3; y += 3; w -= 6; h -= 6; tb = min(30.0, max(3.0, min(w, h) * 0.12))
        S_.append([round(x, 2), round(y, 2), round(w, 2), round(h, 2), '%d · %s' % (s, adi), round(tb, 2), oda_of[s]])
        KR = kare([(j, len(k[1])) for j, k in enumerate(KIS)], x + 1, y + tb, w - 2, h - tb - 1, True)
        for j, (kad, ay) in enumerate(KIS):
            kx, ky, kw, kh = KR[j]; kx += 0.8; ky += 0.8; kw -= 1.6; kh -= 1.6; kt = min(14.0, max(1.0, min(kw, kh) * 0.1))
            K_.append([round(kx, 3), round(ky, 3), round(kw, 3), round(kh, 3), kad, round(kt, 3), s])
            for (ax, ay_, cs), a in zip(izgara(len(ay), kx, ky + kt, kw, kh - kt, True), ay):
                gg = cs * 0.04; A_.append([round(ax + gg, 3), round(ay_ + gg, 3), round(cs - 2 * gg, 3), '%d:%d' % (s, a), round((cs - 2 * gg) * 0.16, 3)])
    return {'durum': T['durum'], 'odalar': ODA, 'S': S_, 'K': K_, 'A': A_}
if __name__ == '__main__':
    O = olay(5620, 40, 1720, 1720)
    print(len(O['odalar']), [len(o['poly']) for o in O['odalar']], [o['delik'] for o in O['odalar']], len(O['S']), len(O['K']), len(O['A']))

import json, collections, pathlib
B = pathlib.Path(__file__).resolve().parent.parent
PENCERE = 8
def ayetler():
    v = collections.OrderedDict()
    for l in open(B / "veri_harici" / "eyupipler" / "quran-morphology.txt", encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        if len(p) < 4:
            continue
        s, a, k, _ = (int(x) for x in p[0].split(":"))
        tg = p[3].split("|")
        kok = next((t[5:] for t in tg if t.startswith("ROOT:")), None)
        v.setdefault((s, a), []).append((k, kok, set(tg)))
    return v
def kokler(parca):
    return [k for _, k, _ in parca if k]
def cikar():
    kenar = collections.defaultdict(lambda: collections.Counter())
    delil = collections.defaultdict(list)
    for (s, a), tok in ayetler().items():
        n = len(tok)
        for i, (_, _, tg) in enumerate(tok):
            if "RSLT" in tg:
                tur = "sart"
                c = next((j for j in range(i - 1, -1, -1) if "COND" in tok[j][2]), None)
                if c is None:
                    continue
                sol = kokler(tok[c + 1:i][:PENCERE]); sag = kokler(tok[i + 1:i + 1 + PENCERE])
            elif "CAUS" in tg:
                tur = "sebep"
                sol = kokler(tok[max(0, i - PENCERE):i]); sag = kokler(tok[i + 1:i + 1 + PENCERE])
            elif "PRP" in tg:
                tur = "gaye"
                sol = kokler(tok[max(0, i - PENCERE):i]); sag = kokler(tok[i + 1:i + 1 + PENCERE])
            else:
                continue
            for x in set(sol):
                for y in set(sag):
                    if x != y:
                        kenar[(x, y)][tur] += 1
                        if len(delil[(x, y)]) < 3:
                            delil[(x, y)].append(f"{s}:{a}")
    return kenar, delil
if __name__ == "__main__":
    k, d = cikar()
    tum = collections.Counter()
    for (x, y), c in k.items():
        for t, n in c.items():
            tum[t] += n
    print(len(k), dict(tum))
    json.dump({f"{x}|{y}": {"n": dict(c), "delil": d[(x, y)]} for (x, y), c in k.items()}, open(pathlib.Path(__file__).parent / "metin_kenarlari.json", "w", encoding="utf-8"), ensure_ascii=False)

"""Programla üretilen mantık / bulmaca / sınır-değer verisi: üreteç, bağımsız denetçi, ölçü.

Kullanım: python3 uret_mantik.py [N] [tohum]
Üç aile: (A) önerme kuralı uygulama, (B) sıralama bulmacası, (C) sınır-değer.
Her örnek: yapısal kayıt (soru, çözüm adımları, cevap) + ondan çizilen Türkçe metin.
Denetçi, çözücüden ayrı bir algoritmayla (sayım / yeniden yürütme) kaydı doğrular.
"""
import itertools
import json
import random
import sys
from collections import Counter

ATOMLAR = [("lamba", "yanar", "yanmaz"), ("kapı", "açılır", "açılmaz"), ("alarm", "çalar", "çalmaz"),
           ("motor", "çalışır", "çalışmaz"), ("pompa", "su basar", "su basmaz"), ("fan", "döner", "dönmez"),
           ("sunucu", "yanıt verir", "yanıt vermez"), ("bağlantı", "kurulur", "kurulmaz"),
           ("kasa", "kilitlenir", "kilitlenmez"), ("vana", "kapanır", "kapanmaz"), ("kuyruk", "boşalır", "boşalmaz"),
           ("kayıt", "silinir", "silinmez"), ("sensör", "ölçer", "ölçmez"), ("ısıtıcı", "ısınır", "ısınmaz"),
           ("pil", "şarj olur", "şarj olmaz"), ("dosya", "kaydedilir", "kaydedilmez"), ("test", "geçer", "geçmez"),
           ("derleme", "başarılır", "başarılmaz")]
IS = ["Eğer {p} ise {q}.", "{p} ise {q}.", "{p} olduğunda {q}.", "Her {p} durumunda {q}."]
VE = ["Eğer {p} ve {r} ise {q}.", "{p} ve aynı zamanda {r} ise {q}.", "{p} ile {r} birlikte gerçekleşirse {q}."]
FACT = ["{p}.", "Biliniyor ki {p}.", "Gözlendi: {p}."]
QUERY = ["{q} mu?", "{q} sonucuna varılır mı?", "Bu durumda {q} denebilir mi?"]


def lit_text(l):
    s, pos, neg = ATOMLAR[l[0]]
    return f"{s} {pos if l[1] else neg}"


def neg(l):
    return (l[0], not l[1])


def kapanis(rules, facts):
    """Birim yayılımı: kural ve karşıtlarıyla. Adım listesi döner."""
    known, steps = set(facts), []
    clauses = []
    for i, (prem, concl) in enumerate(rules):
        clauses.append((i, "düz", list(prem), concl))
        lits = list(prem) + [neg(concl)]
        for j, t in enumerate(lits):
            others = [x for k, x in enumerate(lits) if k != j]
            clauses.append((i, "karşıt", [x for x in others], neg(t)))
    ch = True
    while ch:
        ch = False
        for i, kind, prem, c in clauses:
            if c not in known and all(p in known for p in prem):
                known.add(c)
                steps.append({"kural": i, "tür": kind, "öncül": [list(p) for p in prem], "sonuç": list(c)})
                ch = True
    return known, steps


def modeller(rules, facts, atoms):
    atoms = sorted(atoms)
    out = []
    for vals in itertools.product([False, True], repeat=len(atoms)):
        a = dict(zip(atoms, vals))
        ok = all(a[f[0]] == f[1] for f in facts)
        ok = ok and all((not all(a[p[0]] == p[1] for p in prem)) or a[c[0]] == c[1] for prem, c in rules)
        if ok:
            out.append(a)
    return out


def cevap_sayim(rules, facts, q):
    atoms = {l[0] for l in facts} | {q[0]} | {p[0] for pr, c in rules for p in pr} | {c[0] for pr, c in rules}
    ms = modeller(rules, facts, atoms)
    if not ms:
        return None
    vals = {m[q[0]] == q[1] for m in ms}
    return "kesin doğru" if vals == {True} else "kesin yanlış" if vals == {False} else "belirsiz"


def ornek_A(rng, sinif=None, min_adim=2):
    for _ in range(600):
        idx = rng.sample(range(len(ATOMLAR)), rng.randint(5, 8))
        lit = lambda: (rng.choice(idx), rng.random() < 0.7)
        rules = []
        for _ in range(rng.randint(3, 6)):
            k = rng.choice([1, 1, 2])
            prem = [lit() for _ in range(k)]
            if len({p[0] for p in prem}) < k:
                continue
            c = lit()
            if c[0] in {p[0] for p in prem}:
                continue
            if any(sorted(prem) == sorted(p2) and c == c2 for p2, c2 in rules):
                continue
            rules.append((prem, c))
        facts = [lit() for _ in range(rng.randint(1, 2))]
        if len({f[0] for f in facts}) < len(facts) or len(rules) < 3:
            continue
        known, steps = kapanis(rules, facts)
        if any(neg(l) in known for l in known):
            continue
        q = (rng.choice(idx), rng.random() < 0.5)
        ans = cevap_sayim(rules, facts, q)
        if ans is None:
            continue
        if ans == "kesin doğru" and q not in known:
            continue
        if ans == "kesin yanlış" and neg(q) not in known:
            continue
        if q in facts or neg(q) in facts:
            continue
        if ans != "belirsiz":
            hedef = q if ans == "kesin doğru" else neg(q)
            gerek, bekle = set(), [hedef]
            while bekle:
                x = bekle.pop()
                for k, st in enumerate(steps):
                    if tuple(st["sonuç"]) == x and k not in gerek:
                        gerek.add(k)
                        bekle += [tuple(p) for p in st["öncül"]]
            steps = [st for k, st in enumerate(steps) if k in gerek]
        if len(steps) < min_adim or (sinif and ans != sinif):
            continue
        return {"aile": "A", "kurallar": [[[list(p) for p in pr], list(c)] for pr, c in rules],
                "olgular": [list(f) for f in facts], "soru": list(q), "adımlar": steps, "cevap": ans}
    return None


def metin_A(r, rng):
    def L(l):
        return lit_text(tuple(l))
    s = ["Kurallar:"]
    for i, (pr, c) in enumerate(r["kurallar"], 1):
        if len(pr) == 1:
            s.append(f"K{i}. " + rng.choice(IS).format(p=L(pr[0]), q=L(c)))
        else:
            s.append(f"K{i}. " + rng.choice(VE).format(p=L(pr[0]), r=L(pr[1]), q=L(c)))
    s.append("Olgular: " + " ".join(rng.choice(FACT).format(p=L(f)) for f in r["olgular"]))
    s.append("Soru: " + rng.choice(QUERY).format(q=L(r["soru"])).capitalize() + " (kesin doğru / kesin yanlış / belirsiz)")
    s.append("Çözüm:")
    for n, st in enumerate(r["adımlar"], 1):
        pre = " ve ".join(L(p) for p in st["öncül"])
        how = "K%d" % (st["kural"] + 1) + (" (karşıtı)" if st["tür"] == "karşıt" else "")
        s.append(f"{n}. {pre} olduğundan, {how} gereği: {L(st['sonuç'])}.")
    if r["cevap"] == "belirsiz":
        s.append("Hiçbir kural bu önermeyi ya da değilini türetmiyor ve her iki durumu da sağlayan bir dünya var.")
    s.append("Cevap: " + r["cevap"])
    return "\n".join(s)


def denetle_A(r):
    rules = [([tuple(p) for p in pr], tuple(c)) for pr, c in r["kurallar"]]
    facts = [tuple(f) for f in r["olgular"]]
    q = tuple(r["soru"])
    known = set(facts)
    for st in r["adımlar"]:
        prem = [tuple(p) for p in st["öncül"]]
        c = tuple(st["sonuç"])
        if not all(p in known for p in prem):
            return False
        i = st["kural"]
        if not (0 <= i < len(rules)):
            return False
        sub = [rules[i]]
        atoms = {a for pr, cc in sub for a in [x[0] for x in pr] + [cc[0]]} | {p[0] for p in prem} | {c[0]}
        ms = modeller(sub, prem, atoms)
        if not ms or not all(m[c[0]] == c[1] for m in ms):
            return False
        known.add(c)
    ans = cevap_sayim(rules, facts, q)
    return ans == r["cevap"] and (ans != "kesin doğru" or q in known) and (ans != "kesin yanlış" or neg(q) in known)


ISIMLER = ["Ayşe", "Burak", "Cem", "Deniz", "Ece", "Fatih", "Gül"]


def klozlar_B(n, perm):
    cl = []
    pos = {p: i for i, p in enumerate(perm)}
    for a, b in itertools.permutations(range(n), 2):
        if pos[a] + 1 == pos[b]:
            cl.append(("hemen_sol", a, b))
        if pos[a] < pos[b]:
            cl.append(("sol", a, b))
        if abs(pos[a] - pos[b]) == 2:
            cl.append(("arada_bir", a, b))
    for a in range(n):
        if pos[a] == 0:
            cl.append(("ilk", a))
        if pos[a] == n - 1:
            cl.append(("son", a))
    return cl


def sagla(c, pos):
    t = c[0]
    if t == "hemen_sol":
        return pos[c[1]] + 1 == pos[c[2]]
    if t == "sol":
        return pos[c[1]] < pos[c[2]]
    if t == "arada_bir":
        return abs(pos[c[1]] - pos[c[2]]) == 2
    if t == "ilk":
        return pos[c[1]] == 0
    return pos[c[1]] == len(pos) - 1


def cozum_say(n, clues):
    cnt = 0
    for perm in itertools.permutations(range(n)):
        pos = {p: i for i, p in enumerate(perm)}
        if all(sagla(c, pos) for c in clues):
            cnt += 1
            if cnt > 1:
                return cnt
    return cnt


def ornek_B(rng):
    n = rng.choice([4, 5])
    perm = list(range(n))
    rng.shuffle(perm)
    pool = klozlar_B(n, perm)
    rng.shuffle(pool)
    clues = []
    for c in pool:
        clues.append(c)
        if cozum_say(n, clues) == 1:
            break
    for c in list(clues):
        rest = [x for x in clues if x != c]
        if cozum_say(n, rest) == 1:
            clues = rest
    names = rng.sample(ISIMLER, n)
    dom = {p: set(range(n)) for p in range(n)}
    adim = []

    def destek(c, p, v, d):
        for vals in itertools.product(*[sorted(d[x]) for x in sorted({y for y in c[1:]})]):
            pos = dict(zip(sorted({y for y in c[1:]}), vals))
            if pos[p] == v and len(set(pos.values())) == len(pos) and sagla(c, pos | {k: -99 for k in range(n) if k not in pos}):
                return True
        return False
    ch = True
    while ch:
        ch = False
        for ci, c in enumerate(clues):
            for p in sorted({y for y in c[1:]}):
                for v in sorted(dom[p]):
                    if not destek(c, p, v, dom):
                        dom[p].discard(v)
                        adim.append({"ipucu": ci, "kişi": p, "elenen_konum": v})
                        ch = True
    if any(len(d) != 1 for d in dom.values()):
        return None
    sol = {p: min(d) for p, d in dom.items()}
    return {"aile": "B", "n": n, "isimler": names, "ipuçları": [list(c) for c in clues], "adımlar": adim,
            "cevap": [sol[p] for p in range(n)]}


def metin_B(r, rng):
    N = r["isimler"]
    def f(c):
        t = c[0]
        if t == "hemen_sol":
            return f"{N[c[1]]}, {N[c[2]]}'in hemen solunda oturuyor."
        if t == "sol":
            return f"{N[c[1]]}, {N[c[2]]}'den daha solda."
        if t == "arada_bir":
            return f"{N[c[1]]} ile {N[c[2]]} arasında tam bir kişi var."
        if t == "ilk":
            return f"{N[c[1]]} en solda."
        return f"{N[c[1]]} en sağda."
    s = [f"{r['n']} kişi sıraya diziliyor (konum 1 en sol). İpuçları:"]
    s += [f"İ{i + 1}. " + f(tuple(c)) for i, c in enumerate(r["ipuçları"])]
    s.append("Soru: Herkes hangi konumda?")
    s.append("Çözüm (aday konum eleme):")
    for k, a in enumerate(r["adımlar"], 1):
        s.append(f"{k}. İ{a['ipucu'] + 1} gereği {N[a['kişi']]} için konum {a['elenen_konum'] + 1} elenir.")
    s.append("Cevap: " + ", ".join(f"{N[p]}={r['cevap'][p] + 1}" for p in range(r["n"])))
    return "\n".join(s)


def denetle_B(r):
    n = r["n"]
    clues = [tuple(c) for c in r["ipuçları"]]
    if cozum_say(n, clues) != 1:
        return False
    sol = next(p for p in itertools.permutations(range(n)) if all(sagla(c, {x: i for i, x in enumerate(p)}) for c in clues))
    truth = {x: i for i, x in enumerate(sol)}
    if r["cevap"] != [truth[p] for p in range(n)]:
        return False
    dom = {p: set(range(n)) for p in range(n)}
    for a in r["adımlar"]:
        c = clues[a["ipucu"]]
        p, v = a["kişi"], a["elenen_konum"]
        if p not in c[1:]:
            return False
        ks = sorted(set(c[1:]))
        ok = False
        for vals in itertools.product(*[sorted(dom[x]) for x in ks]):
            pos = dict(zip(ks, vals))
            if pos[p] == v and len(set(vals)) == len(vals) and sagla(c, pos):
                ok = True
        if ok or v == truth[p]:
            return False
        dom[p].discard(v)
    return all(len(d) == 1 for d in dom.values())


def ornek_C(rng):
    t = rng.choice(["sayfa", "kademe", "kalan"])
    if t == "sayfa":
        k = rng.randint(3, 25)
        src = f"def f(n):\n    return (n + {k - 1}) // {k}"
        hedef = rng.randint(2, 9)
    elif t == "kademe":
        e, a, b = rng.randint(5, 40), rng.randint(2, 9), rng.randint(1, 8)
        src = f"def f(n):\n    if n <= {e}:\n        return {a} * n\n    return {a} * {e} + {b} * (n - {e})"
        hedef = rng.randint(a * e + 1, a * e + 60)
    else:
        m, rr = rng.randint(3, 20), 0
        rr = rng.randint(0, m - 1)
        src = f"def f(n):\n    return n % {m} == {rr}"
        hedef = True
    ns = {}
    exec(src, ns)
    f = ns["f"]
    if t == "kalan":
        b = next(n for n in range(0, 200) if f(n) == hedef)
        soru = "f(n) ilk kez True olan en küçük n nedir? Sınır komşularını da hesapla."
    else:
        b = next(n for n in range(0, 2000) if f(n) >= hedef)
        soru = f"f(n) ilk kez >= {hedef} olan en küçük n nedir? Sınır komşularını da hesapla."
    kom = [[n, f(n)] for n in (b - 1, b, b + 1) if n >= 0]
    return {"aile": "C", "kaynak": src, "hedef": hedef, "tür": t, "soru": soru, "komşular": kom, "cevap": b}


def metin_C(r, rng):
    s = ["Python:", r["kaynak"], "Soru: " + r["soru"], "Çözüm:"]
    for n, v in r["komşular"]:
        s.append(f"f({n}) = {v}")
    s.append(f"Sınır n={r['cevap']}: önceki değer koşulu sağlamıyor, bu değer sağlıyor.")
    s.append(f"Cevap: {r['cevap']}")
    return "\n".join(s)


def denetle_C(r):
    ns = {}
    exec(r["kaynak"], ns)
    f = ns["f"]
    ok = (lambda v: v == r["hedef"]) if r["tür"] == "kalan" else (lambda v: v >= r["hedef"])
    b = r["cevap"]
    if not ok(f(b)) or (b > 0 and ok(f(b - 1))):
        return False
    if any(any(ok(f(n)) for n in [m]) for m in range(0, b)):
        return False
    return all(f(n) == v for n, v in r["komşular"])


def bozma(r, rng):
    r = json.loads(json.dumps(r))
    a = r["aile"]
    if a == "A":
        k = rng.choice(["cevap", "adım", "öncül"])
        if k == "cevap":
            r["cevap"] = rng.choice([x for x in ["kesin doğru", "kesin yanlış", "belirsiz"] if x != r["cevap"]])
        elif r["adımlar"]:
            st = rng.choice(r["adımlar"])
            if k == "adım":
                st["sonuç"][1] = not st["sonuç"][1]
            else:
                st["kural"] = (st["kural"] + 1) % len(r["kurallar"])
        else:
            r["cevap"] = "kesin doğru" if r["cevap"] != "kesin doğru" else "belirsiz"
    elif a == "B":
        k = rng.choice(["cevap", "adım"])
        if k == "cevap":
            c = r["cevap"]
            i, j = rng.sample(range(len(c)), 2)
            c[i], c[j] = c[j], c[i]
        elif r["adımlar"]:
            st = rng.choice(r["adımlar"])
            st["elenen_konum"] = (st["elenen_konum"] + 1) % r["n"]
        else:
            r["cevap"][0], r["cevap"][1] = r["cevap"][1], r["cevap"][0]
    else:
        r["cevap"] += rng.choice([-1, 1, 2])
    return r


DEN = {"A": denetle_A, "B": denetle_B, "C": denetle_C}
MET = {"A": metin_A, "B": metin_B, "C": metin_C}
URE = {"A": ornek_A, "B": ornek_B, "C": ornek_C}


def ngram(texts, n=4):
    c = Counter()
    for t in texts:
        w = t.split()
        for i in range(len(w) - n + 1):
            c[tuple(w[i:i + n])] += 1
    return len(c), sum(c.values())


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
    for fam in "ABC":
        recs, texts, tries = [], [], 0
        while len(recs) < N and tries < N * 20:
            tries += 1
            r = ornek_A(rng, rng.choice(['kesin doğru', 'kesin yanlış', 'belirsiz'])) if fam == 'A' else URE[fam](rng)
            if r:
                recs.append(r)
                texts.append(MET[fam](r, rng))
        gecerli = sum(DEN[fam](r) for r in recs)
        reddedilen = sum(not DEN[fam](bozma(r, rng)) for r in recs)
        ayri = len({json.dumps({k: v for k, v in r.items() if k not in ('adımlar', 'komşular')}, sort_keys=True) for r in recs})
        d, tot = ngram(texts)
        uz = sorted(len(t.split()) for t in texts)
        print(f"[{fam}] üretilen={len(recs)} (deneme {tries}) | denetçiyi geçen={gecerli}/{len(recs)} | "
              f"bozulmuş kayıtta REDDEDİLEN={reddedilen}/{len(recs)} | ayrı soru={ayri} | "
              f"4-gram ayrık/toplam={d}/{tot}={d / tot:.2f} | uzunluk ortanca={uz[len(uz) // 2]} p90={uz[int(len(uz) * .9)]}")
        if "--ornek" in sys.argv:
            print("-----\n" + texts[0] + "\n-----")


if __name__ == "__main__":
    main()

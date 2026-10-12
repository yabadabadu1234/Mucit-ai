import numpy as np

D8_ADEDI = 8
RENK_KAYMA_ADEDI = 9


def d8(g, k):
    a = np.asarray(g)
    if k >= 4:
        a = a.T
    return np.rot90(a, k % 4)


def d8_ters(g, k):
    a = np.rot90(np.asarray(g), -(k % 4))
    if k >= 4:
        a = a.T
    return a


def renk_kaydir(g, s):
    a = np.asarray(g)
    return np.where(a == 0, 0, (a - 1 + s) % RENK_KAYMA_ADEDI + 1)


def renk_kaydir_ters(g, s):
    return renk_kaydir(g, (-s) % RENK_KAYMA_ADEDI)


def donustur(g, k, s):
    return renk_kaydir(d8(g, k), s)


def donustur_ters(g, k, s):
    return d8_ters(renk_kaydir_ters(g, s), k)


def _cift(p, k, s):
    return {"input": donustur(p["input"], k, s).tolist(), "output": donustur(p["output"], k, s).tolist()}


def birakma_turetmeleri(gorev, adet):
    ornekler = gorev["train"]
    n = len(ornekler)
    if n < 2:
        return []
    cikti = []
    for i in range(adet):
        j = i % n
        k = (i // n) % D8_ADEDI
        s = (i // (n * D8_ADEDI)) % RENK_KAYMA_ADEDI
        sira = [(j + 1 + m) % n for m in range(n - 1)]
        cikti.append({
            "train": [_cift(ornekler[m], k, s) for m in sira],
            "test": [_cift(ornekler[j], k, s)],
            "kaynak": {"birakilan": j, "d8": k, "kayma": s},
        })
    return cikti


def program_ile_cogalt(sinayici, gorev, adet):
    taban = [p["input"] for p in gorev["train"]] + [t["input"] for t in gorev.get("test", [])]
    cikti = []
    for i in range(adet):
        g = taban[i % len(taban)]
        k = (i // len(taban)) % D8_ADEDI
        s = (i // (len(taban) * D8_ADEDI)) % RENK_KAYMA_ADEDI
        girdi = donustur(g, k, s).tolist()
        sonuc = sinayici(girdi)
        if sonuc is not None:
            cikti.append({"input": girdi, "output": np.asarray(sonuc).tolist(), "kaynak": {"d8": k, "kayma": s, "girdi": i % len(taban)}})
    return cikti
